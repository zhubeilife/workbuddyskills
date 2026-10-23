# 审批状态与签字意见

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


用途：查审批进度、查审批意见，以及写操作后的持久化回读。两个 operation 均为 `read`。

| operation | 方法 | 路径 | 输入 |
|---|---|---|---|
| `contract.request.status` | GET | `/api/workflow/core/paService/v1/getRequestStatus` | `requestId`（必填）、`userid` 由 CLI 注入 query |
| `contract.request.log` | GET | `/api/workflow/core/paService/v1/getRequestLog` | `requestId`（必填）、`otherParams`（分页 JSON 串，如 `{"pageSize":10,"pageNumber":1}`） |

## `flowStatus.code` 枚举（源资料原文）

| code | 含义 |
|---|---|
| 0 | 草稿 |
| 1 | 审批中 |
| 2 | 已退回 |
| 3 | 正常归档 |
| 4 | 强制结束 |
| 5 | 已作废 |
| 6 | 待提交 |
| 7 | 暂停 |
| 8 | 撤销 |

## 调用示例

Windows PowerShell（复杂入参写 UTF-8 文件后传 `--input`，不要在单引号 JSON 里用反斜杠转义引号）：

```powershell
weaver-work-cli --json contract run contract.request.status --input-json '{"requestId":"67890"}'
weaver-work-cli --json contract run contract.request.log --input .\request-log.json
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.request.status --input-json '{"requestId":"67890"}'
weaver-work-cli --json contract run contract.request.log --input-json '{"requestId":"67890","otherParams":"{\"pageSize\":10,\"pageNumber\":1}"}'
```

复杂 JSON 建议写入 UTF-8 文件后用 `--input <path>`，避免不同 shell 的引号转义差异。

## 结果解读

- `contract.request.status` 返回 `requestId`、`workflowId`、`requestName`、`status`、`flowStatus`（`code` + `desc`）、`currentNodeType`；`lastOperator` 等人员 ID 已脱敏。
- `contract.request.log` 返回 `operatorName`、`content`、`commentType`、`stepName`、`addTime`（毫秒时间戳）。
- 成功码为 `message.errcode = "0"`；`data.workflowBaseInfo` 不存在或 `requestId` 与入参不一致时按失败处理。
- `data` 为空数组表示暂无审批记录，属于正常返回。

## 用途约束

- 提交审批后必须用它回读 `flowStatus.code` 为 1 或 3，才能说"提交已生效"。
- 保存表单、创建流程后也用它核验持久化结果。
- 查流程列表用 `contract.workflow.list`，查流程基础信息用 `contract.workflow.query`，不要用本文件的接口替代。

## 注意

- 不要输出完整 `lastOperator`、`creatorId` 等人员 ID。
- 回读一次即可；不要陷入"查询 -> 写入 -> 查询"的循环。
