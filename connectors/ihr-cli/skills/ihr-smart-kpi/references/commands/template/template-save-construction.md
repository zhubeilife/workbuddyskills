# 考核模板保存构造

以网页端三步向导联动为事实源。保存类 CLI 只做类型、必填、枚举、JSON/stdin 互斥和身份字段拒绝；只读 `template +validate-fields` 对前端回传的会话派生 `companyId` 做忽略并丢弃，不转发。业务联动按本文件裁剪，最终以后端校验为准。

## 基本信息

- `assessmentType=NORMAL`：1 个维度；必填 dimensionRule、weightRule。
- `assessmentType=DOUBLE_TRACE`：必须 2 个维度，每维必填名称/规则/权重，且恰好一个 `master=true`。
- `dimensionRule=GRADE` 时 `weightRule` 必须 `CLOSE`。
- `dimensionRule=SCORE` 时 `weightRule` 可为 `CLOSE` 或 `ONE_HUNDRED`。
- 模板名称必填、最长 50；说明最长 2000。
- 已有项目后不得修改 `assessmentType`。
- `leaders` 必填 userId 列表：默认当前登录人，或经 ihr-base 选人。不新增绩效用户列表命令。

## 项目与维度

The CLI enforces exactly one `master=true` dimension for `DOUBLE_TRACE` and rejects
duplicate or blank dimension names before any write request.

- 每个 DIMENSION 至少一个考核类项目（OBJECTIVE/KPI/SENSE_OF_WORTH/ABILITY_ASSESSMENT/SPECIAL_BONUS_PENALTY）。
- 同一维度最多一个 OBJECTIVE。
- `SPECIAL_BONUS_PENALTY` 只允许出现在 `dimensionRule=SCORE` 的维度。
- `weightRule=ONE_HUNDRED` 时至少一项 `itemWeightRule=ASSIGNED`，且这些权重之和为 100。
- 新建项目字段 ID 来自本会话 `template +fields-by-type` 或 `field-library +list`。
- KPI 项目至少展示目标/保底/冲刺/完成值之一（fieldDefaultCode 4/5/6/10 且 isShow）。
- 确认保存项目前调用 `template +validate-fields`，不得用 `formula +field-check` 替代。

## 分数项目权重链

仅 `dimensionRule=SCORE` 时适用；切换时清掉非法字段。

1. 仅 `weightRule=ONE_HUNDRED` 时出现项目权重 ASSIGNED/DONT_OPEN。
2. 指标权重：DONT_OPEN 只能 NO_WEIGHT；ASSIGNED 不得 SUM_EQUAL_ONE_HUNDRED_DIMENSION；维度权重 CLOSE 只能 NO_WEIGHT 或 SUM_EQUAL_ONE_HUNDRED_DIMENSION。
3. 计算方式：NO_WEIGHT 只能 SUM/AVG；有权重才允许 SUM_WITH_WEIGHT。
4. 分值范围：NO_WEIGHT 不得 DYNAMIC_SCORE_RANGE。
5. UNIFIED 必填本会话 `rating-rule +list` 的 normRatingRuleId 并清空自定义/动态分值；CUSTOM 必填 customScoreRange；DYNAMIC 必填 dynamicScoreRange。
6. 切到 DONT_OPEN 或 NO_WEIGHT 时，若当前是 DYNAMIC，改回 UNIFIED 并清空动态分值。

`dimensionRule=GRADE` 时使用 gradeRuleId 与 normResultGradeRule，不发送指标权重/分值范围链。等级规则来自 `grade +list`。

## 奖惩

- VETO 必填 actOn；非 VETO 不依赖 actOn。
- COVERAGE_SCORE 不得与 LINKED_TO_EVALUATOR 组合。
- 加减分默认值符号与区间按 ADD/SUBTRACT/ADD_SUBTRACT 限制。

## 权限

- processBasicId 来自本会话 `process +list`。
- 项目权限 ID 来自本会话 `+item` 或刚保存的项目结构。
- 每个节点至少一个可查看项目。
- 后续自选操作人节点之前，必须已有节点为 ALLOW_SETTING。
- 后节点可见的考核项目，前节点必须可显示或可设置。
- onlyView=true 时不得同时为 ALLOW_SETTING。
- kpiRoleId 来自 `process +list/+node` 或 `template +process`，不接受客户口头角色 ID。

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)
