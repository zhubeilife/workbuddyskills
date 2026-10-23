# -*- coding: utf-8 -*-
"""【第一段 材料对齐】把六类材料合并成每个学生的「画像底稿」roster.json。

做三件事：
  1. 自动识别各表列义（学号/姓名/性别/学科/排名/总分/作业指标/课堂指标）
  2. 按主键合并；**不猜**，所有异常进「对齐说明」
  3. 为每个学生生成材料完整度、学科强弱、趋势变化、分层建议（机器建议，供 AI 修正）

六类材料 = 成绩表（必需）+ 作业表 + 课堂表 + 教师个别描述表 + **往年评语表** + **荣誉材料表**。
「往年评语」是上学期/往年写过的评语，作用**相当于教师对学生的个性化描述**——
成文阶段拿它找"这个人身上稳定的、只属于他的特点"，保持与过去期待的连贯；
但它只是**参考**，不是本学期的事实证据（详见 references/writing-rules.md 规则 5）。
「荣誉材料」（奖状 / 证书 / 荣誉榜，常见形态是用户拍的照片或截图）落进 `荣誉奖项`，
它是**可以直接引用的证据**——也是「竞赛获奖 / 担任职务」这类内容能合法进评语的唯一来源。
以上两张表都与教师个别描述表走**同一条**匹配链路（都由 NameMatcher 执行），只是落进不同字段。

**图片不是第七类材料，而是"把材料录进来"的一种通道**：成绩截图、奖状照片、手写描述照片
都要先由 AI 读图转写成一份标准表（xlsx/csv），再走本脚本。转写口径见
references/image-intake.md；把图片直接传给本脚本会被**友好拒绝**（不会抛 openpyxl 的怪错）。

成绩册的四种"脏"结构都能直接吃（见 read_workbook.py）：
  · 第 1 行是合并的大标题 → 自动跳过，定位真表头
  · 双行表头（「第1次」横向跨 7 科 + 下一行学科名）→ 拼成「第1次-数学」
  · 一个工作簿多张表（平时成绩 / 期中考试成绩 / 期末考试成绩）→ 按考试先后自动分流：
    最靠后的一次当「本次成绩」，之前最近一次当「上次对比」，全是第N次的表当「平时趋势」
  · **成绩分在多个文件里**（期末、期中、平时各存一个 xlsx，很常见；且每个文件的
    工作表名往往都是「Sheet1」）→ 多个路径一起传给 `--scores` 即可，脚本按**文件名**
    当标签合并成一份逻辑清单再选路。旧版只吃一个文件 → 传期末表时不报错，
    但期中进退与平时序列这两份最有价值的证据**根本没进流程**

平时/过程性成绩**保留逐次序列、不取均值**（用户口径）：均值会把
「第一次平时成绩96分、第五次又落回70分」这类最有价值的波动抹平，而这条序列正是
「学习习惯」维度唯一真实的证据源。

主键规则（决定「谁是这个人」，按优先级从高到低）：
  1. 成绩表有学号列、且至少一行有值 → 主键 = 学号；姓名并存，**学号与姓名一起参与匹配校验**
  2. 成绩表没有学号列，或该列整列为空 → 忽略学号，主键 = 姓名
  3. 无学号且同名学生 → 按在成绩表里的出现顺序编号：排在前面的为「张三1号」，后面的为「张三2号」

四条不可松动的底线（都是为了不把材料挂到别人头上）：
  · 名单里有学号时，学号不在名单内一律判「名单外」，不用姓名兜底
  · 成绩表同一个学号出现两次 → 直接报错停止，绝不静默取一条
  · 有学号列却有人没填学号 → 直接报错，绝不混用「学号 / 姓名」两种主键
  · 主键一旦定下就是全局唯一标识，附表的匹配口径与之一致
  · 传了路径但文件不存在 → 直接报错，不静默跳过（否则小贴士会误报成「你没提供材料」）

另有两类「不是学生」的行会被剔掉：底部统计行（「班级平均」「年级最高」）与空行。

用法：
  # 单表
  python prepare_roster.py --scores 示例_成绩表.xlsx --out roster.json
  # 多工作表成绩册（平时 + 期中 + 期末），自动选本次/上次/平时趋势
  python prepare_roster.py --scores 初一3班成绩表.xlsx --class-name "初一3班" \
    --exam-name "初一上学期期末考试" --out roster.json
  # 指定工作表（歧义时脚本会报错并列出可选值）
  python prepare_roster.py --scores 成绩册.xlsx --scores-sheet 期末考试成绩 \
    --prev-sheet 期中考试成绩 --trend-sheet 平时成绩 --out roster.json
  # 期末 / 期中 / 平时是三个独立文件 → 一起传（不用先手工合并成一个工作簿）
  python prepare_roster.py --scores 期末考试成绩.xlsx 期中考试成绩.xlsx 平时成绩.xlsx \
    --out roster.json
  # 有往年（上学期）评语时一起传 —— 它会作为个性化描述的参考并进 roster.json 的「往年评语」
  python prepare_roster.py --scores 成绩表.xlsx --notes 教师描述.xlsx \
    --past-comments 上学期期末评语.xlsx --out roster.json
  # 有奖状 / 证书 / 荣誉榜时一起传 —— 进「荣誉奖项」，是可引用的证据（图片请先读图转写成表）
  python prepare_roster.py --scores 成绩表.xlsx --awards 奖状荣誉清单.csv --out roster.json
"""
import argparse
import csv
import difflib
import json
import os
import re
import sys
from collections import Counter, OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from subjects import (SUBJECT_ALIAS, SUBJECT_POOL, canonical, has_subject_word,
                      subject_bases)  # noqa: E402  学科词表与同义归一的唯一来源
from read_workbook import (is_trend_header, read_workbook, route_sheets,
                           sheet_kind, split_columns, trend_columns)  # noqa: E402  表头/工作表解析

# 历史成绩列的标记词：这些列不参与本次学科统计，避免「期中语文」被当成第二门语文
HIST_MARKERS = ["期中", "上次", "历次", "上学期", "上期", "前次"]

ID_KEYS = ["学号", "考号", "编号", "学籍号", "学生编号"]
NAME_KEYS = ["姓名", "学生姓名", "名字"]
SEX_KEYS = ["性别"]
TOTAL_KEYS = ["总分", "总成绩"]
# 排名类关键词**按这里的前后顺序**取用（见 find_col：外层遍历关键词、内层遍历表头）。
# 「班级排名」写在前面才会真正优先——旧版是「表头顺序先命中先赢」，
# 表头写「…年级排名 班级排名」时先扫到的「年级排名」会赢，班级排名被取成年级排名。
RANK_KEYS = ["班级排名", "班内排名", "班级名次", "班名次", "排名", "名次"]
# 年级/校排名单独一组：它只能当提示，**绝不能当班级排名用**——
# 拿年级排名去做排名分位与排名变化，整个班的分层会整体错位。
GRADE_RANK_KEYS = ["年级排名", "年级名次", "年级位次", "校排名", "校级排名", "全校排名"]

# 成绩表底部的统计行（不是学生）：姓名列写成「班级平均」「年级最高」这类。
STAT_NAME_RE = re.compile(
    r"平均|均分|小计|合计|总计|最高|最低|及格率|优秀率|达标率|班均|年级均|班级均|全班|统计|汇总")

HOMEWORK_FIELDS = OrderedDict([
    ("应交次数", ["应交", "应完成"]),
    ("实交次数", ["实交", "已交"]),
    ("提交率", ["提交率", "交作业率"]),
    ("按时提交率", ["按时", "准时"]),
    ("订正完成率", ["订正"]),
    ("作业质量等级", ["质量等级", "等级", "等级评价"]),
    ("作业备注", ["备注", "说明"]),
])
CLASSROOM_FIELDS = OrderedDict([
    ("发言次数", ["发言", "举手"]),
    ("专注度", ["专注"]),
    ("小组合作", ["合作", "协作"]),
    ("课堂纪律", ["纪律", "守纪"]),
    ("课堂任务完成率", ["任务完成", "完成率"]),
])

# 「主键 + 一段长文本」类附表（教师个别描述 / 往年评语 / 荣誉材料）的文本列名关键词。
# 三张表走**同一个** ingest_text_table()，差别只有落进哪个字段。
#   教师个别描述 —— 本学期、班主任或科任写的观察，是**本周期的证据**
#   往年评语     —— 上学期/往年写过的评语，是**参考**（个性化描述的替代来源），
#                   不是本学期的事实证据，成文时不得照搬（见 writing-rules 规则 5）
#   荣誉奖项     —— 奖状/证书/荣誉榜，是**可直接引用的证据**；也是"竞赛获奖/担任职务"
#                   能合法进评语的唯一来源（规则 2 对它有例外）
NOTE_TEXT_KEYS = ["教师描述", "描述", "观察", "表现", "备注", "情况", "评语"]
PAST_TEXT_KEYS = ["往年评语", "上学期评语", "上期评语", "期末评语", "教师评语",
                  "班主任评语", "综合评语", "评语", "寄语", "评价"]
AWARD_TEXT_KEYS = ["荣誉奖项", "荣誉", "奖项", "获奖", "奖状", "证书", "称号",
                   "表彰", "奖励", "所获荣誉"]

# 图片 / PDF —— 脚本不吃图（没有 OCR，也不该猜）。用户传图时给明确指引，
# 而不是让 openpyxl 抛 "not a zip file" 这种用户看不懂的错。
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".heic", ".heif",
              ".tif", ".tiff", ".svg", ".pdf")


