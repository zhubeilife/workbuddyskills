# 典型调用示例

首次提问：

```json
{
  "name": "medlive_ask",
  "arguments": { "query": "阿司匹林的主要适应症是什么" }
}
```

追问（沿用上一轮的 `chat_group_uuid`）：

```json
{
  "name": "medlive_ask",
  "arguments": {
    "query": "那老年患者的剂量需要调整吗",
    "chat_group_uuid": "<上一轮返回的 chat_group_uuid>"
  }
}
```

上传文档后针对它提问（两步）：

```json
// 1) 上传，返回 structuredContent.file_uuid
{
  "name": "medlive_upload_file",
  "arguments": { "content": "data:application/pdf;name=中国脑卒中防治指导规范.pdf;base64,<base64>" }
}
// 2) 带着 file_uuid 提问
{
  "name": "medlive_ask",
  "arguments": { "query": "这份文档里推荐的食盐摄入量是多少", "file_uuids": ["<file_uuid>"] }
}
```

兜底取回：

```json
{
  "name": "medlive_get_answer",
  "arguments": { "log_uuid": "<medlive_ask 返回的 log_uuid>" }
}
```

回顾会话历史（分页，新的在前）：

```json
{
  "name": "medlive_list_history",
  "arguments": { "chat_group_uuid": "<会话 uuid>", "page_size": 5, "page_num": 1 }
}
```
