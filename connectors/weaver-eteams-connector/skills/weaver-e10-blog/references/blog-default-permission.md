# 默认共享查询（blog.default_permission）

## 何时使用

发布前想确认某日期会共享给哪些对象；一般无需单独调用——`blog.publish.prepare` 默认自动回填默认共享（`share_default=true`）。

## 输入要点

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| date | 是 | 日报归属日期 `YYYY-MM-DD` |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.default_permission --input-json '{"date":"2026-09-17"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.default_permission --input-json '{"date":"2026-09-17"}'
```

## 输出处理

- `list[]`：默认共享对象数组（`obj_id` 展示名、`_entityType` 类型等）。
- `list` 为空表示该日期无默认共享。

## 注意

- 只读操作，无需确认。

## 失败处理

- `business_error`：透出服务端 message。
