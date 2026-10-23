# -*- coding: utf-8 -*-
"""输入边界单测（2026-10-09 缺陷审计的回归测试）。

覆盖审计里 P0/P1/P2 各条实测复现过的缺陷：
  · 排名列优先级：「年级排名」写在「班级排名」前面时，班级排名必须取对
  · 同表「期中总分/期中排名」：本次总分/排名不得取到期中列
  · 学号/考号并存：以学号为主键
  · 学号列部分为空：报错中止，绝不混用两种主键
  · norm_id：学号「1.05」不得被改成「15」
  · --scores 传 CSV 能跑通；传 .xls 是友好拒绝而不是 traceback
  · 「只有教师描述」的降级路径（SKILL 常见问题里的用法）能跑通
  · 成绩表底部统计行（「班级平均」「年级最高」）不当学生
  · 选考/走班科目（物理 18/40 人有成绩）保留、未选考者不计缺考
  · 「语文等级」按文本等级列剔除（文案不再说成"同一门课"）
  · 附表多工作表：数据在第二张时能选中
  · 出表端：评语姓名与名单不符 → 拒绝配对（防串人）
  · 出表端：允许「第3次冲到 96」这类平时序列数字，「考了87」仍报
  · 出表端：平时序列表述口径——标准式「学科+第X次平时成绩NN分」放行，
    省略式「第1次的 74 涨到第6次的 87」「平时线」不给过
  · 出表端：--skip-tips 按固定编号跳，材料给全也不失效
  · 查重端：0 条评语不再崩
  · 成绩分在多个文件（期末/期中/平时各一个 xlsx，工作表名都是通用名）：
    一起传 --scores 能按文件名贴标签并自动分流；逗号分隔写法可用；
    单文件时提醒同目录的其他成绩文件；文件名看不出先后时报错；--scores-sheet 可用文件名标签指到
  · 往年评语作为「个性化描述的参考」：进 roster 的「往年评语」字段（与「教师描述」分开）、
    名单外学号不兜底、缺文件报错、缺人进「缺失项」、小贴士第 1 条改口径、
    跨年照搬命中而改写不误报（短句不参与比对）、similarity_check --past 命令行可用
  · 荣誉材料（奖状/证书/荣誉榜）：--awards 进 roster 的「荣誉奖项」（与教师描述/往年评语分字段）、
    一人多条合并、学号留空时按姓名接、名单外不兜底、--award-col 与「最长文本列」兜底、
    **未覆盖荣誉的人不进「缺失项」**（荣誉不是人人都有；与教师描述对照）
  · 图片通道：把 .png/.jpg/.pdf 传给 --scores 或 --awards → 友好拒绝（不是 openpyxl traceback），
    拒绝文案带三条硬口径指引（回读确认 / 留空 / 图上明确标注）
  · 荣誉表述的材料出处闸门 award_flags：无出处要报、有出处放行、泛词不误报、
    「往年评语」刻意不算出处；40 条示例评语必须 0 命中

跑法（用装了 openpyxl 的解释器）：
  python test_input_edges.py
"""
import json
import os
import subprocess
import sys
import tempfile

from openpyxl import Workbook, load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PREP = os.path.join(HERE, "prepare_roster.py")
EXPORT = os.path.join(HERE, "export_comments.py")
SIM = os.path.join(HERE, "similarity_check.py")
PY = sys.executable

import export_comments as EC        # noqa: E402
import prepare_roster as PR         # noqa: E402
import similarity_check as SC       # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("%s %s%s" % ("✓" if cond else "✗", name,
                       ("  → " + str(detail)) if (detail and not cond) else ""))


