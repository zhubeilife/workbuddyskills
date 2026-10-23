#!/usr/bin/env python3
"""Upload one user-selected local attachment with a one-use capability, no API Key.
Usage: python3 upload_asset.py --file /absolute/attachment.png < ticket.json
The ticket JSON comes from ruyi_begin_upload. Do not print/persist credentials.
"""

import argparse
import http.client
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


def upload(path, ticket):
    url = urlsplit(ticket["uploadUrl"])
    if (
        url.scheme != "https"
        or url.hostname != "ruyi-aigc.zero0123.com"
        or url.port not in (None, 443)
        or url.username
        or url.password
        or url.query
        or url.fragment
        or not re.fullmatch(r"/mcp-painting/v2/uploads/[a-f0-9]{32}", url.path)
    ):
        raise ValueError("上传地址不属于如意素材服务")
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise ValueError("请指定用户本次授权使用的附件绝对路径（常规文件）")
    size = path.stat().st_size
    if not 0 < size <= min(int(ticket["maxBytes"]), 100 * 1024 * 1024):
        raise ValueError("附件为空或超过上传大小限制")
    token = ticket["uploadToken"]
    if not re.fullmatch(r"[A-Za-z0-9_-]{40,100}", token):
        raise ValueError("上传凭证格式无效")
    conn = http.client.HTTPSConnection(url.hostname, timeout=180)
    try:
        conn.putrequest("POST", url.path)
        conn.putheader("X-Upload-Token", token)
        conn.putheader("Content-Type", "application/octet-stream")
        conn.putheader("Content-Length", str(size))
        conn.endheaders()
        with path.open("rb") as source:
            remaining = size
            while remaining:
                chunk = source.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ValueError("附件在上传中发生变化，请先查询本次上传状态")
                conn.send(chunk)
                remaining -= len(chunk)
        response = conn.getresponse()
        result = json.loads(response.read(65536))
        if response.status != 200:
            raise ValueError(
                "上传未成功，请用 ruyi_upload_status 查询原会话；不要重复生成"
            )
        return result
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    try:
        ticket = json.loads(sys.stdin.read(16384))
        print(json.dumps(upload(Path(args.file), ticket), ensure_ascii=False))
    except Exception:
        print(
            json.dumps(
                {"error": "附件上传未完成，请查询原上传会话状态。不要自动重试或生成。"},
                ensure_ascii=False,
            )
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
