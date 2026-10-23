# -*- coding: utf-8 -*-
"""
homework_kit.py — 中小学「作业设计 AI」约束套件
=================================================
把学科包 + 学段包 + prompt 拼装 + 供给路由 + 生成后校验 + 渲染，整合成单一权威源。

为什么要合成一个文件：约束包、路由、校验、渲染四处规则必须始终一致，拆成多个文件
就会出现"改了这里的规则忘了那里"的经典事故。单文件也便于整段复制到别处复用。

五个子命令（用法见 --help 或 SKILL.md）：
    packs     打印学科包 + 学段包
    prompt    拼装可直接投给大模型的 prompt
    route     供给路由：决定每题走 retrieve / adapt / generate
    validate  生成后硬校验，返回 ok / issues
    render    渲染成 Markdown 作业单

只依赖标准库；Python 3.8+。
"""
import argparse
import datetime
import json
import math
import os
import re
import sys
from collections import Counter

# ==========================================================================
# 一、学科约束包：决定"出什么类型的题"
# ==========================================================================
SUBJECT_PACKS = {
    "语文": {
        "types": ["阅读", "古诗文", "语言运用", "写作"],
        "levels": {
            "基础": {"desc": "字词句·默写·单篇理解", "学情": "读写积累薄弱、需夯实字词句与文本基础的学生", "培养目标": "语言建构与运用（准确识记、规范表达）"},
            "巩固": {"desc": "多文本比较·手法赏析", "学情": "有一定积累、需提升文本分析与鉴赏能力的学生", "培养目标": "思维发展与提升·审美鉴赏与创造（比较、赏析、推断）"},
            "拓展": {"desc": "整本书·创意写作·跨媒介", "学情": "阅读面广、表达力强、善思辨的学生", "培养目标": "审美鉴赏与创造·文化传承与理解（整本书阅读、创意表达、跨媒介）"},
        },
        "quant": {
            "text_len": {"小学": "300-500字", "初中": "500-800字"},
            "writing_min": {"小学": 300, "初中": 600},
            "sentence_len_max": 25,
            "must_fields": ["answer", "analysis"],
        },
        "sources": {"require_for": ["阅读", "古诗文"], "venues": ["《中学语文教学》", "《语文建设》", "《小学语文教学》"]},
        "extra_fields": ["rubric"],
        "forbidden": ["争议价值观表述", "未核校的古诗文原文", "无出处赏析"],
    },
    "数学": {
        "types": ["计算题", "应用题", "思维题"],
        "levels": {
            "基础": {"kp": 1, "max_steps": 2, "desc": "单知识点直练·步骤≤2", "学情": "概念模糊、步骤易乱、需建立基本运算与推理习惯的学生", "培养目标": "数学运算·逻辑推理（单知识点直练、步骤规范）"},
            "巩固": {"kp": 2, "max_steps": 4, "desc": "两知识点综合·步骤≤4", "学情": "掌握基础、需提升综合应用与多步推理的学生", "培养目标": "逻辑推理·数学建模（多知识点综合、建模意识）"},
            "拓展": {"kp": ">=2跨知识点或开放探究", "desc": "跨知识点或开放探究", "学情": "学有余力、善抽象建模、爱挑战开放题的学生", "培养目标": "数学抽象·数学建模·数据分析（开放探究、跨情境）"},
        },
        "quant": {"data": "有理数且可算", "solution": "唯一解或明确区间", "must_fields": ["answer", "analysis"]},
        "sources": {"require_for": ["应用题", "思维题"], "venues": ["《中小学数学教育》", "《数学通报》"]},
        "extra_fields": ["cognitive"],
        "forbidden": ["矛盾方程", "无解应用题", "编造数据"],
    },
    "英语": {
        "types": ["词汇语法", "阅读", "写作", "听说任务"],
        "levels": {
            "基础": {"desc": "词汇语法·单句", "学情": "词汇语法薄弱、需夯实语言基础的学生", "培养目标": "语言能力（词汇语法、单句表达）"},
            "巩固": {"desc": "语篇理解·写作80-100词", "学情": "有一定语感、需提升语篇理解与表达能力的学生", "培养目标": "语言能力·思维品质（语篇理解、连贯表达）"},
            "拓展": {"desc": "读后续写·观点表达", "学情": "表达欲强、善思辨、爱读写的学生", "培养目标": "思维品质·文化意识（读后续写、观点表达、跨文化）"},
        },
        "quant": {
            "vocab": "限课标词表，超纲词须标注+中文",
            "reading_words": {"小学": "150-250", "初中": "250-400"},
            "writing_range": {"初中": "80-100词"},
            "must_fields": ["answer", "analysis"],
        },
        "sources": {"require_for": ["阅读", "写作"], "venues": ["《中小学外语教学》", "《英语学习》"]},
        "extra_fields": ["rubric"],
        "forbidden": ["超课标语法项目", "无来源真实语料", "超词表未标注词"],
    },
    "理化生": {
        "types": ["概念辨析", "实验设计", "计算", "现象解释"],
        "levels": {
            "基础": {"desc": "概念识记·单位换算", "学情": "概念不清、实验操作弱、需建立学科基本观念的学生", "培养目标": "物理/化学/生物观念（概念识记、单位换算、基础技能）"},
            "巩固": {"desc": "公式应用·实验步骤", "学情": "掌握基础、需提升知识迁移与综合应用能力的学生", "培养目标": "科学思维（公式应用、实验步骤、因果分析）"},
            "拓展": {"desc": "实验设计·误差分析·跨学科", "学情": "探究意愿强、学有余力、爱动手设计的学生", "培养目标": "科学探究·创新意识（实验设计、误差分析、跨学科）"},
        },
        "quant": {"must_unit": True, "magnitude_real": True, "must_fields": ["answer", "analysis", "safety"]},
        "sources": {"require_for": ["实验设计", "现象解释"], "venues": ["《中学物理教学参考》", "《化学教学》", "《生物学教学》"]},
        "extra_fields": ["safety", "apparatus"],
        "forbidden": ["危险实验", "无单位物理量", "不符合真实量级的数据"],
    },
    "政史地": {
        "types": ["材料分析", "识图填图", "论述"],
        "levels": {
            "基础": {"desc": "史实/概念再认", "学情": "史实/概念模糊、需夯实基础认知的学生", "培养目标": "时空观念·政治认同（史实概念再认）"},
            "巩固": {"desc": "材料解读·因果分析", "学情": "掌握基础、需提升材料解读与因果分析能力的学生", "培养目标": "史料实证·综合思维（材料解读、因果分析）"},
            "拓展": {"desc": "多源史料互证·开放论述", "学情": "善思辨、关注现实、爱探究的学生", "培养目标": "历史解释·家国情怀·人地协调观（多源互证、开放论述）"},
        },
        "quant": {"material_must": "标来源+时间", "map": "必须使用合规标准地图", "must_fields": ["answer", "analysis"]},
        "sources": {"require_for": ["材料分析"], "venues": ["《历史教学》", "《中学地理教学参考》", "《思想政治课教学》"]},
        "extra_fields": ["claim_dimensions"],
        "forbidden": ["未经核实的网络传闻", "无时间出处的材料", "不合规地图与领土表述"],
    },
    "音体美信": {
        "types": ["实践任务单", "作品评价", "过程记录"],
        "levels": {
            "基础": {"desc": "技能模仿", "学情": "技能生疏、需模仿入门的学生", "培养目标": "基础技能·审美感知（技能模仿、动作定型）"},
            "巩固": {"desc": "组合应用", "学情": "掌握基础、需提升组合应用与表现力的学生", "培养目标": "艺术表现·运动能力（组合应用、表现力）"},
            "拓展": {"desc": "创作编排", "学情": "创作欲强、有特长、爱编创的学生", "培养目标": "文化理解·创新实践（创作编排、创意物化）"},
        },
        "quant": {"task_must": "材料/场地/时长明确", "must_fields": ["rubric", "duration", "answer"]},
        "sources": {"require_for": ["实践任务单"], "venues": ["《中国音乐教育》", "《中国学校体育》", "《中国美术教育》"]},
        "extra_fields": ["rubric", "venue_requirement"],
        "forbidden": ["需专业危险器材的任务", "无评价量规的任务", "场地器材不明确"],
    },
}

# ==========================================================================
# 二、学段约束包：横切维度，决定"能出多难、出多少、能不能出书面作业"
# 学段包优先级高于学科包——政策红线（allow_written / max_minutes）不可协商
# ==========================================================================
STAGE_PACKS = {
    "小学低段(1-2)": {
        "stage": "小学低段(1-2)", "allow_written": False, "max_minutes": 0,
        "cognitive_max": "理解", "sentence_len_max": 15,
        "std": "义务教育课程方案(2022)",
        "types": ["口头表达", "实践任务", "观察记录", "亲子阅读"],
        "levels": {"基础": "听说跟读", "巩固": "口头表达", "拓展": "实践小任务"},
        "forbidden": ["书面计算题", "书面家庭作业", "超15字长句", "需家长批改的书面题"],
    },
    "小学中高段(3-6)": {
        "stage": "小学中高段(3-6)", "allow_written": True, "max_minutes": 60,
        "cognitive_max": "应用", "sentence_len_max": 20,
        "std": "义务教育课程方案(2022)",
        "types": ["基础计算", "简单应用", "短文写作", "实践探究"],
        "levels": {"基础": "单知识点直练", "巩固": "两步应用", "拓展": "跨情境小探究"},
        "forbidden": ["总时长超60分钟", "抽象论证", "超纲术语"],
    },
    "初中(7-9)": {
        "stage": "初中(7-9)", "allow_written": True, "max_minutes": 90,
        "cognitive_max": "分析", "sentence_len_max": 25,
        "std": "义务教育课程方案(2022)",
        "types": ["综合应用", "材料分析", "实验设计", "论述表达"],
        "levels": {"基础": "单一技能", "巩固": "多知识点综合", "拓展": "开放探究·跨学科"},
        "forbidden": ["总时长超90分钟", "过量抄写记忆题", "无来源材料题"],
    },
    "高中(10-12)": {
        "stage": "高中(10-12)", "allow_written": True, "max_minutes": 120,
        "cognitive_max": "创造", "sentence_len_max": 35,
        "std": "普通高中课程方案及20科课标(2017年版2020年修订)",
        "types": ["综合论述", "多源互证", "建模探究", "批判性评价"],
        "levels": {"基础": "模块内基础", "巩固": "跨模块综合", "拓展": "真实情境建模·学术性写作"},
        "forbidden": ["低幼化表述", "无评价量规的开放题"],
        "note": "高中无全国统一作业时长硬性规定，120分钟为建议值，按学校规定校准",
    },
}

COG_ORDER = ["记忆", "理解", "应用", "分析", "评价", "创造"]
MODE_LABEL = {"retrieve": "题库原题", "adapt": "改编变式", "generate": "原创生成"}


# ==========================================================================
# 二·一、真题出处的解析：新鲜度 / 考试类型 / 新旧课标适用性
#
# 题库 Label 长得像「2026秋•昌吉州校级月考」。把它当一整串字符串印到作业单上，
# 教师还得自己拆。里面真正影响判断的是三件事：
#  ① 年份够不够新 —— 贴不贴近当年命题趋势；
#  ② 这是什么考试 —— 校级月考和中考真题的含金量完全不同，写「真题」二字太模糊；
#  ③ 是否早于现行课程方案 —— 2022 新课标（高中 2020 修订）是道硬分界线，
#     更早的真题可能基于旧教材、引旧数据，不能默认今天仍适用。
#
# 第三点最容易被忽略：一份 2018 年的物理真题在 2022 版新课标后可能考查方式已经变了。
# 这里是唯一能被机器自动发现的地方，所以做成了显式告警而不是留给人工。
# ==========================================================================
EXAM_TYPES = [
    ("中考真题", ("中考", "中招")),
    ("高考真题", ("高考",)),
    ("统考/联考", ("统考", "联考", "质检", "抽考")),
    ("模拟卷", ("模拟", "押题", "仿真")),
    ("期末卷", ("期末",)),
    ("期中卷", ("期中",)),
    ("月考题", ("月考", "月测")),
    ("单元测", ("单元", "章节")),
    ("开学考", ("开学", "入学", "摸底", "期初")),
    ("竞赛题", ("竞赛", "奥赛")),
]
SCHOOL_SCOPES = [
    ("全国统考", ("全国",)),
    ("省级", ("省级", "省统考", "省质检")),
    ("市级", ("市级", "市统考", "市质检")),
    ("区县级", ("区统考", "区级", "县级")),
    ("校级", ("校级", "校内", "本校")),
]
# 现行课程方案/课标施行年份：早于它的真题需要人工核对是否符合现行教材
STD_REFORM_YEAR = [("高中", 2020), ("小学", 2022), ("初中", 2022)]
FRESHNESS_TIERS = [(1, "当年题"), (3, "近3年"), (5, "5年内"), (99, "5年以上")]


def _stage_reform_year(stage):
    """学段 -> 现行课程方案施行年份。高中按其 2017 版课标 2020 年修订计。"""
    s = str(stage or "")
    for k, y in STD_REFORM_YEAR:
        if k in s:
            return y
    return 2022


def parse_paper_label(label, stage=None, this_year=None):
    """把试卷出处拆成结构化信息。解析不出来就返回空字段，**绝不猜**。

    返回 dict：year / season / region / exam_type / scope / freshness / age /
    outdated（是否早于现行课程方案）/ reform_year / tag（给人看的一句话）
    """
    s = str(label or "").strip().strip("（）()").strip()
    r = {"label": s, "year": None, "season": "", "region": "", "exam_type": "",
         "scope": "", "freshness": "年份不明", "age": None, "outdated": False,
         "reform_year": None, "tag": ""}
    if not s:
        return r

    m = re.search(r"(?:19|20)\d{2}", s)
    if m:
        r["year"] = int(m.group(0))
    ms = re.search(r"(春|夏|秋|冬|暑)", s)
    if ms:
        r["season"] = ms.group(1)

    for name, kws in EXAM_TYPES:                       # 按权威度取第一个命中的即可
        if any(k in s for k in kws):
            r["exam_type"] = name
            break
    for name, kws in SCHOOL_SCOPES:
        if any(k in s for k in kws):
            r["scope"] = name
            break

    for part in [p.strip() for p in re.split(r"[•·｜|▼]", s) if p.strip()]:
        mm = re.search(r"[\u4e00-\u9fa5]{2,8}(?:省|市|自治区|区|县|州|盟|旗|地区)", part)
        if mm:
            r["region"] = mm.group(0)
            break

    ry = _stage_reform_year(stage)
    r["reform_year"] = ry
    if r["year"]:
        y = this_year or datetime.date.today().year
        r["age"] = max(y - r["year"], 0)
        for hi, name in FRESHNESS_TIERS:
            if r["age"] <= hi:
                r["freshness"] = name
                break
        if ry and r["year"] < ry:
            r["outdated"] = True

    bits = [b for b in (r["freshness"], r["exam_type"], r["scope"]) if b]
    r["tag"] = "·".join(bits) or "出处信息不足"
    return r


