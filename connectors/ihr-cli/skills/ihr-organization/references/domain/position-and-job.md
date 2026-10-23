# 职位与职务

## 三个不同概念

| 概念 | 业务含义 | 典型标识 | 常见误用 |
| --- | --- | --- | --- |
| 职位（Position） | 组织中的具体岗位实例，通常属于一个部门，可配置容量和启停/生效状态 | `positionId`、`positionCode` | 把职位名称当成职务定义 |
| 职务（Job Title） | 对工作性质或专业角色的定义，可被多个职位引用 | `jobTitleId`、`jobTitleCode` | 把职务当成部门中的岗位实例 |
| 职务类型（Job Category） | 对职务的分类或族群 | `jobCategoryId`、`jobCategoryCode` | 把分类当作具体职务 |

职位通常引用部门、职务和职级，但返回是否有完整引用字段以命令契约为准。名称相同不代表 ID 相同，也不代表属于同一部门。

## 查询策略

1. 用户要“有哪些岗位/某部门岗位”时使用 `organization +positions`，明确部门、状态和生效日期。
2. 用户要“职务定义/职务类型”时使用 `organization +jobTitles` 或 `organization +jobCategories`。
3. 用户要解释一个职位的完整上下文时，先以职位 ID 或唯一候选锁定职位，再根据返回的 `departmentId`、`jobTitleId` 和 `positionGradeId` 定向读取相关定义；不能从名称直接拼接关系。
4. 列表命令的 `page` 从 1 开始；普通查询只读取当前确认页。统计分析类目标按共享分页规则串行翻页，禁止并发请求。

## 范围和状态

- `positionState=ENABLE/DISABLE/ALL` 只解释职位启停筛选；`ALL` 是扩大到停用职位，不等于所有历史职位。
- `effectiveDateBefore/After` 是职位筛选条件；不能用它回答员工何时任职或岗位历史变更。
- 返回的 `capacity`/`positionNumberStaff*` 是职位配置或查询字段，不等于已占编人数。

## 职位、职务与职务类型对象的固定字段

### 职位

| 字段 | 字段类型 | 业务含义 | 适用结果 | 关键约束 |
| --- | --- | --- | --- | --- |
| `id` / `positionId` | `string` | 职位实例标识 | `+positions` | 当前结果为字符串；名称相同不代表同一职位 |
| `companyId` | `string` | 职位所属公司标识 | `+positions`（若返回） | 由登录上下文决定，不作为用户筛选条件 |
| `positionName` / `positionCode` | `string` | 职位名称/编码 | `+positions` | 不替代职位 ID |
| `abbreviation` | `string` | 职位简称 | `+positions`（若返回） | 不替代正式名称 |
| `departmentId` / `departmentName` | `number` / `string` | 职位所属部门及名称 | `+positions` | 当前部门标识为整数；不证明员工在该部门任职 |
| `jobTitleId` / `jobTitleName` | `string` / `string` | 职务引用及名称摘要 | `+positions` | 当前引用标识为字符串；职务不是职位实例 |
| `positionGradeId` / `positionGradeName` | `string` / `string` | 单层职级引用及名称 | `+positions` | 当前引用标识为字符串；不等于薪资或绩效等级 |
| `positionState` | `string` | 职位启停状态 | `+positions` | `ALL` 不代表全部历史 |
| `effectiveDate` | `string(date)` | 职位定义生效日 | `+positions` | 不等于员工任职生效日 |
| `capacity` | `number` | 职位容量摘要 | `+positions` | 不等于实际任职人数 |
| `description` | `string` | 职位职责描述 | `+positions`（若返回） | 描述文本不等于员工任职事实 |
| `qualifications` | `string` | 职位任职资格 | `+positions`（若返回） | 不等于员工已具备的资格 |
| `parentId` | `string` | 父级职位引用 | `+positions` | 当前结果为字符串；仅在真实返回时使用 |
| `appliedRange` | `string`（响应）／`array<departmentId>`（请求筛选） | 职位适用组织范围 code；请求侧也可按部门 ID 列表筛选 | `+positions` | 响应与请求使用不同结构，不能混用 |
| `appliedRangeMap` | 结构化值 | 行政组织适用范围映射 | `+positions` | 只按实际返回的组织范围解释；不把键名当作职位 ID |
| `appliedRangeDimensionMap` | 结构化值 | 多维组织适用范围映射 | `+positions` | 子键格式必须有命令契约或实际结果支持 |
| `isPositionGroup` | `boolean` | 是否为职位小组 | `+positions` | 当前结果为布尔值；不等于部门或职位状态 |
| `instructions` | `array<string>` | 职位说明书附件标识集合 | `+positions`（若返回） | 仅为附件引用，不把文件 ID 当职位属性或员工资格 |
| `positionInstructionVOList` | `array<object>` | 职位说明书附件信息 | `+positions`（若返回） | 子字段以实际返回为准 |

### 职务

| 字段 | 字段类型 | 业务含义 | 适用结果 |
| --- | --- | --- | --- |
| `id` / `jobTitleId` | `string` | 职务定义标识 | `+jobTitles` | 当前结果为字符串；不与职务类型 ID 混用 |
| `companyId` | `string` | 职务所属公司标识 | `+jobTitles`（若返回） | 由登录上下文决定 |
| `jobTitleName` / `jobTitleCode` | `string` | 职务名称/编码 | `+jobTitles` |
| `abbreviation` | `string` | 职务简称 | `+jobTitles`（若返回） | 不替代正式名称 |
| `jobCategoryId` | `string` | 职务类型引用 | `+jobTitles` | 当前结果为字符串；指向职务类型对象 |
| `minPositionGradeId` / `maxPositionGradeId` | `string` | 允许职级范围 | `+jobTitles` | 当前引用标识为字符串 |
| `minPositionGradeName` / `maxPositionGradeName` | `string` | 允许职级范围名称 | `+jobTitles`（若返回） | 名称不替代职级 ID |
| `effectiveDate` | `string(date)` | 职务定义生效日 | `+jobTitles` |
| `positionSalaryGrade` | `string` | 职务薪级定义 | `+jobTitles`（若返回） | 不等于员工薪资档案中的薪级值 |
| `description` | `string` | 职务描述 | `+jobTitles`（若返回） | 仅解释职务定义 |

### 职务类型

| 字段 | 字段类型 | 业务含义 | 适用结果 |
| --- | --- | --- | --- |
| `id` / `jobCategoryId` | `string` | 职务类型标识 | `+jobCategories` | 当前结果为字符串；不与职务定义 ID 混用 |
| `jobCategoryName` / `jobCategoryCode` | `string` | 职务类型名称/编码 | `+jobCategories` |

命令返回仍为 `PARTIAL`；未声明的职位说明书、职责或扩展属性不在本目录中。
