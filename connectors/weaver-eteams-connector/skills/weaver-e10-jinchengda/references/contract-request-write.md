# 合同审批流程：创建、保存、提交、催办（写操作）

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


四个写操作全部是 `prepare -> apply` 两段，且必须分别报告每一步结果。

| 动作 | prepare | apply | 路径 | 风险 |
|---|---|---|---|---|
| 创建流程实例 | `contract.request.create.prepare` | `contract.request.create.apply` | `POST /api/workflow/core/paService/v2/doCreateRequest` | write |
| 保存表单 | `contract.request.save.prepare` | `contract.request.save.apply` | `POST /api/workflow/core/paService/v1/saveFormData` | write |
| 提交审批 | `contract.request.submit.prepare` | `contract.request.submit.apply` | `POST /api/workflow/core/paService/v1/submitRequest` | high-impact |
| 催办 | `contract.request.supervise.prepare` | `contract.request.supervise.apply` | `POST /api/workflow/core/paService/v1/requestSupervise` | high-impact |

用户 ID 由 CLI 从会话注入：前三个接口注入 `userid`，催办接口注入 `userId`（源资料原文如此）。

## 创建流程实例

- 输入：`workflowId`（必填）、`requestname`、`remark`、`isnextflow`（默认 0）、`isVerifyFormRequired`（默认 false）、`requestLevel`（默认 0）、`formData`、`isNewFormData`、`seniorFormParam`
- `prepare` 不再请求活动版本接口（`getActiveWfId` 在部分租户返回 500 系统错误且无必要），直接用 `contract.workflow.query` / `contract.workflow.list` 解析出的 `workflowId` 创建
- `apply` 成功后从 `message.requestId` 取实例 ID，再用 `getRequestStatus` 回读；缺少 `requestId` 或回读 ID 不一致时返回 `partial/write_uncertain`

## 保存表单

- 输入：`requestId`（必填）、`formData`（必填，含 `dataDetails` 非空数组）、`workflowId`、`userCurrentNodeId`、`isNewFormData`、`seniorFormParam`
- `formData.dataDetails[]` 用 `fieldId` 或 `dataKey` 二选一定位字段；选择类字段用 `dataOptions[].optionId`，有值时优先于 `content`
- `prepare` 先读流程状态，只有草稿（0）、已退回（2）、待提交（6）可写；审批中（1）抛 `policy/already_submitted`，已结束（3/4/5/8）抛 `policy/request_closed`
- 保存 ≠ 创建 ≠ 提交，三者必须分别报告

## 提交审批（最高风险）

- 输入：`requestId`（必填）、`remark`、`userCurrentNodeId`、`requestName`、`formdata`（注意全小写 d）、`otherParams`、`isVerifyFormRequired`（默认 true）
- **必须与"创建并保存"分开的第二次确认**
- `apply` 成功后必须回读 `contract.request.status` 的 `flowStatus.code`：只有 1（审批中）或 3（已归档）才算生效；否则返回 `partial/write_uncertain`
- `1200301`（当前 userid 为空）：停止并诊断会话状态，**不自动切换接口或盲目重试**
- `1200306`（服务端必填校验）：解析缺失字段列表，逐字段补全后重试（最多 3 轮），不切换接口
- 提交后流程进入审批流转，不可撤回（撤回/退回接口未实现）

## 催办（会发送真实通知）

- 输入：`requestId`（必填）、`otherParam`（必填）、`remark`
- `otherParam` 的 `currentOperator`、`doneOperator`、`submitOperator`、`ccOperator`、`otherReminder` **必须至少填 1 个**；`messageRemind`、`emailRemind` 只是提醒方式，不能算作提醒对象
- `prepare` 先读流程状态，只有审批中（1）可催办，否则抛 `policy/not_in_approval`
- 高影响操作：会向真实接收人发送通知，执行前必须展示脱敏摘要并获得明确确认；测试时只向明确的内部测试接收人发送，`remark` 包含 `[WB-SKILL-TEST]`

## 调用示例

Windows PowerShell：

```powershell
weaver-work-cli --json contract run contract.request.create.prepare --input-json '{"workflowId":"12345","requestname":"WB-SKILL-TEST 销售合同审批流程"}'
weaver-work-cli --json contract run contract.request.create.apply --input-json '{"workflowId":"12345","requestname":"WB-SKILL-TEST 销售合同审批流程","continuation":"PREPARE_CONTINUATION","confirm":true}'
weaver-work-cli --json contract run contract.request.save.prepare --input-json '{"requestId":"67890","formData":{"dataDetails":[{"fieldId":"111","content":"WB-SKILL-TEST 客户"}]}}'
weaver-work-cli --json contract run contract.request.submit.prepare --input-json '{"requestId":"67890","requestName":"WB-SKILL-TEST 销售合同审批流程"}'
weaver-work-cli --json contract run contract.request.supervise.prepare --input-json '{"requestId":"67890","remark":"[WB-SKILL-TEST] 测试催办","otherParam":{"currentOperator":1}}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.request.create.prepare --input-json '{"workflowId":"12345","requestname":"WB-SKILL-TEST 销售合同审批流程"}'
weaver-work-cli --json contract run contract.request.create.apply --input-json '{"workflowId":"12345","requestname":"WB-SKILL-TEST 销售合同审批流程","continuation":"PREPARE_CONTINUATION","confirm":true}'
weaver-work-cli --json contract run contract.request.save.prepare --input-json '{"requestId":"67890","formData":{"dataDetails":[{"fieldId":"111","content":"WB-SKILL-TEST 客户"}]}}'
weaver-work-cli --json contract run contract.request.submit.prepare --input-json '{"requestId":"67890","requestName":"WB-SKILL-TEST 销售合同审批流程"}'
weaver-work-cli --json contract run contract.request.supervise.prepare --input-json '{"requestId":"67890","remark":"[WB-SKILL-TEST] 测试催办","otherParam":{"currentOperator":1}}'
```

## 错误与边界

| 场景 | 表现 | 处理 |
|---|---|---|
| `apply` 缺少 `confirm` | `confirmation/required`，退出码 10 | 带 `confirm: true` 与 `prepare` 的 `continuation` 重新调用 |
| 输入与 `prepare` 不一致 | `validation/target_changed` | 重新 `prepare` |
| 流程状态不允许写 | `policy/already_submitted` / `request_closed` / `not_in_approval` | 停止，先撤回/退回或换流程实例 |
| `workflowId` 无效或不可创建 | `doCreateRequest` 返回业务失败 | 重新用 `contract.workflow.query` / `contract.workflow.list` 解析 `workflowId` |
| 提交返回 `1200301` | `authentication/session_expired` | 停止，先确认 E10 登录态 |
| 提交返回 `1200306` | `api/missing_required_fields` | 解析缺失字段补全后重试，最多 3 轮 |
| 写请求超时/断线 | `partial/write_uncertain`，退出码 11 | 停止，只补一次 `contract.request.status` 查询 |

## 注意

- 不要连续重复提交同一个 `.apply`；提交审批最容易因重复提交造成重复流转。
- 12 类合同审批流程共用这组接口，不要为某一类流程假设特殊参数。
- `continuation` 有效期 10 分钟，由 CLI 生成，禁止手工构造或跨操作复用。