# ==========================================================================
# 二·五、文献著录规范（GB/T 7714—2015 简化版）
# 溯源要「可点击、可复核」，就必须给全著录字段：只写"谭霈生《论戏剧性》"
# 教师没法在 CNKI 上定位到具体哪一篇、哪一年、第几期。
# 不同文献类型的著录项不同，硬套"作者+篇名+期刊+年+期"会让专著被迫伪造
# 期刊名和期号——那是比没有溯源更糟的事。所以按 type 分流。
# ==========================================================================
SOURCE_TYPES = {
    # need = 该类型必须给全的字段；缺了就计入「著录缺口」告警而不是编造填充
    "journal":   {"label": "期刊论文", "need": ["author", "title", "container", "year", "issue"]},
    "book":      {"label": "专著",     "need": ["author", "title", "publisher", "year"]},
    "chapter":   {"label": "文集析出", "need": ["author", "title", "container", "publisher", "year"]},
    "thesis":    {"label": "学位论文", "need": ["author", "title", "publisher", "year"]},
    "newspaper": {"label": "报纸",     "need": ["author", "title", "container", "year"]},
    "textbook":  {"label": "教材",     "need": ["title", "publisher", "year"]},
}

_PENDING = "【待补充】"

# 溯源来源优先级（越靠前越优先）。为什么期刊第一：
# ① 教师复核时，期刊论文在 CNKI 上最好定位（作者+篇名+刊名+年+期），专著常有多种版本；
# ② 期刊论文的时效性、观点集中度更适合做材料题；
# ③ 用户明确要求「作者、篇名、来源期刊、年份、期」这条五字段著录，只有 journal 能完整给出。
# 教材排最后：只在题目本身引用教材原文/注释时才算溯源，不能拿教材冒充学术出处。
SOURCE_PRIORITY = ["journal", "thesis", "newspaper", "book", "chapter", "textbook"]


# 学科包只有 6 个（语文/数学/英语/理化生/政史地/音体美），但教师会说"物理""历史"。
# 没有别名表时 "物理" 会静默落到数学包——题型没有实验设计、刊物推荐数学刊物，事故就在这。
SUBJECT_ALIAS = {
    "物理": "理化生", "化学": "理化生", "生物": "理化生", "科学": "理化生",
    "道德与法治": "政史地", "政治": "政史地", "历史": "政史地", "地理": "政史地",
    "音乐": "音体美", "体育": "音体美", "美术": "音体美",
}


def normalize_subject(subject):
    """学科名 -> 学科包键。细分学科（物理）映射到所属包（理化生）；未命中返回 None。"""
    if subject in SUBJECT_PACKS:
        return subject
    return SUBJECT_ALIAS.get(subject or "")


def get_pack(subject, stage):
    """取约束包。未命中必须报错而不是退化成别的学科——静默套用数学规则会产出错误题型。"""
    key = normalize_subject(subject)
    if key is None:
        raise SystemExit("未知学科 %r。可用学科包：%s；或其细分学科：%s"
                         % (subject, "、".join(SUBJECT_PACKS), "、".join(SUBJECT_ALIAS)))
    sp = SUBJECT_PACKS[key]
    stp = STAGE_PACKS.get(stage or "", STAGE_PACKS["初中(7-9)"])
    return {"subject": subject, "stage": stage, "pack_key": key,
            "subject_pack": sp, "stage_pack": stp}


# ==========================================================================
# 三、Prompt 拼装：通用模板 + 学科包 + 学段包（+ 供题计划）
# ==========================================================================
BASE_TEMPLATE = """# 角色
你是「中小学作业设计助手」，依托 CNKI 学术资源与《{std_doc}》，
为教师生成可溯源、对齐课标、分层有据的作业题。
你不替代教师决策——输出永远是待审草稿，不是可直接布置的成品。

# 输入变量
- 学科/学段/年级：{subject} / {stage} / {grade}
- 单元/主题：{unit}
- 课标条目（教师填写，可空）：{std}
- 关联核心素养：{literacy}
- 班级水平：{class_profile}
- 分层比例（基础:巩固:拓展）：{ratio}
- 题型偏好：{types}
- 题量/时长上限：{total_count} 题 / {max_minutes} 分钟
- 是否情境化：{with_context}

# 差异化四锚（这是本产品区别于通用 AI 出题的全部内容）
每道题必须同时具备四个可验证的锚点，缺一个就不是一个合格的产出：
1. 出处：材料/情境题必须挂 CNKI 真实文献出处，可点击溯源
2. 对齐：绑定具体课标条目原文，而不是泛泛的"符合教学要求"
3. 分层依据：按下面学科包定义的分层规则出题，不许凭感觉标难度
4. 认知层级：明确标注布鲁姆层级且不超学段上限

    {pack_text}
    {plan_block}
    {shared_block}
    {topic_block}
# 输出格式（严格 JSON，禁止任何额外解释文字）
{{
  "meta": {{
    "std_aligned": "课标条目原文（必须来自上方输入或检索到的课标库）",
    "literacy": ["核心素养1", "核心素养2"]
  }},
  "items": [
    {{
      "id": 1,
      "level": "基础|巩固|拓展",
      "type": "题型（限学科包 types 白名单）",
      "cognitive": "记忆|理解|应用|分析|评价|创造",
      "stem": "题干（分句不超过 {smax} 字）",
      "answer": "参考答案",
      "analysis": "分步解析",
      "answer_check": {{
        "changed": "adapt 题必填：相对原题改了哪些数据/条件，逐项列清",
        "recompute": "adapt 题必填：用改动后的数据重新求解的过程与结果",
        "verdict": "adapt 题必填：一致（只能填这个；若复算对不上就改数据或改答案后重算）"
      }},
      "dur": 单题预计分钟数（数字）,
      "mode": "written|oral",
      "origin": "retrieve|adapt|generate",
      "source_id": "retrieve 题必填：原题库编号，同时 source_label 填真实试卷出处",
      "based_on": "adapt 题必填：改编自哪道题的 bank_id（机器去重用，不印在作业单上）",
      "based_on_label": "adapt 题必填：该题的真实试卷出处，如「2026秋•昌吉州校级月考」，原样照抄题源出处行",
      "rubric": "写作/作品题必填评价量规",
      "safety": "理化生实验题必填安全提示",
      "sources": [
        {{
          "type": "journal|book|chapter|thesis|newspaper|textbook",
          "author": "作者，多作者用逗号分隔",
          "title": "篇名（期刊/报纸/学位/析出）或书名（专著）",
          "container": "来源期刊名 / 报纸名 / 文集名（专著不需要）",
          "publisher": "出版社或学位授予单位（期刊不需要）",
          "year": 2024,
          "issue": "期号，期刊专用，如 3",
          "pages": "起止页码，如 12-20",
          "generic": false
        }}
      ]
    }}
  ]
}}

# 硬性约束（违反任一条，下游校验器会整批拦截）
1. 学术溯源：学科包 sources.require_for 列出的题型，sources 至少 1 条且 generic=false。
2. 课标对齐：meta.std_aligned 必填，且必须是真实课标条目，不得自行杜撰。
3. 分层规则：严格按上方学科包 levels 定义（知识点数量与步骤数不得越界）。
3b. 分层语义：上方学科包 levels 中每层的「学情」「培养目标」为该层定位，出题内容须贴合对应学情，解析/答案须指向该层培养目标。
4. 语言规范：题干分句不超过 {smax} 字；禁用"超纲/竞赛/极难"；用词限教学白名单。
5. 答案正确：每题必附 answer + analysis；应用题数据须有唯一可算解，不得自相矛盾。
   改编题（adapt）另须附 answer_check 一致性验算（改了什么 / 重算过程 / 结论），三者缺一不可。
6. 反幻觉：sources 必须是真实可检索的文献，禁止编造。无法溯源就标 generic=true 并去掉情境。
6b. 著录完整：sources 必须给全该 type 要求的字段（期刊=作者·篇名·来源期刊·年份·期；
    专著=作者·书名·出版社·年份；教材=书名·出版社·年份）。拿不准的字段宁可留 null 由教师补，
    也不许凭印象填——缺字段只会被记成「著录缺口」告警，填错了是编造。
6c. 来源优先级（重要）：**优先引用 CNKI 期刊论文（type=journal）**，其次学位论文、报纸，
    再次专著与文集析出；教材只在题目本身引用教材原文时才算出处，不得拿教材冒充学术来源。
    优先从本学科刊物中取材：{venues}。
    理由：期刊能给出完整的"作者·篇名·来源期刊·年份·期"，教师复核时可精确定位；
    专著版本多、定位困难，属于次选。同一论点有期刊可引时，不要引专著。
7. 必填字段：按学科包 quant.must_fields / extra_fields 补齐，缺一个都会被拦。
8. 政策红线：小学一二年级不布置书面家庭作业（mode 必须为 oral）；总时长不得超过 {max_minutes} 分钟。
    {plan_rule}
    {shared_rule}
    {topic_rule}
# 禁止
- 禁止"据研究表明…"却没有 sources 的句子
- 禁止答案矛盾、无解、超纲的题目
- 禁止脱离输入课标条目自行发挥
- 政史地：禁止使用不合规地图；涉及台湾、香港、澳门必须表述为中国的一部分
"""


def _venues_for(subject, stage):
    """学科刊物白名单按学段过滤：高中语文包里躺着《小学语文教学》，直接用会闹笑话。"""
    vs = SUBJECT_PACKS.get(normalize_subject(subject) or "", {}).get("sources", {}).get("venues", []) or []
    if subject in SUBJECT_ALIAS:      # 物理题不推《化学教学》：细分学科只保留本学科刊物
        mine = [v for v in vs if subject in v]
        if mine:
            vs = mine
    if "高中" in str(stage) or "初中" in str(stage):
        vs = [v for v in vs if "小学" not in v and "幼" not in v]
    return vs


def build_prompt(p):
    """p 为参数字典，缺字段给默认值而不是报错。"""
    subject = p.get("subject", "数学")
    stage = p.get("stage", "初中(7-9)")
    pack = get_pack(subject, stage)
    sp, stp = pack["subject_pack"], pack["stage_pack"]

    limit = p.get("max_minutes") or stp.get("max_minutes")
    pack_text = (
        "【学科约束包 · %s】\n%s\n\n【学段约束包 · %s】\n%s"
        % (subject, json.dumps(sp, ensure_ascii=False, indent=1),
           stage, json.dumps(stp, ensure_ascii=False, indent=1))
    )

    plan_block = ""
    plan_rule = ""
    if p.get("plan_text"):
        plan_block = "# 供题计划（必须严格遵守）\n%s\n" % p["plan_text"]
        plan_rule = (
            "9. 供题方式：严格按供题计划中每题给出的 mode 输出同名的 origin，禁止擅自改档——"
            "不得把 retrieve 改成 adapt/generate（等于把可以原样用的真题擅自改掉了），"
            "也不得把 adapt 改成 retrieve（会漏填改编依据）。\n"
            "10. retrieve 题的处理原则：该题目标是「拿来就能布置」，因此题干、选项、设问、数据一律原样保留，"
            "不得润色、不得优化表述；你需要补的只有课标绑定、认知层级、估时与解析。"
            "答案沿用原题；若发现原题疑似有误，改为 adapt 并在 meta.notes 里说明，不得自行改题面。\n"
            "11. adapt 题必须做答案一致性验算并填 answer_check{changed, recompute, verdict}："
            "changed 逐项列出相对原题改了哪些数据/条件；recompute 是用改动后的数重新求解的过程；"
            "verdict 只能填「一致」。**改了数据却沿用原答案是这套系统里最贵的错误**——"
            "教师发现一次就不会再用第二次，宁可少出一道，不可错一道。\n"
            "12. 真题年份早于现行课程方案施行年的（计划里已标「可能基于旧教材」），必须在 meta.notes 注明"
            "「该真题出版于 XXXX 年，早于 YYYY 年版课程方案，使用前请核对是否符合现行教材」，不得默认适用。\n"
        )

    # 同材异层（共享材料）模式：老师在 params.shared_material 给一份材料，
    # 全部题目基于它分层。prompt 注入材料 + 约束，模型回写 meta.shared_material 供 render 顶部渲染一次。
    shared_block = ""
    shared_rule = ""
    _sm = (p.get("shared_material") or "").strip()
    if _sm:
        shared_block = (
            "# 共享材料（本作业单全部题目基于同一份材料）\n"
            "以下为唯一共享材料，请原样引用，不要在任意一题里重复粘贴材料正文：\n\n"
            "<<<\n" + _sm + "\n>>>\n\n"
            "请严格按此模式出题：所有题目的 stem 只写「问什么」，用「根据材料…」指代上方材料；"
            "各题 material 字段留空（材料统一在顶部展示一次，不在题内重复）。\n"
        )
        shared_rule = (
            "13. 共享材料模式：输出 JSON 的 meta 必须回写 shared_material 字段，"
            "内容与上方「共享材料」一字不差（便于下游统一渲染一次）；"
            "各题 material 字段留空，stem 只写设问、用「根据材料」指代，禁止在题内重复材料正文。\n"
        )

    # 同主题作文分层：老师围绕一个作文主题(unit)要三档不同立意的写作题。
    # 背景：语文 levels 把「写作」放在拓展层、基础层是字词句，模型极易把基础层退化成字词/阅读，
    # 导致三层题型不一致（不是三个作文）。此处显式约束三层都围绕 unit、题型统一为写作、不同立意。
    topic_block = ""
    topic_rule = ""
    _types = p.get("types") or "、".join(sp.get("types", []))
    _is_writing = ("写作" in str(_types)) or (subject == "语文" and any("写作" in t for t in sp.get("types", [])))
    _unit = (p.get("unit") or "").strip()
    if _is_writing and _unit:
        topic_block = (
            "# 同主题作文分层（本次关键要求）\n"
            "单元/主题为「%s」，三层均须**围绕此同一主题命题、题型统一为写作**，"
            "分别给出由浅入深、适配各层学情的**立意方向**，禁止三层写成不同主题、"
            "禁止把基础层退化成字词默写或单篇阅读理解：\n" % _unit +
            "- 基础层（基础较弱学生）：把一件事写清楚、写完整，情感真实不空洞，"
            "侧重语言建构与运用（记叙要素齐全、语句通顺）；立意可以是「我学会了…」「那一刻我被…」式平实表达。\n"
            "- 巩固层（中等学生）：在叙事基础上写出细节描写与真实感受，"
            "立意落到「我懂得了…（坚持/感恩/勇气/责任）」，侧重思维发展与提升·审美鉴赏与创造。\n"
            "- 拓展层（优秀学生）：立意新颖或思想深刻，可用独特视角、象征、跨媒介或创意结构，"
            "侧重审美鉴赏与创造·文化传承与理解（立意不落俗套、有个人思想）。\n"
        )
        topic_rule = (
            "14. 同主题作文分层：三层都必须是写作题且同主题「%s」，"
            "各层 stem 写清本层「立意方向 + 写作要求 + 字数」，"
            "三层 rubric 量规须对应各层培养目标（基础=内容完整·语言通顺；"
            "巩固=细节·情感；拓展=立意·创意）。\n" % _unit
        )

    return BASE_TEMPLATE.format(
        std_doc=stp.get("std", "义务教育课程方案(2022)"),
        subject=subject, stage=stage, grade=p.get("grade", ""),
        unit=p.get("unit", ""), std=p.get("std", ""), literacy=p.get("literacy", ""),
        class_profile=p.get("class_profile", "均衡型"), ratio=p.get("ratio", "5:3:2"),
        types=p.get("types", "、".join(sp.get("types", []))),
        total_count=p.get("total_count", 10), max_minutes=limit,
        with_context=p.get("with_context", "是"),
        smax=stp.get("sentence_len_max", 25),
        venues="、".join(_venues_for(subject, stage)) or "本学科核心期刊",
        pack_text=pack_text, plan_block=plan_block, plan_rule=plan_rule,
        shared_block=shared_block, shared_rule=shared_rule,
        topic_block=topic_block, topic_rule=topic_rule,
    )


