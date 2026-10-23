# WorkBuddy Connector 鉴权恢复

本文件规定业务调用失败后的鉴权恢复：由 Skill 在当前前台进程执行一次登录命令，让 CLI 打开系统默认浏览器并等待授权。安装、升级和断开连接仍由 WorkBuddy Connector 控制面负责。

## 可触发恢复的证据

- CLI JSON envelope 明确为 `error.code=AUTH_REQUIRED|AUTH_EXPIRED|CREDENTIAL_MISSING`，第一层 `code=NEED_BOSS_AUTH_ADMIN|NEED_BOSS_AUTH_NOT_ADMIN`，或机器可读 HTTP 状态明确为 401。
- `config_error`、`auth_center_not_configured`、`credential_store_error` 属于本地控制面错误，停止并展示安全摘要，不自行修改配置目录或凭证存储。
- HTTP 403 只有在第一层 `code` 未命中 `NEED_BOSS_AUTH_ADMIN|NEED_BOSS_AUTH_NOT_ADMIN` 时才按权限不足直接停止；命中时按同一条 WorkBuddy 登录命令处理。
- 任何 HTTP 429：立刻停止后续 i人事业务调用，不重连、不登录。再按 [租户额度提示](ihr-cli-quota-notice.md) 区分额度耗尽和请求过多。
- 网络失败或 5xx 是暂时性调用失败，不触发登录。
- 自然语言、stderr 片段、字符串包含“401”或模型推断都不是恢复证据。

## WorkBuddy 路由

1. 停止当前业务命令，不继续尝试其他 Domain 或 raw 接口。
2. `error.code=AUTH_REQUIRED|AUTH_EXPIRED|CREDENTIAL_MISSING`、结构化 HTTP 401，或第一层 `code=NEED_BOSS_AUTH_ADMIN|NEED_BOSS_AUTH_NOT_ADMIN`：执行一次
   `ihr-cli auth login --open-browser --source workbuddy-connector --env prod --create-timeout 8s --timeout 5m`
   该命令与 Connector 生命周期使用同一条 auth 命令：CLI 自行打开系统默认浏览器并在当前前台进程等待授权（最长 5 分钟）。不要添加 `--superpwd`、`--no-browser`、`--no-wait` 或 `--json`，不要改用 `auth ensure`。
3. 只有登录命令成功完成后，才允许原业务命令最多重试一次；登录被拒绝或超时后停止。重试后再次返回鉴权错误时停止。
4. 若 CLI 提示未能自动打开浏览器，把 CLI 输出的完整授权链接原样展示给用户，让用户手动打开完成授权；不要重新创建授权会话。

## 安全边界

- 不输出 token、device_code、授权内部字段、完整认证 JSON、敏感配置或认证中心内部地址。
- 不删除旧 credential，不切换 `IHR_CLI_CONFIG_DIR`，不强制使用第二种 credential store。
- Connector 与普通终端首版共享现有 iHR CLI 配置和登录态；断开连接可能同时影响终端当前 profile。
