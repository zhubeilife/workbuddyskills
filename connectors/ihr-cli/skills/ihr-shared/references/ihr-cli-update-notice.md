# 更新提示与 `meta`

ihr-cli 业务成功时仍可能在 JSON 里带可选字段 `meta`。它不改变 `ok`/`success`，不改变退出码，也不等于当前查询失败。

- `meta.updateAvailable`：当前通道有更新的 CLI
- `meta.skillsStale`：官方 Skills 与当前 CLI 版本不一致

## 通道

更新检查跟随当前安装通道，stable 和 beta 分开：

- 正式版对照当前通道的稳定指针
- `*-beta.*` 对照 beta 指针
- 不要把 beta 用户导向 stable，也不要把 stable 用户导向 beta

## Agent 怎么处理

除非用户正在问版本或更新，否则不要把 `meta` 原样当作当前任务的主要答案，也不要为了提示去额外跑 `version`、`upgrade --check` 或 help。

先完成用户当前请求。若输出里有 `meta.updateAvailable`，再简短告知可运行：

```bash
ihr-cli upgrade --yes
```

若有 `meta.skillsStale`，告知：

```bash
ihr-cli skill setup --yes
```

**不要自动执行 upgrade。** 等用户确认后再升级。升级按原通道更新 CLI 并同步官方 Skills。

## 不要自行关闭提示

业务 Agent 不要设置 `IHR_CLI_NO_UPDATE_NOTIFIER`。设了之后，JSON 不再带 `meta.updateAvailable`，人类空命令也不再询问升级。那是脚本或 CI 需要完全干净 JSON 时才用的开关，不是业务查询的默认行为。

## 哪些命令会带 `meta`

- 框架 JSON：`version`、`auth status`、`config`、`install` / `upgrade` / `skill` 等 `ok/message/data` 信封
- 普通业务：Shortcut、Metadata Command、Raw interface 的 `success/command/request/response` 信封也可以带可选 `meta`
- 空命令且在交互终端时，才会向人类询问是否现在升级；Agent 非交互，只看 JSON `meta`