# ==========================================================================
# 四、供给路由：混合配额（mix）
#
# 这里经历过一次认知修正。旧版实际只有「改编 + 少量原创」在跑，retrieve 从未被自动
# 分配过——模型永远在改题，教师拿不到一道可以原样布置的真实考题。用户提出"是不是也该
# 有部分已考过的题让老师选"，根因就是这个：不是缺能力，是缺「混合」这个选项。
#
# 关键分界不是「原创还是检索」，而是**这份作业要不要拿去打分**：
#   · 作业的目的是「学会」，学生见到真题是优点（真实难度、真实设问、答案已被考试校验）；
#   · 只有承担评价功能（周测/月测，要出分、要横向比较）时，学生见过原题才是事故。
# 所以配额必须跟着「作业用途」走，而不是一个固定的 5:3:2。
#
# supply 取值：mix（默认，按用途配比）/ retrieve / adapt / generate（强制单一档）。
# ==========================================================================
JOB_PRESETS = {
    "课前预学": {"orig": 0.70, "adapt": 0.20, "gen": 0.10,
                 "why": "作业目的是摸底而非打分，学生没见过真题才能暴露真实水平；"
                        "真题答案经过考试校验，是最可信的基线"},
    "课后巩固": {"orig": 0.40, "adapt": 0.50, "gen": 0.10,
                 "why": "当天刚讲过同构例题，需要变式防止照抄记忆；"
                        "但要留一两道真题对标真实难度、真实设问"},
    "单元作业": {"orig": 0.35, "adapt": 0.50, "gen": 0.15,
                 "why": "综合贯通阶段，真题交代真实考查方式，改编承担难度梯度，原创补覆盖缺口"},
    "阶段测验": {"orig": 0.10, "adapt": 0.60, "gen": 0.30,
                 "why": "要出分、要横向比较，学生背过原题会让成绩失真——"
                        "这是唯一必须压制原题的场景"},
    "备考复习": {"orig": 0.65, "adapt": 0.30, "gen": 0.05,
                 "why": "熟悉真题的题型、难度、设问本身就是备考内容，原题在此价值最高"},
    "错题重做": {"orig": 0.05, "adapt": 0.75, "gen": 0.20,
                 "why": "目标是同考点二刷换数据换情境；此时留原题等于让学生背答案"},
}

JOB_ALIAS = {
    "预学": "课前预学", "预习": "课前预学", "前置作业": "课前预学", "导学案": "课前预学",
    "课后": "课后巩固", "课时作业": "课后巩固", "单课时作业": "课后巩固", "作业": "课后巩固",
    "单元": "单元作业", "单元复习": "单元作业", "整本书": "单元作业",
    "周测": "阶段测验", "月测": "阶段测验", "月考": "阶段测验", "单元测验": "阶段测验",
    "期中": "备考复习", "期末": "备考复习", "备考": "备考复习", "冲刺": "备考复习", "总复习": "备考复习",
    "错题": "错题重做", "二刷": "错题重做", "滚动复习": "错题重做", "错题本": "错题重做",
}
DEFAULT_JOB = "课后巩固"
SUPPLY_MODES = ("mix", "retrieve", "adapt", "generate")

# 每层取 mode 的优先级顺序：原题天然偏基础（单点、答案稳定），原创偏拓展（新情境），改编兜中间。
# 全局配额是硬的——这一层先取哪一档，只决定同配额下原题落在哪一层，不改变总配额。
LEVEL_MODE_ORDER = {
    "基础": ["retrieve", "adapt", "generate"],
    "巩固": ["adapt", "retrieve", "generate"],
    "拓展": ["adapt", "generate", "retrieve"],
}


def _job_key(s):
    """用途名 -> JOB_PRESETS 键。教师不会说「单元作业」，只会说「单元」。"""
    s = str(s or "").strip()
    if s in JOB_PRESETS:
        return s
    return JOB_ALIAS.get(s)


def _split_quota(total, weights):
    """按比例把题量硬分成三份，保证三份之和严格等于 total（最大余数法）。

    用 round 会在各处差一题，导致 plan 说 3 道原题、实际只出得到 2 道。
    余数最大的档优先补足——否则 8 题 ×10% 的原创会被 floor 成 0，
    小样本下小比例那档直接消失。
    """
    raw = {k: total * float(weights[k]) for k in weights}
    base = {k: int(math.floor(raw[k])) for k in weights}
    order = sorted(weights, key=lambda k: raw[k] - math.floor(raw[k]), reverse=True)
    rem = total - sum(base.values())
    for i in range(max(rem, 0)):
        base[order[i % len(order)]] += 1
    while sum(base.values()) > total:                       # 权重和 >1 时从最多的档扣回
        k = max(base, key=lambda x: base[x])
        if base[k] <= 0:
            break
        base[k] -= 1
    return base


def resolve_supply(p, total):
    """决定三档配额。返回 dict：supply / job_type / quota / why。"""
    supply = str(p.get("supply") or "mix").strip().lower()
    if supply not in SUPPLY_MODES:
        raise SystemExit("未知供给模式 %r。可选：%s" % (supply, "、".join(SUPPLY_MODES)))

    job = _job_key(p.get("job_type") or DEFAULT_JOB)
    if job is None:
        raise SystemExit("未知作业用途 %r。可选：%s；或其简称：%s"
                         % (p.get("job_type"), "、".join(JOB_PRESETS), "、".join(JOB_ALIAS)))

    if supply != "mix":
        q = {"retrieve": 0, "adapt": 0, "generate": 0}
        q[supply] = total
        return {"supply": supply, "job_type": job, "quota": q, "overridden": "",
                "why": "教师指定单一供给：全部走「%s」档" % MODE_LABEL[supply]}

    w = JOB_PRESETS[job]
    quota = _split_quota(total, {"retrieve": w["orig"], "adapt": w["adapt"], "generate": w["gen"]})
    note = ""
    if p.get("gen_cap") is not None:
        # 显式给 gen_cap 时，锁死原创额度，剩下的按预设比例分给真题/改编
        cap = min(max(float(p["gen_cap"]), 0.0), 1.0)
        n_gen = int(round(total * cap))
        rest = total - n_gen
        s = float(w["orig"] + w["adapt"]) or 1.0
        n_ada = int(math.floor(rest * w["adapt"] / s))
        quota = {"retrieve": rest - n_ada, "adapt": n_ada, "generate": n_gen}
        note = ("教师显式指定 gen_cap=%.2f → 原创锁定 %d 题，其余 %d 题按「%s」的预设比例分给真题与改编"
                % (cap, n_gen, rest, job))
    return {"supply": supply, "job_type": job, "quota": quota, "overridden": note, "why": w["why"]}


def presets_text():
    lines = ["%-8s %6s %6s %6s  %s" % ("作业用途", "原题", "改编", "原创", "为什么这么配")]
    for k, v in JOB_PRESETS.items():
        lines.append("%-8s %5.0f%% %5.0f%% %5.0f%%  %s"
                     % (k, v["orig"] * 100, v["adapt"] * 100, v["gen"] * 100, v["why"]))
    lines += ["", "简称：%s" % "、".join("%s→%s" % (a, b) for a, b in JOB_ALIAS.items())]
    return "\n".join(lines)


def _candidates_from_bank(bank, cap=40, with_answer=False):
    """题库原始 JSON -> 候选列表 [{bank_id, stem, level, label(, answer)}]。

    三件必须在这里做掉的事：
    - 候选池不能截断到前 12 条：那样后面的层没有候选可用，会被迫跨层级跨知识点补底座。
      上限放宽到 40 条（plan 文本里每条只摘 200 字题干，体量仍可控）。
    - `bank_id` 只是内部流水号，对外毫无意义；真正要给教师看的是 `Label`（试卷出处），
      两者必须同时取到，缺 label 会让作业单印出「改编自 Q07」这种黑话。
    - 变式包要拿母亲的答案做验算基准，所以答案字段按需取（with_answer）。
    """
    cands = []
    for i, it in enumerate(bank[:cap], 1):
        if not isinstance(it, dict):
            cands.append({"bank_id": "B%d" % i, "stem": str(it)[:200], "level": "", "label": "", "answer": ""})
            continue
        meta = it.get("metadata") or {}
        # ⚠ 字段名是 source_label（不是 label / source）——取错会让候选题全部丢出处，
        #   模型就无从判断这道题来自哪份试卷，真题新鲜度也跟着失效。
        lab = meta.get("source_label") or meta.get("label") or meta.get("source") or ""
        cand = {
            "bank_id": meta.get("bank_id") or ("B%d" % i),
            "stem": (it.get("content") or it.get("text") or it.get("stem") or "")[:200],
            "level": meta.get("level") or meta.get("difficulty") or "",
            "label": lab,
            "answer": (it.get("answer") or meta.get("answer") or "")[:200] if with_answer else "",
        }
        # 考点：选题时用来判断有没有超纲，比看题干猜可靠
        pts = meta.get("points") or []
        if pts:
            cand["points"] = pts[:5]
        # 官方解析标记：有官方解析的题优先选（第 14 条验算有外部基准，风险低）。
        # 只带标记和答案不带正文，否则 40 条候选的 plan 文本会被撑爆。
        if meta.get("official_analysis"):
            cand["has_official"] = True
        if meta.get("official_answer"):
            cand["official_answer"] = meta["official_answer"]
        cands.append(cand)
    return cands


