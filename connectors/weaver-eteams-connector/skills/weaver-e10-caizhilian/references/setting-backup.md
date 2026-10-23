---
name: weaver-setting-backup
description: "对话式管理 weapp 后台\"文件设置 → 备份设置\"页面：开关本地备份、列出备份规则、 调整规则路径/周期/启停、删除规则。`backup on` 一句话开启、`backup update --id N --period 720` 一句话调整。覆盖 `POST /api/file/tenant/setting/save`（开关 `sysLocalFileBackup`）+ `FileBackupController` 全部 5 个 CRUD 端点。Use for 备份设置、本地备份、附件备份、备份规则、backupRule、backupPath、备份周期、 文件设置备份、eteams-file 备份、<your-e10-domain>/info/fileSet/backup."
license: Proprietary
compatibility: 泛微E10采知连配套使用，内部可自由使用与修改，禁止对外分发
metadata:
  maintainer: unknown
  type: capability
  version: 1.0.0
  updated: 2026-08-19
  tags: [备份设置, 本地备份, 备份规则, backupRule, 备份周期]
---

# weaver-setting-backup

让"文件设置 → 备份设置"页面**用一句话就能管**。背后调两类接口：
- `POST /api/file/tenant/setting/save`（开关 `sysLocalFileBackup`）
- `FileBackupController` 全部 5 个 CRUD 端点（list/get/update/delete/enable）

修改前先 diff，写操作必走对话确认。

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

- 用户说"把本地备份打开""关掉本地备份""备份周期改成 720 分钟"
  "列出所有备份规则""禁用规则 id=1""删除规则 id=2"等
- 改 weapp 后台的"备份设置"页（`<your-e10-domain>/info/fileSet/backup`）
- 调试 eteams-file 备份策略

**不适用**：附件设置（见 `weaver-setting-attach`）、加解密设置（见
`weaver-setting-encrypt`）、存储设置、文件采集设置、预览编辑设置、
文件深度清理、页面设置——这 6 个 Tab 走的接口各不相同，**不在本 skill 范围**。

## 命令清单

CLI 软链名 `setting-backup`（用全名避开与 `weaver-setting-attach` 的
`setting-attach`、`weaver-setting-encrypt` 的 `setting-encrypt` 软链冲突）。

| 命令 | 作用 |
|---|---|
| `backup on` | 开启本地备份（无规则时自动建默认规则） |
| `backup off` | 关闭本地备份 |
| `backup show` | 显示开关状态 + 默认规则详情 |
| `backup list` | 列出所有备份规则（表格） |
| `backup update --id <N> [--name] [--org-path] [--backup-path] [--period] [--enable/--disable]` | 调整某条规则 |
| `backup enable --id <N>` | 启用某条规则 |
| `backup disable --id <N>` | 禁用某条规则 |
| `backup delete --id <N> [--yes]` | 删除某条规则（prod 必须 `--yes`） |

## 一句话用法

```text
# 开启本地备份
backup on

# 调整周期（720 分钟 = 12 小时）
backup update --id 1 --period 720

# 改备份路径
backup update --id 1 --backup-path /nfs/data/backup

# 禁用某条规则
backup disable --id 1

# 删规则（prod 必须 --yes）
backup delete --id 2 --yes
```

## 硬性门禁

1. **写操作必须先 diff**——`on/off/update/enable/disable/delete` 不带 `--yes` 时
   把 diff/影响打到 stdout 并等 stdin `y` 才发请求；EOF / `n` 视为取消。
   **对话式 agent 流程**：即使 CLI 已带 `--yes`，**仍必须先在对话里走
   "改前值 / 改后影响 / 明确询问" 三步**（见对话式规则 3），得到
   "改 / 确认 / 好的" 之类回复后才调 CLI。
2. **`prod` 必须 --yes**——防手滑。
3. **不开开关不能调规则**——`backup update/enable/disable/delete` 在
   `sysLocalFileBackup=false` 时拒绝（关着的备份调规则没意义）。
4. **period 范围 60-1440 分钟**（后端 `FileBackupManagerImpl.java:57` 校验）；
   CLI 也做同样校验。
5. **新建规则不能走 CLI**——后端没 `/api/file/create/backup/rule` 端点（前端 bug）；
   唯一新建路径是 `backup on` 在无规则时自动建默认。
6. **保存后校验**——`on/off/update/enable/disable` 后调一次 GET 拉回确认。

