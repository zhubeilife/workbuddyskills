#!/usr/bin/env bash
# =============================================================================
# AI 组卷 · 收尾一条龙（把 S7 的 5 步压成「一条命令 = 一轮」）
#
# 背景（2026-10-10 实测）：组卷墙钟的瓶颈是「模型轮次间隙」，不是 API——
#   25 题的全部 API 纯耗时仅 ≈20s，而墙钟却花了 1195s（间隙 ≈1175s）。
#   故每一轮模型往返都是稀缺资源。S7 原本要 5 次独立脚本调用
#     validate → merge_and_gap → build → render_all → selfcheck
#   = 5 个模型往返；本脚本把它们串成「一个进程、一次调用」，编排层只发 1 轮。
#
# 用法:
#   bash finish.sh --spec spec.json --prefix <out_prefix> [--work-dir .] \
#        [--split-blocks "1-9,10-18,19-25"] [--allow-missing] picks_1.json picks_2.json ...
#
# 参数:
#   --spec           spec.json（含 sections / blueprint.rows / total_score）
#   --prefix         产物前缀（试卷/解析/细目表 用此前缀）
#   --work-dir       中间文件目录（默认 = 当前目录）
#   --split-blocks   给出则走「分块重叠转档」（render_blocks 缝合并单独渲染细目表）
#   --allow-missing  缺题时也照常出卷（降级交付）；默认缺题即停并打印 missing
#
# 退出码:
#   0  三件套齐全且自检通过
#   1  缺题（未加 --allow-missing）→ 打印 missing，等编排层补齐后续跑（幂等，只补缺口）
#   2  缺题但已降级交付（--allow-missing）→ 产物可用，附缺题清单
#   3  自检失败（产物已生成，需人工核对）
#
# 产物:
#   <prefix>_试卷.docx  <prefix>_解析.docx  <prefix>_细目表.html
# =============================================================================
set -uo pipefail

usage() {
  sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
}

SPEC=""; PREFIX=""; WORK_DIR="."; SPLIT_BLOCKS=""; ALLOW_MISSING=0
PICKS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --spec)         SPEC="$2"; shift 2 ;;
    --prefix)       PREFIX="$2"; shift 2 ;;
    --work-dir)     WORK_DIR="$2"; shift 2 ;;
    --split-blocks) SPLIT_BLOCKS="$2"; shift 2 ;;
    --allow-missing) ALLOW_MISSING=1; shift ;;
    -h|--help)      usage ;;
    -*)             echo "[finish] 未知参数: $1" >&2; usage ;;
    *)              PICKS+=("$1"); shift ;;
  esac
done

[ -n "$SPEC" ]   || { echo "[finish] 缺少 --spec" >&2; usage; }
[ -n "$PREFIX" ] || { echo "[finish] 缺少 --prefix" >&2; usage; }
[ "${#PICKS[@]}" -gt 0 ] || { echo "[finish] 未提供任何 picks 文件" >&2; usage; }

SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
SPEC="$(readlink -f "$SPEC")"
mkdir -p "$WORK_DIR"; WORK_DIR="$(cd "$WORK_DIR" && pwd)"
PREFIX_IN="$PREFIX"
OUT_DIR="$(dirname "$PREFIX_IN")"; mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"
PREFIX="$OUT_DIR/$(basename "$PREFIX_IN")"

