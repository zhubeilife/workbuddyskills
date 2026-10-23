# 今承达合同管理 CLI 入口

## 请求头 / 认证

所有 `weaver-work-cli contract run <operation>` 发起的 API 请求均自动携带以下凭证头，值来自 E10 登录会话（由 `weaver-work-cli auth login` 建立），禁止业务输入携带：

| 头 | 值来源 | 说明 |
|---|---|---|
| `Cookie` | E10 登录返回的完整原始 Cookie 串 | CLI 从会话注入，禁止裁剪/去重/改写 |
| `eteamsid` | E10 登录返回的 ETEAMSID | CLI 从会话注入 |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` | CLI 自动拼接，`agentType` 来自登录时的 `--agent_type` 参数 |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。

## operation 合约第一信息源

`weaver-work-cli contract schema` 输出 operation 名称、`risk`、`fixed`（固定的方法与路径）、`inputSchema` 和 `withheldOperations`。调用前先读它，不要凭记忆拼 operation 名和字段名。

- operation 名称统一为 `contract.<domain>.<action>`。
- 写操作一律是 `*.prepare` -> `*.apply` 两段：`prepare` 返回脱敏 `preview` 和 `continuation`，`apply` 必须带 `continuation` 与 `confirm: true`。
- `inputSchema` 的 `additionalProperties` 为 `false`，未声明的字段会被拒绝。
- `withheldOperations` 列出源资料不足、暂未实现的能力，遇到对应意图直接说明不可用，不要尝试用其它接口替代。

## 统一调用方式

所有 operation 都通过 `contract run <operation>` 调用。三种输入方式：

1. `--input-json '<json>'`：简单 JSON，推荐。
2. `--input <path>`：复杂或多行 JSON，先写入 UTF-8（无 BOM 也可，CLI 会自动剥离 BOM）文件。
3. `--input -`：stdin，只有确认当前 shell 能稳定传管道时才使用。

`--input` 与 `--input-json` 不能同时传，同时传会返回 `validation/input_conflict`。

Windows PowerShell：

```powershell
weaver-work-cli contract schema
weaver-work-cli --json contract run contract.template.list --input-json '{"templateName":"采购合同","pageNo":1,"pageSize":10}'
weaver-work-cli --json contract run contract.request.status --input-json '{"requestId":"12345"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli contract schema
weaver-work-cli --json contract run contract.template.list --input-json '{"templateName":"采购合同","pageNo":1,"pageSize":10}'
weaver-work-cli --json contract run contract.request.status --input-json '{"requestId":"12345"}'
```

## 人类友好子命令

除了 `run`，CLI 也提供分组子命令（参数会转成对应的 operation 输入），可用于排查和手工操作：

- `contract type tree`
- `contract template tree|list|detail`
- `contract clause tree|list|groups|search|tags`
- `contract clause reference get|save-prepare|save-apply`
- `contract subject app|form|fields|options|query|create-prepare|create-apply`
- `contract workflow query|list|form-info|field-options`
- `contract request create-prepare|create-apply|save-prepare|save-apply|submit-prepare|submit-apply|supervise-prepare|supervise-apply|status|log`

Agent 侧优先用 `run <operation>`，保证输入与 manifest 完全一致。

## 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 业务/服务错误 |
| 2 | 输入用法错误（含 ID 非法、字段非法） |
| 3 | 认证失败或登录态失效 |
| 4 | 网络错误 |
| 5 | 内部错误 |
| 6 | 策略拒绝（重复引用、流程状态不允许等） |
| 10 | 需要确认（缺少 `confirm` 或 continuation） |
| 11 | `partial/write_uncertain`，结果不确定，禁止自动重试 |

## 注意

- 业务输入不得包含 `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段；用户 ID 由 CLI 从会话注入。
- 环境相关 ID（`appId`、`objId`、`formId`、`workflowId`、`nodeId`）只能运行时解析，禁止使用文档示例值或标准环境 ID 兜底。
- 涉及合同正文或附件的操作，文件内容可能进入大模型上下文，执行前必须获得用户明确确认。
