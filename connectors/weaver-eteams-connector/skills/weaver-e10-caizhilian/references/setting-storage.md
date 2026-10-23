---
name: weaver-setting-storage
description: "对话式修改**两级**文件存储设置： - **系统级**：租户平台（<your-tenant-platform-domain>/tenant/tenant/doc/storageSet）— 影响所有租户 - **租户级**：后台管理中心（<your-e10-domain> 文件设置 → 存储设置）— 只影响当前租户 通过自然语言 / `storage list / show / test / rule set / rule order / rule open / rule add / rule delete / instance add / instance delete` 即可 完成 GET 拉取 → diff 让用户确认 → POST 落库。v0.4.16 大改：auth 模型全错重写（基于客户 2026-08-17 HAR 实证： 之前 listPageToken 路径 + /api/ 路径 + 单 ETEAMSID cookie 三处都错）—— 真实用 **三件套** ETEAMSID + authToken(JWT cookie) + freepass token(URL query from /sp/file/SysStorageSet/freepass) + randomkey(CSRF 每次生成)，两个 level 都走 /papi/（不再 /api/）；v0.4.15 第二次修：本地存储会显示 压缩/加密/算法（前端按存储实例类型动态切换，不是固定 6 字段）；v0.4.15 第一次修：fileSourceType=1/2/3/4 非 0/1/2/3 + 模块传 moduleFlag 英文非中文名；v0.4.14 新建/删除子规则（rule add/delete）；v0.4.13 7 种 存储类型 defaultField 精准化；v0.4.12 完整话术模板库；v0.4.11 输出格式 markdown bullet 强制换行； v0.4.2 修对象存储凭证字段路由（凭证必须嵌套 `storageConfigInfo`）；v0.4.0 开放实例写操作。 Use for 系统存储设置、租户平台存储设置、租户后台存储设置、文件存储规则、业务规则、静态规则、默认规则、 子目录、压缩存储、加密存储、SM4、nginx 配置。"
license: Proprietary
compatibility: 泛微E10采知连配套使用，内部可自由使用与修改，禁止对外分发
metadata:
  maintainer: unknown
  type: capability
  version: 1.0.0
  updated: 2026-08-19
  tags: [存储设置, 系统存储, 租户存储, 存储规则, 业务规则, 静态规则, 压缩存储, 加密存储]
---

# weaver-setting-storage

让"文件存储设置"页（**系统级** + **租户级**）**用对话就能查 + 改**。背后调 papi 接口（v0.4.16：两个 level 都走 papi，tenant 不再是 api）：

### 系统级（papi + all_teams）
- 存储实例：`/papi/file/storage/listStorageInstance` / `getStorageInstance` / `testConnect`
- 存储规则：`/papi/file/storage/rule/frontComp/ruleForm` / `rule/saveData` / `rule/saveOrder` / `rule/saveOpen` / `rule/search`
- 浏览器辅助：`/papi/file/common/browser/associate/storageInstance`
- **鉴权**：三件套（v0.4.16）

### 租户级（papi + 当前租户，v0.4.16 改：之前误写 api）
- 存储实例：`/papi/file/storage/listStorageInstance` / `getStorageInstance` / `testConnect`
- 存储规则：`/papi/file/storage/rule/frontComp/ruleForm` / `rule/saveData` / `rule/delete` / `rule/frontComp/ruleTable`
- 浏览器辅助：`/papi/file/common/browser/{associate,complete,history}/{storageInstance,module}`（前端用，agent 对话式不需要）
- **鉴权**：三件套（v0.4.16 改：跟 system 一样都要三件套，不再"普通 SSO"）

### v0.4.16 鉴权（三件套，所有 papi 接口通用）

业务接口需要同时带：

- **Cookie**（E10 后台 `<your-e10-domain>` 域）：
  - `ETEAMSID=<id>`（如 `PCACCOUNT_xxx-xxx`）
  - `authToken=<JWT>`（eyJ 开头）
  - `LOGIN_TYPE=pc_account` / `langId=7` / `langType=zh_CN`（辅助，不严格校验）
- **URL query**：
  - `token=<freepass token>`（从 `/sp/file/SysStorageSet/freepass?token=xxx` 来的，32 字符 hex）
  - `wea_link_keep_freepass=1`（免登标志）
  - `tenant_langType=zh_CN`
  - `randomkey_<6 chars>=<6 chars>`（CSRF 防护，每次请求生成一对）

> 之前的 `listPageToken.data.token` 跟 freepass token **不一定是同一个**——listPageToken 是租户平台管理类
> 接口用的，E10 后台业务接口用 freepass token。v0.4.16 改：业务接口全部拼 freepass token。

修改前先 diff，**写操作必走对话确认**；CLI 走 GET 拉当前值 → merge 子字段 → diff → POST 落库 → GET 校验。

## When to use

- 用户说"看一下系统存了哪些存储""默认规则是什么""改一下业务规则路径""恢复系统默认"
- 改租户平台"文件存储设置"页（`<your-tenant-platform-domain>/tenant/tenant/doc/storageSet`，系统级 / all_teams）
- 改后台管理中心"文件设置 → 存储设置"页（`<your-e10-domain>`，租户级 / 当前租户，v0.3.0 新加）
- 改 eteams-file 后端 `StoRuleServiceImpl.saveRule` 走的业务/静态/默认规则
- 解释存储实例类型（本地/腾讯云/阿里云/华为云/S3/FastDFS/HDFS）的字段差异
- 解释"子目录 / 压缩存储 / 加密存储 / 文件来源 / 规则顺序 / nginx 配置"的语义

**不适用**：

- 附件设置 → `weaver-setting-attach`
- 加解密设置 → `weaver-setting-encrypt`
- 备份设置 → `weaver-setting-backup`
- **存储实例的写操作**（新增/修改/删除实例）—— 实例是「系统级只读」，
  改实例要进 E10 后台"系统级存储"页面

## 命令清单

> **知识库参考**（v0.4.2+ 整理自 weapp.eteams.cn 文件服务知识库 "文件存储" 目录）：
> 目录架构 / 7 种存储类型 / 4 种方案推荐 / 清理说明 / 联系人索引 → 都在
> [setting-storage-docs-summary.md](setting-storage-docs-summary.md)。客户对话时按里面"对应 skill 能力映射"节对应命令即可。
>
> **话术模板库**(v0.4.12):13 大场景的话术示例(对话式规则 1-10 + 操作回执 + 概念解释 + 错误兜底) → 都在
> [setting-storage-dialogue-templates.md](setting-storage-dialogue-templates.md)。agent 在客户对话中按场景查模板直接套用。

CLI 软链名 `storage`（避开 setting-attach/encrypt/backup 的 `setting-*` 系列）。

**所有命令共享**：`--config <name>` 必填；`--local` 可选（强制标记本地环境，关闭自动 login 和自动 fetch）；`--level system|tenant` 可选（强制选层级，不传按 baseUrl 域名自动判断）；`--token <value>` 可选（临时覆盖 .env.local 里的 `FREEPASS_TOKEN`）；`--auth-token <value>` 可选（v0.4.16 新增，临时覆盖 .env.local 里的 `AUTH_TOKEN`）。

