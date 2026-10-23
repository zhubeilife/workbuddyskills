#!/usr/bin/env python3
"""Render already-authorized MCP delivery responses. No network or API access."""
import argparse
import base64
from datetime import datetime
from html import escape
import ipaddress
import json
from pathlib import Path
import re
from string import Template
import sys
from urllib.parse import urlsplit, urlunsplit

MAX_BYTES = 5_000_000
MAX_COMPANIES = 500
STATUS = {
    'queued': '排队中', 'running': '找客进行中', 'completed': '任务已完成',
    'partial': '任务部分完成', 'failed': '任务未完成', 'cancelled': '任务已取消',
}
FIT = ('强符合', '弱符合')


class SnapshotError(ValueError):
    """A capture cannot safely be presented as the requested task's results."""


def obj(value, name):
    if not isinstance(value, dict):
        raise SnapshotError(name + ' 必须是对象。')
    return value


def count(value, name):
    if type(value) is not int or not 0 <= value <= MAX_COMPANIES:
        raise SnapshotError(name + ' 必须是 0–500 的整数。')
    return value


def text(value, name='', maximum=12000):
    if value is None:
        return ''
    if not isinstance(value, str) or len(value) > maximum:
        raise SnapshotError((name or '文字字段') + ' 类型或长度不正确。')
    # Remove invisible control characters, retain ordinary newlines and tabs.
    return ''.join(c for c in value.strip() if ord(c) >= 32 or c in '\n\t')


def identifier(value, name):
    value = text(value, name, 300)
    if not value or re.search(r'\s', value):
        raise SnapshotError(name + ' 缺失或格式不正确。')
    return value


def terms(value, name):
    if value is None:
        return []
    if isinstance(value, str):
        return [text(value, name)] if value.strip() else []
    if not isinstance(value, list) or len(value) > 100:
        raise SnapshotError(name + ' 必须是文字或文字列表。')
    return list(dict.fromkeys(v for v in (text(v, name) for v in value) if v))


def safe_url(value, domain=False):
    """Only public HTTP(S) web links, with no credentials or capability query."""
    value = text(value, '网页地址', 2000)
    if not value or re.search(r'[\s\\<>"\x00-\x1f]', value):
        return None
    if domain:
        # company.domain is a hostname, never company.domains (business areas).
        if '/' in value or ':' in value or '@' in value:
            return None
        value = 'https://' + value
    try:
        parts = urlsplit(value)
        host = parts.hostname
        if parts.scheme not in ('https', 'http') or not host or parts.username or parts.password:
            return None
        if parts.port not in (None, 80, 443) or '.' not in host:
            return None
        ascii_host = host.encode('idna').decode('ascii')
        if not all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', p) for p in ascii_host.split('.')):
            return None
        try:
            if not ipaddress.ip_address(host).is_global:
                return None
        except ValueError:
            if host.endswith(('.local', '.internal', '.localhost')):
                return None
        # Token-bearing links should never enter a shareable HTML snapshot.
        if re.search(r'(?i)(token|secret|password|authorization|signature|api.?key|code)=', parts.query):
            return None
        return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ''))
    except (ValueError, UnicodeError):
        return None


