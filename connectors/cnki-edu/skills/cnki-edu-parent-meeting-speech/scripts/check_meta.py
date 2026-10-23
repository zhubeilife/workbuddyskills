#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_meta.py — 元信息泄漏检查（交付前最后一道）

用途
----
扫描【即将发给用户的回复草案】或【已生成的交付文本】，检出其中混入的
"自检结论 / 过程元信息"。这类内容属内部执行项（SKILL.md §6「内部执行项」），
一旦出现在给用户的回复里即为违规——**即便它前面挂了"（内部执行）"
"按您要求不再单独展示"这类声明前缀，也不豁免**。

典型失守写法（本脚本要拦的就是它）：
    质量自检（内部执行，按您上一条要求不再单独展示）：语气红线 0 命中、
    建议依据 0 命中、§2 收口句已检出、政策来源无缺漏、docx 结构校验通过
    （3 表 tblW 与列宽和一致）。

三级判定
--------
* **P0 块名**（红线自检 / 政策来源核对 / 质量自检 / …）→ 违规
* **P1 结论句与模板残留**（"N 命中""已检出""校验通过""tblW"、脚本自身的
  `[通过]`／`[不通过]` 输出格式、"占位符""写作要求""📌" 等）→ 违规
* **P2 白名单提示**（字数 / 时长类控时说明）→ **不影响判定**。发言稿的
  【0 时间分配总览】与"按 200 字/分钟测算"属交付物（SKILL.md §6 白名单），
  默认保留，脚本只作提示。

用法
----
    python check_meta.py <文本文件>
    python check_meta.py <文本文件> --user-requested    # 用户明确索要自检结果 → 跳过检查
    python check_meta.py <文本文件> --json              # 机器可读输出

退出码
------
    0 = 干净；1 = 检出泄漏（需删除后再交付）；2 = 用法错误

注意
----
* 只输入 **待发出的回复草案 / 交付文本**，**不要**对 skill 自身的文档
  （SKILL.md、redlines.md、本脚本）运行——那些文件出于"讲规则"的目的
  必然包含这些词，会全量误报。
