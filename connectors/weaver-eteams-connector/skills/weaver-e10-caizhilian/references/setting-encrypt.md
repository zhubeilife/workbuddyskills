---
name: weaver-setting-encrypt
description: "对话式修改 weapp 后台\"文件设置 → 加解密设置\"页面的全部 8 个子字段（加解密功能开关、 第三方加解密软件、软件地址、加解密场景、加密/未加密 × 上传/下载 4 个文件处理字段）。 通过自然语言 / `setting-encrypt set --item key=value` 即可完成读取全量 → modify（保留原值）→ diff 让用户确认 → POST 落库。查询优先使用 `GET /api/file/thirdPlugEncDec/config`，旧版本 404 时兼容 `POST /api/file/tenant/setting`；保存使用 `POST /api/file/tenant/setting/save`。Use for 加解密、加密场景、华途、天锐绿盾、亿赛通、文件设置加解密、 <your-e10-domain>/info/fileSet/encryption."
license: Proprietary
compatibility: 泛微E10采知连配套使用，内部可自由使用与修改，禁止对外分发
metadata:
  maintainer: unknown
  type: capability
  version: 1.1.9
  updated: 2026-09-02
  tags: [加解密, 加密场景, 华途, 天锐绿盾, 亿赛通, 文件设置加解密]
---

# weaver-setting-encrypt

> 版本 1.1.9：修正第三方软件名称到后端编码的转换，亿赛通提交为 `est`；同时兼容旧版本查询接口。

让"文件设置 → 加解密设置"页面**用对话就能改**。背后调两条 HTTP 接口：
- `GET /api/file/thirdPlugEncDec/config`（新版本专用端点，读完整 `EncryptionSettings`）
- 兼容旧版本：专用端点返回 404 时，改用 `POST /api/file/tenant/setting` 读取其
  `data.encryptionSettings`，该请求仅查询，不保存配置
- `POST /api/file/tenant/setting/save`（保存，**EncryptionSettings 整对象 toString 存 JSON**）

修改前先 diff，**写操作必走对话确认**；CLI 走 GET 拉整对象 → merge 子字段 → 整对象 POST，
未指定子字段原样保留。

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

- 用户说"把加解密功能打开""加解密软件地址改成 xxx""场景切到上传下载均不处理"
  "加密文件上传=1 加密"等
- 改 weapp 后台的"加解密设置"页（`<your-e10-domain>/info/fileSet/encryption`）
- 调试 eteams-file 后台加解密功能（华途 / 天锐绿盾 / 亿赛通）

**不适用**：附件设置（见 `weaver-setting-attach`）、存储设置、备份设置、文件采集设置、
预览编辑设置、文件深度清理、页面设置——这 6 个 Tab 走的接口各不相同，**不在本 skill 范围**。

## 命令清单

CLI 软链名 `setting-encrypt`（用全名避开与 `weaver-setting-attach` 的 `setting-attach` 冲突）。

| 命令 | 作用 |
|---|---|
| `setting-encrypt show` | 拉加解密配置并以表格打印（兼容旧版本查询端点） |
| `setting-encrypt set --item <key=value> [--item ...] [--dry-run] [--yes]` | GET → merge 子字段 → diff → 询问 → POST |
| `setting-encrypt diff --item ...` | 只打印解析后的子字段，不调任何接口 |

## 8 个支持字段（扁平 key）

CLI 接受三种写法：snake-case 别名 / 中英别名 / DTO 字段名。完整别名表见
[setting-encrypt-field-map.md](setting-encrypt-field-map.md)。

> **历史说明**：早期版本支持 13 个字段（含加密机分支：`encryptMachineType` /
> `encryptIp` / `encryptPort` / `encryptAppID` / `encryptAppKey`）。前端下拉已移除
> 加密机选项（只剩华途 / 天锐绿盾 / 亿赛通 3 个），后端 `EncryptionSettings.toString()`
> 也漏了 `encryptMachineType` 输出，这 5 个字段已废弃。CLI 一并移除。

