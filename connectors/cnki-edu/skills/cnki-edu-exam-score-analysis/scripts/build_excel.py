# -*- coding: utf-8 -*-
"""Excel 结果册生成器：从 analysis.json 产出多工作表 xlsx。

用法::

    python build_excel.py --analysis analysis.json [--out 高二期末_数语物_成绩分析结果册.xlsx]

也可作为模块被 report_builder.py 调用::

    from build_excel import build
    build("analysis.json", "xxx.xlsx")

依赖：openpyxl。输入只要求 analysis.json —— 学生成绩从
``results[学科].individuals.ranking`` 还原，无需再传原始成绩表。

结果册**只放分析结果与教学要用的事实**，不承载「数据说明」类内部交代（用户要求
2026-10-08）：满分设定 / 分数线设定 / 数据来源 / ``data_notes`` / 未生成工作表的原因
一律不写进工作表。这些内容在 ``analysis.json``、命令行输出与**对话交付说明**里交代。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# openpyxl 只在真正生成 xlsx 时才必需。这里做成软依赖：缺少时模块仍可被 import
# （report_builder 会捕获异常并降级出 HTML/PDF），但单独运行会给出可执行的安装指引，
# 而不是一句裸的 ModuleNotFoundError。
_IMPORT_ERR = None
try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError as exc:  # pragma: no cover
    _IMPORT_ERR = exc
    HAS_OPENPYXL = False

    class _StyleStub:
        """占位对象：让下面的样式常量在没有 openpyxl 时也能完成模块级求值。"""

        def __init__(self, *a, **k):
            pass

        def __call__(self, *a, **k):
            return self

    Workbook = PatternFill = Font = Alignment = Border = Side = get_column_letter = _StyleStub


def require_openpyxl():
    if not HAS_OPENPYXL:
        raise RuntimeError(
            "生成 Excel 结果册需要 openpyxl（原始错误：%s）。\n"
            "请用**同一个** Python 解释器安装后重跑：\n"
            "  \"%s\" -m pip install openpyxl" % (_IMPORT_ERR, sys.executable))

# --------------------------------------------------------------------------- #
# 样式
# --------------------------------------------------------------------------- #
HDR_FILL = PatternFill("solid", fgColor="2F5597")
HDR_FONT = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="微软雅黑", size=13, bold=True, color="1F3864")
SUB_FONT = Font(name="微软雅黑", size=9, italic=True, color="7F7F7F")
BODY_FONT = Font(name="微软雅黑", size=10)
BOLD_FONT = Font(name="微软雅黑", size=10, bold=True)
RED_BOLD = Font(name="微软雅黑", size=10, bold=True, color="C00000")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

FILL = {
    "优秀": PatternFill("solid", fgColor="D6E4F7"),
    "良好": PatternFill("solid", fgColor="E2EFDA"),
    "达标题": PatternFill("solid", fgColor="E2EFDA"),
    "薄弱": PatternFill("solid", fgColor="FFF2CC"),
    "薄弱题": PatternFill("solid", fgColor="FFF2CC"),
    "危险": PatternFill("solid", fgColor="FCE4E4"),
    "共性错题": PatternFill("solid", fgColor="FCE4E4"),
}
NORMAL_FILL = PatternFill("solid", fgColor="EDF6E9")
WARN_FILL = PatternFill("solid", fgColor="FFF2CC")
ALERT_FILL = PatternFill("solid", fgColor="FCE4E4")


def rate_fill(rate):
    """按得分率返回底色——与逐题判定同一套色阶（<60% 红 / 60–75% 橙 / 75–85% 绿 / ≥85% 蓝）。

    ``rate`` 为 None（该生该题无作答记录）时返回 None，格子留白——缺答不等于 0 分。
    """
    if rate is None:
        return None
    if rate < 0.6:
        return FILL["共性错题"]
    if rate < 0.75:
        return FILL["薄弱题"]
    if rate < 0.85:
        return FILL["达标题"]
    return FILL["优秀"]


def pct(v, nd=1):
    return "-" if v is None else "%.*f%%" % (nd, v * 100)


def num(v, nd=2):
    return "-" if v is None else round(float(v), nd)


def q_sort_key(q):
    """题号升序键（用户要求 2026-10-11：表内题号列一律升序）：
    纯数字按数值排（1 < 2 < 10），非纯数字（如「三、实验题」）排在数字题之后。"""
    s = str(q)
    return (0, int(s), "") if s.isdigit() else (1, 0, s)


def band_range(b, full):
    """分数段 → **实际分数区间**（与报告侧 `report_builder.band_range` 同一写法，用户要求 2026-10-11）：

    段边界在数据里是「占满分比例」（``lo`` / ``hi``），渲染前按该科满分换算成分数；
    末档的 ``hi`` 是哨兵值（>1），用 ``min(hi, 1)`` 收成满分，避免出现「135 – 满分 分」这种拼接残渣。
    报告与结果册**必须写成同一种形式**（如「135 – 150 分」），否则同一份数据两处对不上。
    """
    full = full or 0
    lo = b.get("lo") or 0
    hi = min(b.get("hi") or 0, 1.0)
    return "%g – %g 分" % (lo * full, hi * full)


def scope_slug(subs):
    """学科范围的文件名简写：≤4 科直接连写，更多则用「全N科」，避免文件名里出现顿号。"""
    subs = list(subs or [])
    if not subs:
        return "全部学科"
    return "".join(subs) if len(subs) <= 4 else "全%d科" % len(subs)


def plain(v):
    """Excel 单元格是**纯文本**：Markdown 的 ``**加粗**`` 不会渲染，写进去只会显示成字面星号。
    表注 / 标题 / 数据统一在入库前剥掉强调标记（用户要求 2026-10-11）。"""
    return v.replace("**", "") if isinstance(v, str) else v


class Sheet:
    """带标题行 / 表头 / 冻结窗格的简易工作表包装。"""

    def __init__(self, wb, name, title, headers, widths, note=None):
        self.ws = wb.create_sheet(name)
        ws = self.ws
        ws["A1"] = plain(title)
        ws["A1"].font = TITLE_FONT
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(len(headers), 1))
        ws.row_dimensions[1].height = 24
        self.r = 2
        if note:
            ws["A2"] = plain(note)
            ws["A2"].font = SUB_FONT
            ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max(len(headers), 1))
            self.r = 3
        for j, h in enumerate(headers, 1):
            c = ws.cell(self.r, j, plain(h))
            c.fill, c.font, c.alignment, c.border = HDR_FILL, HDR_FONT, CENTER, BORDER
        ws.row_dimensions[self.r].height = 30
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = ws.cell(self.r + 1, 1)
        self.rows = 0

    def add(self, vals, fills=None, wrap_left=True):
        self.r += 1
        self.rows += 1
        for j, v in enumerate(vals, 1):
            c = self.ws.cell(self.r, j, plain(v))
            c.font, c.border = BODY_FONT, BORDER
            wide = isinstance(v, str) and len(v) > 14
            c.alignment = LEFT if (wide and wrap_left) else CENTER
        for j, f in (fills or {}).items():
            if f is not None:
                self.ws.cell(self.r, j).fill = f
        return self.r


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def build(analysis_path, out=None, quiet=False):
    """只吃 ``analysis.json``，不再需要 narrative.json。

    结果册**不承载数据说明**（用户要求 2026-10-08）：``data_notes``（缺失值 / 统计范围 /
    排序告警 / 重复学号合并等）与 ``meta`` 里的满分设定、分数线设定、数据来源一律不写进
    工作表；这些只出现在 ``analysis.json``、命令行输出与**对话交付说明**里。
    被剔除学生的**逐个点名**仍保留（班主任对名单要用），且明细在 ``data_excluded``。
    """
    require_openpyxl()
    with open(analysis_path, "r", encoding="utf-8") as fh:
        an = json.load(fh)

    meta = an["meta"]
    subs = meta["subjects"]
    R = an["results"]
    CROSS = an.get("cross_subject") or {}

    # ---- 从各科 ranking 还原学生成绩（无需原始表） ----
    students = {}
    for s in subs:
        for rec in R[s]["individuals"].get("ranking", []):
            st = students.setdefault(rec["sid"], {"sid": rec["sid"], "name": rec["name"],
                                                 "cls": rec.get("cls", ""), "scores": {}})
            st["scores"][s] = rec["score"]
    nsub = len(subs)
    full_total = sum(R[s]["full"] for s in subs)
    for st in students.values():
        st["total"] = sum(st["scores"].get(s, 0) for s in subs)
        st["n_valid"] = len(st["scores"])
        st["rate"] = st["total"] / full_total if full_total else 0
    srows = sorted(students.values(), key=lambda x: -x["total"])
    for i, st in enumerate(srows, 1):
        st["rank"] = i
    total_mean = (sum(st["total"] for st in srows) / len(srows)) if srows else 0
    if srows:
        tmax = max(st["total"] for st in srows)
        tmin = min(st["total"] for st in srows)
        top = [st["name"] for st in srows if st["total"] == tmax]
        bot = [st["name"] for st in srows if st["total"] == tmin]
    else:
        tmax = tmin = 0
        top = bot = []

    wb = Workbook()
    wb.remove(wb.active)
    # 清掉工作簿的文档属性（用户要求 2026-10-12）：openpyxl 默认把 creator 写成
    # "openpyxl"，老师在「文件 → 信息 → 属性」里会看到这个内部库名；lastModifiedBy
    # 同理。交付文件只留成绩分析本身，不留生成工具的痕迹。
    _props = wb.properties
    _props.creator = ""
    _props.lastModifiedBy = ""
    _props.title = ""
    _props.subject = ""
    _props.description = ""
    _props.keywords = ""
    _props.category = ""

    # 逐题 / 知识点 / 年级层 / 历次 数据是否存在——决定 04、05、09、10 要不要生成（缺数据就不生成，不摆占位行）
    has_q = any(R[s]["questions"] for s in subs)
    has_kp = any(R[s]["knowledge_points"] for s in subs)
    has_grade = bool(an.get("grade_overview"))
    has_hist = bool(an.get("history_summary"))
    # 单科分析（模式 A）下「偏科诊断」无从谈起：只有一科时人人强弱极差都是 0，
    # 生成出来是一张只有表头、一行数据都没有的空表 → 整表不生成（与 04/05/09/10 的处理方式一致）。
    has_balance = nsub >= 2

    # -------------------------------------------------------------- 01 阅读说明
    sh = Sheet(wb, "01 阅读说明",
               "%s · 成绩分析结果册" % meta["exam_name"],
               ["项目", "内容"], [22, 118],
               note=None)
    nav = ["02 学科总览", "03 分数段分布"]
    if has_q:
        nav.append("04 逐题得分率")
    if has_kp:
        nav.append("05 知识点优先级")
    nav += ["06 学生成绩与排名", "07 临界生与分层名单"]
    if has_balance:
        nav.append("08 学生学科均衡性")
    if has_grade:
        nav.append("09 年级班级排名")
    if has_hist:
        nav.append("10 历次成绩对比")
    nav_desc = {   # 与 nav 一一对应的说明文字
        "02 学科总览": "各学科关键指标横向对比（含四率），含分数形态与预警着色",
        "03 分数段分布": "各学科 5 个分数段的人数、占比、累计占比（分数段按各科满分换算成具体分数区间；长表，可直接做数据透视）",
        "04 逐题得分率": "逐题平均得分、得分率、判定等级、各班得分率（各科内按题号升序，讲评优先级见 P 列）",
        "05 知识点优先级": "知识点掌握等级与 P1/P2… 讲评优先级",
        "06 学生成绩与排名": "全体学生各科成绩、各科名次、总分与总分排名（低于及格线标红）",
        "07 临界生与分层名单": "按学科点名：尖子生 / 临界优秀 / 临界及格 / 学困生 / 学科前 20",
        "08 学生学科均衡性": "个人各科得分率、强弱极差、最弱/最强学科（偏科诊断）",
        "09 年级班级排名": "班级总分排名 + 各学科班级排名 + 全年级各学科四率（全年级分数段分布见「03 分数段分布」）",
        "10 历次成绩对比": "历次年级 / 历次班级的总分与各学科成绩、四率变化",
    }
    # 只分析了部分学科时，「全科总分」是错的（主表里还有别的学科列没算进来）
    total_label = meta.get("total_label") or "全科总分"
    # 被剔除的学生必须逐个点名——否则班主任对名单时会发现少人却查不到原因。
    # 先算出来：下面「学生名单范围」要不要写「见下方未纳入统计的学生」取决于它是否为空。
    exc = an.get("data_excluded") or {}
    exc_rows = [(s, e) for s in subs for e in (exc.get(s) or [])]
    # 阅读说明只留「分析结果 + 对账要用的事实」（用户要求 2026-10-08~今）：
    # 不放 满分设定 / 分数线设定 / 数据来源 / 数据说明 / 未生成的工作表 / 主表工作表 /
    # 逐题·知识点·名单范围。满分与各科分数线已逐列写在「02 学科总览」；源文件名、
    # 工作表名、脚本内部信息都属于内部信息，老师不需要在结果册里看到。
    info = [
        ("考试名称", meta["exam_name"]),
        ("分析班级", meta["focus_class"]),
        ("样本人数", "%d 人" % meta["student_count"]),
        ("分析学科", "、".join(subs)),
        (total_label, "均分 %.1f / %g（得分率 %s）；最高 %g（%s）；最低 %g（%s）"
         % (total_mean, full_total, pct(total_mean / full_total if full_total else 0),
            tmax, "、".join(top) or "-", tmin, "、".join(bot) or "-")),
        # 全员计入时不写「被剔除学生见下方…」——否则指着一个并不存在的表
        ("学生名单范围", "「%s」共 %d 人%s。"
         % (meta.get("individual_scope") or "全部样本", len(srows),
            "；被剔除学生见下方「未纳入统计的学生」" if exc_rows else "，全部计入统计")),
        ("生成时间", meta.get("generated_at") or "-"),
        ("", ""),
    ] + [(k, nav_desc[k]) for k in nav]
    for k, v in info:
        r = sh.add([k, v])
        sh.ws.cell(r, 1).font = BOLD_FONT
    # 满分未经用户确认的，必须在阅读说明里置顶点名（满分错了整册的数据基准都错）
    pending_full = meta.get("full_to_confirm") or []
    if pending_full:
        r = sh.add(["⚠️ 待确认的满分", "以下学科的满分不是用户指定的，请核对后再使用："])
        sh.ws.cell(r, 1).font = RED_BOLD
        sh.ws.cell(r, 2).font = Font(name="微软雅黑", size=9, color="C00000")
        for x in pending_full:
            how = ("由成绩分布推断（依据：%s）" % x.get("basis", "-")) if x.get("source") == "inferred" \
                else "按常规 100 分制默认（未做数据校验；语文/数学也可能 150、英语 120、小学科 10/5）"
            r = sh.add(["", "%s → %g 分：%s。" % (x["subject"], x["full"], how)])
            sh.ws.cell(r, 2).font = Font(name="微软雅黑", size=9, color="C00000")

    # 被剔除的学生逐个点名（exc_rows 已在上面算好）
    if exc_rows:
        r = sh.add(["未纳入统计的学生（逐科剔除，不计 0 分）", ""])
        sh.ws.cell(r, 1).font = RED_BOLD
        for s, e in exc_rows:
            r = sh.add([s, "%s（%s）　原始值 %s　原因：%s"
                        % (e.get("name", ""), e.get("cls", ""), e.get("raw", ""), e.get("reason", ""))])
            sh.ws.cell(r, 2).font = Font(name="微软雅黑", size=9, color="C00000")
        r = sh.add(["", "以上学生该科成绩未参与任何统计（均分/及格率/排名/分层/逐题），如需按 0 分计请修正原表后重跑。"])
        sh.ws.cell(r, 2).font = Font(name="微软雅黑", size=9, color="C00000")

    # -------------------------------------------------------------- 02 学科总览
    sh = Sheet(wb, "02 学科总览", "各学科关键指标横向对比（按得分率降序）",
               ["学科", "满分", "及格线", "优秀线", "低分线", "参考人数", "平均分", "中位数", "最高分", "最低分",
                "极差", "标准差", "标准差/满分", "得分率", "及格率", "优秀率", "良好率", "合格率", "不合格率",
                "低分率", "相对学科均值", "分数形态"],
               [9, 7, 8, 8, 8, 9, 9, 8, 8, 8, 7, 8, 11, 9, 9, 9, 9, 9, 9, 9, 12, 11],
               note="四率（优秀 ≥85%｜良好 70–85%｜合格 60–70%｜不合格 <60%）为**互斥**档，相加 100%；"
                    "「及格率」是 ≥60% 的累计值，与四率不在同一层。"
                    "标准差/满分 ≥20% 标红、≥16% 标橙；及格率 <80% 标红、<90% 标橙；低分率 >10% 标红、>5% 标橙；"
                    "「相对学科均值」= (本学科得分率 − 各科得分率均值) ÷ 各科得分率均值 × 100%（正 = 高于学科均值）。"
                    + ("多班样本：上方按学科的行为「本册主范围」，其后依次列「各班层」与「全年级层」。"
                       if meta.get("multi_class") else ""))
    tabs = sorted(CROSS.get("table") or [], key=lambda t: -(t["score_rate"] or 0))
    avg_rate = (sum(t["score_rate"] for t in tabs) / len(tabs)) if tabs else 0
    for t in tabs:
        s = t["subject"]
        st = R[s]
        stdr = (t["std"] or 0) / t["full"]
        fills = {}
        if stdr >= 0.20:
            fills[13] = ALERT_FILL
        elif stdr >= 0.16:
            fills[13] = WARN_FILL
        if t["pass_rate"] < 0.80:
            fills[15] = ALERT_FILL
        elif t["pass_rate"] < 0.90:
            fills[15] = WARN_FILL
        if (t.get("fail_rate") or 0) > 0.20:
            fills[19] = ALERT_FILL
        if t["low_rate"] > 0.10:
            fills[20] = ALERT_FILL
        elif t["low_rate"] > 0.05:
            fills[20] = WARN_FILL
        fills[22] = ALERT_FILL if t["shape"] == "尾部沉重" else FILL["良好"]
        sh.add([s, t["full"], st["pass"], st["excellent"], st["low"],
                t.get("count") or st["stats"]["count"],
                num(t["mean"]), num(t["median"]), num(t["max"]), num(t["min"]),
                num(st["stats"]["range"]), num(t["std"]), pct(stdr, 2), pct(t["score_rate"]),
                pct(t["pass_rate"]), pct(t["excellent_rate"]), pct(t.get("good_rate")),
                pct(t.get("qualified_rate")), pct(t.get("fail_rate")), pct(t["low_rate"]),
                pct((t["score_rate"] - avg_rate) / avg_rate, 2) if avg_rate else "-", t["shape"]],
               fills=fills)
    if tabs:
        mean_of_means = sum(t["mean"] for t in tabs) / len(tabs)
        r = sh.add(["学科均值", "", "", "", "", "", num(mean_of_means), "", "", "", "", "", "",
                    pct(avg_rate), "", "", "", "", "", "", "", ""])
        for j in range(1, 23):
            sh.ws.cell(r, j).font = BOLD_FONT
    # 各班层（用户要求 2026-10-11）：逐个班级给出各学科四率与关键指标。
    # 放在「本册主范围」与「全年级层」之间，班主任可直接筛出本班与平行班对照。
    # 第一列写成「班级 · 学科」，避免为此改列结构；本班已作为主行给出，此处不重复。
    if meta.get("multi_class"):
        sh.add([""] * 22)
        r = sh.add(["—— 各班层（逐个班级 · 各学科）——"] + [""] * 21)
        sh.ws.cell(r, 1).font = BOLD_FONT
        for t in tabs:
            st = R[t["subject"]]
            for c in ((st.get("comparison") or {}).get("by_class") or []):
                if c.get("name") == meta.get("focus_class"):
                    continue
                cr = c.get("score_rate")
                sh.add(["%s · %s" % (c.get("name"), t["subject"]),
                        st["full"], st["pass"], st["excellent"], st["low"], c.get("count"),
                        num(c.get("mean")), num(c.get("median")), num(c.get("max")), num(c.get("min")),
                        num(c.get("range")), num(c.get("std")), pct((c.get("std") or 0) / st["full"], 2),
                        pct(cr), pct(c.get("pass_rate")), pct(c.get("excellent_rate")),
                        pct(c.get("good_rate")), pct(c.get("qualified_rate")),
                        pct(c.get("fail_rate")), pct(c.get("low_rate")),
                        pct((cr - avg_rate) / avg_rate, 2) if (avg_rate and cr) else "-", "-"])
    # 全年级层（全部样本）指标：多班样本时另起一段，直接对照「本册主范围」与「全年级」
    if meta.get("multi_class"):
        sh.add(["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
        r = sh.add(["—— 全年级层（全部样本）——", "", "", "", "", "", "", "", "", "", "", "", "", "",
                    "", "", "", "", "", "", "", ""])
        sh.ws.cell(r, 1).font = BOLD_FONT
        for s in subs:
            ga = R[s].get("stats_all") or {}
            if not ga.get("count"):
                continue
            sh.add([s, R[s]["full"], R[s]["pass"], R[s]["excellent"], R[s]["low"], ga["count"],
                    num(ga["mean"]), num(ga["median"]), num(ga["max"]), num(ga["min"]),
                    num(ga["range"]), num(ga["std"]),
                    pct((ga["std"] or 0) / R[s]["full"], 2), pct(ga["score_rate"]),
                    pct(ga["pass_rate"]), pct(ga["excellent_rate"]), pct(ga.get("good_rate")),
                    pct(ga.get("qualified_rate")), pct(ga.get("fail_rate")), pct(ga["low_rate"]),
                    "-", "-"])

    # -------------------------------------------------------------- 03 分数段分布
    multi_cls = bool(meta.get("multi_class"))
    # 用户要求 2026-10-11：分数段以**具体成绩**呈现（「0 – 90 分」），比例档只作辅助列放后面。
    sh = Sheet(wb, "03 分数段分布", "各学科分数段分布（具体分数区间 / 人数 / 占比）",
               ["学科", "范围", "分数段（分数）", "分段（占满分比例）", "人数", "占比", "累计占比"],
               [9, 15, 22, 18, 8, 9, 11],
               note="「分数段（分数）」按该科满分换算成**实际分数区间**（各科满分不同，同一档对应的区间也不同）；"
                    "「分段（占满分比例）」= 不及格 <60%、60–70%、70–80%、80–90%、优秀 ≥90%。"
                    + ("多班样本：先列本班（%s），再逐个班给出各班，最后列「全年级（全部样本）」。"
                       % meta.get("focus_class") if multi_cls else "")
                    + "同一学科 5 行，可直接做数据透视。")
    for s in subs:
        full = R[s]["full"]
        for b in R[s]["bands"]:
            fill = FILL["危险"] if b["label"].startswith("不及格") else (
                FILL["优秀"] if b["label"].startswith("优秀") else None)
            sh.add([s, meta.get("individual_scope") or "全部样本",
                    band_range(b, full), b["label"],
                    b["count"], pct(b["ratio"]), pct(b["cum"])],
                   fills={4: fill})
    if multi_cls:
        # 各班层（用户要求 2026-10-11）：每个班各学科的分数段分布，放在本班与全年级之间
        for s in subs:
            full = R[s]["full"]
            for c in ((R[s].get("comparison") or {}).get("by_class") or []):
                if c.get("name") == meta.get("focus_class"):
                    continue
                for b in (c.get("bands") or []):
                    fill = FILL["危险"] if b["label"].startswith("不及格") else (
                        FILL["优秀"] if b["label"].startswith("优秀") else None)
                    sh.add([s, c["name"], band_range(b, full), b["label"],
                            b["count"], pct(b["ratio"]), pct(b["cum"])], fills={4: fill})
        for s in subs:
            full = R[s]["full"]
            for b in (R[s].get("bands_all") or []):
                fill = FILL["危险"] if b["label"].startswith("不及格") else (
                    FILL["优秀"] if b["label"].startswith("优秀") else None)
                sh.add([s, "全年级（全部样本）", band_range(b, full), b["label"],
                        b["count"], pct(b["ratio"]), pct(b["cum"])], fills={4: fill})

    # -------------------------------------------------------------- 04 逐题得分率
    # 没有逐题数据的科目**不写「数据缺失」占位行**；全部科目都没有这一列数据时，
    # 整张工作表不生成（报告侧同样整节不渲染）。
    has_q = any(R[s]["questions"] for s in subs)
    two_level = bool(meta.get("two_level_questions"))
    cls_name = meta.get("individual_scope") or "全部样本"
    # 各班逐题得分率（用户要求 2026-10-11）：逐题数据带「学号」且样本有多个班时才给
    class_cols = [c for c in (meta.get("classes") or [])] if meta.get("has_class_question_detail") else []
    if has_q:
        # 逐题数据没有知识点归属时，不摆一列空白的「知识点」——空列本身也是占位
        with_kp = has_kp
        lead = ["学科", "题号"] + (["知识点 / 模块"] if with_kp else []) + ["满分"]
        if two_level:
            # 班级层与年级层并列（用户要求 2026-10-10）：两套均分/得分率/判定同时给出
            cols = lead + ["本班均分", "本班得分率", "本班判定", "讲评优先级", "本班作答",
                           "年级均分", "年级得分率", "年级判定", "年级作答"]
            widths = [9, 14] + ([30] if with_kp else []) + [7, 9, 10, 10, 11, 9, 9, 10, 10, 9]
            note = ("判定：共性错题 <60%%｜薄弱题 60–75%%｜达标题 75–85%%｜优势题 ≥85%%；"
                    "得分率 = 该题平均得分 ÷ 该题满分。**两层并列**：本班 = 「%s」，"
                    "年级 = 全部样本（%d 人）。表内**按题号升序**；"
                    "「讲评优先级」按**本班得分率**升序标注，P1 最需先讲。"
                    % (cls_name, meta.get("grade_scope_count") or meta.get("student_count") or 0))
        else:
            cols = lead + ["平均得分", "得分率", "判定等级", "讲评优先级", "作答人数"]
            widths = [9, 14] + ([30] if with_kp else []) + [7, 9, 9, 11, 11, 9]
            note = ("判定：共性错题 <60%%｜薄弱题 60–75%%｜达标题 75–85%%｜优势题 ≥85%%；"
                    "得分率 = 该题平均得分 ÷ 该题满分。本表范围为「%s」。"
                    "表内**按题号升序**；「讲评优先级」按得分率升序标注，P1 最需先讲。"
                    % cls_name)
        if class_cols:
            cols += ["%s得分率" % c for c in class_cols]
            widths += [11] * len(class_cols)
            note += "末尾逐列给出**每个班级**在该小题上的得分率（每班每题）。"
        note += ("" if with_kp else "本表不含「知识点」列——逐题数据里没有知识点归属（不编造）。")
        note += ("" if all(R[s]["questions"] for s in subs)
                 else "（无逐题数据的科目未列入本表。）")
        sh = Sheet(wb, "04 逐题得分率", "逐题得分率明细（各科内按题号升序；讲评优先级见「P」列）",
                   cols, widths, note=note)
        lvl_idx = cols.index("本班判定" if two_level else "判定等级") + 1
        lvl_all_idx = cols.index("年级判定") + 1 if two_level else None
        for s in subs:
            if not R[s]["questions"]:
                continue
            # 用户要求 2026-10-11：表内**题号列按题号升序**（与试卷题序对照）。
            # 讲评优先级 P1… 另按得分率升序单独算名次——行序不再是得分率序，不能用行号当 P 值。
            prio = {q["q"]: i for i, q in enumerate(sorted(R[s]["questions"],
                                                          key=lambda x: x["rate"]), 1)}
            for q in sorted(R[s]["questions"], key=lambda x: q_sort_key(x["q"])):
                vals = ([s, q["q"]] + ([q["kp"]] if with_kp else []) + [q["full"]])
                if two_level:
                    vals += [num(q["mean"]), pct(q["rate"]), q["level"], "P%d" % prio[q["q"]], q.get("n"),
                             num(q.get("mean_all")), pct(q.get("rate_all")),
                             q.get("level_all"), q.get("n_all")]
                    fills = {lvl_idx: FILL.get(q["level"])}
                    if lvl_all_idx:
                        fills[lvl_all_idx] = FILL.get(q.get("level_all"))
                else:
                    vals += [num(q["mean"]), pct(q["rate"]), q["level"],
                             "P%d" % prio[q["q"]], q.get("n")]
                    fills = {lvl_idx: FILL.get(q["level"])}
                if class_cols:
                    byc = {c["cls"]: c for c in (q.get("by_class") or [])}
                    base = len(vals) + 1
                    vals += [pct(byc[c]["rate"]) if c in byc else "" for c in class_cols]
                    for k, c in enumerate(class_cols):
                        if c in byc:
                            fills[base + k] = rate_fill(byc[c]["rate"])
                sh.add(vals, fills=fills)

    # -------------------------------------------------------------- 05 知识点优先级
    # 整表的存在与否只看 has_kp（= 引擎里有没有聚合出知识点）。
    # 输入表没有「知识点」列、该列整列为空、或只填了 -、/ 、「无」这类占位符时，
    # 引擎的 knowledge_points 一律为空 → 这里整张表不生成（不摆空表、不写「数据缺失」）。
    if has_kp:
        sh = Sheet(wb, "05 知识点优先级", "知识点掌握度与讲评优先级（各科内按得分率升序 = 讲评顺序）",
                   ["学科", "优先级", "知识点 / 模块", "得分率", "掌握等级", "涉及题目", "题数"],
                   [9, 9, 32, 9, 11, 30, 7],
                   note="等级：危险 <60%｜薄弱 60–75%｜良好 75–85%｜优秀 ≥85%。优先级 P1 最需先讲；"
                        "建议每科优先处理 P1–P3。"
                        + ("" if all(R[s]["knowledge_points"] for s in subs)
                           else "（无知识点数据的科目未列入本表。）"))
        for s in subs:
            kps = R[s]["knowledge_points"]
            if not kps:
                continue
            for k in kps:
                sh.add([s, "P%d" % k["priority"], k["kp"], pct(k["rate"]), k["level"],
                        "、".join(k["questions"]), k["question_count"]],
                       fills={5: FILL.get(k["level"])})

    # -------------------------------------------------------------- 06 学生成绩与排名
    scope_label = meta.get("individual_scope") or "全部样本"
    scope_tag = "本班" if meta.get("individual_scope_is_focus") else "样本（含各班）"
    # 每科名次（用户要求 2026-10-11）：取自各科 individuals.ranking（同一名单范围内排序）
    subj_rank = {}
    for s in subs:
        subj_rank[s] = {rec["sid"]: rec.get("rank")
                        for rec in (R[s]["individuals"].get("ranking") or [])}
    # 姓名与学号**各占一列**（用户要求 2026-10-11）；数据里没有真学号时
    # **「学号」列整列不生成**——不拿 #N 兜底编号冒充学号（见 meta.has_student_id）。
    has_sid = bool(meta.get("has_student_id"))
    id_cols = ["学号"] if has_sid else []
    item_cols = ["总分排名"] + id_cols + ["姓名", "班级"] + subs + \
                ["%s名次" % s for s in subs] + \
                [total_label, "总分得分率", "与%s均分差" % scope_tag, "有效科数"]
    sh = Sheet(wb, "06 学生成绩与排名", "%s · 学生成绩明细与排名（按总分降序）" % scope_label,
               item_cols,
               [9] + ([12] if has_sid else []) + [10, 11] + [7] * nsub + [9] * nsub +
               [10, 11, 11, 9],
               note="名单范围：%s。%s满分 %g 分（%d 科合计）。低于及格线的单科标红；"
                    "「各科名次」为**该科在本名单范围内的排名**（同一学生可在不同科目名次不同）；"
                    "「有效科数」<%d 表示存在缺考/空值（按缺失剔除，不计 0 分，被剔除学生见「01 阅读说明」）。"
                    % (scope_label, total_label, full_total, nsub, nsub))
    i_score = 4 + len(id_cols)      # 各科成绩起始列（1-based；排名/（学号）/姓名/班级）
    i_subrank = i_score + nsub      # 各科名次起始列
    i_total = i_subrank + nsub      # 总分列
    for st in srows:
        vals = [st["rank"]] + ([st["sid"]] if has_sid else []) + [st["name"], st["cls"]] + \
               [st["scores"].get(s, "缺考") for s in subs] + \
               [subj_rank.get(s, {}).get(st["sid"], "-") for s in subs] + \
               [st["total"], pct(st["rate"]), num(st["total"] - total_mean, 1), st["n_valid"]]
        fills = {}
        for j, s in enumerate(subs):
            v = st["scores"].get(s)
            if v is None or v < R[s]["pass"]:
                fills[i_score + j] = ALERT_FILL
        diff = st["total"] - total_mean
        fills[i_total + 1] = FILL["优秀"] if st["rate"] >= 0.85 else (
            FILL["良好"] if st["rate"] >= 0.60 else FILL["危险"])
        if diff >= 0:
            fills[i_total + 2] = FILL["良好"]
        elif diff <= -0.10 * full_total:
            fills[i_total + 2] = ALERT_FILL
        else:
            fills[i_total + 2] = WARN_FILL
        r = sh.add(vals, fills=fills)
        for j, s in enumerate(subs):
            if (st["scores"].get(s) or 999) < R[s]["pass"]:
                sh.ws.cell(r, i_score + j).font = RED_BOLD
    if srows:
        r = sh.add(["本班均" if meta.get("individual_scope_is_focus") else "样本均"] +
                   [""] * len(id_cols) + ["%d 人" % len(srows), ""] + [""] * (2 * nsub) +
                   [num(total_mean, 1), pct(total_mean / full_total if full_total else 0), "", ""])
        for j in range(1, len(item_cols) + 1):
            sh.ws.cell(r, j).font = BOLD_FONT

    # -------------------------------------------------------------- 07 分层名单
    hist_order_unknown = an["meta"].get("history_order_source") == "unknown"
    sh = Sheet(wb, "07 临界生与分层名单", "各学科个体分层名单（尖子生 / 临界优秀 / 临界及格 / 学困生）",
               ["学科", "分层", "人数", "学生名单（姓名 + 分数）", "距分数线"],
               [9, 13, 7, 96, 20],
               note="分层规则（按各科实际分数线）：尖子生 ≥ 优秀线；临界优秀 = 优秀线 −5%满分 至 优秀线；"
                    "临界及格 = 及格线 −5%满分 至 及格线；学困生 < 低分线。各科满分与分数线见「02 学科总览」。"
                    "名单按分数排序；优先处理「临界优秀」「临界及格」两类。"
                    "提供历次成绩时，末尾附「进步榜 / 需关注名单」（名次变化 +N = 前进 N 名）。"
                    + ("⚠️ 本次历次考试的**先后顺序无法判定**，末尾两张名单可能整体反向，请先核对"
                       "（补一列「序号」或「日期」后重跑即可自动排序）。"
                       if hist_order_unknown else ""))
    LABELS = [("尖子生", "优秀"), ("临界优秀", "良好"), ("临界及格", "薄弱"), ("学困生", "危险")]
    for s in subs:
        L = R[s]["individuals"]["lists"]
        for key, lv in LABELS:
            v = L.get(key) or []
            gaps = ""
            if v and key == "临界优秀":
                gaps = "距优秀线 %g–%g 分" % (min(x["gap"] for x in v), max(x["gap"] for x in v))
            elif v and key == "临界及格":
                gaps = "距及格线 %g–%g 分" % (min(x["gap"] for x in v), max(x["gap"] for x in v))
            sh.add([s, key, len(v),
                    "、".join("%s %g" % (x["name"], x["score"]) for x in v) or "无",
                    gaps], fills={2: FILL.get(lv)})
        rank = R[s]["individuals"].get("ranking") or []
        if rank:
            sh.add([s, "学科排名前 20", min(20, len(rank)),
                    "、".join("%d.%s %g" % (x["rank"], x["name"], x["score"]) for x in rank[:20]), ""])
    # 有历次成绩时，附进退步名单（基于历次「总分」，与学科无关，故只输出一次）
    hist = next((R[s]["individuals"]["lists"] for s in subs
                 if "进步榜" in R[s]["individuals"]["lists"]), None)
    if hist:
        for key, lv in (("进步榜", "优秀"), ("需关注名单", "危险")):
            v = hist.get(key) or []
            if not v:
                continue
            desc = "、".join(
                "%s（总分 %g→%g，%+g；名次 %+g）"
                % (x.get("name", x.get("sid", "")),
                   (x.get("totals") or [0])[0], (x.get("totals") or [0])[-1],
                   x.get("total_delta") or 0, x.get("rank_delta") or 0)
                for x in v)
            sh.add(["历次总分", key, len(v), desc,
                    "⚠️ 考试顺序待核对，本名单可能整体反向" if hist_order_unknown
                    else "名次 +N = 前进 N 名；按变化量排序"], fills={2: FILL.get(lv)})

    # -------------------------------------------------------------- 08 学科均衡性
    # 同样是学生逐人表，姓名与学号各占一列（用户要求 2026-10-11；无真学号时不出现该列）
    # 单科分析时整表不生成（has_balance 为假）——偏科诊断至少需要两科才有意义。
    if has_balance:
        bal_head = id_cols + ["姓名", total_label, "总分排名"]
        bal_width = ([12] if has_sid else []) + [10, 10, 9]
        sh = Sheet(wb, "08 学生学科均衡性", "学生各科得分率与偏科分析（按强弱极差降序）",
                   bal_head + ["%s得分率" % s for s in subs] +
                   ["强弱极差", "最弱学科", "最强学科"],
                   bal_width + [11] * nsub + [10, 11, 11],
                   note="强弱极差 = 个人最强科得分率 − 最弱科得分率；≥20% 标红、≥15% 标橙，视为明显偏科，"
                        "建议一人一策。")
        bal = []
        for st in srows:
            rates = [(st["scores"][s] / R[s]["full"], s) for s in subs if s in st["scores"]]
            if len(rates) < 2:
                continue
            lo, hi = min(rates), max(rates)
            bal.append((hi[0] - lo[0], st, lo, hi))
        bal.sort(key=lambda x: -x[0])
        i_spread = len(bal_head) + nsub + 1     # 「强弱极差」列的 1-based 列号
        for spread, st, lo, hi in bal:
            fills = {}
            if spread >= 0.20:
                fills[i_spread] = ALERT_FILL
            elif spread >= 0.15:
                fills[i_spread] = WARN_FILL
            sh.add(([st["sid"]] if has_sid else []) + [st["name"], st["total"], st["rank"]] +
                   [pct(st["scores"][s] / R[s]["full"]) if s in st["scores"] else "缺考" for s in subs] +
                   [pct(spread), lo[1], hi[1]], fills=fills)

    # ------------------------------------------------- 09 年级班级排名
    # 全年级总分按班级排名 + 每个学科按班级排名 + 全年级各学科四率与分数段（用户要求 2026-10-11）。
    go = an.get("grade_overview") or {}
    if go:
        sh = Sheet(wb, "09 年级班级排名",
                   "全年级视角：班级总分排名 · 各学科班级排名 · 全年级各学科四率",
                   ["层级", "项目", "学科", "班级", "人数", "平均分", "总满分", "得分率",
                    "优秀率", "良好率", "合格率", "不合格率", "名次"],
                   [11, 16, 9, 14, 8, 10, 9, 9, 9, 9, 9, 10, 8],
                   note="排名依据：总分排名按**总分平均**降序；各学科班级排名按该科**得分率**降序"
                        "（各科满分不同，得分率才可横向比）。四率为互斥档：优秀 ≥85%｜良好 70–85%｜"
                        "合格 60–70%｜不合格 <60%。")
        for r in go.get("by_total") or []:
            sh.add(["班级·总分", "总分排名", "总分", r["cls"], r["n"], num(r["mean_total"]),
                    r["full_total"], pct(r["rate"]), "", "", "", "", r["rank"]],
                   fills={13: FILL["优秀"] if r["rank"] == 1 else None})
        for s in subs:
            for r in go.get("by_subject", {}).get(s) or []:
                sh.add(["班级·学科", "%s班级排名" % s, s, r["cls"], r.get("n"), num(r.get("mean")),
                        R[s]["full"], pct(r.get("score_rate")), "", "", "", "", r["rank"]])
        gs = go.get("grade_stats") or {}
        for s in subs:
            g = gs.get(s) or {}
            if not g.get("count"):
                continue
            sh.add(["全年级·学科", "全年级四率", s, "全部样本", g["count"], num(g.get("mean")),
                    g["full"], pct(g.get("score_rate")), pct(g.get("excellent_rate")),
                    pct(g.get("good_rate")), pct(g.get("qualified_rate")), pct(g.get("fail_rate")), ""])

    # ------------------------------------------------- 10 历次成绩对比
    hs = an.get("history_summary") or {}
    if hs:
        sh = Sheet(wb, "10 历次成绩对比",
                   "历次成绩对比（年级 / 班级 · 总分与各学科 · 四率）",
                   ["层级", "班级", "考试", "科目", "人数", "平均分", "得分率",
                    "优秀率", "良好率", "合格率", "不合格率"],
                   [12, 14, 16, 10, 8, 10, 9, 9, 9, 9, 10],
                   note="四率为互斥档：优秀 ≥85%｜良好 70–85%｜合格 60–70%｜不合格 <60%。"
                        + ("" if hs.get("has_subject_detail")
                           else "本次历次表**只提供了总分**，故只有总分维度的对比；"
                                "补上学科列（如 语文/数学…）或改用「学号/考试/学科/分数」长表即可给出各科。"))
        for r in (hs.get("grade") or {}).get("total") or []:
            sh.add(["年级", "全部样本", r["exam"], "总分", r["n"], num(r["mean"]),
                    pct(r["score_rate"]), "", "", "", ""])
        for s in subs:
            for r in ((hs.get("grade") or {}).get("subjects") or {}).get(s, []):
                sh.add(["年级", "全部样本", r["exam"], s, r["n"], num(r["mean"]),
                        pct(r["score_rate"]), pct(r["excellent_rate"]), pct(r["good_rate"]),
                        pct(r["qualified_rate"]), pct(r["fail_rate"])])
        for c in sorted(hs.get("by_class") or {}):
            blk = hs["by_class"][c]
            for r in blk.get("total") or []:
                sh.add(["班级", c, r["exam"], "总分", r["n"], num(r["mean"]),
                        pct(r["score_rate"]), "", "", "", ""])
            for s in subs:
                for r in (blk.get("subjects") or {}).get(s, []):
                    sh.add(["班级", c, r["exam"], s, r["n"], num(r["mean"]),
                            pct(r["score_rate"]), pct(r["excellent_rate"]), pct(r["good_rate"]),
                            pct(r["qualified_rate"]), pct(r["fail_rate"])])

    if not out:
        out = "%s_%s_成绩分析结果册.xlsx" % (meta["exam_name"], scope_slug(subs))
    wb.save(out)
    if not quiet:
        print("[OK] Excel 结果册已生成：%s" % os.path.abspath(out))
        print("[OK] 工作表：%s" % "、".join(wb.sheetnames))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Excel 结果册生成器（输入 analysis.json）")
    ap.add_argument("--analysis", required=True, help="analysis.json 路径")
    ap.add_argument("--out", default=None, help="输出 xlsx 路径（默认按「考试名_学科范围_成绩分析结果册.xlsx」命名）")
    args = ap.parse_args(argv)
    try:
        build(args.analysis, args.out)
    except RuntimeError as exc:
        print("[错误] %s" % exc)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
