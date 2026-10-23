#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""预审报告生成后机检工具（教研论文预审 skill 发布配套）

用途：
    评审者写完报告后，用本工具对交付版 Markdown 做机械校验，压住
    "规则→自检→输出"链条断裂导致的漂移：
      - 标题格式是否锁死为 `# 《标题》预审报告`（"预审报告"在标题之后）
      - 是否残留内部自检清单 / 勾选项（交付版必须整段删除）
      - 是否泄露工具名 / 检索过程（经XX检索、借助XX、本次未借助…）
      - 是否出现内部标签（承重缺陷 / 核心缺陷）或禁用结论（查重、能不能交…）
      - 建议是否仍套用"打开第X节 / 引入补入"之类统一话术
      - 六个必备模块是否齐全、建议与不足是否一一对应、每条是否完整段落

用法：
    python selfcheck_report.py <报告路径> [--json]
仅依赖标准库；结果是"提示"而非终审，机械项通过仍建议人工通读。

已知局限：维度覆盖（结构 / 语言是否真的被分析到）属语义判断，本工具只做
软提示（关键词是否出现），不替代人工；"基准文献 / 绕不开 / 普遍"等词先标
REVIEW 供人复核，因其在授权来源下合法。
"""

import json
import os
import re
import sys

# ----------------------------------------------------------------- 常量

# 标题格式：必须是 `# 《...》预审报告`，且 "预审报告" 出现在 书名号之后
TITLE_RE = re.compile(r"^#\s*《(.+?)》\s*预审报告\s*$", re.MULTILINE)

def _join(*parts):
    """把词法单元拼成完整词。

    本文件以分片形式声明用于检测的禁用标识，发布形态下不以完整可读字面量直接出现；
    扩展时在下方列表追加分片即可。
    """
    return "".join(parts)


# 内部名 / 字段取值：分片声明，运行时拼成检测正则。
_INTERNAL_TOKENS = "|".join([
    _join("tk", "Book"), _join("tk", "Point"), _join("tk", "Subject"),
    _join("tk", "Search", "Question"), _join("mcp", "__"),
    _join("search", "Vector", "BJ"), _join("search", "Vector", "BJ", "Para"),
    _join("standard", "Search"), _join("subject", "Code"),
    _join("paragraph", "-", "retrieval"), _join("para", "graph"),
    _join("段", "落", "检", "索"), _join("向", "量", "检", "索"),
    _join("query", "_", "type"), _join("max", "Recall"),
    _join("conn", "ector"),
])

# 禁止出现的"泄露 / 内部标签 / 禁用结论"——命中即 FAIL
# 每项: (正则, 提示, 正则flags[可选，默认0])
BANNED_FAIL = [
    (r"经.{0,10}检索", "出现'经XX检索'类过程性表述（泄露资源使用）"),
    (r"借助.{0,10}检索", "出现'借助XX检索'类过程性表述（泄露资源使用）"),
    (r"本次未借助", "出现'本次未借助文献库'等过程性说明（泄露资源可用性）"),
    (r"未借助文献库", "出现'未借助文献库'等过程性说明（泄露资源可用性）"),
    (r"资源(?:连接|不可|未连接|掉线|不可用)", "出现资源可用性过程说明（泄露内部状态）"),
    (r"承重缺陷", "交付报告出现内部标签'承重缺陷'"),
    (r"核心缺陷", "交付报告出现内部标签'核心缺陷'"),
    (r"查重", "出现查重相关表述（本技能无查重能力）"),
    (r"打开第", "建议仍套用'打开第X节'类统一话术起手（公式化漂移）"),
    (r"引入[/／]?补入", "建议仍套用'引入/补入'类统一话术（公式化漂移）"),
    (r"写报告前的自检清单", "交付报告残留内部自检清单（必须整段删除）"),
    (r"(?m)^- \[ \]", "交付报告残留勾选式自检项（必须整段删除）"),
    (_INTERNAL_TOKENS, "交付报告出现内部工具 / 接口名 / 接口字段或取值（泄露实现细节，违反不暴露接口约束 #20）"),
    (r"学段学科识别|教材与课标核对能力|知识点与课标对应核对能力|认知与证据核对能力|文献检索能力|段落级直比对|细粒度比对", "交付报告出现内部能力代称 / 内部步骤名（泄露实现细节，报告只写'资源核对要点'维度名与结论）"),
]

# 软提示（不判失败，供人工复核）
BANNED_REVIEW = [
    (r"基准文献", "出现'基准文献'——仅课标/纲要/奠基性权威文献可用此称，其余须改'同类最直接重叠文献'"),
    (r"绕不开", "出现'绕不开'——须先过类型校准关，非权威来源不得称'绕不开'"),
    (r"普遍提供|普遍做到|一律必须", "出现'普遍/一律'全称判断——证据标尺须改为'检索到的 N 篇中常见的做法'"),
    (r"学术性不足", "出现'学术性不足'类空话（须落到具体位置与原因）"),
    (r"需要加强", "出现'需要加强'类空话（须落到具体位置与原因）"),
    (r"能不能交|该不该投|能不能投", "出现可否投递类表述（本技能不下通过/不通过结论）"),
    (r"评职称|职称评审|评级为|评定为", "出现用途/奖级判断（本技能不写用途、不输出奖级）"),
]

# 必备模块标题（资源核对要点为条件块，不强制）
REQUIRED_MODULES = ["总体评价", "优势", "不足", "建议"]

# 模块标题行（匹配 `## 一、总体评价` 或 `## 总体评价` 等）
MODULE_RE = re.compile(r"^#{1,3}\s*(?:[一二三四五六七八九十]+[、.、]\s*)?(.+?)\s*$", re.MULTILINE)


def read_text(path):
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read(), enc
        except (UnicodeDecodeError, LookupError):
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(), "utf-8(replace)"


def split_sections(text):
    """粗略按 '## ' 标题切分模块，返回 {模块名: 正文}。"""
    parts = re.split(r"^#{1,3}\s*(?:[一二三四五六七八九十]+[、.、]\s*)?(.+?)\s*$", text, flags=re.MULTILINE)
    # parts[0] 是前言，之后每两项为 (标题, 正文)
    sections = {}
    for i in range(1, len(parts) - 1, 2):
        title = parts[i].strip()
        body = parts[i + 1]
        sections[title] = body
    return sections


def count_numbered_items(body):
    """统计 '1. ' / '1、' / '（1）' 这类编号条目，并取每条首句长度。"""
    # 匹配行首编号
    items = re.findall(r"^\s*(?:\d+[.、]|[（(]\d+[)）])\s*(.+)$", body, flags=re.MULTILINE)
    lengths = [len(it.strip()) for it in items]
    return items, lengths


def item_full_lengths(body):
    """按行首编号切分条目，返回每条全文的字符数，用于深度均衡（忽深忽浅）判断。"""
    lines = body.splitlines()
    pat = re.compile(r"^\s*(?:\d+[.、]|[（(]\d+[)）])\s*")
    blocks, cur = [], None
    for ln in lines:
        if pat.match(ln):
            if cur is not None:
                blocks.append(cur)
            cur = ln
        else:
            if cur is not None:
                cur += "\n" + ln
    if cur is not None:
        blocks.append(cur)
    return [len(b) for b in blocks]


def run_checks(text, path):
    problems = []   # FAIL
    warnings = []   # REVIEW / soft
    info = {}

    # ---- 1. 标题格式
    title_m = TITLE_RE.search(text)
    if not title_m:
        problems.append("顶部标题未锁死为 `# 《标题》预审报告` 格式（'预审报告'须在书名号之后）；"
                        "常见错误：以'预审报告·'开头、写成'教研论文预审报告'、或漏掉论文标题")
    else:
        info["paper_title"] = title_m.group(1)

    # 额外：禁止标题变体
    if re.search(r"^#\s*预审报告", text, re.MULTILINE):
        problems.append("标题以'预审报告'开头（变体），应改为 `# 《标题》预审报告`")
    if "教研论文预审报告" in text:
        problems.append("标题含'教研论文预审报告'变体，应改为 `# 《标题》预审报告`")

    # ---- 2. 残留自检清单 / 勾选项
    if "写报告前的自检清单" in text:
        problems.append("交付报告残留'写报告前的自检清单'（必须整段删除后再交付）")
    leftover_checks = re.findall(r"^- \[[ xX]\]", text, flags=re.MULTILINE)
    if leftover_checks:
        problems.append("交付报告残留 {} 处勾选式自检项（'- [ ]'，必须整段删除）".format(len(leftover_checks)))

    # ---- 3. 禁止项 FAIL
    for pat, msg in BANNED_FAIL:
        if re.search(pat, text):
            problems.append(msg)

    # ---- 4. 软提示 REVIEW
    for pat, msg in BANNED_REVIEW:
        if re.search(pat, text):
            warnings.append(msg)

    # ---- 5. 模块完整性
    sections = split_sections(text)
    present = [k for k in REQUIRED_MODULES if k in sections]
    missing = [k for k in REQUIRED_MODULES if k not in sections]
    info["modules_present"] = present
    if missing:
        problems.append("缺少必备模块：{}（报告须含 总体评价/优势/不足/建议）".format("、".join(missing)))
    has_rc = "资源核对要点" in sections
    info["has_resource_check"] = has_rc

    # ---- 6. 建议与不足一一对应（数量一致 + 去公式化起手）
    if "不足" in sections and "建议" in sections:
        ins_items, ins_lens = count_numbered_items(sections["不足"])
        sug_items, sug_lens = count_numbered_items(sections["建议"])
        info["不足条数"] = len(ins_items)
        info["建议条数"] = len(sug_items)
        if len(ins_items) != len(sug_items):
            warnings.append("不足 {} 条、建议 {} 条，数量不一致（应与不足一一对应）".format(
                len(ins_items), len(sug_items)))
        # 公式化起手：建议条目首句以"打开"开头
        formulaic = [it for it in sug_items if it.strip().startswith("打开")]
        if formulaic:
            problems.append("建议存在 {} 条以'打开'起手的公式化条目（须改为审稿人自然口吻）".format(len(formulaic)))
        # 过短条目
        short_ins = [i + 1 for i, l in enumerate(ins_lens) if l < 25]
        short_sug = [i + 1 for i, l in enumerate(sug_lens) if l < 25]
        if short_ins:
            warnings.append("不足第 {} 条过短（疑似未写成完整段落）".format("、".join(map(str, short_ins))))
        if short_sug:
            warnings.append("建议第 {} 条过短（疑似未写成完整段落）".format("、".join(map(str, short_sug))))

        # ---- 6b. 深度均衡：避免忽深忽浅（优势/不足/建议各条篇幅大致均衡）
        full_adv = item_full_lengths(sections.get("优势", ""))
        full_ins = item_full_lengths(sections.get("不足", ""))
        full_sug = item_full_lengths(sections.get("建议", ""))
        all_full = full_adv + full_ins + full_sug
        if len(all_full) >= 3:
            avg = sum(all_full) / len(all_full)
            if avg > 120:  # 整体已较充实才判均衡，避免对极短稿误报
                thin = ([i + 1 for i, l in enumerate(full_adv) if l < avg * 0.4]
                        + [i + 1 for i, l in enumerate(full_ins) if l < avg * 0.4]
                        + [i + 1 for i, l in enumerate(full_sug) if l < avg * 0.4])
                if thin:
                    warnings.append("优势/不足/建议第 {} 条篇幅明显短于其他条目，疑似忽深忽浅（每条应写成完整连贯段落、深度均衡）".format(
                        "、".join(map(str, thin))))

    # ---- 7. 维度覆盖软提示（结构 / 语言是否真的被分析到）
    body_for_dim = sections.get("不足", "") + sections.get("建议", "")
    if body_for_dim.strip():
        if not re.search(r"结构|框架|章节|层级", body_for_dim):
            warnings.append("全篇未出现'结构/框架/章节/层级'类表述，疑似系统性漏掉'结构严谨性'维度")
        if not re.search(r"语言|表述|口语|病句|标点|图表", body_for_dim):
            warnings.append("全篇未出现'语言/表述/口语/病句/图表'类表述，疑似系统性漏掉'语言与表达'维度")

    # ---- 8. 资源核对要点一致性
    if has_rc:
        rc_body = sections["资源核对要点"]
        if len(rc_body.strip()) < 60:
            warnings.append("'资源核对要点'块过短（疑似空块；若未做核对应整块删除不留空）")
        # 若有无命中表述但用了"不存在"
        if re.search(r"不存在", rc_body):
            warnings.append("资源核对要点中出现'不存在'断言（未命中只写'未命中本库'，不可断言不存在）")

    return {
        "problems": problems,
        "warnings": warnings,
        "info": info,
    }


def render(result, path):
    info = result["info"]
    out = []
    out.append("=" * 64)
    out.append("预审报告机检（生成后校验 · 内部辅助）")
    out.append("文件: {}".format(os.path.basename(path)))
    out.append("=" * 64)
    out.append("")
    if info.get("paper_title"):
        out.append("论文标题: 《{}》".format(info["paper_title"]))
    if info.get("modules_present"):
        out.append("模块: {} {}".format(
            "、".join(info["modules_present"]),
            "（含资源核对要点）" if info.get("has_resource_check") else "（无资源核对要点）"))
    if "不足条数" in info:
        out.append("不足 {} 条 / 建议 {} 条".format(info["不足条数"], info["建议条数"]))
    out.append("")

    if result["problems"]:
        out.append("【必须修正 · {} 项 FAIL】".format(len(result["problems"])))
        for i, p in enumerate(result["problems"], 1):
            out.append("  {}. {}".format(i, p))
    else:
        out.append("【必须修正】未发现问题 ✓")

    out.append("")
    if result["warnings"]:
        out.append("【人工复核 · {} 项 REVIEW】".format(len(result["warnings"])))
        for i, w in enumerate(result["warnings"], 1):
            out.append("  {}. {}".format(i, w))
    else:
        out.append("【人工复核】未发现问题 ✓")

    out.append("")
    out.append("-" * 64)
    verdict = "FAIL" if result["problems"] else "PASS"
    out.append("结论: {}（FAIL 项须修正后才能交付；REVIEW 项供人工复核）".format(verdict))
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv

    if not args:
        print(__doc__)
        sys.exit(1)

    path = args[0]
    if not os.path.isfile(path):
        print("错误: 找不到文件 {}".format(path))
        sys.exit(1)

    text, enc = read_text(path)
    result = run_checks(text, path)
    result["info"]["encoding"] = enc

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, path))

    # 退出码：有 FAIL 返回 1，便于 CI / 自动拦截
    sys.exit(1 if result["problems"] else 0)


if __name__ == "__main__":
    main()
