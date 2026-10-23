# Organization 公开命令导航

本表覆盖当前生产 `ihr-organization` Skill 的 19 个 Shortcut 和 4 个已注册 metadata command。它回答“哪个命令表达哪个业务目标、返回什么形状、有哪些关键边界”，不复制完整 flags。执行前读取具体命令 `--help`；Shortcut 查询对应的精确 Shortcut Schema，metadata command 查询该命令对应的 Schema。

## 契约优先级

1. `--help` 是当前 flags、输入方式和默认值的事实源。
2. 命令级 Schema 是已公开输入/输出结构的事实源；若只暴露元数据摘要，不得宣称完整结构。
3. 本目录下的命令 Reference 只补业务含义、返回摘要和已确认的安全边界。
4. 事实冲突时以运行时 Help/Schema 为准，并报告契约漂移；任一侧不完整时保持 `PARTIAL`。

## 组织结构

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询递归组织树 / 组织树节点 | `ihr-cli organization +orgTree` | Shortcut | 起点、层级、停用/虚拟节点、生效日期 | Help + [组织树命令](../commands/org-tree.md) | [组织树命令](../commands/org-tree.md) | `TREE`；节点通过 `children` 递归嵌套 | `PARTIAL`；只读、当前确认范围、不自动递归追加 |
| 查询直属子部门 / 部门 | `ihr-cli organization +departmentChildren` | Shortcut | `department-id` | Help + [直属子部门命令](../commands/department-children.md) | [直属子部门命令](../commands/department-children.md) | 根节点或指定部门的一层 `subDepartments` | `PARTIAL`；根节点不是可猜测的部门 ID |
| 查询部门祖先链 / 部门 | `ihr-cli organization +departmentAncestors` | Shortcut | `department-id` | Help + [部门祖先命令](../commands/department-ancestors.md) | [部门祖先命令](../commands/department-ancestors.md) | 当前部门及其父级列表 | `PARTIAL`；结果包含目标部门自身 |

## 职位、职务与职级

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 筛选职位实例 / 职位 | `ihr-cli organization +positions` | Shortcut | 部门、职务、职级、状态、日期、分页 | Help + [职位命令](../commands/positions.md) | [职位命令](../commands/positions.md) | `PAGE_RESULT`；返回职位及组织引用摘要 | `PARTIAL`；职位、职务、职级 ID 不互换；统计分析、明确全量或完整拉取可串行翻页 |
| 查询职务类型 / 职务类型 | `ihr-cli organization +jobCategories` | Shortcut | 无业务参数 | Help + [职务类型命令](../commands/job-categories.md) | [职务类型命令](../commands/job-categories.md) | `LIST`；分类定义列表 | `PARTIAL`；分类不等于具体职务 |
| 查询职务定义 / 职务 | `ihr-cli organization +jobTitles` | Shortcut | 名称、编码、职务类型、分页 | Help + [职务命令](../commands/job-titles.md) | [职务命令](../commands/job-titles.md) | `PAGE_RESULT`；职务定义及职级范围 | `PARTIAL`；职务不等于部门下职位；统计分析、明确全量或完整拉取可串行翻页 |
| 查询职级体系 / 职级体系 | `ihr-cli organization +gradeSystems` | Shortcut | 体系条件 | Help + [职级体系命令](../commands/grade-systems.md) | [职级体系命令](../commands/grade-systems.md) | `LIST`；职级体系摘要 | `PARTIAL`；后端不承诺分页 |
| 查询租户职级设置 / 职级设置 | `ihr-cli organization +gradeSystemSetting` | Shortcut | 无业务参数 | Help + [职级设置命令](../commands/grade-system-setting.md) | [职级设置命令](../commands/grade-system-setting.md) | `OBJECT`；当前租户职级设置 | `PARTIAL`；空对象不代表没有体系 |
| 查询职级体系树 / 职级体系 | `ihr-cli organization +gradeSystemTree` | Shortcut | 体系、职位、部门、职务条件 | Help + [职级树命令](../commands/grade-system-tree.md) | [职级树命令](../commands/grade-system-tree.md) | `TREE`；职级节点及层级摘要 | `PARTIAL`；过滤 ID 必须已确认 |
| 查询职级序列 / 职级序列 | `ihr-cli organization +gradeSequences` | Shortcut | 体系和序列条件 | Help + [职级序列命令](../commands/grade-sequences.md) | [职级序列命令](../commands/grade-sequences.md) | `LIST`；序列摘要 | `PARTIAL`；`page/size` 不代表可靠分页 |
| 查询职级序列精简列表 / 职级序列 | `ihr-cli organization +gradeSequenceList` | Shortcut | 可选体系/序列条件 | Help + [职级序列精简命令](../commands/grade-sequence-list.md) | [职级序列精简命令](../commands/grade-sequence-list.md) | `LIST`；不展开序列下职级 | `PARTIAL`；不自动补查详情 |
| 查询职层 / 职层 | `ihr-cli organization +gradeLevels` | Shortcut | 职层条件 | Help + [职层命令](../commands/grade-levels.md) | [职层命令](../commands/grade-levels.md) | `LIST`；职层定义列表 | `PARTIAL`；不承诺分页 |
| 查询职层排序 / 职层排序 | `ihr-cli organization +gradeLevelSortList` | Shortcut | 无业务参数 | Help + [职层排序命令](../commands/grade-level-sort-list.md) | [职层排序命令](../commands/grade-level-sort-list.md) | `LIST`；排序配置 | `PARTIAL`；不等于职级树 |
| 查询职级分组 / 职级分组 | `ihr-cli organization +positionGrades` | Shortcut | 分组和序列条件 | Help + [职级分组命令](../commands/position-grades.md) | [职级分组命令](../commands/position-grades.md) | `LIST`；分组及嵌套职级摘要 | `PARTIAL`；raw ID/code 不自动改写 |
| 查询单层职级 / 单层职级 | `ihr-cli organization +positionGradeList` | Shortcut | 可选序列 ID | Help + [单层职级命令](../commands/position-grade-list.md) | [单层职级命令](../commands/position-grade-list.md) | `LIST`；单层职级列表 | `PARTIAL`；序列 ID 必须已确认 |

