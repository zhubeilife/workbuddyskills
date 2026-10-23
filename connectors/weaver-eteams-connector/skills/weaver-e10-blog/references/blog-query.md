# 群体日报查询（blog.query）

## 何时使用

查「一群人」某天 / 某段时间的日报提交情况：直接下属、间接下属、全部下属、我关注的人。按人查单个目标改用 `blog.query_user`。

## 输入要点

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| user_type | 是 | `directSubordinate`（直接下属）/ `indirectSubordinate`（间接下属）/ `allSubordinate`（全部下属）/ `myFollow`（我关注的人） |
| start_date / end_date | 是 | `YYYY-MM-DD`，含边界 |
| keywords | 否 | 内容关键字服务端过滤，可传空串 |
| page_size | 否 | 默认 300（上限 300）。服务端返回行数 ≈ 人数 × 天数，窗口大时务必保持默认值 |
| page_no | 否 | 默认 1。服务端实测**忽略** pageNo，调大不会拿到更多数据，不要靠翻页取数 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.query --input-json '{"user_type":"directSubordinate","start_date":"2026-09-14","end_date":"2026-09-16"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.query --input-json '{"user_type":"myFollow","start_date":"2026-09-14","end_date":"2026-09-16"}'
```

## 输出处理

- `items[]`：每人每天一行，含 `date`（`YYYY-MM-DD`）、`username`、`submit_status`、`blog`（未提交时为 `null`）。
- `submit_status`：`正常` / `补交` / `未提交`（CLI 按「提交时间 vs 日报日期是否同日」判定，不要用原始 later 字段）。
- `not_submitted[]`：未提交的**人天**列表 `{date, user_id, username}`；同一人只缺个别日期也会列出，可直接用于催交。
- `not_submitted_people[]`：整个窗口内一条日报都没有的人（「完全没交」名单）；`missing_count` 是未提交人天数。
- `submitted_count` / `people`：统计与人员清单。
- `_note` 出现时说明**单页 300 行已顶满、窗口更早的部分没取到**（服务端忽略 pageNo，无法翻页）。此时不要重试或调大 page_no；应缩小日期范围或减少人员范围后重查，并向用户说明只覆盖到哪个日期。

## 注意

- 返回较大时只向用户呈现统计摘要和异常行，不粘贴全部 items。
- 查「我关注的人」是合法的 user_type；不要尝试其它写法（follow、myAttention 等）。

## 失败处理

- `range_too_large`：缩小区间（`start_date` 到 `end_date` 按天计数，**上限 62 天**，与 `blog.query_user` 口径一致）。
- `session_expired`：按 shared 规则确认登录域名后重新登录。
- 返回 0 条：如实告知该范围无数据，不要自动换 user_type 重试。