| 别名（key） | DTO 字段 | 类型 | 备注 | 依赖 |
|---|---|---|---|---|
| `open-encrypt` | `openEncryptFunction` | bool | 加解密功能开关 | — |
| `encrypt-plugs` | `encryptPlugs` | enum | 后端编码：`est`=亿赛通、`tipray`=天锐绿盾、`vtext`=华途（对接方式/限制见 [setting-encrypt-third-party-plugins.md](setting-encrypt-third-party-plugins.md)） | — |
| `encrypt-url` | `encryptUrl` | str (URL) | 软件地址 | — |
| `encrypt-scene` | `encryptScene` | enum | 场景：`uploadAndDownloadEncrypt` / `uploadAndDownloadNotProcessed` / `custom` | — |
| `encrypt-file-upload` | `encryptFileUpload` | enum (str) | 加密文件-上传：`0`=解密 `1`=加密 其它=不处理 | `encrypt-scene=custom` |
| `encrypt-file-download` | `encryptFileDownload` | enum (str) | 加密文件-下载：同上 | `encrypt-scene=custom` |
| `unencrypted-file-upload` | `unencryptedFileUpload` | enum (str) | 未加密文件-上传：同上 | `encrypt-scene=custom` |
| `unencrypted-file-download` | `unencryptedFileDownload` | enum (str) | 未加密文件-下载：同上 | `encrypt-scene=custom` |

## 硬性门禁

1. **写操作必须先 diff**——`set` 不带 `--dry-run` 也不带 `--yes` 时，把 diff 打到
   stdout 并等 stdin 输入 `y` 才发 POST；EOF / `n` / 非 `y` 视为取消。
   **对话式 agent 流程**：即使 CLI 已带 `--yes`，**仍必须先在对话里走
   "改前值 / 改后影响 / 明确询问" 三步**（见对话式规则 3），得到
   "改 / 确认 / 好的" 之类回复后才调 CLI。
2. **`prod` 必加 --yes**——生产环境操作时必须同时带 `--yes` 才会发 POST。
3. **整对象 POST，子字段 merge**——`encryptionSettings` 是 DTO 嵌套对象，后端
   `EncryptionSettings.java:49` 的 `updateSysFileItem` 接收**整对象**并存到 `param`
   字段前 `toString()`（整对象变 JSON 串）。CLI 必须 GET 拉整对象 → 改子字段 merge
   进 `current` → **整对象 toString 一起 POST**。**不能只 POST 改了的子字段**
   （后端不支持增量，会覆盖整对象）；也不能"只 diff 几个 key"就 POST（merge 时
   其他子字段会丢）。
4. **保存后再次读取校验**——POST 完按同样的端点兼容逻辑重新读取并比对。
5. **不写日志到 home 之外**——所有凭证 / 日志只落在
   `~/.minimax/skills/weaver-setting-encrypt/` 下。
6. **未指定子字段保留**——CLI 走 GET 拉整对象再 merge；只改指定子字段，其他保留。
7. **license 检查**——没 `ENC_DEC` license 时 GET 返回的 `openEncryptFunction=false`
   且字段大多为空（前后端都可能拒）；CLI 给出 warning 但仍允许 POST（看后端是否真拒）。

### 后端接口执行规则

加解密设置必须由 `scripts/encrypt_setting.py` 调用 `encrypt_api.py` 完成，禁止通过浏览器表单或浏览器自动化写入。浏览器仅可参与 `weaver-work-cli auth login` 登录授权。

- 查询接口优先是 `GET /api/file/thirdPlugEncDec/config`；旧版本返回 404 时，使用
  `POST /api/file/tenant/setting` 读取 `data.encryptionSettings`。保存接口是
  `POST /api/file/tenant/setting/save`。
- 保存前必须 GET 读取完整的 8 字段对象，合并目标字段后整体保存，不能只提交变更字段。
- 保存后必须重新 GET，确认 `encryptPlugs`、`encryptUrl`、`encryptScene` 与目标值一致；否则明确报告“未保存成功”。
- 下拉列表出现“亿赛通”仅说明前端提供该选项，不代表当前租户已经保存亿赛通；接口回读为空才是未配置。
- `[http://12332](http://12332).com` 不是无歧义的 URL。应先确认用户是否要写入 `http://12332.com`，不能由 agent 静默猜测。
- 用户明确表达“设置为 X”是修改意图；在提交外部写入前仍需按对话确认规则取得明确确认。确认一旦收到，应继续当前待保存流程，不要再次结束在“等待确认”。

## 对话式交互规则

