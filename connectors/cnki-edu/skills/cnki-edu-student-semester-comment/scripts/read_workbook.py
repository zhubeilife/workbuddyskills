# -*- coding: utf-8 -*-
"""把「带大标题行 / 双行合并表头 / 多工作表」的成绩册读成标准列名。

真实成绩册的三种"脏"结构（本模块就是为它们写的）：

  1. **第 1 行是合并的大标题**（如「初一3班 平时成绩表（六次）」），真表头在第 2 行
  2. **双行合并表头**：「第1次」横向跨 7 科，下一行才是「数学/语文/…」，
     拼成「第1次-数学」这样的列名，既保留次数信息，又不丢学科识别
  3. **一个工作簿里多张表**：平时成绩 / 期中考试成绩 / 期末考试成绩

对外只暴露四组东西：

  · `read_workbook(path)`       —— 每个工作表都读成 (sheet, headers, rows)，并报出它跳过了几行标题
  · `split_columns(headers)`    —— 把列分成「本次学科列 / 平时趋势列 / 其他」
  · `trend_columns(headers)`    —— 趋势列按「学科 → [(第几次, 列号, 原列名)]」整理
  · `route_sheets(...)`         —— 选主成绩表 / 上次对比表 / 平时趋势表，并把每个决定写成提示

一条口径：**双行表头只在「上格是次数、下格是学科」时拼接**，其余情况一律取下面那格，
避免把「总分」这类单行表头也误拼成「第1次-总分」。
"""
import re

from subjects import canonical, subject_bases

ID_KEYS = ["学号", "考号", "编号", "学籍号", "学生编号"]
NAME_KEYS = ["姓名", "学生姓名", "名字"]

# 平时/过程性成绩的次数标记
_TREND_PATTERNS = [
    re.compile(r"第\s*(\d+)\s*[次回]"),
    re.compile(r"平时\s*(\d+)"),
    re.compile(r"第\s*(\d+)\s*周"),
    re.compile(r"周\s*(\d+)"),
]
# 宽松版：只判断"是不是带次数标记的列"
_TREND_LOOSE = re.compile(r"第\s*\d+\s*[次回]|平时|周\s*\d+|月考|周测|月度|单元测")

# 考试先后顺序：数字越大越靠后。用来决定「本次」与「上次」
EXAM_ORDER = [("期末", 30), ("期中", 20), ("月考", 10), ("单元", 5), ("周测", 1)]

MAX_HEADER_SCAN = 6      # 往下最多看几行找表头


# ---------------------------------------------------------------- 表头识别

def is_trend_header(header):
    """这个列名是不是带次数标记的平时/过程性成绩列。"""
    return bool(header) and bool(_TREND_LOOSE.search(str(header)))


def trend_order(header):
    """取出次数序号；取不到时返回 None。"""
    h = str(header or "")
    for pat in _TREND_PATTERNS:
        m = pat.search(h)
        if m:
            return int(m.group(1))
    return None


def _cells(row):
    return [("" if c is None else str(c).strip()) for c in row]


def _looks_numeric(cell):
    s = str(cell).strip().replace("%", "")
    if s == "":
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def _row_is_data(row):
    """整行以数字为主 → 是数据行，不是表头行。"""
    vals = [c for c in _cells(row) if c != ""]
    if not vals:
        return True
    return sum(1 for c in vals if _looks_numeric(c)) >= max(1, len(vals) * 0.5)


