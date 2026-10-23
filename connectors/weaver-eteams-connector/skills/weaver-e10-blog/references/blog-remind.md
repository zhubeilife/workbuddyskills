# 提醒提交日报（blog.remind prepare -> apply）

## 何时使用

向指定人员发送「请填写日报」提醒消息。多人时逐人发送。

## 输入要点（prepare）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| user_ids / names | 二选一 | 被提醒人列表（userId 数组、逗号分隔串或姓名数组，最多 50 人） |
| date | 是 | 日报归属日期，用于默认文案与年份 |
| content | 否 | 自定义文案；缺省生成「请填写 YYYY年 M月 D日 的日报！」 |
| year | 否 | 日报所属年份；缺省从 date 推断 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.remind.prepare --input-json '{"names":["PLACEHOLDER_NAME"],"date":"2026-08-19"}'
```

用户确认后：

```powershell
weaver-work-cli --json blog run blog.remind.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.remind.prepare --input-json '{"user_ids":"1000000000000000001","date":"2026-08-19"}'
weaver-work-cli --json blog run blog.remind.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

## 输出处理

1. prepare 返回被提醒人清单（`user_id` + 解析出的姓名）、文案与年份、continuation。
2. 向用户复述目标人员与文案，取得明确确认后调 apply。
3. apply 逐人发送；`succeeded[]` / `failed[]` 分别列出结果；status 为 `PARTIAL` 时如实报告失败名单。

## 注意

- 默认文案固定以「请填写」开头且包含与 `date` 一致的日期；自定义文案必须包含具体日期。
- 提醒是推给真人的消息，发送前必须逐项确认人名与文案。

## 失败处理

- `name_not_found` / `name_ambiguous`：修正名单后重新 prepare。
- `partial/write_uncertain`：已发送部分不重发；向用户报告成功与失败名单，失败者确认后重新 prepare。
