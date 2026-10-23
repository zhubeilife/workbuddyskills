# `workflow process` 流程查询与处置

## 能力范围

`workflow process` 用于 HR 侧审批流程的数量、列表、详情、活动任务和单条处置。它与 `workflow ledger` 的区别是：process 面向具体流程记录和后续处置；ledger 面向按大类/状态统计和列表台账。

## 查询命令

| 命令 | 用途 | 关键参数 |
| --- | --- | --- |
| `ihr-cli workflow process +count` | 按流程分组和页签统计数量 | `--group-code`、`--tab-code`、`--keyword` |
| `ihr-cli workflow process +list` | 分页查询流程记录 | 上述筛选项、`--page`（默认 1）、`--rows`（默认 100，最大 300） |
| `ihr-cli workflow process +detail` | 查询单条流程详情 | `--process-id` 必填 |
| `ihr-cli workflow process +tasks` | 查询流程当前活动任务 | `--process-id` 必填 |

查询可使用 flags 或 `--json/--stdin`，两种输入方式不能混用。不得传入 `companyId`、`userId`、`staffId`、token 或 cookie；身份和租户范围由当前登录态提供。

## 写命令

以下命令只允许对单条流程执行，并且都必须先向用户展示目标和动作、获得明确确认：

| 命令 | 必填字段 |
| --- | --- |
| `+approve` | `process-id`、`confirm-process-id`、`task-id`、`act-proc-inst-id`、`approval-setting-id`、`approve-msg` |
| `+deny` | 同上，`approve-msg` 为驳回意见 |
| `+transfer` | `process-id`、`confirm-process-id`、`task-id`、`act-proc-inst-id`、`transfer-staff-id` |
| `+urge` | `type`、`process-id`、`confirm-process-id` |

`--confirm-process-id` 必须与 `--process-id` 完全一致。任何字段缺失、不一致或用户未确认时，停止执行。催办仍保持旧业务语义，但 CLI 不允许省略流程 ID，避免触发按类型全量催办。

## 多步流程

1. 先用 `+list` 在明确的大类、页签和单页范围内定位记录。
2. 从列表结果取得真实 `processId`，调用 `+detail` 核对流程身份和当前状态；详情不是活动 `taskId` 的来源。
3. 调用 `+tasks` 获取当前活动任务。0 条时停止；1 条时使用同一记录的 `taskId`、`actProcInstId` 和 `approvalSettingId`；多条时展示候选并要求用户明确选择，禁止默认取第一条。
4. 向用户展示目标流程、当前处理人和拟执行动作，获得确认后逐条调用写命令；失败立即停止，不自动重试或扩大范围。
5. 写操作后使用 `+detail` 或 `+list` 回读状态；超时或连接中断时将结果标记为未知，回读无法证明状态变化时不得报告成功。

管理员不必出现在 `assignees` 中；`assignees` 表示当前任务处理人，管理员是否能执行同意由后台 `approval.list.approved` 权限判断。单条任务的 `assignees` 有多人不等于存在多条任务，任务数只按 `+tasks` 响应数组元素数判断。

内部 ID 仅用于命令参数传递，不在最终回复中原样展示。最终回复应使用业务名称、处理结果和失败原因，不直接输出完整原始 JSON。

## 分页与结果

`page` 从 1 开始，`rows` 范围为 1-300；JSON 中的数字必须是整数。需要全量时按 `totalPages` 串行翻页，并发固定 1、最多 20 页或 5000 条，达到上限立即停止并说明结果不完整；不得把没有明确范围的请求转换为全量查询。空结果按“暂无符合条件的流程”回答。
