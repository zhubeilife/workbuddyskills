# 薪资表识别产物 Schema

当前 `schemaVersion` 为 `1.0.0`，固定文件名为 `payroll-table-identification.json`。每次分析或用户确认都写入新的唯一目录。

## 顶层字段

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `schemaVersion` | string | 必须为 `1.0.0` |
| `artifactType` | string | 必须为 `payroll-table-identification` |
| `status` | string | `complete`、`needs_confirmation` 或 `blocked` |
| `generatedAt` | string | ISO 8601 时间 |
| `source` | object | 上游提取产物身份 |
| `worksheets` | array | 每张已完整读取的工作表及其物理表格 |
| `mainTableDecision` | object | 薪资主表候选和选择状态 |
| `relationships` | array | 表格之间及外部工作簿的引用关系 |
| `issues` | array | 识别问题和阻断项 |
| `summary` | object | 不含原始业务值的数量摘要 |
| `supersedes` | string/null | 本次结果替代的上一版产物绝对路径；首次分析为 `null` |

## `source`

必须包含：

- `excelArtifactDirectory`：已校验提取目录的绝对路径；
- `excelSchemaVersion`：上游 manifest Schema 版本；
- `sourceFileName`、`sourceFileSha256`：来自上游 manifest；
- `sourceManifestSha256`：本次读取的 `manifest.json` SHA-256；
- `worksheetCount`、`cellCount`、`formulaCount`：本次完整遍历后核对的数量。

任何上游哈希或 Schema 变化都视为新的输入版本。不得复用旧识别结论或静默覆盖下游产物。

## `worksheets[].tables[]`

每张工作表记录 `index`、`name`、`dimension`、`cellsFile`、`cellsRead` 和 `tables`。每个 table 必须包含：

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `tableId` | string | `sheet-<三位序号>:<标准 A1 范围>` |
| `range` | string | 最小物理表格范围 |
| `role` | string | `PAYROLL_MAIN_CANDIDATE`、`AUXILIARY`、`OTHER` 或 `UNCLASSIFIED` |
| `confidence` | string | `HIGH`、`MEDIUM` 或 `LOW` |
| `headerRange` | string/null | 候选表头范围；尚未确定时为 `null` |
| `dataRange` | string/null | 候选数据范围；尚未确定时为 `null` |
| `contentCellCount` | integer | 范围内有值或公式的单元格数 |
| `formulaCellCount` | integer | 范围内公式单元格数 |
| `boundaryEvidence` | array | 物理边界 evidence code，至少一项 |
| `classificationEvidence` | array | 角色判断 evidence code；不得包含原始单元格值 |
| `issues` | array | 当前表格的非阻断或阻断问题 code |

`headerRange` 和 `dataRange` 只是后续处理的候选定位，不构成末级表头或有效员工行确认。

## `mainTableDecision`

| 字段 | 规则 |
| --- | --- |
| `state` | `auto_selected`、`user_selected`、`needs_confirmation` 或 `none` |
| `selectedTableId` | 已选择时为 tableId，否则为 `null` |
| `candidates` | 候选的 `tableId`、`confidence` 和 evidence code 摘要 |
| `confirmedAt` | `user_selected` 时记录 ISO 8601 时间，否则为 `null` |
| `confirmationNote` | 只记录选择范围和确认方式，不复制用户原话或业务数据 |

`status=complete` 时 state 只能是 `auto_selected` 或 `user_selected`。`needs_confirmation` 时不得向后续 Skill 声称主表已确定。

`state`、`role`、`kind`、`resolution` 和 evidence code 是产物内部枚举。用户确认时分别使用“自动选定/用户选定”“薪资主表候选/辅助表/其他表/未分类表”“公式引用/定义名称引用/Excel 表引用/外部工作簿引用”“已解析/未解析”等中文名称。

## `relationships[]`

每条关系包含：

- `kind`：`FORMULA_REFERENCE`、`DEFINED_NAME_REFERENCE`、`TABLE_REFERENCE` 或 `EXTERNAL_WORKBOOK_REFERENCE`；
- `sourceTableId`、`sourceCell`：工作簿级登记但无法定位来源时允许为 `null`；
- `targetTableId`：无法定位到本工作簿物理表格时为 `null`；
- `targetRange`：标准化后的引用范围；
- `businessScope`：`INTRA_TABLE`、`INTRA_WORKBOOK_EXTERNAL` 或 `EXTERNAL_WORKBOOK`；
- `resolution`：`RESOLVED` 或 `UNRESOLVED`；
- `evidence`：引用类型和定位摘要，不包含完整公式文本或单元格值。

重复关系按 `kind + sourceTableId + sourceCell + targetTableId + targetRange` 去重。

## `issues[]`

每项包含 `severity`、`code`、`message` 和可选 `sheetIndex/tableId/location`。

- `INFO`：不影响结果的说明；
- `WARNING`：局部证据不足，但不影响已选主表和关系完整性；
- `BLOCKING`：上游不完整、主表未确认、已选主表实际依赖的引用目标缺失，或产物无法校验。

仅在工作簿元数据中登记、但没有证据表明被已选主表使用的孤立外部链接记录为 `WARNING`，不能单凭 `externalLinkCount` 阻断识别。

`needs_confirmation` 至少包含 `MAIN_TABLE_CONFIRMATION_REQUIRED`。`blocked` 至少包含一个 `BLOCKING` issue。

## `summary`

只记录 `worksheetCount`、`tableCount`、`mainCandidateCount`、`auxiliaryTableCount`、`relationshipCount`、`unresolvedRelationshipCount` 和 `blockingIssueCount`。

## 自检

1. JSON 可完整解析，顶层字段和枚举合法。
2. `source` 的 Schema、哈希和计数与当前上游产物一致。
3. 工作表索引、tableId 和范围不重复；每个 tableId 与所在工作表及范围一致。
4. 表格范围位于对应工作表内；`headerRange`、`dataRange` 位于表格范围内。
5. relationship 引用的 tableId 均存在，或明确为 unresolved。
6. summary 与 worksheets、relationships、issues 的实际数量一致。
7. `complete`、`needs_confirmation`、`blocked` 与 mainTableDecision 和 issues 状态一致。
8. 输出目录原先不存在或为空，没有覆盖既有文件。
