# `ihr-cli smart-kpi template +save-basic`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

受确认地新建或更新考核模板基本信息。

## 何时使用

- 无 ID 新建，有 ID 更新。更新已完成模板必须先走本命令。后续步骤只用返回 ID。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
真实写入必须 `--confirm`；dry-run 不要求。
负载必须 JSON/stdin，允许字段：id、templateName(最长50)、templateDesc(最长2000)、assessmentTargetType、assessmentType、leaders、dimensionBasicParams、quickBuildType。
成功输出 `saved=true`、`mode=CREATE|UPDATE` 和返回 `id`，不编造 ID。

## Agent 安全规则

- 先 dry-run，确认完整负载后再 `--confirm`。
- leaders 用当前登录人或 ihr-base 选人得到的 userId。
- 失败即停，禁止盲重试 CREATE。
- 禁止 raw API。
