# 调用示例

示例中的 ID 均为占位符，调用时使用搜索结果中的真实 ID。示例用于说明工作流，返回字段以实际工具结果为准。

## 整理表单反馈

用户：“整理「项目申请表」的反馈，按申请方向分类。”

1. `list_forms`：`{"keyword":"项目申请表","page":1,"limit":20}`。
2. 确认目标后，`list_form_submissions`：`{"form_id":"<form_id>","limit":20}`。
3. 读取业务 JSON：

```json
{
  "limit": 20,
  "has_more": true,
  "next_cursor": "<next_cursor>",
  "submissions": [
    {
      "fill_id": "<fill_id>",
      "form_id": "<form_id>",
      "submit_time": "<submit_time>",
      "latest_remark": "",
      "fields": []
    }
  ]
}
```

4. 下一页传 `{"form_id":"<form_id>","before_fill_id":"<next_cursor>","limit":20}`，逐页分类汇总。
5. 仅整理数据不需要追加备注。若用户另行要求标记已整理记录，调用 `append_form_submission_remark`：`{"fill_id":"<fill_id>","remark":"已完成人工核对"}`，备注必须符合实际完成的动作，不能照抄不实状态。

## 创建志愿者报名表

1. `get_ai_form_capabilities`：`{}`。
2. `create_ai_form`：

```json
{
  "description": "创建志愿者报名表，收集姓名、手机号、可服务时间和特长。",
  "question_range": "5-10"
}
```

3. 收到 `{"state":"processing","task_token":"<task_token>"}` 后，调用 `get_ai_form_status`：`{"task_token":"<task_token>"}`。
4. 根据 `state` 告知处理状态；只有 `done` 才展示实际返回的 `edit_url`、`release_url`、`public_url` 并报告创建成功。不要把任务 token 当成表单 ID。

## 查询指定场次未签到人员

1. `list_activities`：`{"keyword":"公益开放日","page":1,"limit":20}`。
2. `get_activity_summary`：`{"activity_id":"<activity_id>"}`，从返回的 `sessions` 中确定用户指定场次。
3. `list_activity_signups`：

```json
{
  "activity_id": "<activity_id>",
  "session_id": "<session_id>",
  "signup_status": "success",
  "signin_status": "not_signed_in",
  "limit": 20
}
```

4. 使用 `signups`、`has_more`、`next_cursor` 读取及翻页，下一页参数为 `before_signup_id`。
5. 用户需要完整报名字段时，按返回的 `signup_id` 调用 `get_activity_signup_detail`。如果不限定场次，则省略 `session_id`，并说明采用“任意场次是否签到”的口径。

## 分析月捐项目

1. `list_periodic_projects`：`{"keyword":"伙伴计划","page":1,"limit":20}`。
2. 用明确日期调用 `get_periodic_project_summary`，例如：

```json
{
  "project_id": "<project_id>",
  "start_date": "2026-06-01",
  "end_date": "2026-08-31"
}
```

3. 若需要绑定级分析，再调用 `get_periodic_project_analysis_dataset`，保留项目和日期参数，加入合适的 `limit`。
4. 数据集返回 `columns`、`rows`、`months`、`channel_map`、`has_more`、`next_cursor` 等。根据列名解释行，使用 `before_bind_id` 翻页。
5. 报告分别说明总体指标、结构分析、覆盖范围和待核实的解释。用户问“全机构”时优先调用 `get_periodic_org_summary`，不能用一个项目代表全机构。

## 处理后发送邮件并写回备注

只有用户明确授权外发且另有可用的邮件工具时才执行发送。

1. 用明确的处理标记作为 `exclude_remark` 读取未处理反馈或报名。
2. 为每条记录生成内容，按用户要求核对收件人和发送范围。
3. 用邮件工具发送，取得明确成功结果。
4. 表单反馈调用 `append_form_submission_remark`；活动报名调用 `append_activity_signup_remark`。备注记录已完成的真实动作。
5. 外发成功但备注未确认成功时暂停该批次，报告记录 ID 和当前状态，防止重复外发。