# ---- 定位解释器 ----
find_py() {
  for c in "$HOME"/.workbuddy/binaries/python/versions/*/python.exe \
           "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3; do
    [ -x "$c" ] && { echo "$c"; return 0; }
  done
  command -v python3 2>/dev/null || command -v python 2>/dev/null || true
}
PY="${PYTHON:-$(find_py)}"
[ -n "${PY:-}" ] || { echo "[finish] 未找到 Python 解释器。" >&2; exit 1; }

# selfcheck 需 python-docx → 用 html-to-docx venv 的解释器（与 to_docx.sh 同口径）
VENV="${H2D_VENV:-$HOME/.workbuddy/binaries/python/envs/html-to-docx}"
VPY="$VENV/Scripts/python.exe"; [ -x "$VPY" ] || VPY="$VENV/bin/python"
[ -x "$VPY" ] || VPY="$PY"

MERGED="$WORK_DIR/picks_merged.json"
GAP_SUMMARY="$WORK_DIR/_finish_gap.json"   # 内部产物，前缀 _finish_ 避免与用户的 picks 文件撞名
STATUS=0

echo "==================== [finish] 1/5 校验 ===================="
"$PY" "$SELF_DIR/validate_picks.py" --spec "$SPEC" --json-out "$GAP_SUMMARY" "${PICKS[@]}"
VRC=$?
if [ "$VRC" -ne 0 ] && [ "$ALLOW_MISSING" -eq 0 ]; then
  echo "[finish] ⚠️ 选题不完整（见上）。请只补 missing 题号后续跑（幂等），或加 --allow-missing 降级交付。" >&2
  exit 1
fi

echo "==================== [finish] 2/5 幂等合并 + 缺口 ===================="
"$PY" "$SELF_DIR/merge_and_gap.py" --spec "$SPEC" --existing "$MERGED" --out "$MERGED" "${PICKS[@]}"
MRC=$?
if [ "$MRC" -ne 0 ] && [ "$ALLOW_MISSING" -eq 0 ]; then
  echo "[finish] ⚠️ 仍有缺口（见上）。补齐后再跑，或加 --allow-missing 降级交付。" >&2
  exit 1
fi

echo "==================== [finish] 3/5 组装 ===================="
BUILD_ARGS=(--spec "$SPEC" --picks "$MERGED" --out-dir "$WORK_DIR")
[ -n "$SPLIT_BLOCKS" ] && BUILD_ARGS+=(--split-blocks "$SPLIT_BLOCKS")
[ "$ALLOW_MISSING" -eq 1 ] && BUILD_ARGS+=(--partial)
"$PY" "$SELF_DIR/build_questions.py" "${BUILD_ARGS[@]}"
BRC=$?
[ "$BRC" -eq 0 ] || { echo "[finish] ✗ 组装失败（退出码 $BRC）" >&2; exit 1; }

echo "==================== [finish] 4/5 排版导出 ===================="
if [ -n "$SPLIT_BLOCKS" ]; then
  # 分块重叠：分块转 docx + 缝合；细目表依赖全卷，单独渲染
  BLK=()
  for f in "$WORK_DIR"/questions_block*.json; do [ -f "$f" ] && BLK+=("$f"); done
  if [ "${#BLK[@]}" -gt 0 ]; then
    bash "$SELF_DIR/render_blocks.sh" "$PREFIX" "${BLK[@]}" || { echo "[finish] ✗ 分块渲染失败" >&2; exit 1; }
    "$PY" "$SELF_DIR/render_blueprint.py" "$WORK_DIR/blueprint.json" -o "${PREFIX}_细目表.html" || true
  else
    echo "[finish] 未找到 questions_block*.json，回退到常规一键渲染。" >&2
    bash "$SELF_DIR/render_all.sh" "$WORK_DIR/questions.json" "$WORK_DIR/blueprint.json" "$PREFIX" "$OUT_DIR" || { echo "[finish] ✗ 渲染失败" >&2; exit 1; }
  fi
else
  bash "$SELF_DIR/render_all.sh" "$WORK_DIR/questions.json" "$WORK_DIR/blueprint.json" "$PREFIX" "$OUT_DIR" || { echo "[finish] ✗ 渲染失败" >&2; exit 1; }
fi

echo "==================== [finish] 5/5 自检 ===================="
PAPER_DOCX="${PREFIX}_试卷.docx"
ANA_DOCX="${PREFIX}_解析.docx"
BP_HTML="${PREFIX}_细目表.html"
SC_ARGS=("$PAPER_DOCX" "$ANA_DOCX" --questions "$WORK_DIR/questions.json")
[ -f "$BP_HTML" ] && SC_ARGS+=(--blueprint "$BP_HTML")
"$VPY" "$SELF_DIR/selfcheck_paper.py" "${SC_ARGS[@]}" || STATUS=3

echo ""
echo "==================== [finish] 完成 ===================="
echo "  试卷   : $PAPER_DOCX"
echo "  解析   : $ANA_DOCX"
echo "  细目表 : $BP_HTML"
echo "  中间件 : $WORK_DIR/questions.json  $WORK_DIR/blueprint.json  $MERGED"
if [ "$STATUS" -eq 3 ]; then
  echo "  ⚠️ 自检未通过——产物已生成，请人工核对（退出码 3）。" >&2
  exit 3
fi
if [ "$ALLOW_MISSING" -eq 1 ] && { [ "$VRC" -ne 0 ] || [ "$MRC" -ne 0 ]; }; then
  echo "  ⚠️ 降级交付：存在缺口（missing 见上方 / $GAP_SUMMARY）。退出码 2。"
  exit 2
fi
echo "  ✅ 三件套齐全且自检通过。"
exit 0
