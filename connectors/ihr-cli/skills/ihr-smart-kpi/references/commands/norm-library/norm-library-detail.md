# `ihr-cli smart-kpi norm-library +detail`

读取一个指标库指标的完整详情。

## 何时使用

- 更新指标前，必须用本会话列表结果中的 ID 读取完整详情作为底稿。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--norm-library-id` | string | 是 | 无 | 正整数 ID | `normLibraryId` | 指标库指标 ID，必须来自本会话 `+page` 结果 |

- flags 与 `--json` / `--stdin` 互斥。
- 禁止 `companyId`、`userId`、`staffId`、token、cookie 等身份字段。
- 可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 禁止使用客户或文件直接提供的外来 ID。
- 保持完整 JSON 类型、缺失 key 和 `null`，不补造字段。
- 本期后端详情不按公司拦截，CLI 不做列表预检；ID 只能来自本会话可见查询。
- 禁止 raw API、完整 URL 和自写 HTTP。
