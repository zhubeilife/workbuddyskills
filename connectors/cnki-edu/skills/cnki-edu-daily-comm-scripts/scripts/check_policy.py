# -*- coding: utf-8 -*-
"""
政策数据来源校验器（cnki-edu-daily-comm-scripts）

用途
----
扫描发言稿 / 话术文本，找出「涉及政策、但未标明来源」的句子，强制：
    政策数据只能来自「用户提供」或「官方文件」，
    不得凭记忆写出具体数值 / 年份 / 条款。

判定口径（三层，逐句扫描）
--------------------------------------------------
1. 政策句判定：句中出现政策关键词（双减 / 教育部 / 中考 / 高考 / 选科 /
   指标到校 / 综合素质评价 / 课标 / 招生 / 收费 ……）。
2. 风险判定：政策句中出现下列任一情况，即为「需有据」——
     · 含具体数值 + 量词（60 分钟 / 90 分 / 3+1+2 / 2021 年 / 30% …）
     · 含规定性动词（要求 / 规定 / 明确 / 必须 / 不得 / 严禁 …）
3. 来源判定：同句或前一句若出现来源标记（《文件名》/ 〔2021〕1 号 /
   教育部 / 教育厅 / 学校通知 / 以…为准 …）或占位标记（〔政策待核〕/
   <待核：…> / 待核实 …），则视为已落实；否则报错。

用法
----
  python check_policy.py <文本文件> [--json] [--quiet]
  文本文件可为 .txt / .md，也可直接传 .docx（自动抽取正文）。

注意
----
  本脚本用于校验**生成出来的稿件 / 话术**，不是用来校验本 skill 自身的规则文件
  （如 `redlines.md` 的反例列会"命中"——那是规则说明，不是稿件内容，属正常）。

输出
----
  逐条列出「缺来源」的句子 + 命中原因；退出码 0=通过, 1=有缺来源, 2=用法错误。
"""

import argparse
import json
import os
import re
import sys

# --------------------------------------------------------------------------
# 政策关键词
# --------------------------------------------------------------------------
POLICY_TERMS = (
    "政策", "双减", "教育部", "教育厅", "教育局", "国务院", "省政府", "市政府",
    "课标", "课程标准", "中考", "高考", "新高考", "选科", "选考", "合格考",
    "综合素质评价", "指标到校", "名额分配", "强基计划", "综合评价招生",
    "艺考", "体育单招", "自主招生", "加分", "招生", "升学政策", "录取",
    "收费", "代收", "教辅", "教材征订", "作业总量", "作业时长", "考试管理",
    "作业管理", "成绩公布", "公布排名", "手机管理", "带入课堂", "纸笔考试",
    "课后服务", "五项管理", "睡眠管理", "体质健康", "近视防控",
    "入学", "学籍", "随迁子女",
)

# 政策关键词（正则版）：处理「中考」被「期中考试 / 期末考试」误命中的问题
POLICY_RE = re.compile(
    r"(?:政策|双减|教育部|教育厅|教育局|国务院|省政府|市政府"
    r"|课标|课程标准|(?<![期末])中考|高考|新高考|选科|选考|合格考"
    r"|综合素质评价|指标到校|名额分配|强基计划|综合评价招生"
    r"|艺考|体育单招|自主招生|加分|招生|升学政策|录取"
    r"|收费|代收|教辅|教材征订|作业总量|作业时长|考试管理|作业管理"
    r"|成绩公布|公布排名|手机管理|带入课堂|纸笔考试|课后服务|五项管理"
    r"|睡眠管理|体质健康|近视防控|入学|学籍|随迁子女)"
)

# 政策语境措辞（即使未出现上面关键词，也视为政策语境）
POLICY_CTX = re.compile(
    r"明确规定|政策要求|政策规定|有关要求|上级要求|统一要求|相关规定|国家规定"
    r"|明文规定|按.{0,8}(?:要求|规定)|据.{0,8}(?:要求|规定)"
)

# 政策数值：数字 + 量词
NUM_UNIT = re.compile(
    r"\d+(?:\.\d+)?\s*(?:分钟|小时|课时|课时数|分|%|％|个百分点|次|天|周|个月|年(?!级)|月|日"
    r"|门|科|元|万元|人|名|个|遍|页|万字|小时)"
)

# 3+1+2 / 3+3 这类模式串
MODE_PAT = re.compile(r"[1-3]\+[1-3](?:\+[1-3])?")

# 规定性动词（否定前置排除：「不要求 / 没规定」不算政策要求）
REQUIRE_VERB = re.compile(
    r"(?<![不没未无])(?:要求|规定|明确|统一要求|必须|不得|禁止|严禁|允许|应当|原则上"
    r"|不进行|不组织|取消|不得超过|不公布)"
)

