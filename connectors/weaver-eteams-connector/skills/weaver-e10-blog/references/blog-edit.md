# 编辑日报（blog.edit prepare -> apply）

## 何时使用

修改已存在的日报正文（自己的或有权操作的目标人员日报）。目标当天无日报时报错，应改用发布。

## 输入要点（prepare）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| user_id / name | 否（二选一） | 目标人员；都不传时编辑当前登录人的日报 |
| date | 是 | 日报归属日期 |
| content | 是 | 新正文；纯文本自动包裹 `<p>` |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.edit.prepare --input-json '{"date":"2026-09-17","content":"修正后的日报内容。"}'
```

用户确认后：

```powershell
weaver-work-cli --json blog run blog.edit.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.edit.prepare --input-json '{"user_id":"1000000000000000001","date":"2026-08-18","content":"<p>修正后的日报内容。</p>"}'
weaver-work-cli --json blog run blog.edit.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

## 输出处理

1. prepare 返回原内容（`original.content_text`）与新内容、差异摘要和 continuation。
2. 向用户复述原内容与新内容，取得明确确认后调 apply。
3. apply 回查验证内容已更新，返回 `updated=true, verified=true`。

## 注意

- 编辑覆盖整篇正文，不是追加；确认时让用户看清原内容。
- 内容与新内容相同时 prepare 报 `changes_noop`。

## 失败处理

- `edit_target_missing`：目标当天无日报，建议改用发布。
- `target_changed`：确认期间日报被修改，重新 prepare。
- `partial/write_uncertain`：停止重试，用 `blog.query_user` 回查后报告。
