#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""候选瘦身与 picks 自动装配（候选瘦身与自动装配组件）。

解决的问题
----------
`tkSearchSubjectQuestion` / `tkQuestionAnalysis` 的原始返回含完整题干 / 选项 / 解析 HTML。
若把 25 题的原样返回全塞进模型上下文，会：① 每轮都变慢（上下文膨胀）；② 逼近自动压缩线
（上下文压缩风险）；③ 模型还得**重新输出一遍**才能落盘（二次 token）。

本脚本把这件事拆开：
  * 取数阶段：原始返回**落盘**（`*_pool.json`），模型只看 `table` 产出的**紧凑候选表**（一行一题）。
  * 决策阶段：模型只回「题位 → 短ID」映射（25 行，极省 token，且不会抄错一长串内部 ID）。
  * 装配阶段：`assemble` 从落盘池里回填题干/选项/答案/考点/解析，直接产出 picks。

子命令
------
  table     原始搜题返回 → 紧凑候选表 + sidmap + pool
  pool      原始解析返回（可多个）→ analysis_pool.json
  assemble  「题位→短ID」映射 + pool(+analysis_pool) → picks JSON

示例
----
  python3 shrink_candidates.py table --in raw_s1.json raw_s2.json --out-dir . --prefix cand
  python3 shrink_candidates.py pool  --in raw_a1.json --out analysis_pool.json
  python3 shrink_candidates.py assemble --sidmap cand_sidmap.json --pool cand_pool.json \\
      --analysis-pool analysis_pool.json --spec spec.json --map sel.json --out picks_1.json
