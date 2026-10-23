#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 组卷 · 通用组装器（picks → questions.json + blueprint.json）

把选题产物（一个或多个 picks JSON / 分块文件 / 合并文件）合并、MathJye 线性化、
题号重排、**缺口校验**，并按 spec 生成「试卷数据 questions.json」与「双向细目表
blueprint.json」。

关键增强（v2.1）：
  - **缺口不静默**：题号不连续时，打印缺失题号清单并退出码 1（提示走 merge_and_gap
    续跑），而不是笼统 assert 失败。
  - **分块导出**：`--split-blocks "1-9,10-18,19-25"` 额外产出每块的 questions 文件，
    供「分块渲染 → 分块转 docx → merge_docx 缝合」的重叠并行链路使用。

用法：
    python3 build_questions.py --spec spec.json --picks picks_merged.json [--out-dir .]
    python3 build_questions.py --spec spec.json --picks picks_merged.json \
        --split-blocks "1-9,10-18,19-25"

spec.json 结构（最小）：
{
  "title": "……测试卷",
  "meta": "满分：100 分　　考试时间：90 分钟",
  "exam_info": true,
  "sections": [{"kind":"选择","title":"一、选择题（……）"}, ...],
  "blueprint": {
     "levels": ["了解","理解","掌握","运用"],
     "rows": [{"no":1,"type":"选择","score":2,"module":"…","point":"…",
               "lib_point":"…","level":"了解","difficulty":"易"}, ...]
  }
}

picks 文件形态（自动识别）：顶层数组 / {"picks":[…]} / {"questions":[…]} / {"data":[…]}。
每题字段：no, score, kind, stem, opts, figs, points, analyse, method, answer, afigs。

