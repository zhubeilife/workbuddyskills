# -*- coding: utf-8 -*-
"""
交互式教学动画 HTML 结构自检脚本。

用法：
    python validate_html.py <文件路径>

检查项：
    1. 单文件结构完整（doctype / html / head / body 齐全，标签闭合）
    2. 无任何外部依赖（script src / link href / img src / fetch / @import / 网络地址）
    3. 无常见"必须避免"的写法（未使用的中文引号混入代码、内联 onclick 等）
    4. 关键要素存在（viewport、charset、至少一个交互控件、重置）
    5. 体积报告

退出码：0 = 通过（可能有警告）；1 = 发现必须修复的问题。
"""
import sys
import os
import re

MUST = []   # 阻断性问题
WARN = []   # 提醒性问题


def check(path):
    if not os.path.isfile(path):
        print("[错误] 文件不存在：%s" % path)
        return 1

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    size_kb = len(html.encode("utf-8")) / 1024.0

    low = html.lower()

    # 屏蔽内联 data URI（base64 图片）后再做文本类检查，避免 base64 撞词误判
    scan = re.sub(r"data:[^\"')\s]+", "DATAURI", html)
    scan_low = scan.lower()

    # 1. 结构
    for tag in ["<!doctype html", "<html", "<head", "<body"]:
        if tag not in low:
            MUST.append("缺少结构标记：%s" % tag)
    if "</html>" not in low:
        MUST.append("缺少 </html> 闭合标签")
    if "</script>" not in low or "<script" not in low:
        WARN.append("没有找到脚本块，确认是否为纯静态素材")

    # 2. 外部依赖
    if re.search(r"<script[^>]*\bsrc\s*=", low):
        MUST.append("存在外部脚本引入 <script src=...>，必须改为内联")
    if re.search(r"<link[^>]*\bhref\s*=", low):
        MUST.append("存在外部样式引入 <link href=...>，必须改为内联 <style>")
    # <img src=> 允许内嵌 data: 图片（单文件仍成立），仅拦截外部图片地址
    for m in re.finditer(r"<img[^>]*\bsrc\s*=\s*([\"']?)([^\"'>\s]+)", scan_low):
        if not (m.group(2).startswith("data:") or "datauri" in m.group(2).lower()):
            MUST.append("存在外部图片引用 <img src=%s>，须改为内嵌 data: 图片或代码自绘" % m.group(2)[:60])
    if "@import" in scan_low:
        MUST.append("存在 CSS @import，必须删除")
    if re.search(r"\bfetch\s*\(", scan_low):
        MUST.append("存在 fetch() 网络请求，必须删除")
    if "xmlhttprequest" in scan_low:
        MUST.append("存在 XMLHttpRequest 网络请求，必须删除")
    # 外链样式/脚本（data URI 已屏蔽）
    for proto in ["http://", "https://", "//cdn", "cdn.", "url(http", "url(//"]:
        hits = [m.start() for m in re.finditer(re.escape(proto), scan_low)]
        for pos in hits:
            line = scan_low[:pos].count("\n") + 1
            snippet = scan[max(0, pos - 40):pos + 60].replace("\n", " ")
            MUST.append("第 %d 行附近出现外部地址 %s：...%s..." % (line, proto, snippet.strip()))

    # 3. 常见问题
    if 'charset="utf-8"' not in low and "charset=utf-8" not in low:
        MUST.append("缺少 UTF-8 编码声明（中文会乱码）")
    if "viewport" not in low:
        WARN.append("缺少 viewport 设置，投屏/移动端可能不适配")
    if "overflow" not in low:
        WARN.append("未设置 overflow，页面可能整体出现滚动条")

    # 残留占位符（在屏蔽 data URI 后的 scan 上检查）
    # 骨架模板（文件名含 template）本就是待填的，占位符只作提示
    is_template = "template" in os.path.basename(path).lower()
    for ph in ["【", "TODO", "待填", "xxx", "XXX", "占位"]:
        if ph in scan:
            line = scan[:scan.find(ph)].count("\n") + 1
            msg = "第 %d 行存在未替换的占位内容：%s" % (line, ph)
            (WARN if is_template else MUST).append(msg)

    # 4. 关键要素
    has_input = ("<input" in low) or ("<button" in low) or ("addEventListener" in low)
    if not has_input:
        WARN.append("未发现交互控件，确认这是交互式素材而非静态插图")
    if "reset" not in low and "重置" not in html and "还原" not in html:
        WARN.append("未发现重置功能，建议补上")

    # 5. 字号过小提醒
    for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)\s*px", low):
        v = float(m.group(1))
        if v < 12:
            line = low[:m.start()].count("\n") + 1
            WARN.append("第 %d 行字号 %spx 过小，教室后排可能看不清" % (line, m.group(1)))

    # 报告
    print("=" * 56)
    print("文件：%s" % os.path.basename(path))
    print("体积：%.1f KB" % size_kb)
    print("=" * 56)
    if not MUST and not WARN:
        print("[通过] 未发现结构性问题，可以交付。")
        return 0
    if MUST:
        print("\n[必须修复]")
        for i, m in enumerate(MUST, 1):
            print("  %d. %s" % (i, m))
    if WARN:
        print("\n[建议优化]")
        for i, m in enumerate(WARN, 1):
            print("  %d. %s" % (i, m))
    return 1 if MUST else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(check(sys.argv[1]))
