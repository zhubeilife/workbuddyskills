# 文件上传

本模块把一个本地文件上传到 E10 文件服务，返回经过校验的文件 ID 与本地回执。
上传协议采用 `weaver-file-upload` 的预检查、秒传、普通上传和分片上传契约。
文件绑定到文档、附件字段、表单或消息由调用方负责。

## 运行与认证

- 唯一运行时为 `weaver-work-cli`；源码位于 `src/shortcuts/caizhilian/file-upload/`，
  操作入口位于 `src/shortcuts/caizhilian/operations/handlers/file-upload.ts`。
- 安装与登录遵守 `../../weaver-e10-shared/SKILL.md`。认证只使用 CLI 当前身份或连接器注入的身份。
- 本模块不执行独立 Skill 的 `dist/weaver-file-upload.js`，不复用 `e10-login` 的会话，
  不启动第二套 Chrome 登录；独立 Skill 的双登录模式不属于本 CLI 上传接口。
- 缺少会话或登录失效时按共享规则处理，不自行切换账号或环境。

## 操作与参数

| 操作 | 作用 | 必填 |
| --- | --- | --- |
| `caizhilian.file-upload.contract` | 获取完整命令、参数用途、策略和结果证据 | 无 |
| `caizhilian.file-upload.prepare` | 本地文件/上下文检查与 MD5、SHA256；不登录、不联网、不签发上传票据 | `file_path`、`module` |
| `caizhilian.file-upload.upload.prepare` | 用户授权检查、本地校验、绑定当前环境和身份的确认票据 | `file_path`、`module`、`user_confirmed=true` |
| `caizhilian.file-upload.upload.apply` | 校验确认票据和内容未变，再执行上传 | 上述参数、`continuation`、`confirm=true`（CLI 用 `--yes`） |

上传参数来自真实业务上下文，不能因为缺少可选字段阻塞基础上传。

| 参数 | 用途 |
| --- | --- |
| `file_path` | 普通文件绝对路径；拒绝符号链接，复用已有宿主附件路径 |
| `module` | 真实业务模块，1–64 个字母、数字或 `._-`；无默认值，禁止猜测 |
| `user_confirmed` | 当前用户对本文件上传的明确授权；必须为布尔 `true` |
| `context_file`（可选） | 可选业务上下文 JSON 对象文件绝对路径，最大 64 KiB、嵌套最多 12 层 |
| `chat_id`（可选） | 宿主对话标识，隔离回执；1–128 个字母、数字或 `._-`，默认 `cli` |
| `timeout_seconds`（可选） | 每次请求及响应读取的超时上限，1–3600 秒，默认 300 |

`context_file` 可包含真实业务提供的 `source`（来源场景）、`fieldId`（附件字段）、
`sourceRefId`（来源对象）、`authModule`（鉴权模块）、`customParam`（模块扩展）、
`refId`（关联对象）、`commonText`（通用扩展）、`folderId`（目标文件夹）。
空字符串按原业务语义保留。上下文不得包含凭证或危险对象键，也不能覆盖协议自动字段：
`sf_request_type`、`compressImg`、`module`、`name`、`size`、`MD5`、`lastModified`、
`lastModifiedDate`、`preUploadId`、`uploadType`、`uploadShardSize`、`chunk`、`chunks`、`file`。

### 上传时间戳规则

`lastModified` 与 `lastModifiedDate` 是自 Unix epoch 起的**整数毫秒**，两个字段必须一致。
Node.js `stat().mtimeMs` 可能含小数；CLI 仅在生成协议字段时使用
`String(Math.floor(file.mtime_ms))`，例如 `1791798507076.7322` 转为 `1791798507076`。
预检查、普通上传及每个分片都复用该整数值。不能直接提交带小数的 `mtimeMs`，也不能换成秒。

本地用于检测文件变更的修改时间保留原始精度；无需修改源文件的时间属性。
这些字段由 CLI 生成，不需要用户提供，也不能通过 `context_file` 覆盖。
移植上传协议或维护其他运行时时，必须保留此归一化规则。

## 上传与结果验证

