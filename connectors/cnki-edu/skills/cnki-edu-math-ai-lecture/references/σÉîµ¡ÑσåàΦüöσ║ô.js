#!/usr/bin/env node
/**
 * ══════════════════════════════════════════════════════════════════
 *  内联库同步 —— 几何内核 v2.2 + 绘图层 v1.1
 * ══════════════════════════════════════════════════════════════════
 *
 *  解决的问题：
 *    第三步提示词里有两个「内联槽位」（BEGIN/END 标记区），模型要从槽位里
 *    **整段粘贴**两块库进产物代码。但真源是本目录的 几何内核.js / 绘图层.js，
 *    手工把 1200 行粘进提示词必然漂移（历史上就漏掉过 7 个校验函数）。
 *    本脚本把「同步」变成一条命令，并在同步前后核对内容。
 *
 *  用法（在本目录下执行）：
 *    node 同步内联库.js --check       只比对，不改文件（默认）。一致→退出码 0，不一致→1
 *    node 同步内联库.js --dry         显示将要发生的变化，不写
 *    node 同步内联库.js --write       执行写入（要求目标里已有 BEGIN/END 标记）
 *
 *    可选：--target <提示词路径>       指定目标提示词（默认 ../第3步.txt）
 *          WB_PROMPT3=<路径>          同上，环境变量方式
 *
 *  判据：
 *    ★ 正判据是「逐行逐字比对」（忽略行首缩进与行尾空白）——在标记区里能
 *      找到与真源完全一致的连续段 = 真源与副本一致。
 *    ★ 声明清单差异只作**人类可读提示**，不作判据。且只比对**顶层声明**
 *      （按最小缩进档认定），否则函数内局部量会把列表撑爆成假报警。
 *    ★ 另有一道「副本数量闸门」：同一份库在全文里只允许出现一次，防止
 *      「输出格式示例区里还内联着第二份旧库」——那才是模型真正会照抄的东西。
 *
 *  写入护栏：无 BEGIN/END 标记时**拒绝写入**（库块外面通常套着
 *    `const LIB = (function(){…})()` 包装，整块替换会连包装一起删掉）。
 *    写入前自动备份原件。
 * ══════════════════════════════════════════════════════════════════
 */
'use strict';
const fs = require('fs');
const path = require('path');

const DIR = __dirname;

/* ── 两块库的定义（顺序 = 产物里的粘贴顺序：内核在前，绘图层在后） ── */
const BLOCKS = [
    {
        name: '几何内核',
        file: '几何内核.js',
        begin: '// ==== 几何内核 BEGIN（由 注入内核.js 生成，勿手改）====',
        end: '// ==== 几何内核 END ====',
        fingerprints: ['const DEG = Math.PI / 180;', 'function CKBounds(']
    },
    {
        name: '绘图层',
        file: '绘图层.js',
        begin: '// ==== 绘图层 BEGIN（由 注入内核.js 生成，勿手改）====',
        end: '// ==== 绘图层 END ====',
        fingerprints: ['const _DEG = Math.PI / 180;', 'function drawMathText(']
    }
];

const MODE = process.argv.includes('--write') ? 'write'
    : process.argv.includes('--dry') ? 'dry' : 'check';

/* ─────────── 目标提示词 ─────────── */
let target = process.env.WB_PROMPT3 || '';
const ti = process.argv.indexOf('--target');
if (ti >= 0 && process.argv[ti + 1]) target = process.argv[ti + 1];
if (!target) target = path.join(DIR, '..', '第3步.txt');

/* ─────────── 工具 ─────────── */

/** 归一化一行：去行尾空白 + 去行首缩进。用于「忽略缩进」的逐字比对。 */
const norm = l => l.replace(/\s+$/, '').trim();

/** 拆成 { text, raw, no }，保留原始行号 */
const rows = src => src.split('\n').map((raw, i) => ({ text: norm(raw), raw, no: i }));

/** 在 hay 中寻找与 needle 逐行一致（忽略缩进与空行）的连续段 */
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

/** 全部声明名（缩进无关）——只用于显示"含局部量共 N 个" */
function decls(src) {
    const re = /^[ \t]*(?:const|let|function)\s+([A-Za-z_$][\w$]*)/gm;
    const out = new Set();
    let m;
    while ((m = re.exec(src))) out.add(m[1]);
    return out;
}

