# -*- coding: utf-8 -*-
"""【第三段 交付】把 comments.json 落成一份「姓名 + 评语」两列的 xlsx，表下方附材料补充小贴士。

交付形态（固定，只出这一个 excel 文件）：
  单工作表「评语表」，A 列姓名、B 列评语；
  数据区下方空一行后是「小贴士」区块，按实际缺料情况说明再补哪几类材料可以把评语写得更详细。
  质检结果（字数/分数名次/贬义词/对账）只在控制台输出，不写进表、不另出报告文件。

硬性保障（这些都是交付事故的高发点）：
  1. 严格按 roster.json 的原表顺序输出，不重排、不丢人
  2. 人数与名单逐一对账：漏写、多写、学号对不上 → 报错并列出
  3. **评语的「姓名」与名单姓名对不上 → 拒绝配对并报硬错误**
     （学号抄错一位 / 从别的班复制粘贴 → 会静默串人，这是交付端最严重的一类事故；
     旧版只按学号对账、从不校验姓名）
  4. 字数越界、出现分数名次、平时序列表述不达标、提到其他学生姓名、定性贬义词 → 逐条预警
  5. 小贴士按「实际缺了哪类材料」动态生成，不写空话；材料给全了就不出现对应提示

本轮修正（针对实测暴露的误报/漏报）：
  · 默认字数区间与 SKILL.md 对齐为 120~180（原默认 100~200 会让字数校验形同虚设）
  · 姓名检测区分「独立出现」与「被汉字包围」：名单里有人叫「安静」时，
    正文写「安静下来再读一遍题」只算低置信提示，不再当成点名硬报
  · 分数检测补上「学科名 + 数字」模式：修掉「语文考了87」这类没有「分」字的漏检；
    同时**豁免平时序列数字**（见 SEQ_MASK_RES）
  · **平时序列表述口径**（用户口径 2026-10-09）：引用平时序列一律写成
    「学科 + 第X次平时成绩 NN 分」，如
    「语文从第一次平时成绩74分提升到第六次平时成绩的87分」。
    这是**唯一**能带「分」字出现的写法（「平时成绩」已把口径说清：过程性、不是本次考试），
    见 PLAIN_SEQ_RES；`seq_style_flags()` 反查另三种不达标写法并给出改法：
    省略式「第1次的 74 涨到第6次的 87」、「平时线」这类指代、以及没写清学科
  · **姓名一致性硬校验**：评语里的姓名与名单姓名不一致（且都非空）→ 拒绝配对 + 硬错误
  · 小贴士改固定编号（1教师描述/2课堂/3作业/4上次对比/5分科逐题/6体质劳动/7荣誉奖状），
    `--skip-tips` 按固定编号跳（旧版按当前位置编号，材料给全时会静默失效；
    另支持负数＝从末尾倒数）
  · 小贴士第 1 条认「往年评语」：有往年评语、但没有本学期教师描述时，
    提示改写成「往年评语可作参考，再补一份**本学期**的教师描述」——
    往年评语是参考、不能替代本学期的事实（见 writing-rules 规则 5）
  · 小贴士加第 7 条「荣誉·奖状」：图片（奖状照片/截图）也能作为材料，提示用户可以直接发图
  · **荣誉表述的材料出处校验**（`award_flags()`）：评语里写了奖项/称号，而该生材料
    （教师描述 + 荣誉奖项）里没有任何荣誉记录 → 预警「疑似虚构」。这是规则 2 放开
    「有荣誉材料才可写竞赛/职务」之后的对应闸门：放开一处，就要有一处兜底
  · 数据区按字数设置行高，避免评语在 Excel/预览里被截断
  · 贬义词闸门扩到 21 个词（补 马虎/粗心/粗枝大叶/拖拉/磨蹭/不努力/不用功/不用心/
    不专心/退步/差劲/态度差/厌学/不及格），否定语境白名单补「没有/没/未」——
    固化语气基调「老师对学生：优点表扬到位、缺点委婉给建议」，预警文案直接给出改法
  · **交付文件的「文档属性」不带生成侧信息**（用户要求 2026-10-12）：openpyxl 会在
    docProps/core.xml 写 creator="openpyxl"、在 docProps/app.xml 把 <Application>
    写死成「Microsoft Excel Compatible / Openpyxl 3.1.5」——老师在
    「文件 → 信息 → 属性」里一眼可见。现在生成时置空属性、落盘后再 scrub 一次
    （只重写 docProps 文本，表内容一个字节不动），并用 `workbook_prop_leaks()`
    回读校验，有残留就报 [警告]。闸门见 scripts/test_output_privacy.py

用法：
  python export_comments.py --roster roster.json --comments comments.json \
    --out 评语表.xlsx --min-len 120 --max-len 180
"""
import argparse
import json
import math
import os
import re
import sys
from collections import Counter

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
except ImportError:
    sys.exit("生成 xlsx 需要 openpyxl，请先安装：pip install openpyxl")