def detect_header(rows, max_scan=MAX_HEADER_SCAN):
    """定位表头。

    返回 (start, n_rows, note)：
      start  —— 表头第一行的下标（0 基），它之前的行都是标题行
      n_rows —— 表头占几行（1 = 单行；2 = 「第1次」跨列 + 学科名两行）
    """
    start, note = 0, ""
    for i, r in enumerate(rows[:max_scan]):
        vals = [v for v in _cells(r) if v != ""]
        if not vals:
            continue
        has_id = any(any(k in v for k in ID_KEYS) or any(k in v for k in NAME_KEYS)
                     for v in vals)
        n_subj = sum(1 for v in vals if subject_bases(v))
        if has_id or n_subj >= 2:
            start = i
            break
    else:
        note = "没找到明显的表头行，按第 1 行当表头处理"
        return 0, 1, note

    if start:
        note = "跳过了前 %d 行标题（第 %d 行才是表头）" % (start, start + 1)

    n_rows = 1
    nxt = rows[start + 1] if start + 1 < len(rows) else None
    if nxt is not None and not _row_is_data(nxt):
        vals = [v for v in _cells(nxt) if v != ""]
        nxt_id = any(any(k in v for k in ID_KEYS) or any(k in v for k in NAME_KEYS) for v in vals)
        nxt_subj = sum(1 for v in vals if subject_bases(v))
        # 第二行整个是学科名、既没有学号/姓名、也不是数据 → 判为双行表头
        if vals and not nxt_id and nxt_subj >= max(2, int(len(vals) * 0.6)):
            n_rows = 2
            note = (note + "；" if note else "") + "识别到双行表头（上格是次数/分组，下格是学科名，已拼成「第1次-数学」这类列名）"
    return start, n_rows, note


def _real_width(rows, block):
    """最后一个有内容的列（表头与数据一起看），用来砍掉尾部空列。"""
    last = -1
    for r in list(block) + list(rows):
        for i, c in enumerate(r):
            if c is not None and str(c).strip() != "":
                last = max(last, i)
    return last + 1


def _horiz_fill(row, width, limit):
    """横向合并单元格只把值留在左上角，这里把跨列的值补满。

    只补到 `limit`（表头块里最后一个有内容的列）为止——最后一块「第6次」的
    跨列范围可能比它自己的字更长，所以上界要由整个表头块来定，不能只看本行。
    """
    out, cur = [], ""
    for i in range(width):
        c = row[i] if i < len(row) else ""
        if c:
            cur = c
        out.append(cur if i <= limit else "")
    return out


def build_headers(block, total_rows):
    """把 1~2 行表头压成一行列名。"""
    width = _real_width(total_rows, block)
    grid = []
    for r in block:
        row = _cells(r)[:width]
        grid.append(row + [""] * (width - len(row)))

    if len(block) >= 2:
        limit = max([i for r in grid for i in range(width) if r[i]], default=width - 1)
        top = _horiz_fill(grid[0], width, limit)
        bot = grid[-1]
        headers = []
        for i in range(width):
            t, b = top[i], bot[i]
            if t and b and t != b and subject_bases(b):
                # 上格是次数/分组、下格是学科 → 拼起来，保留趋势信息
                headers.append("%s-%s" % (t, b))
            else:
                headers.append(b or t)
        return headers
    return grid[0] if grid else []


def read_workbook(path, sheets=None):
    """读一个 xlsx，返回 [{sheet, headers, rows, meta}, ...]。"""
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    names = list(sheets) if sheets else list(wb.sheetnames)
    out = []
    for name in names:
        if name not in wb.sheetnames:
            raise KeyError("没有名为「%s」的工作表；可用的有：%s"
                           % (name, "、".join(wb.sheetnames)))
        ws = wb[name]
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue
        start, n_rows, note = detect_header(rows)
        block = rows[start:start + n_rows]
        headers = build_headers(block, rows)
        body = []
        for r in rows[start + n_rows:]:
            r = list(r)
            if all(c is None or str(c).strip() == "" for c in r):
                continue
            if len(r) < len(headers):
                r = r + [None] * (len(headers) - len(r))
            body.append(r[:len(headers)])
        out.append({
            "sheet": name, "headers": headers, "rows": body,
            "meta": {"表头行": start + 1, "表头行数": n_rows, "数据行数": len(body),
                     "说明": note},
        })
    return out