"""
import argparse
import hashlib
import json
import os
import re
import sys

# ---------------------------------------------------------------- 基础工具

# 题型码 → 渲染器 kind（与 render_paper._norm_kind 口径一致）
CATE_TO_KIND = {
    1: "选择", 2: "填空", 3: "多选", 4: "判断", 5: "计算",
    6: "应用", 7: "操作", 9: "解答",
}
CATE_NAME_TO_KIND = [
    ("选择", "选择"), ("填空", "填空"), ("多选", "多选"), ("判断", "判断"),
    ("解答", "解答"), ("计算", "计算"), ("应用", "应用"), ("操作", "操作"),
    ("阅读", "阅读理解"), ("完形", "完形填空"), ("书面表达", "书面表达"),
    ("补全对话", "补全对话"), ("连词成句", "连词成句"), ("句型转换", "句型转换"),
    ("单词拼写", "单词拼写"), ("排序", "排序"), ("改错", "改错"),
]


def _jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _jdump(obj, path):
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def _items(raw):
    """把各种形态的返回归一化成题目对象列表。"""
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        for k in ("data", "questions", "picks", "list", "result"):
            v = raw.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
        # 单题对象
        if "SID" in raw or "Content" in raw:
            return [raw]
    return []


def _text(html, limit=None):
    """HTML → 纯文本（保留公式可读性：只去标签与压缩空白）。"""
    s = html or ""
    s = re.sub(r"<img[^>]*>", "〔图〕", s, flags=re.I)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = (s.replace("&nbsp;", " ").replace("&amp;", "&")
          .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
          .replace("&quot;", '"'))
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("|", "｜")          # 防 Markdown 表格破裂
    if limit and len(s) > limit:
        s = s[:limit] + "…"
    return s


# ⚠️ 交付物红线：**不提供**「接口 Points[].Value → 考点」的提取器。
#    题库内部考点名属接口元数据字段值，任何对外产物（解析/细目表）都不得出现；
#    【考点】只能来自教师侧命名（细目表 `point` 或模型显式给定），否则留空、不渲染。
#    （原 `_points_of()` 已按此红线移除，勿再加回。）


def _degree_band(deg):
    try:
        d = float(deg)
    except (TypeError, ValueError):
        return ""
    if d >= 0.8:
        return "易"
    if d >= 0.6:
        return "较易"
    if d >= 0.4:
        return "中"
    if d >= 0.2:
        return "较难"
    return "难"


def _kind_of(obj, default="解答"):
    n = obj.get("CateName") or ""
    for key, kind in CATE_NAME_TO_KIND:
        if key in n:
            return kind
    c = obj.get("Cate")
    if isinstance(c, int) and c in CATE_TO_KIND:
        return CATE_TO_KIND[c]
    return default


def _answer_of(obj, style="letter"):
    """答案：DisplayAnswer 已是纯文本；Answers 元素可能含 MathJye，**保留原始 HTML**
    （线性化由下游 build_questions/render_paper 统一做）。"""
    if style == "none":
        return ""
    disp = (obj.get("DisplayAnswer") or "").strip()
    ans = obj.get("Answers") or []
    body = disp
    if not body:
        body = "；".join(str(a).strip() for a in ans if str(a).strip())
    if not body:
        return ""
    if style == "pretty":
        kind = _kind_of(obj)
        if kind == "选择" and disp:
            return "故选：%s．" % disp
        if kind in ("填空", "多选", "判断") and not disp:
            return "故答案为：%s．" % body
    return body


def _sid(obj):
    return str(obj.get("SID") or obj.get("sid") or "").strip()


def _stem_hash(html):
    """题干判重键：题干 + 选项 去标签/空白后的哈希；过短不参与（防误报）。

    ⚠️ 仅用于**判重**，不入库、不外显；源串来自内存对象，不落盘。
    """
    s = html or ""
    if not isinstance(s, str):
        s = str(s)
    s = re.sub(r"<img[^>]*>", "〔图〕", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\s+", "", s)
    s = (s.replace("&nbsp;", "").replace("&amp;", "&")
          .replace("&lt;", "<").replace("&gt;", ">"))
    if len(s) < 30:
        return None
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- table

def cmd_table(args):
    pool, sidmap, rows, seen = {}, {}, [], set()
    n = 0
    for path in args.inputs:
        try:
            raw = _jload(path)
        except Exception as e:
            print("[shrink] 跳过 %s（%s）" % (path, e), file=sys.stderr)
            continue
        for obj in _items(raw):
            sid = _sid(obj)
            if not sid or sid in seen:
                continue
            seen.add(sid)
            n += 1
            short = "s%02d" % n
            sidmap[short] = sid
            pool[sid] = obj
            rows.append({
                "id": short,
                "cate": _kind_of(obj),
                # ⚠️ 只留「已归一化的五档」；不落 `Degree` 原值、`Label`/`CateName` 等接口元数据字段值
                "band": _degree_band(obj.get("Degree")),
                "stem": _text(obj.get("Content"), args.max_text),
                "nopts": len(obj.get("Options") or []),
            })

    if not rows:
        print("[shrink] 未从输入中解析出任何题目。", file=sys.stderr)
        return 1

    prefix = os.path.join(args.out_dir, args.prefix)
    _jdump(sidmap, prefix + "_sidmap.json")
    _jdump(pool, prefix + "_pool.json")

    if args.format == "json":
        _jdump(rows, prefix + "_table.json")
        table_path = prefix + "_table.json"
    else:
        sep = "\t" if args.format == "tsv" else " | "
        lines = []
        if args.format == "md":
            lines.append("| ID | 题型 | 难度 | 选项数 | 题干（前%d字） |" % args.max_text)
            lines.append("|---|---|---|---|---|")
        for r in rows:
            cells = [r["id"], r["cate"], (r["band"] or "-"),
                     str(r["nopts"]), r["stem"]]
            lines.append(sep.join(cells) if args.format == "tsv" else "| " + " | ".join(cells) + " |")
        table_path = prefix + "_table." + ("tsv" if args.format == "tsv" else "md")
        with open(table_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    print("[shrink] 候选 %d 条" % len(rows))
    print("[shrink] 候选表: %s" % table_path)
    print("[shrink] 短ID映射: %s" % (prefix + "_sidmap.json"))
    print("[shrink] 原始池: %s" % (prefix + "_pool.json"))
    print("[shrink] 提示：决策时只回 <题位>:<ID>（如 1:s03），其余由 assemble 自动回填。")
    return 0


# ---------------------------------------------------------------- pool

def cmd_pool(args):
    pool = {}
    for path in args.inputs:
        try:
            raw = _jload(path)
        except Exception as e:
            print("[shrink] 跳过 %s（%s）" % (path, e), file=sys.stderr)
            continue
        for obj in _items(raw):
            sid = _sid(obj)
            if sid:
                pool[sid] = obj
    _jdump(pool, args.out)
    print("[shrink] 解析池: %d 题 → %s" % (len(pool), args.out))
    return 0


# ---------------------------------------------------------------- assemble

def _load_map(path):
    """接受 {"1":"s03"} 或 [{"no":1,"sid":"s03"}] 或 [[1,"s03"]]。"""
    d = _jload(path)
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out[int(re.sub(r"\D", "", str(k)) or 0)] = str(v).strip()
    elif isinstance(d, list):
        for it in d:
            if isinstance(it, dict):
                no = it.get("no", it.get("slot"))
                sid = it.get("sid", it.get("SID", it.get("id")))
            else:
                no, sid = it[0], it[1]
            out[int(re.sub(r"\D", "", str(no)) or 0)] = str(sid).strip()
    return {k: v for k, v in out.items() if k and v}


def _score_kind_from_spec(spec_path):
    """spec.blueprint.rows → {no: {type, score}}；spec.sections 提供默认 kind 序。"""
    info = {}
    try:
        spec = _jload(spec_path)
    except Exception:
        return info
    for r in ((spec.get("blueprint") or {}).get("rows") or []):
        try:
            no = int(r.get("no"))
        except (TypeError, ValueError):
            continue
        info[no] = {"kind": r.get("type") or "", "score": r.get("score"),
                    "point": r.get("point") or "", "lib_point": r.get("lib_point") or "",
                    "level": r.get("level") or "", "module": r.get("module") or ""}
    return info


def _resolve_sid(token, sidmap, pool):
    t = str(token).strip()
    if t in pool:
        return t
    if t in sidmap:
        return sidmap[t]
    # 大小写/零填充容错：s3 → s03
    m = re.fullmatch(r"[sS](\d+)", t)
    if m:
        cand = "s%02d" % int(m.group(1))
        if cand in sidmap:
            return sidmap[cand]
    # 短前缀匹配完整 SID
    hits = [k for k in pool if k.startswith(t)] if len(t) >= 8 else []
    if len(hits) == 1:
        return hits[0]
    return ""


def cmd_assemble(args):
    sidmap = _jload(args.sidmap) if args.sidmap and os.path.exists(args.sidmap) else {}
    pool = {}
    for p in (args.pool or []):
        if os.path.exists(p):
            pool.update(_jload(p))
    ana = {}
    if args.analysis_pool and os.path.exists(args.analysis_pool):
        ana = _jload(args.analysis_pool)

    sel = _load_map(args.map)
    spec_info = _score_kind_from_spec(args.spec) if args.spec else {}
    meta = {}
    if args.meta and os.path.exists(args.meta):
        for it in _jload(args.meta):
            try:
                meta[int(it["no"])] = it
            except (KeyError, TypeError, ValueError):
                continue

    out, misses = [], []
    for no in sorted(sel):
        token = sel[no]
        sid = _resolve_sid(token, sidmap, pool)
        if not sid or sid not in pool:
            misses.append({"no": no, "token": token, "reason": "SID 未在原始池中找到"})
            continue
        src = pool[sid]
        an = ana.get(sid, {})
        m = meta.get(no, {})
        si = spec_info.get(no, {})

        q = {
            "no": no,
            "kind": m.get("kind") or si.get("kind") or _kind_of(src),
            "score": m.get("score", si.get("score", 0)) or 0,
            "stem": src.get("Content") or "",
            "opts": src.get("Options") or [],
            "answer": _answer_of(an or src, args.answer_style),
            # ⚠️ 【考点】只取教师侧命名（模型给 / 细目表 `point`），
            #    **绝不回退接口 `Points[].Value`**（题库内部考点名＝接口元数据字段值）。
            "points": m.get("points") or si.get("point") or "",
            # ⚠️ analyse/method 必须保留**原始 HTML**（含 MathJye 标记与 <br />）：
            #    下一步 build_questions / render_paper 依赖它们做公式线性化与分行。
            "analyse": (an.get("Analyse") or "").strip(),
            "method": (an.get("Method") or "").strip(),
            "afigs": [],
            # ⚠️ 不写 `sid`（题库内部 ID）与 `source`（题源标注）—— 均为接口元数据字段值，
            #    下游 build_questions/render_* 都不消费（且 build_questions 本就会剔除）。
            "difficulty": _degree_band(src.get("Degree")),
        }
        for k in ("bp", "lib", "cog", "module"):
            if m.get(k):
                q[k] = m[k]
        if si.get("point") and "bp" not in q:
            q["bp"] = si["point"]
        if si.get("lib_point") and "lib" not in q:
            q["lib"] = si["lib_point"]
        if si.get("level") and "cog" not in q:
            q["cog"] = si["level"]
        out.append(q)

    _jdump(out, args.out)
    print("[shrink] picks: %d 题 → %s" % (len(out), args.out))

    # —— 判重：先在「SID 仍在池中」时按 SID 判重（零成本、最可靠），
    #    再用题干哈希兜底（防不同 SID 但内容相同）。判重通过后写入 picks 时**不落 SID**
    #    （即"先保留 SID 判重，判重后再剥离"，与元数据红线一致）。
    sid_pos = {}
    for no in sorted(sel):
        _s = _resolve_sid(sel[no], sidmap, pool)
        if _s:
            sid_pos.setdefault(_s, []).append(no)
    sid_dups = {s: sorted(nos) for s, nos in sid_pos.items() if len(nos) > 1}

    stem_pos = {}
    for q in out:
        h = _stem_hash(q.get("stem"))
        if h:
            stem_pos.setdefault(h, []).append(q.get("no"))
    stem_dups = {h: sorted(nos) for h, nos in stem_pos.items() if len(nos) > 1}

    if sid_dups or stem_dups:
        for s, nos in sorted(sid_dups.items()):
            print("[shrink] ⚠️ 同一 SID 被多个题位选中：题位 %s" % (nos,), file=sys.stderr)
        for h, nos in sorted(stem_dups.items()):
            print("[shrink] ⚠️ 题干内容重复：题位 %s" % (nos,), file=sys.stderr)
        if not args.allow_dup:
            print("[shrink] ❌ 判重失败：请重新决策（每个题位选不同题），或加 --allow-dup 强制通过。",
                  file=sys.stderr)
            return 2
        print("[shrink] ⚠️ --allow-dup 已指定，判重告警被忽略（题位仍重复）。", file=sys.stderr)

    if misses:
        print("[shrink] ⚠️ 未装配 %d 个题位：" % len(misses), file=sys.stderr)
        for m in misses:
            print("   no=%s token=%s（%s）" % (m["no"], m["token"], m["reason"]), file=sys.stderr)
        return 1
    print("[shrink] OK")
    return 0


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="候选瘦身与 picks 自动装配")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("table", help="原始搜题返回 → 紧凑候选表 + sidmap + pool")
    p.add_argument("--in", dest="inputs", nargs="+", required=True)
    p.add_argument("--out-dir", default=".")
    p.add_argument("--prefix", default="cand")
    p.add_argument("--max-text", type=int, default=48)
    p.add_argument("--format", choices=["md", "tsv", "json"], default="md")
    p.set_defaults(func=cmd_table)

    p = sub.add_parser("pool", help="原始解析返回（可多个）→ analysis_pool.json")
    p.add_argument("--in", dest="inputs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_pool)

    p = sub.add_parser("assemble", help="「题位→短ID」+ 池 → picks JSON")
    p.add_argument("--map", required=True, help="形如 {\"1\":\"s03\"} 或 [{\"no\":1,\"sid\":\"s03\"}]")
    p.add_argument("--sidmap", default="")
    p.add_argument("--pool", nargs="+", default=[])
    p.add_argument("--analysis-pool", default="")
    p.add_argument("--spec", default="")
    p.add_argument("--meta", default="")
    p.add_argument("--answer-style", choices=["letter", "pretty", "none"], default="letter")
    p.add_argument("--allow-dup", action="store_true",
                   help="允许题位重复（默认对「重复 SID / 同题干」拦截并返回码 2）")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_assemble)

    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
