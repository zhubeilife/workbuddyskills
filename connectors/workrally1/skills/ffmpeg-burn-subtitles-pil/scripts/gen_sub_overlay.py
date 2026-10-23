#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕图层渲染：subs.json → 每条 cue 一张全画布 RGBA 透明 PNG。
适用于 ffmpeg 无 ass/subtitles/drawtext 滤镜的环境，再由 ffmpeg overlay 合成。

版式默认值对齐 workrally-brand-film-pipeline §6a-2（中英短句字幕标准）：
  中上英下、各一行、底部居中、白字细黑描边；
  中文字号 ≈ 0.053×Ha，英文 ≈ 0.039×Ha（英文约为中文的 74%）；
  英文可见底缘距有效影像区底部 ≈ 0.03×Ha，两行可见间隙 ≈ 0.008×Ha。
以上是实现起点，须用原尺寸裁切 + 亮底对照校准，不是已验收值。

环境变量（均可选）：
  PROJ            项目根目录（读 99_工作底稿/subs.json，写 04_字幕/_overlay/）
  W, H            画布宽高（= 成片有效影像区像素，必须与底片一致）
  CN_FONT, CN_INDEX, EN_FONT, EN_INDEX   字体文件与 .ttc 索引
字体加载失败会直接报错退出，不回退到默认字体（回退会把中文渲染成方块且不报错）。
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PROJ = os.environ.get("PROJ")
if not PROJ:
    sys.exit("请设置环境变量 PROJ=<项目根目录>")
WD = os.path.join(PROJ, "99_工作底稿")
OUT = os.path.join(PROJ, "04_字幕", "_overlay")
os.makedirs(OUT, exist_ok=True)

W = int(os.environ.get("W", 1920))
H = int(os.environ.get("H", 1080))
HA = H

CN_FONT = os.environ.get("CN_FONT", "/System/Library/Fonts/STHeiti Medium.ttc")
CN_INDEX = int(os.environ.get("CN_INDEX", 1))
EN_FONT = os.environ.get("EN_FONT", "/System/Library/Fonts/HelveticaNeue.ttc")
EN_INDEX = int(os.environ.get("EN_INDEX", 0))

CN_SIZE = round(0.053 * HA)
EN_SIZE = round(0.039 * HA)
CN_STROKE = max(2, round(CN_SIZE / 20))
EN_STROKE = max(2, round(EN_SIZE / 20))
BOTTOM_MARGIN = round(0.03 * HA)
LINE_GAP = round(0.008 * HA)


def load_font(path, size, index):
    try:
        f = ImageFont.truetype(path, size, index=index)
    except OSError as e:
        sys.exit(f"字体加载失败：{path} index={index}：{e}（请用 CN_FONT/EN_FONT 指定本机存在的字体）")
    print(f"字体：{path} index={index} → {f.getname()}  size={size}")
    return f


cn_font = load_font(CN_FONT, CN_SIZE, CN_INDEX)
en_font = load_font(EN_FONT, EN_SIZE, EN_INDEX)

_probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def ref_box(font, stroke, sample):
    return _probe.textbbox((0, 0), sample, font=font, anchor="ls", stroke_width=stroke)


# 以固定参照字形确定两行基线，避免每条 cue 因有无降部字母而上下跳动
_en_ref = ref_box(en_font, EN_STROKE, "Hgjpqy")
_cn_ref = ref_box(cn_font, CN_STROKE, "中文字幕测试")
EN_BASELINE = H - BOTTOM_MARGIN - _en_ref[3]
EN_TOP = EN_BASELINE + _en_ref[1]
CN_BASELINE = EN_TOP - LINE_GAP - _cn_ref[3]


def draw_center(dr, text, font, stroke, baseline):
    b = dr.textbbox((0, 0), text, font=font, anchor="ls", stroke_width=stroke)
    w = b[2] - b[0]
    if w > W * 0.8:
        print(f"  ⚠️ 超过有效宽度 80%，请按 §6a-2 继续拆短句：{text}")
    x = (W - w) // 2 - b[0]
    dr.text((x, baseline), text, font=font, anchor="ls", fill=(255, 255, 255, 255),
            stroke_width=stroke, stroke_fill=(0, 0, 0, 235))


subs = json.load(open(os.path.join(WD, "subs.json")))
made = []
for i, s in enumerate(subs):
    cn, en = s.get("cn", ""), s.get("en", "")
    if not cn and not en:
        continue
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    if cn:
        draw_center(dr, cn, cn_font, CN_STROKE, CN_BASELINE)
    if en:
        draw_center(dr, en, en_font, EN_STROKE, EN_BASELINE)
    p = os.path.join(OUT, f"cue_{i:03d}.png")
    img.save(p, optimize=True)
    made.append((i, s.get("key"), round(s["start"], 3), round(s["end"], 3)))

print(f"生成 {len(made)} 张字幕图层 PNG → {OUT}（画布 {W}×{H}）")
shown = made if len(made) <= 9 else made[:6] + [None] + made[-3:]
for m in shown:
    print("   ..." if m is None else f"   {m}")
