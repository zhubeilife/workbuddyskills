# Excel 创建薪资模板编排产物 Schema

当前 `schemaVersion` 为 `1.0.0`，固定文件名为 `payroll-template-from-excel.json`。每次输入、确认、阶段或执行状态变化都写入新的 `artifact-vNNN` 目录，通过 `supersedes` 关联上一版。

## 顶层字段

| 字段 | 规则 |
| --- | --- |
| `schemaVersion` | 固定 `1.0.0`。 |
| `artifactType` | 固定 `payroll-template-from-excel`。 |
| `runId` | 本次编排的唯一标识。 |
| `status` | `needs_input`、`needs_confirmation`、`in_progress`、`complete`、`blocked` 或 `unknown`。 |
| `currentStage` | `EXTRACT`、`IDENTIFY`、`PROPOSE_FIELDS`、`PLAN`、`FINALIZE_FIELDS`、`CREATE_TEMPLATE`、`PREPARE_FORMULAS`、`SAVE_RULES`、`SAVE_ATTENDANCE` 或 `COMPLETE`。 |
| `nextStage` | 最早未完成阶段；完成时为 `null`。 |
| `generatedAt/completedAt` | ISO 8601 时间；未完成时 `completedAt=null`。 |
| `executionContext` | 环境、不可逆公司指纹及最近验证时间。 |
| `source` | 工作簿与三个上游阶段产物的身份链。 |
| `template` | 模板请求、ID 和模板阶段产物引用。 |
| `layoutPlan` | Excel 列到一层模板分组的已确认计划。 |
| `formulaPlan` | 公式列分类和公式阶段产物引用，不含公式正文或样例值。 |
| `stages` | 各阶段状态、阶段产物和副作用摘要。 |
| `issues` | `INFO`、`WARNING` 或 `BLOCKING` 问题。 |
| `summary` | 列、映射、公式和已发生写入的数量。 |
| `supersedes` | 上一版本绝对路径；第一版为 `null`。 |

## 执行上下文与身份

```json
{
  "executionContext": {
    "environment": "qa2",
    "companyFingerprintSha256": "不可逆哈希",
    "verifiedAt": "ISO 8601"
  },
  "source": {
    "sourceFileName": "payroll.xlsx",
    "sourceFileSha256": "...",
    "excelArtifact": {"path": "绝对路径/manifest.json", "sha256": "..."},
    "identificationArtifact": {"path": "绝对路径/payroll-table-identification.json", "sha256": "..."},
    "mappingArtifact": {"path": "绝对路径/salary-field-mapping.json", "sha256": "..."},
    "selectedTableId": "sheet-001:A1:Z100"
  }
}
```

公司指纹由当前环境和稳定公司身份生成，只用于检测切换；产物不得保存原始 `companyId`、`userId`、token、Authorization 或权限对象。

## `template`

```json
{
  "requestedName": "2026 年薪资模板",
  "configFromType": "EMPTY_TEMPLATE",
  "salarySplit": false,
  "payrollConfigId": "717142133149696",
  "artifact": {"path": "绝对路径/payroll-template-creation.json", "sha256": "..."}
}
```

模板 ID 始终保存为字符串。CREATE 成功前为 `null`，成功后所有阶段必须保持同一值。

## `layoutPlan`

```json
{
  "status": "PROPOSED|CONFIRMED",
  "groups": [
    {"name": "收入项", "excelColumnIds": ["sheet-001:col:C", "sheet-001:col:D"]}
  ],
  "ungroupedExcelColumnIds": ["sheet-001:col:A"],
  "columnCount": 3,
  "confirmedAt": "ISO 8601 或 null",
  "payloadSha256": "规范化布局计划哈希"
}
```

所有映射列必须恰好出现一次；数组顺序就是模板顺序。这里只保存 Excel 列标识，不把列标识提交业务接口或写入业务库。

## `formulaPlan`

```json
{
  "status": "NOT_REQUIRED|NEEDS_INPUT|CONFIRMED|COMPLETE",
  "targets": [
    {
      "excelColumnId": "sheet-001:col:D",
      "fieldCode": "bonus",
      "fieldName": "奖金",
      "decision": "FORMULA|INPUT",
      "patternCount": 1,
      "hasMixedValues": false,
      "formulaArtifact": {"path": "绝对路径/formula-edit.json", "sha256": "..."},
      "validated": true,
      "calculated": true,
      "expectedConfirmed": true
    }
  ],
  "formulaTargetCount": 1,
  "inputOverrideCount": 0,
  "confirmedAt": "ISO 8601 或 null"
}
```

产物不保存公式正文、单元格地址列表、员工行或试算原始值。`decision=FORMULA` 的目标完成时必须引用公式编辑阶段产物，并通过验证、试算和结果确认。

## `stages`

每个阶段包含：

- `status`：`NOT_STARTED`、`NEEDS_INPUT`、`AWAITING_CONFIRMATION`、`SUCCEEDED`、`SKIPPED`、`FAILED` 或 `UNKNOWN`；
- `startedAt/completedAt`；
- `childSkill` 和可选 `childArtifact.path/sha256`；
- `inputSha256`：传给对应阶段的规范化输入哈希；
- `confirmation`：确认状态、时间和对应 payload 哈希；
- `result`：只保存完成条件和数量，不复制阶段产物正文。

`EXTRACT/IDENTIFY/PROPOSE_FIELDS/FINALIZE_FIELDS/PREPARE_FORMULAS/CREATE_TEMPLATE/SAVE_RULES/SAVE_ATTENDANCE` 分别引用对应阶段产物。`PROPOSE_FIELDS` 与 `FINALIZE_FIELDS` 引用同一个字段匹配运行的不同版本；`PLAN` 由本 Use Case 完成。没有公式目标时 `PREPARE_FORMULAS.status=SKIPPED`。

## `summary` 与副作用

`summary` 至少记录：

- `columnCount/mappingCount/groupCount/ungroupedCount`；
- `formulaTargetCount/inputTargetCount`；
- `enabledFieldCount/createdFieldCount`；
- `templateCreated/rulesSaved/attendanceSaved`。

已发生写入即使后续失败也保留在摘要。编排产物只记录稳定 ID、名称和数量，不复制批量请求、完整规则或页面默认考勤正文。

## 状态与自检

1. 每个路径为绝对路径且目标存在；哈希、Schema、源文件和已选主表身份逐层一致。
2. `currentStage/nextStage/status` 与最早未完成阶段一致；`unknown` 至少有一个 `UNKNOWN` 写阶段，`blocked` 至少有一个 `BLOCKING` issue。
3. 布局列集合等于映射产物完整列集合；所有目标唯一且顺序稳定。
4. 公式数量与公式计划一致；每个 FORMULA 目标都有已完成阶段产物，每个 INPUT 目标不携带公式阶段产物。
5. 每次写入的确认晚于对应 dry-run，且确认哈希、执行输入哈希一致。
6. 模板 ID 在 CREATE 后不可变化；RULES 和 ATTENDANCE 的成功结果分别满足 `verified=true` 与 `saved=true/savedCount=1/settingsSource=PAGE_DEFAULTS`。
7. `complete` 仅用于全部必要阶段 `SUCCEEDED` 或允许的 `SKIPPED`、无 BLOCKING issue、`nextStage=null` 且 `completedAt` 非空。
8. 新版本不得覆盖旧目录；产物不得包含员工数据、薪资样例、完整公式、原始公司/用户身份或凭据。
