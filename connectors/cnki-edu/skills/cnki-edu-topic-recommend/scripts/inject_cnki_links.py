#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_cnki_links.py —— 知网文献引用链接注入与覆盖校验

用途（配合 cnki-edu-topic-recommend 技能的 INJECT_LINKS 子程序）：
  1. 从 searchVectorBJ 的原始检索结果（JSON / 工具持久化 .txt）中抽取「篇名 → url」映射；
  2. 把报告 Markdown 中所有**裸露的**《篇名》批量转成可点击链接 [《篇名》](url)；
  3. 报告仍未覆盖的《》清单，供人工核对（课标标准名、作品书名属正常残留）。

设计要点：
  - **只注入映射中确实存在的篇名**，绝不猜测或拼接 URL（避免指向错误文献）。
  - 已带链接的引用不会被重复包裹（用 (?<!\\[) 负向断言判定）。
  - 全角/半角标点、空格差异做归一化后匹配（如"建立阅读档案,落实..."与"，"）。

用法：
  # 注入并校验
  python inject_cnki_links.py 报告.md --results <检索结果文件或目录> [...]
  # 只校验不修改
  python inject_cnki_links.py 报告.md --check-only --results ...
  # 只导出篇名→url 映射（生成报告前查看有哪些可链文献）
  python inject_cnki_links.py --dump-map --results ...
"""

import argparse
import glob
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TITLE_KEYS = ("篇名", "Title", "title")
URL_KEYS = ("url", "URL", "Url")

# 归一化：统一标点与空白，便于全角/半角混用场景匹配
_PUNCT = {
    "，": ",", "：": ":", "；": ";", "（": "(", "）": ")",
    "“": '"', "”": '"', "‘": "'", "’": "'", "？": "?", "！": "!",
    "－": "-", "—": "-", "～": "~", "　": " ",
}


def normalize(text: str) -> str:
    # 先剥掉书名号：映射的 key 来自「篇名」（无书名号），而报告中的 token 带《》
    text = re.sub(r"[《》]", "", (text or "").strip())
    for a, b in _PUNCT.items():
        text = text.replace(a, b)
    text = re.sub(r"\s+", "", text)
    return text.lower()


def load_map(paths) -> dict:
    """从若干检索结果文件/目录中抽取 篇名→url。"""
    result = {}
    files = []
    for p in paths:
        if os.path.isdir(p):
            files.extend(sorted(glob.glob(os.path.join(p, "*.txt"))))
            files.extend(sorted(glob.glob(os.path.join(p, "*.json"))))
        else:
            files.append(p)

    for f in files:
        try:
            raw = open(f, encoding="utf-8", errors="ignore").read()
        except OSError as e:
            print(f"[warn] 无法读取 {f}: {e}", file=sys.stderr)
            continue
        raw = raw.strip()
        # 兼容带前缀/后缀的持久化输出，截取第一个 JSON 结构
        start = min([i for i in (raw.find("{"), raw.find("[")) if i >= 0], default=-1)
        if start > 0:
            raw = raw[start:]
        try:
            doc = json.loads(raw)
        except Exception:
            continue  # 非 JSON 文件（如报告本身）静默跳过

        items = []
        if isinstance(doc, dict):
            data = doc.get("data")
            if isinstance(data, list):
                items = [x for x in data if isinstance(x, dict)]
            elif isinstance(data, dict):
                items = [data]
            else:
                items = [doc]
        elif isinstance(doc, list):
            items = [x for x in doc if isinstance(x, dict)]

        for it in items:
            title = ""
            for k in TITLE_KEYS:
                if it.get(k):
                    title = str(it[k]).strip()
                    break
            url = ""
            for k in URL_KEYS:
                if it.get(k):
                    url = str(it[k]).strip()
                    break
            if title and url:
                result.setdefault(normalize(title), (title, url))
    return result


BARE_TITLE = re.compile(r"(?<!\[)《[^》]+》")


def inject(text: str, link_map: dict, exclude_norm: set):
    """把裸露《篇名》替换为 Markdown 链接，返回 (新文本, 命中数, 未覆盖标题列表)。"""
    injected = 0
    remaining = []

    def repl(m):
        nonlocal injected
        tok = m.group(0)
        key = normalize(tok)
        if key in exclude_norm:
            return tok
        hit = link_map.get(key)
        if hit:
            injected += 1
            return f"[{tok}]({hit[1]})"
        remaining.append(tok)
        return tok

    new_text = BARE_TITLE.sub(repl, text)
    return new_text, injected, remaining


def main():
    ap = argparse.ArgumentParser(description="知网文献引用链接注入与覆盖校验")
    ap.add_argument("report", nargs="?", help="待处理的 Markdown 报告路径")
    ap.add_argument("--results", nargs="*", default=[],
                    help="searchVectorBJ 检索结果文件/目录（可多个）")
    ap.add_argument("--exclude", nargs="*", default=[],
                    help="不参与链接注入的《》名称（课标标准名、作品书名等）")
    ap.add_argument("--check-only", action="store_true", help="只校验，不改写文件")
    ap.add_argument("--dump-map", action="store_true", help="只导出篇名→url 映射")
    args = ap.parse_args()

    if not args.results:
        print("[error] 至少需要提供一个 --results 来源", file=sys.stderr)
        return 2

    link_map = load_map(args.results)
    print(f"[info] 从检索结果中解析出 {len(link_map)} 条「篇名→url」映射")

    if args.dump_map or not args.report:
        for title, url in sorted(link_map.values(), key=lambda x: x[0]):
            print(f"{title}\t{url}")
        return 0

    if not os.path.isfile(args.report):
        print(f"[error] 报告不存在：{args.report}", file=sys.stderr)
        return 2

    text = open(args.report, encoding="utf-8").read()
    exclude_norm = {normalize(x) for x in args.exclude}

    new_text, injected, remaining = inject(text, link_map, exclude_norm)

    if not args.check_only and injected:
        open(args.report, "w", encoding="utf-8").write(new_text)

    print(f"[info] 新注入链接：{injected} 处")
    uniq_remaining = sorted(set(remaining))
    if uniq_remaining:
        print(f"[warn] 仍未覆盖的裸露《》共 {len(uniq_remaining)} 个，需人工确认是否为非文献名：")
        for t in uniq_remaining:
            print(f"   - {t}")
    else:
        print("[ok] 全部《》均已带链接或已列入排除项")

    # 最终覆盖统计
    linked = re.findall(r"\[《[^》]+》\]\(https?://[^)]*\)", new_text)
    print(f"[info] 报告内文献链接总数：{len(linked)}（唯一 {len(set(linked))} 篇）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
