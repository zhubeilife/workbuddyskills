#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cnki-edu-daily-comm-scripts 建议依据校验脚本：检查「建议是否从事实出」。

背景（规则来源：redlines.md 第 11 类、SKILL.md 第七节第 7 条）：
一条与事实无关联的通用建议（全文只讲课堂纪律，却建议"帮孩子调整作息"），
会被家长读成"你们家没管好"——即红线第 1 类（评价 / 暗示指责家庭）换了层皮。
本脚本负责抓「短语层」的脱节；「这条建议前面哪句事实在支撑它」的对应关系，
只能由人工层逐条追问。**脚本查短语，人工查对应关系，两者不可互相替代。**

判定逻辑（只查"外部归因类"高危领域，避免误伤校内可观察建议）：
  1) 定位「请求句」：句中含请求 / 建议标记（请 / 建议 / 希望 / 麻烦 / 配合 / 提醒 …）；
  2) 在该句中找「高危领域词」（作息睡眠 / 情绪心理 / 家庭因素 / 身体健康 / 电子产品 / 通用套话）；
  3) 回溯该领域词之前的文本（含本句前置部分），若存在**已确立**的同领域表述则通过；
     「已确立」= 该处附近不含假设 / 询问标记（如果 / 是否 / 是不是 / 可能 / 了解一下 …），
     即"我看到的"成立，"如果睡得晚""想跟您了解一下作息"不算。
  4) 回溯不到 → 报「建议脱离事实」。

用法:
  python check_advice.py <文本文件>

输出: JSON {total, hits:[{category, domain, matched, line, context}], summary}
退出码: 0=通过, 1=有命中（需人工逐条确认）, 2=错误
"""
import argparse
import json
import os
import re
import sys

# ---- 高危领域：家庭 / 外部侧因素，最容易被当作通用建议凭空塞入 ----
# 校内可观察领域（课堂 / 作业 / 成绩 / 同伴）不纳入，避免误伤有事实支撑的建议。
DOMAINS = [
    ("作息睡眠", r"(作息|睡眠|早睡|晚睡|睡得|熬夜|打瞌睡|休息不够|起不来|早点休息)"),
    ("情绪心理", r"(情绪|心理|心情|焦虑|压力大|不开心|闷闷不乐)"),
    ("家庭因素", r"(家庭氛围|家庭情况|父母关系|家里情况|离异|家庭变故|亲子关系)"),
    ("身体健康", r"(身体健康|生病|感冒|发烧|体质|视力)"),
    ("电子产品", r"(手机|电子产品|平板|打游戏|刷视频|屏幕时间)"),
    ("通用套话", r"(陪陪|陪伴|多鼓励|多沟通|多表扬|培养.{0,4}习惯|养成.{0,4}习惯|做好榜样|营造.{0,6}(氛围|环境))"),
]

# 请求 / 建议标记：句中出现即认定该句在"提要求"
REQUEST = r"(请|建议|希望|麻烦|配合|提醒|尽量|最好|不妨|试试|需要您|辛苦您)"

# 假设 / 询问标记：出现这些说明该领域只是猜测或想了解，不算已确立的事实
HYPOTHETICAL = ("如果", "是否", "是不是", "可能", "也许", "大概", "了解一下", "想问问",
                "问问", "方便说", "跟您了解", "了解下")

# 观察标记：与领域词同句出现、且位于领域词之前时，视为已确立
# 只收"我看到的"这类实义观察词，不收"听/说"等单字（单字极易误伤）
OBSERVE = ("发现", "注意到", "观察到", "看到", "听说", "提到", "反映")

SENT_SPLIT = re.compile(r"[。！？!?\n]+")


def established(prior_text, dom_pat):
    """prior_text 中是否存在「已确立」的该领域表述（附近不含假设 / 询问标记）。"""
    for m in re.finditer(dom_pat, prior_text):
        left = prior_text[max(0, m.start() - 14): m.start()]
        if any(h in left for h in HYPOTHETICAL):
            continue
        return True
    return False


def scan(lines):
    hits = []
    # 全文累积文本（跨行），用于回溯"前文是否已确立"
    walked = ""
    for i, line in enumerate(lines, 1):
        if not line.strip():
            walked += "\n"
            continue
        for sent in SENT_SPLIT.split(line):
            if not sent.strip():
                continue
            if not re.search(REQUEST, sent):
                walked += sent + "。"
                continue
            for dom_name, dom_pat in DOMAINS:
                for m in re.finditer(dom_pat, sent):
                    prior = walked + sent[:m.start()]
                    # 同句内若存在观察标记，视为已确立
                    same_sent_observed = (
                        any(o in sent for o in OBSERVE)
                        and m.start() > max((sent.find(o) for o in OBSERVE if o in sent), default=10 ** 9)
                    )
                    if same_sent_observed or established(prior, dom_pat):
                        continue
                    hits.append({
                        "category": "建议脱离事实",
                        "domain": dom_name,
                        "matched": m.group(0),
                        "line": i,
                        "context": sent[max(0, m.start() - 16): m.end() + 16].strip(),
                    })
            walked += sent + "。"
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text_file")
    args = ap.parse_args()
    if not os.path.isfile(args.text_file):
        print(json.dumps({"error": "文件不存在: %s" % args.text_file}, ensure_ascii=False))
        sys.exit(2)

    with open(args.text_file, encoding="utf-8") as f:
        lines = f.read().splitlines()

    hits = scan(lines)
    print(json.dumps({
        "total": len(hits),
        "hits": hits,
        "summary": ("建议依据检查通过" if not hits
                    else "命中 %d 处建议疑似脱离事实，需人工逐条确认：有事实支撑则保留，凭空塞入则删除" % len(hits)),
    }, ensure_ascii=False, indent=2))
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
