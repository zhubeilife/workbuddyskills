#!/usr/bin/env python3
"""Build a self-contained Lingxi form analysis dashboard."""
import html
import json
import sys
from datetime import date
from pathlib import Path


def load(path, default=None):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {} if default is None else default


def esc(value):
    return html.escape(str(value or ""))


def pct(value):
    return f"{float(value):.1f}%"


def timeline_svg(items):
    if not items:
        return '<div class="empty">暂无趋势数据</div>'
    width, height = 900, 260
    left, right, top, bottom = 54, 20, 24, 42
    inner_w, inner_h = width - left - right, height - top - bottom
    maximum = max(item["count"] for item in items) or 1
    step = inner_w / max(len(items), 1)
    bar_w = min(54, step * 0.58)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="提交趋势">']
    for index in range(5):
        value = maximum * index / 4
        y = top + inner_h * (1 - value / maximum)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="axis">{value:.0f}</text>')
    for index, item in enumerate(items):
        x = left + step * (index + 0.5)
        bar_h = inner_h * item["count"] / maximum
        y = top + inner_h - bar_h
        parts.append(f'<rect x="{x-bar_w/2:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" fill="#2563eb"/>')
        parts.append(f'<text x="{x:.1f}" y="{max(y-7, 14):.1f}" text-anchor="middle" class="value">{item["count"]}</text>')
        parts.append(f'<text x="{x:.1f}" y="{height-14}" text-anchor="middle" class="axis">{esc(item["period"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def option_bars(options):
    if not options:
        return '<div class="empty">暂无可统计选项</div>'
    maximum = max(item["count"] for item in options) or 1
    rows = []
    for item in options:
        width = item["count"] / maximum * 100
        rows.append(
            '<div class="bar-row">'
            f'<div class="bar-label" title="{esc(item["label"])}">{esc(item["label"])}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%"></div></div>'
            f'<div class="bar-value">{item["count"]} · {pct(item["share"])}</div>'
            '</div>'
        )
    return "".join(rows)


def list_items(items, empty_text):
    if not items:
        return f'<div class="empty">{esc(empty_text)}</div>'
    return '<ul class="clean-list">' + "".join(f'<li>{esc(item)}</li>' for item in items) + '</ul>'


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_dashboard.py <data-dir> <output-html>")
    data_dir = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    analysis = load(data_dir / "analysis.json")
    insights = load(data_dir / "insights.json", {})
    if analysis.get("privacy", {}).get("data_masked") is not True:
        raise SystemExit("Refusing to build a shareable dashboard from unmasked data")

    form = analysis.get("form") or {}
    overview = analysis.get("overview") or {}
    distributions = analysis.get("field_distributions") or []
    open_text = analysis.get("open_text_fields") or []
    field_sections = []
    for field in distributions:
        field_sections.append(
            '<section class="field-card">'
            f'<div class="field-head"><div><h3>{esc(field["name"])}</h3><span>{field["answered_count"]} 人作答 · {field["blank_count"]} 人未填</span></div></div>'
            f'{option_bars(field.get("options") or [])}'
            '</section>'
        )
    open_rows = "".join(
        f'<tr><td>{esc(item["name"])}</td><td>{item["answered_count"]}</td><td>{item["blank_count"]}</td><td>{item["average_length"]}</td></tr>'
        for item in open_text
    ) or '<tr><td colspan="4" class="empty">暂无开放题</td></tr>'

    themes = insights.get("themes") or []
    theme_cards = "".join(
        '<div class="theme">'
        f'<div class="theme-count">{int(item.get("count", 0))}</div>'
        f'<div><h4>{esc(item.get("name"))}</h4><p>{esc(item.get("description"))}</p></div>'
        '</div>'
        for item in themes
    ) or '<div class="empty">未提供开放题主题归纳</div>'

    document = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(form.get("title") or "表单")} · 表单数据分析看板</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f6f8;color:#172033;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;letter-spacing:0}}.shell{{max-width:1180px;margin:0 auto;padding:28px 24px 56px}}header{{background:#172033;color:#fff;padding:30px;border-radius:8px}}header .eyebrow{{color:#93c5fd;font-size:13px;font-weight:700}}h1{{font-size:30px;margin:8px 0 10px}}header p{{margin:0;color:#cbd5e1;line-height:1.7}}.privacy{{display:inline-block;margin-top:16px;padding:6px 10px;border:1px solid #475569;border-radius:4px;color:#dbeafe;font-size:12px}}.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}}.kpi,.panel,.field-card{{background:#fff;border:1px solid #e2e8f0;border-radius:8px}}.kpi{{padding:18px}}.kpi span{{font-size:13px;color:#64748b}}.kpi strong{{display:block;font-size:26px;margin:7px 0;color:#0f172a}}.kpi small{{color:#94a3b8}}.panel{{padding:22px;margin-top:16px}}.panel h2{{font-size:19px;margin:0 0 16px}}.panel-note{{color:#64748b;font-size:13px;margin:-8px 0 18px}}svg{{width:100%;height:auto;font-family:inherit}}svg .axis{{font-size:11px;fill:#64748b}}svg .value{{font-size:11px;fill:#172033;font-weight:700}}.field-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}.field-card{{padding:18px}}.field-head h3{{font-size:16px;margin:0 0 4px}}.field-head span{{font-size:12px;color:#64748b}}.bar-row{{display:grid;grid-template-columns:110px 1fr 90px;align-items:center;gap:10px;margin-top:14px}}.bar-label{{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.bar-track{{height:10px;background:#e8eef7;border-radius:3px;overflow:hidden}}.bar-fill{{height:100%;background:#2563eb}}.bar-value{{font-size:12px;color:#475569;text-align:right}}table{{width:100%;border-collapse:collapse}}th,td{{padding:11px 10px;border-bottom:1px solid #e2e8f0;text-align:left;font-size:13px}}th{{color:#64748b;font-weight:600;background:#f8fafc}}.insight-summary{{font-size:17px;line-height:1.75;padding:16px;background:#eff6ff;border-left:4px solid #2563eb}}.theme-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:16px 0}}.theme{{display:flex;gap:13px;padding:14px;border:1px solid #e2e8f0;border-radius:6px}}.theme-count{{width:42px;height:42px;display:grid;place-items:center;background:#172033;color:#fff;border-radius:4px;font-weight:700}}.theme h4{{margin:0 0 5px;font-size:14px}}.theme p{{margin:0;color:#64748b;font-size:13px;line-height:1.6}}.clean-list{{margin:0;padding-left:20px}}.clean-list li{{margin:9px 0;line-height:1.65}}.empty{{padding:18px;color:#94a3b8;text-align:center}}footer{{color:#64748b;font-size:12px;line-height:1.7;margin-top:18px}}@media(max-width:760px){{.shell{{padding:14px}}header{{padding:22px}}h1{{font-size:24px}}.kpis{{grid-template-columns:repeat(2,1fr)}}.field-grid,.theme-grid{{grid-template-columns:1fr}}.bar-row{{grid-template-columns:88px 1fr 76px}}}}
