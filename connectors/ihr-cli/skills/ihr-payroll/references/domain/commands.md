# Payroll 公开命令导航

本表覆盖当前 `ihr-cli payroll` 注册的公开 Shortcut。Payroll interface-meta 中只有 `formula/excel-functions` 为 `ACTIVE`，但它仍未自动注册；其他定义为 `DRAFT` 且未自动注册。因此当前 Agent 可执行面以本表中的 Shortcut 为准，不能从 metadata 文件名推导额外命令。

## 契约读取规则

1. 准备执行命令前，只定向定位相关条目一次；不要通读无关分组。
2. 完整 flags、别名和输入方式先读取具体命令 `--help`。
3. Shortcut 的机器输入/输出结构使用对应的精确 `ihr-cli schema payroll ... +<action>`；Schema 若为 `PARTIAL`，本表指向的过渡命令 Reference 补充业务输入、返回摘要、安全边界和完成证据。
4. Help 与 Reference 冲突时以 Help 为准并报告契约漂移；输出无法由当前 Reference 解释时停止，不按示例猜测字段。
5. 查询类 JSON 输入的公共约束见[查询命令公共契约](../commands/query-command-contract.md)；用户确认中的名称与内部标识规则见[展示名称规范](../commands/display-names.md)。

`PARTIAL` 表示命令真实可执行，但 Help/Schema 尚未独立覆盖全部输入输出契约，执行前必须读取本表指向的过渡 Reference。

## 员工主体的薪资信息查询

本节中的“员工”是 Payroll 业务对象的主体，命令查询的是银行卡、薪资档案和扣缴关系等薪资信息，不是员工花名册、任职或生命周期。员工身份需要解析时，按各命令条目的规则使用 Staff 或 Payroll 的定位链；命令归属仍以实际 Payroll 业务对象和 CLI 注册路径为准。

| 业务动作 / 主对象 | 稳定命令 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- |
| 查询指定员工银行卡 / 银行卡 | `ihr-cli payroll bankCard +detail` | `staff-id` | Help + [银行卡](../commands/bank-card.md) | [银行卡](../commands/bank-card.md) | `summary/staffId/cards` | `PARTIAL`；单员工、敏感；先 `staff +search` |
| 查询薪资档案列表 / 薪资档案 | `ihr-cli payroll salaryProfile +list` | 姓名、工号、状态、组织、动态字段、分页 | Help + [档案列表](../commands/salary-profile-list.md) | [档案列表](../commands/salary-profile-list.md) | 分页人员与档案摘要 | `PARTIAL`；动态字段最多 20 |
| 查询档案字段或详情 / 薪资档案 | `ihr-cli payroll salaryProfile +detail` | `staff-id`、`fields`、`fields-only` | Help + [档案详情](../commands/salary-profile-detail.md) | [档案详情](../commands/salary-profile-detail.md) | 字段定义或单员工档案 | `PARTIAL`；详情员工由档案列表定位 |
| 查询扣缴义务人 / 扣缴关系 | `ihr-cli payroll corporation +detail` | `staff-id` | Help + [扣缴义务人](../commands/corporation.md) | [扣缴义务人](../commands/corporation.md) | `summary/staffId/records` | `PARTIAL`；单员工、敏感、明确触发 |

## 台账、方案与核算

| 业务动作 / 主对象 | 稳定命令 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- |
| 查询薪资台账列表 / 台账 | `ihr-cli payroll ledger +list` | 名称、年月或日期范围、分页 | Help + [台账列表](../commands/ledger-list.md) | [台账列表](../commands/ledger-list.md) | history/merge 台账列表 | `PARTIAL`；敏感；不支持 split 子台账 |
| 查询台账字段或明细 / 台账 | `ihr-cli payroll ledger +detail` | 列表上下文、`fields`、人员模糊条件、分页 | Help + [台账明细](../commands/ledger-detail.md) | [台账明细](../commands/ledger-detail.md) | 字段定义或当前页员工明细 | `PARTIAL`；必须使用同一列表项上下文 |
| 查询共享薪资台账 / 共享台账 | `ihr-cli payroll ledger +shared-list` | JSON 中的名称、账期、分页 | Help + [共享台账](../commands/ledger-shared-list.md) | [共享台账](../commands/ledger-shared-list.md) | 共享台账候选 | `PARTIAL`；敏感、单次查询 |
| 查询薪资方案 / 方案 | `ihr-cli payroll salaryPlan +list` | JSON 中的名称、月份、状态、类型 | Help + [方案列表](../commands/salary-plan-list.md) | [方案列表](../commands/salary-plan-list.md) | 普通薪资方案列表 | `PARTIAL`；只读、单次查询 |
| 查询共享薪资方案 / 共享方案 | `ihr-cli payroll salaryPlan +shared-list` | JSON 中的名称、月份、状态 | Help + [共享方案](../commands/salary-plan-shared-list.md) | [共享方案](../commands/salary-plan-shared-list.md) | 共享薪资方案列表 | `PARTIAL`；不能与普通方案自动合并 |
| 查询未关联方案人数 / 方案覆盖 | `ihr-cli payroll salaryPlan +unassigned-count` | 无业务参数 | Help + [未关联人数](../commands/salary-plan-unassigned-count.md) | [未关联人数](../commands/salary-plan-unassigned-count.md) | 当前权限范围内人数 | `PARTIAL`；不是人员名单或工资统计 |
| 查询核算结果明细 / 核算任务 | `ihr-cli payroll salaryTask +detail` | JSON 中的任务和筛选条件 | Help + [核算明细](../commands/salary-task-detail.md) | [核算明细](../commands/salary-task-detail.md) | 核算结果明细 | `PARTIAL`；只读、明确任务范围 |
| 查询核算表格配置 / 核算表格 | `ihr-cli payroll salaryTask +table` | JSON `code` | Help + [核算表格](../commands/salary-task-table.md) | [核算表格](../commands/salary-task-table.md) | 表格字段配置 | `PARTIAL`；不得枚举 code 或构造写入 |

