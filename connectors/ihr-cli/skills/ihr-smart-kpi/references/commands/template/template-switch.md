# `ihr-cli smart-kpi template +switch`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

受确认地启用或停用考核模板。

## 何时使用

- SETTING 模板不能启用，该拒绝由后端负责。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--id` | string | 是 | 无 | 正整数 ID | `id` | 本会话模板 ID |
| `--enabled` | bool | 是 | 无 | `true` 启用 / `false` 停用 | `enabled` | 开关 |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
真实写入必须 `--confirm`；dry-run 不要求。
void 成功：`saved=true`。

## Agent 安全规则

- 禁止外来 ID。
- 失败即停。
- 禁止 raw API。
