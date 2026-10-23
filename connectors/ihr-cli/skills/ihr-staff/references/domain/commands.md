# Staff 公开命令导航

本文件覆盖当前真实公开且允许 Agent 执行的 Staff 命令。它用于选命令、确认返回范围和定位契约，不复制完整 flags。

## 契约读取规则

1. 准备执行命令前只定位相关条目一次；自然语言目标定位相关分组，显式命令只定位对应行。
2. flags 和输入方式先读取具体命令 `--help`；Shortcut 查询对应的精确 Shortcut Schema，metadata command 再读取该命令对应的 Schema。
3. 本表指向的命令 Reference 只补当前 Help/Schema 未完整表达的业务输入、返回摘要和安全边界。
4. Help 与 Reference 冲突时以 Help 为准；Schema 与 Reference 冲突时以 Schema 为准，并报告契约漂移。
5. `COMPLETE` 只表示输入、输出都有完整机器契约；当前条目均存在输出开放对象、Shortcut Schema 缺口或 metadata Schema 暴露不完整，因此标记 `PARTIAL`，只使用已声明子集。

当前 metadata Schema 的精确查询可能只暴露命令元数据摘要，不能默认视为完整的输入/输出 Schema。只有运行时实际返回并覆盖字段结构的部分才可作为 Schema 事实；其余内容必须沿用明确标记的过渡 Reference，并保持 `PARTIAL`。

## 花名册与字段结构

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询员工花名册 / 员工信息 | `ihr-cli staff +search` | Shortcut | 人员、部门、状态、字段、分页 | Help + [花名册命令](../commands/roster.md) | [花名册命令](../commands/roster.md) | `response.data.list` 分页及 `response.data.totalElements` 总数；字段受权限和 `fields` 影响 | `PARTIAL`；普通查询当前页，统计分析、明确全量或完整拉取按受控规则串行翻页、禁止并发 |
| 查询单员工详情 / 员工信息 | `ihr-cli staff +get` | Shortcut | `staff-id` | Help + [花名册命令](../commands/roster.md) | [花名册命令](../commands/roster.md) | 单员工 `response` | `PARTIAL`；必须唯一 `staffId` |
| 查询 Flex Meta 列表 / 元数据 | `ihr-cli staff +flexMetaList` | Shortcut | `kind` | Help + [Flex Meta 命令](../commands/flex-meta.md) | [Flex Meta 命令](../commands/flex-meta.md) | 当前租户过滤后的元数据列表 | `PARTIAL`；只读、租户级、按需一次 |
| 查询 Flex Meta 详情 / 元数据 | `ihr-cli staff flex-meta get` | Metadata | `meta-data-id` | Help + Schema + [Flex Meta 命令](../commands/flex-meta.md) | Schema + [Flex Meta 命令](../commands/flex-meta.md) | 一份 FlexMetaData 详情及字段配置 | `PARTIAL`；`MEDIUM / CONFIRM_REQUIRED`；可能包含更新操作人手机号，接口无独立功能权限/员工数据范围保护 |
| 查询 Flex Meta 详情 / 元数据 | `ihr-cli staff +flexMetaGet` | Shortcut | `meta-data-id` | Help + [Flex Meta 命令](../commands/flex-meta.md) | [Flex Meta 命令](../commands/flex-meta.md) | 一份 FlexMetaData 详情及字段配置 | `PARTIAL`；`MEDIUM / CONFIRM_REQUIRED`；兼容入口，可能包含更新操作人手机号，接口无独立功能权限/员工数据范围保护 |
| 查询可排序字段 / 元数据 | `ihr-cli staff +flexMetaSortableFields` | Shortcut | `meta-data-id` | Help + [Flex Meta 命令](../commands/flex-meta.md) | [Flex Meta 命令](../commands/flex-meta.md) | 可排序字段列表 | `PARTIAL`；只读，不等于完整字段详情 |
| 查询平铺选项 / 字段选项 | `ihr-cli staff +flexMetaValueList` | Shortcut | `code-value-id`、父项、停用过滤 | Help + [Flex Meta 命令](../commands/flex-meta.md) | [Flex Meta 命令](../commands/flex-meta.md) | 平铺选项，使用 `codeValue/displayName/isValid` 已声明子集 | `PARTIAL`；只读、名称多匹配先确认 |
| 查询树形选项 / 字段选项 | `ihr-cli staff +flexMetaValueTree` | Shortcut | `code-type-id`、`group-code` | Help + [Flex Meta 命令](../commands/flex-meta.md) | [Flex Meta 命令](../commands/flex-meta.md) | 树形选项结构 | `PARTIAL`；只读、不补查其他组 |

