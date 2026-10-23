#!/usr/bin/env python3
"""Download successful CreatOK task results into the current workspace.

The manifest is read from stdin. It must be either the complete `result_assets`
array returned by `creatok_task_get`, or an object containing that array.
This helper intentionally has no option for request headers or credentials.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


MAX_DOWNLOAD_BYTES = 2 * 1024 * 1024 * 1024
TASK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,191}$")
SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
CONTENT_TYPE_EXTENSIONS = {
    "image/avif": ".avif",
    "image/gif": ".gif",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
}
ALLOWED_URL_EXTENSIONS = {
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".png",
    ".webm",
    ".webp",
}


class HttpsOnlyRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        absolute_url = urljoin(req.full_url, newurl)
        _validate_https_url(absolute_url)
        return super().redirect_request(req, fp, code, msg, headers, absolute_url)


def _validate_https_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("only absolute HTTPS result URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("credentials in result URLs are not allowed")


def _load_items() -> list[dict[str, Any]]:
    try:
        manifest = json.load(sys.stdin)
    except json.JSONDecodeError as error:
        raise ValueError(f"stdin is not valid JSON: {error.msg}") from error

    if isinstance(manifest, dict):
        manifest = manifest.get("result_assets")
    if not isinstance(manifest, list):
        raise ValueError("manifest must be a result_assets array or contain one")
    if not manifest:
        raise ValueError("result_assets is empty")
    if len(manifest) > 32:
        raise ValueError("result_assets contains more than 32 items")
    if not all(isinstance(item, dict) for item in manifest):
        raise ValueError("every result asset must be an object")
    return manifest


def _media_type(item: dict[str, Any]) -> str:
    value = item.get("media_type")
    if value in {"image", "video"}:
        return value
    title = item.get("title")
    if isinstance(title, str):
        lowered = title.lower()
        if lowered.startswith("image"):
            return "image"
        if lowered.startswith("video"):
            return "video"
    raise ValueError("result asset is missing a valid media_type")


def _item_url(item: dict[str, Any]) -> str:
    value = item.get("media_url", item.get("uri"))
    if not isinstance(value, str) or not value:
        raise ValueError("result asset is missing media_url/resource_link.uri")
    _validate_https_url(value)
    return value


def _expected_size(item: dict[str, Any]) -> int | None:
    value = item.get("size_bytes", item.get("size"))
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("result asset size must be a positive integer or null")
    if value > MAX_DOWNLOAD_BYTES:
        raise ValueError("result asset exceeds the local delivery size limit")
    return value


def _safe_uid(item: dict[str, Any], index: int) -> str:
    value = item.get("uid", item.get("name"))
    if not isinstance(value, str) or not value:
        return f"result-{index:02d}"
    safe = SAFE_NAME_PATTERN.sub("-", value).strip(".-_")[:80]
    return safe or f"result-{index:02d}"


def _extension(content_type: str, url: str, media_type: str) -> str:
    normalized = content_type.split(";", 1)[0].strip().lower()
    if normalized in CONTENT_TYPE_EXTENSIONS:
        return CONTENT_TYPE_EXTENSIONS[normalized]
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in ALLOWED_URL_EXTENSIONS:
        return ".jpg" if suffix == ".jpeg" else suffix
    return ".png" if media_type == "image" else ".mp4"


def _download_one(
    opener, item: dict[str, Any], index: int, output_dir: Path
) -> dict[str, Any]:  # noqa: ANN001
    media_type = _media_type(item)
    url = _item_url(item)
    expected_size = _expected_size(item)
    request = Request(
        url,
        headers={
            "Accept": "image/*, video/*, application/octet-stream",
            "User-Agent": "CreatOK-WorkBuddy-Delivery/1.0",
        },
        method="GET",
    )

    temporary_path: Path | None = None
    try:
        with opener.open(request, timeout=45) as response:
            _validate_https_url(response.geturl())
            content_type = response.headers.get("Content-Type", "")
            normalized_type = content_type.split(";", 1)[0].strip().lower()
            if normalized_type and normalized_type != "application/octet-stream":
                if not normalized_type.startswith(f"{media_type}/"):
                    raise ValueError(
                        f"unexpected Content-Type {normalized_type!r} for {media_type} result"
                    )

            declared_length = response.headers.get("Content-Length")
            if declared_length:
                try:
                    declared_bytes = int(declared_length)
                except ValueError as error:
                    raise ValueError("invalid Content-Length") from error
                if declared_bytes <= 0 or declared_bytes > MAX_DOWNLOAD_BYTES:
                    raise ValueError("invalid or oversized Content-Length")
                if expected_size is not None and declared_bytes != expected_size:
                    raise ValueError("Content-Length does not match result asset size")

            extension = _extension(content_type, response.geturl(), media_type)
            filename = f"{index:02d}-{_safe_uid(item, index)}{extension}"
            destination = output_dir / filename
            file_descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{filename}.", suffix=".part", dir=output_dir
            )
            temporary_path = Path(temporary_name)
            total = 0
            with os.fdopen(file_descriptor, "wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise ValueError("download exceeds the local delivery size limit")
                    output.write(chunk)
                output.flush()
                os.fsync(output.fileno())

            if total == 0:
                raise ValueError("downloaded file is empty")
            if expected_size is not None and total != expected_size:
                raise ValueError("downloaded size does not match result asset size")
            os.replace(temporary_path, destination)
            temporary_path = None
            return {
                "index": index,
                "uid": item.get("uid", item.get("name")),
                "media_type": media_type,
                "path": str(destination.resolve()),
                "size_bytes": total,
            }
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    arguments = parser.parse_args()

    if not TASK_ID_PATTERN.fullmatch(arguments.task_id):
        print(
            json.dumps({"ok": False, "error": "invalid task_id"}),
            file=sys.stdout,
        )
        return 2

    try:
        items = _load_items()
        workspace = Path.cwd().resolve()
        expected_parent = (workspace / "creatok_output").resolve()
        if expected_parent.parent != workspace:
            raise ValueError("creatok_output must be a directory inside the current workspace")
        output_dir = (expected_parent / arguments.task_id).resolve()
        if output_dir.parent != expected_parent:
            raise ValueError("output directory must remain inside the current workspace")
        output_dir.mkdir(parents=True, exist_ok=True)

        opener = build_opener(HttpsOnlyRedirectHandler())
        downloaded = []
        failed = []
        for index, item in enumerate(items, start=1):
            try:
                downloaded.append(_download_one(opener, item, index, output_dir))
            except (HTTPError, URLError, OSError, ValueError) as error:
                failed.append(
                    {
                        "index": index,
                        "uid": item.get("uid", item.get("name")),
                        "error": str(error),
                    }
                )

        result = {
            "ok": not failed,
            "task_id": arguments.task_id,
            "output_dir": str(output_dir),
            "downloaded": downloaded,
            "failed": failed,
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0 if not failed else 1
    except (OSError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
