# E10 认证与会话

## 什么时候读取

用户需要登录、切换 profile、诊断 E10 连接、处理登录失效，或任务涉及 `base-url`、auth 文件、Keychain、`WEAVER_*` 环境变量时读取本文件。
当当前智能体身份明确为 XiaoE，且认证流程涉及 `XIAOE_*` 环境变量或 `xiaoeUserData/tokens.py` 时也读取本文件。成对的平台凭据，或桌面客户端精确注入的 `XIAOE_DATA_ROOT` / `XIAOE_ROBOT_DATA_ROOT` / `XIAOE_USER_SETTINGS_PATH` / `XIAOE_ROBOT_ROOT` 可标识 XiaoE 宿主；仅本机存在脚本、客户端目录、`XIAOE_SKILL_*` 或 `WEAVER_XIAOE_*` 配置不能据此判定。

## 基本检查

```text
weaver-work-cli auth status --no-check
weaver-work-cli auth whoami
```

`--no-check` 只读取本地登录态；需要实际验证服务端可用性时使用业务命令或明确带 live 校验的命令。

## 认证隔离与禁止探查旧目录

`weaver-work-cli auth root` 是唯一用于确认本 CLI 认证根目录的命令；默认根目录位于用户主目录下的 `.weaver-work-cli/e10`（Windows PowerShell：`$env:USERPROFILE\.weaver-work-cli\e10`；macOS/Linux：`$HOME/.weaver-work-cli/e10`）。Agent 不得因为历史兼容信息去读取、列出、打印或解析用户主目录下的旧 `.e10-cli`，也不得探查 `e10-login` / `e10-cli` 的 auth、config 或 Keychain 数据。

登录态判断只允许通过 `weaver-work-cli auth status --no-check`、`weaver-work-cli auth profile list/current`、`weaver-work-cli doctor --e10` 和业务命令返回的 JSON 错误完成。只有用户明确提供外部 auth 文件路径时，才可按用户要求使用 `--auth <path>` 或 `E10_AUTH_PATH`；不能主动搜索旧认证目录。

## 未登录 / 登录失效：仅 XiaoE 智能体自动尝试统一登录

业务命令依赖 E10 登录态。出现以下任一情况即判定为未登录或登录失效：

- `weaver-work-cli auth status` 输出 `loggedIn: false`，或本地不存在 auth 文件
- `weaver-work-cli doctor --e10` 的 `e10AuthFile` 检查为 `ok: false`
- 业务命令失败，stderr JSON 中 `error.type === "authentication"`（如 `E10 auth not found`）
- 业务命令返回 `error.subtype === "session_expired"`（E10 登录态 401/302 失效）

此时**禁止**：

- 使用示例占位域名（如 `https://weapp.xxx.cn`）或自行猜测域名执行登录
- 未向用户确认登录域名前，反复重试业务命令
- 要求用户提供 Cookie、ETEAMSID、业务 Token（见安全边界）
- 读取、列出、打印或解析用户主目录下的旧 `.e10-cli`、`e10-login` / `e10-cli` 的历史 auth、config 或 Keychain 数据

**正确流程（按序执行，缺一不可）：**

0. **仅 XiaoE 智能体环境优先自动尝试统一登录**：只有宿主/任务上下文明确标识当前智能体为 XiaoE、当前命令进程收到 XiaoE 按次注入的成对平台凭据，或收到桌面 XiaoE 精确注入的运行时路径标记时，才运行：
   ```text
   weaver-work-cli auth xiaoe
   ```
   本机存在 `xiaoeUserData/tokens.py`、XiaoE 客户端目录、`XIAOE_SKILL_*` 或 `WEAVER_XIAOE_*` 配置都只表示“凭据可能可用”，不表示“当前智能体是 XiaoE”。桌面 XiaoE 的精确宿主标记是 `XIAOE_DATA_ROOT`、`XIAOE_ROBOT_DATA_ROOT`、`XIAOE_USER_SETTINGS_PATH`、`XIAOE_ROBOT_ROOT`。通用 `WORKBUDDY_*` / `CODEX_*` 运行时变量也可能存在于 XiaoE 进程中，不能覆盖成对的平台凭据或上述桌面标记；明确的 `WORKBUDDY_AGENT_TYPE` / `CODEX_AGENT_TYPE` 非 XiaoE 身份除外。WorkBuddy、Codex 及其他智能体必须跳过此步，进入下方浏览器 OAuth 流程。
   CLI 会按“显式 `--base-url` → 专用 `WEAVER_XIAOE_*` E10 配置/映射 → 当前 profile `config.baseUrl` → CLI 内置默认值”解析 E10 登录域名；`XIAOE_DOMAIN` 只作为 XiaoE/erpa 换票服务地址。业务命令在未显式指定 `--auth` / `--profile` 时，也会自动优先尝试这一步。若凭证有效，会直接保存登录态，`agentType` 固定为 `XiaoE`，然后继续原业务操作。若 Web/Linux 返回 `authentication/xiaoe_web_credential_unavailable`，反馈宿主登录态/凭据注入异常后停止，不要自动进入下方浏览器流程，也不要要求用户去本地终端重复登录。Agent 不得因为本地存在旧 profile 就跳过统一登录，也不得要求用户提供或展示 `XIAOE_*` / ETEAMSID。

