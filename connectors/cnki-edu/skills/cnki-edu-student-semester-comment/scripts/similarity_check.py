# -*- coding: utf-8 -*-
"""【第三段】评语雷同度自检。

为什么需要它：班主任写几十条评语，最大的质量事故不是写错字，而是"一个味儿"。
家长群里一对比就露馅。本脚本把"像不像"变成可量化的分数。

六类检测：
  1. 区别性字形相似度  —— 剔除套话后的汉字 bigram Jaccard（主指标）
  2. 骨架相似度        —— 把「学科/时间/数字/姓名」等可替换槽位归一后，再看 bigram Jaccard
  3. 同句式句对        —— 逐句抽象成句式模板（实词→○，虚词保留），跨评语找同一句式
  4. 开头撞车        —— 前 N 字完全相同的评语对
  5. 结尾撞车        —— 后 N 字完全相同的评语对（万能收尾句的照妖镜）
  6. 标签与转译词扎堆  —— 同一印象标签用了几次、同一个"待改进"说法用了几次

为什么需要 2 和 3：主指标剔除套话后看的是**实词**重合度，于是「同一个句式、把里面的
学科/时间/数字/事迹全换成另一个人的」，实词几乎全不重合，主指标只有 0.05 上下，
看起来比谁都干净——这是最典型的漏网雷同形态。「十二周里你的数学作业一次没落下」
与「十六周里你的英语笔记一篇没缺过」，人一眼就看出是一个模子，主指标却判可接受。
2 从"把可替换成分抹掉再看"、3 从"逐句看句法骨架"两个角度把它抓回来。

另有一项**跨年**检测（`--past`，选了往年评语材料才跑）：
上面六类比的都是"今年这几十条之间像不像"，比不出「学生自己这一年的评语照搬了去年的」——
那种情况在这六类里根本没有可比对象。传 `--past` 后，把每人的评语逐句与**他自己**的
往年评语比一遍句式骨架，命中即提示换骨架重写（阈值沿用句级 0.82，同一把尺子）。

用法：
  python similarity_check.py --comments comments.json                       # 只看控制台结论，不落盘
  python similarity_check.py --comments comments.json --out 雷同度报告.md    # 需要可核查的文件时
  python similarity_check.py --comments comments.json \
      --comments-too comments_naive.json --tag-too 模板写法                  # 加对照组
  python similarity_check.py --comments comments.json --past roster.json    # 再查「有没有照搬去年那句」
"""
import argparse
import itertools
import json
import os
import re
import sys
from collections import Counter, OrderedDict

# 校园评语里的高频套话 bigram —— 它们出现在几十条评语里是正常的，不该算"雷同"
CLICHE = set("""
学习 习上 上课 课堂 老师 同学 班级 集体 平时 一直 总是 能够 可以 希望 期待 相信
努力 认真 认真 踏实 勤奋 刻苦 积极 主动 乐观 开朗 阳光 善良 热心 礼貌 尊敬 师长
作业 成绩 期末 学期 这学 本学 下学 继续 保持 加油 再接 再厉 更上 一层 进步 优秀
表现 方面 地方 时候 一定 更加 明显 很大 非常 十分 比较 有些 有点 还需 需要 建议
提高 提升 加强 注意 争取 做到 做得 做到 好的 不错 很好 值得 特别 尤其 虽然 但是
""".split())

# 转译词：用于检测"待改进"表述是否扎堆
SOFTEN_PAT = ["还有较大提升空间", "需要加强", "有待提高", "还需努力", "继续努力",
              "更加专注", "更多投入", "更大进步", "有待提升", "尚需加强"]

HAN = re.compile(r"[^\u4e00-\u9fff]")
HAN_RUN = re.compile(r"[^\u4e00-\u9fff]+")

# ---------- 骨架检测用到的词表 ----------
# 学科名：说同一件事时最常被整体替换的成分。
# 长名在前，避免「道德与法治」被截成「道德」后再匹配不上（同一门课的简称/全称都要能归零）。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from subjects import SUBJECT_POOL  # noqa: E402

SUBJECT_WORDS = sorted(SUBJECT_POOL + ["劳动"], key=len, reverse=True)

