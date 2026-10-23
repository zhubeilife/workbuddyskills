#!/usr/bin/env bash
# 更新 GitHub Pages（gh-pages 分支）上的清单网页
# 用法: ./publish_pages.sh
# 流程: 重新生成 HTML -> 提交 main -> 更新 gh-pages 分支（只含网页文件，避开全量检出）
set -euo pipefail
cd "$(dirname "$0")"

./gen_html.sh

# 提交 main 上的源文件（若有变化）
git add CATALOG-full.md CATALOG-full.html index.html gen_html.sh publish_pages.sh README.md 2>/dev/null || true
if ! git diff --cached --quiet; then
  git commit -m "docs: update catalog html viewer"
  git push origin main
  echo "main 已更新"
else
  echo "main 无变化"
fi

# 更新 gh-pages 分支
TMP=$(mktemp -d /tmp/gh-pages-pub.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
git clone -q --branch gh-pages --single-branch --depth 1 git@github.com:zhubeilife/workbuddyskills.git "$TMP"
cp index.html CATALOG-full.html "$TMP/"
cd "$TMP"
git add index.html CATALOG-full.html
if ! git diff --cached --quiet; then
  git -c user.name="zhubeilife" -c user.email="zhubeilife@users.noreply.github.com" \
    commit -q -m "deploy: update catalog html viewer"
  git push -q origin gh-pages
  echo "gh-pages 已更新，约 1 分钟后 https://zhubeilife.github.io/workbuddyskills/ 生效"
else
  echo "gh-pages 无变化"
fi
