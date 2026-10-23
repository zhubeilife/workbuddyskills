# `ihr-cli smart-kpi process +node`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

读取考核流程节点详情。

## 何时使用

- 从节点详情拷取 `kpiRoleId`。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--process-node-id` | string | 是 | 无 | 正整数 ID | `processNodeId` | 本会话流程节点 ID |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- ID 来自本会话流程/权限详情。
- 禁止 raw API。
