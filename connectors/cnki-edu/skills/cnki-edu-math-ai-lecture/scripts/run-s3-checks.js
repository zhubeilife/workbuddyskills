#!/usr/bin/env node
'use strict';

/**
 * ══════════════════════════════════════════════════════════════════
 *  run-s3-checks.js —— S3 / S3.5 出口「一条命令」全量校验（P1-B）
 * ══════════════════════════════════════════════════════════════════
 *
 *  归属：cnki-edu-math-ai-lecture
 *
 *  目的：把原先散落的 8 个独立校验调用（装配 / CK / 帧计数 / 白名单 /
 *        voiceText 符号 / recordToAccumulator / 静态 22 项 / 语法）
 *        合并为**一次工具调用** → 减少 Agent 每轮的上下文重发。
 *
 *  用法：
 *      node scripts/run-s3-checks.js <产物.js> [--s2 <s2.js>] [--raw] [--json] [--quiet]
 *
 *    <产物.js>   装配后的绘图代码（含两块内联库）。若传入的是 slim 裸产物、
 *                带 @@INJECT 标记，脚本会自动先做注入（等价 assemble-artifact.js）。
 *    --s2 <f>    讲题方案（用于 voiceText 数学符号扫描）；省略则尝试从产物内提取。
 *    --raw       强制按「未注入」处理（即使没检测到标记）。
 *    --json      输出结构化 JSON（供流程判断）。
 *
 *  输出：静态体检（A~G）+ 实跑 CK（H）+ 帧结构（I）+ 语音可播性（J）+ 页面加载模拟（K）
 *  退出码：0 全绿 / 1 有问题 / 2 参数或文件错误
 * ══════════════════════════════════════════════════════════════════
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SKILL = path.join(__dirname, '..');
const LIBDIR = path.join(SKILL, 'references');

const BANKS = [
    {
        tag: '几何内核', file: '几何内核.js', ver: 'v2.2', mark: 'GEOM_KERNEL',
        fingerprints: ['const DEG = Math.PI / 180;', 'function CKBounds(', 'function CK(']
    },
    {
        tag: '绘图层', file: '绘图层.js', ver: 'v1.1', mark: 'DRAW_LAYER',
        fingerprints: ['const _DEG = Math.PI / 180;', 'function drawMathText(']
    }
];

const BANNED_SYMBOLS = '△∠⊥∥∽≌°√π⊙±≠≥≤∴∵∈²³×÷';

/* ── 参数 ── */
const argv = process.argv.slice(2);
let s2Path = null, forceRaw = false, asJson = false, quiet = false, file = null, dumpPath = null;
for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--s2') { s2Path = argv[++i]; continue; }
    if (a === '--raw') { forceRaw = true; continue; }
    if (a === '--json') { asJson = true; continue; }
    if (a === '--quiet') { quiet = true; continue; }
    if (a === '--dump') { dumpPath = argv[++i]; continue; }
    if (a.startsWith('--')) { console.error('未知参数：' + a); process.exit(2); }
    if (!file) file = a;
}
if (!file || !fs.existsSync(file)) {
    console.error('用法：node scripts/run-s3-checks.js <产物.js> [--s2 <s2.js>] [--raw] [--json] [--quiet]');
    process.exit(2);
}

const read = p => fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');

/* ══════════════════════════════════════════════════════════════════
 *  第 0 步：需要时先做内联库注入（与 assemble-artifact.js 同规则）
 * ══════════════════════════════════════════════════════════════════ */
