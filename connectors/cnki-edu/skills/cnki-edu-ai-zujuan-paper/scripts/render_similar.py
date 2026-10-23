#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 组卷 · 「题找题·相似题巩固」分组卷渲染器

用法：
    python3 render_similar.py <groups.json> -o <out.html> [--part both|paper|analysis]

适用场景（场景 g）：用户给出 1~N 道试题的原题文本/图片，要求"巩固/专项练习"，
而非按知识点组卷。产物为「原题 + 相似练习」的分组卷，**不含双向细目表**。

⚠️ **产物为两份独立文件（用户硬性要求）**：试卷 docx（不含解析）+ 解析 docx。
   用 `--part paper` / `--part analysis` 分别产出两个 HTML，再各自转 docx。
   `--part both`（合卷）仅为兼容旧用法保留，**默认交付不用**。

结构：
    试卷区：  一、第 1 组 → 【原题】… / 【相似练习 1】… / 【相似练习 2】…
    解析区：  每组逐题给 【考点】【分析】【解答】（独立成篇，不再需要卷内分页）

排版沿用《试卷与解析排版标准 v1.2》（与 render_paper.py 同一套硬约束：
选项无边框表格绝不折行、页边距转换时显式传参、字号钉在元素上、小问分行）。

输入 JSON 结构：
{
  "title": "...", "meta": "...", "exam_info": false,
  "groups": [{
      "no": 1, "note": "可选组说明",
      "items": [
        {"role": "原题", "score": 10,
         "kind": "解答", "stem": "...", "figs": [], "opts": [],
         "points": "...", "analyse": "...", "method": "...", "answer": "...", "afigs": []}
      ]}]
}
"""
import os, sys, json, html, re, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_paper import (  # noqa: E402
    opts_block, fix_blanks, split_subq, fig, CSS as BASE_CSS,
    clean_body, _render_q_body, _is_subq_kind,
)

CN = "一二三四五六七八九十"

EXTRA_CSS = """
.role { font-weight: bold; }
.q .role, .ana-q .role { margin-right: 2pt; }
.grp-title { font-size: 12pt; font-weight: bold; margin: 16pt 0 8pt; line-height: 1.5; }
.grp-note { font-size: 10.5pt; color: #000000; margin: -4pt 0 6pt; line-height: 1.5; }
"""


def cn_no(n):
    return CN[n - 1] if 1 <= n <= len(CN) else str(n)


def _lead(it):
    """题干前缀：角色标签（加粗）+ 分值。

    ⚠️ 交付物红线：**不渲染题源标注**（接口 `Label`/`SourceReports` 属题库元数据字段值），
    即便上游条目带了 `label` 也不输出。"""
    role = it.get("role") or ""
    s = f'<b class="role">【{html.escape(role)}】</b>' if role else ""
    if it.get("score"):
        s += f'（{it["score"]}分）'
    return s


def _qdict(it):
    """把「相似题条目」映射成 render_paper._render_q_body 需要的题目结构。

    复用链路 A 的题干清洗与排版管线（clean_body → MathJye 线性化 / 去 <del> 高亮 /
    去 substruct-mark / 去题图 float → 解答题图重排到「叙述与首个小问之间」→ 小问分行），
    使两条链路的版式完全一致。
    """
    return {
        "stem": it.get("stem") or "",
        "kind": it.get("kind") or "解答",
        "figs": it.get("figs") or [],
        "opts": it.get("opts") or [],
    }


def render_paper(cfg):
    out = ['<div class="wrap">']
    out.append(f'<div class="title">{html.escape(cfg["title"])}</div>')
    if cfg.get("meta"):
        out.append(f'<div class="meta">{html.escape(cfg["meta"])}</div>')
    if cfg.get("exam_info", False):
        out.append('<div class="exam-info"><span>班级：__________</span>'
                   '<span>姓名：__________</span><span>日期：__________</span></div>')
    for g in cfg["groups"]:
        out.append(f'<div class="grp-title">{cn_no(g["no"])}、第 {g["no"]} 组</div>')
        if g.get("note"):
            out.append(f'<div class="grp-note">{g["note"]}</div>')
        for it in g["items"]:
            out += _render_q_body(_qdict(it), "q", _lead(it))
    out.append('</div>')
    return "\n".join(out)


def render_analysis(cfg):
    out = ['<div class="wrap ana-sec">']
    out.append(f'<div class="ana-title">{html.escape(cfg["title"])}<br />参考答案与试题解析</div>')
    for g in cfg["groups"]:
        out.append(f'<div class="grp-title">{cn_no(g["no"])}、第 {g["no"]} 组</div>')
        for it in g["items"]:
            q = _qdict(it)
            out += _render_q_body(q, "ana-q", _lead(it))
            if it.get("points"):
                out.append(f'<div class="ana-p"><span class="lab">【考点】</span>'
                           f'{it["points"]}</div>')
            if it.get("analyse"):
                out.append(f'<div class="ana-p"><span class="lab">【分析】</span>'
                           f'{clean_body(it["analyse"])}</div>')
            if it.get("method"):
                meth = clean_body(it["method"])
                meth = split_subq(meth) if _is_subq_kind(q["kind"]) else meth
                # 「解：」去重：题库 Method 常自带"解："，避免出现"解：解："
                m = re.match(r'^\s*解\s*[:：]\s*', meth)
                if m:
                    meth = meth[m.end():]
                out.append(f'<div class="ana-p"><span class="lab">【解答】</span>解：{meth}</div>')
            for f in it.get("afigs") or []:
                out.append(f'<div class="fig">{fig(f)}</div>')
            if it.get("answer"):
                out.append(f'<div class="ana-p ansline">{clean_body(it["answer"])}</div>')
    out.append('</div>')
    return "\n".join(out)


def build(cfg, part="both"):
    if part == "paper":
        body = render_paper(cfg)
    elif part == "analysis":
        body = render_analysis(cfg)
    else:
        body = render_paper(cfg) + "\n" + render_analysis(cfg)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>{html.escape(cfg["title"])}</title>
<style>{BASE_CSS}{EXTRA_CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 题找题·相似题巩固 分组卷渲染器")
    ap.add_argument("input", help="分组题目 JSON 文件路径")
    ap.add_argument("-o", "--output", help="输出 HTML 路径（默认与输入同目录同名 .html）")
    ap.add_argument("--part", choices=["both", "paper", "analysis"], default="both",
                    help="渲染哪一部分：paper=仅试卷（默认交付，第一份 docx）｜"
                         "analysis=仅解析（第二份 docx）｜both=合卷（兼容旧用法，默认不交付）")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        cfg = json.load(f)

    out_path = args.output or os.path.splitext(os.path.abspath(args.input))[0] + ".html"
    doc = build(cfg, args.part)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    n = sum(len(g["items"]) for g in cfg["groups"])
    print(f"[render_similar] 已生成({args.part}): {out_path}  ({len(doc)} chars, {len(cfg['groups'])} 组 / {n} 题)")


if __name__ == "__main__":
    main()
