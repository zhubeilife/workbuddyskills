# 回执与签到

## 何时使用

查会议回执情况、给某人回执（参加/不参加/请假）、查签到记录与统计，以及**补签 / 补签退 / 清除签到记录**。

## 输入要点

### 回执

- 回执更新**必须传回执记录主键 `id`**（不是 `memberId`）；`prepare` 会自动按 `memberId` 回查定位。
- ⚠️ **`memberId` 字段语义（2026-10-08 真机实测，两个环境一致）**：`meeting.receipt.list` 返回的一条回执里，
  **`memberId` 是「姓名」、`memberIdId` 才是「人员 id」**。因此 `receipt.update.prepare` 的 `memberId`
  **两种写法都接受**（人员 id 或姓名）；CLI 会按 `memberIdId` / `memberId` 依次匹配，并在写请求 body 里统一带上**解析后的人员 id**。
  列表输出的原始字段保持原样（`memberId`=姓名、`memberIdId`=人员 id），**不要**把 `memberId` 当成 id 使用。
- `attendStatus` 枚举：`0`=未填写、`1`=参加、`2`=不参加（回执"否/请假"传 2）。
- 回执列表接口必须带 `isMobile`（CLI 缺省 `false`）**与 `memberType`（CLI 缺省 `1`）**：2026-10-08 真机实测
  **不传 `memberType` 必报 500「系统内部错误」**（此前只挡住了 `isMobile`），两者均已由 CLI 托管，调用方无需显式传。

### 签到

- **`meeting.sign.list` 返回的 `signs[].id` 是「签到记录 id」**——补签/补签退/清除签到用的就是它，**不是会议 id、也不是人员 id**；`mtId`（会议 id）可省略，CLI 会按记录回查，若显式传入则必须与记录一致（不一致报 `sign_record_mismatch`）。
- 三个写动作与源码接口一一对应（`MeetingSignController`）：
  - 补签 `meeting.sign.mark.*` → `signMeetingByHandOne`（写 `signtime`，**已有签到时间会被覆盖**）
  - 补签退 `meeting.sign.back.*` → `signBackMeetingByHandOne`（写 `signbackTime`）
  - 清除签到 `meeting.sign.clear.*` → `delSign`（清空签到/签退时间与地点，复位为未签到）
- `ip` 与 `tenantKey` 由服务端从请求注入，CLI 不传。
- **本人扫码签到（`signMeeting`）不提供**：依赖现场二维码票据（qrticket）与设备 IP，代签会破坏签到真实性；请引导用户现场扫码或走 H5 签到。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json meeting run meeting.receipt.list --input-json '{"mtId":"1305624900858404950"}'
weaver-work-cli --json meeting run meeting.receipt.update.prepare --input-json '{"mtId":"1305624900858404950","memberId":"101","attendStatus":2,"remark":"请假"}'
# 用户确认后：
weaver-work-cli --json meeting run meeting.receipt.update.apply --input-json '{"confirm":true,"continuation":"<prepare返回的continuation>"}'
weaver-work-cli --json meeting run meeting.sign.list --input-json '{"mtId":"1305624900858404950"}'
# 补签（id 取 sign.list 里的 signs[].id）：
weaver-work-cli --json meeting run meeting.sign.mark.prepare --input-json '{"id":"1305624900858404951"}'
weaver-work-cli --json meeting run meeting.sign.mark.apply --input-json '{"confirm":true,"continuation":"<prepare返回的continuation>","id":"1305624900858404951"}'
# 补签退 / 清除签到（同构，换 operation）：
weaver-work-cli --json meeting run meeting.sign.back.prepare --input-json '{"id":"1305624900858404951"}'
weaver-work-cli --json meeting run meeting.sign.clear.prepare --input-json '{"id":"1305624900858404951"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json meeting run meeting.receipt.list --input-json '{"mtId":"1305624900858404950"}'
weaver-work-cli --json meeting run meeting.sign.list --input-json '{"mtId":"1305624900858404950"}'
weaver-work-cli --json meeting run meeting.sign.mark.prepare --input-json '{"id":"1305624900858404951"}'
weaver-work-cli --json meeting run meeting.sign.mark.apply --input-json '{"confirm":true,"continuation":"<prepare返回的continuation>","id":"1305624900858404951"}'
weaver-work-cli --json meeting run meeting.sign.back.prepare --input-json '{"id":"1305624900858404951"}'
weaver-work-cli --json meeting run meeting.sign.clear.prepare --input-json '{"id":"1305624900858404951"}'
```

## 输出处理

- `receipt.list` 返回 `receipts[]`（含 `id`/`memberId`/`attendStatus`/`remark`）；`receipt.update.prepare` 返回 `preview`（含定位到的回执记录 `id`）。
- `sign.list` 返回 `signs[]` 与 `summary`（`total`/`signed`/`unsigned`），输出 Markdown 表格。
- 签到写操作的 `prepare` 返回 `preview`：`signRecordId` / `meetingId` / `userid`（记录里的即 sign 所属人员 id）/ `current`（现有签到与签退时间）/ `effect` / `warnings` / `note`。
- **确认前必须把 `preview` 转述给用户**：给谁（`userid`）、哪场会（`meetingId`）、当前状态、这次会改什么（`effect`），以及 `warnings`（如"已有签到时间会被覆盖""该人员尚未签到，先补签退可能不符合业务预期""没有签到记录，清除不会改变数据"）。
- `apply` 成功返回 `COMPLETE` + `action` + `signRecordId` + `meetingId`；随后用 `meeting.sign.list` 回查。

## 注意

- 回执与签到写操作都属于**改写事实**：apply 前必须取得用户对"目标对象 + 动作"的明确确认。
- 确认对象不要只念 id：签到场景先 `meeting.sign.list` 找到对应人员那行，把**人员姓名/账号 + 会议**说清楚再确认。
- 签到写操作接口返回 `WeaResult.success(false)` 表示未生效，CLI 会报 `sign_not_applied`（**不报成功**）；此时先用 `meeting.sign.list` 复查记录是否还存在。
- 清除签到**无法通过 CLI 恢复**（服务端无恢复接口），必须提醒用户。

## 失败处理

- `receipt_not_found`：先用 `meeting.receipt.list` 核对 `memberId`。
- `sign_record_not_found`：id 不是签到记录 id（常见误传会议 id / 人员 id），先用 `meeting.sign.list` 取 `signs[].id`。
- `sign_record_mismatch`：传入的 `mtId` 与记录所属会议不一致，核对后重试。
- `sign_not_applied`：服务端未生效（记录可能已被删除），复查后重试。
- `target_changed` / `continuation_expired`：重新 prepare 再确认。
- 写请求发出后网络中断 → `partial/write_uncertain`：禁止自动重试，先 `meeting.receipt.list` / `meeting.sign.list` 回查是否已生效。