let src = read(file);
const needsInject = forceRaw || /\/\*\s*@@INJECT:/.test(src);
const injectLog = [];
if (needsInject) {
    for (const b of BANKS) {
        const marker = `@@INJECT:${b.mark}@@`;
        const idx = src.split('\n').findIndex(l => l.includes(marker));
        if (idx < 0) { console.error('❌ 未找到注入标记：' + marker); process.exit(1); }
        const line = src.split('\n')[idx];
        const indent = (line.match(/^\s*/) || [''])[0];
        const lib = read(path.join(LIBDIR, b.file));
        const injected = lib.split('\n').map(l => (l.trim() === '' ? '' : indent + l)).join('\n');
        src = src.replace(line, injected);
        injectLog.push(`${b.tag}(${b.ver}) 注入 ${lib.split('\n').filter(l => l.trim()).length} 行非空代码`);
    }
    if (/\/\*\s*@@INJECT:/.test(src)) { console.error('❌ 仍有未替换的注入标记'); process.exit(1); }
}

if (dumpPath) { fs.writeFileSync(dumpPath, src, 'utf8'); console.log('已写出注入后产物：' + dumpPath); }

const lines = src.split('\n');
const R = { file, injected: injectLog, checks: [], problems: [] };
const ok = (n, d) => R.checks.push({ name: n, pass: true, detail: d || '' });
const bad = (n, d) => { R.checks.push({ name: n, pass: false, detail: d || '' }); R.problems.push(n + (d ? '：' + d : '')); };

/* ── A. 语法可编译（vm，不 spawn 子进程） ── */
try { new vm.Script(src, { filename: path.basename(file) }); ok('A. 语法可解析', 'vm 编译通过'); }
catch (e) { bad('A. 语法可解析', e.message.split('\n')[0]); }

/* ── B/C. 两块库：逐字保真 + 副本唯一 ── */
const norm = l => l.replace(/\s+$/, '').trim();
const rows = s => s.split('\n').map(r => norm(r)).filter(t => t !== '');
const srcRows = rows(src);
R.libNonEmpty = 0;
for (const b of BANKS) {
    const sRows = rows(read(path.join(LIBDIR, b.file)));
    R.libNonEmpty += sRows.length;
    let hit = false;
    outer: for (let i = 0; i + sRows.length <= srcRows.length; i++) {
        for (let j = 0; j < sRows.length; j++) if (srcRows[i + j] !== sRows[j]) continue outer;
        hit = true; break;
    }
    if (hit) ok('B. ' + b.tag + ' 逐字一致', sRows.length + ' 行非空代码命中');
    else bad('B. ' + b.tag + ' 逐字一致', '未找到与真源一致的连续段');

    const dups = b.fingerprints.map(fp => ({ fp, n: src.split(fp).length - 1 })).filter(d => d.n !== 1);
    if (!dups.length) ok('C. ' + b.tag + ' 副本唯一');
    else bad('C. ' + b.tag + ' 副本唯一', dups.map(d => d.fp + '→' + d.n + '次').join('；'));
}

