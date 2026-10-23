# 评论日报（blog.comment prepare -> apply）

## 何时使用

对某条日报发表评论。目标日报必须存在：`prepare` 阶段按「blog_id」或「日期 + 人员」自动定位，找不到即报错（不询问、不猜测）。

## 输入要点（prepare）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| blog_id | 与 date 二选一 | 日报记录 id |
| date | 与 blog_id 二选一 | 日报归属日期，配合 user_id / name 定位 |
| user_id / name | 否（二选一） | 目标人员；都缺省时定位当前登录人当天日报 |
| content | 是 | 评论内容 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.comment.prepare --input-json '{"name":"PLACEHOLDER_NAME","date":"2026-08-18","content":"辛苦了，已核对。"}'
```

用户确认后：

```powershell
weaver-work-cli --json blog run blog.comment.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.comment.prepare --input-json '{"date":"2026-08-18","content":"辛苦了，已核对。"}'
weaver-work-cli --json blog run blog.comment.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

## 输出处理

1. prepare 返回目标日报摘要（`target_content_text`）与评论内容、continuation。
2. 向用户复述目标日报与评论内容，确认后调 apply。
3. apply 通过评论列表回查验证，返回 `comment_id`。

## 注意

- 评论对目标日报的可见人群可见；发送前必须确认内容。
- 目标日期无日报时报 `target_missing`，如实向用户报告「对应日期 X 人员 X 无日报，无法评论」。

## 失败处理

- `target_missing` / `name_ambiguous` / `name_not_found`：按错误详情处理。
- `partial/write_uncertain`：停止重试，用 `blog.comments` 回查后报告。