## 对话式交互规则

> 这些是 **agent 在对话中使用本 skill 时**的硬约束，跟底层 CLI 脚本无关。命令行直接跑
> `backup` 可以绕过，但任何经由本 skill 的 agent 流程都必须遵守。

1. **操作前必查登录态**
   每次执行业务操作前，确认 CLI 已完成登录：
   - 若 `weaver-work-cli auth status` 显示未登录，提示用户执行 `weaver-work-cli auth login` 或 `weaver-work-cli auth set` 完成登录
   - 登录完成后**立刻**继续用户原本的请求，不要让用户再敲一次命令

2. **查询要简洁**（`show / list` 时的输出格式）
   - **只返回三样**：设置项名（业务中文）、当前值、**当前租户名**
   - **不要**返回：bool 三态展开、enum 解释、字段语义说明、风险提示、
     "建议/可以这么做" 等附加内容 —— 这些只在用户追问时再说
   - `show` 开关状态：单行一行，格式固定

     ```
     <租户名> · <设置项名>：<当前值>
     ```

   - `show` / `list` 规则详情：**按列表逐项展示**（每行一个字段），
     规则名前**不显示** `规则 #<id>`，直接用规则名。格式固定：

     ```
     <租户名> · <规则名>：
     - 状态：<启用 / 禁用>
     - 源目录：<org-path>
     - 备份目录：<backup-path>
     - 周期：<period> 分钟
     ```

     - 多条规则时按顺序依次排列，每条独立一组

3. **修改前必须三步问清**
   - 步骤 a — **改前的值**：说清楚这一项当前是什么（从 GET 里取，不要瞎猜）；
     涉及路径/周期时复述当前值，让客户确认是不是他/她要改的那条
   - 步骤 b — **改后影响**：说清楚改完影响什么业务、触及哪些文件、是否
     **会触发新文件 IO 失败**（路径不可达时）、周期超出 60-1440 范围时
     明确说"会被后端拒"
   - 步骤 c — **明确询问**：用一句话问"要改成 X 吗？"，**得到用户肯定回复
     (y / 改 / 确认 / 好的 之类)才发 POST**，即使 CLI 已带 `--yes` 也不许跳过
   - 三步可以一次消息里说全，但步骤 c 的问句**必须独立成行**，不能藏在
     长段落里让人找不到
   - `on` 操作必须确认开关目标（"现在关着要开 / 现在开着要关"）和**是否
     已经在所有 E10 节点挂载好共享备份目录**（见规则 5 的运维前置）

4. **话术面向客户（非开发）**
   本 skill 的对话对象是**客户/业务人员**，不是开发。所有输出话术：
   - **禁止出现**：CLI key（`--id` / `--period` / `--org-path` 等）、DTO 字段名
     （`sysLocalFileBackup` 等）、布尔字面值（`true` / `false`）、HTTP 术语
     （POST / GET / 200 / 401）、内部流程术语（"步骤 a / 步骤 b / 步骤 c"、
     "diff"、"回 y / 改"、"落库"）
   - **必须使用**：业务中文名（"本地备份"、"备份规则"、"备份周期"）、
     业务状态（"已开启 / 已关闭"、"启用 / 禁用"）、自然语言确认
     （"要打开吗？回 改 / 确认 / 好的"）
   - 需要看技术细节时（用户主动问"用的什么字段" / "接口是啥" / "为什么改不了"），
     **只在该轮回应**展开，平时一律隐藏
   - 身份信息隐藏 `userId` / `tenantKey` 这类内部 ID，只说"当前租户"
   - **路径描述严禁用 E10 内部术语**（如 E10 内部 path 概念），统一用
     业务中文（"源目录" / "备份目录"）

