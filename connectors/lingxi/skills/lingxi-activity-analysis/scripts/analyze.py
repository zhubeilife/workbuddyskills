#!/usr/bin/env python3
"""Analyze Lingxi activity summary and masked signup/signin lists."""
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


def load(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save(path, value):
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def day(value):
    value = str(value or "")[:10]
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return "未知"


def hour(value):
    value = str(value or "")
    try:
        return datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S").strftime("%H:00")
    except ValueError:
        return "未知"


def counter_rows(counter, key):
    return [{key: name, "count": count} for name, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: analyze.py <data-dir>")
    data_dir = Path(sys.argv[1]).resolve()
    summary = load(data_dir / "summary.json")
    signup_payload = load(data_dir / "signups.json")
    signin_payload = load(data_dir / "signins.json")
    if signup_payload.get("data_masked") is not True or signin_payload.get("data_masked") is not True:
        raise SystemExit("Refusing shared dashboard analysis: signup and signin data must be masked")

    signups = list(signup_payload.get("signups") or [])
    signins = list(signin_payload.get("signins") or [])
    metrics = summary.get("metrics") or {}
    payment = summary.get("payment_summary") or {"is_paid_activity": False}

    signup_timeline = Counter(day(item.get("signup_time")) for item in signups)
    signin_timeline = Counter(day(item.get("signin_time")) for item in signins)
    signup_sources = Counter(str(item.get("source") or "unknown") for item in signups)
    signup_statuses = Counter(str(item.get("status_text") or item.get("status") or "未知") for item in signups)
    signin_sources = Counter(str(item.get("source") or "unknown") for item in signins)
    signin_hours = Counter(hour(item.get("signin_time")) for item in signins)
    remarked = sum(1 for item in signups if str(item.get("latest_remark") or "").strip())

    output = {
        "activity": summary.get("activity") or signup_payload.get("activity") or {},
        "overview": {
            "signup_count": len(signups),
            "signup_success_count": int(metrics.get("signup_success_count") or 0),
            "signup_cancel_count": int(metrics.get("signup_cancel_count") or 0),
            "signed_in_people_count": int(metrics.get("signed_in_people_count") or 0),
            "signin_count": int(metrics.get("signin_count") or 0),
            "signin_rate": float(metrics.get("signin_rate") or 0),
            "signout_count": int(metrics.get("signout_count") or 0),
            "total_log_time": float(metrics.get("total_log_time") or 0),
            "average_log_time": float(metrics.get("average_log_time") or 0),
            "remarked_count": remarked,
            "unremarked_count": len(signups) - remarked,
            "pv": int(metrics.get("pv") or 0),
            "uv": int(metrics.get("uv") or 0),
        },
        "signup_timeline": [{"period": key, "count": signup_timeline[key]} for key in sorted(signup_timeline)],
        "signin_timeline": [{"period": key, "count": signin_timeline[key]} for key in sorted(signin_timeline)],
        "signup_sources": counter_rows(signup_sources, "source"),
        "signup_statuses": counter_rows(signup_statuses, "status"),
        "signin_sources": counter_rows(signin_sources, "source"),
        "signin_hours": [{"hour": key, "count": signin_hours[key]} for key in sorted(signin_hours)],
        "sessions": summary.get("sessions") or [],
        "payment": {
            "is_paid_activity": bool(payment.get("is_paid_activity")),
            "order_signup_count": int(payment.get("order_signup_count") or 0),
            "paid_signup_count": int(payment.get("paid_signup_count") or 0),
            "unpaid_signup_count": int(payment.get("unpaid_signup_count") or 0),
            "payment_success_order_count": int(payment.get("payment_success_order_count") or 0),
            "payment_success_amount": float(payment.get("payment_success_amount") or 0),
            "average_paid_amount": float(payment.get("average_paid_amount") or 0),
            "refunding_amount": float(payment.get("refunding_amount") or 0),
            "refunded_amount": float(payment.get("refunded_amount") or 0),
            "net_received_amount": float(payment.get("net_received_amount") or 0),
        },
        "tickets": summary.get("ticket_breakdown") or [],
        "metric_notes": summary.get("metric_notes") or [],
        "privacy": {"data_masked": True, "contains_row_level_data": False},
    }
    save(data_dir / "analysis.json", output)
    print("OK ->", data_dir / "analysis.json")


if __name__ == "__main__":
    main()