</style>
</head>
<body><main class="shell">
<header><div class="eyebrow">LINGXI FORM INSIGHT</div><h1>{esc(form.get("title") or "表单数据分析看板")}</h1><p>表单数据分析看板 · 生成日期 {date.today().isoformat()}</p><div class="privacy">数据已脱敏 · 看板不包含个人提交明细</div></header>
<div class="kpis">
<div class="kpi"><span>提交总量</span><strong>{overview.get("submission_count",0)}</strong><small>当前分析范围</small></div>
<div class="kpi"><span>已备注记录</span><strong>{overview.get("remarked_count",0)}</strong><small>占比 {pct(overview.get("remarked_rate",0))}</small></div>
<div class="kpi"><span>待处理记录</span><strong>{overview.get("unremarked_count",0)}</strong><small>以是否存在备注判断</small></div>
<div class="kpi"><span>覆盖月份</span><strong>{len(analysis.get("timeline") or [])}</strong><small>{esc(overview.get("first_submit_time",""))[:10]} 至 {esc(overview.get("last_submit_time",""))[:10]}</small></div>
</div>
<section class="panel"><h2>提交趋势</h2><div class="panel-note">按提交月份统计</div>{timeline_svg(analysis.get("timeline") or [])}</section>
<section class="panel"><h2>字段分布</h2><div class="panel-note">仅展示非敏感、适合聚合统计的字段</div><div class="field-grid">{''.join(field_sections) or '<div class="empty">暂无可统计字段</div>'}</div></section>
<section class="panel"><h2>开放题完成情况</h2><div class="panel-note">只统计作答数量和平均长度，不展示个人原文</div><table><thead><tr><th>字段</th><th>作答</th><th>未填</th><th>平均字数</th></tr></thead><tbody>{open_rows}</tbody></table></section>
<section class="panel"><h2>AI 洞察与建议</h2><div class="insight-summary">{esc(insights.get("summary") or "尚未生成 AI 总结。")}</div><div class="theme-grid">{theme_cards}</div><h3>建议</h3>{list_items(insights.get("recommendations") or [], "暂无建议")}</section>
<footer>统计结果来自灵析 MCP 返回的脱敏数据。备注处理率仅表示记录是否存在备注，不等同于业务流程已经完成。HTML 为自包含文件，可离线打开和直接转发。</footer>
</main></body></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print("OK ->", output)


if __name__ == "__main__":
    main()
