# 会议模块全功能验证清单（99 个 operation）

> **给执行方（其他智能体）的结论**：本 skill 通过 `weaver-work-cli` 暴露会议模块**全部 99 个 operation**
> （标准版 28 + EB 版 70 + 跨模式 1），**除本文「第 6 节 不在范围」列出的 8 项外，全部可在真机上验证完成**。
> 本文提供可直接照做的流程、逐条判据与负向用例；请按本文顺序执行，逐条留证据。

## 1. 先决条件（缺一不可）

1. **CLI**：`weaver-work-cli --version`。未安装或读取失败 → **必须先提示用户先补齐**（安装方式以共享规则为准，Agent 不能自行安装）。
2. **共享规则**：先读 `../weaver-e10-shared/SKILL.md`（安装、E10 认证、JSON 输出、高风险写入规则）。
3. **登录态**：`weaver-work-cli auth status --json` → `valid=true`；否 `=` `session_expired` 时按共享规则处理，**禁止**自行拼 Cookie。
4. **环境模式（强制第一步）**：`meeting.env.detect` → `mode=eb` 或 `mode=standard`。
   - `mode=eb` → 只能用 `meeting.eb.*`；`mode=standard` → 只能用标准版 operation。
   - **两套接口与数据互不相通**，在 EB 环境调标准版接口只会拿到空数据（反之亦然）。
5. **多租户提醒**：同一账号在不同站点（baseUrl）看到的会议不同；验证前先记录 `baseUrl` 与 `userId`，写入类验证**只用自建数据**。

## 2. 验证纪律（硬规则，违反即结论无效）

| 规则 | 说明 |
|---|---|
| 写入四步走 | `prepare` → 向用户/发起方摘要 preview → `apply`（`confirm:true` + `continuation`）→ **回读** → **清理** |
| 只用自建数据 | 写入验证一律新建名为 `CLI-VERIFY-<时间戳>` 的会议/会议室/类型/议题，**禁止**改动或删除他人真实数据 |
| 不跳步 | **禁止**跳过 prepare 直接 apply；**禁止**用真实会议试删除 |
| 失败也是结论 | FAIL 必须原文给出 `error.type/subtype` 与报错文案，**禁止**把失败写成"没有数据" |
| EB 写失败 ≠ 没写入 | EB 接口报校验错误时数据可能已落库 → **先回查再决定重试**（否则产生重复数据） |
| 每条留证据 | 记录 `operation` + 入参摘要 + 关键输出片段（id / status / count），便于复核 |
| continuation | 默认 10 分钟有效；过期返回 `continuation_expired` → 重新 prepare，**不要**重用旧 token |

## 3. 判据代号（下文表格中引用）

| 代号 | 含义 |
|---|---|
| `R-LIST` | `ok=true`；`total` 与 `count` 自洽（`total>=count`）；`rows` 每项含 `mainTable`（EB）或业务字段（标准版）；`pageNo/pageSize` 回显正确 |
| `R-DETAIL` | `ok=true` 且 `data` 非空；id 不存在时必须报 `not_found`（**不是**返回空对象） |
| `R-COUNT` | `withCount:true` 时 `total` 存在；count 与 list 允许不一致时以 `max(total, count)` 为准 |
| `W-PREP` | `status=AWAITING_CONFIRMATION`，含 `preview`（path/body）+ `continuation`；EB 的 update/delete `preview.path` **必带 `?id=<主键>`** |
| `W-APPLY` | `status=COMPLETE`；随后按"回读"列核对。**入参口径：只传 `confirm`+`continuation` 即可**（业务字段取 prepare 快照）；若同时传业务字段，必须与快照一致，否则 `target_changed` |
| `W-FAIL-SAFE` | 缺必填 → `missing_required_field`；未确认 → `confirmation.required`；主键缺失 → 服务端原文报错（不得静默成功） |
| `W-CLEAN` | 用删除类 operation 清理自建数据；EB 清理首选 `meeting.eb.meeting.delete`（级联回收占用/回执/签到） |

