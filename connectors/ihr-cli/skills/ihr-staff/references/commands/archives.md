# 员工档案命令

本文件补充 `staff +archiveList/+archiveGet` 的分支、返回和高风险输入。完整 flags 读取具体命令 `--help`。

## `staff +archiveList`

| 关键输入 | 规则 |
| --- | --- |
| `--meta-data-code` | 必填；固定档案使用白名单 code，自定义档案使用当前租户真实 `metaCode` |
| `--meta-data-type` | 固定白名单可省略或传 `ENTITY`；自定义子集必须为 `SUBSET` |
| `--search-items` | 当前档案的查询条件 JSON 数组；只使用真实字段和操作符 |
| `--sort-field/--sort-type` | 只用于支持排序的固定档案；自定义子集不支持 |
| `--page/--page-size` | 用户侧从 1 开始；每页 1-1000 条 |

固定白名单：`tab_staff_education`、`tab_staff_job_history`、`tab_staff_certificate`、`tab_staff_family_member`、`tab_staff_performance`。

成功时 `response` 是所选档案分支的分页业务结果。各分支列表路径可能不同，不能把一个分支的字段路径套给另一个分支；只使用实际响应和本次导航已声明的总数/列表字段。

## `staff +archiveGet`

| 关键输入 | 规则 |
| --- | --- |
| `--staff-id` | 唯一员工 ID，必填 |
| `--meta-data-code` | 一个或多个真实自定义子集 `metaCode`，最多五个 |
| `--meta-data-type` | 必须为 `SUBSET` |

成功时 `response` 是指定员工的自定义子集结果，不是跨员工列表，也不支持固定 `ENTITY` 档案。

## 共同边界

- 固定档案与自定义子集进入不同协议，页码和字段别名转换由 CLI 处理。
- 教育经历按姓名或工号查询时直接使用 `staffName/LIKE` 或 `staffNo/LIKE`，不虚构 `staffId/EQUAL`。
- `+archiveList` 不支持花名册 `--fields`；自定义子集没有真实字段 code 时不能构造筛选条件。
- 一次只查询一个已确认档案类别。普通查询只读当前页；该类别的统计分析可按查询语义串行翻页，禁止并发请求、同时枚举其他档案类别或自动重试。