# 时间/频次槽位：同骨架换词时几乎必换
SLOT_TIME = ["这学期", "本学期", "上学期", "下学期", "这学年", "本学年", "新学期",
             "期末考试", "期末", "期中考试", "期中", "月考", "期初", "开学", "平时",
             "最近", "近来", "这阵子", "这段时间", "这一阵", "每天", "每周", "每次",
             "每回", "往后", "今后", "接下来", "将来", "以后", "下回", "下次"]

SLOT_DIGIT = re.compile(r"\d+(?:\.\d+)?")
SLOT_CN_NUM = re.compile(r"[零一二三四五六七八九十百千两]+")

# 功能字：句式抽象时**保留**的字（虚词、体标记、通用句式字）。
# 只列真正的虚字——量词（个/次/篇/回/份…）刻意不收，否则会把"换了量词"抹平掉。
FUNC_CHARS = set(
    "的了着过呢吗吧啊呀哦嘛"
    "是就有会能要得可应须该想让被把给对向跟和与同"
    "不没无未莫别"
    "很太更最挺稍颇"
    "也还都又再才只仅便即"
    "在从到往离经"
    "这那哪谁什怎"
    "上中下里内外前后间边"
    "你的我他她它咱"
)

# 双字功能词：整体保留（避免被拆成两个实字）
FUNC_PHRASES = ["原本", "本来", "其实", "确实", "的确", "大概", "也许", "似乎", "好像",
                "仿佛", "简直", "几乎", "尤其", "甚至", "特别", "十分", "虽然", "但是",
                "可是", "不过", "而是", "只是", "就是", "还是", "因为", "所以", "并且",
                "而且", "或者", "即使", "无论", "不管", "因此", "于是", "否则", "总是",
                "一直", "从来", "已经", "曾经", "正在", "将要", "可以", "能够", "应该",
                "必须", "需要", "值得", "显得", "算是", "变得", "觉得", "知道", "发现",
                "看到", "相信", "希望", "期待", "如果", "再说", "对于", "至于", "顺着",
                "趁着", "随着", "沿着", "按照", "根据", "由于", "为了", "除了"]

# 切句：句子是句式骨架的天然单位。只在句末标点处切，**逗号不切**——
# 切太碎会让模板退化成「但○了○」这种没有鉴别力的碎片。
SENT_SPLIT = re.compile(r"[。！？!?；;\n\r]+")


def han(s):
    return HAN.sub("", s or "")


def bigrams(s):
    """按标点/数字切段后再取 bigram，避免产出「期你」「上你」这类跨标点伪词。"""
    out = set()
    for seg in HAN_RUN.split(s or ""):
        for i in range(len(seg) - 1):
            out.add(seg[i:i + 2])
    return out


def distinct_bigrams(s):
    # 注意：不能先 han(s) 再切 bigram，否则会跨标点拼出「期你」这类伪词。
    # 交给 bigrams() 自己按标点分段。
    return {b for b in bigrams(s) if b not in CLICHE}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    i = len(a & b)
    u = len(a | b)
    return round(i / u, 4) if u else 0.0


# ---------- 「同骨架换词」检测 ----------
def slot_normalize(text, names=()):
    """把可替换槽位归一：姓名→&、时间→$、学科→@、数字→#。

    这一步的目的不是「更准地算相似度」，而是**故意抹掉最容易被换掉的成分**，
    让「十二周里你的数学作业」和「十六周里你的英语笔记」剩下同样的骨架。
    """
    s = text or ""
    for nm in names:
        if nm and len(nm) >= 2 and nm in s:
            s = s.replace(nm, "&")
    for w in SLOT_TIME:
        if w in s:
            s = s.replace(w, "$")
    for w in SUBJECT_WORDS:
        if w in s:
            s = s.replace(w, "@")
    s = SLOT_DIGIT.sub("#", s)
    s = SLOT_CN_NUM.sub("#", s)
    s = re.sub(r"([#$@&])\1+", r"\1", s)
    return s


def skeleton_bigrams(text, names=()):
    """骨架 bigram：槽位归一 + 剔套话后的汉字 bigram。"""
    return {b for b in bigrams(slot_normalize(text, names)) if b not in CLICHE}


