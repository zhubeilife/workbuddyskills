#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 组卷 · 双向细目表渲染器

用法：
    python3 render_blueprint.py <blueprint.json> [-o <out.html>]

输出两份表：
 1) 「内容 × 认知层次」双向细目表（分值分布 + 合计 + 占比）
 2) 「题号 × 分值 × 知识点 × 认知层次 × 难度档」逐题对照表

输入 JSON 结构见 references/example_blueprint.json。
"""
import os, sys, json, html, argparse

LEVELS_DEFAULT = ["了解", "理解", "掌握", "运用"]

CSS = """
@page { size: A4; margin: 2.0cm 1.8cm; }
body { font-family: "宋体", SimSun, "Times New Roman", serif; font-size: 10.5pt;
       line-height: 1.5; color: #000; margin: 0; background: #fff; }
.wrap { max-width: 900px; margin: 0 auto; padding: 24px 26px; }
.title { font-size: 15pt; font-weight: bold; text-align: center; margin: 0 0 4pt; }
.meta { text-align: center; font-size: 10.5pt; margin: 0 0 14pt; }
h2 { font-size: 11pt; margin: 16pt 0 6pt; }
table { border-collapse: collapse; width: 100%; font-size: 10.5pt; }
th, td { border: 1px solid #333; padding: 4pt 6pt; text-align: center; }
th { background: #f0f0f0; font-weight: bold; }
td.left { text-align: left; }
tr.total td, tr.total th { font-weight: bold; background: #fafafa; }
tr.mod td { background: #f7f7f7; }
tr.mod td.modname { font-weight: bold; }
.note { font-size: 9.5pt; color: #444; margin-top: 14pt; line-height: 1.6; }
"""


def render_table1(levels, modules):
    col_w = max(10, 70 // (len(levels) + 2))
    head = (f'<tr><th style="width:16%">知识模块</th>'
            f'<th style="width:30%">知识点</th>'
            + "".join(f'<th>{html.escape(l)}</th>' for l in levels)
            + f'<th style="width:10%">小计</th></tr>')
    rows = []
    for m in modules:
        pts = m["points"]
        for i, p in enumerate(pts):
            scores = p.get("scores", {})
            cells = "".join(f'<td>{scores.get(l, 0)}</td>' for l in levels)
            sub = sum(scores.get(l, 0) for l in levels)
            modname = m["name"] if i == 0 else ""
            # ⚠️ 交付物红线：细目表**不渲染**题库内部考点名（接口元数据字段值）。
            #    `p.get("lib")` 仍保留在 blueprint.json 中留档复核，只在此处不输出。
            name_cell = html.escape(p["name"])
            rows.append(f'<tr class="mod"><td class="left modname">{html.escape(modname)}</td>'
                        f'<td class="left">{name_cell}</td>{cells}<td>{sub}</td></tr>')
    tot = {l: sum(p.get("scores", {}).get(l, 0) for m in modules for p in m["points"]) for l in levels}
    grand = sum(tot.values()) or 1
    rows.append('<tr class="total"><td class="left">合计</td><td class="left">——</td>'
                + "".join(f'<td>{tot[l]}</td>' for l in levels)
                + f'<td>{sum(tot.values())}</td></tr>')
    rows.append('<tr class="total"><td class="left">占比</td><td class="left">——</td>'
                + "".join(f'<td>{tot[l] / grand * 100:.1f}%</td>' for l in levels)
                + '<td>100%</td></tr>')
    return "<table>" + head + "".join(rows) + "</table>", tot


def render_table2(per_question):
    head = ('<tr><th>题号</th><th>题型</th><th>分值</th><th>知识模块</th>'
            '<th>细目表知识点</th><th>认知层次</th><th>难度档</th></tr>')
    rows = []
    for q in per_question:
        note = f' <span title="{html.escape(q["note"])}">▲</span>' if q.get("note") else ""
        rows.append(
            f'<tr><td>{q["no"]}</td><td>{html.escape(str(q.get("type", "")))}</td>'
            f'<td>{q.get("score", "")}</td>'
            f'<td class="left">{html.escape(q.get("module", ""))}</td>'
            f'<td class="left">{html.escape(q.get("point", ""))}</td>'
            f'<td>{html.escape(q.get("level", ""))}</td>'
            f'<td>{html.escape(q.get("difficulty", ""))}{note}</td></tr>')
    return "<table>" + head + "".join(rows) + "</table>"


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 双向细目表渲染器")
    ap.add_argument("input", help="细目表 JSON 路径")
    ap.add_argument("-o", "--output", help="输出 HTML 路径（默认同目录同名 .html）")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        cfg = json.load(f)

    levels = cfg.get("levels", LEVELS_DEFAULT)
    t1, tot = render_table1(levels, cfg["modules"])
    t2 = render_table2(cfg.get("per_question", []))
    dist = " · ".join(f'{l} {tot[l]}' for l in levels)
    total = sum(tot.values())

    body = f"""<div class="wrap">
  <div class="title">{html.escape(cfg["title"])}<br />双向细目表（命题蓝图）</div>
  <div class="meta">{html.escape(cfg.get("meta", ""))} | 认知层次分布 {dist} | 合计 {total} 分</div>
  <h2>一、内容 × 认知层次 双向细目表（分值分布）</h2>
  {t1}
  <h2>二、题号 × 分值 × 知识点 × 认知层次 逐题对照</h2>
  {t2}
  {f'<div class="note">{html.escape(cfg["note"])}</div>' if cfg.get("note") else ''}
</div>"""

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8" /><title>{html.escape(cfg["title"])} · 双向细目表</title>
<style>{CSS}</style></head>
<body>
{body}
</body>
</html>
"""
    out_path = args.output or os.path.splitext(os.path.abspath(args.input))[0] + ".html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"[render_blueprint] 已生成: {out_path}  ({len(doc)} chars, 合计 {total} 分)")


if __name__ == "__main__":
    main()
