# 采知连文档：检索、详情与创建/编辑

## 何时使用

- 用户要在采知连（E10 文档中心 / 知识库）里找文档、看文档详情。
- 用户要新建文档：在线 HTML 文档、Markdown 文档、上传 Office 文件建文档、批量上传文件建文档。
- 用户要改文档：改标题/摘要/关键词/失效日期、换作者、保存在线正文、用本地文件替换正文。

## 输入要点

### 检索与详情

| operation | 必填 | 关键可选 |
| --- | --- | --- |
| `caizhilian.document.search` | 无 | `keywords`、`folder_id`、`include_sub_folder`、`creator_user_id`、`create_time`、`page_no`、`page_size`（默认 40） |
| `caizhilian.document.get` | `doc_id` | 无 |
| `caizhilian.user.current` | 无 | 无 |

- `folder_id` 的根节点约定：`100`=系统、`200`=公共、`300`=个人；具体子文件夹 ID 用 `caizhilian.folder.query-by-name` 查。
- `include_sub_folder` 只在传了 `folder_id` 时才写入请求体，不传 `folder_id` 时该字段无效。
- `create_time` 支持枚举 `today` / `yesterday` / `this_week` / `last_week` / `this_month` / `last_month` / `this_year` / `last_year` / `last_7_days` / `last_30_days` / `last_90_days`，也支持 `last_<N>_days` 和显式区间 `YYYY-MM-DD HH:MM~YYYY-MM-DD HH:MM`；无法解析报 `validation/time_range_invalid`。区间按东八区计算。
- `caizhilian.user.current` 返回当前登录人的 `employeeId` / `employeeName`，创建文档缺 `author_id` 时可先取它。

### 创建文档

| operation | 必填 | 说明 |
| --- | --- | --- |
| `caizhilian.document.create-html` | `name`、`folder_id`、`folder_type`、`author_id` | `summary` 传 HTML 正文 |
| `caizhilian.document.create-markdown` | `name`、`folder_id`、`folder_type`、`author_id` | `summary` 传 Markdown 文本，或 `file_path` 指向本地 `.md`/`.markdown`（读到内容后覆盖 `summary`） |
| `caizhilian.document.create-office` | `file_path`、`folder_id`、`folder_type`、`author_id` | 只接受 `.doc/.docx/.xls/.xlsx/.ppt/.pptx`；`name` 缺省取文件名（不含扩展名） |
| `caizhilian.document.create-by-upload` | `file_paths`、`folder_id`、`folder_type` | `author_id` 缺省取当前登录人；`file_paths` 接受字符串或数组，去重保序，最多并发 8 个 |

公共可选字段：`participant_ids`、`abstract_text`、`keywords`、`auto_invalidate_date`（`YYYY-MM-DD`）、`tags`、`virtual_folder_ids`、`doc_category`（`0`=普通，`1`=重要）、`cover_picture_id`（`create-by-upload` 无 `cover_picture_id`）。

- `folder_type` 枚举：`company`=公共、`privy`=个人、`sys`=系统。
- `tags` 元素是对象，形如 `{"id":"1","privacy":false}`；`id` 用 `caizhilian.tag.search` 查。
- Markdown 文件按 UTF-8 严格解码，失败回退 GBK，两者都失败报 `validation/file_encoding_unknown`。
- **1:1 保留源行为（重要）**：`create-html` / `create-markdown` / `create-office` 的 prepare 会并发做「文件夹创建权限校验 + 文件夹默认值兜底 + 默认共享兜底」，但源逻辑让**共享兜底结果覆盖文件夹兜底结果**，所以这三个操作实际不会把文件夹默认的 `participant_ids` / `virtual_folder_ids` 回填进请求体；被丢弃时 prepare 会在 `warnings` 里明确提示。需要生效请显式传这两个字段，或改用 `caizhilian.document.create-by-upload`（不做共享兜底，文件夹默认值会回填）。

### 编辑文档

| operation | 必填 | 说明 |
| --- | --- | --- |
| `caizhilian.document.update-field` | `doc_id`、`field`、`value` | `field` 枚举：`abstract`（摘要）/`auto_invalid_date`（失效日期）/`keywords`（关键词）/`name`（标题，不允许空串） |
| `caizhilian.document.update-author` | `doc_id`、`user_id` | 变更文档作者 |
| `caizhilian.document.update-html` | `doc_id`、`summary` | 保存在线 HTML 正文并生成新版本 |
| `caizhilian.document.replace-content` | `file_path`、`doc_id` | 用本地文件替换正文（`reUpload` + `afterReplaceDocumentContent`），扩展名需与文档正文类型匹配 |

