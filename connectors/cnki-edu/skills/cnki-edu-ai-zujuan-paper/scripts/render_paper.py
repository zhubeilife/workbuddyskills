#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 组卷 · 试卷与解析渲染器（v1.4）

用法：
    python3 render_paper.py <questions.json> -o <out.html> [--part both|paper|analysis]

依据《试卷与解析排版标准 v1.4》渲染：
- `--part both`（默认）：试卷 + 解析合卷（兼容旧行为）
- `--part paper`   ：**仅试卷**（不含解析）—— 对应"第一份：试卷 docx"
- `--part analysis`：**仅解析**（含题头重列 + 考点/分析/解答）—— 对应"第二份：解析 docx"

要点：
- A4；卷名/解析标题 15pt 加粗居中；题型标题 12pt 加粗；正文 10.5pt 行距 1.5
- 题号悬挂缩进 13.65pt；解析标签【】蓝色 0000FF；合卷时试卷与解析之间强制分页
- 选项用**无边框表格 + 列宽反算**，保证**绝不折行**
- 题图引用题库图片域名（见 `IMG` 常量，可用环境变量 `ZJ_IMG_HOST` 覆盖；+ no-referrer + lazy），不落地缓存
- **v1.4 新增**：
  ① `normalize_math()` —— 把题库数学标记（MathJye 分数 <table>、上下标 <span>）线性化为可读文本，
     避免 html-to-docx 把分数表渲染成散乱表格（"吸水水 3 4" 类垃圾）。
  ② 解析「解：」去重 —— 题库 Method 常自带"解："，渲染器不再无条件前置。
  ③ 题图去 `float:right` —— 题库题干图片常带 `float:right`，会与文字错位/压字，统一改为独立居中成段。

输入 JSON 结构见 references/example_questions.json。
"""
import os, sys, json, html, re, argparse

# 题库图片域名。保持常量+环境变量双通道：既不改动现有行为，也便于需要时整体切换/代理。
IMG = os.environ.get("ZJ_IMG_HOST", "https://img.jyeoo.net").rstrip("/")

# ---------------- 选项排版：自适应 1/2/4 行，且绝不折行 ----------------
# 实测：①转换器把选项表总宽固定为 8640 twips = 432pt；②单元格右边距 10pt；
#      ③转换器会在 "A" 与 "．" 间插空格、使实际文本比原串宽约 11pt。
CONTENT_W = 416.0       # 保守排版预算（转换器实际表宽 432pt，再留安全余量）
CELL_PAD = 14.0         # 单元格右边距 10pt + 4pt 余量
EXTRA_SPACE = 11.0      # 转换器插空带来的额外宽度
SAFETY = 1.03           # 文本宽度安全系数


def _is_img(x):
    x = x.strip()
    return x.startswith("http") or x.startswith("/")


def _upgrade_https(src):
    """题图强制走 https，避免混合内容（mixed-content）被浏览器/预览拦截。

    背景：题库部分题图原始为 http://img.jyeoo.net/...，嵌进 https 页面或经转换器抓取时
    会被当成混合内容 block（见 references/edu-api-notes.md:89）。IMG 常量默认已是 https，
    但题干/选项里**绝对路径的 http:// 题图**不会经过 IMG 拼接、需在此显式升级。"""
    if src.startswith("http://"):
        return "https://" + src[len("http://"):]
    return src


def _force_https_imgs(s):
    """对原始 HTML 片段里的 <img src="http://..."> 做 http→https 升级（覆盖绝对路径题图）。"""
    if not s or "http://" not in s:
        return s
    return re.sub(r'src="http://([^"]+)"',
                  lambda m: f'src="https://{m.group(1)}"', s)


def fig(src, w=None):
    """渲染一张题图；src 可为 http(s) URL、/quiz/... 相对路径，或已是 HTML 片段。"""
    if src.strip().startswith("<"):
        return src
    url = _upgrade_https(src if src.startswith("http") else IMG + src)
    dim = f' width="{w}"' if w else ''
    return (f'<img class="fig-img" src="{url}"{dim} '
            f'referrerpolicy="no-referrer" loading="lazy" alt="题图" />')


def _opt_html(o):
    """选项内容：已是 HTML 片段 → 升级其内嵌 http 题图为 https；图片路径 → 转 <img>；否则纯文本。"""
    s = o.strip()
    if s.startswith("<"):
        return _force_https_imgs(o)
    if _is_img(s):
        return fig(s, 64)
    return o


def _disp_w(s):
    """保守估算一段文本在 10.5pt 下的显示宽度(pt)：CJK 1em、ASCII 0.53em，再计插空+安全系数。"""
    s = re.sub(r'<[^>]+>', '', s)
    w = 0.0
    for ch in s:
        w += 10.6 if ord(ch) > 0x2E7F else 5.6
    return w * SAFETY + EXTRA_SPACE