## 汇报、地点与成本中心

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询员工汇报关系 / 汇报关系 | `ihr-cli organization +reportToTree` | Shortcut | 唯一员工、汇报类型 | Help + [汇报树命令](../commands/report-to-tree.md) | [汇报树命令](../commands/report-to-tree.md) | `TREE`；员工关系节点 | `PARTIAL`；不是部门树，汇报类型需动态解析 |
| 查询公司工作地点 / 工作地点 | `ihr-cli organization +companySites` | Shortcut | 名称、地区、类型、分页 | Help + [地点命令](../commands/company-sites.md) | [地点命令](../commands/company-sites.md) | `PAGE_RESULT`；地点定义列表 | `PARTIAL`；地区 code 不自动改写，地点不是部门；统计分析、明确全量或完整拉取可串行翻页 |
| 查询成本中心 / 成本中心 | `ihr-cli organization +costCenters` | Shortcut | 条件、排序、分页 | Help + [成本中心命令](../commands/cost-centers.md) | [成本中心命令](../commands/cost-centers.md) | `PAGE_RESULT`；成本中心定义列表 | `PARTIAL`；`criteria/orders` 仅使用公开字段；统计分析、明确全量或完整拉取可串行翻页 |
| 查询成本中心分组 / 成本中心分组 | `ihr-cli organization +costCenterGroups` | Shortcut | 无业务参数 | Help + [成本中心分组命令](../commands/cost-center-groups.md) | [成本中心分组命令](../commands/cost-center-groups.md) | `LIST`；成本中心分组列表 | `PARTIAL`；分组不是成本中心记录 |

## 编制 metadata command

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询编制部门记录 / 编制部门记录 | `ihr-cli organization headcount-department search` | Metadata | 年度、日期、管控方式、分页 | Help + Schema + [编制命令](../commands/headcount.md) | Schema + [编制命令](../commands/headcount.md) | `PAGE_RESULT`；`response.body.data.content` 及分页统计 | `PARTIAL`；当前编制数据范围，只读；统计分析、明确全量或完整拉取可串行翻页、禁止并发 |
| 查询移除部门提示 / 编制方案 | `ihr-cli organization headcount-department reduce-list` | Metadata | 已确认编制年度 ID | Help + Schema + [编制命令](../commands/headcount.md) | Schema + [编制命令](../commands/headcount.md) | `LIST`；方案移除部门提示 | `PARTIAL`；ID 必须来自已确认年度，不猜测 |
| 读取编制维度 / 编制维度 | `ihr-cli organization headcount-dimension by-id` | Metadata | 已确认编制记录 ID | Help + Schema + [编制命令](../commands/headcount.md) | Schema + [编制命令](../commands/headcount.md) | `OBJECT`；维度详情 | `PARTIAL`；ID 必须来自已确认 search 结果 |
| 计算占编数量 / 占编结果 | `ihr-cli organization headcount-dimension occupy-count` | Metadata | 编制部门 ID、控编维度 | Help + Schema + [编制命令](../commands/headcount.md) | Schema + [编制命令](../commands/headcount.md) | `OBJECT`；服务端占编计算结果 | `PARTIAL`；ID 必须已确认，空维度不等于部门总人数 |

`organization headcount-dimension child-hc-count` 当前为 `DRAFT` 且未注册，不在公开命令表中。
