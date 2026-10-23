# -*- coding: utf-8 -*-
"""轻量级 SVG 图表库（纯标准库，无第三方依赖）。

所有函数返回 ``<svg>...</svg>`` 字符串，可直接内联进 HTML 报告。
设计约束：
  * 浅色底 + 深色字，中文标签，关键值直接标注在图上；
  * 统一配色：蓝 #4472C4 / 橙 #ED7D31 / 绿 #70AD47 / 红 #C00000；
  * 图表随容器宽度自适应（width=100%，viewBox 固定）。
"""

from __future__ import annotations

import math
from html import escape

FONT = ("-apple-system,'Microsoft YaHei','PingFang SC','Hiragino Sans GB',"
        "'Source Han Sans SC',Arial,sans-serif")

BLUE = "#4472C4"
ORANGE = "#ED7D31"
GREEN = "#70AD47"
RED = "#C00000"
PALETTE = [BLUE, ORANGE, GREEN, RED, "#7030A0", "#00B0F0", "#FFC000", "#A5A5A5"]

# 知识点掌握等级配色：红=危险，黄=薄弱，绿=良好，深蓝=优秀
LEVEL_COLORS = {
    "优秀": "#2F5597",
    "良好": "#70AD47",
    "薄弱": "#FFC000",
    "危险": "#C00000",
}
LEVEL_ORDER = ["优秀", "良好", "薄弱", "危险"]

INK = "#2B2B2B"
MUTED = "#6B6B6B"
AXIS = "#C4C4C4"
GRID = "#ECECEC"


# --------------------------------------------------------------------------- #
# 基础工具
# --------------------------------------------------------------------------- #
def _e(text) -> str:
    return escape(str(text), quote=True)


def _nice_ceil(value: float) -> float:
    """把上界取整成 1/1.5/2/2.5/3/4/5/6/8/10 × 10^n 形式，保证刻度漂亮。"""
    if value is None or value <= 0 or not math.isfinite(value):
        return 1.0
    exp = math.floor(math.log10(value))
    base = 10.0 ** exp
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if value <= m * base + 1e-9:
            return m * base
    return 10.0 * base


def _ticks(vmax: float, count: int = 5):
    """生成 0..vmax 的 count 段刻度（含端点）。"""
    return [vmax * i / count for i in range(count + 1)]


def _num(v, nd: int = 0) -> str:
    if v is None:
        return "-"
    if nd == 0:
        return "{:.0f}".format(v)
    return ("{:." + str(nd) + "f}").format(v).rstrip("0").rstrip(".") if v != int(v) else "{:.0f}".format(v)


def _pct(v: float, nd: int = 1) -> str:
    return _num(v * 100, nd) + "%"


def _open_svg(w: int, h: int, title: str = "") -> str:
    parts = [
        '<svg viewBox="0 0 %d %d" width="100%%" height="auto" '
        'preserveAspectRatio="xMidYMid meet" role="img" '
        'style="font-family:%s;display:block;max-width:100%%">' % (w, h, FONT)
    ]
    if title:
        parts.append("<title>%s</title>" % _e(title))
    return "".join(parts)


def _chart_title(x, y, text, sub="", anchor="start", size=15):
    out = ['<text x="%s" y="%s" font-size="%s" font-weight="700" fill="%s" '
           'text-anchor="%s">%s</text>' % (x, y, size, INK, anchor, _e(text))]
    if sub:
        out.append('<text x="%s" y="%s" font-size="11" fill="%s" text-anchor="%s">%s</text>'
                   % (x, y + 16, MUTED, anchor, _e(sub)))
    return "".join(out)


