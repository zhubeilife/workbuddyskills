# `ihr-cli smart-kpi template +item`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

读取考核模板项目配置，作为更新底稿。

## 何时使用

- 客户确认更新后读取完整项目，列表摘要不能替代。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--template-basic-id` | string | 是 | 无 | 正整数 ID | `templateBasicId` | 本会话模板 ID |
| `--for-show` | bool | 否 | false | `true`/`false` | `forShow` | 是否按展示视图读取 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 更新必须先 `+save-basic`，本命令使用返回 ID。
- 禁止 raw API。
