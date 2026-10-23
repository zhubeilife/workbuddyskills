#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cnki-edu-daily-comm-scripts docx 结构校验器 —— 生成 .docx 后必跑。

五项校验：
  A. XML 可解析（minidom）
  B. 标签平衡（栈式扫描，跳过自闭合）
  C. 表格专项：tblW == Σ首行tcW / 有 tblBorders / tblStyle 必须在 styles.xml 中定义 / tblPr 成对闭合
  D. 内部块零残留：文档里不得出现「回复专用」的元信息块（【沟通要素】头等）
  E. 标题零写作说明：PPT 页标题等处不得挂写作说明括注（如「数据怎么看（三个口径）」；序号类「（一）」放行）

用法:
  python check_docx.py <文件.docx> [更多.docx ...]

输出: 每份文件一行结论；退出码 0=全部通过, 1=有问题, 2=用法错误
"""
import os
import re
import sys
import zipfile
import xml.dom.minidom as md


BORDER_COLORS = ("B4B2A9", "D3D1C7", "808080", "auto", "000000")

# D 项：只该出现在「聊天回复」里、不得进入交付文件的内部块标记。
# 注意：【待补信息】【0 时间分配总览】是**白名单内**的交付内容，故意不列入。
INTERNAL_BLOCK_MARKERS = (
    "【沟通要素】", "【用户身份】", "【沟通对象】", "【沟通方式", "【本次目的】",
    "【任务形态】", "【场景判定】", "【策略】",
    "【红线自检】", "【政策来源核对】", "【质量自检】", "【自检摘要】",
)


def doc_text(doc):
    """抽取 document.xml 的全部可见文字（含表格单元格）。"""
    return "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", doc, re.S))


def para_texts(doc):
    """逐段抽取文本（用于按行判断标题）。"""
    out = []
    for pa in re.findall(r"<w:p[ >].*?</w:p>", doc, re.S):
        out.append("".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", pa, re.S)))
    return out


# E 项：PPT 页标题行（形如「第 7 页｜标题」）
PPT_TITLE_RE = re.compile(r"^第\s*[0-9]+\s*页\s*[｜|]\s*(.+?)\s*$")
# 括号内容若是纯序号（一 / 二 / 12 …）则属页序，放行
SERIAL_ONLY_RE = re.compile(r"^[一二三四五六七八九十百0-9]+$")
BRACKET_RE = re.compile(r"[（(]([^（()）]{1,16})[)）]")


def struct_ok(doc):
    """栈式标签平衡扫描"""
    tokens = re.findall(r"<(/?)(\w[\w:.\-]*)([^>]*?)(/?)>", doc)
    stack = []
    for close, tag, attrs, selfclose in tokens:
        if selfclose == "/":
            continue
        if close == "/":
            if not stack or stack[-1] != tag:
                return False, "期望 </%s>，实际 </%s>" % (stack[-1] if stack else "?", tag)
            stack.pop()
        else:
            stack.append(tag)
    if stack:
        return False, "未闭合标签: %s" % stack
    return True, ""


def check_docx(path):
    problems = []
    notes = []

    try:
        z = zipfile.ZipFile(path)
    except Exception as e:
        return ["无法打开 zip: %s" % e], []

    if z.testzip() is not None:
        problems.append("zip 内容损坏: %s" % z.testzip())

    for need in ("word/document.xml", "word/styles.xml", "[Content_Types].xml"):
        if need not in z.namelist():
            problems.append("缺少部件: %s" % need)
    if problems:
        return problems, notes

    doc = z.read("word/document.xml").decode("utf-8")
    styles = z.read("word/styles.xml").decode("utf-8")

    # A. XML 可解析
    try:
        md.parseString(doc.encode("utf-8"))
    except Exception as e:
        problems.append("XML 解析失败: %s" % e)

    # B. 标签平衡
    ok, msg = struct_ok(doc)
    if not ok:
        problems.append("标签不平衡: %s" % msg)

    # C. 表格专项
    defined = set(re.findall(r'w:styleId="([^"]+)"', styles))
    tables = re.findall(r"<w:tbl>.*?</w:tbl>", doc, re.S)
    for i, t in enumerate(tables, 1):
        # tblPr 成对
        o = len(re.findall(r"<w:tblPr[ >]", t))
        c = len(re.findall(r"</w:tblPr>", t))
        if o != c:
            problems.append("表%d: <w:tblPr> 未闭合 (%d 开 / %d 闭)" % (i, o, c))

        # tblStyle 有效性
        for ref in set(re.findall(r'<w:tblStyle w:val="([^"]+)"/>', t)):
            if ref not in defined:
                problems.append("表%d: 引用了 styles.xml 中不存在的 tblStyle '%s'" % (i, ref))

        # tblBorders
        if "tblBorders" not in t:
            problems.append("表%d: 缺少 tblBorders（无边框线）" % i)

        # tblW == Σ首行 tcW
        m = re.search(r'<w:tblW w:w="(\d+)"', t)
        rows = re.findall(r"<w:tr>.*?</w:tr>", t, re.S)
        if m and rows:
            w_tbl = int(m.group(1))
            w_cells = sum(int(v) for v in re.findall(r'<w:tcW w:w="(\d+)"', rows[0]))
            if w_tbl != w_cells:
                problems.append("表%d: tblW=%d 但首行格宽和=%d（表宽与列宽不符）" % (i, w_tbl, w_cells))

    if tables:
        notes.append("共 %d 个表格" % len(tables))

    # D. 内部块零残留（回复专用块不得写进交付文件）
    text = doc_text(doc)
    hits = [m for m in INTERNAL_BLOCK_MARKERS if m in text]
    if hits:
        problems.append(
            "残留内部块（属回复专用，不得进交付文件）: %s"
            " —— 整块删除后另存，勿只删其中几行" % "、".join(hits)
        )

    # E. 标题不得挂写作说明括注（PPT 页标题等）
    for t in para_texts(doc):
        m = PPT_TITLE_RE.match(t)
        if not m:
            continue
        for g in BRACKET_RE.findall(m.group(1)):
            if SERIAL_ONLY_RE.match(g.strip()):
                continue  # 「班里的事（一）」属页序，放行
            problems.append(
                "页标题带写作说明括注: 「%s」中的「（%s）」—— 标题只写标题本身，"
                "正文已列出条数，无需再标注；序号类（一）（二）可留" % (t.strip(), g)
            )

    return problems, notes


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    any_bad = False
    for p in sys.argv[1:]:
        if not os.path.isfile(p):
            print("[跳过] 文件不存在: %s" % p)
            any_bad = True
            continue
        problems, notes = check_docx(p)
        name = os.path.basename(p)
        if problems:
            any_bad = True
            print("[不通过] %s" % name)
            for x in problems:
                print("        - %s" % x)
        else:
            extra = ("  (%s)" % "，".join(notes)) if notes else ""
            print("[通过]   %s%s" % (name, extra))

    sys.exit(1 if any_bad else 0)


if __name__ == "__main__":
    main()
