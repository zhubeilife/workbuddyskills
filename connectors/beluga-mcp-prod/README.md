# Beluga MCP（生产）连接器包

连接 Beluga 生产环境 MCP 网关:`https://beluga-server-cn.heytapmobi.com/beluga-mcp/gateway`

## 包结构

```
beluga-prod/
├── connector-meta.json     # 连接器元数据(名称/描述/示例指令)
├── mcp.json                # MCP Server 配置(streamableHttp)
├── icon.svg                # 连接器图标
├── connect.py              # 一键接入脚本(推荐用户使用)
├── token_<name>.json       # 接入后自动生成的令牌缓存(含 refresh_token,勿外传)
├── client_<name>.json      # 接入后自动生成的客户端注册信息
└── skills/beluga/SKILL.md  # Agent 使用说明(接入方式 + 工具清单 + 调用约定)
```

## 用户接入(三步)

```bash
python connect.py     # 1. 运行脚本,浏览器自动弹出 → 登录 Beluga 账号并授权
                      # 2. 脚本自动换取令牌并写入 ~/.workbuddy/mcp.json
                      # 3. 回到 WorkBuddy「插件 → MCP 服务器」点击「信任/重连」
```

日常维护:

- `python connect.py --check` — 验证连接并列出可用工具
- `python connect.py --refresh` — 令牌过期(默认 30 天)后静默续期,无需重新登录

## 关于 connect.py（2026-10-09 更新）

**服务端限制已解除**：经实测，Beluga OAuth 的动态客户端注册（RFC 7591）
现已接受 WorkBuddy 原生自定义协议回调
`workbuddy://workbuddy/mcp/connector%3A<source>/oauth/callback`
（HTTP 201 注册成功并回显 redirect_uris），授权端点同样接受，
且对未注册回调仍严格校验（400 拦截）。

**因此用户现在可直接在 WorkBuddy「插件 → MCP 服务器」添加本连接器，
走原生授权（点「信任」）即可完成接入，无需运行 connect.py。**

connect.py 保留作为备用/调试工具：

- `python connect.py --check` — 验证连接并列出可用工具
- `python connect.py --refresh` — 令牌过期后静默续期（依赖 client_*.json）
- `python connect.py` — 手动完整授权（标准 MCP OAuth 2.1 流程，PKCE +
  loopback http 回调），对其他有同类限制的 MCP 网关也可复用
  （通过 `--url` / `--name` 参数）

## 安全说明

- `token_*.json` 含 access_token 与 refresh_token,等同账号凭据,
  请勿提交到版本库或随包分发。
- 打包发布前请删除本机生成的 `token_*.json` 与 `client_*.json`。
