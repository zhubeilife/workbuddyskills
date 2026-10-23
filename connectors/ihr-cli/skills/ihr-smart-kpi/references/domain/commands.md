# Smart KPI 命令导航

本文件列出当前 Smart KPI Skill 的全部真实命令，用于选择命令和了解返回范围，不复制所有 flags。完整 flags 以具体命令 `--help` 为准；Shortcut 的机器输入/输出结构使用对应的精确 `ihr-cli schema smart-kpi ... +<action>`，业务 Reference 只补充 Schema 未覆盖的输入语义、返回摘要和业务边界。

## 契约读取顺序

1. 准备执行任何 Smart KPI 命令前，先在下表定位相关命令条目一次。
2. 按条目中的输入来源和输出来源读取具体命令 `--help` 和命令 Reference。
3. Help 与 Reference 冲突时以 Help 为准并报告文档漂移。
4. 命令不存在或目标需要未声明动作时停止，不使用 raw API 补齐。

完整性含义：`COMPLETE` 表示输入输出均有完整机器契约；`PARTIAL` 表示只能安全使用已声明或已审核的子集。

## 绩效待办

这两个命令均为当前登录人范围内的只读租户数据查询，不接受 JSON/stdin、身份字段或任意后端查询条件。

| 业务动作 / 主结果 | 命令 | 输入来源 | 输出来源 | 完整性 | 返回摘要与关键边界 |
| --- | --- | --- | --- | --- | --- |
| 查询绩效待办汇总 | `ihr-cli smart-kpi todo +summary` | Help + [命令契约](../commands/todo/summary.md) | [命令契约](../commands/todo/summary.md) | `COMPLETE` | 原生总数、10 类计数、分类合计和一致性；非零分类单独列出 |
| 查询考核评分待办 | `ihr-cli smart-kpi todo +score` | Help + [命令契约](../commands/todo/score.md) | [命令契约](../commands/todo/score.md) | `PARTIAL` | 单页评分待办及分页信息；按三字段页内去重，内部 ID 默认隐藏 |

## 绩效结果

这些命令均为只读、敏感、租户级组合查询。

| 业务动作 / 主结果 | 命令 | 输入来源 | 输出来源 | 完整性 | 返回摘要与关键边界 |
| --- | --- | --- | --- | --- | --- |
| 查询员工绩效结果总览 | `ihr-cli smart-kpi result +staff-overview` | Help + [命令契约](../commands/performance/result-staff-overview.md) | [命令契约](../commands/performance/result-staff-overview.md) | `PARTIAL` | 按任务分组的员工结果摘要；空范围先确认 |
| 查询组织绩效结果总览 | `ihr-cli smart-kpi result +org-overview` | Help + [命令契约](../commands/performance/result-org-overview.md) | [命令契约](../commands/performance/result-org-overview.md) | `PARTIAL` | 按任务分组的组织结果摘要；不接受员工条件 |
| 查询员工考核得分明细 | `ihr-cli smart-kpi score +staff-detail` | Help + [命令契约](../commands/performance/score-staff-detail.md) | [命令契约](../commands/performance/score-staff-detail.md) | `PARTIAL` | 员工维度、项目、指标和动态字段；任一步失败整体失败 |
| 查询组织考核得分明细 | `ihr-cli smart-kpi score +org-detail` | Help + [命令契约](../commands/performance/score-org-detail.md) | [命令契约](../commands/performance/score-org-detail.md) | `PARTIAL` | 组织维度、项目、指标和动态字段；不接受员工条件 |
| 查询员工评估人总览 | `ihr-cli smart-kpi appraiser +staff-overview` | Help + [命令契约](../commands/performance/appraiser-staff-overview.md) | [命令契约](../commands/performance/appraiser-staff-overview.md) | `PARTIAL` | 节点、评估人角色和维度总评，不含指标明细 |
| 查询组织评估人总览 | `ihr-cli smart-kpi appraiser +org-overview` | Help + [命令契约](../commands/performance/appraiser-org-overview.md) | [命令契约](../commands/performance/appraiser-org-overview.md) | `PARTIAL` | 组织评估人及维度总评，不含指标明细 |
| 查询员工评估人评分明细 | `ihr-cli smart-kpi appraiser +staff-score-detail` | Help + [命令契约](../commands/performance/appraiser-staff-score-detail.md) | [命令契约](../commands/performance/appraiser-staff-score-detail.md) | `PARTIAL` | 每位评估人的维度、项目和指标评分 |
| 查询组织评估人评分明细 | `ihr-cli smart-kpi appraiser +org-score-detail` | Help + [命令契约](../commands/performance/appraiser-org-score-detail.md) | [命令契约](../commands/performance/appraiser-org-score-detail.md) | `PARTIAL` | 每位评估人的组织维度、项目和指标评分 |