| 命令 | 作用 | 适用 |
|---|---|---|
| `storage login --config <name> [--base-url <url>]` | **v0.4.16 重写**：起 Chrome + 登录页 + 让用户从租户平台点"进入 E10 后台文件存储设置"链接 → 跳到 `/sp/file/SysStorageSet/freepass?token=xxx` → 自动抓 ETEAMSID + authToken + freepass token 三件套落盘。<br>**本地**：不自动起 Chrome，提示手动配三件套。 | both |
| `storage env --config <name> [--local] [--level]` | 打印当前 config 解析结果（含 `env_type` / `level` / `token` 状态） | both |
| `storage list --config <name> [--page 1] [--size 20]` | 列存储实例 | both |
| `storage show <instance_id> --config <name>` | 单实例详情（7 类字段全展开，accessKey 自动 mask） | both |
| `storage test <instance_id> --config <name>` | 测试某实例连接 | both |
| `storage rule show --config <name> [--default] [--id <ruleId>]` | 拉规则详情（系统级同时返回业务+静态；租户级只返回业务） | both |
| `storage rule list --config <name> [--name <kw>]` | 高级搜索规则列表 | both |
| `storage rule set --config <name> (--default \| --id N) --item k=v [--item ...] [--rule-type 0\|1] [--dry-run] [--yes]` | 改规则：GET → merge → diff → 询问 → POST → 校验。<br>**租户级不支持 `--rule-type 1`（静态规则）**。 | both（rule-type 1 仅 system） |
| `storage rule add --config <name> --name <X> --source <id\|name> --source-type {0\|1\|2\|3} --instance <id> --sub-dir {1..5} [--storage-path] [--algorithm SM4] [--on\|--off] [--compressed] [--encrypted] --yes` | **新建子规则**(v0.4.14):走 `POST /api/file/storage/rule/saveData` ADD 路径,传 `ruleInfoList` 含 1 条不带 id 的 `StoRuleInfo`。 | both |
| `storage rule order --config <name> --ids 1,2,3 [--yes]` | 改规则顺序 | system（租户级可调但意义小） |
| `storage rule delete --config <name> --id <ruleId> --yes` | **删除子规则**(v0.4.14):走 `POST /api/file/storage/rule/delete` 删一条子规则。 | both |
| `storage rule open --config <name> --id N (--on \| --off) [--yes]` | 启用/停用某条 | both |
| `storage rule reset-default --config <name> --yes` | 恢复系统默认 | system only（租户级没有"系统默认"可恢复） |
| `storage explain <field\|type\|concept>` | 解释某字段/存储类型/概念，**不调任何接口** | both |

## 13 个支持字段（rule 子字段，CLI 接受 3 种写法）

snake-case 别名 / 中文别名 / DTO 字段名（驼峰）。完整别名表见
[setting-storage-field-map.md](setting-storage-field-map.md)。

### 通用（业务/静态都可用）

| CLI key | DTO 字段 | 类型 | 备注 |
|---|---|---|---|
| `rule-name` | `ruleName` | str | 多语言字段 |
| `rule-open` | `ruleOpen` | bool | true=启用 / false=停用 |

### 业务规则（`--rule-type 0`，默认）

| CLI key | DTO 字段 | 类型 | 备注 |
|---|---|---|---|
| `storage-instance` | `storageInstanceId` | str | 业务文件落到哪个实例 |
| `storage-path` | `storagePath` | str | 业务文件存储路径（相对 tenantKey） |
| `file-source` | `fileSourceValue` | str | 文件来源 id 列表，逗号分隔 |
| `file-source-type` | `fileSourceType` | enum | `-1`=默认 `0`=模块 `1`=目录 `2`=分部 `3`=部门 |
| `sub-directory-type` | `subDirectoryType` | enum | `1`=年 `2`=月 `3`=天 `4`=部门 `5`=无 |
| `compressed-storage` | `compressedStorage` | bool | 仅本地存储生效 |
| `encrypted-storage` | `encryptedStorage` | bool | 仅本地存储，配套 `sys-file-algorithm` |
| `sys-file-algorithm` | `sysFileAlgorithm` | str | 默认 `SM4` |

### 静态规则（`--rule-type 1`）

| CLI key | DTO 字段 | 类型 | 备注 |
|---|---|---|---|
| `static-storage-instance` | `staticStorageInstanceId` | str | 静态资源落到哪个实例 |
| `static-storage-path` | `staticStoragePath` | str | 静态资源路径/存储桶 |
| `static-nginx-config` | `expandRuleConfig.staticNginxConfig` | str | nginx 配置（嵌套 JSON 子字段，CLI 子字段 merge） |

## 7 种存储类型

CLI 改规则时"选存储实例"指的就是这些。完整字段差异见
[setting-storage-storage-types.md](setting-storage-storage-types.md)：

| code | 名称 | 关键字段 |
|---|---|---|
| 0 | 本地存储 | `storagePath` |
| 1 | 腾讯云 COS | `region` / `bucket` / `accessId` / `accessKey` / `endPoint` |
| 2 | 阿里云 OSS | 同上 + `cname` |
| 3 | 华为云 OBS | 同上 + `rootPath` |
| 4 | S3 标准 | `region` / `bucket` / `accessId` / `accessKey` / `storageHost` / `pathStyle` / `rootPath` |
| 5 | FastDFS | `trackerServers` / `downLoadHost` |
| 6 | HDFS | `hdfsServerIp` / `hdfsServerPort` / `hdfsUserName` / `rootPath` |

## 硬性门禁

1. **写操作必须先 diff** —— `rule set` 不带 `--dry-run` 也不带 `--yes` 时，把 diff
   打到 stdout 并等 stdin 输入 `y` 才发 POST；EOF / `n` / 非 `y` 视为取消。
   **对话式 agent 流程**：即使 CLI 已带 `--yes`，**仍必须先在对话里走
   "改前值 / 改后影响 / 明确询问" 三步**（见对话式规则 4），得到
   "改 / 确认 / 好的" 之类回复后才调 CLI。
2. **环境必须显式** —— 不绑定默认环境；缺 `--config` 且无 ENV 兜底时报错退出。
3. **`prod` 必加 --yes** —— `--config prod` 时必须同时带 `--yes` 才会发 POST。
4. **业务规则 vs 静态规则字段互斥** —— `--rule-type 0`（业务，默认）只接受
   业务/通用字段；`--rule-type 1`（静态）只接受静态/通用字段。CLI 在 parse 阶段
   就拒，不发到后端。
5. **改完后 GET 校验** —— POST 完调一次 `ruleForm` 重拉，比对 expected 与服务端真实值。
6. **不写日志到 home 之外** —— 所有凭证 / 日志只落在
   `~/.minimax/skills/weaver-setting-storage/` 下。
