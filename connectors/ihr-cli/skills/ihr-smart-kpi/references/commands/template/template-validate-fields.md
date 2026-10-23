# `ihr-cli smart-kpi template +validate-fields`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

Backend payload contract: each item is an `ItemFieldParam` object and requires
`fieldNameCustomMessage`, `showNameCustomMessage`, and
`fillPlaceHolderCustomMessage` objects. Formula fields may additionally provide
`formulaCalculationRule` with `fieldEnterRule=FORMULA_CALCULATION`. Session-derived
context is not part of the CLI payload; frontend-shaped context is removed before
the request is sent.

Nested message objects are also schema-checked (`message`, `messageKey`,
`messageDetails[].locale/message`, and `operation`). The frontend compatibility
field `companyId` is ignored and discarded before validation/request forwarding;
other unknown or identity fields are rejected.

校验考核模板项目字段公式，不保存。

## 何时使用

- `+save-item --confirm` 前必须先调用。`hasError=true` 即停。

## 参数

本命令没有分项 flags，必须使用 `--json` 或 `--stdin`。

JSON 根必须是非空字段对象数组。不接受 flags。flags 与 `--json` / `--stdin` 互斥。CLI 不公开身份字段；前端回传的 `companyId` 会被忽略并丢弃，不会转发。其他身份字段仍被拒绝。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
不得用 `formula +field-check` 替代。

## Agent 安全规则

- 校验失败即停，不进入项目保存。
- 禁止 raw API。
