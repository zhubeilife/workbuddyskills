# Flow 生成工作流

## 准备与提交

1. 若用户提供参考素材，先调用 `creator_upload_media` 获取真实 `media_id`：公网 HTTPS URL 用 `source_url` 参数，本地文件用 `file_data`（base64）+ `filename` + `mime_type` 参数。然后发现模型并按 [模型与参数](model-and-operation.md) 校验请求。无需每次生成前自检连接。
2. 已有 project_id 时用 `creator_get_project` 验证 id、scene_key=flow 和可访问性；无项目或用户要求新建时用 `creator_create_project`，名称取创作主题，不含无关个人信息。保存返回的真实 id。创建结果不确定时不重建；可用 `creator_list_projects` 核实，但不能仅凭同名认定为新建项目。
3. 首次提交前生成 request_id，在当前会话保存重试所需的完整参数快照。按工具 schema 调用 `creator_create_generation_task`，保存返回的 task_id、project_id、status、output_count；必需字段缺失时报告合同错误，不合成。
4. 超时或断连时说明“提交结果未确认”。已有 task_id 则查询；没有 task_id 时不自动重发。用户明确要求重试后，仅以原 request_id 和完全相同参数重试一次；缺少原 ID 或参数则停止，不重建猜测值。已失败任务仅在用户明确要求重新生成时使用新 request_id。

## 查询与等待

- `creator_query_task` 传 task_ids 数组，在返回的 tasks 中按 task_id 精确匹配；不假定顺序，缺少目标任务则报告合同缺失。
- status：0=排队、1=执行中、2=完成、3=失败、4=取消。未知值显式报错；2/3/4 结束任务轮询。
- 仅查询状态时查一次后报告，不额外读取 history。生成流程每 12 秒查询一次，一次交互自动等待最多 5 分钟，用户明确预算优先；轮询与后续产物等待共用预算。
- 到达预算或用户停止等待时，说明最后观测状态，按后续查询需要提供 task_id。停止等待不等于失败或取消，不能承诺后台持续监控；当前无取消工具。
- 失败或取消只报告返回的相关原因，遵守技能入口的输出与隐私规则。

## 获取与展示产物

- 生成流程或用户要求查看产物时，任务终态后用对应 project_id 调用 `creator_get_history`；按 task_id 匹配 cards，多输出不能只取第一张。分页终点取 pagination.total_pages，不猜页数。
- card_type=media 时读取 media.id、media.url、media.media_type；图片优先内嵌展示，视频使用可用的预览能力或链接。仅在复用需要时附 media_id，不重复罗列已展示的链接。
- 展示匹配任务的全部 media，并简短说明 failed_output 的相关失败原因；任务完成不等于所有输出成功。
- 无目标卡片或只有 processing 时，在剩余预算内每 12 秒查询 history；预算耗尽后说明任务状态与产物暂不可用，不重新生成。
- URL、媒体快照或分页必需字段缺失时明确报告。不以 source_media、其它任务图片或 artifact_refs 替代，不构造项目 URL、本地路径或媒体地址。

完成展示或结束等待后，按技能入口规则调用 `creator_get_project_link` 并附“查看项目”链接。

## 错误与恢复

工具 isError=true、协议或后端错误均停止依赖操作，提取不含敏感信息的原因和必要下一步。认证失败按技能入口引导重新连接；其它错误不默认归因为认证问题。

### 星币不足

- 仅 `code=INSUFFICIENT_BALANCE` 触发。提示“星币不足，请充值后回复‘继续’。”用返回的 recharge_url 展示充值链接。缺少链接时说明充值入口缺失；若返回 configuration_error，提取相关配置原因，不猜地址或切换环境。
- 保留本次参数、request_id、已返回的 task_id 与最后状态，不要求用户重填。不自动充值、重试或重新授权；该错误本身不证明任务未创建或已取消。
- 用户回复“继续”后，已有 task_id 则先查询：排队或执行中继续等待，完成读取产物，失败或取消报告状态；只有明确要求重新生成才创建新逻辑任务。
- 没有 task_id 且明确收到提交接口的余额不足拒绝时，使用原 request_id 和相同参数重试一次。提交结果不确定时遵守上述提交恢复规则，不换 ID 或盲目重发。
- “继续”只授权恢复本次操作，不证明到账。再次余额不足则提示并停止，不承诺后台自动续跑。
