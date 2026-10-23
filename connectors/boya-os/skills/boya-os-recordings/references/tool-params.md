# Boya OS MCP 工具参数速查

> 9 个工具全部**只读**。`R` = 必填，`O` = 可选。

## 1. list_recordings — 录音列表

按录制时间倒序，新在前。不传筛选即返回最新一页。

| 参数 | 必填 | 说明 |
|---|---|---|
| `date_from` | O | 起始日期 `yyyy-MM-dd`（含当天 00:00:00），按**录制时间**过滤。只查单日时与 `date_to` 相同。与 `period` 二选一 |
| `date_to` | O | 结束日期 `yyyy-MM-dd`（含当天 23:59:59）。与 `period` 二选一 |
| `period` | O | 相对时间段：`today` 今天 / `yesterday` 昨天 / `this_week` 本周一至今 / `last_week` 上周一至周日 / `this_month` 本月 1 日至今 / `last_month` 上整月。与 `date_from`/`date_to` 二选一 |
| `min_duration` | O | 最短时长（秒）下限，只保留能识别出时长的录音 |
| `max_duration` | O | 最长时长（秒）上限（需 ≥ `min_duration`） |
| `folder_id` | O | 文件夹 ID（`parent_id`），只返回该文件夹下的录音 |
| `page` | O | 页码，从 1 开始，默认 1 |
| `page_size` | O | 每页条数 1–100，默认 20 |

**返回**：`total`（匹配总数）、`items[]`，每项含 `recordingId`、`title`、`folderName`（根目录为 null）、`deviceName`（未绑定为 null）、`durationSec`、`language`、`status`（`pending`/`processing`/`success`/`failed`）、`hasTranscript`/`hasSummary`/`hasMindmap`/`hasActionItems`、时间字段。

---

## 2. search_recordings — 搜索录音

**字面包含匹配**（非语义/模糊），匹配标题与文件名、转写正文、AI 纪要。

| 参数 | 必填 | 说明 |
|---|---|---|
| `query` | **R** | 检索关键词。用**可能原样出现**在标题/正文里的词或短语；中文不要口语化改写 |
| `scope` | O | `all` 全部（默认）/ `title` 标题与文件名 / `transcript` 转写正文 / `summary` 纪要 |
| `page` | O | 页码，从 1 开始，默认 1 |
| `page_size` | O | 每页条数 1–100，默认 20 |

**返回**：`total`、`items[]`，每项含 `recordingId` 与 `matchType`（`title` > `transcript` > `summary`，一条录音只保留最高优先级命中）及命中片段 `snippet`。

---

## 3. get_recording — 录音详情

| 参数 | 必填 | 说明 |
|---|---|---|
| `recording_id` | **R** | 录音 ID（即转写 ID / `upload_id`），取列表返回的 `recordingId` |
| `include_audio_url` | O | 是否额外返回 `audioUrl`（10 分钟有效的预签名播放直链），默认 `false` |

**返回**：`title`、文件名、文件类型/扩展名、文件夹、`deviceSn` 与 `deviceName`、`durationSec`、`language`、`status`、四个 `has*` 标记、`recordedAt`、`createdAt`（+ `audioUrl`）。

**异常**：录音不存在或无权限时按 `RESOURCE_NOT_FOUND` 返回（防探测，不做区分）。

---

## 4. get_transcript — 转写正文

| 参数 | 必填 | 说明 |
|---|---|---|
| `recording_id` | **R** | 同上 |
| `format` | O | `text` 纯文本（默认）/ `markdown` 结构化 / `json` 原始逐句（含说话人、起止时间、文本；**最完整且不截断**，忽略截断参数） |
| `include_speakers` | O | `text`/`markdown` 是否带说话人标签，默认 `false` |
| `include_timestamps` | O | `text`/`markdown` 是否带 `[mm:ss]` 时间戳，默认 `false` |
| `start_ms` | O | 时间窗起点（毫秒，含）。只返回与 `[start_ms,end_ms]` 有重叠的句子。如 10:00 → `600000` |
| `end_ms` | O | 时间窗终点（毫秒，含）。与 `start_ms` 同时传时需 ≥ `start_ms` |
| `max_chars` | O | `text`/`markdown` 内容最大字符数，超出截断并置 `truncated=true`；不传=不截断；`json` 忽略 |
| `offset` | O | 按句分页起点（从 0），默认 0 |
| `limit` | O | 本页句子数 1–50，默认 50。**超长转写请递增 `offset` 续取** |

**返回**：`sentenceCount`（本页句数）、`total`（窗口内总句数）、`offset`、`limit`、`hasMore`、`language`、`durationSec`。

