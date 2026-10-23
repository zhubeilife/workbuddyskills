# 花名册查询命令

本文件补充 `staff +search/+get` 当前 Shortcut 参数和返回摘要。完整 flags 仍以具体命令 `--help` 为准。

## `staff +search`

查询员工花名册列表，只读，不修改员工数据。

| 参数 | 类型 | 默认值 | 业务说明 |
| --- | --- | --- | --- |
| `--keyword` | string | 无 | 按姓名模糊匹配 |
| `--staff-id` / `--staffId` | string | 无 | 按员工 ID 精确筛选；两个 alias 不同时传 |
| `--staff-no` / `--staffNo` | string | 无 | 按工号模糊筛选 |
| `--mobile-no` / `--mobileNo` | string | 无 | 按手机号模糊筛选 |
| `--email` | string | 无 | 按工作邮箱模糊筛选 |
| `--department-id` / `--departmentId` | string | 无 | 一个或多个部门 ID，逗号分隔 |
| `--status` | string | 无 | `active/inactive/all` 或服务端原始状态；`all` 不含 `DELETE` |
| `--fields` | string | 基础可读字段 | 逗号分隔字段 code，可以包含真实 Flex `fieldName` |
| `--page` | int | `1` | 1-based 当前页 |
| `--page-size` / `--pageSize` | int | `20` | 每页 1-1000 条 |

JSON/stdin 与分项 flags 互斥。JSON 可以使用 `fields/flexSearchItems/page/pageSize`，也可以使用 `keyword/staffId/staffNo/mobileNo/email/departmentId/status` 这些 Shortcut 友好字段。

不支持的旧输入包括 `includeFlex/includeMeta/tagCodes/sortField/sortType/sortVos`。需要动态字段值时把真实字段 code 放入 `fields`；字段说明单独查询 Flex Meta。

成功响应为 Shortcut envelope，重点业务路径：

| 路径 | 说明 |
| --- | --- |
| `response.data.page` | 当前页 |
| `response.data.rows` | 每页条数 |
| `response.data.totalElements` | 总记录数 |
| `response.data.totalPages` | 总页数 |
| `response.data.list[]` | 员工列表；字段由 `fields` 和服务端权限决定 |

Metadata 中的 `responseMeta.dataPath: list` 是相对于业务 `data` 对象的路径；最终 CLI envelope 需要使用 `response.data.list`。

## `staff +get`

按唯一员工 ID 查询详情：

| 参数 | 类型 | 必填条件 | 业务说明 |
| --- | --- | --- | --- |
| `--staff-id` / `--staffId` | string | 分项参数模式二选一必填；JSON 可提供 `staffId` | 员工业务 ID，不能用姓名或工号替代 |

成功响应的 `response` 是单员工详情对象。详情接口可以返回比花名册列表更多的员工业务字段；实际字段集合由服务端权限、租户配置、脱敏和接口投影决定。字段业务含义和类型见[员工对象](../domain/employee.md)，不要把 Schema 当前公开的部分字段误解为详情响应的完整字段上限。

## 分页与统计

- 普通查询、员工定位和详情前置查询默认只读取当前页；不要为了寻找唯一员工而自动枚举后续页。
- 当用户明确提出统计/汇总/分析、完整名单或需要先拿到完整结果再处理，且满足 [Staff 查询语义](../domain/query-semantics.md) 时，可以在固定人员、部门、状态和期间范围内串行读取全部页。用户已经明确该范围时，不需要逐页再次确认。
- **必须按页码顺序串行请求，禁止并发请求多页**；不自动重试。
- 仅当用户只要数量、`response.data.totalElements` 已能完整回答、并且没有要求拉取全部行时，才用服务端总数。明确全量或后续分析时串行读取全部页。
- 逐页聚合时必须保持筛选条件和字段投影不变，校验 `response.data.page`、`response.data.totalPages`、`response.data.totalElements` 和员工 `id`；出现空页、重复页、总数变化、请求失败或超过执行上限时停止，并说明结果不完整。
- 不得用自动翻页把当前花名册说成某天当时的在职，或补出期初分母、关系生效时点和当前命令未返回的字段；也不得把全量读取扩大成导出、敏感字段枚举或跨租户查询。

## 执行边界

- 用户只给姓名、工号或手机号时，先执行 `+search` 获取候选；多候选先确认。
- 查询范围、字段和当前页由用户请求确定；普通查询不自动翻页。统计分析、明确全量或完整拉取按本文件的受控规则串行翻页，禁止并发，不导出或枚举无关员工。
- 手机号、证件号等敏感信息按 Shared 规则最小展示。
- `companyId/userId` 由会话注入，不进入业务参数。
- 失败时按结构化错误停止，不自动重试或改走 raw API。
