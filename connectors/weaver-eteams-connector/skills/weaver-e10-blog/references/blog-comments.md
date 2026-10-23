# 评论查询（blog.comments）

## 何时使用

查看某条日报下已有的评论列表（分页）。

## 输入要点

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| blog_id | 是 | 日报记录 id |
| page_no / page_size | 否 | 默认 1 / 20，page_size 上限 100 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.comments --input-json '{"blog_id":"1000000000000000001"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.comments --input-json '{"blog_id":"1000000000000000001","page_size":50}'
```

## 输出处理

- `total_count`：评论总数；`comments[]` 含评论人（`commentor.name`）、`content`、`create_time`。
- 需要目标日报 id 但只知道「人 + 日期」时，用 `blog.comment.prepare`（内部自动定位）。

## 注意

- 只读操作，无需确认。

## 失败处理

- `business_error`：透出服务端 message，检查 blog_id 是否有效。
