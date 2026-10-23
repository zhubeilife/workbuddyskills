# `ihr-cli smart-kpi grade +list`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

查询等级规则候选，供等级评价项目选用。

## 何时使用

- 维度规则为 GRADE 时取 `gradeRuleId`。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--grade-name` | string | 否 | 无 | 名称筛选 | `gradeName` | 按等级名称筛选 |
| `--enabled` | bool | 否 | true | `true`/`false` | `enabled` | 默认只查启用 |
| `--score-matching` | bool | 否 | false | `true`/`false` | `scoreMatching` | 是否开启分数匹配 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
只读，不做等级规则管理。

## Agent 安全规则

- 禁止身份字段。
- 禁止 raw API。
