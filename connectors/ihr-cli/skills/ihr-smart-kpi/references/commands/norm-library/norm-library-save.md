# `ihr-cli smart-kpi norm-library +save`

`normScope` follows the frontend/backend contract as a two-dimensional array. Each condition object uses a non-empty string array for `value`, for example `[[{"value":["staff-id"],"equal":"EQUAL","type":"STAFF"}]]`. The CLI also accepts a legacy single string and normalizes it to a one-element string array. Numeric values, objects, empty arrays, and empty strings are rejected locally.

受确认地新建或完整更新一个指标库指标。

## 何时使用

- 客户已确认完整载荷后保存。构造规则见 [指标库保存构造](norm-library-save-construction.md)。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--json` / `--stdin` | object | 是 | 无 | 完整保存对象 | 见构造 reference | 业务载荷只接受 JSON 或 stdin，不接受分项 flags |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求；缺少时本地拒绝且不发请求 |

JSON 顶层公开字段：`id`、`normName`、`normCode`、`normType`、`normCategoryId`、`departmentIds`、`normScope`、`ratingType`、`ratingFormula`、`carryRule`、`digit`、`allowEditFormula`、`normMenuType`、`kpiNormFieldParamList`。

- 无 `id` 为新建，有 `id` 为完整更新。
- 成功响应为 void，不解析、不编造 ID，不自动回读。
- 禁止 `companyId`、`userId`、`staffId`、token、cookie 和遗留顶层字段。
- 可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 先 dry-run，确认绑定当前完整载荷后再 `--confirm`。
- 更新 ID 必须来自本会话详情。
- 附件字段只提交附件 ID，不提交文件名、地址或完整上传对象。
- 字段展示走公共字段规则；公式先走 `ihr-cli smart-kpi formula +check` / `ihr-cli smart-kpi formula +field-check`。
- 失败即停，未知结果不盲重试，禁止 raw API。
