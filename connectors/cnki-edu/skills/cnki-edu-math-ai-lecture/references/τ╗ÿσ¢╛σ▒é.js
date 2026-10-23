// ══════════════════════════════════════════════════════════════════════
//  绘图层 v1.1 —— 让「画出来长什么样」由代码保证，而不是由模型每次现写
//
//  与几何内核的分工（互补，不能互相替代）：
//    · 几何内核 管「点在哪」  —— 失败表现：图错了、答案对不上   —— CK() 能抓到
//    · 绘图层   管「长什么样」—— 失败表现：图看着怪、标注越界   —— CK() 抓不到
//
//  它真正的价值不是「少写代码」，而是：
//    ★ 把「画布白名单」从**文字约束**变成**代码约束**。
//      旧写法：「画布上不能出现汉字 / 数字 / 等式 / 坐标」—— 靠模型记住，实测被违反多次
//              （试题6 画 (1)(2)(3)、试题7 写 = 1 − 1/2 + 1/2、试题8 为凑画布画坐标轴）
//      新写法：drawMathText() 内部逐字符白名单，违规字符**画不出来**，并计入 CK 体系
//
//  为什么不用 throw：本产物是交付给学生的单页 HTML，一个未捕获异常 = 整页空白。
//    改为「拒绝绘制 + 记录 + 计入 CK」→ 违规不会静默（角标变红、裁决驳回），
//    但页面仍然可用。**可见的失败**优于**不可用的正确**。
//
//  用法：与几何内核一起整段粘贴进同一个 IIFE（见第三步提示词「输出格式」）。
//        本文件被「注入内核.js」同步进第三步提示词的「绘图层 BEGIN/END」标记区，
//        标记区是真源的唯一副本，**不要手改标记区内容**。
//
//  前置约定（由**产物骨架**保证，本文件不复定义）：
//    · ctx      —— 主画布 2D 上下文    · W / H —— 画布宽高（本流水线 360 × 260）
//    · drawBaseScene() —— 题目特定的基底绘制（本文件只调用，不定义）
//  本文件**自己定义**的东西（产物不要再定义一遍，否则 `Identifier 'X' has already been declared`）：
//    · stateAccumulator / resetAccumulator / recordToAccumulator / replayAccumulator
// ══════════════════════════════════════════════════════════════════════

/* ── 角度常量：自定义一份，**不依赖几何内核**（两块可以各自独立存在） ──
   注意不要写成 `const DEG` —— 内核里已经有 `const DEG`，同作用域重复声明会 SyntaxError。 */
const _DEG = Math.PI / 180;

// 容错：可选参数若被传成颜色字符串（旧清单签名 `…, color`），自动包成 `{ color }`。
function _normOpts(o) {
    if (o === undefined || o === null) return {};
    if (typeof o === 'string') return { color: o };
    return o;
}

/* ═══════════ A. 画布与状态（8） ═══════════ */

// 【清屏】唯一合法的"擦掉全部"方式。只允许在 drawBaseScene 与清理式动画的 tick 里调用。
function clearCanvas() { ctx.clearRect(0, 0, W, H); }

/**
 * 【状态累积容器】保存「本帧之前所有已出现的元素」，每帧第二步原样回放。
 * ★ 由绘图层统一声明 —— 产物不再自己定义它，避免"忘了声明"或"误声明成函数内局部变量"
 *   （后者会让后面所有帧都看不到前面画的元素，表现为"画面失忆"）。
 */
const stateAccumulator = [];

// 【清空累积】只在"重新进入场景"（多图题切到下一幅图）时用；普通帧切换**禁止**清空。
function resetAccumulator() { stateAccumulator.length = 0; return stateAccumulator; }

// 【记录本帧新增元素】动画播完后必须调用，否则下一帧会丢。
function recordToAccumulator(item) {
    stateAccumulator.push(item);
    return item;
}

/**
 * 【回放累积元素】每帧第 3 步固定调用。
 * ★ 这里是**记录格式的唯一权威定义** —— 产物往 stateAccumulator 里塞的记录，
 *   必须用下面这些 type，其它 type 一律不会被画出来（也不会报错，属静默丢失，禁止）。
 *   type 可选：line / ray / point / circle / arc / rightangle / anglearc / equalmark /
 *             parallelmark / symbol / label / text / polygon / hatch / curve
 */
function replayAccumulator() {
    if (!stateAccumulator || !stateAccumulator.length) return;
    stateAccumulator.forEach(function (it) {
        if (!it || !it.type) return;
        switch (it.type) {
            case 'line':         drawLine(it.x1, it.y1, it.x2, it.y2, it.color, it.width, it.dash); break;
            case 'ray':          drawRay(it.x1, it.y1, it.x2, it.y2, it.color, it.width, it.dash, it.arrow); break;
            case 'point':        drawPoint(it.x, it.y, it.label, it.color, it.offsetX, it.offsetY, it.baseline); break;
            case 'circle':       drawCircle(it.cx, it.cy, it.r, it.color, it.width, it.dash); break;
            case 'arc':          drawArc(it.cx, it.cy, it.r, it.a0, it.a1, it.color, it.width, it.dash); break;
            case 'rightangle':   drawRightAngle(it.vertex, it.p1, it.p2, it.size); break;
            case 'anglearc':     drawAngleArc(it.vertex, it.p1, it.p2, it.color, it.radius); break;
            case 'equalmark':    drawEqualMark(it.x1, it.y1, it.x2, it.y2, it.count); break;
            case 'parallelmark': drawParallelMark(it.x1, it.y1, it.x2, it.y2, it.count); break;
            case 'symbol':
                // ★ 按内容路由：结论标记（✓ ✗ ？ ！ ✕）走 drawSymbol；数学关系符（∽ ≌ …）属画布文字，走 drawMathText。
                //   若一律走 drawSymbol，关系符会被其白名单拦截（只允许勾叉符号）→ 帧重放时刷屏违规告警。
                if (_SYM_OK.test(it.text)) drawSymbol(it.x, it.y, it.text, it.color, it.size);
                else drawMathText(it.text, it.x, it.y, { size: it.size, color: it.color, align: 'center', baseline: 'middle' });
                break;
            case 'label':        drawLabel(it.x, it.y, it.label, it.color, it.dx, it.dy); break;
            case 'text':         drawMathText(it.text, it.x, it.y, it.opts); break;
            case 'polygon':      drawPolygon(it.pts, it.opts); break;
            case 'hatch':        hatchRegion(it.pts, it.opts); break;
            case 'curve':        drawCurve(it.mp, it.fn, it.xMin, it.xMax, it.opts); break;
            default:
                console.error('❌ 未知的累积记录类型「' + it.type + '」—— 该元素不会被绘制（见 replayAccumulator 的 type 表）');
        }
    });
}