绩效命令共享的完整筛选参数、结果路径和资源上限见[绩效查询命令](../commands/performance/reports.md)。

## 任务进度与催办

| 业务动作 | 命令 | 输入来源 | 输出来源 | 完整性 | 返回摘要与关键边界 |
| --- | --- | --- | --- | --- | --- |
| 查询任务及当前节点 | `ihr-cli smart-kpi task-progress +scan` | Help + [命令契约](../commands/task-manage/task-progress-scan.md) | 同上 | `PARTIAL` | 内部解析年度/周期并精确查任务；不判断异常；生成受控上下文令牌 |
| 查询节点待处理人员 | `ihr-cli smart-kpi task-progress +staff` | Help + [命令契约](../commands/task-manage/task-progress-staff.md) | 同上 | `PARTIAL` | 返回后端 `stayDays` 和稳定人员序号；令牌必须来自 `+scan` |
| 催办选定人员 | `ihr-cli smart-kpi task-progress +urge` | Help + [命令契约](../commands/task-manage/task-progress-urge.md) | 同上 | `PARTIAL` | 传入异常人员序号，先预览，明确 `--yes` 后批量催办；不自动重新查询 |

## 指标模板配置与导入

以下命令均已在 Runtime 注册，并用于指标模板查询、公式校验、保存和文件导入编排。治理清单中的 HOLD 只表示命令合同证据未完成，不阻止本 Skill 按原导入流程使用这些命令。

| 业务动作 / 主对象 | 命令 | 输入来源 | 输出来源 | 完整性 | 返回摘要与关键边界 |
| --- | --- | --- | --- | --- | --- |
| 选择考核模板 | `ihr-cli smart-kpi template +list` | Help + [命令契约](../commands/norm-template/template-list.md) | [命令契约](../commands/norm-template/template-list.md) | `PARTIAL` | 文件解析前确认考核模板 |
| 读取新建指标模板结构 | `ihr-cli smart-kpi norm-template +struct` | Help + [命令契约](../commands/norm-template/norm-template-struct.md) | [命令契约](../commands/norm-template/norm-template-struct.md) | `PARTIAL` | 新建底稿；不能替代更新详情 |
| 查询现有指标模板 | `ihr-cli smart-kpi norm-template +list` | Help + [命令契约](../commands/norm-template/norm-template-list.md) | [命令契约](../commands/norm-template/norm-template-list.md) | `PARTIAL` | 按页串行读取完整列表，辅助新增/更新判断 |
| 读取指标模板完整详情 | `ihr-cli smart-kpi norm-template +detail` | Help + [命令契约](../commands/norm-template/norm-template-detail.md) | [命令契约](../commands/norm-template/norm-template-detail.md) | `PARTIAL` | 更新底稿和写后回读 |
| 查询指标分类树 | `ihr-cli smart-kpi norm-category +tree` | Help + [命令契约](../commands/norm-template/norm-category-tree.md) | [命令契约](../commands/norm-template/norm-category-tree.md) | `PARTIAL` | 遇到 `NORM_TYPE` 时解析分类 |
| 查询合法计量单位 | `ihr-cli smart-kpi unit +list` | Help + [命令契约](../commands/norm-template/unit-list.md) | [命令契约](../commands/norm-template/unit-list.md) | `PARTIAL` | 单位名称必须唯一解析 |
| 批量匹配指标库引用 | `ihr-cli smart-kpi norm-library +quote-search` | Help + [命令契约](../commands/norm-template/norm-library-quote-search.md) | [命令契约](../commands/norm-template/norm-library-quote-search.md) | `PARTIAL` | 按编码或名称精确匹配 |
| 校验单条公式 | `ihr-cli smart-kpi formula +check` | Help + [命令契约](../commands/norm-template/formula-check.md) | [命令契约](../commands/norm-template/formula-check.md) | `PARTIAL` | 返回结构化校验结果；exit 0 不等于公式通过 |
| 校验字段公式集合 | `ihr-cli smart-kpi formula +field-check` | Help + [命令契约](../commands/norm-template/formula-field-check.md) | [命令契约](../commands/norm-template/formula-field-check.md) | `PARTIAL` | 检查当前字段完整性和循环依赖；不保存 |
| 保存完整指标模板 | `ihr-cli smart-kpi norm-template +save` | Help + [命令契约](../commands/norm-template/norm-template-save.md) | [命令契约](../commands/norm-template/norm-template-save.md) | `PARTIAL` | 写入、敏感、租户级、单模板；dry-run 后逐模板确认，成功返回 ID 供 `+detail` 保存后回读 |