## 4. 全量清单

### 4.1 标准版（28 个，`mode=standard`）

| # | operation | 风险 | 必填入参 | 判据 | 回读 / 清理 |
|---|---|---|---|---|---|
| 1 | `meeting.env.detect` | read | — | 返回 `mode` + `baseUrl`；`refresh:true` 能强制刷新 | — |
| 2 | `meeting.calendar.base` | read | — | 返回工作日/时段等日历基础设置 | — |
| 3 | `meeting.detail.field` | read | `id` | `R-DETAIL` | 用 `meeting.list` 取 id |
| 4 | `meeting.list` | read | — | `R-LIST`（客户端按 `filterDate` 过滤，天然覆盖各角色） | — |
| 5 | `meeting.room.list` | read | — | `R-LIST`（`beginDate`/`endDate`/`onlyAvailable` 生效） | — |
| 6 | `meeting.room.usage` | read | — | `R-LIST`（`roomid`+`currentdate` 定位占用视图） | — |
| 7 | `meeting.type.list` | read | — | `R-LIST` | — |
| 8 | `meeting.conflict.room` | read | `beginDatetime`,`endDatetime`,`address` | 返回冲突判定（`cansub`）；同房间同时间应有冲突 | — |
| 9 | `meeting.conflict.member` | read | `beginDatetime`,`endDatetime`,`hrmids` | 同上，人员维度 | — |
| 10 | `meeting.conflict.roomAttribute` | read | `beginDatetime`,`endDatetime`,`address` | 同上，会议室属性维度 | — |
| 11 | `meeting.create.prepare` | read-before-write | `name`,`beginDatetime`,`endDatetime` | `W-PREP` + 内部自动跑冲突检测（`conflict_rejected` 属正常拒绝路径） | 记 `continuation` |
| 12 | `meeting.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | `meeting.list` 应出现；清理用 `meeting.delete.*` |
| 13 | `meeting.cancel.prepare` | read-before-write | `id` | `W-PREP` | — |
| 14 | `meeting.cancel.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读状态=已取消；不可用自建会议时跳过 |
| 15 | `meeting.delete.prepare` | read-before-write | `id` | `W-PREP` | — |
| 16 | `meeting.delete.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | **软删**：正常列表不再出现（进回收站） |
| 17 | `meeting.change.prepare` | read-before-write | `id` | `W-PREP`；按会议状态自动决定 `operateType`（草稿=UPDATE/正常=CHANGE） | — |
| 18 | `meeting.change.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读被改字段（如名称/时间） |
| 19 | `meeting.receipt.list` | read | `mtId` | `R-LIST` | 用 `mtId` 关联会议 |
| 20 | `meeting.receipt.update.prepare` | read-before-write | `mtId`,`memberId`,`attendStatus` | `W-PREP` | — |
| 21 | `meeting.receipt.update.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | `receipt.list` 回读 `attendStatus` |
| 22 | `meeting.sign.list` | read | `mtId` | `R-LIST`（返回 `signs[].id`，是补签/签退/清除的入参来源） | — |
| 23 | `meeting.sign.mark.prepare` | read-before-write | `id`（签到记录 id） | `W-PREP` | — |
| 24 | `meeting.sign.mark.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | `sign.list` 回读 `sign_time` 有值 |
| 25 | `meeting.sign.back.prepare` | read-before-write | `id` | `W-PREP` | — |
| 26 | `meeting.sign.back.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读签退时间 |
| 27 | `meeting.sign.clear.prepare` | read-before-write | `id` | `W-PREP` | — |
| 28 | `meeting.sign.clear.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读签到记录已清空 |

### 4.2 EB 版 · 会议与冲突（`mode=eb`）

