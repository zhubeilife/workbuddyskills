# -*- coding: utf-8 -*-
"""表头/工作表解析单测：标题行、双行合并表头、多工作表、平时趋势。

对应真实成绩册最常见的三种"脏"结构，以及用户口径「6 次平时保留趋势不取均值」。

跑法（用装了 openpyxl 的解释器）：
  python test_workbook_layout.py
"""
import json
import os
import subprocess
import sys
import tempfile

from openpyxl import Workbook

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from read_workbook import read_workbook, sheet_kind, trend_columns  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PREP = os.path.join(HERE, "prepare_roster.py")
PY = sys.executable

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("%s %s%s" % ("✓" if cond else "✗", name,
                       ("  → " + str(detail)) if (detail and not cond) else ""))


def run(cmd):
    p = subprocess.run([PY] + cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def prep(tmp, tag, extra=None, name="成绩册.xlsx"):
    out = os.path.join(tmp, "roster_%s.json" % tag)
    cmd = [PREP, "--scores", os.path.join(tmp, name), "--out", out, "--class-name", "初一3班"]
    cmd += (extra or [])
    code, log = run(cmd)
    data = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
    return code, log, data


def put(ws, row, col, value):
    ws.cell(row=row, column=col).value = value


def add_exam_sheet(wb, title, rows, subjects=("数学", "语文")):
    """加一张「标题行 + 单行表头」的考试表。rows = [(学号, 姓名, 各科...), ...]"""
    ws = wb.create_sheet(title)
    ws.merge_cells(start_row=1, start_column=1, end_row=1,
                   end_column=2 + len(subjects) + 2)
    put(ws, 1, 1, "初一3班 %s表（各科满分100）" % title)
    names = ["学号", "姓名"] + list(subjects) + ["总成绩", "排名"]
    for j, h in enumerate(names, 1):
        put(ws, 2, j, h)
    for i, r in enumerate(rows, 3):
        for j, v in enumerate(r, 1):
            put(ws, i, j, v)
    return ws


def add_trend_sheet(wb, title, subjects, series):
    """加一张「标题行 + 双行合并表头」的平时成绩表。

    series: [(学号, 姓名, {学科: [第1次...第N次]}), ...]
    """
    ws = wb.create_sheet(title)
    first = series[0][2]
    n = len(next(iter(first.values())))
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=2 + n * len(subjects))
    put(ws, 1, 1, "初一3班 %s表（%d 次）" % (title, n))
    ws.merge_cells(start_row=2, start_column=1, end_row=3, end_column=1)
    put(ws, 2, 1, "学号")
    ws.merge_cells(start_row=2, start_column=2, end_row=3, end_column=2)
    put(ws, 2, 2, "姓名")
    for k in range(n):
        c0 = 3 + k * len(subjects)
        ws.merge_cells(start_row=2, start_column=c0, end_row=2, end_column=c0 + len(subjects) - 1)
        put(ws, 2, c0, "第%d次" % (k + 1))
        for j, sub in enumerate(subjects):
            put(ws, 3, c0 + j, sub)
    for i, (sid, nm, cols) in enumerate(series, 4):
        put(ws, i, 1, sid)
        put(ws, i, 2, nm)
        # 表头是「按次分块」（第k次：数学/语文/英语…），所以数据也按次优先排列
        for k, sub in enumerate(subjects):
            for j, v in enumerate(cols[sub]):
                put(ws, i, 3 + j * len(subjects) + k, v)
    return ws


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tgt = os.path.join(tmp, "成绩册.xlsx")

        print("=" * 68)
        print("A 首行即表头（单行）→ 不误判成双行表头")
        wb = Workbook()
        ws = wb.active
        ws.title = "期末考试成绩"
        put(ws, 1, 1, "学号"); put(ws, 1, 2, "姓名"); put(ws, 1, 3, "语文"); put(ws, 1, 4, "数学")
        for i, r in enumerate([(2001, "张三", 90, 80), (2002, "李四", 70, 60)], 2):
            for j, v in enumerate(r, 1):
                put(ws, i, j, v)
        wb.save(tgt)
        code, log, d = prep(tmp, "A")
        check("A1 正常出结果", code == 0, log[-400:])
        check("A2 学科列没被拼坏",
              d and d["meta"]["学科"] == ["语文", "数学"], d and d["meta"]["学科"])
        check("A3 没有平时趋势", d and not any(s.get("平时趋势") for s in d["roster"]))
        check("A4 单元测试：形态判为成绩表", sheet_kind(read_workbook(tgt)[0]["headers"]) == "scores")

        print("=" * 68)
        print("B 第 1 行是合并大标题 → 自动跳过，定位真表头")
        wb = Workbook()
        ws = wb.active
        ws.title = "期末考试成绩"
        ws.merge_cells("A1:D1")
        ws["A1"] = "初一3班 期末考试成绩表（各科满分100）"
        for j, h in enumerate(["学号", "姓名", "语文", "数学"], 1):
            put(ws, 2, j, h)
        for i, r in enumerate([(2001, "张三", 90, 80), (2002, "李四", 70, 60)], 3):
            for j, v in enumerate(r, 1):
                put(ws, i, j, v)
        wb.save(tgt)
        code, log, d = prep(tmp, "B")
        check("B1 正常出结果", code == 0, log[-400:])
        check("B2 主键列找到了", d and [s["姓名"] for s in d["roster"]] == ["张三", "李四"],
              d and [(s["学号"], s["姓名"]) for s in d["roster"]])
        check("B3 提示写明跳过了标题行",
              d and any("跳过" in n for n in d["对齐说明"]["机器提示"]))
        check("B4 单元测试：表头行 = 第 2 行",
              read_workbook(tgt)[0]["meta"]["表头行"] == 2)

        print("=" * 68)
        print("C 标题行 + 双行合并表头（第N次 × 学科）→ 拼成「第1次-数学」")
        wb = Workbook()
        wb.remove(wb.active)
        subj = ["数学", "语文", "英语"]
        series = [(2001, "张三", {"数学": [70, 72, 74, 80, 82, 84],
                                  "语文": [90, 90, 91, 90, 92, 91],
                                  "英语": [60, 61, 62, 63, 64, 65]}),
                  (2002, "李四", {"数学": [90, 88, 86, 85, 84, 83],
                                  "语文": [80, 81, 82, 83, 84, 85],
                                  "英语": [70, 71, 72, 73, 74, 75]})]
        add_trend_sheet(wb, "平时成绩", subj, series)
        add_exam_sheet(wb, "期末考试成绩",
                       [(2001, "张三", 84, 91, 65, 240, 1),
                        (2002, "李四", 83, 85, 75, 243, 2)], subjects=subj)
        wb.save(tgt)

        sheets = read_workbook(tgt)
        trend_ws = [s for s in sheets if s["sheet"] == "平时成绩"][0]
        check("C1 双行表头被识别为两行", trend_ws["meta"]["表头行数"] == 2, trend_ws["meta"])
        check("C2 列名拼成「第1次-数学」",
              trend_ws["headers"][:5] == ["学号", "姓名", "第1次-数学", "第1次-语文", "第1次-英语"],
              trend_ws["headers"][:5])
        check("C3 末尾一块没被截断（第6次-英语 在列名里）",
              trend_ws["headers"][-1] == "第6次-英语", trend_ws["headers"][-1])
        check("C4 趋势列整理出 3 门课 × 6 次",
              len(trend_columns(trend_ws["headers"])) == 3
              and all(len(v) == 6 for v in trend_columns(trend_ws["headers"]).values()))
        check("C5 单元测试：形态判为平时表", sheet_kind(trend_ws["headers"]) == "trend")

        code, log, d = prep(tmp, "C")
        check("C6 整链路正常出结果", code == 0, log[-400:])
        check("C7 双行表头与趋势取用都写进了提示",
              d and any("双行表头" in n for n in d["对齐说明"]["机器提示"])
              and any("不取均值" in n for n in d["对齐说明"]["机器提示"]), log[-400:])
        t = (d["roster"][0].get("平时趋势") or {}).get("数学", {}) if d else {}
        check("C8 数学逐次序列完整保留", t.get("逐次") == [70, 72, 74, 80, 82, 84], t)
        check("C9 没有产出均值字段", "均值" not in t, list(t.keys()))
        check("C10 方向判为上行", t.get("方向") == "上行", t.get("方向"))
        check("C11 跨度算对", t.get("跨度") == 14, t.get("跨度"))
        check("C12 本次成绩仍取期末表",
              d and d["meta"]["工作表"]["本次成绩"] == "期末考试成绩",
              d and d["meta"].get("工作表"))

        print("=" * 68)
        print("D 双行表头里夹着非学科列（「总分」）→ 不拼接")
        wb = Workbook()
        ws = wb.active
        ws.title = "期末考试成绩"
        ws.merge_cells("A1:E1")
        ws["A1"] = "标题行"
        put(ws, 2, 1, "学号"); put(ws, 2, 2, "姓名")
        ws.merge_cells("C2:D2")
        put(ws, 2, 3, "本次")
        put(ws, 2, 5, "总分")
        put(ws, 3, 3, "数学"); put(ws, 3, 4, "语文")
        for i, r in enumerate([(2001, "张三", 80, 90, 170), (2002, "李四", 60, 70, 130)], 4):
            for j, v in enumerate(r, 1):
                put(ws, i, j, v)
        wb.save(tgt)
        hs = read_workbook(tgt)[0]["headers"]
        check("D1 单元测试：总分列没被拼上次数",
              "总分" in hs and not any(h.endswith("-总分") for h in hs), hs)
        code, log, d = prep(tmp, "D")
        check("D2 正常出结果", code == 0, log[-400:])
        check("D3 总分取值正确",
              d and d["roster"][0]["成绩"]["总分"] == 170,
              d and d["roster"][0]["成绩"].get("总分"))

        print("=" * 68)
        print("E 多工作表（平时 / 期中 / 期末）→ 自动分流本次 / 上次 / 平时")
        wb = Workbook()
        wb.remove(wb.active)
        add_trend_sheet(wb, "平时成绩", ["数学", "语文"],
                        [(2001, "张三", {"数学": [60, 62], "语文": [90, 92]}),
                         (2002, "李四", {"数学": [70, 72], "语文": [80, 82]})])
        add_exam_sheet(wb, "期中考试成绩",
                       [(2001, "张三", 70, 71, 141, 2), (2002, "李四", 75, 79, 154, 1)])
        add_exam_sheet(wb, "期末考试成绩",
                       [(2001, "张三", 80, 81, 161, 1), (2002, "李四", 85, 84, 169, 2)])
        wb.save(tgt)
        code, log, d = prep(tmp, "E")
        check("E1 正常出结果", code == 0, log[-400:])
        check("E2 本次自动取期末",
              d and d["meta"]["工作表"]["本次成绩"] == "期末考试成绩", d and d["meta"]["工作表"])
        check("E3 上次对比自动取期中",
              d and d["meta"]["工作表"]["上次对比"] == "期中考试成绩")
        check("E4 平时趋势自动取平时成绩",
              d and d["meta"]["工作表"]["平时趋势"] == "平时成绩")
        z = d["roster"][0]["成绩"] if d else {}
        check("E5 总分变化算对（张三 141→161，+20）",
              z.get("上次总分") == 141 and z.get("总分变化") == 20, z)
        check("E6 排名变化算对（张三 2→1，+1）",
              z.get("上次排名") == 2 and z.get("排名变化") == 1, z)
        check("E7 上次各科带过来了",
              z.get("上次各科") == {"数学": 70, "语文": 71}, z.get("上次各科"))
        check("E8 平时趋势与本次学科同名",
              d and set(d["roster"][0]["平时趋势"]) == {"数学", "语文"},
              d and list(d["roster"][0].get("平时趋势", {})))

        print("=" * 68)
        print("F 两张成绩表且名字看不出先后 → 报错要求指定")
        wb = Workbook()
        ws = wb.active
        ws.title = "表一"
        for j, h in enumerate(["学号", "姓名", "数学"], 1):
            put(ws, 1, j, h)
        put(ws, 2, 1, 2001); put(ws, 2, 2, "张三"); put(ws, 2, 3, 80)
        ws2 = wb.create_sheet("表二")
        for j, h in enumerate(["学号", "姓名", "数学"], 1):
            put(ws2, 1, j, h)
        put(ws2, 2, 1, 2001); put(ws2, 2, 2, "张三"); put(ws2, 2, 3, 60)
        wb.save(tgt)
        code, log, d = prep(tmp, "F")
        check("F1 非零退出", code != 0, log[-300:])
        check("F2 提示用 --scores-sheet", "--scores-sheet" in log)

        print("=" * 68)
        print("G 用 --scores-sheet 指定表一 → 生效")
        code, log, d = prep(tmp, "G", extra=["--scores-sheet", "表一"])
        check("G1 指定生效", code == 0 and d and d["meta"]["工作表"]["本次成绩"] == "表一",
              d and d["meta"].get("工作表"))
        check("G2 名字无先后时不乱猜上次对比",
              d and d["meta"]["工作表"]["上次对比"] is None, d and d["meta"].get("工作表"))

        print("=" * 68)
        print("H 平时趋势缺一次 → 逐次保留空位、特征只按有分数的算")
        wb = Workbook()
        wb.remove(wb.active)
        add_trend_sheet(wb, "平时成绩", ["数学"],
                        [(2001, "张三", {"数学": [70, None, 90]}),
                         (2002, "李四", {"数学": [80, 82, 84]})])
        add_exam_sheet(wb, "期末考试成绩",
                       [(2001, "张三", 88, 200, 1), (2002, "李四", 82, 195, 2)], subjects=["数学"])
        wb.save(tgt)
        code, log, d = prep(tmp, "H")
        t = (d["roster"][0].get("平时趋势") or {}).get("数学", {}) if d else {}
        check("H1 正常出结果", code == 0, log[-400:])
        check("H2 逐次保留空位", t.get("逐次") == [70, None, 90], t.get("逐次"))
        check("H3 记录缺哪一次", t.get("缺次") == [2], t.get("缺次"))
        check("H4 只按有分数的算首末", t.get("首") == 70 and t.get("末") == 90, t)
        check("H5 有分数次数=2", t.get("有分数次数") == 2, t.get("有分数次数"))

    print("=" * 68)
    print("通过 %d / 失败 %d" % (len(PASS), len(FAIL)))
    if FAIL:
        print("失败用例：" + "、".join(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
