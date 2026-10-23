#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""月捐项目脱敏明细分析：analyze.py <data-dir>，输出 analysis.json。"""
import json, os, sys
from collections import defaultdict

BASE = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
DS = json.load(open(os.path.join(BASE, "dataset.json")))
SM = json.load(open(os.path.join(BASE, "summary.json")))
MONTHS = DS["months"]
COLS = DS["columns"]
CH = {int(k): v for k, v in DS["channel_map"].items()}

rows = [dict(zip(COLS, r)) for r in DS["rows"]]
R = lambda r, i: r[i]
# named access
def g(row, col): return row[col]

def ratio(value, total, digits=1):
    return round(value / total, digits) if total else 0

out = {}

# ---------- 0. 数据完整性 ----------
binded = [r for r in rows if r["status"] == "binded"]
unbinded = [r for r in rows if r["status"] == "unbind"]
out["integrity"] = {
    "total_rows": len(rows),
    "binded": len(binded),
    "unbind": len(unbinded),
    "dataset_mrr": sum(r["current_amount"] for r in binded),
    "system_mrr": SM["current_snapshot"]["current_mrr"],
    "dataset_active": len(binded),
    "system_active": SM["current_snapshot"]["active_bind_count"],
    "dataset_period_amount": sum(r["period_paid_amount"] for r in rows),
    "system_period_amount": SM["range_summary"]["paid_amount"],
}

# ---------- 1. 月度趋势（明细侧复算，与系统汇总对照） ----------
monthly = []
for i, m in enumerate(MONTHS):
    amt = sum(r["monthly_paid_amounts"][i] for r in rows)
    cnt = sum(r["monthly_paid_counts"][i] for r in rows)
    payers = sum(1 for r in rows if r["monthly_paid_counts"][i] > 0)
    new_b = sum(1 for r in rows if r["created_month"] == m)
    fails = sum(r["monthly_failed_counts"][i] for r in rows)
    failed_binds = sum(1 for r in rows if r["monthly_failed_counts"][i] > 0)
    monthly.append({"month": m, "paid_amount": amt, "paid_count": cnt, "payers": payers,
                    "new_binds": new_b, "failed": fails, "failed_binds": failed_binds})
out["monthly_detail"] = monthly
out["monthly_system"] = SM["monthly_trend"]

# ---------- 2. 当前盘子：档位分布 ----------
tiers = [(20, "20元"), (50, "50元"), (100, "100元"), (200, "200元"), (400, "400元")]
tier_dist = []
for amt_v, label in tiers:
    grp = [r for r in binded if r["current_amount"] == amt_v]
    tier_dist.append({"tier": label, "count": len(grp),
                      "mrr": sum(r["current_amount"] for r in grp),
                      "pct": ratio(len(grp) * 100, len(binded))})
other = [r for r in binded if r["current_amount"] not in [t[0] for t in tiers]]
if other:
    tier_dist.append({"tier": "其他", "count": len(other), "mrr": sum(r["current_amount"] for r in other),
                      "pct": ratio(len(other) * 100, len(binded))})
out["tier_dist"] = tier_dist
out["avg_amount"] = ratio(sum(r["current_amount"] for r in binded), len(binded), 2)

# ---------- 3. 持续捐赠次数 & 留存 ----------
buckets = [(1, 1, "1次"), (2, 3, "2-3次"), (4, 6, "4-6次"), (7, 9, "7-9次"), (10, 12, "10-12次")]
persist = []
for lo, hi, label in buckets:
    grp = [r for r in rows if lo <= r["lifetime_paid_count"] <= hi]
    persist.append({"range": label, "count": len(grp),
                    "pct": ratio(len(grp) * 100, len(rows)),
                    "still_active": sum(1 for r in grp if r["status"] == "binded")})
out["persist_dist"] = persist
out["avg_lifetime_paid"] = ratio(sum(r["lifetime_paid_count"] for r in rows), len(rows))

