#!/usr/bin/env node
'use strict';

/**
 * ══════════════════════════════════════════════════════════════════
 *  verify-artifact.js —— Step 3 产物体检（独立复算，不采信模型自称）
 * ══════════════════════════════════════════════════════════════════
 *
 *  用法：
 *      node verify-artifact.js <产物.js>            # 体检 + 打印报告
 *      node verify-artifact.js <产物.js> --json     # 只输出 JSON（供批量对比）
 *
 *  体检项：
 *    A. 语法可解析（vm 进程内编译，不 spawn 子进程）
 *    B. 两块内联库与真源**逐字一致**（忽略行首缩进与行尾空白）
 *    C. 副本数量闸门（库指纹在全文只出现 1 次）
 *    D. 骨架完整性（档位声明 / W,H / LIB / 解构 / qAcc,switchQ,recQ / navigationMap / drawFunctions）
 *    E. 每帧末行 finishFrame()
 *    F. 违规项（产物区 recordToAccumulator( 命中数、自写同名绘图基元）
 *    G. CKDrawViolations() 是否在 CKSummary() 之前
 *
 *  退出码：0 全部通过 / 1 有问题 / 2 参数或文件错误
 * ══════════════════════════════════════════════════════════════════
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SKILL = path.join(__dirname, '..');
const LIBDIR = path.join(SKILL, 'references');

const BANKS = [
    {
        tag: '几何内核', file: '几何内核.js', ver: 'v2.2',
        fingerprints: ['const DEG = Math.PI / 180;', 'function CKBounds(']
    },
    {
        tag: '绘图层', file: '绘图层.js', ver: 'v1.1',
        fingerprints: ['const _DEG = Math.PI / 180;', 'function drawMathText(']
    }
];

const argv = process.argv.slice(2);
const AS_JSON = argv.includes('--json');
const file = argv.find(a => !a.startsWith('--'));
if (!file || !fs.existsSync(file)) {
    console.error('用法：node verify-artifact.js <产物.js> [--json]');
    process.exit(2);
}

/* ── 归一化比对工具（与 同步内联库.js 同口径） ── */
const norm = l => l.replace(/\s+$/, '').trim();
const rows = src => src.split('\n').map(raw => ({ text: norm(raw), raw }));

function findCopy(hay, needle) {
    const H = hay.filter(r => r.text !== '');
    const N = needle.filter(r => r.text !== '');
    if (!N.length) return null;
    outer:
    for (let i = 0; i + N.length <= H.length; i++) {
        for (let j = 0; j < N.length; j++) {
            if (H[i + j].text !== N[j].text) continue outer;
        }
        return { start: H[i], end: H[i + N.length - 1], count: N.length };
    }
    return null;
}
function firstDiff(hay, needle) {
    const H = hay.filter(r => r.text !== '');
    const N = needle.filter(r => r.text !== '');
    for (let i = 0; i < Math.min(H.length, N.length); i++) {
        if (H[i].text !== N[i].text) return { i, got: H[i].text, want: N[i].text };
    }
    return null;
}

/* ── 读入 ── */
const src = fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
const lines = src.split('\n');
const srcRows = rows(src);
const code = src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');   // 去注释后的代码

const R = { file, lineCount: lines.length, checks: [], problems: [] };
const ok = (name, detail) => R.checks.push({ name, pass: true, detail: detail || '' });
const bad = (name, detail) => { R.checks.push({ name, pass: false, detail: detail || '' }); R.problems.push(name + (detail ? '：' + detail : '')); };

/* ── A. 语法 ──
   用进程内 vm.Script 编译，**不 spawn 子进程**（受限/沙箱环境下 spawn node 会 EBUSY 假失败；
   run-s3-checks.js 的 A 项同样用 vm.Script，两者保持一致）。 */
try {
    new vm.Script(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''), { filename: path.basename(file) });
    ok('A. 语法可解析', 'vm 编译通过');
} catch (e) {
    bad('A. 语法可解析', String(e && e.message ? e.message : e).split('\n')[0]);
}

/* ── B. 两块库逐字保真 ── */
R.libNonEmpty = 0;
for (const b of BANKS) {
    const p = path.join(LIBDIR, b.file);
    const srcText = fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
    const sRows = rows(srcText);
    R.libNonEmpty += sRows.filter(r => r.text !== '').length;
    const hit = findCopy(srcRows, sRows);
    if (hit) {
        ok('B. ' + b.tag + ' 逐字一致', '命中 ' + hit.count + ' 行非空代码');
    } else {
        const d = firstDiff(srcRows, sRows);
        bad('B. ' + b.tag + ' 逐字一致',
            d ? '首处差异在第 ' + (d.i + 1) + ' 行非空行｜产物: ' + String(d.got).slice(0, 60) +
                ' ｜真源: ' + String(d.want).slice(0, 60)
                : '未找到与真源一致的连续段');
    }
}

/* ── C. 副本数量闸门 ── */
for (const b of BANKS) {
    const dups = b.fingerprints.map(fp => ({
        fp, n: src.split(fp).length - 1
    }));
    const badOnes = dups.filter(d => d.n !== 1);
    if (!badOnes.length) ok('C. ' + b.tag + ' 副本唯一', '全文各 1 份');
    else bad('C. ' + b.tag + ' 副本唯一',
        badOnes.map(d => d.fp + ' → ' + d.n + ' 次').join('；'));
}

