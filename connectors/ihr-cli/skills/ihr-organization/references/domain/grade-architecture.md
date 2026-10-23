# 职级架构

## 对象层次

本模块将这些对象分开记录；名称相近不代表可以互换：

1. **职级体系（Grade System）**：租户的一套职级制度及其适用设置。
2. **职级序列（Grade Sequence）**：体系内的序列，例如管理、专业等业务序列；具体名称由租户配置决定。
3. **职层（Grade Level）**：序列或体系中的层级过滤对象；命令返回列表，不承诺分页。
4. **职级分组（Position Grade Group）**：对职级的分组视图。
5. **单层职级（Position Grade）**：可被职位引用的具体职级定义。

以上关系以实际返回字段和当前租户配置为准。不能因为名称中出现“level”“sequence”或“grade”就推断父子关系。

## 读取顺序

当用户要“解释职级体系”时：

1. 读取 `organization +gradeSystemSetting`，理解当前租户设置。
2. 当前没有公开的职位职级切换操作；不能把未公开的定义当作可执行能力或据此判断新旧入口。
3. 需要体系树时使用 `organization +gradeSystemTree`，过滤条件只提交已确认的职位、部门或职务 ID。
4. 需要序列/职层/分组/单层职级清单时，分别使用对应命令；列表返回不一定有分页统计。

## 约束

- `page`/`pageSize` 在若干职级查询中只是兼容 carrier，不能据此承诺分页或自动翻页。
- `allGradeTree` 会扩大体系树范围，只有用户明确需要完整树时使用。
- `functionCode` 是协议值，不是自然语言功能名称；未确认的值不猜测。
- 空树、空列表和空设置对象不能推断“没有职级体系”或“没有权限”。
- 职级定义不等于薪资等级、绩效等级或员工当前任职状态。

## 职级对象的固定字段

职级命令有多个 `LIST` 和一个递归 `TREE`，当前返回完整度为 `PARTIAL`。下表只登记已在命令说明中稳定出现的字段；不能根据 `grade/level/sequence` 字样补出未声明字段。

| 字段 | 字段类型 | 业务含义 | 适用结果 | 关键约束 |
| --- | --- | --- | --- | --- |
| `id` / `gradeSystemId` | `string` | 职级体系标识 | `+gradeSystems`、`+gradeSystemTree` | 当前结果为字符串；不能与序列或职级 ID 互换 |
| `name` / `gradeSystemName` | `string` | 职级体系名称 | 体系列表/树 | 不推断新旧体系 |
| `sequenceId` / `sequenceName` | `string` / `string` | 序列标识/名称 | 序列结果、单层职级筛选 | 当前结果为字符串；不等于职层 |
| `gradeLevelId` / `levelId` | `string` | 职层标识 | 职层结果 | 当前结果为字符串；只定位职层 |
| `gradeLevelName` / `levelName` | `string` | 职层名称 | 职层结果 | 排序不证明父子关系 |
| `positionGradeGroupId` / `groupId` | `string` | 职级分组标识 | 分组结果 | 当前结果为字符串；不等于单层职级 |
| `groupName` | `string` | 职级分组名称 | 分组/单层职级结果 | 不替代分组 ID |
| `positionGradeId` | `string` | 单层职级标识 | 分组/单层结果 | 当前结果为字符串；可被职位引用 |
| `positionGradeName` | `string` | 单层职级名称 | 分组/单层结果 | 不等于薪资等级 |
| `status` | `string` | 体系或分组状态 | 具体结果（若返回） | 不跨对象解释 |
| `sort` / `sortOrder` | `integer` | 展示顺序 | 排序结果（若返回） | 不证明层级关系 |
| `children` | `array<object>` | 职级树下级节点 | `+gradeSystemTree` | 子字段开放 |
| `positionGradeVos` | `array<object>` | 分组中的职级集合 | `+positionGrades` | 数组项字段以返回为准 |

`page/pageSize` 在若干职级命令中是兼容输入，不构成字段目录，也不代表结果可以自动分页。