// 【每帧收尾】★ 每个 drawFrame_N 与每个动画 tick 的**最后一步**必须调用它。
//   作用：把「绘图校验 n/n」画到画布右下角——把控制台里的隐形结果变成手机上一眼可见。
//   动画的每 tick 都必须重画，因为 tick 里的 clearCanvas() 会把它擦掉。
function finishFrame() { drawCKBadge(); }

// 【画布角标】读内核写的 window.__CK_REPORT__，在右下角留白区外画「CK n/n」。
//   未跑 CKSummary() 时显示「CK --」（这本身也是信号：校验没跑）。
//   角标是全文**唯一**允许在画布上出现数字的地方，属交付水印，不算题目内容。
function drawCKBadge() {
    let rep = null;
    try { if (typeof window !== 'undefined') rep = window.__CK_REPORT__; } catch (e) { rep = null; }
    const ok = !!(rep && rep.ok);
    const txt = rep ? ('CK ' + rep.pass + '/' + rep.total) : 'CK --';
    const bx = (typeof W === 'number' ? W : 360) - 7;
    const by = (typeof H === 'number' ? H : 260) - 6;
    ctx.save();
    ctx.font = '600 10px ui-monospace, Menlo, Consolas, monospace';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'alphabetic';
    const w = ctx.measureText(txt).width + 8;
    ctx.fillStyle = ok ? 'rgba(22,163,74,0.10)' : 'rgba(220,38,38,0.12)';
    ctx.fillRect(bx - w + 4, by - 11, w, 14);
    ctx.fillStyle = ok ? '#15803d' : '#b91c1c';
    ctx.fillText(txt, bx, by);
    ctx.restore();
}

/**
 * 【把画布白名单违规计入 CK 体系】★ 必须在 CKSummary() **之前**调用。
 *   为什么必须挂进 CK：else 违规只躺在 console 里，没人看、没人判、不进裁决。
 *   调用后：违规数 > 0 → 多出一条 ❌ CK 项 → CKSummary 输出 n-1/n → 角标变红 → 出口裁决驳回。
 */
function CKDrawViolations() {
    if (typeof CK === 'function') {
        return CK('画布白名单（不得出现汉字/数字/等号/坐标）', _drawViolations.length, 0);
    }
    console.error('❌ CKDrawViolations() 找不到内核的 CK() —— 请确认几何内核与本绘图层在同一个 IIFE 内');
    return _drawViolations.length === 0;
}

/* ═══════════ B. 基础图元（5） ═══════════ */

// 【点】画圆点 + 单字母标签。与中心点距 < 5px 的其它点会自动让标签错开。
function drawPoint(x, y, label, color, offsetX, offsetY, baseline) {
    color = color || '#1e293b';
    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    ctx.fill();
    if (label) {
        const dx = (offsetX === undefined ? 0 : offsetX);
        const dy = (offsetY === undefined ? -8 : offsetY);
        drawMathText(label, x + dx, y + dy, { size: 15, color: color, align: 'center', baseline: baseline || 'alphabetic' });
    }
    ctx.restore();
}

function drawLine(x1, y1, x2, y2, color, width, dash) {
    ctx.save();
    ctx.strokeStyle = color || '#1e293b';
    ctx.lineWidth = width || 1.5;
    if (dash) ctx.setLineDash(Array.isArray(dash) ? dash : [5, 4]);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    ctx.restore();
}

// 【射线】从 (x1,y1) 过 (x2,y2) 延伸到画布外；arrow=true 时末端画箭头。
function drawRay(x1, y1, x2, y2, color, width, dash, arrow) {
    const dx = x2 - x1, dy = y2 - y1;
    const L = Math.hypot(dx, dy) || 1;
    const far = (W + H) * 2;
    const ex = x1 + dx / L * far, ey = y1 + dy / L * far;
    drawLine(x1, y1, ex, ey, color, width, dash);
    if (arrow) _arrowHead(x1, y1, x2, y2, color);
}

function drawCircle(cx, cy, r, color, width, dash) {
    ctx.save();
    ctx.strokeStyle = color || '#1e293b';
    ctx.lineWidth = width || 1.5;
    if (dash) ctx.setLineDash(Array.isArray(dash) ? dash : [5, 4]);
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
}