1. 未确认上传时，在文件读取、认证和网络操作前拒绝 `upload.prepare/apply`。
2. 票据绑定环境、身份、完整入参、文件 SHA256 和上下文哈希；确认后改变文件或上下文必须重新 prepare。
3. 执行 `preUploadCheck`，两个上传接口均固定 `sf_request_type=ajax`。
4. `second` 直接解析已有文件对象；`common` 流式上传整个文件；`chunk` 使用服务端 MiB 分片大小，
   逐片发送精确切片、零起始编号、总片数与实际片字节数。未知策略和缺少预检字段直接失败。
5. 中间分片必须明确 `endChunk=false` 且没有终态文件 ID；最终结果必须包含非空文件 ID。
   服务端返回的非零大小必须与本地一致；HTTP 200 或 `endChunk=true` 本身不能证明成功。
6. 文件不会整体缓存在内存。multipart 使用精确 `Content-Length`，包含安全文件名和 RFC 5987 UTF-8 文件名。
   响应最大 4 MiB，保留大整数文件 ID 的字符串精度。

成功结果包含 `version=weaver_file_upload_result.v1`、`business_verified=true`、
`upload_type`、归一化 `file`、`integrity.md5/sha256`、安全 `request_evidence`、
`receipt_ref` 与 `receipt_sha256`。同时保留兼容字段 `file_id`、`file_name`、`size`、`ext`。

回执位于 CLI 私有状态目录下的 `caizhilian/file-upload/runs/<chat_id>/receipts/`，
POSIX 文件权限为 `0600`、回执目录为 `0700`。回执只保存归一化元数据和哈希，
不保存凭证、签名 URL、业务上下文值、multipart 或原始服务端响应。

## 失败处理

- 上传 POST 后的连接中断、响应读取或协议失败返回 `partial/write_uncertain`，
  `execution_state=unknown`、`retry_safe=false`，不得自动重放。
- 文件上传已确认成功但回执写入失败返回 `partial/receipt_write_failed`，携带已上传文件 ID；
  不得因回执失败重新上传。
- 服务端明确拒绝、策略无效、分片不一致、文件 ID 缺失或大小不符都是失败；不得报告为上传成功。
- 若 `/api/file/module/upload` 返回业务 `code=500`（HTTP 可能仍为 200），且错误含
  `For input string: "1791798507076.7322"` 这类带小数的毫秒时间戳，说明提交值触发整数解析错误。
  检查所用 CLI 是否包含时间戳归一化修复；维护其他运行时时核对上述两个字段。
  不能仅凭 500 判定为此问题；结果不确定时仍遵守不得自动重放的规则。
- 本地准备和预检失败没有上传文件内容的副作用。重新上传必须是用户授权的新事务。

## 命令示例

先读取 contract。下面的 `document` 只示意真实文档业务；使用时必须来自当前调用方场景。
只有用户已经明确确认后，才传 `user_confirmed=true`，并遵守共享规则的连接器参数要求。

Windows PowerShell：

```powershell
weaver-work-cli --json caizhilian run caizhilian.file-upload.contract
weaver-work-cli --json caizhilian run caizhilian.file-upload.prepare --input-json '{"file_path":"C:\\data\\report.pdf","module":"document"}'
weaver-work-cli --json caizhilian run caizhilian.file-upload.upload.prepare --input-json '{"file_path":"C:\\data\\report.pdf","module":"document","user_confirmed":true,"chat_id":"current-chat"}'
weaver-work-cli --json caizhilian run caizhilian.file-upload.upload.apply --input-json '{"file_path":"C:\\data\\report.pdf","module":"document","user_confirmed":true,"chat_id":"current-chat"}' --continuation TOKEN --yes
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json caizhilian run caizhilian.file-upload.contract
weaver-work-cli --json caizhilian run caizhilian.file-upload.prepare --input-json '{"file_path":"/data/report.pdf","module":"document"}'
weaver-work-cli --json caizhilian run caizhilian.file-upload.upload.prepare --input-json '{"file_path":"/data/report.pdf","module":"document","user_confirmed":true,"chat_id":"current-chat"}'
weaver-work-cli --json caizhilian run caizhilian.file-upload.upload.apply --input-json '{"file_path":"/data/report.pdf","module":"document","user_confirmed":true,"chat_id":"current-chat"}' --continuation TOKEN --yes
```

## 验证范围

`test/business/caizhilian-file-upload.test.ts` 使用本机 HTTP 服务验证真实 multipart 传输、
三种上传策略、带小数毫秒的文件修改时间归一化、内容变更保护、授权门禁、回执和失败恢复。
此验证不等于真实 E10 租户验证。
