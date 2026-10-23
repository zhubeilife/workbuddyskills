---
name: weaver-setting-attach
description: "对话式修改\"文件设置 → 附件设置\"页面的 15 个配置项（上传最大、上传格式控制 方式、附件打开方式、批量下载、禁止移动端下载、附加提示、图片压缩、版本清理、 打印转 PDF 等）。通过自然语言 / `setting set --item key=value` 即可完成 GET 全量 → modify（保留原值） → diff 让用户确认 → POST 落库，无需打开 浏览器逐项点击。覆盖 weapp 端 `POST /api/file/tenant/setting` 与 `POST /api/file/tenant/setting/save` 两条接口。另提供只读查询：按审批流程 ID 查附件上传目录（caizhilian.setting-attach.list-upload-folders）。Use for 改附件设置、改上传 最大、改附件打开方式、改白名单黑名单、附件批量下载、禁止移动端下载、附加 提示、文件设置、文件上传、格式限制、图片压缩、版本清理、清理文件版本、 打印转 PDF、按流程查上传目录、流程附件目录、流程上传文件夹、eteams-file 后台、<your-e10-domain>/info/fileSet/attach."
license: Proprietary
compatibility: 泛微E10采知连配套使用，内部可自由使用与修改，禁止对外分发
metadata:
  maintainer: unknown
  type: capability
  version: 1.0.0
  updated: 2026-10-13
  tags: [附件设置, 上传最大, 格式控制, 批量下载, 图片压缩, 版本清理, 打印转PDF, 流程上传目录]
---

# weaver-setting-attach

让"文件设置 → 附件设置"页面**用对话就能改**。背后只调两条 HTTP 接口
（`POST /api/file/tenant/setting` 拉全量 / `POST /api/file/tenant/setting/save`
保存），改之前先 diff 让用户确认，**绝不会**误清空未指定字段。

## 前置依赖

### 认证前置（必须）

本模块通过 CLI 托管的认证获取凭证（base_url + Cookie + eteamsid + User-Agent），凭证契约见共享规则 [`../../weaver-e10-shared/SKILL.md`](../../weaver-e10-shared/SKILL.md)，不依赖手动配置文件，Agent 不得自己读取或输出凭证。

**使用前必须确保**：
1. CLI 已安装：`weaver-work-cli --version` 能正常输出版本号
2. 已完成登录：`weaver-work-cli auth status` 显示已登录

**首次登录**：
```text
# OAuth2.0 浏览器授权（推荐）
weaver-work-cli auth login

# 或手动写入 ETEAMSID（从浏览器 DevTools 复制）
weaver-work-cli auth set --eteamsid "PCACCOUNT_xxx"
```

**凭证过期处理**：操作返回认证错误时，提示用户通过 `weaver-work-cli auth login` 或 `weaver-work-cli auth set` 重新登录。

## When to use

- 用户说「把附件批量下载关了」「上传最大改成 2G」「白名单改成 png,jpg」
  「禁止移动端下载附件打开」「图片音视频在新页签打开」等
- 改 weapp 后台的"附件设置"页（`<your-e10-domain>/info/fileSet/attach`）
- 需要批量修附件设置但不想打开浏览器一项项点
- 调试 eteams-file 后台设置项
- 出现「附件设置 / 上传设置 / 打开方式 / 批量下载 / 禁止移动端 / 附加提示 /
  格式白名单黑名单 / 上传分片」等关键词

不适用：存储设置、备份设置、文件采集设置、加解密设置、预览编辑设置、文件
深度清理、页面设置——这些 Tab 走的是另一套接口（多数要 `POST /papi/file/...`），
**不在本 skill 范围**。

## 命令清单

| 命令 | 作用 |
|---|---|
| `setting show` | 拉全量设置并以表格打印 |
| `setting set --item <key=value> [--item ...] [--dry-run] [--yes]` | GET → 合并 → diff → 询问 → POST |
| `setting diff --item ...` | 只打印 diff，不调任何接口 |

## 按流程查附件上传目录（caizhilian.setting-attach.list-upload-folders）

