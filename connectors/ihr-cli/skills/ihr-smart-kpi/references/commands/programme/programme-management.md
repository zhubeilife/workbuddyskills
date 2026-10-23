# 考核方案管理

考核方案命令覆盖方案列表、详情和五个配置步骤。命令按后端资源动作拆分，Skill 负责在同一会话中编排，不把多个写入接口拼成一个请求。

## 命令清单

只读命令：

- `ihr-cli smart-kpi programme +list`
- `ihr-cli smart-kpi programme +detail`
- `ihr-cli smart-kpi programme +period`
- `ihr-cli smart-kpi programme +scope`
- `ihr-cli smart-kpi programme +scope-templates`
- `ihr-cli smart-kpi programme +process`
- `ihr-cli smart-kpi programme +process-nodes`
- `ihr-cli smart-kpi programme +result-setting`
- `ihr-cli smart-kpi programme +grade-rules`
- `ihr-cli smart-kpi programme +force-rules`
- `ihr-cli smart-kpi programme +department-groups`

写入命令：

- `ihr-cli smart-kpi programme +save-basic`
- `ihr-cli smart-kpi programme +save-period`
- `ihr-cli smart-kpi programme +save-scope`
- `ihr-cli smart-kpi programme +save-process`
- `ihr-cli smart-kpi programme +save-result-setting`

所有完整 flags 以对应命令的 `--help` 为准。复杂保存载荷使用 `--json` 或 `--stdin`，两者不能同时使用，也不能和同一命令的分项 flags 混用。真实保存必须带 `--confirm`；不带 `--confirm` 的执行不会发送写入请求。

## 定位和 ID

1. 先用 `programme +list` 按名称、类型、运行状态、设置状态和考核对象查询。
2. 由当前会话列表结果得到唯一 `programmeId` 后，才调用详情或步骤命令。
3. 不把 `companyId`、`userId`、`staffId`、`leader`、token 或权限字段作为业务输入；后端从登录上下文注入并校验。
4. 不做额外列表预检，不用猜测的外部 ID 绕过后端权限和数据范围。

当前 CLI 不维护方案 ID 的会话归属清单，也不通过额外列表请求代替后端对象级授权。后端源码中详情及部分步骤接口未见统一的方案归属注解或公司条件时，不能把第 2 条当作服务端安全边界；跨公司/非当前数据范围的真实权限验证保持 `PENDING`，应由绩效服务补齐对象级校验后再完成安全验收。

## 页面步骤和编排

前端页面顺序是：基本信息、考核周期、考核范围、流程、结果设置。CLI 不强制顺序；Skill 根据用户目标按需读取和保存。

- 基本信息：`+detail` 或新建载荷，保存用 `+save-basic`。后端返回 `IdVo.id`，后续步骤使用该 ID。
- 考核周期：先用方案详情取得流程 ID，再用 `process +list` 的 `hasAppointedDateNode` 判断是否适用；不适用时返回成功 envelope 的 `applicable=false`，退出码为 0，且不调用周期读写接口。
- 考核范围：先读 `+scope-templates` 获取可选考核模板和指标模板，再按前端二维 `paramList` 构造 `+save-scope`。
- 流程：使用 `+process` 和 `+process-nodes` 获取现有设置与节点，按 `evaluateSetting` 二选一填写 `unifyProcessSettingParams` 或 `evaluateProcessSettings`，再调用 `+save-process`。
- 结果设置：先读取 `+result-setting`、`+process-nodes`、`+grade-rules`、`+force-rules`、`+department-groups`，按联动条件裁剪字段后调用 `+save-result-setting`。

第 4 步流程保存和第 5 步结果设置保存会由后端清理该方案未开始任务，并按现有逻辑重建任务。Skill 不自行删除任务；真实写入前必须向客户说明这一副作用并取得确认。

## 基本信息构造

`+save-basic` 的 JSON 对象对应后端 `ProgrammeBasicParam`。必须提供 `programmeName`、`programmeType`（`CYCLE`/`ACYCLIC`）和 `assessmentTargetType`（`STAFF`/`ORGANIZATION`）。

- 周期全选时，`cycleSettingIds` 中的 `all` 转换为 `cycleAllSelected=true`，并从 ID 列表移除 `all`。
- 部分周期时，保留调用方提供的 `cycleSettingIds`，CLI 不按名称解析、补齐或替换 ID。
- `effectiveTimeBegin`、`effectiveTimeEnd` 只接受 `yyyy-MM-dd`；页面展示字段 `effectiveTime` 不发送。
- 仅 `autoOpen=true` 时保留 `autoOpenTimeParam`；否则删除该字段。
- `autoInheritLastCycleNorm` 只对 `CYCLE` 保留。
- `updateCycleVersion` 只透传调用方明确提供的布尔值。传 `true` 表示让后端使用最新周期规则快照；CLI 不根据 `cycleHasNewVersion` 自动改写。

## 周期版本

当调用方明确传 `updateCycleVersion=true` 时：