def opts_block(opts):
    """把 ABCD 选项渲染成无边框表格，自动均衡分行且**保证不折行**。
    - 纯文本选项：能一行放下 → 1 行 4 列；否则 2 行各 2 个；再否则 4 行各 1 个。
    - **图片选项**（电路图等）：固定 **2×2 网格**，字母标签与图片**同行**（避免"字母独占一行、
      图片另一行"的错位），图片限宽以便两列并排。
    列宽按各列最长内容反算，剩余空间平摊铺满整表。
    """
    raw = [o.strip() for o in opts]
    is_img_opt = [x.startswith("<img") or _is_img(x) for x in raw]

    if any(is_img_opt):
        # 图片选项：2×2 网格，标签与图片同行，图片缩放到 46% 宽以便并排
        CELL = ('border:none;padding:3pt 8pt 3pt 0;vertical-align:middle;'
                'white-space:nowrap;width:50%;font-size:10.5pt;')
        cells = []
        for i, o in enumerate(raw):
            letter = chr(65 + i)
            if is_img_opt[i]:
                img = _force_https_imgs(o) if o.startswith("<img") else fig(o, 180)
                content = f'{letter}．{img}'
            else:
                content = f'{letter}．{_opt_html(o)}'
            cells.append(f'<td style="{CELL}">{content}</td>')
        trs = []
        for r in range(0, len(cells), 2):
            pair = cells[r:r + 2]
            if len(pair) == 1:
                pair.append(f'<td style="{CELL}"></td>')
            trs.append('<tr>' + ''.join(pair) + '</tr>')
        return ('<table class="opt-tbl" style="border-collapse:collapse;width:100%;'
                'table-layout:fixed;border:none;margin:4pt 0 8pt;">' + "".join(trs) + '</table>')

    labels = [f'{chr(65 + i)}．{_opt_html(o)}' for i, o in enumerate(raw)]
    ws = [_disp_w(x) for x in labels]

    n = len(labels)

    # 候选列数：从多到少（列多→行少→更紧凑）。第 c 列 = 索引 {c, c+per, …}，
    # 与下方「按行填充」渲染顺序一致；支持任意选项数（2/3/4/…），不再硬编码 4 选项。
    def _cols_for(per):
        nrows = (n + per - 1) // per
        return [[r * per + c for r in range(nrows) if r * per + c < n] for c in range(per)]

    best = None
    for per in range(min(n, 4), 0, -1):
        cols = _cols_for(per)
        if len(cols) != per or not all(cols):
            continue
        req = [max(ws[i] for i in c) + CELL_PAD for c in cols]
        if sum(req) <= CONTENT_W:
            best = (per, req)
            break
    if best is None:
        per = 1
        best = (1, [max(ws) + CELL_PAD])
    per, req = best

    leftover = CONTENT_W - sum(req)
    add = leftover / len(req) if req else 0.0
    widths = [(r + add) / CONTENT_W * 100.0 for r in req]
    rows = (n + per - 1) // per

    trs = []
    for r in range(rows):
        tds = []
        for c in range(per):
            k = r * per + c
            if k < len(labels):
                tds.append(
                    f'<td style="border:none;padding:2pt 10pt 2pt 0;vertical-align:top;'
                    f'white-space:nowrap;width:{widths[c]:.2f}%;">{labels[k]}</td>')
        trs.append('<tr>' + ''.join(tds) + '</tr>')
    return ('<table class="opt-tbl" style="border-collapse:collapse;width:100%;'
            'table-layout:fixed;border:none;margin:4pt 0 8pt;">' + "".join(trs) + '</table>')


BLANK = '<u>　　　　</u>'   # 安全的填空线：html-to-docx 下会生成真实下划线


def fix_blanks(s):
    """把 3 个及以上连续下划线（____）替换为 <u>全角空格</u>。
    背景：html-to-docx 会把 "文字________" 误判为「表单域」，并**丢弃该空之后整段文字**；
    改用 <u>　　　　</u> 可保留原义、生成真实下划线，且不触发误判。
    同时把题库的填空占位标记（quizPutTag 空 div）一并转为下划线。"""
    if not s:
        return s
    s = re.sub(r'<!--BA--><div class="quizPutTag"[^>]*>\s*(?:&nbsp;)?\s*</div><!--EA-->', BLANK, s)
    s = re.sub(r'<!--BA--><div class="quizPutTag"[^>]*>(.*?)</div><!--EA-->', r'\1', s, flags=re.S)
    return re.sub(r'_{3,}', BLANK, s)


