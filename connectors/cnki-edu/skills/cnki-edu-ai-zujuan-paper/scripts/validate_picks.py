#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 组卷 · 选题校验器（题号连续性 + 每题完整性 + 识别 PARTIAL + 计算缺口）

用途：一次组卷会由多个「分块 picks 文件」产出（每块可能因上下文压缩/中断而残缺）。
在 build 之前，必须先跑本脚本，确认：
  ① 所有文件 JSON 可解析；
  ② 题号相对 expected 集合**连续无缺**（missing 为空）；
  ③ 每题含必要字段（no/kind/score/stem）且 analyse/method 至少其一非空；
  ④ 每题 kind/score 与 spec 一致（若给了 spec）；
  ⑤ 识别 `status != COMPLETE` 的残卷文件（如 PARTIAL_CHECKPOINT）；
  ⑥ **题干判重**：用「题干 + 选项」归一化哈希，找出占了多个题位的**同一道题**。若存在缺口 → **不进入 build**，转为「只补 missing 题号」的续跑（见 merge_and_gap.py）。

用法：
    python3 validate_picks.py --spec spec.json picks_1.json picks_2.json ...
    python3 validate_picks.py --expect 25 picks_*.json
    python3 validate_picks.py --spec spec.json --json-out gap.json picks_*.json
    python3 validate_picks.py --quiet --spec spec.json --json-out gap.json picks_*.json   # 只回摘要+出错项