def reject_image(path, label="材料"):
    """图片/PDF 不是脚本能读的表：友好拒绝，并把「先读图转写成表」的口径讲清楚。"""
    ext = os.path.splitext(str(path))[1].lower()
    if ext not in IMAGE_EXTS:
        return
    sys.exit(
        "%s不是表格文件（%s 是图片/PDF），本脚本不能直接读图：%s\n"
        "请先由 AI 读图转写成一份标准表，再传给本脚本（口径见 references/image-intake.md）：\n"
        "  · 成绩表截图 / 统计截图 → 转写为 xlsx 或 csv，列名照原表写（学号/姓名/各科/总分/排名）\n"
        "  · 奖状 / 证书 / 荣誉榜   → 转写为「学号|姓名|荣誉奖项」三列，一条一行，"
        "级别与时间并入奖项文本（如「校级三好学生（校级，2026年6月）」）\n"
        "  · 教师手写描述照片       → 转写为「学号|姓名|教师描述」三列\n"
        "  · 成绩趋势图（柱状/折线）→ 只转写图上**明确标注**的数字，没标注的一律留空\n"
        "⚠ 转写完成后必须先回读给用户核对（姓名与数字最容易读错），确认后再跑本脚本。"
        % (label, ext, path))


def norm_name(s):
    """姓名归一化：去空格、全角转半角空白、去括号备注。"""
    if s is None:
        return ""
    s = str(s)
    s = s.replace("\u3000", "").replace(" ", "").replace("\t", "")
    s = re.sub(r"[（(].*?[)）]", "", s)
    return s.strip()


def norm_id(s):
    """学号归一化：只去掉「数字被读成浮点」带来的尾巴 `.0`。

    旧版是无差别 `replace(".0", "")`，于是学号 `1.05` 变成 `15`、`20240.05` 变成
    `202405`——两串不一样的学号会被改成同一个，静默串人。这里改成只认「整数 + 全零小数尾」。
    """
    if s is None:
        return ""
    t = str(s).strip()
    if re.fullmatch(r"[+-]?\d+\.0+", t):
        t = t.split(".")[0]
    return t


def is_stat_row(sid, nm):
    """这一行是不是成绩/附表底部的统计行（「班级平均」「年级最高」）。

    统计行必须挡在学生名单之外——否则「班级平均」会变成一个「学生」，
    要给他写评语，写不出就报「漏写」硬错误。
    只在**没有学号且姓名命中统计词**时才判（有学号的永远是学生）。
    """
    return (not sid) and bool(nm) and bool(STAT_NAME_RE.search(nm))


def read_table(path, sheet=None):
    """读一张表，返回 (headers, rows, meta)。

    真正的解析在 read_workbook.py 里，它会：
      · 跳过表头之上的大标题行（合并单元格那种）
      · 认出双行表头并把「第1次 + 数学」拼成「第1次-数学」
      · 按 `sheet` 指定工作表；不指定时取**最适合当数据表的那张**
    支持 .xlsx/.xls(友好拒绝)/.csv；图片与 PDF 也**友好拒绝**（提示先读图转写成表）。

    多工作表时不再死认第一张：附表（作业/课堂/描述）也常常一个文件里放了几张表，
    第一张可能是封面或说明页。这里挑「有姓名/学号列、数据行最多」的那张，
    并把改选写进 meta 的「多表提示」，由调用方讲给用户听。
    """
    reject_image(path, "这张表")
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".txt"):
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            data = list(csv.reader(f))
        if not data:
            return [], [], {"sheet": "(csv)", "说明": "空文件"}
        headers = [c.strip() for c in data[0]]
        rows = [list(r) + [None] * (len(headers) - len(r)) for r in data[1:]]
        return (headers, rows,
                {"sheet": "(csv)", "表头行": 1, "表头行数": 1,
                 "数据行数": len(rows), "说明": "csv：第 1 行即表头"})
    if ext == ".xls":
        sys.exit("旧版 .xls 不被支持，请先另存为 .xlsx 或 .csv：" + path)
    try:
        from openpyxl import load_workbook  # noqa: F401
    except ImportError:
        sys.exit("读取 .xlsx 需要 openpyxl：pip install openpyxl")
    sheets = read_workbook(path, [sheet] if sheet else None)
    if not sheets:
        return [], [], {"sheet": sheet or "(首表)", "说明": "空表"}

    if sheet is None and len(sheets) > 1:
        def _score(s):
            hs = s["headers"]
            key_hit = 1 if any(
                h and (any(k in h for k in ID_KEYS) or any(k in h for k in NAME_KEYS))
                for h in hs) else 0
            return (key_hit, s["meta"].get("数据行数", 0))
        best = max(sheets, key=_score)
    else:
        best = sheets[0]

    meta = dict(best["meta"])
    if best["sheet"] != sheets[0]["sheet"]:
        meta["多表提示"] = (
            "这个文件有 %d 张工作表，已改选「%s」（含姓名/学号列、数据行最多），"
            "而不是第一张「%s」；若选错了请把要用的那张单独存一个文件"
            % (len(sheets), best["sheet"], sheets[0]["sheet"]))
    return best["headers"], best["rows"], meta


# 「Sheet1」「工作表1」这类通用工作表名——不含任何考试信息，跨文件时会撞成一堆同名表
GENERIC_SHEET_RE = re.compile(r"^(?:sheet|工作表|数据|明细|列表|table|list|新建)\s*\d*$",
                              re.IGNORECASE)
# 文件名里出现这些词，就"像"一份成绩材料（用于提醒用户"同目录还有别的"）
SCORES_NAME_HINT_RE = re.compile(r"期中|期末|月考|单元|周测|平时|成绩|分数")


def load_scores_sources(paths, notices=None):
    """把 1~N 个成绩文件读成**一份合并的工作表清单**，交给 route_sheets 选路。

    为什么允许多文件：期末 / 期中 / 平时常常是三个独立文件（本项目实测数据就是这样），
    而每个文件的工作表名往往都叫「Sheet1」。旧版 `--scores` 只吃一个文件，于是：

      · 传期末表 → 期中对比与平时序列**根本没进流程**（不报错、不提示，只是安静地不存在，
        这两份恰好是最有价值的证据：一个是进退趋势，一个是学习习惯）
      · 想带上它们 → 只能自己写脚本先合成一个工作簿（技能用户不该被要求做这件事）

    这里按**文件名**给通用名的表贴标签（「初一3班期末考试成绩」），选路才能看出考试先后
    （否则期末/期中/平时全叫 Sheet1，route_sheets 会直接报「名字看不出先后」）。
    标签规则：工作表名有意义就用它；是通用名就用文件名（一个文件多张通用名表则加表名后缀）。
    """
    out = []
    for p in paths:
        reject_image(p, "成绩表")
        ext = os.path.splitext(p)[1].lower()
        if ext in (".csv", ".txt", ".xls"):
            # .csv 直接用；.xls 由 read_table 友好拒绝并给提示
            headers, rows, meta = read_table(p)
            if not headers:
                sys.exit("成绩表为空：" + p)
            sheets = [{"sheet": meta.get("sheet", "(csv)"), "headers": headers,
                       "rows": [list(r) + [None] * (len(headers) - len(r)) for r in rows],
                       "meta": meta}]
        else:
            sheets = read_workbook(p)
        if not sheets:
            sys.exit("成绩表为空：" + p)
        stem = os.path.splitext(os.path.basename(p))[0]
        for s in sheets:
            s["source"] = os.path.basename(p)
            nm = str(s.get("sheet") or "")
            if GENERIC_SHEET_RE.match(nm):
                s["sheet"] = stem if len(sheets) == 1 else "%s·%s" % (stem, nm)
        out.extend(sheets)

    # 跨文件重名 → 加序号，保证标签唯一（否则 --scores-sheet 指不准）
    used, renamed = {}, []
    for s in out:
        base, lab, i = s["sheet"], s["sheet"], 2
        while lab in used:
            lab, i = "%s(%d)" % (base, i), i + 1
        if lab != base:
            renamed.append("%s → %s（与前面的表重名）" % (base, lab))
        used[lab] = True
        s["sheet"] = lab
    if renamed and notices is not None:
        notices.append("这些表重名了，已加序号区分：%s" % "、".join(renamed))
    return out


def sibling_scores_hint(paths):
    """只传了**一个**成绩文件时，提醒同目录下还有别的「像成绩表」的文件。

    这是本项目最容易踩、也最贵的一个坑：期末 / 期中 / 平时是三份独立文件，
    而只传期末表**不会报错**——期中进退与平时序列安静地缺席，评语就只能写
    「成绩稳定」这种没有证据的套话，用户还不知道为什么。
    脚本没法替用户决定「旁边那份文件是不是同一次对齐要用的」，所以只提醒、不阻断。
    """
    if len(paths) != 1:
        return []
    d = os.path.dirname(os.path.abspath(paths[0]))
    given = os.path.basename(paths[0])
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return []
    sibs = [n for n in names
            if n != given and not n.startswith("~$")
            and n.lower().endswith((".xlsx", ".xls", ".csv"))
            and SCORES_NAME_HINT_RE.search(n)]
    if not sibs:
        return []
    return ["⚠ 只传了一个成绩文件，但同目录下还有这些文件名里带考试/成绩字样的表格：%s。"
            "如果它们属于**同一次对齐**（期末/期中/平时各存一个文件是最常见的形态），"
            "请一起传给 --scores；否则「期中进退」与「平时序列」这两个维度会整体缺席，"
            "例：--scores \"%s\" \"%s\""
            % ("、".join(sibs), given, os.path.join(d, sibs[0]))]


def find_col(headers, keys, exclude=()):
    """找列：**外层遍历关键词、内层遍历表头**（关键词优先级 > 表头顺序）。

    ⚠️ 这个顺序不是随便定的。旧版是「表头顺序先命中先赢」，于是
    `RANK_KEYS` 里「班级排名」写在「年级排名」前面完全不起作用；
    `ID_KEYS` 里「学号」写在「考号」前面也不起作用。
    改成关键词优先后，两处优先级才真正生效。
    """
    for k in keys:
        for i, h in enumerate(headers):
            if i in exclude:
                continue
            if h and k in h:
                return i
    return None