HEAD_FILL = PatternFill("solid", fgColor="DCE9F7")
TIP_FILL = PatternFill("solid", fgColor="FFF9E8")
THIN = Side(style="thin", color="D0D0D0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HAN = re.compile(r"[^\u4e00-\u9fff]")

TIP_TITLE = "小贴士：再补下面这些材料，评语可以写得更详细"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from subjects import SUBJECT_POOL as SUBJ_WORDS  # noqa: E402  学科词表唯一来源（含「道法」等简称）
# 只抓「具体数字」，不抓「名次」「满分」「分数」这类抽象词——
# 「名次往前挪了一截」「听力小测常常满分」都是写作规则明确允许的合法表述，
# 把词本身当违规会造成大面积误报（实测在 40 人示例上误报 11 条）。
SCORE_NUM_RES = [
    (r"\d+\s*分", "含分数"),
    (r"第\s*\d+\s*名", "含名次"),
    (r"(考了|考得|得了|拿了|扣了|丢了|涨了|退了)\s*\d+", "疑似出现分数"),
    (r"(排名|名次|位次)[^，。；！？]{0,2}\d+", "疑似出现名次"),
    (r"\d+\s*(名|位)(?=[，。、；：！？\s]|$)", "疑似出现名次"),
]
# 旧写法「第3次冲到 96」「地理第4次摸到96」（不带「分」）仍被**豁免**，属于兼容兜底：
# 它表达的是过程波动，不是把本次考试分摊到家长面前。但**推荐**写法已是标准式
# 「学科+第X次平时成绩NN分」——`seq_style_flags()` 会把这类省略式提示出来改写。
# 检测前先把这类片段里的数字屏蔽掉（换成 x），免得「学科名后 4 字内有数字」
# 把它误判成「疑似出现分数」。
SEQ_MASK_RES = [
    re.compile(r"第\s*\d+\s*[次回周]"),
    re.compile(r"(?:摸到|冲到|到了|成了|上到|攀到|涨到|升到|回到|落到|掉到|降到|跌到|"
               r"退到|达到|逼近|突破)\s*\d+(?:\.\d+)?"),
    re.compile(r"(?:从|由)\s*\d+(?:\.\d+)?\s*(?:到|至|→|~|—|-)\s*\d+(?:\.\d+)?"),
]

# **推荐（也是唯一允许带「分」字）的平时序列表述**（用户口径 2026-10-09）：
#     语文从第一次平时成绩74分提升到第六次平时成绩的87分。
# 「第一次 / 第六次 + 平时成绩 + NN分」把三件事一次说清：哪一科、第几次、是不是平时成绩。
# 旧写法「从第1次的 74 一直涨到第6次的 87」读者看不出这是平时成绩（会当成期末分），
# 也看不出是哪一科——所以标准式里的「NN分」豁免「含分数」硬规则，别的「NN分」照报。
PLAIN_SEQ_RES = [
    re.compile(r"第\s*[0-9一二三四五六七八九十]+\s*次\s*平时(?:成绩|分数|分)\s*的?\s*"
               r"\d+(?:\.\d+)?\s*分"),
    re.compile(r"平时(?:成绩|分数)\s*的?\s*[^，。；！？]{0,10}?\d+(?:\.\d+)?\s*分"),
]


def mask_plain_seq(body):
    """屏蔽标准式「第N次平时成绩 NN 分」——它是唯一允许带「分」字的平时序列写法。

    只屏蔽这一种；「冲到 96 分」「期末考了 87 分」里没有「平时成绩」口径，照旧上报。
    """
    s = body or ""
    for pat in PLAIN_SEQ_RES:
        s = pat.sub(lambda m: re.sub(r"\d", "x", m.group(0)), s)
    return s


def mask_sequence_numbers(body):
    """把「第3次冲到 96」这类允许的平时序列数字换成 x，交给后续规则忽略。"""
    s = body or ""
    for pat in SEQ_MASK_RES:
        s = pat.sub(lambda m: re.sub(r"\d", "x", m.group(0)), s)
    return s


# 平时序列表述口径的机检（用户口径 2026-10-09）——标准式：**学科 + 第X次平时成绩 NN 分**。
# 反查三类不达标写法，命中只提示并给出改法，不改写：
#   A 省略式「第1次的 74 涨到第6次的 87」——看不出是平时成绩、也看不出哪一科
#   B 写了平时成绩+数字，但全篇没出现学科名
#   C 用「平时线」这类自造指代代替「平时成绩」
SEQ_ABBR_RE = re.compile(r"第\s*[0-9一二三四五六七八九十]+\s*次")
SEQ_PLAIN_NUM_RE = re.compile(r"平时(?:成绩|分数)?[^，。；！？]{0,6}\d")


# 语气基调（老师对学生：优点表扬到位、缺点委婉给建议）的机检闸门——
# 只收「定性负面判断」的词：评价的是这个人/他的态度，而不是可执行的动作。
# 刻意不收的：单字「差」「弱」（「你差的不是能力」「差的时候能错一半」都是合法表述）、
# 「放弃」（「等于放弃了回头检查的机会」）、「内向/自卑/偏科」（易误伤且未必是贬义）。
# 加词前先拿 references/comments.json（40 条优质评语）跑一遍，必须仍为 0 命中。
NEG_WORDS = (
    "很差", "太差", "差劲", "态度差", "态度不端正",
    "不认真", "不努力", "不用功", "不用心", "不专心",
    "马虎", "粗心", "粗枝大叶", "拖拉", "磨蹭",
    "退步", "不及格", "厌学", "孤僻", "笨", "懒",
)
# 否定语境白名单（"不是笨""谈不上懒""没有退步"属鼓励性表述，不算问题）。
# 只认紧邻否定（词前 4 字内、且以否定词收尾）："老师没有说你粗心"这类隔了人称的说法仍会预警——
# 方向是对的（宁可提示，不愿漏掉真正的定性贬义），它只是软提示，人工扫一眼即可。
NEG_PRE_RE = re.compile(r"(不是|不算|谈不上|并非|别|没有|没|不|未)$")
CHARS_PER_LINE = 46

# 荣誉/获奖类表述的词表 —— 规则 2「禁止虚构」的机检闸门之一。
# 背景：用户上传奖状/证书照片后，`荣誉奖项` 成了**可引用的证据**（规则 2 对它开了口子）；
# 开了这个口子，就必须有东西兜住「材料里没有、评语里却写了荣誉」。
# 只收**明确的奖项与称号**，刻意不收的（会大面积误报）：
#   · 「优秀」「进步」「表现好」——泛词，绝大多数是程度描述而非荣誉
#   · 光「奖」/「竞赛」/「比赛」——「参加比赛」「题很难的竞赛」都不是获奖陈述
AWARD_WORDS = (
    "奖状", "证书", "奖杯", "奖牌", "奖学金", "获奖", "荣获",
    "一等奖", "二等奖", "三等奖", "特等奖", "优秀奖",
    "冠军", "亚军", "季军",
    "三好学生", "三好生", "优秀班干", "优秀干部", "优秀团员",
    "优秀少先队员", "文明学生", "先进个人", "荣誉称号",
)


def han_len(s):
    return len(HAN.sub("", s or ""))


def is_zh(c):
    return bool(c) and "\u4e00" <= c <= "\u9fff"


def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def norm_name_cmp(s):
    """对比用姓名归一化：去空白/全角空格、去括号备注（与 prepare_roster 的口径一致）。"""
    s = re.sub(r"[\s\u3000]+", "", str(s or ""))
    return re.sub(r"[（(].*?[)）]", "", s).strip()


def name_hits(body, own_name, all_names):
    """查正文里是否出现其他学生姓名。

    返回 (高置信, 低置信)：
      · 高置信 —— 姓名左右都不是汉字（独立出现），基本可以确定是点名
      · 低置信 —— 姓名被汉字包住（「安静下来」「许多时候」），可能只是常用词，需人工自查
    另外：姓名被更长的名单姓名包含时不计（正文写「王浩然」，不因名单里还有「王浩」而报警）。
    """
    hard, soft = [], []
    for nm in all_names:
        if not nm or nm == own_name:
            continue
        i = body.find(nm)
        while i >= 0:
            if not any(o != nm and nm in o and o in body for o in all_names):
                l = body[i - 1] if i > 0 else ""
                r = body[i + len(nm):i + len(nm) + 1]
                (soft if (is_zh(l) or is_zh(r)) else hard).append(nm)
            i = body.find(nm, i + 1)
    return sorted(set(hard)), sorted(set(soft))


def score_flags(body):
    """查正文里是否出现分数/名次。

    判据是「具体数字」，不是「词」：
      · 「87分」「第3名」「考了87」「名次第12」都算
      · 「名次往前挪了一截」「听力小测常常满分」「比分数重要得多」不算——
        这些是写作规则里允许的程度描述，按词判会造成大面积误报
      · 「第3次冲到 96」（不带「分」的旧式序列数字）不算——见 SEQ_MASK_RES，
        但它已不是推荐写法，`seq_style_flags()` 会提示改成标准式
      · 「语文第六次平时成绩87分」（标准式）不算——见 PLAIN_SEQ_RES；
        但「第3次冲到96分」「期末语文考了87分」这类照报（没写平时成绩口径）
    另外抓「学科名 + 4 字内数字」：这是实测跑掉最多的一类（「语文考了87」不带「分」字）。
    """
    raw = body or ""
    masked = mask_sequence_numbers(raw)
    plain_masked = mask_plain_seq(masked)
    # 「含分数」只在**原文**上屏蔽标准式平时成绩写法后判：口径是「只有标准式的 NN 分允许出现」，
    # 所以「第3次冲到96分」「期末考了87分」照报；「第3次冲到 96」（不带「分」）不算分数。
    plain_raw = mask_plain_seq(raw)
    flags = []
    for pat, tag in SCORE_NUM_RES:
        target = plain_raw if tag == "含分数" else masked
        if re.search(pat, target):
            flags.append(tag)
    for s in SUBJ_WORDS:
        hit = False
        for m in re.finditer(re.escape(s), plain_masked):
            if re.search(r"\d", plain_masked[m.end():m.end() + 4]):
                flags.append("疑似出现分数（「%s」后紧跟数字）" % s)
                hit = True
                break
        if hit:
            break
    return flags


def seq_style_flags(body):
    """查平时序列的**表述口径**是否达标（用户口径 2026-10-09）。

    标准式（唯一推荐）：**学科 + 第X次平时成绩 NN 分**
        语文从第一次平时成绩74分提升到第六次平时成绩的87分
    命中下面三类只提示、不改写，预警文案里直接给改法。实测 40 人真实材料首稿有 5 条踩到 A。
    """
    b = body or ""
    flags = []
    # A 省略式：「第1次的 74 一直涨到第6次的 87」——读者看不出是平时成绩，也看不出哪一科
    for m in SEQ_ABBR_RE.finditer(b):
        seg = re.split(r"[，。；！？、]", b[m.end():m.end() + 12])[0]
        if re.search(r"\d", seg) and "平时" not in seg:
            flags.append("平时序列表述是省略式（「%s%s…」）——请写成"
                         "「学科+第X次平时成绩NN分」" % (m.group(0), seg.strip()[:6]))
            break
    # B 有平时成绩的数字、但全篇没出现任何学科名 → 补上学科
    if SEQ_PLAIN_NUM_RE.search(b) and not any(s in b for s in SUBJ_WORDS):
        flags.append("平时成绩的数字没写清是哪一科——请写成"
                     "「学科+第X次平时成绩NN分」")
    # C 自造指代：用「平时线」代替「平时成绩」
    if "平时线" in b:
        flags.append("「平时线」是自造说法——请写成「学科+第X次平时成绩NN分」")
    return flags


def award_flags(body, materials):
    """查「评语里写了荣誉、材料里却没有」——规则 2 禁虚构的机检闸门。

    为什么需要它：用户上传奖状/证书后，`荣誉奖项` 成了**可直接引用的证据**，
    规则 2 因此对它开了一个口子（有材料就能写竞赛/职务）。开了口子就要有兜底——
    否则「去年听家长提过、顺手写上」这类虚构会从新口子漏进来。

    判据刻意保守（**不误报是前提**）：
      · 正文出现 AWARD_WORDS 里的**明确奖项/称号**才触发
      · 该生的「教师描述 + 荣誉奖项」里只要出现同类词就算有出处，直接放行
      · **「往年评语」不算出处**——规则 5 要求往年的事须在今年材料里能对上；
        只凭去年写过就写成本学期事实，正是这条闸门要拦的
    命中只提示、不改写；确认没有出处就删掉这句。
    """
    b = body or ""
    hit = [w for w in AWARD_WORDS if w in b]
    if not hit:
        return []
    mat = materials or ""
    if any(w in mat for w in AWARD_WORDS):
        return []
    return ["评语里出现荣誉/获奖类表述（%s），但该生材料里找不到出处——"
            "请核对：有奖状/证书/荣誉材料才算数，否则属虚构（规则 2）；"
            "若确实有，请把奖状照片或荣誉表一并给我" % "、".join(hit)]


def build_tips(students):
    """按实际缺料情况生成小贴士，返回 [(固定编号, 文案), ...]。

    编号是**固定编号**、不随缺料多少漂移：
      1 教师个别描述 / 2 课堂表现 / 3 作业统计 / 4 上次总分·排名 / 5 分科逐题 /
      6 体质·劳动 / 7 荣誉·奖状
    `--skip-tips` 就是按这个编号跳的。**编号一旦发布就不再复用**（缺料时该条缺席，
    但编号不回收），否则老用户的 `--skip-tips` 会静默指到别处。
    旧版按「当前列表里的位置」编号：材料一给全，「分科逐题」从 5 掉到 1，
    `--skip-tips 5,6` 就静默失效了（文档却写着"固定收尾两条永远排在最后"）。
    """
    tips = []
    has_hw = any(s.get("作业") for s in students)
    has_cls = any(s.get("课堂") for s in students)
    has_note = any((s.get("教师描述") or "").strip() for s in students)
    has_past = any((s.get("往年评语") or "").strip() for s in students)
    has_award = any((s.get("荣誉奖项") or "").strip() for s in students)
    has_prev_total = any(s.get("成绩", {}).get("上次总分") is not None for s in students)
    has_prev_rank = any(s.get("成绩", {}).get("上次排名") is not None for s in students)

    if not has_note:
        if has_past:
            tips.append((1,
                "已收到《往年评语》，可作个性化描述的参考（孩子身上稳定的特点、去年提过的期待）；"
                "若还能补一份**本学期**的《教师个别描述》会更好——"
                "往年评语写的是孩子去年的样子，本学期的变化需要本学期的材料，"
                "否则评语容易写成去年那一条的翻版。"))
        else:
            tips.append((1,
                "再给一份《教师个别描述》——班主任或科任各写一两句就够，哪怕只是"
                "「跑完八百米给同学递水」这样一个小动作。评语里就会出现只属于这个孩子的画面，"
                "从「看成绩」变成「写人」，这是最能提升评语质量的一份材料。"))
    if not has_cls:
        tips.append((2,
            "再给一张《课堂表现统计表》（发言次数、专注度、小组合作、课堂纪律）——"
            "可以补上「品格与集体」这一维度，写出课堂参与、同伴合作、守纪表现。"))
    if not has_hw:
        tips.append((3,
            "再给一张《作业统计表》（应交/实交次数、按时提交率、订正完成率）——"
            "评语就能从「成绩稳」写到「作业习惯稳」，把按时上交、订正及时这类细节落到实处。"))
    if not has_prev_total and not has_prev_rank:
        tips.append((4,
            "再给上一次考试的总分与排名（期中或上学期期末均可）——"
            "评语就能写出进退趋势，比如「比上学期往前走了一截」。"))
    elif has_prev_total and not has_prev_rank:
        tips.append((4,
            "再补上上次考试的班级排名——目前只能比总分的进退，"
            "补齐排名之后才能写出名次的变化。"))
    tips.append((5,
        "再给分科逐题得分或知识点得失明细——建议就能落到具体章节，"
        "「圆锥曲线那道大题一步没漏」「作文每次都写满」比笼统的「继续努力」有力得多。"))
    tips.append((6,
        "若评语用于「三好学生」等评选，再给体育/体质测试、劳动或志愿服务记录——"
        "就能覆盖体质与其他维度，不让评价只落在学习上。"))
    if not has_award:
        tips.append((7,
            "若有奖状、证书或荣誉榜（校内评优、学科竞赛、社会实践等），**拍照或截图发来**即可——"
            "评语里就能写上具体的那一项荣誉，而不只是「表现优秀」。"
            "图片我会先读出来列成清单跟你核对，确认无误再写进评语。"))
    return tips


# --------------------------------------------------------------------------- #
# 交付文件的「文档属性」不得带生成侧信息（用户要求 2026-10-12）
#
# 事故形态：openpyxl 写出的 xlsx 里，`docProps/core.xml` 的 <dc:creator> 默认是
# "openpyxl"，`docProps/app.xml` 的 <Application> 写死成
# "Microsoft Excel Compatible / Openpyxl 3.1.5"。老师或家长在
# 「文件 → 信息 → 属性」里一眼就能看见"作者：openpyxl"与生成库的精确版本号——
# 这是工具侧的元数据，跟评语内容毫无关系，不该随交付物外流。
#
# 三条固定口径：
#   ① 只清**值**，不动交付表的任何内容（表里本来就没有内部字段名，
#      见 scripts/test_output_privacy.py 的闸门）
#   ② **清空**而不是编造：creator 置空，不写"班主任""某某中学"这类假值
#   ③ 落盘后必须**回读校验**，有残留就在控制台打 [警告]（不静默放过）
# --------------------------------------------------------------------------- #
PROP_ATTRS = ("creator", "lastModifiedBy", "title", "subject",
              "description", "keywords", "category")
# docProps 里要清空的元素（core.xml 与 app.xml）
PROP_TAGS = ("dc:creator", "cp:lastModifiedBy", "dc:title", "dc:subject",
             "dc:description", "cp:keywords", "cp:category",
             "Application", "AppVersion")
# 交付 xlsx 里出现这些串 = 生成侧元数据残留
PROP_LEAK_WORDS = ("openpyxl", "microsoft excel compatible", "workbuddy")


def harden_workbook_props(wb):
    """把工作簿的文档属性全部置空（生成时就把 core.xml 写干净）。

    覆盖 openpyxl 默认的 creator="openpyxl"。`company` **不是** openpyxl 的真实属性
    （设了也不会序列化），不要写进来。
    """
    props = wb.properties
    for a in PROP_ATTRS:
        if hasattr(props, a):
            setattr(props, a, "")
    return wb


def neutralize_extended_props():
    """让 openpyxl 写出的 docProps/app.xml 不带库名与版本号（幂等）。

    <Application> 是 openpyxl 在 `openpyxl/writer/excel.py` 里**现造对象时写死**的
    （`ExtendedProperties.__init__` 里的 f"Microsoft Excel Compatible / Openpyxl {版本}"），
    workbook 属性里没有对应开关，所以只能在 `save()` 前改写这个类。
    即便这段失效（换 openpyxl 版本改了内部结构），落盘后的 `scrub_xlsx_props()`
    仍会兜住，`workbook_prop_leaks()` 会回读校验并报警——不会静默放过。
    """
    try:
        from openpyxl.packaging.extended import ExtendedProperties
    except Exception:                       # 内部结构变了也不该让出表失败
        return False
    if getattr(ExtendedProperties, "_cnki_neutralized", False):
        return True
    _orig_init = ExtendedProperties.__init__

    def _init(self, *a, **kw):
        _orig_init(self, *a, **kw)
        self.Application = ""
        self.AppVersion = ""

    ExtendedProperties.__init__ = _init
    ExtendedProperties._cnki_neutralized = True
    return True


def _blank_xml_tag(xml, tag):
    """把 <tag>任意内容</tag> 清成空元素；自闭合写法原样保留。"""
    pat = re.compile(r"(<%s(?:\s[^>]*)?>).*?(</%s>)" % (re.escape(tag), re.escape(tag)),
                     re.S)
    return pat.sub(r"\1\2", xml)


def scrub_xlsx_props(path):
    """落盘后兜底：清掉 xlsx 里 docProps 的生成侧元数据（返回被处理的条目名）。

    只重写 `docProps/*.xml` 的文本，其余条目**原样搬运**——表内容、样式、合并单元格
    一个字节都不动（zip 结构自描述，不存在偏移失配问题）。
    """
    import zipfile
    tmp = path + ".scrubtmp"
    hits = []
    with zipfile.ZipFile(path) as zin:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.startswith("docProps/") and item.filename.endswith(".xml"):
                    txt = data.decode("utf-8")
                    new = txt
                    for tag in PROP_TAGS:
                        new = _blank_xml_tag(new, tag)
                    if new != txt:
                        hits.append(item.filename)
                        data = new.encode("utf-8")
                zout.writestr(item, data)
    os.replace(tmp, path)
    return hits


def workbook_prop_leaks(path):
    """回读交付 xlsx，返回仍残留的生成侧串（空列表 = 干净）。"""
    import zipfile
    leaks = []
    try:
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                txt = z.read(n).decode("utf-8", "replace").lower()
                for w in PROP_LEAK_WORDS:
                    if w in txt:
                        leaks.append("%s 里的 %s" % (n, w))
    except Exception as e:                  # zip 损坏等也要报出来，不能静默
        leaks.append("读取 %s 失败：%s" % (os.path.basename(path), e))
    return leaks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", required=True)
    ap.add_argument("--comments", required=True)
    ap.add_argument("--out", default="评语表.xlsx")
    ap.add_argument("--min-len", type=int, default=120,
                    help="汉字数下限（默认 120，与 SKILL.md 的口径一致）")
    ap.add_argument("--max-len", type=int, default=180,
                    help="汉字数上限（默认 180，与 SKILL.md 的口径一致）")
    ap.add_argument("--skip-tips", default="",
                    help="跳过表下小贴士：正数=固定编号（1教师描述 2课堂 3作业 4上次对比 "
                         "5分科逐题 6体质劳动 7荣誉奖状），负数=从末尾倒数（-1 是最后一条）")
    ap.add_argument("--strict", action="store_true", help="有硬错误时非零退出")
    args = ap.parse_args()

    roster = load_json(args.roster)
    cdoc = load_json(args.comments)
    students = roster["roster"]
    comments = cdoc.get("comments", cdoc if isinstance(cdoc, list) else [])
    cmap = {str(c.get("学号", "")).strip(): c for c in comments}
    # 宽容一点：主键写歪（空着／写成姓名）时用姓名回接，但仅在该姓名于名单里唯一时生效，
    # 重名学生一律要求把主键写清楚——否则可能把评语挂到同名的另一位头上。
    _name_cnt = Counter(s["姓名"] for s in students if s["姓名"])
    _by_name = {}
    for c in comments:
        nm = str(c.get("姓名", "")).strip()
        if nm:
            _by_name[nm] = c
    resolved, aliased, mismatch, no_name = {}, [], [], 0
    for s in students:
        k = s["学号"]
        if k in cmap:
            c = cmap[k]
            cnm = norm_name_cmp(c.get("姓名", ""))
            snm = norm_name_cmp(s["姓名"])
            if not cnm:
                no_name += 1
            elif snm and cnm != snm:
                # 交付端最严重的一类事故：学号抄错一位、或从别的班文件复制粘贴，
                # 评语的姓名与名单姓名对不上——绝不能把这段文字挂上去。
                # 旧版只按学号对账、**从不校验姓名**，会静默串人且零预警。
                mismatch.append({"学号": k, "名单姓名": s["姓名"],
                                 "评语姓名": str(c.get("姓名", "")).strip()})
                continue
            resolved[k] = c
            continue
        nm = s["姓名"]
        if nm and _name_cnt[nm] == 1 and nm in _by_name:
            resolved[k] = _by_name[nm]
            aliased.append(nm)

    errors, warns = [], []
    if mismatch:
        errors.append(
            "评语里的「姓名」与名单对不上 %d 条，已**拒绝配对**"
            "（不把这段文字挂到任何学生头上）：%s\n"
            "      请核对是不是学号串行、或从别处复制粘贴过来的；姓名与学号必须属于同一个人。"
            % (len(mismatch),
               "；".join("%s 名单「%s」← 评语写「%s」"
                         % (m["学号"], m["名单姓名"], m["评语姓名"]) for m in mismatch)))
    # 1. 对账
    missing = [s for s in students if s["学号"] not in resolved]
    _used = {id(c) for c in resolved.values()}
    extra = [c for c in comments if id(c) not in _used]
    _roster_ids = {s["学号"] for s in students}
    if missing:
        errors.append("漏写 %d 人：%s" % (len(missing),
                                      "、".join("%s(主键 %s)" % (s["姓名"], s["学号"])
                                                for s in missing)))
    if extra:
        def _why(c):
            return ("（姓名与名单不符，见上）"
                    if str(c.get("学号", "")).strip() in _roster_ids else "（主键不在名单内）")
        errors.append("多出 %d 条：%s"
                      % (len(extra), "、".join(
                          "%s %s%s" % (c.get("学号"), str(c.get("姓名", "") or "").strip(), _why(c))
                          for c in extra)))
    if no_name and roster.get("meta", {}).get("主键") == "学号":
        warns.append({"学号": "-", "姓名": "-",
                      "问题": ["有 %d 条评语没写「姓名」，无法交叉校验是否串人——"
                               "建议把姓名一并写上（脚本会用它与名单核对）" % no_name]})

    # 2. 逐条体检
    all_names = {s["姓名"] for s in students}
    rows = []
    for i, s in enumerate(students, 1):
        c = resolved.get(s["学号"], {})
        body = (c.get("评语正文") or c.get("正文") or "").strip()
        n = han_len(body)
        flags = []
        if not body:
            flags.append("正文为空")
        else:
            if n < args.min_len:
                flags.append("字数偏少(%d)" % n)
            if n > args.max_len:
                flags.append("字数偏多(%d)" % n)
            flags.extend(score_flags(body))
            flags.extend(seq_style_flags(body))
            # 荣誉表述必须有材料出处（教师描述 or 荣誉奖项）；
            # 「往年评语」刻意不算——规则 5 要求往年的事在今年材料里能对上
            flags.extend(award_flags(
                body, " ".join(str(s.get(k) or "")
                               for k in ("教师描述", "荣誉奖项"))))
            hard, soft = name_hits(body, s["姓名"], all_names)
            if hard:
                flags.append("提到其他学生：%s" % "、".join(hard))
            if soft:
                flags.append("疑似提到其他学生：%s（可能只是常用词，请自查）"
                             % "、".join(soft))
            # 语气基调机检：定性贬义（带否定语境识别："不是笨""谈不上懒""没有退步"属鼓励性表述）
            for w in NEG_WORDS:
                for m in re.finditer(re.escape(w), body):
                    pre = body[max(0, m.start() - 4):m.start()]
                    if NEG_PRE_RE.search(pre):
                        continue
                    flags.append("含定性贬义词「%s」（语气基调要求改成可执行的下一步）" % w)
                    break
        if flags:
            warns.append({"学号": s["学号"], "姓名": s["姓名"], "问题": flags})
        rows.append({"序号": i, "姓名": s["姓名"], "评语正文": body, "字数": n})

    tips = build_tips(students)
    # 跳过小贴士：正数 = 固定编号（1教师描述/2课堂/3作业/4上次对比/5分科逐题/6体质劳动/7荣誉奖状）；
    # 负数 = 从末尾倒数（-1 是最后一条）。编号固定，不随缺料多少漂移。
    skip = set()
    for x in args.skip_tips.split(","):
        x = x.strip()
        if not x:
            continue
        try:
            v = int(x)
        except ValueError:
            continue
        if v > 0:
            skip.add(v)
        elif v < 0 and len(tips) + v >= 0:
            skip.add(tips[len(tips) + v][0])
    if skip:
        tips = [(tid, t) for tid, t in tips if tid not in skip]

    # 3. 写 xlsx：单表，A 列姓名 + B 列评语，下方小贴士
    wb = Workbook()
    harden_workbook_props(wb)          # 文档属性置空（openpyxl 默认 creator="openpyxl"）
    neutralize_extended_props()        # app.xml 的 <Application> 不带库名与版本号
    ws = wb.active
    ws.title = "评语表"
    ws.append(["姓名", "评语"])
    for r in rows:
        ws.append([r["姓名"], r["评语正文"]])
    last_data_row = ws.max_row

    tip_title_row = last_data_row + 2
    ws.cell(row=tip_title_row, column=1, value=TIP_TITLE)
    ws.merge_cells(start_row=tip_title_row, start_column=1,
                   end_row=tip_title_row, end_column=2)
    for k, (tid, t) in enumerate(tips):
        rr = tip_title_row + 1 + k
        ws.cell(row=rr, column=1, value="%d. %s" % (tid, t))
        ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=2)

    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 96
    # 表头
    for c in (1, 2):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True)
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER
    ws.row_dimensions[1].height = 20
    # 数据区（按字数预估行高，避免评语被截成一两行显示）
    for r in rows:
        rr = r["序号"] + 1
        for c in (1, 2):
            cell = ws.cell(row=rr, column=c)
            cell.border = BORDER
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[rr].height = 16 + max(1, math.ceil(r["字数"] / CHARS_PER_LINE)) * 17
    # 小贴士区：合并整行 + 浅黄底 + 自动换行 + 预留行高，保证预览/打印不截字
    ws.cell(row=tip_title_row, column=1).font = Font(bold=True, color="8A5A00")
    ws.row_dimensions[tip_title_row].height = 20
    for rr in range(tip_title_row + 1, tip_title_row + 1 + len(tips)):
        for c in (1, 2):
            cell = ws.cell(row=rr, column=c)
            cell.fill = TIP_FILL
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        # 提示文字较长，按 110 字/行预估
        txt = str(ws.cell(row=rr, column=1).value or "")
        ws.row_dimensions[rr].height = 16 + max(1, math.ceil(han_len(txt) / 108)) * 17
    # 小贴士标题行也铺底色
    for c in (1, 2):
        ws.cell(row=tip_title_row, column=c).fill = TIP_FILL
    ws.freeze_panes = "A2"

    wb.save(args.out)
    scrub_xlsx_props(args.out)              # 落盘后兜底：清 docProps 里的生成侧元数据
    prop_leaks = workbook_prop_leaks(args.out)   # 回读校验，有残留必须报出来

    # 4. 控制台汇报（质检信息只在这里出现，不进表）
    n = len(rows)
    lens = [r["字数"] for r in rows if r["字数"]]
    print("评语表已生成 -> %s" % os.path.abspath(args.out))
    print("  表结构：单表「姓名 + 评语」两列 %d 条；下方附 %d 条材料补充小贴士（序号为固定编号）"
          % (n, len(tips)))
    print("  人数：%d（名单 %d）　字数：最短 %d / 最长 %d / 平均 %.1f　区间校验 %d~%d"
          % (n, len(students), min(lens) if lens else 0, max(lens) if lens else 0,
             sum(lens) / len(lens) if lens else 0, args.min_len, args.max_len))
    if aliased:
        print("  [对账] %d 条没有写主键、已按姓名接上（%s）—— 下次请直接把 roster.json 的主键抄进「学号」"
              % (len(aliased), "、".join(aliased)))
    lack = roster.get("对齐说明", {}).get("缺失学生") or []
    if lack:
        print("  [材料] %d 人有缺失指标（详见 roster.json 的「对齐说明」，"
              "评语中不得引用其缺失的那类材料）" % len(lack))
    if prop_leaks:
        print("\n  [警告] 交付表的文档属性里仍有生成侧标记：%s——"
              "请在「文件 → 信息 → 属性」里核对，必要时重跑出表。" % "；".join(prop_leaks))
    else:
        print("  文档属性：已清空（发出去的文件在「文件 → 信息 → 属性」里看不到生成工具）")
    print("\n  [小贴士] 已写入表下方：")
    for tid, t in tips:
        print("    %d. %s" % (tid, t))
    if errors:
        print("\n  [硬错误] ")
        for e in errors:
            print("    × %s" % e)
    if warns:
        print("\n  [预警] %d 条有问题标记：" % len(warns))
        for w in warns:
            print("    ! %s %s → %s" % (w["学号"], w["姓名"], "／".join(w["问题"])))
    if not errors and not warns:
        print("\n  全部通过：人数对账一致、字数达标、无分数名次、平时序列表述合规、"
              "荣誉表述均有材料出处、无定性贬义词。")
    if errors and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
