# -*- coding: utf-8 -*-
"""
md2docx.py — 把家长会发言稿 Markdown 转成可直接打印的 Word(.docx)

用法：
    python md2docx.py <输入.md> <输出.docx>

说明：
    - 解析本技能输出的 Markdown：# 标题、> 副标题、##/### 章节、
      表格、'- ' 列表、**加粗**、普通段落。
    - 中文字体统一设为「微软雅黑」，A4 页边距，时间分配表带边框。
    - 生成的 .docx 用 Word / WPS 双击即开，可直接改、直接打印。

⚠️ 运行环境若禁止脚本读取本地文件（沙箱限制）：
    把发言稿正文内联进本文件的 SRC_TEXT 常量（见文件末尾示例），
    再直接 `python md2docx.py` 即可，无需读取外部 .md。

依赖：python-docx  `pip install python-docx`
"""
import re
import sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

CJK = "Microsoft YaHei"  # 微软雅黑，WPS/Word 通用中文字体


def set_run_font(run, size=None, bold=None, italic=None, color=None):
    run.font.name = CJK
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = rpr.makeelement(qn('w:rFonts'), {})
        rpr.append(rfonts)
    rfonts.set(qn('w:eastAsia'), CJK)
    rfonts.set(qn('w:ascii'), CJK)
    rfonts.set(qn('w:hAnsi'), CJK)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_runs(par, text):
    parts = re.split(r'\*\*(.+?)\*\*', text)
    for i, seg in enumerate(parts):
        if seg == "":
            continue
        run = par.add_run(seg)
        set_run_font(run, bold=(i % 2 == 1))


def md_to_docx(text, dst):
    doc = Document()

    normal = doc.styles['Normal']
    normal.font.name = CJK
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), CJK)
    normal.element.rPr.rFonts.set(qn('w:ascii'), CJK)
    normal.element.rPr.rFonts.set(qn('w:hAnsi'), CJK)

    for s in doc.sections:
        s.top_margin = Cm(2.2)
        s.bottom_margin = Cm(2.2)
        s.left_margin = Cm(2.4)
        s.right_margin = Cm(2.4)

    lines = text.split('\n')
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            i += 1
            continue

        if stripped.startswith('# '):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped[2:].strip())
            set_run_font(run, size=20, bold=True)
            p.space_after = Pt(6)
            i += 1
            continue

        if stripped.startswith('> '):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(stripped[2:].strip())
            set_run_font(run, size=10.5, italic=True, color=RGBColor(0x60, 0x60, 0x60))
            p.space_after = Pt(10)
            i += 1
            continue

        if stripped.startswith('## '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[3:].strip())
            set_run_font(run, size=15, bold=True)
            run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
            p.space_before = Pt(10)
            p.space_after = Pt(4)
            i += 1
            continue

        if stripped.startswith('### '):
            p = doc.add_paragraph()
            run = p.add_run(stripped[4:].strip())
            set_run_font(run, size=13, bold=True)
            i += 1
            continue

        if stripped.startswith('|'):
            tbl_lines = []
            while i < n and lines[i].strip().startswith('|'):
                tbl_lines.append(lines[i].strip())
                i += 1
            rows = [[c.strip() for c in tl.strip('|').split('|')] for tl in tbl_lines]
            data_rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]
            if not data_rows:
                continue
            header, body = data_rows[0], data_rows[1:]
            table = doc.add_table(rows=1, cols=len(header))
            try:
                table.style = 'Table Grid'
            except Exception:
                pass
            hdr = table.rows[0].cells
            for j, h in enumerate(header):
                hdr[j].text = ""
                r = hdr[j].paragraphs[0].add_run(h)
                set_run_font(r, size=10.5, bold=True)
            for row in body:
                cells = table.add_row().cells
                for j, val in enumerate(row):
                    cells[j].text = ""
                    r = cells[j].paragraphs[0].add_run(val)
                    set_run_font(r, size=10.5)
            doc.add_paragraph().space_after = Pt(2)
            continue

        if stripped.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            add_runs(p, stripped[2:].strip())
            i += 1
            continue

        p = doc.add_paragraph()
        add_runs(p, stripped)
        p.paragraph_format.space_after = Pt(6)
        p.line_spacing = 1.25
        i += 1

    doc.save(dst)
    print("saved:", dst)


def main():
    if len(sys.argv) >= 3:
        src, dst = sys.argv[1], sys.argv[2]
        with open(src, encoding='utf-8') as f:
            text = f.read()
    else:
        # 沙箱/无参数兜底：用内联正文（把发言稿填进下方 SRC_TEXT）
        if SRC_TEXT is None:
            print("用法: python md2docx.py <输入.md> <输出.docx>")
            sys.exit(1)
        text = SRC_TEXT
        dst = sys.argv[1] if len(sys.argv) == 2 else "发言稿.docx"
    md_to_docx(text, dst)


# —— 沙箱兜底：若环境禁止读取本地文件，把发言稿 Markdown 全文贴到此处 ——
SRC_TEXT = None

if __name__ == '__main__':
    main()