- 全选周期使用 `cycleAllSelected=true`；
- 部分选择必须提供调用方从最新周期规则读取到的 `cycleSettingIds`；
- CLI 不按名称查找或替换周期 ID，ID 合法性由后端校验。

未传或传 `false` 时，CLI 不主动刷新周期版本，沿用后端默认语义。

## 范围、流程和结果设置

- 范围 `settingParams` 保留二维 `paramList`，每个范围包含 `scopeName`、`templateId`、`normTemplateId`、`orderNum`，以及每项的 `value`、`equal`、`type`。关闭 `staffOnRule`/`staffOffRule` 时不要发送对应字段。
- 流程只能按 `evaluateSetting=UNIFY_PROCESS` 发送统一流程参数，或按 `evaluateSetting=NORM_PROCESS` 发送指标流程参数；不要同时发送两个互斥分支。
- 流程数据引用的 `referenceDataTimingStart/End` 可以直接使用页面回显对象；其中 `fetchDataTimeNodeType`、`kpiProgrammeBasicId`、节点名称和表单校验元数据仅用于页面展示/校验，CLI 会丢弃它们，只转换 `id`、触发方式、节点 ID 和时间设置。
- 结果设置先读取详情和节点。没有评分维度时删除总分、保留位数、进位字段；未启用等级时删除等级、分组和节点强制分布字段，并发送空 `nodeConfigParams`；强制分布关闭时同样发送空节点配置。
- 结果设置使用的等级、强制分布规则和部门分组 ID 必须来自本次会话的候选查询结果，不接受无法追溯来源的外部 ID。

## 保存结果

`+save-basic` 成功必须展示后端实际返回的 `id`。其他步骤后端成功响应为 `void`，CLI 只输出 `saved=true`，不得伪造 ID，也不自动回查详情。保存失败保留业务错误信息并返回非零退出码；不得把已落库但响应异常改写成普通成功。

## 证据来源

- 前端：`ihr360-smart-kpi-static/src/actions/programme.ts`、`templates.ts`、`appraisal-period-setting`、`programme-result-setting/data-mapper.ts`。
- 后端：`ihr360-smart-kpi-provider/.../controller/programme/Programme*Controller.java` 和 `ihr360-smart-kpi-entity/.../param/programme/` DTO。
- Interface Meta：`metadata/interface-meta/smart-kpi/programme/`。

未从源码确认的枚举、权限表达式和运行时数据范围保持 `PENDING`，不以静态文档代替真实环境证据。

## 命令索引与输入边界

下列小节用于保持命令、flags 和本 reference 的可检索契约一致。全局 `--json`、`--stdin`、`--dry-run`、`--pretty`、`--output-file` 与 `--expected-env` 按共享 CLI 契约处理。

### `ihr-cli smart-kpi programme +list`

- `--page`：页码。
- `--page-size`：每页条数，原样透传后端分页约束。
- `--programme-name`：方案名称。
- `--programme-type`：`CYCLE` 或 `ACYCLIC`。
- `--cycle-rule-name`：周期规则名称。
- `--status`：运行状态。
- `--setting-status`：设置状态。
- `--assessment-target-type`：`STAFF` 或 `ORGANIZATION`，必填。

### `ihr-cli smart-kpi programme +detail`

- `--programme-id`：当前会话已定位的方案 ID，必填。
- `--for-show`：是否按展示语义读取。

### `ihr-cli smart-kpi programme +period`

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `--programme-id` | string | 是 | 方案 ID。用于判断方案是否包含指定日期节点。 |

### `ihr-cli smart-kpi programme +save-period`

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `--programme-id` | string | 是 | 仅用于 CLI 周期适用性预检查，不会发送到周期保存请求载荷。 |

| 输入 | 说明 |
| --- | --- |
| `--confirm` | 真实写入确认；JSON/stdin 载荷必填。 |

示例载荷（每个周期节点必须来自 `+period` 返回结果）：

```json
[
  {
    "id": 101,
    "beginTime": {"cycleScopeType": "CYCLE_START_BEFORE", "cycleUnitType": "DAY", "quantity": 2},
    "endTime": {"cycleScopeType": "CYCLE_END_AFTER", "cycleUnitType": "DAY", "quantity": 1},
    "autoEnd": false
  }
]
```

`beginTime/endTime` 只保留 `cycleScopeType`、`cycleUnitType`、`quantity`；日期展示字符串不能直接作为周期时间对象传入。

### `ihr-cli smart-kpi programme +scope`

- `--programme-id`：方案 ID，必填。

### `ihr-cli smart-kpi programme +scope-templates`

- `--programme-id`：方案 ID，必填。

### `ihr-cli smart-kpi programme +save-scope`

| 输入 | 说明 |
| --- | --- |
| `--confirm` | 真实写入确认；JSON/stdin 载荷必填。 |

范围载荷示例：

```json
{
  "programmeId": 21,
  "settingParams": [
    {
      "scopeName": "华东员工组",
      "templateId": 301,
      "normTemplateId": 401,
      "orderNum": 1,
      "paramList": [[
        {"value": ["staff-id-from-master-data"], "equal": "EQUAL", "type": "STAFF"}
      ]]
    }
  ]
}
```

