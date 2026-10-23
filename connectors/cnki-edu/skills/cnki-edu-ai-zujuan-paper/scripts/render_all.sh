#!/usr/bin/env bash
# =============================================================================
# AI 组卷 · 一键成卷（渲染三份 HTML + 并行转两份 docx）
#
# 用法:
#   bash render_all.sh <questions.json> <blueprint.json> <out_prefix> [out_dir]
#
# 产出（out_dir 默认 = out_prefix 所在目录）:
#   <prefix>_试卷.docx      试卷（不含解析）
#   <prefix>_解析.docx      解析（【考点】【分析】【解答】）
#   <prefix>_细目表.html    双向细目表
#   <prefix>_paper.html / <prefix>_analysis.html   过程文件
#
# 说明:
#   - 渲染与「转 docx」都尽量并行（两份 docx 同时转换）→ 少轮次、省墙钟
#   - 页边距/悬挂缩进/解析分页由 to_docx.sh 内建后处理完成
# =============================================================================
set -euo pipefail

if [ $# -lt 3 ]; then
  echo "用法: bash render_all.sh <questions.json> <blueprint.json> <out_prefix> [out_dir]" >&2
  exit 2
fi
QJSON="$(readlink -f "$1")"
BPJSON="$(readlink -f "$2")"
PREFIX_IN="$3"
OUT_DIR="${4:-$(dirname "$PREFIX_IN")}"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
PREFIX="$OUT_DIR/$(basename "$PREFIX_IN")"

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"

# 定位 Python（与 to_docx.sh 同口径：优先托管解释器）
find_py() {
  for c in "$HOME"/.workbuddy/binaries/python/versions/*/python.exe \
           "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3; do
    [ -x "$c" ] && { echo "$c"; return 0; }
  done
  command -v python3 2>/dev/null || command -v python 2>/dev/null || true
}
PY="${PYTHON:-$(find_py)}"
[ -n "${PY:-}" ] || { echo "[render_all] 未找到 Python 解释器。" >&2; exit 1; }

PAPER_HTML="${PREFIX}_paper.html"
ANA_HTML="${PREFIX}_analysis.html"
BP_HTML="${PREFIX}_细目表.html"

# 1) 渲染三份 HTML（彼此独立，可并行）
"$PY" "$SELF_DIR/render_paper.py" "$QJSON" -o "$PAPER_HTML" --part paper &
"$PY" "$SELF_DIR/render_paper.py" "$QJSON" -o "$ANA_HTML" --part analysis &
"$PY" "$SELF_DIR/render_blueprint.py" "$BPJSON" -o "$BP_HTML" &
wait

# 2) 并行转两份 docx
DOCX_PAPER="${PREFIX}_试卷.docx"
DOCX_ANA="${PREFIX}_解析.docx"
bash "$SELF_DIR/to_docx.sh" "$PAPER_HTML" "$DOCX_PAPER" &
P=$!
bash "$SELF_DIR/to_docx.sh" "$ANA_HTML" "$DOCX_ANA" &
A=$!
wait "$P"; wait "$A"

echo "[render_all] 完成:"
echo "  $DOCX_PAPER"
echo "  $DOCX_ANA"
echo "  $BP_HTML"