7. **未指定子字段保留** —— CLI 走 GET 拉整对象再 merge；只改指定子字段，其它保留。
8. **租户平台实例只读（v0.4.0 已开放实例写操作，v0.4.2 修字段路由）** —— CLI 走
   `instance add / delete` 改实例。**对象存储凭证必须嵌套 `storageConfigInfo` 字段**：
   - 顶层（`StorageInstanceConfigParam` 顶层）：`instanceName / storagePath / storageState / instanceType / httpHttps`
   - 嵌套（`StorageConfigInfo` 实体）：`bucket / region / accessId / accessKey / endPoint / rootPath / storageHost / pathStyle / cname / hdfsServerIp / hdfsServerPort / hdfsUserName / trackerServers / group / ...`
   - CLI 自动按字段名归类，调用方无需关心平铺/嵌套。**注意**：
     - 华为云 (`instanceType=3`) 的 `defaultField()` 不含 `REGION`（区域信息塞在 endPoint 里，形如 `obs.cn-north-4.myhuaweicloud.com`），后端 `getRequiredStorageConfigInfo` 会主动过滤掉 region，传了也白传。
     - 腾讯云/阿里云/华为云/S3 这四种"对象存储"的 `storagePath` 顶层字段**通常为空**（信息在 `bucket` 里），CLI 不校验。
   - **空壳实例 update 触发后端 NPE**：`StoInstanceDataServiceImpl.canProceed:269-271` 在 `db.configInfo` 为 NULL 时 NPE。
     这是 eteams-file 后端 bug，CLI 不自动修。**解法**：新建一个不同名字的实例（避开空壳），或让 DBA 在 db 里把空壳的 `config_info` 字段从 NULL 改成 `{}`，或走 E10 二开流程修 canProceed。
9. **license 检查** —— 没 `STORAGE_RULE` license 时 `ruleList` 走 `StoRuleFrontCompServiceImpl.java:317`
   直接返回空；CLI 会给 warning 但仍允许 POST（让后端真拒）。
10. **本地/远程分流（v0.2.0 新增，v0.4.16 保留）** —— CLI 按 `BASE_URL` 自动判断：
    - `127.0.0.1` / `localhost` / `0.0.0.0` / `127.*` → **local**：不自动 login、不自动 fetch 三件套；缺三件套直接报错并提示用户填到 `.env.local`
    - 其它 → **remote**：`login` 自动起专用 Chrome 让用户登录 + 抓三件套；业务调用时从 `.env.local` 读
    - `--local` 可显式强制标记
11. **papi URL 必须拼三件套（v0.4.16 重写）** —— 所有 papi 业务接口都要求：
    - URL query 拼 `token=<freepass token>` + `wea_link_keep_freepass=1` + `tenant_langType=zh_CN` + `randomkey_xxxx`（每次生成）
    - Cookie 设 `ETEAMSID` + `authToken`（JWT）
    - CLI 走 `_papi_qs(freepass_token, randomkey)` + `_session(eteams_id, auth_token)` 统一处理
    - **v0.4.16 之前 SKILL.md 写"拼 listPageToken.data.token"是错的**——listPageToken 是租户平台管理类接口用的；E10 后台业务接口用 freepass token
12. **系统级 vs 租户级分流（v0.3.0 新增，v0.4.16 改：两个 level 都走 papi）** —— CLI 按 `BASE_URL` 域名自动判断 level（system/tenant），但**两个 level 的业务接口都是 `/papi/file/...`**：
    - `<your-tenant-platform-domain>` → **system**（系统级 / papi / all_teams / 需 sysStorageRule=true）
    - `<your-e10-domain>` → **tenant**（E10 后台 / papi / 当前租户 / 需 sysStorageRule=false）—— **v0.4.16 改：之前误写"api/file/..."**
    - 其它 → 保守默认 `system`
    - `--level system|tenant` 可显式强制
13. **租户级不支持静态规则（v0.3.0 新增，v0.4.16 保留）** —— 后台管理中心只支持业务规则 + 默认规则；
    `--rule-type 1` 在 tenant 模式下 CLI 直接报"租户级没有静态规则"。
14. **agent 不得擅自新建 / 改 / 删数据绕开校验（v0.4.15 新加，客户纠错后固化）** ——
    客户回执"好的"**只代表同意本次确认的字段和值**,**不代表**同意 agent 擅自做超出范围的操作(新建 / 修改 / 删除任何数据、修改任何环境配置、调整任何不在确认清单里的字段)。
    - **典型违规场景**(v0.4.15 客户现场纠错):客户说"用默认存储实例" → 校验过不去 → agent 擅自新建一个存储实例(或新建一个测试实例)绕开校验 → **绝对禁止**
    - **正确做法**:
      1. **停下来**,直接告诉客户失败原因(校验过不去的具体异常信息)
      2. **列出 2-3 条可行路径**让客户选(换已有实例 / 客户在自己环境试 / 找二开修后端 bug),**不擅自造数据**
      3. **不**为"测试验证"而新建任何数据(包括"临时"实例、"测试"子规则);实在需要验证,优先用 mock / 静态分析 / HAR 抓包
    - **判断标准**:客户没明确说"建一个新的" / "新建一个绕开" 时,agent **不要**主动做"新建 / 改 / 删"任何数据
    - **覆盖范围**:
      - 存储实例(不能擅自 `instance add` 绕开 `validateStorageInstance` 等校验)
      - 子规则(不能擅自 `rule add` 试各种 source-type 找能过的)
      - 任何其它写操作(instanceType / configInfo / rule / 备份规则 / 附件设置 / 加解密设置 都受这条约束)
    - **例外**(agent 可以自动做的):**只读**操作(`list / show / test / search / explain`)+ **已经在客户确认清单里的写操作**(客户明确"好的" + 已经在确认对话里列出了完整 payload)
    - **如果客户**明确说"你帮我建一个试一下" / "新建一个本地存储实例来跑测试" / "建一个空壳的看看能不能触发"——才算"客户明确同意新建",但仍建议 agent 在执行前再**简短复述一下"我建一个 X 实例,只用于测试,完事我会删"** 让客户二次确认

## 对话式交互规则

> 这些是 **agent 在对话中使用本 skill 时**的硬约束，跟底层 CLI 脚本无关。命令行直接跑
> `storage` 可以绕过，但任何经由本 skill 的 agent 流程都必须遵守。

1. **支持自定义环境链接**
   - 用户在对话里直接给出 `https://...` 形式的 baseUrl，**按这个 URL 走**，
     **不要**要求用户去改 `.env.local` 或加新 config
   - 落地方式：临时 `export WEILE_<NAME>_BASE_URL=<url>`，或 CLI 加 `--base-url <url>`
   - 凭证沿用现有 config；若该 URL 下无凭证，按规则 2 触发登录流程
   - 同一会话内多次操作复用同一 baseUrl，不要每次都让用户重输
   - **如果用户在内置浏览器里已经登录了对应页面**，可以直接用同一个浏览器的
     `ETEAMSID`（通过内置浏览器 DevTools / `Application > Cookies` 抓到），写到
     `.env.local` 即可跳过 `storage login` 流程

