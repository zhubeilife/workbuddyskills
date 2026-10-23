#!/usr/bin/env python3
"""Build a self-contained Lingxi activity analysis dashboard."""
import html
import json
import sys
from datetime import date
from pathlib import Path


SOURCE_NAMES = {
    "client": "用户报名",
    "admin": "管理员录入",
    "import": "批量导入",
    "scan_qrcode": "扫码签到",
    "mobile": "移动端签到",
    "signup": "报名联动",
    "unknown": "其他",
}


def load(path, default=None):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {} if default is None else default


def esc(value):
    return html.escape(str(value or ""))


def money(value):
    return f"¥{float(value or 0):,.2f}"


def percent(value):
    return f"{float(value or 0):.1f}%"


def bar_chart(items, label_key, color="#0f766e"):
    if not items:
        return '<div class="empty">暂无数据</div>'
    maximum = max(item.get("count", 0) for item in items) or 1
    rows = []
    for item in items:
        label = SOURCE_NAMES.get(str(item.get(label_key)), str(item.get(label_key) or "未知"))
        count = int(item.get("count") or 0)
        width = count / maximum * 100
        rows.append(
            '<div class="bar-row">'
            f'<div class="bar-label">{esc(label)}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%;background:{color}"></div></div>'
            f'<div class="bar-value">{count}</div>'
            '</div>'
        )
    return "".join(rows)


def timeline_svg(items, color="#0f766e"):
    if not items:
        return '<div class="empty">暂无趋势数据</div>'
    width, height = 900, 250
    left, right, top, bottom = 52, 18, 22, 48
    inner_w, inner_h = width - left - right, height - top - bottom
    maximum = max(item["count"] for item in items) or 1
    step = inner_w / max(len(items), 1)
    bar_w = min(44, step * 0.6)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img">']
    for index in range(5):
        value = maximum * index / 4
        y = top + inner_h * (1 - value / maximum)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        parts.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" class="axis">{value:.0f}</text>')
    for index, item in enumerate(items):
        x = left + step * (index + 0.5)
        bar_h = inner_h * item["count"] / maximum
        y = top + inner_h - bar_h
        label = str(item["period"])[5:] if len(str(item["period"])) >= 10 else str(item["period"])
        parts.append(f'<rect x="{x-bar_w/2:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="3" fill="{color}"/>')
        parts.append(f'<text x="{x:.1f}" y="{max(y-7, 14):.1f}" text-anchor="middle" class="value">{item["count"]}</text>')
        parts.append(f'<text x="{x:.1f}" y="{height-16}" text-anchor="middle" class="axis">{esc(label)}</text>')
    parts.append("</svg>")
    return "".join(parts)


