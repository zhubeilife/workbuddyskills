# 群聊群组操作

## 查询群组

使用 `search_3chat_groups` 查询群组、发送账号或群成员。

- `groups[].group_id` 是上下文查询和发送使用的标准群 ID。
- `groups[].channel_type` 表示群所属消息渠道。
- `groups[].managed_accounts[]` 是能够承担发送任务的渠道接入账号。发送时使用同一群下的 `channel_account_id`。此数组查询结果可能为空，原因是渠道接入账号均已退出此群组，出现这种极端情况时，此群组无法执行发送消息的操作。
- 多个可用发送账号且用户意图不明确时，请用户选择。
- `include_members=true` 时返回成员。`participant_id` 是群内成员 ID，`customerName` 是渠道名称，`groupNickName` 是群昵称，`customer_id` 是关联客户 ID。
- `member_type` 使用 `COLLEAGUE`、`CUSTOMER`、`MANAGED_ACCOUNT`；`role` 使用 `ADMIN`、`MEMBER`。
- 不得使用 `external_group_id`、`imRoomId` 或 `im_bot_id` 代替 `group_id` 或 `channel_account_id`。

## 查询群上下文

确定群 ID 后使用 `search_3chat_groups_context`。

- 查询限制顺序与客户上下文一致：时间过滤、对话数量、每个对话的消息数量。
- 成功结果核心路径为 `data.results[].context.session`；群会话的 `session_type` 为 `group`。
- `session_memory_summary` 是群会话的生命周期记忆摘要。
- `reply_strategy` 使用 `HUMAN` 或 `AI_ASSISTANT`。
- `agent_logs` 只属于 `AI_AGENT` 消息。
- `NO_SESSION`、`NO_CONVERSATION`、`NO_MESSAGE` 是本次范围内的正常无数据结果。

从群成员转为私聊跟进时，优先使用成员的 `customer_id` 查询客户和客户上下文，不要仅按名称重新模糊匹配。
