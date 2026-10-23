# -*- coding: utf-8 -*-
"""
Beluga MCP 一键接入脚本(WorkBuddy / 通用 streamableHttp MCP 均适用)

背景:WorkBuddy 原生 OAuth 使用自定义 scheme 回调,而 Beluga OAuth 服务端
的动态客户端注册(DCR)仅接受 http/https 回调,原生授权会报
「客户端元数据无效」。本脚本用标准 MCP OAuth 2.1 流程完成接入:

  1. 发现网关的 OAuth 元数据(authorization / token / registration 端点)
  2. 动态注册客户端(redirect_uri = http://localhost:<port>/callback)
  3. 本地起回调监听 + 自动拉起浏览器,用户登录授权
  4. PKCE 换取 access_token / refresh_token
  5. 把 Bearer Token 写入 ~/.workbuddy/mcp.json 对应 server 的 headers
  6. 验证 initialize 并列出可用工具

用法:
  python connect.py                       # 完整接入(默认生产网关)
  python connect.py --check               # 用已保存的 token 验证并列出工具
  python connect.py --refresh             # 用 refresh_token 续期并更新配置
  python connect.py --url <gateway> --name <server名>   # 接入其他网关

仅依赖 Python 3.9+ 标准库。
"""
import argparse
import base64
import hashlib
import http.server
import json
import os
import secrets
import socket
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

DEFAULT_URL = "https://beluga-server-cn.heytapmobi.com/beluga-mcp/gateway"
DEFAULT_NAME = "beluga-mcp-prod"
TOKEN_TTL_MARGIN = 60  # 秒:access_token 剩余寿命低于此值视为临期


def http_json(url, data=None, headers=None, method=None, timeout=30):
    """请求并解析 JSON;若响应是 SSE 文本则原样返回字符串。"""
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            try:
                return resp.status, dict(resp.headers), json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, dict(resp.headers), raw
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, dict(e.headers), body


def discover_oauth(gateway_url):
    """按 RFC 8414 / MCP 规范发现 OAuth 端点。"""
    parsed = urllib.parse.urlparse(gateway_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path.rstrip("/")

    # 1) 受保护资源元数据
    candidates = [
        f"{root}/.well-known/oauth-protected-resource{path}",
        f"{root}/.well-known/oauth-protected-resource",
    ]
    pr = None
    for u in candidates:
        code, _, body = http_json(u)
        if code == 200 and isinstance(body, dict) and "authorization_servers" in body:
            pr = body
            break
    if not pr:
        raise RuntimeError("网关未提供 oauth-protected-resource 元数据,可能不需要 OAuth")

    # 2) 授权服务器元数据(两种 well-known 路径变体都试)
    as_issuer = pr["authorization_servers"][0].rstrip("/")
    issuer_path = urllib.parse.urlparse(as_issuer).path
    candidates = [
        f"{root}/.well-known/oauth-authorization-server{issuer_path}",
        f"{as_issuer}/.well-known/oauth-authorization-server",
    ]
    for u in candidates:
        code, _, body = http_json(u)
        if code == 200 and isinstance(body, dict) and "authorization_endpoint" in body:
            return body
    raise RuntimeError("未找到 oauth-authorization-server 元数据")


def register_client(as_meta, redirect_uri, scope):
    reg = as_meta.get("registration_endpoint")
    if not reg:
        raise RuntimeError("授权服务器不支持动态客户端注册,请向平台方申请固定 client_id")
    payload = {
        "client_name": "WorkBuddy Beluga Connector",
        "redirect_uris": [redirect_uri],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }
    if scope:
        payload["scope"] = scope
    code, _, body = http_json(reg, data=json.dumps(payload).encode(),
                              headers={"Content-Type": "application/json"})
    if code != 201 or "client_id" not in body:
        raise RuntimeError(f"动态注册失败({code}): {body}")
    return body["client_id"]


def free_port(start=5678, tries=20):
    for p in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise RuntimeError("本地无可用端口")


def authorize_in_browser(as_meta, client_id, redirect_uri, scope):
    """本地监听 + 自动拉起浏览器 + PKCE,返回授权码。"""
    import time
    port = int(urllib.parse.urlparse(redirect_uri).port)
    result = {}
    done = threading.Event()

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.urlparse(self.path)
            if q.path == urllib.parse.urlparse(redirect_uri).path:
                params = urllib.parse.parse_qs(q.query)
                result.update({k: v[0] for k, v in params.items()})
                ok = "code" in result
                msg = ("<h2>&#9989; 授权成功!请回到 WorkBuddy。</h2><p>可关闭此页面。</p>"
                       if ok else
                       "<h2>&#10060; 授权失败</h2><pre>" + str(params) + "</pre>")
                done.set()
            else:
                msg = "<h2>404</h2>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))

        def log_message(self, *a):
            pass

    socketserver = __import__("socketserver")
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    verifier = base64.urlsafe_b64encode(secrets.token_bytes(60)).decode().rstrip("=")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")

    url = (f"{as_meta['authorization_endpoint']}?response_type=code"
           f"&client_id={urllib.parse.quote(client_id)}"
           f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
           f"&scope={urllib.parse.quote(scope or 'mcp')}"
           f"&state={secrets.token_hex(8)}"
           f"&code_challenge={challenge}&code_challenge_method=S256")

    print(f"[3/6] 打开浏览器进行授权(如未自动弹出,请手动打开):\n      {url}\n")
    webbrowser.open(url)
    if not done.wait(420):
        raise RuntimeError("超时:7 分钟内未收到授权回调")
    if "code" not in result:
        raise RuntimeError(f"授权失败: {result}")
    return result["code"], verifier


def exchange_token(as_meta, code, verifier, client_id, redirect_uri):
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": verifier,
    }).encode()
    code_, _, body = http_json(as_meta["token_endpoint"], data=data,
                               headers={"Content-Type": "application/x-www-form-urlencoded"})
    if code_ != 200 or "access_token" not in body:
        raise RuntimeError(f"换取令牌失败({code_}): {body}")
    return body


