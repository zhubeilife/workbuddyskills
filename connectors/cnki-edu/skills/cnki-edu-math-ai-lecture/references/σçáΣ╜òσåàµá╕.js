// ══════════════════════════════════════════════════════════════════════
//  几何内核 v2.2 —— 让 LLM「按尺规构造」而不是「手算坐标」
//
//  设计目标：覆盖初中数学全部平面几何作图需求。
//    v1.x 的算子集只覆盖「直线族」（点/线/垂线/交点），
//    对「圆族」完全缺失 —— 实测两份真实产物（2026·浙江圆题、2025·宁夏
//    尺规作图）全部栽在这里：
//      · 圆题的 C、E 是「直线 ∩ 圆」的交点 → 手算后 |OC| 差 8.6px、
//        ∠FGE 实际 46.92°（要求 90°，差 43°）
//      · 尺规作图的两弧交点 Q，模型在注释里直接写「示意位置」
//    这两类交点数学上是二次方程，人算必错、代码算准。
//
//  v2.2 变更（相对 v2.1，算子集不变，只收紧"可传参数"）：
//    ① CKBounds 只接受 1 个参数，删掉 (pts,pad) / (pts,W,H) 两条通道。
//       尖角：题面有点名 H 时写 CKBounds(ALL, W, H) → 第 3 参是点对象 → mg=360
//       → 全部点误判越界。留白区是流水线常量，调用点传它没有意义。
//    ② CKSpacing 的 minGap 冻结进内核常量 SPACING_MIN。
//    一句话：**凡是能当参数传进去的阈值，模型一定会改** —— 全部收进内核。
//
//  v2.1 变更（相对 v2.0，算子集不变，只扩报告）：
//    CKSummary 写入的 window.__CK_REPORT__ 增加 names 字段（全部校验项名称）。
//    为什么必须加：出口裁决要判断"有没有做题目结论/答案反查"，
//    而**文本判据是死的** —— 本文件 CKConcl/CKAns 的定义里就写着「【结论】」三个字，
//    于是"产物文件里出现过【结论】"对任何内联了内核的页面都恒为真。
//    只有"运行时真的执行过一条名字带【结论】/【答案】的 CK"才算证据。
//
//  v2.0 新增（相对 v1.1）：
//    ① 圆族：onCircle / circleLineInters / circleCircleInters /
//            arcMid / tangentAt / tangentPt
//    ② 交点选择器：nearerTo / fartherFrom / upperOf / lowerOf / onSideOf
//       —— 用「离谁近/在上方」这类语义选点，取代 ± 号猜测
//    ③ 直线对象化：parallelThrough / perpThrough / lineInter
//    ④ 整图变换：rotateAbout / reflect / scaleAbout（旋转·翻折·位似）
//    ⑤ 特殊点：perpBisectorPt（中垂线） / angleBisectorPt（角平分线） / lerp
//    ⑥ 量测：dist / areaOf / ratio
//    ⑦ 校验包装：CKPerp / CKParallel / CKCollinear / CKOnCircle / CKEqual /
//                CKConcl / CKAns（把"怎么量"也收进内核，模型只报期望值）
//
//  用法：整段复制到 Step 3 绘图代码区最前面（包在 IIFE 里），
//        然后用构造函数表达图形，最后 CK() 自检、CKSummary() 汇总。
//
//  核心思想：
//    1. 只给「基础点位」写数字（圆心、半径、一条基准线）
//    2. 其余点一律由构造关系算出（中点/垂线/交点/垂足/定角射线/圆交点）
//    3. 交付前必须跑 CK()；任何 ❌ 先修好，不许改阈值（CK 没有容差参数）
// ══════════════════════════════════════════════════════════════════════

const DEG = Math.PI / 180;

/* ─────────────── 基础向量运算 ─────────────── */
const sub = (a, b) => ({ x: a.x - b.x, y: a.y - b.y });      // a - b
const add = (a, b) => ({ x: a.x + b.x, y: a.y + b.y });      // a + b
const mul = (a, k) => ({ x: a.x * k, y: a.y * k });          // a × k
const len = a => Math.hypot(a.x, a.y);                       // 模长
const dot = (a, b) => a.x * b.x + a.y * b.y;                 // 点积（仅构造用，禁止直接当判定）
const cross = (a, b) => a.x * b.y - a.y * b.x;               // 叉积
const unit = a => { const l = Math.hypot(a.x, a.y) || 1; return { x: a.x / l, y: a.y / l }; };
const dist = (A, B) => len(sub(A, B));                       // 两点距离

