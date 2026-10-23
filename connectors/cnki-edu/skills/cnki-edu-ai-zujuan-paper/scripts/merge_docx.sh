#!/usr/bin/env bash
# =============================================================================
# AI 组卷 · 分块 docx 缝合（wrapper：定位含 docxcompose 的 venv 后调用 merge_docx.py）
#
# 用法:
#   bash merge_docx.sh --out <最终.docx> [--page-break] <块1.docx> <块2.docx> ...
# =============================================================================
set -euo pipefail

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"

# 复用 to_docx.sh 的 venv 口径（docxcompose 装在该 venv 内）
VENV="${H2D_VENV:-$HOME/.workbuddy/binaries/python/envs/html-to-docx}"
VPY="$VENV/Scripts/python.exe"; [ -x "$VPY" ] || VPY="$VENV/bin/python"

if [ ! -x "$VPY" ]; then
  echo "[merge_docx] 未找到 html-to-docx venv（$VENV）。请先运行一次 to_docx.sh 以创建依赖。" >&2
  exit 1
fi
if ! "$VPY" -c "import docxcompose" >/dev/null 2>&1; then
  echo "[merge_docx] venv 缺少 docxcompose，正在安装…" >&2
  "$VPY" -m pip install -q docxcompose
fi

exec "$VPY" "$SELF_DIR/merge_docx.py" "$@"