def route_supply(p):
    stage = p.get("stage", "初中(7-9)")
    pack = get_pack(p.get("subject", "数学"), stage)
    stp = pack["stage_pack"]

    bank = p.get("bank") or []
    if isinstance(bank, str):
        try:
            bank = json.loads(bank)
        except Exception:
            bank = [{"content": bank}]

    cands = _candidates_from_bank(bank)

    total = int(p.get("total_count") or 10)
    parts = [float(x) for x in (p.get("ratio") or "5:3:2").replace("：", ":").split(":")]
    if len(parts) != 3 or sum(parts) <= 0:
        parts = [5, 3, 2]
    rsum = float(sum(parts))
    levels = ["基础", "巩固", "拓展"]
    counts, acc = {}, 0
    for i, lv in enumerate(levels):
        n = int(round(total * parts[i] / rsum))
        if i == len(levels) - 1:
            n = total - acc
        counts[lv] = max(n, 0)
        acc += counts[lv]

    # 配额不看旧版那个「每层第一题给原创」的固定套路，改由用途决定三档各多少题。
    supply = resolve_supply(p, total)
    quota = dict(supply["quota"])

    per_level = {lv: ([c for c in cands if lv in str(c.get("level", ""))] or cands) for lv in levels}

    # 候选分配必须去重：早期版本用 pool[k % len(pool)]，候选不足时同一 bank_id 会被
    # 分给多道题，产出「孪生题」（两道题改编自同一道原题）。已用集合 + 跨层共享。
    used = set()

    def _pick(pool):
        # ① 优先本层池内未用过的候选
        for c in pool:
            if c["bank_id"] not in used:
                used.add(c["bank_id"])
                return c, False
        # ② 本层池用尽，从全库未用候选中补（难度档标注不准时靠这步兜底）
        for c in cands:
            if c["bank_id"] not in used:
                used.add(c["bank_id"])
                return c, False
        # ③ 真的没有未用候选了，才被迫复用
        if not (pool or cands):
            return None, False
        src = pool or cands
        return src[len(used) % len(src)], True

    # 教师可以逐题指定供给方式：params["overrides"] = {"3": "retrieve", "7": "adapt"}。
    # 配额是统计意义上的默认值，而教师见过这些题、比配额更懂本班——所以指认优先级高于配额。
    # 这也是「让老师选」最直接的落地：不必为了改一道题去整体切换作业用途。
    forced, forced_bad, borrowed = {}, [], []
    for k, v in (p.get("overrides") or {}).items():
        try:
            idx = int(k)
        except Exception:
            forced_bad.append("题号 %r 不是整数" % k)
            continue
        m = str(v or "").strip().lower()
        if m not in MODE_LABEL:
            forced_bad.append("第 %s 题=%r（只能 retrieve/adapt/generate）" % (k, v))
        elif 1 <= idx <= total:
            forced[idx] = m
        else:
            forced_bad.append("第 %s 题=%r（超出题量 %d）" % (k, v, total))

    plan = []
    for lv in levels:
        pool = per_level[lv]
        for _ in range(counts[lv]):
            n = len(plan) + 1
            note = ""
            forced_mode = forced.get(n)
            if forced_mode:
                # ① 教师指认优先：配额只是默认值，见上面那段
                mode = forced_mode
                note = "教师指定本题走「%s」" % MODE_LABEL[mode]
            else:
                # ② 否则按本层的 mode 偏好取一个还有余额的档（总配额是硬的，这一步只决定落在哪层）
                mode = None
                for m in LEVEL_MODE_ORDER[lv]:
                    if quota.get(m, 0) > 0:
                        mode = m
                        break
            if mode is None:                       # 配额被前几层打空了
                mode = "adapt" if cands else "generate"
                note = "%s；配额已用尽，按兜底方式出" % note if note else "配额已用尽，按兜底方式出"
            # ③ 但 retrieve/adapt 都必须有候选底座，没题库就不能硬撑
            if mode in ("retrieve", "adapt") and not cands:
                mode = "generate"
                note = "%s；题库无候选题，降级为原创" % note if note else "题库无候选题，降级为原创"
            if forced_mode and quota.get(mode, 0) <= 0:
                borrowed.append("第 %d 题按教师指定走了「%s」，该档配额已分完，各档题数随之调整"
                                % (n, MODE_LABEL[mode]))
            quota[mode] = quota.get(mode, 0) - 1

            if mode == "generate":
                reason = "出新情境题并挂 CNKI 素材溯源"
                plan.append({"level": lv, "mode": "generate", "override": bool(forced_mode),
                             "reason": ("%s；%s" % (note, reason)) if note else reason,
                             "bank_id": "", "bank_stem": "", "bank_label": "", "freshness": ""})
                continue

            b, reused = _pick(pool)
            _lab = b.get("label") or ""
            if mode == "retrieve":
                reason = ("题库真题原样布置（%s%s）：题面/选项/设问一字不改，答案沿用原题，"
                          "只补绑课标条目、标注认知层级与估时" % (b["bank_id"], "，%s" % _lab if _lab else ""))
            else:
                reason = "题库有候选题（%s%s），按本班学情改参数/换情境/调难度" % (
                    b["bank_id"], "，%s" % _lab if _lab else "")
                if reused:
                    reason += "；候选题已用尽，被迫复用该题，必须显著改编（换情境或换设问），不得与原改编题雷同"
            if note:
                reason = "%s；%s" % (note, reason)
            # 真题出处里藏着新鲜度与考试类型，机器拆开给教师看，别让人自己读流水串
            _info = parse_paper_label(_lab, stage)
            plan.append({"level": lv, "mode": mode, "reason": reason,
                         "bank_id": b["bank_id"], "bank_stem": b["stem"],
                         "bank_label": _lab, "reused": reused,
                         "override": bool(forced_mode), "freshness": _info["tag"],
                         "label_year": _info["year"], "label_outdated": _info["outdated"]})

    # 政策红线直接压到供给层：低段一律转口头/实践任务
    if stp.get("allow_written") is False:
        for x in plan:
            x["mode"] = "adapt" if x["bank_id"] else "generate"
            x["reason"] = "小学低段不布置书面作业，改为口头表达/实践任务"
            x["force_oral"] = True

    # 题库不足会把 retrieve/adapt 降级成 generate，此时必须放宽原创上限——
    # 否则校验器会把「客观无处可选」报成「教师超配额」，那是误报。
    gen_actual = len([x for x in plan if x["mode"] == "generate"])
    gen_planned = supply["quota"]["generate"]
    gen_max = max(gen_planned, gen_actual)
    degraded = []
    if gen_actual > gen_planned:
        degraded.append("题库候选不足，%d 道题由原题/改编降级为原创（原计划原创 %d 题）"
                        % (gen_actual - gen_planned, gen_planned))

    ctx_on = str(p.get("with_context", "")).strip() == "是"
    q = supply["quota"]
    lines = [
        "## 供题计划（共 %d 题）" % total,
        "分层题量：基础 %d · 巩固 %d · 拓展 %d" % (counts["基础"], counts["巩固"], counts["拓展"]),
        "原创题上限：%d 题" % gen_max,
        "",
        "### 本次供给策略",
        "- 模式：%s　作业用途：%s" % (supply["supply"], supply["job_type"]),
        "- 配额：真题原样选用 %d 题 · 改编变式 %d 题 · 原创生成 %d 题" % (
            q["retrieve"], q["adapt"], q["generate"]),
        "- 依据：%s" % supply["why"],
    ]
    act = {m: len([x for x in plan if x["mode"] == m]) for m in MODE_LABEL}
    if any(act[m] != q.get(m, 0) for m in MODE_LABEL):
        lines.append("- 实际分配：真题 %d 题 · 改编 %d 题 · 原创 %d 题（教师指认后与配额不同，以实际分配为准）"
                     % (act["retrieve"], act["adapt"], act["generate"]))
    if forced:
        lines.append("- 教师逐题指认：%s（指认优先于配额）"
                     % "、".join("第%d题→%s" % (n, MODE_LABEL[m]) for n, m in sorted(forced.items())))
    if forced_bad:
        lines.append("- 指认无效已忽略：%s" % "；".join(forced_bad))
    for b in borrowed:
        lines.append("- 配额调整：%s" % b)
    if supply["overridden"]:
        lines.append("- 覆盖：%s" % supply["overridden"])
    if gen_actual > gen_planned:
        lines.append("- 降级：题库候选不足，%d 道题由原题/改编降级为原创（已放开原创上限，属客观无奈）"
                     % (gen_actual - gen_planned))
    lines += [
        "",
        "### 为什么这里可以直接用考过的真题",
        "- 作业的目的是「学会」不是「区分」。学生见到真题不是缺点：那意味着真实难度、真实设问、答案已被考试校验。",
        "- 只有这份作业要出分、要排队名（周测/月测/单元测验）时才必须压制原题，否则学生背答案、成绩失真。",
        "- retrieve 题的价值恰恰在「拿来就能用」，所以**题面一字不改**——擅自润色就等于取消了这一档。",
        "",
        "### 每题供题方式（必须严格遵守，并在输出 JSON 中填写 origin 字段）",
    ]
    for i, x in enumerate(plan, 1):
        lines.append("%d. [%s/%s·%s] %s" % (
            i, x["level"], x["mode"], MODE_LABEL.get(x["mode"], x["mode"]), x["reason"]))
        if x["bank_stem"]:
            lines.append("   候选题干（%s）：%s" % ("原样使用" if x["mode"] == "retrieve" else "改编素材",
                                                    x["bank_stem"]))
        if x["mode"] == "retrieve":
            lines.append("   硬要求：题面/选项/设问**一字不改**，答案沿用原题；你只补课标绑定、认知层级、估时、解析")
            lines.append("   必填：source_id = %s" % x["bank_id"])
        if x.get("bank_label"):
            field = "source_label" if x["mode"] == "retrieve" else "based_on_label"
            lines.append("   题源出处：%s → 输出 JSON 中 %s 必须原样填这个" % (x["bank_label"], field))
        if x.get("freshness"):
            lines.append("   真题新鲜度：%s%s" % (
                x["freshness"],
                "；注意：该真题出版于 %d 年，早于现行课程方案（%d 年版），使用前须核对是否符合现行教材"
                % (x["label_year"], _stage_reform_year(stage)) if x.get("label_outdated") else ""))
        if x["mode"] == "adapt":
            lines.append("   必做：填 answer_check{changed, recompute, verdict}——改了哪些数据、用新数据重算一遍、结论只能写「一致」")
        if x.get("reused") and x["mode"] == "adapt":
            lines.append("   警告：候选题已用尽，此题被迫复用底座，必须显著改编，不得与同底座的另一题雷同")
        if x.get("force_oral"):
            lines.append("   强制：mode 字段必须填 oral")
    lines += [
        "",
        "### 三档定义",
        "- retrieve：题库真题**原样取用**——题面不改，只补课标绑定与层级标注。origin='retrieve'，"
        "必填 source_id 与 source_label（真实试卷出处）。发现原题有误不得自行改题面，降级为 adapt 并在 notes 说明",
        "- adapt：在候选题干基础上改参数/换情境/调难度，origin='adapt'，必须填 based_on（原题 bank_id）"
        " 与 based_on_label（真实试卷出处）",
        "- generate：原创生成，origin='generate'，必须填 sources（CNKI 素材出处，generic=false）",
        "",
        "### 硬约束",
        "1. 原创题不得超过 %d 题；超出部分必须降级为 adapt。" % gen_max,
        "2. generate 题若无 CNKI 素材来源，必须降级为 adapt 或改出无情境题并标 generic=true。",
        "3. adapt 题不得照抄候选题干，必须至少改动参数、情境或设问之一。",
        "4. 情境化开关：%s。" % ("开启，优先使用真实素材编情境" if ctx_on else "关闭，可用无情境题"),
    ]
    require_for = pack["subject_pack"].get("sources", {}).get("require_for")
    if require_for:
        lines.append("5. 本学科需溯源的题型：%s。" % "、".join(require_for))

    return {
        "plan_text": "\n".join(lines),
        "plan_json": json.dumps({
            "total": total, "counts": counts, "gen_max": gen_max,
            "supply": supply["supply"], "job_type": supply["job_type"],
            "quota": supply["quota"], "why": supply["why"],
            "overridden": supply["overridden"], "degraded": degraded,
            "overrides": {str(k): v for k, v in forced.items()},
            "overrides_invalid": forced_bad, "actual": act,
            "items": plan,
        }, ensure_ascii=False),
        "bank_count": len(cands),
    }


# ==========================================================================
# 四·五、一题多变式包
#
# 一道好真题最值钱的不是题本身，而是它背后的**考点模板**。所以「改编」最站得住的位置
# 从来不是替代原题，而是 1:N 派生：
#
#   一道 2026 秋·月考真题（retrieve，正式作业/备考用）
#     └─ 同构换数 → 隔周二刷
#     └─ 换情境   → 分层作业 B 卷
#     └─ 逆向设问 → 拓展层
#
# 教师最缺的其实就是这个：同一个考点、互不重复、难度递进的几次训练机会。
# 产出结构与主供题计划同形，可原样喂回 validate 走第 13 条逐题比对。
# ==========================================================================
VARIANT_KINDS = [
    {"key": "retune", "name": "同构换数", "step": 0,
     "how": "考点、设问、解题结构一律不动，只替换其中的数值与对象名称（如把「铁块」换成「木块」，把 2 N 换成 3 N）",
     "why": "同考点二刷最省心的做法：结构熟悉而数据陌生，能检验学生是真会还是背答案",
     "risk": "换了数值必须重算，且结果要落回真实量级（不要出现 250 kg 的木块）"},
    {"key": "rescene", "name": "换情境", "step": 0,
     "how": "保留考点与解题路径，把情境换成学生身边的真实场景（校园、家庭、本地素材），数据随之重设",
     "why": "解决「原题情境陈旧、不是我这班学生熟悉的」——同一考点换个壳再练一次",
     "risk": "新情境的数据必须是真实量级，不得出现家庭月用水 5000 L 这类离谱数值"},
    {"key": "reverse", "name": "逆向设问", "step": 1,
     "how": "把「求 A」改成「已知 A 求 B」，或改为「判断并说明理由」「怎样做才能使……」",
     "why": "认知层级自然上升一级，适合当拓展层，也是最容易出区分度的一招",
     "risk": "开放化的一刹那就必须给评分要点（rubric），否则教师没法批"},
    {"key": "recondition", "name": "增减条件", "step": 0, "to": "拓展",
     "how": "删掉一个已知条件使其开放，或加一条无用信息让学生判断哪些信息有效",
     "why": "练的是审题与建模，最接近新课标要求的批判性思维",
     "risk": "必须保证题仍有确定解，或明确写成开放题并给评分要点"},
]
VARIANT_ORDER = [v["key"] for v in VARIANT_KINDS]
_LEVEL_UP = {"基础": "巩固", "巩固": "拓展", "拓展": "拓展"}


def _variant_level(kind, base_level):
    """变式的建议分层：同构换数与换情境停留在母题层，逆向设问升一级，增减条件固定为拓展。"""
    if kind.get("to"):
        return kind["to"]
    lv = str(base_level or "巩固") or "巩固"
    for _ in range(int(kind.get("step", 0))):
        lv = _LEVEL_UP.get(lv, "拓展")
    return lv


def variant_plan(parent, subject, stage, n=3, kinds=None):
    """母题 -> N 个互不重复的变式计划。返回 {plan_text, plan_json, keys, invalid}。

    parent 需要 id / level / type / stem / answer / bank_id / label 字段，
    缺哪几个就从 rendered 计划里少几行，不报错——变式包也常直接拿题库真题做母题。
    """
    lut = {v["key"]: v for v in VARIANT_KINDS}
    keys = [str(k).strip().lower() for k in (kinds or []) if str(k).strip()]
    invalid = [k for k in keys if k not in lut]
    keys = [k for k in keys if k in lut]
    if not keys:
        m = max(min(int(n or 3), len(VARIANT_ORDER)), 1)
        keys = VARIANT_ORDER[:m]

    base_level = str(parent.get("level") or "巩固") or "巩固"
    items = []
    for key in keys:
        v = lut[key]
        items.append({
            "level": _variant_level(v, base_level), "mode": "adapt",
            "reason": "%s：%s（为什么这么做：%s）" % (v["name"], v["how"], v["why"]),
            "bank_id": parent.get("bank_id") or "", "bank_stem": parent.get("stem") or "",
            "bank_label": parent.get("label") or "", "variant": key, "variant_name": v["name"],
            "risk": v["risk"], "why": v["why"], "override": False, "freshness": "",
        })

    who = "母题第 %s 题" % parent["id"] if parent.get("id") is not None else "所选真题"
    tag = parse_paper_label(parent.get("label") or "", stage)
    lines = ["## 变式包（%s → %d 个变式）" % (who, len(items))]
    if parent.get("type"):
        lines[-1] += " · %s" % parent["type"]
    if parent.get("label"):
        # 显示用清洗后的字符串，但「原样填」必须给原始值——题库 Label 常自带全角括号
        lines.append("母题出处：%s%s" % (_norm_label(parent["label"]),
                                        "（%s）" % tag["tag"] if tag["tag"] else ""))
    if parent.get("stem"):
        lines.append("> 母题题干：%s" % parent["stem"])
    if parent.get("answer"):
        lines.append("> 母题答案：%s（**只作验算基准，不得照抄**——变式的数据已经变了）" % parent["answer"])
    lines += [
        "",
        "### 每个变式都必须满足",
        "1. origin='adapt'、based_on=%s、based_on_label 原样填「%s」"
        % (parent.get("bank_id") or "母题 bank_id", parent.get("label") or "母题出处"),
        "2. 至少改动「数据 / 情境 / 设问 / 条件」中的一类——下方每题已指定改哪一类，照它改",
        "3. 必做答案一致性验算：填 answer_check{changed, recompute, verdict}，verdict 只能写「一致」。"
        "变式全是改编题，改了数据却沿用母题答案是这套东西最贵的错误",
        "4. 变式之间不得雷同，也不得与作业单里其他题撞题（两题同 based_on 会被判孪生题）",
        "5. 每个变式都要重新估 dur 与认知层级，不许照抄母题",
        "",
        "### 变式清单",
    ]
    for i, x in enumerate(items, 1):
        lines.append("%d. [%s/adapt·%s] %s" % (i, x["level"], x["variant_name"], x["reason"]))
        lines.append("   当心：%s" % x["risk"])
    lines += ["", "（%s 建议保留为 retrieve 原样使用；变式用于下周错题重做与分层 B 卷）" % who]

    counts = {lv: len([x for x in items if x["level"] == lv]) for lv in ("基础", "巩固", "拓展")}
    return {
        "plan_text": "\n".join(lines),
        "plan_json": json.dumps({
            "total": len(items), "counts": counts, "gen_max": 0,
            "supply": "adapt", "job_type": "变式包",
            "quota": {"retrieve": 0, "adapt": len(items), "generate": 0},
            "why": "给已被证明考得到的真题派生变式，用于分层 B 卷与错题隔周二刷",
            "parent": {k: parent.get(k) for k in ("id", "level", "type", "bank_id", "label")},
            "items": items,
        }, ensure_ascii=False),
        "keys": keys, "invalid": invalid,
    }


def _parent_from_items(data, idx=None):
    """从 items.json 里挑出母题。图纸里的 base 信息要从 source/based_on 两边捞：
    retrieve 题的底座在 source_*，adapt 题的底座在 based_on_*。"""
    arr = (data.get("items") if isinstance(data, dict) else data) or []
    if not arr:
        raise SystemExit("items 为空，无从挑母题")
    it = None
    if idx is not None:
        it = next((x for x in arr if str(x.get("id")) == str(idx)), None)
        if it is None:
            raise SystemExit("items 里没有 id=%s（可用 id：%s）"
                             % (idx, "、".join(str(x.get("id")) for x in arr)))
    else:
        it = arr[0]
    return {
        "id": it.get("id"), "level": it.get("level") or "", "type": it.get("type") or "",
        "stem": it.get("stem") or "", "answer": it.get("answer") or "",
        "analysis": it.get("analysis") or "", "origin": it.get("origin") or "",
        "bank_id": it.get("source_id") or it.get("based_on") or "",
        "label": it.get("source_label") or it.get("based_on_label") or "",
    }


# ==========================================================================
# 五、生成后硬校验
# 这是整套差异化的地基。写了规则从没见它拦过东西，等于没写——跑完必看 issues。
# ==========================================================================
def _extract_json(text):
    raw = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", raw, re.S)
    if m:
        raw = m.group(1).strip()
    # 定位最外层 JSON 值（对象或数组），用括号栈匹配，跳过字符串内的括号
    start = None
    for ch in ("[", "{"):
        idx = raw.find(ch)
        if idx >= 0 and (start is None or idx < start):
            start = idx
    if start is None:
        return None, "模型未输出合法的 JSON"
    open_ch = raw[start]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0
    end = None
    i, n = start, len(raw)
    while i < n:
        c = raw[i]
        if c in ('"', "'"):          # 跳过字符串（含转义字符），避免误判其中的括号
            q = c
            i += 1
            while i < n:
                if raw[i] == "\\":
                    i += 2
                    continue
                if raw[i] == q:
                    i += 1
                    break
                i += 1
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                end = i
                break
        i += 1
    if end is None:
        return None, "模型输出的 JSON 未闭合"
    try:
        return json.loads(raw[start:end + 1]), None
    except Exception as ex:
        return None, "JSON 解析失败：%s" % ex


def _sentences(s):
    return [x for x in re.split(r"[。；;！？!?\n]", s or "") if x.strip()]


