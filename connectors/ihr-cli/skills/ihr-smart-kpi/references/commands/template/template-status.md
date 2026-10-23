# `ihr-cli smart-kpi template +status`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

读取考核模板是否已配置项目。

## 何时使用

- 决定下一步读 `+item` 还是按新建结构构造。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--template-basic-id` | string | 是 | 无 | 正整数 ID | `templateBasicId` | 本会话模板 ID |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- ID 必须来自本会话。
- 禁止 raw API。
