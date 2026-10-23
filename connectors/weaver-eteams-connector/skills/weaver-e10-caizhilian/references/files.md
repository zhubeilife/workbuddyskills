# 采知连文件类操作：附件、封面、文档比对

## 何时使用

- 用户要给某篇文档**上传/替换附件**，或把附件**下载到本地**（含转 PDF 版本）。
- 用户要给文档**设置封面图片**、只上传封面图片拿 `file_id`，或**移除封面**。
- 用户要做**文档比对**：找可比对的文档、列出文档下可比对的文件对象、上传本地文件参与比对、提交左右两个文件拿比对链接。

> 文件类操作会读写用户本地磁盘，并把本地文件内容上传到 E10。**任何涉及附件、图片的上传/下载，都必须先向用户展示文件路径、文件名、大小，并取得明确确认后再执行**；文件内容不得进入大模型上下文。

## 输入要点

### 附件（attachment）

| operation | risk | 必填 | 可选 |
| --- | --- | --- | --- |
| `caizhilian.attachment.upload.prepare` / `.apply` | read-before-write / read-with-upload | `file_path`、`doc_id` | `folder_id` |
| `caizhilian.attachment.replace.prepare` / `.apply` | read-before-write / read-with-upload | `file_path`、`doc_id`、`attachment_id`、`folder_id` | 无 |
| `caizhilian.attachment.download` | local-file-write | `attachment_id`、`doc_id` | `save_path` |
| `caizhilian.attachment.download-as-pdf` | local-file-write | `attachment_id`、`doc_id` | `save_path` |

