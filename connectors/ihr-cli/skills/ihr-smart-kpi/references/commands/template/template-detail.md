# `ihr-cli smart-kpi template +detail`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

读取考核模板基本信息详情。

## 何时使用

- 更新或回读前，用本会话 `template +list` 或 `+save-basic`/`+copy` 返回的 ID。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--id` | string | 是 | 无 | 正整数 ID | `id` | 必须来自本会话列表或保存返回值 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 禁止外来 ID。CLI 不做列表预检。
- 指标模板导入不得调用本命令。
- 禁止 raw API。