从客户文件导入指标模板时，按 [导入流程](../use-cases/norm-template-import/guide.md) 编排上表命令，不要改走 raw API。


## 计量单位管理

| 业务动作 | 命令 | 参数来源 | 公开契约 | 关键边界 |
| --- | --- | --- | --- | --- |
| 查询已启用单位 | `ihr-cli smart-kpi unit +list` | Help + [命令契约](../commands/norm-template/unit-list.md) | PARTIAL | 不分页；导入与管理共用 |
| 读取单位详情 | `ihr-cli smart-kpi unit +detail` | Help + [命令契约](../commands/unit/unit-detail.md) | PARTIAL | ID 来自本会话列表 |
| 新建或更新单位 | `ihr-cli smart-kpi unit +save` | Help + [命令契约](../commands/unit/unit-save.md) | PARTIAL | dry-run 后 --confirm；void 成功 |

## 指标库管理

| 业务动作 | 命令 | 输入来源 | 完整性 | 关键边界 |
| --- | --- | --- | --- | --- |
| 分页查询指标库 | `ihr-cli smart-kpi norm-library +page` | Help + [命令契约](../commands/norm-library/norm-library-page.md) | PARTIAL | 必须选库类型；page-size 默认/最大 1000 |
| 读取指标详情 | `ihr-cli smart-kpi norm-library +detail` | Help + [命令契约](../commands/norm-library/norm-library-detail.md) | PARTIAL | ID 来自本会话查询 |
| 保存指标 | `ihr-cli smart-kpi norm-library +save` | Help + [命令契约](../commands/norm-library/norm-library-save.md) | PARTIAL | dry-run 后 --confirm；void 成功 |
| 保存分类 | `ihr-cli smart-kpi norm-category +save` | Help + [命令契约](../commands/norm-library/norm-category-save.md) | PARTIAL | dry-run 后 --confirm |
| 查询字段基础列表 | `ihr-cli smart-kpi field-library +list` | Help + [命令契约](../commands/norm-library/field-library-list.md) | PARTIAL | 新建字段元数据来源 |

## 考核方案管理

考核方案列表、详情和五步配置使用以下命令：`ihr-cli smart-kpi programme +list`、`ihr-cli smart-kpi programme +detail`、`ihr-cli smart-kpi programme +save-basic`、`ihr-cli smart-kpi programme +period`、`ihr-cli smart-kpi programme +save-period`、`ihr-cli smart-kpi programme +scope`、`ihr-cli smart-kpi programme +scope-templates`、`ihr-cli smart-kpi programme +save-scope`、`ihr-cli smart-kpi programme +process`、`ihr-cli smart-kpi programme +process-nodes`、`ihr-cli smart-kpi programme +save-process`、`ihr-cli smart-kpi programme +result-setting`、`ihr-cli smart-kpi programme +grade-rules`、`ihr-cli smart-kpi programme +force-rules`、`ihr-cli smart-kpi programme +department-groups`、`ihr-cli smart-kpi programme +save-result-setting`。完整命令、构参及确认规则见 [考核方案管理](../commands/programme/programme-management.md)。