* 只读 UTF-8 文本；.docx 请先抽取正文为 .txt。
* 本脚本的输出同属内部动作，**不写入给用户的回复**。
"""

import argparse
import json
import re
import sys

# P0：块名 / 字段名——只要出现，基本可以判定为自检块泄漏
P0_PATTERNS = [
    r"红线自检",
    r"政策来源核对",
    r"质量自检",
    r"自检摘要",
    r"自检结果",
    r"自检记录",
    r"元信息泄漏",
    r"内部执行项",
]

# P1：结论句式——通过与否、命中数、修正处数、校验项名称
P1_PATTERNS = [
    r"\d+\s*处?\s*命中",
    r"零命中",
    r"已检出",
    r"(?:校验|检查|复检|自检)(?:均已|全部|一律)?(?:通过|合格)",
    r"(?:通过|合格)[，,、：:]\s*\d+\s*处",
    r"无缺漏",
    r"逐处核对",
    r"tblW",
    r"列宽和一致",
    r"已修正\s*\d+\s*处",
    r"身份指向自查",
    r"建议依据核查",
    r"脚本检查",
    r"各项检查均已",
    r"结构收口(?:✓|√|通过)",
    r"第\s*[X二三四五六七八九十\d]+\s*段末?已收口",
    # 校验脚本自身的输出格式（.[通过] / [不通过] / [跳过] / [错误]）
    r"\[通过\]|\[不通过\]|\[未通过\]|\[跳过\]|\[错误\]",
    # 过程动词
    r"已跑|复检|逐项结论|明细如下|清单如下",
    # 模板残留（§6 硬性要求 8「四清」对应的词）
    r"占位符|写作要求|写作指令|不随模板输出|📌",
    # 自检类动词
    r"自查(?:通过|完成|记录)",
]

# P2：白名单（SKILL.md §6）——字数 / 时长类控时说明。
# 发言稿的【0 时间分配总览】与"按 200 字/分钟朗读测算"属**交付物**（已确认保留），
# 脚本只作提示、**不影响通过与否**，以免把正常交付内容判成违规。
P2_PATTERNS = [
    r"正文\s*\d+\s*字|共\s*\d+\s*字|字数\s*\d+|字数区间",
    r"朗读测算|字\s*/\s*分钟|字/分钟",
]

# 声明前缀：与结论共现时，用于提示"前缀不豁免"（本身不单独判违规）
PREFIX_PATTERNS = [
    r"不单独展示",
    r"不再单独展示",
    r"内部执行",
    r"内部项",
    r"仅供.*参考",
    r"不对外",
]


def scan(text):
    """返回 (violations, warnings, notes, prefix_hits)。"""
    violations, warnings, notes, prefix_hits = [], [], [], []
    for idx, line in enumerate(text.splitlines(), 1):
        raw = line.strip()
        if not raw:
            continue
        has_prefix = any(re.search(p, raw) for p in PREFIX_PATTERNS)
        if has_prefix:
            prefix_hits.append((idx, raw))
        for pat in P0_PATTERNS:
            if re.search(pat, raw):
                violations.append((idx, pat, raw))
                break
        else:
            for pat in P1_PATTERNS:
                if re.search(pat, raw):
                    warnings.append((idx, pat, raw))
                    break
            else:
                for pat in P2_PATTERNS:
                    if re.search(pat, raw):
                        notes.append((idx, pat, raw))
                        break
    return violations, warnings, notes, prefix_hits


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("path", help="待检查的文本文件（UTF-8）")
    ap.add_argument("--user-requested", action="store_true",
                    help="用户明确索要自检结果时跳过检查（唯一豁免情形）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = ap.parse_args()

    if args.user_requested:
        msg = "用户明确索要自检结果 → 本次豁免；仍不得输出与本次索要无关的其他自检项。"
        print(json.dumps({"skipped": True, "reason": msg}, ensure_ascii=False, indent=2)
              if args.json else msg)
        return 0

    try:
        with open(args.path, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"[ERROR] 文件不存在：{args.path}", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print("[ERROR] 非 UTF-8 文本；.docx 请先抽取正文为 .txt。", file=sys.stderr)
        return 2

    violations, warnings, notes, prefix_hits = scan(text)
    dirty = bool(violations or warnings)

    if args.json:
        print(json.dumps({
            "clean": not dirty,
            "violations": [{"line": l, "pattern": p, "text": t} for l, p, t in violations],
            "warnings": [{"line": l, "pattern": p, "text": t} for l, p, t in warnings],
            "notes": [{"line": l, "pattern": p, "text": t} for l, p, t in notes],
            "declaration_prefixes": [{"line": l, "text": t} for l, t in prefix_hits],
        }, ensure_ascii=False, indent=2))
        return 1 if dirty else 0

    if not dirty:
        print("元信息泄漏检查：通过（0 处命中）")
        for l, p, t in notes:
            print(f"[提示·白名单] 第 {l} 行  匹配 /{p}/")
            print(f"             {t[:110]}")
        if notes:
            print("（以上属 SKILL.md §6 白名单内的控时说明，**默认保留**——无需删除。）")
        print("提示：本行结果同属内部动作，不写入给用户的回复。")
        return 0

    print("元信息泄漏检查：**未通过** —— 检出自检结论 / 过程元信息，删除后再交付")
    print("=" * 62)
    for l, p, t in violations:
        print(f"[违规·块名] 第 {l} 行  匹配 /{p}/")
        print(f"           {t[:110]}")
    for l, p, t in warnings:
        print(f"[疑似·结论] 第 {l} 行  匹配 /{p}/")
        print(f"           {t[:110]}")
    for l, p, t in notes:
        print(f"[提示·白名单] 第 {l} 行  匹配 /{p}/")
        print(f"             {t[:110]}")
    if prefix_hits:
        print("-" * 62)
        print("检出「声明式前缀」——**前缀不豁免**：加了前缀照样是输出，必须一并删除：")
        for l, t in prefix_hits:
            print(f"  第 {l} 行  {t[:110]}")
    print("=" * 62)
    print("处理：整句删除（不是改写、不是换个说法），定稿前自问——")
    print("     「这句话是不是在描述我做了什么检查、结果如何？」是 → 删。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
