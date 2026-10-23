# 错误与安全处理

## 常见结果

| 错误/状态 | 处理 |
|---|---|
| `ENTERPRISE_FEATURE_DISABLED` | 说明企业账号已识别，但系统企业工具总开关关闭；联系管理员在“系统设置”中启用，不尝试隐藏工具 |
| `ENTERPRISE_RUNTIME_NOT_CONFIGURED` / `ENTERPRISE_RUNTIME_UNAVAILABLE` | 管理员检查 MySQL 企业查询后端、企业控制表和 Redis；校验通过前不得声称企业能力已开放 |
| `CONFIRMATION_REQUIRED` | 调用确认工具并让用户逐项确认 |
| `INVALID_QUERY` / `INVALID_EXPORT_REQUEST` | 根据实时 Schema 修正参数，重新完成受影响的确认 |
| `DATA_SCOPE_DENIED` | 说明当前企业访问配置的数据范围，不静默改小范围执行 |
| `TOOL_NOT_ALLOWED` | 说明当前企业访问配置未获该工具权限 |
| `RATE_LIMITED` | 稍后再尝试当前安全操作，不拆分请求绕过 |
| `EXPORT_PREVIEW_CONFIRMATION_REQUIRED` | 展示 `zhiping_preview_export` 的 20 条样本并取得用户确认；查询条件变化后重新预览 |
| `choice_required` / `EXPORT_QUOTA_CHOICE_REQUIRED` | 展示所需条数与剩余额度，等待用户选择指定条数、用光额度或停止下载；不代答 |
| `INVALID_DOWNLOAD_ROWS` | 请用户选择 1 至当日剩余额度的条数 |
| `QUOTA_EXCEEDED` | 原样展示维度、用户访问配置/公司层级及实际数字；不拆任务绕过 |
| `EXPORT_CONFLICT` | 查询并等待 `active_job_id` 进入终态 |
| `EXPORT_NOT_FOUND` | 核对是否使用本次成功创建返回的完整 job_id |
| `EXPORT_TOKEN_MISMATCH` | 保持创建任务时的同一 OAuth 企业身份；不要换账号重建相同任务 |
| `EXPORT_FILE_MISSING` | 说明服务端文件缺失并联系运维；不使用查询兜底 |
| `confirmation_required` | 停止轮询；用 Host 实际支持的结构化交互，或完整展示服务端问题和选项，等待用户明确答复 |
| `failed` | 逐字报告错误码和错误信息，停止自动重试 |

只有服务端明确返回 `EXPORT_STORAGE_FULL` 或 `EXPORT_STORAGE_QUOTA_EXCEEDED` 时，才能判断为存储不足。普通 `EXPORT_FAILED` 不能猜测成磁盘、网络、SQL 或权限问题。

## 禁止的恢复方式

- 按机构、日期、产品或指标拆分以绕过限额。
- 反复调用在线查询取得全部页面。
- 把预览结果、多个导出或 Host 本地文件拼成客户文件。
- 自动改成最近日期、其他机构、其他产品维度或较少字段。
- 在 Host 中生成或运行 SQL、Python 导出脚本。
- 读取本地知识库副本覆盖 MCP 实时契约。

## 可以执行的恢复方式

- 参数不符合实时 Schema：修正参数并重新确认。
- 用户主动改变范围：按新需求重新开始确认流程。
- 服务端要求补充确认：把服务端统计和选项完整展示给用户。
- 限流但未超过日配额：在合理等待后重试同一安全调用。
- 运维或权限错误：提供 `request_id`、`job_id`、原始错误码和错误信息，停止业务兜底。

## 请求预算与错误恢复

认证、身份路由、问题记录、业务调用和个人计费共用从 MCP 入口起算的 25 秒协作式预算；失败后的积分恢复另有最多 3 秒预算。生产总延迟仍需实测，不能把客户端 30 秒连接超时等同于业务保障。

企业工具返回 `isError=true` 或 `error` / `error_code` 时只能报告实际失败，不得声称任务完成；正常空结果仍是成功。`UPSTREAM_TIMEOUT` 表示结果尚未确认，不得自动重试企业创建导出、月报或保存/删除偏好。同步工作线程可能继续运行，先由管理员核查；已有真实 job_id 时才可查询状态，不得猜测任务标识。个人请求以原 request_key 核查，`BILLING_RECOVERY_PENDING` 时查看余额，不承诺已退分，不更换标识重复计费。

服务在问题记录启用时向授权页展示实际保留天数。问题参数仍仅用于排障和用途分析，不发送凭证、手机号或验证码。