| # | operation | 风险 | 必填入参 | 判据 | 回读 / 清理 |
|---|---|---|---|---|---|
| 29 | `meeting.eb.meeting.list` | read | — | `R-LIST`+`R-COUNT`；分页必须落 body `pageInfo`（只放 URL 会恒回 10 条） | — |
| 30 | `meeting.eb.meeting.detail` | read | `id` | `R-DETAIL`（数据在 `datas[0].mainTable`） | — |
| 31 | `meeting.eb.meeting.create.prepare` | read-before-write | `mt_creator`,`mt_name`,`begin_datetime`,`end_datetime`,`mt_status`,`operate_type` | `W-PREP`；内部先读 `baseSet` 判流程建会 + 冲突检测 | 记 `continuation` |
| 32 | `meeting.eb.meeting.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY`；`data.association` 应报占用/回执/签到补建结果 | 回读 list；`W-CLEAN` |
| 33 | `meeting.eb.meeting.change.prepare` | read-before-write | `id`,`operate_type` | `W-PREP`（取消用 `operate_type=CANCEL` + `mt_status=4`） | — |
| 34 | `meeting.eb.meeting.change.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读被改字段 |
| 35 | `meeting.eb.meeting.delete.prepare` | read-before-write | `id` | `W-PREP`（preview.path 带 `?id=`） | — |
| 36 | `meeting.eb.meeting.delete.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list 不含；**级联回收占用/回执/签到** |
| 37 | `meeting.eb.meeting.markDecided.prepare` | read-before-write | `id`,`is_decision` | `W-PREP` | — |
| 38 | `meeting.eb.meeting.markDecided.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 `is_decision`/`decision_Id` |
| 39 | `meeting.eb.conflict.room` | read | `beginDatetime`,`endDatetime`,`address` | 返回冲突结论；自建会议后应能识别本场会 | — |
| 40 | `meeting.eb.conflict.member` | read | `beginDatetime`,`endDatetime`,`hrmMembers` | 同上，参会人维度 | — |

### 4.3 EB 版 · 会议室 / 占用

| # | operation | 风险 | 必填入参 | 判据 | 回读 / 清理 |
|---|---|---|---|---|---|
| 41 | `meeting.eb.room.list` | read | — | `R-LIST`+`R-COUNT` | — |
| 42 | `meeting.eb.room.detail` | read | `id` | `R-DETAIL` | — |
| 43 | `meeting.eb.room.create.prepare` | read-before-write | `room_name`,`hrm_ids`,`org_id`,`status` | `W-PREP` | 记 `continuation` |
| 44 | `meeting.eb.room.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list；清理用 `.delete.*` |
| 45 | `meeting.eb.room.update.prepare` | read-before-write | `id` | `W-PREP`（preview.path 带 `?id=`） | — |
| 46 | `meeting.eb.room.update.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读被改字段 |
| 47 | `meeting.eb.room.delete.prepare` | read-before-write | `id` | `W-PREP` | — |
| 48 | `meeting.eb.room.delete.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list 不含（**只删自建会议室**） |
| 49 | `meeting.eb.roomUsage.list` | read | — | `R-LIST`+`R-COUNT` | — |
| 50 | `meeting.eb.roomUsage.detail` | read | `id` | `R-DETAIL` | — |
| 51 | `meeting.eb.roomUsage.create.prepare` | read-before-write | `mt_id` | `W-PREP` | 记 `continuation` |
| 52 | `meeting.eb.roomUsage.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list；**表关联字段是 `room_id`** |
| 53 | `meeting.eb.roomUsage.delete.prepare` | read-before-write | `id` | `W-PREP` | 见第 6 节：apply 侧环境已知异常 |
| 54 | `meeting.eb.roomUsage.delete.apply` | high-risk-write | `confirm`,`continuation` | 见第 6 节（改用 `meeting.eb.meeting.delete` 级联释放） | — |

### 4.4 EB 版 · 签到 / 回执

| # | operation | 风险 | 必填入参 | 判据 | 回读 / 清理 |
|---|---|---|---|---|---|
| 55 | `meeting.eb.sign.list` | read | — | `R-LIST`+`R-COUNT`；`data.progress.summary` 含 `signed/notSigned/attendanceRate/byState`，并带 `progress.page` | 注意 `mt_id` 返回的是**会议名称**，筛选参数 `mt_id` 才是会议 id |
| 56 | `meeting.eb.sign.detail` | read | `id` | `R-DETAIL` | — |
| 57 | `meeting.eb.sign.create.prepare` | read-before-write | `mt_id` | `W-PREP` | 记 `continuation` |
| 58 | `meeting.eb.sign.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list（时间字段**必须带秒**） |
| 59 | `meeting.eb.sign.update.prepare` | read-before-write | `id`,`mt_id` | `W-PREP`（preview.path 带 `?id=`） | — |
| 60 | `meeting.eb.sign.update.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读被改字段 |
| 61 | `meeting.eb.sign.mark.prepare` | read-before-write | `mt_id`,`user_id` | `W-PREP`；**补签走更新，不是新增** | 记 `continuation` |
| 62 | `meeting.eb.sign.mark.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 `sign.list` 的 `sign_time` |
| 63 | `meeting.eb.receipt.list` | read | — | `R-LIST`+`R-COUNT`；`progress.summary` 含 `attend/decline/noReply/replyRate` | `attend_status` 空=未回执、`0`=不参加、`1`=参加 |
| 64 | `meeting.eb.receipt.detail` | read | `id` | `R-DETAIL` | — |
| 65 | `meeting.eb.receipt.create.prepare` | read-before-write | `mt_id`,`member_type`,`member_id`,`member_manager` | `W-PREP` | 记 `continuation` |
| 66 | `meeting.eb.receipt.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list；清理随会议删除 |
| 67 | `meeting.eb.receipt.update.prepare` | read-before-write | `id`,`mt_id`,`member_id`,`attend_status` | `W-PREP` | — |
| 68 | `meeting.eb.receipt.update.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 `attend_status` |

