#!/usr/bin/env python3
"""把 weaver-work-cli 发票查询的完整 JSON envelope 裁成语义摘要。

为什么需要它
------------
`invoice.list` / `invoice.enterprise.list` 的原始输出里，单条发票有 40+ 字段
（`custom_field_*`、`rb`、`oa`、`suser`、`agricultural_*` 等对调用方无用），
10 条就是 35KB 左右。要拿到"号码 / 金额 / 购销方"就得先解析一遍。

优先用 CLI 原生能力
------------------
CLI 0.1.17 起支持 `--view summary`（语义平表）与 `--fields a,b.c`（点路径投影），
Agent 应当优先用它们，不必写脚本：

    weaver-work-cli --json invoice list --view summary

本脚本用于以下兜底场景：
  1. 目标机器上的 CLI 版本低于 0.1.17，没有 `--view summary`
  2. 需要把结果整理成 markdown 表格直接贴给用户
  3. 需要在多份导出文件之间做汇总核对

用法
----
    weaver-work-cli --json invoice run invoice.list --input-json '{"page_size":10}' > list.json
    python invoice-summarize.py list.json
    python invoice-summarize.py list.json --format table
    weaver-work-cli --json invoice list | python invoice-summarize.py -

输入可以是：完整 envelope、`data` 对象、`{items:[...]}`，或 E10 原生 `{infos:[...]}` 响应。

字段口径与 CLI `--view summary` 保持一致（见 references/invoice-output-view.md）。
"""

from __future__ import annotations

import argparse
import json
import sys

# 与 src/shortcuts/invoice/projection.ts 的 SUMMARY_ITEM_FIELDS 保持同序同义
SUMMARY_FIELDS = [
    "fid",
    "number",
    "code",
    "typeName",
    "date",
    "amount",
    "total",
    "taxAmount",
    "buyer",
    "buyerTaxNo",
    "payer",
    "payerTaxNo",
    "valid",
    "status",
    "reimState",
    "reimRequests",
    "fileName",
    "detailUrl",
]

TABLE_COLUMNS = [
    ("number", "发票号码"),
    ("typeName", "类型"),
    ("date", "开票日期"),
    ("total", "价税合计"),
    ("payer", "销方"),
    ("buyer", "购方"),
    ("reimRequests", "关联报销单"),
]


def as_dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).lstrip("\ufeff").strip()


def as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def summarize_item(item: dict) -> dict:
    """把一条原始发票对象裁成语义摘要；空值省键，票面自带的 '0' 保留。"""
    comm = as_dict(item.get("comm_info"))
    pro = as_dict(comm.get("pro"))
    price = as_dict(comm.get("price"))
    buyer = as_dict(comm.get("buyer"))
    payer = as_dict(comm.get("payer"))
    modify = as_dict(item.get("modify_info"))
    oreim = as_dict(item.get("oreim"))
    reim_list = oreim.get("list_reim") if isinstance(oreim.get("list_reim"), list) else []

    summary = {
        "fid": as_text(item.get("fid") or item.get("id")),
        "number": as_text(item.get("number")),
        "code": as_text(item.get("code")),
        "typeName": as_text(pro.get("cname")),
        "date": as_text(pro.get("date")),
        "amount": as_text(price.get("amount")),
        "total": as_text(price.get("total")),
        "taxAmount": as_text(price.get("dtax")),
        "buyer": as_text(buyer.get("company")),
        "buyerTaxNo": as_text(buyer.get("tcode")),
        "payer": as_text(payer.get("company")),
        "payerTaxNo": as_text(payer.get("tcode")),
        "valid": as_int(pro.get("valid")),
        "status": as_int(pro.get("status")),
        "reimState": as_int(pro.get("sreim")),
        "reimRequests": [as_text(as_dict(entry).get("name")) for entry in reim_list if as_text(as_dict(entry).get("name"))],
        "fileName": as_text(modify.get("fname")),
        "detailUrl": as_text(item.get("detailUrl")),
    }
    return {key: value for key, value in summary.items() if value not in ("", None, [])}


def extract_items(payload: object) -> tuple[list, dict]:
    """兼容 envelope / data / items / E10 原生 infos 四种输入形状。"""
    root = as_dict(payload)
    data = as_dict(root.get("data")) or root
    for key in ("items", "infos"):
        candidate = data.get(key)
        if isinstance(candidate, list):
            return candidate, data
    if isinstance(payload, list):
        return payload, {}
    return [], data


def summarize_payload(payload: object) -> dict:
    items, data = extract_items(payload)
    summary = {}
    for key in ("total", "totalAmount", "totalAmountExcludingTax", "hasMore", "scope"):
        if data.get(key) is not None:
            summary[key] = data[key]
    summary["items"] = [summarize_item(as_dict(item)) for item in items]
    summary["itemCount"] = len(summary["items"])
    return summary


def render_cell(item: dict, key: str) -> str:
    value = item.get(key)
    if key == "reimRequests":
        names = value if isinstance(value, list) else []
        if not names:
            return "-"
        return names[0] if len(names) == 1 else f"{names[0]} 等 {len(names)} 笔"
    return str(value) if value is not None else ""


def render_table(summary: dict) -> str:
    lines = []
    header = "| " + " | ".join(label for _, label in TABLE_COLUMNS) + " |"
    divider = "|" + "---|" * len(TABLE_COLUMNS)
    lines.append(header)
    lines.append(divider)
    for item in summary["items"]:
        cells = [render_cell(item, key) for key, _ in TABLE_COLUMNS]
        lines.append("| " + " | ".join(cells) + " |")

    parts = [f"共 {summary.get('itemCount', 0)} 张"]
    if summary.get("total") is not None:
        parts.append(f"票夹总数 {summary['total']}")
    if summary.get("totalAmount") is not None:
        parts.append(f"价税合计 {summary['totalAmount']}")
    if summary.get("hasMore"):
        parts.append("还有更多（hasMore=true）")
    lines.append("")
    lines.append("；".join(parts))
    lines.append("")
    lines.append("注：`reimState`（票面 `comm_info.pro.sreim`）的取值语义未在 CLI 契约中定义，只能原样呈现，不要自行解读成已报销/未报销。")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="把 weaver-work-cli 发票查询的完整 JSON 输出裁成语义摘要（CLI --view summary 的兜底方案）",
    )
    parser.add_argument("path", help="JSON 文件路径，或 - 表示从标准输入读取")
    parser.add_argument("--format", choices=["json", "table"], default="json", help="json=摘要对象（默认），table=markdown 表格")
    parser.add_argument("--indent", type=int, default=1, help="json 格式的缩进，默认 1")
    args = parser.parse_args(argv)

    if args.path == "-":
        raw = sys.stdin.read()
    else:
        try:
            with open(args.path, encoding="utf-8-sig") as handle:
                raw = handle.read()
        except OSError as error:
            print(f"无法读取 {args.path}：{error}", file=sys.stderr)
            return 1

    try:
        payload = json.loads(raw.lstrip("\ufeff"))
    except json.JSONDecodeError as error:
        print(f"{args.path} 不是合法 JSON：{error}", file=sys.stderr)
        return 1

    summary = summarize_payload(payload)
    if args.format == "table":
        print(render_table(summary))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=args.indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