5. **做不到时正确引导**
   客户要改的项**当前工具/接口改不了**或**前置条件没满足**时，**不要**静默
   截断、**不要**发注定失败的请求。常见场景：
   - **共享备份目录没挂载（硬阻断）** — 调 `on / update / enable` 前必须
     主动问"你那边的运维同事已经把共享备份目录挂到所有 E10 节点了吗？"，
     客户回"挂好了 / 已挂"才继续；客户说不清楚或没挂，**直接停手**并
     解释"没挂载就开后端写文件会失败"，不要静默继续
   - **路径不在 E10 服务器能访问的目录（白话，禁止静默接受）** — 源目录
     和备份目录都必须是 E10 应用服务器能访问的目录（不能是客户本机的
     `/Users/xxx`、不能是某个应用节点临时目录、不能是其他服务器的远程
     路径），否则后端写不进去。改路径时 agent **必须**在话术里复述这个约束
   - **改"备份目录"前必做本地预校验，不发注定失败的请求** — 后端
     `FileSettingManagerImpl.checkBackupPath`
     （`src/main/java/com/weaver/teams/file/e10/manager/file/FileSettingManagerImpl.java:276-302`）
     会拒 5 类路径，agent 改路径前**必须**在 CLI 端先把目标路径跑一遍
     等价校验，任一不过**直接告诉客户"后端会拒：<原因>"，让客户重新给路径**，
     **不要**静默发请求让后端报错。5 项校验：

     1. 必须以 `/` 开头（Windows 跳过这条）
     2. 不能含 `\` `*` `?` `"` `<` `>` `|`
     3. FILE_PATH 正则不匹配（`\s` 空白 + `\` + `;` + `'` + `*` + `？`(全角) + `?` + `"` + `<` + `>` + `|`）
     4. 不能等于源目录（源目录按 `;` 切分后逐个比较）
     5. 不能是源目录的子目录（源目录末尾补 `/` 后取备份路径前 N 位对比）

     CLI 已有 `_validate_backup_path()` 函数封装这 5 项（`scripts/backup_setting.py`），
     `cmd_update` 在 `--backup-path` 显式传值时自动跑，错误打到 stderr 并
     `return 4`，不发请求。常见客户语言：
     - "路径要以 / 开头"（CODE_20080）
     - "路径不能含特殊字符 \* ? \" < > |"（CODE_20078）
     - "路径不能含空白 / 分号 / 单引号 / 全角问号"（FILE_PATH 正则）
     - "备份路径不能和源路径相同"（CODE_20082）
     - "备份路径不能是源路径的子目录"（CODE_20079）
   - **period 超范围（60-1440 分钟）** — 客户想设"30 分钟"或"2880 分钟"，
     直接告诉客户范围是 60-1440 分钟（1-24 小时），**不**静默截断
   - **规则 id 不存在** — `update / enable / disable / delete --id N` 里的 N
     找不到时，先调一次 `list` 把当前 id 列表给客户看，让客户重新指定
   - **只支持 1 条默认规则，不能新增** — 后端业务上只允许存在 1 条"默认
     备份规则"，也没有新建规则端点。客户想"新建第二条规则"时，**直接
     告诉客户后端不支持**（不是 CLI 限制，是产品设计），只能在现有默认
     规则上调路径 / 周期 / 启停。新装环境无规则时，启用本地备份（`on`）
     会自动建这条默认规则
   - **`update` 想开/关的开关没显式传** — 没传 `--enable/--disable` 时
     保持原状态；客户**明确说**"要启用" 时**必须**传 `--enable`
   - **后端返回致命错误**（已知）：不重试，直接告诉客户失败原因 + 正确路径
   - 话术模板：
     "这里改不了：<原因>。需要去<正确路径>那里先做<前置操作>。
      在那边保存后，回到这里再让我帮你改备份设置里的对应项，
      就能改到你想要的值了。"

6. **典型部署模板（默认值参考）**
   客户问"备份能干嘛用" / "本地存储 + 备份服务器" 场景怎么配 / "默认值是多少"，
   直接给两步走 + 默认参考值：
   - **第一步（运维前置）**：运维把共享备份目录挂到所有 E10 节点
   - **第二步（业务配置）**：在 E10 后台 文件设置 → 备份设置 开启 + 配置 + 保存
   - **默认参考值**：源目录 = E10 文件数据目录（如 `/nfs/date`），
     备份目录 = 共享备份目录（如 `/nfs/bakFile`），
     周期 = **1440 分钟（24 小时）**
   - 客户明确想调时，**先报出这个参考值再问**"想调到多少"，别直接问"设多少"

## 宿主

CLI 入口：

```text
python3 scripts/backup_setting.py <cmd> [args]
```


## 与 weaver-setting-attach / weaver-setting-encrypt 的关系

三个 skill **互相独立**，可在同一台机器共存：

