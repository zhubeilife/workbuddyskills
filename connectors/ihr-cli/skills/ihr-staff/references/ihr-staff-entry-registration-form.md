# ihr-cli staff entry registration-form

入职登记表审核能力。用于查看待确认/退回修改的入职登记表，以及 HR 审核通过。

它是 `staff entry` 下的审核子环节：`staff entry +search` 查待入职/已入职/已放弃表单；本能力查入职登记表审核列表。

| 用户意图 | 命令 |
| --- | --- |
| 查入职登记表审核列表 | `ihr-cli staff entry registration-form +search` |
| 查登记附件清单 | `ihr-cli staff entry registration-form +attachments --entry-info-id <id>` |
| 按 ID 核对该人的姓名和手机号 | `ihr-cli staff entry registration-form +search --registration-id <id>` |
| 审核通过 | 先确认姓名+手机号，再执行 `ihr-cli staff entry registration-form +approval-pass --confirm-registration-id <同一登记表ID>` |

详细参数见：

- [审核列表](ihr-staff-entry-registration-form-search.md)
- [审核通过](ihr-staff-entry-registration-form-approval-pass.md)