2. **操作前必查登录态 + 三件套（v0.4.16 重写：之前 v0.2.0/v0.3.0 章节全错）**
   每次 `list / show / test / rule *` 之前先确认对应 config 的 **三件套齐**：`ETEAMSID` + `authToken` + `freepass_token`（在 `.env.local` 里看 `WEILE_<NAME>_ETEAMSID` / `WEILE_<NAME>_AUTH_TOKEN` / `WEILE_<NAME>_FREEPASS_TOKEN`），并按 level 选择登录入口：
   - **(0) 客户要求改存储时，先确认 level（v0.4.2 客户规则 1，v0.4.4 补"区别"说明）**：
     - **客户没明说必须主动问**，不能假设
     - **客户分不清 system/tenant 时（v0.4.4 新加）**，告知两者的区别：
       - **系统级**（租户平台 `tenant.*`）：改的是 `all_teams`，**影响所有租户**；改系统级业务规则 = 改所有租户业务文件最终落点
       - **租户级**（后台管理中心 `weapp.*`）：改的是**当前租户**；改租户级规则 = 单租户覆盖
       - **场景区别**：改系统级 = 给所有租户统一；改租户级 = 单个租户特殊化（例如某个租户量特别大要单独挂云存储）
       - **入口区别**：系统级 = 租户平台 `<your-tenant-platform-domain>/.../storageSet`；租户级 = E10 后台 `<your-e10-domain> → 文件设置 → 存储设置`
       - **v0.4.16 关键修正**：两个 level 的业务接口**都走 `/papi/file/...`**——之前 v0.3.0 写 tenant 走 `/api/...` 是错的（HAR 实证）
   - **(1) 系统级**（v0.4.2 客户规则 1，v0.4.16 改流程）：先确认客户已**登录租户平台**（`<your-tenant-platform-domain>`）；没登录就告知客户去登录或从浏览器 DevTools 拿三件套写到 `.env.local`
   - **(2) 租户级**（v0.4.2 客户规则 1，v0.4.16 改流程）：先确认客户已**登录 E10 后台**（`<your-e10-domain>`）；三种走法：
     - 优先触发独立登录 skill（如 `weaver-im login`）
     - 或弹登录框让客户登录
     - 或客户提供三件套（DevTools 抓 `ETEAMSID` + `authToken` cookie + 任意 papi URL 上的 `token` query 参数）写到 `.env.local`
   - **(3) 优先复用已有登录 skill** — 若系统已装独立的 Weaver 登录入口（如
     `weaver-im login`、`weaver-file-dev-flow` 的登录阶段、或其他第三方
     "weaver-login" skill），**先 `skill({name: "..."})` 加载它走它的登录流程**，
     拿到三件套落到 `WEILE_<NAME>_ETEAMSID` / `_AUTH_TOKEN` / `_FREEPASS_TOKEN` 后再继续
   - **(4) 复用内置浏览器** — 如果用户已在内置浏览器里登录了 weapp / tenant 域名，
     从浏览器 DevTools 拿 `ETEAMSID` + `authToken` cookie 值 + 任意 papi URL 上的 `token` 参数
     写到 `.env.local` 即可
   - **(5) 没有现成登录入口时** — 按 env_type 分流：
     - **远程**（baseUrl 不是 127.*/localhost/0.0.0.0）：回落到本 skill 自带的
       `storage login`，起专用 Chrome 弹登录页 + 让用户从租户平台点"进入 E10 后台文件存储设置"
       链接 → 跳到 `/sp/file/SysStorageSet/freepass?token=xxx` → 自动抓三件套全部落盘
     - **本地**（baseUrl 是 127.*/localhost/0.0.0.0）：**不自动起 Chrome**，
       直接提示用户在浏览器登录后从 DevTools 抓三件套复制到 `.env.local`：
       `WEILE_<NAME>_ETEAMSID` / `WEILE_<NAME>_AUTH_TOKEN` / `WEILE_<NAME>_FREEPASS_TOKEN`
   - **(6) 三件套齐全才发业务请求** — `Session.require_auth()` 会校验三件套；缺哪件报具体错误
   - **(7) 登录 / 三件套准备好后立即调 `storage list` 验证**，失败的话让客户重新登录 / 提供三件套

3. **查询要简洁**（`list / show / rule show` 时的输出格式）
   - **只返回三样**：**真实租户名**（v0.1.0 改的是系统级，不区分租户，可省）、
     设置项名（中文别名或 DTO 字段名）、当前值
   - **不要**返回：bool 三态展开、enum 解释、字段语义说明、风险提示、
     "建议/可以这么做" 等附加内容 —— 这些只在用户追问时再说
   - 多项查询时一行一项，格式固定：

     ```
     <租户名或「系统级」> · <设置项名>：<当前值>
     ```

4. **修改前必须三步问清**
   - 步骤 a — **改前的值**：说清楚这一项当前是什么（从 GET 里取，不要瞎猜）
   - 步骤 b — **改后影响**：说清楚改完会影响什么业务、放行/禁止哪些场景、
     触及哪些用户，以及是否会**间接影响其他字段**（如 `encrypted-storage=true`
     后 `sys-file-algorithm` 才生效；改默认规则会脱离系统默认）
   - 步骤 c — **明确询问**：用一句话问"要改成 X 吗？"，**得到用户肯定回复
     (y / 改 / 确认 / 好的 之类)才发 POST**，即使 CLI 已带 `--yes` 也不许跳过
   - 三步可以一次消息里说全，但步骤 c 的问句**必须独立成行**，不能藏在
     长段落里让人找不到

5. **话术面向客户（非开发）**
   本 skill 的对话对象是**客户/业务人员**，不是开发。所有输出话术：
   - **禁止出现**：CLI key（`rule-name`、`storage-instance` 等）、DTO 字段名
     （`ruleName`、`storageInstanceId` 等）、布尔字面值（`true` / `false`）、
     HTTP 术语（POST / GET / 200 / 401）、内部流程术语（"步骤 a / 步骤 b / 步骤 c"、
     "diff"、"回 y / 改"、"落库"）、内部命令（`storage rule set`、`--item`）
   - **必须使用**：业务中文名（"业务规则"、"默认规则"、"存储实例"、"子目录"）、
     业务状态（"已启用 / 已停用"）、自然语言确认（"要改吗？回 改 / 确认 / 好的"）
   - 需要看技术细节时（用户主动问"用的什么字段" / "接口是啥" / "为什么改不了"），
     **只在该轮回应**展开，平时一律隐藏
   - 身份信息隐藏 `userId` / `tenantKey` / `ETEAMSID` 这类内部 ID，只说"当前租户"
     或"系统级"
   - 可选自检：`python3 scripts/reply_lint.py --text '...'` 跑一遍话术合规