/* ── D. 骨架完整性 ── */
const code = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
for (const [name, re] of [
    ['档位声明 window.__DRAW_TIER__', /window\.__DRAW_TIER__\s*=\s*'[ABC]'/],
    ['画布尺寸 const W = 360, H = 260', /const\s+W\s*=\s*360\s*,\s*H\s*=\s*260/],
    ['LIB IIFE', /const\s+LIB\s*=\s*\(\s*function\s*\(/],
    ['pts 取自 LIB', /const\s+pts\s*=\s*LIB\.pts/],
    ['解构语句 = LIB', /\}\s*=\s*LIB\s*;/],
    ['持久/临时：qAcc', /\bqAcc\b/],
    ['持久/临时：switchQ', /function\s+switchQ/],
    ['持久/临时：recQ', /function\s+recQ/],
    ['navigationMap', /\bnavigationMap\b/],
    ['drawFunctions', /\bdrawFunctions\b/],
    ['抄写自检日志', /抄写自检日志/]
]) (re.test(src) ? ok : bad).call(null, 'D. ' + name);

const desc = code.match(/const\s*\{[\s\S]*?\}\s*=\s*LIB\s*;/);
if (desc) (/recordToAccumulator/.test(desc[0]) ? bad : ok).call(null, 'D. 解构不含 recordToAccumulator');
else bad('D. 解构语句可定位', '未能提取 `const { … } = LIB;`');

/* ── E. 每帧末行 finishFrame() ── */
{
    const frames = [];
    lines.forEach((l, i) => { const m = l.match(/^\s*function\s+(drawFrame_\d+)\s*\(/); if (m) frames.push({ name: m[1], at: i }); });
    const funcEnd = startAt => {
        let depth = 0, started = false;
        for (let i = startAt; i < lines.length; i++) {
            const l = lines[i].replace(/\/\/.*$/, '').replace(/\/\*[\s\S]*?\*\//g, '');
            for (const ch of l) {
                if (ch === '{') { depth++; started = true; }
                else if (ch === '}') { depth--; if (started && depth === 0) return i; }
            }
        }
        return -1;
    };
    const missing = [];
    frames.forEach(f => {
        const e = funcEnd(f.at);
        if (e < 0) { missing.push(f.name + '→未闭合'); return; }
        const body = lines.slice(f.at + 1, e).map(l => l.trim()).filter(t => t && !t.startsWith('//') && !t.startsWith('/*') && !t.startsWith('*'));
        if (!/finishFrame\s*\(\s*\)/.test(body[body.length - 1] || '')) missing.push(f.name + '→' + String(body[body.length - 1] || '').slice(0, 30));
    });
    R.frameCount = frames.length;
    R.frameNames = frames.map(f => f.name);
    if (!frames.length) bad('E. drawFrame_N 存在', '未找到');
    else if (missing.length) bad('E. 每帧末行 finishFrame()', '缺 ' + missing.length + ' 处：' + missing.slice(0, 4).join(' ｜ '));
    else ok('E. 每帧末行 finishFrame()', frames.length + ' 帧全部合规');
}

/* ── F. 违规项 ── */
{
    const libStart = lines.findIndex(l => /const\s+LIB\s*=\s*\(\s*function\s*\(/.test(l));
    const afterLib = libStart >= 0 ? lines.slice(libStart + 1).join('\n') : src;
    const n = (afterLib.replace(/function\s+recordToAccumulator/g, '').match(/recordToAccumulator\s*\(/g) || []).length;
    (n === 0 ? ok : bad).call(null, 'F. 产物区无 recordToAccumulator 调用', n ? '命中 ' + n + ' 次' : '');

    const prims = ['drawLine', 'drawPoint', 'drawMathText', 'clearCanvas', 'replayAccumulator', 'stopAnim', 'finishFrame', 'drawCircle', 'drawArc', 'drawPolygon'];
    const selfDef = prims.map(p => ({ p, c: (src.match(new RegExp('function\\s+' + p + '\\s*\\(', 'g')) || []).length })).filter(x => x.c > 1);
    (!selfDef.length ? ok : bad).call(null, 'F. 无自写重复绘图基元', selfDef.map(x => x.p + '(' + x.c + ')').join('、'));

    const timers = (code.match(/\b(setInterval|setTimeout)\s*\(/g) || []).length;
    (timers === 0 ? ok : bad).call(null, 'F. 无 setInterval/setTimeout', timers ? '命中 ' + timers + ' 次' : '');
}

/* ── G. CKDrawViolations 早于 CKSummary ── */
{
    const a = src.indexOf('CKDrawViolations()'), b = src.lastIndexOf('CKSummary()');
    if (a < 0) bad('G. CKDrawViolations 存在', '未找到');
    else if (b < 0) bad('G. CKSummary 存在', '未找到');
    else (a < b ? ok : bad).call(null, 'G. CKDrawViolations 早于 CKSummary');
}

/* ── H. 实跑 CKSummary + CKDrawViolations（vm，mock canvas） ── */
{
    const captured = [];
    const mkCtx = () => new Proxy({}, {
        get: (t, k) => {
            if (k === 'canvas') return { width: 360, height: 260 };
            if (k === 'measureText') return () => ({ width: 10 });
            if (k === 'createLinearGradient' || k === 'createRadialGradient') return () => ({ addColorStop() { } });
            if (k === 'getImageData') return () => ({ data: [] });
            if (k === 'createPattern') return () => ({});
            if (typeof k === 'string' && /^(fillStyle|strokeStyle|lineWidth|font|textAlign|textBaseline|globalAlpha|lineCap|lineJoin|miterLimit|shadowBlur|shadowColor|shadowOffsetX|shadowOffsetY|globalCompositeOperation|lineDashOffset|filter|imageSmoothingEnabled)$/.test(k)) return '';
            return () => { };
        },
        set: () => true
    });
    const sandbox = {
        console: { log: (...a) => captured.push(a.join(' ')), error: (...a) => captured.push('ERR ' + a.join(' ')), warn: (...a) => captured.push('WARN ' + a.join(' ')) },
        Math, JSON, Date, Array, Object, String, Number, Boolean, RegExp, Error, isNaN, isFinite, parseInt, parseFloat,
        performance: { now: () => Date.now() },
        requestAnimationFrame: () => 0,
        cancelAnimationFrame: () => { },
        setTimeout: () => 0,
        clearTimeout: () => { },
        setInterval: () => 0,
        clearInterval: () => { },
        devicePixelRatio: 1
    };
    sandbox.window = sandbox;
    sandbox.globalThis = sandbox;
    // 仿真页面模板（step4）在 S3 代码前声明的 `const canvasEl / const ctx`：
    // 裸 S3 自身不含 ctx（由模板提供，见 references/html-template.html 数据区 3-前置），
    // K 段驱动 drawFrame_N 时必须有它，否则会误报 `ctx is not defined`。
    sandbox.ctx = mkCtx();
    sandbox.canvasEl = { width: 360, height: 260, getContext: mkCtx, style: {} };
    sandbox.document = { getElementById: () => ({ getContext: mkCtx, width: 360, height: 260, style: {} }), createElement: () => ({ getContext: mkCtx, style: {} }), addEventListener() { }, querySelector: () => null, body: { appendChild() { } } };
    let runErr = null;
    try { vm.createContext(sandbox); vm.runInContext(src, sandbox, { filename: path.basename(file) }); }
    catch (e) { runErr = e.message; }

    const ckLine = captured.find(l => l.includes('【绘图校验】')) || '';
    R.ckLine = ckLine;
    R.capturedTail = captured.slice(-14);
    const mCk = ckLine.match(/(\d+)\s*\/\s*(\d+)/);
    R.ckPass = mCk ? Number(mCk[1]) : null;
    R.ckTotal = mCk ? Number(mCk[2]) : null;
    R.ckReport = sandbox.window && sandbox.window.__CK_REPORT__ ? sandbox.window.__CK_REPORT__ : null;

    if (runErr) bad('H. 产物可执行（vm）', runErr.split('\n')[0]);
    else ok('H. 产物可执行（vm）', '无抛错');
    if (!mCk) bad('H. CKSummary 全绿', '未捕获到【绘图校验】汇总行');
    else if (R.ckPass === R.ckTotal) ok('H. CKSummary 全绿', ckLine.trim());
    else bad('H. CKSummary 全绿', ckLine.trim());
    const errLines = captured.filter(l => l.startsWith('ERR'));
    if (errLines.length) bad('H. 无 console.error', errLines.length + ' 条：' + errLines.slice(0, 2).join(' ｜ '));
    else ok('H. 无 console.error');

    /* ── K. 页面加载模拟：逐帧实跑 drawFrame_N（补 H 只跑 CK 的盲区） ──
       背景：H 只执行脚本末尾的 CKSummary / CKDrawViolations，**从不调用各 drawFrame_N**。
       于是两类问题会被 H 漏掉、直到页面打开才爆发：
         ① 帧函数体内的 ReferenceError —— 构造点集/几何算子若没从 LIB 解构到顶层，
            帧里引用它们即抛（页面白屏）；
         ② 帧内 replayAccumulator 触发的画布白名单违规（console.error 刷屏）。
       本段模拟页面 renderNode：按帧号顺序调用每个 drawFrame_N，捕获抛错与驱动期 console.error。 */
    {
        const errBefore = captured.length;
        const frameNames = R.frameNames || [];
        const frameErrs = [];
        for (const fn of frameNames) {
            const f = sandbox[fn];
            if (typeof f !== 'function') { frameErrs.push(fn + '→未成为全局函数（页面不会调用它）'); continue; }
            try { f(); } catch (e) { frameErrs.push(fn + '→' + (e && e.message ? e.message : String(e))); }
        }
        const newErrs = captured.slice(errBefore).filter(l => l.startsWith('ERR'));
        R.frameDriveCount = frameNames.length;
        R.frameDriveErrors = frameErrs;
        R.frameDriveConsoleErrors = newErrs;
        if (!frameNames.length) bad('K. 页面加载模拟（逐帧执行 drawFrame_N）', '无可驱动的帧函数');
        else if (frameErrs.length) bad('K. 页面加载模拟（逐帧执行 drawFrame_N）', frameErrs.slice(0, 3).join(' ｜ '));
        else ok('K. 页面加载模拟（逐帧执行 drawFrame_N）', frameNames.length + ' 帧实跑无抛错');
        if (newErrs.length) bad('K. 帧执行无 console.error（白名单等）', newErrs.length + ' 条：' + newErrs.slice(0, 2).join(' ｜ '));
        else ok('K. 帧执行无 console.error（白名单等）');
    }
}

/* ── I. 帧结构一致性 ── */
{
    const frameNums = (R.frameNames || []).map(n => Number(n.replace('drawFrame_', ''))).sort((a, b) => a - b);
    const contiguous = frameNums.length > 0 && frameNums.every((v, i) => v === i);
    (contiguous ? ok : bad).call(null, 'I. 帧号 0..N 连续', frameNums.join(','));
    const dfm = src.match(/const\s+drawFunctions\s*=\s*\[([\s\S]*?)\]/);
    if (dfm) {
        const items = (dfm[1].match(/drawFrame_\d+/g) || []);
        R.drawFunctionsLen = items.length;
        if (items.length === frameNums.length) ok('I. drawFunctions 长度 = 帧数', items.length + ' 项');
        else bad('I. drawFunctions 长度 = 帧数', items.length + ' vs 帧数 ' + frameNums.length);
    } else bad('I. drawFunctions 可定位', '未找到');

    const nav = src.match(/const\s+navigationMap\s*=\s*\{[\s\S]*?\n\s*\};/);
    if (nav) {
        const nums = [];
        for (const m of nav[0].matchAll(/frame:\s*(\d+)/g)) nums.push(Number(m[1]));
        for (const m of nav[0].matchAll(/frames:\s*\[([0-9,\s]+)\]/g)) m[1].split(',').forEach(x => { if (x.trim() !== '') nums.push(Number(x.trim())); });
        for (const m of nav[0].matchAll(/(?:totalIntro|finalSummary)\s*:\s*(\d+)/g)) nums.push(Number(m[1]));
        const uniq = [...new Set(nums)].sort((a, b) => a - b);
        R.navFrames = uniq;
        const same = uniq.length === frameNums.length && uniq.every((v, i) => v === frameNums[i]);
        (same ? ok : bad).call(null, 'I. navigationMap 覆盖全部帧', uniq.join(','));
    } else bad('I. navigationMap 可定位', '未找到');
}

/* ── J. 语音可播性：voiceText 数学符号扫描 ── */
{
    let text = '';
    if (s2Path && fs.existsSync(s2Path)) text = read(s2Path);
    else {
        const qd = src.match(/const\s+questionData\s*=\s*\{[\s\S]*?\n\s*\};/);
        if (qd) text = qd[0];
    }
    if (!text) bad('J. voiceText 可扫描', '未提供 --s2 且产物内未找到 questionData');
    else {
        const vts = [...text.matchAll(/voiceText:\s*"([^"]*)"/g)].map(m => m[1]);
        R.voiceTextCount = vts.length;
        const hits = [];
        vts.forEach((v, i) => { for (const ch of BANNED_SYMBOLS) if (v.includes(ch)) hits.push('#' + i + '[' + ch + ']'); });
        R.voiceHits = hits;
        if (!vts.length) bad('J. voiceText 存在', '未提取到 voiceText');
        else if (hits.length) bad('J. voiceText 无数学符号', hits.length + ' 处：' + hits.slice(0, 6).join(' '));
        else ok('J. voiceText 无数学符号', vts.length + ' 条全清白');

        const marks = ['[指令性]', '[启发性]', '[确认性]', '[升华性]', '[转折]', '[冲突]', '[pause'];
        const present = marks.filter(m => text.includes(m));
        R.voiceMarks = present;
        if (present.length >= 4) ok('J. 方括号标记保留', present.join(' '));
        else bad('J. 方括号标记保留', '仅见 ' + present.join(' '));
    }
}

/* ══════════════════════════════════════════════════════════════════
 *  输出
 * ══════════════════════════════════════════════════════════════════ */
const summary = {
    file: R.file,
    injected: R.injected,
    pass: R.problems.length === 0,
    problems: R.problems,
    libNonEmpty: R.libNonEmpty,
    frameCount: R.frameCount || 0,
    drawFunctionsLen: R.drawFunctionsLen || 0,
    navFrames: R.navFrames || [],
    ck: R.ckLine ? R.ckLine.trim() : null,
    ckPass: R.ckPass, ckTotal: R.ckTotal,
    ckOk: R.ckReport ? R.ckReport.ok : null,
    voiceTextCount: R.voiceTextCount || 0,
    voiceHits: R.voiceHits || [],
    frameDriveCount: R.frameDriveCount || 0,
    frameDriveErrors: R.frameDriveErrors || [],
    frameDriveConsoleErrors: R.frameDriveConsoleErrors || [],
    checks: R.checks
};

if (asJson) {
    console.log(JSON.stringify(summary, null, 2));
    process.exit(R.problems.length ? 1 : 0);
}

if (!quiet) {
    console.log('产物　：' + R.file);
    if (R.injected.length) R.injected.forEach(x => console.log('注入　：' + x));
    console.log('行数　：' + lines.length + '　库非空代码：' + R.libNonEmpty + ' 行');
    console.log('─'.repeat(64));
    for (const c of R.checks) console.log((c.pass ? '  ✅ ' : '  ❌ ') + c.name + (c.detail ? '　—— ' + c.detail : ''));
    console.log('─'.repeat(64));
    console.log('帧数：' + summary.frameCount + '　drawFunctions：' + summary.drawFunctionsLen +
        '　navigationMap 覆盖：' + (summary.navFrames.length ? summary.navFrames.join(',') : '—'));
    console.log('CK：' + (summary.ck || '—') + '　__CK_REPORT__.ok=' + summary.ckOk);
    console.log('voiceText：' + summary.voiceTextCount + ' 条，符号命中 ' + summary.voiceHits.length);
    console.log('═'.repeat(64));
}
if (R.problems.length) {
    console.log('结论：❌ ' + R.problems.length + ' 项未通过 —— ' + R.problems.slice(0, 6).join(' ｜ '));
    process.exit(1);
}
console.log('结论：✅ 全部 ' + R.checks.length + ' 项通过（帧 ' + summary.frameCount + '，CK ' + summary.ck + '）');
process.exit(0);
