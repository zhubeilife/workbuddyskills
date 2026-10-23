# 客户查询与上下文

## 查询客户

使用 `search_3chat_customers` 查询客户，然后再按需读取上下文或发送消息。

- 只使用实时 Schema 中存在的标准字段和当前空间已暴露的自定义字段，不得编造字段。
- 不同筛选字段之间按 AND 匹配。
- `name.filter` 中的多个名称按 OR 匹配，支持 1～100 个不重复值；`name.value` 与 `name.filter` 二选一。
- `conditionType=FILTER` 表示精确匹配，`FUZZY` 表示模糊匹配；省略时沿用 `match_mode`。
- `query_mode=resolve` 用于定位一个客户。返回多人时，只有下一步必须操作一个客户才要求用户选择。
- `query_mode=list` 用于分页获取全部匹配客户，不能因为结果很多而要求确认唯一客户。
- 查询完整名单时持续分页，直到返回结果证明数据已完整。

## 最后一次咨询时间

`last_visit_start_time` 和 `last_visit_end_time` 筛选客户字段 `last_visit_time`。

- `last_visit_time` 表示客户最后一次发送消息的时间，即最后一次咨询时间。
- 客户通过单聊或群聊发送消息都会更新该字段。
- 它不是最后一次创建、开启或关闭对话的时间。
- 返回字段 `customers[].lastVisitTime` 使用相同概念。
- 省略相应时间参数表示不设置该方向的时间限制。

## 查询客户上下文

确定客户 ID 后，使用 `search_3chat_customers_context`。

- 先按 `conversation_start_time` 过滤，再取每个客户最近的 `conversation_limit` 个对话，最后为每个对话应用 `message_limit`。
- 省略 `conversation_start_time` 表示不按对话开始时间限制，不要传入 `null`。
- `include_conversations` 控制对话实体字段；`include_conversation_custom_fields` 控制对话自定义字段；`include_conversation_messages` 控制消息明细；`include_agent_logs` 控制 `AI_AGENT` 消息中的 `agent_logs`。
- 成功结果的核心路径为 `data.results[].context.session`。
- `session.session_memory_summary` 是客户全生命周期沟通记忆摘要。
- `session.conversations[]` 是本次查询返回的对话，`conversations[].messages[]` 是消息明细。
- `reply_strategy` 使用 `HUMAN` 或 `AI_ASSISTANT`。
- `transfer_status` 使用 `NOT_TRANSFERRED`、`WAITING` 或 `TRANSFERRED`。
- `NO_SESSION`、`NO_CONVERSATION`、`NO_MESSAGE` 只表示本次查询范围内没有相应数据。结合时间条件、限制、返回开关、`warnings` 和摘要判断，不得推断客户从未沟通。

## 分析输出

客户分析应区分：身份与画像事实、明确需求与兴趣、成交阶段证据、顾虑与未解决问题、近期互动、已约定跟进，以及模型建议。没有字段或消息证据时，不得自行判断高意向、成交、沉默或流失。
