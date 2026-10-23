# `ihr-cli smart-kpi template +save-item`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

`dimensionParams` follows `TemplateDimensionParam`: every entry has
`dimensionType` (`NORMAL_ITEM` or `DIMENSION`) and a non-empty `items` array. Each
item must include `templateItemType`; typed item parameters remain backend-owned.

Typed item parameters are checked recursively. Their `fieldParams` use the same
`ItemFieldParam` contract, and identity fields are rejected at every nested level.

受确认地保存考核模板项目配置。

## 何时使用

- 仅对 SETTING 且最新模板保存。确认前必须先 `template +validate-fields`。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
真实写入必须 `--confirm`；dry-run 不要求。
JSON 为 `{templateBasicId, dimensionParams}`。成功 void：`saved=true`，不编造 ID，不自动回读。非 SETTING 保持后端业务错误。

## Agent 安全规则

- 更新必须先 `+save-basic`，只用返回 ID。
- 校验失败不得 `--confirm`。
- 失败即停。
- 禁止 raw API。
