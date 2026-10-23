#!/usr/bin/env python3
"""批量资产联络图（§2f/规则：不抽样，逐格看完再列返工清单）。
CHAR/CROWD 4列、PROP 4列、SC 1列，每格左上角烤编号。
资产文件按真实格式命名（.png / .jpg / .webp），三种扩展名都会收录。

Usage:
  python3 contact_sheet.py --assets <assets_dir> --outdir <qc_dir>
"""
import argparse
import glob
import os

from PIL import Image, ImageDraw, ImageFont

EXTS = (".png", ".jpg", ".jpeg", ".webp")
PUA = "\ue001"  # 私用区码位，任何字体都必然缺此字形

# 联络图标签含中文资产名，必须用能渲染 CJK 的字体。
# 加载后必须实测验证（见 load_label_font），不静默回退默认字体——那会把中文渲染成方块且不报错。
CJK_CANDIDATES = (
    ("/System/Library/Fonts/STHeiti Medium.ttc", 1),    # Heiti SC
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0),    # Heiti TC
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),  # W3
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 2),  # W6
    ("/System/Library/Fonts/PingFang.ttc", 1),
    ("/Library/Fonts/Arial Unicode.ttf", 0),
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
)
ASCII_FALLBACK = "/System/Library/Fonts/Helvetica.ttc"


def _ink(font, ch):
    """渲染单字并数墨点，用于判断字体是否有该字形。"""
    im = Image.new("L", (48, 48), 0)
    ImageDraw.Draw(im).text((2, 2), ch, font=font, fill=255)
    return sum(1 for p in im.getdata() if p > 40)


def load_label_font(size):
    """返回 (font, cjk_ok, 来源)。以「母」与私用区码位的墨点是否相同判定 CJK 字形是否存在。"""
    env = os.environ.get("LABEL_FONT")
    cands = ([(env, int(os.environ.get("LABEL_FONT_INDEX", "0")))] if env else []) + list(CJK_CANDIDATES)
    for path, idx in cands:
        if not os.path.exists(path):
            continue
        try:
            fnt = ImageFont.truetype(path, size, index=idx)
        except Exception:  # noqa: BLE001
            continue
        cjk_ink = _ink(fnt, "母")
        if cjk_ink > 0 and cjk_ink != _ink(fnt, PUA):
            return fnt, True, f"{path}#{idx}"
    try:
        return ImageFont.truetype(ASCII_FALLBACK, size), False, ASCII_FALLBACK
    except Exception:  # noqa: BLE001
        return ImageFont.load_default(), False, "PIL default"

GROUPS = {
    "CHAR": (("CHAR-", "CROWD-"), 4, 420),
    "PROP": (("PROP-",), 4, 460),
    "SC": (("SC-",), 1, 900),
}


def collect(assets_dir, prefixes):
    files = []
    for p in prefixes:
        for f in glob.glob(os.path.join(assets_dir, p + "*")):
            if os.path.splitext(f)[1].lower() in EXTS:
                files.append(f)
    return sorted(files)


def build(name, files, cols, cell, outdir):
    if not files:
        print(f"跳过 {name}: 无文件")
        return
    rows = (len(files) + cols - 1) // cols
    fnt, cjk_ok, fpath = load_label_font(26)
    grid = Image.new("RGB", (cols * cell, rows * cell), (26, 26, 28))
    d = ImageDraw.Draw(grid)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        im.thumbnail((cell - 8, cell - 8))
        x = (i % cols) * cell + (cell - im.width) // 2
        y = (i // cols) * cell + (cell - im.height) // 2
        grid.paste(im, (x, y))
        label = os.path.splitext(os.path.basename(f))[0]
        if not cjk_ok:  # 无 CJK 字体时降级为 ASCII，宁可少字也不出方块
            label = label.encode("ascii", "replace").decode("ascii")
        x0, y0 = (i % cols) * cell, (i // cols) * cell
        bx = d.textbbox((0, 0), label, font=fnt)
        d.rectangle([x0, y0, x0 + (bx[2] - bx[0]) + 20, y0 + (bx[3] - bx[1]) + 14], fill=(0, 0, 0))
        d.text((x0 + 10, y0 + 5), label, font=fnt, fill=(255, 235, 120))
    out = os.path.join(outdir, f"SHEET_{name}.png")
    grid.save(out)
    print(f"{out}  ({len(files)} 张, 标签字体 {fpath}{'' if cjk_ok else ' ⚠️无CJK字形'})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default="assets")
    ap.add_argument("--outdir", default="qc")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    for n, (prefixes, c, cell) in GROUPS.items():
        build(n, collect(a.assets, prefixes), c, cell, a.outdir)