def bullet_list(items, empty_text):
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

    activity = analysis.get("activity") or {}
    overview = analysis.get("overview") or {}
    payment = analysis.get("payment") or {}
    sessions = analysis.get("sessions") or []
    tickets = analysis.get("tickets") or []

    session_rows = "".join(
        '<tr>'
        f'<td>{esc(item.get("name"))}</td><td>{int(item.get("signed_in_people_count") or 0)}</td>'
        f'<td>{int(item.get("signin_count") or 0)}</td><td>{percent(item.get("signin_rate"))}</td>'
        f'<td>{int(item.get("signout_count") or 0)}</td><td>{float(item.get("total_log_time") or 0):g}</td>'
        '</tr>'
        for item in sessions
    ) or '<tr><td colspan="6" class="empty">暂无场次数据</td></tr>'

    if payment.get("is_paid_activity"):
        payment_content = f'''
        <div class="kpis payment-kpis">
          <div class="kpi"><span>历史支付成功</span><strong>{money(payment.get("payment_success_amount"))}</strong><small>{payment.get("payment_success_order_count",0)} 笔订单</small></div>
          <div class="kpi"><span>付费报名人数</span><strong>{payment.get("paid_signup_count",0)}</strong><small>未付费 {payment.get("unpaid_signup_count",0)} 人</small></div>
          <div class="kpi"><span>付费客单价</span><strong>{money(payment.get("average_paid_amount"))}</strong><small>按付费报名人数计算</small></div>
          <div class="kpi"><span>净收入</span><strong>{money(payment.get("net_received_amount"))}</strong><small>已退款 {money(payment.get("refunded_amount"))}</small></div>
        </div>'''
        ticket_rows = "".join(
            '<tr>'
            f'<td>{esc(item.get("ticket_name"))}{"（已删除）" if item.get("deleted") else ""}</td>'
            f'<td>{money(item.get("current_unit_price"))}</td><td>{int(item.get("paid_signup_count") or 0)}</td>'
            f'<td>{money(item.get("payment_success_amount"))}</td><td>{money(item.get("refunded_amount"))}</td>'
            f'<td>{money(item.get("net_received_amount"))}</td></tr>'
            for item in tickets
        ) or '<tr><td colspan="6" class="empty">暂无票档数据</td></tr>'
    else:
        payment_content = '<div class="empty">这是免费活动，不展示支付和退款指标。</div>'
        ticket_rows = '<tr><td colspan="6" class="empty">免费活动无票档收入数据</td></tr>'

    highlights = "".join(f'<div class="highlight">{esc(item)}</div>' for item in (insights.get("highlights") or []))
    notes = "".join(f'<li>{esc(item)}</li>' for item in (analysis.get("metric_notes") or []))
    document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(activity.get("title") or "活动")} · 活动经营分析看板</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f5f7f8;color:#18302d;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;letter-spacing:0}}.shell{{max-width:1180px;margin:0 auto;padding:28px 24px 56px}}header{{padding:30px;background:#123c36;color:#fff;border-radius:8px}}.eyebrow{{color:#99f6e4;font-size:13px;font-weight:700}}h1{{font-size:30px;margin:8px 0 10px}}header p{{color:#ccfbf1;margin:0;line-height:1.7}}.privacy{{display:inline-block;margin-top:16px;padding:6px 10px;border:1px solid #5eead4;border-radius:4px;color:#ccfbf1;font-size:12px}}.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}}.kpi,.panel{{background:#fff;border:1px solid #dfe8e6;border-radius:8px}}.kpi{{padding:18px}}.kpi span{{font-size:13px;color:#647b77}}.kpi strong{{display:block;font-size:25px;margin:7px 0;color:#123c36}}.kpi small{{color:#8aa09c}}.panel{{padding:22px;margin-top:16px}}.panel h2{{font-size:19px;margin:0 0 16px}}.panel h3{{font-size:15px;margin:20px 0 10px}}.panel-note{{color:#647b77;font-size:13px;margin:-8px 0 18px}}.two-col{{display:grid;grid-template-columns:1.2fr .8fr;gap:18px}}svg{{width:100%;height:auto;font-family:inherit}}svg .axis{{font-size:11px;fill:#64748b}}svg .value{{font-size:11px;fill:#18302d;font-weight:700}}.bar-row{{display:grid;grid-template-columns:100px 1fr 42px;align-items:center;gap:10px;margin-top:14px}}.bar-label{{font-size:13px}}.bar-track{{height:10px;background:#e3ecea;border-radius:3px;overflow:hidden}}.bar-fill{{height:100%}}.bar-value{{font-size:12px;color:#526d68;text-align:right}}table{{width:100%;border-collapse:collapse}}th,td{{padding:11px 10px;border-bottom:1px solid #dfe8e6;text-align:left;font-size:13px}}th{{color:#647b77;font-weight:600;background:#f7faf9}}.payment-kpis{{margin:0 0 18px}}.insight-summary{{font-size:17px;line-height:1.75;padding:16px;background:#ecfdf5;border-left:4px solid #0f766e}}.highlights{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:14px 0}}.highlight{{padding:14px;border:1px solid #dfe8e6;border-radius:6px;background:#fff}}.clean-list{{margin:0;padding-left:20px}}.clean-list li{{margin:9px 0;line-height:1.65}}.empty{{padding:18px;color:#8aa09c;text-align:center}}footer{{color:#647b77;font-size:12px;line-height:1.7;margin-top:18px}}@media(max-width:760px){{.shell{{padding:14px}}header{{padding:22px}}h1{{font-size:24px}}.kpis{{grid-template-columns:repeat(2,1fr)}}.two-col,.highlights{{grid-template-columns:1fr}}}}