## 员工档案与标签

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询固定或自定义档案列表 / 档案记录 | `ihr-cli staff +archiveList` | Shortcut | `meta-data-code/type`、条件、排序、分页 | Help + [员工档案命令](../commands/archives.md) | [员工档案命令](../commands/archives.md) | 所选档案分支的分页结果 | `PARTIAL`；固定白名单与 `SUBSET` 不混用；统计分析、明确全量或完整拉取可串行翻页 |
| 查询单员工自定义子集 / 档案记录 | `ihr-cli staff +archiveGet` | Shortcut | `staff-id`、最多五个 `metaCode`、`SUBSET` | Help + [员工档案命令](../commands/archives.md) | [员工档案命令](../commands/archives.md) | 单员工一个或多个自定义子集 | `PARTIAL`；只读、唯一员工 |
| 查询员工已有标签 / 员工标签记录 | `ihr-cli staff +tags` | Shortcut | `staff-id` | Help + [员工业务记录命令](../commands/employee-business-records.md) | [员工业务记录命令](../commands/employee-business-records.md) | 当前已有标签列表 | `PARTIAL`；不包含标签定义和写入 |

## 待入职查询与写入

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询待入职、已确认或已放弃 / 待入职表单 | `ihr-cli staff entry +search` | Shortcut | `state`、人员、部门、字段、分页 | Help + [入职查询命令](../commands/entry-query.md) | [入职查询命令](../commands/entry-query.md) | 入职表单分页结果 | `PARTIAL`；只读、三个列表分支不混用；统计分析、明确全量或完整拉取可串行翻页 |
| 查询单条待入职详情 / 待入职表单 | `ihr-cli staff entry +get` | Shortcut | `entry-form-id` | Help + [入职查询命令](../commands/entry-query.md) | [入职查询命令](../commands/entry-query.md) | 单条入职表单详情 | `PARTIAL`；必须真实 `entryFormId` |
| 查询入职审批待办 / 审批记录 | `ihr-cli staff entry application +search` | Shortcut | 人员、部门、待审批状态、分页 | Help + [入职查询命令](../commands/entry-query.md) | [入职查询命令](../commands/entry-query.md) | 当前用户可见的脱敏单页待审批记录 | `PARTIAL`；敏感、必须有筛选、不处理审批；明确全量可串行翻页 |
| 创建单条待入职 / 待入职表单 | `ihr-cli staff entry +create` | Shortcut | 姓名、部门、手机号、预计日期、确认姓名 | Help + [待入职写入命令](../commands/entry-write.md) | [待入职写入命令](../commands/entry-write.md) | 执行检查及创建响应 | `PARTIAL`；高影响写入、dry-run、精确确认、禁止重试 |
| 读取可维护字段 / 待入职字段规则 | `ihr-cli staff entry +update-fields` | Shortcut | `entry-form-id` | Help + [待入职写入命令](../commands/entry-write.md) | [待入职写入命令](../commands/entry-write.md) | 白名单字段组、必填/只读/选项规则 | `PARTIAL`；只读、每次编辑必须重新读取 |
| 更新单条待入职 / 待入职表单 | `ihr-cli staff entry +update` | Shortcut | `entry-form-id`、完整载荷、确认 ID | Help + [待入职写入命令](../commands/entry-write.md) | [待入职写入命令](../commands/entry-write.md) | 更新响应，需详情回读 | `PARTIAL`；高影响写入、非 patch、二次确认 |
| 确认待入职并触发归档 / 待入职表单 | `ihr-cli staff entry +confirm` | Shortcut | `entry-form-id`、确认 ID、弱编确认 | Help + [待入职写入命令](../commands/entry-write.md) | [待入职写入命令](../commands/entry-write.md) | 确认归档响应，需 joined/花名册回读 | `PARTIAL`；高影响写入、强编失败停止 |

