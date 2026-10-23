# 入职查询命令

本文件补充待入职表单和入职审批查询的业务分支与返回。登记表查询见[入职登记命令](registration-form.md)。完整 flags 读取命令 `--help`。

## 待入职表单

### `staff entry +search`

| 高频输入 | 业务含义 |
| --- | --- |
| `--state pending/joined/abandoned` | 选择待入职、已确认入职或已放弃列表；默认 `pending` |
| `--keyword/--mobile` | 按姓名或手机号筛选 |
| `--department-id/--position-id` | 一个或多个真实 ID |
| `--fields` | 选择列表返回字段 |
| `--search-blacklist` | 在入职列表中补充黑名单状态，不等于查询黑名单台账 |
| `--page/--page-size` | 用户侧 1-based，每页 1-1000 条 |

CLI 固定追加对应 `state` 的列表条件，并与用户条件按 AND 组合。成功响应是待入职表单分页结果；只有该结果明确提供的总数字段才能用于数量解释。

### `staff entry +get`

`--entry-form-id` 必填。成功时 `response` 是单条待入职详情。必须使用候选结果中的真实 `entryFormId`，不能以 `staffId`、姓名或工号替代。

## 入职审批待办

### `staff entry application +search`

查询当前用户有权查看的入职审批待审批列表。至少提供一个人员、部门、职位、员工类型、审批状态或日期范围筛选；允许的待审批状态为 `INITIATE/WAITING_HR_APPROVAL/AUDIT`。

高频 flags 为 `--keyword/--staff-name`、`--id-card-no`、`--mobile`、`--department-name`、`--position-name`、`--staff-type`、`--application-status` 和分页参数。证件号只作精确筛选，不在结果中回显。

成功响应是脱敏后的单页审批记录。该命令不推进审批，也不能用来替代待入职列表或登记表审核列表。

## 共同边界

- 查询前确认目标是待入职表单还是入职审批记录；二者标识和状态不同。
- `entry +search`：普通查询只读当前页；统计分析类按 [Staff 查询语义](../domain/query-semantics.md) 串行翻页，禁止并发请求和自动重试，不扩大到全租户。
- `entry application +search`：敏感审批列表。普通查询只查用户确认的范围和当前页；明确全量、完整拉取或后续分析时按共享规则串行翻页，禁止并发。不处理审批。
- 手机号、证件号等敏感筛选和结果按最小必要使用与展示。