// 向量旋转 deg 度（逆时针为正；canvas 的 y 轴向下，视觉上表现为顺时针）
const rot = (a, deg) => ({
  x: a.x * Math.cos(deg * DEG) - a.y * Math.sin(deg * DEG),
  y: a.x * Math.sin(deg * DEG) + a.y * Math.cos(deg * DEG)
});

/* ═══════════ 一、直线族构造算子 ═══════════ */

// 【中点】D = mid(A, C)                                        —— 对应「D 是 AC 中点」
const mid = (a, b) => ({ x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 });

// 【定比取点】P = A + t·(B−A)                                  —— 对应「BF = t·BC」，t=0.5 即中点
const lerp = (A, B, t) => add(A, mul(sub(B, A), t));

// 【射线取点】从 P 沿 dir 方向走 d 的距离                      —— 对应「在射线 XX 上取点」
const rayPt = (P, dir, d) => add(P, mul(unit(dir), d));

// 【延长】从 X 过 Y 再延长 extra                                —— 对应「延长 DE 到 F，使 EF = d」
const extendTo = (X, Y, extra) => rayPt(X, sub(Y, X), len(sub(Y, X)) + (extra || 0));

// 【垂线方向】过 (XY) 的垂线方向                                —— 对应「作 XX 的垂线」
const perpOf = (X, Y) => rot(unit(sub(Y, X)), 90);

// 【直线交点】线1 过 p1 方向 d1；线2 过 p2 方向 d2              —— 对应「交 XX 于点 X」
const inter = (p1, d1, p2, d2) => {
  const den = cross(d1, d2);
  if (Math.abs(den) < 1e-9) return null;               // 平行，无交点
  return add(p1, mul(d1, cross(sub(p2, p1), d2) / den));
};

// 【直线对象】把「过 P、方向 d」打包，便于链式表达
const parallelThrough = (P, X, Y) => ({ p1: P, d: sub(Y, X) });    // 过 P 平行于 XY
const perpThrough = (P, X, Y) => ({ p1: P, d: perpOf(X, Y) });     // 过 P 垂直于 XY
const lineInter = (L1, L2) => inter(L1.p1, L1.d, L2.p1, L2.d);     // 两直线对象求交

// 【垂足】A 到直线 (XY) 的垂足                                  —— 对应「过 A 作 XX 的垂线，垂足为 P」
const foot = (A, X, Y) => {
  const d = unit(sub(Y, X));
  return add(X, mul(d, dot(sub(A, X), d)));
};

// 【定角射线与直线求交（自动判侧，无符号猜测）】
//   从 origin 出发、与 origin→ref 成 ang 度的射线，与「过 Q、方向 d」的直线求交；
//   side = +1 取与 Q 沿 +d 方向同侧的交点，-1 取异侧。
const angledInter = (origin, ref, ang, Q, d, side) => {
  const cands = [ang, -ang]
    .map(a => inter(origin, rot(unit(sub(ref, origin)), a), Q, d))
    .filter(Boolean);
  if (cands.length === 0) return null;                  // 两方向都平行
  if (cands.length === 1) return cands[0];
  const s = side < 0 ? -1 : 1;
  return cands.find(c => s * dot(d, sub(c, Q)) > 0) || cands[0];
};

/* ═══════════ 二、圆族构造算子（v2.0 新增） ═══════════ */

// 【圆上取点】圆心 O、半径 R，方向为「O→ref 旋转 ang 度」        —— 对应「点 C 在 ⊙O 上」
const onCircle = (O, R, ref, ang) => {
    const base = len(sub(ref, O)) < 1e-9 ? { x: 1, y: 0 } : unit(sub(ref, O));
    return add(O, mul(rot(base, ang || 0), R));
};

// 【圆上按角度取点】ang 为**画布绝对角**（0° = +x 方向，正值视觉顺时针）。
//   放「直径端点」「正多边形顶点」这类点用它最稳，不必先找一个参考点。
const onCircleAt = (O, R, ang) => add(O, mul(rot({ x: 1, y: 0 }, ang), R));

// 【直线 × 圆 交点】直线过 p1、方向 d；圆 (O, R)。
//   返回数组，**按沿 d 方向排序**（[0] 为离 p1 近的，[1] 为远的）；相离返回 []。
const circleLineInters = (O, R, p1, d) => {
  const u = unit(d), f = sub(p1, O);
  const b = dot(f, u), c = dot(f, f) - R * R;
  const disc = b * b - c;
  if (disc < -1e-9) return [];
  const s = Math.sqrt(Math.max(0, disc));
  return [{ t: -b - s }, { t: -b + s }].sort((p, q) => p.t - q.t).map(o => add(p1, mul(u, o.t)));
};