1. **先调用宿主提供的提问 / 弹框能力询问用户**，让用户二选一：
   - 输入本次要登录的 E10 登录域名（base URL），形如 `https://<企业域名>`；或
   - 从已有 profile 中选择一个已登录环境：先运行 `weaver-work-cli auth profile list` 列出候选，让用户选择。
2. 用户提供了**新域名**时，用真实域名执行浏览器 OAuth 登录：
   ```text
   weaver-work-cli auth login --base-url "<用户输入的域名>" --agent_type "<当前智能体名称>"
   ```
   端口冲突时加 `--port 19801`。
3. 用户选择了**已有 profile** 时，切换后验证登录态：
   ```text
   weaver-work-cli auth profile use PROFILE_NAME
   weaver-work-cli auth status
   ```
4. 登录成功后再继续原业务操作。仍失败时，把 `error.type/subtype/message` 原样反馈给用户并停止，不要自动重试。

登录域名一律以用户实际提供为准；拿不到域名前，不要执行任何依赖登录态的业务命令。

## 浏览器 OAuth 防挂起

`auth login`（以及 macOS/Windows 桌面宿主上的 `auth xiaoe` 降级）会在本机 `127.0.0.1:19800` 监听浏览器回调，最长等待 5 分钟。Agent 沙箱/托管环境中的外部浏览器无法回调容器内地址。执行规则：

1. Web/Linux 中运行 `auth xiaoe` 时，收到 `xiaoe_web_credential_unavailable` 即反馈并停止；不要自动改跑 `auth login`。
2. 只有用户明确要求浏览器授权且确认 CLI 与浏览器同机时，才执行 `auth login`；仍须限时等待，超时未完成即终止并反馈。
3. 用户无法本地执行浏览器登录时，经用户明确同意后改用保底方式 `weaver-work-cli auth set --eteamsid "<ETEAMSID>" --base-url "<用户确认的登录域名>"`，由用户从已登录浏览器主动提供 ETEAMSID；Agent 不得索取、展示或转述该值。
4. 严禁不加限制地前台运行 `auth xiaoe` / `auth login` 并等待 OAuth 回调。

## 登录

先取得用户确认的登录域名（见上节流程），再让用户通过浏览器 OAuth 登录：

```text
weaver-work-cli auth login --base-url "<用户确认的登录域名>" --agent_type "<当前智能体名称>"
```

`auth login` / `auth oidc` 是严格的浏览器 OAuth 入口，不会因为本机可发现 XiaoE 凭据、脚本或客户端文件而改走 XiaoE 统一登录。

在 XiaoE 宿主环境中，`auth xiaoe` 先使用平台注入的 `XIAOE_USER_TOKEN` + `XIAOE_DOMAIN` 换取 ETEAMSID（沙箱唯一可用来源）：先走 Node 主路径，失败后由 CLI npm 包自带的 `scripts/xiaoe_env.py` 作标准库兼容回退；拿不到时再读宿主 `xiaoeUserData/tokens.py` 的 stdout JSON（仅桌面宿主），再退回内置原生实现读取桌面 XiaoE 客户端会话（优先 `XIAOE_USER_SETTINGS_PATH`，其次 `XIAOE_ROBOT_DATA_ROOT` / `XIAOE_ROBOT_ROOT`，最后默认 `XiaoE/Robots/<id>/user_settings.json`，不需要 `tokens.py` 或本机 Python）；仍未识别到可用凭证时，才读取 `WEAVER_XIAOE_*` 环境变量里的“当前登录域名 -> ETEAMSID”统一登录映射，并且保存的 `agentType` 固定为 `XiaoE`。`XIAOE_DOMAIN` 是 XiaoE/erpa 换票服务地址，不能作为 E10 地址；E10 目标按“显式 `--base-url` → 专用 `WEAVER_XIAOE_*` E10 配置/映射 → 当前 profile → CLI 内置默认值”解析。Node 和 Python 兼容路径都校验业务码及 `data.eteamId`，保留系统 CA 校验，只允许同源重定向或同主机 HTTP→HTTPS 升级。统一登录失败时，Web/Linux 返回 `authentication/xiaoe_web_credential_unavailable`，不自动启动 localhost 浏览器 OAuth；macOS/Windows 桌面宿主才允许自动降级。