> 这些是 **agent 在对话中使用本 skill 时**的硬约束，跟底层 CLI 脚本无关。命令行直接跑
> `setting-encrypt` 可以绕过，但任何经由本 skill 的 agent 流程都必须遵守。

1. **操作前必查登录态**
   每次执行业务操作前，确认 CLI 已完成登录：
   - 若 `weaver-work-cli auth status` 显示未登录，提示用户执行 `weaver-work-cli auth login` 或 `weaver-work-cli auth set` 完成登录
   - 登录完成后**立刻**继续用户原本的请求，不要让用户再敲一次命令

2. **查询要简洁**（`show` / 读设置时的输出格式）
   - **只返回三样**：设置项名（中文别名或 DTO 字段名）、当前值、**当前租户名**
   - **不要**返回：bool 三态展开、enum 解释、字段语义说明、风险提示、
     "建议/可以这么做" 等附加内容 —— 这些只在用户追问时再说
   - 多项查询时一行一项，格式固定：

     ```
     <租户名> · <设置项名>：<当前值>
     ```

3. **修改前必须三步问清**
   - 步骤 a — **改前的值**：说清楚这一项当前是什么（从 GET 里取，不要瞎猜）
   - 步骤 b — **改后影响**：说清楚改完会影响什么业务、放行/禁止哪些场景、
     触及哪些用户，以及是否会**间接影响其他字段**（如 `encrypt-scene=custom`
     后 4 个文件处理字段才生效）
   - 步骤 c — **明确询问**：用一句话问"要改成 X 吗？"，**得到用户肯定回复
     (y / 改 / 确认 / 好的 之类)才发 POST**，即使 CLI 已带 `--yes` 也不许跳过
   - 三步可以一次消息里说全，但步骤 c 的问句**必须独立成行**，不能藏在
     长段落里让人找不到

4. **话术面向客户（非开发）**
   本 skill 的对话对象是**客户/业务人员**，不是开发。所有输出话术：
   - **禁止出现**：CLI key（`open-encrypt`、`encrypt-plugs` 等）、DTO 字段名
     （`openEncryptFunction`、`encryptPlugs` 等）、布尔字面值（`true` / `false`）、
     HTTP 术语（POST / GET / 200 / 401）、内部流程术语（"步骤 a / 步骤 b / 步骤 c"、
     "diff"、"回 y / 改"、"落库"、"diff 让用户确认"）
   - **必须使用**：业务中文名（"加解密功能"、"加解密软件"、"加解密场景"）、
     业务状态（"已开启 / 已关闭"）、自然语言确认（"要打开吗？回 改 / 确认 / 好的"）
   - 需要看技术细节时（用户主动问"用的什么字段" / "接口是啥" / "为什么改不了"），
     **只在该轮回应**展开，平时一律隐藏
   - 身份信息隐藏 `userId` / `tenantKey` 这类内部 ID，只说"当前租户"

5. **做不到时正确引导**
   客户要改的项**当前工具/接口改不了**时，**不要**静默截断、**不要**发注定失败
   的请求。常见场景：
   - **license 没开**：租户没 `ENC_DEC` license 时，GET 返回的 `openEncryptFunction=false`
     且大部分字段为空，POST 也会被后端拒。引导客户去找管理员开 license，
     或者先去 eteams 后台"租户平台 → 租户详情 → 加解密授权"申请
   - **字段只读**：某些字段受权限管控（当前登录账号没写权限）。让客户找管理员授权
   - **字段间依赖**：`encrypt-file-upload` 等 4 个文件处理字段要
     `encrypt-scene=custom` 才生效（其他依赖关系：3 个加解密软件分支的配置项完全相同，
     不再有"加密机分支"额外配 IP/端口/appID/appKey 的差异）
   - **远程服务/插件对接问题**：客户报"加解密不生效"，但 E10 后台配置本身没问题——
     这是**远程加解密服务不通**（华途/亿赛通）或**天锐绿盾本地没装**导致，**不是
     改 E10 后台设置能解决的**。让客户找对应厂商/运维：
     - 华途对接出问题 → 找华途侧开发 / 客户运维
     - 亿赛通对接出问题 → 找亿赛通侧开发 / 客户运维
     - 天锐绿盾没生效 → 检查应用服务器本地是否安装(文档:见 setting-encrypt-third-party-plugins.md 一节)
     - 总部开发**只负责 E10 后台配置项，不管远程服务**；不要试图通过改 E10 设置来"修"
   - **集成官方支持之外的插件**：走 E10 二开流程（由总部开发评估接入）
   - **后端返回致命错误**（已知）：不重试，直接告诉客户失败原因 + 正确路径
   - 话术模板：
     "这里改不了：<原因>。需要去<正确路径>那里先做<前置操作>。
      在那边保存后，回到这里再让我帮你改加解密设置里的对应项，
      就能改到你想要的值了。"