/* ── D. 骨架完整性 ── */
const skeleton = [
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
];
for (const [name, re] of skeleton) {
    if (re.test(src)) ok('D. ' + name);
    else bad('D. ' + name, '未找到');
}
// 解构语句不得含 recordToAccumulator（用去注释后的 code，避免提示词要求的说明性注释造成误报）
const desc = code.match(/const\s*\{[\s\S]*?\}\s*=\s*LIB\s*;/);
if (desc) {
    if (/recordToAccumulator/.test(desc[0])) bad('D. 解构不含 recordToAccumulator', '解构语句里出现了它');
    else ok('D. 解构不含 recordToAccumulator', '（注释中的说明性提及不计）');
} else {
    bad('D. 解构语句可定位', '未能从去注释代码中提取 `const { … } = LIB;`');
}

/* ── E. 每个 drawFrame_N 末行 finishFrame()（drawBaseScene 不要求，故不计入） ── */
{
    const frames = [];
    lines.forEach((l, i) => {
        const m = l.match(/^\s*function\s+(drawFrame_\d+)\s*\(/);
        if (m) frames.push({ name: m[1], at: i });
    });
    // 用大括号配平定位函数体，避免把「下一个函数之前的一切」误当作函数体
    function funcEnd(startAt) {
        let depth = 0, started = false;
        for (let i = startAt; i < lines.length; i++) {
            const l = lines[i].replace(/\/\/.*$/, '').replace(/\/\*[\s\S]*?\*\//g, '');
            for (const ch of l) {
                if (ch === '{') { depth++; started = true; }
                else if (ch === '}') { depth--; if (started && depth === 0) return i; }
            }
        }
        return -1;
    }

    const missing = [];
    frames.forEach(f => {
        const e = funcEnd(f.at);
        if (e < 0) { missing.push(f.name + '→ 函数体未闭合'); return; }
        const body = lines.slice(f.at + 1, e)
            .map(l => l.trim())
            .filter(t => t && !t.startsWith('//') && !t.startsWith('/*') && !t.startsWith('*'));
        const last = body[body.length - 1] || '';
        if (!/finishFrame\s*\(\s*\)/.test(last)) missing.push(f.name + '→「' + String(last).slice(0, 36) + '」');
    });
    if (!frames.length) bad('E. drawFrame_N 存在', '未找到任何 drawFrame_N');
    else if (missing.length) bad('E. 每帧末行 finishFrame()', '缺 ' + missing.length + ' 处：' + missing.slice(0, 4).join(' ｜ '));
    else ok('E. 每帧末行 finishFrame()', frames.length + ' 个 drawFrame_N 全部合规');
    R.frameCount = frames.length;
}

/* ── F. 违规项 ── */
{
    // 产物区（LIB 之外）的 recordToAccumulator 调用
    // 近似：LIB IIFE 结束后的文本
    const libStart = lines.findIndex(l => /const\s+LIB\s*=\s*\(\s*function\s*\(/.test(l));
    const afterLib = libStart >= 0 ? lines.slice(libStart + 1).join('\n') : src;
    const n = (afterLib.replace(/function\s+recordToAccumulator/g, '').match(/recordToAccumulator\s*\(/g) || []).length;
    if (n === 0) ok('F. 产物区无 recordToAccumulator 调用');
    else bad('F. 产物区无 recordToAccumulator 调用', '命中 ' + n + ' 次');

    // 自写同名绘图基元（重复定义）
    const prims = ['drawLine', 'drawPoint', 'drawMathText', 'clearCanvas', 'replayAccumulator', 'stopAnim', 'finishFrame', 'drawCircle', 'drawArc', 'drawPolygon'];
    const selfDef = [];
    for (const p of prims) {
        const re = new RegExp('function\\s+' + p + '\\s*\\(', 'g');
        const c = (src.match(re) || []).length;
        if (c > 1) selfDef.push(p + '(' + c + ' 次)');
    }
    if (!selfDef.length) ok('F. 无自写重复绘图基元');
    else bad('F. 无自写重复绘图基元', selfDef.join('、'));

    // setTimeout / setInterval 绕过动画引擎
    const timers = (code.match(/\b(setInterval|setTimeout)\s*\(/g) || []).length;
    if (timers === 0) ok('F. 无 setInterval/setTimeout 绕过动画引擎');
    else bad('F. 无 setInterval/setTimeout 绕过动画引擎', '命中 ' + timers + ' 次');
}

/* ── G. CKDrawViolations 早于 CKSummary ── */
{
    const a = src.indexOf('CKDrawViolations()');
    const b = src.lastIndexOf('CKSummary()');
    if (a < 0) bad('G. 调用 CKSummary()', '未找到 CKSummary()');
    else if (b < 0) bad('G. CKDrawViolations 早于 CKSummary', '未找到 CKDrawViolations()');
    else if (a < b) ok('G. CKDrawViolations 早于 CKSummary');
    else bad('G. CKDrawViolations 早于 CKSummary', '顺序反了');
}

/* ── 输出 ── */
if (AS_JSON) {
    console.log(JSON.stringify({
        file: R.file,
        lineCount: R.lineCount,
        libNonEmpty: R.libNonEmpty,
        frameCount: R.frameCount || 0,
        pass: R.problems.length === 0,
        problems: R.problems,
        checks: R.checks
    }, null, 2));
    process.exit(R.problems.length ? 1 : 0);
}

console.log('产物　：' + R.file);
console.log('行数　：' + R.lineCount + '\n');
for (const c of R.checks) {
    console.log((c.pass ? '  ✅ ' : '  ❌ ') + c.name + (c.detail ? '　—— ' + c.detail : ''));
}
console.log('\n' + '═'.repeat(60));
if (R.problems.length) {
    console.log('体检结论：❌ ' + R.problems.length + ' 项未通过');
    process.exit(1);
} else {
    console.log('体检结论：✅ 全部 ' + R.checks.length + ' 项通过');
    process.exit(0);
}