</style></head><body><main class="shell">
<header><div class="eyebrow">LINGXI ACTIVITY INSIGHT</div><h1>{esc(activity.get("title") or "活动经营分析看板")}</h1><p>活动经营分析看板 · {esc(activity.get("dynamic_status_text"))} · 生成日期 {date.today().isoformat()}</p><div class="privacy">数据已脱敏 · 看板不包含报名或签到个人明细</div></header>
<div class="kpis">
<div class="kpi"><span>报名成功</span><strong>{overview.get("signup_success_count",0)}</strong><small>取消 {overview.get("signup_cancel_count",0)} 人</small></div>
<div class="kpi"><span>签到人数</span><strong>{overview.get("signed_in_people_count",0)}</strong><small>签到率 {percent(overview.get("signin_rate"))}</small></div>
<div class="kpi"><span>访问表现</span><strong>{overview.get("uv",0)} UV</strong><small>{overview.get("pv",0)} PV</small></div>
<div class="kpi"><span>累计服务时长</span><strong>{float(overview.get("total_log_time",0)):g}</strong><small>平均 {float(overview.get("average_log_time",0)):g}</small></div>
</div>
<section class="panel"><h2>报名趋势与来源</h2><div class="two-col"><div>{timeline_svg(analysis.get("signup_timeline") or [])}</div><div><h3>报名来源</h3>{bar_chart(analysis.get("signup_sources") or [], "source")}<h3>报名状态</h3>{bar_chart(analysis.get("signup_statuses") or [], "status", "#2563eb")}</div></div></section>
<section class="panel"><h2>签到表现</h2><div class="panel-note">签到人数按报名记录去重，签到流水适用于多场次分析</div><div class="two-col"><div>{timeline_svg(analysis.get("signin_timeline") or [], "#ea580c")}</div><div><h3>签到方式</h3>{bar_chart(analysis.get("signin_sources") or [], "source", "#ea580c")}<h3>签到时段</h3>{bar_chart(analysis.get("signin_hours") or [], "hour", "#7c3aed")}</div></div><h3>场次表现</h3><table><thead><tr><th>场次</th><th>签到人数</th><th>签到流水</th><th>签到率</th><th>签退</th><th>服务时长</th></tr></thead><tbody>{session_rows}</tbody></table></section>
<section class="panel"><h2>支付与退款</h2>{payment_content}<h3>票档表现</h3><table><thead><tr><th>票档</th><th>当前价格</th><th>付费人数</th><th>历史支付</th><th>退款</th><th>净收入</th></tr></thead><tbody>{ticket_rows}</tbody></table></section>
<section class="panel"><h2>AI 洞察与建议</h2><div class="insight-summary">{esc(insights.get("summary") or "尚未生成 AI 总结。")}</div><div class="highlights">{highlights or '<div class="empty">暂无关键发现</div>'}</div><h3>建议</h3>{bullet_list(insights.get("recommendations") or [], "暂无建议")}</section>
<section class="panel"><h2>统计口径</h2><ul class="clean-list">{notes or '<li>请以灵析 MCP 返回的 metric_notes 为准。</li>'}</ul></section>
<footer>统计汇总来自灵析 MCP。支付成功订单数不等于付费报名人数；多场次活动的签到流水数可能大于签到人数。HTML 为自包含文件，可离线打开和直接转发。</footer>
</main></body></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print("OK ->", output)


if __name__ == "__main__":
    main()
