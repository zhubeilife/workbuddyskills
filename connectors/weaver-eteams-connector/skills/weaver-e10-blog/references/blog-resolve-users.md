# HRM 姓名解析（blog.resolve_users）

## 何时使用

用户只给了姓名而没有 userId，且后续需要跨多次调用复用 userId（如先查日报再提醒）时，先解析一次。

## 输入要点

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| name | 是 | 员工姓名，精确匹配 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.resolve_users --input-json '{"name":"PLACEHOLDER_NAME"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.resolve_users --input-json '{"name":"PLACEHOLDER_NAME"}'
```

## 输出处理

- `matched`：命中人数；`users[]` 含 `user_id` / `name` / `department`。
- 多命中时向用户列出候选让其选择，不要自行挑第一个。

## 注意

- 单次查询类操作（query_user、remind.prepare）内部已支持直接传 `name`，无需先解析。

## 失败处理

- `matched=0`：如实告知未找到该员工，请用户确认姓名。
