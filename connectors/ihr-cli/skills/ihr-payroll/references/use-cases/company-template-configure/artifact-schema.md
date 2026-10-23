# 薪资模板操作产物 Schema

当前 `schemaVersion` 为 `2.0.0`，固定文件名为 `payroll-template-creation.json`。产物描述一次从 `CREATE`、`RULES` 或 `ATTENDANCE` 开始的模板业务操作；每次输入、dry-run、确认或执行状态变化都写入新的 `artifact-vNNN` 目录，通过 `supersedes` 关联上一版。

## 顶层字段

| 字段 | 规则 |
| --- | --- |
| `schemaVersion` | 固定 `2.0.0`。 |
| `artifactType` | 固定 `payroll-template-creation`。 |
| `status` | `needs_input`、`needs_confirmation`、`in_progress`、`complete` 或 `blocked`。 |
| `startStage` | `CREATE`、`RULES` 或 `ATTENDANCE`。 |
| `currentStage` | `CREATE`、`RULES`、`ATTENDANCE` 或 `COMPLETE`。 |
| `nextStage` | 最早未完成阶段；完成时为 `null`。 |
| `generatedAt` | ISO 8601 时间。 |
| `template` | 模板名称、正整数 `payrollConfigId`、固定来源和拆分设置。 |
| `requestedRules` | 用户提供的分组、项目、顺序和明确删除项；未进入 RULES 时为 `null`。 |
| `steps` | `create`、`rules`、`attendance` 三个阶段状态。 |
| `issues` | `INFO`、`WARNING` 或 `BLOCKING` 问题。 |
| `summary` | 请求阶段、完成阶段和业务计数。 |
| `completedAt` | 本次请求路线全部完成时的时间；其他状态为 `null`。 |
| `supersedes` | 上一版本产物的绝对路径；第一版为 `null`。 |

产物不包含 Excel 路径、工作表、表头、列映射、单元格、薪资值或其他 Use Case 的阶段产物身份。

## `template`

```json
{
  "name": "模板名称或 null",
  "payrollConfigId": 123,
  "configFromType": "EMPTY_TEMPLATE",
  "salarySplit": false
}
```

从 RULES 或 ATTENDANCE 开始时名称可以在读取服务端模板后补齐。`payrollConfigId` 在 CREATE 成功前为 `null`，之后必须是同一个正整数。身份字段、token 和权限对象不得进入产物。

## `requestedRules`

只保存用户确认的业务结构和规范化哈希：

- `payloadSha256`：规范化分组、项目引用、顺序和删除项的 SHA-256；
- `groups[]`：有序分组，每项包含唯一 `name` 和有序 `projects[]`；
- `ungroupedProjects[]`：有序项目引用；
- `removeProjects[]`：用户明确要求删除的项目引用；
- `confirmedAt`：用户确认该业务结构的时间。

项目引用只保存用户提供的 `metaId`、code 或名称，以及解析后的 code/name；不复制候选树或完整服务端响应。公式正文只有在用户明确提供已准备配置且 RULES 保存确实需要时才保存在 `steps.rules.payload.rules`，不进入摘要或最终回复。

`steps` 中的状态、阶段和成功布尔值是机器状态；对用户展示时使用“第一步模板创建/第二步薪资项目/第三步考勤计薪”“待确认/已成功/失败/结果未知”等名称。项目类型、类别、来源、计税、进位和成本方式优先使用对应名称字段，ID/code 只作内部绑定。

## `steps`

每个阶段都有：

- `required`：本次路线是否要求该阶段；
- `status`：`NOT_REQUESTED`、`NEEDS_INPUT`、`AWAITING_CONFIRMATION`、`SUCCEEDED`、`FAILED` 或 `UNKNOWN`；
- `payloadSha256` 和必要的 public `payload`；
- `dryRun`：状态、执行时间、退出码和验证后的业务摘要；
- `confirmation`：`NOT_REQUIRED`、`AWAITING_CONFIRMATION` 或 `CONFIRMED`、确认时间和影响数量；
- `execution`：执行时间、退出码和经校验的结构化结果；
- `completedAt`。

### `steps.create`

payload 只包含：

```json
{"name":"模板名称","templateType":"EMPTY_TEMPLATE"}
```

成功结果必须包含 `createdCount=1`、正整数 `payrollConfigId`、相同名称、`configFromType=EMPTY_TEMPLATE` 和 `salarySplit=false`。

### `steps.rules`

payload 是 `snapshotHash + rules`，其中 `rules` 只含 `payrollConfigId/groupList/noGroupSalaryFieldList`。同时记录：

- snapshot 读取时间和原始 `snapshotHash`；
- `groupCount/fieldCount/inputCount/formulaCount`；
- `addedCount/movedCount/removedCount` 及明确删除项目身份；
- 成功结果的 `verified=true` 和新 `snapshotHash`；或写入已发生后只读快照通过业务不变量校验，且差异仅为第二步规则允许忽略的服务端隐藏元数据规范化。

### `steps.attendance`

payload 只包含 `payrollConfigId`。成功结果必须包含 `saved=true`、`savedCount=1`、相同模板 ID、正整数 `attendancePlanId` 和 `settingsSource=PAGE_DEFAULTS`。

## 状态与恢复

- 缺少当前阶段必要业务输入时为 `needs_input`，不执行该阶段写命令。
- dry-run 成功但尚未确认时为 `needs_confirmation`。
- 前序阶段成功、后续阶段尚未完成时为 `in_progress`，并通过 `nextStage` 指向恢复入口。
- 明确失败或未知结果为 `blocked`，至少有一个 `BLOCKING` issue；`UNKNOWN` 不得改写为失败或成功。
- `complete` 只用于本次路线要求的全部阶段均为 `SUCCEEDED`，`currentStage=COMPLETE`、`nextStage=null` 且 `completedAt` 非空。

## 自检

1. JSON、枚举和必填字段合法，新版本没有覆盖旧目录。
2. 本次路线的必要输入在首个写入前已齐备；已有产物不是硬前置条件。
3. 三个阶段始终使用同一 `payrollConfigId`；每个写阶段的 dry-run、确认和执行 payload 哈希一致。
4. RULES 从最新 snapshot 完整集合合并；未明确删除的项目仍存在，明确删除项与确认摘要一致。
5. CREATE、RULES、ATTENDANCE 的成功条件分别满足；任何 UNKNOWN、业务读回不一致或 BLOCKING issue 都不能标记 complete。
6. `nextStage` 是最早未完成阶段，恢复时不重复明确成功的写入。