**只读操作**。用户给出审批流程（含 e-builder 建模流程）的 ID，查该流程的附件会
上传到哪些知识库文件夹。CLI 会自动合并「通用附件设置」与各「附件字段」的目录
配置，去重后一次返回。

```text
weaver-work-cli --json caizhilian run caizhilian.setting-attach.list-upload-folders --input-json '{"workflow_id":"12345"}'
```

- **入参**：`workflow_id`（审批流程 ID，字符串，必填，不要用 JSON 数字传）。
- **返回**：`folders` 数组，每项含
  - `id` / `name` / `path`：文件夹 ID、名称、完整路径；
  - `sources`：该文件夹的来源列表——`{type:"common_setting"}` 表示来自流程的
    通用附件设置；`{type:"field", field_id, field_name}` 表示来自某个附件字段的
    目录配置。同一文件夹出现在多个来源时会合并成多条 `sources`。
- **行为细节**：只有目录型（folderType=1）的附件字段才查字段级目录，其余字段跳过；
  个别字段查询失败时跳过该字段，不影响其余来源。

**反向查询**：从文件夹反查哪些审批流程把它设为上传目录，用
`caizhilian.setting-attach.list-workflows-by-folders`（入参 `folder_ids`）。

**排查提示**：返回空 `folders` 只表示该流程没有配置任何上传目录（或环境不支持），
先和用户核对流程 ID 是否正确，不要据此断定「流程不存在」或「功能不支持」。

## 按名称搜索审批流程（caizhilian.setting-attach.search-workflows）

**只读操作**。按流程名称模糊搜索审批流程（含 e-builder 建模流程），返回流程 ID、
名称和类型。典型用途：用户只说了流程名称时，先用本操作搜到流程 ID，再查该流程的
附件上传目录（`caizhilian.setting-attach.list-upload-folders`）。

```text
weaver-work-cli --json caizhilian run caizhilian.setting-attach.search-workflows --input-json '{"keyword":"附件文档普通流程"}'
```

- **入参**：`keyword`（流程名称搜索词，模糊匹配，自动去除首尾空格；可选，不传或
  空白返回全部流程）、`page_no`（默认 1）、`page_size`（默认 100）。旧字段名 `name`
  仍可作为 `keyword` 的别名使用，但两者同时出现且取值不一致会报错。
- **返回**：`{ page_no, page_size, has_next, workflows: [{ id, workflowName, typeName }] }`。
  `id` 就是 `list-upload-folders` 需要的流程 ID（字符串，后续入参直接引用）。
- **分页**：默认只查第一页；返回 `has_next=true` 时先告诉用户还有更多结果，由用户
  决定是否继续翻页，不要自动翻页拉全量。
- **匹配语义**：按流程名称模糊匹配；同名流程可能有多条（不同分部/类型），用
  `typeName` 和上下文区分，拿不准时让用户选，不要自行挑一条。

## 15 个支持字段

字段别名（中文 / 英文 / DTO 字段名）三选一即可：

