#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合成路径 A：字幕图层视频 + 单次 overlay。
cue PNG（gen_sub_overlay.py 产出）与透明垫片按帧级时间轴交替 → concat 成一条图层流 → 对底片做一次 overlay。

时间轴规则（与路径 B 相同，对齐 workrally-brand-film-pipeline §6a-1 / §6a-2）：
- subs.json 的 start/end 必须是**成片时间**（词级语音时间经真实剪辑映射换算、偏移只加一次）；
  本脚本不做设计网格换算，也不填补缺失时间。
- 按帧量化为半开区间 [start_frame, end_frame)，相邻 cue 不在边界帧同时出现，不累积舍入漂移。
- 交叠时**把前一条的终点截到后一条的起点**（后一条保持开口时刻），不推迟后一条。

用法：
  PROJ=<项目根> BASE=<无字幕母版.mp4> OUT=<输出.mp4> python3 gen_sub_layer.py [--dry] [--tlimit=秒]
  subs.json 位于 $PROJ/99_工作底稿/subs.json，cue PNG 位于 $PROJ/04_字幕/_overlay/cue_XXX.png
"""
import json
import os
import subprocess
import sys
from fractions import Fraction

from PIL import Image

PROJ = os.environ.get("PROJ")
BASE = os.environ.get("BASE")
OUT = os.environ.get("OUT")
if not (PROJ and BASE and OUT):
    sys.exit("请设置环境变量 PROJ、BASE（无字幕母版）、OUT（输出文件）")
WD = os.path.join(PROJ, "99_工作底稿")
OV = os.path.join(PROJ, "04_字幕", "_overlay")


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    j = json.loads(r.stdout)
    s = j["streams"][0]
    return int(s["width"]), int(s["height"]), Fraction(s["r_frame_rate"]), float(j["format"]["duration"])


W, H, FPS, TOTAL = probe(BASE)
TOTAL_F = int(TOTAL * FPS)

blank = os.path.join(OV, "transparent.png")
if not os.path.exists(blank) or Image.open(blank).size != (W, H):
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)

subs = json.load(open(os.path.join(WD, "subs.json")))
cues = []
for i, s in enumerate(subs):
    path = os.path.join(OV, f"cue_{i:03d}.png")
    if not os.path.exists(path):
        continue
    if Image.open(path).size != (W, H):
        sys.exit(f"❌ {path} 尺寸与底片 {W}×{H} 不一致")
    sf = round(float(s["start"]) * FPS)
    ef = min(round(float(s["end"]) * FPS), TOTAL_F)
    if sf < ef:
        cues.append([sf, ef, path, s.get("key", i)])
cues.sort(key=lambda c: c[0])

truncated = 0
for a, b in zip(cues, cues[1:]):
    if a[1] > b[0]:
        a[1] = b[0]
        truncated += 1
cues = [c for c in cues if c[0] < c[1]]

segs, cursor = [], 0
for sf, ef, path, _ in cues:
    if sf > cursor:
        segs.append((blank, sf - cursor))
    segs.append((path, ef - sf))
    cursor = ef
if cursor < TOTAL_F:
    segs.append((blank, TOTAL_F - cursor))

print(f"底片 {W}×{H} @ {float(FPS):.3f}fps，{TOTAL_F} 帧；cue {len(cues)} 条（交叠截断 {truncated} 处），图层段 {len(segs)}")

ins, fc, labels = [], [], []
for k, (path, nframes) in enumerate(segs):
    # -t 取略大于 n 帧的上界，再用 trim=end_frame 精确截到 n 帧，避免秒数舍入导致的逐段漂移
    ins += ["-loop", "1", "-framerate", str(FPS), "-t", f"{float((nframes + 1) / FPS):.6f}", "-i", path]
    # -i BASE 是输入 0，图层段依次是输入 1..N，故用 k+1
    fc.append(f"[{k + 1}:v]trim=end_frame={nframes},setpts=PTS-STARTPTS,format=rgba[s{k}]")
    labels.append(f"[s{k}]")
fc.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[layer]")

out, tlimit = OUT, TOTAL
for a in sys.argv:
    if a.startswith("--tlimit="):
        tlimit = float(a.split("=")[1])
        root, ext = os.path.splitext(OUT)
        out = f"{root}_TEST{ext}"

script = os.path.join(WD, "_sub_layer_filter.txt")
open(script, "w").write(";".join(fc) + ";[0:v][layer]overlay=0:0:eof_action=pass,format=yuv420p[vout]")

cmd = ["ffmpeg", "-y", "-v", "error", "-i", BASE] + ins + [
    "-filter_complex_script", script,
    "-map", "[vout]", "-map", "0:a?",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "copy", "-movflags", "+faststart",
    "-t", f"{tlimit:.3f}", out,
]

if "--dry" in sys.argv:
    print("inputs:", len(segs) + 1, " filter script:", script)
    sys.exit(0)

print(f"开始合板 → {out}", flush=True)
r = subprocess.run(cmd)
print("rc =", r.returncode, "（rc=0 只证明语法通过，必须按 Verification 做字芯掩膜验收）")