**未转写/转写失败**：`status` 非 `success` 且 `content` 为空——**正常返回，不是错误**。

---

## 5. get_summary — 会议纪要

| 参数 | 必填 | 说明 |
|---|---|---|
| `recording_id` | **R** | 同上 |

**返回**：`title`、`summaryText`（纪要正文）、`mainText`（要点）、`keywords`、`mindmap`（思维导图原文）、`version`、`updatedAt`。

一次调用即拿到**纪要 + 导图**；只想要导图原文才用 `get_map`。**只返回已有最新纪要，不会触发生成或重新生成**——需要生成请到 Boya OS App 端操作。

**无纪要/纪要失败**：`hasSummary=false` 且各内容字段为 null——**正常返回，不是错误**。

**批量场景**：先用 `list_recordings` 的 `hasSummary` 挑出有纪要的录音再逐个调用，避免无效调用。

---

## 6. get_map — 思维导图

| 参数 | 必填 | 说明 |
|---|---|---|
| `recording_id` | **R** | 同上 |

**返回**：`mindmap`（markmap 兼容的 Markdown，可直接渲染）、`updatedAt`。

**只返回已有导图，绝不触发生成**。无导图（纪要未生成或无导图内容）时 `hasMap=false`、`mindmap` 为空串——**正常返回，不是错误**。

需要整份纪要（正文/要点/导图）时优先用 `get_summary`。

---

## 7. get_action_items — 待办事项

`items` 是**两类来源的合集**：① 已生成的结构化待办（`source=memo`）；② 从录音纪要中按规则抽取的行动项（`source=main_text`/`mindmap`）。

| 参数 | 必填 | 说明 |
|---|---|---|
| `recording_id` | O | 只看该录音派生/关联的待办，及其纪要中抽取的行动项。**用户问"我的待办"时不要传**（不传=查全部） |
| `include_completed` | O | 是否含已完成项，默认 `false`。纪要抽取项恒为未完成，两种情况下都会返回 |
| `due_from` | O | 起始到期日 `yyyy-MM-dd`（含当天 00:00:00，按 `remind_time` 过滤）。只查单日时与 `due_to` 相同。**仅作用于结构化待办** |
| `due_to` | O | 结束到期日 `yyyy-MM-dd`（含当天 23:59:59，按 `remind_time` 过滤）。**仅作用于结构化待办** |
| `created_from` | O | 起始创建日 `yyyy-MM-dd`（含当天 00:00:00，按 `create_time` 过滤）。**仅作用于结构化待办** |
| `created_to` | O | 结束创建日 `yyyy-MM-dd`（含当天 23:59:59，按 `create_time` 过滤）。**仅作用于结构化待办** |

**返回**：`total`、`items[]`，每条含 `source`、`completable`（`true`=真实待办、有 `itemId`，可在 App 完成或设提醒；`false`=纪要里的行动项，**尚未生成待办，无法完成或提醒**）、`itemId`、内容与日期字段。

**日期参数行为**：带任一日期参数时**只返回结构化待办**，纪要抽取项（无日期）不会出现。

**无待办**：`items: []`、`total: 0`——**正常返回，不是错误**。

**注意**：列表/详情里的 `hasActionItems` 只是"是否有待办"的开关，要看明细必须调用本工具。

---

## 8. list_devices — 设备列表

无入参。

**返回**：每台设备的 `deviceId`（即设备 SN）、`deviceName`、`sn`、`firmwareVersion`、`boundAt`。

- 不返回录音数量，**也不支持按设备筛选录音**（设备归属列并非在所有上传路径都写入）。
- 只返回状态为**已绑定**的设备；已解绑设备不在列表中。
- 单条录音上的 `deviceSn`/`deviceName` 仅作展示。

---

## 9. list_folders — 文件夹列表

无入参。

**返回**：每个文件夹的 `folderId`（可直接用作 `list_recordings` 的 `folder_id`）、`name`、`parentId`、`createdAt`、`recordingCount`（该文件夹下**本账号未删除/未回收**的录音条数）。

- 未分类（根目录）的录音不属于任何文件夹，不在列表中。
- 想看某文件夹下的具体录音，把 `folderId` 传给 `list_recordings`。

---

## 通用约定

- **鉴权**：由 WorkBuddy 的 OAuth 统一管理，调用方无需传 token；令牌过期会自动刷新。
- **分页**：返回条数 < `total` 时需继续翻页取完。
- **空态**：`hasSummary`/`hasMap` 为 false、`items` 为空数组均属正常响应，按"尚未生成/暂无内容"回复用户。
- **ID 传递**：`recordingId` 只能来自 `list_recordings` / `search_recordings` 的返回，禁止编造。