def refresh_token(as_meta, tok, client_id):
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": tok["refresh_token"],
        "client_id": client_id,
    }).encode()
    code, _, body = http_json(as_meta["token_endpoint"], data=data,
                              headers={"Content-Type": "application/x-www-form-urlencoded"})
    if code != 200 or "access_token" not in body:
        raise RuntimeError(f"刷新令牌失败({code}): {body}")
    # 某些实现不回传新 refresh_token,保留旧的
    if "refresh_token" not in body:
        body["refresh_token"] = tok["refresh_token"]
    return body


def write_config(config_path, server_name, gateway_url, access_token):
    cfg = {}
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
    srv = cfg.setdefault("mcpServers", {}).setdefault(server_name, {})
    srv["type"] = "streamableHttp"
    srv["url"] = gateway_url
    srv.setdefault("timeout", 30000)
    srv["headers"] = {"Authorization": f"Bearer {access_token}"}
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_or_register_state(state_path):
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state_path, state):
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def mcp_rpc(gateway_url, token, method, params=None, rpc_id=1):
    payload = {"jsonrpc": "2.0", "id": rpc_id, "method": method}
    if params is not None:
        payload["params"] = params
    code, _, body = http_json(
        gateway_url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json, text/event-stream",
                 "Authorization": f"Bearer {token}"},
        timeout=30)
    if code == 401:
        raise PermissionError("令牌无效或已过期(401)")
    # streamableHttp 可能返回 SSE 帧,统一抽出 data: 行
    if isinstance(body, dict):
        return body
    text = body if isinstance(body, str) else json.dumps(body)
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data: "):
            try:
                return json.loads(line[6:])
            except Exception:
                pass
    return {"raw": text}


def list_tools(gateway_url, token):
    resp = mcp_rpc(gateway_url, token, "tools/list", {}, rpc_id=2)
    tools = resp.get("result", {}).get("tools", []) if isinstance(resp, dict) else []
    return tools