| 别名（key） | DTO 字段 | 类型 | 备注 |
|---|---|---|---|
| `upload-max` | `sysMaxSingleUploadSize` | 数字 + 单位（KB/MB/GB） | 不可超过 `sysMaxSingleUploadLimitSize` |
| `shard-size` | `uploadShardSize` | 整数 MB | 1 ≤ n ≤ 50 |
| `format-mode` | `sysFormatWhitesEnable` | `whitelist` / `blacklist` | 切换模式后会自动迁移 `format-list` |
| `format-list` | `sysFormatWhites` 或 `sysFormatBlacks` | 逗号/分号分隔扩展名 | 自动按当前 mode 写到正确字段 |
| `non-image-open` | `sysNonImageMediaOpenType` | `newTab` / `popupWindow` | 后端实际只有这两个值（v0.1.0 表格写的 dialog/directDownload 是错的，已纠正） |
| `image-open` | `sysImageMediaOpenType` | `newTab` / `previewComponent` | |
| `show-attach-list` | `sysPreviewShowAttachmentList` | bool | |
| `attach-expand` | `sysAttachmentListDefaultExpand` | bool | |
| `custom-msg` | `sysUploadCustomMsgEnable` (+ `sysUploadCustomMsg`) | bool (+ 文本) | 写 `custom-msg=true::安全提示文本` 一次性带上 |
| `batch-download` | `sysBatchDownload` | bool | |
| `mobile-block` | `sysAppDownload` | bool | 自然语义"禁止移动端下载"为 true（CLI true ↔ DTO true） |
| `download-pdf-types` | `sysDownloadToPdfFileTypes` | 逗号分隔扩展名 | |
| `img-compress` | `sysImgCompressEnable` | bool | 图片压缩总开关（关闭时子项 img-compress-quality 不生效） |
| `img-compress-quality` | `sysImgCompressQuality` | `low` / `medium` / `high` | 压缩质量（仅在 img-compress 开启时生效） |
| `auto-clear-version` | `sysAutoClearFileVersion` | bool | 文件版本自动清理总开关（关闭时子项 version-size / version-time 不生效） |
| `version-size` | `sysFileVersionSize` | 整数(1-500) / `-1`(不限) | 每个文件最多保留多少个历史版本。**与 `version-time` 互斥**，由 `version-clean-type` 决定生效哪个 |
| `version-time` | `sysFileVersionTime` | 整数(1-1095) / `-1`(永久) | 每个文件的历史版本保留多少天。**与 `version-size` 互斥**，由 `version-clean-type` 决定生效哪个 |
| `print-pdf-types` | `sysPrintToPdfFileTypes` | 逗号分隔扩展名 | 打印时需要转 PDF 的扩展名（空 = 未启用，独立项） |
| `version-clean-type` | `sysAutoClearFileVersionType` | `versionSize` / `versionTime` | 版本清理方式（按份数 / 按时间）—— v0.2.0 补。**决定 `version-size` 和 `version-time` 哪个生效** |
| `version-size-type` | `sysFileVersionSizeType` | `selected` / `custom` | 份数那一行 UI 状态（selected = 选下拉 / custom = 自定义）—— v0.2.0 补 |
| `version-time-type` | `sysFileVersionTimeType` | `selected` / `custom` | 时间那一行 UI 状态（selected = 选下拉 / custom = 自定义）—— v0.2.0 补 |

### 版本清理设置规则（强制）

设置版本清理时，**必须同时设置以下 6 个字段**才能让前端正确生效：

```json
{
  "auto-clear-version": true,
  "version-size": <数量>,
  "version-time": <天数>,
  "version-clean-type": "versionSize",
  "version-size-type": "custom",
  "version-time-type": "custom"
}
```

**单独设置 `version-size` 或 `version-time` 不会生效**，必须同时设置 `version-size-type` 和 `version-time-type` 为 `custom`。

完整别名表见 [setting-attach-field-map.md](setting-attach-field-map.md)。

## 硬性门禁

1. **写操作必须先 diff**——`set` 不带 `--dry-run` 也不带 `--yes` 时，强制把 diff
   打到 stdout 并等用户在 stdin 输入 `y` 才发 POST；EOF / `n` / 非 `y` 全部视为取消。
2. **`prod` 必加 --yes**——生产环境操作时必须同时带 `--yes` 才会发 POST，
   防止手滑改生产。
3. **只 POST changed 字段，不透传全量**——后端 `fileSettingSave` 是**逐字段 update**（遍历
   DTO，非 null 字段调 `FileSetItemServiceProxy.updateSysFileItem`），且会用每个字段名
   调 `FileobjTenantPermissionEnum.valueOf(key)`；**只读/虚拟字段**（如
   `sysMaxSingleUploadLimitSize`、`id` 等）不在 enum 里，会抛
   `IllegalArgumentException` 让整笔事务回滚。`set` 只把 diff 出的字段 POST 上去。
4. **保存后再次 GET 校验**——POST 完调一次 `tenant/setting` 比对 diff，不一致立即
   报错并打印服务端返回值。
5. **不写日志到 home 之外**——所有凭证 / 日志只落在 `~/.minimax/skills/weaver-setting-attach/`
   下，不写系统级。