# cohort 留存：按 created_month 分组，逐月存活率（以该月有成功扣款计）
cohorts = []
for cm in sorted(set(r["created_month"] for r in rows)):
    # A creation cohort outside the requested months has no complete curve here.
    if cm not in MONTHS:
        continue
    grp = [r for r in rows if r["created_month"] == cm]
    start_idx = MONTHS.index(cm)
    n = len(grp)
    curve = []
    for j in range(start_idx, len(MONTHS)):
        alive = sum(1 for r in grp if r["monthly_paid_counts"][j] > 0)
        curve.append({"month": MONTHS[j], "alive": alive, "rate": round(alive / n * 100, 1)})
    # 最终仍在捐
    still = sum(1 for r in grp if r["status"] == "binded")
    cohorts.append({"cohort": cm, "size": n, "final_alive": curve[-1]["alive"],
                    "final_rate": curve[-1]["rate"], "still_binded": still,
                    "still_pct": round(still / n * 100, 1), "curve": curve})
out["cohorts"] = cohorts

# ---------- 4. 扣款失败 ----------
fail_rows = [r for r in rows if r["period_failed_count"] > 0]
recovered = [r for r in fail_rows if r["status"] == "binded"]
churned_after_fail = [r for r in fail_rows if r["status"] == "unbind"]
# 失败月份分布
fail_by_month = [{"month": m, "failed": sum(r["monthly_failed_counts"][i] for r in rows)}
                 for i, m in enumerate(MONTHS)]
# 连续失败后流失判定：unbind 且失败发生在最后两个有活动的月份
out["failure"] = {
    "failed_bind_count": len(fail_rows),
    "failed_attempt_total": sum(r["period_failed_count"] for r in fail_rows),
    "recovered": len(recovered),
    "churned_after_fail": len(churned_after_fail),
    "churned_all_balance_reason": sum(1 for r in churned_after_fail if r["unbind_reason"] == "not_enough_balance"),
    "recovered_avg_lifetime": round(sum(r["lifetime_paid_count"] for r in recovered) / len(recovered), 1) if recovered else 0,
    "recovered_mrr_now": sum(r["current_amount"] for r in recovered),
    "churned_lost_mrr": sum(r["current_amount"] for r in churned_after_fail),
    "fail_by_month": fail_by_month,
    "recovered_rows": [{"amount": r["current_amount"], "channel": CH.get(r["channel_id"]), "lifetime": r["lifetime_paid_count"], "contact": r["contact_status"]} for r in recovered],
}

# ---------- 5. 取消 / 恢复 / 尝试取消 ----------
reason_cn = {"not_enough_balance": "余额不足", "economic_pressures": "经济压力", "other": "其他",
             "modify_donate_time": "调整扣款日期", "not_satisfied": "对项目不满意", "lose_trust": "信任度下降", "": "未填写"}
voluntary = [r for r in unbinded if r["period_failed_count"] == 0]
fail_churn = [r for r in unbinded if r["period_failed_count"] > 0]
reason_stat = defaultdict(lambda: {"count": 0, "amount": 0})
for r in unbinded:
    reason_stat[reason_cn.get(r["unbind_reason"], r["unbind_reason"])]["count"] += 1
    reason_stat[reason_cn.get(r["unbind_reason"], r["unbind_reason"])]["amount"] += r["current_amount"]
out["cancel"] = {
    "unbind_rows": len(unbinded),
    "voluntary": len(voluntary),
    "voluntary_lost_mrr": sum(r["current_amount"] for r in voluntary),
    "fail_churn": len(fail_churn),
    "fail_churn_lost_mrr": sum(r["current_amount"] for r in fail_churn),
    "reasons": [{"reason": k, **v} for k, v in sorted(reason_stat.items(), key=lambda x: -x[1]["count"])],
    "rebind_count": sum(1 for r in rows if r["rebind_count"] > 0),
    "rebind_rows": [{"amount": r["current_amount"], "reason": reason_cn.get(r["unbind_reason"]), "channel": CH.get(r["channel_id"]), "contact": r["contact_status"]} for r in rows if r["rebind_count"] > 0],
    "try_unbind_rows": sum(1 for r in rows if r["try_unbind_count"] > 0),
    "try_unbind_retained": sum(1 for r in rows if r["try_unbind_count"] > 0 and r["status"] == "binded" and r["rebind_count"] == 0),
    "try_unbind_system": SM["range_summary"]["try_unbind_count"],
    "unbind_month_dist": [{"month": m, "count": sum(1 for r in unbinded if r["unbind_time"][:7] == m)} for m in MONTHS],
}

