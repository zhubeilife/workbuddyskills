# -*- coding: utf-8 -*-
"""中小学考试成绩分析引擎。

用法示例::

    python exam_analysis.py --data 成绩.xlsx --subjects "数学,语文" \
        --exam-name "高二期中考试" --focus-class "高二(3)班" \
        --full "数学=150,语文=150" \
        --params params.json --out analysis.json

输入约定
--------
* 主表（默认第一个工作表）：「学号 / 姓名 / 班级 / <学科名>...」宽表，
  每个学科一列，存该生该科总分。**重复学号按同一人合并、保留最后一条**。
* 逐题表（可选，长表，默认工作表名 ``逐题``）：
  列 = 学号, 学科, 题号, 满分, 得分, 知识点(可选)
* 历次表（可选，长表，默认工作表名 ``历次``）：
  列 = 学号, 姓名(可选), 考试, 总分, 排名(可选), 序号/日期(建议)

满分的解析顺序（**猜错满分会让整份报告作废**）
-------------------------------------------
① ``params.json`` 的 ``subjects.<学科>.full`` → ② ``--full "语文=150,数学=100"`` →
③ 由该列成绩反推（唯一候选才采信，标记「待确认」）→ ④ 推断不出/多个候选 →
**停止并返回退出码 3，请用户给出**（除非显式 ``--full-policy default``）。

分制分布：**常规 100 分制**，其次 150 / 10 / 5 分制。同一学科（如语文、数学）100 与 150
都真实存在，所以「用户没说满分」时**只在能唯一反推时才动，能反推也标「待确认」，
反推不出就停下来问用户**——既不静默按学科名猜，也不拿「常规分制」硬套。

历次考试先后（同样会静默出错，必须标注）
-------------------------------------
① ``--history-order`` → ② 「序号」列 → ③ 「日期」列 → ④ 名称里的序号（第2次 / 第一次 / 二模）。
**都排不出（有名称既无序号也无日期）时只警告、不阻断**：打印 ``[警告]``、写进 ``data_notes``，
报告摘要 / 维度 6 与 Excel「07」显著标注，报告照常产出——顺序存疑只影响维度 6 的
趋势与进步榜，不该让其余 5 个维度也拿不到。按名称硬排会把「持续进步」判成「波动」、进步榜点错人，
而且不会报错，所以告警必须显著。历次表只有 1 次考试时退回横截面分层。

不编造数据
----------
* 逐题表没有「知识点」列（或整列为空）时 ``knowledge_points = []``，报告维度 4 与
  Excel「05」整块不生成，题目 ``kp`` 留空——**绝不兜底成「未标注」**（那是假教学结论）。
* 某科整列没有可解析分数（整列缺考/非数值）时该科退出分析，但**在 `data_notes` 里点名**，
  不再静默丢科。

输出：结构化 ``analysis.json``，供 report_builder.py 渲染成报告。
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import math
import os
import re
import statistics
import sys

# --------------------------------------------------------------------------- #
# 默认学科参数：满分；及格线/优秀线/低分线默认按 60% / 85% / 40% 派生
#
# ⚠️ 满分**绝不做静默兜底**：语文 100 分制、150 分制都真实存在，数学 100/120/150 也都有，
#    小学科还常见 10 分制、5 分制。满分猜错 → 及格率/优秀率/分数段/形态判定全部作废，
#    所以满分的解析顺序是：
#       ① params.json 的 subjects.<学科>.full   ② 命令行 --full 学科=满分
#       ③ 由本列成绩推断（唯一候选才采信，且标记「待确认」）
#       ④ 推断不出 / 推断不唯一 → **停下来请用户给出**（退出码 3）
#
# 分制分布（2026-10-08 用户给定）：**常规分制为 100 分**，其次 150 分、10 分、5 分；
#    其余（120/200/750…）较少见。FULL_COMMON 只用在两个**非判定**的地方：
#      ① --full-policy default 这一显式兜底所采用的默认值（= 常规 100 分制）
#      ② 把反推出的候选分制按「常见度」排序后展示给用户（100 排第一并标注「常规」）
#    它**不会**替用户决定任何一科的满分。
# --------------------------------------------------------------------------- #
FULL_COMMON = [100, 150, 10, 5]   # 按常见度降序；100 = 常规分制
DEFAULT_FULL_COMMON = 100         # 常规分制，仅 --full-policy default 时使用
DEFAULT_FULL = {
    # 汇总列（不参与学科自动识别，仅在显式把它当学科分析时兜底）
    "总成绩": 750, "总分": 750,
}
PASS_R, EXC_R, LOW_R = 0.60, 0.85, 0.40
# 四率（优秀 / 良好 / 合格 / 不合格）的**互斥分档**边界：
#   优秀 ≥ 优秀线（默认 85%）｜良好 70–85%｜合格 60–70%｜不合格 < 及格线（默认 60%）
# 四档相加 = 100%，可直接与「分数段分布」对照着看。GOOD_R 是「良好档」的下沿（默认 70%）。
# 注意：这与维度 1 里沿用的**累计统计**「及格率（≥60%）」不是一回事——及格率 ⊇ 良好+优秀。
GOOD_R = 0.70

# 常见满分（用于按成绩反推分制）。常规 100 分制；5 / 10 分制在小学与部分校本课程里很常见。
FULL_CANDIDATES = [5, 10, 15, 20, 30, 40, 50, 60, 70, 75, 80, 100, 120, 150, 200, 250, 300, 750]
# 观测最高分至少要达到满分的这个比例，才认为「这个满分」可信。
# 例：最高分 88 → 只有 100 分制入选（88 ≥ 85），120/150 分制被排除 → 可直接采用；
#     最高分 68 → 70/75/80 分制都说得通 → 判为「无法判断」，停下来请用户给出。
FULL_INFER_RATIO = 0.85
NEED_INPUT_EXIT = 3

BAND_DEFS = [
    ("不及格(<60%)", 0.0, 0.60),
    ("60–70%", 0.60, 0.70),
    ("70–80%", 0.70, 0.80),
    ("80–90%", 0.80, 0.90),
    ("优秀(≥90%)", 0.90, 10.0),
]

Q_LEVELS = [("共性错题", 0.0, 0.60), ("薄弱题", 0.60, 0.75), ("达标题", 0.75, 0.85), ("优势题", 0.85, 10.0)]
KP_LEVELS = [("危险", 0.0, 0.60), ("薄弱", 0.60, 0.75), ("良好", 0.75, 0.85), ("优秀", 0.85, 10.0)]

NULL_TOKENS = {"", "-", "—", "–", "/", "\\", "缺考", "缺", "n/a", "na", "nan", "none", "null", "."}

# 「知识点」列里的**占位符**：填了东西，但不是真知识点。
# 不认出来的后果很具体——会造出名字叫「-」的假知识点，并让 Excel「05 知识点优先级」
# 在这种「其实没有知识点数据」的表上凭空出现（用户要求 2026-10-11：没有知识点数据就不该有这张表）。
KP_BLANK = {"无", "暂无", "无知识点", "未标注", "未填写", "未填", "待定", "待填", "未知",
            "空", "略", "没有", "?", "？", "／", "＼", "…", "..."}

# 学科别名：仅用于判断「是不是同一门课」，**不改写输出**（输出仍用用户给的学科名）。
# 与姊妹 skill cnki-edu-student-semester-comment 的 subjects.py 保持同一份词表。
SUBJECT_ALIAS = {
    "道法": "道德与法治", "德法": "道德与法治", "思想品德": "道德与法治",
    "思品": "道德与法治", "政治": "思想政治", "政治生活": "思想政治",
    "历史与社会": "历史与社会", "地理与社会": "历史与社会",
}

# 表头探测用：命中这些词的列名基本可以确定是真表头（而不是「初一(3)班期中考试成绩表」这类合并大标题）。
STRONG_HEADER_TOKENS = ("学号", "考号", "学籍号", "座号", "姓名", "名字",
                        "班级", "班别", "行政班", "学科", "科目", "题号")
WEAK_HEADER_TOKENS = ("序号", "满分", "得分", "分数", "成绩", "总分", "排名", "名次", "学生")

# 常见学科名（归一后）。用于识别「表头明显是一门课、却整列没有分数」的情况——
# 这种列过去被静默丢弃（整列「缺考」时连学科都不进分析范围），老师无从发现少算了一科。
KNOWN_SUBJECTS = {
    "语文", "数学", "英语", "物理", "化学", "生物", "政治", "历史", "地理",
    "道德与法治", "思想政治", "科学", "信息技术", "信息科技", "体育", "音乐", "美术",
    "思想品德", "历史与社会", "物理与化学", "综合",
}


def norm_subject(name) -> str:
    s = str(name).strip()
    return SUBJECT_ALIAS.get(s, s)


def match_subject_col(headers, subject):
    """学科列匹配：先精确 → 再别名等价 → 最后子串包含。"""
    raw = str(subject).strip()
    for h in headers:
        if str(h).strip() == raw:
            return h
    tgt = norm_subject(raw)
    for h in headers:
        if norm_subject(h) == tgt:
            return h
    if raw:
        for h in headers:
            if raw in str(h):
                return h
    return None


def header_row_score(row) -> int:
    """给一行打分：表头关键词越多分越高。强关键词权重 2，弱关键词权重 1。"""
    cells = [str(c).strip() for c in row if str(c).strip()]
    strong = sum(1 for c in cells if any(t in c for t in STRONG_HEADER_TOKENS))
    weak = sum(1 for c in cells if any(t in c for t in WEAK_HEADER_TOKENS))
    return 2 * strong + weak


def find_header_row(data, max_scan=8):
    """在前若干行里找真表头行下标：跳过「合并大标题行」等前置行。

    只在第一行得分不足（不像表头）时才向后找，避免把正常数据表误判成有前置标题。
    """
    if not data:
        return 0
    if header_row_score(data[0]) >= 2:
        return 0
    best, best_score = 0, header_row_score(data[0])
    for i, row in enumerate(data[1:max_scan], 1):
        sc = header_row_score(row)
        if sc > best_score:
            best, best_score = i, sc
    return best if best_score >= 2 else 0


# --------------------------------------------------------------------------- #
# 满分解析（用户指定 > 数据推断 > 停下来问用户）
# --------------------------------------------------------------------------- #
def parse_full_arg(text):
    """解析 ``--full "语文=150,数学=100,物理=10"`` → ``{"语文": 150.0, ...}``。"""
    out = {}
    if not text:
        return out
    for chunk in str(text).replace("、", ",").replace("，", ",").replace(";", ",").replace("；", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        for sep in ("=", ":", "："):
            if sep in chunk:
                k, v = chunk.split(sep, 1)
                k, v = k.strip(), to_num(v)
                if k and v:
                    out[k] = float(v)
                break
        else:
            raise SystemExit("--full 格式应为「学科=满分」，逗号分隔，例如 --full \"语文=150,物理=100\"；"
                             "收到「%s」。" % chunk)
    return out


def lookup_by_subject(mapping, subject):
    """在 dict 里按学科名取值：先精确，再走学科别名（道法 ↔ 道德与法治）。"""
    if not mapping:
        return None
    if subject in mapping:
        return mapping[subject]
    tgt = norm_subject(subject)
    for k, v in mapping.items():
        if norm_subject(k) == tgt:
            return v
    return None


def infer_full(values):
    """按本列成绩反推满分。

    返回 ``(candidates, basis)``：``candidates`` 为可能的分制列表（升序），
    ``basis`` 为给用户看的一句话依据。空列表表示「推断不出」。

    注意：这里**先滤掉不可能的成绩**（负数、超过最大候选 750 的脏值），
    否则一个 999 的异常值就会把最高分抬到无法反推的程度。
    """
    lim = FULL_CANDIDATES[-1]
    nums = [v for v in values if isinstance(v, (int, float)) and 0 <= v <= lim]
    if not nums:
        return [], "该列没有可用的数值"
    mx = max(nums)
    cands = [c for c in FULL_CANDIDATES if mx <= c + 1e-9 and mx >= FULL_INFER_RATIO * c - 1e-9]
    basis = "本列最高分 %g" % rnd(mx)
    return cands, basis


def sort_full_candidates(cands):
    """把候选分制按「常见度」排序：100（常规）→ 150 → 10 → 5 → 其余（升序）。

    只影响**展示顺序**（给用户看的待确认清单 / 报告说明），不参与任何判定——
    判定仍然是「唯一候选才采信，否则停下来问用户」。
    """
    def key(c):
        try:
            return (0, FULL_COMMON.index(c))
        except ValueError:
            return (1, c)
    return sorted(cands, key=key)


def full_candidates_text(cands, sep="、"):
    """候选分制的中文罗列，常规 100 分制加标注（便于用户一眼看到最可能的那项）。"""
    return sep.join("%g 分制%s" % (c, "（常规）" if c in FULL_COMMON and c == 100 else "")
                    for c in sort_full_candidates(cands))


def full_confirm_note(subject, full, source, basis, candidates):
    """把「满分未经用户确认」写成一句中文说明（进 data_notes 与报告）。"""
    if source == "inferred":
        return ("「%s」未指定满分，已按成绩分布推断为 %g 分（依据：%s；数据支持的候选：%s）。"
                "**请核对**，如与实际不符，用 --full \"%s=<满分>\" 或 params.json 指定后重跑。"
                % (subject, full, basis, full_candidates_text(candidates) or "-", subject))
    return ("「%s」未指定满分，按**常规 100 分制**（内置默认，未做数据校验）计为 %g 分。**请核对**："
            "语文/数学常见 150 分制、英语常见 120 分制、小学科常见 10/5 分制；"
            "如与实际不符，用 --full \"%s=<满分>\" 或 params.json 指定后重跑。"
            % (subject, full, subject))


def unresolved_full_message(pending):
    """满分无法确定时给用户的提示（含「怎么补」的具体命令）。"""
    lines = ["", "[需确认] 以下学科的满分无法确定，为避免整份报告建立在错误的满分上，已停止分析："]
    for p in pending:
        if p["candidates"]:
            lines.append("  · %s：%s，数据支持 %s——请确认实际满分是多少"
                         % (p["subject"], p["basis"], full_candidates_text(p["candidates"])))
        else:
            lines.append("  · %s：%s，无法反推满分——请确认实际满分是多少" % (p["subject"], p["basis"]))
    lines.append("")
    lines.append("  常见满分：100 分（常规，多数校内考试）、150 分、10 分、5 分；120/200/750 等较少见。"
                 "请以卷面实际满分为准。")
    lines.append("")
    lines.append("  请用以下任一方式指定后重跑（前者最快）：")
    lines.append("    --full \"%s\"" % ",".join("%s=<满分>" % p["subject"] for p in pending))
    lines.append("    或在 params.json 里写 {\"subjects\": {\"%s\": {\"full\": <满分>}}}" % pending[0]["subject"])
    lines.append("  若用户明确表示「不用问，没给的就按常规分制（100 分）」——"
                 "可加 --full-policy default 跳过本次确认（仍会登记为待确认）。")
    lines.append("")
    return "\n".join(lines)


def unreliable_history_warning(names):
    """历次考试先后**无法判定**时的告警文案（**只警告，不阻断**）。

    顺序排不出时报告照常产出，但趋势判定 / 进步榜 / 需关注名单可能整体反向，
    所以必须把这条告警同时送进 stderr 与 ``data_notes``（``analysis.json`` + 对话交付说明，
    报告与 Excel 结果册都不承载数据说明），并在报告维度 6 上显著标注。
    """
    lines = ["", "[警告] 历次成绩表的「考试」列无法判断先后顺序 —— 已按名称自然序估算，"
             "趋势判定与进步榜**可能反向**："]
    lines.append("  · 考试名称：%s" % "、".join(str(n) for n in names))
    lines.append("  · 部分名称既不含数字也没有「序号」/「日期」列（如「期中考试」「期末考试」），"
                 "引擎无从知道哪个在前。")
    lines.append("")
    lines.append("  建议用以下任一方式明确顺序后重跑（成本很低）：")
    lines.append("    --history-order \"%s\"" % ",".join(str(n) for n in names))
    lines.append("    或在历次表里加一列「序号」（1、2、3…）或「日期」，引擎会自动按它排序。")
    lines.append("  如本次不打算用趋势结论，可忽略本告警，维度 6 的表格仍可作原始记录参考。")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 表格读取
# --------------------------------------------------------------------------- #
def load_table(path: str, sheet: str | None = None, notes=None):
    """返回 (headers, rows)；rows 为 dict 列表。支持 .xlsx/.xlsm/.csv/.txt。

    ``notes`` 可选：传入列表时，会自动跳过前置标题行、跳过非首选工作表等
    情况写成中文说明，归入 `data_notes`（交付时在对话里复述；报告与 Excel 结果册都不展示）。
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".txt", ".tsv"):
        delim = "\t" if ext == ".tsv" else None
        for enc in ("utf-8-sig", "utf-8", "gbk", "gb18030"):
            try:
                with open(path, "r", encoding=enc, newline="") as fh:
                    if delim:
                        reader = csv.reader(fh, delimiter=delim)
                    else:
                        sample = fh.read(4096)
                        fh.seek(0)
                        try:
                            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
                        except Exception:
                            dialect = csv.excel
                        reader = csv.reader(fh, dialect)
                    data = [r for r in reader]
                break
            except UnicodeDecodeError:
                continue
        else:
            raise RuntimeError("无法识别 CSV 编码：%s" % path)
        data = [[c.strip() for c in row] for row in data if any(str(c).strip() for c in row)]
    else:
        try:
            from openpyxl import load_workbook
        except ImportError:  # pragma: no cover
            raise RuntimeError("读取 Excel 需要 openpyxl，请先安装：pip install openpyxl")
        wb = load_workbook(path, data_only=True, read_only=True)
        if sheet and sheet in wb.sheetnames:
            ws = wb[sheet]
        else:
            if sheet and notes is not None:
                notes.append("指定的工作表「%s」不存在，已改用第一个工作表「%s」；本文件包含：%s"
                             % (sheet, wb.sheetnames[0], "、".join(wb.sheetnames)))
            ws = wb[wb.sheetnames[0]]
        data = []
        for row in ws.iter_rows(values_only=True):
            vals = ["" if v is None else v for v in row]
            if any(str(v).strip() for v in vals):
                data.append([str(v).strip() if not isinstance(v, (int, float)) else v for v in vals])
        wb.close()

    if not data:
        return [], []
    hidx = find_header_row(data)
    if hidx and notes is not None:
        notes.append("检测到主表前 %d 行为表外标题行，已自动跳过，以第 %d 行作为表头。"
                     % (hidx, hidx + 1))
    headers = [str(h).strip() for h in data[hidx]]
    rows = []
    for raw in data[hidx + 1:]:
        if not any(str(c).strip() for c in raw):
            continue
        rec = {}
        for i, h in enumerate(headers):
            if not h:
                continue
            rec[h] = raw[i] if i < len(raw) else ""
        rows.append(rec)
    return headers, rows


