# 安装与可用性检查

## 什么时候读取

命令不可用、版本不确定、用户刚安装、全局命令可能指向旧版本，或需要确认当前安装包含哪些 Agent Skill 时读取本文件。

## 检查命令

```text
weaver-work-cli --version
weaver-work-cli setup invoice
weaver-work-cli doctor --e10
weaver-work-cli skills list
```

`weaver-work-cli skills list` 只证明包内 Skill 文件可读，不证明业务 API 可用；E10 登录态和 live API 仍需按业务命令实际验证。

## 命令找不到（退出码 127）：先区分「未安装」与「已安装但不在 PATH」

`weaver-work-cli --version` 报 `command not found` 或退出码 127 时，**不要直接判定为未安装并重装**。CLI 可能已安装在非默认 npm 前缀下，只是当前 shell 的 PATH 未包含全局 bin 目录。按顺序处理：

1. 定位全局 bin 目录（macOS/Linux bash/zsh）：

```bash
npm prefix -g
npm bin -g 2>/dev/null || echo "$(npm prefix -g)/bin"
ls "$(npm prefix -g)/bin" | grep -i weaver
```

Windows PowerShell：

```powershell
npm prefix -g
Get-ChildItem "$(npm prefix -g)" -Filter "weaver-work-cli*" -Recurse -Depth 1 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
```

2. 若能在全局 bin 目录中找到 `weaver-work-cli`，先把它前置到 PATH 再验证，**不要安装**：

macOS/Linux（bash/zsh）：

```bash
export PATH="$(npm prefix -g)/bin:$PATH"
weaver-work-cli --version
```

Windows PowerShell：

```powershell
$env:Path = "$(npm prefix -g);$env:Path"
weaver-work-cli --version
```

PATH 前置后仍不可用，或全局 bin 目录里根本没有 `weaver-work-cli`，才判定为「未安装」，进入下一节的来源选择流程。

3. 沙箱/容器环境里若 PATH 前置仍失败，按 [`non-interactive-environment.md`](non-interactive-environment.md) 收尾：记录退出码与耗时并反馈，不自动执行全局安装。

## Agent 自动安装运行时

当 `weaver-work-cli --version` 失败或用户要求代装时，Agent 先让用户选择来源；未同意前不改全局 npm 环境。

建议提示词：

```text
未检测到 weaver-work-cli。是否安装运行时？
请选择：1. npm 源安装（可填 registry）；2. 本地代码安装（需仓库绝对路径）。
```

用户选 npm 源安装后执行；如提供 registry，把安装命令换成 `npm install -g weaver-work-cli --registry "<NPM_REGISTRY_URL>"`：

```text
node --version
npm --version
npm install -g weaver-work-cli
weaver-work-cli --version
```

用户选本地代码安装时，先取得仓库绝对路径并确认有 `package.json`；路径缺失或错误时先追问。

Windows PowerShell：

```powershell
$WeaverWorkCliRoot = "C:\path\to\weaver-work-cli"
if (-not (Test-Path "$WeaverWorkCliRoot\package.json")) { throw "invalid weaver-work-cli path" }
Set-Location $WeaverWorkCliRoot
npm install
npm run build
npm link
weaver-work-cli --version
```

macOS/Linux（bash/zsh）：

```bash
WEAVER_WORK_CLI_ROOT="/path/to/weaver-work-cli"
test -f "$WEAVER_WORK_CLI_ROOT/package.json" || exit 1
cd "$WEAVER_WORK_CLI_ROOT"
npm install
npm run build
npm link
weaver-work-cli --version
```

权限错误时停止并报告，不自动加 `sudo`。

## 本地构建验证

如果怀疑全局 `weaver-work-cli` 仍是旧版本，在仓库内直接调用当前构建产物：

```text
node dist/index.js --version
node dist/index.js commands list
node dist/index.js skills list
```

## 推荐交付模式

`weaver-work-cli` 发布包是唯一必须安装的运行时，包含 CLI 命令、E10 鉴权、
发票业务 operation 和随包 Agent Skill 文档。普通用户通过组织认可的包管理器来源安装后即可使用：

```text
weaver-work-cli setup invoice
weaver-work-cli auth login --base-url "<E10_BASE_URL>" --agent_type "<当前智能体名称>"
weaver-work-cli invoice schema
```

如果当前环境需要让 Codex/Agent 直接加载发票 Skill，优先使用随包一键安装：

```text
weaver-work-cli skills install yepiaotong
```

该命令会同时安装 `weaver-e10-shared` 和 `weaver-e10-yepiaotong` 到
环境变量 `CODEX_HOME` 下的 `skills` 子目录；未设置 `CODEX_HOME` 时使用用户主目录下的 `.codex/skills`
（Windows PowerShell：`$env:USERPROFILE\.codex\skills`；macOS/Linux：`$HOME/.codex/skills`）。默认目标
面向 Codex CLI；WorkBuddy 等桌面 Agent 的用户级 Skill 目录不是默认目标，需
显式指定后再安装（目标目录位置以对应 Agent 的官方文档为准）：

```bash
weaver-work-cli skills install yepiaotong --target-dir "<目标 Agent 的用户级技能目录>"
```

`skills install` 是拷贝语义，装出的是真实副本，不与源目录联动。目标目录里
已有旧条目（旧副本或软链）时不能直接覆盖：目标是软链会报
`ERR_FS_CP_DIR_TO_NON_DIR`，Windows 用 `Remove-Item -Recurse -Force`、macOS/Linux 用 `rm -rf` 断链再安装；覆盖安装不会清理目标里已
不存在的旧文件。安装只是文件拷贝，不需要 E10 登录；Agent 需新会话或重载
Skill 后才读取新内容。完整安装/升级流程见仓库 `docs/agent-skill-install.md`。

交付给 Agent 的 Skill ZIP 不内置运行时，只声明依赖本机可用的 `weaver-work-cli`
bin。ZIP 主要用于平台导入、离线分发或版本归档，不应作为普通用户的必经安装步骤。
