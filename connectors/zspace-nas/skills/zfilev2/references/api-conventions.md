# 极空间接口约定速查（跨服务通用）

> 本文件由 `scripts/gen-skills.mjs` 复制到 `skills/zfilev2/references/`，供各服务 Skill 引用。

## 响应外层

- 统一 `{code, msg, ts, data}`；成功 `code == "200"`（**字符串**，连接器同时兼容数字 200）。
- 例外：
  - `file_search` 出错时 `code` 是**数字**（2=参数错误、8=搜索失败、9=结果失败）；
  - `appstore` 的 `open/*` 返回 `{code:200, msg, data, time}`（数字），未安装应用返回 `code:400`；
  - `zfilev2` 额外带 `reason`/`suggest` 字段。
- 常见 NAS 错误码：

| code | 含义 |
|---|---|
| N001208 | 令牌失效 |
| N001212 | 参数有误 |
| N001315 | 文件/目录不存在 |
| N001320 | 父目录不存在（写入/上传） |
| N001391 | 相册不存在 |
| N001411 | 无权限 |
| N001414 | 新设备登录需短信验证（仅授权流程） |
| N007008 | 目标文件夹不存在（move/copy） |

## 分页家族（各服务不一致，连接器已适配）

| 家族 | 服务 | 参数 |
|---|---|---|
| `start` + `num` | zfilev2、zalbumv2、zspoolv3、zcomic、pluginbackup | `start` 从 0 开始 |
| `start` + `size` | downloader、ftprsync | — |
| `page` + `page_size` | zmusicv2、zreader、zaudio、media_converter、mailmanager | **1-based** |
| `start` + `limit` | zvideo_v2 | `start` 为 **1-based 页码** |
| `StartIndex` + `Limit` | zvideo_v2 的 Emby 面 | 连接器未使用该面 |

## 连接器输出整形

列表类载荷被整形为 `{<原键>: [...], total, truncated?, next_start?}`：

- `total` 优先取 NAS 自报的 `total`/`count`，否则为数组长度；
- 超过硬上限（目录 2000 / 搜索 500 / 相册 500 / 日志 200 / 媒体 200）时 `truncated:true` 并给出 `next_start`；
- 非列表载荷原样返回。

## 鉴权

- 网关（openresty `:5055`）校验 Cookie `token`；`OA.` 前缀的 OAuth 令牌需要 NAS 侧补丁（见 `nas-patches/README.md`）。
- LAN 直连：`Cookie: token=<AT>;plat=<plat>;device=workbuddy-connector`。
- 云端（`oauth.zconnect.cn` 网关）：`Authorization: Bearer <AT>` + `nas-id` + `remote-port: 5055`；上传/下载额外带 `request-purpose`（`file_upload` / `file_download`）以命中 3MB/s 限速桶。
- 经云端转发时空 body 的 POST 会挂起 → 连接器自动附加无害参数 `_wb=1`。
- **`/local/*` 不可达**：网关对 `location /local/` 配了 `allow 127.0.0.1; deny all;`。所有内部路由（如 zfilev2 的 `/local/v2/file/share/create`、`/local/v2/file/labels/add`）连接器一律不可用，必须走对外路由。

## 路径映射

| 前缀 | 含义 | 权限 |
|---|---|---|
| `/sata11/my/data/...`（盘位名因设备而异） | 个人空间 | 读写 |
| `/public/...` | 公共空间 | 按账号配置 |
| `/share/...` | 他人分享给我（共享空间） | 通常只读 |
| `/extdev/...` | 外接设备（eSATA/USB/网盘挂载） | 读写 |
| `/.recycle/my` | 回收站 | 恢复/清空 |

## 连接器自定义错误码

| code | 含义 | 处理 |
|---|---|---|
| `E_AUTH_EXPIRED` | 授权失效且自动续期失败 | 重新「连接」授权 |
| `E_FIRMWARE_TOO_OLD` | 固件不支持 OAuth 令牌 | 升级固件 |
| `E_APP_NOT_INSTALLED` | 依赖的应用未安装 | 到 NAS 应用商店安装后 `app_status {refresh:true}` 复检 |
| `E_PARAM` | 参数校验失败 | 按提示修正 |
| `E_FORBIDDEN` | 命中禁用路径（内部路由/高危运维） | 不要重试 |
| `E_NOT_ALLOWED` | 只读白名单外的兜底查询 | 改用专用工具 |
| `E_OFFSET_MISMATCH` | 续传 offset 与本地文件不符 | 用 `offset=0` |
| `E_UPLOAD` / `E_DOWNLOAD` | 上传/下载失败 | 可重试（上传会续传） |

## 明确禁用（硬黑名单，任何工具都不可达）

重启/关机、存储池格式化与重置、RAID 重建、磁盘移除、外接盘擦除、快照回滚、
网络接口改配（`/v1/interface/update`、`/v1/bond/*`、`/v1/bridge/*`）、
防火墙规则下发（`apply`/`enable`）、应用安装卸载、虚拟机开关机、iSCSI 配置变更、
`/local/*` 内部路由、各类 `pprof` 调试开关、`/pluginbackup/local/...` 未鉴权删除接口。