def sheet_names(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".txt", ".tsv"):
        return []
    try:
        from openpyxl import load_workbook
    except ImportError:  # pragma: no cover
        return []
    wb = load_workbook(path, data_only=True, read_only=True)
    names = list(wb.sheetnames)
    wb.close()
    return names


def pick_sheet(path, wanted, exclude=()):
    """在 workbook 中模糊匹配工作表名（如 逐题 / 逐题得分 / 逐题分析）。"""
    for name in sheet_names(path):
        if name in exclude:
            continue
        for key in wanted:
            if key in name:
                return name
    return None


def to_num(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s.lower() in NULL_TOKENS:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def is_missing(v) -> bool:
    if v is None:
        return True
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return False
    return str(v).strip().lower() in NULL_TOKENS


def norm_kp(v) -> str:
    """「知识点」单元格归一：空值 / NULL_TOKENS / KP_BLANK 占位符 → 空串（= 这道题没有归属）。

    唯一的入口在这里。上游归一过一次，下游（build_kp、报告维度 4、Excel 04/05）
    就不必各自判断——所以**不要再在别处写第二份占位符词表**。
    """
    s = "" if v is None else str(v).strip()
    if not s or s.lower() in NULL_TOKENS or s in KP_BLANK:
        return ""
    return s


def pick_col(headers, candidates):
    """按候选名找列。候选里的 None/空串会被忽略——否则 --id-col 等可选参数
    默认值 None 会让 `None in h` 直接抛 TypeError。"""
    cands = [c for c in candidates if c not in (None, "")]
    for cand in cands:
        for h in headers:
            if h == cand:
                return h
    for cand in cands:
        for h in headers:
            if cand in h:
                return h
    return None


# --------------------------------------------------------------------------- #
# 统计工具
# --------------------------------------------------------------------------- #
def pop_std(vals):
    if len(vals) < 2:
        return 0.0
    m = sum(vals) / len(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / len(vals))


def rnd(x, nd=2):
    if x is None:
        return None
    return round(float(x) + 0.0, nd)


def ratio(num, den):
    return (num / den) if den else 0.0


def classify(value, table):
    for label, lo, hi in table:
        if lo <= value < hi:
            return label
    return table[-1][0]


def basic_stats(vals, full, smeta=None):
    """基础统计量。及格/优秀/低分线优先取 smeta 中的自定义设定，否则按满分比例派生。

    四率（互斥分档，相加 100%）：优秀 ≥ 优秀线｜良好 ≥ 良好线且 < 优秀线｜
    合格 ≥ 及格线且 < 良好线｜不合格 < 及格线。
    另有沿用的**累计统计** ``pass_rate``（及格率 = ≥ 及格线人数 ÷ 有效人数）——
    它与四率并存：及格率 ⊇ 良好率 + 优秀率 + 合格率，两者不要混着讲。
    """
    n = len(vals)
    if n == 0:
        return {"count": 0}
    smeta = smeta or {}
    pass_line = smeta.get("pass") or full * PASS_R
    exc_line = smeta.get("excellent") or full * EXC_R
    low_line = smeta.get("low") or full * LOW_R
    # 良好线：取「满分×70%」与及格线的较大者，保证四档不重叠、漏算
    good_line = smeta.get("good") or max(full * GOOD_R, pass_line)
    mean = sum(vals) / n
    return {
        "count": n,
        "mean": rnd(mean),
        "max": rnd(max(vals)),
        "min": rnd(min(vals)),
        "median": rnd(statistics.median(sorted(vals))),
        "range": rnd(max(vals) - min(vals)),
        "std": rnd(pop_std(vals)),
        "pass_rate": rnd(ratio(sum(1 for v in vals if v >= pass_line), n), 4),
        "excellent_rate": rnd(ratio(sum(1 for v in vals if v >= exc_line), n), 4),
        "good_rate": rnd(ratio(sum(1 for v in vals if good_line <= v < exc_line), n), 4),
        "qualified_rate": rnd(ratio(sum(1 for v in vals if pass_line <= v < good_line), n), 4),
        "fail_rate": rnd(ratio(sum(1 for v in vals if v < pass_line), n), 4),
        "low_rate": rnd(ratio(sum(1 for v in vals if v < low_line), n), 4),
        "score_rate": rnd(ratio(mean, full), 4),
        "lines": {"pass": rnd(pass_line), "good": rnd(good_line),
                  "excellent": rnd(exc_line), "low": rnd(low_line)},
    }


def band_table(vals, full):
    n = len(vals) or 1
    out, cum, cd = [], 0, 0.0
    for label, lo, hi in BAND_DEFS:
        c = sum(1 for v in vals if lo * full <= v < hi * full)
        cum += c
        cd += c / n
        out.append({"label": label, "count": c, "ratio": rnd(c / n, 4), "cum": rnd(cd, 4),
                    "lo": lo, "hi": hi})
    return out


def detect_shape(vals, full):
    """判定成绩形态：正态集中 / 高分偏态 / 尾部沉重 / 两极分化。"""
    if not vals:
        return {"type": "数据不足", "evidence": "无有效成绩"}
    n = len(vals)
    mean_r = (sum(vals) / n) / full
    exc = sum(1 for v in vals if v >= full * 0.90) / n
    good = sum(1 for v in vals if full * 0.80 <= v < full * 0.90) / n
    fail = sum(1 for v in vals if v < full * 0.60) / n
    lowmid = sum(1 for v in vals if full * 0.60 <= v < full * 0.70) / n
    mid = sum(1 for v in vals if full * 0.70 <= v < full * 0.80) / n

    ev = ("优秀≥90%%占比 %.1f%%、不及格占比 %.1f%%、均分得分率 %.1f%%"
          % (exc * 100, fail * 100, mean_r * 100))
    if exc >= 0.20 and fail >= 0.20:
        return {"type": "两极分化", "evidence": "两端同时堆积（%s），标准差偏大，教学需分层施策" % ev}
    if fail >= 0.30 or (fail + lowmid >= 0.50 and mean_r < 0.70):
        return {"type": "尾部沉重", "evidence": "低分段人数偏多（%s），需优先做基础补差" % ev}
    if exc + good >= 0.55 or mean_r >= 0.80:
        return {"type": "高分偏态", "evidence": "中高分段集中（%s），整体掌握较好，宜做拔高训练" % ev}
    seg = {"不及格(<60%)": fail, "60–70%": lowmid, "70–80%": mid, "80–90%": good, "优秀(≥90%)": exc}
    top = max(seg, key=lambda k: seg[k])
    return {"type": "正态集中", "evidence": "%s 段占比最高（%.1f%%），分布接近钟形（%s），适合整体推进"
            % (top, seg[top] * 100, ev)}


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def run(args):
    notes = []
    # ---------------- 参数 ----------------
    params = {}
    if args.params and os.path.exists(args.params):
        with open(args.params, "r", encoding="utf-8") as fh:
            params = json.load(fh)
    elif args.params:
        notes.append("指定的参数文件不存在：%s，已按默认参数执行。" % args.params)

    exam_name = args.exam_name or params.get("exam_name") or "考试成绩"
    focus_class = args.focus_class or params.get("class_name")
    teacher = params.get("teacher", "")
    exam_date = params.get("date", "")

    explicit_focus = bool(args.focus_class or params.get("class_name"))

    headers, rows = load_table(args.data, args.sheet, notes)
    used_sheet = args.sheet or (sheet_names(args.data) or [None])[0]
    if not rows and not args.sheet:
        # 第一个工作表可能只是封面/填写说明：依次尝试其余工作表，取第一个有数据行的。
        candidates = sheet_names(args.data)
        for name in candidates[1:]:
            h2, r2 = load_table(args.data, name, None)
            if r2:
                headers, rows, used_sheet = h2, r2, name
                notes.append("第一个工作表不是成绩表，已自动改用「%s」作为主表。" % name)
                break
    if not rows:
        names = sheet_names(args.data)
        raise SystemExit("主表没有读到数据行，请检查 --data / --sheet。"
                         + ("本文件包含工作表：%s（可用 --sheet 指定，或先跑 --list-sheets 查看）"
                            % "、".join(names) if names else ""))

    id_col = pick_col(headers, [args.id_col, "学号", "考号", "学籍号", "id"])
    name_col = pick_col(headers, [args.name_col, "姓名", "名字", "学生", "name"])
    class_col = pick_col(headers, [args.class_col, "班级", "班别", "行政班", "class"])

    reserved = {c for c in (id_col, name_col, class_col) if c}
    skip_words = ("总分", "总成绩", "排名", "名次", "年级", "学号", "姓名", "班级", "备注", "序号",
                  "考号", "学籍号", "座号")

    # 「看起来是学科列」的列（有数值）——用于判断本次是不是只分析了其中一部分学科，
    # 进而决定 Excel 里该写「全科总分」还是「所选学科总分」。
    detected = []
    for h in headers:
        if not h or h in reserved or any(w in h for w in skip_words):
            continue
        if any(to_num(r.get(h)) is not None for r in rows):
            detected.append(h)
    # 表头明显是一门课、整列却一个分数都没有（如整列写「缺考」）——过去会被静默丢弃
    empty_known = [h for h in headers
                   if h and h not in reserved and not any(w in h for w in skip_words)
                   and h not in detected and norm_subject(h) in KNOWN_SUBJECTS]

    if args.subjects and args.subjects.strip() not in ("", "所有", "全部", "all"):
        subjects = [x.strip() for x in args.subjects.replace("、", ",").replace("，", ",").split(",") if x.strip()]
    else:
        subjects = list(detected)
        notes.append("未显式指定学科范围，已自动识别为：%s" % "、".join(subjects))
        if empty_known:
            notes.append("主表里的「%s」列没有任何可解析的分数（整列缺考/空值/非数值），"
                         "已**不纳入**本次分析——请确认该科是否确实没有成绩，或原表是否需要修正。"
                         % "、".join(empty_known))

    if not subjects:
        raise SystemExit("未识别到任何学科列，请用 --subjects 指定；当前表头为：%s"
                         % "、".join(h for h in headers if h))

    subj_params = params.get("subjects", {}) or {}
    cli_full = parse_full_arg(getattr(args, "full", None))
    policy = str(getattr(args, "full_policy", None) or params.get("full_policy") or "ask").strip().lower()
    if policy not in ("ask", "default"):
        raise SystemExit("--full-policy 只支持 ask / default，收到「%s」。" % policy)

    meta, missing_cols, to_confirm, unresolved, empty_cols = {}, [], [], [], []
    for s in subjects:
        col = match_subject_col(headers, s)
        if col is None:
            missing_cols.append(s)
            continue
        p = lookup_by_subject(subj_params, s) or {}
        # 用户显式给过满分就不再猜：params.json 优先，其次 --full
        user_full = p.get("full") or lookup_by_subject(cli_full, s)
        col_vals = [v for v in (to_num(r.get(col)) for r in rows) if v is not None]
        if not col_vals:
            # 列在、但整列没有一个可用分数（整列缺考/空值/文本）→ 不再静默丢科，
            # 也不能反推满分（反推不出会误报成「满分无法确定」），单独登记并明确告知。
            empty_cols.append(s)
            continue
        cands, basis = infer_full(col_vals)

        if user_full:
            full, source = float(user_full), "user"
        elif len(cands) == 1:
            full, source = float(cands[0]), "inferred"
        elif policy == "default":
            # 显式兜底：用户明确表示「不用问」时，一律按常规 100 分制（汇总列 750）
            full, source = float(DEFAULT_FULL.get(s, DEFAULT_FULL_COMMON)), "default"
        else:
            # 推断不出、或推断出多个可能 → 不擅自决定，停下来请用户给出
            unresolved.append({"subject": s, "basis": basis, "candidates": cands})
            continue

        if source == "user":
            notes.append("「%s」满分 %g 分（用户指定），及格 %.0f / 良好 %.0f / 优秀 %.0f / 低分 %.0f。"
                         % (s, full, full * PASS_R, full * GOOD_R, full * EXC_R, full * LOW_R))
        else:
            to_confirm.append({"subject": s, "full": rnd(full), "source": source,
                               "basis": basis, "candidates": cands,
                               "candidates_text": "、".join("%g" % c for c in sort_full_candidates(cands))})
            notes.append(full_confirm_note(s, full, source, basis, cands))
            if full not in FULL_COMMON:
                notes.append("⚠️ 「%s」的满分 %g 分**不是常见分制**（常见：100（常规）/ 150 / 10 / 5），"
                             "请重点复核；若实际是 100 分制，用 --full \"%s=100\" 重跑即可。"
                             % (s, full, s))
        meta[s] = {
            "column": col,
            "full": full,
            "pass": float(p.get("pass") or full * PASS_R),
            "good": float(p.get("good") or full * GOOD_R),
            "excellent": float(p.get("excellent") or full * EXC_R),
            "low": float(p.get("low") or full * LOW_R),
            "full_source": source,
            "default_full": source in ("inferred", "default"),
        }
    if unresolved:
        sys.stderr.write(unresolved_full_message(unresolved))
        raise SystemExit(NEED_INPUT_EXIT)
    for s in missing_cols:
        notes.append("主表中找不到学科列「%s」，已跳过该学科（可用 --subjects 指定实际列名）。" % s)
    for s in empty_cols:
        notes.append("主表「%s」列没有任何可解析的分数（整列缺考 / 空值 / 非数值），"
                     "已从本次分析中剔除——请确认该科数据是否确实为空。" % s)
    if empty_cols:
        sys.stderr.write("[提示] 以下学科列整列没有分数，已剔除：%s。请确认原表。\n"
                         % "、".join(empty_cols))
    subjects = [s for s in subjects if s in meta]
    if not subjects:
        if empty_cols:
            raise SystemExit("所有待分析学科列都是空的（%s）。请检查数据文件："
                             "这些列里没有任何可解析的分数。" % "、".join(empty_cols))
        raise SystemExit("所有学科列都缺失。当前表头为：%s"
                         % "、".join(h for h in headers if h))
    if to_confirm:
        notes.append("⚠️ 满分确认提醒：%s 共 %d 个学科的满分不是由用户指定，而是推断/默认得到的。"
                     "满分直接决定及格率、优秀率、分数段与形态判定，**交付前请与用户核对一遍**。"
                     % ("、".join(x["subject"] for x in to_confirm), len(to_confirm)))

    # ---------------- 班级分组 ----------------
    # 重复学号按「同一人」合并，**保留最后一条记录**（用户 2026-10-08 要求）。
    # 过去同一学号出现两行会被当成两个学生：人数虚高、均分失真、排名表里同一人出现两次。
    student_rows, _seen_sid, dup_rows = [], {}, []
    for i, r in enumerate(rows):
        raw_sid = str(r.get(id_col, "")).strip() if id_col else ""
        sid = raw_sid or ("#%d" % (i + 1))
        rec = {
            "sid": sid,
            # 学号缺失时用 #N 兜底（内部仍需一人一个键），但**这列假学号不对外显示**——
            # 用户要求 2026-10-11：数据里没有真学号，报告与结果册就不出「学号」列。
            # 判定结果汇总为 meta.has_student_id。
            "sid_auto": not raw_sid,
            "name": str(r.get(name_col, "")).strip() if name_col else "",
            "cls": str(r.get(class_col, "")).strip() if class_col else (focus_class or "本班"),
            "raw": r,
        }
        if id_col and sid in _seen_sid:
            prev = student_rows[_seen_sid[sid]]
            dup_rows.append({"sid": sid, "kept": rec["name"], "dropped": prev["name"]})
            student_rows[_seen_sid[sid]] = rec     # 取最后一条
        else:
            _seen_sid[sid] = len(student_rows)
            student_rows.append(rec)
    if dup_rows:
        notes.append("主表有 %d 个重复学号，已按同一人合并、**保留最后一条记录**：%s%s。"
                     "如这不是期望行为，请修正原表后重跑。"
                     % (len(dup_rows),
                        "、".join("%s（%s）" % (d["sid"], d["kept"] or "姓名空")
                                  for d in dup_rows[:8]),
                        "…" if len(dup_rows) > 8 else ""))

    classes = sorted({s["cls"] for s in student_rows if s["cls"]})
    if not class_col:
        notes.append("主表无「班级」列，全部样本按同一群体处理（维度 5 的平行班对比不可用）。")
    focus_class_requested = focus_class
    if not focus_class:
        focus_class = classes[0] if classes else "本班"
        if classes:
            notes.append("未指定重点班级，已默认以「%s」为主分析对象（维度 1/2/5）。" % focus_class)
    if focus_class not in classes and classes:
        # 指定的班级不存在 → 统计上回退为全部学生，**标签也必须跟着改**，
        # 否则封面会写一个并不存在的班级名，与「全部样本」的范围互相矛盾。
        notes.append("指定的班级「%s」在主表中不存在（现有班级：%s），"
                     "维度 1/2/5 已改为分析全部 %d 名学生。"
                     % (focus_class, "、".join(classes), len(student_rows)))
        focus_class = "全部样本"
        explicit_focus = False

    # 维度 3/4/6 的统计范围：显式指定班级时收敛到该班，否则维持全部样本。
    # （此前维度 1/2/5 用本班、维度 3/4/6 用全年级，同一份报告里两套范围且标签写成「班内」。）
    # 单班样本（班级列缺失、或班级列只有一个取值）本身就是「本班」，收敛与不收敛等价，
    # 但**标签必须写成班级名**——否则老师会看到封面写「初一3班」、排名表却写「样本（含各班）」。
    # 班级层 = 主分析班级（未显式指定时 engine 已默认取第一个班，并给出提示）；
    # 单班样本时班级层与年级层相同，报告只呈现一套、不摆两份一样的数字。
    # 维度 3 从此**两层并列**（班级层 + 年级层，用户要求 2026-10-10），
    # 维度 4/6 与维度 1/2/5 一致收敛到同一个班（此前 4/6 用全年级、1/2/5 用本班，两套范围）。
    multi_class = len(classes) > 1
    scope_class = focus_class if focus_class in classes else None
    scope_sids = ({st["sid"] for st in student_rows if st["cls"] == scope_class}
                  if scope_class else None)
    if scope_class and multi_class:
        notes.append("统计范围说明：维度 1/2/5 与 4/6 用「%s」（%d 人）；维度 3 · 逐题得分率按"
                     "**班级层「%s」+ 年级层「全部样本」**两层并列统计，两层数字并排呈现。"
                     % (focus_class, len(scope_sids), scope_class))
    elif scope_class:
        notes.append("单班样本：「%s」即全部样本，逐题统计的班级层与年级层相同（%d 人）。"
                     % (scope_class, len(scope_sids)))
    else:
        notes.append("主表没有可用的班级划分，逐题统计只有一层（全部 %d 人）。" % len(student_rows))

    # ---------------- 逐题 / 历次 ----------------
    q_sheet = (args.questions_sheet or pick_sheet(args.data, ["逐题"], exclude=(used_sheet,))) if args.data else None
    h_sheet = (args.history_sheet or pick_sheet(args.data, ["历次", "历次成绩", "历史"],
                                                exclude=(used_sheet,))) if args.data else None
    history_order = ([x.strip() for x in args.history_order.replace("、", ",").replace("，", ",").split(",")
                      if x.strip()] if args.history_order else params.get("history_order") or None)
    questions, q_has_kp, history, hinfo = {}, False, {}, {}
    if q_sheet:
        try:
            qh, qr = load_table(args.data, q_sheet, notes)
            questions, q_has_kp = parse_questions(qh, qr, subjects, notes)
        except Exception as exc:
            notes.append("读取逐题表（%s）失败：%s" % (q_sheet, exc))
    # 逐题表是否带「学号」——决定能不能按班级分层、能不能定位到每个学生
    q_has_sid = any(sid for sub in (questions or {}).values()
                    for d in sub.values() for sid in (d.get("sids") or []))
    # 两层是否**真的不同源**：单班样本时班级层就是全体，两层数字一模一样，只呈现一套。
    two_level_q = bool(scope_sids is not None and q_has_sid
                       and len(scope_sids) < len(student_rows))
    if questions and scope_sids is not None:
        if not q_has_sid:
            notes.append("逐题表没有「学号」列：无法按班级分层，逐题的班级层与年级层相同（均为全部样本），"
                         "各班逐题对比也不生成。给逐题表补一列「学号」即可全部启用。")
        elif two_level_q:
            notes.append("逐题得分率按班级层「%s」+ 年级层「全部样本」两层并列统计，"
                         "并逐班给出每道小题的得分率。" % scope_class)
        else:
            notes.append("逐题得分率为「%s」全体 %d 人（单班样本，班级层与年级层是同一批人，只呈现一套）。"
                         % (scope_class, len(scope_sids)))
    if not questions:
        notes.append("未提供逐题得分数据：报告的「维度 3 · 逐题得分率」"
                     "与结果册的「04 逐题得分率」**本次不生成**（不做空板块占位）。"
                     "如需启用，请补一份长表：学号/学科/题号/满分/得分/知识点（工作表名可含「逐题」）。")
    if h_sheet:
        try:
            hh, hr = load_table(args.data, h_sheet, notes)
            history, hinfo = parse_history(hh, hr, subjects, notes, order=history_order)
        except Exception as exc:
            notes.append("读取历次成绩表（%s）失败：%s" % (h_sheet, exc))
            history, hinfo = {}, {}
    if history and not hinfo.get("has_subject_detail"):
        notes.append("历次成绩表只有「总分」（没有各学科列），历次对比只到总分维度；"
                     "若要历次各学科的四率与班级对比，请在历次表里补上学科列"
                     "（如 语文 / 数学…），或用「学号 / 考试 / 学科 / 分数」的长表形态。")
    # 历次只有 1 次考试 → 谈不上趋势，直接退回横截面分层（章节标题也跟着改）
    if history:
        max_pts = max((len(rec.get("points") or []) for rec in history.values()), default=0)
        if max_pts <= 1:
            notes.append("历次成绩表只包含 1 次考试（%s），无法做趋势 / 进退步追踪，"
                         "「个体追踪」已改用横截面分层。如需趋势分析，请补充至少 2 次考试的记录。"
                         % "、".join(str(n) for n in (hinfo.get("names") or ["-"])))
            history, hinfo = {}, {}
    # 考试先后无法判定 → **只警告不阻断**：报告照常产出（其余 5 个维度仍然有效），
    # 但告警同时进 stderr、data_notes 与报告维度 6 —— 趋势与进步榜可能整体反向。
    if hinfo.get("source") == "unknown":
        sys.stderr.write(unreliable_history_warning(hinfo.get("names") or []))
    if not history:
        notes.append("未提供历次成绩，「个体追踪」将改用横截面分层（尖子生 / 临界优秀 / 临界及格 / 学困生）。")
    elif hinfo.get("source") == "natural" and history_order is None:
        notes.append("历次成绩的先后顺序是按「考试」名称里的序号自动排的（第2次 < 第10次）。"
                     "若与实际先后不符，请用 --history-order \"第1次月考,期中考试,第2次月考,期末考试\" 显式指定。")

    # ---------------- 分学科分析 ----------------
    results = {}
    excluded_all = {}
    # 学号 → 班级：逐题表按人给出各班每题得分率时要用（历次表也复用同一张映射）
    sid2cls = {st["sid"]: st["cls"] for st in student_rows}
    # 学号 → 各科有效分数（**全体学生**）：年级层的班级排名要用（不能用已收敛到本班的 ranking）
    score_map = {}
    for s in subjects:
        col = meta[s]["column"]
        full = meta[s]["full"]

        valid, blank, abnormal, excluded = [], 0, [], []
        for st in student_rows:
            raw = st["raw"].get(col)
            v = to_num(raw)
            if v is None:
                if is_missing(raw):
                    blank += 1
                    excluded.append({"sid": st["sid"], "name": st["name"] or st["sid"], "cls": st["cls"],
                                     "raw": "" if raw is None else str(raw).strip(), "reason": "缺考/空值"})
                else:
                    abnormal.append(str(raw))
                    excluded.append({"sid": st["sid"], "name": st["name"] or st["sid"], "cls": st["cls"],
                                     "raw": str(raw).strip(), "reason": "非数值"})
                continue
            if v < -0.001 or v > full + 0.001:
                abnormal.append("%s（%.2f）" % (st["name"] or st["sid"], v))
                excluded.append({"sid": st["sid"], "name": st["name"] or st["sid"], "cls": st["cls"],
                                 "raw": rnd(v), "reason": "超出 0~%g" % full})
                continue
            valid.append((st, v))
        if blank:
            notes.append("「%s」有 %d 条空值/缺考记录，统计时按缺失剔除（未计 0 分），"
                         "被剔除学生的完整名单见 Excel「01 阅读说明」。" % (s, blank))
        if abnormal:
            notes.append("「%s」发现 %d 条异常值（超出 0~%g 或非数值），已剔除：%s"
                         % (s, len(abnormal), full, "、".join(abnormal[:8]) + ("…" if len(abnormal) > 8 else "")))
        if excluded:
            excluded_all[s] = excluded

        for st, v in valid:
            rec = score_map.setdefault(st["sid"], {"cls": st["cls"], "scores": {}})
            rec["scores"][s] = v
            if not rec.get("cls"):
                rec["cls"] = st["cls"]

        scores = [v for _, v in valid]
        focus_scores = [v for st, v in valid if st["cls"] == focus_class] or scores

        item = {
            "column": col,
            "full": full,
            "full_source": meta[s]["full_source"],
            "pass": meta[s]["pass"],
            "good": meta[s]["good"],
            "excellent": meta[s]["excellent"],
            "low": meta[s]["low"],
            "stats": basic_stats(focus_scores, full, meta[s]),
            "stats_all": basic_stats(scores, full, meta[s]),
            "bands": band_table(focus_scores, full),
            "bands_all": band_table(scores, full),
            "shape": detect_shape(focus_scores, full),
            "questions": build_questions(s, questions.get(s), full, meta[s], scope_sids,
                                          two_level_q, sid2cls, classes),
            "knowledge_points": [],
            "excluded": excluded,
            "comparison": build_comparison(s, valid, student_rows, classes, focus_class,
                                           full, params, meta[s]),
            "individuals": build_individuals(s, valid, focus_class, full, meta[s],
                                             history, questions.get(s), scope_class),
        }
        # build_questions 在班级层该题无记录时会自动退回年级层，所以这里通常不会为空；
        # 真为空说明逐题表里该学科一道有效记录都没有 → 交给下面的 questions_missing。
        item["knowledge_points"] = build_kp(item["questions"], meta[s])
        if not item["questions"]:
            item["questions_missing"] = True
        results[s] = item

    cross = build_cross(subjects, results, history)
    grade_overview = build_grade_overview(subjects, results, score_map, classes)
    history_summary = build_history_summary(history, hinfo, subjects, results, sid2cls, classes)

    # 只分析部分学科时，「全科总分」这个说法是错的（主表里还有别的学科列没算进来）
    partial = len(subjects) < len(detected)
    total_label = "所选学科总分" if partial else "全科总分"
    if partial:
        notes.append("本次只分析了 %d 个学科（%s），主表里共识别到 %d 个学科列（%s）。"
                     "结果册里的「%s」是**所选学科合计**（满分 %g 分），不代表学校层面的整份总分。"
                     % (len(subjects), "、".join(subjects), len(detected), "、".join(detected),
                        total_label, sum(meta[s]["full"] for s in subjects)))

    out = {
        "meta": {
            "exam_name": exam_name,
            "focus_class": focus_class,
            "focus_class_requested": focus_class_requested,
            "focus_class_explicit": explicit_focus,
            "classes": classes,
            "teacher": teacher,
            "date": exam_date,
            "student_count": len(student_rows),
            # 有没有**真实学号**（用户要求 2026-10-11）：假学号（#N 兜底）不显示成「学号」列。
            "has_student_id": any(not st.get("sid_auto") for st in student_rows),
            "source_sheet": used_sheet,
            "subjects": subjects,
            "subject_scope_label": "、".join(subjects),
            "mode": "single" if len(subjects) == 1 else "multi",
            "partial_subjects": partial,
            "total_label": total_label,
            "has_knowledge_points": bool(q_has_kp),
            "history_order_source": hinfo.get("source") or "none",
            "history_order_reliable": bool(hinfo.get("reliable", True)),
            "duplicate_sids": dup_rows,
            "full_policy": policy,
            "full_to_confirm": to_confirm,
            "full_summary": "；".join("%s %g 分（%s）"
                                   % (s, meta[s]["full"],
                                      {"user": "用户指定", "inferred": "数据推断·待确认",
                                       "default": "常规100分制·待确认"}[meta[s]["full_source"]])
                                   for s in subjects),
            "individual_scope": scope_class or "全部样本",
            "individual_scope_is_focus": bool(scope_class),
            # 维度 3 的两层：班级层 = individual_scope，年级层 = 全部样本（用户要求 2026-10-10）
            "grade_scope": "全部样本",
            "grade_scope_count": len(student_rows),
            "two_level_questions": two_level_q,
            "has_class_question_detail": bool(two_level_q and classes),
            "multi_class": bool(classes) and len(classes) > 1,
            "has_history_summary": bool(history_summary),
            "generated_at": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source_file": os.path.basename(args.data),
            "params": params,
        },
        "data_notes": notes,
        "data_excluded": excluded_all,
        "results": results,
        "cross_subject": cross,
        "grade_overview": grade_overview,
        "history_summary": history_summary,
    }
    return out


# --------------------------------------------------------------------------- #
# 逐题
# --------------------------------------------------------------------------- #
def parse_questions(headers, rows, subjects, notes):
    """解析逐题长表。

    ⚠️ **绝不凭空造知识点**：逐题表没有「知识点」列（或该列整列为空）时，
    ``questions[].kp`` 一律留空、``knowledge_points`` 为空 → 报告的维度 4 与 Excel 的
    「05 知识点优先级」整节/整表不生成。此处曾用 ``d["kp"] or "未标注"`` 兜底，
    结果报告摘要会写出「共性薄弱知识点集中：数学→未标注（65.0%）」这种**虚构教学结论**。
    """
    c_sub = pick_col(headers, ["学科", "科目"])
    c_q = pick_col(headers, ["题号", "题目", "小题"])
    c_full = pick_col(headers, ["满分", "分值", "题目满分"])
    c_score = pick_col(headers, ["得分", "分数", "学生得分"])
    c_kp = pick_col(headers, ["知识点", "考点", "知识块"])
    c_id = pick_col(headers, ["学号", "考号", "学籍号", "id"])
    if not (c_sub and c_q and c_full and c_score):
        notes.append("逐题表缺少必需列（学科/题号/满分/得分），已忽略该表。")
        return {}, False
    alias_map = {}
    for s in subjects:
        alias_map.setdefault(norm_subject(s), s)
    out = {}
    for r in rows:
        sub = str(r.get(c_sub, "")).strip()
        key = alias_map.get(norm_subject(sub))
        if key is None:
            continue
        q = str(r.get(c_q, "")).strip()
        full = to_num(r.get(c_full))
        score = to_num(r.get(c_score))
        if not q or full in (None, 0) or score is None:
            continue
        sid = str(r.get(c_id, "")).strip() if c_id else ""
        d = out.setdefault(key, {}).setdefault(q, {"full": full, "scores": [], "sids": [], "kp": ""})
        # 同一 (题号, 学号) 出现多次（重复行）时按「取最后一条」覆盖，避免同一人重复计数
        if sid and sid in d["sids"]:
            d["scores"][d["sids"].index(sid)] = score
        else:
            d["scores"].append(score)
            d["sids"].append(sid)
        kp = norm_kp(r.get(c_kp, "")) if c_kp else ""
        if kp and not d["kp"]:
            d["kp"] = kp
    all_q = [d for sub in out.values() for d in sub.values()]
    n_q = len(all_q)
    n_kp = sum(1 for d in all_q if d["kp"])
    if n_q == 0:
        return {}, False
    if n_kp == 0:
        if c_kp:
            notes.append("逐题表有「知识点」列但**整列为空（或只填了 -、/ 之类的占位符）**，"
                         "知识点相关统计（报告维度 4、Excel「05 知识点优先级」）本次不生成——"
                         "不编造知识点。补齐该列即可自动生成。")
        else:
            notes.append("逐题表**没有「知识点」列**，知识点相关统计（报告维度 4、"
                         "Excel「05 知识点优先级」）本次不生成——不编造知识点。"
                         "加一列「知识点」即可自动生成。")
        return out, False
    if n_kp < n_q:
        notes.append("逐题表有 %d 道题没有知识点归属（共 %d 道），**这些题不参与知识点统计**"
                     "（报告维度 4 / Excel 05 只统计有归属的 %d 道）；逐题得分率（维度 3）不受影响。"
                     % (n_q - n_kp, n_q, n_kp))
    return out, True


def q_sort_key(q):
    """题号排序键：纯数字 / 小数按数值排（2 在 10 前），其余（「一」「（3）」）排在数字之后。"""
    s = str(q).strip()
    try:
        return (0, float(s), "")
    except ValueError:
        return (1, 0.0, s)


def build_questions(subject, qdata, full, smeta, scope_sids=None, two_level=False,
                    sid2cls=None, classes=None):
    """逐题得分率，**同时算出班级层、年级层与各班三套**（用户要求 2026-10-10）。

    ``scope_sids`` 不为 None 时它是**班级层**（本班）的学号集合，此时每题除了班级层
    还带一份**年级层**（全部样本）的均值/得分率/判定。
    ``two_level`` 表示两层**真的不同源**（班级人数 < 样本人数）——单班样本时班级层就是全体，
    两层数字一模一样，此时置 False，报告与结果册只呈现一套、不摆两份重复的表格。
    逐题表没有「学号」列时无法分层，两层自然相同。

    ``sid2cls`` / ``classes`` 都给齐时，每题再带一份 ``by_class``：**每个班级**在该题上的
    平均得分与得分率（用户要求 2026-10-10：「每个班级每道小题的得分率」）。

    ``kp`` 原样透传（可能为空串）——空就是「这道题没有知识点归属」，不用「未标注」占位。
    """
    if not qdata:
        return []
    sid2cls = sid2cls or {}
    items = []
    for q, d in qdata.items():
        sids = list(d.get("sids") or [])
        scores_all = list(d.get("scores") or [])
        has_sid = any(sids)
        if scope_sids is not None and has_sid:
            cls_scores = [sc for sid, sc in zip(sids, scores_all) if sid in scope_sids]
        else:
            cls_scores = scores_all
        if not cls_scores and not scores_all:
            continue
        # 班级层在该题没有记录时退回年级层——否则这道题会整题消失，年级视角也跟着丢
        use = cls_scores or scores_all
        mean = sum(use) / len(use)
        rate = ratio(mean, d["full"])
        mean_all = (sum(scores_all) / len(scores_all)) if scores_all else mean
        rate_all = ratio(mean_all, d["full"])
        # 各班在该题上的得分率（逐班统计，绝不把多科 / 多班混在一起）
        by_class = []
        if classes and has_sid:
            buckets = {}
            for sid, sc in zip(sids, scores_all):
                c = sid2cls.get(sid)
                if c:
                    buckets.setdefault(c, []).append(sc)
            for c in classes:
                vals = buckets.get(c) or []
                if not vals:
                    continue
                cm = sum(vals) / len(vals)
                by_class.append({"cls": c, "mean": rnd(cm),
                                 "rate": rnd(ratio(cm, d["full"]), 4),
                                 "n": len(vals)})
        items.append({
            "q": q, "full": rnd(d["full"]),
            "mean": rnd(mean), "rate": rnd(rate, 4), "n": len(use),
            "level": classify(rate, Q_LEVELS),
            "mean_all": rnd(mean_all), "rate_all": rnd(rate_all, 4), "n_all": len(scores_all),
            "level_all": classify(rate_all, Q_LEVELS),
            "two_scope": bool(two_level),
            "by_class": by_class,
            "kp": d.get("kp") or "",
        })
    items.sort(key=lambda x: q_sort_key(x["q"]))
    return items


def build_grade_overview(subjects, results, score_map, classes):
    """年级层总览（用户要求 2026-10-11）：**全年级总分按班级排名 + 每个学科按班级排名**。

    ``score_map`` = ``{sid: {"cls": 班级, "scores": {学科: 分数}}}``，**覆盖全部学生**
    （不能用 ``individuals.ranking``——那份排名已按主分析班级收敛，看不到别的班）。

    返回::

        {"by_total":  [{cls, n, mean_total, full_total, rate, rank}],
         "by_subject": {学科: [{cls, n, mean, score_rate, rank}]},
         "grade_stats": {学科: {mean, score_rate, excellent_rate, good_rate,
                                qualified_rate, fail_rate, bands}},
         "class_count": N}

    排名按**均分**降序（各班人数可能不同，用均分比总平均更公平）；
    各科班级排名按该科**得分率**降序（各科满分不同，得分率才可横向比）。
    ``classes`` 少于 2 个时返回 ``{}``（单班样本谈不上「班级排名」）。
    """
    if not classes or len(classes) < 2:
        return {}
    full_total = sum(results[s]["full"] for s in subjects)
    cls_total, cls_sub = {}, {}
    for sid, rec in score_map.items():
        c = rec.get("cls") or ""
        if not c:
            continue
        tot, got = 0.0, 0
        for s in subjects:
            v = (rec.get("scores") or {}).get(s)
            if v is None:
                continue
            tot += v
            got += 1
            cls_sub.setdefault(s, {}).setdefault(c, []).append(v)
        if got:
            cls_total.setdefault(c, []).append(tot)
    by_total = []
    for c in classes:
        vals = cls_total.get(c) or []
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        by_total.append({"cls": c, "n": len(vals), "mean_total": rnd(mean),
                         "full_total": rnd(full_total),
                         "rate": rnd(ratio(mean, full_total), 4)})
    by_total.sort(key=lambda x: -x["mean_total"])
    for i, r in enumerate(by_total, 1):
        r["rank"] = i

    # ---- 每个学科：各班得分率排名 ----
    by_subject = {}
    for s in subjects:
        rows = []
        for c in classes:
            vals = (cls_sub.get(s) or {}).get(c) or []
            if not vals:
                continue
            rows.append({"cls": c, "n": len(vals), "mean": rnd(sum(vals) / len(vals)),
                         "score_rate": rnd(ratio(sum(vals) / len(vals), results[s]["full"]), 4)})
        rows.sort(key=lambda x: -(x.get("score_rate") or 0))
        for i, r in enumerate(rows, 1):
            r["rank"] = i
        by_subject[s] = rows

    # ---- 全年级各学科四率 + 分数段分布 ----
    grade_stats = {}
    for s in subjects:
        it = results[s]
        st = it.get("stats_all") or {}
        grade_stats[s] = {
            "full": it["full"], "count": st.get("count"),
            "mean": st.get("mean"), "score_rate": st.get("score_rate"),
            "excellent_rate": st.get("excellent_rate"),
            "good_rate": st.get("good_rate"),
            "qualified_rate": st.get("qualified_rate"),
            "fail_rate": st.get("fail_rate"),
            "pass_rate": st.get("pass_rate"),
            "bands": it.get("bands_all") or [],
        }
    return {"by_total": by_total, "by_subject": by_subject,
            "grade_stats": grade_stats, "class_count": len(classes)}


def build_history_summary(history, hinfo, subjects, results, sid2cls, classes):
    """历次成绩对比（用户要求 2026-10-11）：**历次年级 / 历次班级**的成绩对比。

    依赖历次表。历次表除「学号 / 考试 / 总分」外，若还带**学科列**（如 语文 / 数学…）
    或长表式的「学科 + 分数」列，则学科层指标一并算出；没有学科列时只给总分维度的对比
    （这时 ``has_subject_detail`` 为 False，报告与结果册据此如实标注，**不编造学科历次数据**）。

    返回::

        {"exams": [考试名…], "has_subject_detail": bool,
         "grade": {"total": [{exam, mean, n}],
                   "subjects": {学科: [{exam, mean, score_rate, excellent_rate,
                                        good_rate, qualified_rate, fail_rate}]}},
         "by_class": {班级: {"total": [...], "subjects": {…}}}}
    """
    if not history or not hinfo or not hinfo.get("names"):
        return {}
    exams = [str(x) for x in hinfo["names"]]
    subj_detail = bool(hinfo.get("has_subject_detail"))

    # 逐考试聚合：总分（年级 / 班级）
    grade_total, cls_total = [], {}
    grade_sub, cls_sub = {}, {}
    for rec in history.values():
        cls = sid2cls.get(rec.get("sid")) or rec.get("cls") or "（未标注班级）"
        for pt in rec.get("points") or []:
            exam = str(pt.get("exam"))
            if pt.get("total") is not None:
                grade_total.append((exam, pt["total"]))
                cls_total.setdefault(cls, []).append((exam, pt["total"]))
            for sj, sc in (pt.get("subjects") or {}).items():
                if sc is None:
                    continue
                grade_sub.setdefault(sj, []).append((exam, sc))
                cls_sub.setdefault(cls, {}).setdefault(sj, []).append((exam, sc))

    def agg(pairs, full):
        """把 (考试, 分数) 对聚合成逐次均分 + 四率。"""
        buck = {}
        for exam, v in pairs:
            buck.setdefault(exam, []).append(v)
        out = []
        for exam in exams:
            vals = buck.get(exam) or []
            if not vals:
                continue
            st = basic_stats(vals, full, {"excellent": full * EXC_R, "good": full * GOOD_R,
                                          "pass": full * PASS_R, "low": full * LOW_R})
            out.append({"exam": exam, "n": st["count"], "mean": st["mean"],
                        "score_rate": st["score_rate"],
                        "excellent_rate": st["excellent_rate"], "good_rate": st["good_rate"],
                        "qualified_rate": st["qualified_rate"], "fail_rate": st["fail_rate"],
                        "pass_rate": st["pass_rate"]})
        return out

    full_total = sum(results[s]["full"] for s in subjects)
    grade = {"total": agg(grade_total, full_total),
             "subjects": {s: agg(grade_sub.get(s) or [], results[s]["full"])
                          for s in subjects if grade_sub.get(s)}}
    by_class = {}
    for c, pairs in cls_total.items():
        by_class[c] = {"total": agg(pairs, full_total), "subjects": {}}
    for c, sjmap in cls_sub.items():
        for s in subjects:
            if sjmap.get(s):
                by_class.setdefault(c, {"total": [], "subjects": {}})
                by_class[c]["subjects"][s] = agg(sjmap[s], results[s]["full"])
    return {"exams": exams, "has_subject_detail": subj_detail,
            "grade": grade, "by_class": by_class}


def build_kp(questions, smeta):
    """知识点聚合。**只聚合有知识点归属的题**；一道都没有时返回 []（维度 4 整节不生成）。"""
    if not questions:
        return []
    agg = {}
    for it in questions:
        kp = str(it.get("kp") or "").strip()
        if not kp:
            continue
        agg.setdefault(kp, []).append(it)
    if not agg:
        return []
    rows = []
    for kp, its in agg.items():
        rate = sum(i["rate"] for i in its) / len(its)
        rows.append({
            "kp": kp,
            "rate": rnd(rate, 4),
            "level": classify(rate, KP_LEVELS),
            # 涉及题号一律**升序**（用户要求 2026-10-11：表内题号列都按题号排），
            # 不依赖上游 questions 的排列顺序。
            "questions": sorted([i["q"] for i in its], key=q_sort_key),
            "question_count": len(its),
        })
    rows.sort(key=lambda x: x["rate"])
    for i, r in enumerate(rows, 1):
        r["priority"] = i
    return rows


# --------------------------------------------------------------------------- #
# 对比
# --------------------------------------------------------------------------- #
def build_comparison(subject, valid, student_rows, classes, focus_class, full, params, smeta):
    def metrics(vals):
        st = basic_stats(vals, full, smeta)
        if not st.get("count"):
            return None
        return {
            "count": st["count"], "mean": st["mean"], "median": st["median"],
            "max": st["max"], "min": st["min"], "range": st["range"], "std": st["std"],
            "pass_rate": st["pass_rate"], "excellent_rate": st["excellent_rate"],
            "good_rate": st["good_rate"], "qualified_rate": st["qualified_rate"],
            "fail_rate": st["fail_rate"],
            "low_rate": st["low_rate"], "score_rate": st["score_rate"],
            "bands": band_table(vals, full),
        }

    by_class = []
    for c in classes:
        vals = [v for st, v in valid if st["cls"] == c]
        m = metrics(vals)
        if m:
            m["name"] = c
            by_class.append(m)

    focus_vals = [v for st, v in valid if st["cls"] == focus_class] or [v for _, v in valid]
    focus_m = metrics(focus_vals)
    if focus_m:
        focus_m["name"] = focus_class
    all_vals = [v for _, v in valid]
    all_m = metrics(all_vals)

    benchmarks = []
    if all_m:
        benchmarks.append(dict(all_m, name="年级均分（本次）", kind="年级"))
    bm = (params.get("benchmarks") or {})
    for label, mapping in bm.items():
        if isinstance(mapping, dict) and subject in mapping:
            val = to_num(mapping[subject])
            if val is not None:
                benchmarks.append({
                    "name": label, "kind": "基准", "avg": rnd(val), "mean": rnd(val),
                    "source": "explicit",
                })
    if not bm:
        # 允许 params 里直接写 bench_年级 / bench_区市
        for key, label in (("bench_grade", "年级均分（外部）"), ("bench_region", "区市均分")):
            val = to_num(params.get(key, {}).get(subject) if isinstance(params.get(key), dict) else params.get(key))
            if val is not None:
                benchmarks.append({"name": label, "kind": "基准", "avg": rnd(val), "mean": rnd(val)})
    if len(benchmarks) <= 1:
        note_missing = True
    else:
        note_missing = False

    fmean = focus_m["mean"] if focus_m else None
    for b in benchmarks:
        bmean = b.get("mean")
        if bmean and fmean is not None:
            b["over_rate"] = rnd((fmean - bmean) / bmean * 100, 2)
        else:
            b["over_rate"] = None
    for c in by_class:
        if all_m and all_m.get("mean"):
            c["over_rate"] = rnd((c["mean"] - all_m["mean"]) / all_m["mean"] * 100, 2)
        else:
            c["over_rate"] = None

    return {
        "focus": focus_m, "by_class": by_class, "benchmarks": benchmarks,
        "grade": all_m, "need_external_benchmark": note_missing,
    }


# --------------------------------------------------------------------------- #
# 个体
# --------------------------------------------------------------------------- #
def natural_key(text):
    """把「第2次月考」「第10次月考」按数字大小排序（避免字典序把第10次排到第2次前）。"""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", str(text)) if t != ""]


CN_DIGITS = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
             "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_to_int(text):
    """把「一 / 二 / 十 / 十二 / 二十三」这类中文数字转成整数；解析不了返回 None。

    学校成绩表里「第一次月考」「二模」这类写法非常常见，而中文数字的**字典序与数值序
    不一致**（三 < 二 in Unicode），若不解析就会把「第三次月考」排到「第二次月考」前面。
    """
    s = str(text).strip()
    if not s:
        return None
    if "十" in s:
        head, _, tail = s.partition("十")
        tens = CN_DIGITS.get(head, 1) if head else 1
        if head and head not in CN_DIGITS:
            return None
        ones = CN_DIGITS.get(tail, 0) if tail else 0
        if tail and tail not in CN_DIGITS:
            return None
        return tens * 10 + ones
    total = 0
    for ch in s:
        if ch not in CN_DIGITS:
            return None
        total = total * 10 + CN_DIGITS[ch]
    return total


def parse_exam_seq(value):
    """尝试把「考试」列的值解析成可比较的时间键（数字 → 日期 → 名称里的序号 → None）。"""
    if isinstance(value, _dt.datetime):
        return value.timestamp()
    if isinstance(value, _dt.date):
        return _dt.datetime(value.year, value.month, value.day).timestamp()
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    if s.replace(".", "", 1).isdigit():
        return float(s)
    m = re.search(r"(\d{4})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})", s)
    if m:
        try:
            return _dt.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).timestamp()
        except ValueError:
            return None
    m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", s)
    if m:
        try:
            return _dt.datetime(2000, int(m.group(1)), int(m.group(2))).timestamp()
        except ValueError:
            return None
    # 名称里的序号：「第3次月考」「第3次」「第3轮」「3模」「三模」「第三次月考」
    m = re.search(r"第\s*([0-9]+|[零一二两三四五六七八九十]+)\s*[次轮回阶段]", s) \
        or re.search(r"([0-9]+|[零一二两三四五六七八九十]+)\s*模", s)
    if m:
        raw = m.group(1)
        return float(raw) if raw.isdigit() else cn_to_int(raw)
    return None


