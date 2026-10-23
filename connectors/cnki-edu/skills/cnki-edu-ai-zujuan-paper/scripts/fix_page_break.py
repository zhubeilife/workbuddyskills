#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx 后处理：给「解析区标题」段落补强制分页（w:pageBreakBefore）。

为什么需要：
    HTML→docx 转换器**完全不支持**任何 HTML/CSS 分页写法——实测 6 种全部失效：
      .ana{page-break-before:always} / <p style="page-break-before:always">
      <div style="page-break-before:always"></div> / <br style="page-break-before:always">
      <div style="break-before:page"></div> / 空段落占位
    产物里 pageBreakBefore=0、w:type="page"=0 → 试卷与解析连排。
    故必须像「题号悬挂缩进」一样走**转换后 XML 后处理**。

    ⚠️ 若「解析」单独成篇（试卷/解析两份独立文件时），锚段会位于文档最前，
    此时**不补分页**（否则文首多出一整页空白）——脚本自动跳过。

用法：
    python3 fix_page_break.py <docx路径> ["锚文本"，默认 参考答案与试题解析]
"""
import os
import re
import shutil
import sys
import zipfile

TARGET_FILE = "word/document.xml"


def insert_pbb(seg: str) -> str:
    """在段落 XML 的 <w:pPr> 内插入 <w:pageBreakBefore/>（按 OOXML 子元素序：置于 spacing 之前）。"""
    m = re.search(r"<w:pPr(?:\s[^>]*)?>", seg)
    if m:
        ps = re.search(r"</w:pStyle>", seg)          # 若有 pStyle，必须排在其后
        idx = ps.end() if ps else m.end()
        return seg[:idx] + "<w:pageBreakBefore/>" + seg[idx:]
    m2 = re.match(r"<w:p(?:\s[^>]*)?>", seg)         # 无 pPr → 新建
    return seg[:m2.end()] + "<w:pPr><w:pageBreakBefore/></w:pPr>" + seg[m2.end():]


def fix_xml(xml: str, anchor: str) -> tuple:
    cnt = 0
    all_ps = list(re.finditer(r"<w:p(?:\s[^>]*)?>.*?</w:p>", xml, re.S))
    # 定位第一个"有可见文字"的段落（其前的空段落不计），用于判断锚段是否已在文首。
    first_text_pos = None
    for m in all_ps:
        if re.sub(r"<[^>]+>", "", m.group(0)).strip():
            first_text_pos = m.start()
            break
    for m in reversed(all_ps):
        seg = m.group(0)
        if "w:pageBreakBefore" in seg:
            continue
        if anchor not in re.sub(r"<[^>]+>", "", seg):
            continue
        # 锚段若已是文档首个有文字的段落（例如「解析」单独成篇），不能再加分页，
        # 否则会在文首多出一整页空白。仅当锚段前面还有正文时才分页。
        if first_text_pos is not None and m.start() == first_text_pos:
            continue
        xml = xml[:m.start()] + insert_pbb(seg) + xml[m.end():]
        cnt += 1
    return xml, cnt


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fix_page_break.py <docx> [锚文本]", file=sys.stderr)
        sys.exit(2)
    path = os.path.abspath(sys.argv[1])
    anchor = sys.argv[2] if len(sys.argv) > 2 else "参考答案与试题解析"
    if not os.path.isfile(path):
        print(f"[fix_pagebreak] 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    tmp = path + ".fixing"
    total = 0
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == TARGET_FILE:
                xml = data.decode("utf-8")
                xml, n = fix_xml(xml, anchor)
                total += n
                data = xml.encode("utf-8")
            zout.writestr(item, data)

    if total == 0:
        os.remove(tmp)
        print(f"[fix_pagebreak] 无需处理（未找到含「{anchor}」的段落）")
        return
    shutil.move(tmp, path)
    print(f"[fix_pagebreak] 已补强制分页 pageBreakBefore: {total} 个段落")


if __name__ == "__main__":
    main()
