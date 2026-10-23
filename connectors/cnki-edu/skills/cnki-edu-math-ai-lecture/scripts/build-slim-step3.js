#!/usr/bin/env node
'use strict';

/**
 * ══════════════════════════════════════════════════════════════════
 *  build-slim-step3.js
 *  生成「脚本注入模式」版第三步提示词（step3-drawing-code.slim.md）
 * ══════════════════════════════════════════════════════════════════
 *
 *  背景：full 版（2301 行）里内联着两块库正文共 1215 行，要求模型
 *       「整段粘贴、一字不改」。这带来一整类抄写失真风险（历史上踩过
 *       _textViolation 正则括号丢失、漏粘绘图层等坑）。
 *
 *  本脚本把 full 版变成 slim 版，**只变一个变量**：
 *      两块库正文 → 两行注入标记（@@INJECT:GEOM_KERNEL@@ / @@INJECT:DRAW_LAYER@@）
 *      其余规则（构造区 / 校验区 / CK 硬门槛 / 持久临时分层 / 输出格式）一字不改。
 *
 *  用法：
 *      node build-slim-step3.js            # 生成 slim 版
 *      node build-slim-step3.js --check    # 只校验 full 版槽位与真源一致，不写文件
 *
 *  退出码：0 成功 / 1 有 patch 未命中（需修表） / 2 槽位或真源缺失
 * ══════════════════════════════════════════════════════════════════
 */

const fs = require('fs');
const path = require('path');

const SKILL = path.join(__dirname, '..');
const FULL = path.join(SKILL, 'references', 'step3-drawing-code.full.md');
const SLIM = path.join(SKILL, 'references', 'step3-drawing-code.slim.md');
const LIBDIR = path.join(SKILL, 'references');

const CHECK_ONLY = process.argv.includes('--check');

/* ── 两块库的定义（顺序 = 注入顺序） ── */
const BANKS = [
    {
        tag: '几何内核',
        file: '几何内核.js',
        ver: 'v2.2',
        begin: '// ==== 几何内核 BEGIN（由 注入内核.js 生成，勿手改）====',
        end: '// ==== 几何内核 END ====',
        mark: '@@INJECT:GEOM_KERNEL@@',
        fingerprints: ['const DEG = Math.PI / 180;', 'function CKBounds(']
    },
    {
        tag: '绘图层',
        file: '绘图层.js',
        ver: 'v1.1',
        begin: '// ==== 绘图层 BEGIN（由 注入内核.js 生成，勿手改）====',
        end: '// ==== 绘图层 END ====',
        mark: '@@INJECT:DRAW_LAYER@@',
        fingerprints: ['const _DEG = Math.PI / 180;', 'function drawMathText(']
    }
];

/* ── 需要改写的原文 → 新文（每条必须恰好命中 1 次，否则报错退出） ── */
const PATCHES = [
    {
        desc: '卷首「当前版本要点」第 1 条',
        find: '> 1. 坐标**只能由几何构造算出**，禁止手写数字。两块内联库整段粘贴、一字不改、顺序不调。',
        repl: '> 1. 坐标**只能由几何构造算出**，禁止手写数字。两块内联库由装配脚本注入，产物里**只写两行注入标记**（见卷首「本版模式声明」）。'
    },
    {
        desc: '内联库小节标题',
        find: '## 内联库：几何内核 + 绘图层\n\n> ⚠️ 两块里的函数名',
        repl: '## 内联库：几何内核 + 绘图层（本版：脚本注入模式）\n\n> ⚠️ 两块里的函数名'
    },
    {
        desc: '「两块都必须原样复制」提示',
        find: '> ★ 两块都必须原样复制，禁止自己另写同名函数。',
        repl: '> ★ 两块都由装配脚本按注入标记写入，**禁止自己另写同名函数、禁止手写任何库代码正文**。'
    },
    {
        desc: 'C 档对照表「两块内联库照粘」',
        find: '两块内联库照粘；',
        repl: '两块注入标记照写；'
    },
    {
        desc: 'C 档第 4 条',
        find: '4. **C 档也要粘两块内联库**：',
        repl: '4. **C 档也要写两块注入标记**：'
    },
    {
        desc: '抄写自检清单「两块 BEGIN/END 标记本身」',
        find: '- [ ] 两块 BEGIN/END 标记本身',
        repl: '- [ ] 两块注入标记本身（`@@INJECT:GEOM_KERNEL@@` / `@@INJECT:DRAW_LAYER@@`）'
    },
    {
        desc: '抄写自检日志模板「两块标记区」',
        find: ' *  两块标记区        ✅ BEGIN/END 各一对，顺序未调',
        repl: ' *  两块注入标记      ✅ 各一行，顺序未调',
        all: true
    },
    {
        desc: '档位替换表 A 档',
        find: '两块全粘；构造链；',
        repl: '两块注入标记；构造链；'
    },
    {
        desc: '档位替换表 B 档',
        find: '两块全粘；构造区改为',
        repl: '两块注入标记；构造区改为'
    },
    {
        desc: '档位替换表 C 档',
        find: '两块仍全粘；',
        repl: '两块注入标记照写；'
    },
    {
        desc: '检查清单「绘图层与角标」第 1 条',
        find: '- [ ] ★ **两块内联库是否都是从本文件上方「## 内联库：几何内核 + 绘图层」一节的标记区整段复制**？（几何内核 `BEGIN → END`、再绘图层 `BEGIN → END`，素材只有那一份，**不得凭记忆重写、不得精简、不得重排缩进**）',
        repl: '- [ ] ★ **`LIB` 内是否只写了 `/* @@INJECT:GEOM_KERNEL@@ */` 然后 `/* @@INJECT:DRAW_LAYER@@ */` 两行注入标记**？（先内核、后绘图层；**不得凭记忆重写、不得手写任何库代码**——真源由装配脚本按标记注入）'
    },
    {
        desc: '【用户输入】区硬性约束第 3 条',
        find: '3. ★ **先把两块内联库整段粘进 `LIB`**：**素材就在本文件上方「## 内联库：几何内核 + 绘图层」一节里**——从该节的「几何内核 BEGIN → END」、再「绘图层 BEGIN → END」标记区**整段复制**（先内核、后绘图层），**一字不改、顺序不调**；**禁止凭记忆重写、禁止精简、禁止重排缩进**',
        repl: '3. ★ **先在 `LIB` 内写下两行注入标记**：第一行 `/* @@INJECT:GEOM_KERNEL@@ */`、第二行 `/* @@INJECT:DRAW_LAYER@@ */`（先内核、后绘图层，顺序不调）；**不要写任何库代码正文**——装配脚本会按标记注入真源。**禁止凭记忆重写、禁止手写库代码**'
    }
];

