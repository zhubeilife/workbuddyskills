# Use Case：创建或分步配置公司薪资模板

## 目标定义

根据用户明确的来源和配置范围，完成公司薪资模板第一步创建、第二步完整薪资项目保存或第三步页面默认考勤计薪规则保存。每个原子目标分别确认和验证；只有用户明确要求的阶段全部取得完成证据，才报告本次目标完成。

## 业务判断

1. 先按[公司薪资模板复杂目标导航](../../domain/company-template.md)判断工作簿是不是本次模板输入。是则改读[从 Excel 创建模板](../template-from-excel/guide.md)，不得进入本 Guide 的 CREATE。
2. 再判断最终目标是空白/系统来源模板、固定空白三步续建，还是修改已有模板公式。
3. 固定空白三步续建继续读取[固定空白三步配置](fixed-blank-three-step.md)；已有模板公式修改改读[公式编辑](../formula-edit/guide.md)。
4. 本 Guide 只处理用户明确的公司模板阶段，不自动把“创建”升级为完整三步。走本路径时，第二步项目只来自用户提供的分组和项目，不从工作簿推导。
5. 第二步是完整项目集合替换，必须基于最新 snapshot；第三步只保存页面默认值，不询问考勤参数。
6. 模板创建、项目保存、默认考勤规则保存和员工实际发薪是四个不同完成边界。

## 执行与验证

固定空白来源且用户目标覆盖连续三个阶段时，以下摘要与[固定空白三步配置](fixed-blank-three-step.md)共同适用；第二步详细合并规则与恢复产物分别见[第二步配置规则](second-step-rules.md)和[模板操作产物 Schema](artifact-schema.md)。

### 第一步：创建

1. 需要系统来源时先读取 `companyTemplate +system-list` 的 Help 和 Reference，并确认唯一系统模板。
2. 读取 `companyTemplate +create` 契约，dry-run 后确认模板名称、来源、系统模板名称（如有）和 `salarySplit=false`。
3. 只执行一次；返回正整数 `payrollConfigId` 且结果与确认一致，才算第一步完成。

### 第二步：保存项目

1. 用户只给已有模板名称时，按[按名称定位已有公司模板](../../domain/company-template.md)绑定后再 snapshot。已有模板 ID 时直接使用 `companyTemplate +snapshot` 取得最新完整 `rules/snapshotHash`。
2. 需要增减项目时使用 `companyTemplate +addable-fields --for-rules`，并按[公司薪资项目](../../domain/salary-fields.md)处理复用、启用、加入和创建。
3. 构造完整 rules；dry-run 后确认分组数、项目数、增加项、删除项和公式变化，只提交一次。
4. 只有 `companyTemplate +save-rules` 返回 `verified=true` 且模板 ID/保存内容一致，才算第二步完成。

### 第三步：默认考勤规则

1. 定位 `companyTemplate +attendance-default` 契约，对已确认模板 dry-run。
2. 用户独立确认“保存页面当前默认值”后只执行一次。
3. `saved=true`、`savedCount=1`、相同模板 ID 和 `settingsSource=PAGE_DEFAULTS` 同时满足才算完成。

## 停止条件

- 创建来源或系统模板多候选未确认；
- 已有模板名称无法唯一定位、snapshotHash 过期、项目集合不完整或哈希冲突；
- 用户要求修改未公开的调薪、批量、月标准计薪天数或具体考勤参数；
- 写入超时、网络中断或响应无法判定。先按公开只读能力核对；创建后可用 `companyTemplate +list --name <模板名称>` 回读，零命中时提示页面核验，禁止自动重试创建；
- 用户拒绝当前阶段确认，或前一阶段未取得完成证据。
