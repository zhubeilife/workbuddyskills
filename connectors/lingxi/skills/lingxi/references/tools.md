# 工具参数参考

本文件从 2026-09-09 本地灵析 MCP Provider 的 `tools()` 提取，覆盖 18 个工具。它是连接器发布快照，不是生产接口的实时响应；实际调用以当前可用定义和业务响应为准。

下表保留服务端参数说明，包括默认值和上限。没有明确说明的参数不补造默认值。工具返回通常是 MCP 文本内容中的业务 JSON；工作流和返回示例见 `workflows.md`。

## create_ai_form

根据自然语言需求创建灵析表单草稿，并返回异步任务 token。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `description` | string | 是 | 表单需求描述，最多 500 字。 |
| `question_range` | string | 否 | 题目数量范围，默认 5-10。 枚举：`5-10`, `10-15`, `15-20`。 |

## get_ai_form_status

查询 AI 创建表单任务状态，完成后返回表单编辑页、发布页和 C 端访问链接。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `task_token` | string | 是 | create_ai_form 返回的任务 token。 |

## get_ai_form_capabilities

查看灵析 AI 创建表单当前支持的题型、联系人字段和限制。

无参数，传 `{}`。

## list_forms

获取当前机构可由灵析 MCP 继续处理的旧版表单列表，支持按标题搜索。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `keyword` | string | 否 | 表单标题关键词，可不传。 |
| `page` | integer | 否 | 页码，默认 1。 |
| `limit` | integer | 否 | 每页数量，默认 20，最大 50。 |

## get_periodic_org_summary

获取当前机构全部月捐项目的经营汇总数据，包含当前盘子、区间汇总、月度趋势和项目拆分。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start_date` | string | 否 | 开始日期，格式 YYYY-MM-DD；不传默认近 12 个月。 |
| `end_date` | string | 否 | 结束日期，格式 YYYY-MM-DD；不传默认今天。 |

## list_periodic_projects

获取当前机构月捐项目列表，支持按项目名称和状态筛选。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `keyword` | string | 否 | 项目名称关键词，可不传。 |
| `status` | string | 否 | 项目状态：draft、published、closed、stop、admin_closed、suspend、completed。 |
| `page` | integer | 否 | 页码，默认 1。 |
| `limit` | integer | 否 | 每页数量，默认 20，最大 50。 |

## get_periodic_project_summary

获取当前机构指定月捐项目的当前盘子、区间汇总和月度经营趋势。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project_id` | string | 是 | 月捐项目 ID，支持项目加密 ID 或数字 ID。 |
| `start_date` | string | 否 | 开始日期，格式 YYYY-MM-DD；不传默认近 12 个月。 |
| `end_date` | string | 否 | 结束日期，格式 YYYY-MM-DD；不传默认今天。 |

## get_periodic_project_analysis_dataset

分页获取指定月捐项目的脱敏紧凑分析数据，每个月捐绑定返回一行。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `project_id` | string | 是 | 月捐项目 ID，支持项目加密 ID 或数字 ID。 |
| `start_date` | string | 否 | 开始日期，格式 YYYY-MM-DD；不传默认近 12 个月。 |
| `end_date` | string | 否 | 结束日期，格式 YYYY-MM-DD；不传默认今天。 |
| `before_bind_id` | string | 否 | 游标分页参数，传上一批返回的 next_cursor 获取更早绑定。 |
| `limit` | integer | 否 | 返回数量，默认 200，最大 500。 |

## list_form_submissions

获取当前机构指定表单的提交记录列表，可按备注关键词排除已处理记录。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `form_id` | string | 是 | 表单 ID，支持 LXE 加密 ID 或数字 ID。 |
| `before_fill_id` | string | 否 | 游标分页参数，传上一批返回的 next_cursor 获取更早提交记录。 |
| `exclude_remark` | string | 否 | 排除包含该备注关键词的提交记录，例如：已完成发送。 |
| `limit` | integer | 否 | 返回数量，默认 20，最大 200。 |
| `mask_sensitive_data` | boolean | 否 | 是否对姓名、手机、邮箱、身份证和地址脱敏。默认 false；仅当用户明确要求脱敏时传 true。 Schema 默认值：`false`。 |

## get_form_submission_detail

获取当前机构某条表单提交记录的完整字段和备注。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `fill_id` | string | 是 | 提交记录 ID，支持 LXE 加密 ID 或数字 ID。 |
| `mask_sensitive_data` | boolean | 否 | 是否对姓名、手机、邮箱、身份证和地址脱敏。默认 false；仅当用户明确要求脱敏时传 true。 Schema 默认值：`false`。 |

