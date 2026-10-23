# EB 版（eBuilder 会议应用）operations

## 何时使用

`meeting.env.detect` 判定 **`mode=eb`** 时，全部意图改用 `meeting.eb.*`。

> 标准版与 EB 版是**两套独立接口与数据**：标准版是 Java REST（`/api/meeting/**`、表 `mt_detail` 等），
> EB 版是 eBuilder formdata（`/api/ebuilder/form/formdata/v2/**`、表 `uf_*`）。**不可混用、数据互不相通**——
> 在 EB 环境调用标准版接口只会拿到空数据。
> EB 版独有：议题、纪要（标准版会议本身没有这两类数据）。

## 调用约定（实现已内建，了解即可排错）

| 环节 | 约定 |
|---|---|
| 路径 | `/api/ebuilder/form/formdata/v2/{saveFormData｜updateFormData｜deleteFormData｜getFormDataByPk｜getFormDataList｜getFormDataCount}/{interfacePk}` |
| 列表/总数 | 筛选条件走 **URL query**（参数名为 eBuilder 配置的占位符名，如 `hrmmember`、`mt_status`，**不是表 dataKey**）；body 必须带 `datajson`；CLI 先 count 再 list（同条件），`total` 来自 count |
| 详情 | `getFormDataByPk`，body 顶层 `mainTable.id` |
| 写操作 | body 用 **`datas` 数组**包裹 `mainTable`（缺 `datas` 会报"datas节点未找到"），`header.operator` 为当前用户 |
| 日期字段（**两种格式并存，务必看清**） | **① 多数不带秒 `yyyy-MM-dd HH:mm`**：会议 `begin_datetime` / `end_datetime`、决议明细 `begin_datetime` / `end_datetime`；**② 少数必须带秒 `yyyy-MM-dd HH:mm:ss`**：决议任务 `finish_date`、签到 `sign_time` / `signback_time` / `allow_late_time`。传错会报「传入字段:xxx…不满足传入格式」（2026-09-21 真机实测）|
| **写/改操作的主键** | **update 的主键必须走 URL**（形如 `POST /updateFormData/{interfacePk}?id=<主键>`）：只放在 body 的 `datas[].mainTable.id` 会被拒，报「**主键传入不能为空**」（2026-09-21 真机实测 `update_meeting_sign_info`）。CLI 已按接口声明自动携带，body 里同时保留 `id` 以满足文档「id 必填」。|
| 人员 id（**分场景，勿混**） | **决议 / 冲突检测 / 会议人员 → HRM 员工 id**（形如 `1305319992400396336`）：`executors`、`rummager`、`hrm_members`、`signMember` 筛选用；**签到表的 `user_id` → 实测存的是 E10 userId**（形如 `6788539829119521816`），补签匹配按它比对。姓名→员工 id 用 `weaver-e10-hrm`。⚠️ 传错**不报错**，但会静默查不到 / 冲突漏检 |
| 新建/更新 | create 不传 id（系统生成）；update/delete 必传 id |
| **⚠️ 返回结构（必读）** | **人员 / 关联 / 状态 / 选择类字段返回的是「对象数组」，不是字符串**，形如 `[{"name":"崔智友","id":"1305319807700025376"}]` —— 取 id 读 `[0].id`、取显示名读 `[0].name`；**禁止**把整个数组直接当字符串拼接（会显示成 `System.Object[]`，看起来像"字段为空"）。已实测这类字段：`executors` / `rummager` / `mt_id` / `relate_decision` / `decision_status` / `detail1[].executor` / `detail1[].finish_status`；而 `finish_date` / `id` / 日期 / 普通文本字段是字符串 |
| **⚠️ 写操作失败语义（必读）** | **EB 写接口"报错"≠"没有写入"**：实测 `create_mt_decision` 因字段校验失败（传了不被接受的 `data_status`）返回错误，但主表与明细**已经落库**，重试后产生了**重复决议 + 重复任务**。因此：写操作失败后**必须先回查**（`list` / `detail`）再决定重试或删除；CLI 的语义化写操作（`decision.publish` 等）在拿不到明确成功证据时会抛 **`partial`** 而非普通失败，并按此提示调用方 |

