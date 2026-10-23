#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cnki-edu-parent-meeting-speech 发言稿结构校验器 —— 成稿后必跑。

背景（为什么需要这个脚本）：
  「§2 段末必须有一句收口总结句」这条硬规则，此前只写在 speech-roles.md 的正文里，
  既没有脚本、也没有进 SKILL.md 的必跑步骤，等于**软规则**。
  实测反扫 12 份历史稿件，**7 份未收口**（直接以"第 X 件事"结尾）——
  与"表格结构"那次的教训同源：规则不落到校验器上，就会持续失守。

本脚本检查四项（A/B/C 判违规，D 为提示级）：
  A. 收口句检查：§2（班情通报 / 学科学情概览）段末是否有收口总结句。
     违规模式：
       - 段末最后一段以「第 X 件事」开头且以该列举句结尾（列举未完，未收口）
       - 段末若干段内无任何收口线索词
  B. 列举完整性提示：§2 的「第 X 件事」是否连续编号（1,2,3…不跳号）
  C. 字数预算：统计中文字符数，对照时长估算（200 字/分钟）给出提示
  D. 开场钩子回收提示（提示级，不影响通过）：开场若用引语钩子，检查是否在正文 / 结尾回收；
     并查「回到开头那句话」的被引内容是否真的出现在开场（防悬空引用）

用法:
  python check_structure.py <文本文件> --role <班主任|学科老师|兼任> [--minutes 45]

  文本文件可为 .txt/.md，也可直接传 .docx（自动抽取正文）。