### 4.5 EB 版 · 纪要 / 类型 / 议题

| # | operation | 风险 | 必填入参 | 判据 | 回读 / 清理 |
|---|---|---|---|---|---|
| 69 | `meeting.eb.minute.list` | read | — | `R-LIST`+`R-COUNT`；`mt_id` 支持逗号多值；关键字：`mt_minutes_subject`/`mt_minutes_no`/`parse_content`（正文 HTML）/`minutes_status` | 创建见第 6 节（无自定义接口） |
| 70 | `meeting.eb.type.list` | read | — | `R-LIST`+`R-COUNT` | — |
| 71 | `meeting.eb.type.create.prepare` | read-before-write | `type_name` | `W-PREP` | 记 `continuation` |
| 72 | `meeting.eb.type.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list；清理用 `.delete.*` |
| 73 | `meeting.eb.type.delete.prepare` | read-before-write | `id` | `W-PREP` | — |
| 74 | `meeting.eb.type.delete.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list 不含（**只删自建类型**） |
| 75 | `meeting.eb.topicType.list` | read | — | `R-LIST`+`R-COUNT` | — |
| 76 | `meeting.eb.topicType.detail` | read | `id` | `R-DETAIL` | — |
| 77 | `meeting.eb.topicType.update.prepare` | read-before-write | `id` | `W-PREP`；**先读原值**（部分字段 detail 不回值，需从 list 取） | 记 `continuation` |
| 78 | `meeting.eb.topicType.update.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读被改字段 |
| 79 | `meeting.eb.topicType.delete.prepare` | read-before-write | `id` | `W-PREP` | — |
| 80 | `meeting.eb.topicType.delete.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list 不含 |
| 81 | `meeting.eb.topic.list` | read | — | `R-LIST`+`R-COUNT`（议题为 EB 独有） | — |
| 82 | `meeting.eb.topic.detail` | read | `id` | `R-DETAIL` | — |
| 83 | `meeting.eb.topic.update.prepare` | read-before-write | `id` | `W-PREP` | 记 `continuation` |
| 84 | `meeting.eb.topic.update.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读被改字段 |
| 85 | `meeting.eb.topic.delete.prepare` | read-before-write | `id` | `W-PREP` | — |
| 86 | `meeting.eb.topic.delete.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list 不含（**只删自建议题**） |