// 【圆弧】a0/a1 为画布绝对角（度，0° = +x 方向，正值视觉顺时针）
function drawArc(cx, cy, r, a0, a1, color, width, dash) {
    ctx.save();
    ctx.strokeStyle = color || '#1e293b';
    ctx.lineWidth = width || 1.5;
    if (dash) ctx.setLineDash(Array.isArray(dash) ? dash : [5, 4]);
    ctx.beginPath();
    ctx.arc(cx, cy, r, a0 * _DEG, a1 * _DEG);
    ctx.stroke();
    ctx.restore();
}

// 【箭头】内部用；画在 (x2,y2) 处、指向 (x1,y1)→(x2,y2) 方向
function _arrowHead(x1, y1, x2, y2, color, size) {
    const a = Math.atan2(y2 - y1, x2 - x1);
    const s = size || 8;
    ctx.save();
    ctx.fillStyle = color || '#1e293b';
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - s * Math.cos(a - 0.38), y2 - s * Math.sin(a - 0.38));
    ctx.lineTo(x2 - s * Math.cos(a + 0.38), y2 - s * Math.sin(a + 0.38));
    ctx.closePath();
    ctx.fill();
    ctx.restore();
}

/* ═══════════ C. 多边形与填充（2） ═══════════ */

// 【多边形】ptsArr 为画布坐标数组；opts = { fill, stroke, color, fillColor, width, dash, alpha }
function drawPolygon(ptsArr, opts) {
    opts = _normOpts(opts);
    if (!ptsArr || ptsArr.length < 2) return;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(ptsArr[0].x, ptsArr[0].y);
    for (let i = 1; i < ptsArr.length; i++) ctx.lineTo(ptsArr[i].x, ptsArr[i].y);
    ctx.closePath();
    if (opts.fill) { ctx.globalAlpha = (opts.alpha === undefined ? 0.18 : opts.alpha); ctx.fillStyle = opts.fillColor || '#3b82f6'; ctx.fill(); ctx.globalAlpha = 1; }
    if (opts.stroke !== false) {
        ctx.strokeStyle = opts.color || '#1e293b';
        ctx.lineWidth = opts.width || 1.5;
        if (opts.dash) ctx.setLineDash(Array.isArray(opts.dash) ? opts.dash : [5, 4]);
        ctx.stroke();
    }
    ctx.restore();
}

// 【斜线阴影填充】相似题/面积题常用。opts = { gap, angle(度), color, alpha }
function hatchRegion(ptsArr, opts) {
    opts = _normOpts(opts);
    if (!ptsArr || ptsArr.length < 3) return;
    const gap = opts.gap || 7;
    const ang = (opts.angle === undefined ? -45 : opts.angle) * _DEG;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(ptsArr[0].x, ptsArr[0].y);
    for (let i = 1; i < ptsArr.length; i++) ctx.lineTo(ptsArr[i].x, ptsArr[i].y);
    ctx.closePath();
    ctx.clip();
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    ptsArr.forEach(function (p) { x0 = Math.min(x0, p.x); y0 = Math.min(y0, p.y); x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y); });
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    const R = Math.hypot(x1 - x0, y1 - y0) / 2 + gap;
    const dx = Math.cos(ang), dy = Math.sin(ang);
    ctx.strokeStyle = opts.color || '#64748b';
    ctx.globalAlpha = (opts.alpha === undefined ? 0.5 : opts.alpha);
    ctx.lineWidth = 1;
    for (let d = -R; d <= R; d += gap) {
        const px = cx - dy * d, py = cy + dx * d;
        ctx.beginPath();
        ctx.moveTo(px - dx * R, py - dy * R);
        ctx.lineTo(px + dx * R, py + dy * R);
        ctx.stroke();
    }
    ctx.restore();
}

/* ═══════════ D. 角与标记（4） ═══════════ */

// 【角弧】只画弧线，不写角度值（画布禁止数字）。
function drawAngleArc(vertex, p1, p2, color, radius) {
    const a1 = Math.atan2(p1.y - vertex.y, p1.x - vertex.x) / _DEG;
    const a2 = Math.atan2(p2.y - vertex.y, p2.x - vertex.x) / _DEG;
    let d = a2 - a1;
    while (d <= -180) d += 360;
    while (d > 180) d -= 360;
    drawArc(vertex.x, vertex.y, radius || 18, a1, a1 + d, color || '#ef4444', 1.5);
}

