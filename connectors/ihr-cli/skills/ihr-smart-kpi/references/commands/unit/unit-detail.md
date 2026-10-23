# `ihr-cli smart-kpi unit +detail`

读取一个计量单位的详情。

## 何时使用

- 更新单位前，用本会话 `unit +list` 得到的 ID 读取当前名称。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--id` | string | 是 | 无 | 正整数 ID | `id` | 必须来自本会话 `unit +list` |

- flags 与 `--json` / `--stdin` 互斥。
- 禁止 `companyId`、`userId`、token、cookie。
- 可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 禁止使用客户或文件直接提供的外来 ID。
- CLI 不做列表预检；本期详情接口无本公司校验。
- 禁止 raw API。