| | weaver-setting-attach | weaver-setting-encrypt | weaver-setting-backup |
|---|---|---|---|
| 改的页面 | 文件设置 → 附件设置 | 文件设置 → 加解密设置 | 文件设置 → 备份设置 |
| CLI 软链 | `setting-attach` | `setting-encrypt` | `setting-backup` |
| 共享 | 后端 `POST /api/file/tenant/setting/save` 共用一份；凭证统一通过 CLI 托管的认证获取 |
| 不同 | attach 走"逐字段 update"；encrypt 走"整对象 toString"；backup 走"开关字段 + 独立 CRUD 控制器" |

## 版本

- 0.1.0（2026-08-06）首次创建。
- 0.2.0（2026-08-06）优化：对话式规则完整内联 6 条（去除外部仓库依赖），加上 backup
  特有"业务前置 + 路径约束 + 典型部署模板"作为规则 6/7 整合；重写"与 attach/encrypt
  关系"段（删开发内部决策）；门禁 1 补对话确认说明；加版本号规则。
- 0.2.1（2026-08-09）优化：规则 3 `show` / `list` 规则详情输出格式改为按列表
  逐项展示，规则名前不再显示 `规则 #<id>`，直接用规则名。
- 0.2.2（2026-08-09）澄清：业务上后端只支持 1 条"默认备份规则"，不能
  新建第二条。规则 6 改写为"只支持 1 条默认规则，不能新增"，去掉
  "新建规则没 CLI 入口"的旧表述（之前会让用户去找 weapp 后台手动加，
  实际是后端根本不支持）。
- 0.2.3（2026-08-09）修 bug + 加预校验：
  - `scripts/backup_api.py 的 `get_rule`` 参数从 `id` 改为 `backupId`（后端
    `FileBackupServiceImpl.getBackupRule:88` 校验的是 `backupId`，传 `id`
    被拒）
  - `scripts/backup_setting.py 的 `cmd_update`` 拉详情时多下沉一层到 `weaForm.data`，
    否则 `backupName` 等字段读到空串
  - 规则 6 加"改备份目录前必做本地预校验"：把后端
    `FileSettingManagerImpl.checkBackupPath:276-302` 的 5 项校验
    （`/` 开头 / 硬禁字符 / FILE_PATH 正则 / 不等于源路径 / 非源路径子目录）
    搬到 CLI 端 `_validate_backup_path()`，update 前自动跑，错误直接
    拦在客户端不发请求

版本号规则 `x.y.z`：
- **x 升** — 大重构（接口变化、DTO 结构变化、命令大幅增删）
- **y 升** — 新增命令、新增子模块、新增业务场景
- **z 升** — 文案修正、门禁澄清、不改行为的小修
# 接口协议

## 端点

| 操作 | 方法 | URL | 入参 | 出参 |
|---|---|---|---|---|
| 拉 settings（含开关） | POST | `{base}/api/file/tenant/setting` | `{}` | `{code, data: {sysLocalFileBackup: ...}}` |
| 改开关 | POST | `{base}/api/file/tenant/setting/save` | `{sysLocalFileBackup: true/false}` | `{code, data: ...}` |
| 列规则 | POST | `{base}/api/file/get/backup/rule/list` | `{pageNo, pageSize}` | `{code, data: FileBackupListDto}` |
| 单个规则详情 | GET | `{base}/api/file/get/backup/rule?id=N` | `?id=N` | `{code, data: FileBackupFormDto}` |
| 更新规则 | POST | `{base}/api/file/update/backup/rule` | `BackupRuleUpdateParam` | `{code, data: null}` |
| 删除规则 | POST | `{base}/api/file/delete/backup/rule` | `{ids: [N]}` | `{code, data: null}` |
| 启停规则 | POST | `{base}/api/file/enable/backup/rule` | `{id, enableStatus}` | `{code, data: null}` |

## 鉴权

`Cookie: ETEAMSID=<id>`，与前端一致。

## POST 注意事项

1. **开关是逐字段 update**：只传 `sysLocalFileBackup` 一个字段，后端不会清空
   其它字段（参考 agent memory 中 weaver-setting-attach 的同款经验）。
2. **开开关 + 无规则 = 自动建默认规则**——`SysLocalFileBackup.java:138-159`：
   ```java
   getInitFileBackup(tenantKey, newValue)
   → 取第一个 LOCAL_STORE 实例 → 构造 BackupRuleCreateParam
     （backupName=默认备份规则, backupPath=orgPath/backup, enableStatus=true）
   → fileBackupManager.createFileBackup(...)
   ```