# --------------------------------------------------------------------------
# 答案一致性验算（adapt 题）
#
# 教师对 AI 出题的不信任，源头从来不是"题出得不够好"，而是"改了数据没改成答案"。
# 一次错答案，整套东西就不会被用第二次——所以这条必须是**阻塞级**，不是提醒级。
# 让模型把验算过程显式写出来有两个好处：一是逼它真的重算一遍而不是凭感觉给答案，
# 二是教师复核时可以直接顺着 recompute 查，不必自己动手算。
# --------------------------------------------------------------------------
_CHECK_FIELDS = [
    ("changed", "相对原题改了哪些数据/条件，逐项列清"),
    ("recompute", "用改动后的数据重新求解的过程与结果"),
    ("verdict", "结论，只能填「一致」"),
]
_VERDICT_OK = ("一致", "自洽", "通过", "已复核")


def _nums(s):
    """提取数字串（含小数），用于复算烟测。"""
    return set(re.findall(r"\d+(?:\.\d+)?", str(s or "")))


def _squash(s):
    """去掉空白与常见标点，用于题面比对（题库原文常常自带题号前缀）。"""
    return re.sub(r"[\s，。、；：？！（）()\[\]·•“”\"'《》,.;:?!_-]", "", str(s or ""))


def _answer_check_checks(i):
    """返回 (阻塞项, 提醒项)：adapt 题的一致性验算是否做了、做得对不对。"""
    oid = i.get("id", "?")
    ac = i.get("answer_check")
    if not isinstance(ac, dict) or not ac:
        return (["第 %s 题 origin=adapt 但缺 answer_check：改编题必须先重算答案。"
                 "须填 changed（改了哪些数据/条件）· recompute（用改动后的数据重新求解）· "
                 "verdict（结论，只能填「一致」），三者缺一不可" % oid], [])
    miss = [k for k, _ in _CHECK_FIELDS if not ac.get(k)]
    if miss:
        d = dict(_CHECK_FIELDS)
        return (["第 %s 题 answer_check 缺字段：%s（%s）"
                 % (oid, "、".join(miss), "；".join("%s = %s" % (f, d[f]) for f in miss))], [])
    verdict = str(ac.get("verdict") or "").strip()
    if verdict not in _VERDICT_OK:
        return (["第 %s 题 answer_check.verdict=%r，说明改编数据与原答案对不上。"
                 "要么调整数据使它仍有干净解，要么给出与新题面自洽的新答案并重算，"
                 "改完再填「一致」——不得带着「不一致」交出去" % (oid, verdict)], [])
    warns = []
    if not _str_items(ac.get("changed")):
        warns.append("第 %s 题 answer_check.changed 是空的：声称做了验算却没列出改了什么，"
                     "请把改动的数据/条件逐项补上" % oid)
    na, nr = _nums(i.get("answer")), _nums(ac.get("recompute"))
    if na and nr and not (na & nr) and not (na & _nums(i.get("analysis"))):
        warns.append("第 %s 题答案里的数值 %s 在 recompute 与解析中都找不到，"
                     "复算结果与所给答案可能对不上，请重新核一遍"
                     % (oid, "、".join(sorted(na)[:5])))
    return [], warns


def _str_items(v):
    """changed 可以是字符串也可以是列表，统一成非空片段数。"""
    if v is None:
        return []
    return [x for x in ([v] if isinstance(v, str) else v) if str(x).strip()]


def _official_checks(i):
    """官方解析交叉校验 —— 用 tkQuestionAnalysis 拿到的官方答案/解析当基准。

    为什么这条比让模型自己复算更可靠：搜题接口只给答案不给解析，过去第 14 条
    验算是「模型改编 → 模型复算 → 模型判一致」，自证循环，编错了也查不出来。
    官方解析是出题方给的解，拿它当外部基准才叫校验。

    分级：
      retrieve 题答案与官方不一致 -> 阻塞（retrieve 的定义就是原样使用）
      adapt 题答案与官方不一致   -> 提醒（改编后答案可以变，但必须在 recompute 里说清）
    """
    oid = i.get("id", "?")
    o = i.get("origin")
    off = str(i.get("official_answer") or "").strip()
    if not off:
        return [], []
    cur = str(i.get("answer") or "").strip()
    if not cur or _squash(cur) == _squash(off):
        return [], []

    issues, warns = [], []
    if o == "retrieve":
        issues.append("第 %s 题 origin=retrieve，但所给答案「%s」与题库官方答案「%s」不一致。"
                      "retrieve 的含义就是原样拿来用，题面与答案都不得改动；"
                      "若确需改答案，应改走 adapt 并做答案一致性验算" % (oid, cur, off))
    elif o == "adapt":
        ac = i.get("answer_check") or {}
        blob = " ".join(str(ac.get(k) or "") for k in ("changed", "recompute", "verdict"))
        if _squash(off) not in _squash(blob):
            warns.append("第 %s 题改编后答案「%s」与原题库官方答案「%s」不同，"
                         "但 answer_check 里没提到原答案。请在 recompute 中说明为什么变了"
                         "（换了数据 / 换了问法 / 只是化简形式不同），否则无法判断是正常改编还是算错"
                         % (oid, cur, off))

    # 数值层弱校验：答案里的数字应当能在官方解析里找到（选择题答案为字母时自动跳过）
    oa = str(i.get("official_analysis") or "")
    na, noa = _nums(cur), _nums(oa)
    if na and noa and not (na & noa):
        warns.append("第 %s 题答案中的数值 %s 在官方解析里一个都没出现，"
                     "请核对是否算错或单位换算有误（官方解析：%s…）"
                     % (oid, "、".join(sorted(na)[:5]), oa[:30].replace("\n", " ")))
    return issues, warns


def _stem_mismatch_warns(plan_item, item):
    """retrieve 题面必须与题库原文一致——擅自润色就等于把这一档取消了。"""
    base = _squash(plan_item.get("bank_stem") or "")
    # 长材料题按规范「段落放 material、设问放 stem」，题面是两者拼接。
    # 只比 stem 会让所有带材料的 retrieve 题必然误报（段落根本不在 stem 里）。
    out = _squash(item.get("material") or "") + _squash(item.get("stem") or "")
    if not base or not out:
        return []
    a, b = out[:30], base[:30]
    if (a and a in base) or (b and b in out):     # 题库原文常带题号/出处前缀，用包含而非相等
        return []
    return ["第 %s 题是 retrieve 题，但题面与题库原文前 30 字不一致，疑似擅自改动了原题表述或数据。"
            "retrieve 的价值就在「拿来就能布置」，题面必须一字不改；"
            "若原题确有问题应改走 adapt 并在 notes 说明（也可能只是题库原文带前缀，请人工确认）"
            % item.get("id", "?")]


def validate(llm_text, subject, stage, plan_json=None, max_minutes=None):
    pack = get_pack(subject, stage)
    sp, stp = pack["subject_pack"], pack["stage_pack"]

    data, err = _extract_json(llm_text)
    if err:
        return {"ok": False, "ok_str": "false", "issues": [err],
                "items_json": "{}", "summary": "解析失败", "items": [], "data": {}, "warns": []}

    items = data.get("items", []) or []
    issues = []

    if not items:
        issues.append("未生成任何题目（items 为空）")

    # 1 课标对齐
    if not (data.get("meta", {}) or {}).get("std_aligned"):
        issues.append("meta.std_aligned 缺失：未绑定课标条目")

    # 2 书面红线（政策，优先级最高）
    if stp.get("allow_written") is False:
        for i in items:
            if str(i.get("mode", "written")).lower() != "oral":
                issues.append("第 %s 题为书面题，但 %s 不布置书面家庭作业（政策红线）"
                              % (i.get("id", "?"), stp.get("stage", "该学段")))

    # 3 总时长
    limit = max_minutes or stp.get("max_minutes", 0)
    total = 0.0
    for i in items:
        try:
            total += float(i.get("dur", 0) or 0)
        except Exception:
            pass
    if limit and total > limit:
        issues.append("预计总时长 %.0f 分钟 > 上限 %s 分钟，需压缩题量或降低单题时长" % (total, limit))

    # 4 溯源必填（仅约束改编/原创；直接使用题库原题的 retrieve 不挂文献溯源，不受此限）
    for kw in sp.get("sources", {}).get("require_for", []) or []:
        for i in items:
            if i.get("origin") == "retrieve":
                continue
            if kw in str(i.get("type", "")):
                real = [s for s in (i.get("sources") or []) if not s.get("generic", False)]
                if not real:
                    issues.append("第 %s 题（%s）缺少可溯源的 CNKI 来源，需补 sources 或改出无情境题"
                                  % (i.get("id", "?"), i.get("type", "")))

    # 4b 溯源著录完整性（告警级，不阻塞，仅校验改编/原创题的文献著录；retrieve 真题不挂文献溯源）
    warns = []
    for i in items:
        if i.get("origin") == "retrieve":
            continue
        real = [s for s in (i.get("sources") or []) if not s.get("generic", False)]
        for s in real:
            warns += _source_gaps(s, "第 %s 题" % i.get("id", "?"))
        # 期刊优先：学术性溯源（非教材）里一条期刊/学位论文都没有，提示去换
        if real:
            academic = [s for s in real if s.get("type") != "textbook"]
            best = min((SOURCE_PRIORITY.index(s["type"]) for s in academic
                        if s.get("type") in SOURCE_PRIORITY), default=None)
            venues = "、".join(_venues_for(subject, stage)[:2])
            vhint = "（优先%s）" % venues if venues else ""
            if not academic:
                # 只有教材：教材不是学术来源，这正是最该提醒"补学术溯源"的情形，不能静默
                warns.append("第 %s 题只有教材溯源，教材不算学术来源，建议补引 CNKI 期刊论文%s，"
                             "以便给出完整的「作者·篇名·来源期刊·年份·期」"
                             % (i.get("id", "?"), vhint))
            elif best is not None and best > SOURCE_PRIORITY.index("journal"):
                warns.append("第 %s 题溯源未含期刊论文（当前最优为%s），建议改引 CNKI 期刊论文%s，"
                             "以便给出完整的「作者·篇名·来源期刊·年份·期」"
                             % (i.get("id", "?"),
                                SOURCE_TYPES[SOURCE_PRIORITY[best]]["label"], vhint))
    if warns:
        warns.append("以上为提醒项，不阻塞交付。著录缺失处渲染为【待补充】，请勿凭印象补填——"
                     "编造的溯源比没有溯源更糟；可到 CNKI 检索原文后补齐。")

    # 共享材料模式：各题 material 应为空，留了会在渲染时被忽略（材料已在顶部统一展示一次）
    _shared = (data.get("meta", {}) or {}).get("shared_material")
    if _shared:
        for i in items:
            if i.get("material"):
                warns.append("第 %s 题在共享材料模式下仍带 material 字段，渲染时该字段会被忽略"
                             "（共享材料已在顶部统一展示），请改为在 stem 里用「根据材料」指代"
                             % i.get("id", "?"))

    # 5 必填字段
    must = (sp.get("quant", {}).get("must_fields") or ["answer", "analysis"]) + (sp.get("extra_fields") or [])
    for i in items:
        # 量规/安全提示只在对应题型上强制，避免误伤
        check = [f for f in must if f not in ("rubric", "safety", "apparatus", "claim_dimensions", "venue_requirement")]
        if str(i.get("origin", "")) == "retrieve":
            # 题库原题的答案就在源题库里，不应由模型重写（否则既违背「题面一字不改」，
            # 又诱导编造答案）。仅当教师确实在 items 里补了答案时才校核，否则留空交回查。
            check = [f for f in check if f not in ("answer", "analysis")]
        t = str(i.get("type", ""))
        if any(k in t for k in ("写作", "作品", "论述", "听说", "实践", "任务")):
            check += [f for f in ("rubric",) if f in must]
        if any(k in t for k in ("实验",)):
            check += [f for f in ("safety", "apparatus") if f in must]
        miss = [f for f in check if not i.get(f)]
        if miss:
            issues.append("第 %s 题缺少必填字段：%s" % (i.get("id", "?"), "、".join(miss)))

    # 6 分句长度
    smax = stp.get("sentence_len_max", 25)
    for i in items:
        over = [seg for seg in _sentences(str(i.get("stem", ""))) if len(seg) > smax]
        if not over:
            continue
        msg = "第 %s 题题干分句超 %s 字（%d 字），需拆分" % (i.get("id", "?"), smax, len(over[0]))
        if str(i.get("origin", "")) == "retrieve":
            # retrieve 的全部价值就在「题面一字不改」。真题原设问常常偏长（尤其小学引导语），
            # 为了凑分句上限去改写它，等于把 retrieve 悄悄做成了 adapt——那是第 13 条要拦的事。
            # 分句上限约束的是模型自撰的题干，所以这里降级为提醒。
            warns.append(msg + "；但本题是 retrieve 真题，题面要求一字不改，"
                              "如需拆分应改走 adapt 并注明，或保持原样直接布置")
        else:
            issues.append(msg)

    # 7 认知层级上限
    cmax = stp.get("cognitive_max")
    if cmax in COG_ORDER:
        cap = COG_ORDER.index(cmax)
        for i in items:
            c = i.get("cognitive")
            if c in COG_ORDER and COG_ORDER.index(c) > cap:
                issues.append("第 %s 题认知层级「%s」超过学段上限「%s」" % (i.get("id", "?"), c, cmax))

    # 8 禁例关键词
    forb = set((sp.get("forbidden", []) or []) + (stp.get("forbidden", []) or []) + ["超纲", "竞赛", "极难"])
    for i in items:
        blob = json.dumps(i, ensure_ascii=False)
        for kw in forb:
            if kw and kw in blob:
                issues.append("第 %s 题命中禁例关键词：%s" % (i.get("id", "?"), kw))

    # 9~12 供给方式校验
    # 关键：校验必须「无条件」先跑结构级防编造，再「按计划」做事实级核对。
    # 旧版把这些全塞进 `if plan:` 里——不传 --plan 时纯 AI 编造的题（无 origin / 无
    # source_id / 无 based_on / 无 CNKI 文献）会直接通过校验。这正是「作业设计不能纯靠
    # AI 编」要堵的口子：每题要么来自原题（retrieve）、要么基于原题创作（adapt）、
    # 要么基于知网文献创作（generate），绝不允许无出处。
    plan = {}
    if plan_json:
        try:
            plan = json.loads(plan_json) if isinstance(plan_json, str) else plan_json
        except Exception:
            plan = {}
    pit = plan.get("items") or []

    # —— 无条件：每题必须声明合法 origin 并带齐对应依据（结构级防编造）——
    for i in items:
        o = i.get("origin")
        if o not in MODE_LABEL:
            issues.append("第 %s 题 origin 字段缺失或非法（应为 retrieve/adapt/generate）——"
                          "每题必须标明来源档位，不得无出处" % i.get("id", "?"))
            continue
        if o == "retrieve" and not i.get("source_id"):
            issues.append("第 %s 题 origin=retrieve 但缺 source_id（原题库编号）——"
                          "直接用原题必须能回查到题库真题" % i.get("id", "?"))
        if o == "adapt" and not i.get("based_on"):
            issues.append("第 %s 题 origin=adapt 但缺 based_on（未标明改编自哪道真实原题）"
                          % i.get("id", "?"))
        if o == "adapt":
            bad, wa = _answer_check_checks(i)
            issues += bad
            warns += wa
        # 官方解析交叉校验（题库方答案当外部基准，打破「模型自证」）——无条件跑
        bad, wa = _official_checks(i)
        issues += bad
        warns += wa
        # 题源出处的新旧课标适用性：机器能看出来的就别留给教师看
        lbl = i.get("source_label") if o == "retrieve" else (
            i.get("based_on_label") if o == "adapt" else "")
        if lbl:
            info = parse_paper_label(lbl, stage)
            if info["outdated"]:
                warns.append("第 %s 题的真题出版于 %d 年，早于现行课程方案施行年（%d 年版），"
                             "可能基于旧教材/旧课标，使用前须人工核对是否仍适用"
                             % (i.get("id", "?"), info["year"], info["reform_year"]))
            elif info["year"] is None:
                warns.append("第 %s 题的题源出处「%s」未含年份，无法判断新鲜度与新/旧课标适用性，"
                             "建议回查题库补齐" % (i.get("id", "?"), _norm_label(lbl)))
        # bank_id 是内部流水号，印在作业单上教师看不懂，也无从核题。
        if o == "adapt" and i.get("based_on") and not i.get("based_on_label"):
            warns.append("第 %s 题缺 based_on_label：作业单上会退化成「改编自题库题 %s」，"
                         "应补该题的真实试卷出处（题库 label 字段）" % (i.get("id", "?"), i["based_on"]))
        if o == "retrieve" and i.get("source_id") and not i.get("source_label"):
            warns.append("第 %s 题缺 source_label：作业单上会退化成裸题库编号 %s，"
                         "应补真实试卷出处" % (i.get("id", "?"), i["source_id"]))
        if o == "generate":
            real = [s for s in (i.get("sources") or []) if not s.get("generic", False)]
            if not real:
                # 经 searchVectorBJ 实检无相关文献：绝不能凭空挂文献，本题应改为 adapt（以真实原题为底）
                if i.get("based_on"):
                    issues.append("第 %s 题 origin=generate 但无 CNKI 文献支撑，且有 based_on 原题底座 "
                                  "→ 应改为 adapt（基于原题改编），并在作业单如实标注『未检索到可引用 "
                                  "CNKI 文献』；generate 不允许无文献" % i.get("id", "?"))
                else:
                    issues.append("第 %s 题 origin=generate 既无 CNKI 文献又无原题底座，属纯 AI 编造 "
                                  "——原创必须基于经 searchVectorBJ 实检返回的真实篇名，否则改为 "
                                  "adapt（基于某道真实原题）" % i.get("id", "?"))

    # —— 孪生题：同底座改编等于同一题出现两次（不依赖计划）——
    seen = {}
    for i in items:
        b = i.get("based_on")
        if i.get("origin") == "adapt" and b:
            if b in seen:
                issues.append("第 %s 题与第 %s 题改编自同一道候选题 %s（孪生题），"
                              "须换一道底座或显著改编设问" % (i.get("id", "?"), seen[b], b))
            else:
                seen[b] = i.get("id", "?")

    # —— 以下为计划专属核对（传了 --plan 才生效）——
    if plan:
        gen_max = plan.get("gen_max", 0)
        gen_n = len([i for i in items if i.get("origin") == "generate"])
        if gen_n > gen_max:
            issues.append("原创题 %d 道超过上限 %d 道，超出部分须降级为 adapt" % (gen_n, gen_max))
        # 事实级核对：声明的 source_id / based_on 必须落在计划里真实抓取的候选题 bank_id 中，
        # 否则即引用了计划外或编造的题源——这才真正拦住「纯靠 AI 编」。
        real_bank_ids = {str(x.get("bank_id") or "").strip() for x in pit if x.get("bank_id")}
        if real_bank_ids:
            for i in items:
                o = i.get("origin")
                sid = str(i.get("source_id") or "").strip() if i.get("source_id") else ""
                bon = str(i.get("based_on") or "").strip() if i.get("based_on") else ""
                if o == "retrieve" and sid and sid not in real_bank_ids:
                    issues.append("第 %s 题 origin=retrieve 但 source_id=%r 不在供题计划的真实候选题列表内，"
                                  "疑似引用计划外或编造的原题编号；必须改用计划内真题或改走 adapt"
                                  % (i.get("id", "?"), sid))
                if o == "adapt" and bon and bon not in real_bank_ids:
                    issues.append("第 %s 题 origin=adapt 但 based_on=%r 不在供题计划的真实候选题列表内，"
                                  "疑似引用计划外或编造的底座；必须改用计划内真题"
                                  % (i.get("id", "?"), bon))
        # retrieve 题面一致性：计划里存着题库原文，模型擅自润色了表述就当场抓出来
        if len(pit) == len(items):
            for pi, it in zip(pit, items):
                if pi.get("mode") == "retrieve" and it.get("origin") == "retrieve":
                    warns += _stem_mismatch_warns(pi, it)

        # 13 是否照办了供题计划：模型擅自把 retrieve 写成 adapt，等于把「可以原样用的真题」
        # 又改了一遍——mix 配额的意义会当场失效，所以这条要拦而不是提醒。
        planned = [x.get("mode") for x in pit]
        actual = [i.get("origin") for i in items]
        if planned:
            if len(planned) == len(actual):
                for n, (pm, am) in enumerate(zip(planned, actual), 1):
                    if am in MODE_LABEL and pm != am:
                        issues.append("第 %d 题 origin=%s，但供题计划指定的这一题是 %s；"
                                      "必须按计划出%s"
                                      % (n, am, pm,
                                         "（retrieve 题只需原样保留题面，补课标绑定与层级标注）"
                                         if pm == "retrieve" else "（不得擅自改档）"))
            else:
                warns.append("题量与供题计划不一致（计划 %d 题 / 实际 %d 题），"
                             "逐题比对已跳过，请人工核对每题的 origin 是否与计划相符"
                             % (len(planned), len(actual)))

    ok = len(issues) == 0
    summary = "共 %d 题 · 预计 %.0f 分钟 · 校验 %s" % (
        len(items), total, "通过" if ok else "拦截 %d 项" % len(issues))
    if warns:
        summary += " · 提醒 %d 项" % len([w for w in warns if w.startswith("第")])
    return {
        "ok": ok,
        "ok_str": "true" if ok else "false",
        "issues": issues,
        "warns": warns,
        "items_json": json.dumps(data, ensure_ascii=False),
        "summary": summary,
        "items": items,
        "data": data,
    }