// 【直角符号】vertex 是直角顶点，p1/p2 是两条直角边上的点（**必须给**，否则朝向会画错）。
function drawRightAngle(vertex, p1, p2, size) {
    if (!p1 || !p2) { console.error('❌ drawRightAngle 必须给出 p1、p2（两条直角边上的点），否则无法确定朝向'); return; }
    const s = size || 9;
    const u1 = { x: p1.x - vertex.x, y: p1.y - vertex.y };
    const u2 = { x: p2.x - vertex.x, y: p2.y - vertex.y };
    const l1 = Math.hypot(u1.x, u1.y) || 1, l2 = Math.hypot(u2.x, u2.y) || 1;
    const a = { x: vertex.x + u1.x / l1 * s, y: vertex.y + u1.y / l1 * s };
    const b = { x: vertex.x + u2.x / l2 * s, y: vertex.y + u2.y / l2 * s };
    const m = { x: a.x + b.x - vertex.x, y: a.y + b.y - vertex.y };
    ctx.save();
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(m.x, m.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
    ctx.restore();
}

// 【等长标记】在线段 (x1,y1)-(x2,y2) 中点画 count 条短横（1＝〡，2＝〢）
function drawEqualMark(x1, y1, x2, y2, count) {
    count = count || 1;
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const L = Math.hypot(x2 - x1, y2 - y1) || 1;
    const nx = -(y2 - y1) / L, ny = (x2 - x1) / L;      // 法向
    const tx = (x2 - x1) / L, ty = (y2 - y1) / L;       // 切向
    ctx.save();
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1.5;
    for (let i = 0; i < count; i++) {
        const off = (i - (count - 1) / 2) * 4;
        const px = mx + tx * off, py = my + ty * off;
        ctx.beginPath();
        ctx.moveTo(px - nx * 4, py - ny * 4);
        ctx.lineTo(px + nx * 4, py + ny * 4);
        ctx.stroke();
    }
    ctx.restore();
}

// 【平行标记】在线段中点画 count 个「>」形标记（1 个单箭头，2 个双箭头）
function drawParallelMark(x1, y1, x2, y2, count) {
    count = count || 1;
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    const L = Math.hypot(x2 - x1, y2 - y1) || 1;
    const tx = (x2 - x1) / L, ty = (y2 - y1) / L;
    const nx = -ty, ny = tx;
    ctx.save();
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1.5;
    for (let i = 0; i < count; i++) {
        const off = (i - (count - 1) / 2) * 5;
        const px = mx + tx * off, py = my + ty * off;
        ctx.beginPath();
        ctx.moveTo(px - tx * 3 - nx * 4, py - ty * 3 - ny * 4);
        ctx.lineTo(px + tx * 3, py + ty * 3);
        ctx.lineTo(px - tx * 3 + nx * 4, py - ty * 3 + ny * 4);
        ctx.stroke();
    }
    ctx.restore();
}

/* ═══════════ E. 坐标与曲线（4）—— B 档（函数图像）主力 ═══════════ */

/**
 * 【建立坐标映射】返回 mp 对象，后续 drawAxes / drawGrid / drawCurve 都用它。
 *   数学坐标 (x, y) → 画布坐标 mp.X(x), mp.Y(y)。pad 是坐标轴距画布边缘的留白。
 */
function mapping(xMin, xMax, yMin, yMax, pad) {
    pad = pad || 34;
    const w = W - pad * 2, h = H - pad * 2;
    const sx = w / (xMax - xMin), sy = h / (yMax - yMin);
    const ox = (0 - xMin) * sx + pad, oy = H - pad - (0 - yMin) * sy;
    return {
        xMin: xMin, xMax: xMax, yMin: yMin, yMax: yMax,
        X: function (mx) { return pad + (mx - xMin) * sx; },
        Y: function (my) { return H - pad - (my - yMin) * sy; },
        invX: function (px) { return xMin + (px - pad) / sx; },
        invY: function (py) { return yMin + (H - pad - py) / sy; },
        origin: { x: ox, y: oy }, sx: sx, sy: sy, pad: pad
    };
}

// 【坐标轴】x/y 轴 + 箭头 + 刻度（刻度值是画布上唯一允许的数字，由 drawTickText 单独画）
function drawAxes(mp, opts) {
    opts = _normOpts(opts);
    const c = opts.color || '#475569';
    const step = opts.step || 1;
    const showTicks = opts.ticks !== false;
    drawLine(mp.X(mp.xMin), mp.origin.y, mp.X(mp.xMax), mp.origin.y, c, 1.5);
    drawLine(mp.origin.x, mp.Y(mp.yMin), mp.origin.x, mp.Y(mp.yMax), c, 1.5);
    _arrowHead(mp.X(mp.xMin), mp.origin.y, mp.X(mp.xMax), mp.origin.y, c, 7);
    _arrowHead(mp.origin.x, mp.Y(mp.yMin), mp.origin.x, mp.Y(mp.yMax), c, 7);
    if (!showTicks) return mp;
    drawMathText('O', mp.origin.x - 9, mp.origin.y + 12, { size: 12, color: c, align: 'center' });
    for (let v = Math.ceil(mp.xMin / step) * step; v <= mp.xMax; v += step) {
        if (Math.abs(v) < 1e-9) continue;
        const px = mp.X(v);
        drawLine(px, mp.origin.y - 3, px, mp.origin.y + 3, c, 1);
        if (opts.xLabels !== false) drawTickText(String(Math.round(v * 1000) / 1000), px, mp.origin.y + 13);
    }
    for (let v = Math.ceil(mp.yMin / step) * step; v <= mp.yMax; v += step) {
        if (Math.abs(v) < 1e-9) continue;
        const py = mp.Y(v);
        drawLine(mp.origin.x - 3, py, mp.origin.x + 3, py, c, 1);
        if (opts.yLabels === true) drawTickText(String(Math.round(v * 1000) / 1000), mp.origin.x - 8, py + 4, 'right');
    }
    if (opts.xName) drawMathText(opts.xName, mp.X(mp.xMax) + 4, mp.origin.y + 13, { size: 13, color: c });
    if (opts.yName) drawMathText(opts.yName, mp.origin.x + 8, mp.Y(mp.yMax) + 4, { size: 13, color: c });
    return mp;
}

// 【网格】虚线背景网格
function drawGrid(mp, step, opts) {
    opts = _normOpts(opts);
    step = step || 1;
    const c = opts.color || '#e2e8f0';
    for (let v = Math.ceil(mp.xMin / step) * step; v <= mp.xMax; v += step) {
        drawLine(mp.X(v), mp.Y(mp.yMin), mp.X(v), mp.Y(mp.yMax), c, 1, [2, 3]);
    }
    for (let v = Math.ceil(mp.yMin / step) * step; v <= mp.yMax; v += step) {
        drawLine(mp.X(mp.xMin), mp.Y(v), mp.X(mp.xMax), mp.Y(v), c, 1, [2, 3]);
    }
}

/**
 * 【曲线】★ 只有这一个曲线函数 —— 一次/二次/反比例/其它全部传 fn，**不要按函数类型各写一个**。
 *   mp：mapping 对象；fn：t => y（数学坐标）；采样失败或跳出 mp 范围的点自动断开（不连线）。
 *   opts = { color, width, dash, samples, xMin, xMax }
 */
function drawCurve(mp, fn, xMin, xMax, opts) {
    opts = _normOpts(opts);
    const n = opts.samples || 240;
    const x0 = (xMin === undefined ? mp.xMin : xMin);
    const x1 = (xMax === undefined ? mp.xMax : xMax);
    const yLo = mp.yMin - (mp.yMax - mp.yMin) * 0.5;
    const yHi = mp.yMax + (mp.yMax - mp.yMin) * 0.5;
    ctx.save();
    ctx.strokeStyle = opts.color || '#2563eb';
    ctx.lineWidth = opts.width || 2;
    if (opts.dash) ctx.setLineDash(Array.isArray(opts.dash) ? opts.dash : [5, 4]);
    let started = false;
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
        const mx = x0 + (x1 - x0) * i / n;
        let my;
        try { my = fn(mx); } catch (e) { my = NaN; }
        if (typeof my !== 'number' || !isFinite(my) || my < yLo || my > yHi) { started = false; continue; }
        const px = mp.X(mx), py = mp.Y(my);
        if (!started) { ctx.moveTo(px, py); started = true; } else { ctx.lineTo(px, py); }
    }
    ctx.stroke();
    ctx.restore();
}