- `replace-content` 要求本地文件与目标文档的**正文类型**一致（WORD 文档只能用 Office 文件替换，不能用 PDF 等）；类型不匹配或没有替换权限时，该操作不可用——如实告知用户并停止，**不要自行改用其他方式**（另建文档、复制权限、删除重建等）达成目的。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json caizhilian run caizhilian.document.search --input-json '{"keywords":"季度报告","folder_id":"200","page_size":10}'
weaver-work-cli --json caizhilian run caizhilian.document.get --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.document.create-html.prepare --input-json '{"name":"季度报告","folder_id":"456","folder_type":"company","author_id":"789","summary":"<p>正文</p>"}'
weaver-work-cli --json caizhilian run caizhilian.document.create-html.apply --input-json '{"name":"季度报告","folder_id":"456","folder_type":"company","author_id":"789","summary":"<p>正文</p>"}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.document.create-office.prepare --input-json '{"file_path":"C:\\docs\\方案.docx","folder_id":"456","folder_type":"company","author_id":"789"}'
weaver-work-cli --json caizhilian run caizhilian.document.update-field.prepare --input-json '{"doc_id":"1234567890","field":"name","value":"季度报告(终版)"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json caizhilian run caizhilian.document.search --input-json '{"keywords":"季度报告","folder_id":"200","page_size":10}'
weaver-work-cli --json caizhilian run caizhilian.document.get --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.document.create-html.prepare --input-json '{"name":"季度报告","folder_id":"456","folder_type":"company","author_id":"789","summary":"<p>正文</p>"}'
weaver-work-cli --json caizhilian run caizhilian.document.create-html.apply --input-json '{"name":"季度报告","folder_id":"456","folder_type":"company","author_id":"789","summary":"<p>正文</p>"}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.document.create-office.prepare --input-json '{"file_path":"/tmp/docs/plan.docx","folder_id":"456","folder_type":"company","author_id":"789"}'
weaver-work-cli --json caizhilian run caizhilian.document.update-field.prepare --input-json '{"doc_id":"1234567890","field":"name","value":"季度报告(终版)"}'
```

写操作一律 `prepare` -> 用户确认 -> `apply`，`apply` 的入参必须与 `prepare` 完全一致（详见 `write-protocol.md`）。

## 输出处理

- `document.search` 返回 `{ total, page_no, page_size, has_next, documents[] }`；每条含 `id`、`name`、`docCreateTime`、`docLastUpdateTime`、`docAuthorId/Name`、`docCreatorId/Name`、`folderPathName`、`belongFolderIds`、`type`、`size`、`docStatus`、`docStatusName`。回复默认用 Markdown 表格展示序号/标题/作者/所属文件夹/更新时间，`id` 只作为后续 operation 入参，不当作展示内容。
- `document.get` 返回文档基础信息：`docName`（名称）、`abstractText`（摘要）、`authorId`/`authorName`（负责人）、`creatorId`/`creatorName`（创建者）、`docStatus`（状态码）、`keywords`、`summary`（HTML 正文摘要）、`createTime`、`lastUpdateTime`、`contentMainType`/`content`（正文文件 ID）/`contentType`（如 WORD / EXCEL / PPT / PDF）、`coordinate`（1=协同文档）、`parentFolders[]`（`id`/`name`/`namePath`/`type`）、`attachments[]`（`id`/`name`/`extName`/`size`（bytes）/`createTime`）、`permission`（操作权限标志：`withEditPermission`、`canEditTitle`、`canEditContent`、`canDelete`、`canDownload`、`canMove`、`canUploadFile`、`maxSize`（MB）、`replaceMainText` 等）、`operateMenuSettings[]`（可用操作菜单，仅保留 `show=true` 且 `openStatus=1` 的项）。字段较多时只摘要用户关心的部分；写操作前可用 `permission` 判断当前用户是否被允许，不要凭猜测。
- 创建类 `prepare` 返回 `data` 里的预览（`doc_type`、`content_type`、`name`、`folder_id`、`folder_type`、`author_id`、`content_length`、`tags_count`、`participant_ids`、`virtual_folder_ids`、`doc_share_list_count`、`request`）+ `continuation` + `expires_in_ms` + `hint`，`meta.status = "PREPARED"`。向用户摘要时给出标题、目标文件夹、作者、正文长度和将要产生的副作用。
- 创建类 `apply` 返回 `{ doc_id }`（新文档 ID，可用 `document.get` 复核）；`create-office.apply` 额外带 `file_id`；`create-by-upload.apply` 批量时返回 `{ results[], summary: { total, success, failed } }`，单文件时返回 `{ doc_id, file_id, name, size, ext_name }`（`meta.batch=false`）；单个文件失败会写进 `results[].error` 和 `warnings`，不要当成整体失败重试。
- 编辑类 `apply` 返回变更回显：`update-field` → `{ doc_id, <field 对应字段名>: 新值 }`（`name` / `keywords` / `abstract_text` / `auto_invalidate_date`）；`update-author` → `{ doc_id, user_id }`；`update-html` → `{ doc_id, summary }`；`replace-content` → 上传结果 `{ file_id, name, size, ext_name, version }`（`meta` 带 `doc_id` / `content_type`）。

## 注意

- 创建和编辑文档都是服务端写操作：`create-html` / `create-markdown` / `update-field` / `update-author` / `update-html` 是 `high-risk-write`，`create-office` / `create-by-upload` / `replace-content` 是 `read-with-upload`（会读本地文件并上传）。
- 创建文档前，服务端会校验**目标文件夹的新建文档权限与允许的文档类型**（合约中以 `permissions` 标记为 `folder.create-document`）：无权限或类型不允许时返回 `folder_no_create_permission` / `doc_type_not_allowed`，原样转述给用户，不要重试；需要提前确认时用 `caizhilian.folder.permission.query`。
- 执行任何读本地文件、上传文件、替换正文的操作前，必须先提醒用户：文件内容会被上传到 E10 采知连文档中心或文件服务器，并可能进入大模型上下文用于理解和处理；必须等用户明确确认后再继续。
- `update-html` 会生成新版本，`replace-content` 会替换正文文件；两者都不可撤销，确认摘要里必须写明目标 `doc_id` 与文档标题。
- 不要为了「补全信息」自动多查一遍：用户已给 `doc_id` 时直接 `document.get` 或对应 `prepare`。

## 失败处理

| error.subtype | 触发场景 | 处理 |
| --- | --- | --- |
| `field_required` / `field_empty` | 缺必填或值为空（如 `field=name` 传空串） | 补齐后重试一次 |
| `enum_invalid` | `folder_type` / `field` 取值非法 | 按枚举修正 |
| `doc_category_invalid` | `doc_category` 不是整数 | 只传 `0` 或 `1` |
| `id_invalid` | `doc_id` / `folder_id` / `author_id` 非数字 | 重新查真实 ID |
| `time_range_invalid` | `create_time` 无法解析 | 用枚举或显式区间 |
| `file_not_found` / `file_unreadable` / `file_path_invalid` | 本地文件问题 | 让用户确认路径与权限，不要猜路径 |
| `file_type_not_allowed` / `file_type_mismatch` | 扩展名不被接受或与正文类型不匹配 | 如实告知不支持并停止；不要自行改用其他方式达成（换文件属于用户的决定，先问用户） |
| `file_encoding_unknown` | Markdown 既不是 UTF-8 也不是 GBK | 让用户转码后重试 |
| `permission_check_failed` / `folder_no_create_permission` / `doc_type_not_allowed` | prepare 前置权限校验失败 | 原样转述，提示需要文件夹管理权限，不要重试 |
| `user_info_unavailable` | 未传 `author_id` 且取不到当前用户 | 先用 `caizhilian.user.current`，再显式传 `author_id` |
| `doc_not_found` | 文档不存在或已被删除 | 如实告知用户「文档不存在或已被删除」，可用 `document.search` 重新定位；不要反复重试同一个 ID |
| `doc_info_unavailable` | 目标文档信息取不到 | 用 `document.get` 复核 `doc_id` |
| `plan_changed` | prepare 与 apply 之间文件内容/元信息变化 | 重新 prepare |
| `api/business_error` | 服务端业务失败 | 转述 message，不要重复提交写请求 |
| `partial/write_uncertain` | 创建/替换结果不确定 | 立即停止，最多补一次 `document.search` 或 `document.get` 只读回查，禁止自动重放 |