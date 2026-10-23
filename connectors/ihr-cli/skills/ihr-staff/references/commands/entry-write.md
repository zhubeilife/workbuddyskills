# 待入职写入命令

本文件补充单条待入职创建、字段发现、编辑和确认的输入输出缺口。所有操作必须使用对应 Use Case Guide；完整 flags 仍以具体命令 `--help` 为准。

## `staff entry +create`

最小必填：`--name`、正整数 `--department-id`、11 位大陆手机号 `--mobile`、有效日期 `--entry-date YYYY-MM-DD`。可选职位、证件、性别、邮箱、合同类型、员工类型、试用期和自定义字段。

- dry-run 不需要 `--confirm-name`，只验证本地输入并展示计划；不会执行远端重复、黑名单、租户字段或编制检查。
- 实际创建必须提供与姓名完全一致的 `--confirm-name`。
- 执行链先读取当前租户配置并校验动态必填字段，再检查手机号、可选证件号和黑名单，最后创建。
- 成功 `response` 包含检查结果与 `created` 创建响应。创建响应结构仍为部分契约；必须从实际响应或后续查询确认新 `entryFormId`。

## `staff entry +update-fields`

`--entry-form-id` 必填，不接受业务 JSON/stdin。命令先验证目标详情的数据权限，再返回白名单化的字段规则：

- `fieldGroups[].metaCode/metaName/groupName`；
- `fields[].fieldName/label/fieldType`；
- `required/readOnly/editable/isMain`；
- 服务端实际提供的长度、数值、格式限制；
- 选项的 `value/label/children`。

该命令只读，不更新待入职。编辑每条记录前都要重新读取一次，不能复用其他租户或旧会话结果。

## `staff entry +update`

使用 `--entry-form-id` 与 `--update-json`，或 JSON 对象中的 `entryFormId/payload`。`payload` 是基于当前详情合并后的完整更新载荷，不是单字段 patch。

- dry-run 不需要确认 ID，只展示权限检查、元数据检查和更新计划；它不实际读取远端详情或字段规则。
- 实际更新必须提供与目标完全一致的 `--confirm-entry-form-id`。
- CLI 会再次读取详情、验证目标 ID、读取字段元数据并拒绝只读或未配置字段。
- 成功 `response` 是更新响应，但结构为部分契约；必须用 `entry +get` 回读用户要求修改的字段。

## `staff entry +confirm`

`--entry-form-id` 必填。dry-run 只展示权限检查和确认计划；实际执行必须提供相同的 `--confirm-entry-form-id`。

确认会同时处理关联登记和审批：未处于结束状态的登记表收集可能被放弃，未处于结束状态的入职审批可能被放弃或作废。执行前必须从详情核对并把该副作用纳入用户确认。

成功 `response` 是确认归档响应，结构为部分契约。完成证据必须来自后续 `entry +search --state joined`，并在得到 `staffId` 后按需要核对花名册。弱编制警告只有在用户再次确认后才允许 `--hc-weak` 重试一次；强编制失败停止。

## 共同写入规则

- 只处理一个明确对象；禁止批量、并发和自动重试。
- Use Case 中此前读取的详情、字段规则和候选状态只用于构造计划；最终提交必须由 CLI 或后端基于最新服务端状态重新校验目标身份、当前状态、权限、重复提交和业务前置条件。
- 身份上下文、token、Authorization 和内部字段不得进入业务载荷。
- `--json/--stdin` 与分项 flags 互斥。
- 超时或响应不明时先只读核对：创建查待入职候选，更新查详情，确认查 joined 与花名册；在结果仍未知时停止。
