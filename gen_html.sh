#!/usr/bin/env bash
# 从 CATALOG-full.md 重新生成 CATALOG-full.html
# 用法: ./gen_html.sh
# 依赖: pandoc (brew install pandoc) 和 python3
set -euo pipefail
cd "$(dirname "$0")"

SRC="CATALOG-full.md"
BODY="$(mktemp /tmp/catalog-body.XXXXXX.html)"
trap 'rm -f "$BODY"' EXIT

pandoc -f gfm -t html5 "$SRC" -o "$BODY"

BODY="$BODY" python3 << 'PYEOF'
import os

body = open(os.environ['BODY']).read()

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>workbuddyskills 完整清单（补充版）</title>
<style>
:root { --border:#d0d7de; --head-bg:#f6f8fa; --hover:#fff8c5; --accent:#0969da; }
* { box-sizing: border-box; }
body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
       margin: 0; color: #1f2328; line-height: 1.6; }
.container { max-width: 1280px; margin: 0 auto; padding: 24px 32px 80px; }
h1 { font-size: 1.7rem; border-bottom: 2px solid var(--border); padding-bottom: .3em; }
h2 { font-size: 1.4rem; margin-top: 2em; border-bottom: 1px solid var(--border); padding-bottom: .2em; }
h3 { font-size: 1.1rem; margin-top: 1.8em; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
blockquote { margin: 1em 0; padding: .5em 1em; color: #57606a; border-left: 4px solid var(--border); background: var(--head-bg); }
code { background: #eff1f3; padding: .15em .4em; border-radius: 4px; font-size: .88em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: .88rem; display: block; overflow-x: auto; }
thead th { position: sticky; top: 52px; background: var(--head-bg); z-index: 2; }
th, td { border: 1px solid var(--border); padding: 6px 10px; text-align: left; vertical-align: top; }
tbody tr:nth-child(even) { background: #fafbfc; }
tbody tr:hover { background: var(--hover); }
td:first-child { white-space: nowrap; }
#searchbar { position: sticky; top: 0; z-index: 10; background: #fff; padding: 10px 0;
             display: flex; gap: 12px; align-items: center; border-bottom: 1px solid var(--border); }
#q { flex: 1; padding: 8px 12px; font-size: 1rem; border: 1px solid var(--border); border-radius: 6px; }
#q:focus { outline: 2px solid var(--accent); }
#stat { color: #57606a; font-size: .85rem; white-space: nowrap; }
#top { position: fixed; right: 24px; bottom: 24px; padding: 8px 14px; background: var(--accent); color: #fff;
       border: none; border-radius: 6px; cursor: pointer; opacity: .85; display: none; }
tr.hide { display: none; }
</style>
</head>
<body>
<div class="container">
<div id="searchbar">
  <input id="q" type="search" placeholder="搜索：名称 / 用途 / 前置条件（实时过滤）…">
  <span id="stat"></span>
</div>
''' + body + '''
</div>
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑ 顶部</button>
<script>
const q = document.getElementById('q'), stat = document.getElementById('stat');
const rows = [...document.querySelectorAll('tbody tr')];
function filter() {
  const k = q.value.trim().toLowerCase();
  let shown = 0;
  for (const r of rows) {
    const hit = !k || r.textContent.toLowerCase().includes(k);
    r.classList.toggle('hide', !hit);
    if (hit) shown++;
  }
  stat.textContent = k ? `匹配 ${shown} / ${rows.length} 条` : `共 ${rows.length} 条`;
  document.querySelectorAll('table').forEach(t => {
    const visible = [...t.querySelectorAll('tbody tr')].some(r => !r.classList.contains('hide'));
    t.style.display = visible ? '' : 'none';
  });
}
q.addEventListener('input', filter);
filter();
addEventListener('scroll', () => {
  document.getElementById('top').style.display = scrollY > 600 ? 'block' : 'none';
});
</script>
</body>
</html>'''

open('CATALOG-full.html', 'w').write(html)
print(f"生成 CATALOG-full.html, 大小: {len(html)} 字节")
PYEOF

# 同步生成 index.html，使 GitHub Pages 根地址可直接打开
cp CATALOG-full.html index.html
echo "生成 index.html（与 CATALOG-full.html 内容相同，供 Pages 根路径访问）"