## 宿主

CLI 入口：

```text
python3 scripts/encrypt_setting.py <cmd> [args]
```


## 与 weaver-setting-attach 的关系

两个 skill **互相独立**，可在同一台机器共存：

| | weaver-setting-attach | weaver-setting-encrypt |
|---|---|---|
| 改的页面 | 文件设置 → 附件设置 | 文件设置 → 加解密设置 |
| CLI 软链 | `setting-attach` | `setting-encrypt` |
| 共享 | 后端 `POST /api/file/tenant/setting/save` 共用一份；凭证统一通过 CLI 托管的认证获取 |
| 不同 | encrypt 优先用 `thirdPlugEncDec/config`，旧版本兼容 `tenant/setting`；POST 模式不同（attach 走"逐字段 update"，encrypt 走"整对象 toString"） |

## 版本

- 0.1.0（2026-08-06）首次创建。覆盖 eteams-file 截图"加解密设置" Tab 的 13 字段。
- 0.2.0（2026-08-06）优化：对话式规则完整内联（去除外部仓库依赖）、字段表加"依赖"列、
  软链名统一为 `setting-encrypt`、门禁 4 表述修正、删除开发内部决策泄露、版本号规则确立。
- 0.2.1（2026-08-06）业务知识沉淀：新建 `setting-encrypt-third-party-plugins.md`，写入 3 个官方
  插件对接步骤 / 限制 / 二开联系人；修正 `encryptPlugs` 常见值（"三未信安"→"天锐绿盾 / 华途"）；
  对话式规则 6 增加"远程服务/插件对接问题"与"集成官方支持之外插件"两类引导。
- 1.0.0（2026-08-09）字段大删减：前端 UI 下拉已移除加密机（`encryptMachine`）选项，
  后端 `EncryptionSettings.toString()` 也漏了 `encryptMachineType` 输出。删除 5 个
  加密机专属字段（`encrypt-machine-type` / `encrypt-ip` / `encrypt-port` / `encrypt-app-id` /
  `encrypt-app-key`），CLI 字段表从 13 缩到 8。`encryptPlugs` 现在固定为华途 / 天锐绿盾 /
  亿赛通 3 个值；3 个软件分支的配置项完全相同，不再有"加密机分支"差异。
- 1.1.7（2026-09-02）明确只能通过后端接口执行加解密设置，移除浏览器写入流程，保留未保存状态判定和歧义 URL 处理。
- 1.1.8（2026-09-02）兼容旧版本部署中 `thirdPlugEncDec/config` 不存在的情况：查询和保存后校验在专用接口 404 时改用 `tenant/setting` 的 `encryptionSettings`。

版本号规则 `x.y.z`：
- **x 升** — 大重构（GET/POST 模式变化、DTO 结构变化、字段大幅增删）
- **y 升** — 新增字段、新增命令、新增子模块
- **z 升** — 文案修正、门禁澄清、依赖注补充、不改行为的小修
# 接口协议

## 端点

| 操作 | 方法 | URL | 入参 | 出参 |
|---|---|---|---|---|
| 拉加解密配置（新版本） | `GET` | `{baseUrl}/api/file/thirdPlugEncDec/config` | （无） | `{code, data: EncryptionSettings}` |
| 拉加解密配置（旧版本兼容） | `POST` | `{baseUrl}/api/file/tenant/setting` | `{}` | `{code, data: FileSettingDto}`，取 `data.encryptionSettings` |
| 保存（走通用 setting save） | `POST` | `{baseUrl}/api/file/tenant/setting/save` | `{encryptionSettings: {...}}` | `{code, data: FileSettingDto}` |

## 鉴权

`Cookie: ETEAMSID=<id>`，与前端一致。

## EncryptionSettings 完整字段（8 子字段）

