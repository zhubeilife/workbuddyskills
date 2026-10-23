# 入职登记命令

本文件补充入职登记表、附件、模板和审核通过命令。完整 flags 以具体命令 `--help` 为准。

## `staff entry registration-form +search`

查询待确认和退回修改的审核列表，状态固定收窄为 `CONFIRM/RECHECK`。常用筛选包括姓名、手机号、部门 ID、员工类型、入职日期、提交日期、流水号、登记表 ID 和当前页。

成功 `response` 是分页审核列表。重点只使用实际返回的 `registrationId`、姓名、脱敏手机号、`registrationStatus`、关联 `entryInfoId/entryFormId`、模板信息及分页总数；响应元素仍为部分契约。

## `staff entry registration-form +get`

`--registration-id` 必填。成功 `response` 是单条登记表审核摘要，包括基础信息、登记状态、模板信息、关联 ID，以及动态字段的展示名、类型、必填和是否已填写；不保证返回动态字段原值。

## `staff entry registration-form +attachments`

`--entry-info-id` 必填。成功 `response` 是附件槽位数组，包括名称、说明、类型、必填、启用状态和已上传文件元数据。文件 ID 只用于当前授权范围的文件读取入口；不得拼接下载地址或枚举 ID。本命令不读取文件内容。

## `staff entry registration-template +get`

`--code` 必填，`--version` 可选；省略版本时读取当前有效版本。模板 code 必须来自用户或当前登记表结果，不猜测或枚举。

成功响应是白名单化的模板规则摘要，包括模板名称、状态、版本、字段必填/类型和附件要求。它只用于理解登记要求，不修改模板，也不能以模板 ID 代替登记表 ID。

## `staff entry registration-form +approval-pass`

`--registration-id` 必填；可选关联 `--entry-id`、邮件、短信和备注。首次执行 `--hc-weak=false`。dry-run 不需要确认 ID，只验证本地输入并展示计划。

实际审核必须提供相同的 `--confirm-registration-id`。审核通过还会把登记资料同步到已有待入职，或创建对应待入职；不会直接进入花名册。成功 `response.state=true` 表示本次审核通过；`warnInfoDetails` 表示编制提示。执行后必须重新查询同一登记表，并核对可获得的关联 `entryFormId`。

## 共同边界

- 审核列表普通查询只读取用户确认的当前页；明确全量、完整拉取或后续分析时按共享规则串行翻页，禁止并发。不执行审核通过。
- 审核前用同一登记表核对姓名、手机号、状态和关联对象；需要附件时再查询附件。
- 审核前的查询结果只是规划依据；最终提交必须由 CLI 或后端重新读取并校验登记表状态、关联待入职、权限、重复审核和业务前置条件。
- 是否发送短信/邮件会产生外部通知，必须在最终确认中明确列出；默认均为 false。
- 审核通过不等于确认待入职或进入花名册；它可能创建或更新关联待入职。
- 弱编警告经二次确认后只重试一次；权限、强编、业务失败或结果未知时停止并只读核对。
