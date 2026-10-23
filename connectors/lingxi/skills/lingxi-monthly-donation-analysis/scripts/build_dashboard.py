#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""月捐项目经营数据看板生成器（通用参数化版，无外部依赖）

输入文件（位于传入的 data 目录）：
  - dataset.json    脱敏明细数据集（lingxi MCP get_periodic_project_analysis_dataset 原样落盘）
  - summary.json    经营汇总（lingxi MCP get_periodic_project_summary 原样落盘）
  - analysis.json   由 analyze.py 生成的八维分析结果
  - insights.json   可选：agent 撰写的叙事文本（项目名、各板块洞察、人群、建议、口径说明）

输出：
  - <outdir>/dashboard.html  自包含 HTML 看板（内联 SVG，可离线打开/直接转发）

用法：
  python3 build_dashboard.py <data-dir> [outdir]
"""
import json, os, html, sys, math
from datetime import date

BASE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(BASE, "analysis.json")))
S = json.load(open(os.path.join(BASE, "summary.json")))
DS = json.load(open(os.path.join(BASE, "dataset.json")))
try:
    CFG = json.load(open(os.path.join(BASE, "insights.json")))
except Exception:
    CFG = {}

MONTHS = DS["months"]
MLBL = [m[2:].replace("-", "/") for m in MONTHS]
PROJ = CFG.get("project_name") or S.get("project", {}).get("project_name") or "月捐项目"
DR = S.get("date_range", {})
RANGE_TXT = f"{DR.get('start_date','')} ~ {DR.get('end_date','')}"
TODAY = date.today().isoformat()
INS = CFG.get("insights", {})
NOTES = CFG.get("kpi_notes", {})

def esc(s): return html.escape(str(s))
def ins(key):
    t = str(INS.get(key, "") or "").strip()
    return f'<div class="insight">{t}</div>' if t else ""

# ---------- 安全取数 ----------
def fmt_money(v):
    return f"¥{v:,.0f}" if float(v) == int(float(v)) else f"¥{v:,.2f}"

SM_RS = S.get("range_summary", {})
SM_CS = S.get("current_snapshot", {})
mt = S.get("monthly_trend", [])
amounts = [m.get("paid_amount", 0) for m in mt]
payers = [m.get("paying_bind_count", 0) for m in mt]
news = [m.get("new_bind_count", 0) for m in mt]
fails = [m.get("pay_failed_count", 0) for m in mt]

n_binded = A["integrity"]["binded"]
n_rows = A["integrity"]["total_rows"]
mrr = SM_CS.get("current_mrr") or A["integrity"]["dataset_mrr"]
period_amt = SM_RS.get("paid_amount") or A["integrity"]["dataset_period_amount"]
def pct(x, base):
    return f"{x / base * 100:.1f}%" if base else "—"

# ---------- SVG 图表 helpers ----------
def nice(m):
    if m <= 0: return 1
    p = 10 ** math.floor(math.log10(m))
    for f in (1, 2, 2.5, 5, 10):
        if m <= f * p: return f * p
    return 10 * p

def polyline_chart(series, labels, w=920, h=300, yfmt=lambda v: str(int(v)), pad_l=52, pad_r=52, pad_t=24, pad_b=34):
    vals0 = [v for s in series if s.get("axis", 0) == 0 for v in s["data"]]
    max0 = nice(max(vals0)) if vals0 else 1
    n = len(labels)
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    X = lambda i: pad_l + (iw * i / (n - 1) if n > 1 else iw / 2)
    Y0 = lambda v: pad_t + ih * (1 - v / max0)
    parts = [f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" font-family="inherit">']
    for k in range(5):
        v = max0 * k / 4
        y = Y0(v)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" stroke="#e9ecef" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#868e96">{yfmt(v)}</text>')
    for i, lb in enumerate(labels):
        parts.append(f'<text x="{X(i):.1f}" y="{h-12}" text-anchor="middle" font-size="10.5" fill="#868e96">{lb}</text>')
    for s in series:
        pts = " ".join(f"{X(i):.1f},{Y0(v):.1f}" for i, v in enumerate(s["data"]))
        dash = ' stroke-dasharray="5 4"' if s.get("dash") else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{s["color"]}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        for i, v in enumerate(s["data"]):
            parts.append(f'<circle cx="{X(i):.1f}" cy="{Y0(v):.1f}" r="3" fill="#fff" stroke="{s["color"]}" stroke-width="2"/>')
    parts.append("</svg>")
    return "".join(parts)

def combo_bars_line(bars, lines, labels, w=920, h=300, pad_l=52, pad_r=52, pad_t=24, pad_b=34):
    max0 = nice(max([max(bars["data"])] + [max(l["data"]) for l in lines if l.get("axis", 0) == 0]))
    max1 = nice(max([max(l["data"]) for l in lines if l.get("axis", 1) == 1] or [1]))
    n = len(labels)
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    X = lambda i: pad_l + iw * (i + 0.5) / n
    Y0 = lambda v: pad_t + ih * (1 - v / max0)
    Y1 = lambda v: pad_t + ih * (1 - v / max1)
    parts = [f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" font-family="inherit">']
    for k in range(5):
        v = max0 * k / 4
        y = Y0(v)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-pad_r}" y2="{y:.1f}" stroke="#e9ecef"/>')
        parts.append(f'<text x="{pad_l-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#868e96">{int(v)}</text>')
        parts.append(f'<text x="{w-pad_r+8}" y="{y+4:.1f}" font-size="11" fill="#adb5bd">{max1*k/4:g}</text>')
    for i, lb in enumerate(labels):
        parts.append(f'<text x="{X(i):.1f}" y="{h-12}" text-anchor="middle" font-size="10.5" fill="#868e96">{lb}</text>')
    bw = iw / n * 0.42
    for i, v in enumerate(bars["data"]):
        y = Y0(v)
        parts.append(f'<rect x="{X(i)-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{pad_t+ih-y:.1f}" rx="3" fill="{bars["color"]}" opacity="0.85"/>')
        parts.append(f'<text x="{X(i):.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="10" fill="{bars["color"]}" font-weight="600">{v if v else ""}</text>')
    for l in lines:
        Y = Y0 if l.get("axis", 0) == 0 else Y1
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(l["data"]))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{l["color"]}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, v in enumerate(l["data"]):
            parts.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3" fill="#fff" stroke="{l["color"]}" stroke-width="2"/>')
    parts.append("</svg>")
    return "".join(parts)

def bar_chart_h(items, w=560, row_h=34, pad_l=110, pad_r=60, color="#e8590c", fmt=str):
    h = row_h * len(items) + 10
    maxv = max([v for _, v, *_ in items] or [1])
    parts = [f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" font-family="inherit">']
    for i, item in enumerate(items):
        label, v = item[0], item[1]
        sub = item[2] if len(item) > 2 else None
        y = i * row_h + 8
        bw = (w - pad_l - pad_r) * v / maxv if maxv else 0
        parts.append(f'<text x="{pad_l-8}" y="{y+15}" text-anchor="end" font-size="12.5" fill="#495057">{esc(label)}</text>')
        parts.append(f'<rect x="{pad_l}" y="{y+2}" width="{max(bw,2):.1f}" height="20" rx="4" fill="{color}" opacity="0.9"/>')
        txt = fmt(v) + (f" · {sub}" if sub else "")
        parts.append(f'<text x="{max(pad_l+bw+6, pad_l+8):.1f}" y="{y+17}" font-size="12" fill="#343a40" font-weight="600">{esc(txt)}</text>')
    parts.append("</svg>")
    return "".join(parts)

def bar_chart_v(labels, data, w=920, h=260, color="#4263eb", pad_l=40, pad_t=18, pad_b=30):
    n = len(labels)
    iw, ih = w - pad_l - 10, h - pad_t - pad_b
    maxv = max(data or [1]) or 1
    parts = [f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:auto" font-family="inherit">']
    for k in range(3):
        y = pad_t + ih * (1 - (k + 1) / 3)
        parts.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w-10}" y2="{y:.1f}" stroke="#e9ecef"/>')
    bw = iw / n * 0.5
    for i, v in enumerate(data):
        x = pad_l + iw * (i + 0.5)
        y = pad_t + ih * (1 - v / maxv)
        parts.append(f'<rect x="{x-bw/2:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(pad_t+ih-y,0):.1f}" rx="3" fill="{color}" opacity="0.88"/>')
        parts.append(f'<text x="{x:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="11" fill="#495057" font-weight="600">{v if v else ""}</text>')
        parts.append(f'<text x="{x:.1f}" y="{h-10}" text-anchor="middle" font-size="10.5" fill="#868e96">{labels[i]}</text>')
    parts.append("</svg>")
    return "".join(parts)

def kpi_cards(items):
    cells = []
    for title, val, sub, color in items:
        cells.append(f'''<div class="kpi"><div class="kpi-t">{esc(title)}</div>
        <div class="kpi-v" style="color:{color}">{esc(val)}</div>
        <div class="kpi-s">{esc(sub)}</div></div>''')
    return f'<div class="kpi-grid">{"".join(cells)}</div>'

# ---------- 数据准备 ----------
tier_dist = A.get("tier_dist", [])
persist = A.get("persist_dist", [])
reasons = A.get("cancel", {}).get("reasons", [])
chans = A.get("channels", [])
cohorts = A.get("cohorts", [])
coh_map = {c["cohort"]: c for c in cohorts}
cnote = {c.get("cohort"): c.get("note", "") for c in CFG.get("cohort_notes", [])}

# cohort 图：取前 4 个批次
coh_keys = [c["cohort"] for c in cohorts[:4]]
COH_COLORS = ["#e8590c", "#f08c00", "#74b816", "#4263eb"]
def cohort_chart():
    if not coh_keys:
        return '<p class="note">所选区间没有可绘制的新绑定 cohort。</p>'
    series = []
    for i, cm in enumerate(coh_keys):
        c = coh_map[cm]
        series.append({"name": cm, "data": [p["rate"] for p in c["curve"]], "color": COH_COLORS[i % 4]})
    maxlen = max(len(s["data"]) for s in series)
    labels = [f"第{i+1}月" for i in range(maxlen)]
    return polyline_chart(series, labels, w=920, h=280, yfmt=lambda v: f"{v:.0f}%")

coh_legend = "".join(
    f'<span><i style="background:{COH_COLORS[i%4]}"></i>{cm} 批（{coh_map[cm]["size"]}人，最终留存 {coh_map[cm]["still_pct"]}%）</span>'
    for i, cm in enumerate(coh_keys))

# ---------- KPI（数字全部自动计算；副标题可用 insights.kpi_notes 覆盖） ----------
seg_new = A.get("segments", {}).get("contact", {}).get("new", {})
seg_rep = A.get("segments", {}).get("contact", {}).get("repeat", {})
amt_ch = A.get("amount_change", {})
cancel = A.get("cancel", {})
failure = A.get("failure", {})
peak_payers = max(payers) if payers else 0
kpi1 = [
    ("区间累计收入", fmt_money(period_amt), NOTES.get("区间累计收入") or f"{SM_RS.get('paid_count', 0):,} 笔成功扣款", "#e8590c"),
    ("当前在捐人数", f"{SM_CS.get('active_bind_count', n_binded)} 人", NOTES.get("当前在捐人数") or (f"较峰值 {peak_payers} 人的月度扣款人数" if peak_payers else ""), "#4263eb"),
    ("当前 MRR", fmt_money(mrr), NOTES.get("当前MRR") or "月度经常性收入", "#e8590c"),
    ("平均月捐金额", fmt_money(SM_CS.get("avg_bind_amount", 0)), NOTES.get("平均月捐金额") or "在捐绑定口径", "#4263eb"),
    ("新增月捐绑定", f"{SM_RS.get('new_bind_count', 0)} 人", NOTES.get("新增月捐绑定") or f"其中老捐赠人 {seg_rep.get('count', 0)} 人", "#2f9e44"),
    ("区间解绑", f"{SM_RS.get('unbind_count', 0)} 人次", NOTES.get("区间解绑") or f"含 {SM_RS.get('rebind_count', 0)} 人解绑后重新绑定", "#e03131"),
]
net_delta = amt_ch.get("net_mrr_delta", 0)
kpi2 = [
    ("扣款失败绑定", f"{SM_RS.get('pay_failed_count', 0)} 个", NOTES.get("扣款失败绑定") or f"涉及金额 {fmt_money(SM_RS.get('pay_failed_amount', 0))}", "#e03131"),
    ("失败后恢复", f"{failure.get('recovered', 0)} 人", NOTES.get("失败后恢复") or f"恢复率 {pct(failure.get('recovered', 0), failure.get('failed_bind_count', 0) or 1)}", "#2f9e44"),
    ("连续失败后流失", f"{failure.get('churned_after_fail', 0)} 人", NOTES.get("连续失败后流失") or f"流失 MRR {fmt_money(failure.get('churned_lost_mrr', 0))}/月", "#e03131"),
    ("尝试取消", f"{SM_RS.get('try_unbind_count', 0)} 人次", NOTES.get("尝试取消") or f"其中 {cancel.get('try_unbind_retained', 0)} 人发起后仍在捐", "#e03131"),
    ("提额 / 降额", f"{SM_RS.get('amount_up_count', 0)} / {SM_RS.get('amount_down_count', 0)} 人", NOTES.get("提额/降额") or f"净影响 MRR {'+' if net_delta >= 0 else '−'}¥{abs(net_delta):,}/月", "#e8590c"),
    ("区间留存率", (NOTES.get("区间留存率_value") or (f"{coh_map[coh_keys[0]]['still_pct']}%" if coh_keys else "—")), NOTES.get("区间留存率") or ("首批 cohort 口径" if coh_keys else ""), "#2f9e44"),
]

# ---------- 明细表格（全部数据驱动） ----------
monthly_rows = "".join(
    f'<tr><td>{m["month"]}</td><td class="num">{m.get("paid_amount",0):,}</td><td class="num">{m.get("paying_bind_count",0)}</td>'
    f'<td class="num">{m.get("new_bind_count",0)}</td><td class="num">{m.get("unbind_count",0)}</td><td class="num">{m.get("pay_failed_count",0)}</td></tr>'
    for m in mt)
monthly_total = (
    f'<tr style="font-weight:700;background:#fff8f3"><td>合计</td><td class="num">{sum(amounts):,}</td><td class="num">—</td>'
    f'<td class="num">{sum(news)}</td><td class="num">{sum(m.get("unbind_count",0) for m in mt)}</td>'
    f'<td class="num">{sum(fails)} 人次（{SM_RS.get("pay_failed_count",0)} 个绑定）</td></tr>')

tier_rows = "".join(
    f'<tr><td>{t["tier"]}</td><td class="num">{t["count"]}</td><td class="num">{t["pct"]}%</td>'
    f'<td class="num">{t["mrr"]:,}</td><td class="num">{pct(t["mrr"], mrr)}</td></tr>'
    for t in tier_dist)
tier_total = (f'<tr style="font-weight:700;background:#fff8f3"><td>合计</td><td class="num">{n_binded}</td>'
              f'<td class="num">100%</td><td class="num">{mrr:,}</td><td class="num">100%</td></tr>')

cohort_rows = "".join(
    f'<tr><td>{c["cohort"]}</td><td class="num">{c["size"]}</td><td class="num">{c["still_binded"]}</td>'
    f'<td class="num {"good" if c["still_pct"] >= 60 else "bad"}">{c["still_pct"]}%</td><td>{esc(cnote.get(c["cohort"], ""))}</td></tr>'
    for c in cohorts)

persist_rows = "".join(
    f'<tr><td>{p["range"]}</td><td class="num">{p["count"]}</td><td class="num">{p["pct"]}%</td><td class="num">{p["still_active"]}</td></tr>'
    for p in persist)

fail_month_lbl = [m[2:].replace("-", "/") for m in [x["month"] for x in failure.get("fail_by_month", [])]]
fail_month_dat = [x["failed"] for x in failure.get("fail_by_month", [])]

up_detail_str = "、".join(f'{d.get("from","?")}→{d.get("to","?")}' for d in amt_ch.get("up_detail", []))
down_detail_str = "、".join(f'→{d.get("to","?")}' for d in amt_ch.get("down_detail", []))

try_unbind_split = (f"尝试取消 {SM_RS.get('try_unbind_count', 0)} 人次的去向："
                    f"<b>{cancel.get('try_unbind_retained', 0)} 人发起取消但仍在捐</b>、"
                    f"<b>{SM_RS.get('rebind_count', 0)} 人取消后重新绑定</b>、"
                    f"<b>{cancel.get('unbind_rows', 0) - SM_RS.get('rebind_count', 0)} 人最终解绑</b>（明细口径）。")

channel_rows = "".join(
    f'<tr><td><b>{esc(c["channel"])}</b></td><td class="num">{c["total"]}</td><td class="num">{c["active"]}</td>'
    f'<td class="num">{c["retention_pct"]}%</td><td class="num">{c["period_amount"]:,}</td><td class="num">{pct(c["period_amount"], period_amt)}</td>'
    f'<td class="num">{c["mrr_now"]:,}</td><td class="num">{c["avg_amount"]}</td><td class="num">{c["failed_binds"]}</td><td class="num">{c["unbind"]}</td></tr>'
    for c in chans)

pops = CFG.get("populations", [])
pop_rows = "".join(
    f'<tr><td class="{"good" if p.get("good", True) else "bad"}">{p.get("name","")}</td><td class="num">{p.get("size","")}</td><td>{p.get("perf","")}</td></tr>'
    for p in pops) or '<tr><td colspan="3" style="color:#868e96">（未提供 insights.json populations，可运行时补充）</td></tr>'

recs = CFG.get("recommendations", [])
rec_html = "".join(
    f'<div class="rec"><div class="no">{i+1}</div><div>{r}</div></div>' for i, r in enumerate(recs)) \
    or '<div class="note">（未提供 insights.json recommendations，可运行时补充）</div>'

appendix_extra = "".join(
    f'<tr><td>{esc(a.get("item",""))}</td><td>{a.get("note","")}</td></tr>' for a in CFG.get("appendix", []))
metric_notes = "".join(f'<li>{esc(n)}</li>' for n in S.get("metric_notes", []))

badge_sys = '<span class="tag sys">权威口径 · 系统汇总</span>'
badge_det = f'<span class="tag det">明细分析 · {n_rows}条脱敏绑定</span>'
hero_note = CFG.get("hero_note") or (
    f"状态：{esc(S.get('project', {}).get('status_text', '—'))} · 最近一笔扣款 {esc(S.get('project', {}).get('last_donate_time', '—'))}")

reason_color = {"余额不足": "#e03131", "信任度下降": "#f08c00", "经济压力": "#fab005", "其他": "#adb5bd",
                "调整扣款日期": "#74c0fc", "对项目不满意": "#9775fa", "未填写": "#ced4da"}

html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(PROJ)} · 月捐项目经营数据看板（{MLBL[0] if MLBL else ""} ~ {MLBL[-1] if MLBL else ""}）</title>
<style>
:root {{ --ink:#343a40; --sub:#868e96; --line:#e9ecef; --card:#ffffff; --bg:#f6f7f9;
  --orange:#e8590c; --blue:#4263eb; --green:#2f9e44; --red:#e03131; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  background:var(--bg); color:var(--ink); line-height:1.6; padding:28px 18px 60px; }}
.wrap {{ max-width:1180px; margin:0 auto; }}
header.hero {{ background:linear-gradient(120deg,#fff4e6,#ffe8d1 55%,#ffd8a8); border-radius:16px; padding:30px 34px; margin-bottom:22px; border:1px solid #ffe3c2; }}
header.hero h1 {{ font-size:25px; letter-spacing:.5px; }}
header.hero .meta {{ color:#8a5a2b; font-size:13px; margin-top:8px; }}
header.hero .meta b {{ color:#c2530f; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:22px 24px; margin-bottom:22px; box-shadow:0 1px 3px rgba(16,24,40,.04); }}
.sec-t {{ font-size:18px; font-weight:700; margin-bottom:4px; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }}
.sec-d {{ color:var(--sub); font-size:13px; margin-bottom:14px; }}
.tag {{ font-size:11px; padding:2px 9px; border-radius:999px; font-weight:600; white-space:nowrap; }}
.tag.sys {{ background:#fff0f6; color:#c2255c; border:1px solid #fcc2d7; }}
.tag.det {{ background:#e7f5ff; color:#1971c2; border:1px solid #a5d8ff; }}
.tag.mix {{ background:#fff4e6; color:#d9480f; border:1px solid #ffd8a8; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; }}
.kpi {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:14px 16px; }}
.kpi-t {{ font-size:12.5px; color:var(--sub); }}
.kpi-v {{ font-size:22px; font-weight:800; margin:2px 0; }}
.kpi-s {{ font-size:11.5px; color:var(--sub); }}
.legend {{ display:flex; gap:18px; flex-wrap:wrap; font-size:12.5px; color:#495057; margin-top:8px; }}
.legend i {{ display:inline-block; width:10px; height:10px; border-radius:3px; margin-right:5px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:6px; }}
th {{ background:#f8f9fa; text-align:left; font-weight:600; color:#495057; }}
th,td {{ padding:8px 10px; border-bottom:1px solid var(--line); }}
tr:last-child td {{ border-bottom:none; }}
td.num,th.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
.good {{ color:var(--green); font-weight:700; }} .bad {{ color:var(--red); font-weight:700; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:22px; }}
@media (max-width:900px) {{ .two {{ grid-template-columns:1fr; }} }}
.insight {{ background:#fff9db; border:1px solid #ffe066; border-radius:10px; padding:10px 14px; font-size:13px; margin-top:12px; color:#664d03; }}
.rec {{ display:flex; gap:12px; padding:12px 0; border-bottom:1px dashed var(--line); }}
.rec:last-child {{ border-bottom:none; }}
.rec .no {{ flex:0 0 26px; height:26px; border-radius:50%; background:var(--orange); color:#fff; font-weight:700; font-size:13px; display:flex; align-items:center; justify-content:center; }}
.rec b {{ color:#c2530f; }}
.note {{ font-size:12px; color:var(--sub); margin-top:10px; }}
footer {{ text-align:center; color:var(--sub); font-size:12px; margin-top:8px; }}
</style>
</head>
<body><div class="wrap">

<header class="hero">
  <h1>🧡 「{esc(PROJ)}」月捐项目经营数据看板</h1>
  <div class="meta">统计区间 <b>{esc(RANGE_TXT)}</b>（{len(MONTHS)} 个月） · {hero_note}<br>
  指标口径：<b>权威口径</b> = 系统经营汇总接口返回；<b>明细分析</b> = 基于 {n_rows} 条脱敏月捐绑定记录（无任何个人身份信息）的复算结论。</div>
</header>

<div class="card">
  <div class="sec-t">核心指标总览 {badge_sys}</div>
  <div class="sec-d">以下均为系统经营汇总接口返回的权威数值；括注为明细数据的交叉验证结果。</div>
  {kpi_cards(kpi1)}
  <div style="height:12px"></div>
  {kpi_cards(kpi2)}
  <div class="note">✔ 对账：明细复算 区间收入 {fmt_money(A["integrity"]["dataset_period_amount"])}、在捐 {A["integrity"]["dataset_active"]} 人、MRR {fmt_money(A["integrity"]["dataset_mrr"])} —— 与系统汇总{'一致' if A["integrity"]["dataset_mrr"] == A["integrity"]["system_mrr"] and A["integrity"]["dataset_period_amount"] == A["integrity"]["system_period_amount"] else '存在差异，请核对口径'}。</div>
</div>

<div class="card">
  <div class="sec-t">一 · 月度经营趋势：收入、成功扣款人数与新增月捐人 {badge_sys}</div>
  <div class="sec-d">柱＝新增月捐绑定（左轴）；实线＝月收入（左轴，元）；虚线＝成功扣款人数（右轴，人）。</div>
  {combo_bars_line({"label":"新增","data":news,"color":"#ffc9c9"}, [
      {"name":"月收入","data":amounts,"color":"#e8590c","axis":0},
      {"name":"成功扣款人数","data":payers,"color":"#4263eb","axis":1,"dash":True},
  ], MLBL, w=940, h=310)}
  <div class="legend"><span><i style="background:#ffc9c9"></i>新增月捐绑定（人）</span><span><i style="background:#e8590c"></i>月收入（元，左轴）</span><span><i style="background:#4263eb"></i>成功扣款人数（右轴）</span></div>
  <table>
    <tr><th>月份</th><th class="num">月收入(¥)</th><th class="num">成功扣款人数</th><th class="num">新增月捐人</th><th class="num">解绑</th><th class="num">扣款失败(人次)</th></tr>
    {monthly_rows}
    {monthly_total}
  </table>
  {ins("trend")}
</div>

<div class="card">
  <div class="sec-t">二 · 当前盘子：在捐人数、MRR 与金额档位分布 <span class="tag mix">权威 + 明细</span></div>
  <div class="sec-d">在捐 {n_binded} 人 / MRR {fmt_money(mrr)} / 平均月捐 {fmt_money(SM_CS.get("avg_bind_amount", 0))} 为系统权威口径；档位拆分由明细计算。</div>
  <div class="two">
    <div>{bar_chart_h([(t["tier"], t["count"], f"占比 {t['pct']}%") for t in tier_dist], color="#e8590c", fmt=lambda v: f"{v} 人")}</div>
    <div>
      <table>
        <tr><th>档位</th><th class="num">在捐人数</th><th class="num">占比</th><th class="num">MRR贡献(¥)</th><th class="num">MRR占比</th></tr>
        {tier_rows}
        {tier_total}
      </table>
      {ins("tier")}
    </div>
  </div>
</div>

<div class="card">
  <div class="sec-t">三 · 持续捐赠次数与留存 {badge_det}</div>
  <div class="sec-d">按绑定加入月份（cohort）追踪逐月存活率（当月有成功扣款计为存活）。</div>
  {cohort_chart()}
  <div class="legend">{coh_legend}</div>
  <table>
    <tr><th>加入批次</th><th class="num">人数</th><th class="num">仍在捐</th><th class="num">留存率</th><th>说明</th></tr>
    {cohort_rows}
  </table>
  <div class="two" style="margin-top:14px">
    <div>
      <div class="sec-t" style="font-size:15px">累计成功扣款次数分布（{n_rows} 个绑定）</div>
      {bar_chart_v([p["range"] for p in persist], [p["count"] for p in persist], w=440, h=230, color="#4263eb")}
      <div class="note">人均累计成功扣款 <b>{A.get("avg_lifetime_paid", 0)}</b> 次。</div>
    </div>
    <div>
      <div class="sec-t" style="font-size:15px">留存结构</div>
      <table>
        <tr><th>持续次数</th><th class="num">绑定数</th><th class="num">占比</th><th class="num">其中仍在捐</th></tr>
        {persist_rows}
      </table>
      {ins("persist")}
    </div>
  </div>
</div>

<div class="card">
  <div class="sec-t">四 · 扣款失败、失败后恢复与连续失败流失 <span class="tag mix">权威 + 明细</span></div>
  <div class="sec-d">系统口径：{SM_RS.get("pay_failed_count", 0)} 个绑定发生扣款失败，涉及失败金额 {fmt_money(SM_RS.get("pay_failed_amount", 0))}。</div>
  <div class="two">
    <div>
      <div class="sec-t" style="font-size:15px">月度扣款失败次数（明细）</div>
      {bar_chart_v(fail_month_lbl, fail_month_dat, w=440, h=230, color="#e03131")}
      <div class="note">失败合计 {failure.get("failed_attempt_total", 0)} 次（明细口径，系统按绑定数计 {SM_RS.get("pay_failed_count", 0)}）。</div>
    </div>
    <div>
      <div class="sec-t" style="font-size:15px">{failure.get("failed_bind_count", 0)} 个失败绑定的去向</div>
      <table>
        <tr><th>去向</th><th class="num">绑定数</th><th class="num">占比</th><th class="num">MRR</th></tr>
        <tr><td class="good">失败后恢复（仍在捐）</td><td class="num">{failure.get("recovered", 0)}</td><td class="num">{pct(failure.get("recovered", 0), failure.get("failed_bind_count", 0) or 1)}</td><td class="num">保留 {fmt_money(failure.get("recovered_mrr_now", 0))}/月</td></tr>
        <tr><td class="bad">连续失败后解绑流失</td><td class="num">{failure.get("churned_after_fail", 0)}</td><td class="num">{pct(failure.get("churned_after_fail", 0), failure.get("failed_bind_count", 0) or 1)}</td><td class="num">流失 {fmt_money(failure.get("churned_lost_mrr", 0))}/月</td></tr>
      </table>
      {ins("failure")}
    </div>
  </div>
</div>

<div class="card">
  <div class="sec-t">五 · 取消捐赠、恢复绑定、尝试取消与取消原因 <span class="tag mix">权威 + 明细</span></div>
  <div class="sec-d">系统口径：区间解绑 {SM_RS.get("unbind_count", 0)} 人次、恢复绑定 {SM_RS.get("rebind_count", 0)} 人、尝试取消 {SM_RS.get("try_unbind_count", 0)} 人次。</div>
  <div class="two">
    <div>
      <div class="sec-t" style="font-size:15px">取消原因分布（{cancel.get("unbind_rows", 0)} 个最终解绑绑定）</div>
      {bar_chart_h([(r["reason"], r["count"], f"流失MRR ¥{r['amount']}") for r in reasons], color="#e03131", fmt=lambda v: f"{v} 人")}
      <div class="note">{try_unbind_split}</div>
    </div>
    <div>
      <table>
        <tr><th>流失类型</th><th class="num">人数</th><th class="num">流失 MRR</th></tr>
        <tr><td>被动流失（连续扣款失败）</td><td class="num">{cancel.get("fail_churn", 0)}</td><td class="num">{fmt_money(cancel.get("fail_churn_lost_mrr", 0))}/月</td></tr>
        <tr><td>主动取消</td><td class="num">{cancel.get("voluntary", 0)}</td><td class="num">{fmt_money(cancel.get("voluntary_lost_mrr", 0))}/月</td></tr>
        <tr style="background:#fff8f3"><td><b>合计</b></td><td class="num"><b>{cancel.get("unbind_rows", 0)}</b></td><td class="num"><b>{fmt_money(cancel.get("voluntary_lost_mrr", 0) + cancel.get("fail_churn_lost_mrr", 0))}/月</b></td></tr>
      </table>
      <table style="margin-top:10px">
        <tr><th>解绑后重新绑定（回流）</th><th class="num">人数</th></tr>
        <tr><td>解绑后回归</td><td class="num">{cancel.get("rebind_count", 0)}</td></tr>
      </table>
      {ins("cancel")}
    </div>
  </div>
</div>

<div class="card">
  <div class="sec-t">六 · 提额与降额对收入的影响 {badge_det}</div>
  <div class="sec-d">系统口径：提额 {SM_RS.get("amount_up_count", 0)} 人、降额 {SM_RS.get("amount_down_count", 0)} 人；明细可还原变动前后金额。</div>
  <div class="two">
    <div>
      <table>
        <tr><th>变动</th><th>明细</th><th class="num">MRR 影响</th></tr>
        <tr><td class="good">提额 {amt_ch.get("up_count", 0)} 人</td><td>{esc(up_detail_str)}</td><td class="num good">+¥{amt_ch.get("up_mrr_delta", 0):,}/月</td></tr>
        <tr><td class="bad">降额 {amt_ch.get("down_count", 0)} 人</td><td>{esc(down_detail_str)}</td><td class="num bad">−¥{abs(amt_ch.get("down_mrr_delta", 0)):,}/月</td></tr>
        <tr style="background:#fff8f3;font-weight:700"><td>净影响</td><td></td><td class="num">{'+' if amt_ch.get("net_mrr_delta", 0) >= 0 else '−'}¥{abs(amt_ch.get("net_mrr_delta", 0)):,}/月</td></tr>
      </table>
      {ins("amount")}
    </div>
    <div>
      <table>
        <tr><th>渠道</th><th>人数</th></tr>
        <tr><td>提额人群渠道</td><td>{esc("、".join(str(d.get("channel", "")) for d in amt_ch.get("up_detail", [])))}</td></tr>
        <tr><td>降额人群渠道</td><td>{esc("、".join(str(d.get("channel", "")) for d in amt_ch.get("down_detail", [])))}</td></tr>
      </table>
    </div>
  </div>
</div>

<div class="card">
  <div class="sec-t">七 · 渠道表现：新增、收入、留存与流失 {badge_det}</div>
  <div class="sec-d">按 {n_rows} 个绑定的渠道归属计算（脱敏明细）。</div>
  <table>
    <tr><th>渠道</th><th class="num">累计绑定</th><th class="num">当前在捐</th><th class="num">留存率</th><th class="num">区间收入(¥)</th><th class="num">收入占比</th><th class="num">当前MRR(¥)</th><th class="num">在捐客单(¥)</th><th class="num">失败绑定</th><th class="num">解绑</th></tr>
    {channel_rows}
  </table>
  <div class="two" style="margin-top:12px">
    <div>{bar_chart_h([(c["channel"], c["period_amount"], f"MRR ¥{c['mrr_now']}") for c in chans], color="#4263eb", fmt=lambda v: f"¥{v:,}")}</div>
    <div>{ins("channel")}</div>
  </div>
</div>

<div class="card">
  <div class="sec-t">八 · 重点人群识别与运营建议 <span class="tag det">明细分析结论</span></div>
  <div class="sec-d">基于脱敏明细的分组对比（不涉及任何个人身份识别）。</div>
  <div class="two">
    <div>
      <table>
        <tr><th>人群</th><th class="num">规模</th><th>表现</th></tr>
        {pop_rows}
      </table>
    </div>
    <div>{rec_html}</div>
  </div>
</div>

<div class="card">
  <div class="sec-t">附 · 口径与数据说明</div>
  <table>
    <tr><th>项目</th><th>说明</th></tr>
    <tr><td>数据来源</td><td>系统「月捐项目经营汇总」与「脱敏分析数据集」两个接口；明细共 {n_rows} 条绑定记录。</td></tr>
    {appendix_extra}
    <tr><td>隐私</td><td>明细数据已脱敏（无姓名/手机号/邮箱等身份信息）；本看板全部为群体聚合分析，不识别、不推测任何具体捐赠人。</td></tr>
  </table>
  <ul style="margin:10px 0 0 20px;font-size:12px;color:#868e96">{metric_notes}</ul>
</div>

<footer>「{esc(PROJ)}」月捐项目经营数据看板 · 数据区间 {esc(RANGE_TXT)} · 生成于 {TODAY} · 全部数据已脱敏</footer>
</div></body></html>
"""

outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(BASE)
os.makedirs(outdir, exist_ok=True)
out_path = os.path.join(outdir, "dashboard.html")
open(out_path, "w").write(html_doc)
print("OK ->", out_path)
