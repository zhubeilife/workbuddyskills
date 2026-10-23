#!/usr/bin/env python3
"""Analyze merged Lingxi form submissions without emitting row-level data."""
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


SENSITIVE_WORDS = ("姓名", "名字", "手机", "电话", "邮箱", "邮件", "身份证", "证件", "地址")
SENSITIVE_TYPES = {"name", "mobile", "phone", "email", "idcard", "identity", "address"}
MULTI_TYPES = {"checkbox", "multiple", "multi_select", "multiselect", "select_multi"}
CATEGORY_TYPES = {"radio", "select", "dropdown", "checkbox", "multiple", "multi_select", "multiselect", "select_multi"}


def load(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save(path, value):
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def is_sensitive(field):
    name = str(field.get("name", "")).lower()
    field_type = str(field.get("type", "")).lower()
    return field_type in SENSITIVE_TYPES or any(word in name for word in SENSITIVE_WORDS)


def period(value):
    value = str(value or "")[:10]
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m")
    except ValueError:
        return "未知"


def split_values(value, field_type):
    text = str(value or "").strip()
    if not text:
        return []
    if field_type in MULTI_TYPES or "；" in text:
        return [item.strip() for item in text.replace(";", "；").split("；") if item.strip()]
    return [text]


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: analyze.py <data-dir>")
    data_dir = Path(sys.argv[1]).resolve()
    payload = load(data_dir / "submissions.json")
    if payload.get("data_masked") is not True:
        raise SystemExit("Refusing shared dashboard analysis: submissions.json must have data_masked=true")

    submissions = list(payload.get("submissions") or [])
    timeline = Counter(period(row.get("submit_time")) for row in submissions)
    remarked = sum(1 for row in submissions if str(row.get("latest_remark", "")).strip())

    fields = {}
    values = defaultdict(list)
    for submission in submissions:
        for field in submission.get("fields") or []:
            key = str(field.get("key") or field.get("name") or "")
            if not key or is_sensitive(field):
                continue
            fields.setdefault(key, {
                "key": key,
                "name": str(field.get("name") or key),
                "type": str(field.get("type") or "").lower(),
            })
            values[key].append(str(field.get("value") or "").strip())

    distributions = []
    open_text = []
    total = len(submissions)
    for key, field in fields.items():
        raw = values[key]
        non_empty = [value for value in raw if value]
        unique = set(non_empty)
        field_type = field["type"]
        categorical = field_type in CATEGORY_TYPES or (non_empty and len(unique) <= 12 and max(map(len, unique)) <= 40)
        if categorical:
            counts = Counter()
            for value in non_empty:
                counts.update(split_values(value, field_type))
            options = [
                {"label": label, "count": count, "share": round(count / total * 100, 1) if total else 0}
                for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:15]
            ]
            distributions.append({
                **field,
                "answered_count": len(non_empty),
                "blank_count": total - len(non_empty),
                "options": options,
            })
        else:
            open_text.append({
                **field,
                "answered_count": len(non_empty),
                "blank_count": total - len(non_empty),
                "average_length": round(sum(map(len, non_empty)) / len(non_empty), 1) if non_empty else 0,
            })

    distributions.sort(key=lambda item: (-item["answered_count"], item["name"]))
    open_text.sort(key=lambda item: (-item["answered_count"], item["name"]))
    output = {
        "form": payload.get("form") or {},
        "overview": {
            "submission_count": total,
            "remarked_count": remarked,
            "unremarked_count": total - remarked,
            "remarked_rate": round(remarked / total * 100, 1) if total else 0,
            "first_submit_time": min((str(row.get("submit_time") or "") for row in submissions), default=""),
            "last_submit_time": max((str(row.get("submit_time") or "") for row in submissions), default=""),
        },
        "timeline": [{"period": key, "count": timeline[key]} for key in sorted(timeline)],
        "field_distributions": distributions,
        "open_text_fields": open_text,
        "privacy": {"data_masked": True, "contains_row_level_data": False},
    }
    save(data_dir / "analysis.json", output)
    print("OK ->", data_dir / "analysis.json")


if __name__ == "__main__":
    main()
