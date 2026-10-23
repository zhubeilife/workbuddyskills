# -*- coding: utf-8 -*-
"""多工作表成绩册 → skill 标准输入 适配器。

很多学校的成绩册是一个 xlsx 里塞十几张表：全科成绩汇总、单科表、学科统计、分数段、小题得分明细。
prepare_roster.py 只吃标准单行表头的宽表，所以先跑这个脚本把两样东西抽出来：

  <out-dir>/成绩表_评语输入.xlsx   学号/姓名/班级 + 各科 + 总分 + 班级排名（喂给 --scores）
  <out-dir>/逐题证据.json          每个学生的题型结构与知识点得失（第三段成文时的「具体细节」证据源）

用法：
  python adapt_exam_workbook.py --workbook 成绩册.xlsx --out-dir 工作目录
  python adapt_exam_workbook.py --workbook 成绩册.xlsx --out-dir out --sheet 高二(3)班 --subjects 语文,数学

说明：
- 自动找「全科汇总」类工作表（表头含 学号/考号/学籍号 且含 >=2 个学科列），表头允许不在第一行
- 「逐题」表需为长表：学号|学科|题号|满分|得分[|知识点]；没有这张表时只出宽表，证据降级
- 总分缺失按各科求和；班级排名缺失按总分降序自算
- 客观题判定：题号含「选择题/听力/阅读/完形」归客观，其余归主观（与源表客观题小计口径核对过）
"""
import argparse
import json
import os
import re
import sys

try:
    import openpyxl
    from openpyxl.styles import Alignment, Font
except ImportError:
    sys.exit("本脚本读写 xlsx 需要 openpyxl，请先安装：pip install openpyxl")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from subjects import SUBJECT_POOL  # noqa: E402  学科词表唯一来源（含「道法」等简称）

ID_KEYS = ("学号", "考号", "学籍号")
NAME_KEYS = ("姓名", "学生姓名")
CLASS_KEYS = ("班级",)
TOTAL_KEYS = ("总分", "总成绩", "合计")
RANK_KEYS = ("班级排名", "排名", "名次", "班名次")
OBJ_PAT = re.compile(r"选择题|听力|阅读|完形")


def pick_col(headers, keys):
    for i, h in enumerate(headers):
        if h and any(k == str(h).strip() or k in str(h) for k in keys):
            return i
    return None


def norm(v):
    return "" if v is None else str(v).strip()


def find_scores_sheet(wb, want_class=""):
    """挑出全科汇总类工作表，并返回 (ws, 表头行号)。"""
    best = None
    for ws in wb.worksheets:
        for r, row in enumerate(ws.iter_rows(values_only=True), 1):
            if r > 8:            # 表头最多容忍前 8 行（标题/说明行）
                break
            headers = [norm(c) for c in row]
            if pick_col(headers, ID_KEYS) is None:
                continue
            subs = [h for h in headers if h in SUBJECT_POOL]
            if len(subs) < 2:
                continue
            if want_class and not any(want_class in norm(c) for row2 in ws.iter_rows(min_row=r + 1,
                                                                                    max_row=r + 3,
                                                                                    values_only=True)
                                      for c in row2):
                continue
            best = (ws, r)
            break
        if best:
            break
    if not best:
        raise SystemExit("找不到「全科成绩汇总」类工作表：需要一列学号/考号，且至少 2 个学科列（%s）"
                         % "、".join(SUBJECT_POOL))
    return best


def read_scores(wb, explicit_subjects=""):
    ws, hrow = find_scores_sheet(wb)
    rows = list(ws.iter_rows(values_only=True))
    headers = [norm(c) for c in rows[hrow - 1]]
    i_id, i_name = pick_col(headers, ID_KEYS), pick_col(headers, NAME_KEYS)
    i_cls, i_total, i_rank = pick_col(headers, CLASS_KEYS), pick_col(headers, TOTAL_KEYS), pick_col(headers, RANK_KEYS)
    if explicit_subjects:
        subjects = [s.strip() for s in explicit_subjects.split(",") if s.strip()]
    else:
        subjects = [h for h in headers if h in SUBJECT_POOL]
    if not subjects:
        raise SystemExit("识别不到学科列，请用 --subjects 指定，例如 --subjects 语文,数学,英语")
    students = []
    for r in rows[hrow:]:
        sid = norm(r[i_id]) if i_id is not None else ""
        if not sid:
            continue
        scores = {}
        for s in subjects:
            v = r[headers.index(s)]
            if isinstance(v, (int, float)):
                scores[s] = v
        if not scores:
            continue
        total = r[i_total] if i_total is not None and isinstance(r[i_total], (int, float)) else sum(scores.values())
        students.append({
            "学号": sid,
            "姓名": norm(r[i_name]) if i_name is not None else "",
            "班级": norm(r[i_cls]) if i_cls is not None else "",
            "成绩": scores,
            "总分": total,
            "_原表排名": r[i_rank] if i_rank is not None and isinstance(r[i_rank], (int, float)) else None,
        })
    if not any(s["_原表排名"] for s in students):
        for i, s in enumerate(sorted(students, key=lambda x: -x["总分"]), 1):
            s["班级排名"] = i
    else:
        for s in students:
            s["班级排名"] = s["_原表排名"]
    return students, subjects, ws.title