def sentence_templates(text, names=()):
    """把评语切成句，每句抽象成句式模板（保留 list 形式）。

    实词一律压成 ○ 并合并连续 ○，虚词按原样保留。于是
      「数学这门课你原本基础不牢，但期末一口气提到了八十多」
      「物理这门课你原本入门不顺，但期中一口气拿到了九十多」
    都得到 `○这○你原本○不○但○了○`——换词换不掉句法骨架。
    """
    out = []
    for seg in SENT_SPLIT.split(text or ""):
        seg = han(seg)
        if len(seg) < 8:
            continue
        s = slot_normalize(seg, names)
        tpl, i = [], 0
        while i < len(s):
            hit = None
            for p in FUNC_PHRASES:
                if s.startswith(p, i):
                    hit = p
                    break
            if hit:
                tpl.append(hit)
                i += len(hit)
                continue
            ch = s[i]
            if ch in FUNC_CHARS:
                tpl.append(ch)
            elif not tpl or tpl[-1] != "○":
                tpl.append("○")
            i += 1
        # 少于 6 个元素的模板鉴别力太弱（「○你○」什么句子都能撞上）
        if len(tpl) >= 6:
            out.append((tpl, seg))
    return out


def seq_sim(a, b):
    """两个模板序列的相似度 = 1 - 归一化编辑距离（元素级）。"""
    la, lb = len(a), len(b)
    if not la or not lb:
        return 0.0
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        ca = a[i - 1]
        for j in range(1, lb + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (0 if ca == b[j - 1] else 1))
        prev = cur
    return round(1.0 - prev[lb] / float(max(la, lb)), 4)


def tpl_rough(a, b):
    """粗筛用：模板元素 bigram 的 Jaccard，比编辑距离便宜得多。"""
    return jaccard({(a[i], a[i + 1]) for i in range(len(a) - 1)},
                   {(b[i], b[i + 1]) for i in range(len(b) - 1)})


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    items = d.get("comments", d if isinstance(d, list) else [])
    out = []
    for c in items:
        out.append({
            "学号": str(c.get("学号", "")),
            "姓名": c.get("姓名", ""),
            "标签": c.get("核心印象标签", "") or c.get("标签", ""),
            "分层": c.get("分层", ""),
            "正文": c.get("评语正文", "") or c.get("正文", ""),
        })
    return out


def load_past(path):
    """读「往年评语」来源，返回 {学号: 往年评语文本}。

    兼容两种输入（--past 都认）：
      · roster.json（prepare_roster.py 的产物）→ 取每条 roster 记录的「往年评语」
      · comments.json 样式（[{学号,姓名,评语正文}] 或 {"comments":[...]}）→ 取「往年评语/评语正文」
    """
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    out = {}
    if isinstance(d, dict) and "roster" in d:
        for s in d["roster"]:
            t = (s.get("往年评语") or "").strip()
            if t:
                out[str(s.get("学号", ""))] = t
    else:
        items = d.get("comments", d if isinstance(d, list) else [])
        for c in items:
            t = (c.get("往年评语") or c.get("评语正文") or c.get("正文") or "").strip()
            if t:
                out[str(c.get("学号", ""))] = t
    return out


def past_overlap(items, past_map, warn=0.82, top_n=5):
    """把「今年这版评语」逐句与**同一个学生**的往年评语比对。

    为什么单列这一项：批内的三项指标比的是**今年同学之间**是否雷同，
    「学生自己今年的评语抄了去年那条」在这三项里**完全看不见**（没有可比对象）。
    而往年评语正是本次写作的参考材料，最容易踩的坑就是照搬去年那句——
    换几个词、句法骨架一模一样。

    阈值沿用句级 0.82（与 `--sent-warn` 同一把尺子）：它已被 40 条真实评语校准过——
    批内最像的两个句子只有 0.706，0.82 之上只有"真照搬"才会命中，不误报是前提。

    覆盖面与批内「同句式句对」一致：**不足 8 个汉字的短句不参与比对**（鉴别力太弱），
    所以抓的是长句照搬；短句层面仍靠人工扫开头与结尾。
    """
    hits, per = [], []
    for it in items:
        k = str(it.get("学号", ""))
        ptxt = past_map.get(k, "")
        if not ptxt:
            continue
        cur = sentence_templates(it["正文"])
        old = sentence_templates(ptxt)
        pairs = []
        for (ta, sa) in cur:
            for (tb, sb) in old:
                if tpl_rough(ta, tb) < 0.4:      # 粗筛，省掉绝大部分编辑距离计算
                    continue
                sim = seq_sim(ta, tb)
                if sim >= warn:
                    pairs.append({"相似度": sim, "今年": sa, "往年": sb})
        pairs.sort(key=lambda x: -x["相似度"])
        per.append({"学号": k, "姓名": it.get("姓名", ""),
                    "今年句数": len(cur), "往年句数": len(old),
                    "最高": (pairs[0]["相似度"] if pairs else 0.0)})
        if pairs:
            hits.append({"学号": k, "姓名": it.get("姓名", ""), "最高": pairs[0]["相似度"],
                         "组数": len(pairs), "句对": pairs[:top_n]})
    hits.sort(key=lambda x: -x["最高"])
    return {"命中": hits, "逐人": per, "覆盖人数": len(per), "命中人数": len(hits),
            "命中组数": sum(h["组数"] for h in hits)}