def validate(snapshot):
    obj(snapshot, '快照')
    captured = text(snapshot.get('capturedAt'), 'capturedAt', 60)
    try:
        timestamp = datetime.fromisoformat(captured.replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            raise ValueError()
    except ValueError:
        raise SnapshotError('capturedAt 需要包含时区的 ISO 时间。') from None
    job = obj(snapshot.get('job'), 'job_get 返回值')
    job_id = identifier(job.get('id'), '任务编号')
    if job.get('kind') != 'leads' or job.get('status') not in STATUS:
        raise SnapshotError('只支持获客任务的已知状态。')
    target = count(job.get('targetCount'), '任务目标数量')
    if target < 1:
        raise SnapshotError('任务目标数量必须大于零。')
    delivered = count(job.get('delivered'), '任务交付数量')
    for key in ('progress', 'message'):
        text(job.get(key), key)
    terms(job.get('warnings'), '任务提醒')
    pages = snapshot.get('pages')
    if not isinstance(pages, list) or not 1 <= len(pages) <= 50:
        raise SnapshotError('需要 1–50 页真实 job_results 响应。')
    cursor = None
    summary = None
    rows, seen, company_ids = [], {}, set()
    anomalies = []
    excluded = 0
    for page_index, page in enumerate(pages):
        obj(page, '采集页')
        if 'after' not in page or page['after'] != cursor or (page_index and cursor is None):
            raise SnapshotError('结果游标不连续；请从第一页重新读取同一任务。')
        response = obj(page.get('response'), 'job_results 返回值')
        if response.get('jobId', job_id) != job_id:
            raise SnapshotError('结果页属于其他任务，不能合并。')
        current_summary = obj(response.get('summary'), '结果汇总')
        current_summary = {key: count(current_summary.get(key), '汇总 ' + key) for key in ('total', 'strong', 'weak')}
        if current_summary['strong'] + current_summary['weak'] != current_summary['total']:
            raise SnapshotError('强弱符合数量与汇总总数不一致。')
        if summary is not None and summary != current_summary:
            raise SnapshotError('分页期间结果汇总发生变化；请重新读取后再生成快照。')
        summary = current_summary
        items = response.get('items')
        if not isinstance(items, list) or len(items) > 10:
            raise SnapshotError('每页必须是最多 10 条结果。')
        for row in items:
            obj(row, '交付记录')
        next_cursor = response.get('nextCursor')
        if 'nextCursor' not in response or (next_cursor is not None and not isinstance(next_cursor, str)):
            raise SnapshotError('结果页缺少有效 nextCursor。')
        if next_cursor is not None:
            identifier(next_cursor, '下一页游标')
            if len(items) != 10 or next_cursor != items[-1].get('id') or next_cursor == cursor:
                raise SnapshotError('下一页游标与本页末条交付不一致。')
        for row in items:
            delivery_id = identifier(row.get('id'), '交付编号')
            if row.get('jobId', job_id) != job_id:
                raise SnapshotError('交付记录属于其他任务，不能合并。')
            if delivery_id in seen:
                if seen[delivery_id] != row:
                    raise SnapshotError('同一交付编号出现不同内容，请重新读取。')
                continue
            seen[delivery_id] = row
            if row.get('fit') not in FIT:
                excluded += 1
                continue
            company = obj(row.get('company'), '交付公司')
            # Validate the exact fields used, ignore unrelated/private fields.
            for key in ('name', 'domain', 'country', 'industry', 'synopsis', 'identity', 'role'):
                text(company.get(key), '公司 ' + key)
            for key in ('products', 'roles', 'domains'):
                terms(company.get(key), '公司 ' + key)
            text(row.get('reason'), '符合理由')
            routes = row.get('matchedRoutes', [])
            if not isinstance(routes, list) or len(routes) > 30:
                raise SnapshotError('匹配路线应为列表。')
            for route in routes:
                obj(route, '匹配路线')
                text(route.get('title'), '路线名称')
            identity = company.get('id')
            if identity is not None:
                identity = identifier(identity, '公司编号')
                if identity in company_ids:
                    anomalies.append('不同交付记录出现相同公司编号，请核对服务端结果；此页保留原始交付记录。')
                company_ids.add(identity)
            rows.append(row)
        cursor = next_cursor
    if len(rows) > summary['total'] or sum(r['fit'] == '强符合' for r in rows) > summary['strong'] or sum(r['fit'] == '弱符合' for r in rows) > summary['weak']:
        raise SnapshotError('当前交付列表超过服务端汇总，请重新读取。')
    if excluded:
        anomalies.append('响应包含非强符合／弱符合记录，未展示这些内容。')
    if delivered != summary['total']:
        anomalies.append('任务进度与结果汇总数量不一致，需要重新读取核对；当前仅展示已读取的交付记录。')
    complete = cursor is None and len(rows) == summary['total'] and not excluded and delivered == summary['total']
    if cursor is not None or len(rows) < summary['total'] or excluded:
        anomalies.append('当前为部分结果快照，尚未展示全部交付；请在对话中继续读取。')
    return job, rows, summary, complete, list(dict.fromkeys(anomalies)), captured


def e(value):
    return escape(str(value), quote=True)


def field(label, value):
    if not value:
        return ''
    return '<div class="field"><dt>' + e(label) + '</dt><dd>' + e(value) + '</dd></div>'


def public_sources(company):
    sources = company.get('sources', [])
    if not isinstance(sources, list) or len(sources) > 100:
        raise SnapshotError('公司来源必须是有界列表。')
    links = {}
    for source in sources:
        obj(source, '资料来源')
        # Internal kind/id rows have no public URL and are deliberately omitted.
        url = safe_url(source.get('url'))
        if url and url not in links:
            links[url] = text(source.get('title'), '来源标题', 2000) or urlsplit(url).hostname
    if not links:
        return ''
    title = '资料来源' + ('（展示前 6 条）' if len(links) > 6 else '')
    return '<section class="sources"><h3>' + title + '</h3><ul>' + ''.join('<li><a href="' + e(url) + '" target="_blank" rel="noopener noreferrer">' + e(label) + ' <span aria-hidden="true">↗</span></a></li>' for url, label in list(links.items())[:6]) + '</ul></section>'


def task_scope(job):
    brief = obj(job.get('searchBrief', {}), '任务范围')
    routes = brief.get('routes', [])
    if not isinstance(routes, list) or len(routes) > 30:
        raise SnapshotError('任务路线必须是有界列表。')
    titles = []
    for route in routes:
        obj(route, '任务路线')
        title = text(route.get('title'), '任务路线名称')
        if title and title not in titles:
            titles.append(title)
    if titles:
        content = '<ul>' + ''.join('<li>' + e(title) + '</li>' for title in titles) + '</ul>'
    else:
        requirement = text(brief.get('requirement'), '任务需求') or text(job.get('query'), '任务需求')
        content = '<p>' + e(requirement) + '</p>' if requirement else ''
    countries = terms(brief.get('countries'), '目标市场')
    if countries:
        content += '<p class="scope-market">目标市场：' + e(' · '.join(countries)) + '</p>'
    return '<section class="scope"><h2>本次找客范围</h2>' + content + '</section>' if content else ''


def render(snapshot):
    job, rows, summary, complete, anomalies, captured = validate(snapshot)
    cards = []
    for index, row in enumerate(rows, 1):
        company = row['company']
        website = safe_url(company.get('domain'), domain=True)
        link = ('<a class="website" href="' + e(website) + '" target="_blank" rel="noopener noreferrer">' + e(company['domain']) + ' <span aria-hidden="true">↗</span></a>') if website else ''
        roles = terms(company.get('roles'), '角色') or terms(company.get('role') or company.get('identity'), '角色')
        details = ''.join((
            field('产品与服务', ' · '.join(terms(company.get('products'), '产品'))),
            field('所属行业', company.get('industry')),
            field('公司身份', ' · '.join(roles)),
            field('业务领域', ' · '.join(terms(company.get('domains'), '业务领域'))),
        ))
        routes = ' · '.join(dict.fromkeys(text(r.get('title')) for r in row.get('matchedRoutes', []) if text(r.get('title'))))
        cards.append('<article class="company"><div class="company-top"><span class="number">' + f'{index:02d}' + '</span><span class="fit ' + ('strong' if row['fit'] == '强符合' else 'weak') + '">' + row['fit'] + '</span></div><h2>' + e(company.get('name') or '公司名称未提供') + '</h2><div class="company-meta">' + ('<span>' + e(company['country']) + '</span>' if company.get('country') else '') + link + '</div>' + ('<p class="synopsis">' + e(company['synopsis']) + '</p>' if company.get('synopsis') else '') + '<dl>' + details + '</dl><section class="reason"><h3>匹配理由</h3><p>' + e(row.get('reason') or '本条交付未提供说明。') + '</p>' + ('<p class="matched">已记录的匹配路线：' + e(routes) + '</p>' if routes else '') + '</section>' + public_sources(company) + '</article>')
    running = job['status'] in ('queued', 'running')
    if not cards:
        empty = '任务仍在进行，暂时没有已交付公司。' if running else '这次任务暂无已交付公司。'
        cards = ['<section class="empty"><h2>' + empty + '</h2><p>这里只展示真实交付的公司，不以候选数量代替交付。</p></section>']
    notices = list(dict.fromkeys(anomalies + terms(job.get('warnings'), '任务提醒')))
    notice_html = '<aside class="notices" aria-label="结果说明">' + ''.join('<p>' + e(n) + '</p>' for n in notices) + '</aside>' if notices else ''
    strong = sum(row['fit'] == '强符合' for row in rows)
    weak = len(rows) - strong
    snapshot_label = '进行中的结果快照' if running else ('' if complete else '部分交付快照')
    message = text(job.get('message')) or text(job.get('progress'))
    template_path = Path(__file__).resolve().parent.parent / 'templates' / 'results.html'
    logo = template_path.parent.parent / 'assets' / 'brand-logo.png'
    brand_logo = 'data:image/png;base64,' + base64.b64encode(logo.read_bytes()).decode('ascii')
    return Template(template_path.read_text(encoding='utf-8')).substitute(
        status_badge='<span class="status">' + e(STATUS[job['status']]) + '</span>' if job['status'] != 'completed' else '', brand_logo=brand_logo,
        snapshot_badge='<span>' + e(snapshot_label) + '</span>' if snapshot_label else '', captured=e(captured),
        target=e(job['targetCount']), visible=e(len(rows)), total=e(summary['total']), strong=e(strong), weak=e(weak),
        message='<p class="message">' + e(message) + '</p>' if message else '',
        scope=task_scope(job), notices=notice_html, cards='\n'.join(cards),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve() or args.output.suffix.lower() != '.html':
            raise SnapshotError('输出必须为独立的 .html 文件。')
        if args.input.stat().st_size > MAX_BYTES:
            raise SnapshotError('结果快照超过 5 MB。')
        raw = args.input.read_text(encoding='utf-8')
        snapshot = json.loads(raw)
        result = render(snapshot)
        args.output.write_text(result, encoding='utf-8')
        print('已生成静态结果页。')
    except (SnapshotError, OSError, ValueError, TypeError, RecursionError):
        # Do not echo inputs, private response fields, paths or credentials.
        print('无法生成结果页：结果格式或采集状态不完整。请在对话中使用已读取的结果说明情况，必要时重新读取同一任务；不要重复开任务。', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
