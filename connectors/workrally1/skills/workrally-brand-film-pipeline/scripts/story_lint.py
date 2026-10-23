#!/usr/bin/env python3
"""
剧情保真与视频提示词机检（workrally-brand-film-pipeline §3b，规则版本 2026.09.29.5）

只用 Python 标准库，不联网、不调用外部命令，只读输入文件。

用法:
    python3 story_lint.py ledger <剧情台账.json>
    python3 story_lint.py prompt <视频提示词.md> --ledger <剧情台账.json> [--max-prompt-words N]

两个子命令都通过才可以提交视频生成；任何 FAIL 退出码为 1。

剧情台账（JSON，字段说明见 SKILL.md §3b）:
{
  "rule_version": "2026.09.29.5",
  "audio_policy": "native_sfx_verbatim_dialogue_no_music",
  "source_events": [{"event_id": "EV001", "scene": "场1", "text": "林晚推门进屋", "origin": "script"}],
  "source_lines":  [{"src": "D001", "speaker": "林晚", "text": "门没锁。", "origin": "script"}],
  "units": [{
    "unit_id": "U01", "duration": 12, "blocking": true,
    "shots": [{
      "shot_id": "SH01", "t": [0, 5], "event_refs": ["EV001"],
      "camera": {"pos": [4.5, 1.6], "facing": 180, "fov": 47},
      "subjects": {"林晚": {"pos": [0.1, 2.0], "frame": "center"}},
      "dialogue": [{"src": "D001", "part": "", "text": "门没锁。", "window": [2.6, 3.4]}]
    }]
  }]
}

坐标：x 向东、y 向北（或 x 沿主视轴、y 在其左侧），单位一致即可；facing 为摄影机朝向，
从 +x 逆时针量的角度（东 0、北 90、西 180、南 270）。

视频提示词文件（Markdown，结构见 §4a）: 每个生成单元一个 `## <unit_id> · …` 标题，
下面第一个 ```text 代码块是提示词正文。【时间轴镜头】里镜头行写 `[起–止秒] 镜头N：…`，
镜内分拍写 `[起–止秒] …`，两者都是单元内的半开区间。
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

CURRENT_RULE_VERSION = '2026.09.29.5'
LEGACY_BEFORE = (2026, 9, 29, 4)

TOLERANCE_S = 0.05
NEGATION_MAX_PER_UNIT = 5
RATE_MIN, RATE_MAX = 3.5, 4.2
FG_EXTRA_DEG = 10
LENGTH_WARN_RATIO = 0.9

CONTEXT_REFS = [
    '上一镜头', '上一个镜头', '上个镜头', '上一镜', '上一段', '上一条', '上一单元', '上一组',
    '前一镜', '前一段', '刚才', '刚刚', '继续', '接着', '同上', '照旧', '依旧', '仍然',
    '保持原样', '和之前一样', '与之前相同', '延续前面', '如前所述', '紧接上', '前情提要', '又一次',
]

SCENE_NUMBER_PATTERNS = [
    r'第\s*\d+\s*集', r'第\s*\d+\s*场', r'EP-?\d+', r'SCENE-?\d+',
    r'(?<![\d.])\d+-\d+\s*[日夜晨昏]',
]

NEGATION_MARKERS = [
    '严禁', '禁止', '不得', '不要', '避免', '杜绝', '不加', '不出现', '不允许', '绝不', '没有',
]
NEGATION_EXEMPT = ['没有任何文字']

SECTIONS = ['总控', '参考绑定', '人物', '空间', '光线与色彩', '时间轴镜头', '声音方案', '一致性与限制', '默认摄影']
REQUIRED_SECTIONS = ['总控', '参考绑定', '空间', '光线与色彩', '时间轴镜头', '声音方案', '一致性与限制', '默认摄影']
RETIRED_SECTIONS = ['生成单元', '整体叙事', '对白原文', '空间连续性']
LIGHT_FIELDS = ['主光源', '方向', '摄影机', '色板']

FOV_TABLE = {107: '广角直线', 84: '经典广角', 63: '标准偏广', 47: '标准', 29: '短中焦人像', 18: '经典长焦', 8: '超长焦观察'}
TRANSITIONS = ['硬切', '叠化', '匹配剪辑']
FRAMES = {'left': '画面左侧', 'center': '画面中间', 'right': '画面右侧', 'fg': '前景', 'off': '画外'}

AUDIO_POLICIES = ('native_sfx_verbatim_dialogue_no_music', 'all_post_production')
SOUND_PLANS = {
    ('native_sfx_verbatim_dialogue_no_music', True):
        '同期生成对白、画面内可见声源的环境声与动作音效，全片无配乐、无歌声。'
        '台词用剧本原语言，按时间轴逐字说完，每句一次；括号里的说明和镜头标签只用于表演，不念出来。',
    ('native_sfx_verbatim_dialogue_no_music', False):
        '同期生成画面内可见声源的环境声与动作音效，全片无配乐、无歌声；本段没有台词。'
        '括号里的说明和镜头标签只用于表演，不念出来。',
    ('all_post_production', True): '视频静音。台词只作表演与口型参考，不发出声音。',
    ('all_post_production', False): '视频静音。',
}
BINDING_ONCE = '构图和运镜以本提示词为准'

SECTION_RE = re.compile(r'【(' + '|'.join(SECTIONS + RETIRED_SECTIONS) + r')】')
SPAN = r'\[\s*(\d+(?:\.\d+)?)\s*秒?\s*[–—\-~至]\s*(\d+(?:\.\d+)?)\s*秒?\s*\]'
SPAN_RE = re.compile(SPAN)
SHOT_LINE_RE = re.compile(r'^[ \t]*' + SPAN + r'\s*镜头\s*(\d+)', re.M)
BEAT_LINE_RE = re.compile(r'^[ \t]*' + SPAN, re.M)
QUOTE_RE = re.compile(r'[“"「『]([^”"」』]*)[”"」』]')
WINDOW_AFTER_QUOTE = r'\s*（\s*(\d+(?:\.\d+)?)\s*至\s*(\d+(?:\.\d+)?)\s*秒说完'
FACING_RE = re.compile(r'朝[东南西北]{1,2}|拍向|面向')
FOV_RE = re.compile(r'（\s*(\d+)\s*°\s*视场\s*）')
SCREEN_SIDE_RE = re.compile(r'画面[左右]|画[左右]侧')
SIDE_PHRASE_RE = re.compile(r'画面(左|右|中)|不入画|画外')
CJK_RE = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)*|\d")


class Report:
    def __init__(self):
        self.items = []

    def fail(self, code, msg):
        self.items.append(('FAIL', code, msg))

    def warn(self, code, msg):
        self.items.append(('WARN', code, msg))

    @property
    def failed(self):
        return any(level == 'FAIL' for level, _, _ in self.items)

    def print(self, title):
        print(f'== {title} ==')
        for level, code, msg in self.items:
            print(f'[{level}] {code} {msg}')
        n_fail = sum(1 for i in self.items if i[0] == 'FAIL')
        n_warn = sum(1 for i in self.items if i[0] == 'WARN')
        print(f'结果：FAIL {n_fail} / WARN {n_warn}' + ('  ✅ 通过' if not n_fail else '  ❌ 不通过'))


def load_ledger(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def squash(text):
    return re.sub(r'\s+', '', text or '')


def parse_version(value):
    try:
        return tuple(int(x) for x in str(value).split('.'))
    except ValueError:
        return None


def rule_profile(ledger, rep):
    """早于 2026.09.29.4 的项目按旧提示词结构检查（legacy），其余按当前结构（current）。"""
    value = ledger.get('rule_version')
    if value is None:
        rep.warn('V00', f'台账没有 rule_version，按当前规则 {CURRENT_RULE_VERSION} 检查')
        return 'current'
    parsed = parse_version(value)
    if not parsed:
        rep.fail('V00', f'rule_version 写成「{value}」，格式应为 YYYY.MM.DD.N')
        return 'current'
    return 'legacy' if parsed < LEGACY_BEFORE else 'current'


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def is_point(p):
    return isinstance(p, list) and len(p) == 2 and all(is_num(x) for x in p)


def part_label(d):
    return f'{d.get("src")}-{d["part"]}' if d.get('part') else str(d.get('src'))


# ---------------- 台词语速 ----------------

def english_syllables(word):
    lower = word.lower()
    w = lower.replace("'", '')
    if len(w) <= 3:
        return 1
    n = len(re.findall(r'[aeiouy]+', w))
    if lower.endswith("n't") and w[-3] not in 'aeiouy':
        n += 1
    elif w.endswith('e') and not w.endswith(('le', 'ee', 'ye')):
        n -= 1
    elif w.endswith('ed') and w[-3] not in 'td':
        n -= 1
    elif w.endswith('es') and not w.endswith(('ses', 'xes', 'zes', 'ches', 'shes', 'ges', 'ces')):
        n -= 1
    return max(1, n)


def spoken_units(text):
    """中文按字计，英文按音节估算，数字每位算一个；标点与省略号不计。"""
    n = len(CJK_RE.findall(text or ''))
    for tok in WORD_RE.findall(text or ''):
        n += 1 if tok.isdigit() else english_syllables(tok)
    return n


def check_rate(label, text, a, b, rep):
    n = spoken_units(text)
    if n == 0:
        rep.warn('D05', f'{label} 没有可读的字，未检查语速：{text}')
        return
    dur = b - a
    slowest = n / (dur + 2 * TOLERANCE_S)
    fastest = n / max(dur - 2 * TOLERANCE_S, 1e-6)
    if fastest >= RATE_MIN and slowest <= RATE_MAX:
        return
    rate = n / dur
    kind = '太慢' if rate < RATE_MIN else '太快'
    unit = '字（英文按音节估算）' if re.search(r'[A-Za-z]', text or '') else '字'
    rep.fail('D05', f'{label} {n} {unit}说 {dur:g} 秒 = {rate:.1f} 字/秒，{kind}；'
                    f'要求 {RATE_MIN}–{RATE_MAX} 字/秒，时窗应为 {n / RATE_MAX:.2f}–{n / RATE_MIN:.2f} 秒'
                    + ('（把时窗缩短；句中有明显停顿的，拆成两段各写时窗）' if kind == '太慢'
                       else '（不删词：先延长镜头，再拆单元，最后跨镜拆句，见 §4c-0 ③）'))


# ---------------- 视锥 ----------------

def bearing(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))


def rel_angle(cam, facing, q):
    """相对摄影机朝向的角度，逆时针为正；正值在画面左边。"""
    return (bearing(cam, q) - facing + 180) % 360 - 180


def frame_side(rel, fov):
    x = math.tan(math.radians(rel)) / math.tan(math.radians(fov / 2))
    return 'left' if x > 1 / 3 else 'right' if x < -1 / 3 else 'center'


def lint_geometry(label, shot, rep):
    """返回 False 表示本镜没有机位数据。"""
    cam, subjects = shot.get('camera'), shot.get('subjects')
    if not cam and not subjects:
        return False
    if not isinstance(cam, dict) or not is_point(cam.get('pos')) or not is_num(cam.get('facing')) or not is_num(cam.get('fov')):
        rep.fail('G00', f'{label} camera 要写 pos=[x, y]、facing（度）和 fov（度）：{cam}')
        return True
    if int(cam['fov']) not in FOV_TABLE or cam['fov'] != int(cam['fov']):
        rep.fail('G00', f'{label} camera.fov={cam["fov"]}° 不在 §4a 视场角换算表里（{"/".join(map(str, FOV_TABLE))}）')
        return True
    if not isinstance(subjects, dict) or not subjects:
        rep.fail('G00', f'{label} 缺 subjects：写出本镜画面里要出现（或明确不入画）的人物与地标')
        return True

    fov, facing, pos = float(cam['fov']), float(cam['facing']), cam['pos']
    for name, s in subjects.items():
        frame = (s or {}).get('frame')
        if frame not in FRAMES or not is_point((s or {}).get('pos')):
            rep.fail('G00', f'{label} subjects.{name} 要写 pos=[x, y] 和 frame（{"/".join(FRAMES)}）')
            continue
        if math.dist(pos, s['pos']) < 1e-6:
            continue
        r = rel_angle(pos, facing, s['pos'])
        half = fov / 2
        if frame == 'off':
            if abs(r) <= half:
                rep.warn('G03', f'{label} {name} 写的是不入画，但按机位在视场内（偏 {r:.0f}°）；确认有遮挡，否则改站位或机位')
            continue
        limit = half + (FG_EXTRA_DEG if frame == 'fg' else 0)
        if abs(r) > 90:
            rep.fail('G01', f'{label} {name} 在摄影机背后（偏 {r:.0f}°），写成{FRAMES[frame]}不可能成立')
        elif abs(r) > limit:
            rep.fail('G01', f'{label} {name} 在视场外（偏 {r:.0f}°，{fov:g}° 视场只到 ±{limit:g}°）')
        elif frame != 'fg':
            side = frame_side(r, fov)
            if side != frame:
                msg = f'{label} {name} 写在{FRAMES[frame]}，按机位算在{FRAMES[side]}（偏 {r:.0f}°）'
                if {side, frame} == {'left', 'right'}:
                    rep.fail('G02', msg)
                else:
                    rep.warn('G02', msg)
    return True


# ---------------- ledger ----------------

def lint_ledger(ledger, rep):
    profile = rule_profile(ledger, rep)
    events = ledger.get('source_events') or []
    lines = ledger.get('source_lines') or []
    units = ledger.get('units') or []

    policy = ledger.get('audio_policy')
    if policy is not None and policy not in AUDIO_POLICIES:
        rep.fail('A00', f'audio_policy 写成「{policy}」，只能是 {" / ".join(AUDIO_POLICIES)}')

    if not events:
        rep.fail('E00', 'source_events 为空：剧情事件必须从当前剧本逐条登记')
    event_ids = set()
    for ev in events:
        eid = ev.get('event_id')
        if not eid or not (ev.get('text') or '').strip():
            rep.fail('E00', f'剧情事件缺 event_id 或 text：{ev}')
            continue
        if eid in event_ids:
            rep.fail('E00', f'剧情事件 ID 重复：{eid}')
        event_ids.add(eid)
        if ev.get('origin') != 'script':
            rep.fail('E00', f'{eid} 的 origin 不是 script，只能登记当前剧本里的剧情')

    line_by_src = {}
    for ln in lines:
        src = ln.get('src')
        if not src or not (ln.get('text') or '').strip():
            rep.fail('D00', f'台词缺 src 或 text：{ln}')
            continue
        if src in line_by_src:
            rep.fail('D00', f'台词 ID 重复：{src}')
        line_by_src[src] = ln
        if ln.get('origin') != 'script':
            rep.fail('D03', f'{src} 的 origin 不是 script，只能登记当前剧本里的台词')

    if not units:
        rep.fail('U00', 'units 为空')

    referenced = set()
    parts_by_src = {}
    seen_units = set()
    for unit in units:
        uid = unit.get('unit_id')
        if not uid:
            rep.fail('U00', f'生成单元缺 unit_id：{unit}')
            continue
        if uid in seen_units:
            rep.fail('U00', f'生成单元 ID 重复：{uid}')
        seen_units.add(uid)
        shots = unit.get('shots') or []
        if not shots:
            rep.fail('U00', f'{uid} 没有镜头')
            continue

        if unit.get('continuous') and len(shots) != 1:
            rep.fail('T02', f'{uid} 标了一镜到底（continuous），台账里却有 {len(shots)} 个镜头')

        speakers = {line_by_src[d['src']].get('speaker') for s in shots for d in s.get('dialogue') or []
                    if d.get('src') in line_by_src}
        needs_camera = (bool(unit.get('blocking')) or len(speakers) >= 2) and profile == 'current'
        missing_camera = []
        windows = []

        cursor = 0.0
        for i, shot in enumerate(shots):
            sid = shot.get('shot_id', '?')
            label = f'{uid}/{sid}'
            refs = shot.get('event_refs') or []
            if not refs:
                rep.fail('E01', f'{label} 没有 event_refs：每个镜头必须挂上它落实的原剧情事件')
            for r in refs:
                if r not in event_ids:
                    rep.fail('E01', f'{label} 引用了不存在的剧情事件 {r}')
                referenced.add(r)

            transition = shot.get('transition')
            if i > 0 and transition is not None and transition not in TRANSITIONS:
                rep.fail('T02', f'{label} transition 写成「{transition}」，只能是 {" / ".join(TRANSITIONS)}')

            t = shot.get('t')
            if not (isinstance(t, list) and len(t) == 2 and all(is_num(x) for x in t)):
                rep.fail('T01', f'{label} 缺少时间段 t=[起, 止)')
                continue
            start, end = float(t[0]), float(t[1])
            if end <= start:
                rep.fail('T01', f'{label} 时间段止点不大于起点：{t}')
            if abs(start - cursor) > TOLERANCE_S:
                kind = '空洞' if start > cursor else '重叠'
                rep.fail('T01', f'{label} 与前一镜之间有{kind}：应从 {cursor:g} 秒开始，实际 {start:g} 秒')
            cursor = end

            if not lint_geometry(label, shot, rep):
                missing_camera.append(sid)

            for d in shot.get('dialogue') or []:
                src = d.get('src')
                if src not in line_by_src:
                    rep.fail('D03', f'{label} 的台词 {src} 不在 source_lines 里，不能使用剧本外台词')
                    continue
                text = d.get('text') or ''
                parts_by_src.setdefault(src, []).append((d.get('part') or '', text, label))
                w = d.get('window')
                where = f'{label} 台词 {part_label(d)}「{text}」'
                if not (isinstance(w, list) and len(w) == 2 and all(is_num(x) for x in w) and w[1] > w[0]):
                    rep.fail('D04', f'{where} 缺说话时窗 window=[起, 止]（单元内秒数）')
                    continue
                a, b = float(w[0]), float(w[1])
                if a < start - TOLERANCE_S or b > end + TOLERANCE_S:
                    rep.fail('D04', f'{where} 时窗 {a:g}–{b:g} 秒超出本镜 {start:g}–{end:g} 秒')
                check_rate(where, text, a, b, rep)
                windows.append((a, b, line_by_src[src].get('speaker'), where))

        windows.sort()
        for i, (a1, b1, sp1, w1) in enumerate(windows):
            for a2, b2, sp2, w2 in windows[i + 1:]:
                if a2 >= b1 - TOLERANCE_S:
                    break
                if sp1 == sp2:
                    rep.fail('D06', f'{w1} 与 {w2} 是同一人，时窗重叠')
                else:
                    rep.warn('D06', f'{w1} 与 {w2} 时窗重叠（两人抢话时保留，否则错开）')

        if missing_camera:
            if needs_camera:
                rep.fail('G00', f'{uid} 是走位单元（多人对话或 blocking=true），镜头 {"、".join(missing_camera)} 缺 camera/subjects，无法做视锥检查')
            else:
                rep.warn('G00', f'{uid} 镜头 {"、".join(missing_camera)} 没写 camera/subjects，未做视锥检查')

        duration = unit.get('duration')
        if duration is None:
            rep.fail('T01', f'{uid} 缺少 duration')
        elif abs(cursor - float(duration)) > TOLERANCE_S:
            rep.fail('T01', f'{uid} 镜头时间在 {cursor:g} 秒结束，与单元时长 {duration} 秒不一致')

    for eid in sorted(event_ids - referenced):
        rep.fail('E02', f'剧情事件 {eid} 没有被任何镜头落实（漏拍）：{_event_text(events, eid)}')

    for src, ln in line_by_src.items():
        parts = parts_by_src.get(src)
        if not parts:
            rep.fail('D02', f'台词 {src} 没有出现在任何镜头里（漏台词）：{ln["text"]}')
            continue
        joined = ''.join(p[1] for p in sorted(parts, key=lambda p: p[0]))
        if squash(joined) != squash(ln['text']):
            where = '、'.join(p[2] for p in parts)
            rep.fail('D01', f'台词 {src} 分段拼接后与原文不一致（{where}）\n'
                            f'      原文：{ln["text"]}\n      拼接：{joined}')


def _event_text(events, eid):
    for ev in events:
        if ev.get('event_id') == eid:
            return ev.get('text', '')
    return ''


# ---------------- prompt ----------------

def split_prompt_units(md_text):
    units = {}
    for m in re.finditer(r'^##\s+(\S+)[^\n]*\n(.*?)(?=^##\s|\Z)', md_text, re.S | re.M):
        block = re.search(r'```(?:text)?\n(.*?)```', m.group(2), re.S)
        if block:
            units[m.group(1)] = block.group(1)
    return units


def split_sections(prompt):
    """只按 §4a 规定的段名切分；段内出现的其他【…】（如声音方案里的【默认】）算正文。"""
    sections = {}
    matches = list(SECTION_RE.finditer(prompt))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(prompt)
        sections[m.group(1)] = sections.get(m.group(1), '') + prompt[m.end():end]
    return sections


def director_text(prompt, sections, verbatim, sound_fixed):
    """去掉默认摄影段、声音方案的固定文字、引号内台词与剧本原文，只留导演层自己写的文字。
    sound_fixed=None 表示整段声音方案都不计（旧项目）。"""
    text = prompt
    if sections.get('默认摄影'):
        text = text.replace(sections['默认摄影'], '')
    sound = sections.get('声音方案')
    if sound:
        if sound_fixed is None:
            text = text.replace(sound, '')
        elif sound.lstrip().startswith(sound_fixed):
            text = text.replace(sound, sound.lstrip()[len(sound_fixed):])
    text = QUOTE_RE.sub('', text)
    for v in sorted(verbatim, key=len, reverse=True):
        if len(v) >= 4:
            text = text.replace(v, '')
    return text


def check_spans(uid, label, spans, start, end, rep, code):
    cursor = start
    for a, b in spans:
        if abs(a - cursor) > TOLERANCE_S:
            kind = '空洞' if a > cursor else '重叠'
            rep.fail(code, f'{uid} {label}在 {cursor:g} 秒处有{kind}（下一段从 {a:g} 秒开始）')
        if b <= a:
            rep.fail(code, f'{uid} {label}时间段 [{a:g}–{b:g}] 止点不大于起点')
        cursor = b
    if spans and abs(cursor - end) > TOLERANCE_S:
        rep.fail(code, f'{uid} {label}在 {cursor:g} 秒结束，应在 {end:g} 秒结束')


def parse_timeline(timeline):
    """镜头行、镜头行所在整行、镜内正文与分拍行（带在 timeline 里的起止位置）。"""
    shots = []
    matches = list(SHOT_LINE_RE.finditer(timeline))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(timeline)
        header_end = timeline.find('\n', m.end())
        if header_end == -1 or header_end > end:
            header_end = end
        body = timeline[header_end:end]
        beats = []
        for bm in BEAT_LINE_RE.finditer(body):
            line_end = body.find('\n', bm.end())
            line_end = len(body) if line_end == -1 else line_end
            beats.append((float(bm.group(1)), float(bm.group(2)), header_end + bm.start(), header_end + line_end))
        shots.append({
            'n': int(m.group(3)),
            'span': (float(m.group(1)), float(m.group(2))),
            'header': timeline[m.start():header_end],
            'body': body,
            'beats': beats,
            'start': m.start(),
            'end': end,
        })
    return shots


def lint_timeline(uid, unit, shots, rep):
    duration = unit.get('duration')
    if not shots:
        rep.fail('P06', f'{uid} 的【时间轴镜头】里没有找到「[起–止秒] 镜头N」镜头行')
        return
    if duration is not None:
        check_spans(uid, '镜头时间轴', [s['span'] for s in shots], 0.0, float(duration), rep, 'P06')

    for i, s in enumerate(shots):
        n, (a, b), body = s['n'], s['span'], s['body']
        if n != i + 1:
            rep.fail('P06', f'{uid} 镜头编号不连续：第 {i + 1} 个镜头写成了「镜头{n}」')
        if not s['beats']:
            rep.fail('P09', f'{uid} 镜头{n} 没有 [起–止秒] 分拍')
        else:
            check_spans(uid, f'镜头{n} 分拍', [(x, y) for x, y, _, _ in s['beats']], a, b, rep, 'P06')
        if '表演：' not in body:
            rep.fail('P09', f'{uid} 镜头{n} 缺少「表演：」微表演')
        if '背景：' not in body:
            rep.fail('P09', f'{uid} 镜头{n} 缺少「背景：」')
        if '站位：' not in body:
            rep.warn('P09', f'{uid} 镜头{n} 没有「站位：」（纯空镜可忽略，有人物时必须写）')
        if i == 0 and '首帧：' not in body:
            rep.fail('P09', f'{uid} 第一镜缺少「首帧：」')
        if i == len(shots) - 1 and '本镜结束：' not in body:
            rep.fail('P09', f'{uid} 最后一镜缺少「本镜结束：」')

        if not FACING_RE.search(s['header']):
            rep.fail('P11', f'{uid} 镜头{n} 的机位没写朝向：写「朝西」或「拍向{{地标}}」')
        for fov in FOV_RE.findall(s['header']):
            if int(fov) not in FOV_TABLE:
                rep.fail('P14', f'{uid} 镜头{n} 视场角 {fov}° 不在 §4a 换算表里（{"/".join(map(str, FOV_TABLE))}）')


def lint_transitions(uid, unit, control, shots, rep):
    ledger_shots = unit.get('shots', [])
    if unit.get('continuous'):
        if '一镜到底' not in control:
            rep.fail('P10', f'{uid} 台账标了一镜到底，【总控】里没有写「一镜到底」')
        return
    m = re.search(r'共\s*(\d+)\s*个镜头', control)
    if not m:
        rep.fail('P10', f'{uid} 【总控】没有写「共N个镜头」的镜头数锁')
    else:
        declared = int(m.group(1))
        if shots and declared != len(shots):
            rep.fail('P10', f'{uid} 【总控】写共 {declared} 个镜头，时间轴实际 {len(shots)} 个')
        if declared != len(ledger_shots):
            rep.fail('P10', f'{uid} 【总控】写共 {declared} 个镜头，剧情台账里本单元有 {len(ledger_shots)} 个')

    kinds = [(k + 1, s.get('transition') or '硬切') for k, s in enumerate(ledger_shots) if k > 0]
    special = [(k, t) for k, t in kinds if t != '硬切']
    if len(ledger_shots) > 1:
        if not special and '只用硬切' not in control:
            rep.fail('P10', f'{uid} 【总控】要写「镜头之间只用硬切」')
        for k, t in special:
            phrase = f'镜头{k - 1}到镜头{k}{t}'
            if phrase not in control:
                rep.fail('P10', f'{uid} 台账里镜头{k} 用{t}，【总控】要写「{phrase}」')
        if special and len(special) < len(kinds) and '其余硬切' not in control:
            rep.fail('P10', f'{uid} 【总控】写了特殊转场，还要写「其余硬切」')
        if special and '只用硬切' in control:
            rep.fail('P10', f'{uid} 台账里有{special[0][1]}，【总控】却写「只用硬切」')

    for k, t in kinds:
        if k - 1 < len(shots):
            head = shots[k - 1]['header']
            got = re.search(r'镜头\s*\d+\s*[：:]\s*([^。，,]*)', head)
            if not got or got.group(1).strip() != t:
                rep.fail('P10', f'{uid} 镜头{k} 应以「镜头{k}：{t}。」开头')


def lint_dialogue_windows(uid, unit, timeline, shots, rep):
    for i, lshot in enumerate(unit.get('shots', [])):
        if i >= len(shots):
            break
        s = shots[i]
        region = timeline[s['start']:s['end']]
        for d in lshot.get('dialogue') or []:
            text, w = d.get('text') or '', d.get('window')
            label = f'{uid} 镜头{s["n"]} 台词 {part_label(d)}「{text}」'
            m = re.search(r'[“"「『]' + re.escape(text) + r'[”"」』]' + WINDOW_AFTER_QUOTE, region)
            if not m:
                if re.search(r'[“"「『]' + re.escape(text) + r'[”"」』]', region):
                    rep.fail('P12', f'{label} 引号后面要紧跟「（起至止秒说完」')
                else:
                    rep.fail('P12', f'{label} 没有写在镜头{s["n"]}的分拍里')
                continue
            a, b = float(m.group(1)), float(m.group(2))
            if isinstance(w, list) and len(w) == 2 and all(is_num(x) for x in w):
                if abs(a - w[0]) > TOLERANCE_S or abs(b - w[1]) > TOLERANCE_S:
                    rep.fail('P12', f'{label} 提示词写 {a:g}至{b:g}秒，台账 window 是 {w[0]:g}–{w[1]:g} 秒')
            pos = s['start'] + m.start()
            beat = next((bt for bt in s['beats'] if bt[2] <= pos < bt[3]), None)
            if not beat:
                rep.fail('P12', f'{label} 不在任何「[起–止秒]」分拍行里')
            elif a < beat[0] - TOLERANCE_S or b > beat[1] + TOLERANCE_S:
                rep.fail('P12', f'{label} 时窗 {a:g}–{b:g} 秒超出所在分拍 {beat[0]:g}–{beat[1]:g} 秒')


def lint_standing(uid, unit, shots, rep):
    names_side = {'左': 'left', '右': 'right', '中': 'center'}
    for i, lshot in enumerate(unit.get('shots', [])):
        subjects = lshot.get('subjects') or {}
        if not subjects or i >= len(shots):
            continue
        stand = '\n'.join(ln.strip()[3:] for ln in shots[i]['body'].splitlines() if ln.strip().startswith('站位：'))
        if not stand:
            continue
        sentences = [x.strip() for x in re.split(r'[。\n]', stand) if x.strip()]
        for name, s in subjects.items():
            frame = (s or {}).get('frame')
            if '·' in name or frame not in FRAMES:
                continue
            sent = next((x for x in sentences if x.startswith(name)), None)
            hit = SIDE_PHRASE_RE.search(sent) if sent else None
            if not hit:
                continue
            claim = names_side[hit.group(1)] if hit.group(1) else 'off'
            msg = f'{uid} 镜头{shots[i]["n"]} 站位写{name}「{hit.group(0)}」，台账视锥是{FRAMES[frame]}'
            if frame == 'fg':
                if claim == 'off':
                    rep.fail('P15', msg)
            elif (frame == 'off') != (claim == 'off') or {frame, claim} == {'left', 'right'}:
                rep.fail('P15', msg)
            elif frame != claim:
                rep.warn('P15', msg)


def voice_of(section, speaker, names):
    marks = sorted((m.start(), n) for n in names for m in re.finditer(re.escape(n) + '：', section))
    for k, (pos, n) in enumerate(marks):
        if n != speaker:
            continue
        seg = section[pos:marks[k + 1][0] if k + 1 < len(marks) else len(section)]
        v = re.search(r'声线：([^。\n]*)', seg)
        if v:
            return v.group(1).strip()
    return None


def lint_prompt(md_path, ledger, rep, max_words=0):
    profile = rule_profile(ledger, rep)
    prompt_text = Path(md_path).read_text(encoding='utf-8')
    units_md = split_prompt_units(prompt_text)
    ledger_units = {u.get('unit_id'): u for u in ledger.get('units', [])}
    line_by_src = {ln.get('src'): ln for ln in ledger.get('source_lines', []) if ln.get('src')}
    policy = ledger.get('audio_policy') or AUDIO_POLICIES[0]
    verbatim = [ev.get('text', '') for ev in ledger.get('source_events', [])]
    verbatim += [ln.get('text', '') for ln in ledger.get('source_lines', [])]
    id_tokens = set(ledger_units)
    names = {ln.get('speaker') for ln in line_by_src.values() if ln.get('speaker')}
    for u in ledger_units.values():
        for s in u.get('shots', []):
            if s.get('shot_id'):
                id_tokens.add(s['shot_id'])
            names.update(k.split('·')[0] for k in (s.get('subjects') or {}))
    voices = {}

    if profile == 'legacy':
        rep.warn('V00', f'台账 rule_version={ledger.get("rule_version")} 早于 2026.09.29.4，按旧提示词结构检查：'
                        '只查指代词、场次编号、否定词、@图、时间轴首尾相接、台词逐字和长度')
    if not max_words:
        rep.warn('P17', '没有传 --max-prompt-words，未检查长度上限；用当轮 canvas_video_provider_config 的 max_prompt_words')

    for uid in ledger_units:
        if uid not in units_md:
            rep.fail('P00', f'台账里的生成单元 {uid} 在提示词文件中没有对应的 `## {uid}` 段落')
    for uid in units_md:
        if uid not in ledger_units:
            rep.fail('P00', f'提示词里的 {uid} 不在剧情台账中')

    for uid, prompt in units_md.items():
        unit = ledger_units.get(uid)
        if not unit:
            continue
        sections = split_sections(prompt)
        has_dialogue = any(s.get('dialogue') for s in unit.get('shots', []))
        sound_fixed = SOUND_PLANS.get((policy, has_dialogue)) if profile == 'current' else None
        own = director_text(prompt, sections, verbatim, sound_fixed)

        if '@图' in prompt:
            rep.fail('P04', f'{uid} 使用了 @图 标签；WorkRally 参考图必须写「第N张图片」，对应参考数组下标')

        hits, scan = [], own
        for w in sorted(CONTEXT_REFS, key=len, reverse=True):
            if w in scan:
                hits.append(w)
                scan = scan.replace(w, '')
        if hits:
            rep.fail('P01', f'{uid} 出现上下文指代词：{"、".join(hits)}（提示词必须独立可读，把前情展开成完整物理状态）')

        for pat in SCENE_NUMBER_PATTERNS:
            for m in re.finditer(pat, prompt):
                rep.fail('P02', f'{uid} 泄漏场次或剧集编号：「{m.group(0)}」')

        neg_text = own
        for w in NEGATION_EXEMPT:
            neg_text = neg_text.replace(w, '')
        negs, total = [], 0
        for w in sorted(NEGATION_MARKERS, key=len, reverse=True):
            n = neg_text.count(w)
            if n:
                negs.append(f'{w}×{n}')
                total += n
                neg_text = neg_text.replace(w, '')
        if total > NEGATION_MAX_PER_UNIT:
            rep.fail('P03', f'{uid} 否定词 {total} 个，超过 {NEGATION_MAX_PER_UNIT} 个：{"、".join(negs)}'
                            f'（先写该是什么样；默认摄影、声音方案固定文字、引号内台词与剧本原文不计入）')

        flat = squash(prompt)
        for shot in unit.get('shots', []):
            for d in shot.get('dialogue') or []:
                text = d.get('text') or ''
                if text and flat.count(squash(text)) == 0:
                    rep.fail('P07', f'{uid}/{shot.get("shot_id", "?")} 的台词 {d.get("src")} 没有在提示词里逐字出现：{text}')

        length = len(prompt.strip())
        if max_words:
            if length > max_words:
                rep.fail('P17', f'{uid} 提示词 {length} 字，超过平台上限 {max_words}')
            elif length > max_words * LENGTH_WARN_RATIO:
                rep.warn('P17', f'{uid} 提示词 {length} 字，接近平台上限 {max_words}')

        timeline = sections.get('时间轴镜头', '')
        if profile == 'legacy':
            spans = [(float(a), float(b)) for a, b in BEAT_LINE_RE.findall(timeline)]
            if not spans:
                rep.fail('P06', f'{uid} 的【时间轴镜头】里没有「[起–止秒]」行')
            elif unit.get('duration') is not None:
                check_spans(uid, '时间轴', spans, 0.0, float(unit['duration']), rep, 'P06')
            continue

        for token in sorted(id_tokens):
            if re.search(r'(?<![A-Za-z0-9_-])' + re.escape(token) + r'(?![A-Za-z0-9_])', prompt):
                rep.fail('P02', f'{uid} 正文里出现了单元号或镜号「{token}」，只能写在 Markdown 标题与台账里')

        for name in RETIRED_SECTIONS:
            if name in sections:
                rep.fail('P08', f'{uid} 仍在使用已停用的【{name}】段（§4a 已并入其他段落）')
        for name in REQUIRED_SECTIONS + (['人物'] if has_dialogue else []):
            if name not in sections:
                rep.fail('P08', f'{uid} 缺少【{name}】段')
        order = [m.group(1) for m in SECTION_RE.finditer(prompt) if m.group(1) in SECTIONS]
        expected = [s for s in SECTIONS if s in order]
        if order != expected:
            rep.warn('P08', f'{uid} 段落顺序与 §4a 不一致：{" → ".join(order)}')

        light = sections.get('光线与色彩', '')
        if light:
            missing = [f for f in LIGHT_FIELDS if f not in light]
            if missing:
                rep.fail('P05', f'{uid} 【光线与色彩】缺少：{"、".join(missing)}')

        shots = parse_timeline(timeline)
        lint_timeline(uid, unit, shots, rep)
        lint_transitions(uid, unit, sections.get('总控', ''), shots, rep)
        lint_dialogue_windows(uid, unit, timeline, shots, rep)
        lint_standing(uid, unit, shots, rep)

        m = re.search(r'方向：([^；;。\n]*)', light)
        if m and len(shots) > 1 and SCREEN_SIDE_RE.search(m.group(1)):
            rep.fail('P13', f'{uid} 【光线与色彩】方向写成「{m.group(1)}」：{len(shots)} 个镜头机位不同，画面左右会变，'
                            '单元级只写世界方位（如房间北侧），画面左右写进单镜')

        for i, lshot in enumerate(unit.get('shots', [])):
            cam = lshot.get('camera') or {}
            if i < len(shots) and is_num(cam.get('fov')):
                written = [int(x) for x in FOV_RE.findall(shots[i]['header'])]
                if written and int(cam['fov']) not in written:
                    rep.fail('P14', f'{uid} 镜头{shots[i]["n"]} 写 {written[0]}° 视场，台账 camera.fov 是 {cam["fov"]:g}°')

        speakers = []
        for s in unit.get('shots', []):
            for d in s.get('dialogue') or []:
                sp = (line_by_src.get(d.get('src')) or {}).get('speaker')
                if sp and sp not in speakers:
                    speakers.append(sp)
        people = sections.get('人物', '')
        for sp in speakers:
            v = voice_of(people, sp, names)
            if v is None:
                rep.fail('P16', f'{uid} 【人物】里 {sp} 没有写「声线：」')
            else:
                voices.setdefault(sp, []).append((uid, v))

        sound = sections.get('声音方案', '')
        if sound_fixed and not sound.lstrip().startswith(sound_fixed):
            kind = '有台词' if has_dialogue else '无台词'
            rep.fail('P18', f'{uid} 【声音方案】要以 {policy}（{kind}）的固定文字开头，逐字照抄：\n      {sound_fixed}')

        binding = sections.get('参考绑定', '')
        if binding.count(BINDING_ONCE) > 1:
            rep.warn('P19', f'{uid} 【参考绑定】里「{BINDING_ONCE}」写了 {binding.count(BINDING_ONCE)} 次，写一次即可')

    for sp, entries in voices.items():
        if len({squash(v) for _, v in entries}) > 1:
            listed = '；'.join(f'{u}「{v}」' for u, v in entries)
            rep.fail('P16', f'{sp} 的声线在各单元不一致，同一角色全片只能用一套：{listed}')


def main():
    ap = argparse.ArgumentParser(description='剧情保真与视频提示词机检')
    sub = ap.add_subparsers(dest='cmd', required=True)
    p_ledger = sub.add_parser('ledger', help='检查剧情台账：剧情事件覆盖、台词保真与语速、镜头时间、转场、视锥')
    p_ledger.add_argument('ledger')
    p_prompt = sub.add_parser('prompt', help='检查视频提示词：§4a 结构、指代词、编号、否定词、时间轴、台词时窗、站位、声线、长度')
    p_prompt.add_argument('prompts')
    p_prompt.add_argument('--ledger', required=True)
    p_prompt.add_argument('--max-prompt-words', type=int, default=0,
                          help='当轮 canvas_video_provider_config 返回的 max_prompt_words；0 表示不检查')
    args = ap.parse_args()

    rep = Report()
    if args.cmd == 'ledger':
        lint_ledger(load_ledger(args.ledger), rep)
        rep.print(f'剧情台账 {args.ledger}')
    else:
        lint_prompt(args.prompts, load_ledger(args.ledger), rep, args.max_prompt_words)
        rep.print(f'视频提示词 {args.prompts}')
    sys.exit(1 if rep.failed else 0)


if __name__ == '__main__':
    main()