# ---------------------------------------------------------------- 列分类

def split_columns(headers):
    """把列名分成 (本次学科列, 平时趋势列, 其他列)。"""
    plain, trend, other = [], [], []
    for i, h in enumerate(headers):
        if not h:
            continue
        if not subject_bases(h):
            other.append((i, h))
        elif is_trend_header(h):
            trend.append((i, h))
        else:
            plain.append((i, h))
    return plain, trend, other


def sheet_kind(headers):
    """scores = 本次成绩表；trend = 只有平时/过程性列；other = 都不像。"""
    plain, trend, _ = split_columns(headers)
    if plain:
        return "scores"
    if trend:
        return "trend"
    return "other"


def trend_columns(headers):
    """趋势列整理成 {学科本体: [(次序号, 列号, 原列名), ...]}，按次数排序。"""
    _, trend, _ = split_columns(headers)
    out = {}
    for i, h in trend:
        bases = subject_bases(h)
        if len(bases) != 1:
            continue                      # 一列同时命中多门课 → 不敢认，跳过
        base = canonical(list(bases)[0])
        order = trend_order(h)
        if order is None:
            order = len(out.get(base, [])) + 1
        out.setdefault(base, []).append((order, i, h))
    for base in out:
        out[base].sort(key=lambda x: (x[0], x[1]))
    return out


def exam_rank(sheet_name):
    """工作表名里体现的考试先后（越大越靠后）；看不出来给 None。"""
    for key, rank in EXAM_ORDER:
        if key in str(sheet_name):
            return rank
    return None


# ---------------------------------------------------------------- 工作表选路