# ---------------- 题库数学标记 → 线性文本 ----------------
# 题库用 <span class="MathJye"> 包裹公式：分数用嵌套 <table>（上行分子 / 下行分母），
# 上下标用 <span style="vertical-align:sub|super"> 或 <div mathtag="msubsup_sub|_sup"> 表达。
# html-to-docx 会把嵌套<table>当成真表格渲染 → 分数被打散成散乱的行/格（如"吸水水""3""4"各占一行）。
# 对策：在进入 HTML 前把公式"线性化"为纯文本（分数写成 (分子)/(分母)），彻底消除表格。
# ⚠️ MathJye span 高度嵌套（r3 内层共 58 个 <span>），正则 `.*?</span>` 会停在第一个内层闭合，
#    故必须用「标签深度计数」匹配到对应的外层闭合标签。

_RE_FRAC_TABLE = re.compile(
    r'<table\b[^>]*>\s*<tr>\s*<td\b[^>]*>(.*?)</td>\s*</tr>\s*'
    r'<tr>\s*<td\b[^>]*>(.*?)</td>\s*</tr>\s*</table>', re.S)
_RE_TAG = re.compile(r'<[^>]+>')


def _strip_tags(s):
    return _RE_TAG.sub('', s)


def _extract_math_spans(s):
    """找出所有 class="MathJye" 的 <span>，按标签深度返回 (内容, start, end)。
    返回三元组列表，内容为**不含最外层 span 标签**的内部 HTML。"""
    out = []
    for m in re.finditer(r'<span\b[^>]*class="MathJye"[^>]*>', s):
        start = m.end()
        depth = 1
        i = start
        while i < len(s) and depth > 0:
            nxt = s.find('<span', i)
            cls = s.find('</span>', i)
            if cls == -1:
                break
            if nxt != -1 and nxt < cls:
                depth += 1
                i = nxt + 5
            else:
                depth -= 1
                i = cls + 7
        if depth == 0:
            out.append((s[start:i - 7], m.start(), i))
    return out


def _linearize_fraction(s):
    """把 MathJye 里的分数表转成 (分子)/(分母)，递归处理内部嵌套表。"""
    def rep(m):
        num = _strip_tags(m.group(1)).strip()
        den = _strip_tags(m.group(2)).strip()
        return f'({num})/({den})'
    prev = None
    while prev != s:
        prev = s
        s = _RE_FRAC_TABLE.sub(rep, s)
    return s


def _math_to_linear(inner):
    """把一段 MathJye 内部内容转成线性文本。
    顺序：① sub/sup 的内联 span 与 div 形式 → <sub>/<sup>（先固定上下标语义，再线性化分数）；
          ② 分数表 → (a)/(b)；③ 剥掉残留的 span/div 壳与 mathtag 噪声。"""
    # 内联上下标 span：内容可能仍含嵌套 → 用非贪婪够用（此处内容一般无深嵌套）
    inner = re.sub(
        r'<span\b[^>]*style="[^"]*vertical-align:\s*sub[^"]*"[^>]*>(.*?)</span>',
        lambda m: f'<sub>{_strip_tags(m.group(1))}</sub>', inner, flags=re.S)
    inner = re.sub(
        r'<span\b[^>]*style="[^"]*vertical-align:\s*super[^"]*"[^>]*>(.*?)</span>',
        lambda m: f'<sup>{_strip_tags(m.group(1))}</sup>', inner, flags=re.S)
    # div 形式上下标（mathtag="msubsup_sub|_sup"）
    inner = re.sub(
        r'<div\b[^>]*mathtag="msubsup_sub"[^>]*>(.*?)</div>',
        lambda m: f'<sub>{_strip_tags(m.group(1))}</sub>', inner, flags=re.S)
    inner = re.sub(
        r'<div\b[^>]*mathtag="msubsup_sup"[^>]*>(.*?)</div>',
        lambda m: f'<sup>{_strip_tags(m.group(1))}</sup>', inner, flags=re.S)
    # 分数表 → 线性
    inner = _linearize_fraction(inner)
    # 剥掉剩余的结构标签，仅保留文本与已生成的 <sub>/<sup>/<br>
    inner = re.sub(r'<(?!sub\b|sup\b|/sub|/sup|br\b)[^>]+>', '', inner)
    return inner


