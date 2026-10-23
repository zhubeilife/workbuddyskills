# 薪资流程用户展示名称规范

本规范适用于 Excel→薪资模板流程的用户回复、确认卡片、dry-run 摘要和产物摘要。命令参数、机器产物和接口 payload 仍需要 code/ID、payload 哈希、接口路径等技术字段；这些内部标识不直接作为用户选择项或普通确认文案。

## 展示原则

1. 先展示业务名称，再展示业务含义；用户选择字段类型、类别、进位、成本方式、来源或模板阶段时只看到名称。
2. code、metaId、fieldId、serviceRefId、接口字段名、HTTP method、接口路径、headers、profile、raw payload、payload 哈希和稳定 issue code 只用于内部绑定、审计和恢复。只有用户明确要求查看原始技术数据，或需要解释写入未知、哈希不一致、回查不一致等阻断原因时，才单独展示最小必要字段，并标注“技术标识”。
3. 接口同时返回 `name`/`title`/`label` 与 code 时，取名称字段；缺少名称时停止该选择并向用户询问名称映射，不把 code 当名称、不拼接临时译名。
4. 布尔值用“是/否”或“开启/关闭”；状态用“有效/失效”“已确认/待确认”等业务词。不要把 `true/false`、`valid` 或状态 code 直接放进确认句。
5. 业务对象优先展示名称：薪资项目名称、字段类型名称、类别名称、来源名称、计税类型名称、模板名称、分组名称和公式函数名称。字段 code 仅用于内部公式和 payload。

## 已有名称来源

| 用户要确认的项目 | 展示字段 | 名称来源 | 缺名称时 |
| --- | --- | --- | --- |
| 自定义字段类型 | `typeName` | `salaryField +create-options` 的 `types[]` | 停止选择并向用户询问该类型名称 |
| 字段所属类别 | `categoryName` | `types[]/categories[]` 或 `addable-fields` | 停止选择并向用户询问该类别名称 |
| 进位规则 | `name`/`roundingModeName` | `create-options` 或字段列表 | 停止选择并向用户询问名称 |
| 公司成本方式 | `name`/`companyCostOperationName` | `create-options` 或字段列表 | 非空派生值缺少名称时停止确认并补齐名称 |
| 薪资项目来源 | `sourceName`/`displaySource` | 字段列表、详情或台账字段模式 | 停止展示该候选，不回显 source code |
| 计税类型 | `taxTypeName` | 字段列表/详情 | 停止展示该候选，不回显 tax type code |
| 取值类型 | `valueTypeName` | 字段列表/档案字段模式 | 停止展示该候选，不回显 value type code |
| 薪资档案引用来源 | `usingStaffSalarySourceName` | 字段列表/详情 | 停止展示该设置，不回显内部值 |
| 系统模板类别 | `categoryName` | 系统模板列表 | 停止让用户选择该候选，不回显类别 code |
| 系统项目类别/类型 | `categoryName/typeName` | 未加入系统项目或可添加字段 | 停止让用户选择该候选，不回显 code |

## 固定中文名称

以下是已经由业务约束确定、无需再向用户展示机器枚举的名称。内部值只在命令中使用：

| 内部值 | 用户展示名称 |
| --- | --- |
| `EMPTY_TEMPLATE` | 空白模板 |
| `salarySplit=false` | 按工时拆分工资：关闭 |
| `PAGE_DEFAULTS` | 页面当前默认值 |
| `INPUT`（取值来源） | 输入 |
| `FUNCTION`（公式来源） | 公式 |
| `USR` / `SYS` | 用户公式 / 系统公式 |
| `PRIMITIVE` / `ROUND` / `CEIL` / `FLOOR` | 原始数据 / 四舍五入 / 向上舍入数字 / 向下舍入数字 |
| `ADD` / `SUBTRACT` | 公司成本加项 / 公司成本减项 |
| `CODE` / `IDEOGRAPHIC`（公式格式） | 字段编码公式 / 项目名称公式 |
| `EXCEL` / `BUSINESS_RULE` / `IDEOGRAPHIC` / `CODE`（公式来源） | Excel 公式 / 业务规则 / 项目名称公式 / 字段编码公式 |
| `REUSE` / `CREATE_SYSTEM` / `CREATE_CUSTOM` / `UNRESOLVED` | 复用现有项目 / 加入系统项目 / 新建自定义项目 / 待处理 |
| `FORMULA` / `INPUT`（列决定） | 公式计算 / 人工输入 |
| `CREATE` / `RULES` / `ATTENDANCE` | 第一步模板创建 / 第二步薪资项目 / 第三步考勤计薪 |
| `EXTRACT` / `IDENTIFY` / `PROPOSE_FIELDS` / `PLAN` / `FINALIZE_FIELDS` / `PREPARE_FORMULAS` / `SAVE_RULES` / `SAVE_ATTENDANCE` | Excel 提取 / 主表识别 / 字段提案 / 模板布局与公式计划 / 字段确认写入 / 公式准备 / 第二步保存 / 第三步保存 |
| `PAYROLL_MAIN_CANDIDATE` / `AUXILIARY` / `OTHER` / `UNCLASSIFIED` | 薪资主表候选 / 辅助表 / 其他表 / 未分类表 |
| `FORMULA_REFERENCE` / `DEFINED_NAME_REFERENCE` / `TABLE_REFERENCE` / `EXTERNAL_WORKBOOK_REFERENCE` | 公式引用 / 定义名称引用 / Excel 表引用 / 外部工作簿引用 |

薪资档案引用来源如果出现在候选详情中，优先使用接口或 CLI 返回的名称：`INPUT`=输入、`OPTION`=选项、`RANK_SALARY_SYSTEM`=职级薪酬体系、`SMART_APP_VALUE`=智搭云取值、`SMART_APP_OPTION`=智搭云选项。出现未登记值时停止展示该设置并向用户询问名称。

## 用户确认模板

确认句应类似：

> “请确认新字段‘交通补贴’：字段类型‘金额’，所属类别‘税前加项’，进位规则‘四舍五入’，公司成本‘加项’，引用薪资档案‘是’，强制使用‘否’，档案必填‘否’。取值来源固定为‘输入’。”

不要写成：

> “typeCode=pretaxallowance、categoryCode=xxx、roundingMode=ROUND、companyCostOperation=ADD、valueSource=INPUT。”

如果接口只给 code 而没有名称，向用户提出最小问题，例如：“接口返回了一个未命名字段类型，内部标识为技术数据，无法安全让你选择。请提供该类型的中文名称；提供后我会只在内部绑定该标识。”