## 入职登记与审核

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询审核列表 / 入职登记表 | `ihr-cli staff entry registration-form +search` | Shortcut | 人员、状态、日期、登记 ID、分页 | Help + [入职登记命令](../commands/registration-form.md) | [入职登记命令](../commands/registration-form.md) | `CONFIRM/RECHECK` 分页列表 | `PARTIAL`；敏感、范围固定收窄；明确全量可串行翻页 |
| 查询登记详情 / 入职登记表 | `ihr-cli staff entry registration-form +get` | Shortcut | `registration-id` | Help + [入职登记命令](../commands/registration-form.md) | [入职登记命令](../commands/registration-form.md) | 单条审核摘要和字段填写状态 | `PARTIAL`；敏感、只读、动态值不完整 |
| 查询登记附件 / 附件槽位 | `ihr-cli staff entry registration-form +attachments` | Shortcut | `entry-info-id` | Help + [入职登记命令](../commands/registration-form.md) | [入职登记命令](../commands/registration-form.md) | 附件槽位和文件元数据 | `PARTIAL`；不读取内容、不拼下载地址 |
| 查询登记模板 / 模板规则 | `ihr-cli staff entry registration-template +get` | Shortcut | `code`、可选版本 | Help + [入职登记命令](../commands/registration-form.md) | [入职登记命令](../commands/registration-form.md) | 模板字段与附件规则摘要 | `PARTIAL`；只读、code 不猜测 |
| 审核通过登记表 / 入职登记表 | `ihr-cli staff entry registration-form +approval-pass` | Shortcut | 登记 ID、关联入职 ID、通知、备注、确认 ID | Help + [入职登记命令](../commands/registration-form.md) | [入职登记命令](../commands/registration-form.md) | `state` 或编制警告，需状态回读 | `PARTIAL`；高影响写入、外部通知显式确认 |

## 转正、调动与离职流程命令

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询转正流程单据 | `ihr-cli staff positive +search` | Shortcut | 列表、业务/审批/考核状态、人员、分页 | Help + [入转调离查询命令](../commands/lifecycle-records.md) | [入转调离查询命令](../commands/lifecycle-records.md) | 转正分页结果 | `PARTIAL`；只读、状态维度分开；统计分析、明确全量或完整拉取可串行翻页 |
| 查询调动流程单据 | `ihr-cli staff transfer +search` | Shortcut | 人员、部门、业务/审批状态、分页 | Help + [入转调离查询命令](../commands/lifecycle-records.md) | [入转调离查询命令](../commands/lifecycle-records.md) | 调动分页结果 | `PARTIAL`；只读、两个状态分别解释；统计分析、明确全量或完整拉取可串行翻页 |
| 查询租户调动设置 / 调动设置 | `ihr-cli staff transfer-setting +get` | Shortcut | 无业务参数 | Help + [入转调离查询命令](../commands/lifecycle-records.md) | [入转调离查询命令](../commands/lifecycle-records.md) | 当前租户规则对象 | `PARTIAL`；租户级、只读、只执行一次 |
| 查询离职流程单据 | `ihr-cli staff quit +search` | Shortcut | 列表、业务/审批/交接状态、人员、分页 | Help + [入转调离查询命令](../commands/lifecycle-records.md) | [入转调离查询命令](../commands/lifecycle-records.md) | 离职分页结果 | `PARTIAL`；只读、不证明下游完成；统计分析、明确全量或完整拉取可串行翻页 |

