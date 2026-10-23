#!/usr/bin/env python3
"""批量生图下载入口（MCP 版）：按 title 前缀筛出资产 → 生成 registry → 交给 workrally-asset-qc 串行下载与校验。

下载与完整性校验的唯一实现在 `workrally-asset-qc/scripts/fetch_assets.py`
（串行下载、PNG/JPEG/WEBP 完整性校验、按文件头真实格式命名）。本脚本只负责筛选与生成 registry，
不做并发下载，也不发起任何 WorkRally API 调用。

Usage:
  # 1) Agent 先调 MCP: asset_search(project_id="<PID>", material_type=["image"], page_size=100)
  #    把返回原样写入 /tmp/workrally/assets.json
  # 2) 再跑本脚本：
  python3 download_assets.py /tmp/workrally/assets.json ./out/ CAT01_,CAT02_,AI_TIER

若返回里 asset_details.url 缺失或已过期（签名有时效），
先让 Agent 调 asset_detail(asset_ids=[...])（一次最多 50 个）重新取 URL 再下载。

输入 JSON 结构假设（asset_search 返回）：
    {"assets": [{"id": "...", "title": "...", "asset_details": {"url": "https://..."}}, ...]}
"""
import json
import os
import subprocess
import sys
from pathlib import Path

FETCH = Path(__file__).resolve().parents[2] / "workrally-asset-qc" / "scripts" / "fetch_assets.py"

if len(sys.argv) < 4:
    print("Usage: download_assets.py <assets.json> <out_dir> <prefix1,prefix2,...>")
    sys.exit(1)

assets_path = sys.argv[1]
out_dir = Path(sys.argv[2])
prefixes = [p for p in sys.argv[3].split(",") if p]
out_dir.mkdir(parents=True, exist_ok=True)

with open(assets_path) as f:
    data = json.load(f)

if isinstance(data, list):
    assets = data
else:
    assets = data.get("assets") or data.get("data") or data.get("list") or []

registry, skipped_no_url = [], []
for a in assets:
    title = os.path.splitext(a.get("title") or "")[0]
    if not any(title.startswith(p) for p in prefixes):
        continue
    details = a.get("asset_details") or {}
    url = details.get("download_url") or details.get("url") or ""
    if not url:
        skipped_no_url.append(title)
        continue
    registry.append({"code": title, "file": title.lower(), "asset_id": a.get("id"), "download_url": url})

reg_path = out_dir / "assets_registry.json"
json.dump({"assets": registry}, open(reg_path, "w"), ensure_ascii=False, indent=2)
print(f"registry: {reg_path}（{len(registry)} 条）", flush=True)

if skipped_no_url:
    print(f"⚠️ {len(skipped_no_url)} 条无可用 URL（签名可能过期），请先用 asset_detail 重取：")
    for t in skipped_no_url[:10]:
        print("   -", t)

if not FETCH.exists():
    print(f"❌ 未找到 {FETCH}，请确认同插件内的 workrally-asset-qc 技能存在")
    sys.exit(2)

sys.exit(subprocess.run([sys.executable, str(FETCH), "--registry", str(reg_path), "--out", str(out_dir)]).returncode)