## operation 清单

| 模块 | 读 | 写（prepare → apply） | interfacePk |
|---|---|---|---|
| 会议 6.x | `meeting.eb.meeting.list` / `.detail` | `meeting.eb.meeting.create` / `.change` / `.delete` | query_mtDetail_list(+count) / query_mtDetail_info / create_meeting / change_meeting / delete_mtDetail |
| 会议室 2.x | `meeting.eb.room.list` / `.detail` | `meeting.eb.room.create` / `.update` / `.delete` | query_meeting_room_list(+count) / query_room_info / create_room / update_room / delete_room |
| 占用 5.x | `meeting.eb.roomUsage.list` / `.detail` | `meeting.eb.roomUsage.create` / `.delete` | query_roomusage_list(+count) / query_roomusage / create_roomusage / delete_roomusage |
| 签到 1.x | `meeting.eb.sign.list` / `.detail` | `meeting.eb.sign.create` / `.update` | query_meeting_sign_list(+count) / query_meeting_sign_info / create_meeting_sign / update_meeting_sign_info |
| 回执 4.x | `meeting.eb.receipt.list` / `.detail` | `meeting.eb.receipt.create` / `.update` | query_meeting_receipt_list(+count) / query_meeting_receipt / create_meeting_receipt / update_meeting_receipt |
| 纪要 3.x | `meeting.eb.minute.list` | **创建未实现**（走 OpenAPI，无自定义 interfacePk） | query_meeting_minute_list(+count) |
| 会议类型 3.5 | `meeting.eb.type.list` | `meeting.eb.type.create` / `.delete` | query_mt_type_list(+count) / create_mt_type / delete_mt_type |
| 议题类型 8.x | `meeting.eb.topicType.list` / `.detail` | `meeting.eb.topicType.update` / `.delete` | query_mt_topicType_list(+count) / query_mt_topicType_info / update_mt_topicType_info / delete_mt_topicType_info |
| 会议议题 9.x | `meeting.eb.topic.list` / `.detail` | `meeting.eb.topic.update` / `.delete` | query_mt_topic_list(+count) / query_mt_topic_info / update_mt_topic_info / delete_mt_topic_info |
| 应用设置 7.x | `meeting.eb.baseSet.get` | — | query_meeting_baseset |
| 冲突检测 | `meeting.eb.conflict.room` / `.member`（只读） | — | query_roomusage_list / query_mtDetail_list + query_meeting_receipt_list(+count) |
| **决议概述** | `meeting.eb.decision.list` / `.detail` | `meeting.eb.decision.create` / `.delete` / **`.publish`（推荐）** | query_mt_decision_list(+count) / query_mt_decision_info / create_mt_decision / delete_mt_decision / update_mt_isdecision |
| **决议任务** | `meeting.eb.decisionTask.list` | `meeting.eb.decisionTask.update` | query_mt_decision_task_list(+count) / update_mt_decision_task |
| **补签（语义化）** | — | `meeting.eb.sign.mark` | update_meeting_sign_info（自动定位签到记录 id）|

> ⚠️ **补签务必带时间（或让 CLI 补当前时间）**：2026-10-08 真机实测，只传 `mt_id` + `user_id` 时 update 里没有任何
> 时间字段，**服务端照样返回成功、CLI 也报 COMPLETE，但签到记录一点没变**（静默无效）。现 CLI 已兜底：
> 未传 `sign_time` / `signback_time` / `sign_out_status` 时按"补签"语义**自动补当前时间**（带秒）并写入 `warnings`，
> 实际写入值在 `preview.after` 里可见；要指定时间请显式传 `sign_time`（`yyyy-MM-dd HH:mm:ss`，带秒）。