def _sweep_leftover_fractions(s):
    """兜底清扫：有些分数表跨越了 MathJye span 边界（分式表落在 span 之外）。
    这类表都带特征 `border-bottom:1px solid black`（分子下划线），据此精确识别并线性化，
    绝不误伤真正的数据表（数据表用 class="edittable" / 普通边框，不含此特征）。"""
    if "border-bottom:1px solid black" not in s:
        return s
    # 只线性化"分数形态"的表：<table …><tr><td …border-bottom:1px solid black…>A</td></tr><tr><td…>B</td></tr></table>
    prev = None
    while prev != s:
        prev = s
        s = re.sub(
            r'<table\b[^>]*>\s*<tr>\s*<td\b[^>]*border-bottom:1px solid black[^>]*>(.*?)</td>\s*</tr>'
            r'\s*<tr>\s*<td\b[^>]*>(.*?)</td>\s*</tr>\s*</table>',
            lambda m: f'({_strip_tags(m.group(1)).strip()})/({_strip_tags(m.group(2)).strip()})',
            s, flags=re.S)
    # 清掉残留的孤立 </span>（MathJye 边界清洗不彻底时可能出现）
    s = re.sub(r'</span>(?=\s|$|<br|[，。；、）])', '', s)
    return s


def normalize_math(s):
    """对外主入口：把整段 HTML 里的 MathJye 公式线性化（从后往前替换，避免位移），
    再做一次兜底分数清扫。真正的数据表（class="edittable" 等）原样保留。"""
    if not s:
        return s
    if "MathJye" in s:
        spans = _extract_math_spans(s)
        for inner, a, b in reversed(spans):
            s = s[:a] + _math_to_linear(inner) + s[b:]
    return _sweep_leftover_fractions(s)


def strip_float_img(s):
    """题干里题库常把图片写成 float:right，会与正文错位/压字。
    此处仅去掉浮动样式（图片位置由渲染器统一放到独立行居中）。"""
    if not s:
        return s
    return re.sub(r'(<img\b[^>]*?)style="[^"]*float\s*:\s*right[^"]*"',
                  r'\1style="vertical-align:middle;"', s, flags=re.I)


SUBQ_CUT = "。；！？：）"      # 允许出现在小问标号之前的句末/引出标点（含收尾括号）


# 解答题内嵌图片的重排 -------------------------------------------------
# 题库把题图直接塞在题干 HTML 里，且位置不定：有的在**最前面**（如 Q21，带 float:right），
# 有的在**最后面**（如 Q22）。解答题的理想版式是「题干叙述 → 图 → 小问（1）（2）…」，
# 故需把题干里的 <img> 抽出来、改放到叙述与小问之间。

def extract_stem_figs(s):
    """从题干 HTML 中抽出所有 <img> 标签，返回 (去掉图片的文本, [图片HTML片段...])。

    抽出图片后常残留「连续的两个 `<br />`」（原为「文字<br/>图<br/>文字」），
    此处折叠为一处，避免产物里出现空行。"""
    if not s:
        return s, []
    figs = re.findall(r'<img\b[^>]*>', s)
    text = re.sub(r'<img\b[^>]*>', '', s)
    text = re.sub(r'(?:\s*<br\s*/?>\s*){2,}', '<br />', text)
    return text, figs


def split_at_first_subq(s):
    """把题干文本按**第一个小问标号**切成 (叙述, 小问段)。

    判定"第一个小问标号"与 split_subq 完全一致（段首 / 紧邻 `<br />` / 前字为句末标点或 `>`），
    以免把"五（2）班"这类校园称谓误当成小问。若不存在小问边界，则全部算作叙述。
    """
    if not s:
        return s, ""
    t = re.sub(r'(?:\s*<br\s*/?>\s*)+(?=（[1-9]）)', '\x00', s)
    for i in range(len(t)):
        if t[i] == '\x00':
            # 哨兵处即"叙述"与"（N）"的交界（哨兵本身代表被吞掉的换行，交界处丢弃即可）
            return t[:i], t[i + 1:]
        m = re.match(r'（([1-9])）', t[i:])
        prev = t[i - 1] if i > 0 else ''
        if m and (prev == '' or prev in SUBQ_CUT or prev == '>'):
            return t[:i], t[i:]
    return t, ""