/* ── 卷首模式声明（插入到第一个 `---` 之后） ── */
const BANNER = [
    '---',
    '',
    '## ⚠️ 本版模式声明（脚本注入模式 / slim）—— 优先于下文一切「粘贴」措辞',
    '',
    '本文件**不含**两块内联库正文（几何内核 v2.2 + 绘图层 v1.1，约 1215 行）。',
    '库正文在 `references/` 下，由 `scripts/assemble-artifact.js` **按标记注入**你的产物代码。',
    '',
    '**因此：下文凡出现「从『## 内联库』一节整段粘贴 / 整段复制 / 一字不改」的要求，一律替换为以下动作：**',
    '',
    '> 在产物 `LIB` 内（`const LIB = (function () {` 之后的**第一、二行**）**只写两行注入标记**，不写任何库代码：',
    '> ```javascript',
    '>   /* @@INJECT:GEOM_KERNEL@@ */',
    '>   /* @@INJECT:DRAW_LAYER@@ */',
    '> ```',
    '> 先内核、后绘图层，顺序不变；标记独占一行，缩进与 `LIB` 内其他代码一致（本流水线为 2 空格）。',
    '',
    '**除「库从哪来」这一点外，全部规则一字未改** —— 构造区、校验区、`CK()` 硬门槛、',
    '持久/临时分层、六层结构、输出格式、抄写自检日志，全部照旧执行。',
    '',
    '---',
    ''
];

/* ── 输出格式骨架替换区的新内容 ── */
const SKELETON = [
    '// ★★★ pts 必须由"几何内核构造"产出 ★★★',
    '// ⚠️ 【内联库来源 · 本版为脚本注入模式】',
    '//    本文件不含两块库正文。在你的产物里，LIB 内的第一、二行**只写两行注入标记**：',
    '//      /* @@INJECT:GEOM_KERNEL@@ */',
    '//      /* @@INJECT:DRAW_LAYER@@ */',
    '//    （先内核、后绘图层，顺序不要调）。装配脚本 assemble-artifact.js 会按标记注入真源全文。',
    '//  ★ 禁止在标记处手写任何库代码正文；★ 禁止在此处另行定义任何与两块同名的函数。',
    '// ══════════════════════════════════════════════════════════════'
];

function die(msg, code) {
    console.error('❌ ' + msg);
    process.exit(code || 1);
}

/* ══════════ 1. 读入并定位槽位 ══════════ */
if (!fs.existsSync(FULL)) die('找不到 full 版提示词：' + FULL, 2);
const lines = fs.readFileSync(FULL, 'utf8').split('\n');

for (const b of BANKS) {
    const p = path.join(LIBDIR, b.file);
    if (!fs.existsSync(p)) die('缺少真源文件：' + p, 2);
    b.src = fs.readFileSync(p, 'utf8');
    b.srcLines = b.src.split('\n').filter(l => l.trim() !== '').length;
    b.bi = lines.findIndex(l => l.trim() === b.begin);
    b.ei = lines.findIndex(l => l.trim() === b.end);
    if (b.bi < 0 || b.ei < 0 || b.ei <= b.bi) {
        die('未找到 ' + b.tag + ' 的 BEGIN/END 标记 —— 无法定位槽位', 2);
    }
    console.log('【' + b.tag + '】槽位第 ' + (b.bi + 1) + ' ~ ' + (b.ei + 1) + ' 行　真源 ' + b.srcLines + ' 行非空代码');
}