## append_form_submission_remark

给当前机构某条表单提交记录追加备注，用于标记 Agent 已处理。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `fill_id` | string | 是 | 提交记录 ID，支持 LXE 加密 ID 或数字 ID。 |
| `remark` | string | 是 | 要追加的备注内容，例如：已完成发送。 |

## list_activities

获取当前机构已发布活动列表，支持按标题、动态状态、发布时间和免费/收费筛选。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `keyword` | string | 否 | 活动标题关键词，可不传。 |
| `status` | string | 否 | 活动动态状态：waiting_signup、signup、waitlist、end_signup、signin、end_signin。 |
| `start_date` | string | 否 | 发布时间开始日期，格式 YYYY-MM-DD。 |
| `end_date` | string | 否 | 发布时间结束日期，格式 YYYY-MM-DD。 |
| `is_free` | boolean | 否 | 是否只查询免费活动，不传表示不限制。 |
| `page` | integer | 否 | 页码，默认 1。 |
| `limit` | integer | 否 | 每页数量，默认 20，最大 200。 |

## get_activity_summary

获取当前机构指定活动的基本信息、报名签到经营概览和访问链接。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `activity_id` | string | 是 | 活动 ID，支持活动加密 ID 或数字 ID。 |

## list_activity_signups

分页获取当前机构指定活动的报名记录，可排除包含指定备注的已处理记录。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `activity_id` | string | 是 | 活动 ID，支持活动加密 ID 或数字 ID。 |
| `before_signup_id` | string | 否 | 游标分页参数，传上一批返回的 next_cursor 获取更早报名记录。 |
| `session_id` | string | 否 | 签到场次 ID。与 signin_status 一起使用时，按指定场次筛选已签到或未签到报名人。 |
| `keyword` | string | 否 | 姓名、手机、邮箱或报名表单内容关键词。 |
| `signup_status` | string | 否 | 报名状态：success、cancel、waitlist、waitlist_success、waitlist_fail、waitlist_cancel。 |
| `signin_status` | string | 否 | 签到状态：signed_in 或 not_signed_in。 |
| `start_date` | string | 否 | 报名开始日期，格式 YYYY-MM-DD。 |
| `end_date` | string | 否 | 报名结束日期，格式 YYYY-MM-DD。 |
| `exclude_remark` | string | 否 | 排除备注中包含该关键词的报名记录，例如：已完成发送。 |
| `limit` | integer | 否 | 返回数量，默认 20，最大 200。 |
| `mask_sensitive_data` | boolean | 否 | 是否对姓名、手机、邮箱、身份证和地址脱敏。默认 false；仅当用户明确要求脱敏时传 true。 Schema 默认值：`false`。 |

## list_activity_signins

分页获取当前机构指定活动的签到流水，支持按签到场次和签到日期筛选。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `activity_id` | string | 是 | 活动 ID，支持活动加密 ID 或数字 ID。 |
| `session_id` | string | 否 | 签到场次 ID，可不传。 |
| `before_signin_id` | string | 否 | 游标分页参数，传上一批返回的 next_cursor 获取更早签到记录。 |
| `start_date` | string | 否 | 签到开始日期，格式 YYYY-MM-DD。 |
| `end_date` | string | 否 | 签到结束日期，格式 YYYY-MM-DD。 |
| `limit` | integer | 否 | 返回数量，默认 20，最大 200。 |
| `mask_sensitive_data` | boolean | 否 | 是否对姓名、手机、邮箱、身份证和地址脱敏。默认 false；仅当用户明确要求脱敏时传 true。 Schema 默认值：`false`。 |

## get_activity_signup_detail

获取当前机构某条活动报名记录的完整报名字段、签到状态、支付状态和备注。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `signup_id` | string | 是 | 活动报名记录 ID，支持活动加密 ID 或数字 ID。 |
| `mask_sensitive_data` | boolean | 否 | 是否对姓名、手机、邮箱、身份证和地址脱敏。默认 false；仅当用户明确要求脱敏时传 true。 Schema 默认值：`false`。 |

## append_activity_signup_remark

给当前机构某条活动报名记录追加处理备注，不覆盖原有备注。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `signup_id` | string | 是 | 活动报名记录 ID，支持活动加密 ID 或数字 ID。 |
| `remark` | string | 是 | 要追加的备注内容，例如：已完成发送。 |

## get_ai_quota

免费查询当前机构共享 AI 可用额度和累计消耗额度。已开通机构按服务端配置一次性获赠初始额度，试运行期间不过期，用完不自动补发。

无参数，传 `{}`。