def history_sort_rule(all_points, names, notes, explicit_order=None):
    """决定历次成绩的排序规则。

    返回 ``(key, source, reliable)``：

    * ``source`` ∈ ``explicit``（--history-order）/ ``seq``（序号、日期或名称里的序号）/
      ``single``（只有一场考试）/ ``natural``（名称里都带序号但只在名称层面可比）/
      ``unknown``（有名称既无序号也无日期 → **顺序不可判定**）
    * ``reliable=False`` 时调用方**不再阻断**，而是把告警写进 stderr 与 ``data_notes``，
      并在报告维度 6 上显著标注 —— 趋势判定 / 进步榜 / 需关注名单可能整体反向，
      但报告本体（其余 5 个维度）仍然是有效的，不该因为维度 6 的顺序存疑就整份不出。

    优先级：显式 ``--history-order`` > 显式「序号」列 > 「日期」列 > 名称里的序号/中文数字
    （第2次 < 第10次；第1次 = 第一次；一模 < 二模）。**不再用裸字典序**——字典序会把
    「第10次月考」排到「第1次月考」前面，使趋势判定整体反转。
    """
    if explicit_order:
        idx = {n: i for i, n in enumerate(explicit_order)}
        missing = [n for n in names if n not in idx]
        if missing and notes is not None:
            notes.append("--history-order 未覆盖这些考试名称：%s（已排在末尾）。"
                         % "、".join(dict.fromkeys(missing)))
        return (lambda p: idx.get(p["exam"], len(idx) + 1)), "explicit", True
    # 「序号」或「日期」可用时按它排（只要 9 成以上记录有值即可）
    with_seq = [p for p in all_points if p.get("seq") is not None]
    if with_seq and len(with_seq) >= 0.9 * len(all_points) \
            and len({p["seq"] for p in with_seq}) > 1:
        return (lambda p: (p["seq"] if p.get("seq") is not None else float("inf"))), "seq", True
    if len(names) <= 1:
        return (lambda p: natural_key(p["exam"])), "single", True
    if all(re.search(r"\d", str(n)) for n in names):
        return (lambda p: natural_key(p["exam"])), "natural", True
    # 有名称既不含数字、也不来自序号/日期列 → 顺序不可判定：**只警告不阻断**
    if notes is not None:
        notes.append("历次成绩的「考试」列无法判断先后顺序（考试名称：%s），已按名称自然序估算 —— "
                     "趋势判定、进步榜、需关注名单**可能整体反向**，请核对（本项已在报告「核心结论摘要」"
                     "与维度 6 显著标注，Excel 01/07 也有标注）。补一列「序号」或「日期」，或用 --history-order \"%s\" "
                     "指定顺序后重跑即可。"
                     % ("、".join(str(n) for n in names), ",".join(str(n) for n in names)))
    return (lambda p: natural_key(p["exam"])), "unknown", False