## 常用命令

Windows PowerShell：

```powershell
weaver-work-cli --json meeting run meeting.env.detect --input-json '{"refresh":true}'
weaver-work-cli --json meeting run meeting.eb.baseSet.get --input-json '{}'
weaver-work-cli --json meeting run meeting.eb.meeting.list --input-json '{"hrmmember":"100","mt_status":"2","pageSize":20}'
weaver-work-cli --json meeting run meeting.eb.meeting.detail --input-json '{"id":"1306126102057902085"}'
weaver-work-cli --json meeting run meeting.eb.meeting.create.prepare --input-json '{"mt_creator":"100","mt_name":"周会","begin_datetime":"2026-09-20 09:00","end_datetime":"2026-09-20 10:30","mt_status":"2","operate_type":"ADD"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json meeting run meeting.env.detect --input-json '{"refresh":true}'
weaver-work-cli --json meeting run meeting.eb.baseSet.get --input-json '{}'
weaver-work-cli --json meeting run meeting.eb.meeting.list --input-json '{"hrmmember":"100","mt_status":"2","pageSize":20}'
weaver-work-cli --json meeting run meeting.eb.meeting.detail --input-json '{"id":"1306126102057902085"}'
weaver-work-cli --json meeting run meeting.eb.meeting.create.prepare --input-json '{"mt_creator":"100","mt_name":"周会","begin_datetime":"2026-09-20 09:00","end_datetime":"2026-09-20 10:30","mt_status":"2","operate_type":"ADD"}'
```

## 输出处理

- list：`{ total, pageNo, pageSize, count, rows, filters }`——`total` 来自 count 接口，`rows` 是当前页数据。
- detail / baseSet：`{ id, data }` / `{ data, count }`（baseSet 多条时取第一条）。
- write prepare：`{ status: 'AWAITING_CONFIRMATION', preview: { interfacePk, kind, body, path, notes }, continuation }`——**先向用户摘要 body 内容再确认**。
- write apply：`{ status: 'COMPLETE', interfacePk, dataIds }`；回读用对应 list/detail 核对。

## 会议决议与决议任务（EB 版，2026-09-21 新增）

**用途**：把会议成果（结合会议议题、纪要、用户提供的文档/信息）**汇总成决议**，系统按决议明细**自动生成待办任务**，后续可跟踪完成情况。

### 一句话链路

```
① meeting.eb.decision.publish   ← 推荐入口：写「决议概述 + 明细」，并自动把会议标为已决议
   ├ 内部第 1 步 create_mt_decision   写概述（mt_content）+ 明细（detail1，每条 = 一项待办）
   └ 内部第 2 步 update_mt_isdecision 写回会议：decision_Id + is_decision=2 + mt_status=8
② （用户配置的 ESB 联动）按决议明细生成「决议任务」数据 —— CLI 不参与、不写任务表
③ meeting.eb.decisionTask.list      查任务（按会议 / 执行人 / 状态）
④ meeting.eb.decisionTask.update    按执行人更新任务完成状态
```

### 关键字段口径（务必按此传）

- **`mt_content`**：决议概述文本（一段话），由调用方汇总后传入，CLI 不生成内容。
- **不要传 `data_status`**：`create_mt_decision` **不接受**该字段（真机报 `DataError:dataKey:data_status,该字段不存在`），提交状态由系统自动置 `1`（回查列表 `data_status=1`，ESB 联动照常触发）。
- **`detail1`（决议明细，至少 1 条）**：
  | 字段 | 必填 | 说明 |
  |---|---|---|
  | `decision_title` | ✅ | 决议标题（= 任务标题）|
  | `executors` | ✅ | 执行人，**HRM 员工 id**（多人逗号分隔）|
  | `begin_datetime` / `end_datetime` | ✅ | `yyyy-MM-dd HH:mm` |
  | `decision_status` | ✅ | 0未完成 / 1已完成 / 2已延期（默认 0）|
  | `rummager` | ⭕ | 检查人，**员工 id**（**非必填**）|
  | `related_type` | ⭕ | 0未关联 / 1日程 / 2任务（默认 0）|
  | `sort_number` | ⭕ | 明细序号，省略时按数组顺序自动编号 |
