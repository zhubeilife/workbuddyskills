# 工具参考

四个工具的完整参数与返回值说明。什么时候用哪个工具、如何串联，见 [SKILL.md](../SKILL.md) 的「工作流」。

## medlive_ask

向医学问答服务提问并获取完整答案。**消耗用户配额。**

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `query` | string | 是 | 用户的医学问题，最长 10000 字 |
| `chat_group_uuid` | string | 否 | 会话 uuid。**追问时必须传上一轮返回的值**以保持上下文；首次提问不传，服务会自动新建会话 |
| `file_uuids` | string[] | 否 | 要针对其提问的已上传文件 uuid，取 `medlive_upload_file` 的返回值（需为解析完成状态）；不传就是普通问答。同一会话的追问会继续带上已挂载的文档，不必重复传 |

返回值（文本形式）：

```
<完整答案>

---
log_uuid=<本次问答记录 uuid> chat_group_uuid=<会话 uuid>
```

`chat_group_uuid` 和 `log_uuid` 是后续追问与兜底必需，**在回答用户后记住它们**（`structuredContent` 里有同名字段，任取其一）；这两个值属于程序元信息，**不要展示给用户**。

- 答案正文是已经渲染好的 Markdown：引用角标是可点击的内联链接（如 `[[2]](url)`，点击打开文献原文），序号从 1 连续（与 `#### 参考文献` 列表一致）；末尾依次是 `#### 参考文献`（内容是文献标题）与 `#### 追问` 两段列表；答案里的图片保持原样。**原样完整输出**，不要改写、删减、总结、翻译或补充。
- 服务端判定无需检索（非医学问题、附件无文字、检索为空）时，话术作为正文正常返回，但 `structuredContent.no_answer = true`：照话术如实回复，不要补造医学结论。

## medlive_upload_file

把文档上传到问答服务并等待解析完成，返回 `file_uuid`；把它放进 `medlive_ask` 的 `file_uuids`，即可针对这份文档提问。上传与解析**不消耗配额**。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `content` | string | 是 | 文件内容：完整 data URI（`data:application/pdf;name=指南.pdf;base64,<内容>`）或裸 base64 |
| `file_name` | string | 否 | 文件名，必须带扩展名；data URI 里带了 `name=` 时可省略 |

支持 pdf/doc/docx/txt 与 jpeg/png/jpg/webp/heic；pdf/doc/docx 单个不超过 50MB，其它不超过 10MB。
解析通常几秒到几分钟，工具会轮询到解析结束或超时：返回「文件仍在解析中」时**不要**拿去提问，稍后用同一个 `file_uuid` 重试。
先确认客户端能把附件按 data URI 传入；拿不到附件内容时本工具不可用，改用纯文本提问。

## medlive_get_answer

按 `log_uuid` 取回已生成并落库的答案。只读，不消耗配额。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `log_uuid` | string | 是 | 问答记录 uuid，由 `medlive_ask` 返回 |

用途：`medlive_ask` 超时或流中断后的兜底；或回看历史问答。只能取回已存在的记录，不能用于提出新问题。

## medlive_list_history

按 `chat_group_uuid` 取回某个会话的问答历史**分页列表**。只读，不消耗配额。用于回顾一段对话、回答「我上次问了什么」「回顾这个会话」等；列表里某条需要完整答案时，用 `medlive_get_answer` 按它的 `log_uuid` 取详情。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `chat_group_uuid` | string | 是 | 会话 uuid，由 `medlive_ask` 返回（追问时用的那个） |
| `page_size` | int | 否 | 每页条数，默认 5，最大 20 |
| `page_num` | int | 否 | 页码，从 1 开始，默认 1 |
| `order` | string | 否 | `desc`（默认，新的在前）或 `asc` |

返回值：会话信息 + 分页列表，每项含 `uuid`(=log_uuid)、`question`、`answer`（正文）、`created_at` 等。

- 列表按时间**倒序**，回顾时从第一页看最新问答；分页小步取（默认 5 条），避免一次拉全量。
- 它只列**已发生**的记录，不会发起新的问答，也不会消耗配额。
