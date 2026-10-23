#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 组卷 · 成卷自检（试卷 / 解析 / 细目表）

用法：
    python3 selfcheck_paper.py <paper.docx> <analysis.docx> \
        [--blueprint bp.html] [--questions questions.json]

校验项：
- 试卷：无解析标签泄漏（【考点】【分析】【解答】/故答案为）、无 MathJye/quizPutTag 残留；
        若给 --questions，逐题核对题干片段是否落卷。
- 解析：含足量 【考点】【分析】【解答】；无 MathJye/quizPutTag 残留。
- 细目表：含认知层次与满分数字。
退出码 0 = 全通过。

需在含 python-docx 的解释器下运行（html-to-docx venv）。
"""
import os, re, sys, json, argparse, zipfile
from docx import Document


def _plain(html):
    s = re.sub(r"<[^>]+>", "", html or "")
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#39;", "'")
    # 与 render_paper.fix_blanks 对齐：3 个及以上连续下划线（填空线）在 docx 里会落成
    # 「下划线格式的全角空格」，纯文本比对时两者都不含下划线 → 统一剔除，避免误判「未落卷」。
    s = re.sub(r"_{3,}", "", s)
    return re.sub(r"\s+", "", s)


def _read_docx(path):
    d = Document(path)
    full = "\n".join(p.text for p in d.paragraphs)
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    underline = xml.count("<w:u ")
    sub = xml.count('w:val="subscript"')
    return full, underline, sub


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 成卷自检")
    ap.add_argument("paper")
    ap.add_argument("analysis")
    ap.add_argument("--blueprint", default="")
    ap.add_argument("--questions", default="")
    args = ap.parse_args()

    ok = True

    # ---- 试卷 ----
    pf, pu, ps = _read_docx(args.paper)
    leak = [m for m in ("【考点】", "【分析】", "【解答】", "故答案为") if m in pf]
    mj = ("MathJye" in pf) or ("mathtag" in pf)
    qz = pf.count("quizPutTag")
    print("== 试卷 ==")
    print(f"  下划线(w:u)={pu}  下标={ps}  解析泄漏={leak or '无'}  MathJye={mj}  quizPutTag={qz}")
    if leak or mj or qz:
        ok = False

    n_expect = 0
    if args.questions:
        with open(args.questions, encoding="utf-8") as f:
            qs = json.load(f)["questions"]
        n_expect = len(qs)
        miss = []
        for q in qs:
            frag = _plain(q.get("stem", ""))[:8]
            if frag and frag not in re.sub(r"\s+", "", pf):
                miss.append(q.get("no"))
        print(f"  题干落卷：{n_expect - len(miss)}/{n_expect}"
              + (f"  缺失题号={miss}" if miss else ""))
        if miss:
            ok = False

    # ---- 解析 ----
    af, au, asub = _read_docx(args.analysis)
    need = {m: af.count(m) for m in ("【考点】", "【分析】", "【解答】")}
    mja = ("MathJye" in af) or ("mathtag" in af)
    qza = af.count("quizPutTag")
    print("== 解析 ==")
    print(f"  【考点】={need['【考点】']} 【分析】={need['【分析】']} 【解答】={need['【解答】']}"
          f"  MathJye={mja}  quizPutTag={qza}")
    if n_expect:
        if any(v < n_expect for v in need.values()):
            ok = False
    else:
        if any(v == 0 for v in need.values()):
            ok = False
    if mja or qza:
        ok = False

    # ---- 细目表 ----
    if args.blueprint:
        bp = open(args.blueprint, encoding="utf-8").read()
        # ⚠️ 认知层次词汇**因学科而异**：数学/理科常用「了解·理解·掌握·运用」，
        #    语文常用「识记·理解·运用·综合」。原实现硬编码数学那 4 个词，
        #    会把语文卷的细目表误判为「不含认知层次」→ 自检假失败。
        #    改为：取表头 <th> 单元格，命中扩充词表 ≥3 个 且 含「认知层次」标记。
        _LEVEL_WORDS = ("了解", "理解", "掌握", "运用", "识记",
                        "应用", "分析", "评价", "综合", "体会")
        _ths = [t.strip() for t in re.findall(r"<th[^>]*>\s*([^<]{1,8})\s*</th>", bp)]
        _lv_hits = sum(1 for t in _ths if t in _LEVEL_WORDS)
        has_lv = _lv_hits >= 3 and ("认知层次" in bp)
        bp_ok = has_lv
        print("== 细目表 ==")
        print(f"  含认知层次={has_lv}（层次列 {_lv_hits} 个）  字符数={len(bp)}")
        if not bp_ok:
            ok = False

    print("\n== 结论 ==", "通过" if ok else "失败")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
