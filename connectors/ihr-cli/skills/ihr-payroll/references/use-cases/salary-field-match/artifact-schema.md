# 薪资项目映射产物 Schema

当前 `schemaVersion` 为 `1.1.0`，固定文件名为 `salary-field-mapping.json`。每次分析、确认、dry-run 或执行结果都写入新的唯一目录，通过 `supersedes` 关联上一版。

## 顶层字段

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `schemaVersion` | string | 固定 `1.1.0`。 |
| `artifactType` | string | 固定 `payroll-salary-field-mapping`。 |
| `status` | string | `needs_confirmation`、`complete` 或 `blocked`。 |
| `stage` | string | `HEADER`、`MAPPING`、`ENABLE`、`CREATE` 或 `COMPLETE`。 |
| `generatedAt` | string | ISO 8601 时间。 |
| `source` | object | 上游识别、提取和源文件身份。 |
| `columns` | array | 主表全部数据列及表头确认、候选和最终映射。 |
| `enableBatch` | object/null | 已确认失效候选的规范化启用批次、列绑定、确认和读回结果。 |
| `createBatch` | object/null | 缺失项目的规范化批次、确认和执行结果。 |
| `issues` | array | 提示、警告和阻断项。 |
| `summary` | object | 数量自检。 |
| `supersedes` | string/null | 上一版本产物绝对路径。 |

## `source`

必须包含：

- `identificationArtifactPath`、`identificationArtifactSha256`；
- `excelArtifactDirectory`、`excelManifestSha256`；
- `sourceFileName`、`sourceFileSha256`；
- `selectedTableId`、`worksheetIndex`、`worksheetName`、`tableRange`、`headerRange`、`dataRange`；
- 本次完整读取核对后的 `cellCount` 和 `formulaCount`。

任何路径目标、哈希、计数或 selectedTableId 变化都使旧确认和旧创建 payload 失效。

## `columns[]`

每个主表数据列必须有一项：

| 字段 | 规则 |
| --- | --- |
| `excelColumnId` | `sheet-NNN:col:<列字母>`，全局唯一。 |
| `columnIndex/columnLetter/order` | 正整数列号、大写列字母和主表内顺序。 |
| `headerCells` | 表头节点的地址和原始文本；只含表头，不含员工数据。 |
| `originalLeafName/normalizedName` | 原始末级名称和用于候选匹配的规范化名称。 |
| `groupPath` | 从上层到末级的表头路径；上层只用于分组。 |
| `confirmation` | `PROPOSED` 或 `CONFIRMED`，以及确认时间；不复制用户原话。 |
| `candidates` | 按匹配顺序记录候选类型、名称、必要内部标识、`valid` 状态和推荐原因；失效候选明确记录需要先启用。 |
| `decision` | `REUSE`、`CREATE_SYSTEM`、`CREATE_CUSTOM` 或 `UNRESOLVED`。 |
| `target` | 已确认目标的 meta ID/code、系统 code 或 CUSTOM 设置；失效复用候选在启用完成前包含 `activation=REQUIRED`，成功后改为 `activation=COMPLETED`。 |
| `issues` | 当前列的 issue codes。 |

`CREATE_CUSTOM.target.settings` 必须包含 `fieldName/typeCode/typeName/categoryCode/categoryName/roundingMode/roundingModeName/decimalPlaces/useInStaffSalary/forcedToUse/required/remark/valueSource/valueSourceName`；`valueSource` 固定 `INPUT`、`valueSourceName` 固定“输入”。所选类型的 `companycostop` 非空时，另含与其完全一致的 `companyCostOperation/companyCostOperationName`；为空时省略这两个字段，并在创建请求中省略 `companyCostNumOp`。没有可配置值或应有名称时不得用 `null` 伪装已确认。

产物中的 `typeCode/categoryCode/roundingMode/companyCostOperation/valueSource` 仅用于机器执行；面向用户的确认摘要使用对应 `typeName/categoryName/roundingModeName/companyCostOperationName/valueSourceName`。`companyCostOperation` 是字段类型的派生绑定，不是用户选择；字段类型 `companycostop` 为空时展示“不计入公司成本”。接口返回非空 `companycostop` 但无法解析名称时，记录待补名称并阻断完整提案。

## `enableBatch`

没有确认“启用后复用”的候选时为 `null`。存在时包含：