- `upload` 是新增附件；`replace` 走源 `reUpload`，**保留原附件 ID**（旧文件版本被顶替），所以 `attachment_id` 与 `folder_id` 都是必填，必须先用 `caizhilian.document.get` 或 `caizhilian.compare.list-file-objects` 拿到真实附件 ID。
- `download` 的 `save_path` 可以是**完整文件路径**，也可以是以 `/` 或 `\` 结尾的**目录**（目录时文件名取自响应头 `content-disposition`，已过滤路径穿越字符）。
- 未传 `save_path` 且没有配置默认下载目录时直接报 `no_save_path`（源 `assets/config.json` 的 `http.download.default_dir` 为空，CLI 侧不提供默认目录），必须让用户给出保存位置。
- `download-as-pdf` 会先调 `/api/file/download/toPdf?fileId=<attachment_id>` 预检，服务端返回不支持时报 `pdf_not_supported`；支持时带 `downloadToPdf=true` 下载 PDF 版本。
- 下载单文件上限 **100MB**，超限报 `file_too_large`；下载/上传超时 **120 秒**（普通接口 12 秒）。
- 同名文件已存在时按源的 `rename` 策略自动改名为 `名称(1).扩展名`、`名称(2).扩展名`……**不覆盖**已有文件。

### 附件历史版本（attachment.list-versions）

| operation | risk | 必填 | 可选 |
| --- | --- | --- | --- |
| `caizhilian.attachment.list-versions` | read | `attachment_id` | `doc_id`、`page_no`(1)、`page_size`(10) |

- 按附件 ID 查询该附件的**全部历史版本**（每次替换/新建产生的版本都在列表里，含当前最新版本）。
- `attachment_id` 来自 `caizhilian.document.get` 或 `caizhilian.compare.list-file-objects`；`doc_id` 可传可不传（不传时按空处理），需要时可同时给。
- 返回每个版本的 `id`（版本 ID）、`name`（文件名）、`versionNumber`（版本号）、`updateTime`、`describe`（版本说明，如「新建」「替换」）、`extName`（扩展名）。
- `updateTime` 自动转为东八区 `YYYY-MM-DD HH:MM:SS`：毫秒/秒时间戳均可，已是时间格式的字符串原样透传，无法识别的值原样保留。
- 结果超过一页时 `has_next=true`，用 `page_no` 翻页；不要拿返回计数推断总量。

### 封面（cover）

| operation | risk | 必填 | 说明 |
| --- | --- | --- | --- |
| `caizhilian.cover.upload.prepare` / `.apply` | read-before-write / read-with-upload | `file_path` | 只上传图片拿 `file_id`，**不改任何文档** |
| `caizhilian.cover.set.prepare` / `.apply` | read-before-write / read-with-upload | `doc_id`、`file_path` | 上传图片后把 `coverPictureId` 写到文档基础字段 |
| `caizhilian.cover.remove.prepare` / `.apply` | read-before-write / high-risk-write | `doc_id` | 把 `coverPictureId` 置空 |

- 封面图片扩展名白名单（源 `IMAGE_ALLOWED_EXT`）：`.bmp`、`.gif`、`.jpeg`、`.jpg`、`.png`、`.webp`；不在白名单报 `file_type_not_allowed`。
- `cover.set` 是**两步服务端写入**（先上传、再改文档字段），中途失败可能出现「图片已上传但封面未生效」，此时不要自动重放，先 `document.get` 回查。

### 文档比对（compare）

| operation | risk | 必填 | 可选 |
| --- | --- | --- | --- |
| `caizhilian.compare.search-documents` | read | 无 | `name`、`author`、`creator`、`create_time`、`folder`、`page_no`(1)、`page_size`(20) |
| `caizhilian.compare.list-file-objects` | read | `doc_id` | 无 |
| `caizhilian.compare.upload-file.prepare` / `.apply` | read-before-write / read-with-upload | `file_path` | 无 |
| `caizhilian.compare.submit.prepare` / `.apply` | read-before-write / external-artifact | `left_file_id`、`right_file_id` | 无 |

- 典型链路：`search-documents` 或 `list-file-objects` 拿到左右两侧的 `file_id` → （本地文件则 `upload-file` 拿 `file_id`）→ `submit` 得到 `compare_link`。
- `submit` 的 13 个比对选项在源里**全部固定为 0**，CLI 1:1 沿用，不暴露给用户配置。
- `compare_link` 是**外部制品**：CLI 只返回链接，不代下载、不代打开。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json caizhilian run caizhilian.attachment.upload.prepare --input-json '{"doc_id":"1234567890","file_path":"C:\\data\\合同.pdf"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.upload.apply --input-json '{"doc_id":"1234567890","file_path":"C:\\data\\合同.pdf"}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.attachment.replace.prepare --input-json '{"doc_id":"1234567890","attachment_id":"888","folder_id":"456","file_path":"C:\\data\\合同v2.pdf"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.download --input-json '{"doc_id":"1234567890","attachment_id":"888","save_path":"C:\\data\\out\\合同.pdf"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.download-as-pdf --input-json '{"doc_id":"1234567890","attachment_id":"888","save_path":"C:\\data\\out"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.list-versions --input-json '{"attachment_id":"888"}'
weaver-work-cli --json caizhilian run caizhilian.cover.set.prepare --input-json '{"doc_id":"1234567890","file_path":"C:\\data\\cover.png"}'
weaver-work-cli --json caizhilian run caizhilian.cover.remove.prepare --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.compare.list-file-objects --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.compare.submit.prepare --input-json '{"left_file_id":"888","right_file_id":"999"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json caizhilian run caizhilian.attachment.upload.prepare --input-json '{"doc_id":"1234567890","file_path":"/tmp/data/contract.pdf"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.upload.apply --input-json '{"doc_id":"1234567890","file_path":"/tmp/data/contract.pdf"}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.attachment.replace.prepare --input-json '{"doc_id":"1234567890","attachment_id":"888","folder_id":"456","file_path":"/tmp/data/contract-v2.pdf"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.download --input-json '{"doc_id":"1234567890","attachment_id":"888","save_path":"/tmp/data/out/contract.pdf"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.download-as-pdf --input-json '{"doc_id":"1234567890","attachment_id":"888","save_path":"/tmp/data/out/"}'
weaver-work-cli --json caizhilian run caizhilian.attachment.list-versions --input-json '{"attachment_id":"888"}'
weaver-work-cli --json caizhilian run caizhilian.cover.set.prepare --input-json '{"doc_id":"1234567890","file_path":"/tmp/data/cover.png"}'
weaver-work-cli --json caizhilian run caizhilian.cover.remove.prepare --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.compare.list-file-objects --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.compare.submit.prepare --input-json '{"left_file_id":"888","right_file_id":"999"}'
```

## 输出处理

