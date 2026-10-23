#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 组卷 · 幂等合并 + 缺口计算（断点续跑的核心）

把「已有的合并文件」与「新拉到的分块文件」幂等合并：
  - 按题号去重，**同题号取更完整者，绝不把已成功的好题覆盖成差题**；
  - 输出统一的**顶层数组**合并文件（`picks_merged.json`）；
  - 计算并打印 **missing（缺口题号）**，供编排层「只补缺口」。

这是「失败只补坏题、成功永不丢失」的落点：无论哪一块失败/中断，
已落盘的好题都在，续跑只需针对 missing 题号。

用法：
    # 首次合并三块
    python3 merge_and_gap.py --spec spec.json --out picks_merged.json picks_1.json picks_2.json picks_3.json
    # 续跑：在已有合并文件基础上追加新拉的补题块
    python3 merge_and_gap.py --spec spec.json --existing picks_merged.json --out picks_merged.json picks_gap.json

退出码：0 = 已无缺口（可进 build）；1 = 仍有 missing（继续补）。
"""
import os, sys, json, argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from validate_picks import collect, expected_nos_from_spec, validate  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 幂等合并 + 缺口计算")
    ap.add_argument("--out", required=True, help="合并后写入的 picks JSON（顶层数组）")
    ap.add_argument("--existing", default=None, help="已有合并文件（续跑时传入，会被合并进来）")
    ap.add_argument("--spec", default=None)
    ap.add_argument("--expect", type=int, default=None)
    ap.add_argument("--json-out", default=None, help="机器可读汇总输出路径")
    ap.add_argument("--keep-meta", action="store_true",
                    help="输出现有文件的 status/note 等元字段（默认只输出纯数组）")
    ap.add_argument("picks", nargs="*", help="新拉到的分块 picks（可多个）")
    args = ap.parse_args()

    spec = json.load(open(args.spec, encoding="utf-8")) if args.spec else None

    files = list(args.picks)
    if args.existing:
        # 首次合并时 existing 尚不存在属正常情况，不应记为 failed（否则输出噪音、
        # 且会误导编排层以为文件损坏）。真·缺失的只有 args.picks 里的文件。
        if os.path.exists(args.existing):
            files.insert(0, args.existing)
        else:
            sys.stderr.write(f"[merge_and_gap] （existing {args.existing} 尚不存在，按首次合并处理）\n")

    q_by_no, dup, partial_files, failed = collect(files)

    expected = expected_nos_from_spec(spec)
    if expected is None and args.expect:
        expected = list(range(1, args.expect + 1))
    if expected is None:
        expected = list(range(1, (max(q_by_no) if q_by_no else 0) + 1))

    present, missing, extra, invalid, content_dup = validate(q_by_no, expected, spec)

    # 输出：按题号排序的顶层数组（统一 picks 结构，消灭 A/B/C 三形态并存）
    ordered = [q_by_no[no] for no in present]
    status = "COMPLETE" if (not missing and not extra and not invalid) else "PARTIAL_CHECKPOINT"
    if args.keep_meta:
        payload = {
            "status": status,
            "missing_slots": missing,
            "questions": ordered,
        }
    else:
        payload = ordered
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    summary = {
        "status": status,
        "out": args.out,
        "merged_count": len(ordered),
        "expected_count": len(expected),
        "missing": missing,
        "extra": extra,
        "duplicates": sorted(set(dup)),
        "invalid": invalid,
        "content_duplicates": content_dup,
        "partial_files": partial_files,
        "failed_files": failed,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)

    sys.stderr.write(
        f"[merge_and_gap] 合并 {len(ordered)} 题 → {args.out}; "
        f"missing={missing or '无'}; {'可进 build' if status == 'COMPLETE' else '需继续补 missing'}\n"
    )
    sys.exit(0 if status == "COMPLETE" else 1)


if __name__ == "__main__":
    main()
