#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP 数据适配层 —— 把「CNKI 基础教育」MCP 的原始返回，标准化为 homework_kit 的输入格式。

数据入口唯一：WorkBuddy 连接器里的 **CNKI 基础教育（edu）MCP**。
题库（tk*）与学术文献（searchVectorBJ）都必须走它，不允许用本地文件或公开检索拼题库。

设计原则：
1. 本脚本【不做网络请求】。MCP 工具由 Agent 在会话里调用，把原始 JSON 落盘后交给本脚本清洗。
2. 接口名、参数、学科码全部集中在文件顶部的常量表，后期换接口只改这几张表。
3. 输出格式严格对齐 homework_kit.route / validate 的期望，可直接串联。
4. 文献接口【不返回作者 / 刊名 / 卷 / 页码】。本脚本只结构化它能给的（篇名、摘要、年份、期号），
   其余一律留 None 并记进 need_fields，交由补齐环节按篇名核实后回填。
   缺字段渲染为灰色【待补充】——缺是待补，填错是编造，后者比没有溯源更糟。

典型串联：
    1) Agent 调 MCP 拿原始 JSON -> raw_bank.json / raw_lit.json
    2) python mcp_adapters.py bank --raw raw_bank.json --out bank.json
    3) python mcp_adapters.py lit  --raw raw_lit.json --out sources.json
       （文献缺作者/刊名：按篇名核实后写 fill.json，再 --fill fill.json 回填）
    4) 把 bank.json / sources.json 塞进 params.json -> homework_kit.py route -> validate
