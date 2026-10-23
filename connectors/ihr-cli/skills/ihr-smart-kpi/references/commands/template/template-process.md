# `ihr-cli smart-kpi template +process`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

读取考核模板权限配置。

## 何时使用

- 保存权限前读取底稿，或按所选流程初始化。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--template-id` | string | 是 | 无 | 正整数 ID | `templateId` | 本会话模板 ID |
| `--process-basic-id` | string | 否 | 无 | 正整数 ID | `processBasicId` | 可省略的流程 ID |
| `--view` | bool | 否 | 无 | `true`/`false` | `view` | 是否按查看模式 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- `kpiRoleId` 只能从本命令或 `process +list/+node` 拷取。
- 禁止 raw API。