6. **做不到时正确引导**
   客户要改的项**当前工具/接口改不了**时，**不要**静默截断、**不要**发注定失败
   的请求。常见场景：
   - **租户平台实例是系统级只读**：客户说"我想新建一个本地存储实例" →
     CLI 没法做。引导客户去 E10 后台"系统级存储 → 新建"，在那边建完再来
     改业务规则里选这个新实例
   - **license 没开**：租户没 `STORAGE_RULE` license 时 `ruleList` 返回空，
     改规则会失败。引导客户找管理员开 license
   - **三件套拿不到**（v0.4.16 重写）：远程环境 `storage login` 失败时，引导客户
     `storage login --config <name>` 重新登录；或手动从浏览器 DevTools 抓三件套
     写到 `WEILE_<NAME>_ETEAMSID` + `WEILE_<NAME>_AUTH_TOKEN` + `WEILE_<NAME>_FREEPASS_TOKEN`
     —— 注意 v0.4.16 改：token 来自 freepass 入口 URL（`/sp/file/SysStorageSet/freepass?token=xxx`），
     不是 listPageToken 响应
   - **字段间依赖**：
     - `encrypted-storage=true` 但 `sys-file-algorithm` 为空 → CLI 自动填 `SM4`（门禁）
     - 业务规则下 `sub-directory-type=4`（按部门）但没分部 license → 后端会拒
     - 静态规则 `static-nginx-config` 改完还要"同步到 nginx 服务器"才能生效
       → 引导客户去 E10 后台"系统级存储 → 静态文件规则"点"同步"按钮
   - **改默认规则的副作用**：脱离系统默认（前端弹窗原话），要回退用
     `storage rule reset-default`
   - **后端返回致命错误**（已知）：不重试，直接告诉客户失败原因 + 正确路径
   - 话术模板：
     "这里改不了：<原因>。需要去<正确路径>那里先做<前置操作>。
      在那边保存后，回到这里再让我帮你改存储设置里的对应项，
      就能改到你想要的值了。"

7. **改存储规则前：先列当前所有项 + 逐项说明，按 level 分流（v0.4.2 客户规则 2，v0.4.4 补租户级，v0.4.14 补新建子规则）**
   改存储规则时按 level 走不同流程，**都先列当前所有项再问客户改哪些**：

   **A. 系统级**（租户平台）：
   - 调 `storage rule show --default` 拉出"**业务文件存储规则**" + "**静态文件存储规则**"两套全部当前值
   - 把每一项用**业务中文名**列出来（参考 `setting-storage-docs-summary.md` 第 1 节"7 个标识目录"和 `setting-storage-field-map.md` 13 个字段），并**逐项说明这一项是控制什么的**（业务含义 + 改了会影响哪些业务）
   - **只**改客户说想改的项；其它项保持原值（门禁 7：未指定子字段保留）
   - 不要在列出当前值的同时"顺便"推荐改某项；客户没问就不主动建议

   **B. 租户级**（E10 后台管理中心，v0.4.4 客户规则 2 重点）：
   - 调 `storage rule show --default` 拉**当前租户的默认存储规则**详细信息（含里面挂的存储实例的【名称 / 类型 / 启用状态】）
   - 调 `storage rule list` 拉**当前租户的所有存储子规则**（`--name` 可选模糊），**每条规则都要给客户展示完整详情**：
     - 规则名称 / 启用状态 / 文件来源 / 子目录类型
     - **这条规则挂的存储实例的【名称 / 类型 / 启用状态】**（客户要知道这条规则最终落到哪个实例）
   - 然后告诉客户"默认规则 + N 条子规则"的全景，问要改哪条
   - 改的是"默认规则" → 调 `storage rule set --default --item ...`
   - 改的是"子规则 id=N" → 调 `storage rule set --id N --item ...`
   - **绝不**只看默认规则就跳过子规则——子规则可能"挂的实例"跟默认规则完全不一样（按文件来源分部）

   **C. 租户级 新建子规则**（v0.4.14 新加，v0.4.15 字段含义 + 保存关系搞清楚后固化，v0.4.15 第二次修：客户截图实证"选了本地存储就显示压缩/加密"——前端不是固定 6 字段，是按存储实例类型动态显示）：
   - **走 `storage rule add` CLI**（不是 `rule set`），走 `POST /api/file/storage/rule/saveData` ADD 路径——传 `ruleInfoList` 含 1 条**不带 id** 的 `StoRuleInfo`
   - **前端"新建存储规则"页面字段是动态的，按"存储实例"类型切换**（v0.4.15 客户截图 + 第二次纠错，`useRuleDetail.tsx:557-566` `onFormChange` 里 `formStore.setHide(filedKey, isNotLocal)` 决定显隐）：
     - **基础 6 字段（无论选什么存储实例都显示）**：
       - 规则名
       - 文件来源（前端只让用户选"模块 / 文件夹"两种——分部/部门被前端 `fileSourceTypeOptions` 注释掉，见 `constants.tsx:221-226`）
       - 存储实例
       - 存储路径
       - 子目录
       - 启用
     - **本地存储 专属字段**（选了本地存储才出现）：
       - **压缩存储**（`compressedStorage` Switch 开关）
       - **加密存储**（`encryptedStorage` Switch 开关）
       - **加密算法**（`sysFileAlgorithm`，开了"加密存储"才出现，是个 Icon 按钮点开弹窗选，默认 `SM4`，可选 `AES-256`）
     - **非本地存储（腾讯 / 阿里 / 华为 / S3 / FastDFS / HDFS）**：基础 6 字段，**不**显示压缩/加密/算法（云存储不需要）
   - **前端动态显隐逻辑**（`useRuleDetail.tsx:558-566`）：
     ```ts
     if ('storageInstance' in value) {
         const instanceType = value.storageInstance[0]?.instanceType;
         const isNotLocal = instanceType !== InstanceType.LOCAL;
         // 存储路径,子目录,压缩存储,加密存储 在非本地存储下需要隐藏
         ['compressedStorage', 'encryptedStorage'].forEach(filedKey => formStore.setHide(filedKey, isNotLocal))
         // 本地存储 且还没选择子目录时 子目录页默认更新为 "按【天】生成子目录"
         if (!formStore.getFormDatas()?.subDirectoryType && !isNotLocal) {
             formStore.updateDatas({subDirectoryType: '2'});
         }
     }
     ```
   - **v0.4.15 第一次改错了：以为"租户级子规则 = 6 字段固定"，是看客户截图"还没选存储实例"时的状态得出的**——客户第二次纠错明确：选了本地存储就有压缩/加密/算法 3 个。**正确认知**：基础 6 + 选了本地再加 2-3 个 = 6~9 字段之间
   - **`fileSourceType` 实际值是 1/2/3/4**（v0.4.15 修 v0.4.14 错误：v0.4.14 SKILL.md 写 0/1/2/3，但后端 `FileSourceTypeEnum` 真实值是 1=模块 2=文件夹 3=分部 4=部门 -1=默认）：
     - `fileSourceType=1`（模块）：`fileSourceValue` = **moduleFlag 英文**（如 `"document"`），不是模块中文名"文档"——后端 `searchModuleStrToEntry` 用它去 `fileModuleBrowser.getModuleMap()` 里查，找不到就 `filter(Objects::nonNull)` 静默丢弃
     - `fileSourceType=2`（文件夹）：`fileSourceValue` = **文档中心目录 id**（数字字符串，多个用逗号分隔）
     - `fileSourceType=3`（分部）：`fileSourceValue` = **分部 id**（数字）
     - `fileSourceType=4`（部门）：`fileSourceValue` = **部门 id**（数字）
   - **`fileSourceValue` 怎么传值**（v0.4.15 关键认知，前端 + 后端双向验证）：
     - **前端 Browser(type=module)** 调 `/api/file/common/browser/complete/module` 拿 `Map<moduleFlag, moduleName>`，每条 module 包装成 `{id: moduleFlag, title: moduleFlag, content: moduleName}`（HAR 实测确认）
     - 前端保存时 `useRuleDetail.tsx:346` `(fileSource || []).map((item: any) => item.id).join(',')` —— **`item.id` = moduleFlag 英文**，不是中文 moduleName
     - **后端 `saveGeneralRule` → `splitFileSourceValue` → case MODULE**（`StoRuleServiceImpl.java:1146-1153`）：`searchModuleStrToEntry(fileSourceValue)` 在 `getModuleMap()` 里查，**找到就 `setFileSourceStr(moduleFlag)` 入库，找不到就 filter 掉（静默丢弃）**
     - **反推**：传中文 moduleName（如"文档"）→ `getModuleMap()` 找不到 → 被 filter 掉 → 看似保存成功但 `fileSourceValue` 入库为空（v0.4.14 已踩此坑）
   - **给必填值的话术**（v0.4.15 修正版 + 本地存储专属字段）：
     - 基础 6 字段：规则名 / 文件来源 / 存储实例 / 存储路径 / 子目录 / 启用
     - **如果选本地存储**：追加问"压缩存储"开不开（默认关）+ "加密存储"开不开（默认关）+ 开了加密就问"加密算法"（默认 `SM4`，可选 `AES-256`）
     - **如果选云存储**：不追问压缩/加密/算法
   - **模块对应关系速查表**（v0.4.15 HAR 实测当前租户 license，常见模块，跨租户可能有出入）：

     | 业务中文名 | moduleFlag(英文) |
     |---|---|
     | 知识管理（"文档"） | `document` |
     | 公文管理 | `odoc` |
     | 流程 | `workflow` |
     | 邮件 | `email` |
     | 项目 | `project` |
     | 协作 | `cowork` |
     | 日程 | `calendar` |

     完整列表调 `/api/file/common/browser/complete/module` 拉（HAR 实测当前租户 197 个 moduleFlag）。**未知模块让客户用前端 Browser 选好后告诉我 moduleFlag 英文**——前端选择器会同时显示 moduleFlag 和 moduleName，agent 没法直接替客户选（需要 Browser 操作）。

