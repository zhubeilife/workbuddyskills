# -*- coding: utf-8 -*-
"""「道法 = 道德与法治」同义归一的针对性单测（含反例）。

跑法：python test_subject_alias.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PREPARE = os.path.join(HERE, "prepare_roster.py")

CASES = [
    # (用例名, 表头, 期望学科集合, 期望提示关键词)
    ("A 只用简称「道法」", ["学号", "姓名", "语文", "道法", "数学"],
     {"语文", "道法", "数学"}, None),
    ("B 简称+全称并存（须去重）", ["学号", "姓名", "语文", "道法", "道德与法治", "数学"],
     {"语文", "道法", "数学"}, "同一门课"),
    ("C 历史列与简称同门（不得救回）", ["学号", "姓名", "语文", "道法", "期中道德与法治", "数学"],
     {"语文", "道法", "数学"}, "历史成绩列"),
    ("D 历史列确实是新学科（必须救回）", ["学号", "姓名", "语文", "数学", "期中物理"],
     {"语文", "数学", "期中物理"}, "已按本次成绩使用"),
    ("E 只用全称「道德与法治」", ["学号", "姓名", "语文", "道德与法治", "数学"],
     {"语文", "道德与法治", "数学"}, None),
    ("F 别称「德法」", ["学号", "姓名", "语文", "德法", "数学"],
     {"语文", "德法", "数学"}, None),
]


def build(path, headers):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for i, name in enumerate(["甲", "乙", "丙"], 1):
        row = []
        for h in headers:
            if h == "学号":
                row.append("S%03d" % i)
            elif h == "姓名":
                row.append(name)
            else:
                row.append(70 + i + len(h) % 7)
        ws.append(row)
    wb.save(path)


def run_case(name, headers, want_subjects, want_note):
    tmp = tempfile.mkdtemp(prefix="subjtest_")
    try:
        src = os.path.join(tmp, "成绩表.xlsx")
        out = os.path.join(tmp, "roster.json")
        build(src, headers)
        p = subprocess.run(
            [sys.executable, PREPARE, "--scores", src, "--out", out],
            capture_output=True, text=True, encoding="utf-8")
        if p.returncode != 0:
            return name, False, "脚本非零退出：%s" % (p.stdout + p.stderr).strip()[:300]
        import json
        d = json.load(open(out, encoding="utf-8"))
        got = set(d["meta"]["学科"])
        notes = " ".join(d["对齐说明"]["机器提示"])
        if got != want_subjects:
            return name, False, "学科集不符：期望 %s，实际 %s" % (sorted(want_subjects), sorted(got))
        if want_note and want_note not in notes:
            return name, False, "缺少预期提示「%s」；实际提示：%s" % (want_note, notes or "（空）")
        if not want_note:
            # 用例 A/E/F 不应出现「历史成绩列」「同一门课」这类多余提示
            for bad in ("同一门课", "历史成绩列"):
                if bad in notes:
                    return name, False, "出现不该有的提示「%s」：%s" % (bad, notes)
        return name, True, "学科 %s" % "、".join(sorted(got))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_explicit_alias():
    """--subjects 传简称、表里写全称，应能对上并给出提示。"""
    tmp = tempfile.mkdtemp(prefix="subjtest_")
    try:
        src = os.path.join(tmp, "成绩表.xlsx")
        out = os.path.join(tmp, "roster.json")
        build(src, ["学号", "姓名", "语文", "道德与法治", "数学"])
        p = subprocess.run([sys.executable, PREPARE, "--scores", src,
                            "--subjects", "语文,道法,数学", "--out", out],
                           capture_output=True, text=True, encoding="utf-8")
        if p.returncode != 0:
            return "--subjects 传简称", False, (p.stdout + p.stderr).strip()[:300]
        import json
        d = json.load(open(out, encoding="utf-8"))
        got = set(d["meta"]["学科"])
        if got != {"语文", "道德与法治", "数学"}:
            return "--subjects 传简称", False, "学科集不符：%s" % sorted(got)
        if "同学科的不同写法" not in " ".join(d["对齐说明"]["机器提示"]):
            return "--subjects 传简称", False, "未提示已按同学科写法匹配"
        return "--subjects 传简称", True, "已对到「道德与法治」"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    fails = 0
    for c in CASES:
        nm, ok, detail = run_case(*c)
        print(("  ✓ " if ok else "  ✗ ") + nm + " → " + detail)
        fails += 0 if ok else 1
    nm, ok, detail = run_explicit_alias()
    print(("  ✓ " if ok else "  ✗ ") + nm + " → " + detail)
    fails += 0 if ok else 1
    print("\n%s（%d 个用例，失败 %d）" % ("全部通过" if not fails else "存在失败", len(CASES) + 1, fails))
    sys.exit(1 if fails else 0)