def analyze(items, tag="本组", head_n=6, tail_n=8, warn=0.24, high=0.32,
            skel_warn=0.18, skel_high=0.28, sent_warn=0.82):
    n = len(items)
    if n == 0:
        # 0 条评语时 min()/max() 会抛 ValueError: min() iterable argument is empty，
        # 直接崩掉（评语还没写、或 --comments-too 指向空文件时就会踩到）。
        # 这里给一份结构完整的空结果，让控制台照常给出「没有可检评语」的结论。
        return OrderedDict([
            ("tag", tag), ("人数", 0),
            ("字数", {"最短": 0, "最长": 0, "平均": 0}),
            ("最相似对", []),
            ("相似度分布", {"平均": 0, "≥%.2f(高度雷同)的对数" % high: 0,
                        "≥%.2f(需检查)的对数" % warn: 0, "总对数": 0}),
            ("骨架最相似对", []),
            ("骨架相似度分布", {"平均": 0, "≥%.2f(高度同骨架)的对数" % skel_high: 0,
                          "≥%.2f(同骨架)的对数" % skel_warn: 0, "总对数": 0}),
            ("同句式句对", []), ("同句式句对总数", 0), ("句子总数", 0),
            ("开头撞车", []), ("结尾撞车", []), ("标签扎堆", []),
            ("转译词扎堆", []), ("高频区别性词", []),
            ("结论", ["没有可检评语（0 条）——请检查 --comments 指向的文件是否为空"]),
        ])
    res = OrderedDict()
    res["tag"] = tag
    res["人数"] = n
    lens = [len(han(x["正文"])) for x in items]
    res["字数"] = {"最短": min(lens), "最长": max(lens),
                   "平均": round(sum(lens) / n, 1)}

    all_names = [x["姓名"] for x in items if x.get("姓名")]
    pairs, skpairs = [], []
    for a, b in itertools.combinations(range(n), 2):
        ta, tb = items[a]["正文"], items[b]["正文"]
        pairs.append((jaccard(distinct_bigrams(ta), distinct_bigrams(tb)), a, b))
        skpairs.append((jaccard(skeleton_bigrams(ta, all_names),
                                skeleton_bigrams(tb, all_names)), a, b))
    pairs.sort(reverse=True)
    res["最相似对"] = [{
        "相似度": s, "A": "%s %s" % (items[a]["学号"], items[a]["姓名"]),
        "B": "%s %s" % (items[b]["学号"], items[b]["姓名"]),
        "A正文": items[a]["正文"], "B正文": items[b]["正文"],
        "判定": "高度雷同" if s >= high else ("需检查" if s >= warn else "可接受"),
    } for s, a, b in pairs[:10]]
    scores = [p[0] for p in pairs]
    res["相似度分布"] = {
        "平均": round(sum(scores) / len(scores), 4) if scores else 0,
        "≥%.2f(高度雷同)的对数" % high: sum(1 for s in scores if s >= high),
        "≥%.2f(需检查)的对数" % warn: sum(1 for s in scores if s >= warn),
        "总对数": len(scores),
    }

    # ---- 骨架相似度（指标 2）：抹掉可替换槽位后再比，专治「同骨架换词」 ----
    skpairs.sort(reverse=True)
    res["骨架最相似对"] = [{
        "相似度": s, "A": "%s %s" % (items[a]["学号"], items[a]["姓名"]),
        "B": "%s %s" % (items[b]["学号"], items[b]["姓名"]),
        "A骨架": slot_normalize(items[a]["正文"], all_names),
        "B骨架": slot_normalize(items[b]["正文"], all_names),
        "A正文": items[a]["正文"], "B正文": items[b]["正文"],
    } for s, a, b in skpairs[:8]]
    sks = [p[0] for p in skpairs]
    res["骨架相似度分布"] = {
        "平均": round(sum(sks) / len(sks), 4) if sks else 0,
        "≥%.2f(高度同骨架)的对数" % skel_high: sum(1 for s in sks if s >= skel_high),
        "≥%.2f(同骨架)的对数" % skel_warn: sum(1 for s in sks if s >= skel_warn),
        "总对数": len(sks),
    }

    # ---- 同句式句对（指标 3）：逐句抽象成模板，跨评语找同一句式 ----
    sents = []
    for idx, x in enumerate(items):
        for k, (tpl, raw) in enumerate(sentence_templates(x["正文"], all_names), 1):
            sents.append({"i": idx, "k": k, "tpl": tpl, "raw": raw})
    dups = []
    for a, b in itertools.combinations(range(len(sents)), 2):
        A, B = sents[a], sents[b]
        if A["i"] == B["i"]:
            continue
        if abs(len(A["tpl"]) - len(B["tpl"])) > 2:
            continue
        if tpl_rough(A["tpl"], B["tpl"]) < 0.35:      # 粗筛，避免全量算编辑距离
            continue
        sim = seq_sim(A["tpl"], B["tpl"])
        if sim >= sent_warn:
            dups.append((sim, a, b))
    dups.sort(reverse=True)
    res["同句式句对"] = [{
        "相似度": sim,
        "模板": "".join(sents[a]["tpl"]),
        "A": "%s %s 第%d句" % (items[sents[a]["i"]]["学号"], items[sents[a]["i"]]["姓名"], sents[a]["k"]),
        "A句": sents[a]["raw"],
        "B": "%s %s 第%d句" % (items[sents[b]["i"]]["学号"], items[sents[b]["i"]]["姓名"], sents[b]["k"]),
        "B句": sents[b]["raw"],
    } for sim, a, b in dups[:8]]
    res["同句式句对总数"] = len(dups)
    res["句子总数"] = len(sents)

    head = Counter(han(x["正文"])[:head_n] for x in items)
    tail = Counter(han(x["正文"])[-tail_n:] for x in items)
    res["开头撞车"] = [{"开头": k, "次数": v,
                        "涉及": [x["姓名"] for x in items if han(x["正文"])[:head_n] == k]}
                       for k, v in head.most_common() if v > 1]
    res["结尾撞车"] = [{"结尾": k, "次数": v,
                        "涉及": [x["姓名"] for x in items if han(x["正文"])[-tail_n:] == k]}
                       for k, v in tail.most_common() if v > 1]

    lab = Counter(x["标签"] for x in items if x["标签"])
    res["标签扎堆"] = [{"标签": k, "次数": v} for k, v in lab.most_common() if v > 1]
    soft = []
    for p in SOFTEN_PAT:
        c = sum(1 for x in items if p in x["正文"])
        if c > 1:
            soft.append({"表述": p, "次数": c})
    res["转译词扎堆"] = sorted(soft, key=lambda d: -d["次数"])

    allbg = Counter()
    for x in items:
        allbg.update(distinct_bigrams(x["正文"]))
    res["高频区别性词"] = [{"bigram": k, "出现评语数": v}
                       for k, v in allbg.most_common(12) if v > max(2, n * 0.08)]

    res["结论"] = []
    d = res["相似度分布"]
    if d["≥%.2f(高度雷同)的对数" % high]:
        res["结论"].append("存在 %d 对高度雷同评语，必须改写" % d["≥%.2f(高度雷同)的对数" % high])
    skd = res["骨架相似度分布"]
    if skd["≥%.2f(高度同骨架)的对数" % skel_high]:
        res["结论"].append(
            "有 %d 对评语「骨架高度重合」：抹掉学科/时间/数字/姓名后仍高度相似，"
            "属于同一个句式模子换了内容，必须换句法"
            % skd["≥%.2f(高度同骨架)的对数" % skel_high])
    if res["同句式句对总数"]:
        res["结论"].append(
            "有 %d 组句子句式完全相同或近乎相同（只换了具体事迹），是最典型的「一个味儿」，"
            "必须逐组重写句法" % res["同句式句对总数"])
    if res["结尾撞车"]:
        res["结论"].append("有 %d 组评语结尾完全相同，万能收尾句需逐一替换"
                          % len(res["结尾撞车"]))
    if res["开头撞车"]:
        res["结论"].append("有 %d 组评语开头完全相同，需打散" % len(res["开头撞车"]))
    if res["标签扎堆"]:
        res["结论"].append("标签复用 %d 处（同一标签最多用于 2 人）" % len(res["标签扎堆"]))
    if not res["结论"]:
        res["结论"].append("未发现雷同问题，通过")
    return res