/** 顶层声明清单：以声明行的最小缩进档为基准（真源无包装，此法成立） */
function topDecls(src) {
    const re = /^([ \t]*)(?:const|let|function)\s+([A-Za-z_$][\w$]*)/gm;
    const all = [];
    let m;
    while ((m = re.exec(src))) all.push({ indent: m[1].length, name: m[2] });
    if (!all.length) return new Set();
    const base = Math.min(...all.map(d => d.indent));
    return new Set(all.filter(d => d.indent === base).map(d => d.name));
}

/* ─────────── 读入 ─────────── */
if (!fs.existsSync(target)) {
    console.error('❌ 找不到目标提示词：' + target);
    console.error('   用 --target <路径> 或 WB_PROMPT3=<路径> 指定。');
    process.exit(2);
}

const lines = fs.readFileSync(target, 'utf8').split('\n');
const srcCache = new Map();
for (const b of BLOCKS) {
    const p = path.join(DIR, b.file);
    if (!fs.existsSync(p)) {
        console.error('❌ 缺少真源文件：' + p);
        process.exit(2);
    }
    srcCache.set(b.name, fs.readFileSync(p, 'utf8'));
}

console.log('目标提示词：' + target);
console.log('真源目录　：' + DIR);
console.log('模式　　　：' + MODE);

/* ─────────── 逐块检查 ─────────── */
const plans = [];   // { b, beginIdx, endIdx, base, newBlock, ok, curLen, srcLen }
let allOk = true;

for (const b of BLOCKS) {
    const src = srcCache.get(b.name);
    const sRows = rows(src);
    const sDecl = decls(src);
    const sTop = topDecls(src);
    const ver = (src.match(/(?:几何内核|绘图层)\s*v[\d.]+/) || ['(无版本注释)'])[0];

    console.log('\n' + '═'.repeat(66));
    console.log('【' + b.name + '】' + ver + '　顶层声明 ' + sTop.size +
        ' 个（含函数内局部量共 ' + sDecl.size + ' 个）');

    let bi = -1, ei = -1;
    lines.forEach((l, i) => {
        if (l.trim() === b.begin) bi = i;
        if (l.trim() === b.end) ei = i;
    });

    if (bi < 0 || ei < 0 || ei <= bi) {
        console.log('  ❌ 未找到 BEGIN/END 标记 —— 无法定位内联槽位');
        console.log('     BEGIN 行应为：' + b.begin);
        console.log('     END   行应为：' + b.end);
        allOk = false;
        plans.push({ b, beginIdx: -1, endIdx: -1, ok: false });
        continue;
    }

    const regionRaw = lines.slice(bi + 1, ei);
    const curInline = regionRaw.join('\n');

    /* 正判据：逐字比对 */
    const hit = findCopy(rows(curInline), sRows);
    const iDecl = decls(curInline);
    const missing = [...sTop].filter(d => !iDecl.has(d));
    const inVer = (curInline.match(/(?:几何内核|绘图层)\s*v[\d.]+/) || ['(无版本注释)'])[0];

    console.log('  内联槽位：第 ' + (bi + 1) + ' ~ ' + (ei + 1) + ' 行，现内容版本 ' + inVer);
    if (hit) {
        console.log('  ✅ 槽位内存在与真源逐字一致的段落（' + hit.count + ' 行非空代码）');
    } else {
        console.log('  ❌ 槽位内**找不到**与真源逐字一致的段落 —— 是旧版、占位、或被改动过');
        const H = rows(curInline).filter(r => r.text !== '');
        const N = sRows.filter(r => r.text !== '');
        let fd = -1;
        for (let i = 0; i < Math.min(H.length, N.length); i++) {
            if (H[i].text !== N[i].text) { fd = i; break; }
        }
        if (fd >= 0) {
            console.log('     第一处差异（按非空行序号对齐，仅供参考）：');
            console.log('       槽位：' + (H[fd] ? H[fd].text.slice(0, 88) : '(槽位更短)'));
            console.log('       真源：' + (N[fd] ? N[fd].text.slice(0, 88) : '(真源更短)'));
        } else if (H.length !== N.length) {
            console.log('     前 ' + Math.min(H.length, N.length) + ' 行相同，仅行数不同（槽位 ' +
                H.length + ' 行 / 真源 ' + N.length + ' 行）');
        }
    }

    const mShow = missing.slice(0, 12).join(', ') +
        (missing.length > 12 ? ', …（共 ' + missing.length + ' 个）' : '');
    console.log('  缺失顶层声明：' +
        (missing.length ? '❌ ' + missing.length + ' 个 → ' + mShow : '✅ 无'));

    /* 副本数量闸门：全文只允许一份 */
    const dupBad = b.fingerprints.map(fp => ({
        fp,
        hits: lines.map((_, i) => i)
            .filter(i => lines[i].indexOf('>') !== 0 && lines[i].indexOf(fp) >= 0)
    })).filter(d => d.hits.length > 1);
    console.log('  副本数量闸门：' + (dupBad.length ? '❌ 标记区外还有副本' : '✅ 全文仅 1 份'));
    if (dupBad.length) {
        dupBad.forEach(d => console.log('     ' + d.fp + ' → 第 ' +
            d.hits.map(i => i + 1).join('、') + ' 行'));
        console.log('     ⚠️ 标记区之外的副本才是模型真正会照抄的东西，请删除，只留槽位一份。');
    }

    const ok = !!hit && missing.length === 0 && dupBad.length === 0;
    if (!ok) allOk = false;

    /* 生成新块（缩进对齐 BEGIN 行） */
    const base = (lines[bi].match(/^[ \t]*/) || [''])[0];
    const newBlock = [
        base + b.begin,
        ...src.split('\n').map(l => (l.trim() === '' ? '' : base + l)),
        base + b.end
    ];
    plans.push({
        b, beginIdx: bi, endIdx: ei, base, newBlock, ok,
        curLen: regionRaw.length, srcLen: src.split('\n').length
    });
}