3. **新建规则的端点不存在**——前端 `createBackupRule` 调的是
   `/api/file/create/backup/rule`，后端 `FileBackupController` 里**没有**这个
   端点。前端 bug，CLI 不暴露 `create`。
4. **period 范围 60-1440 分钟**——后端 `FileBackupManagerImpl.java:57` 校验。
5. **delete 是批量**——body 是 `{ids: [N1, N2, ...]}`；CLI 一次只支持一个
   id，多个需要循环。
6. **enable 接口的字段是 `enableStatus`（Boolean），不是 `enabled`**——后端
   `BackupRuleEnableParam` 用 `enableStatus` 字段。

## 后端实现位置

- Controller：`eteams-file/src/main/java/com/weaver/teams/file/e10/mvc/web/FileBackupController.java`
- 开关注册：`eteams-file/src/main/java/com/weaver/teams/file/e10/manager/set/impl/SysLocalFileBackup.java`
- 规则 CRUD：`eteams-file/src/main/java/com/weaver/teams/file/e10/service/web/impl/FileBackupServiceImpl.java`
- Param/DTO：`eteams-file/src/main/java/com/weaver/teams/file/e10/param/BackupRule*.java`
- 前端 UI：`weapp-file/src/components/pc/FileSet/components/BackupSet/`
# 字段说明

## 顶层：本地备份开关

- **DTO 字段**：`sysLocalFileBackup`（Boolean）
- **GET 端点**：`POST /api/file/tenant/setting`
- **SAVE 端点**：`POST /api/file/tenant/setting/save`（只传这一个字段）
- **特殊行为**：开时如果当前无规则，**自动建默认规则**（用第一个本地存储实例的 path，详见 `SysLocalFileBackup.java:138-159`）

## 备份规则字段

| CLI flag | 后端字段 | 类型 | 必填 | 备注 |
|---|---|---|---|---|
| `--id` | `id` | Long | update/enable/disable/delete 必填 | 规则主键 |
| `--name` | `backupName` | String | update 必填 | 规则名称，< 255 字符 |
| `--org-path` | `orgPath` | String | update 可选 | 源路径 |
| `--backup-path` | `backupPath` | String | update 必填 | 备份路径 |
| `--period` | `period` | Long (分钟) | update 必填 | **60-1440**（1 小时 - 24 小时） |
| `--enable` | `enableStatus=true` | Boolean | update 可选（与 --disable 互斥） | 启用 |
| `--disable` | `enableStatus=false` | Boolean | 同上 | 禁用 |
| — | `backupConfig` | String | update 可选 | 高级配置（CLI 暂不暴露） |

> 列表接口 (`POST /api/file/get/backup/rule/list`) 返回 `FileBackupListDto`：
> ```json
> {
>   "columns": [...],
>   "list": [
>     {
>       "id": 1,
>       "backupName": "默认备份规则",
>       "orgPath": "/nfs/data",
>       "backupPath": "/nfs/data/backup",
>       "period": 1440,
>       "enableStatus": 1,
>       "backupConfig": "..."
>     }
>   ],
>   "pageNo": 1, "pageSize": 50,
>   "totalCount": 1, "totalPages": 1, "nextPage": null
> }
> ```
> `enableStatus` 后端用 0/1 整数表示；CLI 自动翻译成"启用/禁用"。

## ⚠️ 已知坑

1. **没有"新建规则"接口**——后端 `FileBackupController` 没有
   `/api/file/create/backup/rule` 端点；前端代码 `RuleDialog.tsx:120` 调了但
   后端没实现，是个**前端 bug**。CLI 不暴露 `create` 子命令。
2. **唯一新建路径**：`backup on` 开启本地备份时如果无规则会自动建默认
   （用第一个本地存储实例的 path）。如果租户没有本地存储实例，
   `SysLocalFileBackup.java:142` 会抛 `BusinessException("no useful local storage")`。
3. **规则操作需要本地备份开启**——CLI 在 `update/enable/disable/delete` 前
   会 GET 一次 settings 检查 `sysLocalFileBackup`，没开会拒绝并提示先 `on`。
4. **period 范围 60-1440**（后端 `FileBackupManagerImpl.java:57` 校验），
   CLI 也做同样校验；非整数倍数的"1440"会被四舍五入（按分钟）。