def to_md(results, warn, high, skel_warn=0.18, skel_high=0.28):
    L = ["# 评语雷同度自检报告", ""]
    for r in results:
        L.append("## %s" % r["tag"])
        L.append("")
        L.append("- 人数：%d　字数：最短 %d / 最长 %d / 平均 %.1f"
                 % (r["人数"], r["字数"]["最短"], r["字数"]["最长"], r["字数"]["平均"]))
        d = r["相似度分布"]
        L.append("- 区别性相似度：平均 %.4f　≥%.2f 有 %d 对　≥%.2f 有 %d 对（共 %d 对组合）"
                 % (d["平均"], warn, d["≥%.2f(需检查)的对数" % warn],
                    high, d["≥%.2f(高度雷同)的对数" % high], d["总对数"]))
        sd = r["骨架相似度分布"]
        L.append("- 骨架相似度：平均 %.4f　≥%.2f 有 %d 对　≥%.2f 有 %d 对"
                 % (sd["平均"], skel_warn, sd["≥%.2f(同骨架)的对数" % skel_warn],
                    skel_high, sd["≥%.2f(高度同骨架)的对数" % skel_high]))
        L.append("- 同句式句对：%d 组（共 %d 个句子参与比对）"
                 % (r["同句式句对总数"], r["句子总数"]))
        L.append("- 结论：%s" % "；".join(r["结论"]))
        L.append("")
        L.append("### 最相似 5 对")
        L.append("")
        L.append("| 相似度 | 判定 | A | B |")
        L.append("|---|---|---|---|")
        for p in r["最相似对"][:5]:
            L.append("| %.4f | %s | %s | %s |" % (p["相似度"], p["判定"], p["A"], p["B"]))
        L.append("")
        if r["最相似对"]:
            t = r["最相似对"][0]
            L.append("**最相似一对原文对照**")
            L.append("")
            L.append("- %s：%s" % (t["A"], t["A正文"]))
            L.append("- %s：%s" % (t["B"], t["B正文"]))
            L.append("")
        L.append("### 骨架最相似 5 对（抹掉学科/时间/数字/姓名后再比）")
        L.append("")
        if r["骨架最相似对"]:
            L.append("| 骨架相似度 | A | B |")
            L.append("|---|---|---|")
            for p in r["骨架最相似对"][:5]:
                L.append("| %.4f | %s | %s |" % (p["相似度"], p["A"], p["B"]))
            L.append("")
            t = r["骨架最相似对"][0]
            L.append("**骨架对照（同一套槽位符：#数字　$时间　@学科　&姓名）**")
            L.append("")
            L.append("- %s：%s" % (t["A"], t["A骨架"]))
            L.append("- %s：%s" % (t["B"], t["B骨架"]))
            L.append("")
        else:
            L.append("- 无")
            L.append("")
        L.append("### 同句式句对（句式模板一致＝只换了内容）")
        L.append("")
        if r["同句式句对"]:
            L.append("| 相似度 | 模板 | A 句 | B 句 |")
            L.append("|---|---|---|---|")
            for p in r["同句式句对"][:8]:
                L.append("| %.2f | %s | %s | %s |" % (p["相似度"], p["模板"],
                                                       p["A"], p["B"]))
            L.append("")
            for p in r["同句式句对"][:3]:
                L.append("- 模板：`%s`" % p["模板"])
                L.append("  - %s：%s" % (p["A"], p["A句"]))
                L.append("  - %s：%s" % (p["B"], p["B句"]))
            L.append("")
        else:
            L.append("- 无")
            L.append("")
        L.append("### 开头撞车")
        L.append("")
        if r["开头撞车"]:
            for h in r["开头撞车"][:5]:
                L.append("- 「%s…」×%d：%s" % (h["开头"], h["次数"], "、".join(h["涉及"])))
        else:
            L.append("- 无")
        L.append("")
        L.append("### 结尾撞车")
        L.append("")
        if r["结尾撞车"]:
            for h in r["结尾撞车"][:5]:
                L.append("- 「…%s」×%d：%s" % (h["结尾"], h["次数"], "、".join(h["涉及"])))
        else:
            L.append("- 无")
        L.append("")
        L.append("### 标签扎堆")
        L.append("")
        if r["标签扎堆"]:
            for h in r["标签扎堆"][:6]:
                L.append("- 「%s」×%d" % (h["标签"], h["次数"]))
        else:
            L.append("- 无")
        L.append("")
        L.append("### 转译词扎堆（同一「待改进」说法的复用）")
        L.append("")
        if r["转译词扎堆"]:
            for h in r["转译词扎堆"][:6]:
                L.append("- 「%s」×%d" % (h["表述"], h["次数"]))
        else:
            L.append("- 无")
        L.append("")
        L.append("### 高频区别性词（值得警惕的「新套路」）")
        L.append("")
        if r["高频区别性词"]:
            L.append("　".join("%s×%d" % (h["bigram"], h["出现评语数"]) for h in r["高频区别性词"]))
        else:
            L.append("- 无")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comments", required=True, help="待检评语 JSON")
    ap.add_argument("--comments-too", default="", help="对照组评语 JSON（如模板写法基线）")
    ap.add_argument("--tag", default="本组评语")
    ap.add_argument("--tag-too", default="对照组")
    ap.add_argument("--head-n", type=int, default=6)
    ap.add_argument("--tail-n", type=int, default=8)
    ap.add_argument("--warn", type=float, default=0.24)
    ap.add_argument("--high", type=float, default=0.32)
    ap.add_argument("--skel-warn", type=float, default=0.18,
                    help="骨架相似度「同骨架」阈值（已归一槽位）")
    ap.add_argument("--skel-high", type=float, default=0.28,
                    help="骨架相似度「高度同骨架」阈值")
    ap.add_argument("--sent-warn", type=float, default=0.82,
                    help="句级句式模板相似度阈值（1.0＝模板完全相同）")
    ap.add_argument("--past", default="",
                    help="往年评语来源（roster.json 的「往年评语」，或 comments.json 样式）；"
                         "给了就额外比一遍「今年是否照搬了同一个学生的往年评语」")
    ap.add_argument("--past-warn", type=float, default=0.82,
                    help="与往年评语的句级句式模板阈值（默认沿用 --sent-warn 的 0.82）")
    ap.add_argument("--out", default="",
                    help="报告落盘路径；**留空则不落盘**，只在控制台打印结论（默认行为）")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    kw = dict(head_n=args.head_n, tail_n=args.tail_n, warn=args.warn, high=args.high,
              skel_warn=args.skel_warn, skel_high=args.skel_high, sent_warn=args.sent_warn)
    cur_items = load(args.comments)
    results = [analyze(cur_items, args.tag, **kw)]
    if args.comments_too and os.path.exists(args.comments_too):
        results.append(analyze(load(args.comments_too), args.tag_too, **kw))

    md = to_md(results, args.warn, args.high, args.skel_warn, args.skel_high)
    if len(results) == 2:
        a, b = results
        md += ("\n## 对照结论\n\n本组平均区别性相似度 %.4f，对照组 %.4f。"
               "本组骨架相似度 %.4f，对照组 %.4f。"
               "本组高度雷同对数 %d，对照组 %d。\n"
               % (a["相似度分布"]["平均"], b["相似度分布"]["平均"],
                  a["骨架相似度分布"]["平均"], b["骨架相似度分布"]["平均"],
                  a["相似度分布"]["≥%.2f(高度雷同)的对数" % args.high],
                  b["相似度分布"]["≥%.2f(高度雷同)的对数" % args.high]))

    # ---------- 与往年评语的重合（跨年照搬检测） ----------
    ov = None
    if args.past:
        if not os.path.exists(args.past):
            print("[往年评语] 文件不存在，已跳过 --past：%s" % args.past)
        else:
            ov = past_overlap(cur_items, load_past(args.past), warn=args.past_warn)
            md += ("\n## 与往年评语的重合（逐句句式比对）\n\n"
                   "覆盖 %d 人（今年这版与往年评语都有的）｜句级阈值 %.2f。\n\n"
                   % (ov["覆盖人数"], args.past_warn))
            if not ov["覆盖人数"]:
                md += "未读到往年评语（`--past` 指向的文件里没有「往年评语」字段）。\n"
            elif not ov["命中"]:
                md += "无照搬往年措辞的句子。\n"
            else:
                md += "命中 %d 人 / %d 组，须换骨架重写：\n\n" % (ov["命中人数"], ov["命中组数"])
                for h in ov["命中"][:10]:
                    md += "- **%s（%s）** 最高 %.2f，%d 组\n" % (
                        h["姓名"], h["学号"], h["最高"], h["组数"])
                    for p in h["句对"][:3]:
                        md += "  - 今年：%s\n    往年：%s\n" % (p["今年"], p["往年"])
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    for r in results:
        d = r["相似度分布"]
        sd = r["骨架相似度分布"]
        print("[%s] 区别性相似度 平均 %.4f | 高度雷同 %d 对 | 需检查 %d 对"
              % (r["tag"], d["平均"], d["≥%.2f(高度雷同)的对数" % args.high],
                 d["≥%.2f(需检查)的对数" % args.warn]))
        print("     骨架相似度   平均 %.4f | 高度同骨架 %d 对 | 同骨架 %d 对"
              % (sd["平均"], sd["≥%.2f(高度同骨架)的对数" % args.skel_high],
                 sd["≥%.2f(同骨架)的对数" % args.skel_warn]))
        print("     同句式句对 %d 组（%d 个句子参与）| 结尾撞车 %d 组 | 开头撞车 %d 组"
              % (r["同句式句对总数"], r["句子总数"],
                 len(r["结尾撞车"]), len(r["开头撞车"])))
        print("     结论：%s" % "；".join(r["结论"]))
        for p in r["同句式句对"][:3]:
            print("     ・同句式 相似度 %.2f　模板：%s" % (p["相似度"], p["模板"]))
            print("       A %s：%s" % (p["A"], p["A句"]))
            print("       B %s：%s" % (p["B"], p["B句"]))
        hf = r["高频区别性词"]
        if hf:
            print("     高频区别性词（须人工过一遍）：%s"
                  % "  ".join("%s×%d" % (h["bigram"], h["出现评语数"]) for h in hf))
        else:
            print("     高频区别性词：无（样本较小时阈值筛不出，请直接人工比对开头与结尾句式）")
    if ov is not None:
        print("[与往年评语的重合] 覆盖 %d 人｜高度重合 %d 人 / %d 组（句级阈值 %.2f）"
              % (ov["覆盖人数"], ov["命中人数"], ov["命中组数"], args.past_warn))
        if not ov["覆盖人数"]:
            print("     未读到往年评语——--past 指向的文件里没有「往年评语」字段"
                  "（roster.json 由 prepare_roster.py --past-comments 生成时才有）")
        elif not ov["命中"]:
            print("     结论：无照搬往年措辞的句子")
        else:
            for h in ov["命中"][:3]:
                print("     ・%s（%s）最高 %.2f，%d 组"
                      % (h["姓名"], h["学号"], h["最高"], h["组数"]))
                for p in h["句对"][:2]:
                    print("       今年：%s" % p["今年"])
                    print("       往年：%s" % p["往年"])
            print("     处置：这几句**换骨架**重写（不是换同义词）——"
                  "往年评语只作参考，不得照搬（详见 writing-rules 规则 5）")
    if args.out:
        print("报告已写入：%s" % os.path.abspath(args.out))
    else:
        print("（未指定 --out，报告未落盘；需要可核查的文件时再加 --out 雷同度报告.md）")


if __name__ == "__main__":
    main()