console.log('\n' + '═'.repeat(66));
console.log('一致性总判：' + (allOk ? '✅ 两块都已与真源一致' : '⚠️ 存在不一致，需要同步'));

if (MODE === 'check') {
    process.exit(allOk ? 0 : 1);
}

/* ─────────── 写入护栏 ─────────── */
const bad = plans.filter(p => p.beginIdx < 0);
if (bad.length) {
    console.log('\n' + '─'.repeat(66));
    console.log('⛔ 块「' + bad.map(p => p.b.name).join('、') + '」缺少 BEGIN/END 标记，拒绝写入。');
    console.log('   原因：库块外面通常套着 `const LIB = (function(){…})()` 包装，');
    console.log('         整块替换会连包装一起删掉，属于破坏性操作。');
    console.log('   请先在该提示词里补上标记行，再跑 --dry / --write。');
    console.log('─'.repeat(66));
    process.exit(2);
}

/* ─────────── 预览 / 写入 ─────────── */
console.log('\n【将要发生的变化】');
for (const p of plans) {
    const delta = p.newBlock.length - (p.endIdx - p.beginIdx + 1);
    console.log('  · ' + p.b.name + '：第 ' + (p.beginIdx + 1) + ' ~ ' + (p.endIdx + 1) +
        ' 行被替换　槽位 ' + p.curLen + ' 行 → 真源 ' + p.srcLen + ' 行　（' +
        (delta >= 0 ? '+' : '') + delta + ' 行）　缩进基准 ' + p.base.length + ' 空格');
}

if (MODE === 'dry') {
    console.log('\n（--dry 模式，未写入文件）');
    process.exit(0);
}

/* 写入前自动备份（用户要求：改原件必须先备份并告知路径） */
const d = new Date();
const p2 = n => String(n).padStart(2, '0');
const stamp = '' + d.getFullYear() + p2(d.getMonth() + 1) + p2(d.getDate()) +
    '_' + p2(d.getHours()) + p2(d.getMinutes()) + p2(d.getSeconds());
const backup = target + '.bak_' + stamp;
try {
    fs.copyFileSync(target, backup);
    console.log('\n🗂  原件已备份：' + backup);
} catch (e) {
    console.error('\n❌ 备份失败，已中止写入：' + e.message);
    process.exit(3);
}

/* 从后往前替换，避免行号漂移 */
let out = lines.slice();
for (const p of plans.sort((a, b) => b.beginIdx - a.beginIdx)) {
    out = [...out.slice(0, p.beginIdx), ...p.newBlock, ...out.slice(p.endIdx + 1)];
}
fs.writeFileSync(target, out.join('\n'), 'utf8');

console.log('✅ 已写入：' + target);
console.log('   行数：' + lines.length + ' → ' + out.length);
console.log('   请再跑一次 --check 复核；并核对第 3.5 步提示词里对两块库函数的描述是否仍准确。');
