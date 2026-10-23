# 入转调离查询命令

本文件补充转正、调动、离职和租户调动设置的高频筛选与返回边界。四种入转调离业务记录彼此独立；完整 flags 使用具体命令 `--help`。

## `staff positive +search`

| 高频输入 | 业务含义 |
| --- | --- |
| `--state pending/completed` | 待转正或已转正列表；默认 pending |
| `--status` | `STAY_CONFIRM/HAS_CONFIRM/COMPLETED/GIVE_UP/QUIT_GIVE_UP` |
| `--application-status` | 转正审批状态 |
| `--assessment-status` | `INITIATE/PROCESSING/REVOKED/COMPLETED` |
| 人员、部门、员工类型、排序和分页 | 只按当前目标收窄 |

成功 `response` 是转正记录分页结果。列表分支、转正业务状态、审批状态和考核状态分别解释。

## `staff transfer +search`

常用筛选包括姓名、工号、部门 ID、调动单 `positiveStatus`、审批 `entryApplicationStatus`、排序和 1-based 当前页。命令只接受当前公开的 specification 条件，不接收 `tableCode/fieldList/fields`。

成功 `response` 是调动单分页结果。分别读取 `positiveStatus`、`entryApplicationStatus` 和实际存在的 `transferMode`；不要合成为单一“调动状态”。

## `staff transfer-setting +get`

无业务参数并拒绝业务 JSON/stdin。成功 `response` 是当前租户调动设置：`automaticTransfer`、`searchDepartment`、`sendSms`、`sendEmail`、`smsCount`、`mailSetting`。这是设置对象，不是调动单。

## `staff quit +search`

| 高频输入 | 业务含义 |
| --- | --- |
| `--state pending/completed` | 待离职或已离职列表；默认 pending |
| `--status` | `STAY_CONFIRM/HAS_CONFIRM/COMPLETED/GIVE_UP` |
| `--application-status` | 离职审批状态 |
| `--handover-status` | `UN_START/WAITING_HR_APPROVAL/COUNTERSIGN/PASSED/ABANDON` |
| `--quit-type` | 当前租户离职类型 code |

成功 `response` 是离职记录分页结果。业务、审批、交接和时间字段分别解释；不能从其中一个字段推断所有离职事项完成。

## 共同边界

- 当前四个命令均为只读；没有转正、调动、离职详情或办理命令。
- 普通查询只读取用户确认的人员、部门、状态和当前页。统计分析类按 [Staff 查询语义](../domain/query-semantics.md) 串行翻页，禁止并发请求和自动重试。
- 返回分页契约为部分完整；只使用实际响应中已确认的列表和总数字段。