6. **版本清理必须一次到位**——设置版本清理时，必须同时设置 6 个字段（`auto-clear-version`、
   `version-size`、`version-time`、`version-clean-type`、`version-size-type`、`version-time-type`），
   其中 `version-size-type` 和 `version-time-type` 必须为 `custom`，否则前端不生效。

## 对话式交互规则

> 这些是 **agent 在对话中使用本 skill 时**的硬约束,跟底层 CLI 脚本无关。
> 命令行直接跑 `setting.py` 可以绕过,但任何经由本 skill 的 agent 流程都必须遵守。

1. **操作前必查登录态**
   每次执行业务操作前，确认 CLI 已完成登录：
   - 若 `weaver-work-cli auth status` 显示未登录，提示用户执行 `weaver-work-cli auth login` 或 `weaver-work-cli auth set` 完成登录
   - 登录完成后**立刻**继续用户原本的请求，不要让用户再敲一次命令

2. **查询要简洁**(`show` / 读设置时的输出格式)
   - **只返回三样**:**设置项名**(中文别名或 DTO 字段名)、
     当前值、**当前租户名**
   - **不要**返回:bool 三态展开、enum 解释、字段语义说明、风险提示、
     "建议/可以这么做" 等附加内容 —— 这些只在用户追问时再说
   - 多项查询时一行一项,格式固定:

     ```
     <租户名> · <设置项名>：<当前值>
     ```

3. **修改前必须三步问清**
   - 步骤 a — **改前的值**:说清楚这一项当前是什么(从 GET 里取,不要瞎猜)
   - 步骤 b — **改后影响**:说清楚改完会影响什么业务、放行/禁止哪些格式、
     触及哪些用户,以及是否会**间接影响其他字段**(如 `format-mode` 切换会
     迁移 `format-list` 到另一个 DTO 字段)
   - 步骤 c — **明确询问**:用一句话问"要改成 X 吗?",**得到用户肯定回复
     (y / 改 / 确认 / 好的 之类)才发 POST**,即使 CLI 已带 `--yes` 也不许跳过
   - 三步可以一次消息里说全,但步骤 c 的问句**必须独立成行**,不能藏在
     长段落里让人找不到

   **互斥字段必须主动引导**：当用户同时设置互斥字段时，必须在执行前说明
   互斥关系并让用户选择，不能先执行再提醒。典型场景：

   - **版本清理**：`version-size`（按份数）和 `version-time`（按时间）互斥，
     由 `version-clean-type` 决定生效哪个。用户同时设置两个值时，必须先问
     「你想按份数保留（如最多保留 4 个版本），还是按时间保留（如保留 12 天）？」，
     确认后再设置对应的清理方式和数值
   - **格式控制**：`format-mode` 切换会迁移 `format-list` 到另一个字段，
     必须说明迁移影响

4. **话术面向客户(非开发)**
   本 skill 的对话对象是**客户/业务人员**,不是开发。所有输出话术:
   - **禁止出现**:CLI key(`mobile-block`、`upload-max`、`format-list` 等)、
     DTO 字段名(`sysAppDownload`、`sysMaxSingleUploadSize` 等)、布尔字面值
     (`true` / `false`)、HTTP 术语(POST / GET / 200 / 401)、内部流程术语
     ("步骤 a / 步骤 b / 步骤 c"、"diff"、"回 y / 改"、"落库"、"diff 让用户确认")
   - **必须使用**:业务中文名("移动端禁止下载" 开关、"上传单文件最大"、
     "黑白名单")、业务状态("已开启 / 已关闭 / 允许 / 禁止"、
     "顶到上限 / 不会真生效")、自然语言确认("要打开吗?回 改 / 确认 / 好的")
   - 需要看技术细节时(用户主动问"用的什么字段" / "接口是啥" / "为什么改不了"),
     **只在该轮回应**展开,平时一律隐藏
   - 身份信息隐藏 `userId` / `tenantKey` 这类内部 ID,只说"当前租户"