## CNB 个税

| 业务动作 / 主对象 | 稳定命令 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- |
| 查询申报主体 / CNB 申报 | `ihr-cli payroll cnbPlugins taxApply +list` | JSON 期间、主体、员工、分页 | Help + [CNB 个税](../commands/cnb-tax.md) | [CNB 个税](../commands/cnb-tax.md) | 申报主体或记录列表 | `PARTIAL`；只读；统计分析、明确全量或完整拉取可串行翻页 |
| 查询申报明细状态 / CNB 申报 | `ihr-cli payroll cnbPlugins taxApply +detail-status` | JSON 主体、类型、期间 | Help + [CNB 个税](../commands/cnb-tax.md) | [CNB 个税](../commands/cnb-tax.md) | 申报明细状态 | `PARTIAL`；不是申报动作 |
| 查询缴款汇总 / CNB 缴款 | `ihr-cli payroll cnbPlugins taxPayment +total-list` | JSON 主体、计税期间、分页 | Help + [CNB 个税](../commands/cnb-tax.md) | [CNB 个税](../commands/cnb-tax.md) | 缴款汇总结果 | `PARTIAL`；不是确认或缴款动作 |

## 公司薪资项目与公式

| 业务动作 / 主对象 | 稳定命令 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- |
| 查询公司薪资项目 / 项目 | `ihr-cli payroll salaryField +list` | 名称、有效状态、分页 | Help + [项目列表](../commands/salary-field-list.md) | [项目列表](../commands/salary-field-list.md) | 公司项目分页 | `PARTIAL`；省略 `valid` 才能发现失效项 |
| 查询公司薪资项目详情 / 项目 | `ihr-cli payroll salaryField +detail` | `meta-id` | Help + [项目详情](../commands/salary-field-detail.md) | [项目详情](../commands/salary-field-detail.md) | 单项目详情 | `PARTIAL`；只使用已确认 metaId |
| 查询模板可添加项目 / 模板项目 | `ihr-cli payroll companyTemplate +addable-fields` | 模板 ID、规则模式 | Help + [可添加项目](../commands/company-template-addable-fields.md) | [可添加项目](../commands/company-template-addable-fields.md) | 可复用项目树和规则对象 | `PARTIAL`；不自行拼接 ruleField |
| 查询未加入系统项目 / 系统项目 | `ihr-cli payroll salaryField +system-not-added` | `scope`、名称 | Help + [未加入系统项目](../commands/salary-field-system-not-added.md) | [未加入系统项目](../commands/salary-field-system-not-added.md) | 系统项目候选 | `PARTIAL`；当前公司无候选后再使用 |
| 查询项目创建选项 / 创建配置 | `ihr-cli payroll salaryField +create-options` | 无 | Help + [创建选项](../commands/salary-field-create-options.md) | [创建选项](../commands/salary-field-create-options.md) | 类别、类型、进位和成本选项 | `PARTIAL`；缺名称的选项停止 |
| 启用失效项目 / 项目 | `ihr-cli payroll salaryField +batch-enable` | `meta-ids` | Help + [批量启用](../commands/salary-field-batch-enable.md) | [批量启用](../commands/salary-field-batch-enable.md) | 有序启用结果 | `PARTIAL`；写入、dry-run、部分失败停止 |
| 加入系统项目 / 项目 | `ihr-cli payroll salaryField +add-system` | 完整系统候选对象 | Help + [加入系统项目](../commands/salary-field-add-system.md) | [加入系统项目](../commands/salary-field-add-system.md) | 加入和读回结果 | `PARTIAL`；写入、dry-run |
| 创建自定义项目 / 项目 | `ihr-cli payroll salaryField +create` | 名称、类型、类别和数值设置 | Help + [创建项目](../commands/salary-field-create.md) | [创建项目](../commands/salary-field-create.md) | 创建和读回结果 | `PARTIAL`；写入、完整设置确认 |
| 批量原子创建项目 / 项目集合 | `ihr-cli payroll salaryField +batch-create` | `createRequests` | Help + [批量创建](../commands/salary-field-batch-create.md) | [批量创建](../commands/salary-field-batch-create.md) | 有序批次结果 | `PARTIAL`；禁止循环单条，结果未知时停止 |
| 查询公式函数 / 公式语言 | `ihr-cli payroll formula +functions` | 无 | Help + [函数列表](../commands/formula-functions.md) | [函数列表](../commands/formula-functions.md) | 当前公司函数名称集合 | `PARTIAL`；结合静态公式语言解释 |
| 校验公式 / 公式 | `ihr-cli payroll formula +validate` | 字段、公式、格式、可引用字段 | Help + [公式校验](../commands/formula-validate.md) | [公式校验](../commands/formula-validate.md) | 规范化公式与校验结果 | `PARTIAL`；不等于模板保存 |
| 试算公式 / 公式 | `ihr-cli payroll formula +calc` | 公式、样例字段值、进位和小数位 | Help + [公式试算](../commands/formula-calc.md) | [公式试算](../commands/formula-calc.md) | 当前样例试算值 | `PARTIAL`；不等于实际工资 |

