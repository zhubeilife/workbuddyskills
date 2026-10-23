# `ihr-cli smart-kpi template +save-process`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

Each process node follows `TemplateProcessNodeSaveParam`: `processNodeId`, a valid
`nodeType`, `templateNodeOtherAuth` object, and a non-empty
`templateItemAuthList` are required. Each item authorization requires
`kpiTemplateItemId`, `itemType`, and `orderNum`.

`templateNodeOtherAuth`, special-auth entries, handler settings, and
`templateItemAuthList[].children` are recursively checked; unknown and identity
fields are rejected.

受确认地保存考核模板权限配置。

## 何时使用

- 第三步。成功后模板状态由后端变为 COMPLETE。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--confirm` | bool | 真实执行时必填 | 无 | 存在即确认 | 无 | dry-run 不要求 |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
真实写入必须 `--confirm`；dry-run 不要求。
JSON 含 processBasicId、templateBasicId、templateProcessNodeList，可选 processBasicUpdatedAt。void 成功。

## Agent 安全规则

- `kpiRoleId` 来自本会话流程/权限详情，不新增角色列表命令。
- 失败即停。
- 禁止 raw API。