- **`data_status`**：创建时 CLI **固定传 `1`（提交）** —— 传 0（暂存）**不会触发 ESB 联动，决议任务永远不会生成**。
- **会议侧**：`is_decision=2`（决议提交完成）+ `decision_Id=<决议概述 id>` + `mt_status=8`（结束）。**产生决议后会议即视为结束**，这是服务端口径（服务端源码 `decisionStatus==2` 时 `isover=true`）。
- **任务侧**：`mainTable` = 一条任务（含 `decision_title` / `executors` / `decision_status` / `mt_id` / `relate_decision`）；`detail1` = 各执行人的 `finish_status`（0未完成/1已完成/2已延期）+ `finish_date`。

### 返回结构（解析前必读，2026-09-21 真机实测）

`decision.list` / `decisionTask.list` / `decision.detail` 中，**人员、关联、状态类字段返回的是「对象数组」而不是字符串**：

```json
"executors":       [{ "name": "崔智友", "id": "1305319807700025376" }]
"rummager":        [{ "name": "裴永俊", "id": "1305319812204708008" }]
"mt_id":           [{ "name": "你好中国", "id": "1316455906280819022" }]
"relate_decision": [{ "name": "会议决议概述表-…", "id": "1316456666740138910" }]
"decision_status": [{ "name": "未完成", "id": "0" }]
```

⇒ 取 id 读 `[0].id`、取显示名读 `[0].name`；**不要**把整个数组直接当字符串拼进回复（会显示成 `System.Object[]`）。
`detail1[]` 里 **`executor` 是对象数组**，而 **`finish_status` 是字符串**（形如 `"未完成"` / `"已完成"`），`finish_date` / `id` 也是字符串。
⚠️ **`decisionTask.list` 的 `detail1` 并非每行都返回**（真机实测：同一批任务里只有部分行带 `detail1`）—— 需要逐个执行人的完成状态时，不要假设每条都有 `detail1`；主表 `decision_status` 与 `detail1[].finish_status` 是两套状态（**主表归检查人维护，CLI 只更新 `detail1`**）。

**筛选参数（已真机验证生效）**：
- `decision.list` / `decisionTask.list`：`mt_id` = **会议 id**（不是决议 id、不是任务 id）。用无关会议 id 查询返回 0 条、用真实会议 id 返回正确条数 ⇒ 参数确实生效。
- `decisionTask.list` 另支持 `relate_decision`（决议概述 id）、`executors`（员工 id）、`decision_status`。
- 实测样例：「你好中国」（`mt_id=1316455906280819022`）→ 决议 1 条 + 决议任务 2 条（「解决方案」「研究方案」，执行人崔智友、检查人裴永俊）；**证明 ESB 联动确实按决议明细生成了任务**。

### 必须遵守的行为

1. **优先用 `meeting.eb.decision.publish`**，不要手写"create 完再 markDecided"两步 —— 漏第二步会造成「决议建了、会议却还显示未决议」的半成品状态。
2. **一次会议只有一个决议概述**：重复 publish 前先 `decision.list`（按 `mt_id`）确认是否已有。
3. **明细至少 1 条**：没有明细等于没有任务，CLI 直接拒绝（`missing_required_field`）。
4. **`publish` 是写操作**：必须先 `prepare` 给用户看预览（概述 + 明细逐条），用户确认后才 `apply`。
5. **部分失败必须如实转达**：
   - 决议已建但**写回会议失败** → 抛 `partial`，消息含 `decision_Id` —— **不要重复创建决议**，可稍后用 `meeting.eb.meeting.markDecided` 补标记（正文里说明了这点）。
   - 决议可能已写入但**没返回 `dataIds`** → 抛 `partial`，提示先用 `decision.list(mt_id)` 回查，**同样不要重复创建**。