- **prepare 返回**：`data` 含本地文件预览 `{ file_name, file_size, file_md5, ext_name }` + `upload` 预览块（`path`、`extra_body`、`allowed_ext`、`required_permission`、`deferred_to_apply: true`），外加 `continuation`、`expires_in_ms`、`hint`，`meta.status = "PREPARED"`。向用户摘要时必须写清「哪个文件、多大、传到哪篇文档/做什么」。
- **上传类 apply 返回**：`{ file_id, name, size, ext_name, ... }`（`attachment.upload` 额外把源的 `uploadTime` 改名为 `upload_time` 放在最后；`attachment.replace` 与 `document.replace-content` 额外带 `version`（新版本号））。命中服务端 MD5 秒传时不会真正传文件，但返回结构一致。
- **下载类返回**：`{ file_path, file_name, file_size }`，`meta` 带 `{ doc_id, attachment_id }`。回复用户时给出**绝对路径 + 文件大小**，并提示已存在同名文件时被自动改名。
- `cover.upload.apply` 返回 `{ file_id, name, size, ext_name }`；`cover.set.apply` 返回 `{ doc_id, file_id, name }`；`cover.remove.apply` 返回 `{ doc_id, cover_picture_id }`（`cover_picture_id` 为删除后的空串）。
- `compare.list-file-objects` 返回 `{ attachments: [{ docId, file_id, ext_name, file_name, size, updateTime }] }`，其中 `file_id` 就是 `compare.submit` 需要的 ID；用 Markdown 表格摘要「文件名/类型/大小/更新时间」。
- `attachment.list-versions` 返回 `{ versions: [{ id, name, versionNumber, updateTime, describe, extName }], has_next }`；`updateTime` 已转为东八区时间字符串。用 Markdown 表格摘要「版本号/文件名/更新时间/版本说明」，`id` 作为后续操作入参，不作为展示主体。
- `compare.search-documents` 与 `document.search` 同构（`{ page_no, page_size, has_next, documents[] }`），参见 `document.md`。
- `compare.submit.apply` 返回 `{ compare_link }`，把链接原样交给用户，不要尝试抓取链接内容。

## 注意

- **附件、图片属于用户私有数据**：上传前必须让用户确认文件路径与目标文档；下载前必须确认保存位置。文件二进制内容**不得读入大模型上下文**，只能引用路径、文件名、大小、MD5 这类元数据。
- 用户只说「把那个文件传上去」时，**必须先取得明确确认**（哪个文件、传到哪篇文档），不要自行猜测路径或复用上一次的路径。
- `attachment.replace` 会顶替原附件内容且**不可撤销**，确认摘要里必须写明被替换的 `attachment_id` 与文件名。
- `cover.remove` 是 high-risk-write：封面移除后需要重新上传才能恢复，确认摘要要说明后果。
- prepare 之后如果本地文件被改动（MD5 或大小变化），apply 会报 `file_changed`，必须重新 prepare——不要试图绕过。
- 上传/下载是**长耗时操作**（120 秒超时）：一次只跑一个，不要并发批量上传；批量建文档请用 `document.create-by-upload`（见 `document.md`）。
- `compare.upload-file` 上传前会走比对模块的上传凭证权限校验（合约中以 `permissions` 标记为 `compare.upload`）；校验失败时原样转述错误，不要重试或改用其他接口绕行。
- 下载会写本地磁盘，属于 CLI 的 local-file-write 能力：只在用户指定的目录内写入，不要自作主张落到仓库工作区或系统目录。

## 失败处理

| error.subtype | 触发场景 | 处理 |
| --- | --- | --- |
| `file_not_found` | 路径不存在或不是文件 | 让用户确认路径，不要猜 |
| `file_unreadable` | 文件被占用或无读权限 | 提示关闭占用程序后重试一次 |
| `file_path_invalid` | `file_path` 为空 | 补齐后重试 |
| `file_type_not_allowed` | 扩展名不在白名单（封面图片、Office 建文档、替换正文各有白名单） | 转述支持的扩展名清单给用户 |
| `file_too_large` | 下载内容超过 100MB | 告知上限，建议改用 E10 页面下载 |
| `no_save_path` | 下载未给 `save_path` 且无默认目录 | 向用户索要保存路径 |
| `pdf_not_supported` | 该附件不支持转 PDF | 改用 `attachment.download` 下原文件 |
| `file_changed` | prepare 后本地文件被修改 | 重新 prepare |
| `upload_precheck_invalid` | 预上传检查响应缺 `preUploadId`/`uploadType` | 停止，把 message 交给用户 |
| `permission_denied` | 预上传检查返回无 `upload` 权限 | 转述给用户，不要重试 |
| `field_required` | `doc_id` / `attachment_id` / `folder_id` 为空 | 先用只读操作补齐真实 ID |
| `plan_changed` / `continuation_*` | 请求体指纹或票据校验失败 | 见 `write-protocol.md` |
| `partial/write_uncertain` | 上传/改字段结果不确定 | 立即停止，最多补一次 `document.get` 或 `compare.list-file-objects` 只读回查，禁止重放 |