5. **超上限引导**(以"上传单文件最大" 为典型场景;其他带硬上限的字段同款处理)
   客户要把某项值改成**超过该租户硬上限**的数(常见就是"上传单文件最大"
   超过当前租户的上限,比如上限 1 GB、客户要 2 GB):
   - **不要**静默截断、**不要**自动改,直接告诉客户改不了 + 给出正确路径
   - 口语化提示(无开发词):
     "你要改成 X 已经超过你们租户的上限了(当前上限 Y),附件设置里调不了,
     需要去『**租户平台 → 租户详情**』那里把上限先调高"
   - 用口语化文字告知客户操作步骤(三步走):
     1. 打开『**租户平台 → 租户管理**』,在列表里找到并点击要设置的租户
     2. 进入租户详情页,点击右上角"编辑"
     3. 在编辑页找到"单文件最大上传"输入框,填入需要的值,点击右上角"保存"
   - 引导话术末尾加一句:
     "在租户平台那里保存后,回到这里再让我帮你改附件设置里的对应项,
     就能设到你想要的值了"

## 宿主

CLI 入口：

```text
python3 scripts/attach_setting.py <cmd> [args]
```

装好后 `setting show / set ...` 即可直接调用。


## 与 weaver-im 的关系

两者**不共享凭证**（`auth_opt2` 决策）。现在统一通过 CLI 托管的认证获取凭证。

## 版本

- 0.1.0（2026-08-06）首次创建。覆盖 eteams-file 截图"附件设置" Tab 的 11 字段。
- 0.2.0（2026-08-09）补 6 字段：图片压缩(`img-compress` / `img-compress-quality`)、
  版本清理(`auto-clear-version` / `version-size` / `version-time`)、
  打印转 PDF(`print-pdf-types`)。这 3 类功能实际也在附件设置同一页
  (`AttachSet/index.tsx`),0.1.0 时只覆盖 11 项漏了。同时修 `mobile-block`
  alias 的 `invert=True` 方向写反 bug(CLI true 现在直接对应 DTO true)。
# 接口协议

## 端点

| 操作 | 方法 | URL | 入参 | 出参 |
|---|---|---|---|---|
| 拉全量 | `POST` | `{baseUrl}/api/file/tenant/setting` | `{}`（body 留空对象） | `{status, data: FileSettingDto}` |
| 保存 | `POST` | `{baseUrl}/api/file/tenant/setting/save` | `FileSettingDto`（全量） | `{status, data: FileSettingDto}` |

`{baseUrl}` 例：`https://<your-e10-domain>`

## 鉴权

走 `Cookie: ETEAMSID=<id>`，与前端 `axios` 默认 cookie 行为一致。

CLI 自动从 `.env.local` / ENV 读取并塞进 Cookie。

## FileSettingDto 节选（11 字段 + 只读）

完整 DTO 见 eteams-file 仓库 `BaseSetDto.java`。下面只列本 skill 关心的字段：

```json
{
  "sysMaxSingleUploadSize": "1000",          // str (数字+单位)
  "sysMaxSingleUploadLimitSize": "2048",     // str, 只读回传，写时透传
  "uploadShardSize": 5,                      // int
  "sysFormatWhitesEnable": true,             // bool, true=白名单
  "sysFormatWhites": "*",                    // str, 逗号/分号分隔
  "sysFormatBlacks": "",                     // str
  "sysNonImageMediaOpenType": "dialog",      // enum: newTab/dialog/directDownload
  "sysImageMediaOpenType": "previewComponent", // enum: newTab/previewComponent
  "sysPreviewShowAttachmentList": true,      // bool
  "sysAttachmentListDefaultExpand": true,    // bool
  "sysUploadCustomMsgEnable": false,         // bool
  "sysUploadCustomMsg": "",                  // str
  "sysBatchDownload": true,                  // bool
  "sysAppDownload": true,                    // bool (true=禁止移动端下载)
  "sysDownloadToPdfFileTypes": ""            // str
}
```

未指定字段透传：CLI 先 GET 全量 → 把你传的字段 merge 进去 → POST 回去。**绝不会**清空未指定字段。

## 错误码

