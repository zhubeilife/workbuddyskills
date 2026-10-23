# 消息发送

发送会改变外部状态。用户只要求分析、筛选对象、拟定内容或预览时，不得调用发送工具。

## 发送前确认

紧接发送前展示：确切客户或群组、相关发送账号或渠道、最终正文、附件，以及单发或批量范围。只有用户明确确认后才发送；确认后任何业务参数发生变化都要重新确认。

## 附件

- 已有最终可下载 HTTP/HTTPS 直链时直接使用。
- URL 不能依赖鉴权、自定义请求头、交互页面或跳转短链。
- 无合法直链时调用 `upload_3chat_attachment`。
- 上传成功后优先把完整 `data.attachment` 原样放入 `attachments`；至少传入 `data.attachment.url`。
- 不得缩短、改写、转义或使用 Markdown 包装 URL。
- 上传成功不代表消息已发送。

## 单条发送

- 客户：使用 `send_3chat_customer_message`，提供一个确定的 `customer_id`。
- 群组：使用 `send_3chat_group_message`，提供标准 `group_id` 和同一群 `managed_accounts[]` 中的 `channel_account_id`。
- 为一次逻辑发送生成稳定的 `idempotency_key`。只有明确允许同请求重试时才复用该键。

## 批量发送

- 客户批量工具最多 100 项，实际建议每批 1～3 项。
- 群组批量建议每批 1～3 项，同批 `group_id` 和 `idempotency_key` 不能重复。
- 每个 `items[]` 有自己的 `confirmation_token` 和 `idempotency_key`。
- 返回 `job_id` 后只查询原任务，不重新创建整批。
- 使用 `get_3chat_batch_send_status` 读取整体状态和 `data.results[]`；`data.results[].success` 判断单项是否处理成功。

## WhatsApp 模板

使用 `send_3chat_customer_whatsapp_template` 发送已审批模板，尤其是超过 WhatsApp 24 小时服务窗口的场景。

- 客户必须关联当前租户的 YCloud Channel。
- 显式指定 `channel_account_id` 时必须与客户关联账号一致。
- `variables` 传编号或命名变量到文本值的映射，不要自行渲染整段正文代替模板。
- 媒体 Header 模板必须提供类型匹配的 `header_media`。
- 发送前确认客户、账号、模板、语言、变量和媒体。

`accepted`、`sent`、`COMPLETED` 只表示系统处理状态，不代表渠道送达或客户已读。