8. **改/选存储实例时：先列已有 + 让客户选（v0.4.2 客户规则 3）**
   改规则的"存储实例"字段 / 改"业务文件要落到哪个实例"时：
   - **先调 `storage list` 列出所有已有存储实例**，每个实例给出 **三要素**：**名称 / 类型（本地/腾讯/阿里/华为/S3/FastDFS/HDFS）/ 启用状态**
   - **问客户"选已有实例 / 新建一个"**——不要直接跳到"新建"；新建是高成本操作，能复用就先复用
   - 客户说"选已有" → 调 `storage show <id>` 把详情给客户确认，再调 `rule set --item storage-instance=<id>`
   - 客户说"新建" → 走规则 9

9. **新建存储实例：列支持类型 + 按 defaultField 给必填值 + 测试先于保存（v0.4.2 客户规则 4 + 5，v0.4.13 精准化）**
   新建存储实例必须按这个三步走，**不能跳步也不能漏字段**：

   - **步骤 a — 列支持类型**：先把 7 种支持的存储类型告诉客户（本地 / 腾讯云 / 阿里云 / 华为云 / S3 / FastDFS / HDFS），让客户选要新建哪种
   - **步骤 b — 按 defaultField 给必填值（v0.4.13 客户反馈关键修正）**：
     - 客户选好类型后，**按 `setting-storage-storage-types.md` 列出的该类型 defaultField 给字段**——**不能给页面上没有的字段**(v0.4.2 误给阿里云"二级路径"客户截图明确标红)
     - **每种类型的字段都不一样**：
       - 本地:实例名 + 存储路径
       - 腾讯云:实例名 + 协议 + 终端节点 + 区域 + 桶 + 访问 id/key(共 7 项,含独立"区域"字段)
       - 阿里云:实例名 + 协议 + 终端节点 + 桶 + 访问 id/key + CNAME(**没"区域"独立字段,没"二级路径"**)
       - 华为云:实例名 + 协议 + 终端节点 + 桶 + 访问 id/key + 二级路径(可选)(**没"区域"独立字段**)
       - S3:实例名 + 协议 + 终端节点 + S3 host + 区域 + 桶 + 访问 id/key + PathStyle + 二级路径(可选)
       - FastDFS:实例名 + trackerServers + downLoadHost(**没终端节点/桶/凭证**)
       - HDFS:实例名 + hdfsServerIp + hdfsServerPort + 存储路径 + hdfsUserName(**没终端节点/桶/凭证**)
     - **终端节点(END_POINT) 是个组合控件(v0.4.13 客户反馈关键认知)**：左侧是**协议下拉**(`http://` / `https://`),右侧是**域名文本框**。**协议走 `httpHttps` 顶层字段 + 域名走 `endPoint` 嵌套字段**——不能拼成一个字符串
     - 凭证（访问 id / 访问 key）不复读到对话里，收到后只说"已收到"
   - **步骤 c — 测试先于保存（v0.4.2 客户规则 5，v0.4.13 强制）**：
     - 客户填好后，**agent 必须立刻调 `storage test-create` 测试连通性**(不调 `instance add`)
     - 测试通过 → 才调 `storage instance add` 保存
     - 测试不通过 → **绝不保存**，根据后端返回的异常告诉客户原因 + 怎么改（例如：桶不存在 → 检查桶名；访问 key 错 → 检查凭证；端点拼错 → 检查协议和域名）
     - **测试 CLI**: `storage test-create` 走 `testConnect` 不传 id,跟 `instance add` 拆开,严格"先测后存"
     - **绝对不能**问"要存吗"再保存——客户给完整信息后**agent 必须先测试**,告诉客户测试结果,客户说"存"才存
   - **注意**：步骤 c 的"测试"是后端 `testConnect` 走真实凭证 + 真实桶的真实请求，比"保存后再看"靠谱得多

