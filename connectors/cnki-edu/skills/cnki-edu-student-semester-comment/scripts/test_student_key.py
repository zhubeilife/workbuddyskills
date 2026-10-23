# -*- coding: utf-8 -*-
"""主键规则单测。

覆盖三条规则：
  1. 成绩表有学号列（且非全空）→ 主键 = 学号，姓名并存
  2. 没有学号列 / 整列为空 → 忽略学号，主键 = 姓名
  3. 无学号且同名学生 → 按出现顺序编「张三1号」「张三2号」

以及三条附带的匹配行为：
  4. 重复学号 → 直接报错停止
  5. 附表没有学号列 → 能按姓名接上（无论名单有没有学号）
  6. 同名多人 + 附表无学号 → 按出现顺序对应，并给出人工核对提示

跑法（用装了 openpyxl 的解释器）：
  python test_student_key.py
"""
import json
import os
import subprocess
import sys
import tempfile

from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))
PREP = os.path.join(HERE, "prepare_roster.py")
EXPORT = os.path.join(HERE, "export_comments.py")
PY = sys.executable

PASS, FAIL = [], []


def xlsx(path, rows):
    wb = Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    wb.save(path)
    return path


def run(cmd):
    p = subprocess.run([PY] + cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def prep(tmp, scores, homework=None, notes=None, tag=""):
    out = os.path.join(tmp, "roster_%s.json" % tag)
    cmd = [PREP, "--scores", scores, "--out", out, "--class-name", "初一"]
    if homework:
        cmd += ["--homework", homework]
    if notes:
        cmd += ["--notes", notes]
    code, log = run(cmd)
    data = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
    return code, log, data


def keys_of(data):
    return [s["学号"] for s in data["roster"]]


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("%s %s%s" % ("✓" if cond else "✗", name, ("  → " + detail) if detail and not cond else ""))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        print("=" * 68)
        print("A 无学号列 → 以姓名为主键")
        s = xlsx(os.path.join(tmp, "A.xlsx"),
                 [["姓名", "语文", "数学"], ["张三", 90, 80], ["李四", 70, 60]])
        code, log, d = prep(tmp, s, tag="A")
        check("A1 正常出结果", code == 0, log[-300:])
        check("A2 主键 = 姓名", d and keys_of(d) == ["张三", "李四"], str(keys_of(d) if d else None))
        check("A3 meta 标注主键为姓名", d and d["meta"]["主键"] == "姓名")
        check("A4 提示里写明忽略学号",
              d and any("没有学号列" in n or "整列为空" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("B 无学号 + 重名 → 按出现顺序编 1号 / 2号")
        s = xlsx(os.path.join(tmp, "B.xlsx"),
                 [["姓名", "语文"], ["张三", 90], ["李四", 70], ["张三", 50]])
        code, log, d = prep(tmp, s, tag="B")
        check("B1 正常出结果（不再报错停止）", code == 0, log[-300:])
        check("B2 排前面的为 1 号", d and keys_of(d) == ["张三1号", "李四", "张三2号"],
              str(keys_of(d) if d else None))
        g = {x["学号"]: x["成绩"]["语文"] for x in (d["roster"] if d else [])}
        check("B3 成绩没串位（1号=90 / 2号=50）", g.get("张三1号") == 90 and g.get("张三2号") == 50, str(g))
        check("B4 提示要求人工核对",
              d and any("同名学生" in n and "顺序" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("C 有学号 + 有姓名 → 主键 = 学号")
        s = xlsx(os.path.join(tmp, "C.xlsx"),
                 [["学号", "姓名", "语文"], ["2001", "张三", 90], ["2002", "李四", 70]])
        code, log, d = prep(tmp, s, tag="C")
        check("C1 正常出结果", code == 0, log[-300:])
        check("C2 主键 = 学号", d and keys_of(d) == ["2001", "2002"], str(keys_of(d) if d else None))
        check("C3 姓名并存", d and [x["姓名"] for x in d["roster"]] == ["张三", "李四"])
        check("C4 主键来源标记为学号",
              d and all(x["主键来源"] == "学号" for x in d["roster"]))

        print("=" * 68)
        print("D 有学号列但整列为空 → 退化为姓名主键")
        s = xlsx(os.path.join(tmp, "D.xlsx"),
                 [["学号", "姓名", "语文"], [None, "张三", 90], [None, "李四", 70]])
        code, log, d = prep(tmp, s, tag="D")
        check("D1 正常出结果", code == 0, log[-300:])
        check("D2 主键 = 姓名", d and keys_of(d) == ["张三", "李四"], str(keys_of(d) if d else None))

        print("=" * 68)
        print("E 同一学号出现两次 → 直接报错停止")
        s = xlsx(os.path.join(tmp, "E.xlsx"),
                 [["学号", "姓名", "语文"], ["2001", "张三", 90], ["2001", "李四", 80]])
        code, log, d = prep(tmp, s, tag="E")
        check("E1 非零退出", code != 0)
        check("E2 报错点明重复学号", "重复学号" in log, log[-300:])

        print("=" * 68)
        print("F 有学号 + 重名（不同学号同名）→ 不编号，靠学号区分")
        s = xlsx(os.path.join(tmp, "F.xlsx"),
                 [["学号", "姓名", "语文"], ["2001", "张三", 90], ["2002", "张三", 80]])
        code, log, d = prep(tmp, s, tag="F")
        check("F1 正常出结果", code == 0, log[-300:])
        check("F2 不编号", d and keys_of(d) == ["2001", "2002"], str(keys_of(d) if d else None))
        check("F3 提示重名需人工核对",
              d and any("重名" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("G 附表没有学号列 → 按姓名接上（名单以姓名为主键）")
        s = xlsx(os.path.join(tmp, "G.xlsx"),
                 [["姓名", "语文"], ["张三", 90], ["李四", 70]])
        hw = xlsx(os.path.join(tmp, "G_hw.xlsx"),
                  [["姓名", "应交次数", "实交次数"], ["张三", 10, 10], ["李四", 10, 8]])
        code, log, d = prep(tmp, s, homework=hw, tag="G")
        h = {x["姓名"]: x["作业"] for x in (d["roster"] if d else [])}
        check("G1 两张表接上", code == 0 and h.get("张三") and h.get("李四"), str(h))
        check("G2 欠交次数算对", h.get("李四", {}).get("欠交次数") == 2, str(h))

        print("=" * 68)
        print("H 重名 + 附表无学号 → 按出现顺序对应")
        s = xlsx(os.path.join(tmp, "H.xlsx"),
                 [["姓名", "语文"], ["张三", 90], ["李四", 70], ["张三", 50]])
        hw = xlsx(os.path.join(tmp, "H_hw.xlsx"),
                  [["姓名", "应交次数", "实交次数"],
                   ["张三", 10, 10], ["李四", 10, 9], ["张三", 10, 3]])
        code, log, d = prep(tmp, s, homework=hw, tag="H")
        h = {x["学号"]: x["作业"] for x in (d["roster"] if d else [])}
        check("H1 两个张三各自接上",
              h.get("张三1号", {}).get("欠交次数") == 0 and h.get("张三2号", {}).get("欠交次数") == 7,
              str(h))
        check("H2 提示要求人工核对",
              d and any("出现顺序" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("I 名单有学号、附表学号是名单外的 → 判名单外，不用姓名兜底")
        s = xlsx(os.path.join(tmp, "I.xlsx"),
                 [["学号", "姓名", "语文"], ["2001", "张三", 90], ["2002", "李四", 70]])
        nt = xlsx(os.path.join(tmp, "I_notes.xlsx"),
                  [["学号", "姓名", "教师描述"], ["9999", "张三", "上课爱发言，作业工整"]])
        code, log, d = prep(tmp, s, notes=nt, tag="I")
        un = d["对齐说明"]["未匹配记录"] if d else []
        check("I1 判为名单外", any("名单外" in u["原因"] for u in un), str(un))
        check("I2 没有被接到张三头上",
              not any(x["教师描述"] for x in (d["roster"] if d else [])))

        print("=" * 68)
        print("J 出表端：评语只写姓名、主键留空 → 也能对账")
        s = xlsx(os.path.join(tmp, "J.xlsx"),
                 [["姓名", "语文"], ["张三", 90], ["李四", 70]])
        code, log, d = prep(tmp, s, tag="J")
        rp = os.path.join(tmp, "roster_J.json")
        cm = os.path.join(tmp, "comments_J.json")
        body = ("这一学期的语文课上，该生从开学第一次记录起就把位置守住了，" * 3)
        json.dump({"comments": [
            {"学号": "", "姓名": "张三", "评语正文": body},
            {"学号": "", "姓名": "李四", "评语正文": body},
        ]}, open(cm, "w", encoding="utf-8"), ensure_ascii=False)
        code, log = run([EXPORT, "--roster", rp, "--comments", cm,
                         "--out", os.path.join(tmp, "out.xlsx")])
        check("J1 没有硬错误（不漏写）", code == 0 and "漏写" not in log, log[-400:])
        check("J2 提示已按姓名接上", "[对账]" in log, log[-400:])

    print("=" * 68)
    print("通过 %d / 失败 %d" % (len(PASS), len(FAIL)))
    if FAIL:
        print("失败用例：" + "、".join(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