/* ══════════ 2. 槽位正文 → 注入标记占位 ══════════ */
let out = lines.slice();
for (const b of [...BANKS].sort((a, c) => c.bi - a.bi)) {
    const placeholder = [
        '  // 【装配脚本注入位 · ' + b.tag + '】本版不含库正文。',
        '  // 产物代码里在此位置只写一行： /* ' + b.mark + ' */',
        '  // 由 scripts/assemble-artifact.js 从 references/' + b.file +
        '（' + b.ver + '，' + b.srcLines + ' 行非空代码）注入。'
    ];
    out.splice(b.bi + 1, b.ei - b.bi - 1, ...placeholder);
}

/* ══════════ 3. 输出格式骨架替换（按行定位，避开引号差异） ══════════ */
{
    const iStart = out.findIndex(l => l.includes('pts 必须由'));
    const iEndMark = out.findIndex(l => l.includes('禁止在此处另行定义'));
    if (iStart < 0 || iEndMark < 0 || iEndMark <= iStart) {
        die('未找到输出格式骨架区（定位串：pts 必须由 / 禁止在此处另行定义）');
    }
    out.splice(iStart, iEndMark - iStart + 1, ...SKELETON);
    console.log('骨架区替换：第 ' + (iStart + 1) + ' ~ ' + (iEndMark + 1) + ' 行 → ' + SKELETON.length + ' 行');
}

/* ══════════ 4. 文本 patch ══════════ */
let text = out.join('\n');
let failed = 0;
const report = [];
for (const p of PATCHES) {
    const n = text.split(p.find).length - 1;
    if (n === 0) {
        console.error('❌ patch 未命中：' + p.desc);
        console.error('   查找串：' + p.find.slice(0, 90) + (p.find.length > 90 ? ' …' : ''));
        failed++;
        continue;
    }
    if (n > 1 && !p.all) {
        console.error('❌ patch 命中 ' + n + ' 次（应为 1）：' + p.desc);
        failed++;
        continue;
    }
    text = p.all ? text.split(p.find).join(p.repl) : text.replace(p.find, p.repl);
    report.push('  ✅ ' + p.desc + (p.all ? '（' + n + ' 处）' : ''));
}
console.log('\n【文本改写】');
report.forEach(r => console.log(r));
if (failed) die('有 ' + failed + ' 条 patch 未命中 —— 请修正 PATCHES 表后重跑');

/* ══════════ 5. 插入卷首模式声明 ══════════ */
{
    const arr = text.split('\n');
    const dash = arr.findIndex(l => l.trim() === '---');
    if (dash < 0) die('未找到卷首 `---` 分隔线，无法插入模式声明');
    arr.splice(dash + 1, 0, ...BANNER);
    text = arr.join('\n');
    console.log('卷首模式声明已插入（第 ' + (dash + 2) + ' 行起，' + BANNER.length + ' 行）');
}

/* ══════════ 6. 自检 ══════════ */
const problems = [];
for (const b of BANKS) {
    for (const fp of b.fingerprints) {
        if (text.includes(fp)) problems.push('slim 版仍残留 ' + b.tag + ' 代码指纹：' + fp);
    }
    const cnt = text.split(b.mark).length - 1;
    if (cnt < 1) problems.push('slim 版缺少注入标记 ' + b.mark);
    else console.log('注入标记 ' + b.mark + ' 出现 ' + cnt + ' 次');
    // 槽位占位说明必须存在
    if (!text.includes('【装配脚本注入位 · ' + b.tag + '】'))
        problems.push('slim 版缺少 ' + b.tag + ' 的槽位占位说明');
    // BEGIN / END 标记有意保留（让 slim 与 full 结构最接近），但必须仍成对
    if (!text.includes(b.begin) || !text.includes(b.end))
        problems.push(b.tag + ' 的 BEGIN/END 标记被破坏（应成对保留）');
}

if (problems.length) {
    problems.forEach(p => console.error('❌ ' + p));
    die('自检未通过');
}
console.log('自检：✅ 两块库正文已完全移除，注入标记齐备');

/* ══════════ 7. 写出 ══════════ */
const slimLines = text.split('\n');
if (CHECK_ONLY) {
    console.log('\n（--check 模式，未写入文件）');
    process.exit(0);
}
fs.writeFileSync(SLIM, text, 'utf8');
console.log('\n✅ 已生成：' + SLIM);
console.log('   行数：' + lines.length + ' → ' + slimLines.length +
    '（-' + (lines.length - slimLines.length) + ' 行）');