def find_col_exact_first(headers, keys, exclude=()):
    """先精确命中（列名整体等于某个关键词），再退回关键词优先的模糊包含。

    避免「语文总分」抢在「总分」前面被当成总分列——那样会把语文成绩也算丢。
    """
    for i, h in enumerate(headers):
        if i not in exclude and h in keys:
            return i
    return find_col(headers, keys, exclude)


def build_keys(rows, i_id, i_name):
    """按主键规则为成绩表每一行算出主键。

    规则（与模块 docstring 一致）：
      1. 学号列存在且至少一行有值 → 该行主键 = 学号
      2. 无学号列 / 整列为空 / 该行学号为空 → 主键 = 姓名
      3. 走姓名主键的同一姓名出现多次 → 按出现顺序编「姓名1号」「姓名2号」

    另外挡掉两类「不是学生」的行：
      · 底部统计行（「班级平均」「年级最高」，学号空 + 姓名命中统计词）
      · 空行

    返回 (pairs, id_col_live, notes, missing_id)：
      pairs —— 与 rows 等长，元素为 (主键, 主键来源)；既无学号也无姓名的行给 (None, None)
      id_col_live —— 学号列是否真的可用（存在且非全空）
      notes —— 需要向上汇报的提示
      missing_id —— 学号列可用、但这些行**没填学号**（由调用方决定是否中止：
                   混用「学号 / 姓名」两种主键会让整表口径漂移）
    """
    raw, stat_rows = [], []
    for r in rows:
        sid = norm_id(r[i_id]) if (i_id is not None and i_id < len(r)) else ""
        nm = norm_name(r[i_name]) if (i_name is not None and i_name < len(r)) else ""
        if is_stat_row(sid, nm):
            stat_rows.append(nm)
            raw.append((None, None))
            continue
        raw.append((sid, nm))

    id_col_live = any(sid for sid, _ in raw)

    # 只对「真正要走姓名主键」的人统计重名——有学号的人不参与编号
    name_total = Counter(nm for sid, nm in raw
                         if nm and not (id_col_live and sid))

    seen = Counter()
    pairs, numbered = [], []
    for sid, nm in raw:
        if not sid and not nm:
            pairs.append((None, None))
            continue
        if id_col_live and sid:
            pairs.append((sid, "学号"))          # 学号为主键，姓名并存一起匹配
            continue
        seen[nm] += 1
        if name_total[nm] > 1:
            key, src = "%s%d号" % (nm, seen[nm]), "姓名序号"
            numbered.append(key)
        else:
            key, src = nm, "姓名"
        pairs.append((key, src))

    notes = []
    if stat_rows:
        notes.append("成绩表底部这些行看起来是统计行（不是学生），已剔除、不计入名单：%s"
                     % "、".join(dict.fromkeys(stat_rows)))
    if numbered:
        notes.append("成绩表里有同名学生，已按出现顺序编号：%s —— "
                     "这些人的附表中若没有学号，将按出现顺序对应，务必人工核对"
                     % "、".join(numbered))
    missing_id = list(dict.fromkeys(nm for sid, nm in raw
                                    if id_col_live and not sid and nm))
    return pairs, id_col_live, notes, missing_id


class NameMatcher:
    """统一的跨表匹配口径。

    · 名单里有学号 → 附表也必须用学号对；学号不在名单内一律判「名单外」，不用姓名兜底
    · 名单本身没有学号（以姓名为主键）→ 附表带学号也对不上，退回按姓名匹配
    · 同名多人 → 按该附表内的出现顺序依次对应名单里的第 1 号、第 2 号，并提示人工核对
    """

    def __init__(self, students):
        self.students = students
        self.by_name = OrderedDict()
        for k, v in students.items():
            if v["姓名"]:
                self.by_name.setdefault(v["姓名"], []).append(k)
        self.has_id = any(v.get("主键来源") == "学号" for v in students.values())
        self.seen = Counter()
        self.order_hit = set()

    def new_table(self):
        """每换一张附表调用一次：重置「同名第几次出现」的计数。"""
        self.seen.clear()
        self.order_hit.clear()

    def match(self, sid, nm):
        """返回 (命中的主键, 失败原因)；失败原因非空即视为「未匹配/名单外」。"""
        if sid and sid in self.students:
            return sid, ""
        if sid and self.has_id:
            return "", "学号不在名单内（名单外学生或学号录入错误）"
        if not nm:
            if sid:
                return "", "学号不在名单内，且本行没有姓名，无法对应到名单"
            return "", "本行既无学号也无姓名"
        keys = self.by_name.get(nm)
        if not keys:
            return "", "姓名无法匹配到名单"
        if len(keys) == 1:
            return keys[0], ""
        # 同名多人：按本表出现顺序对应（第 1 次出现的 → 第 1 号）
        self.seen[nm] += 1
        i = self.seen[nm] - 1
        if i >= len(keys):
            return "", ("重名（%s）在本表已出现 %d 次，名单里只有 %d 位，"
                        "超出部分无法对应，请补学号" % (nm, self.seen[nm], len(keys)))
        self.order_hit.add(nm)
        return keys[i], ""


def to_num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("%", "")
    if s == "" or s in ("-", "—", "缺考", "缺"):
        return None
    try:
        f = float(s)
    except ValueError:
        return None
    return f


def pct(v):
    """把 0.93 / 93 / 93% 统一成 0.93"""
    n = to_num(v)
    if n is None:
        return None
    if n > 1.5:
        n = n / 100.0
    return round(n, 4)


def col_profile(headers, rows, h):
    """一列的画像：(能解析成数字的个数, 非空单元格数, 总行数)。

    用来区分三种「不是成绩」的列：
      · 有内容但一个数字都解析不出 → 文本等级列（「语文等级」A/B/C）
      · 整列空白 → 忽略
      · 有数字但人数明显偏少 → 选考/走班科目（要保留，不能丢）
    """
    ci = headers.index(h)
    blank = {"", "-", "—", "缺", "缺考", "无", "未考", "／", "/"}
    vals = [r[ci] if ci < len(r) else None for r in rows]
    nonempty = [v for v in vals if v is not None and str(v).strip() not in blank]
    got = sum(1 for v in nonempty if to_num(v) is not None)
    return got, len(nonempty), len(rows)


def detect_subjects(headers, rows, exclude, explicit):
    """识别学科列。返回 (学科列名列表, 提示列表, 选考科目集合)。

    白名单优先：只要列名**含学科名**就算学科列——「语文」「语文成绩」
    「期末语文」「语文(150分)」都能命中。
    绝不再按「列名含期末/期中就排除」来判断，那会把最常见的
    「期末语文」这类列名整列误杀。

    三条保护：
      1. 含「期中/上次/历次」的历史列不进本次学科（跨期对比请用「期中总分」列）
      2. 整列是文本等级的列（「语文等级」A/B/C）被丢弃——否则全班会被误判成缺考
      3. 有分数但人数明显偏少的列**保留**（可能是选考/走班科目），只提示不丢列

    第 3 条是必须的：新中考/新高考选考科目、走班制班级（物理/历史二选一）时，
    某科往往只有一半人考。旧版把「不足 50% 有分数」一律当等级列丢掉，
    于是物理整科消失、那 18 人反被判「缺考物理」，还会把用户引去查一个
    根本不存在的「等级列」问题。

    同义写法（「道法」＝「道德与法治」）按学科本体归一后再判断，
    所以「期中道德与法治」不会被当成一门新学科救回来，
    「道法」与「道德与法治」两列并存时也只取一处。
    """
    notes = []
    if explicit:
        # 兼容两种入参：命令行传来的逗号分隔字符串（主路径），或已经切好的列表。
        # 早先直接对字符串做 for 会按「字符」遍历，把「语文,数学」拆成
        # 「语」「文」「,」「数」「学」，导致 --subjects 一传就报「列找不到」。
        if isinstance(explicit, str):
            explicit = explicit.split(",")
        want = [s.strip() for s in explicit if s and s.strip()]
        resolved, missing = [], []
        for w in want:
            if w in headers:
                resolved.append(w)
                continue
            hit = next((h for h in headers if h and subject_bases(h) & subject_bases(w)), None)
            if hit:
                resolved.append(hit)
                notes.append("--subjects 指定的「%s」在表里叫「%s」（同学科的不同写法），已按该列取用"
                             % (w, hit))
            else:
                missing.append(w)
        if missing:
            sys.exit("--subjects 指定的列在成绩表中找不到：%s\n该表实际列名：%s"
                     % ("、".join(missing), "、".join(h for h in headers if h)))
        return resolved, notes, set()

    excluded = set(exclude)
    for i, h in enumerate(headers):
        if not h:
            continue
        if any(k in h for k in TOTAL_KEYS) or any(k in h for k in RANK_KEYS) \
                or any(k in h for k in GRADE_RANK_KEYS):
            excluded.add(i)

    cand = [h for i, h in enumerate(headers)
            if i not in excluded and h and has_subject_word(h)]
    # 平时/过程性成绩列（「第1次-数学」「平时3-语文」）不进本次学科统计——
    # 否则同一门课会被第 1 次、第 2 次…第 6 次算成六门，班均直接失真。
    # 它们由 step「平时趋势」单独整理成逐次序列。
    trend_like = [h for h in cand if is_trend_header(h)]
    if trend_like:
        cand = [h for h in cand if h not in trend_like]
        notes.append("这些列是平时/过程性成绩（带次数标记），不进本次学科统计、"
                     "已单独整理为「平时趋势」：共 %d 列（如 %s）"
                     % (len(trend_like), "、".join(trend_like[:3])))
    hist = [h for h in cand if any(m in h for m in HIST_MARKERS)]
    cur = [h for h in cand if h not in hist]

    def classify(cols):
        num, text, empty, thin = [], [], [], []
        for h in cols:
            got, nonempty, total = col_profile(headers, rows, h)
            if got == 0:
                (text if nonempty else empty).append(h)
            else:
                num.append(h)
                if got < max(1, total * 0.5):
                    thin.append((h, got, total))
        return num, text, empty, thin

    # 先按「有没有分数」把列分开，再在**有分数的列**里做同门去重。
    # 顺序很重要：旧版先做同门去重，于是「语文等级」A/B/C 被判成「语文」的
    # 另一种写法剔除，文案还说成"同一门课的另一种写法"——原因完全指错。
    cur_num, text_cols, empty_cols, sparse = classify(cur)

    # 同一门课的多种写法（「道法」与「道德与法治」）同时出现时只保留第一列，
    # 否则同一门课会被算两次，班均、学科偏差、总分全部失真。
    seen_subj, cur_dedup, dup_cols = {}, [], []
    for h in cur_num:
        dup_of = next((seen_subj[c] for c in subject_bases(h) if c in seen_subj), None)
        if dup_of and dup_of != h:
            dup_cols.append("%s（同「%s」，同一门课的另一种写法）" % (h, dup_of))
            continue
        cur_dedup.append(h)
        for c in subject_bases(h):
            seen_subj.setdefault(c, h)
    if dup_cols:
        notes.append("这些列与前面的列其实是同一门课，已只取前一处、剔除重复列：%s"
                     % "、".join(dup_cols))
    cur = cur_dedup

    if hist:
        cur_bases = set()
        for h in cur:
            cur_bases.update(subject_bases(h))
        rescued = []
        for h in hist:
            if not (subject_bases(h) - cur_bases):
                continue
            got, nonempty, total = col_profile(headers, rows, h)
            if got == 0:
                (text_cols if nonempty else empty_cols).append(h)
                continue
            cur.append(h)
            rescued.append(h)
            if got < max(1, total * 0.5):
                sparse.append((h, got, total))
        if rescued:
            notes.append("这些列含「期中/上次」但本次没有对应列，已按本次成绩使用：%s"
                         % "、".join(rescued))
        rest = [h for h in hist if h not in rescued]
        if rest:
            notes.append("检测到历史成绩列：%s —— 本次学科只用当前列；"
                         "如需进退趋势分析，请把跨期对比列命名为「期中总分」「期中排名」"
                         % "、".join(rest))

    if sparse:
        notes.append(
            "这些学科只有部分学生有成绩，**已保留**（不再整列丢弃）：%s —— "
            "多半是选考/走班科目：未选考的同学不计该科缺考、该科也不计入总分，"
            "该科班均只按有成绩的同学算；评语里不要给未选考的同学写该科"
            % "、".join("%s（%d/%d 人）" % (name, g, t) for name, g, t in sparse))
    if text_cols:
        notes.append("这些列名里有学科词，但整列是文本等级（A/B/C 等第，解析不出分数），"
                     "已不作为学科：%s" % "、".join(text_cols))
    if empty_cols:
        notes.append("这些列名里有学科词，但整列是空的，已忽略：%s" % "、".join(empty_cols))
    return cur, notes, set(name for name, _g, _t in sparse)


