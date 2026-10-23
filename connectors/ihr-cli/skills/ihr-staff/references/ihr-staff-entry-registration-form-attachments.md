# ihr-cli staff entry registration-form +attachments

## 入职登记附件清单

按入职信息 ID 查询登记附件配置槽位及已上传文件的元数据。用于审核前确认候选人的附件是否存在、属于哪个槽位以及文件名和大小。

命令：

`ihr-cli staff entry registration-form +attachments --entry-info-id <入职信息ID>`

参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `--entry-info-id` | string | 是 | 入职信息业务 ID。 |

也支持 `--json` 或 `--stdin`，公开输入字段为 `entryInfoId`；JSON/stdin 与分项参数互斥。

返回结果是附件槽位数组。每个槽位包含名称、说明、类型、是否必填、启用状态和 `attachements` 文件数组；文件项包含 `fileId`、文件名、附件名称和大小。`fileId` 只能作为用户已确认范围内的 `ihr-cli file +get --file-id <fileId>` 或 `file +batch-get` 输入，文件服务会再次校验当前登录态的可见性；不得根据 ID 拼接下载地址、枚举 ID 或把它展示给不需要该标识的用户。公开 Shortcut 不输出槽位 ID、附件记录 ID、签名 URL 或未知上游字段；当前命令不读取文件内容、不提供下载能力。

这是租户范围内的敏感只读查询，策略为 `CONFIRM_REQUIRED`。只有用户已明确指定入职信息 ID、并确认要在当前审核流程查看附件清单后才执行一次；不得猜测或批量枚举 ID。遇到权限错误应停止并提示重新登录或缩小范围，不能使用 raw interface 绕过 staff 命令。
