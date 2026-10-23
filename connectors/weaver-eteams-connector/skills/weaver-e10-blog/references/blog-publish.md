# 发布日报（blog.publish prepare -> apply）

## 何时使用

为当前登录人新建指定日期的日报。只能发布自己的日报；当天已有日报时 prepare 会直接报错（防重复提交），应改用 blog.edit。

## 输入要点（prepare）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| date | 是 | 日报归属日期 `YYYY-MM-DD` |
| content | 是 | 正文；纯文本自动包裹 `<p>`，HTML 原样保留 |
| share_default | 否 | 默认 true：自动回填该日期默认共享对象；false 表示仅自己可见 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.publish.prepare --input-json '{"date":"2026-09-17","content":"今日完成：接口联调；明日计划：冒烟测试。"}'
```

用户确认后：

```powershell
weaver-work-cli --json blog run blog.publish.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.publish.prepare --input-json '{"date":"2026-09-17","content":"今日完成：接口联调；明日计划：冒烟测试。"}'
weaver-work-cli --json blog run blog.publish.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

## 输出处理

1. prepare 返回 `status=AWAITING_CONFIRMATION`、日期、内容与 continuation（10 分钟有效）。
2. 向用户复述日期与内容，取得明确确认（如「确认发布」）后才能调 apply。
3. apply 内部回查验证：返回 `blog_id` 与 `submit_status`（当天补交属正常现象）。

## 注意

- 日报正文会进入业务系统并对共享对象可见；发布前必须逐字确认内容来自用户。
- continuation 由 CLI 签发，禁止手工构造或复用过期 token。

## 失败处理

- `publish_already_exists`：当天已有日报，向用户说明并建议改用编辑。
- `target_changed`：确认期间出现了日报，重新 prepare。
- `confirmation.required`：未带 `confirm=true`。
- `partial/write_uncertain`：停止重试，用 `blog.query_user` 回查后报告。