def ingest_text_table(path, field, text_keys, col_override, label, students, matcher,
                      name2sid, ambig_names, notes_report, miss_is_gap=True):
    """把一张「主键 + 一段长文本」的表并进 `students[*][field]`，返回命中行数。

    服务三类材料：**教师个别描述**（field="教师描述"）、**往年评语**（field="往年评语"）、
    **荣誉材料**（field="荣誉奖项"）。
    三者的匹配口径必须**逐字相同**——都由 NameMatcher 执行，学号优先、名单外不兜底。
    这段逻辑原先只写在教师描述表那一段里；新增往年评语时若另抄一份，
    两条链路的匹配口径迟早会漂移（subject 词表就是这么踩过一次的坑），
    所以收敛成这一个函数——**口径只有一处**。

    label 只用于提示文案（「教师描述表」/「往年评语表」/「荣誉材料表」），不影响匹配行为。

    miss_is_gap：**没有该字段的人要不要记「缺失项」**。
      教师描述、往年评语 → True（这两类本来就该覆盖全班，缺人是材料没给全）；
      荣誉材料 → **False**：荣誉不是人人都有，未覆盖**不是缺失**。
      旧版把荣誉也当缺失时，40 人示例里 23 人被记「缺 荣誉奖项」、控制台刷了 23 行——
      噪声会淹没真正该看的缺失项（作业/课堂缺人），所以单列一个开关。
    """
    if not path or not os.path.exists(path):
        return 0
    nh, nrows, nm_meta = read_table(path)
    if nm_meta.get("多表提示"):
        notes_report["机器提示"].append("%s：%s" % (label, nm_meta["多表提示"]))
    n_id, n_name = find_col(nh, ID_KEYS), find_col(nh, NAME_KEYS)
    if col_override:
        n_text = find_col(nh, [col_override])
    else:
        n_text = find_col(nh, text_keys)
    if n_text is None:
        widths = []
        for i, h in enumerate(nh):
            if i in (n_id, n_name) or h == "":
                continue
            w = max([len(str(r[i])) for r in nrows if i < len(r) and r[i]] or [0])
            widths.append((w, i))
        if widths:
            n_text = max(widths)[1]
    hit, unmatched, conflict, suspect = 0, [], [], []
    matcher.new_table()
    for r in nrows:
        sid = norm_id(r[n_id]) if n_id is not None else ""
        nm = norm_name(r[n_name]) if n_name is not None else ""
        text = ("" if n_text is None or r[n_text] is None else str(r[n_text]).strip())
        if not text or is_stat_row(sid, nm):
            continue
        # 主键策略（与作业表/课堂表完全一致，见 NameMatcher）：名单里有学号就以学号为准，
        # 学号不在名单内 → 直接判名单外，不用姓名兜底；名单本身没有学号时才按姓名接
        key, why = matcher.match(sid, nm)
        if not key and not sid and nm:
            # 仅当整个表都没有学号时才尝试姓名近似，且要求等长 + 高相似 + 不是重名
            cand = [c for c in difflib.get_close_matches(
                nm, list(name2sid.keys()), n=1, cutoff=0.8)
                if len(c) == len(nm) and c not in ambig_names]
            if cand:
                key = name2sid[cand[0]]
                why = ""
                suspect.append({"学号": key, "名单姓名": cand[0], "描述表姓名": nm,
                                "处理": "已暂按同一人合并，请人工确认"})
        if not key:
            unmatched.append({"来源": os.path.basename(path), "学号": sid,
                              "姓名": nm, "原因": why,
                              "描述预览": text[:40]})
            continue
        if nm and students[key]["姓名"] and nm != students[key]["姓名"]:
            conflict.append({"学号": key, "主表姓名": students[key]["姓名"],
                             "描述表姓名": nm,
                             "性质": "姓名不一致（同音/错字），已按学号归一，需人工核对是否同一人"})
        prev = students[key][field]
        if text in prev:
            notes_report["机器提示"].append(
                "%s存在完全重复的记录（%s %s），已自动去重"
                % (label, key, students[key]["姓名"]))
        else:
            students[key][field] = (prev + " " + text).strip() if prev else text
        hit += 1
    if unmatched:
        notes_report["未匹配记录"].extend(unmatched)
    if conflict:
        notes_report["姓名冲突"].extend(conflict)
    if suspect:
        notes_report["疑似同一人"].extend(suspect)
    if matcher.order_hit:
        notes_report["机器提示"].append(
            "%s没有学号列且有同名学生（%s），已按两表出现顺序对应 —— 务必人工核对"
            % (label, "、".join(sorted(matcher.order_hit))))
    if miss_is_gap:
        miss = [{"学号": k, "姓名": v["姓名"]} for k, v in students.items() if not v[field]]
        for m in miss:
            students[m["学号"]]["缺失项"].append(field)
        if miss:
            notes_report["机器提示"].append(
                "无%s %d 人：%s" % (field, len(miss), "、".join(m["姓名"] for m in miss)))
    else:
        # 覆盖不到的人**不算缺失**（荣誉不是人人都有），但要点名提醒：
        # 这些同学的评语里不能出现任何奖项/称号——否则就是虚构（规则 2）
        gap = [v["姓名"] for v in students.values() if not v[field]]
        notes_report["机器提示"].append(
            "%s覆盖 %d/%d 人。**荣誉不是人人都有，未覆盖的人不算缺失**——"
            "但下面这些同学的评语里不要出现任何奖项或称号（写了就是虚构）：%s"
            % (label, len(students) - len(gap), len(students), "、".join(gap)))
    notes_report["覆盖人数"][label] = hit
    return hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True, nargs="+", metavar="成绩文件",
                    help="本次/上次/平时成绩文件，可传多个（期末、期中、平时各一个文件时"
                         "一起传，脚本按文件名分辨考试先后）；也支持逗号分隔")
    ap.add_argument("--homework")
    ap.add_argument("--classroom")
    ap.add_argument("--notes")
    ap.add_argument("--past-comments",
                    help="往年（上学期）学生评语表，任选；作为个性化描述的**参考**"
                         "并进 roster.json 的「往年评语」。表内只需 学号/姓名 + 一列评语文本")
    ap.add_argument("--awards",
                    help="荣誉材料表（奖状/证书/荣誉榜），任选；进 roster.json 的「荣誉奖项」。"
                         "表内只需 学号/姓名 + 一列荣誉文本（一条一行，级别与时间并入文本）。"
                         "常见来源是用户拍的奖状照片或截图——**图片请先读图转写成表**再传进来")
    ap.add_argument("--subjects", default="", help="指定学科列，逗号分隔；留空自动识别")
    ap.add_argument("--class-name", default="")
    ap.add_argument("--exam-name", default="本学期期末考试")
    ap.add_argument("--out", default="roster.json")
    ap.add_argument("--note-col", default="", help="教师描述表中的描述列名；留空自动取最长文本列")
    ap.add_argument("--past-comment-col", default="",
                    help="往年评语表中的评语列名；留空自动识别（往年评语/上学期评语/评语…），"
                         "都认不出时取最长文本列")
    ap.add_argument("--award-col", default="",
                    help="荣誉材料表中的荣誉列名；留空自动识别（荣誉奖项/奖项/荣誉/奖状/证书…），"
                         "都认不出时取最长文本列")
    ap.add_argument("--scores-sheet", default="",
                    help="成绩表用哪个工作表；留空自动选（多张成绩表时按考试先后取最靠后的）。"
                         "传了多个成绩文件时，标签取**文件名**（如「初一3班期末考试成绩」）")
    ap.add_argument("--prev-sheet", default="",
                    help="「上次对比」用哪个工作表；留空自动取主表之前最近一次考试的那张")
    ap.add_argument("--trend-sheet", default="",
                    help="平时/过程性成绩用哪个工作表；留空自动取唯一一张「全是第N次」的表")
    args = ap.parse_args()

    # `--scores` 既支持「空格分隔的多个路径」，也支持「一个参数里逗号分隔」（旧式写法）
    scores_paths = []
    for x in args.scores:
        scores_paths.extend([t.strip() for t in str(x).split(",") if t.strip()])
    if not scores_paths:
        sys.exit("--scores 至少要有一个成绩文件")
    args.scores = scores_paths

    # ---------- 输入文件存在性（缺文件必须报错，不能静默降级） ----------
    for p in scores_paths:
        if not os.path.exists(p):
            sys.exit("成绩表文件不存在：%s\n"
                     "（请检查路径拼写；成绩分在多个文件里时全部一起传给 --scores）" % p)
        reject_image(p, "成绩表")
    for label, p in (("作业统计表", args.homework),
                     ("课堂表现统计表", args.classroom), ("教师个别描述表", args.notes),
                     ("往年评语表", args.past_comments), ("荣誉材料表", args.awards)):
        if p and not os.path.exists(p):
            sys.exit("%s 文件不存在：%s\n"
                     "（请检查路径拼写；如果确实没有这类材料，请不要传该参数——"
                     "静默跳过会让交付的小贴士误报成「你没提供材料」）" % (label, p))

    # ---------- 主表：成绩（1~N 个文件合并成一份工作表清单） ----------
    pre_notices = []
    # 每个文件各自解析：.csv 直接读、.xls 友好拒绝、.xlsx 走 read_workbook；
    # 工作表名是「Sheet1」这类通用名时按**文件名**贴标签，
    # 否则期末/期中/平时三份文件的表全叫 Sheet1，选路看不出先后。
    all_sheets = load_scores_sources(scores_paths, pre_notices)
    if not all_sheets:
        sys.exit("成绩表为空：" + "、".join(scores_paths))
    if len(scores_paths) > 1:
        pre_notices.append(
            "本次成绩来自 %d 个文件，已合并成一份工作表清单（标签取文件名）：%s"
            % (len(scores_paths), "、".join(s["sheet"] for s in all_sheets)))
    pre_notices.extend(sibling_scores_hint(scores_paths))
    try:
        main_sheet, prev_sheet, trend_sheet, route_notes = route_sheets(
            all_sheets, args.scores_sheet, args.trend_sheet, args.prev_sheet)
    except KeyError as e:
        sys.exit(str(e.args[0]))
    except LookupError as e:
        sys.exit(str(e.args[0]))
    for s in all_sheets:
        if s["meta"].get("说明"):
            pre_notices.append("工作表「%s」：%s" % (s["sheet"], s["meta"]["说明"]))
    pre_notices.extend(route_notes)

    sh, srows = main_sheet["headers"], main_sheet["rows"]
    if not sh:
        sys.exit("成绩表为空：" + "、".join(scores_paths))
    plain_cols, _trend_in_main, _other = split_columns(sh)
    # 整簿一张成绩表都没有 → 走「只有名单、没有成绩数据」的降级路径（见 route_sheets），
    # 此时主表本来就没有成绩列，不该再拦；只有「簿里明明有成绩表、却选了张没成绩的表」才拦。
    no_scores_sheet = not any(sheet_kind(s["headers"]) == "scores" for s in all_sheets)
    if not plain_cols and not no_scores_sheet:
        sys.exit("工作表「%s」里没有本次考试成绩列（只有平时/过程性成绩列）。\n"
                 "请用 --scores-sheet 指定一张考试表，或把这张表用 --trend-sheet 当平时趋势。\n"
                 "可用的工作表有：%s"
                 % (main_sheet["sheet"], "、".join(s["sheet"] for s in all_sheets)))
    i_id = find_col(sh, ID_KEYS)
    i_name = find_col(sh, NAME_KEYS)
    if i_id is None and i_name is None:
        sys.exit("成绩表里找不到「学号」或「姓名」列，无法建立主键")
    i_sex = find_col(sh, SEX_KEYS)
    # 历史列（期中总分/上次排名）不能当本次总分/排名——否则本次与上次命中的是同一列，
    # 「总分变化」「排名变化」自己减自己、恒为 0，还会宣称"已生成变化"。
    # 年级/校排名也不能当班级排名——拿它做分位，全班分层会整体错位。
    hist_excl = set(i for i, h in enumerate(sh)
                    if h and any(m in h for m in HIST_MARKERS))
    grade_rank_excl = set(i for i, h in enumerate(sh)
                          if h and any(k in h for k in GRADE_RANK_KEYS))
    i_total = find_col_exact_first(sh, TOTAL_KEYS, exclude=hist_excl)
    i_rank = find_col_exact_first(sh, RANK_KEYS, exclude=hist_excl | grade_rank_excl)
    if i_total is not None and has_subject_word(sh[i_total]):
        pre_notices.append("总分列「%s」看起来是单科总分（表里没有全局总分），"
                           "已按无总分列处理，总分由各科求和得出" % sh[i_total])
        i_total = None
    if i_rank is not None and has_subject_word(sh[i_rank]):
        pre_notices.append("排名列「%s」看起来是单科排名，已按无排名列处理" % sh[i_rank])
        i_rank = None
    if grade_rank_excl:
        gnames = "、".join(sh[i] for i in sorted(grade_rank_excl))
        if i_rank is None:
            pre_notices.append(
                "表里只有「%s」这类年级/校排名，没有班级排名 → 本次不做排名分位与排名变化"
                "（年级排名的位次基数不同，直接当班级排名用会让整个班的分层错位）；"
                "要做排名类分析请补一列「班级排名」" % gnames)
        else:
            pre_notices.append(
                "表里既有班级排名、也有「%s」——排名类字段一律以班级排名为准，"
                "年级排名本次未使用" % gnames)
    id_cols = [h for h in sh if h and any(k in h for k in ID_KEYS)]
    if len(id_cols) > 1:
        pre_notices.append("表里有多个编号列（%s）——本次以「%s」为主键列（学号优先于考号）"
                           % ("、".join(dict.fromkeys(id_cols)), sh[i_id]))
    known_excl = set(i for i in [i_id, i_name, i_sex, i_total, i_rank] if i is not None)
    subjects, subj_notes, sparse_subjects = detect_subjects(
        sh, srows, known_excl, args.subjects)
    pre_notices.extend(subj_notes)
    if not subjects:
        used = set(i for i in [i_id, i_name, i_sex, i_total, i_rank] if i is not None)
        suspicious = []
        for i, h in enumerate(sh):
            if i in used or not h:
                continue
            vals = [to_num(r[i]) for r in srows if i < len(r)]
            if sum(1 for v in vals if v is not None) >= max(1, len(srows) * 0.5):
                suspicious.append(h)
        if suspicious:
            sys.exit("成绩表里这些列整列都是数字，但没有一个能识别成学科列：%s\n"
                     "请用 --subjects 明确指定列名（例如 --subjects 语文,数学,英语）后重跑。"
                     % "、".join(suspicious))
        pre_notices.append(
            "未识别到学科列，本次按「只有名单、没有成绩数据」处理——"
            "评语中不得出现任何数字，只能用教师描述里的行为细节取材")

    # ---------- 建主键 ----------
    # 有学号 → 学号（姓名并存一起校验）；没有学号 → 姓名；无学号且重名 → 姓名1号 / 姓名2号
    key_pairs, id_col_live, key_notes, missing_id_rows = build_keys(srows, i_id, i_name)
    pre_notices.extend(key_notes)
    if missing_id_rows:
        # 有学号列、却有人没填学号 → 绝不能一边用学号、一边退回姓名：
        # 一次对齐里混两种主键，meta 只记一种，附表匹配口径也跟着漂移。
        sys.exit("成绩表有学号列，但这些行没填学号：%s\n"
                 "主键必须全班统一，否则同一份名单里会混用「学号 / 姓名」两种主键，"
                 "附表的匹配口径也随之漂移。请二选一后重跑：\n"
                 "  ① 把这些同学的学号补齐；\n"
                 "  ② 把学号整列删掉（脚本会改以姓名为主键，重名者自动编号）。"
                 % "、".join(missing_id_rows))
    pre_notices.append(
        "主键规则：成绩表有学号列 → 主键 = 学号（姓名并存，一起参与匹配校验）"
        if id_col_live else
        "主键规则：成绩表没有学号列（或该列整列为空），已忽略学号、"
        "以「姓名」为主键（重名者按出现顺序编为「张三1号」「张三2号」）")

    students = OrderedDict()
    dup_id = []
    for r, (key, src) in zip(srows, key_pairs):
        if not key:
            continue
        nm = norm_name(r[i_name]) if (i_name is not None and i_name < len(r)) else ""
        if key in students:
            dup_id.append("%s %s" % (key, nm or students[key]["姓名"]))
            continue
        students[key] = {
            "学号": key, "姓名": nm, "主键来源": src,
            "性别": (str(r[i_sex]).strip() if i_sex is not None and r[i_sex] else ""),
            "成绩": {}, "平时趋势": {}, "作业": None, "课堂": None,
            "教师描述": "", "往年评语": "", "荣誉奖项": "",
            "缺失项": [],
        }
        for s in subjects:
            students[key]["成绩"][s] = to_num(r[sh.index(s)])
        if i_total is not None:
            students[key]["成绩"]["总分"] = to_num(r[i_total])
        else:
            # 自动求和时排除选考/走班科目：只有部分同学有成绩的科目一旦算进总分，
            # 选考与未选考的同学总分就不可比了（该科成绩仍保留在「成绩」里可单独引用）。
            total_bases = [x for x in subjects if x not in sparse_subjects] or subjects
            vals = [v for v in (students[key]["成绩"].get(x) for x in total_bases)
                    if v is not None]
            if not vals:
                vals = [v for v in students[key]["成绩"].values() if v is not None]
            students[key]["成绩"]["总分"] = round(sum(vals), 1) if vals else None
            if sparse_subjects:
                students[key]["成绩"]["总分说明"] = (
                    "总分未计入选考/走班科目：%s（这些科只有部分同学有成绩，"
                    "计入会让总分不可横向比较）" % "、".join(sorted(sparse_subjects)))
        if i_rank is not None:
            students[key]["成绩"]["班级排名"] = to_num(r[i_rank])

    if dup_id:
        sys.exit("成绩表存在重复学号，无法判断哪一行是本人，已停止对齐：\n  %s\n"
                 "请先在成绩表里合并/删除重复行再重跑。\n"
                 "（如果这张表本来就没有学号，请把学号列整列删掉——"
                 "脚本会改以姓名为主键，重名者自动编号。）" % "\n  ".join(dup_id))

    matcher = NameMatcher(students)
    # 重名：靠学号区分；附表没有学号时按出现顺序对应，必须人工核对
    if matcher.has_id and any(len(v) > 1 for v in matcher.by_name.values()):
        detail = []
        for nm, ks in sorted(matcher.by_name.items()):
            if len(ks) > 1:
                detail.append("%s（学号 %s）" % (nm, "、".join(ks)))
        pre_notices.append(
            "全班存在重名：%s —— 这些学生优先靠学号匹配；"
            "附表若没有学号列，脚本会按出现顺序对应，必须人工核对，"
            "评语中也不要写姓名以外的区分方式" % "；".join(detail))

    # 期中对比列（可选）。这两列不能与本次总分/排名命中的是同一列——
    # 那样「变化」就是自己减自己、恒为 0（SKILL 推荐的「期中总分/期中排名」列名正是如此）。
    mid_total_i = find_col_exact_first(sh, ["期中总分", "上次总分", "期中成绩"])
    mid_rank_i = find_col_exact_first(sh, ["期中排名", "上次排名", "期中名次"])
    if mid_total_i is not None and mid_total_i == i_total:
        sys.exit("「%s」既被当成本次总分、又被当成上次总分，无法计算变化。"
                 "请把本次总分的列名改成「总分」、上次的用「期中总分」再重跑。"
                 % sh[mid_total_i])
    if mid_rank_i is not None and mid_rank_i == i_rank:
        sys.exit("「%s」既被当成本次排名、又被当成上次排名，无法计算变化。"
                 "请把本次排名的列名改成「班级排名」、上次的用「期中排名」再重跑。"
                 % sh[mid_rank_i])
    # 本次总分是「各科求和」而不是表里的总分列时，与「上次总分」不同源，
    # 两者相减没有意义 → 不产出「总分变化」，并明确告诉用户为什么。
    total_is_sum = i_total is None
    name2sid = {nm: ks[0] for nm, ks in matcher.by_name.items() if len(ks) == 1}
    ambig_names = set(nm for nm, ks in matcher.by_name.items() if len(ks) > 1)
    # 学科本体 → 本次成绩表里的写法。把别的表里的「道法」对到本表的「道德与法治」，
    # 保证不同表之间的同一门课用的是同一个名字（归一只在内部判断用，输出以主表为准）。
    main_base2name = {}
    for s in subjects:
        for b in subject_bases(s):
            main_base2name.setdefault(b, s)

    notes_report = {
        "覆盖人数": {}, "缺失学生": [], "缺考学生": [], "姓名冲突": [], "名单外记录": [],
        "疑似同一人": [], "未匹配记录": [], "字段口径": [], "机器提示": list(pre_notices),
    }

    # ---------- 期中/上次对比 ----------
    # 两条来源：① 同一张表里的「期中总分/上次总分」列；② 另一张工作表（如「期中考试成绩」）
    if mid_total_i is not None or mid_rank_i is not None:
        for r, (key, _src) in zip(srows, key_pairs):
            if not key or key not in students:
                continue
            g = students[key]["成绩"]
            if mid_total_i is not None and not total_is_sum:
                mt = to_num(r[mid_total_i])
                if mt is not None and g.get("总分") is not None:
                    g["上次总分"] = mt
                    g["总分变化"] = round(g["总分"] - mt, 1)
            if mid_rank_i is not None:
                mr = to_num(r[mid_rank_i])
                if mr is not None and g.get("班级排名") is not None:
                    g["上次排名"] = mr
                    # 名次数字变小 = 进步，故用「上次 - 本次」，正数=进步
                    g["排名变化"] = int(mr - g["班级排名"])
        made = []
        if mid_total_i is not None and not total_is_sum:
            made.append("总分变化")
        if mid_rank_i is not None:
            made.append("排名变化")
        if made:
            notes_report["字段口径"].append(
                "成绩表含期中对比列，已生成「%s」（两者均为正数时表示进步）" % "、".join(made))
        if mid_total_i is not None and total_is_sum:
            notes_report["机器提示"].append(
                "表里只有「%s」这样的历史总分列，没有本次总分列 → 本次总分按各科求和得出，"
                "与上次总分不同源，已**不生成**「总分变化」；要算进退请补一列本次总分（如「总分」）"
                % sh[mid_total_i])
    elif prev_sheet is not None:
        ph, prows = prev_sheet["headers"], prev_sheet["rows"]
        p_id, p_name = find_col(ph, ID_KEYS), find_col(ph, NAME_KEYS)
        p_hist = set(i for i, h in enumerate(ph)
                     if h and any(m in h for m in HIST_MARKERS))
        p_grank = set(i for i, h in enumerate(ph)
                      if h and any(k in h for k in GRADE_RANK_KEYS))
        p_total = find_col_exact_first(ph, TOTAL_KEYS, exclude=p_hist)
        p_rank = find_col_exact_first(ph, RANK_KEYS, exclude=p_hist | p_grank)
        if p_total is not None and has_subject_word(ph[p_total]):
            p_total = None
        if p_rank is not None and has_subject_word(ph[p_rank]):
            p_rank = None
        # 上次各科：与本次学科同一门课的列
        p_subj = {}
        for i, h in enumerate(ph):
            if not h or is_trend_header(h):
                continue
            for b in subject_bases(h):
                if b in main_base2name and main_base2name[b] not in p_subj:
                    p_subj[main_base2name[b]] = i
        matcher.new_table()
        hit = 0
        for r in prows:
            sid = norm_id(r[p_id]) if p_id is not None else ""
            nm = norm_name(r[p_name]) if p_name is not None else ""
            key, why = matcher.match(sid, nm)
            if not key:
                notes_report["未匹配记录"].append(
                    {"来源": "工作表「%s」（上次对比）" % prev_sheet["sheet"],
                     "学号": sid, "姓名": nm, "原因": why})
                continue
            g = students[key]["成绩"]
            if p_total is not None and not total_is_sum:
                mt = to_num(r[p_total])
                if mt is not None and g.get("总分") is not None:
                    g["上次总分"] = mt
                    g["总分变化"] = round(g["总分"] - mt, 1)
            if p_rank is not None:
                mr = to_num(r[p_rank])
                if mr is not None and g.get("班级排名") is not None:
                    g["上次排名"] = mr
                    g["排名变化"] = int(mr - g["班级排名"])
            last = {}
            for s, ci in p_subj.items():
                v = to_num(r[ci])
                if v is not None:
                    last[s] = v
            if last:
                g["上次各科"] = last
                g["上次各科说明"] = "来自工作表「%s」，仅用于判断单科进退，未参与本次班均" \
                                     % prev_sheet["sheet"]
            hit += 1
        notes_report["覆盖人数"]["上次对比表"] = hit
        made = []
        if p_total is not None and not total_is_sum:
            made.append("总分变化")
        if p_rank is not None:
            made.append("排名变化")
        notes_report["字段口径"].append(
            "「上次总分/上次排名/上次各科」取自工作表「%s」%s"
            % (prev_sheet["sheet"],
               "，已生成「%s」（两者均为正数时表示进步）" % "、".join(made) if made
               else "；本次没有总分列（总分由各科求和），与上次总分不同源，未生成「总分变化」"))
        if matcher.order_hit:
            notes_report["机器提示"].append(
                "上次对比表没有学号列且有同名学生（%s），已按出现顺序对应 —— 务必人工核对"
                % "、".join(sorted(matcher.order_hit)))

    # ---------- 平时/过程性成绩：保留逐次序列，不取均值 ----------
    # 用户口径（2026-10-08）：6 次平时成绩保留趋势，不合并成均值——
    # 均值会把「第一次平时成绩96分、第五次又落回70分」这种最有价值的波动抹平，
    # 而这条序列正是「学习习惯」维度唯一真实的证据源。
    if trend_sheet is not None:
        th, trows = trend_sheet["headers"], trend_sheet["rows"]
        tcols = trend_columns(th)
        t_id, t_name = find_col(th, ID_KEYS), find_col(th, NAME_KEYS)
        matcher.new_table()
        hit, no_trend = 0, []
        for r in trows:
            sid = norm_id(r[t_id]) if t_id is not None else ""
            nm = norm_name(r[t_name]) if t_name is not None else ""
            key, why = matcher.match(sid, nm)
            if not key:
                notes_report["未匹配记录"].append(
                    {"来源": "工作表「%s」（平时趋势）" % trend_sheet["sheet"],
                     "学号": sid, "姓名": nm, "原因": why})
                continue
            d = {}
            for base, cols in tcols.items():
                name = main_base2name.get(base, base)
                seq = [to_num(r[i]) for _o, i, _h in cols]
                present = [v for v in seq if v is not None]
                item = {"逐次": seq, "共几次": len(seq), "有分数次数": len(present)}
                if len(present) < len(seq):
                    item["缺次"] = [o for (o, _i, _h), v in zip(cols, seq) if v is None]
                if present:
                    delta = round(present[-1] - present[0], 1)
                    item.update({
                        "首": present[0], "末": present[-1],
                        "最高": max(present), "最低": min(present),
                        "跨度": round(max(present) - min(present), 1),
                        "首末差": delta,
                        "方向": ("上行" if delta >= 3 else
                                 "下行" if delta <= -3 else "基本持平"),
                    })
                d[name] = item
            if d:
                students[key]["平时趋势"] = d
                hit += 1
            else:
                no_trend.append(key)
        notes_report["覆盖人数"]["平时趋势表"] = hit
        notes_report["字段口径"].append(
            "「平时趋势」来自工作表「%s」：**保留逐次序列，不产出均值**，"
            "并把序列特征（首/末/最高/最低/跨度/首末差/方向）一并给出；"
            "成文时**一律用标准式引用**——「学科+第X次平时成绩NN分」，"
            "如「数学从第一次平时成绩74分提升到第六次平时成绩的87分」"
            "（不要写「第1次的 74 涨到第6次的 87」「那条平时线」，也不要用平均分替代趋势）"
            % trend_sheet["sheet"])
        miss = [{"学号": k, "姓名": v["姓名"]} for k, v in students.items()
                if not v.get("平时趋势")]
        for m in miss:
            students[m["学号"]]["缺失项"].append("平时成绩")
        if miss:
            notes_report["机器提示"].append(
                "平时趋势表缺 %d 人：%s" % (len(miss), "、".join(m["姓名"] for m in miss)))
        if matcher.order_hit:
            notes_report["机器提示"].append(
                "平时趋势表没有学号列且有同名学生（%s），已按出现顺序对应 —— 务必人工核对"
                % "、".join(sorted(matcher.order_hit)))

    # ---------- 作业表 ----------
    if args.homework and os.path.exists(args.homework):
        hh, hrows, hm = read_table(args.homework)
        if hm.get("多表提示"):
            notes_report["机器提示"].append("作业统计表：" + hm["多表提示"])
        j_id, j_name = find_col(hh, ID_KEYS), find_col(hh, NAME_KEYS)
        colmap = {}
        for std, keys in HOMEWORK_FIELDS.items():
            ci = find_col(hh, keys)
            if ci is not None:
                colmap[std] = ci
        hit, unmatched, duprow = 0, [], []
        matcher.new_table()
        for r in hrows:
            sid = norm_id(r[j_id]) if j_id is not None else ""
            nm = norm_name(r[j_name]) if j_name is not None else ""
            if is_stat_row(sid, nm):
                continue
            key, why = matcher.match(sid, nm)
            if not key:
                unmatched.append({"来源": os.path.basename(args.homework),
                                  "学号": sid, "姓名": nm, "原因": why})
                continue
            if students[key]["作业"] is not None:
                duprow.append("%s %s" % (key, students[key]["姓名"]))
            d = {}
            for std, ci in colmap.items():
                v = r[ci]
                if std in ("提交率", "按时提交率", "订正完成率"):
                    d[std] = pct(v)
                elif std in ("应交次数", "实交次数"):
                    n = to_num(v)
                    d[std] = int(n) if n is not None else None
                else:
                    d[std] = ("" if v is None else str(v).strip())
            if d.get("应交次数") and d.get("实交次数") is not None:
                d["欠交次数"] = d["应交次数"] - d["实交次数"]
            students[key]["作业"] = d
            hit += 1
        if unmatched:
            notes_report["未匹配记录"].extend(unmatched)
        if duprow:
            notes_report["机器提示"].append(
                "作业表里有同一个人出现多行，已取最后一行：%s" % "、".join(sorted(set(duprow))))
        if matcher.order_hit:
            notes_report["机器提示"].append(
                "作业表没有学号列且有同名学生（%s），已按两表出现顺序对应 —— 务必人工核对"
                % "、".join(sorted(matcher.order_hit)))
        miss = [{"学号": k, "姓名": v["姓名"]} for k, v in students.items() if v["作业"] is None]
        for m in miss:
            students[m["学号"]]["缺失项"].append("作业统计")
        if miss:
            notes_report["机器提示"].append(
                "作业表缺 %d 人：%s" % (len(miss), "、".join(m["姓名"] for m in miss)))
        notes_report["覆盖人数"]["作业表"] = hit

    # ---------- 课堂表 ----------
    if args.classroom and os.path.exists(args.classroom):
        ch, crows, cm = read_table(args.classroom)
        if cm.get("多表提示"):
            notes_report["机器提示"].append("课堂表现统计表：" + cm["多表提示"])
        k_id, k_name = find_col(ch, ID_KEYS), find_col(ch, NAME_KEYS)
        colmap = {}
        for std, keys in CLASSROOM_FIELDS.items():
            ci = find_col(ch, keys)
            if ci is not None:
                colmap[std] = ci
        hit, unmatched, typo, duprow = 0, [], [], []
        matcher.new_table()
        for r in crows:
            sid = norm_id(r[k_id]) if k_id is not None else ""
            raw_name = r[k_name] if k_name is not None else ""
            nm = norm_name(raw_name)
            if is_stat_row(sid, nm):
                continue
            key, why = matcher.match(sid, nm)
            if not key:
                unmatched.append({"来源": os.path.basename(args.classroom),
                                  "学号": sid, "姓名": nm, "原因": why})
                continue
            if students[key]["课堂"] is not None:
                duprow.append("%s %s" % (key, students[key]["姓名"]))
            if raw_name is not None and str(raw_name) != students[key]["姓名"]:
                typo.append({"学号": key, "主表姓名": students[key]["姓名"],
                             "本表写法": str(raw_name),
                             "性质": "仅写法差异（空格/全角），已归一"})
            d = {}
            for std, ci in colmap.items():
                v = r[ci]
                if std == "课堂任务完成率":
                    d[std] = pct(v)
                elif std == "发言次数":
                    n = to_num(v)
                    d[std] = int(n) if n is not None else None
                else:
                    d[std] = to_num(v)
            students[key]["课堂"] = d
            hit += 1
        if unmatched:
            notes_report["未匹配记录"].extend(unmatched)
        if typo:
            notes_report["姓名冲突"].extend(typo)
        if duprow:
            notes_report["机器提示"].append(
                "课堂表里有同一个人出现多行，已取最后一行：%s" % "、".join(sorted(set(duprow))))
        if matcher.order_hit:
            notes_report["机器提示"].append(
                "课堂表没有学号列且有同名学生（%s），已按两表出现顺序对应 —— 务必人工核对"
                % "、".join(sorted(matcher.order_hit)))
        miss = [{"学号": k, "姓名": v["姓名"]} for k, v in students.items() if v["课堂"] is None]
        for m in miss:
            students[m["学号"]]["缺失项"].append("课堂表现")
        if miss:
            notes_report["机器提示"].append(
                "课堂表缺 %d 人：%s" % (len(miss), "、".join(m["姓名"] for m in miss)))
        notes_report["覆盖人数"]["课堂表"] = hit

    # ---------- 教师个别描述 + 往年评语 + 荣誉材料 ----------
    # 三张表走**同一条**匹配链路（ingest_text_table → NameMatcher），差别只有落进哪个字段：
    #   · 教师描述 → students[*]["教师描述"]（本学期的证据）
    #   · 往年评语 → students[*]["往年评语"]（参考；成文规则见 writing-rules 规则 5）
    #   · 荣誉奖项 → students[*]["荣誉奖项"]（**可直接引用的证据**；规则 2 对它有例外）
    if args.notes and os.path.exists(args.notes):
        ingest_text_table(args.notes, "教师描述", NOTE_TEXT_KEYS, args.note_col,
                          "教师描述表", students, matcher, name2sid, ambig_names,
                          notes_report)

    if args.past_comments and os.path.exists(args.past_comments):
        ingest_text_table(args.past_comments, "往年评语", PAST_TEXT_KEYS,
                          args.past_comment_col, "往年评语表", students, matcher,
                          name2sid, ambig_names, notes_report)
        notes_report["字段口径"].append(
            "往年评语是**参考**、不是本学期的事实证据：可借它找到这个人身上稳定的、"
            "只属于他的特点，保持与过去期待的连贯；但不得照搬往年措辞，"
            "其中的事实须以本学期材料为准（与今年材料冲突时以今年为准），"
            "也不得引用其中的分数/名次")

    if args.awards and os.path.exists(args.awards):
        ingest_text_table(args.awards, "荣誉奖项", AWARD_TEXT_KEYS, args.award_col,
                          "荣誉材料表", students, matcher, name2sid, ambig_names,
                          notes_report, miss_is_gap=False)
        notes_report["字段口径"].append(
            "荣誉奖项来自奖状/证书/荣誉榜（图片需先经 AI 读图转写成表），是**可引用的证据**："
            "奖项名称、级别（校级/区级/市级）、时间都可以写进评语，但必须忠于原文、"
            "**级别不得夸大**（校级不能写成市级，三等奖不能写成一等奖）；"
            "材料里没有的竞赛/职务仍然不许写（writing-rules 规则 2 不变）；"
            "时间久远的（如小学时期）只当「稳定特点」的佐证，不写成本学期新发生的事")

    # ---------- 派生：学科强弱 / 缺考 / 分层建议 ----------
    avg = {}
    for s in subjects:
        vals = [v["成绩"].get(s) for v in students.values() if v["成绩"].get(s) is not None]
        avg[s] = round(sum(vals) / len(vals), 1) if vals else None
    ranks = [v["成绩"].get("班级排名") for v in students.values()
             if v["成绩"].get("班级排名") is not None]
    n = len(students)
    if sparse_subjects:
        notes_report["机器提示"].append(
            "选考/走班科目：%s —— 未参加的同学**不计缺考**（只记「未选考科目」，"
            "不算缺考、不占用排名类禁用），这些科也不计入总分；"
            "评语中不要给未选考的同学写这些科"
            % "、".join(sorted(sparse_subjects)))
    for sid, st in students.items():
        g = st["成绩"]
        missing_exam = [s for s in subjects if g.get(s) is None and s not in sparse_subjects]
        not_taken = [s for s in subjects if g.get(s) is None and s in sparse_subjects]
        if not_taken:
            st["未选考科目"] = not_taken
        if missing_exam:
            st["缺考科目"] = missing_exam
            notes_report["缺考学生"].append({
                "学号": sid, "姓名": st["姓名"], "缺考科目": missing_exam,
                "原表总分": g.get("总分"), "原表排名": g.get("班级排名"),
                "处理": "该科按「无数据」处理，未计 0 分；但原表总分/排名已受缺考影响，"
                        "不可与其他学生横向比较，评语中不要使用排名类表述",
            })
            notes_report["机器提示"].append(
                "%s(%s) 缺考科目：%s —— 原表总分与排名已受缺考影响，评语中禁止使用排名类表述"
                % (st["姓名"], sid, "、".join(missing_exam)))
        diffs = {s: round(g[s] - avg[s], 1) for s in subjects
                 if g.get(s) is not None and avg.get(s) is not None}
        present = [g[s] for s in subjects if g.get(s) is not None]
        if present:
            g["已考科目总分"] = round(sum(present), 1)
            if missing_exam:
                g["已考科目总分说明"] = "仅含已考科目，不可与全班总分直接比较"
        g["学科偏差"] = diffs
        if diffs:
            g["优势学科"] = max(diffs, key=diffs.get)
            g["短板学科"] = min(diffs, key=diffs.get)
            g["优势学科领先"] = diffs[g["优势学科"]]
            g["短板学科落后"] = diffs[g["短板学科"]]
        # 机器分层建议（仅供参考，最终由 AI 结合教师描述修正）
        r = g.get("班级排名")
        dr = g.get("排名变化")
        if n < 10:
            st["分层建议"] = "待人工确认（全班不足 10 人，分位规则失效）"
        elif missing_exam:
            st["分层建议"] = "待人工确认（有缺考科目，排名不可比）"
        elif r is None:
            st["分层建议"] = "待定"
        elif r <= max(1, n * 0.25) and (dr is None or dr >= -3):
            st["分层建议"] = "A 优秀稳定"
        elif r > n * 0.75:
            st["分层建议"] = "D 需重点帮扶"
        elif dr is not None and dr <= -max(3, round(n * 0.15)):
            st["分层建议"] = "C 波动待稳"
        else:
            st["分层建议"] = "B 踏实平稳"
    if n < 10:
        notes_report["机器提示"].append(
            "全班不足 10 人：分位类规则整体失效，「分层建议」一律标为待人工确认，必须人工分层")
    elif subjects and any(v["成绩"].get("班级排名") for v in students.values()):
        notes_report["机器提示"].append(
            "「C 波动待稳」的判定阈值已按班额缩放（排名下降 ≥ %d 位）"
            % max(3, round(n * 0.15)))
    notes_report["机器提示"].append("分层建议为规则初判（排名分位+排名变化），必须结合教师描述人工/AI 修正后再用")

    notes_report["覆盖人数"]["主表人数"] = n
    notes_report["覆盖人数"]["学科均分"] = avg
    notes_report["名单外记录"] = [
        {"来源": u["来源"], "学号": u["学号"], "姓名": u["姓名"], "原因": u["原因"]}
        for u in notes_report["未匹配记录"] if "名单" in u.get("原因", "")
    ]
    notes_report["缺失学生"] = [{"学号": k, "姓名": v["姓名"], "缺什么": v["缺失项"]}
                              for k, v in students.items() if v["缺失项"]]
    notes_report["字段口径"] = [
        "成绩册读法：自动跳过表头之上的大标题行；双行表头（上格次数、下格学科）拼成"
        "「第1次-数学」这类列名；多工作表时按考试先后自动选「本次 / 上次对比 / 平时趋势」",
        "主键规则：成绩表有学号列（且至少一行有值）→ 主键 = 学号，姓名并存、二者一起参与匹配校验；"
        "没有学号列或整列为空 → 忽略学号，主键 = 姓名",
        "无学号且同名学生 → 按成绩表里的出现顺序编号：排在前面的为「张三1号」，后面的为「张三2号」",
        "附表匹配：名单里有学号时，学号不在名单内一律判「名单外」，不用姓名兜底；"
        "名单本身没有学号（以姓名为主键）时，附表可以只凭姓名接上",
        "同名多人且附表没有学号 → 按该附表内的出现顺序依次对应 1号/2号，并在「机器提示」中要求人工核对",
        "成绩表同一个学号出现两次 → 直接停止对齐并报错，不静默取一条",
        "成绩表有学号列却有人没填学号 → 直接报错，绝不混用「学号 / 姓名」两种主键",
        "成绩表底部统计行（「班级平均」「年级最高」）按「无学号 + 姓名含统计词」剔除，不计入名单",
        "选考/走班科目（只有部分同学有成绩的学科）保留为学科，但不计入总分、"
        "未选考的同学不计缺考（只记「未选考科目」）",
        "姓名已做归一化（去空格/全角空格/括号备注），但不会自动改写主表姓名",
        "缺失指标按「无数据」处理，不按 0 分计，不虚构",
        "作业提交率/订正率统一归一到 0~1 小数",
    ] + notes_report["字段口径"]

    meta = {
        "班级": args.class_name, "考试": args.exam_name,
        "学科": subjects, "人数": n,
        "选考科目": sorted(sparse_subjects),
        "主键": "学号" if id_col_live else "姓名",
        "工作表": {
            "本次成绩": main_sheet["sheet"],
            "上次对比": prev_sheet["sheet"] if prev_sheet is not None else None,
            "平时趋势": trend_sheet["sheet"] if trend_sheet is not None else None,
        },
        "生成脚本": "prepare_roster.py",
        "生成时间": __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    out = {"meta": meta, "roster": list(students.values()), "对齐说明": notes_report}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("材料对齐完成 -> %s" % os.path.abspath(args.out))
    print("  班级：%s   人数：%d   学科：%s"
          % (args.class_name or "(未填)", n, "、".join(subjects) or "(未识别，按无成绩数据处理)"))
    print("  主键：%s" % ("学号（姓名并存校验）" if id_col_live
                        else "姓名（成绩表没有可用学号列，重名者已编 1号/2号）"))
    print("  工作表：本次「%s」%s%s"
          % (main_sheet["sheet"],
             "　上次对比「%s」" % prev_sheet["sheet"] if prev_sheet is not None else "",
             "　平时趋势「%s」（保留逐次，不取均值）" % trend_sheet["sheet"]
             if trend_sheet is not None else ""))
    print("  覆盖：%s" % notes_report["覆盖人数"])
    if sparse_subjects:
        print("  [选考] 只有部分同学有成绩的科目（保留、不计入总分、未选考者不计缺考）：%s"
              % "、".join(sorted(sparse_subjects)))
    if notes_report["缺失学生"]:
        print("  [缺失] %d 人存在缺失指标：" % len(notes_report["缺失学生"]))
        for m in notes_report["缺失学生"]:
            print("      %s %s → 缺 %s" % (m["学号"], m["姓名"], "、".join(m["缺什么"])))
    if notes_report["缺考学生"]:
        print("  [缺考] %d 人（排名受影响，评语禁用排名类表述）：" % len(notes_report["缺考学生"]))
        for m in notes_report["缺考学生"]:
            print("      %s %s 缺考 %s（原表总分 %s / 排名 %s）"
                  % (m["学号"], m["姓名"], "、".join(m["缺考科目"]),
                     m["原表总分"], m["原表排名"]))
    if notes_report["姓名冲突"]:
        print("  [姓名冲突] %d 条（已按学号归一，需人工核对）：" % len(notes_report["姓名冲突"]))
        for c in notes_report["姓名冲突"]:
            print("      %s：主表「%s」vs 本表「%s」 —— %s"
                  % (c["学号"], c["主表姓名"],
                     c.get("描述表姓名") or c.get("本表写法"), c.get("性质", "")))
    if notes_report["疑似同一人"]:
        print("  [疑似同一人] %d 条（已暂合并，务必人工确认）：" % len(notes_report["疑似同一人"]))
        for s in notes_report["疑似同一人"]:
            print("      「%s」→ 名单「%s」(学号 %s)" % (s["描述表姓名"], s["名单姓名"], s["学号"]))
    if notes_report["未匹配记录"]:
        print("  [未匹配] %d 条（未纳入，需人工确认）：" % len(notes_report["未匹配记录"]))
        for u in notes_report["未匹配记录"]:
            print("      %s %s ← %s（%s）" % (u["学号"], u["姓名"], u["来源"], u["原因"]))
    warn = [n for n in notes_report["机器提示"] if n.startswith("⚠")]
    if warn:
        # ⚠ 开头的提示是「会影响材料完整性」的行动项（如只传了一个成绩文件），
        # 必须直接在控制台露面——埋在 json 里容易被跳过，而它正是静默丢维度的唯一征兆
        print("  [重要提示] %d 条（需读给用户 / 影响材料完整性）：" % len(warn))
        for w in warn:
            print("      " + w)
    print("  [提示] %d 条，详见 roster.json 的「对齐说明」" % len(notes_report["机器提示"]))


if __name__ == "__main__":
    main()
