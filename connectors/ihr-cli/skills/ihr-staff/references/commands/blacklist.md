# 黑名单查询命令

## `staff blacklist +search`

查询当前租户自有且未删除的黑名单记录。完整 flags 读取命令 `--help`。

常用筛选：

- `--staff-name/--staff-no/--mobile/--id-card-no`：人员线索；
- `--effect-status UNCONFIRM/EFFECT/INVALID`：生效状态；
- `--submitter/--remark`：提交人或备注；
- `--created-from/--created-to`：闭区间日期，必须成对且开始不晚于结束；
- `--sort-field/--sort-direction`：必须成对；
- `--page/--page-size`：1-based，单页最多 100 条。

成功时保留黑名单分页业务响应；空结果是成功空页，不改成“不存在”。手机号和证件号筛选会在公开请求输出中脱敏；备注仍属于敏感业务文本，只按用户目标最小展示。

执行前必须明确至少一项人员、状态、日期范围，或用户明确要求拉取当前权限可见的全部记录。普通查询只执行一次当前页；明确全量、完整拉取或后续分析时按共享规则串行翻页，禁止并发。如只需数量且未要求拉全部行，使用权威总数。禁止导出或改走 raw API。
