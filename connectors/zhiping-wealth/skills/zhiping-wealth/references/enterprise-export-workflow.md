# 服务端导出状态机

## 1. 准备请求

保存用户最初提出的完整导出需求为 `request_text`，选择一个 MCP 原生支持的 `topic`，按照实时 Schema 形成 `query`。除定位必要的发行机构 ID 外，不先调用业务查询工具取数。

货架 `app_shelf` 导出不要求点名销售机构：`sale_agency_ids=[]` 表示全部销售机构，非空列表表示指定销售机构且不限制数量。若用户按理财发行机构指定关联的代销机构，先调用 `zhiping_search_distributors_by_issuer` 获取实际代销机构 ID，再一次性写入 `sale_agency_ids`，不得每 10 家拆分任务。当用户在请求中点名发行机构（如"X理财/渤银理财发行"）时，必须把该机构解析为 org_id（如渤银=1057）写入 `issuer_org_ids`，把货架查询收敛到该发行机构的产品，避免全市场扫大表；`issuer_org_ids` 与 `sale_agency_ids`/`all_market` 正交可共存，且不是用户确认项。

## 2. 循环获取确认项

确认定义以服务端内置的 `智评理财数据库_知识库_20260914/scripts/confirmation_checklist.py` 为准。通用门禁字段固定从运行时 `MANDATORY_ITEMS` 读取（当前 11 项），并追加当前业务主题的专项字段。字段必须有可追溯值，但不等于每项都要弹窗：服务端可在用户原话与规范化 query 完全一致时绑定明确答案和安全的执行默认值。导出项目名称、逻辑路径和文件名称可由服务端生成，实际文件只能落到租户隔离目录。

调用：

```text
zhiping_get_export_confirmations(topic, request_text, query, answers)
```

处理返回状态：

- `questions` 或 `invalid_answers`：暂停创建任务。Host 实际提供兼容的结构化问答工具时，可使用返回的 `client_interaction.arguments`；否则按 `questions` 的原顺序和完整选项展示给用户，等待明确答复。`AskUserQuestion` 只是建议的适配器名称，不能据此声称 WorkBuddy 已内置该工具。
- `confirmed` 且 `auto_resolution.mode=explicit_request_fast_path`：用户已明确提出下载/导出，服务端已验证原话与 query 一致并生成一次性确认记录；直接创建任务，不再弹出普通确认或最终确认，也不保存长期偏好。
- 每轮只展示服务端本次返回的 `questions`，最多 4 项。不得把 `skipped_confirmations`、历史清单或 Skill 自己推断的问题加入弹窗，也不得添加“补充信息”。
- 保持服务端顺序：专题确认项在前，通用确认项在后；不要重排、合并或跨轮提前询问。只有服务端返回 `final_confirmation` 时才单独展示最终确认。
- 累计用户本轮明确提交的答案，并原样保留服务端 `server_resolved_answers` 已写入 `cumulative_answers` 的答案。服务端已解析的项目不得重复询问；客户端不得从原始需求自行推断服务端未解析的其他答案。
- 选项包含 `query_patch` 时合并到 query，再次调用确认工具。
- `final_confirmation`：向用户展示本次完整摘要并单独确认；不能复用历史最终确认。
- `confirmed`：保存服务端返回的完整 `confirmed_confirmations`，不要自行重建或删字段。

仅对服务端实际返回的 `questions`，选项原文、顺序和数量不得改变。知识库默认项会显示“（推荐）”，但 Host 不得自行预选或代答；服务端快通道生成的 `server_resolved_answers` 不属于 Host 代答。如果 Host 的按钮数量不足，按服务端 `presentation_instruction` 展示完整选项并让用户输入编号，不能删减选项。

明确需求示例：“帮我下载招银理财现金管理类存续的理财产品的基础数据”。当机构已解析到 `institution_ids`、现金管理类已绑定 `filters.investment_type=[5]`、当前存续已绑定 `survival_mode=point_today` 且维度为默认子产品时，确认工具应直接返回 `confirmed`。任一范围缺失、冲突或包含指定日期/区间、新发、到期等额外语义时，继续询问真正未解决的参数。

只有用户明确要求复用已保存偏好时，才使用 `reuse_preference` 或 `preference_id`。即使复用偏好，本次最终确认仍必须重新完成。

## 3. 预览并确认数据

业务确认完成后，用同一 `topic`、`request_text`、`query` 和完整 `confirmations` 调用 `zhiping_preview_export`。将返回的最多 20 条样本展示给用户，明确询问数据是否正确；预览免费且不能翻页。用户确认后，保存本次 `preview_token`，创建任务时传 `preview_confirmation={"decision":"confirm","token":<preview_token>}`。用户否认或修改查询条件时，重新完成受影响的业务确认并再次预览。不得由 Host 代替用户确认。

## 4. 创建任务

向 `zhiping_create_export` 提交相同的 `request_text`、最终 query 和完整 confirmations。成功时保存响应中逐字返回的 `job_id`。

- 返回 `job_id` 后先轮询状态，后台先核算数据量和剩余额度。无 `job_id` 时不得轮询。
- 下载量未超过剩余额度时服务端直接按全量创建任务，不能主动截短。

- 无 `job_id`：创建未成功，停止；不要调用状态工具。
- `EXPORT_CONFLICT`：保存 `active_job_id`，先等待原任务终态，不并行创建新任务。
- 任何确认或参数错误：修正后重新完成受影响的确认，不能沿用旧摘要。

## 5. 查询状态

只使用本次成功创建响应中的 `job_id` 调用 `zhiping_get_export_status`：

| 状态 | 动作 |
|---|---|
| `queued` | 继续轮询，不声称文件可下载 |
| `running` | 继续轮询，不创建重复任务 |
| `ready` | 使用当前响应的 `download_url` 交付 |
| `confirmation_required` | 停止轮询，执行返回的用户交互；旧任务不会自动继续 |
| `failed` | 原样报告 `error_code` 和 `error_message`，停止 |
| `consumed` | 报告 `remaining_download_rows_today`：您当日剩余下载额度 XX 条 |

后台补充确认完成后，按返回指令更新 query 或 confirmations，重新完成必要的最终确认并创建新任务。不要继续轮询旧任务。
若 `user_confirmation.status=quota_choice_confirmation`，展示所需条数与当日剩余额度，等待用户选择“下载指定条数”“将额度用光”或“停止下载”。指定条数须为 1 至剩余额度；分别用 `quota_choice=specified, specified_rows=<用户数值>`、`quota_choice=remaining` 或 `quota_choice=stop` 提交原 `query`、`confirmations` 和预览凭证。此时不修改业务条件，也不代答。

## 6. 下载

只下载 `ready` 状态返回的一次性 URL。不要用 HEAD、预览器或重复 GET 探测链接。导出失败、链接过期或文件缺失时报告服务端状态，不以查询分页或客户端 Excel 生成兜底。
成功下载后查询一次任务状态，向用户反馈当日剩余下载额度。