def split_subq(text):
    """把解答题/计算题里的每个小问（1）（2）… 拆到单独一行。

    ⚠️ 不能无脑替换 `（N）`：题干正文里存在"阳光小学五（2）班""（1）班"这类
    校园称谓，误判会把它拆成新行。故只在**确定是小问边界**时换行，判据：
      1) 该标号位于段首；或
      2) **其前面紧邻 `<br />` 换行标签**（题库原作者已显式换行 → 最可靠的信号）；或
      3) 前一字符是句末/引出标点（。；！？：））——含"（均填"a"或"b"）（2）"这种
         前一问以括号收尾、紧接下一问的情形；或
      4) 前一字符是 HTML 标签结束符 `>`（如 `</sub>（1）` 紧跟在标签后）。

    反例保护：`五（2）班`（前一字符是 CJK"五"）不会被拆。
    注意：题库里同一行可能用 `<br />` 分隔小问，也可能用标点直接相接；两种都要覆盖。
    """
    if not text:
        return text
    # 记录"哪些位置原本就有 <br /> 紧跟（N）"——这些是显式小问边界。
    # 策略：把「<br />（N）」统一改写成哨兵，随后按边界规则换行，最后还原。
    t = re.sub(r'(?:\s*<br\s*/?>\s*)+(?=（[1-9]）)', '\x00', text)

    out, prev, i, n = [], '', 0, len(t)
    while i < n:
        if t[i] == '\x00':                 # 显式 <br/>（N）信号：恢复为换行
            out.append('<br />')
            prev, i = '\x00', i + 1
            continue
        m = re.match(r'（([1-9])）', t[i:])
        if m and (prev == '' or prev == '\x00' or prev in SUBQ_CUT or prev == '>'):
            out.append('<br />' + m.group(0))
            prev, i = '）', i + m.end()
            continue
        out.append(t[i])
        prev, i = t[i], i + 1
    s = ''.join(out)
    # 清理：段首多余的换行、以及连续两个换行
    s = re.sub(r'^(?:\s*<br\s*/?>\s*)+', '', s)
    s = re.sub(r'(?:<br\s*/?>\s*){2,}', '<br />', s)
    return s


def strip_substruct(s):
    """题库的 `<bdo class="substruct-mark red">` 是无内容的记分占位符，纯噪声，去掉。"""
    if not s:
        return s
    return re.sub(r'<bdo\b[^>]*class="substruct-mark[^"]*"[^>]*>\s*</bdo>', '', s)


def tidy_punct(s):
    """清洗多余标点：`。。` / `；。` / `，。` 等重复句末标点归一为单个 `。`。"""
    if not s:
        return s
    s = re.sub(r'([。；，、]){2,}', '。', s)
    s = re.sub(r'[；，、]。', '。', s)
    return s


def norm_mathjye(s):
    """题库语文标记归一。转换器对题库 `mathjye-*` 类的下划线识别不稳定
    （同款 mathjye-underpoint 有时落 w:u、有时不落），故划线族 bdo 直接转原生 `<u>` 标签
    （实测转换器对 <u> 下划线支持最稳）；对齐族（aligncenter/alignright）保留 bdo+CSS
    （text-align 已验证可用）。"""
    if not s:
        return s
    for cls in ('mathjye-underpoint2', 'mathjye-underpoint', 'mathjye-underline', 'mathjye-underwave'):
        s = re.sub(r'<bdo class="' + cls + r'"[^>]*>(.*?)</bdo>', r'<u>\1</u>', s, flags=re.S)
    return s


MAT_SEP = "\x01"   # 阅读材料段分隔哨兵（渲染期内部使用，不会落进产物）


def norm_mat(s):
    """阅读材料行的缩进归一：把「<br/> 后跟 6 个 &nbsp;」的行首缩进替换为哨兵 MAT_SEP。

    历史组卷稿/题库稿常用 6 个 &nbsp;（≈3 汉字）做材料行缩进，叠加段落左缩进 13.65pt 后
    实际约 4.3 汉字，明显过深。改为哨兵后由 _render_q_body 拆成独立 .mat 段落，
    由 CSS 统一给 **2 汉字**（21pt）缩进。
    """
    if not s:
        return s
    return re.sub(r'(?:\s*<br\s*/?>\s*)*(?:&nbsp;){6}', MAT_SEP, s)


def _split_mat(stem):
    """按 MAT_SEP 把题干切成 (首行, [材料段…])，并清掉各段首尾多余换行。"""
    parts = stem.split(MAT_SEP)
    lead = re.sub(r'(?:\s*<br\s*/?>\s*)+$', '', parts[0]).strip()
    mats = [re.sub(r'^(?:\s*<br\s*/?>\s*)+|(?:\s*<br\s*/?>\s*)+$', '', p).strip()
            for p in parts[1:]]
    return lead, [m for m in mats if m]


def clean_body(s):
    """正文/解析通用清洗：去关键词高亮 → 题库记分占位 → 数学线性化 → 去浮动图 → 填空线 → 标点整理。"""
    if not s:
        return s
    s = _force_https_imgs(s)              # 题干/解析内嵌题图若带 http://，先升级为 https 防混合内容拦截
    s = re.sub(r'</?del\b[^>]*>', '', s)   # 搜题接口的关键词高亮 <del>：只去标签、保留文字
    s = strip_substruct(s)
    s = normalize_math(s)
    s = strip_float_img(s)
    s = fix_blanks(s)
    s = norm_mathjye(s)
    return tidy_punct(s)


