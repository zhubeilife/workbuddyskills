# `ihr-cli smart-kpi norm-category +save`

受确认地新建或更新一个指标分类。

## 何时使用

- 客户已确认分类名称、菜单类型和父分类后保存。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--category-name` | string | 是 | 无 | 非空文本 | `categoryName` | 分类名称 |
| `--norm-menu-type` | string | 是 | 无 | `CURRENCY_NORMS` / `COMPETENCE` / `SENSE_OF_WORTH` | `normMenuType` | 必须显式选择指标库类型 |
| `--id` | string | 否 | 无 | 正整数 ID | `id` | 更新时提供；新建不传 |
| `--parent-id` | string | 否 | 无 | 正整数 ID | `parentId` | 子分类提供；根分类不传或 `0` |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求 |

- flags 与 `--json` / `--stdin` 共用同一规范化器，不能混用。
- 禁止 `companyId`、`userId`、`staffId`、token、cookie。
- 成功响应为 void，不编造 ID。
- 可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 名称相似或同名时先查分类树并让客户选择，不能自动把相似分类当成更新目标。
- 先 dry-run，确认当前载荷后再 `--confirm`。
- 失败即停，禁止 raw API。