## 黑名单、合同、协议与异动

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 查询黑名单 / 黑名单记录 | `ihr-cli staff blacklist +search` | Shortcut | 人员、状态、日期、分页 | Help + [黑名单命令](../commands/blacklist.md) | [黑名单命令](../commands/blacklist.md) | 敏感分页结果 | `PARTIAL`；需明确范围、禁止导出；明确全量可串行翻页 |
| 查询合同 / 合同记录 | `ihr-cli staff contract +search` | Shortcut | 人员、部门、分页 | Help + [员工业务记录命令](../commands/employee-business-records.md) | [员工业务记录命令](../commands/employee-business-records.md) | 合同分页列表 | `PARTIAL`；只读、无详情、记录数非人数；统计分析、明确全量或完整拉取可串行翻页 |
| 查询协议 / 协议记录 | `ihr-cli staff agreement +search` | Shortcut | 人员、部门、分页 | Help + [员工业务记录命令](../commands/employee-business-records.md) | [员工业务记录命令](../commands/employee-business-records.md) | 协议分页列表 | `PARTIAL`；只读、无详情、记录数非人数；统计分析、明确全量或完整拉取可串行翻页 |
| 查询已发生异动 / 异动记录 | `ihr-cli staff change-record +search` | Shortcut | 人员、类型、三个时间范围、分页 | Help + [员工业务记录命令](../commands/employee-business-records.md) | [员工业务记录命令](../commands/employee-business-records.md) | `content/totalElements/totalPages` | `PARTIAL`；只读、三类时间不混用；统计分析、明确全量或完整拉取可串行翻页 |

## 培训

| 业务动作 / 主对象 | 稳定命令 | 类型 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 汇总培训记录 / 四类记录数 | `ihr-cli staff training count` | Metadata | `staffStatuses` body | Help + Schema + [培训命令](../commands/training.md) | Schema + [培训命令](../commands/training.md) | 四类培训记录数 | `PARTIAL`；只读、不是培训人数 |
| 查询线上课程 / 课程记录 | `ihr-cli staff training course-record-page` | Metadata | `staffId/page/size` body | Help + Schema + [培训命令](../commands/training.md) | Schema + [培训命令](../commands/training.md) | `dataList + pageInfo` | `PARTIAL`；单员工当前页，元素开放 |
| 查询考试 / 考试记录 | `ihr-cli staff training exam-record-page` | Metadata | `staffId/page/size` body | Help + Schema + [培训命令](../commands/training.md) | Schema + [培训命令](../commands/training.md) | `dataList + pageInfo` | `PARTIAL`；单员工当前页，元素开放 |
| 查询学习地图 / 学习记录 | `ihr-cli staff training learnmap-record-page` | Metadata | `staffId/page/size` body | Help + Schema + [培训命令](../commands/training.md) | Schema + [培训命令](../commands/training.md) | `dataList + pageInfo` | `PARTIAL`；单员工当前页，元素开放 |
| 查询线下培训 / 培训记录 | `ihr-cli staff training offline-training-record-page` | Metadata | `staffId/page/size` body | Help + Schema + [培训命令](../commands/training.md) | Schema + [培训命令](../commands/training.md) | `dataList + pageInfo` | `PARTIAL`；单员工当前页，元素开放 |

## 当前能力缺口

以下内容不进入公开命令表，也不得构造、执行或用 raw API 补齐：

- 花名册员工基础信息修改、员工批量导入或导出；
- 标签定义、标签维护和批量打标；
- 入职审批任务的处理；
- 转正、调动、离职的详情、创建、修改、提交、审批、撤回、确认或生效；
- 合同、协议、黑名单的写入和详情；
- 非白名单 `ENTITY` 档案入口；
- 历史员工快照、依赖历史分母的标准比率、趋势，以及把记录数改称人数；自然语言查询按[Staff 查询语义](query-semantics.md)组合公开命令，未命中快路径不是停止条件。

`staff flex-meta get` 和 `staff +flexMetaGet` 均是当前公开入口：前者由 `ACTIVE + autoRegisterCommand=true` 的 metadata 注册，后者是同一业务目标的 Shortcut 入口。它们只用于读取已确认的元数据 ID，不应被误列为能力缺口；响应中的内部字段仍按权限和返回完整度处理。
