#!/usr/bin/env bash
# =============================================================================
# AI 组卷 · HTML → 自包含 .docx 导出
#
# 用法:
#   bash to_docx.sh <input.html> <output.docx> [额外的 html_to_docx convert 参数...]
#
# 特性:
#   - 自动定位 tencent-docx 插件里的 html-to-docx 转换器
#   - 依赖缺失时自动创建隔离 venv 并安装
#   - 页边距按《试卷与解析排版标准》显式传参（上下 2.5cm / 左右 2.0cm）
#     —— 转换器不读 CSS @page，默认左右 3.17cm，必须显式指定
#   - 转换时自动下载并内嵌远程题图（产物自包含）
# =============================================================================
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "用法: bash to_docx.sh <input.html> <output.docx> [额外参数...]" >&2
  exit 2
fi
IN="$1"; OUT="$2"; shift 2

# 统一转绝对路径（脚本中途会 cd 到转换器目录，相对路径会失效）
IN="$(readlink -f "$IN" 2>/dev/null || echo "$IN")"
OUT_DIR="$(dirname "$OUT")"; mkdir -p "$OUT_DIR"
OUT="$(cd "$OUT_DIR" && pwd)/$(basename "$OUT")"

# 1) 定位 html-to-docx 转换器
PLUGIN="$(ls -d "$HOME"/.workbuddy/plugins/cache/*/tencent-docx/*/ 2>/dev/null | head -1 || true)"
if [ -z "${PLUGIN:-}" ]; then
  echo "[to_docx] 未找到 tencent-docx 插件（html-to-docx 转换器）。" >&2
  echo "          请确认已安装 tencent-docx 技能/插件。" >&2
  exit 1
fi
SCRIPTS="$PLUGIN/skills/html-to-docx/scripts"
[ -d "$SCRIPTS" ] || { echo "[to_docx] 未找到转换器目录: $SCRIPTS" >&2; exit 1; }
[ -f "$SCRIPTS/html_to_docx/__main__.py" ] || { echo "[to_docx] 转换器包缺失: $SCRIPTS/html_to_docx" >&2; exit 1; }
REQ="$SCRIPTS/requirements.txt"

# 2) 定位一个可用的 Python
find_py() {
  for c in "$HOME"/.workbuddy/binaries/python/versions/*/python.exe \
           "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3 \
           "$HOME"/.workbuddy/binaries/python/versions/*/bin/python; do
    [ -x "$c" ] && { echo "$c"; return 0; }
  done
  command -v python3 2>/dev/null || command -v python 2>/dev/null || true
}
PY="${PYTHON:-$(find_py)}"
[ -n "${PY:-}" ] || { echo "[to_docx] 未找到 Python 解释器。" >&2; exit 1; }

# 3) 准备隔离 venv（放在托管目录，不污染用户环境）
# 注意：html_to_docx 是转换器目录内的本地包（用 `cd $SCRIPTS && python -m html_to_docx` 运行），
#       不安装进 venv，故就绪检查只看第三方依赖是否齐。
VENV="${H2D_VENV:-$HOME/.workbuddy/binaries/python/envs/html-to-docx}"
VPY="$VENV/Scripts/python.exe"; [ -x "$VPY" ] || VPY="$VENV/bin/python"
need_install=1
if [ -x "$VPY" ] && \
   "$VPY" -c "import click, docx, lxml, PIL, httpx, bs4" >/dev/null 2>&1; then
  need_install=0
fi
if [ "$need_install" -eq 1 ]; then
  echo "[to_docx] 准备转换依赖（首次运行，稍候）…"
  rm -rf "$VENV"
  "$PY" -m venv "$VENV"
  VPY="$VENV/Scripts/python.exe"; [ -x "$VPY" ] || VPY="$VENV/bin/python"
  "$VPY" -m pip install -q --upgrade pip
  "$VPY" -m pip install -q --only-binary=:all: -r "$REQ"
fi

# 4) 转换（页边距显式传参）
cd "$SCRIPTS"
"$VPY" -m html_to_docx convert "$IN" -o "$OUT" --page-size A4 \
  --margin-top 2.5 --margin-bottom 2.5 --margin-left 2.0 --margin-right 2.0 "$@"

# 5) 后处理：补「题号悬挂缩进」
# 转换器忽略负 text-indent，CSS 的悬挂只能落成 w:ind left；此处就地补 w:hanging，
# 使首行回退到页边距、续行缩进 13.65pt，符合《试卷与解析排版标准》§6-1。
SELF_DIR="$(cd "$(dirname "$0")" && pwd)"
FIX="$SELF_DIR/fix_hanging_indent.py"
if [ -f "$FIX" ]; then
  "$VPY" "$FIX" "$OUT" 273
fi

# 6) 后处理：补「解析区强制分页」
# 转换器完全不支持任何 HTML/CSS 分页写法（实测 6 种探针全失效），必须走转换后
# XML 后处理。锚文本默认「参考答案与试题解析」，与 render_paper/render_similar
# 产出的解析区标题（{title}<br />参考答案与试题解析）一致；可通过
# H2D_PAGEBREAK_ANCHOR 环境变量覆盖（例如只需对特定卷种分页时）。
FIXPB="$SELF_DIR/fix_page_break.py"
if [ -f "$FIXPB" ]; then
  ANCHOR="${H2D_PAGEBREAK_ANCHOR:-参考答案与试题解析}"
  "$VPY" "$FIXPB" "$OUT" "$ANCHOR" || true
fi

echo "[to_docx] 已生成: $OUT"
