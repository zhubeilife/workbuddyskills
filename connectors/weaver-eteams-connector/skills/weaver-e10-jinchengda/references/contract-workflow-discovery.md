# 合同审批流程：流程与表单解析

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


用途：把"流程名称""字段名称""选项名称"等人类语义，解析成运行时可用的 `workflowId`、`fieldId`、`optionId`。全部为 `read`。

## operation 与接口

| operation | 方法 | 路径 | 关键输入 |
|---|---|---|---|
| `contract.workflow.query` | POST | `/api/workflow/pathdef/openapi/getBaseInfoByCondition` | `workflowName`（必填）、`workflowType`、`status` |
| `contract.workflow.list` | POST | `/api/workflow/list/paService/v1/getCreateWorkflowList` | `wfpCode`（必填，0 个人审批 / 1 团队审批）、`filterHide` |
| `contract.workflow.form.info` | POST | 三段式，见下方说明 | `workflowId`（必填） |
| `contract.workflow.field.options` | POST | `/api/workflow/core/paService/v1/getFieldOption` | `fieldId`（必填）、`pageNo`、`pageSize` |

前三个接口由 CLI 注入 `userid`（来自 E10 会话），业务输入禁止携带。

### `contract.workflow.form.info` 的三段式

一次 `form.info` 调用内部串三次请求，中间值（requestId / nodeId / authStr / formId）由 CLI 自行传递，调用方只需要 `workflowId`：

| 步骤 | 路径 | 作用 |
|---|---|---|
| 1 | `/api/workflow/core/flowPage/loadBaseParam` | 取表单会话：`requestId`、`nodeId`、`authStr`、`authSignature` |
| 2 | `/api/workflow/core/flowPage/loadFrameParam` | 取表单身份：`formId`、`relateType`、节点与权限开关 |
| 3 | `/api/workflow/core/form/core/getFormLayout` | 取字段布局：`form`、`formLayout`、`viewRelateConfig`（静态必填） |

第三步路径按 `relateType` 切换：建模表单（`WEA_EBUILDER`）走 `/api/ebuilder/flow/form/core/getFormLayout`，
普通工作流表单保持 `/api/workflow/core/form/core/getFormLayout`。

> 历史实现走 `/api/workflow/pathdef/openapi/getFormInfo`（openapi 系列），在 E10 10.0.9807.01 合同租户上
> 返回成功但**表单为空**，读不到任何字段。已废弃。

输出要点：`formId`、`layoutId`、`requiredFields`、`subFormRequired`（明细表必填）、
`fields[]`（`id`/`name`/`componentKey`/`required`/`readOnly`/`subFormId`/`isBrowser`/`browserType`/`options`/`format`）。
`requiredSource` 标出必填口径的来源：`viewRelateConfig`（服务端下发，权威）或 `field-metadata`（字段自带标记）。
`readOnly` / `disableEdit` 的字段写不进去；`subFormId` 非空的字段属于明细表，要放进该明细的行数据里。

## 处理链

1. 名称明确：用 `contract.workflow.query`，取返回条目的 `activeWfId`（或 `id`）作为 `workflowId`。
2. 名称不明确：用 `contract.workflow.list` 枚举前台可发起流程，让用户选择。
3. 读字段定义：用 `contract.workflow.form.info`，一次调用完成三段式读取；从 `fields[]` 取 `id`、`componentKey`、`required`、`options`、`format`。
4. 读选项：普通 Select/RadioBox/CheckBox 的选项直接就在 `fields[].options` 里；浏览按钮类字段（人力/部门/建模对象等，`isBrowser=true`）的候选用 `contract.workflow.field.options` 查，`fieldId` 取字段 id。

## 调用示例

Windows PowerShell：

```powershell
weaver-work-cli --json contract run contract.workflow.query --input-json '{"workflowName":"销售合同起草","status":"1"}'
weaver-work-cli --json contract run contract.workflow.list --input-json '{"wfpCode":0}'
weaver-work-cli --json contract run contract.workflow.form.info --input-json '{"workflowId":"12345"}'
weaver-work-cli --json contract run contract.workflow.field.options --input-json '{"fieldId":"111","pageNo":1,"pageSize":50}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.workflow.query --input-json '{"workflowName":"销售合同起草","status":"1"}'
weaver-work-cli --json contract run contract.workflow.list --input-json '{"wfpCode":0}'
weaver-work-cli --json contract run contract.workflow.form.info --input-json '{"workflowId":"12345"}'
weaver-work-cli --json contract run contract.workflow.field.options --input-json '{"fieldId":"111","pageNo":1,"pageSize":50}'
```

## 结果解读与边界

- 成功码按路径分组判定：`/api/workflow/core/paService/**` 看 `message.errcode`（0 与 200 都算成功）；
  三段式表单接口没有 `message` 节点，靠 `fail`/`status` 与显式 errcode 判定——只有出现非 0/200 的 errcode 才算失败。
  响应载荷统一包在 `data` 里，顶层 `code/msg/status` 只是传输状态。
- `baseInfoList` 为空 = 未找到同名流程：提示用户确认名称或改用 `contract.workflow.list` 枚举。
- 同名多结果：展示候选（名称、版本）请用户选择，或加 `status=1` 收敛，**不默认取第一条**。
- 名称匹配不到选项：展示候选请用户确认，**不得猜测 optionId**。
- 非选择类字段（文本、金额、日期）没有选项，本接口不提供。
- 响应中的 `tenantKey`、`creator` 等环境敏感字段不输出。

## 注意

- 12 类合同审批流程（销售、采购、协议、变更、解除、关闭、开票、收款、付款、履约计划、进度提报、供应商准入）都走同一条解析链，不要为每类流程假设固定的 `workflowId`。
- **发起流程前不需要、也不允许再去调用活动版本接口**：`getActiveWfId` 在部分租户返回 500 系统错误，`contract.request.create.prepare` 已经不依赖它，直接用 `workflow.query` / `workflow.list` 解析出的 `workflowId` 发起即可。
- **读不到字段时先怀疑路径，不要怀疑表单**：`fields` 为空就该怀疑选错了接口族（见上方「三段式」说明），不要据此告诉用户"这个表单没有字段"。
- 要按真实表单发起（带必填校验、明细行、浏览按钮解析），用 `weaver-e10-workflow` 的 `workflow.createForm` → `createPrepare` → `createApply`；`form.info` 只负责把表单结构读出来。
- 解析完成前不要进入写操作；写操作见 [`contract-request-write.md`](contract-request-write.md)。