| HTTP | 业务 status | 含义 |
|---|---|---|
| 200 | `0` | 成功 |
| 200 | 非 0 | 业务异常，看 `msg` 字段 |
| 401/403 | — | ETEAMSID 失效/没权限，重跑 `setting login --config <name>` |
| 5xx | — | 后端挂了，看日志 |

## 后端实现位置（参考）

- Controller：`eteams-file/src/main/java/com/weaver/teams/file/e10/mvc/web/FileSettingController.java`
- DTO：`com.weaver.teams.file.e10.dto.FileSettingDto` / `BaseSetDto`
- 设置项注册：`com.weaver.teams.file.e10.manager.set.FileSetFactory`
- 前端调用：`weapp-file/src/api/fileSetApi.ts` 中 `fileSetDatas` / `fileSetSave`

## POST 注意事项

1. **保存是逐字段 update，不是覆盖式全量**。后端 `fileSettingSave` 遍历 DTO，对**非 null**
   字段调 `FileSetItemServiceProxy.updateSysFileItem(...)`；null 字段跳过不处理。
   意味着：未指定字段**不会被清空**（因为后端根本不动它们）。
2. **但绝对不能透传只读/虚拟字段**——后端用每个字段名 `FileobjTenantPermissionEnum.valueOf(key)`，
   `sysMaxSingleUploadLimitSize` 等虚拟字段不在 enum 里，会抛
   `IllegalArgumentException: No enum constant ...` 让整笔事务回滚。
3. **只 POST 改了的字段**。CLI 用 `field_map.diff` 算出 changed 字段后只发这一份。
4. **服务端会校验范围**：传超范围值会返回业务异常（status=false / code=500），
   CLI 会原样打印 `detailErrorMessage`。
5. **操作日志**：`FileOpLogManager` 会记一条 `fileSetting` 日志（管理员可在"操作日志"里看到）。
# 字段对照表（11 项）

> 对应 eteams-file 后端 `BaseSetDto` / `FileSettingDto`。
> 任意字段用 CLI key、中文别名、或 DTO 字段名（最后一个）都接受。

## 1. 上传最大

- **CLI key**：`upload-max`
- **中文**：`上传最大` / `最大上传`
- **DTO 字段**：`sysMaxSingleUploadSize`
- **类型**：整数 + 单位
- **单位**：`B / KB / MB / GB / TB`（单字母简写也行：`2G` ≡ `2GB`）
- **示例**：
  ```text
  --item upload-max=2G         # 2048 MB
  --item upload-max=2048MB
  --item upload-max=512KB      # 1 MB（< 1MB 自动取整为 1）
  ```
- **校验**：不可超过 `sysMaxSingleUploadLimitSize`（GET 时带回），否则拒绝保存。

## 2. 上传分片大小

- **CLI key**：`shard-size`
- **中文**：`上传分片大小` / `分片大小`
- **DTO 字段**：`uploadShardSize`
- **类型**：整数 MB
- **范围**：1 ≤ n ≤ 50
- **示例**：`--item shard-size=8`

## 3. 上传格式控制方式

- **CLI key**：`format-mode`
- **中文**：`格式控制方式` / `黑白名单模式`
- **DTO 字段**：`sysFormatWhitesEnable`（Boolean：true = 白名单）
- **值**：`whitelist` / `blacklist`（也支持中文：`白名单` / `黑名单`）
- **示例**：`--item format-mode=whitelist`

## 4. 格式列表

- **CLI key**：`format-list`
- **中文**：`格式列表` / `白名单` / `黑名单` / `格式白名单` / `格式黑名单`
- **DTO 字段**：按当前 mode 自动写到 `sysFormatWhites`（白名单 mode）或 `sysFormatBlacks`（黑名单 mode）
- **类型**：字符串，扩展名列表
- **分隔符**：`,` 或 `;` 都接受
- **示例**：
  ```text
  --item format-mode=whitelist --item format-list='png,jpg,jpeg'
  --item format-list='*'             # 全部（白名单下"*" = 允许所有）
  --item format-list='exe,bat,sh'    # 黑名单下禁止这些
  ```

## 5. 非图片/音视频打开方式