6. **任务与进度的读法（真机实测口径）**：
   - **一条决议明细 = 一个任务**；明细里写多个执行人 ⇒ 该任务**多人共同跟进**（实测：1 明细 + 2 执行人 → 只生成 1 个任务）。
   - ⚠️ **2026-10-08 复测出现「1 明细 + 1 执行人 → 生成 2 条任务」**：任务条数由**用户配置的 ESB 联动**决定，
     可能随模板/配置变化，**不要用「明细条数 = 任务数」推算**，一律以 `decisionTask.list` 的实际返回为准。
   - **更新**用 `meeting.eb.decisionTask.update`：按 `executor` 写 `detail1`（`finish_status` 未完成/已完成/已延期 + `finish_date` **带秒**）。
   - ⚠️ **`markDecided` 的必填组合（2026-10-08 实测）**：`is_decision=2`（决议提交完成）时**必须同时传 `decision_Id` 与 `mt_status`**，
     否则 `prepare` 能通过、`apply` 被服务端拒绝：原文 `DataError:存为未填写的必填字段: decision_Id,mt_status ,请确认`。
     正确样例：`{"id":"<会议id>","decision_Id":"<决议概述id>","is_decision":"2","mt_status":"8"}`（回读会议：`mt_status=结束`）。
     **`finish_date` 是服务端必填**；把任务改回「未完成」时传一个**空格**即可显式清空。
     **同一执行人重复更新 = 覆盖该人记录，不同执行人 = 追加**（实测两人跟进后 detail1 保留两条，互不覆盖）。
   - ★ **读进度直接用 `decisionTask.list` 返回的 `data.progress`**（不必自己解析 detail1）：
     `progress.summary` = 整页汇总（`total` / `done` / `overdue` / `inProgress` / `pending`）；
     `progress.items[].progress` = 逐任务 `{ total, done, overdue, pending, status, members[] }`，
     其中 `status ∈ done 全员完成 | overdue 有人延期 | inProgress 部分完成 | pending 尚未开始`，
     `members[]` 给出每人 `executorId` / `executorName` / `status` / `finishDate`。
     ⚠️ 统计以 `executors` 为人员基准：**未跟进的执行人也会计入 `total` 并算作 `pending`**（不会漏人）。
   - 原始信息仍可从 `rows[].detail1`（每人 `finish_status` / `finish_date` / `executor`）读取；`rows` **原样返回、未被改写**。
     ⚠️ **`mainTable.decision_status` 不可作为进度依据**：实测**始终为「未完成」**，既不随 detail1 变化，也无法经 `update_mt_decision_task` 写入（该接口只映射 detail1）。
   - 查询：`meeting.eb.decisionTask.list`（按 `mt_id` 查某会议全部任务 / 按 `executors` 传员工 id 查某人的任务 / 分页 `pageNo`+`pageSize`）。
7. **`executors` / `rummager` / `user_id` 一律传 HRM 员工 id**（不是 E10 userId）—— 传错不报错但会静默失效。

## 冲突检测（EB 版，强制）

> 2026-09-20 补齐：此前 EB 版建会**没有任何冲突校验** —— 重复占用同一间会议室、参会人在同一时段撞会都不会被拦住。