# ==========================================================================
# 六、渲染：分层 Markdown 作业单
# ==========================================================================
def _norm_label(s):
    """清洗试卷出处：题库给的 Label 自带全角括号，印到「改编自：」后面是冗余的。

    统一在这里剥，模型填不填括号都能得到干净结果，不依赖人工一致性。
    """
    return str(s or "").strip().strip("（）()").strip()


def _freshness_suffix(label, stage=None):
    """给题源出处补一句「近3年·期末卷·校级」，顺手标出早于现行课程方案的旧真题。"""
    info = parse_paper_label(label, stage)
    if not info["label"]:
        return ""
    tail = "（%s" % info["tag"]
    if info["outdated"]:
        tail += "；%d 年出版，早于 %d 年版课程方案，须核对是否符合现行教材" % (
            info["year"], info["reform_year"])
    return tail + "）"


def _fmt_source(s):
    """按文献类型渲染 GB/T 7714 著录。

    缺字段一律渲染成【待补充】而不是留空或猜填——教师一眼看出要去哪里补，
    比假装完整安全得多。旧格式 {name, year} 仍兼容。
    """
    if not isinstance(s, dict):
        return str(s)
    t = s.get("type")
    if t not in SOURCE_TYPES:
        # 旧格式兜底：只有 name / year
        return "%s（%s 年）" % (s.get("name", _PENDING), s["year"]) if s.get("year") else s.get("name", _PENDING)

    g = lambda k, pend: s.get(k) or pend  # noqa: E731
    author = g("author", _PENDING + "作者")
    title = g("title", _PENDING + "题名")
    container = g("container", _PENDING + "来源期刊")
    year = str(s.get("year") or _PENDING)
    issue = g("issue", _PENDING)
    pub = g("publisher", _PENDING + "出版社")
    pages = s.get("pages")
    vol = s.get("volume")          # 卷号：可选。有则按「年，卷(期)」；无则退回「年(期)」

    tail = ("：%s．" % pages) if pages else "．"
    if t == "journal":
        yr_issue = "%s，%s(%s)" % (year, vol, issue) if vol else "%s(%s)" % (year, issue)
        return "%s．%s[J]．%s，%s%s" % (author, title, container, yr_issue, tail)
    if t == "book":
        return "%s．%s[M]．%s，%s．" % (author, title, pub, year)
    if t == "chapter":
        return "%s．%s[M]//%s．%s，%s%s" % (author, title, container, pub, year, tail)
    if t == "thesis":
        return "%s．%s[D]．%s，%s．" % (author, title, pub, year)
    if t == "newspaper":
        return "%s．%s[N]．%s，%s．" % (author, title, container, year)
    if t == "textbook":
        return "%s．%s，%s．" % (title, pub, year)
    return s.get("name", title)


def _source_gaps(s, idx_label):
    """检查一条溯源的著录项缺什么，返回告警文案列表。"""
    t = s.get("type")
    if t not in SOURCE_TYPES:
        if not s.get("name"):
            return ["%s 溯源未标注 type（应为 %s），且无 name 兜底" % (idx_label, "／".join(SOURCE_TYPES))]
        return ["%s 溯源为旧格式（仅 name），建议补 type 与完整著录字段" % idx_label]
    miss = [f for f in SOURCE_TYPES[t]["need"] if not s.get(f)]
    if not miss:
        return []
    cn = {"author": "作者", "title": "篇名", "container": "来源期刊", "year": "年份",
          "issue": "期", "publisher": "出版社"}
    return ["%s 溯源（%s）著录缺：%s" % (idx_label, SOURCE_TYPES[t]["label"],
                                   "、".join(cn.get(f, f) for f in miss))]


def render(items, issues_text="", meta=None, warns=None, stage=None, subject=None, figures="both"):
    lines = ["# 作业设计单", ""]
    if meta:
        if meta.get("std_aligned"):
            lines += ["**课标对齐**：%s" % meta["std_aligned"], ""]
        if meta.get("literacy"):
            lines += ["**核心素养**：%s" % "、".join(meta["literacy"]), ""]
    dist = Counter(i.get("origin", "") for i in items)
    if dist:
        seg = "、".join("%s %d 题" % (MODE_LABEL.get(k, k), v) for k, v in dist.items() if k)
        lines += ["**题目来源**：%s" % seg, ""]

    # 同材异层：共享材料只在顶部渲染一次，下面各题不再重复材料块
    shared = (meta or {}).get("shared_material") if isinstance(meta, dict) else None
    if shared:
        lines += ["## 共享材料", ""]
        for ln in str(shared).split("\n"):
            lines.append("> %s" % ln if ln.strip() else ">")
        lines.append("")

    for lv in ["基础", "巩固", "拓展"]:
        sub = [i for i in items if i.get("level") == lv]
        if not sub:
            continue
        lines += ["## %s（%d 题）" % (lv, len(sub)), ""]
        _sem = {}
        if subject and subject in SUBJECT_PACKS and isinstance(SUBJECT_PACKS[subject].get("levels", {}).get(lv), dict):
            _sem = SUBJECT_PACKS[subject]["levels"][lv]
        if _sem.get("学情") or _sem.get("培养目标"):
            _bits = []
            if _sem.get("学情"):
                _bits.append("面向学情：%s" % _sem["学情"])
            if _sem.get("培养目标"):
                _bits.append("培养目标：%s" % _sem["培养目标"])
            lines += ["> " + " ｜ ".join(_bits), ""]
        for it in sub:
            lines.append("**%s. %s**｜%s｜%s｜%s分钟" % (
                it.get("id", "?"), it.get("type", ""), it.get("cognitive", ""),
                MODE_LABEL.get(it.get("origin", ""), "未标注"), it.get("dur", "-")))
            if not shared and it.get("material"):
                lines += ["", "**材料**："]
                for ln in str(it["material"]).split("\n"):
                    lines.append(ln if ln.strip() else "")
                lines.append("")
            if it.get("points"):
                lines += ["", "**考查知识点**：%s" % it["points"], ""]
            lines += ["", "**题干**：%s" % it.get("stem", ""), ""]
            tbl = it.get("table")
            if tbl:
                lines += [""] + _gfm_table_md(tbl) + [""]
            qs = it.get("questions")
            if qs:
                lines += ["**问题**："] + [str(q) for q in qs] + [""]
            # 原图（如题库自带的折线统计图）按 figures 范围嵌入；retrieve 真题的原图
            # 是原题完整信息的一部分，必须保留，不能像早期版本那样直接丢弃。
            figs = it.get("figures") or []
            if figs and figures in ("both", "teacher"):
                for _fg in figs:
                    lines.append("![%s](%s)" % (_fg.get("caption", "原题附图"), _fg.get("path", "")))
            if it.get("rubric"):
                lines += ["**评价量规**：%s" % it["rubric"]]
            if it.get("safety"):
                lines += ["**安全提示**：%s" % it["safety"]]
            if it.get("source_id"):
                lab = _norm_label(it.get("source_label"))
                lines += ["**原题出处**：%s%s" % (lab or it["source_id"], _freshness_suffix(lab, stage))]
            if it.get("based_on"):
                # based_on 是内部流水号，对外无意义；有真实试卷出处就显示出出处。
                _bl = _norm_label(it.get("based_on_label"))
                lines += (["**改编自**：%s%s" % (_bl, _freshness_suffix(_bl, stage))] if _bl else
                          ["**改编自**：题库题 %s（该题未提供试卷出处）" % it["based_on"]])
            # 学术溯源（CNKI 文献）仅「改编/原创且结合了知网数据」才标注；
            # 直接使用题库原题（retrieve）取真题原样，不挂文献溯源，只显示原题出处。
            if it.get("origin") in ("adapt", "generate"):
                srcs = [s for s in (it.get("sources") or []) if not s.get("generic", False)]
                if srcs:
                    lines += ["**学术溯源**：%s" % "；".join(
                        _fmt_source(s) for s in srcs)]
                else:
                    # 已检索但无真相关文献：如实标注「说没有」，绝不编造；
                    # adapt 以原题为底，generate 无文献须改为 adapt
                    lines += ["**学术溯源**：未检索到可引用 CNKI 文献"
                              "（已通过 searchVectorBJ 检索相关主题，无直接相关结果）"]
            if str(it.get("origin", "")) == "retrieve" and not (it.get("answer") or it.get("analysis")):
                # 题库原题答案在源题库，不在作业单里重写；给出回查提示，避免空白或编造。
                lines += ["", "<details><summary>参考答案与解析</summary>", "",
                          "**答案**：（本题为题库原题，标准答案请回查原卷/题库）", "",
                          "**解析**：以题库官方解析为准。"]
            else:
                # 已有真实答案/解析（来自题库官方解析接口或改编题验算）：直接给出
                lines += ["", "**参考答案与解析**：", "",
                          "**答案**：%s" % it.get("answer", ""), "",
                          "**解析**：%s" % it.get("analysis", "")]
            _ac = it.get("answer_check") or {}
            if isinstance(_ac, dict) and any(_ac.get(k) for k in ("changed", "recompute", "verdict")):
                # 改编题最贵的错是改数据不改答案，所以验算过程必须印出来给教师复核，而不是藏在 JSON 里
                lines += ["", "**答案一致性验算**：结论 %s｜改动：%s｜重算：%s"
                          % (_ac.get("verdict", "未填"),
                             "、".join(_str_items(_ac.get("changed"))) or "未填",
                             _ac.get("recompute", "未填"))]
            lines += ["", "</details>", ""]
    total = 0.0
    for i in items:
        try:
            total += float(i.get("dur", 0) or 0)
        except Exception:
            pass
    lines += ["---", "预计总时长：%.0f 分钟｜题量：%d 题" % (total, len(items))]
    notes = (meta or {}).get("notes") or []
    if notes:
        lines += ["", "## 使用前必读", ""]
        lines += ["- %s" % n for n in notes]
    if warns:
        lines += ["", "## 著录缺口与溯源提醒（需教师处理）", ""]
        lines += ["- %s" % w for w in warns]
    if issues_text:
        lines += ["", "> 校验未通过，以下问题须教师确认：", "> %s" % issues_text.replace("\n", "\n> ")]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Word(.docx) 导出：给老师直接可用 / 打印 / 二次编辑的格式
