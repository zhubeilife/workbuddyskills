# 日报导出（blog.export）

## 何时使用

把日期段内的日报导出为本地 `.xlsx` 文件。

## 输入要点

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| start_date / end_date | 是 | 日期范围（含边界） |
| output | 是 | 本地输出路径，必须是 `.xlsx` 文件；已存在时 CLI 拒绝覆盖 |
| page_size | 否 | 默认 200 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.export --input-json '{"start_date":"2026-08-01","end_date":"2026-08-31","output":"C:\\tmp\\blog-2026-08.xlsx"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.export --input-json '{"start_date":"2026-08-01","end_date":"2026-08-31","output":"/tmp/blog-2026-08.xlsx"}'
```

## 输出处理

- `output`：落盘路径；`bytes`：文件大小。
- 导出范围为当前账号**有权限查看的全部日报**（不限于本人）；xlsx 第一行是标题，第二行是表头（姓名 / 部门 / 日报日期 / 提交状态 / 日报提交时间 / 是否隐藏 / 日报内容）。

## 注意

- 这是本地文件写入：`output_exists` 时换路径或先征得用户同意移除旧文件，不要静默覆盖。
- 导出的日报内容会进入本地文件；如需把文件内容发给外部服务或进入大模型上下文，先向用户确认。

## 失败处理

- `output_parent_missing` / `output_parent_invalid`：先创建输出目录。
- `export_failed`：服务端返回了非 xlsx 内容，错误详情带响应预览，向用户报告。