- **自动强制（建会/变更自带）**：`meeting.eb.meeting.create.prepare` 与 `meeting.eb.meeting.change.prepare` 在生成确认预览**之前**自动执行会议室与参会人冲突检测（传了 `address` / `hrm_members` 才会真的发起查询）。命中时按应用设置处置：
  - `room_conflict=1` / `member_conflict=1`（禁止提交）→ 抛 `conflict_rejected`：**直接停止，不询问、不新建**；
  - `room_conflict=0` / `member_conflict=0`（仅提醒）→ 写入 `warnings`：**如实告知冲突 + 建议换时间/换地点 + 决定权交用户**；CLI 与服务端都不阻止提交，但 CLI **不主动建议忽略冲突**，也不提供"忽略 / 强制"类选项；
  - 检测请求本身失败 → 抛 `conflict_check_failed`（fail-closed：宁可拦住，不可漏检）。
- **只查不建**：`meeting.eb.conflict.room` / `meeting.eb.conflict.member`，返回 `verdict`：`ok` 无冲突 / `warn` 仅提醒 / `rejected` 禁止提交 / `skipped` 应用设置已关闭该项检测。
- **口径（与 standalone skill 一致，不可擅改）**：
  - 策略来自 `meeting.eb.baseSet.get` → `room_conflict_chk` / `room_conflict`、`member_conflict_chk` / `member_conflict`（`chk=0` 表示关闭检测，**页面同样不校验**）；
  - 会议室：查占用视图 `query_roomusage_list`（**过滤参数 `address` = 会议室 id**；时间重叠：占用开始 < 我的结束 且 占用结束 > 我的开始；占用视图只对有效状态生成，无需再过滤状态）。⚠️ 该接口**返回体的 `address` 字段为空**，会议室要读 **`room_id`** —— 别据此误判成"检测失效"；
  - 参会人：**2 次请求方案（无 N+1）** —— `query_mtDetail_list`（时间范围 + `mt_status=1,2,8,9`）取候选会议 → `query_meeting_receipt_list?mt_id=<多值批量>`（分批 + 分页拉全）→ 本地求交集；**禁止**退回「逐场会议查回执」的旧做法；
  - 参会人以**回执表 `member_id`** 为准（会议表 `hrm_members` 是渲染文本，不可靠），且只统计 `member_type=1`（参会人员）；
  - ⚠️ **传参口径（2026-09-20 实测）**：`hrm_members` 必须是 **HRM 员工 id**；传 E10 userId **不报错**，但与回执 `member_id` 比对不上 → **静默漏检**（表现为"无冲突"）。人员 → 员工 id 用 `weaver-e10-hrm`；
  - `org_members`（参会部门）CLI **不展开**成员，因此只有 `hrm_members` 参与人员冲突检测 —— 该情况会以 warning 如实说明，需要覆盖部门成员时请先把部门展开为员工 id。
- **冲突处置的唯一依据就是应用设置**（`room_conflict` / `member_conflict`），CLI 不额外加码、也不引入任何隐藏校验：
  - `1`「禁止提交」→ 怎么都不允许提交，直接拒绝（`conflict_rejected`）；
  - `0`「仅提醒」→ 如实告知冲突并建议换时间/换地点，**是否继续由用户决定**（`prepare` 只给 `warnings`，不阻止 `apply`）；CLI **不主动建议忽略冲突**。

## 建会特别说明（EB 版）

1. 先 `meeting.eb.baseSet.get` 读 `only_flow_create` / `open_mt_approve` / `mt_new_wf`：
   - `only_flow_create=1` 或审批开启 → **会议需经流程创建**，CLI 不直接建会，提示用户走 workflow；
   - 未开启 → 可 `meeting.eb.meeting.create.prepare`。