CSS = """
@page { size: A4; margin: 2.5cm 2.0cm; }
* { box-sizing: border-box; }
/* ⚠️ 行距必须"钉"在元素上：转换器对 body 级 line-height 会做 ×0.85 补偿，
   只有元素级 line-height:1.5 才会落成 Word 的真正 1.5 倍（w:line=360）。 */
body { font-family: "宋体", SimSun, "Times New Roman", serif; font-size: 10.5pt;
       line-height: 1.5; color: #000000; margin: 0; background: #fff; }
.wrap { max-width: 900px; margin: 0 auto; padding: 24px 28px; }
.title { font-size: 15pt; font-weight: bold; text-align: center; margin: 0 0 4pt; line-height: 1.5; }
.meta { text-align: center; font-size: 10.5pt; margin: 0 0 10pt; line-height: 1.5; }
.exam-info { text-align: center; font-size: 10.5pt; margin: 0 0 14pt; line-height: 1.5;
             border-bottom: 1px dashed #999; padding-bottom: 8pt; }
.exam-info span { margin: 0 10pt; }
.sec-title { font-size: 12pt; font-weight: bold; margin: 16pt 0 8pt; line-height: 1.5; }
/* 题号悬挂缩进：margin-left 必须**单独声明**（转换器不解析 margin 简写），
   可落成 w:ind w:left=273；负 text-indent 会被忽略 → 悬挂由 fix_hanging_indent.py 后处理补 w:hanging。 */
.q { font-size: 10.5pt; margin-top: 10pt; margin-bottom: 4pt; margin-left: 13.65pt; text-indent: -13.65pt; text-align: justify; line-height: 1.5; }
/* 解答题小问块：紧跟在题干图之后，不参与题号悬挂缩进，左边与正文对齐。 */
.qsub { margin-top: 4pt; margin-bottom: 4pt; margin-left: 0; text-indent: 0; }
/* 阅读材料段（材料一／问一／答…）：独立成段，统一 **首行缩进 2 汉字**（text-indent:21pt），
   续行回到左边界（margin-left:0），符合中文"每段开头空两格"的排版习惯。
   背景：旧稿用行首 6 个 &nbsp;（≈3 汉字）做材料缩进，叠加段落左缩进 13.65pt 后
   实际≈4.3 汉字，明显过深；现改为独立 .mat 段 + 首行缩进 2 汉字
   （text-indent:21pt → 转换器落 w:firstLine=420）。注意：html-to-docx 转换器按 CSS 出现
   顺序后者覆盖前者，且对连字符类名处理异常，故此处用内联 style 钉死，不再依赖类选择器。 */
.q.mat, .ana-q.mat { margin-top: 0; margin-bottom: 0; text-indent: 21pt; margin-left: 0; }
.opt-tbl { font-size: 10.5pt; border-collapse: collapse; width: 100%; table-layout: fixed; border: none; margin: 4pt 0 8pt; }
.opt-tbl td { font-size: 10.5pt; border: none; padding: 2pt 10pt 2pt 0; vertical-align: top; text-align: left; white-space: nowrap; line-height: 1.5; }
.opt-tbl img { vertical-align: middle; }
.fig { text-align: center; margin: 6pt 0; }
.fig img { max-width: 90%; }
.tbl { border-collapse: collapse; margin: 6pt auto; font-size: 10.5pt; }
.tbl td, .tbl th { border: 1px solid #333; padding: 2pt 8pt; text-align: center; line-height: 1.5; }
/* 题库原生数据表（如化学计量的质量对照表）：class="edittable"，需给框线，否则渲染成无框表。 */
.edittable { border-collapse: collapse; margin: 6pt auto; font-size: 10.5pt; }
.edittable td, .edittable th { border: 1px solid #333; padding: 2pt 8pt; text-align: center; vertical-align: middle; line-height: 1.5; }
.edittable .quizPutTag, .edittable u { white-space: nowrap; }
.ana-sec { page-break-before: always; }
.ana-title { font-size: 15pt; font-weight: bold; text-align: center; margin: 6pt 0 12pt; line-height: 1.5; }
.lab { color: #0000FF; }
.ana-q { font-size: 10.5pt; margin-top: 10pt; margin-bottom: 4pt; margin-left: 13.65pt; text-indent: -13.65pt; text-align: justify; line-height: 1.5; }
.ana-q.qsub { margin-top: 4pt; margin-bottom: 4pt; margin-left: 0; text-indent: 0; }
.ana-p { font-size: 10.5pt; margin: 4pt 0; text-align: justify; line-height: 1.5; }
.ansline { font-size: 10.5pt; margin: 4pt 0; line-height: 1.5; }
/* 题库语文标记兜底（v1.6 新增）：转换器按 <style> 类渲染，缺规则则丢失版式。
   aligncenter/alignright 作块级居中/右对齐；划线 solid、加点 dotted、波浪线 wavy。 */
.mathjye-aligncenter { display: block; text-align: center; font-weight: bold; margin: 4pt 0; line-height: 1.5; }
.mathjye-alignright  { display: block; text-align: right; margin: 4pt 0; line-height: 1.5; }
/* 转换器仅识别裸 text-decoration:underline（dotted/wavy 会被忽略）；加点/划线/波浪线统一落 solid 下划线。 */
.mathjye-underline   { text-decoration: underline; }
.mathjye-underpoint  { text-decoration: underline; }
.mathjye-underpoint2 { text-decoration: underline; }
.mathjye-underwave   { text-decoration: underline; }
"""