需要显式表达“XiaoE 优先”的场景也可以使用等价入口：

```text
weaver-work-cli auth xiaoe
```

该命令先尝试 XiaoE 统一登录；统一登录不可用时先反馈原因。Web/Linux 环境直接结束并返回结构化错误，不自动切换浏览器 OAuth；macOS/Windows 桌面宿主可以继续降级。用户明确切换域名时再追加 `--base-url "<用户确认的登录域名>"`。

命令首先输出不含凭证的 preflight 摘要：`hostDetected` 表示是否识别为 XiaoE 宿主，`attempted` 表示是否实际进入统一登录链路，`tokenScriptDetected` 表示是否发现宿主脚本，`clientSettingsDetected` 表示是否发现可供 Node 换票的桌面会话文件。脚本分支开始时会打印 `Trying XiaoE token script credential...`，Node 会话分支开始时会打印 `Trying built-in XiaoE client session credential...`。成功结果及后续 `auth status` 的 `credentialSourceStep=2`、`credentialSourceType=token_script`、`credentialSourceLabel=xiaoeUserData/tokens.py` 可确认脚本换票已完成；`credentialSourceStep=3`、`credentialSourceType=xiaoe_client`、`credentialSourceLabel=XiaoE client settings` 表示未依赖 `tokens.py`、由 Node 直接换票。

如果端口冲突：

```text
weaver-work-cli auth login --base-url "<用户确认的登录域名>" --agent_type "<当前智能体名称>" --port 19801
```

`<当前智能体名称>` 使用发起登录验证的宿主标识，例如 WorkBuddy 传 `workbuddy`，Codex 传 `codex`。CLI 会把该值同时写入 E10 授权 URL 的 `agent_type` 和 `from` 参数，其中 `from` 用于授权确认页的客户端名称展示。如果宿主无法确认名称，才允许省略 `--agent_type`；CLI 会尝试从 `WEAVER_AGENT_TYPE`、`WORKBUDDY_AGENT_TYPE`、`CODEX_AGENT_TYPE` 以及 `WORKBUDDY_*` / `CODEX_*` 环境变量推断，最后回落为 `weaver-work-cli`。

授权成功后，本地回调页会为已识别的桌面智能体显示应用打开弹层。CLI 内置 WorkBuddy
（`workbuddy://`）、智能小 E（`xiaoe-client://`）和 Codex（`codex://`）映射；其他
智能体在 `agent_type` 本身是合法协议名时，默认按 `<agent_type>://` 唤起。Windows/macOS
安装包都需要注册对应协议。用户确认后，页面以
一次性令牌请求本地 CLI，由 CLI 调用系统协议处理器，避免浏览器直接访问自定义协议时
出现不可定制的 Chrome/Edge 原生确认框；宿主需要返回当前会话等精确位置时，
可在执行登录命令时增加 `--agent-return-url "<宿主提供的自定义协议 URL>"`，或注入
`WEAVER_AGENT_RETURN_URL`。客户端协议名与 `agent_type` 不一致时也应使用该覆盖。返回
地址只接受桌面应用自定义协议；不要传网页、脚本或
本地文件 URL。“始终打开”偏好保存在当前本地回调地址的浏览器存储中；未识别到返回协议
时，页面只提示用户手动返回智能体或终端。本地 CLI 打开通道默认保留 15 分钟；通道结束
后页面会自动退回浏览器自定义协议打开方式，不直接显示网络请求错误。
智能小 E 统一登录成功时不会经过浏览器；只有统一登录不可用并降级为桌面浏览器 OAuth 时，
才显示“返回智能小 E”弹层。

保底方式是让用户手动写入浏览器中的 `ETEAMSID`：

```text
weaver-work-cli auth set --eteamsid "PCACCOUNT_xxx" --base-url "<用户确认的登录域名>" --agent_type "<当前智能体名称>"
```

## Profile 与环境

```text
weaver-work-cli auth profile list
weaver-work-cli auth profile current
weaver-work-cli auth profile use PROFILE_NAME
weaver-work-cli --profile PROFILE_NAME auth status --no-check
```

