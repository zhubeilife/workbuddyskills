#!/usr/bin/env python3
"""解析 MCP 超限自动落盘的原始响应文件 → 精简 compact JSONL 批次。

用法:
  python3 pull_dump.py <dump_file> <raw_dir> <batch_name> [--save-cursor <file>]

说明:
  - MCP 大页响应（如 limit=200）常因超 token 被客户端自动保存为 .txt 文件，
    本脚本把该原始 JSON 按「数据管道准则」裁剪为单行 JSONL，模型不必手写数据。
  - 自动把 envelope 中的 next_cursor 写入 <raw_dir>/../_next_cursor.txt
    （传 --save-cursor 可自定义路径）。
"""
import json
import os
import sys


def compress(record: dict) -> dict:
    fields = []
    for f in record.get("fields", []):
        fields.append({
            "key": f.get("key"),
            "name": f.get("name"),
            "type": f.get("type", ""),
            "value": f.get("value", ""),
        })
    out = {
        "fill_id": record.get("fill_id"),
        "submit_time": record.get("submit_time"),
    }
    if record.get("latest_remark") is not None:
        out["latest_remark"] = record.get("latest_remark")
    if fields:
        out["fields"] = fields
    return out


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 2

    dump_path = sys.argv[1]
    raw_dir = sys.argv[2]
    batch_name = sys.argv[3]
    cursor_file = None
    if "--save-cursor" in sys.argv:
        i = sys.argv.index("--save-cursor")
        cursor_file = sys.argv[i + 1]

    with open(dump_path, encoding="utf-8") as fh:
        data = json.load(fh)

    if data.get("isError"):
        raise SystemExit("MCP returned an error; no batch written")
    if "content" in data:
        payloads = []
        for item in data["content"]:
            if item.get("type") == "text":
                try:
                    payload = json.loads(item.get("text", ""))
                except (TypeError, ValueError):
                    continue
                if isinstance(payload, dict) and "submissions" in payload:
                    payloads.append(payload)
        if len(payloads) != 1:
            raise SystemExit("Expected exactly one submissions payload; no batch written")
        data = payloads[0]
    if data.get("data_masked") is not True or not isinstance(data.get("submissions"), list):
        raise SystemExit("Expected masked submissions response; no batch written")
    if not isinstance(data.get("has_more"), bool) or (data["has_more"] and not data.get("next_cursor")):
        raise SystemExit("Missing pagination state; no batch written")
    os.makedirs(raw_dir, exist_ok=True)
    subs = data["submissions"]
    form = data.get("form", {})
    out_path = os.path.join(raw_dir, batch_name)
    with open(out_path, "w", encoding="utf-8") as fh:
        for r in subs:
            fh.write(json.dumps(compress(r), ensure_ascii=False) + "\n")
    with open(out_path + ".meta.json", "w", encoding="utf-8") as fh:
        json.dump({key: data.get(key) for key in ("data_masked", "has_more", "next_cursor", "form")}, fh,
                  ensure_ascii=False)

    cursor = data.get("next_cursor")
    if cursor_file:
        with open(cursor_file, "w") as fh:
            fh.write(cursor or "")
    else:
        # default: <raw_dir>/../_next_cursor.txt
        parent = os.path.dirname(os.path.normpath(raw_dir))
        with open(os.path.join(parent, "_next_cursor.txt"), "w") as fh:
            fh.write(cursor or "")

    print(f"OK {batch_name}: {len(subs)} rows | form={form.get('title')} "
          f"| has_more={data.get('has_more')} | next_cursor={cursor}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
