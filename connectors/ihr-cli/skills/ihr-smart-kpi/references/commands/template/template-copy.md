# `ihr-cli smart-kpi template +copy`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

`name` is limited to 50 Unicode characters, matching the frontend copy dialog and
the backend template-name constraint.

受确认地复制考核模板。

## 何时使用

- 源 ID 来自本会话 `template +list`。成功返回新 ID。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--id` | string | 是 | 无 | 正整数 ID | `id` | 源模板 ID |
| `--name` | string | 是 | 无 | 新名称 | `name` | 新模板名称 |
| `--copy-norm-template` | bool | 否 | false | `true`/`false` | `copyNormTemplate` | 是否同时复制指标模板 |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
真实写入必须 `--confirm`；dry-run 不要求。
成功输出 `saved=true`、`mode=COPY` 和新 `id`。

## Agent 安全规则

- 禁止外来 ID。
- 失败即停。
- 禁止 raw API。