零侵入：仅 `from render_paper import normalize_math` 复用 MathJye 线性化，不改 skill 业务文件。
"""
import os, sys, json, argparse
from collections import OrderedDict

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from render_paper import normalize_math  # noqa: E402
from validate_picks import collect, expected_nos_from_spec, validate  # noqa: E402

LEVELS_DEFAULT = ["了解", "理解", "掌握", "运用"]
KIND_ORDER = ["选择", "填空", "多选", "判断", "解答"]


def _norm_text(s):
    return normalize_math(s) if isinstance(s, str) and s else s


def _load_picks(paths):
    """兼容多形态 picks（数组 / picks / questions / data），返回扁平题目列表。"""
    out = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict):
            d = d.get("picks") or d.get("questions") or d.get("data") or []
        out.extend(d)
    return out


def _normalize_questions(raw):
    qs = []
    for q in raw:
        q2 = dict(q)
        q2["stem"] = _norm_text(q.get("stem", ""))
        q2["opts"] = [_norm_text(o) for o in q.get("opts", [])]
        q2["analyse"] = _norm_text(q.get("analyse", ""))
        q2["method"] = _norm_text(q.get("method", ""))
        q2["answer"] = _norm_text(q.get("answer", ""))
        if q2.get("answer") in ("见试题解答内容", "见解析"):
            q2["answer"] = ""  # 答案已嵌于 method
        if q2.get("points"):
            q2["points"] = q2["points"].replace(";", "；")
        q2.setdefault("figs", [])
        q2.setdefault("afigs", [])
        for k in ("sid", "label", "SID", "Label"):
            q2.pop(k, None)
        qs.append(q2)
    qs.sort(key=lambda x: x["no"])
    return qs


def _derive_sections(qs):
    kinds = []
    for q in qs:
        if q.get("kind") not in kinds:
            kinds.append(q.get("kind"))
    kinds.sort(key=lambda k: KIND_ORDER.index(k) if k in KIND_ORDER else 99)
    return [{"kind": k, "title": f"（未提供分节标题，kind={k}）"} for k in kinds]


def _section_title_map(spec):
    m = {}
    for s in (spec.get("sections") or []):
        if s.get("kind"):
            m[s["kind"]] = s.get("title", "")
    return m


def _sections_for_range(qs, lo, hi, title_map, fallback):
    """给定块内题号区间，返回该块的 sections。
    ⚠️ 关键：**只要本块含某题型的题，就必须把该 kind 列入 sections**——否则
    render_paper 按 sections 的 kind 过滤渲染，会**整块丢失该题型**（题型首题在
    上一块时最易踩坑）。标题仅在该 kind 首题落于本块时打印；否则 title 置空
    （仍参与渲染，但 render_paper 会跳过空标题，避免缝合后重复分节标题）。"""
    first_no = {}
    for q in qs:
        k = q.get("kind")
        if k not in first_no:
            first_no[k] = q["no"]
    secs = []
    kinds_in_block = [k for k in KIND_ORDER if any(q.get("kind") == k and lo <= q["no"] <= hi for q in qs)]
    for k in kinds_in_block:
        show_title = first_no.get(k) is not None and lo <= first_no[k] <= hi
        title = (title_map.get(k) or fallback.get(k, f"（{k}）")) if show_title else ""
        secs.append({"kind": k, "title": title})
    return secs


def _build_blueprint(bp_spec, title):
    rows = bp_spec.get("rows", [])
    levels = bp_spec.get("levels", LEVELS_DEFAULT)
    modules = OrderedDict()
    for r in rows:
        modules.setdefault(r.get("module", "——"), []).append(r)
    mod_list = []
    for mod, rs in modules.items():
        pts = [{"name": r.get("point", ""), "lib": r.get("lib_point", ""),
                "scores": {r.get("level", levels[0]): r.get("score", 0)}} for r in rs]
        mod_list.append({"name": mod, "points": pts})
    per_q = [{"no": r["no"], "type": r.get("type", ""), "score": r.get("score", 0),
              "module": r.get("module", ""), "point": r.get("point", ""),
              "lib_point": r.get("lib_point", ""), "level": r.get("level", ""),
              "difficulty": r.get("difficulty", "")} for r in rows]
    lv_total = {l: 0 for l in levels}
    for r in rows:
        if r.get("level") in lv_total:
            lv_total[r["level"]] += r.get("score", 0)
    return {
        "title": bp_spec.get("title", title),
        "meta": bp_spec.get("meta") or "满分：%d 分 | 认知层次 %s" % (
            sum(lv_total.values()), "∶".join(f"{l}{lv_total[l]}" for l in levels)),
        "levels": levels,
        "modules": mod_list,
        "per_question": per_q,
        "note": bp_spec.get("note", ""),
    }, lv_total


def _parse_blocks(s):
    """'1-9,10-18,19-25' → [(1,9),(10,18),(19,25)]"""
    out = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.append((int(a), int(b)))
        else:
            out.append((int(part), int(part)))
    return out


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 通用组装器")
    ap.add_argument("--spec", required=True, help="spec JSON（title/sections/blueprint）")
    ap.add_argument("--picks", nargs="*", default=[], help="picks JSON 文件（可多个/分块）")
    ap.add_argument("--out-dir", default=".", help="输出目录（默认当前目录）")
    ap.add_argument("--questions-name", default="questions.json")
    ap.add_argument("--blueprint-name", default="blueprint.json")
    ap.add_argument("--split-blocks", default=None,
                    help='额外导出分块 questions，如 "1-9,10-18,19-25"（供重叠并行转档）')
    ap.add_argument("--partial", action="store_true",
                    help="缺题时也照常生成（默认缺题即报错退出）")
    ap.add_argument("--strict", action="store_true",
                    help="题目分值合计 != spec.total_score 时报错（默认只告警）")
    args = ap.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)

    picks = args.picks or spec.get("picks", [])
    raw = _load_picks(picks)
    qs = _normalize_questions(raw)

    # —— 缺口校验（不再静默 assert）——
    expected = expected_nos_from_spec(spec) or list(range(1, len(qs) + 1))
    q_by_no, _, _, _ = collect(picks)
    present, missing, extra, invalid, content_dup = validate(q_by_no, expected, spec)
    if missing or extra or invalid:
        sys.stderr.write(f"[build] ⚠️ 选题不完整：missing={missing or '无'} extra={extra or '无'} invalid={len(invalid)} 项\n")
        for it in invalid:
            sys.stderr.write(f"        - 题{it['no']}: {', '.join(it['errors'])}\n")
        if not args.partial:
            sys.stderr.write("[build] 已中止。请先跑 `merge_and_gap.py` 补齐 missing 题号（幂等续跑），"
                             "或加 --partial 强制生成残卷。\n")
            raise SystemExit(1)

    sections = spec.get("sections") or _derive_sections(qs)
    cfg = {
        "title": spec["title"],
        "meta": spec.get("meta", ""),
        "exam_info": spec.get("exam_info", True),
        "sections": sections,
        "questions": qs,
    }
    os.makedirs(args.out_dir, exist_ok=True)
    q_path = os.path.join(args.out_dir, args.questions_name)
    with open(q_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=1)
    total = sum(q["score"] for q in qs)
    print(f"[build] {q_path}  已生成：{len(qs)} 题，合计 {total} 分")

    # —— 分块导出（供「分块渲染 → 分块转 docx → 缝合」重叠并行）——
    if args.split_blocks:
        title_map = _section_title_map(spec)
        fallback = {s["kind"]: s.get("title", "") for s in sections}
        base = args.questions_name[:-5] if args.questions_name.endswith(".json") else args.questions_name
        for i, (lo, hi) in enumerate(_parse_blocks(args.split_blocks), 1):
            sub = [q for q in qs if lo <= q["no"] <= hi]
            if not sub:
                continue
            sub_cfg = {
                "title": spec["title"],
                "meta": spec.get("meta", ""),
                "exam_info": (i == 1),        # 卷头（学校/班级…）只在首块
                "omit_header": (i != 1),      # 非首块不再重复标题/卷头（缝合时用）
                "sections": _sections_for_range(qs, lo, hi, title_map, fallback),
                "questions": sub,
                "global_offset": lo - 1,
            }
            bp = os.path.join(args.out_dir, f"{base}_block{i}.json")
            with open(bp, "w", encoding="utf-8") as f:
                json.dump(sub_cfg, f, ensure_ascii=False, indent=1)
            print(f"[build] {bp}  分块 {i}：题 {lo}-{hi}（{len(sub)} 题）")

    if spec.get("total_score") and total != spec["total_score"]:
        msg = f"[build] ⚠️ 分值合计 {total} != spec.total_score {spec['total_score']}"
        if args.strict:
            raise SystemExit(msg)
        print(msg)

    bp_spec = spec.get("blueprint")
    if bp_spec and bp_spec.get("rows"):
        bp, lv = _build_blueprint(bp_spec, spec["title"])
        b_path = os.path.join(args.out_dir, args.blueprint_name)
        with open(b_path, "w", encoding="utf-8") as f:
            json.dump(bp, f, ensure_ascii=False, indent=1)
        dist = " ".join(f"{k}{v}" for k, v in lv.items())
        print(f"[build] {b_path}  已生成：{len(bp['modules'])} 模块 / "
              f"{len(bp['per_question'])} 题对照；认知层次 {dist}")


if __name__ == "__main__":
    main()
