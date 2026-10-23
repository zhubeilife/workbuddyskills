#!/usr/bin/env bash
# =============================================================================
# AI 组卷 · 分块重叠成卷（渲染 + 转 docx 按块并行 + 缝合）
#
# 用途：拉题阶段按块并行时，某一块的 picks 一就绪即可**立刻**渲染并转档，
#       与仍在拉取的其它块**重叠**，最后把各块 docx 缝合成完整的两份交付物。
#
# 用法:
#   bash render_blocks.sh <out_prefix> <block1.json> <block2.json> [block3.json ...]
#
#   入参 blockN.json 由 build_questions.py --split-blocks 产出
#   （已带全局题号 + omit_header 控制，缝合后标题/卷头不会重复）。
#
# 产出（out_prefix 所在目录）:
#   <prefix>_试卷.docx   分块转档后缝合
#   <prefix>_解析.docx   分块转档后缝合
#   <prefix>_b{i}_paper.html / _analysis.html   过程文件
#
# 说明:
#   - 各块的「渲染 + 转 docx」并发进行（块级并行），比「全部拉完再一次性转」更省墙钟。
#   - 双向细目表依赖全卷，请用 render_blueprint.py 单独渲染（见 render_all.sh）。
# =============================================================================
set -euo pipefail

if [ $# -lt 3 ]; then
  echo "用法: bash render_blocks.sh <out_prefix> <block1.json> <block2.json> [...]" >&2
  exit 2
fi

PREFIX_IN="$1"; shift
OUT_DIR="$(dirname "$PREFIX_IN")"
mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
PREFIX="$OUT_DIR/$(basename "$PREFIX_IN")"

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"

find_py() {
  for c in "$HOME"/.workbuddy/binaries/python/versions/*/python.exe \
           "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3; do
    [ -x "$c" ] && { echo "$c"; return 0; }
  done
  command -v python3 2>/dev/null || command -v python 2>/dev/null || true
}
PY="${PYTHON:-$(find_py)}"
[ -n "${PY:-}" ] || { echo "[render_blocks] 未找到 Python 解释器。" >&2; exit 1; }

BLOCKS=("$@")
PAPER_DOCX=()
ANA_DOCX=()
PIDS=()

# —— 逐块：渲染 HTML（后台）→ 转两份 docx（后台）；所有块并发 ——
for i in "${!BLOCKS[@]}"; do
  BJ="${BLOCKS[$i]}"
  BJ="$(readlink -f "$BJ")"
  n=$((i+1))
  PH="${PREFIX}_b${n}_paper.html"
  AH="${PREFIX}_b${n}_analysis.html"
  PD="${PREFIX}_b${n}_paper.docx"
  AD="${PREFIX}_b${n}_analysis.docx"
  PAPER_DOCX+=("$PD")
  ANA_DOCX+=("$AD")

  (
    "$PY" "$SELF_DIR/render_paper.py" "$BJ" -o "$PH" --part paper
    "$PY" "$SELF_DIR/render_paper.py" "$BJ" -o "$AH" --part analysis
    bash "$SELF_DIR/to_docx.sh" "$PH" "$PD" >/dev/null
    bash "$SELF_DIR/to_docx.sh" "$AH" "$AD" >/dev/null
    echo "[render_blocks] 块 $n 完成"
  ) &
  PIDS+=("$!")
done

# 等待所有块
FAIL=0
for pid in "${PIDS[@]}"; do
  wait "$pid" || FAIL=1
done
[ "$FAIL" -eq 0 ] || { echo "[render_blocks] 有块失败，终止缝合。" >&2; exit 1; }

# —— 缝合 ——
bash "$SELF_DIR/merge_docx.sh" --out "${PREFIX}_试卷.docx" "${PAPER_DOCX[@]}"
bash "$SELF_DIR/merge_docx.sh" --out "${PREFIX}_解析.docx" "${ANA_DOCX[@]}"

echo "[render_blocks] 完成:"
echo "  ${PREFIX}_试卷.docx"
echo "  ${PREFIX}_解析.docx"
