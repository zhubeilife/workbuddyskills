#!/usr/bin/env python3
"""串行下载资产 + 完整性校验 + 按文件头真实格式命名（下载与完整性校验的唯一实现）。

- 必须串行：并行 curl 下载大文件会静默截断（文件头合法但数据流不完整）。
- 完整性：PNG 累积 IDAT 后 zlib 解压；JPEG 检查 SOI/EOI 并用 Pillow 完整解码；WEBP 检查 RIFF 长度并解码。
- 命名：扩展名一律按文件头真实格式（PNG→.png，JPEG→.jpg，WEBP→.webp），不按回执标签或 registry 里的扩展名。
- 结果（真实文件名、格式、宽高、字节数、校验结论）回写 registry，供后续 QC 与台账使用。

Usage:
  python3 fetch_assets.py --registry <assets_registry.json> --out <assets_dir> [--force]

registry 结构：
  {"assets": [{"code": "CHAR-01", "file": "CHAR-01", "download_url": "https://..."}, ...]}
  `file` 可带或不带扩展名，只取其主干名。
"""
import argparse
import json
import os
import struct
import subprocess
import sys
import zlib

EXT_BY_FMT = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}
KNOWN_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def sniff(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:3] == b"\xff\xd8\xff":
        return "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def png_ok(data):
    pos, idat = 8, b""
    while pos < len(data):
        (ln,) = struct.unpack(">I", data[pos:pos + 4])
        t = data[pos + 4:pos + 8]
        if t == b"IDAT":
            idat += data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    zlib.decompress(idat)


def pil_decode(path):
    try:
        from PIL import Image
    except ImportError:
        return None, None, "Pillow 未安装，未做完整解码"
    with Image.open(path) as im:
        im.load()
        return im.width, im.height, None


def verify(path):
    data = open(path, "rb").read()
    fmt = sniff(data)
    if fmt is None:
        return None, False, "未知格式（非 PNG/JPEG/WEBP）", None, None
    try:
        if fmt == "png":
            png_ok(data)
        elif fmt == "jpeg" and not data.rstrip(b"\x00").endswith(b"\xff\xd9"):
            return fmt, False, "JPEG 缺少 EOI，疑似截断", None, None
        elif fmt == "webp":
            (riff_len,) = struct.unpack("<I", data[4:8])
            if riff_len + 8 > len(data):
                return fmt, False, "WEBP RIFF 长度不足，疑似截断", None, None
        w, h, note = pil_decode(path)
    except Exception as e:  # noqa: BLE001
        return fmt, False, f"解码失败: {e}", None, None
    return fmt, True, note or "ok", w, h


def stem_of(name):
    base, ext = os.path.splitext(name)
    return base if ext.lower() in KNOWN_EXTS else name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--force", action="store_true", help="已存在也重新下载")
    a = ap.parse_args()

    reg = json.load(open(a.registry))
    os.makedirs(a.out, exist_ok=True)
    bad = 0
    for item in reg["assets"]:
        stem = stem_of(item.get("file") or item["code"])
        existing = [os.path.join(a.out, stem + e) for e in EXT_BY_FMT.values()
                    if os.path.exists(os.path.join(a.out, stem + e))]
        if existing and not a.force:
            path = existing[0]
        else:
            path = os.path.join(a.out, stem + ".download")
            r = subprocess.run(["curl", "-sL", "--fail", "--max-time", "300", "-o", path, item["download_url"]])
            if r.returncode != 0:
                print(f"FAIL {item['code']:<10} curl exit {r.returncode}（签名可能过期，用 asset_detail 重取 URL）")
                item["qc_download"] = "failed"
                bad += 1
                continue

        fmt, ok, why, w, h = verify(path)
        if fmt:
            final = os.path.join(a.out, stem + EXT_BY_FMT[fmt])
            if path != final:
                os.replace(path, final)
                path = final
        size = os.path.getsize(path)
        item.update({"file": os.path.basename(path), "format": fmt, "width": w, "height": h,
                     "bytes": size, "qc_download": "ok" if ok else "bad", "qc_note": why})
        flag = "OK " if ok else "BAD"
        bad += 0 if ok else 1
        print(f"{flag} {item['code']:<10} {fmt or '?':<5} {w}x{h}  {size / 1e6:.2f}MB  {os.path.basename(path)}  {why}")

    json.dump(reg, open(a.registry, "w"), ensure_ascii=False, indent=2)
    print(f"\n合计: {len(reg['assets'])} 条，异常: {bad}（结果已回写 {a.registry}）")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
