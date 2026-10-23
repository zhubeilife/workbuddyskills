# -*- coding: utf-8 -*-
"""把 CNKI 基础教育题库的官方解析回填进作业单 items.json。

用途：作业设计八步流程里，retrieve（题库真题）档默认只留「回查原卷」占位。
本题库搜题接口不返回解析，必须用 tkQuestionAnalysis 按 SID 单独回查。
本脚本把回查到的官方答案/解析/考点清洗后写回 retrieve 档的 answer/analysis/points，
题面（stem/source_id）一字不动。

典型用法（LLM 主流程）：
  1) 对话里逐题调 mcp__<SERVER>__tkQuestionAnalysis(SID=..., subjectCode=NN)，把返回的 data 存成 raw_analysis.json
  2) python scripts/fill_analysis.py --items items.json --analysis raw_analysis.json --out items.json
     （不传 --out 则原地覆盖 items.json）

也可复用 mcp_adapters 已标准化的 analysis.json：
  python scripts/fill_analysis.py --items items.json --analysis analysis.json

匹配规则：只回填 origin=="retrieve" 且 source_id 能命中解析 SID 的题；
匹配不到的 retrieve 题保留原题答案（若已有）并留「回查原卷」占位，绝不编造解析。
依赖：纯标准库 + 同目录 mcp_adapters（复用 strip_html / normalize_analysis / fill_item_with_analysis）。
"""
import json
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcp_adapters as ma  # noqa: E402


PLACEHOLDER = "（官方解析待回查：请在题库/原卷核对答案与解析后再行布置）"


def main():
    ap = argparse.ArgumentParser(description="官方解析回填：tkQuestionAnalysis 结果 -> items.json 的 retrieve 档")
    ap.add_argument("--items", required=True, help="作业单 items.json（含 meta + items）")
    ap.add_argument("--analysis", required=True, help="tkQuestionAnalysis 原始返回/标准化结果 JSON")
    ap.add_argument("--out", default="", help="输出路径，默认原地覆盖 --items")
    ap.add_argument("--subject-code", default="", help="学科码（仅用于日志提示）")
    ap.add_argument("--no-fallback", action="store_true",
                    help="匹配不到解析的 retrieve 题不留占位提示（默认留占位）")
    args = ap.parse_args()

    if not os.path.exists(args.items):
        print("items 文件不存在：%s" % args.items, file=sys.stderr)
        sys.exit(2)
    if not os.path.exists(args.analysis):
        print("analysis 文件不存在：%s" % args.analysis, file=sys.stderr)
        sys.exit(2)

    data = json.load(open(args.items, encoding="utf-8"))
    items = data.get("items") or []
    norm = ma.load_analysis_any(args.analysis)
    by_sid = {}
    for a in norm:
        sid = (a.get("sid") or "").strip()
        if sid and (a.get("body") or a.get("answer")):
            by_sid[sid] = a

    filled = 0
    skipped = 0
    for it in items:
        if it.get("origin") != "retrieve":
            continue
        sid = (it.get("source_id") or "").strip()
        a = by_sid.get(sid)
        if a and ma.fill_item_with_analysis(it, a):
            filled += 1
            continue
        # 未命中：保留已有答案，解析留占位（除非 --no-fallback）
        if not args.no_fallback and not (it.get("analysis") or "").strip():
            it["analysis"] = PLACEHOLDER
        skipped += 1

    out = args.out or args.items
    json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    sc = ("（subjectCode=%s）" % args.subject_code) if args.subject_code else ""
    print("官方解析回填完成 -> %s" % out)
    print("  回填 %d 题｜未命中/留占位 %d 题（解析档共 %d 条，去重命中 %d SID）"
          % (filled, skipped, len(norm), len(by_sid)))


if __name__ == "__main__":
    main()
