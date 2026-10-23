# 编制管理

## 对象

- **编制方案/周期**：一段计划周期及其管控配置。
- **编制部门记录**：某个编制方案下对应组织部门的计划记录，有独立的 `hcDepartmentId`/记录 `id`、部门引用、计划人数、直属人数、预算和周期字段。
- **控编维度**：用于细分编制控制的动态列和条件，例如职务、职级或其他租户配置维度；字段名和值必须来自已返回的维度定义或用户提供的协议值。
- **占编数量**：在一个已确认编制部门记录和控编条件下计算出的服务端结果。

## 公开查询链

```mermaid
flowchart LR
    Search[headcount-department search\n方案/周期筛选] --> Record[确认编制部门记录 ID]
    Record --> Detail[headcount-dimension by-id\n读取维度定义]
    Detail --> Count[headcount-dimension occupy-count\n控编条件下占编数量]
```

## 口径约束

- 普通 `departmentId` 与编制部门记录 `id` 不是同一个标识；`by-id`/`occupy-count` 只能使用 `search` 已返回的记录 ID。
- `totalHcCount`/`directHcCount` 是计划配置；`dimensionOccupyCount` 是条件计算结果；三者不能当作同一“人数”。
- 空 `controlDimensions` 按服务端真实返回处理；不能自行解释为整个部门总占编。
- `search` 和 `reduce-list` 受当前编制部门数据范围影响；`by-id` 和 `occupy-count` 没有同等强度的已确认数据范围保证，因此更严格依赖已授权 ID。
- 当前只公开 `search`、`reduce-list`、`by-id` 和 `occupy-count`。`child-hc-count` 是草稿，不执行、不用 raw API 代替。

## 编制对象的固定字段

| 对象 | 字段 | 字段类型 | 业务含义 | 适用结果 | 关键约束 |
| --- | --- | --- | --- | --- | --- |
| 编制部门记录 | `id` / `hcDepartmentId` | 文本标识 | 编制部门记录标识 | `headcount-department search` | 不能用普通 `departmentId` 替代 |
| 编制部门记录 | `departmentId` / `departmentPathName` | 整数标识 / 文本 | 对应部门及路径名称 | search 结果 | `departmentId` 只作为部门引用 |
| 编制方案 | `hcYearId` / `hcYearPlanId` | 整数标识 / 文本标识 | 年度和方案标识 | search 结果 | 必须来自同一结果 |
| 编制周期 | `hcPlanPeriodId` / `startDate` / `endDate` | 文本标识 / 日期 | 计划适用周期 | search 结果 | 不等于查询执行时间 |
| 编制周期 | `hcPlanPeriodDate` | 文本 | 面向展示的周期日期文本 | search 结果 | 仅作为展示，不替代周期 ID |
| 编制部门记录 | `totalHcCount` / `directHcCount` | 整数 | 总计划/直属计划编制数 | search 结果 | 不等于占编数量 |
| 编制部门记录 | `totalHcBudget` / `directHcBudget` | 小数 | 总预算/直属预算 | search 结果 | 不是薪资成本 |
| 编制部门记录 | `publishStatus` | 整数 | `0=待发布`、`1=已发布` | search 结果 | 发布不等于审批完成 |
| 编制部门记录 | `controlDegree` | 整数 | `1=强管控`、`2=弱提醒` | search 请求/结果（若返回） | 只接受命令公开值 |
| 编制部门记录 | `maintainType` | 整数 | `1=分别维护部门编制`、`2=只维护部门直属编制` | search 请求/结果（若返回） | 只接受命令公开值 |
| 编制部门记录 | `isIndependentCalculate` / `isDimension` | 布尔值 | 独立核算/允许维度细分 | search/by-id 结果 | `true` 不等于已有维度数据 |
| 编制部门记录 | `dimensionDetails` | 对象集合 | 按控编维度拆解的明细 | search 结果（若返回） | 嵌套字段以实际返回为准 |
| 编制部门记录 | `planDetail` | 对象 | 所属编制方案详情 | search 结果（若返回） | 子字段以实际返回为准，不把方案详情当部门记录 |
| 编制部门记录 | `overHcBudgetType` / `overDirectHcType` / `overDirectHcBudgetType` | 整数 | 总/直属编制或预算超额类型 | search 结果（若返回） | 只按返回 code 解释；不能替代具体金额 |
| 控编维度 | `dataIndex` / `key` / `title` | 文本 | 字段 code、稳定键和展示名 | `by-id` | 不从标题猜 code |
| 控编维度 | `filter` / `filterConfig` | 布尔值 / 结构化值 | 是否可过滤及配置 | `by-id` | 子结构开放 |
| 控编维度 | `searchMode` / `operator` | 文本 | 条件组合/匹配操作 | `occupy-count` | 当前公开值 `AND/OR`、`IN/EQUALS` |
| 控编维度 | `fieldName` | 文本 | 参与计算的字段 code | `occupy-count` | 必须来自已确认定义 |
| 控编维度 | `fieldValue` | 文本集合 | 维度业务值集合 | `occupy-count` | 不自行补默认值 |
| 占编结果 | `dimensionOccupyCount` | 整数 | 指定维度条件下占编数量 | `occupy-count` | 不替代计划编制或在职人数 |

### 动态维度发现

编制控编维度是具体编制记录的动态结构，不是通用组织自定义字段。必须沿 `search -> by-id -> occupy-count` 获取真实 `fieldName`、操作符和值；当前没有公开的任意组织自定义字段列表命令。无法取得真实维度定义时，停止对应占编查询，不根据标题或常识猜测。