> **v1.0.0 (2026-08-09) 字段大删减**:从 13 缩到 8。前端 UI 下拉已移除加密机
> (`encryptMachine`) 选项,因此删除 `encryptMachineType` / `encryptIp` /
> `encryptPort` / `encryptAppID` / `encryptAppKey` 5 个加密机专属字段。

GET 端点返回的是**扁平 dict**（8 子字段直接平铺）；POST 时整个扁平对象
作为 `encryptionSettings` 字段的值一起发：

```json
// GET /api/file/thirdPlugEncDec/config 响应 data：
{
  "openEncryptFunction": false,
  "encryptPlugs": "",
  "encryptUrl": "",
  "encryptScene": "uploadAndDownloadEncrypt",
  "encryptFileUpload": "",
  "encryptFileDownload": "",
  "unencryptedFileUpload": "",
  "unencryptedFileDownload": ""
}

// POST /api/file/tenant/setting/save  请求 body：
{
  "encryptionSettings": {  ← 整个扁平对象作为这个字段的值
    "openEncryptFunction": true,
    "encryptPlugs": "est",
    ...
  }
}
```

## POST 注意事项

1. **必须传整对象**：后端 `EncryptionSettings.updateSysFileItem` 接收的是
   `FileSettingSaveParam.EncryptionSettings` 整个对象，存到 `param` 字段前
   `toString()`（即整对象变 JSON 字符串存）。**不能只传 changed 子字段**。
2. **查询端点按部署版本选择**：优先走
   `/api/file/thirdPlugEncDec/config`；若返回 404，则走
   `/api/file/tenant/setting` 并读取 `data.encryptionSettings`。后者是旧版本
   沿用的通用文件设置查询接口，查询请求不会保存配置。
3. **未指定子字段保留**：CLI 走 GET → merge → 整对象 POST；只改指定子字段。
   前端历史上可能把 URL 分隔符编码为 `17643b38` / `17643f70`，CLI 会在读取和
   校验时还原为普通 URL。
4. **license 控制**：没 `ENC_DEC` license 时 GET 返回的 `openEncryptFunction=false`，
   且整个对象字段大多为空。
5. **encryptScene 校验**：后端 `StoThirdPlugEncDecProcess.java:718-722` 对值
   做 `equalsIgnoreCase` 比对；不在 enum 内的值会被忽略（不抛错）。
6. **4 个文件处理字段仅 encryptScene=custom 时生效**：其它场景下后端用预设
   覆盖这 4 个字段（实际行为见 `StoThirdPlugEncDecProcess.java:755-770`）。

## 后端实现位置

- Controller：`eteams-file/src/main/java/com/weaver/teams/file/e10/mvc/web/thirdplugencdec/FileThirdPlugEncDecController.java`
- 设置项注册：`eteams-file/src/main/java/com/weaver/teams/file/e10/manager/set/impl/EncryptionSettings.java`
- 业务逻辑：`eteams-file/src/main/java/com/weaver/teams/file/e10/manager/storage/chain/process/StoThirdPlugEncDecProcess.java`
- DTO：`eteams-file/src/main/java/com/weaver/teams/file/e10/dto/BaseSetDto.java`（嵌套类 `EncryptionSettings`）
- 前端 UI：`weapp-file/src/components/pc/FileSet/components/Encryption/index.tsx`
# 字段对照表（8 个子字段）

> 对应 eteams-file 后端 `BaseSetDto.EncryptionSettings`（嵌套类）。
> 整对象 toString() 存到 `FileObjTenantPermission.param` 字段。
> CLI 接受 snake-case 别名 / 中文别名 / DTO 字段名（驼峰）。

> **数据结构说明**：后端 GET `/api/file/thirdPlugEncDec/config` 返回的是**扁平的
> EncryptionSettings 字典**（8 个子字段直接平铺，没有外层 `encryptionSettings` 包装）。
> CLI 内部统一用扁平 dict；POST 时整个扁平对象作为 `encryptionSettings` 字段的值
> 一起发出去（参考 [setting-encrypt-api.md](setting-encrypt-api.md)）。