def main():
    ap = argparse.ArgumentParser(description="Beluga MCP 一键接入")
    ap.add_argument("--url", default=DEFAULT_URL, help="MCP 网关地址")
    ap.add_argument("--name", default=DEFAULT_NAME, help="写入 mcp.json 的 server 名称")
    ap.add_argument("--config", default=os.path.join(os.path.expanduser("~"),
                    ".workbuddy", "mcp.json"), help="目标 mcp.json 路径")
    ap.add_argument("--scope", default="mcp", help="申请的 OAuth scope")
    ap.add_argument("--check", action="store_true", help="仅验证现有令牌并列出工具")
    ap.add_argument("--refresh", action="store_true", help="用 refresh_token 续期")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(here, f"token_{args.name}.json")
    state_path = os.path.join(here, f"client_{args.name}.json")

    tok = load_or_register_state(token_path)

    if args.check:
        if not tok.get("access_token"):
            print("尚未接入,请先运行: python connect.py")
            sys.exit(1)
        try:
            tools = list_tools(args.url, tok["access_token"])
        except PermissionError:
            print("令牌已失效,请运行: python connect.py --refresh")
            sys.exit(2)
        print(f"连接正常,可用工具 {len(tools)} 个:")
        for t in tools:
            print(f"  - {t['name']}: {(t.get('description') or '').splitlines()[0][:60]}")
        return

    if args.refresh:
        if not tok.get("refresh_token"):
            print("没有可用的 refresh_token,请运行: python connect.py")
            sys.exit(1)
        state = load_or_register_state(state_path)
        print("[1/3] 发现 OAuth 元数据...")
        as_meta = discover_oauth(args.url)
        print("[2/3] 刷新令牌...")
        tok = refresh_token(as_meta, tok, state.get("client_id"))
        save_state(token_path, tok)
        print("[3/3] 更新 mcp.json...")
        write_config(args.config, args.name, args.url, tok["access_token"])
        print(f"完成,access_token 有效期约 {tok.get('expires_in', '?')} 秒。")
        return

    # ---- 完整接入 ----
    print(f"[1/6] 探测网关 OAuth 元数据:{args.url}")
    as_meta = discover_oauth(args.url)
    print(f"      issuer = {as_meta.get('issuer')}")

    redirect_port = free_port()
    redirect_uri = f"http://localhost:{redirect_port}/callback"

    print("[2/6] 动态注册 OAuth 客户端...")
    state = load_or_register_state(state_path)
    if state.get("client_id") and state.get("redirect_uri") == redirect_uri:
        client_id = state["client_id"]
        print(f"      复用已注册客户端 {client_id}")
    else:
        client_id = register_client(as_meta, redirect_uri, args.scope)
        print(f"      注册成功 client_id = {client_id}")
    state.update({"client_id": client_id, "redirect_uri": redirect_uri})
    save_state(state_path, state)

    print("[3/6] 浏览器授权...")
    code, verifier = authorize_in_browser(as_meta, client_id, redirect_uri, args.scope)

    print("[4/6] 换取令牌...")
    tok = exchange_token(as_meta, code, verifier, client_id, redirect_uri)
    save_state(token_path, tok)
    print(f"      access_token 有效期约 {tok.get('expires_in', '?')} 秒,"
          f"refresh_token 已保存。")

    print(f"[5/6] 写入 {args.config}(server: {args.name})...")
    write_config(args.config, args.name, args.url, tok["access_token"])

    print("[6/6] 验证连接...")
    try:
        tools = list_tools(args.url, tok["access_token"])
        print(f"      连接成功,可用工具 {len(tools)} 个:")
        for t in tools:
            print(f"        - {t['name']}: {(t.get('description') or '').splitlines()[0][:60]}")
    except Exception as e:
        print(f"      警告:工具列表获取失败({e}),但令牌已写入配置,请重试连接。")

    print("\n✅ 接入完成!回到 WorkBuddy「插件 → MCP 服务器」对该 server 点击"
          "「信任/重连」即可使用。")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