# --------------------------------------------------------------------------
def _table_to_rows(tbl):
    """把 item 的 table 字段统一成 (head, rows)。
    支持两种写法：
      - dict: {"head":[...], "rows":[[...]], "caption":"..."}
      - list: 首行为表头，其余为数据行
    """
    if isinstance(tbl, list):
        rows = [list(r) for r in tbl]
        head = rows[0] if rows else []
        body = rows[1:]
    elif isinstance(tbl, dict):
        head = list(tbl.get("head") or [])
        body = [list(r) for r in (tbl.get("rows") or [])]
    else:
        return [], []
    return head, body


def _gfm_table_md(tbl):
    """把结构化 table 渲染成 GitHub 风格 Markdown 表格（供 md_to_docx 再转真表格）。"""
    head, body = _table_to_rows(tbl)
    if not head and not body:
        return []
    out = []
    if head:
        out.append("| " + " | ".join(str(x) for x in head) + " |")
        out.append("| " + " | ".join("---" for _ in head) + " |")
    for r in body:
        ncol = len(head) if head else len(r)
        cells = [str(r[c]) if c < len(r) else "" for c in range(ncol)]
        out.append("| " + " | ".join(cells) + " |")
    return out


def build_student_md(items, subject, stage, figures="both", shared_material=None):
    """学生视角的作业纸（只有任务 + 训练重点 + 完成标准，不含来源/答案）。"""
    last_lvl = None
    n = 0
    out = []
    _sm = (shared_material or "").strip()
    if _sm:
        out.append("## 共享材料")
        out.append("")
        for ln in _sm.split("\n"):
            out.append("> " + ln if ln.strip() else ">")
        out.append("")
    for it in items:
        n += 1
        lvl = it.get("level", "")
        if lvl != last_lvl:
            if out:
                out.append("")
            out.append("## " + (lvl or "作业"))
            last_lvl = lvl
        qtype = it.get("type") or it.get("题型") or ""
        dur = it.get("dur") or it.get("minutes") or ""
        meta = []
        if qtype:
            meta.append(qtype)
        if dur:
            meta.append("约 %s 分钟" % dur)
        head = "**任务 %d**" % n
        if meta:
            head += "｜" + " · ".join(meta)
        out.append(head)
        stem = (it.get("stem") or "").strip()
        if stem:
            for sl in stem.split("\n"):
                out.append(sl.strip())
        # 材料块：与教师版统一用「**材料**：」格式（解析器当作 part 正确渲染，
        # 不用「> 」块引用——后者会被 md_to_docx 误判为层级 callout 而吞掉）。
        mat = (it.get("material") or "").strip()
        if mat:
            out.append("")
            out.append("**材料**：")
            for ln in mat.split("\n"):
                out.append(ln.strip())
            out.append("")
        tbl = it.get("table")
        if tbl:
            out.append("")
            out += _gfm_table_md(tbl)
            out.append("")
        qs = it.get("questions")
        if qs:
            out.append("**问题**：")
            for q in qs:
                out.append(str(q))
            out.append("")
        figs = it.get("figures") or []
        if figs and figures in ("both", "student"):
            for _fg in figs:
                out.append("![%s](%s)" % (_fg.get("caption", "原题附图"), _fg.get("path", "")))
            out.append("")
        points = it.get("points") or it.get("考查知识点")
        if points:
            pts = "、".join(str(x) for x in points) if isinstance(points, (list, tuple)) else str(points).strip()
            if pts:
                out.append("**训练重点**：" + pts)
        rubric = it.get("rubric") or it.get("评价量规")
        if rubric:
            out.append("**完成标准**：" + str(rubric).strip())
        out.append("")
    return "\n".join(out).strip() + "\n"


def md_to_docx(md_text, out_path=None, subtitle="", doc=None, section_title=None, root_title="作业设计单"):
    """把渲染好的 Markdown 作业单转成老师好用的 Word(.docx)。"""
    from docx import Document
    from docx.shared import Pt, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    CNKI_BLUE = RGBColor(0x0C, 0x45, 0x93)
    GRAY = RGBColor(0x66, 0x66, 0x66)
    DARK = RGBColor(0x22, 0x22, 0x22)

    SHADE = {
        "原题出处": ("EDF2F8", "5B9BD5"),
        "改编自": ("E7F0FA", "2E75B6"),
        "学术溯源": ("E8F5E9", "2E7D32"),
        "未检索到可引用 CNKI 文献": ("F2F2F2", "999999"),
        "答案一致性验算": ("FFF7E6", "C9A227"),
        "参考答案与解析": ("F7F7F7", "BBBBBB"),
    }
    SHADED = set(SHADE.keys())
    TOP_INFO = ("课标对齐", "核心素养", "题目来源")

    def _run(run, name="宋体", size=10.5, bold=False, color=None, italic=False):
        run.font.name = name
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        if color is not None:
            run.font.color.rgb = color
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        rFonts.set(qn("w:eastAsia"), name)
        rFonts.set(qn("w:ascii"), name)
        rFonts.set(qn("w:hAnsi"), name)

    def _shade(p, fill="F2F5FA", border_color=None, border_sz=24):
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
        pPr.append(shd)
        if border_color:
            borders = pPr.find(qn("w:pBdr"))
            if borders is None:
                borders = OxmlElement("w:pBdr")
                pPr.append(borders)
            left = OxmlElement("w:left")
            left.set(qn("w:val"), "single")
            left.set(qn("w:sz"), str(border_sz))
            left.set(qn("w:space"), "6")
            left.set(qn("w:color"), border_color)
            borders.append(left)

    def _blank(doc, h=4):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(h)
        p.paragraph_format.space_before = Pt(0)
        return p

    def _fill_cell(cell, text, bold=False, fill=None, color=None):
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        run = p.add_run(str(text))
        _run(run, "宋体", 9.5, bold=bold, color=color)
        if fill:
            tcPr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), fill)
            tcPr.append(shd)

    def _add_table(doc, tb):
        head = tb.get("head") or []
        rows = tb.get("rows") or []
        if not head and not rows:
            return
        ncol = max(len(head), *(len(r) for r in rows)) if rows else len(head)
        nrow = (1 if head else 0) + len(rows)
        t = doc.add_table(rows=nrow, cols=ncol)
        try:
            t.style = "Table Grid"
        except Exception:
            pass
        t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ridx = 0
        if head:
            for c in range(ncol):
                _fill_cell(t.rows[ridx].cells[c], head[c] if c < len(head) else "",
                           bold=True, fill="0C4593", color=RGBColor(0xFF, 0xFF, 0xFF))
            ridx += 1
        for row in rows:
            for c in range(ncol):
                _fill_cell(t.rows[ridx].cells[c], row[c] if c < len(row) else "")
            ridx += 1
        # 表格上下留白：用紧邻的空白段落控制（Table 无 paragraph_format）

    def _add_figure(doc, fig):
        """嵌入一张原题附图（如题库自带的折线统计图）。路径不存在则降级为占位文字。"""
        path = fig.get("path", "")
        cap = (fig.get("caption") or "").strip()
        if path and os.path.exists(path):
            para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            para.paragraph_format.space_before = Pt(2); para.paragraph_format.space_after = Pt(1)
            try:
                para.add_run().add_picture(path, width=Cm(11))
            except Exception:
                _run(para.add_run("[图片：%s]" % (cap or "原图")), "宋体", 9, False, GRAY)
            if cap:
                cap_p = doc.add_paragraph(); cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                _run(cap_p.add_run(cap), "宋体", 9, False, GRAY)
                cap_p.paragraph_format.space_after = Pt(4)
        else:
            ph = doc.add_paragraph(); ph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _run(ph.add_run("[原题配图未能嵌入：%s]" % (cap or "原图")), "宋体", 9, False, GRAY)
            ph.paragraph_format.space_after = Pt(4)
        _blank(doc, 2)

    # ---- 解析 md ----
    lines = md_text.split("\n")
    title = ""
    info = {}
    tier = None
    tiers = []
    blocks = []
    tables_top = []
    figures_top = []
    i, n = 0, len(lines)
    shared_material = {"heading": "", "lines": []}
    in_shared = False

    def _is_sep_line(s):
        t = s.strip().strip("|").strip()
        if not t:
            return False
        return all(re.fullmatch(r":?-+:?", c.strip()) for c in t.split("|"))

    def _split_pipe(s):
        s = s.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        return [c.strip() for c in s.split("|")]

    def _is_table_start(k):
        return k < n and lines[k].strip().startswith("|") and (k + 1 < n and _is_sep_line(lines[k + 1]))

    def _parse_table(k):
        header = _split_pipe(lines[k])
        j = k + 2
        rows = []
        while j < n:
            ln = lines[j].strip()
            if not ln:
                break
            if ln.startswith("|") or (ln.count("|") >= 1 and ln[0] not in "#>*`"):
                rows.append(_split_pipe(ln))
                j += 1
            else:
                break
        return header, rows, j

    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        # ---- 表格（GFM）检测：将 Markdown 表格转为真正的 Word 表格 ----
        if _is_table_start(i):
            header, rows, j = _parse_table(i)
            tbl = {"head": header, "rows": rows}
            if tier and tier["questions"]:
                tier["questions"][-1].setdefault("tables", []).append(tbl)
            else:
                tables_top.append(tbl)
            i = j
            continue
        if s.startswith("# ") and not title:
            title = s[2:].strip(); i += 1; continue
        if s.startswith("## "):
            name = s[3:].strip()
            if name == "共享材料":
                in_shared = True
                shared_material["heading"] = name
                tier = None
            elif name.startswith(("基础", "巩固", "拓展")):
                in_shared = False
                tier = {"name": name, "callout": "", "questions": []}
                tiers.append(tier)
            elif name.startswith("著录缺口"):
                in_shared = False
                blocks.append({"kind": "footer", "lines": []})
                tier = None
            else:
                in_shared = False
                tier = None
            i += 1; continue
        if s.startswith("> "):
            if in_shared:
                shared_material["lines"].append(s[2:].strip())
            elif tier is not None:
                tier["callout"] = s[2:].strip()
            i += 1; continue
        # 原图嵌入标记：![caption](abspath)
        m_img = re.match(r"^!\[(.*?)\]\((.*?)\)$", s)
        if m_img:
            _fig = {"caption": m_img.group(1).strip(), "path": m_img.group(2).strip()}
            if tier and tier["questions"]:
                tier["questions"][-1].setdefault("figures", []).append(_fig)
            else:
                figures_top.append(_fig)
            i += 1; continue
        # 任务标题：容忍「｜ 在加粗外」(规范) 与「｜ 在加粗内」(历史/易错写法) 两种格式
        th = None
        m_outer = re.match(r"^\*\*(.+?)\*\*\s*｜\s*(.*)$", s)
        if m_outer:
            th = (m_outer.group(1).strip(),
                  [x.strip() for x in m_outer.group(2).split("｜")] if m_outer.group(2).strip() else [])
        else:
            m_inner = re.match(r"^\*\*(.+?｜.+?)\*\*\s*(.*)$", s)
            if m_inner:
                cname, cmeta = m_inner.group(1).split("｜", 1)
                th = (cname.strip(),
                      [x.strip() for x in cmeta.split("｜")] if cmeta.strip() else [])
        if th:
            name, meta = th
            if tier is not None:
                q = {"name": name, "meta": meta, "parts": [], "stem": ""}
                tier["questions"].append(q)
                j = i + 1
                while j < n:
                    nx = lines[j].strip()
                    if not nx or nx.startswith("**") or nx.startswith("## ") or nx.startswith("> ") or nx.startswith("<") or nx.startswith("!["):
                        break
                    if _is_table_start(j):
                        break
                    q["stem"] += ("\n" if q["stem"] else "") + nx
                    j += 1
                i = j
                continue
            i += 1; continue
        ml = re.match(r"^\*\*(.+?)\*\*[：:]\s*(.*)$", s)
        if ml:
            label = ml.group(1).strip()
            content = ml.group(2).strip()
            j = i + 1
            while j < n:
                nx = lines[j].strip()
                if not nx or nx.startswith("**") or nx.startswith("## ") or nx.startswith("> ") or nx.startswith("<") or nx.startswith("!["):
                    break
                if _is_table_start(j):
                    break
                content += "\n" + nx
                j += 1
            i = j
            if label in TOP_INFO or tier is None:
                info[label] = content
            elif tier is not None and tier["questions"]:
                tier["questions"][-1]["parts"].append({"label": label, "content": content})
            else:
                blocks.append({"kind": "meta", "label": label, "content": content})
            continue
        i += 1

    def _fmt_kp(text):
        t = text.strip()
        if t.startswith("[") and t.endswith("]"):
            inner = t[1:-1].replace("', '", "；").replace("','", "；")
            return inner.strip("'\"")
        return t

    # ---- 构建 docx ----
    is_new = doc is None
    if is_new:
        doc = Document()
        sec = doc.sections[0]
        sec.page_height = Cm(29.7); sec.page_width = Cm(21)
        sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)
        sec.top_margin = Cm(2); sec.bottom_margin = Cm(2)
        st = doc.styles["Normal"]
        st.font.name = "宋体"; st.font.size = Pt(10.5)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    if is_new:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _run(p.add_run(root_title), "微软雅黑", 20, True, CNKI_BLUE)
        p.paragraph_format.space_after = Pt(2)
        if subtitle:
            sp = doc.add_paragraph(); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _run(sp.add_run(subtitle), "微软雅黑", 10.5, False, GRAY)
            sp.paragraph_format.space_after = Pt(8)
        else:
            _blank(doc, 6)
    else:
        doc.add_page_break()
        if section_title:
            _blank(doc, 2)
            is_teacher = ("教师" in section_title) or ("备课" in section_title)
            box_fill = "EDE7F6" if is_teacher else "E6EFF7"
            box_color = "7B61FF" if is_teacher else "0C4593"
            title_color = RGBColor(0x5B, 0x3F, 0xB0) if is_teacher else CNKI_BLUE
            hsec = doc.add_paragraph(); _shade(hsec, box_fill, box_color)
            hsec.paragraph_format.space_after = Pt(2); hsec.paragraph_format.space_before = Pt(2)
            _run(hsec.add_run(section_title), "微软雅黑", 13, True, title_color)
            hnote = doc.add_paragraph()
            note_text = ("以下内容仅供教师备课参考，请勿下发给学生。"
                         if is_teacher else
                         "以下内容为学生作业纸，可直接打印下发给学生。")
            _run(hnote.add_run(note_text), "宋体", 9, False, GRAY)
            hnote.paragraph_format.space_after = Pt(6)

    if info:
        card = doc.add_paragraph(); _shade(card, "F2F5FA")
        card.paragraph_format.space_after = Pt(8); card.paragraph_format.space_before = Pt(2)
        for key in TOP_INFO:
            if key in info:
                _run(card.add_run(key + "："), "微软雅黑", 9.5, True, CNKI_BLUE)
                _run(card.add_run(info[key]), "宋体", 9.5, False, DARK)
                card.add_run().add_break()

    # 共享材料（同材异层模式）：在层级之前顶部渲染一次
    if shared_material.get("heading") and shared_material.get("lines"):
        hsm = doc.add_paragraph()
        _run(hsm.add_run(shared_material["heading"]), "微软雅黑", 13, True, CNKI_BLUE)
        hsm.paragraph_format.space_before = Pt(4)
        hsm.paragraph_format.space_after = Pt(2)
        smp = doc.add_paragraph(); _shade(smp, "F2F5FA")
        smp.paragraph_format.space_after = Pt(8); smp.paragraph_format.space_before = Pt(2)
        for li, line in enumerate(shared_material["lines"]):
            if li:
                smp.add_run().add_break()
            _run(smp.add_run(line), "宋体", 9.5, False, DARK)

    # 无层级归属的顶部表格（共享材料中的统计表等）渲染在层级之前
    for tb in tables_top:
        if tb.get("caption"):
            cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _run(cap.add_run(tb["caption"]), "宋体", 9, False, GRAY)
            cap.paragraph_format.space_after = Pt(1)
        _add_table(doc, tb)
    for _fig in figures_top:
        _add_figure(doc, _fig)

    for tier in tiers:
        _blank(doc, 2)
        h = doc.add_paragraph()
        _run(h.add_run(tier["name"]), "微软雅黑", 14, True, CNKI_BLUE)
        h.paragraph_format.space_before = Pt(4); h.paragraph_format.space_after = Pt(2)
        pPr = h._p.get_or_add_pPr()
        pbdr = OxmlElement("w:pBdr"); bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "8")
        bottom.set(qn("w:space"), "2"); bottom.set(qn("w:color"), "0C4593")
        pbdr.append(bottom); pPr.append(pbdr)
        if tier["callout"]:
            cp = doc.add_paragraph(); _shade(cp, "EAF1F8")
            cp.paragraph_format.space_after = Pt(6); cp.paragraph_format.space_before = Pt(2)
            parts = tier["callout"].split("｜")
            labels = ["面向学情", "培养目标"]
            for idx, seg in enumerate(parts):
                seg = seg.strip()
                if "：" in seg:
                    lab, txt = seg.split("：", 1)
                else:
                    lab, txt = (labels[idx] if idx < len(labels) else "说明"), seg
                _run(cp.add_run(lab + "："), "微软雅黑", 9.5, True, CNKI_BLUE)
                _run(cp.add_run(txt.strip()), "宋体", 9.5, False, DARK)
                if idx < len(parts) - 1:
                    cp.add_run().add_break()
        for q in tier["questions"]:
            _blank(doc, 2)
            qp = doc.add_paragraph(); qp.paragraph_format.space_after = Pt(1)
            _run(qp.add_run(q["name"]), "微软雅黑", 11.5, True, DARK)
            if q["meta"]:
                _run(qp.add_run("　" + " · ".join(q["meta"])), "微软雅黑", 9.5, False, GRAY)
            if q.get("stem"):
                sp = doc.add_paragraph(); sp.paragraph_format.space_after = Pt(3)
                segs = q["stem"].split("\n")
                for si, seg in enumerate(segs):
                    if si:
                        sp.add_run().add_break()
                    _run(sp.add_run(seg), "宋体", 10.5, False, DARK)
            for tb in (q.get("tables") or []):
                if tb.get("caption"):
                    cap = doc.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    _run(cap.add_run(tb["caption"]), "宋体", 9, False, GRAY)
                    cap.paragraph_format.space_after = Pt(1)
                _add_table(doc, tb)
            for _fig in (q.get("figures") or []):
                _add_figure(doc, _fig)
            for part in q["parts"]:
                label = part["label"]; content = part["content"].strip()
                if label in ("问题", "子问题"):
                    qp = doc.add_paragraph(); qp.paragraph_format.space_after = Pt(3)
                    for li, line in enumerate(content.split("\n")):
                        if li:
                            qp.add_run().add_break()
                        _run(qp.add_run(line), "宋体", 10.5, False, DARK)
                    continue
                if label == "题干":
                    gp = doc.add_paragraph(); gp.paragraph_format.space_after = Pt(3)
                    _run(gp.add_run(content), "宋体", 11, True, DARK)
                    continue
                if label == "考查知识点":
                    pp = doc.add_paragraph(); pp.paragraph_format.space_after = Pt(2)
                    _run(pp.add_run("考查知识点："), "微软雅黑", 10, True, DARK)
                    _run(pp.add_run(_fmt_kp(content)), "宋体", 10, False, DARK)
                    continue
                if label in SHADED:
                    fill, bcol = SHADE[label]
                    bp = doc.add_paragraph(); _shade(bp, fill, bcol)
                    bp.paragraph_format.space_after = Pt(3); bp.paragraph_format.space_before = Pt(1)
                    italic = (label == "未检索到可引用 CNKI 文献")
                    _run(bp.add_run(label + "："), "微软雅黑", 9.5, True, RGBColor.from_string(bcol), italic)
                    for _i, _seg in enumerate(str(content).split("\n")):
                        if _i:
                            bp.add_run().add_break()
                        _run(bp.add_run(_seg), "宋体", 9.5, False, DARK, italic)
                else:
                    pp = doc.add_paragraph(); pp.paragraph_format.space_after = Pt(3)
                    _run(pp.add_run(label + "："), "微软雅黑", 10, True, DARK)
                    for _i, _seg in enumerate(str(content).split("\n")):
                        if _i:
                            pp.add_run().add_break()
                        _run(pp.add_run(_seg), "宋体", 10, False, DARK)

    for b in blocks:
        if b.get("kind") == "footer" and b.get("lines"):
            _blank(doc, 4)
            fh = doc.add_paragraph()
            _run(fh.add_run("著录缺口与说明"), "微软雅黑", 11, True, RGBColor(0xB0, 0x6A, 0x00))
            fh.paragraph_format.space_after = Pt(2)
            for ln in b["lines"]:
                lp = doc.add_paragraph(ln.strip())
                if not lp.runs:
                    lp.add_run(ln.strip())
                _run(lp.runs[0], "宋体", 9.5, False, GRAY)
                lp.paragraph_format.space_after = Pt(1)

    if out_path:
        doc.save(out_path)
    return doc