// 【圆 × 圆 交点】返回数组（[0] 在 O1→O2 的逆时针侧，[1] 在顺时针侧）；无交点返回 []。
const circleCircleInters = (O1, R1, O2, R2) => {
  const d = dist(O1, O2);
  if (d < 1e-9) return [];                                              // 同心
  if (d > R1 + R2 + 1e-9 || d < Math.abs(R1 - R2) - 1e-9) return [];    // 外离 / 内含
  const a = (R1 * R1 - R2 * R2 + d * d) / (2 * d);
  const h = Math.sqrt(Math.max(0, R1 * R1 - a * a));
  const base = add(O1, mul(unit(sub(O2, O1)), a));
  if (h < 1e-9) return [base];                                          // 相切
  const n = rot(unit(sub(O2, O1)), 90);
  return [add(base, mul(n, h)), add(base, mul(n, -h))];
};

// 【交点选择器】用语义选点，取代 ± 号猜测（交点多于一个时**必须**用它）
const nearerTo = (arr, P) => arr.slice().sort((a, b) => dist(a, P) - dist(b, P))[0] || null;
const fartherFrom = (arr, P) => arr.slice().sort((a, b) => dist(b, P) - dist(a, P))[0] || null;
const upperOf = arr => arr.slice().sort((a, b) => a.y - b.y)[0] || null;   // 画布 y 向下，y 小者在上
const lowerOf = arr => arr.slice().sort((a, b) => b.y - a.y)[0] || null;
const onSideOf = (arr, X, Y, side) => {
  const d = sub(Y, X), s = side < 0 ? -1 : 1;
  return arr.find(p => s * cross(d, sub(p, X)) > 0) || arr[0] || null;
};

// 【弧中点】圆 (O,R) 上弧 AB 的中点；side = +1 / -1 取两侧的那一个
const arcMid = (O, R, A, B, side) => {
  const ua = unit(sub(A, O)), ub = unit(sub(B, O));
  const sum = add(ua, ub);
  let bis = len(sum) < 1e-9 ? rot(ua, 90) : unit(sum);     // 对径点时取垂直方向
  return add(O, mul((side < 0 ? -1 : 1) === 1 ? bis : mul(bis, -1), R));
};

// 【过圆上一点的切线】返回直线对象，可直接喂 lineInter
const tangentAt = (O, R, P) => ({ p1: P, d: perpOf(O, P) });

// 【过圆外一点作圆的切点】side = +1 / -1 取两条切线之一的切点
const tangentPt = (O, R, P, side) => {
  const dOP = dist(P, O);
  if (dOP < R - 1e-9) return null;                          // P 在圆内，无切线
  const aDeg = Math.acos(Math.max(-1, Math.min(1, R / dOP))) / DEG;
  return add(O, mul(rot(unit(sub(P, O)), (side < 0 ? -1 : 1) * aDeg), R));
};

/* ═══════════ 三、整图变换（v2.0 新增） ═══════════ */

// 【绕点旋转】P 绕 O 逆时针转 ang 度                              —— 对应「△ABC 绕点 O 旋转得到△A′B′C′」
const rotateAbout = (P, O, ang) => add(O, rot(sub(P, O), ang));

// 【轴对称】P 关于直线 (XY) 的对称点                              —— 对应「沿 CD 翻折，A 对应 A′」
const reflect = (P, X, Y) => add(mul(foot(P, X, Y), 2), mul(P, -1));

// 【位似/放缩】P 关于中心 O 位似比 k（k<0 为反向）                 —— 对应「以 O 为位似中心放大 k 倍」
const scaleAbout = (P, O, k) => add(O, mul(sub(P, O), k));

// 【中垂线取点】XY 的中垂线上、距中点 |t| 的点
const perpBisectorPt = (X, Y, t) => add(mid(X, Y), mul(perpOf(X, Y), t));

// 【角平分线取点】∠PVQ 的平分线上、距顶点 V 为 t 的点
const angleBisectorPt = (V, P, Q, t) =>
  add(V, mul(unit(add(unit(sub(P, V)), unit(sub(Q, V)))), t));

/* ═══════════ 四、量测算子（供 CK 使用） ═══════════ */

const angBetween = (u, v) =>
  Math.acos(Math.max(-1, Math.min(1, dot(u, v) / ((len(u) * len(v)) || 1)))) / DEG;