通过 `weaver-work-cli run` 执行外部命令时，CLI 会按当前 profile 注入 `WEAVER_BASE_URL`、`WEAVER_ETEAMSID`、`WEAVER_COOKIE`、`WEAVER_USER_AGENT` 和 `WEAVER_AGENT_TYPE`。这些值只给子进程使用，不应在回复或日志中明文展示。

`XIAOE_*` 是平台保留前缀，只由宿主注入给 CLI 消费（`XIAOE_DOMAIN` 是 XiaoE/erpa 换票服务地址、`XIAOE_USER_TOKEN` 是业务凭据，均按次注入；`XIAOE_SKILL_*` 为包内目录变量）。本 CLI 自己的宿主集成变量使用自有前缀 `WEAVER_XIAOE_*`，例如 `WEAVER_XIAOE_AUTH_MAP`（JSON 域名映射）、`WEAVER_XIAOE_E10_BASE_URL`（E10 目标地址）、`WEAVER_XIAOE_TOKEN_SCRIPT_PATH`/`WEAVER_XIAOE_TOKEN_SCRIPT_PYTHON`（指定宿主 `tokens.py` 及解释器）、`WEAVER_XIAOE_DEFAULT_DOMAIN`（默认域名）；旧名 `XIAOE_E10_AUTH_MAP`、`XIAOE_TOKEN_SCRIPT_PATH` 等仅作兼容别名，新集成一律用 `WEAVER_XIAOE_*`。

宿主不会注入 ETEAMSID 环境变量，CLI 也不读取 `XIAOE_ETEAMSID`；ETEAMSID 一律由登录链路换取。CLI 支持两类宿主格式：平台注入的 `XIAOE_DOMAIN` + `XIAOE_USER_TOKEN`，以及 `WEAVER_XIAOE_*` 域名映射。这些格式属于宿主集成细节，不作为用户操作步骤；Agent 不要打印、转述、要求用户手动填写或将其导出到当前 shell。

## XiaoE 凭据由 CLI 独占处理

`auth xiaoe` 或业务命令触发统一登录时，CLI 按以下顺序自行取凭据，Agent **不参与、也不得复现**：

1. **平台注入凭据**：`XIAOE_USER_TOKEN` + `XIAOE_DOMAIN`（小 e 业务服务地址）。先由 Node 直接换票；失败时 CLI 可调用 npm 包自带的 `scripts/xiaoe_env.py` 兼容换票。脚本不属于 Skill，由 CLI 内部执行、解析并隐藏凭证 stdout。
2. **宿主 `tokens.py`**：桌面宿主 `xiaoeUserData/tokens.py`（macOS `~/Library/Application Support/xiaoeUserData/tokens.py`，Windows `%LOCALAPPDATA%\xiaoeUserData\tokens.py`）；CLI 在 macOS 应用包与 Windows 按用户/全局安装目录中自动查找 XiaoE 客户端内置 Python，并优先用它执行脚本；可用 `WEAVER_XIAOE_TOKEN_SCRIPT_PATH` 指定脚本路径，用 `WEAVER_XIAOE_TOKEN_SCRIPT_PYTHON` 指定解释器。
3. **桌面 XiaoE 客户端会话**：优先读取 `XIAOE_USER_SETTINGS_PATH`，其次从 `XIAOE_ROBOT_DATA_ROOT` / `XIAOE_ROBOT_ROOT` 查找，最后回退 `XiaoE/Robots/<id>/user_settings.json`；其中的 `session_id` + `erpa` 由 CLI 内置 Node 实现换取 `eteamId`，不需要宿主 `tokens.py` 或本机 Python。
4. **`WEAVER_XIAOE_*` 环境映射**：当前登录域名到 ETEAMSID 的映射。

Agent 禁止自行执行 `tokens.py`、`xiaoe_env.py` 或任何取 Token 脚本（其 stdout 含 ETEAMSID/Cookie/Token，会进入对话与日志），也禁止把这些脚本放入 shared Skill；禁止 `eval` / `Invoke-Expression` `auth export-weaver-env` 的输出，也禁止要求用户粘贴或展示任何凭证。脚本不存在、Python 依赖缺失、stdout 非法或接口失败，都由 CLI 内部记录并降级；Agent 只需把 CLI 反馈的原因转述给用户，不猜测或伪造 Token。

## 安全边界

Agent 不要要求用户贴 Cookie、ETEAMSID、业务 Token、app key 或 app secret，也不要直接读取用户机器上的 auth、config 或 Keychain 数据。业务 Skill 只负责调用 CLI；登录态读取、Cookie 拼接、业务 Token 获取和 HTTP header 注入都由 `weaver-work-cli` 内部完成。