def _norm_kind(kind):
    """把题型名归一到「核心词」，容忍简/繁写法（选择⇄选择题、解答⇄计算题）。
    返回 选择/填空/作图/实验/计算/判断/多选/其他。"""
    k = (kind or "").strip()
    if "选择" in k:
        return "多选" if "多" in k else "选择"
    if "填空" in k:
        return "填空"
    if "作图" in k:
        return "作图"
    if "实验" in k or "探究" in k:
        return "实验"
    if "计算" in k or "解答" in k or "证明" in k or "综合" in k:
        return "计算"
    if "判断" in k:
        return "判断"
    return k or "其他"


def _is_subq_kind(kind):
    """判断该题型是否需要把小问（1）（2）拆到独立行：解答 / 计算类。"""
    return _norm_kind(kind) == "计算"


def _render_q_body(q, cls, no_prefix):
    """渲染一道题的题干 + 图 + 选项（返回 HTML 行列表）。

    **解答/计算题**：题库把图直接内嵌在题干 HTML 里、位置随机（或在最前、或在最后）。
    按要求统一重排为「题干叙述 → 图（居中）→ 小问（1）（2）…」：
      - 先抽出题干里的 `<img>`（连同 `figs` 字段里的图）；
      - 把无图叙述与小问段在小问标号处切开；
      - 依次输出 叙述段 / 图 / 小问段。
    **其余题型**：保持原顺序（题干原样 → 图 → 选项），不改动习惯版式。

    no_prefix 为题干前缀（试卷用 `21．（8分）`；解析用 `<b>21．（8分）</b>`）。
    """
    stem = norm_mat(clean_body(q["stem"]))
    lead, mats = _split_mat(stem)
    if not _is_subq_kind(q["kind"]):
        # 题图统一移到题干正文**下方、独立成行**：先抽出题干中内联的 <img>（不再内联在题干、不再顶在题首同行），
        # 再连同 figs 字段里的图，作为独立居中段排在正文之后、选项之前。
        text, inline_figs = extract_stem_figs(lead)
        figs = inline_figs + [fig(f) for f in (q.get("figs") or [])]
        out = [f'<div class="{cls}">{no_prefix}{text}</div>']
        for mt in mats:
            out.append(f'<div class="{cls} mat" style="text-indent:21pt;margin-left:0;margin-top:0;margin-bottom:0;">{mt}</div>')
        for f in figs:
            out.append(f'<div class="fig">{f}</div>')
        if q.get("opts"):
            out.append(opts_block(q["opts"]))
        return out

    # —— 解答/计算题：图移到「叙述」与「小问」之间 ——
    text, inline_figs = extract_stem_figs(lead)
    figs = inline_figs + [fig(f) for f in (q.get("figs") or [])]
    narr, subq = split_at_first_subq(text)
    out = []
    if subq:
        # 叙述段（可能为空则省略，避免出现"只有题号"的空段）
        if narr.strip():
            out.append(f'<div class="{cls}">{no_prefix}{narr}</div>')
        else:
            out.append(f'<div class="{cls}">{no_prefix}</div>')
        for mt in mats:
            out.append(f'<div class="{cls} mat" style="text-indent:21pt;margin-left:0;margin-top:0;margin-bottom:0;">{mt}</div>')
        for f in figs:
            out.append(f'<div class="fig">{f}</div>')
        out.append(f'<div class="{cls} qsub">{split_subq(subq)}</div>')
    else:
        out.append(f'<div class="{cls}">{no_prefix}{text}</div>')
        for mt in mats:
            out.append(f'<div class="{cls} mat" style="text-indent:21pt;margin-left:0;margin-top:0;margin-bottom:0;">{mt}</div>')
        for f in figs:
            out.append(f'<div class="fig">{f}</div>')
    if q.get("opts"):
        out.append(opts_block(q["opts"]))
    return out


