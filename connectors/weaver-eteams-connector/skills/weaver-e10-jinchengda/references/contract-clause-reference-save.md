# 条款引用：查询与写入（本模块唯一条款写操作）

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


## 查询：`contract.clause.reference.get`

- 方法/路径：`POST /api/ebd/contract/clauseReference/selectData`
- 风险：`read`（虽为 POST，但属于查询）
- 输入：`fileId`、`requestId`、`clauseId`、`referenceObjType`（默认 1，1=条款）、`startTime`、`endTime`、`pageNum`、`pageSize`
- 响应关键字段：`data.records[].clauseId`、`data.records[].fileName`、`data.total`

用途：查看当前合同文档已引用哪些条款，以及在写入前做重复校验。

## 写入：`contract.clause.reference.save.prepare` -> `contract.clause.reference.save.apply`

- 方法/路径：`POST /api/ebd/contract/clauseReference/saveData`
- 风险：`read-before-write` / `high-risk-write`
- 必填输入：`clauseIds`（非空 ID 数组）、`fileId`、`requestId`；可选 `fileName`、`requestName`
- 固定值：`referenceObjType = 1`（1=条款）

`prepare` 阶段 CLI 会先调用 `selectData` 查已引用条款：若传入的 `clauseIds` 中存在已被引用的条款，直接抛 `policy/already_referenced` 并停止，避免重复插入。

`apply` 阶段写入成功后，CLI 会再次调用 `selectData` 回读：若仍有条款未出现在已引用列表中，返回 `partial/write_uncertain`（退出码 11），此时禁止自动重试，只补一次只读查询并向用户报告。

## 确认要求

写入前必须向用户展示并确认**具体条款、合同和文件**：

- 目标合同文件（`fileId` / `fileName`）
- 关联流程（`requestId` / `requestName`）
- 待引用条款数量与条款 ID 摘要（CLI 返回的 `preview` 已脱敏）

不要把"推荐"描述为"已插入"；只有 `apply` 回读成功后才能说条款已生效。

## 调用示例

Windows PowerShell：

```powershell
weaver-work-cli --json contract run contract.clause.reference.get --input-json '{"fileId":"901","requestId":"902","pageNum":1,"pageSize":20}'
weaver-work-cli --json contract run contract.clause.reference.save.prepare --input-json '{"clauseIds":["301","302"],"fileId":"901","requestId":"902","requestName":"2024年IT设备采购合同"}'
weaver-work-cli --json contract run contract.clause.reference.save.apply --input-json '{"clauseIds":["301","302"],"fileId":"901","requestId":"902","requestName":"2024年IT设备采购合同","continuation":"PREPARE_CONTINUATION","confirm":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.clause.reference.get --input-json '{"fileId":"901","requestId":"902","pageNum":1,"pageSize":20}'
weaver-work-cli --json contract run contract.clause.reference.save.prepare --input-json '{"clauseIds":["301","302"],"fileId":"901","requestId":"902","requestName":"2024年IT设备采购合同"}'
weaver-work-cli --json contract run contract.clause.reference.save.apply --input-json '{"clauseIds":["301","302"],"fileId":"901","requestId":"902","requestName":"2024年IT设备采购合同","continuation":"PREPARE_CONTINUATION","confirm":true}'
```

## 错误与边界

| 场景 | 表现 | 处理 |
|---|---|---|
| 传入已引用条款 | `policy/already_referenced` | 停止，提示用户这些条款已插入，不要重复 |
| `apply` 缺少 `confirm` | `confirmation/required`，退出码 10 | 重新调用时带 `confirm: true` 和 `prepare` 的 `continuation` |
| `apply` 输入与 `prepare` 不一致 | `validation/target_changed` | 停止，重新 `prepare` |
| 写入后回读缺失 | `partial/write_uncertain`，退出码 11 | 停止，不自动重放；只补一次 `contract.clause.reference.get` |
| `code != 0` | `api/business_error` | 报告相对路径、脱敏参数摘要与错误信息后停止 |

## 注意

- `fileId` 需从编辑会话获取、`requestId` 需从流程上下文获取，均为环境相关 ID，禁止使用示例值。
- 合同正文与附件内容可能进入大模型上下文；在读取、展示或写入合同文档前必须获得用户明确确认。
- `continuation` 有效期 10 分钟，由 CLI 生成，禁止手工构造或跨操作复用。