def read_items(wb):
    """逐题长表 -> {学号: {学科: [{题号,满分,得分,知识点,类型}]}}。找不到就返回 {}。"""
    for ws in wb.worksheets:
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        headers = [norm(c) for c in rows[0]]
        i_id = pick_col(headers, ID_KEYS)
        i_sub = pick_col(headers, ("学科", "科目"))
        i_no = pick_col(headers, ("题号", "小题"))
        i_full = pick_col(headers, ("满分", "分值"))
        i_got = pick_col(headers, ("得分", "分数"))
        if None in (i_id, i_sub, i_no, i_full, i_got):
            continue
        i_kp = pick_col(headers, ("知识点", "考点"))
        items = {}
        for r in rows[1:]:
            sid = norm(r[i_id])
            if not sid:
                continue
            qno = norm(r[i_no])
            items.setdefault(sid, {}).setdefault(norm(r[i_sub]), []).append({
                "题号": qno,
                "满分": r[i_full] or 0,
                "得分": r[i_got] or 0,
                "知识点": norm(r[i_kp]) if i_kp is not None else qno,
                "类型": "客观" if OBJ_PAT.search(qno) else "主观",
            })
        return items
    return {}


def rate(got, full):
    return round(got / full, 4) if full else 0.0


def build_evidence(students, items):
    out = []
    for s in students:
        subs = {}
        for sub, qs in items.get(s["学号"], {}).items():
            obj = [q for q in qs if q["类型"] == "客观"]
            subj = [q for q in qs if q["类型"] == "主观"]
            kp = {}
            for q in qs:
                d = kp.setdefault(q["知识点"], {"得分": 0, "满分": 0})
                d["得分"] += q["得分"]
                d["满分"] += q["满分"]
            kplist = sorted(({"知识点": k, "得分": v["得分"], "满分": v["满分"],
                              "得分率": rate(v["得分"], v["满分"])} for k, v in kp.items()),
                            key=lambda x: -x["得分率"])
            subs[sub] = {
                "总分": s["成绩"].get(sub),
                "得分率": rate(s["成绩"].get(sub, 0), sum(q["满分"] for q in qs)),
                "客观得分率": rate(sum(q["得分"] for q in obj), sum(q["满分"] for q in obj)),
                "主观得分率": rate(sum(q["得分"] for q in subj), sum(q["满分"] for q in subj)),
                "知识点": kplist,
                "最强知识点": kplist[0] if kplist else None,
                "最弱知识点": kplist[-1] if kplist else None,
            }
        by_rate = sorted(subs.items(), key=lambda kv: -kv[1]["得分率"])
        o_avg = sum(v["客观得分率"] for v in subs.values()) / len(subs) if subs else 0
        j_avg = sum(v["主观得分率"] for v in subs.values()) / len(subs) if subs else 0
        diff = o_avg - j_avg
        lean = ("客观题强于主观题" if diff >= 0.05 else
                "主观题强于客观题" if diff <= -0.05 else "客观题与主观题均衡")
        cand = [dict(q, 学科=sub) for sub in subs for q in items.get(s["学号"], {}).get(sub, [])
                if q["满分"] >= 8]
        cand.sort(key=lambda q: -rate(q["得分"], q["满分"]))
        gaps = [q for q in cand if rate(q["得分"], q["满分"]) < 0.65][-3:]
        out.append({
            "学号": s["学号"], "姓名": s["姓名"], "总分": s["总分"], "班级排名": s.get("班级排名"),
            "学科": subs,
            "学科得分率极差": round(by_rate[0][1]["得分率"] - by_rate[-1][1]["得分率"], 4) if by_rate else None,
            "优势学科": by_rate[0][0] if by_rate else None,
            "短板学科": by_rate[-1][0] if by_rate else None,
            "题型倾向": lean,
            "亮点题": [{"学科": q["学科"], "题号": q["题号"], "知识点": q["知识点"],
                        "得分": q["得分"], "满分": q["满分"],
                        "得分率": rate(q["得分"], q["满分"])} for q in cand[:3]],
            "待补题": [{"学科": q["学科"], "题号": q["题号"], "知识点": q["知识点"],
                        "得分": q["得分"], "满分": q["满分"],
                        "得分率": rate(q["得分"], q["满分"])} for q in gaps],
        })
    return out


def write_scores_xlsx(students, subjects, out_dir):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "全科成绩汇总"
    ws.append(["学号", "姓名", "班级"] + subjects + ["总分", "班级排名"])
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")
    for s in students:
        ws.append([s["学号"], s["姓名"], s["班级"]]
                  + [s["成绩"].get(x) for x in subjects] + [s["总分"], s["班级排名"]])
    p = os.path.join(out_dir, "成绩表_评语输入.xlsx")
    wb.save(p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", required=True, help="多工作表成绩册 xlsx")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--sheet", default="", help="限定班级关键字（用于挑选汇总表）")
    ap.add_argument("--subjects", default="", help="留空自动识别")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    wb = openpyxl.load_workbook(args.workbook, data_only=True)
    students, subjects, sheet = read_scores(wb, args.subjects)
    items = read_items(wb)
    p = write_scores_xlsx(students, subjects, args.out_dir)
    ev = build_evidence(students, items)
    with open(os.path.join(args.out_dir, "逐题证据.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": {"班级": args.sheet or students[0]["班级"], "人数": len(ev),
                            "来源表": sheet, "学科": subjects},
                   "evidence": ev}, f, ensure_ascii=False, indent=2)
    print("成绩表 -> %s（%d 人，%d 科，取自工作表「%s」）" % (p, len(students), len(subjects), sheet))
    if items:
        print("逐题证据 -> 逐题证据.json（%d 人有分题明细，可作为评语「具体细节」证据源）"
              % sum(1 for e in ev if e["学科"]))
    else:
        print("逐题证据 -> 未找到逐题长表，已跳过；评语只能依赖学科得分率，具体细节会变弱")


if __name__ == "__main__":
    main()