// 【刻度文字】只给 drawAxes/drawBar 内部用（数字白名单的唯一入口）
function drawTickText(text, x, y, align) {
    ctx.save();
    ctx.fillStyle = '#64748b';
    ctx.font = '10px ui-monospace, Menlo, Consolas, monospace';
    ctx.textAlign = align || 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
    ctx.restore();
}

/* ═══════════ F. 统计图形（5）—— B 档（统计/概率）主力 ═══════════ */

/**
 * 【条形图】values 与 labels 等长；条形自 yBase 向上，高度按 max 等比缩放。
 *   opts = { color, axis(是否画基线), valuesOnTop(条顶标数值), max, showValues }
 *   ★ 只用这一个条形函数画所有条形图；不要按"频数直方图/条形图"各写一个。
 */
function drawBar(values, labels, x0, yBase, w, gap, opts) {
    opts = _normOpts(opts);
    if (!values || !values.length) return;
    gap = (gap === undefined ? 6 : gap);
    const maxV = opts.max || Math.max.apply(null, values) || 1;
    const full = opts.full || (yBase - (opts.top === undefined ? 40 : opts.top));
    const colors = opts.colors || [opts.color || '#60a5fa'];
    values.forEach(function (v, i) {
        const h = (v / maxV) * full;
        const bx = x0 + i * (w + gap);
        ctx.save();
        ctx.fillStyle = colors[i % colors.length];
        ctx.globalAlpha = 0.85;
        ctx.fillRect(bx, yBase - h, w, h);
        ctx.globalAlpha = 1;
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 1;
        ctx.strokeRect(bx, yBase - h, w, h);
        ctx.restore();
        if (opts.valuesOnTop) drawTickText(String(v), bx + w / 2, yBase - h - 7, 'center');
        if (labels && labels[i] != null) drawTickText(String(labels[i]), bx + w / 2, yBase + 10, 'center');
    });
    if (opts.axis !== false) drawLine(x0 - 6, yBase, x0 + values.length * (w + gap), yBase, '#475569', 1.5);
}

// 【频数分布直方图】edges 是分组边界（长度 = counts.length + 1），相邻矩形无间隙
function drawHistogram(edges, counts, x0, yBase, w, opts) {
    opts = _normOpts(opts);
    if (!counts || !counts.length) return;
    const maxV = opts.max || Math.max.apply(null, counts) || 1;
    const full = opts.full || (yBase - (opts.top === undefined ? 40 : opts.top));
    const bw = w / counts.length;
    counts.forEach(function (v, i) {
        const h = (v / maxV) * full;
        const bx = x0 + i * bw;
        ctx.save();
        ctx.fillStyle = opts.color || '#93c5fd';
        ctx.globalAlpha = 0.85;
        ctx.fillRect(bx, yBase - h, bw, h);
        ctx.globalAlpha = 1;
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 1;
        ctx.strokeRect(bx, yBase - h, bw, h);
        ctx.restore();
        if (opts.valuesOnTop) drawTickText(String(v), bx + bw / 2, yBase - h - 7, 'center');
    });
    if (edges) edges.forEach(function (e, i) { drawTickText(String(e), x0 + i * bw, yBase + 10, 'center'); });
    drawLine(x0 - 3, yBase, x0 + w + 3, yBase, '#475569', 1.5);
}

// 【折线图】points 为画布坐标数组；opts = { color, width, dots, dash }
function drawBrokenLine(points, opts) {
    opts = _normOpts(opts);
    if (!points || points.length < 2) return;
    const c = opts.color || '#f97316';
    for (let i = 0; i < points.length - 1; i++) drawLine(points[i].x, points[i].y, points[i + 1].x, points[i + 1].y, c, opts.width || 2, opts.dash);
    if (opts.dots !== false) points.forEach(function (p) { drawPoint(p.x, p.y, null, c); });
}

/**
 * 【扇形图】圆心角 = 360° × 占比。values 自动归一化（不必先算百分比）。
 *   opts = { colors, labels(扇区外侧标名称/字母), r0(内环半径，做环图), startAngle }
 */