def route_sheets(sheets, scores_sheet=None, trend_sheet=None, prev_sheet=None):
    """选出 (主成绩表, 上次对比表, 平时趋势表) 并给出每个自动决定的理由。

    规则（不猜：歧义一律报错，让用户用 --scores-sheet/--prev-sheet/--trend-sheet 指定）：
      · 主成绩表：按考试先后取**最靠后**的那张（期末 > 期中 > 月考 > 单元/周测）
      · 上次对比表：主表之前、顺序上最靠后的另一张成绩表
      · 平时趋势表：全簿里只有一张「全是平时/过程性列」的表时自动采用
      · 整簿一张成绩表都没有、但恰好有一张像名单/描述的表 → 把它当主表，
        走「只有名单、没有成绩数据」的降级路径（支持「只有教师描述」的用法）

    返回 (主表, 上次表, 平时表, 提示列表)；前三个都可能为 None（降级路径下主表非 None）。
    """
    by_name = {}
    for s in sheets:
        by_name[s["sheet"]] = s

    def find(name, label):
        if name and name not in by_name:
            raise KeyError("%s 指定的工作表「%s」不存在；实际有：%s"
                           % (label, name, "、".join(by_name)))
        return by_name.get(name)

    notices = []
    kinds = {s["sheet"]: sheet_kind(s["headers"]) for s in sheets}

    # ---- 主成绩表 ----
    if scores_sheet:
        main = find(scores_sheet, "--scores-sheet")
        notices.append("按 --scores-sheet 指定，本次成绩表取工作表「%s」" % main["sheet"])
    else:
        cands = [s for s in sheets if kinds[s["sheet"]] == "scores"]
        if not cands:
            # 「只有教师描述、没有统计表」的降级出口（SKILL 常见问题里给的就是这个用法）：
            # 整簿没有一张带学科成绩列的表，但有一张像名单/描述的表时，就把它当主表，
            # 按「只有名单、没有成绩数据」处理，而不是直接 LookupError 退出
            # （旧版在这里抛异常，导致该降级路径从未真正跑通）。
            others = [s for s in sheets if kinds[s["sheet"]] == "other"]
            if len(others) == 1:
                main = others[0]
                notices.append(
                    "这次给的材料里没有学科成绩列，只有「%s」一张像名单/描述的表；"
                    "已按「只有名单、没有成绩数据」处理——评语中不得出现任何数字，"
                    "只能用教师描述里的行为细节取材" % main["sheet"])
            else:
                raise LookupError(
                    "这次给的材料里没有一张能当「本次成绩表」的表（要有学号/姓名 + 学科成绩列）。\n"
                    "实际工作表与形态：%s\n"
                    "如果成绩分散在多张单科表里，请先用 --subjects/--sheet 明确指定，"
                    "或整理成一张宽表。\n"
                    "如果这份文件本来就没有成绩、只有教师描述，请让工作簿里**只留一张**"
                    "描述表（或多张表但只有一张是名单/描述表）再试。"
                    % "；".join("%s（%s）" % (k, {"scores": "成绩表", "trend": "平时/趋势表",
                                                "other": "看不出结构"}[v])
                              for k, v in kinds.items()))
        elif len(cands) == 1:
            main = cands[0]
            notices.append("本次成绩表自动取工作表「%s」（唯一一张成绩表）" % main["sheet"])
        else:
            ranked = [(exam_rank(s["sheet"]), s) for s in cands]
            known = [x for x in ranked if x[0] is not None]
            top = max((x[0] for x in known), default=None)
            winners = [s for r, s in ranked if r == top] if top is not None else []
            if len(winners) == 1:
                main = winners[0]
                notices.append(
                    "可用的表里有 %d 张成绩表（%s），按考试先后自动取最靠后的「%s」；"
                    "要用别的请加 --scores-sheet"
                    % (len(cands), "、".join(s["sheet"] for s in cands), main["sheet"]))
            else:
                raise LookupError(
                    "可用的表里有 %d 张成绩表（%s），无法判断哪张是本次成绩，"
                    "请用 --scores-sheet 指定其中一张。"
                    % (len(cands), "、".join(s["sheet"] for s in cands)))

    # ---- 上次对比表 ----
    prev = None
    if prev_sheet:
        prev = find(prev_sheet, "--prev-sheet")
        notices.append("按 --prev-sheet 指定，上次对比表取工作表「%s」" % prev["sheet"])
    elif not prev_sheet:
        my_rank = exam_rank(main["sheet"])
        if my_rank is not None:
            earlier = [s for s in sheets
                       if s["sheet"] != main["sheet"] and kinds[s["sheet"]] == "scores"
                       and exam_rank(s["sheet"]) is not None
                       and exam_rank(s["sheet"]) < my_rank]
            if earlier:
                prev = max(earlier, key=lambda s: exam_rank(s["sheet"]))
                notices.append(
                    "上次对比自动取工作表「%s」（在「%s」之前的最近一次考试）——"
                    "用于生成「总分变化」「排名变化」"
                    % (prev["sheet"], main["sheet"]))

    # ---- 平时趋势表 ----
    trend = None
    if trend_sheet:
        trend = find(trend_sheet, "--trend-sheet")
        notices.append("按 --trend-sheet 指定，平时趋势表取工作表「%s」" % trend["sheet"])
    else:
        cands = [s for s in sheets if kinds[s["sheet"]] == "trend"]
        if len(cands) == 1:
            trend = cands[0]
            notices.append(
                "平时/过程性成绩自动取工作表「%s」——按你的口径**保留逐次序列、不取均值**，"
                "评语应**按标准式**引用（「学科+第X次平时成绩NN分」，"
                "如「语文从第一次平时成绩74分提升到第六次平时成绩的87分」），"
                "而不是一个平均分" % trend["sheet"])
        elif len(cands) > 1:
            notices.append("可用的表里有 %d 张平时/趋势表（%s），未自动采用，"
                           "需要时用 --trend-sheet 指定一张"
                           % (len(cands), "、".join(s["sheet"] for s in cands)))
    return main, prev, trend, notices
