# `ihr-cli smart-kpi rating-rule +list`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

查询评分规则候选，供统一分值范围选用。

## 何时使用

- `scoreRange=UNIFIED_SCORE_RANGE` 时必填 `normRatingRuleId`。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--data-type` | string | 否 | KPI | KPI / OKR / OBJ | `dataType` | 业务类型，考核模板用 KPI |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
只读，不做评分规则管理。

## Agent 安全规则

- ID 必须来自本会话本命令结果。
- 禁止 raw API。
