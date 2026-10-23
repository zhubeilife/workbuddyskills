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

返回结果是附件槽位数组。每个槽位包含名称、说明、类型、`required`、启用状态和 `attachements` 文件数组。`required` 是**公司级**附件项配置（1 = 公司必填、2 = 公司非必填），它不代表模板级「员工必填」；判断「员工必填缺失」必须取 `ihr-cli staff entry registration-template +get`（按该登记表的 templateCode）返回的模板级 `staffRequired`，两者结论不一致时标记为「需人工确认」，不得直接用 `required` 断言员工漏传。文件项包含 `fileId`、文件名、附件名称和大小：`size` 已是人类可读单位（1024 进制，小于 1024 时输出整数 B，其余取最大适用单位 B/KB/MB/GB/TB 并四舍五入保留 1 位小数，如 `351.9 KB`），`sizeBytes` 是同一文件的精确字节数（如 `360371`）；报告直接展示 `size`，不要再自行追加 `bytes` 或做二次换算。`fileId` 只能作为用户已确认范围内的 `ihr-cli file +get --file-id <fileId>` 或 `file +batch-get` 输入，文件服务会再次校验当前登录态的可见性；不得根据 ID 拼接下载地址、枚举 ID 或把它展示给不需要该标识的用户。公开 Shortcut 不输出槽位 ID、附件记录 ID、签名 URL 或未知上游字段；当前命令不读取文件内容、不提供下载能力。`file +get`/`file +upload` 的 `size`、`file +batch-get` 的 `fileSize` 已与本命令采用同一口径（1024 进制、人类可读，保留 1 位小数），并各自附带 `sizeBytes`/`fileSizeBytes` 精确字节字段；三个命令展示一致，可直接复用 CLI 输出的 `size`/`fileSize`，无需二次换算，也不要再追加 `bytes`。

这是租户范围内的敏感只读查询，策略为 `CONFIRM_REQUIRED`。只有用户已明确指定入职信息 ID、并确认要在当前审核流程查看附件清单后才执行一次；不得猜测或批量枚举 ID。遇到权限错误应停止并提示重新登录或缩小范围，不能使用 raw interface 绕过 staff 命令。