def _legend(x, y, items, gap=14, size=11, row_h=18, max_w=None, vertical=True):
    """items: [(label, color), ...]"""
    out = []
    if vertical:
        for i, (label, color) in enumerate(items):
            yy = y + i * row_h
            out.append('<rect x="%s" y="%s" width="10" height="10" rx="2" fill="%s"/>'
                       % (x, yy - 9, color))
            out.append('<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>'
                       % (x + 15, yy, size, INK, _e(label)))
    else:
        cx = x
        for label, color in items:
            out.append('<rect x="%s" y="%s" width="10" height="10" rx="2" fill="%s"/>'
                       % (cx, y - 9, color))
            out.append('<text x="%s" y="%s" font-size="%s" fill="%s">%s</text>'
                       % (cx + 15, y, size, INK, _e(label)))
            cx += gap + 15 + len(str(label)) * (size * 0.95)
    return "".join(out)


def _grid_and_axis(ml, mt, pw, ph, ymax, ymin=0.0, nd=0, ticks=5):
    """返回 (svg片段, y函数)。"""
    out = []

    def y(v):
        span = (ymax - ymin) or 1.0
        return mt + ph - (v - ymin) / span * ph

    for t in _ticks(ymax, ticks):
        yy = y(t)
        out.append('<line x1="%s" y1="%.2f" x2="%s" y2="%.2f" stroke="%s" stroke-width="1"/>'
                   % (ml, yy, ml + pw, yy, GRID))
        out.append('<text x="%s" y="%.2f" font-size="10.5" fill="%s" text-anchor="end">%s</text>'
                   % (ml - 8, yy + 3.5, MUTED, _num(t, nd)))
    out.append('<line x1="%s" y1="%.2f" x2="%s" y2="%.2f" stroke="%s" stroke-width="1.2"/>'
               % (ml, y(0), ml + pw, y(0), AXIS))
    return "".join(out), y


