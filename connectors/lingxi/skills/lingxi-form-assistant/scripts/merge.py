#!/usr/bin/env python3
"""Merge one collection snapshot into submissions.json with local progress metadata.

Raw layout:
    <data_dir>/raw/<form_id>/batch_01.jsonl
    <data_dir>/raw/<form_id>/batch_02.jsonl
    ...
Each batch requires .jsonl.meta.json from pull_dump.py with data_masked=true.
Each JSONL line is ONE compact submission:
    {"fill_id": "...", "submit_time": "2026-09-01 10:00:00",
     "latest_remark": "...", "fields": [{"key","name","type","value"}, ...]}

Outputs:
    <data_dir>/submissions.json   (input for analyze.py, data_masked=true)
    <data_dir>/cache/<form_id>.json  (sync state for incremental fetch)

Design:
    * rerunning the same local batches is idempotent; encrypted IDs may differ on refetch
    * only merges one form per data dir; multiple forms -> error (each form 用独立 data 目录)
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def row_id(row):
    """Local-batch key only; not a stable identity across server requests."""
    for key in ("fill_id", "id", "submission_id", "record_id"):
        value = row.get(key)
        if value:
            return "id:" + str(value)
    payload = json.dumps(
        {"t": row.get("submit_time"), "f": row.get("fields")},
        ensure_ascii=False, sort_keys=True,
    )
    return "fp:" + hashlib.sha1(payload.encode("utf-8")).hexdigest()


REMARK_KEYS = ("latest_remark", "remark", "remark_text", "last_remark", "latestRemark", "handle_remark")


def pick_remark(row):
    for key in REMARK_KEYS:
        value = row.get(key)
        if value:
            return str(value)
    for field in row.get("fields") or []:
        if not isinstance(field, dict):
            continue
        name = str(field.get("name") or "")
        key = str(field.get("key") or "")
        if "备注" in name or "remark" in name.lower() or "remark" in key.lower():
            value = field.get("value")
            if value:
                return str(value)
    return ""


def normalize(row):
    """Keep only fields downstream can use; drop the rest of the envelope."""
    fields = []
    for field in row.get("fields") or []:
        if not isinstance(field, dict):
            continue
        key = str(field.get("key") or field.get("name") or "").strip()
        if not key:
            continue
        fields.append({
            "key": key,
            "name": str(field.get("name") or key),
            "type": str(field.get("type") or "").lower(),
            "value": field.get("value"),
        })
    return {
        "fill_id": str(row.get("fill_id") or row.get("id") or ""),
        "submit_time": str(row.get("submit_time") or row.get("filled_at") or ""),
        "latest_remark": pick_remark(row),
        "fields": fields,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", help="工作目录下的 data 目录")
    parser.add_argument("--form-id", default="", help="表单 ID（有 cache 时可选）")
    parser.add_argument("--title", default="", help="表单名称（有 cache 时可选）")
    parser.add_argument("--caught-up", action="store_true",
                        help="已翻到 has_more=false / 最新端，标记同步完整")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    raw_root = data_dir / "raw"
    if not raw_root.is_dir():
        raise SystemExit("No raw dir: %s" % raw_root)

    form_dirs = [p for p in sorted(raw_root.iterdir()) if p.is_dir()]
    if not form_dirs:
        raise SystemExit("No batches under %s (expected raw/<form_id>/batch_*.jsonl)" % raw_root)
    if len(form_dirs) > 1:
        raise SystemExit("Multiple forms in one data dir: %s. Use a dedicated data dir per form."
                         % ", ".join(p.name for p in form_dirs))
    form_id = args.form_id or form_dirs[0].name
    batches = sorted(form_dirs[0].glob("batch_*.jsonl"))
    if not batches:
        raise SystemExit("No batch_*.jsonl under %s" % form_dirs[0])

    merged = {}
    raw_count = 0
    for batch in batches:
        meta_path = Path(str(batch) + ".meta.json")
        if not meta_path.exists() or load(meta_path).get("data_masked") is not True:
            raise SystemExit("Missing masked-response metadata for %s; re-export via pull_dump.py" % batch.name)
        for line in batch.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            raw_count += 1
            merged[row_id(row)] = normalize(row)

    submissions = list(merged.values())
    submissions.sort(key=lambda row: str(row["submit_time"]))
    total = len(submissions)

    # 缓存读取与增量计算
    cache_path = data_dir / "cache" / (form_id + ".json")
    previous = load(cache_path) if cache_path.exists() else {}
    prev_total = (previous.get("sync") or {}).get("total_count")
    delta = total - prev_total if isinstance(prev_total, int) else None

    title = args.title or (previous.get("form") or {}).get("title") or form_dirs[0].name
    form_meta = {"form_id": form_id, "title": title}
    save(data_dir / "submissions.json", {
        "form": form_meta,
        "data_masked": True,
        "submissions": submissions,
    })

    # 同步状态
    times = [row["submit_time"] for row in submissions if row["submit_time"]]
    newest = submissions[-1] if submissions else {}
    oldest = submissions[0] if submissions else {}
    sync = {
        "total_count": total,
        "newest_submit_id": newest.get("fill_id", ""),
        "newest_submit_time": newest.get("submit_time", ""),
        "oldest_submit_id": oldest.get("fill_id", ""),
        "oldest_submit_time": oldest.get("submit_time", ""),
        "reached_oldest": bool(args.caught_up) or bool((previous.get("sync") or {}).get("reached_oldest")),
        "last_sync_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save(cache_path, {"form": form_meta, "sync": sync})

    print("merged: %d rows from %d batch file(s) (raw lines %d)" % (total, len(batches), raw_count))
    print("form: %s | %s" % (form_id, title))
    if delta is not None:
        print("delta vs cache: %+d (cache had %d)" % (delta, prev_total))
    else:
        print("delta vs cache: n/a (first sync in this dir)")
    print("range: %s -> %s" % (sync["oldest_submit_time"] or "-", sync["newest_submit_time"] or "-"))
    print("OK -> %s" % (data_dir / "submissions.json"))
    print("OK -> %s" % cache_path)


if __name__ == "__main__":
    main()