"""

import argparse
import datetime as _dt
import json
import re
import sys

# ============================================================================
# 【连接器标识】换连接器 / 改显示名，只改这一行
#
# ⚠⚠ 最容易踩的坑：工具名前缀来自连接器在 WorkBuddy 里的【显示名】，
#    不是 ~/.workbuddy/mcp.json 里的 key。而且【用户在连接器管理页重命名，
#    前缀会跟着变】——本机已实测变过两次（edu -> 知网基教 -> edu）。
#    前缀写错的表现是「ToolSearch 查不到」——会被误判成「接口坏了 / 报 500」，
#    实际是从来就调错了名字。改前缀只改下面一行，不要去全文替换工具名。
#
#    不确定当前前缀是什么时：跑 `reconcile --tools tools.json`，
#    它会用观测到的工具名反推真实前缀并直接告诉你该改成什么。
# ============================================================================
MCP_PROVIDER = "edu"               # 连接器显示名 -> 工具前缀 mcp__<显示名>__
MCP_CONFIG_KEY = "edu"             # 仅用于人工排查 mcp.json，不参与拼工具名
MCP_PROVIDER_HISTORY = ["edu", "知网基教"]   # 历史用过的显示名，reconcile 会一并核对


def full_tool(short):
    """短名 -> 工具全名。登记表里一律存短名，保证前缀只在上面一行定义。"""
    return "mcp__%s__%s" % (MCP_PROVIDER, short)


# ============================================================================
# 【接口登记表】新增 / 下线接口只改这一张表
# tool      : 短名（全名由 full_tool() 拼出）
# status    : ok=实测可用 / weak=能用但有坑 / todo=已暴露但未接 / new=未登记过的新接口
#
# ⚠ 这张表是【静态的】，不会自动感知连接器新增的接口。
#   每次升级连接器、或怀疑有漏网接口时，跑 reconcile 子命令做一次对账：
#       Agent 调 ToolSearch 列出当前工具 -> 落盘 tools.json
#       python mcp_adapters.py reconcile --tools tools.json
#   它会报出「登记了但连不上」与「连得上但没登记」两类偏差。
# ============================================================================
MCP_ENDPOINTS = {
    # ---------------------------------------------------------------- 题目检索
    "search_question": {
        "tool": "tkSearchQuestion",
        "params": {"keyword": "关键词(必填)", "subjectCode": "学科码", "type": "题型(0=不限)",
                   "pi": "页码", "ps": "每页条数(上限10)"},
        "returns": "SID/CateName/Label/Content/Options/Answers/DisplayAnswer/Degree/Date",
        "status": "ok",
        "note": "题库主力接口。两个坑：① keyword 含空格会 400，必须拆成单个词分多次检索；"
                "② ps 上限 10，候选不够就翻 pi 或换关键词，别指望一次拿全。Degree 是 0-1 浮点难度。",
        "feeds": "route 的 bank 候选题",
    },
    "search_question_by_point": {
        "tool": "tkSearchSubjectQuestion",
        "params": {"subjectCode": "学科码(必填)", "point": "考点中文名数组(必填)",
                   "ct": "题型(0=不限)", "dg": "难度档 易11/较易12/中档13/较难14/难15",
                   "yr": "年份(2023，多个逗号分隔，0=不限)", "so": "试题来源",
                   "pi": "页码", "ps": "每页条数(上限10)"},
        "returns": "与 tkSearchQuestion 同结构，另多 SourceReports/PaperCount/RealCount",
        "status": "ok",
        "note": "【按考点取题，比关键词检索准得多】——keyword 检索会把「综合题只嵌一问目标考点」"
                "的题混进来（八年级浮力误选热机效率题的病根在这）。"
                "point 要先从 tkPoint 拿；dg/yr 能直接筛难度和年份，可省掉事后按 Degree 分档。"
                "比关键词检索多返回三个字段：SourceReports（完整试卷名，真题新鲜度以此为准）、"
                "RealCount（真实考试引用次数）、PaperCount（收录试卷数）。"
                "注意：dg 难度档方向存疑（标注 11=易(0.8~1.0) 与 Degree 越大越难相反），"
                "只用它筛选，定档一律用返回的 Degree。",
        "feeds": "route 的 bank 候选题（推荐优先于 keyword 检索）",
    },
    "question_same": {
        "tool": "tkQuestionSame",
        "params": {"SID": "原题 SID(必填)", "subjectCode": "学科码(必填)", "num": "相似题数量(必填,≤5)"},
        "returns": "同考点相似题列表",
        "status": "todo",
        "note": "给一道真题找同考点变式，可直接喂 variants 子命令做一题多变式包。"
                "【价值在于它是由服务端算的相似题，不用我们按 Degree 猜难度】，num 上限 5。",
        "feeds": "variants 变式包",
    },
    "question_analysis": {
        "tool": "tkQuestionAnalysis",
        "params": {"SID": "试题ID(必填)", "subjectCode": "学科码(必填)"},
        "returns": "Method(详解)/Analyse(简析)/Discuss(点评)/Points(考点)/Topics(专题)/DisplayAnswer",
        "status": "ok",
        "note": "【补上了题库最大的短板】。两个搜题接口只带回答案，Analyse/Method/Discuss 全是空字符串，"
                "所以过去作业单的 analysis 全靠模型写，第 14 条验算成了模型自证。"
                "Points/Topics 只有这个接口回填（搜题返回的 Points 是空数组）。"
                "接入方式：原始返回先过 analysis 子命令，再用 bank --analysis 按 SID 合并；"
                "合并后校验器用官方答案做交叉校验（retrieve 不符阻塞，adapt 变了未说明提醒）。"
                "不是每题都有解析，返回为空的题不得编解析。",
        "feeds": "metadata.official_analysis / official_answer / points / topics",
    },
    # ---------------------------------------------------------------- 元数据字典
    "list_subject": {
        "tool": "tkSubject",
        "params": {},
        "returns": "subjectCode/subjectName 全量学科表",
        "status": "ok",
        "note": "无参数。学科名带学段前缀（如「初中物理」而非「物理」），所以学科码必须学段+学科二维查表。",
        "feeds": "学科码解析",
    },
    "list_point": {
        "tool": "tkPoint",
        "params": {"subjectCode": "学科码"},
        "returns": "三级知识点树 Name/Desc/Children",
        "status": "weak",
        "note": "【返回极大】（初中数学 30 万字符级，会触发输出截断落盘）。"
                "只按需用 point 子命令抽命中项，不要把整棵树读进上下文。"
                "抽出来的 Name 可直接喂 tkSearchSubjectQuestion 的 point 参数。",
        "feeds": "知识点/课标对齐候选 + search_question_by_point 的输入",
    },
    "list_question_type": {
        "tool": "tkQuestionType",
        "params": {"subjectCode": "学科码"},
        "returns": "题型字典（id -> 题型名）",
        "status": "todo",
        "note": "题型字典。tkSearchQuestion 的 type 参数需要题型【数字】标识，"
                "过去只能传 0（不限）再从结果里挑；有这张字典就能按题型精确取题。",
        "feeds": "search_question.type / 按题型配额",
    },
    "list_question_from": {
        "tool": "tkQuestionFrom",
        "params": {"subjectCode": "学科码"},
        "returns": "试题来源字典（id -> 来源名，如月考/期末/中考）",
        "status": "todo",
        "note": "试题来源字典。配合 tkSearchSubjectQuestion 的 so 参数可按来源筛题。"
                "【对「真题新鲜度」标签有用】——能直接限定只取「期末考试」来源的题，"
                "不必先捞一堆再按 Label 字符串猜它是月考还是期末。",
        "feeds": "真题新鲜度 / search_question_by_point.so",
    },
    "list_book": {
        "tool": "tkBook",
        "params": {"subjectCode": "学科码"},
        "returns": "教材版本/册次数据",
        "status": "todo",
        "note": "按学科取教材目录。给题目标注教材章节、核对「这一课讲到哪」时用。",
        "feeds": "教材出处标注",
    },
    # ---------------------------------------------------------------- 文献
    "search_literature": {
        "tool": "searchVectorBJ",
        "params": {"text": "检索词(必填)", "query_type": "0篇名/1摘要/2小标题/3主题",
                   "type": "文献类型 0期刊,1硕士,2博士,3会议,4报纸(逗号分隔)",
                   "maxRecallNumber": "最大返回数(默认20)", "nprobe": "聚类中心数(默认15)"},
        "returns": "篇名/正文(摘要)/小标题/文件名/product/resource/相关度/距离",
        "status": "ok",
        "note": "学术溯源主力接口，【这是 edu 连接器里唯一的篇级文献检索入口】。三个要点："
                "① 返回【不含】作者、刊名、卷、页码，只有篇名+摘要+文件名；"
                "② 文件名 = 刊码+年份+期号+序号（形如 <刊码>+2023+10+004，可据此拿到年份与期号），"
                "年份与期号可据此拿到，并用来交叉校验外部补齐的著录；"
                "③ 查具体文章用 query_type=0（篇名），查主题用 3；检索词宜短，"
                "长句会漂移成无关学科。",
        "feeds": "items[].sources（学术溯源）",
    },
    "search_literature_para": {
        "tool": "searchVectorBJPara",
        "params": {"text": "检索词(必填)", "query_type": "0篇名小标题/1段落主题", "type": "文献类型"},
        "returns": "文件ID/文件名/篇名/当前小标题/正文/章节序号",
        "status": "weak",
        "note": "段落级检索，【做教辅溯源不要用】。实测检索「控制变量法」大量命中计量经济学、"
                "图像处理类论文，与教学无关；只有要定位某篇具体文献的某个章节时才值得用。",
        "feeds": "（不建议用于作业设计）",
    },
    # ---------------------------------------------------------------- 账号
    "user_state": {
        "tool": "userState",
        "params": {},
        "returns": "true/false",
        "status": "todo",
        "note": "查当前账号有没有该库的权益。无参数，成本极低。"
                "【应放在链路最前面】：返回 false 就不要往下检索了，"
                "否则后续的「查不到题」会被误判成题库无覆盖，实际是账号没权限。"
                "这也是区分「未连接 / 无权益 / 接口错」三类故障的关键一步。",
        "feeds": "开工前置校验",
    },
}

# ============================================================================
# 【已确认不存在的工具名】—— 曾经在文档里登记过，实际 ToolSearch 查不到。
# 列在这里是为了防止后人照抄旧文档反复试错。存短名，同样由 full_tool() 拼全名。
# ============================================================================
DEPRECATED_TOOLS = {
    "searchLiteratureKnowledge":
        "该工具在 edu 连接器中不存在（ToolSearch 精确查名返回无结果）。文献检索请用 searchVectorBJ。",
}

# ============================================================================
# 【学科码表】tkSubject（全名 full_tool("tkSubject")）实测返回（2026-09-29）
# 键 = (skill学科包, 学段)  值 = subjectCode
# None 表示题库无该学科覆盖 -> 必须降级为纯生成
# ============================================================================
_SUBJECT_CODE = {
    ("数学", "小学低段(1-2)"): 10, ("数学", "小学中高段(3-6)"): 10,
    ("数学", "初中(7-9)"): 20, ("数学", "高中(10-12)"): 30,
    ("语文", "小学低段(1-2)"): 11, ("语文", "小学中高段(3-6)"): 11,
    ("语文", "初中(7-9)"): 26, ("语文", "高中(10-12)"): 36,
    ("英语", "小学低段(1-2)"): 12, ("英语", "小学中高段(3-6)"): 12,
    ("英语", "初中(7-9)"): 27, ("英语", "高中(10-12)"): 37,
}

# 理化生 / 政史地 是复合学科包，需要二级学科细分
_SUBJECT_CODE_SUB = {
    "物理": {("理化生", "初中(7-9)"): 21, ("理化生", "高中(10-12)"): 31},
    "化学": {("理化生", "初中(7-9)"): 22, ("理化生", "高中(10-12)"): 32},
    "生物": {("理化生", "初中(7-9)"): 23, ("理化生", "高中(10-12)"): 33},
    "科学": {("理化生", "小学低段(1-2)"): 14, ("理化生", "小学中高段(3-6)"): 14},
    "道德与法治": {("政史地", "小学低段(1-2)"): 15, ("政史地", "小学中高段(3-6)"): 15,
                   ("政史地", "初中(7-9)"): 28},
    "政治": {("政史地", "高中(10-12)"): 38},
    "历史": {("政史地", "初中(7-9)"): 29, ("政史地", "高中(10-12)"): 39},
    "地理": {("政史地", "初中(7-9)"): 25, ("政史地", "高中(10-12)"): 35},
}

# 细分学科 -> 所属复合学科包。学科包可以独立存在（如"物理"），也可以复合（"理化生"），
# 两种写法都要能解析出学科码；否则独立写法会返回 null 并被误判成"题库无覆盖"。
_SUBJECT_PARENT = {
    "物理": "理化生", "化学": "理化生", "生物": "理化生", "科学": "理化生",
    "道德与法治": "政史地", "政治": "政史地", "历史": "政史地", "地理": "政史地",
}

# 难度 Degree(0-1) -> 分层档。阈值可调，改这里即可。
DEGREE_THRESHOLDS = (0.6, 0.85)   # <0.6 基础 | 0.6~0.85 巩固 | >0.85 拓展


def resolve_subject_code(subject, stage, sub=None):
    """解析学科码。返回 (code, 是否需要用户确认二级学科)。

    复合学科包（理化生/政史地）必须传 sub，否则返回候选列表要求确认——
    物理题和化学题混在一起是典型事故，不能靠猜。
    """
    if subject in _SUBJECT_PARENT:      # 直接给细分学科名（如"物理"）也要能解析，否则误判无覆盖
        parent = _SUBJECT_PARENT[subject]
        return _SUBJECT_CODE_SUB.get(subject, {}).get((parent, stage)), False
    if subject in ("理化生", "政史地"):
        if sub:
            return _SUBJECT_CODE_SUB.get(sub, {}).get((subject, stage)), False
        cands = sorted({s for s, m in _SUBJECT_CODE_SUB.items() if (subject, stage) in m})
        return None, cands
    if subject == "音体美":
        return None, []      # 题库无覆盖，直接降级纯生成
    return _SUBJECT_CODE.get((subject, stage)), False


# ---------------------------------------------------------------- 文本清洗
def _frac(m):
    """MathJye 分数表格 -> 分子/分母"""
    tds = re.findall(r"<td[^>]*>(.*?)</td>", m.group(0), re.S)
    tds = [re.sub(r"<[^>]+>", "", t) for t in tds]
    return "/".join(t for t in tds if t.strip())


def strip_html(s):
    """题库题干含大量 HTML（搜索高亮 <del>、角标 <sup>、分数表格、填空占位）。
    清洗目标：保留可读文本，填空位留 ____。"""
    if not s:
        return ""
    s = re.sub(r'<table[^>]*>.*?</table>', _frac, s, flags=re.S)
    s = re.sub(r'<!--BA-->.*?<!--EA-->', '____', s, flags=re.S)
    s = re.sub(r'<div class="quizPutTag"[^>]*>.*?</div>', '____', s, flags=re.S)
    s = re.sub(r'<sup>(.*?)</sup>', r'^\1', s, flags=re.S)
    s = re.sub(r'<sub>(.*?)</sub>', r'_\1', s, flags=re.S)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = (s.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
          .replace("&amp;", "&").replace("&quot;", '"'))
    s = re.sub(r'[ \t]+', ' ', s)
    return re.sub(r'\n{3,}', '\n\n', s).strip()


def degree_to_level(d):
    """Degree -> 基础/巩固/拓展"""
    try:
        d = float(d)
    except (TypeError, ValueError):
        return "巩固"
    lo, hi = DEGREE_THRESHOLDS
    return "基础" if d < lo else ("巩固" if d <= hi else "拓展")


# tkSearchSubjectQuestion 的 dg 难度档（服务端筛选用）
# ⚠ 方向存疑：接口文档标注「11=易(0.8~1.0)」，但 Degree 字段是越大越难，两者方向相反，
#   推测 dg 的区间指的是「正确率」而非难度。未实测校准前【只用 dg 做筛选，不用来定档】，
#   定档一律用返回的 Degree。校准方法见 references/workbuddy-mcp.md。
DG_LEVELS = {0: "不限", 11: "易", 12: "较易", 13: "中档", 14: "较难", 15: "难"}


def dg_to_label(dg):
    """dg 数字档 -> 中文名。仅用于日志与提示，不参与分层定档。"""
    try:
        return DG_LEVELS.get(int(dg), str(dg))
    except (TypeError, ValueError):
        return str(dg)


def _year(ts):
    try:
        ts = int(ts)
        ts = ts / 1000.0 if ts > 1e11 else ts
        return _dt.datetime.fromtimestamp(ts, _dt.timezone.utc).year
    except Exception:
        return None


# ---------------------------------------------------------------- 标准化
def _kv_names(v):
    """[{"Key":..,"Value":..}] -> ["值", ...]。也兼容纯字符串列表。"""
    out = []
    for x in v or []:
        if isinstance(x, dict):
            s = strip_html(str(x.get("Value") or x.get("Name") or "")).strip()
        else:
            s = strip_html(str(x)).strip()
        if s:
            out.append(s)
    return out


def _kv_pairs(v):
    """[{"Key":..,"Value":..}] -> [{"id":..,"name":..}]，保留 ID 便于回查。"""
    out = []
    for x in v or []:
        if not isinstance(x, dict):
            continue
        nm = strip_html(str(x.get("Value") or x.get("Name") or "")).strip()
        if nm:
            out.append({"id": str(x.get("Key") or x.get("Id") or ""), "name": nm})
    return out


def normalize_analysis(raw):
    """tkQuestionAnalysis 原始返回 -> 官方解析结构。

    【这个接口为什么重要】tkSearchQuestion / tkSearchSubjectQuestion 只带回答案，
    解析字段（Analyse/Method/Discuss）是空的。过去作业单里的 analysis 全靠模型写，
    这正是「改编题答案改错」最没底的一环。官方解析给的是出题方的解题过程，
    拿它当第 14 条答案一致性验算的校对基准，比让模型自己复算自己可靠得多。

    实测返回（2026-09-30，初中物理）：
      Method   = 详解正文（逐项分析 + "故选：B"），含 HTML
      Analyse  = 简析（要点式，较短）
      Discuss  = 考点点评
      Points   = 考点（带 ID）——注意：搜题接口返回的 Points 是空的，只有这里回填
      Topics   = 专题（带 ID）
    """
    data = raw.get("data") if isinstance(raw, dict) else raw
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError("解析返回格式异常：data 不是列表（raw keys=%s）" % list(raw)[:6])

    out = []
    for it in data:
        if not isinstance(it, dict):
            continue
        method = strip_html(it.get("Method") or "")
        analyse = strip_html(it.get("Analyse") or "")
        discuss = strip_html(it.get("Discuss") or "")
        sols = [strip_html(s) for s in (it.get("Solutions") or []) if s]
        body = method or analyse or (sols[0] if sols else "")
        out.append({
            "sid": it.get("SID") or "",
            "qtype": it.get("CateName") or "",
            "answer": it.get("DisplayAnswer") or "",
            "degree": it.get("Degree"),
            "method": method,
            "analyse": analyse,
            "discuss": discuss,
            "solutions": sols,
            "body": body,
            "points": _kv_pairs(it.get("Points")),
            "topics": _kv_pairs(it.get("Topics")),
            "has_official": bool(body),
        })
    return out


def merge_analysis(bank, analysis):
    """把官方解析按 SID 合并进 bank 项的 metadata。

    合进去的三个用途：
      official_analysis -> 第 14 条验算的校对基准 / 作业单解析的素材
      points/topics     -> 课标对齐与知识点标注（搜题接口不回填这两个字段）
    """
    if not analysis:
        return bank
    by_sid = {}
    for a in analysis:
        if isinstance(a, dict) and a.get("sid"):
            by_sid[a["sid"]] = a
    for it in bank:
        meta = it.get("metadata") or {}
        a = by_sid.get(meta.get("bank_id") or "")
        if not a:
            continue
        meta["official_analysis"] = a.get("body") or ""
        meta["official_answer"] = a.get("answer") or ""
        if a.get("points") and not meta.get("points"):
            meta["points"] = [p["name"] for p in a["points"]]
        if a.get("topics"):
            meta["topics"] = [t["name"] for t in a["topics"]]
    return bank


def build_analysis_fields(a):
    """normalize_analysis 的单项 -> 可直接写入作业单 item 的字段。

    返回 {answer, analysis, points, official_answer}：
      - answer / official_answer 取题库官方 DisplayAnswer（清洗后），后者供 validate 做
        官方答案交叉校验（与 answer 同值即必过，不触发拦截）。
      - analysis 把 简析(Method- Analyse) / 详解(Method) / 点评(Discuss) 合并为三段式，
        空段自动跳过；全部走 strip_html，分数表/上下标已规整为可读文本。
      - points 取官方回填的考点名（搜题接口不回填，只有解析接口有），用『；』连接。
    """
    if not a:
        return {}
    method = a.get("method") or ""
    analyse = a.get("analyse") or ""
    discuss = a.get("discuss") or ""
    parts = []
    if analyse:
        parts.append("【简析】" + analyse)
    if method:
        parts.append("【详解】" + method)
    if discuss:
        parts.append("【点评】" + discuss)
    points = [p.get("name") for p in (a.get("points") or []) if p.get("name")]
    # DisplayAnswer 是带 <bdo>/&nbsp;/<br> 的原始 HTML，必须清洗；official_answer 与 answer
    # 同值（已清洗），validate 的官方答案交叉校验必过。
    ans = strip_html(a.get("answer") or "")
    return {
        "answer": ans,
        "analysis": "\n".join(parts),
        "points": "；".join(points),
        "official_answer": ans,
    }


def fill_item_with_analysis(item, a):
    """把官方解析回填进单个 retrieve item；成功返回 True，无内容返回 False。

    只动 answer/analysis/points/official_answer/官方来源标记，绝不碰 stem/source_id，
    因此题面依旧一字不改（retrieve 的定义）。
    """
    f = build_analysis_fields(a)
    if not f or not (f["answer"] or f["analysis"]):
        return False
    item["answer"] = f["answer"]
    item["analysis"] = f["analysis"]
    if f["points"]:
        item["points"] = f["points"]
    item["official_answer"] = f["official_answer"]
    item["official_src"] = "tkQuestionAnalysis 回查"
    return True


def load_analysis_any(path):
    """容错加载官方解析 JSON：支持 单条原始响应 / {"data":[...]} / 多条响应列表 /
    已 normalize_analysis 的列表，统一展开成 normalize_analysis 后的列表。"""
    raw = json.load(open(path, encoding="utf-8"))
    raw_items = []
    if isinstance(raw, dict):
        if "data" in raw:
            raw_items = raw["data"]
        else:
            raw_items = [raw]
    elif isinstance(raw, list):
        for x in raw:
            if isinstance(x, dict) and "data" in x:
                raw_items.extend(x["data"])
            else:
                raw_items.append(x)
    norm = []
    for it in raw_items:
        if isinstance(it, dict) and ("Method" in it or "Analyse" in it or "Discuss" in it):
            # 裸 item 字典（缺 data 键）需包成 {data:[it]} 再归一化
            norm.extend(normalize_analysis({"data": [it]}))
        else:
            norm.append(it)
    return norm


def normalize_bank(raw, analysis=None):
    """题库原始返回 -> route 需要的 bank 列表。

    tkSearchQuestion（关键词）与 tkSearchSubjectQuestion（考点）返回结构一致，
    本函数通用；后者还会多带 SourceReports / PaperCount / RealCount 三个字段。

    输出每项：
      {"content": 清洗后题干,
       "metadata": {"bank_id": SID, "level": 分层档, "year": 年份,
                    "qtype": 题型, "answer": 答案, "options": 选项,
                    "degree": 原始难度, "source_label": 试卷出处(简称),
                    "source_reports": 完整试卷名列表,
                    "real_count": 真实考试引用次数, "paper_count": 收录试卷数,
                    "points": 考点名, "topics": 专题名,
                    "official_analysis"/"official_answer": 官方解析（合并后才有）}}
    """
    data = raw.get("data") if isinstance(raw, dict) else raw
    if not isinstance(data, list):
        raise ValueError("题库返回格式异常：data 不是列表（raw keys=%s）" % list(raw)[:6])

    out = []
    for it in data:
        stem = strip_html(it.get("Content") or "")
        if not stem:
            continue
        opts = [strip_html(o) for o in (it.get("Options") or [])]
        opts = [o for o in opts if o]
        ans = it.get("DisplayAnswer") or ""
        if not ans:
            idx = it.get("Answers") or []
            ans = ",".join(str(a) for a in idx)
        reports = [strip_html(str(x.get("Value") or "")).strip()
                   for x in (it.get("SourceReports") or []) if isinstance(x, dict)]
        reports = [r for r in reports if r]
        out.append({
            "content": stem,
            "metadata": {
                "bank_id": it.get("SID") or "",
                "level": degree_to_level(it.get("Degree")),
                "year": _year(it.get("Date")),
                "qtype": it.get("CateName") or "",
                "answer": ans,
                "options": opts,
                "degree": it.get("Degree"),
                "source_label": strip_html(it.get("Label") or ""),
                # 下面三个只有 tkSearchSubjectQuestion 返回
                "source_reports": reports,
                "real_count": it.get("RealCount"),
                "paper_count": it.get("PaperCount"),
                "points": _kv_names(it.get("Points")),
                "topics": _kv_names(it.get("Topics")),
            },
        })
    return merge_analysis(out, analysis)


# ---------------------------------------------------------------- 文献
# searchVectorBJ 的 文件名 是 CNKI 自己的编码：刊码 + 年份 + 期号 + 序号。
# 例：<刊码>+2023+10+004 → 2023 年 / 第 10 期 / 第 004 篇
#     <刊码>+2017+31+022 → 2017 年第 31 期（周刊，期号可以大于 12）
#     <刊码>+2001+S2+051 → 2001 年 S2 增刊
# 年份与期号是这份数据里唯一能机器读出的著录信息，用来交叉校验外部补齐的作者/刊名。
_LIT_FN_RE = re.compile(r"^([A-Za-z]+)(\d{4})(\d{2,3})(\d{3})$")
_LIT_FN_LOOSE_RE = re.compile(r"^([A-Za-z]+)(\d{4})(.+)$")

# searchVectorBJ 不返回、必须由补齐环节提供的字段
LIT_NEED_FIELDS = ("author", "container", "volume", "pages")


def parse_lit_filename(fn):
    """解析文献 文件名 -> {journal_code, year, issue, seq}。解析不出就只回 filename。"""
    fn = (fn or "").strip()
    if not fn:
        return {}
    m = _LIT_FN_RE.match(fn)
    if m:
        code, year, issue, seq = m.groups()
    else:
        m = _LIT_FN_LOOSE_RE.match(fn)
        if not m:
            return {"filename": fn}
        code, year, rest = m.groups()
        seq, issue = rest[-3:], rest[:-3] or ""
    return {
        "filename": fn,
        "journal_code": code,
        "year": int(year),
        "issue": (issue.lstrip("0") or issue) if issue else "",
        "seq": seq,
    }


def normalize_lit(raw):
    """searchVectorBJ 原始返回 -> items[].sources 可挂的溯源列表。

    接口只给 篇名 / 摘要 / 文件名，【不返回作者、刊名、卷、页码】。
    这里能结构化出来的只有年份与期号（藏在文件名里），其余一律 None 并记进 need_fields，
    交给补齐环节按篇名核实后 fill_lit 回填。缺字段由渲染器输出灰色【待补充】，绝不编造。
    """
    data = raw.get("data") if isinstance(raw, dict) else raw
    if not isinstance(data, list):
        return []
    out = []
    for it in data:
        if not isinstance(it, dict):
            continue
        title = (it.get("篇名") or it.get("标题") or "").strip()
        if not title:
            continue
        p = parse_lit_filename(it.get("文件名"))
        # 只有 CJFD（正式出版）的文件名才是「刊码+年+期+序号」。
        # CAPJ 是优先出版，编码规则不同（如 <刊码>+2026+04+090+G 形式），期号不可信，一律不解析。
        trusted = str(it.get("product", "")).upper() == "CJFD"
        rec = {
            "type": "journal" if str(it.get("resource", "")).upper() == "JOURNAL" else "other",
            "title": title,
            "abstract": strip_html(it.get("正文") or it.get("摘要") or "")[:200],
            "year": p.get("year"),
            "issue": (p.get("issue") or None) if trusted else None,
            "author": None,          # 接口不返回 -> 待补
            "container": None,       # 接口不返回刊名 -> 待补
            "volume": None,
            "pages": None,
            "journal_code": p.get("journal_code"),
            "filename": p.get("filename"),
            "relevance": it.get("相关度"),
            "generic": False,
        }
        # CAPJ = 优先出版（尚未定刊期），正式溯源尽量不用
        if it.get("product") == "CAPJ":
            rec["provisional"] = True
        rec["need_fields"] = [f for f in LIT_NEED_FIELDS if not rec.get(f)]
        out.append(rec)
    return out


def fill_lit(items, fill):
    """把核实过的著录回填到 searchVectorBJ 的输出上。

    fill 格式：{篇名: {"author":..., "container":..., "volume":..., "pages":...}}
    规则：
    - 只补 None 字段，已有值不覆盖；
    - year / issue 若与外部值冲突，**保留文件名解析值**并在 notes 里记冲突——
      文件名是 CNKI 自己的编码，可信度高于外部来源；
    - 回填后重算 need_fields，仍缺的继续标【待补充】。
    """
    idx = {x.get("title"): x for x in items if x.get("title")}
    filled = 0
    for title, patch in (fill or {}).items():
        rec = idx.get(title)
        if not rec or not isinstance(patch, dict):
            continue
        for k, v in patch.items():
            if k in ("year", "issue"):
                cur = rec.get(k)
                if cur is not None and str(cur) != str(v):
                    rec.setdefault("notes", []).append(
                        "%s 外部值 %s 与 CNKI 文件名解析值 %s 不一致，已保留文件名值，请人工确认" % (k, v, cur))
                    continue
                if cur is None:
                    rec[k] = v
            elif rec.get(k) is None and v not in (None, ""):
                rec[k] = v
        filled += 1
    for rec in items:
        rec["need_fields"] = [f for f in LIT_NEED_FIELDS if not rec.get(f)]
    return items, filled


def lit_report(items):
    """文献补齐体检报告：多少条可以直接用、多少条还缺字段。"""
    ok = [x for x in items if not x.get("need_fields") and not x.get("provisional")]
    need = [x for x in items if x.get("need_fields")]
    prov = [x for x in items if x.get("provisional")]
    lines = ["[文献体检] 共 %d 条：著录完整 %d · 待补字段 %d · 优先出版(建议不用) %d"
             % (len(items), len(ok), len(need), len(prov))]
    if need:
        lines.append("  待补字段清单（按篇名去 CNKI 核实后回填，缺字段会渲染成【待补充】）：")
        for x in need[:8]:
            lines.append("    · %s  缺：%s" % ((x.get("title") or "")[:36], "/".join(x["need_fields"])))
        lines.append("  年份与期号已由文件名解析得到（如 %s），用它交叉校验核实结果。"
                     % (need[0].get("filename") or "-"))
    if prov:
        lines.append("  ⚠ 优先出版文献未定刊期：%s" % "、".join((x.get("title") or "")[:20] for x in prov[:3]))
    return "\n".join(lines)


def _warn_supply(items):
    """候选题充足度体检。

    题库候选 < 题量时，供给路由会把同一道题重复分配给多题（实测：3 条候选出 6 题，
    SID_C 被用了两次，产出两道高度相似的改编题）。这不是 bug 而是数据不足，
    必须在生成前暴露，而不是等教师发现作业里有两道孪生题。
    """
    from collections import Counter
    lv = Counter(i["metadata"]["level"] for i in items)
    print("\n[候选体检] 分层分布：" + " · ".join("%s %d" % (k, v) for k, v in lv.items()))
    if len(items) < 6:
        print("  ⚠ 候选题仅 %d 条。建议：扩大关键词 / 翻页(pi) 多取 / 拆成多个知识点分别检索，"
              "使候选数 ≥ 题量的 1.5 倍，否则同一题会被重复改编。" % len(items))
    miss = [x for x in ("基础", "巩固", "拓展") if lv.get(x, 0) == 0]
    if miss:
        print("  ⚠ 缺少【%s】档候选题，该档将全部走 generate（原创），"
              "原创占比可能被击穿，注意 gen_cap 校验。" % "、".join(miss))
    dup = [k for k, v in Counter(i["metadata"]["bank_id"] for i in items).items() if v > 1 and k]
    if dup:
        print("  ⚠ 存在重复 SID：%s" % "、".join(dup[:5]))


def find_point(tree, keyword, max_hits=20):
    """在三级知识点树里找命中的知识点（Name 或 Desc 含关键词）。
    只返回命中的叶子路径，避免把 30 万字符全量塞进上下文。"""
    data = tree.get("data") if isinstance(tree, dict) else tree
    hits = []

    def walk(nodes, path):
        for n in nodes or []:
            nm = n.get("Name") or ""
            p = path + [nm]
            if keyword in nm or keyword in (n.get("Desc") or ""):
                hits.append({"path": " > ".join(p), "desc": strip_html(n.get("Desc") or "")[:160]})
            if len(hits) < max_hits:
                walk(n.get("Children") or [], p)

    walk(data or [], [])
    return hits[:max_hits]


# ============================================================================
# 接口对账 —— 解决「登记表是静态的，连接器加了新接口却感知不到」的问题。
#
# 登记表必须静态写死（脚本里要说清每个接口的参数、返回、坑，没法自动生成），
# 所以它天然会滞后于连接器。补救办法是定期做一次双向对账：
#   Agent 侧用 ToolSearch 列出连接器当前暴露的工具 -> 落盘 tools.json
#   python mcp_adapters.py reconcile --tools tools.json
# 两边一比，四类偏差全部暴露出来。
# ============================================================================
_TOOL_NAME_RE = re.compile(r"^mcp__(?P<prefix>.+?)__(?P<short>[A-Za-z0-9_]+)$")


def guess_prefix(names):
    """从观测到的工具全名反推「真实的连接器前缀」。

    为什么需要：MCP_PROVIDER 取自连接器【显示名】，用户在连接器管理页重命名就会变
    （已实测 edu -> 知网基教 -> edu）。写死必然再错一次，且错因极隐蔽
    （症状是 ToolSearch 查不到，容易被误判成接口坏了）。

    做法：把观测到的 mcp__X__Y 拆成 (前缀 X, 短名 Y)，看哪个 X 下头的短名
    与本表登记的短名重合最多。重合数最高那个就是真前缀。
    """
    mine_shorts = {v["tool"] for v in MCP_ENDPOINTS.values()}
    buckets = {}
    for n in names or []:
        m = _TOOL_NAME_RE.match(str(n).strip())
        if not m:
            continue
        buckets.setdefault(m.group("prefix"), set()).add(m.group("short"))

    scored = []
    for pfx, shorts in buckets.items():
        hit = shorts & mine_shorts
        scored.append({"prefix": pfx, "overlap": len(hit),
                       "total": len(shorts), "hits": sorted(hit)})
    scored.sort(key=lambda x: (-x["overlap"], x["prefix"]))

    cur = MCP_PROVIDER
    cur_overlap = len(buckets.get(cur, set()) & mine_shorts)
    drift = bool(scored) and scored[0]["prefix"] != cur and scored[0]["overlap"] > cur_overlap
    return {
        "current": cur,
        "current_overlap": cur_overlap,
        "candidates": scored,
        "best": scored[0] if scored else None,
        "drift": drift,
        "drift_to": (scored[0]["prefix"] if drift else None),
        "history": [h for h in MCP_PROVIDER_HISTORY if h != cur],
    }


def reconcile_tools(observed):
    """把「连接器实际暴露的工具」与登记表比对。

    observed : 工具全名列表。也接受 ToolSearch 那种 [{"name": ...}] / [{"tool": ...}] 结构。
    返回 dict，四类偏差：
      matched       登记了，连接器里也有                    -> 正常
      missing       登记了，连接器里没有                    -> 名字写错 / 已下线 / 前缀错了
      unregistered  连接器里有，本表没登记                  -> 【新接口】，可能有用，要人工评估
      revived       曾以为不存在，现在又出现了              -> 把 DEPRECATED_TOOLS 里那条删掉
      prefix        【前缀漂移诊断】当前前缀对不对，不对该改成什么
    """
    names = []
    for x in observed or []:
        if isinstance(x, dict):
            names.append(str(x.get("name") or x.get("tool") or x.get("id") or ""))
        else:
            names.append(str(x))
    names = {n.strip() for n in names if n and n.strip()}

    prefix = "mcp__%s__" % MCP_PROVIDER
    mine = {full_tool(v["tool"]): k for k, v in MCP_ENDPOINTS.items()}
    deprecated = {full_tool(s): s for s in DEPRECATED_TOOLS}

    same_connector = {n for n in names if n.startswith(prefix)}
    return {
        "provider": MCP_PROVIDER,
        "observed_total": len(names),
        "observed_this_connector": len(same_connector),
        "registered_total": len(mine),
        "matched": sorted((k, t) for t, k in mine.items() if t in names),
        "missing": sorted((k, t) for t, k in mine.items() if t not in names),
        "unregistered": sorted(same_connector - set(mine) - set(deprecated)),
        "revived": sorted((s, t) for t, s in deprecated.items() if t in names),
        "foreign": sorted(n for n in names if not n.startswith(prefix)),
        "prefix": guess_prefix(names),
    }


def render_reconcile(r):
    lines = []
    lines.append("== 接口对账 ==  连接器[%s] · 共暴露 %d 个工具（本连接器 %d 个）· 本表登记 %d 个"
                 % (r["provider"], r["observed_total"], r["observed_this_connector"],
                    r["registered_total"]))
    lines.append("")

    # 前缀漂移放最前面：它一旦错了，下面所有 missing 都是假象
    pf = r.get("prefix") or {}
    if pf.get("drift"):
        best = pf["best"]
        lines.append("[PREFIX-DRIFT] 前缀疑似不对 —— 当前写的 [%s] 只匹配上 %d 个接口，"
                     "而 [%s] 能匹配 %d 个"
                     % (pf["current"], pf["current_overlap"], best["prefix"], best["overlap"]))
        lines.append("     证据：%s" % ", ".join(best["hits"][:6]))
        lines.append("     修复：把 mcp_adapters.py 第 39 行的 MCP_PROVIDER 改成 \"%s\"，"
                     "并把该值追加进 MCP_PROVIDER_HISTORY" % best["prefix"])
        lines.append("     为什么：工具名前缀取自连接器【显示名】，用户在连接器管理页重命名就会变，"
                     "不是 mcp.json 里的 key。")
    else:
        lines.append("[PREFIX-OK] 前缀 [%s] 匹配 %d 个已登记接口"
                     % (pf.get("current", "?"), pf.get("current_overlap", 0)))
        if pf.get("history"):
            lines.append("     历史用过：%s（都曾正确过，改名不是出错）" % ", ".join(pf["history"]))
    lines.append("")

    lines.append("[OK] 登记且可用 (%d)" % len(r["matched"]))
    for k, t in r["matched"]:
        lines.append("     %-24s %s" % (k, t))
    lines.append("")

    if r["missing"]:
        lines.append("[BLOCKER] 登记了但连接器里没有 (%d) —— 优先查工具名前缀写对没有" % len(r["missing"]))
        for k, t in r["missing"]:
            lines.append("     %-24s %s" % (k, t))
        lines.append("     常见原因：① MCP_PROVIDER 与连接器显示名不一致"
                     "（工具全名是 mcp__<显示名>__<短名>，不是 mcp.json 里的 key）；"
                     "② 接口已下线；③ 拼写错误。")
        lines.append("")

    if r["unregistered"]:
        lines.append("[NEW] 连接器里有、本表没登记 (%d) —— 这就是「新接口会不会漏」的答案，需人工评估" % len(r["unregistered"]))
        for t in r["unregistered"]:
            lines.append("     %s" % t)
        lines.append("     处置：① ToolSearch 查它的参数 ② 判断对作业设计有没有用"
                     " ③ 有用就补进 MCP_ENDPOINTS 并写清 params/returns/note/feeds")
        lines.append("")

    if r["revived"]:
        lines.append("[INFO] 曾判为不存在、现在又出现了 (%d) —— 把 DEPRECATED_TOOLS 里那条删掉" % len(r["revived"]))
        for s, t in r["revived"]:
            lines.append("     %s" % t)
        lines.append("")

    if r["foreign"]:
        lines.append("[IGNORED] 不属于本连接器 (%d)" % len(r["foreign"]))
        lines.append("     %s" % ", ".join(r["foreign"][:12]))
        lines.append("")

    ok = not r["missing"]
    lines.append("结论：%s" % ("登记与实际一致" if ok and not r["unregistered"]
                              else "有偏差，按上面 [BLOCKER] / [NEW] 两节处理"))
    return "\n".join(lines)


# ---------------------------------------------------------------- CLI
def _load(p):
    if p == "-":
        return json.load(sys.stdin)
    return json.loads(p) if p.strip().startswith("{") else json.load(open(p, encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser(description="CNKI 基础教育 MCP 数据适配层（题库 + 学术文献）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("endpoints", help="打印接口登记表（看当前接口名与状态）")
    p.add_argument("--only-ok", action="store_true")

    p = sub.add_parser("code", help="解析学科码")
    p.add_argument("--subject", required=True)
    p.add_argument("--stage", required=True)
    p.add_argument("--sub", default=None, help="复合学科包的二级学科，如 物理/化学/历史")

    p = sub.add_parser("bank", help="题库原始返回 -> route 的 bank 列表（关键词/考点两种检索通用）")
    p.add_argument("--raw", required=True)
    p.add_argument("--out", default=None)
    p.add_argument("--level", default=None, help="强制覆盖分层档（题库难度不靠谱时用）")
    p.add_argument("--analysis", default=None,
                   help="tkQuestionAnalysis 的原始返回，按 SID 合并官方解析与考点")

    p = sub.add_parser("analysis", help="tkQuestionAnalysis 原始返回 -> 官方解析")
    p.add_argument("--raw", required=True)
    p.add_argument("--out", default=None)

    p = sub.add_parser("lit", help="文献原始返回 -> sources 列表（searchVectorBJ）")
    p.add_argument("--raw", required=True)
    p.add_argument("--out", default=None)
    p.add_argument("--fill", default=None,
                   help="著录回填文件 {篇名:{author,container,volume,pages}}，用于补接口不返回的字段")

    p = sub.add_parser("point", help="知识点树里找关键词")
    p.add_argument("--raw", required=True)
    p.add_argument("--keyword", required=True)
    p.add_argument("--out", default=None)

    p = sub.add_parser("reconcile",
                       help="拿连接器当前实际暴露的工具清单与登记表对账，发现新接口/失效接口")
    p.add_argument("--tools", required=True,
                   help="工具名清单文件（JSON 数组 或 {\"tools\":[...]}），- 表示 stdin")

    a = ap.parse_args()

    if a.cmd == "endpoints":
        print("provider: %s（WorkBuddy 连接器「CNKI 基础教育」）" % MCP_PROVIDER)
        print("工具全名 = mcp__%s__<短名>。前缀来自连接器显示名，不是 mcp.json 的 key(%s)。"
              % (MCP_PROVIDER, MCP_CONFIG_KEY))
        print("题库与学术文献的统一入口，均走 mcp__%s__*\n" % MCP_PROVIDER)
        for k, v in MCP_ENDPOINTS.items():
            if a.only_ok and v["status"] != "ok":
                continue
            print("[%s] %s" % (v["status"].upper(), k))
            print("  tool    : %s" % full_tool(v["tool"]))
            print("  params  : %s" % json.dumps(v.get("params", {}), ensure_ascii=False))
            print("  returns : %s" % v.get("returns", "-"))
            print("  feeds   : %s" % v.get("feeds", "-"))
            print("  note    : %s" % v.get("note", ""))
            print()
        print("登记表是静态的，不会自动感知连接器新增的接口。"
              "升级连接器后跑 reconcile 子命令做一次双向对账。")
        if DEPRECATED_TOOLS:
            print("\n--- 已确认不存在的工具名（不要照抄旧文档去调）---")
            for short, why in DEPRECATED_TOOLS.items():
                print("  %s : %s" % (full_tool(short), why))
        return

    if a.cmd == "reconcile":
        raw = _load(a.tools)
        if isinstance(raw, dict):
            raw = raw.get("tools") or raw.get("data") or []
        print(render_reconcile(reconcile_tools(raw)))
        return

    if a.cmd == "code":
        code, cands = resolve_subject_code(a.subject, a.stage, a.sub)
        if code:
            print(json.dumps({"subjectCode": code}, ensure_ascii=False))
        elif cands:
            print(json.dumps({"need_confirm": True, "candidates": cands,
                              "hint": "该学科包含多个学科，用 --sub 指定后再查"}, ensure_ascii=False))
        else:
            print(json.dumps({"subjectCode": None,
                              "hint": "题库无该学科覆盖，供给路由将全部走 generate"}, ensure_ascii=False))
        return

    if a.cmd == "analysis":
        items = normalize_analysis(_load(a.raw))
        s = json.dumps(items, ensure_ascii=False, indent=2)
        if a.out:
            open(a.out, "w", encoding="utf-8").write(s)
            print("已写出 %d 条官方解析 -> %s" % (len(items), a.out))
            for x in items:
                print("  [%s] %s | 考点 %s | %s" % (
                    "有解析" if x["has_official"] else "无解析",
                    (x.get("sid") or "-")[:12],
                    "、".join(p["name"] for p in x.get("points", [])[:3]) or "-",
                    (x.get("body") or "")[:40].replace("\n", " ") + "…"))
        else:
            print(s)
        return

    if a.cmd == "bank":
        ana = normalize_analysis(_load(a.analysis)) if a.analysis else None
        items = normalize_bank(_load(a.raw), analysis=ana)
        if a.level:
            for it in items:
                it["metadata"]["level"] = a.level
        s = json.dumps(items, ensure_ascii=False, indent=2)
        if a.out:
            open(a.out, "w", encoding="utf-8").write(s)
            print("已写出 %d 条候选题 -> %s" % (len(items), a.out))
            for it in items[:3]:
                m = it["metadata"]
                print("  [%s|%s|难度%s] %s%s" % (
                    m["level"], m["qtype"] or "-", m["degree"],
                    it["content"][:46], "…" if len(it["content"]) > 46 else ""))
            _warn_supply(items)
        else:
            print(s)
        return

    if a.cmd == "lit":
        items = normalize_lit(_load(a.raw))
        if a.fill:
            items, n = fill_lit(items, _load(a.fill))
            print("已回填 %d 条著录" % n)
        s = json.dumps(items, ensure_ascii=False, indent=2)
        if a.out:
            open(a.out, "w", encoding="utf-8").write(s)
            print("已写出 %d 条溯源来源 -> %s" % (len(items), a.out))
            print(lit_report(items))
        else:
            print(s)
        return

    if a.cmd == "point":
        hits = find_point(_load(a.raw), a.keyword)
        s = json.dumps(hits, ensure_ascii=False, indent=2)
        if a.out:
            open(a.out, "w", encoding="utf-8").write(s)
            print("命中 %d 个知识点 -> %s" % (len(hits), a.out))
            for h in hits[:5]:
                print("  " + h["path"])
        else:
            print(s)
        return


if __name__ == "__main__":
    main()
