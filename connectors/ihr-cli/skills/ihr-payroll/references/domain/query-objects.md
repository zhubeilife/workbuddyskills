# Payroll 查询对象与结果

本文件说明当前公开查询对象如何定位、返回什么业务事实，以及哪些相邻结果不能替代它。完整参数和输出字段读取[公开命令导航](commands.md)中的对应契约。

## 1. 人员银行卡

- 唯一公开入口是 `ihr-cli payroll bankCard +detail`，只支持单员工。
- 命令需要真实 `staffId`。无论用户直接给 ID 还是姓名/工号，都必须先用 `ihr-cli staff +search` 在花名册权限范围内校验唯一员工。
- 不得使用 `salaryProfile +list` 或 Master Data `STAFF` 解析银行卡员工。
- 结果使用 `summary/staffId/cards`；卡号、持卡人和其他已返回银行卡业务字段按原值呈现，不主动展示银行卡图片 ID。
- 不提供列表、多员工、分页、按卡号或银行筛选。空 `cards` 只能按当前响应说明，不能证明员工永远没有银行卡。

## 2. 薪资档案

### 列表

- `salaryProfile +list` 可按姓名、工号、员工 ID、组织 ID、员工状态、纳税身份、方案关系和动态字段筛选。
- 当前页从 1 开始，每页最多 100；员工 ID 最多 100 个，动态字段最多 20 个。
- `fields` 为空时只返回人员和档案摘要；用户只做员工定位时必须保持动态字段为空，不读取额外薪资值。

### 字段与详情

- `salaryProfile +detail --fields-only` 读取当前可用字段定义，不读取员工档案。
- 数据模式必须有唯一真实 `staffId`，选择的字段最多 50 个。
- 姓名或工号只通过同域 `salaryProfile +list` 定位。唯一候选可自动注入；多候选按姓名、工号和部门确认；零候选只说明“未查到对应人员或相关数据”。
- 用户给字段展示名时先 fields-only；唯一字段匹配后注入 code，多候选按名称、类型和选项确认。
- 部门、职位和职级名称需要转 ID 时按目标字段使用 `ihr-master-data`；`positionLevelName` 是职位职级路径，不能替代薪级名称。

## 3. 薪资台账

### 列表定位

- `ledger +list` 至少需要台账名称、完整 `year+month` 或完整日期范围之一；年月与日期范围互斥。
- 每个列表项只按返回的 `ledgerType=history|merge` 处理。`salarySplit` 是属性，不是类型。
- 列表返回的方案、history/merge 标识、年月必须作为一个完整上下文保存，不能从不同列表项拼接。

### 字段与员工明细

- `ledger +detail --fields-only` 读取指定 history/merge 台账的字段定义；字段定义不包含用于推导未公开公式的完整信息。
- 明细模式使用同一条列表结果：history 需要 `salaryPlanId + historyPlanId + year + month`；merge 需要 `mergeReportId + year + month`。
- 用户给字段展示名时先 fields-only；最终明细最多选择 50 个字段。
- 姓名、工号、部门名称直接进入明细命令，由业务接口先筛选再分页；不解析 `staffId`，不使用 `salaryProfile +list`，不做当前页本地匹配。
- split 子台账、`subDatas`、导出、未选择字段和页面控制数据当前不公开。

## 4. 个税扣缴义务人

- 唯一公开入口是 `corporation +detail`，只支持单员工详情。
- 姓名或工号通过最小的 `salaryProfile +list` 定位真实 `staffId`，不得改用 Staff 或 Master Data。
- 结果中的主体、税号、日期和变动类型按原值展示；没有明确状态定义时，不按日期自行选出“当前主体”。
- 不提供主体列表或多员工查询，不循环 staffId，不把零结果改写为“该员工没有薪资档案”。

## 5. 薪资方案、核算任务和共享结果

- `salaryPlan +list` 查询普通薪资方案候选；`salaryPlan +shared-list` 查询共享方案；两者结果不能合并为同一集合。
- `salaryPlan +unassigned-count` 只返回当前权限范围内未关联任何薪资方案的人数，不提供人员名单。
- `salaryTask +detail` 查询核算结果明细；`salaryTask +table` 只读取已确认表格编码对应的字段配置。
- `ledger +shared-list` 查询共享台账候选，不替代普通 `ledger +list`，也不能直接构造普通台账明细上下文。
- 这些命令都只读。方案或任务存在不能推导已经核算完成、已经发布台账或已经发送工资条。

## 6. CNB 个税查询

- `cnbPlugins taxApply +list` 查询申报主体或记录候选。
- `cnbPlugins taxApply +detail-status` 查询已确认主体、类型和期间的明细状态。
- `cnbPlugins taxPayment +total-list` 查询已确认主体和计税期间的缴款汇总结果。
- `taxYear/taxMonth` 是计税期间，不自动等同台账年月。
- 三个入口均不执行申报、确认或缴款，不循环未确认主体或扩展期间。普通查询不自动翻页；已确认主体和计税期间内的统计分析、明确全量或完整拉取可串行翻页，禁止并发。