def run(cmd):
    p = subprocess.run([PY] + cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def xlsx(path, rows, title=None):
    wb = Workbook()
    ws = wb.active
    if title:
        ws.title = title
    for r in rows:
        ws.append(r)
    wb.save(path)
    return path


def prep(scores, out, extra=None):
    cmd = [PREP, "--scores", scores, "--out", out, "--class-name", "初一"]
    cmd += (extra or [])
    code, log = run(cmd)
    data = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
    return code, log, data


def tips_of(data):
    return [s.get("分层建议") for s in data["roster"]]


def main():
    with tempfile.TemporaryDirectory() as tmp:
        print("=" * 68)
        print("A 单元：「年级排名」在「班级排名」前面 → 班级排名仍取对")
        hs = ["学号", "姓名", "语文", "数学", "年级排名", "班级排名"]
        rows = [["2001", "张三", 90, 80, 12, 3], ["2002", "李四", 70, 60, 40, 9]]
        check("A1 班级排名列 = 班级排名（不是年级排名）",
              PR.find_col_exact_first(hs, PR.RANK_KEYS) == 5,
              PR.find_col_exact_first(hs, PR.RANK_KEYS))
        check("A2 关键词优先级生效（班级排名 优先于 泛化「排名」）",
              PR.find_col(["排名", "班级排名"], PR.RANK_KEYS) == 1,
              PR.find_col(["排名", "班级排名"], PR.RANK_KEYS))
        check("A3 泛化「排名」会命中「年级排名」→ 必须靠 exclude 排掉（main 已排）",
              PR.find_col(["年级排名", "排名"], PR.RANK_KEYS) == 0
              and PR.find_col(["年级排名", "排名"], PR.RANK_KEYS, exclude={0}) == 1)
        check("A4 学号优先于考号（#13）",
              PR.find_col(["考号", "学号", "姓名"], PR.ID_KEYS) == 1)

        p = xlsx(os.path.join(tmp, "rank.xlsx"), [hs] + rows)
        code, log, d = prep(p, os.path.join(tmp, "rank.json"))
        g = d["roster"][0]["成绩"] if d else {}
        check("A5 张三班级排名 = 3", code == 0 and g.get("班级排名") == 3.0, g.get("班级排名"))
        check("A6 提示说明年级排名未使用",
              d and any("年级排名" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("B 单元：只有「年级排名」→ 不做排名分析（不拿它当班级排名）")
        p = xlsx(os.path.join(tmp, "grank.xlsx"),
                 [["学号", "姓名", "语文", "年级排名"], ["2001", "张三", 90, 12]])
        code, log, d = prep(p, os.path.join(tmp, "grank.json"))
        g = d["roster"][0]["成绩"] if d else {}
        check("B1 不产出「班级排名」", code == 0 and "班级排名" not in g, list(g))
        check("B2 提示已说明原因",
              d and any("只有" in n and "年级" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("C 单元：同表「期中总分/期中排名」→ 本次不取期中列")
        p = xlsx(os.path.join(tmp, "mid.xlsx"),
                 [["学号", "姓名", "期末语文", "期中总分"], ["2001", "张三", 95, 250]])
        code, log, d = prep(p, os.path.join(tmp, "mid.json"))
        g = d["roster"][0]["成绩"] if d else {}
        check("C1 本次总分 = 期末语文求和（95），不是期中 250",
              code == 0 and g.get("总分") == 95.0, g.get("总分"))
        check("C2 不同源 → 不产出「总分变化」",
              "总分变化" not in g and "上次总分" not in g, list(g))
        check("C3 提示说明为什么不生成变化",
              d and any("不生成" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("D 单元：SKILL 推荐的「期末总分 + 期中总分」 → 变化正常生成")
        p = xlsx(os.path.join(tmp, "ok.xlsx"),
                 [["学号", "姓名", "期中语文", "期末语文", "期中总分", "期末总分",
                   "期中排名", "期末排名"],
                  ["2001", "张三", 70, 80, 200, 220, 5, 3]])
        code, log, d = prep(p, os.path.join(tmp, "ok.json"))
        g = d["roster"][0]["成绩"] if d else {}
        check("D1 本次总分取「期末总分」", code == 0 and g.get("总分") == 220.0, g.get("总分"))
        check("D2 上次总分取「期中总分」", g.get("上次总分") == 200.0, g.get("上次总分"))
        check("D3 总分变化 = +20", g.get("总分变化") == 20.0, g.get("总分变化"))
        check("D4 班级排名取「期末排名」", g.get("班级排名") == 3.0, g.get("班级排名"))
        check("D5 排名变化 = +2", g.get("排名变化") == 2, g.get("排名变化"))
        check("D6 meta.选考科目 为空", d and d["meta"].get("选考科目") == [])

        print("=" * 68)
        print("E 单元：norm_id 只去「浮点尾巴 .0」")
        check("E1 1.05 不被改成 15", PR.norm_id("1.05") == "1.05", PR.norm_id("1.05"))
        check("E2 20240.05 保持", PR.norm_id("20240.05") == "20240.05", PR.norm_id("20240.05"))
        check("E3 2001.0 → 2001", PR.norm_id(2001.0) == "2001", PR.norm_id(2001.0))

        print("=" * 68)
        print("F 单元：统计行不是学生")
        pairs, live, notes, miss = PR.build_keys(
            [["2001", "张三"], ["2002", "李四"], [None, "班级平均"], [None, "年级最高"]],
            0, 1)
        check("F1 统计行主键为空（被剔除）",
              [k for k, _s in pairs] == ["2001", "2002", None, None],
              [k for k, _s in pairs])
        check("F2 提示写明剔除了统计行",
              any("统计行" in n for n in notes), notes)

        p = xlsx(os.path.join(tmp, "stat.xlsx"),
                 [["学号", "姓名", "语文"], ["2001", "张三", 90], ["2002", "李四", 80],
                  [None, "班级平均", 85], [None, "年级最高", 95]])
        code, log, d = prep(p, os.path.join(tmp, "stat.json"))
        check("F3 名单里没有「班级平均」",
              code == 0 and [s["姓名"] for s in d["roster"]] == ["张三", "李四"],
              d and [s["姓名"] for s in d["roster"]])

        print("=" * 68)
        print("G 单元：学号列部分为空 → 报错中止（不混用两种主键）")
        p = xlsx(os.path.join(tmp, "part.xlsx"),
                 [["学号", "姓名", "语文"], ["2001", "张三", 90], [None, "李四", 80]])
        code, log, d = prep(p, os.path.join(tmp, "part.json"))
        check("G1 非零退出", code != 0, log[-200:])
        check("G2 报错点明「没填学号」", "没填学号" in log, log[-300:])

        print("=" * 68)
        print("H 单元：CSV 当 --scores 能跑通；.xls 是友好拒绝")
        csvp = os.path.join(tmp, "scores.csv")
        with open(csvp, "w", encoding="utf-8-sig") as f:
            f.write("学号,姓名,语文,数学\r\n2001,张三,90,80\r\n2002,李四,70,60\r\n")
        code, log, d = prep(csvp, os.path.join(tmp, "csv.json"))
        check("H1 CSV 正常出结果", code == 0, log[-300:])
        check("H2 CSV 学科识别正确",
              d and d["meta"]["学科"] == ["语文", "数学"], d and d["meta"]["学科"])

        xlsp = os.path.join(tmp, "old.xls")
        with open(xlsp, "w", encoding="utf-8") as f:
            f.write("dummy")
        code, log, d = prep(xlsp, os.path.join(tmp, "xls.json"))
        check("H3 .xls 非零退出且无 traceback",
              code != 0 and "Traceback" not in log, log[-200:])
        check("H4 .xls 给出「另存为」提示", "另存为" in log, log[-200:])

        print("=" * 68)
        print("I 单元：「只有教师描述」的降级路径")
        p = xlsx(os.path.join(tmp, "only.xlsx"),
                 [["学号", "姓名", "教师描述"],
                  ["2001", "张三", "运动会跑完八百米还给同学递水"],
                  ["2002", "李四", "板报的文字校对一年没出错别字"]])
        code, log, d = prep(p, os.path.join(tmp, "only.json"),
                            extra=["--notes", p])
        check("I1 不再 LookupError，正常出结果", code == 0, log[-300:])
        check("I2 学科为空（按无成绩数据处理）", d and d["meta"]["学科"] == [], d and d["meta"])
        check("I3 名单与描述都在",
              d and [s["姓名"] for s in d["roster"]] == ["张三", "李四"]
              and all(s["教师描述"] for s in d["roster"]))
        check("I4 提示写明「不得出现任何数字」",
              d and any("不得出现任何数字" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("J 单元：选考/走班科目（物理 18/40）→ 保留、不计缺考")
        rows = [["学号", "姓名", "语文", "物理"]]
        for i in range(40):
            rows.append(["%04d" % (2000 + i), "学生%02d" % i, 80,
                         90 if i < 18 else None])
        p = xlsx(os.path.join(tmp, "elect.xlsx"), rows)
        code, log, d = prep(p, os.path.join(tmp, "elect.json"))
        check("J1 物理整科没丢", code == 0 and d["meta"]["学科"] == ["语文", "物理"],
              d and d["meta"]["学科"])
        check("J2 meta 标出选考科目", d and d["meta"]["选考科目"] == ["物理"],
              d and d["meta"].get("选考科目"))
        check("J3 未选考者不计缺考", d and d["对齐说明"]["缺考学生"] == [],
              d and d["对齐说明"]["缺考学生"][:2])
        not_taken = [s for s in d["roster"] if s.get("未选考科目") == ["物理"]]
        check("J4 未选考者记「未选考科目」", len(not_taken) == 22, len(not_taken))
        check("J5 提示说明该科不计入总分",
              d and any("已保留" in n for n in d["对齐说明"]["机器提示"]))

        print("=" * 68)
        print("K 单元：「语文等级」按文本等级列剔除，文案不说成「同一门课」")
        p = xlsx(os.path.join(tmp, "grade.xlsx"),
                 [["学号", "姓名", "语文", "语文等级"],
                  ["2001", "张三", 90, "A"], ["2002", "李四", 70, "B"]])
        code, log, d = prep(p, os.path.join(tmp, "grade.json"))
        check("K1 学科 = 语文（等级列被剔除）",
              code == 0 and d["meta"]["学科"] == ["语文"], d and d["meta"]["学科"])
        tips = d["对齐说明"]["机器提示"] if d else []
        check("K2 原因是「文本等级」",
              any("文本等级" in n for n in tips), tips)
        check("K3 不再说成「同一门课的另一种写法」",
              not any("同一门课的另一种写法" in n for n in tips), tips)

        print("=" * 68)
        print("L 单元：附表多工作表 → 数据在第二张也能选中")
        wb = Workbook()
        wb.active.title = "封面"
        wb.active["A1"] = "作业统计说明"
        ws2 = wb.create_sheet("数据")
        for r in [["学号", "姓名", "应交次数", "实交次数"],
                  ["2001", "张三", 10, 10], ["2002", "李四", 10, 8]]:
            ws2.append(r)
        hw = os.path.join(tmp, "hw_multi.xlsx")
        wb.save(hw)
        p = xlsx(os.path.join(tmp, "scores_mini.xlsx"),
                 [["学号", "姓名", "语文"], ["2001", "张三", 90], ["2002", "李四", 70]])
        code, log, d = prep(p, os.path.join(tmp, "multi.json"), extra=["--homework", hw])
        h = {s["姓名"]: s["作业"] for s in (d["roster"] if d else [])}
        check("L1 第二张表的数据被读到了",
              code == 0 and h.get("张三") and h.get("李四"), str(h))
        check("L2 提示说明改选了哪张表",
              d and any("已改选" in n for n in d["对齐说明"]["机器提示"]))

    print("=" * 68)
    print("M 单元：出表端 —— 评语姓名与名单不符 → 拒绝配对")
    with tempfile.TemporaryDirectory() as tmp:
        rp = os.path.join(tmp, "r.json")
        cm = os.path.join(tmp, "c.json")
        json.dump({"meta": {"主键": "学号"}, "roster": [
            {"学号": "2001", "姓名": "张三", "成绩": {}, "作业": None, "课堂": None,
             "教师描述": "", "缺失项": []},
            {"学号": "2002", "姓名": "李四", "成绩": {}, "作业": None, "课堂": None,
             "教师描述": "", "缺失项": []}]},
            open(rp, "w", encoding="utf-8"), ensure_ascii=False)
        json.dump({"comments": [
            {"学号": "2001", "姓名": "李四", "评语正文": "这是写给李四的评语" * 12},
            {"学号": "2002", "姓名": "张三", "评语正文": "这是写给张三的评语" * 12}]},
            open(cm, "w", encoding="utf-8"), ensure_ascii=False)
        code, log = run([EXPORT, "--roster", rp, "--comments", cm,
                         "--out", os.path.join(tmp, "o.xlsx"), "--strict"])
        check("M1 --strict 下非零退出", code != 0, log[-200:])
        check("M2 报出「姓名对不上」", "对不上" in log, log[-400:])
        check("M3 没有「全部通过」", "全部通过" not in log, log[-200:])

    print("=" * 68)
    print("N 单元：平时序列数字豁免，「考了87」仍报")
    ok = "十二周里你的数学作业一次没落下，地理第4次摸到96、第5次冲到99，可第6次又落回87。"
    bad = "这学期你的语文考了87，比上次好一些。"
    check("N1 序列数字不报", EC.score_flags(ok) == [], EC.score_flags(ok))
    check("N2 「考了87」仍报", "疑似出现分数" in EC.score_flags(bad), EC.score_flags(bad))
    check("N3 「96分」仍报（带分数单位）", "含分数" in EC.score_flags("第3次冲到96分"),
          EC.score_flags("第3次冲到96分"))
    check("N4 「第3名」仍报", any("名次" in f for f in EC.score_flags("这次排到第3名")),
          EC.score_flags("这次排到第3名"))
    check("N5 「从70到90」不报", EC.score_flags("数学从70到90，一路爬上来") == [],
          EC.score_flags("数学从70到90，一路爬上来"))

    print("=" * 68)
    print("N' 单元：平时序列表述口径（标准式 学科+第X次平时成绩NN分）")
    std = "语文从第一次平时成绩74分提升到第六次平时成绩的87分，看得出你在读和写上花了心思。"
    check("N6 标准式不报分数", EC.score_flags(std) == [], EC.score_flags(std))
    check("N7 标准式表述合规", EC.seq_style_flags(std) == [], EC.seq_style_flags(std))
    check("N8 标准式（不带「的」）也放行",
          EC.score_flags("数学从第一次平时成绩89分一路升到第六次平时成绩100分。") == [] and
          EC.seq_style_flags("数学从第一次平时成绩89分一路升到第六次平时成绩100分。") == [],
          EC.score_flags("数学从第一次平时成绩89分一路升到第六次平时成绩100分。"))
    old = "数学那条平时线从第1次的 74 一直涨到第6次的 87，涨得很实在。"
    check("N9 省略式被抓（数字本身仍豁免）",
          EC.score_flags(old) == [] and len(EC.seq_style_flags(old)) == 2,
          (EC.score_flags(old), EC.seq_style_flags(old)))
    check("N10 「地理第4次摸到96」被提示改写", any("省略式" in f for f in EC.seq_style_flags(ok)),
          EC.seq_style_flags(ok))
    check("N11 「平时线」自造指代被抓",
          any("自造" in f for f in EC.seq_style_flags("英语那条平时线，是你这学期最扎实的证据。")),
          EC.seq_style_flags("英语那条平时线，是你这学期最扎实的证据。"))
    check("N12 标准式但没写学科被抓",
          any("哪一科" in f for f in
              EC.seq_style_flags("从第一次平时成绩74分提升到第六次平时成绩的87分。")),
          EC.seq_style_flags("从第一次平时成绩74分提升到第六次平时成绩的87分。"))
    check("N13 「第3次冲到96分」仍报含分数",
          "含分数" in EC.score_flags("地理第3次冲到96分，第4次又落回87。"),
          EC.score_flags("地理第3次冲到96分，第4次又落回87。"))
    check("N14 期末真实分数仍报",
          "含分数" in EC.score_flags("这次期末数学考了96分。"),
          EC.score_flags("这次期末数学考了96分。"))
    check("N15 「平时成绩…都在97分以上」也放行（口径词在场即豁免）",
          EC.score_flags("语文六次平时成绩都在97分以上，几乎没有波动。") == [],
          EC.score_flags("语文六次平时成绩都在97分以上，几乎没有波动。"))

    print("=" * 68)
    print("O 单元：--skip-tips 按固定编号跳（材料给全时不失效）")
    with tempfile.TemporaryDirectory() as tmp:
        rp = os.path.join(tmp, "r.json")
        cm = os.path.join(tmp, "c.json")
        body = "这学期你的作业一次没落下，讲台上讲题那次思路比答案更让人记住。" * 4
        json.dump({"meta": {"主键": "学号"}, "roster": [
            {"学号": "2001", "姓名": "张三",
             "成绩": {"上次总分": 1, "上次排名": 1},
             "作业": {"应交次数": 10}, "课堂": {"发言次数": 3},
             "教师描述": "跑完八百米给同学递水", "缺失项": []}]},
            open(rp, "w", encoding="utf-8"), ensure_ascii=False)
        json.dump({"comments": [{"学号": "2001", "姓名": "张三", "评语正文": body}]},
                  open(cm, "w", encoding="utf-8"), ensure_ascii=False)
        c0, l0 = run([EXPORT, "--roster", rp, "--comments", cm,
                      "--out", os.path.join(tmp, "a.xlsx")])
        check("O1 材料给全 → 只剩固定编号 5、6，外加第 7 条（没有荣誉材料时才出现）",
              "5. 再给分科逐题" in l0 and "6. " in l0 and "7. " in l0, l0[-400:])
        c1, l1 = run([EXPORT, "--roster", rp, "--comments", cm,
                      "--out", os.path.join(tmp, "b.xlsx"), "--skip-tips", "5,6,7"])
        check("O2 --skip-tips 5,6,7 真的跳掉了", "下方附 0 条" in l1, l1[-400:])
        c2, l2 = run([EXPORT, "--roster", rp, "--comments", cm,
                      "--out", os.path.join(tmp, "c.xlsx"), "--skip-tips", "-1"])
        check("O3 负数从末尾倒数也生效（跳掉最后一条 7 → 还剩 5、6）",
              "下方附 2 条" in l2, l2[-400:])
        # 有荣誉材料时第 7 条不再出现（它问的正是"再有奖状就发来"）
        rp2 = os.path.join(tmp, "r2.json")
        json.dump({"meta": {"主键": "学号"}, "roster": [
            {"学号": "2001", "姓名": "张三",
             "成绩": {"上次总分": 1, "上次排名": 1},
             "作业": {"应交次数": 10}, "课堂": {"发言次数": 3},
             "教师描述": "跑完八百米给同学递水",
             "荣誉奖项": "校级三好学生（校级，2026年1月）", "缺失项": []}]},
            open(rp2, "w", encoding="utf-8"), ensure_ascii=False)
        c3, l3 = run([EXPORT, "--roster", rp2, "--comments", cm,
                      "--out", os.path.join(tmp, "d.xlsx")])
        check("O4 已有荣誉材料 → 第 7 条不再出现（缺什么才说什么）",
              "7. " not in l3, l3[-400:])

    print("=" * 68)
    print("P 单元：查重端 0 条评语不再崩")
    r = SC.analyze([])
    check("P1 analyze([]) 不抛异常且人数 0", r["人数"] == 0)
    check("P2 给出「没有可检评语」结论", any("没有可检评语" in c for c in r["结论"]))
    with tempfile.TemporaryDirectory() as tmp:
        cm = os.path.join(tmp, "empty.json")
        json.dump({"comments": []}, open(cm, "w", encoding="utf-8"), ensure_ascii=False)
        code, log = run([SIM, "--comments", cm])
        check("P3 命令行跑空文件退出码 0", code == 0, log[-300:])
        check("P4 控制台说明没有可检评语", "没有可检评语" in log, log[-300:])

    print("=" * 68)
    print("Q 单元：文档/SKILL 与代码口径一致（平时序列标准式）")
    root = os.path.dirname(HERE)
    docs = {rel: (open(os.path.join(root, rel), encoding="utf-8").read()
                  if os.path.exists(os.path.join(root, rel)) else "")
            for rel in ("SKILL.md", "references/writing-rules.md",
                        "references/data-spec.md", "references/image-intake.md",
                        "scripts/export_comments.py")}
    SAMPLE = "第一次平时成绩74分提升到第六次平时成绩的87分"

    for rel in ("SKILL.md", "references/writing-rules.md",
                "references/data-spec.md", "scripts/export_comments.py"):
        check("Q %s 写明「第X次平时成绩NN分」口径" % rel,
              "次平时成绩" in docs[rel], rel)
    for rel in ("SKILL.md", "references/writing-rules.md", "scripts/export_comments.py"):
        check("Q %s 带标准式完整样例" % rel, SAMPLE in docs[rel], rel)
    full = "语文" + SAMPLE + "，看得出你在读和写上花了心思。"
    check("Q 代码里标准式真的被豁免（不是只写在文档里）",
          EC.score_flags(full) == [] and EC.seq_style_flags(full) == [],
          (EC.score_flags(SAMPLE), EC.seq_style_flags(SAMPLE)))
    # 多文件成绩表也是「文档说了、代码真做了」这一类，一起钉住
    check("Q SKILL/data-spec 都写明「多个成绩文件一起传 --scores」",
          "一起传给 `--scores`" in docs["SKILL.md"]
          and "成绩分在多个文件" in docs["references/data-spec.md"],
          ("一起传给 `--scores`" in docs["SKILL.md"],
           "成绩分在多个文件" in docs["references/data-spec.md"]))

    print("=" * 68)
    print("R 单元：期末/期中/平时是三个独立文件 → 一起传 --scores 即可")
    md = os.path.join(tmp, "multi")
    os.makedirs(md, exist_ok=True)
    hs_e = ["学号", "姓名", "语文", "数学", "总分", "班级排名"]
    fin = xlsx(os.path.join(md, "初一3班期末考试成绩.xlsx"),
               [hs_e, ["2001", "张三", 90, 80, 170, 3], ["2002", "李四", 70, 60, 130, 9]])
    mid = xlsx(os.path.join(md, "初一3班期中考试成绩.xlsx"),
               [hs_e, ["2001", "张三", 85, 70, 155, 5], ["2002", "李四", 72, 64, 136, 8]])
    usual = xlsx(os.path.join(md, "初一3班平时成绩.xlsx"),
                 [["学号", "姓名", "第1次-语文", "第2次-语文"],
                  ["2001", "张三", 74, 87], ["2002", "李四", 80, 79]])
    # 这三个文件的工作表名全是通用名（openpyxl 默认给「Sheet」）——旧版看不出考试先后
    for f in (fin, mid, usual):
        check("R0 %s 的工作表名是通用名（不含考试信息）" % os.path.basename(f),
              bool(PR.GENERIC_SHEET_RE.match(load_workbook(f).sheetnames[0])),
              load_workbook(f).sheetnames)

    outR = os.path.join(tmp, "multi.json")
    code, log = run([PREP, "--scores", fin, mid, usual, "--out", outR,
                     "--class-name", "初一"])
    dR = json.load(open(outR, encoding="utf-8")) if os.path.exists(outR) else None
    ws = ((dR or {}).get("meta", {}) or {}).get("工作表", {})
    check("R1 三个文件一起传 → 跑通、2 人齐",
          code == 0 and dR and len(dR["roster"]) == 2, log[-300:])
    check("R2 通用表名按**文件名**贴标签（期末/期中/平时各归各位）",
          "期末" in ws.get("本次成绩", "") and "期中" in ws.get("上次对比", "")
          and "平时" in ws.get("平时趋势", ""), ws)
    gR = (dR or {}).get("roster", [{}])[0].get("成绩", {})
    check("R3 期中对比真的进来了（总分变化 = 170 − 155 = 15）",
          gR.get("总分变化") == 15.0, gR.get("总分变化"))
    check("R3b 上次各科来自期中表（语文 85）",
          (gR.get("上次各科") or {}).get("语文") == 85.0, gR.get("上次各科"))
    trR = (dR or {}).get("roster", [{}])[0].get("平时趋势", {}).get("语文", {})
    check("R4 平时序列按逐次保留 [74, 87]（不是均值）",
          trR.get("逐次") == [74.0, 87.0], trR)

    outS = os.path.join(tmp, "single.json")
    codeS, logS = run([PREP, "--scores", fin, "--out", outS, "--class-name", "初一"])
    dS = json.load(open(outS, encoding="utf-8")) if os.path.exists(outS) else None
    wsS = ((dS or {}).get("meta", {}) or {}).get("工作表", {})
    check("R5 只传一个文件仍照旧跑（向后兼容），标签也取文件名",
          codeS == 0 and "期末" in wsS.get("本次成绩", ""), (codeS, wsS))
    check("R6 单文件时提醒同目录还有别的成绩文件（防静默丢维度，且要在控制台露面）",
          "同目录下还有" in logS and "[重要提示]" in logS, logS[-400:])

    outC = os.path.join(tmp, "comma.json")
    codeC, _ = run([PREP, "--scores", "%s,%s,%s" % (fin, mid, usual),
                    "--out", outC, "--class-name", "初一"])
    dC = json.load(open(outC, encoding="utf-8")) if os.path.exists(outC) else None
    check("R7 逗号分隔的旧式写法仍然可用",
          codeC == 0 and dC and dC["roster"][0]["成绩"].get("总分变化") == 15.0,
          codeC)

    codeM, logM = run([PREP, "--scores", fin, os.path.join(md, "不存在.xlsx"),
                       "--out", os.path.join(tmp, "x.json"), "--class-name", "初一"])
    check("R8 多个文件里有一个不存在 → 报错（不静默少读一张表）",
          codeM != 0 and "成绩表文件不存在" in logM, (codeM, logM[-200:]))

    a1 = xlsx(os.path.join(md, "表一.xlsx"),
              [hs_e, ["2001", "张三", 90, 80, 170, 3]])
    a2 = xlsx(os.path.join(md, "表二.xlsx"),
              [hs_e, ["2001", "张三", 85, 70, 155, 5]])
    codeA, logA = run([PREP, "--scores", a1, a2, "--out", os.path.join(tmp, "a.json"),
                       "--class-name", "初一"])
    check("R9 文件名看不出考试先后 → 报错要求 --scores-sheet（不瞎猜）",
          codeA != 0 and "--scores-sheet" in logA, (codeA, logA[-260:]))
    outA2 = os.path.join(tmp, "a2.json")
    codeA2, logA2 = run([PREP, "--scores", fin, mid, "--out", outA2,
                         "--class-name", "初一", "--scores-sheet", "初一3班期中考试成绩"])
    dA2 = json.load(open(outA2, encoding="utf-8")) if os.path.exists(outA2) else None
    check("R10 --scores-sheet 能用文件名标签指到（标签是用户可寻址的）",
          codeA2 == 0 and "期中" in (((dA2 or {}).get("meta", {}) or {})
                                      .get("工作表", {}) or {}).get("本次成绩", ""),
          (codeA2, logA2[-200:]))

    labs = [s["sheet"] for s in PR.load_scores_sources([fin, usual])]
    check("R11 标签规则：通用名取文件名、有意义名保留原名",
          labs == ["初一3班期末考试成绩", "初一3班平时成绩"], labs)

    print("=" * 68)
    print("S 单元：往年评语（作为个性化描述的参考材料）")
    sp = xlsx(os.path.join(tmp, "s_scores.xlsx"),
              [["学号", "姓名", "语文", "数学"],
               ["2001", "张三", 90, 80], ["2002", "李四", 70, 60]])
    sn = xlsx(os.path.join(tmp, "s_notes.xlsx"),
              [["学号", "姓名", "教师描述"],
               ["2001", "张三", "讲台上讲过一次压轴题，思路清楚。"]])
    spat = xlsx(os.path.join(tmp, "s_past.xlsx"),
                [["学号", "姓名", "往年评语"],
                 ["2001", "张三", "上学期你解题快，但步骤常省略。"],
                 ["2002", "李四", "上学期你安静，但值日做得很认真。"]])
    outS = os.path.join(tmp, "s.json")
    codeS, logS, dS = prep(sp, outS, ["--notes", sn, "--past-comments", spat])
    smap = {s["学号"]: s for s in (dS or {}).get("roster", [])}
    check("S1 往年评语进 roster（两人都有）",
          codeS == 0 and "解题快" in smap.get("2001", {}).get("往年评语", "")
          and "值日" in smap.get("2002", {}).get("往年评语", ""),
          (codeS, {k: v.get("往年评语") for k, v in smap.items()}))
    check("S2 教师描述与往年评语是两个字段、互不覆盖",
          "压轴题" in smap.get("2001", {}).get("教师描述", "")
          and "压轴题" not in smap.get("2001", {}).get("往年评语", ""),
          smap.get("2001"))
    check("S3 覆盖人数记了「往年评语表」",
          (dS or {}).get("对齐说明", {}).get("覆盖人数", {}).get("往年评语表") == 2,
          (dS or {}).get("对齐说明", {}).get("覆盖人数"))
    check("S4 字段口径写明「往年评语是参考、不是本学期证据」",
          any("往年评语" in x and "参考" in x
              for x in (dS or {}).get("对齐说明", {}).get("字段口径", [])),
          (dS or {}).get("对齐说明", {}).get("字段口径"))

    # 防串人：往年评语表里的名单外学号，绝不能挂到别人头上（与教师描述表同一口径）
    pbad = xlsx(os.path.join(tmp, "s_past_bad.xlsx"),
                [["学号", "姓名", "往年评语"], ["9999", "王浩然", "上学期表现不错。"]])
    oS2 = os.path.join(tmp, "s2.json")
    cS2, lS2, dS2 = prep(sp, oS2, ["--past-comments", pbad])
    un2 = (dS2 or {}).get("对齐说明", {}).get("未匹配记录", [])
    check("S5 往年评语里名单外学号 → 判名单外、不兜底（与教师描述表同一口径）",
          cS2 == 0 and any(u["学号"] == "9999" for u in un2)
          and not any(s.get("往年评语") for s in (dS2 or {}).get("roster", [])),
          (un2, [s.get("往年评语") for s in (dS2 or {}).get("roster", [])]))

    cS3, lS3 = run([PREP, "--scores", sp, "--out", os.path.join(tmp, "s3.json"),
                    "--class-name", "初一",
                    "--past-comments", os.path.join(tmp, "没有这份.xlsx")])
    check("S6 --past-comments 文件不存在 → 报错（不静默跳过）",
          cS3 != 0 and "往年评语表 文件不存在" in lS3, (cS3, lS3[-200:]))

    # 往年评语只覆盖部分学生 → 缺的人记进「缺失项」，不静默当作没有
    pone = xlsx(os.path.join(tmp, "s_past_one.xlsx"),
                [["学号", "姓名", "往年评语"], ["2001", "张三", "上学期你解题快。"]])
    oS4 = os.path.join(tmp, "s4.json")
    cS4, lS4, dS4 = prep(sp, oS4, ["--past-comments", pone])
    missS = {m["学号"]: m["缺什么"] for m in (dS4 or {}).get("对齐说明", {}).get("缺失学生", [])}
    check("S7 往年评语缺人 → 进「缺失项」（往年评语）",
          "往年评语" in missS.get("2002", []), missS)

    tips1 = EC.build_tips([{"教师描述": "", "往年评语": "上学期你解题快，但步骤常省略。",
                            "缺失项": []}])
    tips2 = EC.build_tips([{"教师描述": "讲台上的思路很清楚。", "往年评语": "",
                            "缺失项": []}])
    tips3 = EC.build_tips([{"教师描述": "", "往年评语": "", "缺失项": []}])
    check("S8 有往年评语、没有本学期教师描述 → 小贴士第 1 条改口径、固定编号仍是 1",
          tips1 and tips1[0][0] == 1 and "往年评语" in tips1[0][1], tips1)
    check("S9 有本学期教师描述 → 不再出现第 1 条",
          all(t[0] != 1 for t in tips2), tips2)
    check("S10 两样都没有 → 第 1 条仍是原始文案",
          tips3 and tips3[0][0] == 1 and "教师个别描述" in tips3[0][1], tips3)

    past_one = {"2001": "上学期你解题速度很快，但步骤常常省略，考试时因此丢过不少分。"}
    ov_copy = SC.past_overlap(
        [{"学号": "2001", "姓名": "张三",
          "正文": "上学期你解题速度很快，但步骤常常省略，考试时因此丢过不少分。"}],
        past_one)
    check("S11 逐句比对：照搬往年那一句 → 命中",
          ov_copy["命中人数"] == 1 and ov_copy["命中组数"] >= 1, ov_copy)
    ov_new = SC.past_overlap(
        [{"学号": "2001", "姓名": "张三",
          "正文": "这一学期你在数学课上讲的解法，同学都听明白了其中的思路；把演算写全，效果更好。"}],
        past_one)
    check("S12 换骨架重写后 → 不命中（阈值不误报）",
          ov_new["命中组数"] == 0, ov_new)
    short_one = {"2001": "书写要稳。"}
    ov_short = SC.past_overlap([{"学号": "2001", "姓名": "张三", "正文": "书写要稳。"}], short_one)
    check("S12b 不足 8 字的短句不参与比对（与批内句级检测同一覆盖面，防误报）",
          ov_short["命中组数"] == 0, ov_short)
    check("S13 load_past 认 roster.json 的「往年评语」",
          "解题快" in (SC.load_past(outS) or {}).get("2001", ""),
          SC.load_past(outS))

    cm_path = os.path.join(tmp, "s_cm.json")
    json.dump({"comments": [{"学号": "2001", "姓名": "张三",
                             "评语正文": "上学期你解题速度很快，但步骤常常省略，考试时因此丢过不少分。"}]},
              open(cm_path, "w", encoding="utf-8"), ensure_ascii=False)
    cS5, lS5 = run([SIM, "--comments", cm_path, "--past", outS])
    check("S14 命令行 --past 有专门一节输出（覆盖人数 + 命中）",
          cS5 == 0 and "与往年评语的重合" in lS5, lS5[-400:])
    cS6, lS6 = run([SIM, "--comments", cm_path, "--past", os.path.join(tmp, "无.json")])
    check("S15 --past 指向不存在的文件 → 跳过而非崩",
          cS6 == 0 and "跳过 --past" in lS6, lS6[-300:])

    for rel in ("SKILL.md", "references/writing-rules.md", "references/data-spec.md"):
        check("S16 %s 写到「往年评语」" % rel, "往年评语" in docs[rel], rel)
    check("S17 SKILL 写明 --past-comments 这个入口",
          "--past-comments" in docs["SKILL.md"], "--past-comments" not in docs["SKILL.md"])
    check("S18 writing-rules 写明「只作参考、不得照搬」",
          "不得照搬" in docs["references/writing-rules.md"],
          "不得照搬" not in docs["references/writing-rules.md"])

    print("=" * 68)
    print("T 单元：荣誉材料（奖状/证书/荣誉榜）与图片材料通道")
    tp = xlsx(os.path.join(tmp, "t_scores.xlsx"),
              [["学号", "姓名", "语文", "数学"],
               ["2001", "张三", 90, 80], ["2002", "李四", 70, 60],
               ["2003", "王五", 85, 75]])
    tn = xlsx(os.path.join(tmp, "t_notes.xlsx"),
              [["学号", "姓名", "教师描述"],
               ["2001", "张三", "讲台上讲过压轴题。"],
               ["2002", "李四", "值日做得很认真。"],
               ["2003", "王五", "化学实验记录写得最全。"]])
    taw = xlsx(os.path.join(tmp, "t_awards.xlsx"),
               [["学号", "姓名", "荣誉奖项"],
                ["2001", "张三", "校级三好学生（校级，2026年1月）"],
                ["2001", "张三", "区数学竞赛三等奖（区级，2026年3月）"],
                ["", "李四", "校级阅读之星（校级，2026年4月）"]])
    outT = os.path.join(tmp, "t.json")
    codeT, logT, dT = prep(tp, outT, ["--notes", tn, "--awards", taw])
    tmap = {s["学号"]: s for s in (dT or {}).get("roster", [])}
    check("T1 荣誉进 roster 的「荣誉奖项」字段",
          codeT == 0 and "三好学生" in tmap.get("2001", {}).get("荣誉奖项", ""),
          (codeT, tmap.get("2001")))
    check("T2 荣誉与教师描述是不同字段、互不覆盖",
          "压轴题" in tmap.get("2001", {}).get("教师描述", "")
          and "压轴题" not in tmap.get("2001", {}).get("荣誉奖项", ""),
          tmap.get("2001"))
    check("T3 一人多条荣誉 → 合并（不覆盖）",
          "三好学生" in tmap.get("2001", {}).get("荣誉奖项", "")
          and "数学竞赛" in tmap.get("2001", {}).get("荣誉奖项", ""),
          tmap.get("2001", {}).get("荣誉奖项"))
    check("T4 学号留空 + 姓名唯一 → 按姓名接上（奖状上没学号是常态）",
          "阅读之星" in tmap.get("2002", {}).get("荣誉奖项", ""),
          tmap.get("2002"))
    check("T5 覆盖人数记了「荣誉材料表」",
          (dT or {}).get("对齐说明", {}).get("覆盖人数", {}).get("荣誉材料表") == 3,
          (dT or {}).get("对齐说明", {}).get("覆盖人数"))
    check("T6 字段口径写明「荣誉是可引用的证据、级别不得夸大」",
          any("荣誉" in x and "证据" in x for x in
              (dT or {}).get("对齐说明", {}).get("字段口径", [])),
          (dT or {}).get("对齐说明", {}).get("字段口径"))

    # ★ 关键回归：荣誉「不是人人都有」，未覆盖的人绝不能进「缺失项」
    #   （旧写法会把它当缺失，40 人示例里刷出 23 条「缺 荣誉奖项」，淹没真正的缺失）
    missT = {m["学号"]: m["缺什么"]
             for m in (dT or {}).get("对齐说明", {}).get("缺失学生", [])}
    check("T7 未拿到荣誉的人**不**进「缺失项」（荣誉不是人人都有）",
          "2003" not in missT and "荣誉奖项" not in missT.get("2003", []), missT)
    check("T8 但要点名提醒「这些同学的评语里不要出现奖项/称号」",
          any("荣誉不是人人都有" in n for n in
              (dT or {}).get("对齐说明", {}).get("机器提示", [])),
          (dT or {}).get("对齐说明", {}).get("机器提示"))
    cT2, lT2 = run([PREP, "--scores", tp, "--awards",
                    os.path.join(tmp, "没有这份.xlsx"),
                    "--out", os.path.join(tmp, "t2.json"), "--class-name", "初一"])
    check("T9 --awards 文件不存在 → 报错（不静默跳过）",
          cT2 != 0 and "荣誉材料表 文件不存在" in lT2, (cT2, lT2[-200:]))
    # 对照：教师描述这类「本就该覆盖全班」的材料，缺人仍然进缺失项
    one_note = xlsx(os.path.join(tmp, "t_one_note.xlsx"),
                    [["学号", "姓名", "教师描述"],
                     ["2001", "张三", "压轴题。"], ["2002", "李四", ""]])
    cT3, lT3, dT3 = prep(tp, os.path.join(tmp, "t3.json"), ["--notes", one_note])
    missT3 = {m["学号"]: m["缺什么"]
              for m in (dT3 or {}).get("对齐说明", {}).get("缺失学生", [])}
    check("T10 对照：教师描述缺人**仍然**进「缺失项」（miss_is_gap 默认不变）",
          "教师描述" in missT3.get("2002", []), missT3)

    # 防串人：荣誉表里的名单外学号，不兜底（与其余附表逐字相同）
    tbad = xlsx(os.path.join(tmp, "t_bad.xlsx"),
                [["学号", "姓名", "荣誉奖项"], ["9999", "王浩然", "市级优秀学生（市级，2026年5月）"]])
    cT4, lT4, dT4 = prep(tp, os.path.join(tmp, "t4.json"), ["--awards", tbad])
    unT = (dT4 or {}).get("对齐说明", {}).get("未匹配记录", [])
    check("T11 荣誉表里名单外学号 → 判名单外、不兜底",
          cT4 == 0 and any(u["学号"] == "9999" for u in unT)
          and not any(s.get("荣誉奖项") for s in (dT4 or {}).get("roster", [])),
          (unT, [s.get("荣誉奖项") for s in (dT4 or {}).get("roster", [])]))
    src_prep = open(os.path.join(HERE, "prepare_roster.py"), encoding="utf-8").read()
    check("T12 三类文本表共用同一个 ingest_text_table；荣誉显式传 miss_is_gap=False",
          src_prep.count("def ingest_text_table(") == 1
          and all(('"%s"' % f) in src_prep for f in ("教师描述", "往年评语", "荣誉奖项"))
          and "miss_is_gap=False" in src_prep,
          (src_prep.count("def ingest_text_table("), "miss_is_gap=False" in src_prep))

    # 列名认不出 → 取最长文本列；--award-col 可指定
    twide = xlsx(os.path.join(tmp, "t_wide.xlsx"),
                 [["学号", "姓名", "级别", "获得情况"],
                  ["2001", "张三", "校级", "校三好学生（校级，2026年1月）"]])
    cT5, lT5, dT5 = prep(tp, os.path.join(tmp, "t5.json"), ["--awards", twide])
    t5 = {s["学号"]: s for s in (dT5 or {}).get("roster", [])}
    check("T13 荣誉列名认不出时取最长文本列（不会静默丢人）",
          cT5 == 0 and "三好学生" in t5.get("2001", {}).get("荣誉奖项", ""),
          t5.get("2001"))
    cT6, lT6, dT6 = prep(tp, os.path.join(tmp, "t6.json"),
                         ["--awards", twide, "--award-col", "级别"])
    t6 = {s["学号"]: s for s in (dT6 or {}).get("roster", [])}
    check("T14 --award-col 指定列名生效",
          cT6 == 0 and t6.get("2001", {}).get("荣誉奖项", "") == "校级",
          t6.get("2001"))

    # ---------------- 图片：友好拒绝，不是 traceback ----------------
    fake_png = os.path.join(tmp, "成绩截图.png")
    open(fake_png, "wb").write(b"\x89PNG\r\n\x1a\n")
    fake_pdf = os.path.join(tmp, "奖状.pdf")
    open(fake_pdf, "wb").write(b"%PDF-1.4\n")
    cP, lP = run([PREP, "--scores", fake_png, "--out", os.path.join(tmp, "x.json")])
    check("T15 成绩表传图片 → 友好拒绝（不是 openpyxl traceback）",
          cP != 0 and "不能直接读图" in lP and "image-intake" in lP and "Traceback" not in lP,
          (cP, lP[-300:]))
    cP2, lP2 = run([PREP, "--scores", tp, "--awards", fake_png,
                    "--out", os.path.join(tmp, "x2.json")])
    check("T16 附表传图片 → 同样友好拒绝",
          cP2 != 0 and "不能直接读图" in lP2, (cP2, lP2[-300:]))
    cP3, lP3 = run([PREP, "--scores", fake_pdf, "--out", os.path.join(tmp, "x3.json")])
    check("T17 PDF 也算「不是表格文件」",
          cP3 != 0 and "图片/PDF" in lP3, (cP3, lP3[-200:]))
    check("T18 reject_image 不误伤正常表格（.xlsx 直接放行）",
          PR.reject_image(tp) is None, PR.reject_image(tp))
    check("T19 拒绝文案里带三条硬口径的指引（回读确认 / 留空 / 图上明确标注）",
          "回读" in lP and "留空" in lP and "明确标注" in lP, lP[-500:])

    # ---------------- 荣誉表述的材料出处闸门 ----------------
    mats = "物理竞赛班成员。"          # 教师描述里没有任何奖项词
    mats2 = "本学期获校级三好学生。"
    check("T20 正文写荣誉、材料里没有 → 报（疑似虚构）",
          bool(EC.award_flags("这学期你被评为校级三好学生，老师为你高兴。", mats)))
    check("T21 材料里有同类荣誉 → 放行",
          EC.award_flags("这学期你被评为校级三好学生，老师为你高兴。", mats2) == [],
          EC.award_flags("这学期你被评为校级三好学生，老师为你高兴。", mats2))
    check("T22 正文没有荣誉表述 → 不触发",
          EC.award_flags("这学期你的数学作业一次没落下。", mats) == [])
    check("T23 词表保守：「优秀」「进步」「参加比赛」等泛词不触发（不误报是前提）",
          EC.award_flags("你积极参加比赛，表现优秀，进步很大。", mats) == [],
          EC.award_flags("你积极参加比赛，表现优秀，进步很大。", mats))
    check("T24 「往年评语」刻意不算出处（规则 5 要求往年的事在今年材料里能对上）",
          bool(EC.award_flags("去年你就拿过校级三好学生。", mats)),
          "闸门只看 教师描述 + 荣誉奖项")

    # 端到端：出表时真的调用这条闸门
    rpT = os.path.join(tmp, "rt.json")
    cmT = os.path.join(tmp, "ct.json")
    json.dump({"meta": {"主键": "学号"}, "roster": [
        {"学号": "2001", "姓名": "张三", "成绩": {}, "作业": None, "课堂": None,
         "教师描述": "讲台上讲过压轴题。", "荣誉奖项": "", "缺失项": []}]},
        open(rpT, "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"comments": [{"学号": "2001", "姓名": "张三",
                             "评语正文": "这学期你被评上校级三好学生，老师看在眼里，也记得你讲台上讲题那次。" * 4}]},
              open(cmT, "w", encoding="utf-8"), ensure_ascii=False)
    cE, lE = run([EXPORT, "--roster", rpT, "--comments", cmT,
                  "--out", os.path.join(tmp, "t.xlsx")])
    check("T25 端到端：出表体检真的会因「荣誉无出处」预警",
          cE == 0 and "荣誉/获奖类表述" in lE and "全部通过" not in lE, lE[-500:])

    # 不误报的前提：40 条真实示例评语（其中「二等奖」「竞赛」都能在教师描述里对上）
    ex_dir = os.path.join(root, "references")
    if os.path.exists(os.path.join(ex_dir, "comments.json")):
        ex_r = json.load(open(os.path.join(ex_dir, "roster.json"), encoding="utf-8"))
        ex_c = json.load(open(os.path.join(ex_dir, "comments.json"), encoding="utf-8"))
        ex_map = {s["学号"]: s for s in ex_r["roster"]}
        hits = []
        for c in ex_c["comments"]:
            s = ex_map.get(str(c.get("学号", "")).strip(), {})
            m = " ".join(str(s.get(k) or "") for k in ("教师描述", "荣誉奖项"))
            f = EC.award_flags(c.get("评语正文", ""), m)
            if f:
                hits.append((c.get("姓名"), f))
        check("T26 40 条示例评语 0 误报（不误报是这套词表的前提）", hits == [], hits)

    # ---------------- 文档同步 ----------------
    check("T27 SKILL 写明「图片是录入通道、不是新的一类材料」",
          "不是新的一类材料" in docs["SKILL.md"], "见 SKILL.md「图片材料」一节")
    check("T28 SKILL 写明 --awards 这个入口",
          "--awards" in docs["SKILL.md"], "--awards" not in docs["SKILL.md"])
    check("T29 image-intake.md 写了三条硬口径（回读确认 / 读不出留空 / 图上数字不当分数）",
          all(k in docs["references/image-intake.md"]
              for k in ("回读确认", "绝不猜", "不当分数用")),
          "见 references/image-intake.md")
    check("T30 data-spec 从「五类输入表」改成「六类」并写明图片不在其中",
          "六类输入表" in docs["references/data-spec.md"]
          and "不在" in docs["references/data-spec.md"],
          "见 references/data-spec.md 开头")
    check("T31 writing-rules 规则 2 写明荣誉材料的例外与「级别不得夸大」",
          "级别不得夸大" in docs["references/writing-rules.md"],
          "见 references/writing-rules.md 规则 2")
    check("T32 SKILL/data-spec/writing-rules 都写到「荣誉」",
          all("荣誉" in docs[r] for r in
              ("SKILL.md", "references/data-spec.md", "references/writing-rules.md")),
          [r for r in ("SKILL.md", "references/data-spec.md",
                       "references/writing-rules.md") if "荣誉" not in docs[r]])

    print("=" * 68)
    print("通过 %d / 失败 %d" % (len(PASS), len(FAIL)))
    if FAIL:
        print("失败用例：" + "、".join(FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