// 顶点 Vtx 处、由 P 与 Q 张开的角度 ∠PVQ
const angAt = (P, Vtx, Q) => angBetween(sub(P, Vtx), sub(Q, Vtx));

// 点到直线 (XY) 的距离（用于判断"点在直线上"）
// 【点到直线距离】★ X、Y 是**直线上的两个点**（不是方向向量！）
//   错误写法：distToLine(P, X, sub(Y, X))   ← 把方向当点，会得到无意义的数
//   正确写法：distToLine(P, X, Y)
const distToLine = (P, L1, L2) => Math.abs(cross(sub(L1, P), sub(L2, L1))) / (len(sub(L2, L1)) || 1);

// 三角形面积 / 两量之比
const areaOf = (A, B, C) => Math.abs(cross(sub(B, A), sub(C, A))) / 2;
const ratio = (a, b) => (b === 0 ? Infinity : a / b);

/* ═══════════ 五、校验闸门（交付前必须全绿） ═══════════ */

// ★ 全部容差只在这里定义一次。CK() 没有容差参数，调用处无法改松判定。
const TOL = { '°': 0.5, 'px': 0.5, '': 1e-6 };

const _ckLog = [];

/**
 * 记录一条约束校验结果。
 * @param name    约束名称（结论/答案项请以【结论】【答案】开头）
 * @param actual  实测值
 * @param expect  期望值
 * @param unit    '°'（角度，容差 0.5°） | 'px'（长度，容差 0.5px） | 省略（精确相等）
 */
function CK(name, actual, expect, unit) {
  const u = unit === undefined ? '' : unit;
  const tol = TOL[u];
  const ok = Math.abs(actual - expect) <= tol;
  _ckLog.push({ ok: ok, name: name });
  const f = v => (u === '°' ? v.toFixed(2) + '°' : u === 'px' ? v.toFixed(1) + 'px' : String(v));
  console[ok ? 'log' : 'error'](
    (ok ? '✅ ' : '❌ ') + '绘图校验 ' + name + '：实测 ' + f(actual) + '，期望 ' + f(expect)
  );
  return ok;
}

/* ── 常用校验包装：把「怎么量」也收进内核，模型只报期望值 ── */
// ⚠️ 两个"垂直"不是一回事，别用错：
//    CKPerp      量的是**顶点角** ∠AVB = 90°（顶点 V、两边到 A 和 B）
//    CKPerpLines 量的是**两条直线**的夹角 = 90°（各自给两点定方向）
const CKPerp = (name, A, V, B) => CK(name, angAt(A, V, B), 90, '°');              // ∠AVB = 90°
const CKPerpLines = (name, X1, Y1, X2, Y2) => CK(name, angBetween(sub(Y1, X1), sub(Y2, X2)), 90, '°'); // 线XY ⊥ 线UV
const CKParallel = (name, X1, Y1, X2, Y2) => {
    const a = angBetween(sub(Y1, X1), sub(Y2, X2));
    return CK(name, Math.min(a, 180 - a), 0, '°');                                  // 方向可反，取锐角
};
const CKCollinear = (name, P, X, Y) => CK(name, distToLine(P, X, Y), 0, 'px');    // P 在直线 XY 上
const CKOnCircle = (name, P, O, R) => CK(name, dist(P, O), R, 'px');              // P 在圆 (O,R) 上
const CKEqual = (name, a, b) => CK(name, a, b, 'px');                            // 两长度相等
const CKConcl = (name, actual, expect, unit) => CK('【结论】' + name, actual, expect, unit);
const CKAns = (name, actual, expect, unit) => CK('【答案】' + name, actual, expect, unit);

/**
 * 画布常量：留白区统一 [pad, W-pad] × [pad, H-pad]，本流水线为 [20,340]×[20,240]。
 * ★ CKBounds 默认直接读这里，**调用时不要传 W / H** ——
 *   点名 A…H 里的 H 会遮蔽画布高度 H，静默算出 NaN，把所有点误判为越界。
 */
const CANVAS = { W: 360, H: 260, pad: 20 };

/**
 * 留白区校验：所有点必须落在 [CANVAS.pad, W-pad] × [pad, H-pad] 内。
 * ★ v2.2：**只接受 1 个参数**。多余参数一概忽略并告警。
 *   为什么删掉「(pts, pad) / (pts, W, H)」两条通道：
 *   实测尖角 —— 若题面有点名叫 `H`，产物写 `CKBounds(ALL, W, H)`，
 *   第 3 个参数是**点对象**，于是落到 `mg = a`（a=360）→ 全部点判越界。
 *   留白区与画布尺寸是**本流水线的常量**，调用点传它没有任何意义，
 *   而这正是「凡是能当参数传进去的阈值，模型一定会改」的同一条铁律。
 *   唯一正确写法：CKBounds(ALL)
 */
