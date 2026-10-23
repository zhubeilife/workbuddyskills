#!/usr/bin/env python3
"""教研论文参考文献与体例检查工具（GB/T 7714-2015 顺序编码制）

用法:
    python check_references.py <文稿路径> [--json]

支持 .md / .txt / .docx 之外的纯文本类文稿；.docx 请先转为文本。
仅依赖标准库。检查结果是"提示"而非判定，格式细节请人工复核。

已知局限：编号识别仅支持半角方括号 [1] / [2]；全角方括号编号（如［１］）
当前不被识别，此类文稿的参考文献条目与正文引用一致性需人工核对。
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------- 常量

TYPE_LABELS = {
    "J": "期刊",
    "M": "专著",
    "C": "会议论文集",
    "D": "学位论文",
    "N": "报纸",
    "S": "标准",
    "P": "专利",
    "R": "报告",
    "EB": "电子公告",
    "DB": "数据库",
    "CP": "计算机程序",
}

REF_SECTION_TITLES = ["参考文献", "参考资料", "主要参考文献", "References", "REFERENCES"]

TYPE_PATTERN = re.compile(r"\[(EB/OL|DB/OL|CP/DK|J/OL|M/OL|[JMCDNSPR])\]")
ENTRY_PATTERN = re.compile(r"^\s*[\[【]\s*(\d+)\s*[\]】]\s*(.+?)\s*$")
# 空条目：只有编号标记、后面没有内容（如 "[1] " 或 "[1]"），说明正文引用无对应
EMPTY_ENTRY_PATTERN = re.compile(r"^\s*[\[【]\s*(\d+)\s*[\]】]\s*$")
# 未编号文献：含文献类型标识但不以 [n] 开头，疑似漏编
UNNUMBERED_PATTERN = re.compile(r"^\s*(?!\[).+?(\[(?:EB/OL|DB/OL|CP/DK|J/OL|M/OL|[JMCDNSPR])\])")
INLINE_CITE_PATTERN = re.compile(r"\[(\d+(?:\s*[-,，]\s*\d+)*)\]")


# ---------------------------------------------------------------- 读取

def read_text(path):
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb18030"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read(), enc
        except (UnicodeDecodeError, LookupError):
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(), "utf-8(replace)"


def split_reference_section(text):
    """返回 (正文, 参考文献段落文本)。找不到则返回 (text, '')。"""
    lines = text.splitlines()
    idx = None
    for i, line in enumerate(lines):
        # 归一化：去首尾空白、去 #*_、去 【】、去内部空格、去冒号
        stripped = line.strip().strip("#*_ ").strip("【】").replace(" ", "").replace("　", "")
        stripped = stripped.rstrip("：: ")
        if stripped in REF_SECTION_TITLES:
            idx = i
            break
    if idx is None:
        return text, ""
    return "\n".join(lines[:idx]), "\n".join(lines[idx + 1:])


# ---------------------------------------------------------------- 检查

def check_reference_entry(num, raw):
    """返回该条目的问题列表。"""
    issues = []
    type_match = TYPE_PATTERN.search(raw)
    if not type_match:
        issues.append("缺少文献类型标识（如 [J]/[M]/[D]/[C]/[EB/OL]）")
        return issues, None

    ref_type = type_match.group(1)
    base_type = ref_type.split("/")[0]

    head = raw[: type_match.start()]

    # 通用：主要责任者
    if not head.strip():
        issues.append("文献类型标识前缺少主要责任者（作者）")
    else:
        author_part = head.split(".")[0].strip()
        if author_part and not author_part.endswith("等") and "," not in author_part and "，" not in author_part:
            # 单一作者不报错，仅供参考
            pass

    # 年份
    if not re.search(r"(19|20)\d{2}", raw):
        issues.append("未见四位年份")

    # 中文数字年份
    if re.search(r"[〇零一二三四五六七八九]{2,}年", raw):
        issues.append("年份使用了中文数字，应改为阿拉伯数字")

    # 页码写法
    if re.search(r"第\s*\d+\s*[-–—]\s*\d+\s*页", raw):
        issues.append("页码不应写作“第 X-Y 页”，应直接写起止页码")

    if base_type == "J" or ref_type == "J/OL":
        if not re.search(r"\)\s*[:：]\s*\d", raw) and not re.search(r",\s*\d{4}\s*[,，]", raw):
            issues.append("期刊条目疑似缺少卷(期)或起止页码，规范格式：刊名, 年, 卷(期): 起止页码")
        if not re.search(r"\d+\s*[-–—]\s*\d+", raw):
            issues.append("期刊条目疑似缺少起止页码")

    elif base_type == "M":
        if not re.search(r"[:：]\s*\S+", raw):
            issues.append("专著条目疑似缺少“出版地: 出版者”")
        if not re.search(r",\s*(19|20)\d{2}", raw):
            issues.append("专著条目疑似缺少“出版者, 出版年”")

    elif base_type == "D":
        if not re.search(r"[:：]\s*\S+", raw):
            issues.append("学位论文条目疑似缺少“保存地: 保存单位”")
        if "[D]" not in raw and ref_type != "[D]":
            issues.append("学位论文标识应为 [D]")

    elif base_type == "N":
        if not re.search(r"\d{4}\s*[-–—]\s*\d{1,2}\s*[-–—]\s*\d{1,2}", raw):
            issues.append("报纸条目疑似缺少出版日期（YYYY-MM-DD）")
        if not re.search(r"\(\s*\d+\s*\)\s*$", raw):
            issues.append("报纸条目疑似缺少版次，格式：报纸名, 日期(版次)")

    elif ref_type in ("EB/OL", "DB/OL", "J/OL", "M/OL"):
        if not re.search(r"\(\s*\d{4}", raw):
            issues.append("电子文献疑似缺少发布日期，格式：(发布日期)")
        if not re.search(r"\[\s*\d{4}", raw):
            issues.append("电子文献疑似缺少引用日期，格式：[引用日期]")
        if not re.search(r"https?://|www\.", raw):
            issues.append("电子文献疑似缺少访问路径（URL）")

    elif base_type == "S":
        if not re.search(r"[A-Z]{1,4}(/T)?\s*\d{3,}", raw):
            issues.append("标准条目疑似缺少标准编号")

    if len(raw) < 12:
        issues.append("条目过短，信息可能不完整")

    # 条目内重复的编号标记（复制上一条编号带入，如 "[5] [1]董文彬…"）
    if re.match(r"^\s*[\[【]\s*\d+\s*[\]】]", raw):
        issues.append("条目内出现重复编号标记（疑似复制上一条编号带入，如“[1]作者…”），请删除多余的编号")

    return issues, ref_type


def expand_citations(cites):
    """把 '1-3,5' 展开为 {1,2,3,5}。"""
    nums = set()
    for token in cites:
        for part in re.split(r"[,，]", token):
            part = part.strip()
            if not part:
                continue
            if "-" in part or "–" in part:
                bits = re.split(r"[-–]", part)
                try:
                    a, b = int(bits[0]), int(bits[-1])
                    nums.update(range(min(a, b), max(a, b) + 1))
                except ValueError:
                    continue
            else:
                try:
                    nums.add(int(part))
                except ValueError:
                    continue
    return nums


def run_checks(text):
    body, ref_text = split_reference_section(text)
    problems = []
    warnings = []
    info = {}

    # ---- 参考文献条目
    entries = {}
    empty_entries = []
    unnumbered = []
    if ref_text.strip():
        for line in ref_text.splitlines():
            if not line.strip():
                continue
            m = ENTRY_PATTERN.match(line)
            if m:
                entries[int(m.group(1))] = m.group(2)
                continue
            me = EMPTY_ENTRY_PATTERN.match(line)
            if me:
                empty_entries.append(int(me.group(1)))
                continue
            mu = UNNUMBERED_PATTERN.match(line)
            if mu:
                unnumbered.append(line.strip())
    else:
        warnings.append("未找到“参考文献”章节标题")

    if empty_entries:
        problems.append(
            "参考文献列表中存在 {} 条空条目（编号 {} 后无内容），正文对应引用将失去落脚点，需补全".format(
                len(empty_entries), "、".join("[" + str(n) + "]" for n in sorted(empty_entries))
            )
        )
    if unnumbered:
        problems.append(
            "检出 {} 条疑似未编号的参考文献（含 [J]/[M] 等标识但未编 [n]），与正文引用无法对应，需补编号".format(
                len(unnumbered)
            )
        )

    info["reference_count"] = len(entries)

    if entries:
        numbers = sorted(entries)
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            missing = sorted(set(expected) - set(numbers))
            extra = sorted(set(numbers) - set(expected))
            msg = "参考文献编号不连续"
            if missing:
                msg += "，缺号: " + ",".join(map(str, missing))
            if extra:
                msg += "，越号: " + ",".join(map(str, extra))
            problems.append(msg)

        type_counts = {}
        for num in numbers:
            raw = entries[num]
            issues, ref_type = check_reference_entry(num, raw)
            if ref_type:
                base = ref_type.split("/")[0]
                type_counts[base] = type_counts.get(base, 0) + 1
            for issue in issues:
                problems.append("[{}] {}".format(num, issue))
        info["reference_types"] = {
            TYPE_LABELS.get(k, k): v for k, v in sorted(type_counts.items())
        }

        if len(numbers) < 5:
            warnings.append("参考文献仅 {} 条，教学研究类论文一般建议 5-15 条".format(len(numbers)))

        # 引用集中度：教材/教参类占比
        textbook_hits = sum(
            1 for raw in entries.values() if re.search(r"教材|教参|教科书|课程标准解读", raw)
        )
        if textbook_hits and textbook_hits / len(entries) > 0.4:
            warnings.append(
                "教材/教参类文献占比超过 40%（{} / {}），建议补充学术期刊文献".format(
                    textbook_hits, len(entries)
                )
            )
    else:
        problems.append("未检出任何编号参考文献条目（格式应为 “[1] 作者. 题名[J]. …”）")

    # ---- 正文引文一致性
    body_cites = set()
    for m in INLINE_CITE_PATTERN.finditer(body):
        body_cites.update(expand_citations([m.group(1)]))
    body_cites = {n for n in body_cites if n > 0}
    info["inline_citation_count"] = len(body_cites)

    if entries:
        only_body = sorted(body_cites - set(entries))
        only_ref = sorted(set(entries) - body_cites)
        if only_body:
            problems.append("正文引用了不存在的编号: " + ",".join(map(str, only_body)))
        if only_ref:
            problems.append(
                "文后下列条目在正文中未见引用（顺序编码制要求一一对应）: "
                + ",".join(map(str, only_ref))
            )
    elif body_cites:
        warnings.append("正文含上标引文标注，但未找到文后参考文献条目")

    # ---- 体例
    has_abstract = bool(re.search(r"(摘\s*要|内容摘要|Abstract)", text, re.I))
    has_keywords = bool(re.search(r"(关键词|关键字|Key\s*words?)", text, re.I))
    if not has_abstract:
        warnings.append("未检出摘要（教学研究类论文通常需要 150-300 字摘要）")
    if not has_keywords:
        warnings.append("未检出关键词（通常需要 3-5 个）")

    abstract_len = None
    am = re.search(r"(?:摘\s*要|内容摘要)[：:\s]*\n?(.{0,600}?)(?:\n\s*\n|关键词|关键字)", text, re.S)
    if am:
        abstract_len = len(re.sub(r"\s", "", am.group(1)))
        info["abstract_length"] = abstract_len
        if abstract_len < 100:
            warnings.append("摘要约 {} 字，偏短，建议 150-300 字".format(abstract_len))
        elif abstract_len > 400:
            warnings.append("摘要约 {} 字，偏长，建议压缩至 150-300 字".format(abstract_len))

    kw = re.search(r"(?:关键词|关键字)[：:\s]*(.{0,120})", text)
    if kw:
        kws = [k for k in re.split(r"[;；,，、\s]+", kw.group(1).strip()) if k]
        info["keyword_count"] = len(kws)
        if len(kws) < 3:
            warnings.append("关键词仅 {} 个，建议 3-5 个".format(len(kws)))
        elif len(kws) > 5:
            warnings.append("关键词 {} 个，偏多，建议精简至 3-5 个".format(len(kws)))
        if any(k in ("教学", "教育", "研究", "方法") for k in kws):
            warnings.append("关键词中含“教学/教育/研究”等泛词，检索区分度低，建议替换")

    # ---- 图表编号
    fig_nums = re.findall(r"图\s*(\d+)", text)
    tab_nums = re.findall(r"表\s*(\d+)", text)
    if fig_nums and len(set(fig_nums)) != len(fig_nums):
        warnings.append("图编号存在重复，请核对")
    if tab_nums and len(set(tab_nums)) != len(tab_nums):
        warnings.append("表编号存在重复，请核对")

    # ---- 字数
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    info["chinese_char_count"] = len(cjk)

    # ---- 书名号内容核对（仅提示疑似官方文件/标准，排除教科书课题名、普通书名）
    all_book_titles = re.findall(r"《[^》]{2,60}》", text)
    policy_like = re.compile(
        r"(标准|纲要|意见|通知|规划|方案|办法|决定|指南|规程|条例|规定|法律|政策|课程方案|指导纲要|20\d{2}\s*年?版)"
    )
    textbook_like = re.compile(r"(教材|课本|课|单元|乘法|除法|面积|小数|分数|认识|教学|练习|习题|教案|语文|数学|英语)")
    suspect_policies = []
    for t in set(all_book_titles):
        if policy_like.search(t) and not textbook_like.search(t):
            suspect_policies.append(t)
    if suspect_policies:
        info["policy_documents"] = sorted(suspect_policies)
        warnings.append(
            "检出 {} 处疑似官方文件/标准引用，请逐条核对名称全称、年份与是否现行有效".format(len(suspect_policies))
        )

    return {
        "problems": problems,
        "warnings": warnings,
        "info": info,
    }


# ---------------------------------------------------------------- 输出

def render(result, path):
    info = result["info"]
    out = []
    out.append("=" * 62)
    out.append("参考文献格式自查（内部辅助，结果并入报告的不足与建议）")
    out.append("文件: {}".format(os.path.basename(path)))
    out.append("=" * 62)

    out.append("")
    out.append("【基本信息】")
    out.append("  中文字数: {}".format(info.get("chinese_char_count", 0)))
    out.append("  参考文献: {} 条".format(info.get("reference_count", 0)))
    if info.get("reference_types"):
        out.append(
            "  文献类型: "
            + "  ".join("{}×{}".format(k, v) for k, v in info["reference_types"].items())
        )
    out.append("  正文引用编号: {} 个".format(info.get("inline_citation_count", 0)))
    if info.get("abstract_length"):
        out.append("  摘要字数: 约 {}".format(info["abstract_length"]))
    if info.get("keyword_count"):
        out.append("  关键词: {} 个".format(info["keyword_count"]))

    if info.get("policy_documents"):
        out.append("")
        out.append("【文献中检出的政策文件名（请逐条核对）】")
        for p in info["policy_documents"]:
            out.append("  - {}".format(p))

    out.append("")
    if result["problems"]:
        out.append("【必须修正 · {} 项】".format(len(result["problems"])))
        for i, p in enumerate(result["problems"], 1):
            out.append("  {}. {}".format(i, p))
    else:
        out.append("【必须修正】未发现问题")

    out.append("")
    if result["warnings"]:
        out.append("【建议核对 · {} 项】".format(len(result["warnings"])))
        for i, w in enumerate(result["warnings"], 1):
            out.append("  {}. {}".format(i, w))
    else:
        out.append("【建议核对】未发现问题")

    out.append("")
    out.append("-" * 62)
    out.append("说明: 只做格式自查，结果并入预审报告的不足与建议，不要单独呈现给用户。")
    out.append("      “没查到”不代表存在问题；文献真实性与相关性请结合文献库在文献核查环节另行核对。")
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
    result = run_checks(text)
    result["info"]["encoding"] = enc

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, path))


if __name__ == "__main__":
    main()
