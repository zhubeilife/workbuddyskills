# `ihr-cli smart-kpi template +fields-by-type`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

按项目类型读取默认字段定义。

## 何时使用

- 新建项目字段 ID 必须来自本命令或 `field-library +list`，不向客户索要字段 ID。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--type` | string | 是 | 无 | KPI / SENSE_OF_WORTH / ABILITY_ASSESSMENT / SPECIAL_BONUS_PENALTY / BASIC_SETTING / DESCRIPTION / CUSTOM_MODULE / OBJECTIVE | `type` | 项目类型 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 不得用 `formula +field-check` 替代项目字段校验。
- 禁止 raw API。
