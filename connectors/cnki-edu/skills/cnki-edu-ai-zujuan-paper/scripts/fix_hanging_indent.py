#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 组卷 · docx 后处理：补「题号悬挂缩进」

为什么需要：
    HTML→docx 转换器**忽略负 text-indent**，因此 CSS 里的悬挂缩进只能落成
    「整段左缩进」（w:ind w:left="273"），首行不会回退到页边距。
    Word 的悬挂 = w:ind 同时给 w:left 与 w:hanging（续行缩进、首行回退）。

本脚本对已生成的 docx 就地补 w:hanging，使其符合《试卷与解析排版标准》§6-1。

用法：
    python3 fix_hanging_indent.py <docx路径> [缩进twips，默认273（=13.65pt）]
"""
import sys, re, os, shutil, zipfile

TARGET_FILE = "word/document.xml"


def fix_xml(xml: str, target: int) -> tuple:
    cnt = 0

    def repl(m):
        nonlocal cnt
        blk = m.group(0)
        mi = re.search(r"<w:ind\b[^>]*/>", blk)
        if not mi:
            return blk
        ind = mi.group(0)
        # 已有悬挂/首行缩进定义 → 不动
        if "w:hanging" in ind or "w:firstLine" in ind:
            return blk
        # 只处理左缩进恰好等于目标值的段落（题号段专用值，避免误伤表格等）
        if f'w:left="{target}"' not in ind and f'w:start="{target}"' not in ind:
            return blk
        cnt += 1
        new_ind = ind[:-2].rstrip() + f' w:hanging="{target}"/>'
        return blk.replace(ind, new_ind)

    xml = re.sub(r"<w:pPr(?:\s[^>]*)?>.*?</w:pPr>", repl, xml, flags=re.S)
    return xml, cnt


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fix_hanging_indent.py <docx> [twips=273]", file=sys.stderr)
        sys.exit(2)
    path = os.path.abspath(sys.argv[1])
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 273
    if not os.path.isfile(path):
        print(f"[fix_indent] 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    tmp = path + ".fixing"
    total = 0
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == TARGET_FILE:
                xml = data.decode("utf-8")
                xml, n = fix_xml(xml, target)
                total += n
                data = xml.encode("utf-8")
            zout.writestr(item, data)

    if total == 0:
        os.remove(tmp)
        print(f"[fix_indent] 无需处理（未发现 left={target} 的段落，或已含 hanging）")
        return
    shutil.move(tmp, path)
    print(f"[fix_indent] 已补悬挂缩进 hanging={target}twips（{target/20:.2f}pt）: {total} 个段落")


if __name__ == "__main__":
    main()