# ==========================================================================
# CLI
# ==========================================================================
def _load_json_or_path(p):
    """参数是 JSON 字符串、文件路径还是 stdin？三种都支持。"""
    if p == "-":
        return json.load(sys.stdin)
    if p.strip().startswith("{") or p.strip().startswith("["):
        return json.loads(p)
    return json.load(open(p, encoding="utf-8"))


def _read_text_or_path(p):
    """items 可能是模型吐的裸文本（带 ```json 围栏），也可能是文件路径。"""
    if p == "-":
        return sys.stdin.read()
    if p.strip().startswith("{") or p.strip().startswith("```"):
        return p
    if os.path.exists(p):
        return open(p, encoding="utf-8").read()
    return p


def main():
    ap = argparse.ArgumentParser(description="中小学作业设计 AI 约束套件")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("packs", help="打印学科包+学段包")
    a.add_argument("--subject", default="数学")
    a.add_argument("--stage", default="初中(7-9)")

    ap_p = sub.add_parser("presets", help="打印六类作业用途的供给配额预设")

    b = sub.add_parser("prompt", help="拼装 prompt")
    b.add_argument("--params", required=True, help="JSON 字符串或 .json 文件路径，- 表示 stdin")

    c = sub.add_parser("route", help="供给路由")
    c.add_argument("--params", required=True)
    c.add_argument("--out-plan", help="把 plan_json 写到文件")

    d = sub.add_parser("validate", help="生成后校验")
    d.add_argument("--items", required=True, help="模型输出（JSON 字符串/文件/-）")
    d.add_argument("--subject", default="数学")
    d.add_argument("--stage", default="初中(7-9)")
    d.add_argument("--plan", help="plan_json 字符串或文件")
    d.add_argument("--max-minutes", type=float)

    f = sub.add_parser("variants", help="一题多变式：拿一道真题派生 N 个互不重复的变式")
    f.add_argument("--items", help="已有 items.json（模型输出或已过校验的作业单）")
    f.add_argument("--id", type=int, help="母题在 items 里的 id；不给则取第一题")
    f.add_argument("--bank", help="题库文件（直接从一道真题派生，不必先做出作业单）")
    f.add_argument("--bank-id", help="题库里的 bank_id，如 Q07")
    f.add_argument("--n", type=int, default=3, help="变式个数（<=4），给了 --kinds 则以 kinds 为准")
    f.add_argument("--kinds", help="逗号分隔：retune(同构换数),rescene(换情境),reverse(逆向设问),recondition(增减条件)")
    f.add_argument("--subject", default="数学")
    f.add_argument("--stage", default="初中(7-9)")
    f.add_argument("--out-plan", help="变式计划写到文件，可直接喂给 validate 的 --plan")

    e = sub.add_parser("render", help="渲染 Markdown 作业单")
    e.add_argument("--items", required=True)
    e.add_argument("--subject", default="数学")
    e.add_argument("--stage", default="初中(7-9)")
    e.add_argument("--plan")
    e.add_argument("--max-minutes", type=float)
    e.add_argument("--out", help="输出文件路径，缺省打印到标准输出")
    e.add_argument("--format", default="md", choices=["md", "docx"],
                   help="输出格式：md 文本 或 docx（老师可直接打印/编辑）")
    e.add_argument("--subtitle", default="", help="docx 副标题（如「一元二次方程的应用 · 初中数学 · 课后巩固」）")
    e.add_argument("--audience", default="teacher", choices=["teacher", "student", "both"],
                   help="docx 内容：teacher=教师设计单（默认）；student=仅学生作业纸；both=学生作业纸+教师备课参考合为一册")
    e.add_argument("--figures", default="both", choices=["both", "teacher", "student", "none"],
                   help="原题附图（如题库自带的折线统计图）嵌入范围："
                        "both=学生+教师(默认)，teacher=仅教师备课参考，student=仅学生作业纸，none=不嵌入")

    args = ap.parse_args()

    if args.cmd == "packs":
        print(json.dumps(get_pack(args.subject, args.stage), ensure_ascii=False, indent=2))

    elif args.cmd == "presets":
        print(presets_text())

    elif args.cmd == "prompt":
        p = _load_json_or_path(args.params)
        # 给了 plan_text 就直接用；否则若是 dict 形式的 plan 也不替它造（prompt 与 route 分开跑是常态）
        print(build_prompt(p))

    elif args.cmd == "route":
        p = _load_json_or_path(args.params)
        r = route_supply(p)
        print(r["plan_text"])
        if args.out_plan:
            open(args.out_plan, "w", encoding="utf-8").write(r["plan_json"])
            print("\n[plan_json 已写入 %s]" % args.out_plan)

    elif args.cmd == "validate":
        plan = None
        if args.plan:
            pl = _load_json_or_path(args.plan)
            plan = json.dumps(pl, ensure_ascii=False) if isinstance(pl, dict) else pl
        r = validate(_read_text_or_path(args.items), args.subject, args.stage, plan, args.max_minutes)
        print(r["summary"])
        for x in r["issues"]:
            print("  -", x)
        for x in r.get("warns", []):
            print("  ~", x)
        if r["ok"]:
            print("  + 全部通过" + ("" if not r.get("warns") else "（有溯源提醒，见上方 ~ 行）"))
        sys.exit(0 if r["ok"] else 1)

    elif args.cmd == "variants":
        if not (args.items or args.bank):
            raise SystemExit("variants 需要 --items（已有作业单）或 --bank（题库文件），二选一")
        if args.items:
            data, err = _extract_json(_read_text_or_path(args.items))
            if err:
                raise SystemExit(err)
            parent = _parent_from_items(data, args.id)
        else:
            cands = _candidates_from_bank(_load_json_or_path(args.bank), with_answer=True)
            if not cands:
                raise SystemExit("题库为空")
            if args.bank_id:
                hit = [c for c in cands if c["bank_id"] == str(args.bank_id)]
                if not hit:
                    raise SystemExit("题库里没有 bank_id=%s（可用：%s）"
                                     % (args.bank_id, "、".join(c["bank_id"] for c in cands[:20])))
                parent = hit[0]
            else:
                parent = cands[0]
        kinds = [k for k in (args.kinds or "").replace("，", ",").split(",") if k.strip()]
        r = variant_plan(parent, args.subject, args.stage, args.n or 3, kinds or None)
        print(r["plan_text"])
        if r["invalid"]:
            print("\n[忽略的未知变式类型：%s；可用：%s]"
                  % ("、".join(r["invalid"]), "、".join(VARIANT_ORDER)))
        if args.out_plan:
            open(args.out_plan, "w", encoding="utf-8").write(r["plan_json"])
            print("\n[变式计划已写入 %s]" % args.out_plan)

    elif args.cmd == "render":
        plan = None
        if args.plan:
            pl = _load_json_or_path(args.plan)
            plan = json.dumps(pl, ensure_ascii=False) if isinstance(pl, dict) else pl
        r = validate(_read_text_or_path(args.items), args.subject, args.stage, plan,
                     getattr(args, "max_minutes", None))
        teacher_md = render(r["items"], "\n".join(r["issues"]), r["data"].get("meta"),
                            r.get("warns"), stage=args.stage, subject=args.subject,
                            figures=getattr(args, "figures", "both"))
        audience = getattr(args, "audience", "teacher")
        figs = getattr(args, "figures", "both")
        fmt = getattr(args, "format", "md")
        out = args.out

        def _student_md():
            _sm = (r.get("data") or {}).get("meta", {}).get("shared_material")
            return build_student_md(r["items"], args.subject, args.stage,
                                   figures=figs, shared_material=_sm)

        if not out:
            if audience == "student":
                print(_student_md())
            elif audience == "both":
                print(_student_md())
                print("\n\n========== 教师备课参考（请勿下发学生）==========\n\n")
                print(teacher_md)
            else:
                print(teacher_md)
            sys.exit(0 if r["ok"] else 1)
        if fmt == "docx" or str(out).endswith(".docx"):
            if not str(out).endswith(".docx"):
                out = str(out) + ".docx"
            if audience == "student":
                md_to_docx(_student_md(), out, getattr(args, "subtitle", ""),
                           root_title="学生作业纸")
            elif audience == "both":
                doc = md_to_docx(_student_md(), None, getattr(args, "subtitle", ""),
                                root_title="学生作业纸")
                md_to_docx(teacher_md, out, "", doc=doc,
                           section_title="教师备课参考（以下内容仅供教师备课，请勿下发学生）")
            else:
                md_to_docx(teacher_md, out, getattr(args, "subtitle", ""))
            print("已写入 %s｜%s" % (out, r["summary"]))
        else:
            if audience == "student":
                open(out, "w", encoding="utf-8").write(_student_md())
            elif audience == "both":
                with open(out, "w", encoding="utf-8") as f:
                    f.write(_student_md())
                    f.write("\n\n========== 教师备课参考（请勿下发学生）==========\n\n")
                    f.write(teacher_md)
            else:
                open(out, "w", encoding="utf-8").write(teacher_md)
            print("已写入 %s｜%s" % (out, r["summary"]))


if __name__ == "__main__":
    main()
