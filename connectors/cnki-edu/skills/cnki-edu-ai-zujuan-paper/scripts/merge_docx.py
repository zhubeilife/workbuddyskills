#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 组卷 · 分块 docx 缝合（N → 1，按传入顺序）

用于「分块渲染 → 分块转 docx → 缝合」的重叠并行链路：把若干块 docx
（如 block1/2/3 的试卷）按给定顺序拼成一份完整 docx。

依赖 `docxcompose`（已在 html-to-docx 转换 venv 内安装），它会正确处理
**题图关系（rels）**、样式与分节的合并——纯手工 XML 拼接会导致图片失效。

用法：
    python3 merge_docx.py --out 高中生物_试卷.docx block1_试卷.docx block2_试卷.docx block3_试卷.docx
    python3 merge_docx.py --out 高中生物_解析.docx --page-break block1_解析.docx block2_解析.docx

说明：
  - 只有 1 个输入时直接复制，不做拼接。
  - 默认不在块之间插分页（题号连续流动）；`--page-break` 可强制块间分页。
  - 请用 html-to-docx venv 的 Python 运行（内含 docxcompose）：见 merge_docx.sh。
"""
import os, sys, argparse, shutil


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 分块 docx 缝合")
    ap.add_argument("--out", required=True)
    ap.add_argument("--page-break", action="store_true", help="块与块之间插入分页")
    ap.add_argument("docs", nargs="+", help="按顺序排列的块 docx")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)

    if len(args.docs) == 1:
        shutil.copyfile(args.docs[0], args.out)
        print(f"[merge_docx] 单块直接复制 → {args.out}")
        return

    try:
        from docx import Document
        from docxcompose.composer import Composer
    except ImportError as e:  # noqa: BLE001
        sys.exit(f"[merge_docx] 缺少 docxcompose（请用 html-to-docx venv 运行，"
                 f"或 `pip install docxcompose`）：{e}")

    from docx.enum.text import WD_BREAK  # noqa: E402

    master = Document(args.docs[0])
    if args.page_break:
        master.add_page_break()
    composer = Composer(master)
    for p in args.docs[1:]:
        sub = Document(p)
        composer.append(sub)
        if args.page_break:
            composer.doc.add_page_break()

    composer.save(args.out)
    print(f"[merge_docx] 缝合 {len(args.docs)} 块 → {args.out}")


if __name__ == "__main__":
    main()