function CKBounds(ptsObj) {
  if (arguments.length > 1) {
    console.warn('⚠️ CKBounds 只接受 1 个参数（画布尺寸与留白区是内核常量，不用传）；' +
      '已忽略多余的 ' + (arguments.length - 1) + ' 个参数。请改写成 CKBounds(pts)。');
  }
  const Wp = CANVAS.W, Hp = CANVAS.H, mg = CANVAS.pad;
  let bad = 0;
  Object.keys(ptsObj).forEach(function (k) {
    const p = ptsObj[k];
    if (!p || typeof p.x !== 'number' || typeof p.y !== 'number') return;
    if (!(p.x >= mg && p.x <= Wp - mg && p.y >= mg && p.y <= Hp - mg)) {
      _ckLog.push({ ok: false, name: '点 ' + k + ' 越界(' + p.x.toFixed(1) + ',' + p.y.toFixed(1) + ')' });
      console.error('❌ 点 ' + k + ' 越界 (' + p.x.toFixed(1) + ',' + p.y.toFixed(1) + ')');
      bad++;
    }
  });
  return bad === 0;
}

/**
 * 汇总并输出。汇总行格式固定为「【绘图校验】n/n 通过」，供 Step 3.5 与
 * 流程外质检脚本用正则抓取；同时把结果写到 window.__CK_REPORT__。
 * @returns {boolean} 是否全部通过
 */
function CKSummary() {
  const bad = _ckLog.filter(r => !r.ok);
  console.log('【绘图校验】' + (_ckLog.length - bad.length) + '/' + _ckLog.length + ' 通过');
  if (bad.length) {
    console.error('⚠️ 以下约束未通过，图形不可交付：');
    bad.forEach(r => console.error('   ❌ ' + r.name));
  }
  try {
    if (typeof window !== 'undefined') {
      window.__CK_REPORT__ = {
        pass: _ckLog.length - bad.length,
        total: _ckLog.length,
        failures: bad.map(r => r.name),
        // ★ 全部校验项名称（不只是失败项）。
        //   为什么需要它：出口裁决要判断"有没有做题目结论/答案反查"，
        //   而文本判据是死的 —— 内核自己的 CKConcl/CKAns 定义里就写着「【结论】」三个字，
        //   于是"文件里出现过【结论】"对任何内联了内核的产物都恒为真。
        //   只有"运行时真的执行过一条名字带【结论】/【答案】的 CK"才算证据。
        names: _ckLog.map(r => r.name),
        ok: bad.length === 0
      };
    }
  } catch (e) { /* 非浏览器环境忽略 */ }
  return bad.length === 0;
}

// 标签最小间距：与 TOL 同理 —— 阈值冻结在内核里，调用点无法改松。
const SPACING_MIN = 12;

// 判断点阵的最小间距，避免标签/点重叠
function CKSpacing(pts) {
  const minGap = SPACING_MIN;
  const ks = Object.keys(pts).filter(k => pts[k] && typeof pts[k].x === 'number');
  let ok = true;
  for (let i = 0; i < ks.length; i++) {
    for (let j = i + 1; j < ks.length; j++) {
      const d = len(sub(pts[ks[i]], pts[ks[j]]));
      if (d < minGap) {
        console.warn('⚠️ ' + ks[i] + ' 与 ' + ks[j] + ' 距离仅 ' + d.toFixed(1) + 'px，标签可能重叠');
        ok = false;
      }
    }
  }
  return ok;
}

/* ═══════════ 六、导出（供 Node 校验脚本使用） ═══════════ */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DEG, sub, add, mul, len, dot, cross, unit, dist, rot,
    mid, lerp, rayPt, extendTo, perpOf, inter, parallelThrough, perpThrough, lineInter, foot, angledInter,
    onCircle, onCircleAt, circleLineInters, circleCircleInters, nearerTo, fartherFrom, upperOf, lowerOf, onSideOf,
    arcMid, tangentAt, tangentPt,
    rotateAbout, reflect, scaleAbout, perpBisectorPt, angleBisectorPt,
    angBetween, angAt, distToLine, areaOf, ratio,
    CANVAS,
    TOL, SPACING_MIN, CK, CKPerp, CKPerpLines, CKParallel, CKCollinear, CKOnCircle, CKEqual, CKConcl, CKAns,
    CKSummary, CKBounds, CKSpacing
  };
}