# ---------- 6. 提额 / 降额 ----------
up_rows = [r for r in rows if r["amount_up_count"] > 0]
down_rows = [r for r in rows if r["amount_down_count"] > 0]
def delta(r):
    arr = [a for a in r["monthly_paid_amounts"] if a > 0]
    return arr[-1] - arr[0] if arr else 0
up_delta = sum(delta(r) for r in up_rows)
down_delta = sum(delta(r) for r in down_rows)
out["amount_change"] = {
    "up_count": len(up_rows), "down_count": len(down_rows),
    "up_mrr_delta": up_delta, "down_mrr_delta": down_delta, "net_mrr_delta": up_delta + down_delta,
    "up_detail": [{"from": min((a for a in r["monthly_paid_amounts"] if a > 0), default=0), "to": r["current_amount"], "channel": CH.get(r["channel_id"]), "contact": r["contact_status"]} for r in up_rows],
    "down_detail": [{"to": r["current_amount"], "channel": CH.get(r["channel_id"]), "contact": r["contact_status"]} for r in down_rows],
}

# ---------- 7. 渠道 ----------
ch_stat = []
for cid, cname in sorted(CH.items()):
    if cid == 0: continue
    grp = [r for r in rows if r["channel_id"] == cid]
    if not grp: continue
    act = [r for r in grp if r["status"] == "binded"]
    ch_stat.append({
        "channel": cname, "total": len(grp), "active": len(act),
        "retention_pct": round(len(act) / len(grp) * 100, 1),
        "period_amount": sum(r["period_paid_amount"] for r in grp),
        "mrr_now": sum(r["current_amount"] for r in act),
        "avg_amount": round(sum(r["current_amount"] for r in act) / len(act), 1) if act else 0,
        "new_binds": len(grp),
        "repeat_share_pct": round(sum(1 for r in grp if r["contact_status"] == "repeat") / len(grp) * 100, 1),
        "failed_binds": sum(1 for r in grp if r["period_failed_count"] > 0),
        "unbind": sum(1 for r in grp if r["status"] == "unbind"),
    })
out["channels"] = sorted(ch_stat, key=lambda x: -x["period_amount"])

# ---------- 8. 人群洞察 ----------
# 新老捐赠人
def seg(rows_, key, val):
    grp = [r for r in rows_ if r[key] == val]
    act = [r for r in grp if r["status"] == "binded"]
    return {"count": len(grp), "active": len(act),
            "retention_pct": round(len(act) / len(grp) * 100, 1) if grp else 0,
            "period_amount": sum(r["period_paid_amount"] for r in grp),
            "mrr": sum(r["current_amount"] for r in act),
            "avg_amount": round(sum(r["current_amount"] for r in act) / len(act), 1) if act else 0}
out["segments"] = {
    "contact": {"new": seg(rows, "contact_status", "new"), "repeat": seg(rows, "contact_status", "repeat")},
}
# 高价值（现额>=200）
hv = [r for r in binded if r["current_amount"] >= 200]
out["segments"]["high_value"] = {"count": len(hv), "mrr": sum(r["current_amount"] for r in hv),
    "pct_of_active": ratio(len(hv) * 100, len(binded)),
    "mrr_pct": ratio(sum(r["current_amount"] for r in hv) * 100, out["integrity"]["dataset_mrr"])}
# 小额（现额<=20）
low = [r for r in rows if r["current_amount"] <= 20]
out["segments"]["low_value"] = {"count": len(low), "churned": sum(1 for r in low if r["status"] == "unbind"),
    "churn_pct": ratio(sum(1 for r in low if r["status"] == "unbind") * 100, len(low))}
# 尝试取消但被挽留人群
retained_try = [r for r in rows if r["try_unbind_count"] > 0 and r["status"] == "binded" and r["rebind_count"] == 0 and r["period_failed_count"] == 0]
out["segments"]["try_unbind_retained"] = {"count": len(retained_try), "mrr": sum(r["current_amount"] for r in retained_try)}

json.dump(out, open(os.path.join(BASE, "analysis.json"), "w"), ensure_ascii=False, indent=1)
print("rows:", len(rows), "| binded:", len(binded), "| unbind:", len(unbinded))
print("dataset MRR:", out["integrity"]["dataset_mrr"], "| dataset amount:", out["integrity"]["dataset_period_amount"])
print("OK -> analysis.json")