## 公司薪资模板

| 业务动作 / 主对象 | 稳定命令 | 常用参数 | 输入契约来源 | 输出契约来源 | 返回摘要 | 完整性 / 风险边界 |
| --- | --- | --- | --- | --- | --- | --- |
| 查询系统模板 / 模板来源 | `ihr-cli payroll companyTemplate +system-list` | 无或 Help 公开筛选 | Help + [系统模板](../commands/company-template-system-list.md) | [系统模板](../commands/company-template-system-list.md) | 系统模板候选 | `PARTIAL`；选择唯一来源后才能创建 |
| 查询公司模板 / 已有模板 | `ihr-cli payroll companyTemplate +list` | 名称 | Help + [公司模板列表](../commands/company-template-list.md) | [公司模板列表](../commands/company-template-list.md) | 当前公司已启用模板 | `PARTIAL`；完整名称精确匹配后继续配置 |
| 创建公司模板 / 模板 | `ihr-cli payroll companyTemplate +create` | 名称、来源、系统模板 ID | Help + [创建模板](../commands/company-template-create.md) | [创建模板](../commands/company-template-create.md) | 新模板 `payrollConfigId` | `PARTIAL`；写入、dry-run、超时不重试 |
| 读取模板项目快照 / 模板 | `ihr-cli payroll companyTemplate +snapshot` | `payroll-config-id` | Help + [模板快照](../commands/company-template-snapshot.md) | [模板快照](../commands/company-template-snapshot.md) | 完整项目规则和快照哈希 | `PARTIAL`；是后续全量保存基线 |
| 保存模板项目 / 模板 | `ihr-cli payroll companyTemplate +save-rules` | 模板 ID、快照哈希、完整 rules | Help + [保存项目](../commands/company-template-save-rules.md) | [保存项目](../commands/company-template-save-rules.md) | `verified` 保存结果 | `PARTIAL`；全量替换、哈希冲突重新确认 |
| 保存页面默认考勤规则 / 模板 | `ihr-cli payroll companyTemplate +attendance-default` | `payroll-config-id` | Help + [默认考勤规则](../commands/company-template-attendance-default.md) | [默认考勤规则](../commands/company-template-attendance-default.md) | `saved/savedCount/settingsSource` | `PARTIAL`；写入页面默认值，不改考勤结果 |

## 当前命令缺口

以下内容不进入公开命令表，命中时按缺口停止：

- 所有 `autoRegisterCommand=false` 的 Payroll metadata command，例如 `payroll attendance-plan detail`、`payroll ledger-entry search`、`payroll salary-field batch-update`；
- split 子台账、薪资导出、工资条发送、核算提交、个税申报/确认/缴款写入；
- 员工与模板关联、任意历史工资总额/平均工资/分位数及个税完成率；
- Excel 提取、表格识别、全量表头映射和端到端建模板；这些由本 Domain 的 Use Case Guide 组织，Excel 提取按需读取独立的 `ihr-excel-read` 契约。
