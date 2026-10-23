# 地点与成本中心

## 工作地点

工作地点是公司可引用的地点定义，包含名称、国家/省/市/区县 code 和地点类型等字段。地区 code 是层级化业务值，不能把城市名称直接当作 code。地点列表是分页结果；扩大页码或地区范围前需要确认。

## 成本中心

成本中心是财务归集定义，成本中心分组是其组织视图。成本中心不是部门，也不是编制方案；同名成本中心仍需以 ID/code 区分。`criteria` 和 `orders` 是公开 JSON 条件/排序载荷，只能使用已确认的业务字段。

## 边界

- `companySiteId` 和 `costCenterId` 只是引用对象 ID，不应当用来替代部门、职位或员工 ID。
- 地点/成本中心列表为空可能是数据范围、过滤条件或租户配置结果，不能解释为不存在。
- 当前命令只读，不维护地点、成本中心或分组。

## 地点与成本中心对象的固定字段

### 工作地点

| 字段 | 字段类型 | 业务含义 | 适用结果 | 关键约束 |
| --- | --- | --- | --- | --- |
| `id` / `companySiteId` | `string` | 地点标识 | `+companySites` | 当前结果为字符串；名称不替代 ID |
| `siteName` | `string` | 地点名称 | `+companySites` | 同名仍需区分 |
| `country` / `province` / `city` / `district` | `string` | 国家、省、市、区县 code | `+companySites` | 只能提交已确认 code |
| `address` | `string` | 地点详细地址 | `+companySites`（若返回） | 不等于考勤打卡地址 |
| `siteType` | `string` | 地点类型 code | `+companySites` | 不从中文名称猜 code |
| `remark` | `string` | 地点描述 | `+companySites`（若返回） | 只作为业务文本 |

### 成本中心与分组

| 字段 | 字段类型 | 业务含义 | 适用结果 | 关键约束 |
| --- | --- | --- | --- | --- |
| `id` / `costCenterId` | `string` | 成本中心标识 | `+costCenters` | 不等于部门 ID |
| `costName` | `string` | 成本中心名称 | `+costCenters` | 名称不替代 ID |
| `costCode` | `string` | 成本中心编码 | `+costCenters` | 不自动解析为部门 |
| `isValid` | `boolean` | 成本中心有效状态 | `+costCenters` | 不推出引用对象状态 |
| `remark` | `string` | 成本中心说明 | `+costCenters`（若返回） | 仅作为业务文本，不改变成本归集关系 |
| `groupId` | `string` | 所属成本中心分组标识 | `+costCenters`（若返回） | 不等于部门 ID；以实际返回为准 |
| `groupName` / `groupCode` | `string` | 所属分组名称/编码 | `+costCenters`（若返回） | 不能用编码替代分组标识 |
| `id` | `string` | 成本中心分组标识 | `+costCenterGroups`（若返回） | 当前结果为字符串；不与成本中心 ID 混用 |
| `name` / `code` | `string` | 分组名称/编码 | `+costCenterGroups`（若返回） | 分组不等于成本中心 |
| `sort` | `integer` | 分组排序值 | `+costCenterGroups`（若返回） | 仅用于分组排序 |
| `count` | `integer` | 分组下成本中心数量摘要 | `+costCenterGroups`（若返回） | 不等于员工人数或成本金额 |