## 考核模板管理

查询与三步配置、复制和启停。更新已完成模板必须先 `+save-basic`。导入继续只用 `template +list` 选考核模板。

| 业务动作 | 命令 | 输入来源 | 完整性 | 关键边界 |
| --- | --- | --- | --- | --- |
| 分页查考核模板 | `ihr-cli smart-kpi template +list` | Help + [命令契约](../commands/norm-template/template-list.md) | PARTIAL | pageSize 1..100；导入与管理共用 |
| 读基本信息 | `ihr-cli smart-kpi template +detail` | Help + [命令契约](../commands/template/template-detail.md) | PARTIAL | ID 来自本会话 |
| 读项目配置状态 | `ihr-cli smart-kpi template +status` | Help + [命令契约](../commands/template/template-status.md) | PARTIAL | 判断是否已配项目 |
| 读项目配置 | `ihr-cli smart-kpi template +item` | Help + [命令契约](../commands/template/template-item.md) | PARTIAL | 更新底稿 |
| 读权限配置 | `ihr-cli smart-kpi template +process` | Help + [命令契约](../commands/template/template-process.md) | PARTIAL | 拷取 kpiRoleId |
| 按类型取默认字段 | `ihr-cli smart-kpi template +fields-by-type` | Help + [命令契约](../commands/template/template-fields-by-type.md) | PARTIAL | 新建字段 ID 来源 |
| 校验项目字段公式 | `ihr-cli smart-kpi template +validate-fields` | Help + [命令契约](../commands/template/template-validate-fields.md) | PARTIAL | 保存项目前必须；不替代 formula +field-check |
| 保存基本信息 | `ihr-cli smart-kpi template +save-basic` | Help + [命令契约](../commands/template/template-save-basic.md) | PARTIAL | dry-run 后 --confirm；返回 ID |
| 保存项目 | `ihr-cli smart-kpi template +save-item` | Help + [命令契约](../commands/template/template-save-item.md) | PARTIAL | void；非 SETTING 后端拒绝 |
| 保存权限 | `ihr-cli smart-kpi template +save-process` | Help + [命令契约](../commands/template/template-save-process.md) | PARTIAL | void |
| 复制模板 | `ihr-cli smart-kpi template +copy` | Help + [命令契约](../commands/template/template-copy.md) | PARTIAL | 返回新 ID |
| 启停模板 | `ihr-cli smart-kpi template +switch` | Help + [命令契约](../commands/template/template-switch.md) | PARTIAL | void；SETTING 不能启用 |
| 流程候选 | `ihr-cli smart-kpi process +list` | Help + [命令契约](../commands/template/process-list.md) | PARTIAL | 只读；返回 `hasAppointedDateNode` 供方案周期适用性判断 |
| 流程节点详情 | `ihr-cli smart-kpi process +node` | Help + [命令契约](../commands/template/process-node.md) | PARTIAL | 拷角色 ID |
| 等级规则候选 | `ihr-cli smart-kpi grade +list` | Help + [命令契约](../commands/template/grade-list.md) | PARTIAL | 只读 |
| 评分规则候选 | `ihr-cli smart-kpi rating-rule +list` | Help + [命令契约](../commands/template/rating-rule-list.md) | PARTIAL | 只读 |

保存负载联动见 [保存构造](../commands/template/template-save-construction.md)。
### Programme applicability correction

The cycle step uses the process associated with the current programme and the existing process-list field `hasAppointedDateNode`. `process +nodes` is not a command in this contract. `programme +save-period` requires `--programme-id` only to perform this preflight; that value is not forwarded to the backend period list payload.