- **CLI key**：`non-image-open`
- **中文**：`非图片音视频打开方式` / `非图片打开方式`
- **DTO 字段**：`sysNonImageMediaOpenType`
- **后端 enum**：`FileMediaOpenTypeEnum`（`newTab` / `popupWindow` 两个值，没有"直接下载"）
- **值**：
  | 英文 | 中文 | 含义 |
  |---|---|---|
  | `newTab` | 新页签 / 新窗口 | 浏览器新标签打开 |
  | `popupWindow` | 弹出窗口 / 弹窗 | 弹出预览层 |
- **示例**：`--item non-image-open=新页签`

## 6. 图片/音视频打开方式

- **CLI key**：`image-open`
- **中文**：`图片音视频打开方式` / `图片打开方式`
- **DTO 字段**：`sysImageMediaOpenType`
- **后端 enum**：`FileMediaOpenTypeEnum`（`newTab` / `previewComponent` 两个值）
- **值**：
  | 英文 | 中文 | 含义 |
  |---|---|---|
  | `newTab` | 新页签 | 浏览器新标签打开 |
  | `previewComponent` | 预览组件 / 预览 | 前端内置预览组件 |
- **示例**：`--item image-open=预览组件`

## 7. 预览时显示附件列表

- **CLI key**：`show-attach-list`
- **中文**：`预览显示附件列表` / `显示附件列表`
- **DTO 字段**：`sysPreviewShowAttachmentList`
- **类型**：Boolean
- **值**：`true` / `false` / `1` / `0` / `开` / `关` / `启用` / `禁用`

## 8. 附件列默认展开

- **CLI key**：`attach-expand`
- **中文**：`附件列默认展开` / `附件列表展开`
- **DTO 字段**：`sysAttachmentListDefaultExpand`
- **类型**：Boolean

## 9. 附件附加提示

- **CLI key**：`custom-msg`
- **中文**：`附加提示` / `上传附加提示`
- **DTO 字段**：`sysUploadCustomMsgEnable`（Boolean）+ `sysUploadCustomMsg`（String）
- **复合写法**：`custom-msg=true::<文本>` 一次性写两个
- **只改 bool 不改文本**：`--item custom-msg=true`
- **示例**：
  ```text
  --item custom-msg=true::请勿上传公司机密文件
  --item custom-msg=false   # 关闭附加提示（不抹掉原 msg 字段）
  ```
- **注意**：单独写 bool 时，旧 msg 文本**会保留**（merge 时透传 current 里的值）；要清空 msg 需显式：
  ```text
  --item custom-msg=false --item sysUploadCustomMsg=
  ```
  （第二个写法直接用 DTO 字段名也能接受，**逃生口**。）

## 10. 附件批量下载

- **CLI key**：`batch-download`
- **中文**：`附件批量下载` / `批量下载`
- **DTO 字段**：`sysBatchDownload`
- **类型**：Boolean

## 11. 禁止移动端下载附件

- **CLI key**：`mobile-block`
- **中文**：`禁止移动端下载` / `移动端禁止下载`
- **DTO 字段**：`sysAppDownload`（CLI true ↔ DTO true，禁止移动端下载）
- **类型**：Boolean
- **示例**：
  ```text
  --item mobile-block=true    # 禁止移动端下载
  --item mobile-block=false   # 允许移动端下载
  ```

## 12. 下载需要转 PDF 的文件格式

- **CLI key**：`download-pdf-types`
- **中文**：`下载转PDF格式` / `下载转pdf`
- **DTO 字段**：`sysDownloadToPdfFileTypes`
- **类型**：字符串，逗号分隔扩展名
- **示例**：`--item download-pdf-types='doc,docx,xls,xlsx'`

---

## 逃生口

任意字段也支持直接用 DTO 字段名（snake case 必须小写）作为 key。
不推荐，仅供复杂场景使用——CLI 会**完全信任**你的值不做校验（除了 merge 时的范围检查）。

```text
--item sysMaxSingleUploadSize=2048
--item sysAppDownload=false
--item sysUploadCustomMsg=   # 清空 msg
```