10. **查询"现在系统是什么存储"时：综合三处 + 去重 + 业务信息 + 无 ID（v0.4.5 新加，v0.4.6 客户视角优化）**
    客户问"现在系统是什么存储"/"现在业务文件存哪了"/"现在用的哪套存储"等**纯查询场景**（不是要改），必须**综合查三处**再综合回答：

    - **A. 查系统级业务文件存储规则** → `storage rule show --level system --default` 拿"业务文件最终落点"（含挂的存储实例 + 子目录规则 + 存储路径）
    - **B. 查系统级静态文件存储规则** → 走 `getStorageInstance` 拿"静态资源最终落点的存储实例详情"（含存储路径/桶/端点等）
    - **C. 查当前租户的存储信息** → `storage rule show --level tenant --default` 拿"租户级默认规则挂的实例"

    **输出格式硬约束（v0.4.6 客户原话）**：
    - **禁止出现 ID**：任何 instance.id / rule.id / usageType 等**纯内部状态字段都不能出现**——这些是开发用字段，不是客户要的"现在用什么"
    - **必须包含业务信息**：每个落点要包含 **存储类型 / 实例名 / 桶名(对象存储) / 区域 / 终端节点 / 存储路径(本地) / 子目录规则**——客户问"现在用什么"就是要这些业务信息，不要只回个名字
    - **分段写但不用编号**：业务文件 / 静态文件 / 租户是否覆盖三段分开写，每段一段自然语言
    - **去重规则**：C 跟 A/B 一致时，**不单独列 C 那一行**——客户问的是"系统是什么存储"，租户级跟系统级一致时只说一次

    **标准输出模板（v0.4.6 → v0.4.7 → v0.4.8 → v0.4.9 → v0.4.10 → v0.4.11 markdown bullet 强制换行）**：
    ```markdown
    当前系统存储概况:

    - 业务文件(租户业务 / 系统公共 / 临时文件)
      - 存储类型:<腾讯云存储/阿里云存储/...>
      - 存储实例:<实例名>
      - 桶:<桶名>             ← 对象存储才有
      - 区域:<区域>            ← 华为云在终端节点里,可不填
      - 终端节点:<终端节点>     ← 对象存储才有
      - 子目录规则:按【...】自动生成(YYYY/MM/DD)

    - 静态文件
      - 存储类型:<本地存储/...>
      - 存储实例:<实例名>
      - 存储路径:<路径>        ← 本地存储才有

    - 当前租户
      - <没有单独覆盖,跟系统级一致>  ← 跟 A/B 一致时
      - <单独挂的:<类型> - <实例名>...>  ← 跟 A/B 不一致时
    ```
    - **格式说明(v0.4.11 关键修复)**：**用 markdown `-` bullet 强制每项独立成行**——所有现代 chat 客户端都会把 `- ` 开头识别为列表项,**强制独占一行**,不会被"压缩单换行"合并
    - 顶层 3 段(业务/静态/租户)用 `-`(顶格 bullet)
    - 段内每个属性用 `  - `(2 空格缩进 bullet)
    - 段间用**单空行**分隔
    - 桶 / 区域 / 终端节点这三项仅在"对象存储(腾讯/阿里/华为/S3)"时才有,本地存储写"存储路径"即可
    - 区域对华为云可不填（信息在终端节点里,见 v0.4.2 硬性门禁 8）
    - 客户问"列出来本地环境的存储信息"实际就是"现在用什么"——不要把全部 21 个实例平铺出来,只讲"正在用的"
    - **反例**(v0.4.6 客户截图标红的错误):表格里出现 id / usageType 列;正文里出现 `storage show <id>` 命令;罗列所有 21+15 个实例——这些都是开发视角,不是客户视角
    - **反例**(v0.4.7 客户反馈):v0.4.6 用"长段落"写法(214 字符挤成 4 段),客户希望**每个属性独立成行**
    - **反例**(v0.4.8 客户反馈):v0.4.7 用"2 空格缩进"写法,客户希望**无缩进直接 key:value**(类似 `存储类型:` 这种示例),让每行更扁更易扫
    - **反例**(v0.4.9 客户反馈):v0.4.8 用"业务文件: / 静态文件: / 当前租户:"这种冒号分段,客户希望用 `###` 三级标题让 3 段更醒目
    - **反例**(v0.4.10 客户反馈):v0.4.9 用 `###` 三级标题 markdown,**某些客户端不渲染 markdown 标题**;v0.4.10 改纯换行,但**chat 客户端会压缩单换行成空格**,多个 key:value 还是挤在一行
    - **反例**(v0.4.11 客户反馈):v0.4.10 纯换行在 chat 客户端被压成空格,key:value 还是挤一行。v0.4.11 用 markdown `-` bullet——列表项在所有 chat 客户端都**强制独占一行**,不会被压缩

## 宿主

CLI 入口：

```text
python3 scripts/setting_storage.py <cmd> [args]
```


## 与 weaver-setting 系列其它 skill 的关系

四个 skill **互相独立**，可在同一台机器共存：

| | weaver-setting-attach | weaver-setting-encrypt | weaver-setting-backup | weaver-setting-storage |
|---|---|---|---|---|
| 改的页面 | 文件设置 → 附件设置 | 文件设置 → 加解密设置 | 文件设置 → 备份设置 | 租户平台 → 文件存储设置 |
| 入口域名 | <your-e10-domain> | <your-e10-domain> | <your-e10-domain> | **<your-tenant-platform-domain>** |
| 接口前缀 | api | api | api | **papi** |
| 作用范围 | 租户 | 租户 | 租户 | **系统级（all_teams）** |
| CLI 软链 | `setting-attach` | `setting-encrypt` | `setting-backup` | **`storage`** |
| 共享 | 互相独立 `.env.local`；可共享同一 ETEAMSID（同 SSO 域） |

## 版本

- **0.4.16**（2026-08-17）**auth 模型全错重写（基于客户 2026-08-17 发的两个 HAR 文件实证）**。修正：
  - **之前 v0.2.0 章节 3 错了**：真实业务接口 URL 拼的 `token=` 不是 listPageToken.data.token，是 freepass token（来自 `/sp/file/SysStorageSet/freepass?token=xxx` 入口）
  - **之前 v0.3.0 章节错了**：租户级实际是 `/papi/file/...`，不是 `/api/file/...`（HAR 里一个 `/api/` 都没有）
  - **之前章节 2 错了**：只抓 ETEAMSID 不够，真实要三件套 `ETEAMSID` + `authToken`（JWT cookie）+ `freepass token`（URL 参数）
  - **之前章节 11 错了**：业务接口还多一个 `randomkey_xxxx`（CSRF 防护，每次请求生成一对）
  - 新 env vars：`WEILE_<NAME>_AUTH_TOKEN` + `WEILE_<NAME>_FREEPASS_TOKEN`（之前 `WEILE_<NAME>_TOKEN` 已废弃）
  - 删 `fetch_page_token` / `_papi_qs(token)` 的旧用法；加 `generate_randomkey()` 和 `fetch_auth_cookies()`
  - `Session.require_auth()` 三件套校验；`require_token()` 兼容只校验 freepass
  - `cmd_login` 重写：让用户从租户平台点链接到 E10 后台再抓三件套
  - 所有 storage_api 函数加 `auth_token` / `freepass_token` 参数（替换 `token`）
  - `auth-flow.md` 完整记录 HAR 实证 + 5 处旧文档错误 + 修方向
  - 现有客户已建的 `webapp` config 需要重新 `storage login` 拿新三件套
- **0.4.15**（2026-08-10）**修子规则字段含义 + fileSourceType 取值 + 本地存储显示压缩/加密/算法**。
- **0.4.14**（2026-08-09）**新建/删除子规则**。
- **0.4.13**（2026-08-09）**7 种存储类型 defaultField 精准化**。
- **0.4.12**（2026-08-09）**完整话术模板库**。
- **0.4.11**（2026-08-09）**对话式输出格式 markdown bullet 强制换行**。
- **0.4.2**（2026-08-08）**对象存储凭证字段路由**（凭证必须嵌套 `storageConfigInfo`）。
- **0.4.0**（2026-08-08）**开放实例写操作**（`instance add / delete`）。
- **0.3.0**（2026-08-09）**租户级接入**（**v0.4.16 改：当时写的 `/api/file/storage/...` 是错的，实际是 `/papi/file/...`**）。
- **0.2.0**（2026-08-09）**鉴权补全**（**v0.4.16 改：当时写的 listPageToken 自动获取 + URL 拼 token 模型是错的，真实是 freepass token**）。
- **0.1.0**（2026-08-06）首次创建。覆盖租户平台（papi / all_teams）「存储实例 +
  存储规则」的系统级查看 + 规则改写。13 个 rule 子字段全部走 CLI 别名 + 中文 + DTO 驼峰三套。