输出: 文本报告；退出码 0=通过, 1=有问题, 2=用法错误
"""
import argparse
import os
import re
import sys
import zipfile

# ---- 收口线索词（出现任一即认为"已收口"）----
CLOSING_CUES = (
    "所以这不是", "所以说", "所以我想", "所以今天", "所以这",
    "我想说的是", "我想说", "我要说的是",
    "这几件事", "这些事", "把这几件", "归结", "指向同一", "指向的其实是",
    "说到底", "归根结底", "本质上是", "本质上", "核心是", "归根",
    "不是一个", "不是「", "不是“",
    "一句话", "概括起来", "总起来说", "总的来说",
)

# ---- 开场钩子回收（D 项 · 提示级）----
HOOK_QUOTE_RE = re.compile(r"“([^”]{8,})”")
CALLBACK_PAT = re.compile(r"回到开头|开头那|开场那|开头提到|开头说的|开头问")
VAGUE_REF_RE = re.compile(r"回到开头(?:那句话|那句话是)?[：:]\s*([^。！？\n]{4,60})")


def hook_notes(paras, sec2_start):
    """提示级：开场钩子是否回收；「回到开头那句话」是否悬空。"""
    out = []
    opening = "".join(paras[:sec2_start])
    full = "".join(paras)
    quotes = [q for q in HOOK_QUOTE_RE.findall(opening) if not q.startswith("<")]
    cb = CALLBACK_PAT.search(full)
    if quotes and not cb:
        out.append("开场有引语钩子（“%s…”），但全文未见回扣句（回到开头…）—— 请确认已闭环"
                   % quotes[0][:12])
    if cb and not quotes:
        out.append("出现「回到开头…」式回扣，但开场没有引语钩子 —— 疑似悬空引用，请核对")
    m = VAGUE_REF_RE.search(full)
    if m:
        seg = re.sub(r"[^\u4e00-\u9fa5]", "", m.group(1))[:12]
        op = re.sub(r"[^\u4e00-\u9fa5]", "", opening)
        if seg and seg not in op:
            out.append("「回到开头那句话」的被引内容（%s…）在开场段找不到 —— 疑似悬空引用"
                       % seg[:10])
    return out


# ---- 「第 X 件事」列举标记 ----
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
ITEM_RE = re.compile(r"第\s*([一二三四五六七八九十\d]+)\s*件事")

# ---- §2 段落标题特征 ----
SEC2_PAT = re.compile(r"班情通报|学科学情概览|班情概览|学情概览|班级情况")
# ---- 后续段落标题（用于界定 §2 的结束）----
SEC3_PAT = re.compile(r"学情分析|学科学习方法|学习方法与家庭配合|家庭教育建议|Q&A|结束语|附\s*[ABCＡＢＣ]|本学科专区")


def read_text(path):
    if path.lower().endswith((".docx", ".doc")):
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        xml = re.sub(r"</w:p>", "\n", xml)
        return re.sub(r"<[^>]+>", "", xml)
    with open(path, encoding="utf-8") as f:
        return f.read()


def split_paras(text):
    return [p.strip() for p in text.splitlines() if p.strip()]


def cn_char_count(text):
    return len(re.findall(r"[\u4e00-\u9fa5]", text))


def check(path, role, minutes):
    problems = []
    notes = []
    text = read_text(path)
    paras = split_paras(text)

    # --- 定位 §2 段落区间 ---
    # 注意：文档开头有时间分配总览表，其中也可能出现「班情通报」字样（目录/表头），
    # 因此不能取"第一个匹配"，而要取**最后一个**长度合规且后随正文的标题。
    sec2_starts = [i for i, p in enumerate(paras)
                   if SEC2_PAT.search(p) and len(p) < 60]
    if not sec2_starts:
        problems.append("未找到 §2 段落标题（班情通报 / 学科学情概览），无法做收口检查")
        return problems, notes

    # 优先选"其后若干段内能出现「第 X 件事」"的那个标题（即真正的正文标题）
    start = sec2_starts[-1]
    for cand in sec2_starts:
        window = paras[cand + 1: cand + 40]
        if any(ITEM_RE.search(p) for p in window) or any(any(c in p for c in CLOSING_CUES) for p in window):
            start = cand
            break

    # --- 找 §2 的结束边界（§3 标题），从 start 之后开始找 ---
    end = None
    for i in range(start + 1, len(paras)):
        if SEC3_PAT.search(paras[i]) and len(paras[i]) < 60:
            end = i
            break
    if end is None:
        end = min(start + 60, len(paras))

    sec2 = paras[start + 1:end]
    if not sec2:
        problems.append("§2 段落为空")
        return problems, notes

    # --- A. 收口句检查 ---
    last = sec2[-1]
    # 找 §2 内最后一条「第 X 件事」列举句
    item_idxs = [i for i, p in enumerate(sec2) if ITEM_RE.search(p)]
    if item_idxs:
        last_item = item_idxs[-1]
        tail = sec2[last_item + 1:]
        closed = any(any(c in p for c in CLOSING_CUES) for p in tail)
        if not closed:
            if len(tail) == 0:
                problems.append(
                    "§2 段末未收口：最后一段即列举项「%s…」，其后没有任何收口句"
                    % last_item_text(sec2[last_item]))
            else:
                problems.append(
                    "§2 段末未收口：列举项「%s…」之后有 %d 段，但均无收口线索词（所以…/我想说的是…/这几件事…/不是一个…问题）"
                    % (last_item_text(sec2[last_item]), len(tail)))
        else:
            notes.append("§2 收口句：已检出")
    else:
        # 没有「第 X 件事」列举，则检查段末是否本身带收口线索
        if any(c in last for c in CLOSING_CUES):
            notes.append("§2 收口句：已检出（无序号列举式）")
        else:
            problems.append("§2 段末未收口：段末无收口线索词，且非「第 X 件事」列举式（无法判定已收口）")

    # --- B. 列举编号连续性 ---
    nums = [ITEM_RE.search(p).group(1) for p in sec2 if ITEM_RE.search(p)]
    seq = [CN_NUM.get(n, int(n) if n.isdigit() else None) for n in nums]
    seq = [s for s in seq if s]
    if seq:
        expect = list(range(1, len(seq) + 1))
        if seq != expect:
            notes.append("§2 列举编号为 %s，非连续 1..%d（请确认是否有意为之）" % (seq, len(seq)))

    # --- C. 字数预算 ---
    n = cn_char_count(text)
    per_min = 200
    est = round(n / per_min, 1)
    budget = {30: (4000, 5000), 45: (6000, 7000), 60: (8000, 9000)}
    notes.append("中文字数 %d（约 %.1f 分钟 @200字/分）" % (n, est))
    if minutes in budget:
        lo, hi = budget[minutes]
        if n < lo:
            notes.append("字数偏少：%d 分钟建议 %d-%d 字，当前 %d 字" % (minutes, lo, hi, n))
        elif n > hi:
            notes.append("字数偏多：%d 分钟建议 %d-%d 字，当前 %d 字" % (minutes, lo, hi, n))
        else:
            notes.append("字数在 %d 分钟建议区间（%d-%d 字）内" % (minutes, lo, hi))

    # --- D. 开场钩子回收提示（提示级）---
    notes.extend(hook_notes(paras, start))

    return problems, notes


def last_item_text(p, n=30):
    p = re.sub(r"\s+", "", p)
    return p[:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text_file")
    ap.add_argument("--role", default="班主任", help="班主任 / 学科老师 / 兼任")
    ap.add_argument("--minutes", type=int, default=45, help="时长（分钟）")
    args = ap.parse_args()

    if not os.path.isfile(args.text_file):
        print("[错误] 文件不存在: %s" % args.text_file)
        sys.exit(2)

    problems, notes = check(args.text_file, args.role, args.minutes)
    name = os.path.basename(args.text_file)
    if problems:
        print("[不通过] %s" % name)
        for p in problems:
            print("        - %s" % p)
        for n in notes:
            print("        · %s" % n)
        sys.exit(1)
    print("[通过]   %s" % name)
    for n in notes:
        print("        · %s" % n)
    sys.exit(0)


if __name__ == "__main__":
    main()
