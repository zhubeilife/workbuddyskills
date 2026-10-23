# 对话查询

## 何时使用

使用 `search_3chat_conversations` 直接筛选、分页、统计或定位对话实体，例如：

- 查询最近 30 天的对话。
- 查询已转人工、等待人工或由 AI 处理的对话。
- 查询未解决、已关闭或某个渠道账号关联的对话。
- 先筛选对话，再按客户或群组读取完整上下文。

该工具不返回消息明细、会话记忆、自定义字段或 `agent_logs`。需要这些内容时，根据返回的 `customer_id` 或 `group_id` 调用相应上下文工具。

## 筛选规则

- 多个已提供字段按 AND 匹配；所有参数都可省略。
- `customer_id` 与 `group_id` 互斥。
- 提供 `customer_id` 时，`session_type` 只能省略或为 `p2p`。
- 提供 `group_id` 时，`session_type` 只能省略或为 `group`。
- `reply_strategy` 只使用 `HUMAN` 和 `AI_ASSISTANT`。
- `transfer_status` 使用 `NOT_TRANSFERRED`、`WAITING`、`TRANSFERRED`。
- `status` 使用 `ACTIVE`、`COMPLETED`、`PAUSED`。
- `solved=false` 是有效筛选条件，不能当成未提供。
- `time_field` 决定时间筛选字段和倒序排序字段，默认 `created_time`。
- `start_time` 和 `end_time` 是 Unix 毫秒时间戳，可以单独提供；同时提供时结束时间不得早于开始时间。
- `offset` 默认 0；`limit` 默认 20，范围 1～100。

## 结果处理

返回 `data.total`、`data.offset`、`data.limit` 和 `data.conversations[]`。无匹配结果时返回 `total=0` 和空数组，这是正常查询结果。不要把对话实体的 `summary` 当成完整聊天记录；需要核对具体表达时读取上下文消息。