def parse_history(headers, rows, subjects=None, notes=None, order=None):
    """解析历次成绩长表。

    支持两种形态：
    ① **宽表** —— 学号 / 考试 / 总分 +（可选）各学科列（列名含学科名，如「语文」「数学」）+（可选）班级；
    ② **长表** —— 学号 / 考试 / 学科 / 分数（同一学生多次考试多行），自动透视成 ① 里那种记录。
    只有「总分」而没有学科列时也能跑（此时 ``has_subject_detail`` 为 False，
    历次对比只到总分维度，**不编造学科历次数据**）。
    """
    notes = notes if notes is not None else []
    subjects = list(subjects or [])
    c_id = pick_col(headers, ["学号", "考号", "id"])
    c_exam = pick_col(headers, ["考试", "考试名称", "次序", "第几次"])
    c_total = pick_col(headers, ["总分", "总成绩"])
    c_rank = pick_col(headers, ["排名", "名次", "班级排名", "年级排名"])
    c_name = pick_col(headers, ["姓名"])
    c_cls = pick_col(headers, ["班级", "班别", "行政班"])
    c_date = pick_col(headers, ["日期", "考试日期", "时间"])
    c_seq = pick_col(headers, ["序号", "次序号", "顺序"])
    # 长表形态：单独一列「学科」+ 一列「分数」
    c_subj = pick_col(headers, ["学科", "科目"])
    c_score = pick_col(headers, ["分数", "得分", "成绩"])
    # 宽表形态：每个学科一列
    subj_cols = {}
    for s in subjects:
        c = match_subject_col(headers, s)
        if c and c not in (c_id, c_exam, c_total, c_score, c_name, c_cls, c_rank, c_seq, c_date, c_subj):
            subj_cols[s] = c
    if c_total is None and subj_cols:
        # 只有各学科列、没有总分列：允许，总分由各科相加得到
        pass
    if not (c_id and c_exam and (c_total or subj_cols or (c_subj and c_score))):
        notes.append("历次成绩表缺少必需列（学号 / 考试 / 总分或学科分数），已忽略该表。")
        return {}, {"source": "none", "reliable": True, "names": [], "has_subject_detail": False}
    if c_seq and c_seq in (c_exam, c_id):
        c_seq = None
    data = {}
    for r in rows:
        sid = str(r.get(c_id, "")).strip()
        exam = str(r.get(c_exam, "")).strip()
        if not sid or not exam:
            continue
        # 学科分数：宽表按列取，长表按「学科」单元格定位到对应学科列
        subs_scores = {}
        for s, c in subj_cols.items():
            v = to_num(r.get(c))
            if v is not None:
                subs_scores[s] = v
        if c_subj and c_score:
            sj = norm_subject(r.get(c_subj))
            for s in subjects:
                if norm_subject(s) == sj or str(r.get(c_subj)).strip() == s:
                    v = to_num(r.get(c_score))
                    if v is not None:
                        subs_scores[s] = v
                    break
        tot = to_num(r.get(c_total))
        if tot is None and subs_scores:
            tot = sum(subs_scores.values())
        if tot is None:
            continue
        seq = to_num(r.get(c_seq)) if c_seq else None
        if seq is None and c_date:
            seq = parse_exam_seq(r.get(c_date))
        if seq is None:
            seq = parse_exam_seq(exam)
        rec = data.setdefault(sid, {"name": str(r.get(c_name, "")).strip() if c_name else "",
                                    "cls": str(r.get(c_cls, "")).strip() if c_cls else "",
                                    "points": []})
        if c_cls and not rec.get("cls"):
            rec["cls"] = str(r.get(c_cls, "")).strip()
        point = {"exam": exam, "total": tot, "seq": seq,
                 "subjects": subs_scores,
                 "rank": to_num(r.get(c_rank)) if c_rank else None}
        # 同一学号 + 同一考试重复出现时按「取最后一条」覆盖，避免重复计数
        merged = False
        for k, p in enumerate(rec["points"]):
            if p["exam"] == exam:
                if not point["subjects"] and p.get("subjects"):
                    point["subjects"] = p["subjects"]
                rec["points"][k] = point
                merged = True
                break
        if not merged:
            rec["points"].append(point)
    names = []
    for rec in data.values():
        for p in rec["points"]:
            if p["exam"] not in names:
                names.append(p["exam"])
    all_points = [p for rec in data.values() for p in rec["points"]]
    key, source, reliable = history_sort_rule(all_points, names, notes, order)
    for rec in data.values():
        rec["points"].sort(key=key)
    has_subj_detail = any(p.get("subjects") for p in all_points)
    return data, {"source": source, "reliable": reliable, "names": names,
                  "has_subject_detail": has_subj_detail}


