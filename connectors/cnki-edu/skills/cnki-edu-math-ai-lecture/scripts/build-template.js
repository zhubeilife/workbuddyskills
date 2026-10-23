#!/usr/bin/env node
'use strict';

/**
 * ══════════════════════════════════════════════════════════════════
 *  build-template.js —— 从 step4-assemble-html.md 抽取 HTML 模板，
 *                       在 6 个可变槽位注入标记，产出 references/html-template.html
 * ══════════════════════════════════════════════════════════════════
 *
 *  归属：cnki-edu-math-ai-lecture（P0-B · S4 脚本化）
 *  来源：与 配套快速版 同名脚本同一设计，**代码落在本 skill**。
 *
 *  用法：  node scripts/build-template.js
 *  产出：  references/html-template.html   （固定骨架 + 6 槽位标记）
 *
 *  单一真源原则：模板始终从 step4 抽取。若 step4 升级，重跑本脚本即可。
 *
 *  6 个槽位标记（注入后由 assemble-html.js 替换）：
 *    @@PAGE_TITLE@@          <title>
 *    @@S1_SENTENCES@@        const sentences
 *    @@S1_TRANSLATIONS@@     const translations
 *    @@S2_QUESTIONDATA@@     const questionData
 *    @@S3_DRAWING@@          数据区3（档位声明→抄写自检日志）
 *    @@QUESTION_TITLE_JSON@@ const QUESTION_TITLE
 * ══════════════════════════════════════════════════════════════════
 */

const fs = require('fs');
const path = require('path');

const SKILL = path.join(__dirname, '..');
const STEP4 = path.join(SKILL, 'references', 'step4-assemble-html.md');
const OUT = path.join(SKILL, 'references', 'html-template.html');

const MARKERS = [
    '@@PAGE_TITLE@@',
    '@@S1_SENTENCES@@',
    '@@S1_TRANSLATIONS@@',
    '@@S2_QUESTIONDATA@@',
    '@@S3_DRAWING@@',
    '@@QUESTION_TITLE_JSON@@'
];

let md = fs.readFileSync(STEP4, 'utf8').replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');

/* ── 1) 抽取 ```html … ``` 模板块 ── */
const m = md.match(/```html\n([\s\S]*?)\n```/);
if (!m) { console.error('❌ 未在 step4 中找到 ```html 模板块'); process.exit(1); }
let tpl = m[1];
const srcBytes = Buffer.byteLength(tpl, 'utf8');

/* ── 2) <title> ── */
const t0 = tpl;
tpl = tpl.replace('<title>【替换为题型名称】</title>', '<title>@@PAGE_TITLE@@</title>');
if (tpl === t0) { console.error('❌ 未匹配 <title> 槽位'); process.exit(1); }

/* ── 3) S1：sentences / translations ── */
const t1 = tpl;
tpl = tpl.replace(/const sentences = \[[\s\S]*?\];/, '/* @@S1_SENTENCES@@ */');
if (tpl === t1) { console.error('❌ 未匹配 sentences 槽位'); process.exit(1); }
const t2 = tpl;
tpl = tpl.replace(/const translations = \[[\s\S]*?\];/, '/* @@S1_TRANSLATIONS@@ */');
if (tpl === t2) { console.error('❌ 未匹配 translations 槽位'); process.exit(1); }

/* ── 4) S2：questionData ── */
const t3 = tpl;
tpl = tpl.replace(/const questionData = \{[\s\S]*?\n        \};/, '/* @@S2_QUESTIONDATA@@ */');
if (tpl === t3) { console.error('❌ 未匹配 questionData 槽位'); process.exit(1); }

/* ── 5) 数据区 3：绘图代码（档位声明 → 抄写自检日志块结束） ── */
const START_ANCHOR = "window.__DRAW_TIER__ = 'A';";
const END_ANCHOR = '         * ═══════════════════════════ */';
const s = tpl.indexOf(START_ANCHOR);
const e = tpl.indexOf(END_ANCHOR);
if (s < 0 || e < 0) { console.error('❌ 未匹配绘图代码区锚点', { s, e }); process.exit(1); }
tpl = tpl.slice(0, s) + '/* @@S3_DRAWING@@ */' + tpl.slice(e + END_ANCHOR.length);

/* ── 6) QUESTION_TITLE ── */
const t4 = tpl;
tpl = tpl.replace('const QUESTION_TITLE = "题型 · 四环讲题";', 'const QUESTION_TITLE = @@QUESTION_TITLE_JSON@@;');
if (tpl === t4) { console.error('❌ 未匹配 QUESTION_TITLE 槽位'); process.exit(1); }

/* ── 校验：6 个标记全部存在 ── */
const missing = MARKERS.filter(k => !tpl.includes(k));
if (missing.length) { console.error('❌ 槽位标记缺失：', missing.join(', ')); process.exit(1); }

fs.writeFileSync(OUT, tpl, 'utf8');

console.log('✅ 模板已生成：' + OUT);
console.log('   行数：' + tpl.split('\n').length + '　字节：' + Buffer.byteLength(tpl, 'utf8') + '（step4 模板块原 ' + srcBytes + ' 字节）');
console.log('   槽位：' + MARKERS.join('  '));