### 4.6 EB 版 · 应用设置 / 决议 / 决议任务

| # | operation | 风险 | 必填入参 | 判据 | 回读 / 清理 |
|---|---|---|---|---|---|
| 87 | `meeting.eb.baseSet.get` | read | — | 返回 `only_flow_create` / `open_mt_approve` / 冲突策略 | 建会前必读 |
| 88 | `meeting.eb.decision.list` | read | — | `R-LIST`+`R-COUNT` | — |
| 89 | `meeting.eb.decision.detail` | read | `id` | `R-DETAIL`（带 `detail1` 明细） | — |
| 90 | `meeting.eb.decision.create.prepare` | read-before-write | `mt_id`,`mt_content`,`detail1` | `W-PREP` | 记 `continuation` |
| 91 | `meeting.eb.decision.create.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 `decision.list`（**写失败也可能已落库，先回查**） |
| 92 | `meeting.eb.decision.delete.prepare` | read-before-write | `id` | `W-PREP` | — |
| 93 | `meeting.eb.decision.delete.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 list 不含（**只删自建决议**） |
| 94 | `meeting.eb.decision.publish.prepare` | read-before-write | `mt_id`,`mt_content`,`detail1` | `W-PREP`；发布 = 写决议 **+ 自动把会议标为已决议** | 记 `continuation` |
| 95 | `meeting.eb.decision.publish.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 `decision.list` + 会议 `is_decision=1` |
| 96 | `meeting.eb.decisionTask.list` | read | — | `R-LIST`+`R-COUNT`；`data.progress.summary={total,done,overdue,inProgress,pending}`、`items[].progress.members[]` | 人员基准取主表 `executors`，**未跟进的执行人也计入 total 且算 pending** |
| 97 | `meeting.eb.decisionTask.update.prepare` | read-before-write | `id`,`detail1` | `W-PREP`；`finish_status` 非法枚举需报 `invalid_enum` | 记 `continuation` |
| 98 | `meeting.eb.decisionTask.update.apply` | high-risk-write | `confirm`,`continuation` | `W-APPLY` | 回读 `decisionTask.list` 的 `detail1.finish_status`（改回未完成需传空格清空 `finish_date`） |

> **计数**：标准版 28（#1–#28）+ EB 版 70（#29–#98）+ 跨模式 1（#99）= **99**，与 `weaver-work-cli meeting schema` 的 operation 数一致。

### 4.7 跨模式（EB / 标准版都可用）

| # | operation | 风险 | 必填入参 | 判据 | 回读 / 清理 |
|---|---|---|---|---|---|
| 99 | `meeting.link` | read | `dataId`（或 `dataIds`） | EB 模式：`source=dynamic`（首次）/`cache`（二次），`url` = `{baseUrl}/sp/ebdfpage/card/0/{objid}/{dataid}`，长 id 不得被舍入；标准版：`url` = `{baseUrl}/sp/meeting/meetingSingle?meetingId=`，且**不发任何请求**；会议室/会议类型在标准版下 `url=null` 且有 warning | 解析失败只降级为 `url=null` + `warnings`，不抛错 |

## 5. 最少可跑示例（两平台各一份）

Windows PowerShell：

```powershell
weaver-work-cli --json meeting run meeting.env.detect --input-json '{"refresh":true}'
weaver-work-cli --json meeting run meeting.eb.meeting.list --input-json '{"pageNo":1,"pageSize":20,"withCount":true}'
weaver-work-cli --json meeting run meeting.eb.decisionTask.list --input-json '{"pageNo":1,"pageSize":20,"withCount":true}'
weaver-work-cli --json meeting run meeting.eb.meeting.create.prepare --input-json '{"mt_creator":"<userId>","mt_name":"CLI-VERIFY-001","begin_datetime":"2026-09-24 09:00","end_datetime":"2026-09-24 10:00","mt_status":"2","operate_type":"ADD"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json meeting run meeting.env.detect --input-json '{"refresh":true}'
weaver-work-cli --json meeting run meeting.eb.meeting.list --input-json '{"pageNo":1,"pageSize":20,"withCount":true}'
weaver-work-cli --json meeting run meeting.eb.decisionTask.list --input-json '{"pageNo":1,"pageSize":20,"withCount":true}'
weaver-work-cli --json meeting run meeting.eb.meeting.create.prepare --input-json '{"mt_creator":"<userId>","mt_name":"CLI-VERIFY-001","begin_datetime":"2026-09-24 09:00","end_datetime":"2026-09-24 10:00","mt_status":"2","operate_type":"ADD"}'
```

### 5.1 EB 写链路验证模板（六步，可照抄）

1. `meeting.eb.meeting.create.prepare`（`mt_name` 用 `CLI-VERIFY-<时间戳>`）→ 记 `continuation`、检查 `preview.body`。
2. `meeting.eb.meeting.create.apply`（`confirm:true` + `continuation`）→ 看 `data.association`（占用/回执/签到补建结果与 warnings）。
3. `meeting.eb.meeting.list` 回读 → 拿到自建会议 id 与状态。
4. 业务子链路：占用（`roomUsage.list?mt_id=`）/签到（`sign.list?mt_id=`）/回执（`receipt.list?mt_id=`）/决议（`decision.create|publish`）/决议任务（`decisionTask.list?mt_id=`）。
5. 冲突复验：用同一 `address` + 同一时间段再跑 `meeting.eb.conflict.room` → 应识别冲突（`conflict_rejected` 或非空 warnings）。
6. 清理：`meeting.eb.meeting.delete.prepare` → `apply`（级联回收占用/回执/签到；决议任务按设计保留）。

### 5.2 标准版写链路验证模板

1. `meeting.create.prepare`（名称 `CLI-VERIFY-<时间戳>`，`yyyy-MM-dd HH:mm`）→ 记 `continuation`。
2. `meeting.create.apply` → `meeting.list` 回读拿 id。
3. `meeting.change.*`（改名称）→ 回读确认字段已变。
4. `meeting.cancel.*` → 回读状态；再 `meeting.delete.*` → 回读列表已移除。

## 6. 不在范围（8 项，**不可验证**，需如实答复，禁止伪造）

| 功能 | 事实与证据 | 正确答复 |
|---|---|---|
| EB 会议纪要**创建 / 更新 / 删除** | 无自定义 interfacePk（只有 `query_meeting_minute_list/_count`）；EB 侧纪要表 tag=`uf_mt_minutes`，只能走 OpenAPI `dataset/v2/saveFormData` | 说明只能在系统页面创建，或按 OpenAPI 通用能力人工处理 |
| `meeting.eb.roomUsage.delete.apply` | 真机实测：URL 带 `?id=` 仍报「主键传入不能为空」（eBuilder 侧配置问题，已穷尽） | 释放占用改走 `meeting.eb.meeting.delete`（**级联回收**） |
| 标准版会议室管理（增/改/删/锁定） | 服务端接口未实现 | EB 环境用 `meeting.eb.room.*`；标准版引导页面操作 |
| 标准版会议类型管理 | 服务端接口未实现 | EB 环境用 `meeting.eb.type.*` |
| 提前结束会议 `meeting.over` | 服务端为空实现（假成功），CLI 不提供 | 引导用户在系统页面结束 |
| 本人扫码签到（`signMeeting`）、签到二维码、大屏签到 | 依赖现场二维码票据 + 设备 IP，AI 代签破坏签到真实性 | 引导用户现场扫码/H5 签到 |
| 回收站（列表 / 还原 / 强制还原） | 本阶段未实现（`delete` 为软删，数据可还原但 CLI 无入口） | 引导用户到会议回收站页面操作 |
| 决议任务删除 | 任务由 ESB 自动生成，**不提供删除**；进度用 `decisionTask.update` 维护 | 说明按设计不支持删除，改为更新完成状态 |

> 附加归属事实（避免误报）：**排座在 EB 版没有该功能**；**标准版会议本身没有议题/纪要**（EB 独有）；两套数据互不相通。

## 7. 负向与边界用例（14 项，验证"完整"的关键）

| # | 场景 | 构造 | 期望 |
|---|---|---|---|
| 1 | 必填缺失 | EB `meeting.create.prepare` 不传 `mt_name` | `missing_required_field`（不得静默通过） |
| 2 | 未确认 | 直接调 `*.apply` 不传 `confirm` | `confirmation.required` |
| 3 | 无效 continuation | `apply` 传过期/伪造 token | `continuation_expired` |
| 4 | id 不存在 | `meeting.eb.meeting.detail` 传不存在 id | `not_found` |
| 5 | 日期格式（不带秒） | EB 会议 `begin_datetime` 传 `2026-09-24 09:00:00` | 报「不满足传入格式」 |
| 6 | 日期格式（必须带秒） | 决议任务 `finish_date` 传 `2026-09-24 09:00` | 报格式错误/必填错误 |
| 7 | 非法枚举 | `decisionTask.update` 传 `finish_status=9` | `invalid_enum` |
| 8 | 分页 | `pageNo=2` 与第 1 页不重复；`total>pageSize` 时 `count=pageSize` | `pageInfo` 必须进 body，否则恒回 10 条 |
| 9 | 多值筛选 | `mt_id=A,B`（逗号） | 结果 = A + B 之和（实测纪要 27+23=50） |
| 10 | 空格清空 | `decisionTask.update` 传 `finish_date=" "` | 落库为空串（服务端 trim），状态回到"未完成" |
| 11 | 主键走 URL | 看 EB update/delete 的 `preview.path` | 必须带 `?id=<主键>`；只放 body 会报「主键传入不能为空」 |
| 12 | 冲突拦截 | 同房间同时间段重复建会 | `conflict_rejected`（应用设置=禁止）或非空 `warnings`（=仅提醒） |
| 13 | 越权 | 用他人不可见会议 id 执行 `change.prepare` | 服务端权限文案**原文转达**（如"您没有变更权限！"） |
| 14 | 汇总口径 | `decisionTask.list` / `sign.list` / `receipt.list` | `progress.page` 明确给出「当页条数 vs 总数」；未跟进执行人计入 total；`is_sign="0"`（缺席）与空（未签到）**分开统计** |

## 8. 回执报告模板（执行方产出）

| # | operation | 结果(PASS/FAIL/跳过) | 关键证据 | 备注 |
|---|---|---|---|---|
| 1 | `meeting.env.detect` | PASS | `mode=eb, baseUrl=…` | — |
| … | … | … | … | … |

必须附：环境（`baseUrl`/`userId`/`mode`）、时间戳、**失败项的原始 `error.type/subtype` 与报错文案**、
自建数据清单（id + 名称）与清理结果（是否已删、残留说明）。

## 9. 可直接粘贴给其他智能体的提示词

```text
你是会议模块的验证执行方。请读取本 skill 的 references/meeting-verification.md，按其中的顺序与判据，
对当前环境的会议功能做一次**全量验证**（标准版 28 + EB 版 70，共 98 个 operation）：

1. 先做先决条件 4 步（CLI 版本、共享规则、登录态、meeting.env.detect 判定 mode），并把结果报给我。
2. 按 mode 选择对应的一套 operation，逐条执行第 4 节表格中的判据；只读直接跑，
   写入按「prepare → 我给确认 → apply → 回读 → 清理」四步走，**只用自建数据**（名称带 CLI-VERIFY- 前缀）。
3. 第 6 节的 8 项不在范围，**不要尝试**，如实说明即可；第 7 节的 14 个负向用例必须逐个跑。
4. 任何失败都要给出原始 error.type/subtype 与报错文案，禁止把失败写成"没有数据"。
5. 最后按第 8 节模板给我一份完整回执，并列出未清理干净的数据 id。
```