def trend_of(seq, key, lower_is_better=False):
    """依据序列判定 持续进步 / 持续下滑 / 波动 / 平稳。

    返回的 delta 统一为「变化量」，**正数=进步**（与报告着色一致）：
    ``lower_is_better=True`` 用于名次序列（名次数字变小才算进步，delta 取反）。
    """
    vals = [p[key] for p in seq if p.get(key) is not None]
    if len(vals) < 2:
        return "数据不足", 0.0
    sign = -1.0 if lower_is_better else 1.0
    diffs = [sign * (vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
    span = max(vals) - min(vals)
    total = sign * (vals[-1] - vals[0])
    up = all(d >= -0.001 for d in diffs)
    down = all(d <= 0.001 for d in diffs)
    if up and total > 0:
        return "持续进步", total
    if down and total < 0:
        return "持续下滑", total
    if span >= max(3.0, abs(total) * 1.5):
        return "波动", total
    return "平稳", total


def build_individuals(subject, valid, focus_class, full, smeta, history, qdata, scope_class=None):
    """个体追踪。

    ``scope_class`` 非空时，排名与分层名单**只统计该班**——此前无论是否指定班级，
    这里都用全体学生排名，报告却标成「班内排名」，与本班范围的维度 1/2/5 冲突。
    """
    exc, ps, lw = smeta["excellent"], smeta["pass"], smeta["low"]
    buf = 0.05 * full
    scope_note = ""
    if scope_class:
        scoped = [(st, v) for st, v in valid if st["cls"] == scope_class]
        if scoped:
            valid = scoped
        else:
            scope_note = "（本班无有效成绩，已回退为全部样本）"
    # 排名范围标签：单班样本（主表无「班级」列）时 scope_class 就是兜底哨兵「本班」，
    # 再拼一次「（本班）」会得到「本班（本班）」这种重复标签。
    if not scope_class:
        rank_scope = "全部样本（含各班）"
    elif scope_class == "本班":
        rank_scope = "本班"
    else:
        rank_scope = "%s（本班）" % scope_class
    out = {"mode": "cross-section", "lists": {}, "history": [],
           "scope": scope_class or "全部样本",
           "scope_note": scope_note,
           "rank_scope": rank_scope}

    top, near_exc, near_pass, weak = [], [], [], []
    recs = []
    for st, v in valid:
        name = st["name"] or st["sid"]
        recs.append({"sid": st["sid"], "name": name, "cls": st["cls"], "score": rnd(v)})
        if v >= exc:
            top.append({"name": name, "score": rnd(v)})
        elif exc - buf <= v < exc:
            near_exc.append({"name": name, "score": rnd(v), "gap": rnd(exc - v)})
        if ps - buf <= v < ps:
            near_pass.append({"name": name, "score": rnd(v), "gap": rnd(ps - v)})
        if v < lw:
            weak.append({"name": name, "score": rnd(v)})
    recs.sort(key=lambda x: -x["score"])
    for i, r in enumerate(recs, 1):
        r["rank"] = i
    out["ranking"] = recs
    out["lists"] = {
        "尖子生": sorted(top, key=lambda x: -x["score"]),
        "临界优秀": sorted(near_exc, key=lambda x: -x["score"]),
        "临界及格": sorted(near_pass, key=lambda x: -x["score"]),
        "学困生": sorted(weak, key=lambda x: x["score"]),
    }

    if history:
        rows = []
        for st, v in valid:
            h = history.get(st["sid"])
            if not h:
                continue
            pts = h["points"]
            t_type, t_delta = trend_of(pts, "total")
            r_type, r_delta = trend_of(pts, "rank", lower_is_better=True)
            rows.append({
                "sid": st["sid"], "name": st["name"] or h.get("name") or st["sid"],
                "cls": st["cls"],
                "exams": [p["exam"] for p in pts],
                "totals": [rnd(p["total"]) for p in pts],
                "ranks": [p["rank"] for p in pts],
                "total_delta": rnd(t_delta), "rank_delta": rnd(r_delta),
                "trend": t_type if t_type != "数据不足" else r_type,
                "trend_score": t_type,
                "trend_rank": r_type,
            })
        # 历次表里的学号与主表一个都对不上（或每人都只有 1 次记录）时**不冒充趋势**，
        # 保持横截面分层——否则章节标题写「个体追踪（历次成绩）」而内容全是「数据不足」。
        if rows:
            out["mode"] = "history"
            rows.sort(key=lambda x: -(x["rank_delta"] or -999))
            out["history"] = rows
            # rank_delta / total_delta 均为「正数=进步」；进步榜取名次前进≥3 名或总分持续进步者
            out["lists"]["进步榜"] = [r for r in rows
                                     if (r["rank_delta"] or 0) >= 3 or r["trend_score"] == "持续进步"][:12]
            watch = sorted([r for r in rows if (r["rank_delta"] or 0) <= -3 or (r["total_delta"] or 0) < 0],
                           key=lambda x: (x["rank_delta"] if x["rank_delta"] is not None else 0,
                                          x["total_delta"] if x["total_delta"] is not None else 0))
            out["lists"]["需关注名单"] = watch[:12]
    return out


# --------------------------------------------------------------------------- #
# 跨学科
# --------------------------------------------------------------------------- #
def build_cross(subjects, results, history):
    if len(subjects) < 2:
        return {}
    table = []
    for s in subjects:
        r = results[s]
        st = r["stats"]
        table.append({
            "subject": s, "full": r["full"],
            "mean": st.get("mean"), "score_rate": st.get("score_rate"),
            "pass_rate": st.get("pass_rate"), "excellent_rate": st.get("excellent_rate"),
            "good_rate": st.get("good_rate"), "qualified_rate": st.get("qualified_rate"),
            "fail_rate": st.get("fail_rate"),
            "low_rate": st.get("low_rate"), "std": st.get("std"),
            "median": st.get("median"), "max": st.get("max"), "min": st.get("min"),
            "shape": r["shape"]["type"],
        })
    top_q, top_kp = {}, {}
    for s in subjects:
        qs = [q for q in results[s]["questions"] if q["level"] in ("共性错题", "薄弱题")]
        qs.sort(key=lambda x: x["rate"])
        top_q[s] = [{"q": q["q"], "rate": q["rate"], "kp": q["kp"]} for q in qs[:3]]
        kps = [k for k in results[s]["knowledge_points"] if k["level"] in ("危险", "薄弱")]
        kps.sort(key=lambda x: x["rate"])
        top_kp[s] = [{"kp": k["kp"], "rate": k["rate"], "level": k["level"],
                      "questions": k["questions"]} for k in kps[:3]]

    # 班级在各学科的排名一致性
    cls_rank = {}
    for s in subjects:
        bcs = sorted([c for c in results[s]["comparison"]["by_class"]],
                     key=lambda c: -(c.get("score_rate") or 0))
        for i, c in enumerate(bcs, 1):
            cls_rank.setdefault(c["name"], {})[s] = i
    consistency = []
    for c, ranks in cls_rank.items():
        if len(ranks) < 2:
            continue
        best = min(ranks.items(), key=lambda kv: kv[1])
        worst = max(ranks.items(), key=lambda kv: kv[1])
        consistency.append({
            "class": c, "ranks": ranks,
            "avg_rank": rnd(sum(ranks.values()) / len(ranks), 2),
            "max_rank": max(ranks.values()),
            "all_top3": all(v <= 3 for v in ranks.values()),
            "lead_subject": best[0], "weak_subject": worst[0],
        })
    consistency.sort(key=lambda x: x["avg_rank"])
    return {"table": table, "top_questions": top_q, "top_knowledge": top_kp,
            "class_consistency": consistency}


# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(description="中小学考试成绩分析引擎")
    ap.add_argument("--data", required=True, help="成绩数据文件（xlsx/csv）")
    ap.add_argument("--sheet", default=None, help="主表所在的工作表名（默认第一个工作表）")
    ap.add_argument("--subjects", default="", help="分析学科范围，逗号分隔；留空自动识别")
    ap.add_argument("--exam-name", default=None, help="考试名称，如「高二期中考试」")
    ap.add_argument("--focus-class", default=None, help="重点分析的班级")
    ap.add_argument("--id-col", default=None)
    ap.add_argument("--name-col", default=None)
    ap.add_argument("--class-col", default=None)
    ap.add_argument("--questions-sheet", default=None, help="逐题得分表工作表名")
    ap.add_argument("--history-sheet", default=None, help="历次成绩表工作表名")
    ap.add_argument("--history-order", default=None,
                    help="历次考试的先后顺序（逗号分隔），如 \"第1次月考,期中考试,第2次月考,期末考试\"；"
                         "历次表既无「序号」也无「日期」、名称又排不出先后时强烈建议给"
                         "（不给只警告不阻断，趋势结论需自行核对）")
    ap.add_argument("--list-sheets", action="store_true", help="只列出工作簿中的工作表名后退出")
    ap.add_argument("--full", default=None,
                    help="各学科满分，逗号分隔，如 \"语文=150,数学=100,物理=10\"；"
                         "优先级高于数据推断，低于 params.json。"
                         "分制多为 100 分（常规）、150 分、10 分、5 分，不确定时请向用户确认")
    ap.add_argument("--full-policy", default=None, choices=["ask", "default"],
                    help="满分缺失时的策略：ask（默认）=推断不出就停下来请用户给出；"
                         "default=用户明确说「不用问」时，一律按常规 100 分制继续（仍会登记待确认）")
    ap.add_argument("--params", default=None, help="params.json（学科满分/基准均分等）")
    ap.add_argument("--out", default="analysis.json", help="输出 JSON 路径")
    args = ap.parse_args(argv)

    if args.list_sheets:
        names = sheet_names(args.data)
        if not names:
            print("[提示] %s 不是多工作表文件（CSV/TXT 无工作表概念）。" % args.data)
            return 0
        print("[OK] %s 共 %d 个工作表：" % (os.path.basename(args.data), len(names)))
        for i, n in enumerate(names):
            hh, rr = load_table(args.data, n, None)
            mark = "  ← 默认主表" if i == 0 else ""
            print("   %d) %-22s  %d 行 × %d 列%s" % (i + 1, n, len(rr), len(hh), mark))
        print("[提示] 用 --sheet 指定主表，--questions-sheet / --history-sheet 指定逐题表与历次表。")
        return 0

    result = run(args)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print("[OK] 学科：%s" % "、".join(result["meta"]["subjects"]))
    print("[OK] 学生 %d 人，班级 %s" % (result["meta"]["student_count"],
                                    "、".join(result["meta"]["classes"]) or "-"))
    print("[OK] 个体名单范围：%s" % result["meta"]["individual_scope"])
    print("[OK] 满分设置：%s" % result["meta"]["full_summary"])
    print("[OK] 已写出 %s" % os.path.abspath(args.out))
    pending = result["meta"].get("full_to_confirm") or []
    if pending:
        print("[需确认] 以下学科的满分不是用户指定的（满分猜错会让及格率/分数段整体失真），"
              "请与用户核对：")
        for x in pending:
            print("         · %s -> %g 分（%s；依据：%s）"
                  % (x["subject"], x["full"],
                     "由成绩分布推断" if x["source"] == "inferred" else "按常规 100 分制默认", x["basis"]))
        print("         常见分制：100（常规）/ 150 / 10 / 5；请把满分向用户核对一遍。")
        print("         如需更正：--full \"%s\""
              % ",".join("%s=%g" % (x["subject"], x["full"]) for x in pending))
    if result["data_notes"]:
        print("[提示] %d 条数据质量说明（只在 analysis.json 与本次输出里，报告与 Excel 结果册均不展示；"
              "交付时必须向用户复述），例如：%s"
              % (len(result["data_notes"]), result["data_notes"][0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
