# -*- coding: utf-8 -*-
"""生成"模板写法"对照组评语，用于量化雷同度自检的效果。

为什么需要对照组：只说"我们的评语不像"没有说服力。
把最典型的套话写法跑一遍同样的自检，两条曲线放到一起，价值就看得见了。
这些模板句就是不给任何约束时，模型最容易产出的东西。

用法：
  python make_naive_baseline.py --roster roster.json --out comments_naive.json
"""
import argparse
import json
import os

# 每一条都是真实存在的高频评语模板，只把姓名填进去
TEMPLATES = [
    "你是一个聪明懂事的学生，学习认真，尊敬师长，团结同学。课堂上能够认真听讲，作业能够按时完成。"
    "希望你在新学期继续努力，发扬优点，改正不足，争取更大的进步。",

    "你是一个文静、踏实的学生，做事认真负责，待人诚恳有礼貌。学习上能够吃苦耐劳，"
    "成绩比较稳定。希望你在新的学期里，更加积极主动地参与课堂讨论，争取更好的成绩。",

    "你热爱集体，关心同学，乐于助人，在班级中表现良好。学习态度端正，能够完成老师布置的各项任务。"
    "希望你在今后的学习中，继续努力，克服困难，不断进步。",

    "你思维敏捷，接受能力强，课堂上能够积极思考。作业书写工整，完成情况良好。"
    "希望你在新学期里更上一层楼，做一个全面发展的好学生。",

    "你性格开朗，为人真诚，能够与同学友好相处。学习上有上进心，但有时不够细心。"
    "希望你今后严格要求自己，取得更加优异的成绩。",
]

QUALITY = ["", "继续加油！", "老师相信你！", "再接再厉！", "期待你的好消息！"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", required=True)
    ap.add_argument("--out", default="comments_naive.json")
    ap.add_argument("--tag", default="模板写法（对照组）")
    args = ap.parse_args()

    with open(args.roster, "r", encoding="utf-8") as f:
        roster = json.load(f)

    comments = []
    for i, s in enumerate(roster["roster"]):
        body = (s["姓名"] + "同学，" + TEMPLATES[i % len(TEMPLATES)]
                + QUALITY[i % len(QUALITY)])
        comments.append({
            "学号": s["学号"], "姓名": s["姓名"],
            "核心印象标签": ["认真踏实", "聪明懂事", "文静稳重", "热爱集体", "积极上进"][i % 5],
            "分层": "未分层",
            "评语正文": body,
            "证据来源": ["无（模板句，未引用任何材料）"],
        })
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"meta": {"版本": args.tag, "说明": "不含任何材料证据的套话模板"},
                   "comments": comments}, f, ensure_ascii=False, indent=2)
    print("对照组评语已生成 -> %s（%d 条）" % (os.path.abspath(args.out), len(comments)))


if __name__ == "__main__":
    main()