- `payloadSha256`：规范化 JSON payload 的 SHA-256；
- `payload`：`salaryField +batch-enable` 的完整输入，只含稳定顺序的唯一 `metaIds`，不含 Excel 标识、公司身份或 token；
- `targetBindings`：每项包含 `metaId`、项目名称和唯一 `excelColumnId`，用于把读回有效项目绑定为 `REUSE`；
- `dryRun`：执行时间、退出码和已验证目标数量；
- `confirmation`：`AWAITING_CONFIRMATION` 或 `CONFIRMED`、确认时间和影响数量；
- `execution`：`NOT_STARTED`、`SUCCEEDED`、`FAILED` 或 `UNKNOWN`，以及 `requestedCount/enabledCount/alreadyValidCount/items`；
- `completedAt`：全部目标读回有效时的完成时间，否则为 `null`。

部分失败、网络结果不确定或读回未生效时，`execution=UNKNOWN`、产物为 `blocked`，对应列保持 `UNRESOLVED`；不得继续执行 createBatch。用户修改目标集合后必须生成新 payload 和 dry-run。

## `createBatch`

没有缺失项目时为 `null`。有缺失项目时包含：

- `payloadSha256`：规范化 JSON payload 的 SHA-256；
- `payload`：`salaryField +batch-create` 的完整输入，只含按稳定顺序排列的 `createRequests`，不含 Excel 标识、公司身份或 token；
- `requestBindings`：每项包含 `requestIndex` 和唯一 `excelColumnId`；索引必须覆盖 `createRequests` 的全部位置，用于把有序创建结果回填到列映射；
- `dryRun`：执行时间、退出码和已验证请求数量；
- `confirmation`：`AWAITING_CONFIRMATION` 或 `CONFIRMED`、确认时间和影响数量；
- `execution`：`NOT_STARTED`、`SUCCEEDED`、`FAILED` 或 `UNKNOWN`，以及成功响应的计数、有序结果和由 `requestBindings` 生成的映射；
- `completedAt`：成功完成时间，否则为 `null`。

请求超时或响应丢失后保持 `UNKNOWN`，不得写成失败或成功，也不得自动重试。

## `issues[]`

每项包含 `severity`、`code`、`message` 和可选 `excelColumnId/location`：

- `INFO`：不影响完成的说明；
- `WARNING`：需要展示但不影响已确认结果；
- `BLOCKING`：上游失效、表头歧义、候选歧义、重复映射、设置缺失、部分响应或创建状态不确定。

候选状态与启用流程 code：

- `INACTIVE_COMPANY_FIELD_CONFIRMATION_REQUIRED`：推荐候选当前失效，需要用户确认是否启用后复用；
- `INACTIVE_COMPANY_FIELD_NAME_CONFLICT`：用户拒绝启用精确同名项目后仍尝试创建同名项目；
- `COMPANY_FIELD_ENABLE_UNKNOWN`：批量启用发生部分失败、响应丢失或读回不一致；
- `COMPANY_FIELD_LOOKUP_INCOMPLETE`：包含查询仍有未读取页，尚不能证明不存在精确同名项目。

`needs_confirmation` 至少有一个待确认列或设置。`blocked` 至少有一个 `BLOCKING` issue。

## `summary`

只记录：

- `columnCount`、`confirmedHeaderCount`；
- `reusedCount`、`enabledForReuseCount`、`systemCreateCount`、`customCreateCount`、`unresolvedCount`；
- `createdCount`、`mappingCount`、`blockingIssueCount`。

## 自检

1. JSON、Schema、枚举和必填字段合法。
2. source 路径、哈希、selectedTableId 和全量计数与当前上游一致。
3. columns 恰好覆盖主表全部数据列；列号、字母、顺序和 excelColumnId 一致且不重复。
4. 每个 `CONFIRMED` 列只有一个最终 decision/target；默认没有重复公司项目目标。
5. summary 与 columns、issues、enableBatch 和 createBatch 的 execution 实际数量一致。
6. 有 enableBatch 时，targetBindings 与 payload.metaIds 按唯一 metaId 一一对应；payloadSha256 正确；只有 execution=`SUCCEEDED` 且全部 items.valid=true 才能把对应列写为 `REUSE`。
7. 有 createBatch 时，requestBindings 与 payload.createRequests 按索引一一对应，且只覆盖 `CREATE_SYSTEM/CREATE_CUSTOM` 列；payloadSha256 与规范化 payload 一致；成功响应按相同索引回填到对应列。
8. `complete` 只能用于所有列已确认且映射完整的结果；有启用或创建项时，相应 execution 必须为 `SUCCEEDED`。
9. 输出目录原先不存在或为空，没有覆盖旧产物。