`paramList` 是前端使用的二维结构；人员、部门和角色值先由外部公共 CLI 解析为真实 ID。`scopeName` 不能重复，模板 ID 必须来自本次 `+scope-templates` 结果。

### `ihr-cli smart-kpi programme +process`

- `--programme-id`：方案 ID，必填。

### `ihr-cli smart-kpi programme +process-nodes`

- `--programme-id`：方案 ID，必填。

### `ihr-cli smart-kpi programme +save-process`

| 输入 | 说明 |
| --- | --- |
| `--confirm` | 真实写入确认；JSON/stdin 载荷必填。 |

统一流程示例：

```json
{
  "programmeId": 21,
  "missOperatorSetting": "SKIP",
  "evaluateSetting": "UNIFY_PROCESS",
  "completionValueSetting": "UNIFY_PROCESS",
  "unifyProcessSettingParams": [
    {"kpiProcessNodeRoleId": 501, "weight": 100}
  ]
}
```

前端流程回显中的 `nodeId`、`matchingType`、`canUpdateRatingType` 和 `checked` 仅用于节点展示或页面状态；CLI 会在发送前移除这些字段，后端只接收 `UnifyProcessSettingParam` 字段。按指标流程时将 `evaluateSetting` 改为 `NORM_PROCESS`，必须传 `completionProcessSettings`（可以是空数组）和 `evaluateProcessSettings`，后者每项包含 `scopeId`、`normTemplateId`、`itemId`、`normId`、`kpiProcessNodeRoleId`、`normSource` 和 `weight`；两种流程数组不能同时提交有效内容。每组流程权重合计必须为 `100`，页面状态字段会被移除。

### `ihr-cli smart-kpi programme +result-setting`

- `--programme-id`：方案 ID，必填。

### `ihr-cli smart-kpi programme +grade-rules`

- `--programme-id`：方案 ID，必填。
- `--grade-name`：等级规则名称，可选。

### `ihr-cli smart-kpi programme +force-rules`

- `--kpi-grade-id`：等级规则 ID，可选。
- `--rule-name`：强制分布规则名称，可选。

### `ihr-cli smart-kpi programme +department-groups`

- `--programme-id`：方案 ID，必填。

### `ihr-cli smart-kpi programme +save-basic`

| 输入 | 说明 |
| --- | --- |
| `--confirm` | 真实写入确认；JSON/stdin 载荷必填。 |

新建周期方案示例：

```json
{
  "programmeName": "2026 年度员工绩效",
  "programmeType": "CYCLE",
  "assessmentTargetType": "STAFF",
  "cycleRuleId": 1001,
  "cycleSettingIds": ["all"],
  "autoOpen": true,
  "autoOpenTimeParam": {"cycleScopeType": "CYCLE_START_BEFORE", "cycleUnitType": "DAY", "quantity": 1},
  "effectiveTimeBegin": "2026-01-01",
  "effectiveTimeEnd": "2026-12-31",
  "updateCycleVersion": true
}
```

更新时在同一对象中提供已确认的 `id`；`updateCycleVersion` 只按调用方明确传入的值透传。页面日期字段 `effectiveTime` 不发送，`cycleSettingIds` 中的 `all` 会转为 `cycleAllSelected=true` 并移除。

### `ihr-cli smart-kpi programme +save-result-setting`

| 输入 | 说明 |
| --- | --- |
| `--confirm` | 真实写入确认；JSON/stdin 载荷必填。 |

结果设置示例：

```json
{
  "kpiProgrammeBasicId": 21,
  "enableGrade": true,
  "gradeGenerateRule": "SCORE_RANKING",
  "groupRule": "DEPARTMENT",
  "departmentLevel": "L1",
  "enableForceDistribution": false,
  "nodeConfigParams": [],
  "resultViewType": "WITH_AUTHORITY",
  "resultViewAuths": ["FINAL_SCORE"]
}
```

`enableGrade=false` 时等级、分组和节点配置会被清理，并强制发送空 `nodeConfigParams`；`enableForceDistribution=false` 时同样发送空节点配置。前端旧字段 `resultViewType/resultViewAuths` 会转换为 `resultViewSettingParam`，电子签旧字段会转换为 `electronTagSettingParam`。
## CLI implementation notes

- Period applicability is determined from the matched process returned by the existing process-list contract and its `hasAppointedDateNode` field. Do not refer to a `process +nodes` command; it is not exposed by this change.
- `programme +period` and `programme +save-period` return `applicable=false` with exit code `0` without calling the period endpoint when the process has no appointed-date node. `+save-period` requires `--programme-id` for this preflight only; it is never included in the period list payload.
- For process saves, the frontend `referenceDataTimingStart/End` objects are converted to `fetchDataRuleParam`. Both sides are required together, and the frontend and backend representations cannot be supplied together.
- Scope conditions use backend enum names for `equal` and `type`; invalid values are rejected locally.
