# 采知连：明确不提供的能力（withheld）与源 Skill 范围外模块

## 何时使用

- 用户要求「列一下有哪些环境 / 看看当前配置 / 重新加载配置 / 切换到测试环境」这类源 Skill 的系统管理能力。
- 用户拿着源 Skill（`weaver-e10-caizhilian` 1.1.17）的 operation 名来调用，但 CLI 里没有对应 operation。
- `caizhilian operations` 的 `withheldOperations` 里给出了名称与理由，需要向用户解释替代方案。

## 输入要点

### 4 个 withheld 系统操作

源 `scripts/system_plugins.py` 的这 4 个插件**没有**转换成 CLI operation。原因都是同一个：它们操作的是源 Skill 自带的 `assets/config.json` 多环境配置与本地登录态缓存，而在 weaver-work-cli 里，环境、配置与登录态由框架统一管理，业务模块不得自建一套。

| 源 operation |  withheld 名称 | 不提供的原因 | 替代命令 |
| --- | --- | --- | --- |
| `list_systems` | `caizhilian.system.list-systems` | 读取 Skill 自带 config.json 的多环境列表与登录态 | `weaver-work-cli config list`、`weaver-work-cli e10 auth status`；连通性自检用 `weaver-work-cli --json caizhilian health` |
| `get_loaded_config` | `caizhilian.system.get-loaded-config` | 输出 Skill 本地配置生效内容（含 cookies 掩码、下载目录） | `weaver-work-cli config list`；不在业务模块内暴露配置快照 |
| `reload_config` | `caizhilian.system.reload-config` | 重新加载 Skill 本地 config.json | 无需替代：CLI 每次进程启动即读取框架配置，没有进程内缓存需要刷新 |
| `switch_config` | `caizhilian.system.switch-config` | 在 Skill 本地多套环境配置间切换 | `weaver-work-cli config set ...`、`weaver-work-cli e10 auth login --base-url <域名>` |

只保留了 `caizhilian.system.health`（源 `check_system_health`）：探测 `/api/doc/config/getUserConfiguration?configKeys`，返回 `{ environment, healthy, base_url, url, status_code, business_code, diagnosis, elapsed_ms }`，其中 `environment.provider` 固定为 `weaver-work-cli:e10-auth`；本地无登录态时抛 `authentication/session_unavailable`。

### 源 Skill 目录内的已补充模块

以下模块已补充到 caizhilian CLI 中：

| 源模块 | CLI 操作 | 说明 |
| --- | --- | --- |
| 系统设置-附件 | `caizhilian.setting-attach.get` / `.set.prepare` / `.set.apply` | 附件全局设置（上传最大、格式控制、批量下载等 11 项） |
| 系统设置-备份 | `caizhilian.setting-backup.get` / `.set.prepare` / `.set.apply` / `.rule.*` | 备份设置（开关、规则 CRUD、启停） |
| 系统设置-加密 | `caizhilian.setting-encrypt.get` / `.set.prepare` / `.set.apply` | 加解密设置（8 项配置） |
| 系统设置-存储 | `caizhilian.setting-storage.instance.*` / `.rule.*` | 存储实例与规则管理 |
| 文件收集 | `caizhilian.file-collection.task.*` / `.scan.*` / `.run.*` / `.cancel.*` / `.delete.*` | FTP/SFTP 文件采集任务管理 |
| 文件上传 | `caizhilian.file-upload.contract` / `.prepare` / `.upload.prepare` / `.upload.apply` | 本地文件上传到文件服务 |

### 源基础设施脚本的处理方式

源的通用基础设施不是业务 operation，已按 weaver-work-cli 的框架能力**等价替换**，不单独暴露：

| 源文件 | 处理方式 |
| --- | --- |
| `scripts/cli.py`、`scripts/engine.py`、`scripts/plugin_base.py` | 由 `src/shortcuts/caizhilian/index.ts` + `operations/registry.ts` 承担（命令注册、operation 分派、prepare/apply 展开） |
| `scripts/http_client.py` | 由 `src/shortcuts/caizhilian/host.ts` + 框架 E10 HTTP client 承担（Cookie/ETEAMSID/User-Agent 注入、超时、重试、下载流处理） |
| `scripts/_session_helper.py`、`scripts/environment_provider.py`、`scripts/cache_manager.py`、`.cache/` | 由框架登录态管理承担（`weaver-work-cli e10 auth ...`）；业务模块不读写登录缓存 |
| `scripts/_utils.py`、`scripts/_plugin_helpers.py` | 直译进 `operations/shared.ts`、`operations/files.ts`、`operations/api.ts`（文件元数据、上传下载、Python 语义小工具） |
| `scripts/response_templates.py` | 输出归一逻辑直译进各 handler（`users[]` / `departments[]` / `documents[]` 等键名与字段） |
| `scripts/reply_lint.py`、`scripts/collection_lint_skill.py` | 属于源 Skill 的回复与 Skill 自检工具，不在业务 CLI 范围 |
| `doc-business-orchestrations/*.json` | 编排建议已落进各 reference 的「典型链路」，不作为可执行 operation 暴露 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli caizhilian operations
weaver-work-cli --json caizhilian health
weaver-work-cli config list
weaver-work-cli e10 auth status
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli caizhilian operations
weaver-work-cli --json caizhilian health
weaver-work-cli config list
weaver-work-cli e10 auth status
```

`caizhilian operations` 的返回里带 `withheldOperations`，每项是 `{ name, reason }`，可以直接把 `reason` 转述给用户。

## 输出处理

- 用户点名要 withheld 能力时：**不要报「做不到」就结束**，要给出上表里的替代命令，并说明「环境与登录态由 weaver-work-cli 框架统一管理」。
- 用户拿源 operation 名（如 `create_html_document`、`search_documents`）来调用时，用 `caizhilian operations` 的 `sourceOperation` 字段反查 CLI operation 名（如 `caizhilian.document.create-html.prepare` / `.apply`），再按 `write-protocol.md` 走确认链。
- `caizhilian health` 的 `diagnosis` 字段是逗号分隔的判定项：`ok`、`network_error`、`http_error`、`http_status_mismatch`、`business_code_mismatch`、`request_failed`。非 `ok` 时把 `status_code`、`business_code`、`elapsed_ms` 一起给用户。

## 注意

- 不要为了让用户满意而**临时补出** withheld 操作，也不要用 curl / 脚本绕过 CLI 去读框架配置或登录态。
- 不要读取、列出、打印或解析 CLI runtime 内部的登录凭据文件；认证相关一律通过 `weaver-work-cli auth` / `weaver-work-cli e10 auth` 命令。
- 源 Skill 范围外模块的能力**不要**用 caizhilian 的 operation 去近似模拟（例如用附件上传去替代「附件全局设置」）。
- 如果用户确实需要范围外模块，回复「需要按 skill-maker 单独生成对应模块 CLI 与 Skill」，不要在本模块里扩权。

## 失败处理

| error.type / subtype | 触发场景 | 处理 |
| --- | --- | --- |
| `validation/operation_unknown` | 调用了 withheld 或范围外的 operation 名 | 用 `caizhilian operations` 校对，按本文件的替代命令回复用户 |
| `authentication/session_unavailable` | `caizhilian health` 时本地无登录态 | 引导用户执行 `weaver-work-cli e10 auth login`，不要猜域名 |
| `api/http_error` / `api/business_error` | health 探测返回非成功码 | 把 `diagnosis`、`status_code`、`business_code` 交给用户 |
| `network/*` | health 探测网络失败 | `retryable=true` 时最多重试一次 |