function drawSector(values, cx, cy, r, opts) {
    opts = _normOpts(opts);
    if (!values || !values.length) return;
    const sum = values.reduce(function (a, b) { return a + b; }, 0) || 1;
    const colors = opts.colors || ['#60a5fa', '#f472b6', '#34d399', '#fbbf24', '#a78bfa', '#fb7185'];
    let a = (opts.startAngle === undefined ? -90 : opts.startAngle) * _DEG;
    values.forEach(function (v, i) {
        const sweep = (v / sum) * Math.PI * 2;
        ctx.save();
        ctx.fillStyle = colors[i % colors.length];
        ctx.globalAlpha = 0.85;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, r, a, a + sweep);
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();
        if (opts.labels && opts.labels[i] != null) {
            const mid = a + sweep / 2;
            const lr = opts.r0 ? (r + opts.r0) / 2 : r * 0.68;
            drawMathText(String(opts.labels[i]), cx + Math.cos(mid) * lr, cy + Math.sin(mid) * lr, { size: 13, align: 'center', baseline: 'middle' });
        }
        a += sweep;
    });
    if (opts.r0) {
        ctx.save();
        ctx.fillStyle = opts.holeColor || '#ffffff';
        ctx.beginPath();
        ctx.arc(cx, cy, opts.r0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
}

// 【树状图】两级分支（概率题）。level1 / level2 是各节点的标签；返回末级节点的画布坐标数组。
function drawTree(level1, level2, cx, y0, dy, opts) {
    opts = _normOpts(opts);
    const l1 = (Array.isArray(level1) ? level1 : (level1 == null ? [] : [level1])).map(String);
    const l2 = (Array.isArray(level2) ? level2 : (level2 == null ? [] : [level2])).map(String);
    if (!l1.length) return [];
    // 把 n 个孩子均匀铺在宽 bw 上、居中于父节点
    const spread = function (n, bw) {
        if (n <= 1) return [0];
        const step = bw / (n - 1);
        return Array.from({ length: n }, function (_, i) { return (i - (n - 1) / 2) * step; });
    };
    const root = { x: cx, y: y0 };
    drawPoint(root.x, root.y, null, '#1e293b');
    drawMathText(opts.root || 'S', root.x + 10, root.y + 4, { size: 13 });
    const s1 = spread(l1.length, opts.span1 || 200);
    const leaves = [];
    l1.forEach(function (t, i) {
        const p1 = { x: root.x + s1[i], y: root.y + dy };
        drawLine(root.x, root.y, p1.x, p1.y, '#94a3b8', 1.2);
        drawPoint(p1.x, p1.y, null, '#1e293b');
        drawMathText(t, p1.x + 9, p1.y + 4, { size: 12 });
        const s2 = spread(l2.length, opts.span2 || 110);
        l2.forEach(function (u, j) {
            const p2 = { x: p1.x + s2[j], y: p1.y + dy };
            drawLine(p1.x, p1.y, p2.x, p2.y, '#cbd5e1', 1);
            drawPoint(p2.x, p2.y, null, '#64748b');
            drawMathText(u, p2.x + 9, p2.y + 4, { size: 11 });
            leaves.push(p2);
        });
    });
    return leaves;
}

/* ═══════════ G. 文字与符号（3）—— 画布白名单的**唯一强制执行点** ═══════════ */

// 违规登记册（供 CKDrawViolations() 与 window.__DRAW_VIOLATIONS__ 使用）
const _drawViolations = [];
if (typeof window !== 'undefined') window.__DRAW_VIOLATIONS__ = _drawViolations;

/**
 * 已声明的**例外**登记册（数值 / 函数标注）。
 * 为什么要它：Step 2 的 canvasChange 可能**明确要求**"标注交点坐标 / 函数式"（如 `(-1,2)`、`y=-2/x`），
 * 那是允许的例外。但例外必须**显式声明**（调用时传 `{ numeric: true }`），
 * 并且会被记进 `window.__DRAW_EXEMPT__` —— 出口裁决能看到"这份产物用了 N 处数值标注"。
 * ★ 关键：**"合法例外"与"绕过白名单"必须可区分**。
 *   不声明而写数字 = 违规（拒画）；声明了 = 放行但留痕。
 */
const _drawExempt = [];
if (typeof window !== 'undefined') window.__DRAW_EXEMPT__ = _drawExempt;

// 允许的字符（正向白名单）：字母 / 撇号 / 希腊字母 / 数学符号 / 空格
const _TEXT_OK = /^[A-Za-z\u2032'\u03b1-\u03c9\u0391-\u03a9\u2220\u25b3\u2299\u223d\u224c\u22a5\u2225\u00b0\u221a\u03c0+\- ]+$/;

/**
 * 【画布数学文字】★ 画布上写文字**只能走这里**，因为只有这里执行白名单。
 *   违规时：不绘制 + 记录 + console.error。违规数由 CKDrawViolations() 计入 CK 体系。
 *   opts = { size, color, align, baseline, weight, numeric }
 *   ★ `numeric: true` = 声明"这一处是 canvasChange 明确要求的数值/函数标注"（只禁汉字，放行数字/等号/坐标）。
 *     不要图省事到处传它 —— 每传一次都会留痕在 `__DRAW_EXEMPT__` 里，出口裁决会看到数量。
 */
function drawMathText(text, x, y, opts) {
    opts = _normOpts(opts);
    const s = String(text == null ? '' : text);
    const bad = _textViolation(s, !!opts.numeric);
    if (bad) {
        _drawViolations.push({ text: s, x: Math.round(x), y: Math.round(y), reason: bad });
        if (typeof window !== 'undefined') window.__DRAW_VIOLATIONS__ = _drawViolations;
        console.error('❌ 画布白名单违规：' + bad + ' —— 「' + s + '」@(' + Math.round(x) + ',' + Math.round(y) + ')。' +
            '画布只允许字母/希腊字母/数学符号（如 ∠ △ ⊙ ∽ ≌ ⊥ ∥ °），不得出现汉字、数字、等式、坐标。' +
            '题目文字请放在画布**之外**的 HTML 区域；' +
            '若这一处确实是 canvasChange 明确要求的数值/函数标注，请显式传 { numeric: true }。');
        return false;
    }
    if (opts.numeric) {
        _drawExempt.push({ text: s, x: Math.round(x), y: Math.round(y) });
        if (typeof window !== 'undefined') window.__DRAW_EXEMPT__ = _drawExempt;
    }
    ctx.save();
    ctx.fillStyle = opts.color || '#1e293b';
    ctx.font = (opts.weight || 'normal') + ' ' + (opts.size || 14) + 'px "Times New Roman", Georgia, serif';
    ctx.textAlign = opts.align || 'left';
    ctx.textBaseline = opts.baseline || 'alphabetic';
    ctx.fillText(s, x, y);
    ctx.restore();
    return true;
}

// 逐条给出违规原因（顺序即优先级，便于给出精确提示）
// numeric = true 时只保留"禁汉字"这一条（用于 canvasChange 明确要求的数值/函数标注）
function _textViolation(s, numeric) {
    if (!s) return null;
    if (/[\u4e00-\u9fa5]/.test(s)) return '出现汉字';
    if (numeric) return null;
    if (/[0-9\uFF10-\uFF19]/.test(s)) return '出现数字';
    if (/[=\uFF1D]/.test(s)) return '出现等号（等式只能写在页面文字区，画布上用符号与弧线表达）';
    if (/\(\s*[-\u2212]?\s*[0-9A-Za-z]/.test(s)) return '出现括号坐标';
    if (!_TEXT_OK.test(s)) return '含白名单之外的字符';
    return null;
}

// 【符号标记】结论打勾/打叉用。仅允许：✓ ✗ ？ ！ ✕
const _SYM_OK = /^[\u2713\u2717\uFF1F\uFF01\u2715]$/;
function drawSymbol(x, y, text, color, size) {
    const s = String(text == null ? '' : text);
    if (!_SYM_OK.test(s)) {
        _drawViolations.push({ text: s, x: Math.round(x), y: Math.round(y), reason: '符号不在允许集（只允许 ✓ ✗ ？ ！ ✕）' });
        if (typeof window !== 'undefined') window.__DRAW_VIOLATIONS__ = _drawViolations;
        console.error('❌ 画布白名单违规：drawSymbol 只允许 ✓ ✗ ？ ！ ✕ —— 收到「' + s + '」');
        return false;
    }
    ctx.save();
    ctx.fillStyle = color || '#16a34a';
    ctx.font = (size || 16) + 'px "Segoe UI Symbol", "Times New Roman", serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(s, x, y);
    ctx.restore();
    return true;
}

// 【点标签】drawMathText 的语义化别名；dx/dy 为相对标签偏移
function drawLabel(x, y, label, color, dx, dy) {
    return drawMathText(label, x + (dx || 0), y + (dy === undefined ? -8 : dy), { size: 15, color: color, align: 'center' });
}

/* ═══════════ H. 动画与高亮（7）—— 全部走同一个 animId，stopAnim() 一次停全部 ═══════════ */

/**
 * ★ 只有一个动画句柄 animId，且**所有动画都用 requestAnimationFrame 实现**。
 *   历史坑：旧模板里 pulseHighlight/breathe 用 setInterval，而 stopAnim() 只
 *   cancelAnimationFrame(animId) —— 于是 setInterval 停不掉，闪烁会在切帧后继续跑。
 *   现在统一为 rAF（时间戳节流），stopAnim() 真正能停全部。
 */
let animId = null;
let _animFinal = null;      // 当前动画的"最终态"绘制；stopAnim() 会据此收尾，避免停成半途

// 【停下所有动画】停在**最终态**（不是半途）：若有收尾函数则补画一次完整静止帧。
function stopAnim() {
    if (animId) { cancelAnimationFrame(animId); animId = null; }
    if (_animFinal) {
        const f = _animFinal; _animFinal = null;
        clearCanvas(); drawBaseScene(); replayAccumulator(); f(); finishFrame();
    }
}

// 内部：统一的"静止帧"三件套（清屏 → 基底 → 回放）
function _settle() { clearCanvas(); drawBaseScene(); replayAccumulator(); }

// 【线动画】从起点渐进画到终点
function animateLine(x1, y1, x2, y2, color, width, dash, duration, isArrow) {
    duration = duration || 800;
    const t0 = performance.now();
    stopAnim();
    _animFinal = function () { drawLine(x1, y1, x2, y2, color, width, dash); if (isArrow) _arrowHead(x1, y1, x2, y2, color); };
    function tick(now) {
        const t = Math.min((now - t0) / duration, 1);
        _settle();
        const cx = x1 + (x2 - x1) * t, cy = y1 + (y2 - y1) * t;
        drawLine(x1, y1, cx, cy, color, width, dash);
        if (t >= 1) { if (isArrow) _arrowHead(x1, y1, x2, y2, color); finishFrame(); animId = null; _animFinal = null; return; }
        finishFrame();
        animId = requestAnimationFrame(tick);
    }
    animId = requestAnimationFrame(tick);
}

// 【高亮脉冲】元素闪烁 times 次后停在强调色（rAF 版，stopAnim 可停）
function pulseHighlight(drawFn, color, times) {
    times = times || 2;
    const period = 200, total = period * times * 2;
    const t0 = performance.now();
    stopAnim();
    _animFinal = function () { drawFn(color || '#ef4444'); };
    function tick(now) {
        const el = now - t0;
        const phase = Math.floor(el / period);
        _settle();
        drawFn(el >= total ? (color || '#ef4444') : (phase % 2 === 0 ? (color || '#ef4444') : '#1e293b'));
        finishFrame();
        if (el >= total) { animId = null; _animFinal = null; return; }
        animId = requestAnimationFrame(tick);
    }
    animId = requestAnimationFrame(tick);
}

// 【渐显】透明度 0→1（globalAlpha 只作用于本元素）
function fadeIn(drawFn, duration) {
    duration = duration || 600;
    const t0 = performance.now();
    stopAnim();
    _animFinal = function () { drawFn(); };
    function tick(now) {
        const t = Math.min((now - t0) / duration, 1);
        _settle();
        ctx.save();
        ctx.globalAlpha = t;
        drawFn();
        ctx.restore();
        finishFrame();
        if (t >= 1) { animId = null; _animFinal = null; return; }
        animId = requestAnimationFrame(tick);
    }
    animId = requestAnimationFrame(tick);
}

// 【变色强调】颜色在 fromColor → toColor 之间线性插值
function colorShift(drawFn, fromColor, toColor, duration) {
    duration = duration || 600;
    const t0 = performance.now();
    const hex = function (c) { const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(c); return m ? [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)] : [0, 0, 0]; };
    const a = hex(fromColor), b = hex(toColor);
    stopAnim();
    _animFinal = function () { drawFn(toColor); };
    function tick(now) {
        const t = Math.min((now - t0) / duration, 1);
        _settle();
        const c = 'rgb(' + Math.round(a[0] + (b[0] - a[0]) * t) + ',' + Math.round(a[1] + (b[1] - a[1]) * t) + ',' + Math.round(a[2] + (b[2] - a[2]) * t) + ')';
        drawFn(c);
        finishFrame();
        if (t >= 1) { animId = null; _animFinal = null; return; }
        animId = requestAnimationFrame(tick);
    }
    animId = requestAnimationFrame(tick);
}

// 【呼吸】慢速脉动，用于 [pause] 停顿期间画面保持；由 stopAnim() 结束
function breathe(drawFn, color) {
    const period = 1400;
    const t0 = performance.now();
    stopAnim();
    _animFinal = function () { drawFn(color); };
    function tick(now) {
        const t = 0.5 + 0.5 * Math.sin((now - t0) / period * Math.PI * 2);
        _settle();
        ctx.save();
        ctx.globalAlpha = 0.6 + 0.4 * t;
        drawFn(color);
        ctx.restore();
        finishFrame();
        animId = requestAnimationFrame(tick);
    }
    animId = requestAnimationFrame(tick);
}

/**
 * 【平移/旋转动画】逐点插值 fromPts → toPts（同名键一一对应）。
 *   order：连线顺序（如 ['A','B','C']）；opts = { color, duration, isArrow, drawFn }
 *   给了 drawFn(interp) 就用它画；否则按 order 把插值点连成闭合折线。
 */
function animateTransform(fromPts, toPts, order, opts) {
    opts = _normOpts(opts);
    const duration = opts.duration || 900;
    const color = opts.color || '#7c3aed';
    const t0 = performance.now();
    const keys = order || Object.keys(fromPts || {});
    const interp = function (t) {
        const o = {};
        keys.forEach(function (k) {
            const a = fromPts[k], b = (toPts && toPts[k]) || fromPts[k];
            if (!a) return;
            o[k] = { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
        });
        return o;
    };
    const paint = function (o) {
        if (opts.drawFn) { opts.drawFn(o); return; }
        const arr = keys.map(function (k) { return o[k]; }).filter(Boolean);
        if (arr.length >= 2) drawPolygon(arr, { stroke: true, color: color, width: 2, fill: false });
        keys.forEach(function (k) { if (o[k]) drawPoint(o[k].x, o[k].y, k, color); });
    };
    stopAnim();
    _animFinal = function () { if (opts.drawFn) opts.drawFn(interp(1)); else paint(interp(1)); };
    function tick(now) {
        const t = Math.min((now - t0) / duration, 1);
        _settle();
        paint(interp(t));
        if (t >= 1 && opts.isArrow) {
            const a = fromPts[keys[0]], b = toPts[keys[0]];
            if (a && b) _arrowHead(a.x, a.y, b.x, b.y, color);
        }
        finishFrame();
        if (t >= 1) { animId = null; _animFinal = null; return; }
        animId = requestAnimationFrame(tick);
    }
    animId = requestAnimationFrame(tick);
}

/* ═══════════ I. 导出（供 Node 侧校验脚本与产物解构使用） ═══════════ */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        clearCanvas, stateAccumulator, resetAccumulator, recordToAccumulator, replayAccumulator,
        finishFrame, drawCKBadge, CKDrawViolations,
        drawPoint, drawLine, drawRay, drawCircle, drawArc, _arrowHead,
        drawPolygon, hatchRegion,
        drawAngleArc, drawRightAngle, drawEqualMark, drawParallelMark,
        mapping, drawAxes, drawGrid, drawCurve, drawTickText,
        drawBar, drawHistogram, drawBrokenLine, drawSector, drawTree,
        drawMathText, drawSymbol, drawLabel, _textViolation, _drawExempt,
        stopAnim, animateLine, pulseHighlight, fadeIn, colorShift, breathe, animateTransform,
        _drawViolations
    };
}
