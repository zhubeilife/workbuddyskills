# 点赞 / 取消点赞（blog.like prepare -> apply）

## 何时使用

对某条日报点赞或取消点赞。目标日报必须存在，`prepare` 阶段自动定位。

## 输入要点（prepare）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| blog_id | 与 date 二选一 | 日报记录 id |
| date | 与 blog_id 二选一 | 日报归属日期，配合 user_id / name 定位 |
| user_id / name | 否（二选一） | 目标人员；都缺省时定位当前登录人当天日报 |
| cancel | 否 | 默认 false=点赞（vote）；true=取消点赞（cancelVote） |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.like.prepare --input-json '{"name":"PLACEHOLDER_NAME","date":"2026-08-18"}'
```

用户确认后：

```powershell
weaver-work-cli --json blog run blog.like.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.like.prepare --input-json '{"date":"2026-08-18","cancel":true}'
weaver-work-cli --json blog run blog.like.apply --input-json '{"continuation":"<prepare 返回的 continuation>","confirm":true}'
```

## 输出处理

- `action`：`vote` / `cancelVote`；`receipt` 是服务端回执文案（如「点赞成功!」）。
- 点赞状态没有只读回查接口，动作是否生效以业务码为准（`verified=false` 属预期，不是失败）。

## 注意

- 目标日期无日报时报 `target_missing`，如实报告「对应日报不存在，无法点赞」。
- 不要为了「确认生效」而重复发送同一动作。

## 失败处理

- `target_missing`：报告目标不存在。
- `business_error`：透出服务端 message。
