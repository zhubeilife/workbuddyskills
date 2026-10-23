# `ihr-cli smart-kpi unit +save`

受确认地新建或更新一个计量单位。

## 何时使用

- 客户确认当前名称后保存。无 `id` 新建，有 `id` 更新。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--unit-name` | string | 是 | 无 | 最长 10，不含数字和 `\ / : * " < > |` | `unitName` | 单位名称 |
| `--id` | string | 否 | 无 | 正整数 ID | `id` | 更新时提供，必须来自本会话列表 |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求 |

- flags 与 `--json` / `--stdin` 归一化，不能混用。
- 成功为 void：`saved=true`，`mode=CREATE|UPDATE`，不编造 ID，不自动回读。
- 禁止身份字段。重名由后端返回业务错误。
- 可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 先 dry-run，确认当前完整载荷后再 `--confirm`。
- 更新必须先 `unit +list` 再 `unit +detail`。
- 指标模板导入不得调用本命令。
- 失败即停，禁止 raw API。