# 来源标记：只认「可查证的来源」——文件名 / 文号 / 学校通知·学校规定 / 以…为准。
# 注意：单独的「教育部 / 教育厅」等机构名不算来源（它只是政策主体，不是文件），
#       必须有具体文件或明确指向才算落实。
SOURCE_MARKERS = re.compile(
    r"(《[^》]{2,80}》"
    r"|〔\d{4}〕\s*\d+\s*号|【\d{4}】\s*\d+\s*号|\[\d{4}\]\s*\d+\s*号|第\s*\d+\s*号"
    r"|学校通知|校通知|学校规定|校规|上级规定|上级文件|官方文件|正式文件|红头文件"
    r"|相关文件|有关部门.{0,6}文件"
    r"|以[^，。；]{0,16}?为准)"
)

# 占位标记：已标注待核，视为已落实（提示而非报错）
PLACEHOLDER = re.compile(
    r"(<待核[^>]*>|〔政策待核[^〕]*〕|\[政策待核[^\]]*\]|待核实|待考证|待确认|请补充|需核实"
    r"|以最新官方口径为准|以官方口径为准|以最新政策为准)"
)

SENT_SPLIT = re.compile(r"[。！？；\n\r]+")


def load_text(path):
    """读入文本；.docx 自动抽取正文。"""
    if path.lower().endswith(".docx"):
        import zipfile

        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"</w:tr>", "\n", xml)
        return re.sub(r"<[^>]+>", "", xml)
    with open(path, encoding="utf-8") as f:
        return f.read()


def scan(text):
    """返回命中列表：每条含 句子 / 原因 / 命中片段。"""
    # 按句切分（保留片段顺序，便于定位）
    sentences = [s.strip() for s in SENT_SPLIT.split(text)]
    sentences = [s for s in sentences if s]
    hits = []

    for i, s in enumerate(sentences):
        is_policy = bool(POLICY_RE.search(s)) or bool(POLICY_CTX.search(s))
        if not is_policy:
            continue

        has_num = bool(NUM_UNIT.search(s)) or bool(MODE_PAT.search(s))
        has_verb = bool(REQUIRE_VERB.search(s))
        if not (has_num or has_verb):
            continue

        # 降噪：仅因规定性动词命中、且无政策数值时，要求动词与政策关键词相邻（≤15 字），
        #       否则视为"顺带提到"而非政策主张。（由 POLICY_CTX 触发的句子不受此限）
        if has_verb and not has_num:
            pm = POLICY_RE.search(s)
            vm = REQUIRE_VERB.search(s)
            if pm and vm and abs(vm.start() - pm.start()) > 15:
                continue

        # 上下文窗口：占位标记常被句号/问号切到相邻片段（如「E1：为什么不公布排名？」+ 下一行标注），
        # 故占位检查向后多看 2 句；来源只认本句与前一句，避免被后文"以…为准"掩盖。
        prev = sentences[i - 1] if i > 0 else ""
        nxt = sentences[i + 1] if i + 1 < len(sentences) else ""
        nxt2 = sentences[i + 2] if i + 2 < len(sentences) else ""

        # 已标占位 → 跳过（视为已落实）
        if PLACEHOLDER.search(prev + "｜" + s + "｜" + nxt + "｜" + nxt2):
            continue

        # 来源：本句或前一句
        src_win = prev + "｜" + s
        if SOURCE_MARKERS.search(src_win):
            continue

        reason = []
        if has_num:
            m = NUM_UNIT.search(s) or MODE_PAT.search(s)
            reason.append("含政策数值「%s」" % (m.group(0).strip() if m else "?"))
        if has_verb:
            m = REQUIRE_VERB.search(s)
            reason.append("含规定性表述「%s」" % m.group(0))
        hits.append({
            "index": i + 1,
            "sentence": s,
            "reason": "、".join(reason),
            "has_source": False,
        })

    return hits


def main():
    ap = argparse.ArgumentParser(
        description="政策数据来源校验器：政策数据须来自用户 / 官方文件。"
    )
    ap.add_argument("text_file", help="待检查的文本文件（.txt/.md/.docx）")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出")
    ap.add_argument("--quiet", action="store_true", help="只输出结论行")
    args = ap.parse_args()

    if not os.path.exists(args.text_file):
        print(json.dumps({"error": "文件不存在: %s" % args.text_file},
                         ensure_ascii=False))
        return 2

    text = load_text(args.text_file)
    hits = scan(text)

    if args.json:
        print(json.dumps({"total": len(hits), "hits": hits}, ensure_ascii=False))
        return 1 if hits else 0

    if not args.quiet:
        print("=" * 66)
        print("政策数据来源校验（政策数据须来自用户 / 官方文件）")
        print("=" * 66)

    if not hits:
        print("[通过] 未发现「涉及政策但缺来源」的句子。")
        return 0

    print("[未通过] 发现 %d 处政策表述缺来源：" % len(hits))
    for h in hits:
        print("  · 第 %d 句：%s" % (h["index"], h["sentence"][:78]))
        print("        原因：%s" % h["reason"])
        print("        修法：补「依据（文件名/文号/发布机构）」；"
              "若无官方来源，改写为占位符 <待核：…> 或加「〔政策待核〕」并列入【待补信息】。")
    print("-" * 66)
    print("提示：政策数值 / 年份 / 条款只能来自【用户提供】或【官方文件】，"
          "不得凭记忆写入。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