> **v1.0.0 (2026-08-09) 字段大删减**:从 13 缩到 8。前端 UI 下拉已移除加密机
> (`encryptMachine`) 选项,后端 `EncryptionSettings.toString()` 也漏了
> `encryptMachineType` 输出,因此删除 5 个加密机专属字段
> (`encrypt-machine-type` / `encrypt-ip` / `encrypt-port` / `encrypt-app-id` /
> `encrypt-app-key`)。3 个加解密软件分支(华途 / 天锐绿盾 / 亿赛通)的配置项
> **完全相同**,不再有"加密机分支"差异。

## 1. 加解密功能开关

- **CLI key**：`open-encrypt`
- **中文**：`加解密功能`
- **DTO 字段**：`openEncryptFunction`
- **类型**：Boolean
- **示例**：`--item open-encrypt=true`

## 2. 第三方加解密软件

- **CLI key**：`encrypt-plugs`
- **中文**：`第三方加解密软件` / `加解密软件`
- **DTO 字段**：`encryptPlugs`
- **类型**：enum（后端内部编码）
- **后端值**：`est`=亿赛通 / `tipray`=天锐绿盾 / `vtext`=华途
- **输入别名**：CLI 也接受 `亿赛通` / `天锐绿盾` / `华途`，提交前会转换为上述编码
- **对接/限制**：
  - 详细对接步骤、限制、二开联系人见 [setting-encrypt-third-party-plugins.md](setting-encrypt-third-party-plugins.md)
  - 天锐绿盾**仅支持本地安装**；远程调用方式需走 E10 二开流程
  - 华途/亿赛通都是远程服务，**总部开发不介入远程服务确认**，找客户/厂商侧
- **示例**：`--item encrypt-plugs=亿赛通`（实际提交 `encryptPlugs=est`）

## 3. 软件地址

- **CLI key**：`encrypt-url`
- **中文**：`软件地址` / `动态链接地址`
- **DTO 字段**：`encryptUrl`
- **类型**：URL 字符串
- **说明**：前端可能将 URL 中的 `/` 编码为 `17643b38`、反斜杠编码为 `17643f70`；CLI
  读取和校验时会自动还原，不应把该编码当作地址内容填写。
- **示例**：`--item encrypt-url=http://<加解密服务IP>:<端口>/sec-server/s/rs/uni`

## 4. 加解密场景

- **CLI key**：`encrypt-scene`
- **中文**：`加解密场景` / `场景`
- **DTO 字段**：`encryptScene`
- **类型**：enum
- **值**（前端 `Encryption/index.tsx:122-129` 实际只有 3 个）：

| 英文 id | 中文 | 含义 |
|---|---|---|
| `uploadAndDownloadEncrypt` | 上传解密，下载加密 | 推荐默认 |
| `uploadAndDownloadNotProcessed` | 上传下载均不处理 | 完全不过加解密软件 |
| `custom` | 自定义 | 走下面 4 个文件处理字段 |

> **截图里看到的第 4 个 radio "上传下载均处理"** —— 前端 data 数组只有 3 个 id，
> 第 4 个是 UI 展示但实际值走 `custom` + 4 个文件处理字段控制。

- **示例**：`--item encrypt-scene=custom` / `--item encrypt-scene=上传下载均不处理`

## 5-8. 4 个文件处理字段

> 仅当 `encrypt-scene=custom` 时生效。
> 值含义：`0`=解密 `1`=加密 其它（如 `2`）=不处理

| CLI key | 中文 | DTO 字段 | 默认 |
|---|---|---|---|
| `encrypt-file-upload` | 加密文件-上传 | `encryptFileUpload` | 加密文件上传时怎么处理 |
| `encrypt-file-download` | 加密文件-下载 | `encryptFileDownload` | 加密文件下载时怎么处理 |
| `unencrypted-file-upload` | 未加密文件-上传 | `unencryptedFileUpload` | 未加密文件上传时怎么处理 |
| `unencrypted-file-download` | 未加密文件-下载 | `unencryptedFileDownload` | 未加密文件下载时怎么处理 |

CLI 接受 3 种写法：

```text
--item encrypt-file-upload=1           # 英文数字
--item encrypt-file-upload=加密        # 中文别名
--item encrypt-file-upload=不处理      # 中文别名
```

## 逃生口

任意字段也支持直接用 DTO 字段名（驼峰）作为 key。**不推荐**：

```text
--item openEncryptFunction=true
--item encryptPlugs=est
```

逃生口只做 `parse_item` 解析，**不做业务校验**。
