# 单人日报查询（blog.query_user）

## 何时使用

查「某一个具体的人」某天或某段时间的日报详情，以及判断某人某天是否提交。这是按人查询的唯一路径——群体接口的按 userId 过滤会被服务端忽略并静默返回登录人自己的日报，禁止使用。

## 输入要点

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| user_id / name | 否 | 目标人员 userId 或姓名（姓名经 HRM 精确解析，同名多命中报错）；**两者都不传时默认查当前登录人**，是「查我自己的日报」的唯一路径 |
| date | 是 | 起始日期 `YYYY-MM-DD` |
| end_date | 否 | 结束日期（含）；缺省只查当天。区间按天逐日扫描，上限 62 天 |

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json blog run blog.query_user --input-json '{"name":"PLACEHOLDER_NAME","date":"2026-08-18"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json blog run blog.query_user --input-json '{"user_id":"1000000000000000001","date":"2026-08-15","end_date":"2026-08-20"}'
```

## 输出处理

- `items[]`：每天一条，`date` 为 `YYYY-MM-DD`；`found=true` 表示当天有日报，`blog.content_text` 是去标签正文，`blog.create_time_str` 是实际提交时间。
- `items[].submit_status`：`正常` / `补交` / `未提交`（无日报的天为 `未提交`），与 `blog.query` 口径一致。
- `submitted_days` / `normal_days` / `later_days` / `missing_days`：区间内的已提交、正常、补交、未提交天数汇总，可直接用于按人报表。
- 编辑 / 评论 / 点赞前的目标定位也可以直接用对应的 prepare 操作（内部同样按此接口解析），无需先手动查 id。

## 注意

- 区间上限 62 天；查询跨月报表时按月分段调用。
- `blog.hasData` 字段不可靠，是否提交以 `found` 为准（CLI 已归一化）。

## 失败处理

- `name_not_found`：请用户确认姓名或改传 user_id。
- `name_ambiguous`：报错里带 `candidates[]`，让用户挑选后改传 user_id。
- `range_too_large`：缩小日期范围。