2. `mt_hours` 由 CLI 按 `begin_datetime`/`end_datetime` **自动计算**（小时，支持小数），无需用户提供。
3. `caller`/`contacter` 未指明时 CLI 默认填当前用户。
4. ⭐ **建会成功后 CLI 会自动补建关联数据**（占用 / 回执 / 签到）—— 自定义接口 `create_meeting` **不会**像页面建会那样生成它们，而这三样是**冲突检测与补签的硬依赖**：
   - **占用** `create_roomusage`：`room_id` = 会议的 `address`、`startdate`/`enddate` 与会议一致（缺它 ⇒ 会议室冲突检测查不到本场会）；
   - **回执** `create_meeting_receipt`：按 `hrm_members` **逐人一条**（`member_type=1`、`member_manager` = `member_id`）（缺它 ⇒ 参会人冲突检测失效）；
   - **签到** `create_meeting_sign`：按 `hrm_members` **逐人一条**（缺它 ⇒ `meeting.eb.sign.mark` 补签无记录可用）。
   - 结果在 `apply` 返回的 **`data.association`**：`{ status: COMPLETE|PARTIAL, mtId, created: { roomUsage, receipt, sign }, warnings }`。
   - **补建失败不中断建会**（主写入已成功）→ 只进 `association.warnings` 并说明后果；**不要因补建失败而重试建会**（会重复建会）。
   - 未传 `address` → 跳过占用；未传 `hrm_members`（如仅用 `org_members` 指定部门，CLI 不展开部门成员）→ 跳过回执与签到，均在 warnings 中说明。
   - 需要"取消会议释放占用"时用 `meeting.eb.meeting.delete`（会级联回收 占用/回执/签到）；`delete_roomusage` 在本环境报「主键传入不能为空」，不可用。

## 出席情况汇总（`data.progress`，2026-09-22）

`meeting.eb.sign.list` 与 `meeting.eb.receipt.list` 的返回也附带 `data.progress`（机制同 `decisionTask.list`：**纯 CLI 侧计算、原始 `rows` 原样返回、不动服务端**）：

- **`progress.page`** = `{ pageNo, pageSize, pageCount, total }`。
  ⚠️ **`summary` 里的计数只覆盖当前页**（`total` 才是全部条数）—— 要全量统计请传足够大的 `pageSize`（上限 200）或逐页累加，别把当页数字当总数。
- **签到** `progress.summary`：`total` / `signed` / `notSigned` / `signedOut` / `attendanceRate` / `byState`（`normal`·`leave`·`late`·`earlyLeave`·`notSignedOut`·`lateAndNotSignedOut`·`lateAndEarlyLeave`·`absent`·`notSigned`·`unknown`）。
  ⚠️ **未签到 = `is_sign` 与 `sign_time` 都为空**；**`is_sign=0` 是「缺席」**（已表态没来）—— 两者语义不同，别混在一起算出席率。
- **回执** `progress.summary`：`total` / `attend` / `decline` / `noReply` / `replyRate` / `attendRate` / `byMemberType`（`attendee`·`customer`·`other`）/ `bookRoom` / `bookTicket`。
  ⚠️ **`attend_status` 为空 = 未回执**（不是"不参加"）；`0` 不参加、`1` 参加。
- 两张表的 `mt_id` 语义不同：**签到表回的是会议名称文本，回执表回的是会议 id** —— 汇总里统一叫 `mtRef`（原样透出）。

## 详情页链接（`meeting.link`，2026-09-23 新增）

链接地址**随模式不同**，且 EB 版必须按表 tag 解析 `objid`（随环境变化、**不等于 formId**），
因此**禁止手工拼 URL** —— 一律用 `meeting.link` 生成（`objid` 按 `baseUrl|tenantKey` 长期缓存）。

| 模式 | 对象 | URL 模板 |
|---|---|---|
| EB 版 | 全部对象 | `{baseUrl}/sp/ebdfpage/card/0/{objid}/{dataid}`（`card` 后的 `0` **恒为 0**） |
| 标准版 | 会议详情 | `{baseUrl}/sp/meeting/meetingSingle?meetingId={meetingid}` |
| 标准版 | 会议室 / 会议类型 | 没有单页 → 只输出数据、不附链接 |

EB 表 tag 映射（`meeting.link` 的 `type` 取值，也可用 `tag` 直接指定表 tag）：