def _render_questions(cfg, cls):
    """把题目按题型分节渲染。cls 为题干 div 的 class（试卷 .q / 解析 .ana-q）。
    题型匹配用 _norm_kind 归一，避免「选择」与「选择题」这类简/繁写法导致整卷丢失。"""
    sec_title = {s["kind"]: s["title"] for s in cfg["sections"]}
    order = [s["kind"] for s in cfg["sections"]]
    out = []
    for kind in order:
        nk = _norm_kind(kind)
        qs = [q for q in cfg["questions"] if _norm_kind(q["kind"]) == nk]
        if not qs:
            continue
        # 空标题 → 只渲染题目、不打印分节标题（分块缝合时避免标题重复，见 build_questions --split-blocks）
        if sec_title.get(kind):
            out.append(f'<div class="sec-title">{sec_title[kind]}</div>')
        for q in qs:
            out += _render_q_body(q, cls, f'{q["no"]}．（{q["score"]}分）')
    return out


def render_paper(cfg):
    out = ['<div class="wrap">']
    # omit_header：分块渲染时只在首块输出标题/卷头，避免缝合后重复（见 merge_docx/Render_blocks）
    if not cfg.get("omit_header"):
        out.append(f'<div class="title">{html.escape(cfg["title"])}</div>')
        # 卷头信息（考试时间·满分 + 学校/班级/姓名/学号填写栏）默认不输出：自动生成的练习/考试卷保持干净版式。
        # 如需保留，在 spec 中显式设置 "show_paper_header": true 即可恢复 meta 与考生填写栏。
        if cfg.get("show_paper_header"):
            if cfg.get("meta"):
                out.append(f'<div class="meta">{html.escape(cfg["meta"])}</div>')
            if cfg.get("exam_info", True):
                out.append('<div class="exam-info"><span>学校：____________</span>'
                           '<span>班级：__________</span><span>姓名：__________</span>'
                           '<span>学号：__________</span></div>')
    out += _render_questions(cfg, "q")
    out.append('</div>')
    return "\n".join(out)


def _ordered_questions(cfg):
    """按「题型分节顺序」返回题目列表——保证试卷与解析**题号顺序一致**。
    修复：解析曾按 JSON 里的原始行序遍历，导致与试卷题号错位（1,8,21,2…）。"""
    order = [_norm_kind(s["kind"]) for s in cfg["sections"]]
    def key(q):
        nk = _norm_kind(q["kind"])
        return (order.index(nk) if nk in order else 99, q["no"])
    return sorted(cfg["questions"], key=key)


def render_analysis(cfg):
    out = ['<div class="wrap ana-sec">']
    # omit_header：分块解析只在首块输出「参考答案与试题解析」标题
    if not cfg.get("omit_header"):
        out.append(f'<div class="ana-title">{html.escape(cfg["title"])}<br />参考答案与试题解析</div>')
    for q in _ordered_questions(cfg):
        out += _render_q_body(q, "ana-q", f'<b>{q["no"]}．（{q["score"]}分）</b>')
        if q.get("points"):
            out.append(f'<div class="ana-p"><span class="lab">【考点】</span>{q["points"]}</div>')
        if q.get("analyse"):
            out.append(f'<div class="ana-p"><span class="lab">【分析】</span>{clean_body(q["analyse"])}</div>')
        if q.get("method"):
            meth = clean_body(q["method"])
            meth = split_subq(meth) if _is_subq_kind(q["kind"]) else meth
            # 「解：」去重：题库 Method 常自带"解："，避免出现"解：解："
            m = re.match(r'^\s*解\s*[:：]\s*', meth)
            if m:
                meth = meth[m.end():]
            out.append(f'<div class="ana-p"><span class="lab">【解答】</span>解：{meth}</div>')
        for f in q.get("afigs") or []:
            out.append(f'<div class="fig">{fig(f)}</div>')
        if q.get("answer"):
            out.append(f'<div class="ana-p ansline">{clean_body(q["answer"])}</div>')
    out.append('</div>')
    return "\n".join(out)


def build(cfg, part="both"):
    if part == "paper":
        body = render_paper(cfg)
    elif part == "analysis":
        body = render_analysis(cfg)
    else:
        body = render_paper(cfg) + "\n" + render_analysis(cfg)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>{html.escape(cfg["title"])}</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="AI 组卷 · 试卷/解析/合卷渲染器")
    ap.add_argument("input", help="题目 JSON 文件路径")
    ap.add_argument("-o", "--output", help="输出 HTML 路径（默认与输入同目录同名 .html）")
    ap.add_argument("--part", choices=["both", "paper", "analysis"], default="both",
                    help="渲染哪一部分：both=合卷（默认）｜paper=仅试卷｜analysis=仅解析")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        cfg = json.load(f)

    out_path = args.output or os.path.splitext(os.path.abspath(args.input))[0] + ".html"
    doc = build(cfg, args.part)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"[render_paper] 已生成({args.part}): {out_path}  ({len(doc)} chars, {len(cfg['questions'])} 题)")


if __name__ == "__main__":
    main()