退出码：0 = COMPLETE（可进 build）；1 = PARTIAL（有缺口/无效题，需续跑）。
本脚本**只读** picks，不修改任何文件（除 --json-out 外）。
"""
import os, sys, json, re, argparse, hashlib

REQUIRED = ["no", "kind", "score", "stem"]

# 题型归一：把「选择题 / 选择 / 多选 / 多选题 / 解答题 / 解答 …」映射到同一口径
_KIND_ALIAS = {
    "选择": "选择", "选择题": "选择", "单选": "选择", "单选题": "选择",
    "多选": "多选", "多选题": "多选", "多项选择": "多选",
    "填空": "填空", "填空题": "填空",
    "判断": "判断", "判断题": "判断",
    "解答": "解答", "解答题": "解答", "计算": "解答", "计算题": "解答",
    "实验": "实验", "实验题": "实验",
}


def _norm_kind(k):
    if not isinstance(k, str):
        return ""
    k = k.strip()
    return _KIND_ALIAS.get(k, k)


def _stem_key(q):
    """题干判重键：picks 已剥离 SID → 用「题干 + 选项」归一化后的哈希兜底。

    归一化：去标签、去空白、还原常见实体；**过短（<30 字）不参与**（防「阅读下列材料」类
    通用短题干误报）。仅用于判重，不落盘、不外显。
    """
    s = q.get("stem") or ""
    if not isinstance(s, str):
        s = str(s)
    o = q.get("opts") or []
    otxt = "|".join(str(x) for x in o) if isinstance(o, list) else str(o)
    raw = s + "||" + otxt
    raw = re.sub(r"<[^>]+>", "", raw)
    raw = re.sub(r"\s+", "", raw)
    raw = (raw.replace("&nbsp;", "").replace("&amp;", "&")
              .replace("&lt;", "<").replace("&gt;", ">"))
    if len(raw) < 30:
        return None
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _completeness(q):
    """给一道题打完整性分，用于多来源同题号时择优选留。"""
    if not isinstance(q, dict):
        return -1
    s = 0
    if q.get("stem"):
        s += min(len(str(q["stem"])) // 50, 20)
    if q.get("opts"):
        s += 3
    if q.get("analyse"):
        s += min(len(str(q["analyse"])) // 50, 20)
    if q.get("method"):
        s += min(len(str(q["method"])) // 50, 20)
    if q.get("answer"):
        s += 1
    if q.get("points"):
        s += 1
    return s


def load_any(path):
    """返回 (questions_list, status_or_None, raw_top_type)。兼容 数组 / {picks|questions|data}。"""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    status = None
    if isinstance(d, dict):
        status = d.get("status")
        d = d.get("picks") or d.get("questions") or d.get("data") or []
    if not isinstance(d, list):
        d = []
    return d, status


def expected_nos_from_spec(spec):
    if not spec:
        return None
    bp = spec.get("blueprint") or {}
    rows = bp.get("rows") or []
    if rows:
        return sorted({r["no"] for r in rows if isinstance(r, dict) and "no" in r})
    if spec.get("total_questions"):
        return list(range(1, int(spec["total_questions"]) + 1))
    return None


def spec_meta(spec):
    bp = (spec or {}).get("blueprint") or {}
    return {r["no"]: r for r in (bp.get("rows") or []) if isinstance(r, dict) and "no" in r}


def collect(paths):
    """合并多个 picks 文件；同题号取更完整者；记录残卷与解析失败文件。"""
    q_by_no, dup, partial_files, failed = {}, [], [], []
    for p in paths:
        try:
            arr, status = load_any(p)
        except Exception as e:  # noqa: BLE001
            failed.append({"file": p, "error": str(e)})
            continue
        if status and str(status).upper() != "COMPLETE":
            partial_files.append({"file": p, "status": status})
        for q in arr:
            if not isinstance(q, dict):
                continue
            no = q.get("no")
            if no is None:
                continue
            if no in q_by_no:
                dup.append(no)
                if _completeness(q) > _completeness(q_by_no[no]):
                    q_by_no[no] = q
            else:
                q_by_no[no] = q
    return q_by_no, dup, partial_files, failed


def validate(q_by_no, expected, spec):
    meta = spec_meta(spec)
    present = sorted(q_by_no)
    missing = sorted(set(expected) - set(present))
    extra = sorted(set(present) - set(expected))
    invalid = []
    for no in present:
        q = q_by_no[no]
        errs = [f"缺 {f}" for f in REQUIRED if q.get(f) in (None, "", [])]
        if not (q.get("analyse") or q.get("method")):
            errs.append("analyse/method 全空")
        if no in meta:
            m = meta[no]
            wt = m.get("type")
            if wt and q.get("kind") and _norm_kind(q["kind"]) != _norm_kind(wt):
                errs.append(f"kind='{q['kind']}' != spec.type='{wt}'")
            ws = m.get("score")
            if ws is not None and q.get("score") not in (ws, 0, None):
                errs.append(f"score={q.get('score')} != spec.score={ws}")
        if errs:
            invalid.append({"no": no, "errors": errs})
    # 题干判重：picks 已无 SID → 用「题干 + 选项」哈希兜底，防「不同 SID 同题」漏网
    buckets = {}
    for no in present:
        key = _stem_key(q_by_no[no])
        if key:
            buckets.setdefault(key, []).append(no)
    content_dup = sorted([sorted(nos) for nos in buckets.values() if len(nos) > 1])
    return present, missing, extra, invalid, content_dup


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 选题校验器")
    ap.add_argument("picks", nargs="+", help="picks JSON（可多个分块文件）")
    ap.add_argument("--spec", default=None, help="spec JSON（含 blueprint.rows → 精确期望题集）")
    ap.add_argument("--expect", type=int, default=None, help="无 spec 时用 1..N 作期望")
    ap.add_argument("--json-out", default=None, help="把机器可读汇总写到该文件")
    ap.add_argument("--quiet", action="store_true",
                    help="只回「1 行摘要 + 出错项」到 stdout（全量 JSON 不再打印；建议配合 --json-out 落盘）")
    args = ap.parse_args()

    spec = json.load(open(args.spec, encoding="utf-8")) if args.spec else None
    q_by_no, dup, partial_files, failed = collect(args.picks)

    expected = expected_nos_from_spec(spec)
    if expected is None and args.expect:
        expected = list(range(1, args.expect + 1))
    if expected is None:
        expected = list(range(1, (max(q_by_no) if q_by_no else 0) + 1))

    present, missing, extra, invalid, content_dup = validate(q_by_no, expected, spec)
    status = "COMPLETE" if (not missing and not extra and not invalid
                            and not content_dup and not failed) else "PARTIAL"

    summary = {
        "status": status,
        "expected_count": len(expected),
        "present_count": len(present),
        "missing": missing,
        "extra": extra,
        "duplicates": sorted(set(dup)),
        "content_duplicates": content_dup,
        "invalid": invalid,
        "partial_files": partial_files,
        "failed_files": failed,
        "present": present,
    }
    if args.quiet:
        # 只回「摘要 + 出错项」——避免整包 JSON（含 present 全量列表）灌进模型上下文
        print(f"[validate] {status}: present {len(present)}/{len(expected)}; "
              f"missing={missing or '无'}; invalid={len(invalid)}; "
              f"题干重复={content_dup or '无'}; "
              f"残卷={len(partial_files)}; 失败文件={len(failed)}")
        for grp in content_dup:
            print(f"  ! 题干重复：题号 {grp}（同一道题占了多个题位）")
        for it in invalid[:20]:
            print(f"  ! no={it['no']}: {'; '.join(it['errors'])}")
        for it in failed:
            print(f"  ! 读取失败 {it['file']}: {it['error']}")
        for it in partial_files:
            print(f"  ~ PARTIAL {it['file']} (status={it['status']})")
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=1))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
    if not args.quiet:
        hint = "→ 可进 build" if status == "COMPLETE" else "→ 需续跑：只补 missing 题号（见 merge_and_gap.py）"
        sys.stderr.write(
            f"[validate] {status}: present {len(present)}/{len(expected)}; "
            f"missing={missing or '无'}; invalid={len(invalid)}; 残卷文件={len(partial_files)} {hint}\n"
        )
    sys.exit(0 if status == "COMPLETE" else 1)


if __name__ == "__main__":
    main()
