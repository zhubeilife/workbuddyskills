# -*- coding: utf-8 -*-
"""生成一份可复现的示例成绩数据（含主表 / 逐题 / 历次 三个工作表），用于自测与演示。

    python make_sample_data.py --out 示例成绩.xlsx --seed 42
"""

from __future__ import annotations

import argparse
import random

SUBJECTS = {
    "数学": (150, 0.68, 22),
    "语文": (150, 0.74, 16),
    "英语": (120, 0.70, 18),
    "物理": (100, 0.62, 19),
    "政治": (100, 0.76, 14),
}
CLASSES = ["高二(1)班", "高二(2)班", "高二(3)班"]
KNOWLEDGE = {
    "数学": ["集合与逻辑", "函数与导数", "三角函数", "数列", "立体几何", "解析几何", "概率统计"],
    "语文": ["字音字形", "词语运用", "古诗文默写", "文言文阅读", "现代文阅读", "语言表达", "写作"],
    "英语": ["听力", "语法填空", "完形填空", "阅读理解", "七选五", "书面表达"],
    "物理": ["运动学", "牛顿定律", "功能关系", "动量守恒", "电场", "恒定电流"],
    "政治": ["经济生活", "政治生活", "文化生活", "生活与哲学", "时事政治"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="示例成绩.xlsx")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--students", type=int, default=45, help="每班人数")
    args = ap.parse_args()

    rng = random.Random(args.seed)

    def clip(v, lo, hi):
        return max(lo, min(hi, v))

    students = []
    sid = 20260001
    for ci, cls in enumerate(CLASSES):
        for k in range(args.students):
            ability = rng.gauss(0, 1)
            # 让 3 班数学偏弱、1 班语文偏强，制造排名差异
            students.append({
                "学号": str(sid),
                "姓名": "%s%02d" % (["赵", "钱", "孙", "李", "周", "吴", "郑", "王", "冯", "陈"][k % 10],
                                   k + 1 + ci * 50),
                "班级": cls,
                "_ability": ability,
                "_cls": ci,
            })
            sid += 1

    main_rows = []
    q_rows = []
    for st in students:
        row = {"学号": st["学号"], "姓名": st["姓名"], "班级": st["班级"]}
        for sub, (full, base, sd) in SUBJECTS.items():
            bias = 0.0
            if sub == "数学" and st["_cls"] == 2:
                bias = -0.06
            if sub == "语文" and st["_cls"] == 0:
                bias = 0.05
            ratio = rng.gauss(base + bias + 0.09 * st["_ability"], sd / full)
            score = round(clip(ratio, 0.15, 1.0) * full)
            row[sub] = score

            # 逐题：按知识点平均分配题目
            kps = KNOWLEDGE[sub]
            n_q = len(kps) * 2
            per_q_full = [round(full / n_q, 1)] * n_q
            per_q_full[-1] = round(full - sum(per_q_full[:-1]), 1)
            for qi in range(n_q):
                kp = kps[qi % len(kps)]
                f = per_q_full[qi]
                hard = 0.9 if kp in ("函数与导数", "解析几何", "动量守恒", "生活与哲学") else 1.0
                q_ratio = clip(ratio * hard + rng.gauss(0, 0.12), 0.0, 1.0)
                q_rows.append({
                    "学号": st["学号"], "学科": sub, "题号": qi + 1,
                    "满分": f, "得分": round(q_ratio * f, 1), "知识点": kp,
                })
        main_rows.append(row)

    # 历次：4 次考试成绩与排名
    # 注意：历次表必须带「序号」或「日期」列——只靠考试名称无法可靠判断先后
    # （「期中考试 / 期末考试」这类名称没有数字，字典序会排错，趋势判定会整体反转）。
    hist_rows = []
    exam_plan = [("第1次月考", 1, "2026-03-15"), ("期中考试", 2, "2026-04-25"),
                 ("第2次月考", 3, "2026-05-20"), ("期末考试", 4, "2026-06-30")]
    exams = [e for e, _, _ in exam_plan]
    exam_seq = {e: q for e, q, _ in exam_plan}
    exam_date = {e: d for e, _, d in exam_plan}
    for i, st in enumerate(students):
        total_of = {}
        subj_of = {}
        rank_of = {}
        for ei, exam in enumerate(exams):
            drift = rng.gauss(0.4, 1.2) * ei * (1 if i % 5 else -1)
            t = 0
            per_sub = {}
            for sub, (full, base, sd) in SUBJECTS.items():
                ratio = rng.gauss(base + 0.09 * st["_ability"] + drift * 0.01, sd / full)
                sc = round(clip(ratio, 0.15, 1.0) * full)
                per_sub[sub] = sc
                t += sc
            total_of[exam] = t
            subj_of[exam] = per_sub
        hist_rows.append((st, total_of, subj_of))
    # 计算每次考试的班级排名
    by_exam = {e: sorted(hist_rows, key=lambda x: -x[1][e]) for e in exams}
    rank_map = {}
    for e, lst in by_exam.items():
        for i, (st, _, _) in enumerate(lst, 1):
            rank_map[(st["学号"], e)] = i
    rows_out = []
    for st, tot, subj in hist_rows:
        for e in exams:
            rows_out.append([st["学号"], st["姓名"], st["班级"], e, tot[e]] +
                            [subj[e][s] for s in SUBJECTS] +
                            [rank_map[(st["学号"], e)], exam_seq[e], exam_date[e]])

    try:
        from openpyxl import Workbook
    except ImportError:
        raise SystemExit("需要 openpyxl：pip install openpyxl")

    wb = Workbook()
    ws = wb.active
    ws.title = "成绩"
    headers = ["学号", "姓名", "班级"] + list(SUBJECTS.keys())
    ws.append(headers)
    for r in main_rows:
        ws.append([r.get(h) for h in headers])

    ws2 = wb.create_sheet("逐题")
    ws2.append(["学号", "学科", "题号", "满分", "得分", "知识点"])
    for r in q_rows:
        ws2.append([r["学号"], r["学科"], r["题号"], r["满分"], r["得分"], r["知识点"]])

    ws3 = wb.create_sheet("历次")
    # 历次表除「总分」外还给出**各学科分数**（可选的宽表写法）——
    # 有了它，报告的「历次成绩对比」就能给出历次年级 / 历次班级的各学科四率。
    ws3.append(["学号", "姓名", "班级", "考试", "总分"] + list(SUBJECTS.keys()) +
               ["排名", "序号", "日期"])
    for r in rows_out:
        ws3.append(r)

    wb.save(args.out)
    print("[OK] 已生成示例数据：%s" % args.out)
    print("     主表「成绩」%d 行 / 逐题表 %d 行 / 历次表 %d 行" % (len(main_rows), len(q_rows), len(rows_out)))


if __name__ == "__main__":
    main()