| type | 表 tag | 对象 |
|---|---|---|
| `meeting`（默认） | `uf_mt_detail` | 会议 |
| `room` | `uf_mt_room_base` | 会议室 |
| `roomType` | `uf_mt_room_type` | 会议室类型 |
| `roomUsage` | `uf_mt_room_usage` | 会议室占用 |
| `setting` | `uf_mt_base_set` | 应用设置 |
| `mtType` | `uf_mt_type` | 会议类型 |
| `sign` | `uf_mt_sign` | 签到 |
| `receipt` | `uf_mt_receipt_member` | 回执 |
| `topic` | `uf_mt_topic` | 议题 |
| `minutes` | `uf_mt_minutes` | 纪要 |

Windows PowerShell：

```powershell
weaver-work-cli --json meeting run meeting.link --input-json '{"dataId":"1305624900858404950","type":"meeting","name":"周会"}'
weaver-work-cli --json meeting run meeting.link --input-json '{"dataIds":["1305624900858404950","1305624900858404951"],"name":"周会"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json meeting run meeting.link --input-json '{"dataId":"1305624900858404950","type":"meeting","name":"周会"}'
weaver-work-cli --json meeting run meeting.link --input-json '{"dataIds":["1305624900858404950","1305624900858404951"],"name":"周会"}'
```

**输出与用法**：

- 单条：`data.path` / `data.url` / `data.markdown`（只有传了 `name` 才带 markdown）。
- 批量：`data.items[]`（列表输出时一次生成全部链接，别逐条调用）。
- `data.source`：`dynamic`（本次解析到 objid）/ `cache`（命中缓存）/ `none`（未取到或标准版无单页）。
- **解析失败只降级**：`url=null` + `warnings`，不抛错、不影响主业务结果 —— 如实说明"链接暂不可用"，
  **不要**因此重试，更不要自己拼 URL。
- `mode` 默认 `auto`（复用 `meeting.env.detect` 的模式判定与缓存）；只有明确知道模式时才显式传 `eb` / `standard`。
- **输出格式**：链接必须内联到名称单元格（`[会议名称](url)`），**禁止**单列「详情链接」一行。

## 注意

- **取消会议**用 `meeting.eb.meeting.change.prepare`（`operate_type=CANCEL` 且 `mt_status=4`），没有独立 cancel 接口。
- `mt_status` 枚举：0草稿/1审批中/2未开始/3退回/4取消/5提前结束/6删除/7锁定/8结束/9进行中/10审批中(变更)/11审批中(取消)。
- 议题表 `uf_mt_topic` 在部分租户未注册，`meeting.eb.topic.list` 返回空数组属正常。
- `meeting.eb.sign.list` 展示时避免同时指定含 `sign_flag` 与 `attend_type` 的字段组合（后端可能 500）。
- 写操作一律 prepare → 用户确认 → apply；`apply` 的字段必须与 `prepare` 快照一致（不一致报 `target_changed`）。

## 失败处理

- 业务失败返回原文 message（如 `传入参数datajson为空或解析异常`、`请求参数不能为空`），**原样转达用户**。
- `missing_required_field`：缺少必填字段，按提示补齐。
- `datetime_invalid`：日期需 `yyyy-MM-dd HH:mm`（不带秒）。
- `eb_write_not_applied`：接口返回 `datajson.status=false`，服务端未生效，核对字段与权限。
- `target_changed` / `continuation_expired`：重新 prepare 并再次确认。
- `partial/write_uncertain`：写请求发出后连接中断，**禁止自动重试**，先 list/detail 回查是否已生效。
- `conflict_rejected`：命中冲突且应用设置为**禁止提交** —— 立即停止，建议用户换时间或换地点；若应用设置为**仅提醒**，则只写入 `warnings`（不抛错），**是否继续由用户决定**（CLI 不主动建议忽略冲突）。
- `conflict_check_failed`：冲突检测接口调用失败（fail-closed，直接拒绝建会），核对占用/回执接口权限后重试。