版本号规则 `x.y.z`：
- **x 升** — 大重构（GET/POST 模式变化、DTO 结构变化、字段大幅增删）
- **y 升** — 新增字段、新增命令、新增子模块
- **z 升** — 文案修正、门禁澄清、依赖注补充、不改行为的小修

## 计划中的下一版

- **0.5.0** —— 批量启停规则（`rule open --batch --ids 1,2,3 --on`）
- **0.6.0** —— 规则按"文件来源"browser 化（用 `list_storage_instance_options`
  + 后端的 `FileModuleBrowser` 给出可选 id 列表，agent 直接对话式问"我帮
  你选了文件来源 X，要不要确认？"）
# 接口协议

v0.1.0 范围：仅**租户平台 / 系统级**（papi + `all_teams`）。weapp 后台的租户级设置走 v0.2.0。

## 端点

### 存储实例

| 操作 | 方法 | URL | 入参 | 出参（data 字段） |
|---|---|---|---|---|
| 列实例 | `POST` | `{base}/papi/file/storage/listStorageInstance` | `{pageNo, pageSize}` | `{columns, operates, data[], total, current}` |
| 单实例详情 | `POST` | `{base}/papi/file/storage/getStorageInstance` | `{id, instanceType?}` | `{weaForm, encFieldList, readOnly}` |
| 保存实例 | `POST` | `{base}/papi/file/storage/saveStorageInstance` | `StorageInstanceConfigParam` | `{code, msg}` |
| 测试连接 | `POST` | `{base}/papi/file/storage/testConnect` | `StorageConfigParam + StorageConfigInfo` | `true / false` |

### 存储规则

| 操作 | 方法 | URL | 入参 | 出参 |
|---|---|---|---|---|
| 拉规则表单 | `GET` | `{base}/papi/file/storage/rule/frontComp/ruleForm?defaultRule=true&id=N&sysStorageRule=true` | query | `{defaultFsRuleWeaForm, fsRuleWeaForm, defaultStaticRuleWeaForm, ...}` |
| 保存规则 | `POST` | `{base}/papi/file/storage/rule/saveData` | `{defaultRule, ruleInfoList[]}` | `{ruleInfoList[]}` |
| 改顺序 | `POST` | `{base}/papi/file/storage/rule/saveOrder` | `{ruleIdList[]}` | `{}` |
| 改启用 | `POST` | `{base}/papi/file/storage/rule/saveOpen` | `{ruleInfoList[]}` | `{}` |
| 删除 | `POST` | `{base}/papi/file/storage/rule/delete` | `{ruleIdList[]}` | `{}` |
| 高级搜索 | `POST` | `{base}/papi/file/storage/rule/search` | `{conditionArr[], ruleType?}` | `{ruleInfoList[]}` |
| 拉规则表 | `GET` | `{base}/papi/file/storage/rule/frontComp/ruleTable` | （无） | `{defaultFsRuleWeaForm, fsRuleTable, ...}` |

### 浏览器辅助

| 操作 | 方法 | URL | 入参 | 出参 |
|---|---|---|---|---|
| 选存储实例（browser） | `POST` | `{base}/papi/file/common/browser/associate/storageInstance` | `{browserMultiple, token, pageNo, pageSize, instanceType?}` | browser rows |

## 鉴权

```
Cookie: ETEAMSID=<id>
```

papi 端点都带 `?wea_link_keep_freepass=1&tenant_langType=zh_CN` 通用 query（browser 端点额外要 `token`）。

## POST 注意事项

1. **租户平台实例是「系统级只读」**：v0.1.0 CLI **不开放** `saveStorageInstance` 写操作；
   `StorageConfigController.java:84` 写操作走 `StorageConfigManagerImpl.saveStorageInstance`，
   `StorageConfigInfo` 字段值是租户级 / 系统级混合的；租户平台只该有读权限
2. **业务规则 vs 静态规则同时改**：调用 `rule/saveData` 时 `defaultRule=true` 会触发
   `StoRuleServiceImpl.java:140-170` 的 saveDefaultRule / saveStaticDefaultRule，
   一次请求可同时改两条（业务 + 静态），按 `ruleType` 字段路由
3. **`staticNginxConfig` 是嵌套 JSON 子字段**：存在 `StoRuleInfo.expandRuleConfig`（JSON 字符串）里；
   改 nginx 配置 → CLI 走子字段 merge，不能整段覆盖
4. **改默认规则会脱离系统默认**：见 `useRuleDetail.tsx:374` 前端弹窗原话
   "修改后将不再继承系统初始化的默认存储实例"
5. **保存后要 GET 校验**：`StoRuleServiceImpl.saveRule` 不回显完整对象，只回 `ruleInfoList`；
   CLI 改完要 `GET ruleForm` 重新拉一遍
6. **`canSelect=false` 的实例不可选**：前端会显示 tooltip "系统级存储实例，不允许修改"；
   CLI 改规则时如果 `storage-instance` 选了这类实例会被前端拒（实际后端按 usageType 过滤）

## 后端实现位置

- Controller（租户平台）：
  - `eteams-file/src/main/java/com/weaver/teams/file/e10/mvc/web/storageconfig/PublicStorageConfigController.java`
  - `eteams-file/src/main/java/com/weaver/teams/file/e10/mvc/web/storagerule/PublicStoRuleController.java`
  - `eteams-file/src/main/java/com/weaver/teams/file/e10/mvc/web/storagerule/PublicStoRuleFrontCompController.java`
- Service：`eteams-file/src/main/java/com/weaver/teams/file/e10/service/web/storagerule/impl/StoRuleServiceImpl.java`
  - `StoRuleFrontCompServiceImpl.java`（表单渲染）
- DTO：
  - `eteams-file/src/main/java/com/weaver/teams/file/e10/param/StorageInstanceConfigParam.java`
  - `eteams-file/src/main/java/com/weaver/teams/file/e10/entity/storagerule/StoRuleParam.java`（含 `StoRuleInfo`）
- 枚举：
  - `eteams-file-client/src/main/java/com/weaver/eteams/file/client/file/enums/storage/StoInstanceTypeEnum.java`（7 种存储类型）
  - `eteams-storage/src/main/java/com/weaver/teams/storage/constant/FileStorage.java`（运行时实例）
- 实体：
  - `eteams-storage/src/main/java/com/weaver/teams/storage/entity/StorageConfigInfo.java`（每种存储类型的字段集）
- 前端：
  - `weapp-file/src/components/pc/FileSet/components/StorageSet/index.tsx`
  - `weapp-file/src/components/pc/FileSet/components/StorageSet/StorageInstance.tsx`（实例）
  - `weapp-file/src/components/pc/FileSet/components/StorageSet/StorageRules.tsx`（规则列表）
  - `weapp-file/src/components/pc/FileSet/components/StorageSet/hooks/useInstanceDetail.tsx`（实例编辑弹窗）
  - `weapp-file/src/components/pc/FileSet/components/StorageSet/hooks/useRuleDetail.tsx`（规则编辑弹窗）
