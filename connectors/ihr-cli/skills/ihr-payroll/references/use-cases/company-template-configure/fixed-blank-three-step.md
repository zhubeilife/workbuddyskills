# 固定空白来源的三步配置

完成一个公司薪资模板的业务配置。新建时固定使用空白模板，依次完成第一步、第二步薪资项目和页面默认考勤规则；已有 `payrollConfigId` 可以从第二步或考勤步骤继续。

用户确认只展示业务名称，遵循 `ihr-payroll` 的 `references/commands/display-names.md`：第一步显示“空白模板”和“按工时拆分工资：关闭”，第二步显示项目名称/分组名称，第三步显示“页面当前默认值”。模板 ID 只作为技术定位信息保留在产物或用户明确要求的技术详情中。

## 路由

本路径只在工作簿不是本次模板输入时使用。判断见[公司薪资模板复杂目标导航](../../domain/company-template.md)。

| 用户目标 | 起点 | 必要输入 | 执行阶段 |
| --- | --- | --- | --- |
| 创建完整模板 | `CREATE` | 模板名称、用户提供的分组和项目 | `CREATE -> RULES -> ATTENDANCE` |
| 继续配置薪资项目 | `RULES` | 已有模板名称或 ID、用户提供的分组和项目 | `RULES -> ATTENDANCE` |
| 只完成默认考勤规则 | `ATTENDANCE` | 已有模板名称或 ID | `ATTENDANCE` |

用户没有明确起点时，有已定位模板仍需确认从第二步还是考勤步骤开始。复用已有模板或只给模板名称时，先按[按名称定位已有公司模板](../../domain/company-template.md)绑定，再进入 RULES 或 ATTENDANCE。没有已有模板则从 `CREATE` 开始。完整创建必须先取得模板名称和第二步分组/项目，避免第一步成功后才发现后续输入缺失。工作簿不能代替这里的分组/项目输入。

## 阶段执行

### CREATE

读取 `ihr-payroll` 的 `references/commands/company-template-create.md`。只允许 `EMPTY_TEMPLATE`，固定 `salarySplit=false`；不查询系统模板。对名称和固定设置执行 dry-run，取得明确确认后只创建一次，并保存返回的正整数 `payrollConfigId`。

### RULES

读取 [第二步配置规则](second-step-rules.md)，以及其中指向的 snapshot、addable-fields 和 save-rules 契约。分组与项目只来自用户提供的模板业务输入，不从 Excel、表头、映射或其他前置流程产物推导。

以最新 snapshot 为完整基线：保留用户未要求删除的已有项目；把用户指定项目解析为 `addable-fields --for-rules` 返回的 `ruleField`，再按用户给出的分组和顺序合并。dry-run 后展示全量替换的模板身份、分组数、项目数、输入项数、公式项数和明确删除项，取得独立确认后只保存一次。只有 `verified=true`，或写入已发生后只读快照满足第二步规则中定义的业务不变量且差异仅为服务端隐藏元数据规范化，才进入下一阶段。

### ATTENDANCE

读取 `ihr-payroll` 的 `references/commands/company-template-attendance-default.md`。本路径只保存页面当前默认规则，不接受、询问或推断具体考勤参数。dry-run 后取得独立确认，只执行一次；只有 `saved=true`、`savedCount=1`、相同模板 ID 和 `settingsSource=PAGE_DEFAULTS` 才算完成。

## 公式边界

本路径不翻译 Excel 公式、不把业务描述转换成公式、不设计公式，也不调用公式转换、校验或试算命令。已有 snapshot 或 `ruleField` 中的公式配置可以原样保留；用户要求新增或修改公式时，暂停 RULES 保存并进入[公式编辑 Use Case](../formula-edit/guide.md)。取得已完成翻译、code 转换、校验、非空试算和结果确认的项目配置后，再重新生成第二步 dry-run。

## 确认与恢复

- 每个写阶段都有自己的 payload 哈希、dry-run 和确认；前一阶段的确认不授权后一阶段写入。
- 参数错误可以在原范围内修正后重新 dry-run。鉴权、权限或明确业务失败在当前阶段停止。
- CREATE 和 ATTENDANCE 没有幂等键；网络超时、连接中断或响应丢失时记录 `UNKNOWN` 并停止，不自动重试或进入下一阶段。
- RULES 哈希过期时重新 snapshot、按同一用户配置合并、重新 dry-run 并重新确认。写入结果未知时只允许读取 snapshot 对比，不自动再次保存。写入已发生但严格读回比较失败时，只按第二步规则的业务不变量判断；仅有服务端隐藏元数据补齐差异时可继续。
- 已明确成功的阶段不重复执行。产物记录 `payrollConfigId` 和最早未完成阶段，后续调用从该阶段恢复。
- 只使用本 Use Case 列出的 `payroll companyTemplate` shortcut；不使用 `ihr-interface`、完整 URL、裸 HTTP 或身份字段绕过。

## 产物

用户未指定输出位置时，在系统临时目录的 `ihr-cli/payroll-template-create/<唯一运行 ID>/artifact-vNNN/` 写出 [模板操作产物](artifact-schema.md)。不询问临时目录，不写项目源码、当前工作目录或 `test/runs`。每次输入、dry-run、确认或执行状态变化都写新版本，不覆盖旧产物。

## 完成条件

- 从 `CREATE` 开始：三个阶段均明确成功。
- 从 `RULES` 开始：RULES 和 ATTENDANCE 均明确成功。
- 从 `ATTENDANCE` 开始：ATTENDANCE 明确成功。
- 产物可解析、模板 ID 始终一致，没有 `BLOCKING` issue，`nextStage=null`。

任何写入结果未知、业务读回不一致、模板身份变化或后续阶段未完成，都不能报告完整模板创建完成。