# --------------------------------------------------------------------------- #
# 1. 柱状图
# --------------------------------------------------------------------------- #
def bar_chart(cats, vals, title="", unit="", refs=None, colors=None,
              w=680, h=330, y_max=None, value_nd=0, sub="", bar_ratio=0.56,
              ref_show_value=True, rotate_labels=False):
    """基础柱状图。refs: [(值, 标签, 颜色), ...] 画水平警戒线。"""
    refs = refs or []
    n = max(len(cats), 1)
    ml, mr, mt, mb = 62, 26, 52 if sub else 40, 58
    pw, ph = w - ml - mr, h - mt - mb
    hi = max([v for v in vals if v is not None] + [r[0] for r in refs] + [0.0])
    ymax = float(y_max) if y_max else _nice_ceil(hi * 1.18) if hi > 0 else 1.0
    nd = 0 if ymax >= 20 else 1
    grid, y = _grid_and_axis(ml, mt, pw, ph, ymax, nd=nd)
    step = pw / n
    bw = min(64, step * bar_ratio)
    out = [_open_svg(w, h, title), _chart_title(ml, 24 if sub else 22, title, sub)]

    # 警戒线
    for val, label, color in refs:
        if val is None or val > ymax:
            continue
        yy = y(val)
        out.append('<line x1="%s" y1="%.2f" x2="%s" y2="%.2f" stroke="%s" stroke-width="1.4" '
                   'stroke-dasharray="6 4" opacity="0.85"/>' % (ml, yy, ml + pw, yy, color))
        txt = "%s %s" % (label, _num(val, value_nd)) if ref_show_value else label
        out.append('<text x="%s" y="%.2f" font-size="10.5" fill="%s" text-anchor="end">%s</text>'
                   % (ml + pw - 2, yy - 5, color, _e(txt)))

    out.append(grid)
    for i, cat in enumerate(cats):
        v = vals[i] if i < len(vals) else 0
        v = 0 if v is None else v
        color = (colors[i] if colors and i < len(colors) else PALETTE[i % len(PALETTE)])
        bx = ml + step * i + (step - bw) / 2
        by = y(v)
        out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="3" fill="%s"/>'
                   % (bx, by, bw, max(y(0) - by, 0), color))
        out.append('<text x="%.2f" y="%.2f" font-size="11" font-weight="600" fill="%s" '
                   'text-anchor="middle">%s</text>' % (bx + bw / 2, by - 6, INK, _num(v, value_nd)))
        if rotate_labels:
            out.append('<text transform="translate(%.2f,%.2f) rotate(-35)" font-size="10.5" '
                       'fill="%s" text-anchor="end">%s</text>'
                       % (ml + step * i + step / 2 + 6, y(0) + 16, MUTED, _e(cat)))
        else:
            out.append('<text x="%.2f" y="%.2f" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                       % (ml + step * i + step / 2, y(0) + 17, MUTED, _e(cat)))
    if unit:
        out.append('<text x="%s" y="%s" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                   % (w / 2, h - 8, MUTED, _e(unit)))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# 2. 饼图（环形）
# --------------------------------------------------------------------------- #
def pie_chart(labels, vals, title="", w=680, h=320, colors=None, sub=""):
    total = sum(v for v in vals if v) or 1
    cx, cy, r = 200, (h / 2 + 12), min(h / 2 - 42, 108)
    out = [_open_svg(w, h, title), _chart_title(24, 26, title, sub)]
    angle = -90.0
    for i, (lab, v) in enumerate(zip(labels, vals)):
        v = v or 0
        sweep = 360.0 * v / total
        color = colors[i] if colors and i < len(colors) else PALETTE[i % len(PALETTE)]
        if v > 0:
            a0 = math.radians(angle)
            a1 = math.radians(angle + sweep)
            x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
            x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
            large = 1 if sweep > 180 else 0
            if sweep >= 359.99:
                out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s"/>' % (cx, cy, r, color))
            else:
                out.append('<path d="M %.2f %.2f L %.2f %.2f A %.2f %.2f 0 %d 1 %.2f %.2f Z" '
                           'fill="%s" stroke="#fff" stroke-width="1.5"/>'
                           % (cx, cy, x0, y0, r, r, large, x1, y1, color))
        angle += sweep
    # 中心留白显示总数
    out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="#FFFFFF" stroke="#EEE"/>' % (cx, cy, r * 0.52))
    out.append('<text x="%.2f" y="%.2f" font-size="13" fill="%s" text-anchor="middle">总人数</text>'
               % (cx, cy - 2, MUTED))
    out.append('<text x="%.2f" y="%.2f" font-size="20" font-weight="700" fill="%s" '
               'text-anchor="middle">%s</text>' % (cx, cy + 22, INK, _num(total)))
    # 图例
    ly = cy - len(labels) * 9 + 6
    for i, (lab, v) in enumerate(zip(labels, vals)):
        color = colors[i] if colors and i < len(colors) else PALETTE[i % len(PALETTE)]
        yy = ly + i * 26
        out.append('<rect x="392" y="%.2f" width="12" height="12" rx="2" fill="%s"/>' % (yy - 10, color))
        out.append('<text x="412" y="%.2f" font-size="12" fill="%s">%s</text>' % (yy, INK, _e(lab)))
        out.append('<text x="412" y="%.2f" font-size="12" font-weight="700" fill="%s">%s人（%s）</text>'
                   % (yy + 15, MUTED, _num(v), _pct(v / total)))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# 3. 折线图
# --------------------------------------------------------------------------- #
def line_chart(xlabels, series, title="", unit="", w=680, h=330, sub="",
               y_max=None, value_nd=1, show_values=True):
    """series: [(名称, [值...]), ...]"""
    ml, mr, mt, mb = 62, 26, 52 if sub else 40, 62
    if series:
        ml = max(ml, 96)
    pw, ph = w - ml - mr, h - mt - mb
    allv = [v for _, vs in series for v in vs if v is not None]
    hi = max(allv + [0]) or 1
    lo = min(allv + [0]) if allv else 0
    ymin = 0 if lo >= 0 else -_nice_ceil(abs(lo) * 1.15)
    ymax = float(y_max) if y_max else _nice_ceil(hi * 1.15)
    nd = 0 if ymax >= 20 else 1
    out = [_open_svg(w, h, title), _chart_title(ml, 24 if sub else 22, title, sub)]
    grid, y = _grid_and_axis(ml, mt, pw, ph, ymax, ymin, nd=nd)
    out.append(grid)
    n = max(len(xlabels), 1)
    step = pw / max(n - 1, 1)

    def x(i):
        return ml + step * i

    for si, (name, vs) in enumerate(series):
        color = PALETTE[si % len(PALETTE)]
        pts = [(x(i), y(v)) for i, v in enumerate(vs) if v is not None]
        if not pts:
            continue
        out.append('<polyline fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round" '
                   'points="%s"/>' % (color, " ".join("%.2f,%.2f" % p for p in pts)))
        for i, v in enumerate(vs):
            if v is None:
                continue
            out.append('<circle cx="%.2f" cy="%.2f" r="4" fill="#fff" stroke="%s" stroke-width="2"/>'
                       % (x(i), y(v), color))
            if show_values:
                out.append('<text x="%.2f" y="%.2f" font-size="10.5" font-weight="600" fill="%s" '
                           'text-anchor="middle">%s</text>'
                           % (x(i), y(v) - 9, color, _num(v, value_nd)))
        # 图例
        out.append('<rect x="%s" y="%.2f" width="12" height="3" rx="1.5" fill="%s"/>' % (12, 40 + si * 18, color))
        out.append('<text x="%s" y="%.2f" font-size="11" fill="%s">%s</text>' % (30, 44 + si * 18, INK, _e(name)))

    for i, lab in enumerate(xlabels):
        out.append('<text x="%.2f" y="%.2f" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                   % (x(i), mt + ph + 18, MUTED, _e(lab)))
    if unit:
        out.append('<text x="%s" y="%s" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                   % (w / 2, h - 8, MUTED, _e(unit)))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# 4. 分组柱状图
# --------------------------------------------------------------------------- #
def grouped_bar_chart(cats, series, title="", unit="", w=680, h=340, sub="",
                      value_nd=1, rotate_labels=False):
    """series: [(名称, [每个分类一个值]), ...] —— 同分类内并列。"""
    m = len(series)
    ml, mr, mt, mb = 62, 26, 52 if sub else 40, 62
    pw, ph = w - ml - mr, h - mt - mb
    allv = [v for _, vs in series for v in vs if v is not None] or [1]
    ymax = _nice_ceil(max(allv) * 1.2)
    nd = 0 if ymax >= 20 else value_nd
    out = [_open_svg(w, h, title), _chart_title(ml, 24 if sub else 22, title, sub)]
    grid, y = _grid_and_axis(ml, mt, pw, ph, ymax, nd=0)
    out.append(grid)
    n = max(len(cats), 1)
    step = pw / n
    gw = step * 0.72
    bw = gw / max(m, 1)
    for i, cat in enumerate(cats):
        base = ml + step * i + (step - gw) / 2
        for si, (name, vs) in enumerate(series):
            v = vs[i] if i < len(vs) else None
            if v is None:
                continue
            color = PALETTE[si % len(PALETTE)]
            bx = base + bw * si
            by = y(v)
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="2.5" fill="%s"/>'
                       % (bx + 1, by, max(bw - 2, 1), max(y(0) - by, 0), color))
            out.append('<text x="%.2f" y="%.2f" font-size="10" font-weight="600" fill="%s" '
                       'text-anchor="middle">%s</text>'
                       % (bx + bw / 2, by - 5, INK, _num(v, nd)))
        if rotate_labels:
            out.append('<text transform="translate(%.2f,%.2f) rotate(-30)" font-size="10.5" fill="%s" '
                       'text-anchor="end">%s</text>' % (ml + step * i + step / 2 + 4, y(0) + 16, MUTED, _e(cat)))
        else:
            out.append('<text x="%.2f" y="%.2f" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                       % (ml + step * i + step / 2, y(0) + 17, MUTED, _e(cat)))
    out.append(_legend(ml, 44, [(name, PALETTE[i % len(PALETTE)]) for i, (name, _) in enumerate(series)],
                       vertical=False))
    if unit:
        out.append('<text x="%s" y="%s" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                   % (w / 2, h - 8, MUTED, _e(unit)))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# 5. 堆积柱状图
# --------------------------------------------------------------------------- #
def stacked_bar_chart(cats, series, title="", unit="", w=680, h=340, sub="", value_nd=0):
    ml, mr, mt, mb = 62, 26, 56 if sub else 40, 62
    pw, ph = w - ml - mr, h - mt - mb
    totals = []
    for i in range(len(cats)):
        totals.append(sum((vs[i] or 0) for _, vs in series))
    ymax = _nice_ceil((max(totals) if totals else 1) * 1.2)
    out = [_open_svg(w, h, title), _chart_title(ml, 24 if sub else 22, title, sub)]
    grid, y = _grid_and_axis(ml, mt, pw, ph, ymax, nd=0)
    out.append(grid)
    n = max(len(cats), 1)
    step = pw / n
    bw = min(58, step * 0.5)
    for i, cat in enumerate(cats):
        bx = ml + step * i + (step - bw) / 2
        acc = 0.0
        for si, (name, vs) in enumerate(series):
            v = vs[i] or 0
            if v <= 0:
                continue
            color = PALETTE[si % len(PALETTE)]
            y0, y1 = y(acc), y(acc + v)
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
                       % (bx, y1, bw, max(y0 - y1, 0), color))
            if y0 - y1 > 15:
                out.append('<text x="%.2f" y="%.2f" font-size="10" font-weight="600" fill="#fff" '
                           'text-anchor="middle">%s</text>' % (bx + bw / 2, (y0 + y1) / 2 + 3.5, _num(v, value_nd)))
            acc += v
        out.append('<text x="%.2f" y="%.2f" font-size="11" font-weight="700" fill="%s" '
                   'text-anchor="middle">%s</text>' % (bx + bw / 2, y(acc) - 6, INK, _num(acc, value_nd)))
        out.append('<text x="%.2f" y="%.2f" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                   % (ml + step * i + step / 2, y(0) + 17, MUTED, _e(cat)))
    out.append(_legend(ml, 46, [(name, PALETTE[i % len(PALETTE)]) for i, (name, _) in enumerate(series)],
                       vertical=False))
    if unit:
        out.append('<text x="%s" y="%s" font-size="10.5" fill="%s" text-anchor="middle">%s</text>'
                   % (w / 2, h - 8, MUTED, _e(unit)))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# 6. 雷达图
# --------------------------------------------------------------------------- #
def radar_chart(axes, series, title="", w=680, h=400, sub="", max_rings=4):
    """series: [(名称, [0~1 之间的归一化值]), ...]；axes 长度需与值一致。"""
    n = len(axes)
    cx, cy = w / 2 - 60, h / 2 + 8
    r = min(h / 2 - 46, 132)
    out = [_open_svg(w, h, title), _chart_title(24, 26, title, sub)]

    def pt(i, frac):
        a = -math.pi / 2 + 2 * math.pi * i / max(n, 1)
        return cx + r * frac * math.cos(a), cy + r * frac * math.sin(a)

    for ring in range(1, max_rings + 1):
        frac = ring / max_rings
        pts = " ".join("%.2f,%.2f" % pt(i, frac) for i in range(n))
        out.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1"/>'
                   % (pts, GRID if ring < max_rings else AXIS))
    for i in range(n):
        x, y = pt(i, 1)
        out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="1"/>'
                   % (cx, cy, x, y, GRID))
        lx, ly = pt(i, 1.16)
        anchor = "middle"
        if lx > cx + 6:
            anchor = "start"
        elif lx < cx - 6:
            anchor = "end"
        out.append('<text x="%.2f" y="%.2f" font-size="11" fill="%s" text-anchor="%s">%s</text>'
                   % (lx, ly + 4, INK, anchor, _e(axes[i])))

    for si, (name, vals) in enumerate(series):
        color = PALETTE[si % len(PALETTE)]
        pts = []
        for i, v in enumerate(vals):
            v = 0 if v is None else max(0.0, min(1.0, v))
            pts.append(pt(i, v))
        out.append('<polygon points="%s" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="2"/>'
                   % (" ".join("%.2f,%.2f" % p for p in pts), color, color))
        for x, y in pts:
            out.append('<circle cx="%.2f" cy="%.2f" r="3" fill="%s"/>' % (x, y, color))
    out.append(_legend(w - 172, 96, [(name, PALETTE[i % len(PALETTE)]) for i, (name, _) in enumerate(series)]))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------- #
# 7. 知识点掌握矩阵（热力图）
# --------------------------------------------------------------------------- #
def heatmap_matrix(rows, title="", w=680, sub="", value_header="得分率",
                   levels=None, cell_h=26):
    """rows: [{'label': 知识点, 'level': '优秀/良好/薄弱/危险', 'value': 0.62}, ...]"""
    levels = levels or LEVEL_ORDER
    n = max(len(rows), 1)
    mt = 84 if sub else 68
    mh = mt + n * cell_h + 34
    h = max(mh, 200)
    label_w = 132
    grid_x = label_w + 10
    grid_w = w - grid_x - 108
    out = [_open_svg(w, h, title), _chart_title(24, 24, title)]
    if sub:
        out.append('<text x="24" y="42" font-size="11" fill="%s">%s</text>' % (MUTED, _e(sub)))

    def cell_text_color(color):
        # 黄色底用深色字，其余白字，保证对比度
        return "#5C4400" if color.upper() in ("#FFC000", "#F2C500", "#FFD700") else "#FFFFFF"

    cw = grid_w / len(levels)
    for j, lv in enumerate(levels):
        x = grid_x + cw * j
        color = LEVEL_COLORS.get(lv, BLUE)
        out.append('<rect x="%.2f" y="%s" width="%.2f" height="22" rx="3" fill="%s" opacity="0.92"/>'
                   % (x + 1, mt - 32, cw - 2, color))
        out.append('<text x="%.2f" y="%s" font-size="11" font-weight="600" fill="%s" '
                   'text-anchor="middle">%s</text>'
                   % (x + cw / 2, mt - 17, cell_text_color(color), _e(lv)))
    out.append('<text x="%.2f" y="%s" font-size="11" font-weight="600" fill="%s">知识点</text>'
               % (12, mt - 17, INK))
    out.append('<text x="%.2f" y="%s" font-size="11" font-weight="600" fill="%s" '
               'text-anchor="end">%s</text>' % (w - 16, mt - 17, INK, _e(value_header)))

    for i, row in enumerate(rows):
        yy = mt + i * cell_h
        lv = row.get("level", "")
        out.append('<rect x="0" y="%s" width="%s" height="%s" fill="%s"/>'
                   % (yy, w, cell_h, "#FAFAFA" if i % 2 == 0 else "#FFFFFF"))
        out.append('<text x="12" y="%.2f" font-size="11.5" fill="%s">%s</text>'
                   % (yy + cell_h / 2 + 4, INK, _e(row.get("label", ""))))
        for j, l in enumerate(levels):
            x = grid_x + cw * j
            hit = (l == lv)
            fill = LEVEL_COLORS.get(l, BLUE) if hit else "#F2F2F2"
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%s" rx="3" fill="%s" '
                       'stroke="#FFFFFF" stroke-width="2"/>'
                       % (x + 1, yy + 2, cw - 2, cell_h - 4, fill))
            if hit:
                out.append('<text x="%.2f" y="%.2f" font-size="10.5" font-weight="700" fill="%s" '
                           'text-anchor="middle">%s</text>'
                           % (x + cw / 2, yy + cell_h / 2 + 4, cell_text_color(fill), _e(lv)))
        out.append('<text x="%.2f" y="%.2f" font-size="12" font-weight="700" fill="%s" '
                   'text-anchor="end">%s</text>'
                   % (w - 16, yy + cell_h / 2 + 4, LEVEL_COLORS.get(lv, INK),
                      _pct(row.get("value", 0), 1)))
    out.append("</svg>")
    return "".join(out)
