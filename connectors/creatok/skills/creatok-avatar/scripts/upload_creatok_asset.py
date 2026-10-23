#!/usr/bin/env python3
"""Upload one explicit local WorkBuddy attachment to a prepared CreatOK URL.

The helper has two modes. ``inspect`` returns only schema-required file metadata;
``put`` validates the complete prepare result from stdin and uploads the exact
file bytes. It never reads connector configuration or accepts arbitrary request
headers, methods, destinations, or credentials.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


MAX_MANIFEST_BYTES = 64 * 1024
MAX_FILE_BYTES = {
    "image": 10 * 1024 * 1024,
    "video": 100 * 1024 * 1024,
}
MEDIA_IDENTITIES = {
    ".jpg": ("image", "image/jpeg"),
    ".jpeg": ("image", "image/jpeg"),
    ".png": ("image", "image/png"),
    ".webp": ("image", "image/webp"),
    ".gif": ("image", "image/gif"),
    ".mp4": ("video", "video/mp4"),
    ".mov": ("video", "video/quicktime"),
    ".avi": ("video", "video/x-msvideo"),
    ".webm": ("video", "video/webm"),
    ".mkv": ("video", "video/x-matroska"),
}


class UploadError(ValueError):
    """A sanitized error that is safe to return to the host model."""


class RejectRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise UploadError("prepared upload endpoint returned a redirect")


@dataclass(frozen=True)
class LocalMedia:
    path: Path
    filename: str
    media_type: str
    content_type: str
    size_bytes: int


@dataclass(frozen=True)
class PreparedUpload:
    upload_url: str
    object_key: str
    media_type: str
    content_type: str
    size_bytes: int


def _load_manifest() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise UploadError("stdin manifest is too large")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise UploadError("stdin must contain one UTF-8 JSON object") from error
    if not isinstance(value, dict):
        raise UploadError("stdin manifest must be an object")
    return value


def _local_media(manifest: dict[str, Any]) -> LocalMedia:
    raw_path = manifest.get("file_path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise UploadError("file_path must be a non-empty string")
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        raise UploadError("file_path must be absolute")
    if candidate.is_symlink():
        raise UploadError("symbolic-link attachments are not allowed")
    try:
        path = candidate.resolve(strict=True)
    except OSError as error:
        raise UploadError("local attachment does not exist") from error
    if not path.is_file():
        raise UploadError("local attachment is not a regular file")
    filename = path.name
    if not filename or len(filename) > 255:
        raise UploadError("local attachment filename is invalid")
    identity = MEDIA_IDENTITIES.get(path.suffix.lower())
    if identity is None:
        raise UploadError("local attachment extension is not supported")
    media_type, content_type = identity
    try:
        size_bytes = path.stat().st_size
    except OSError as error:
        raise UploadError("local attachment metadata could not be read") from error
    if size_bytes <= 0:
        raise UploadError("local attachment is empty")
    if size_bytes > MAX_FILE_BYTES[media_type]:
        raise UploadError(f"local {media_type} exceeds the upload size limit")
    return LocalMedia(path, filename, media_type, content_type, size_bytes)


def _prepare_data(manifest: dict[str, Any]) -> dict[str, Any]:
    value = manifest.get("prepare")
    if not isinstance(value, dict):
        raise UploadError("prepare must contain the complete upload-prepare result")
    if value.get("ok") is True and isinstance(value.get("data"), dict):
        value = value["data"]
    elif isinstance(value.get("data"), dict) and set(value) == {"data"}:
        value = value["data"]
    return value


def _validate_https_url(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise UploadError("prepared upload URL is missing")
    parsed = urlparse(value)
    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise UploadError("prepared upload URL must be absolute HTTPS")
    if parsed.username is not None or parsed.password is not None:
        raise UploadError("prepared upload URL must not contain credentials")
    return value


def _validate_expiry(value: Any) -> None:
    if not isinstance(value, str) or not value:
        raise UploadError("prepared upload expiry is missing")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        expires_at = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise UploadError("prepared upload expiry is invalid") from error
    if expires_at.tzinfo is None:
        raise UploadError("prepared upload expiry must include a timezone")
    if expires_at.astimezone(timezone.utc) <= datetime.now(timezone.utc):
        raise UploadError("prepared upload URL has expired")


def _prepared_upload(manifest: dict[str, Any], media: LocalMedia) -> PreparedUpload:
    data = _prepare_data(manifest)
    if data.get("method") != "PUT":
        raise UploadError("prepared upload method must be PUT")
    if data.get("next_tool") != "creatok_asset_upload_finalize":
        raise UploadError("prepared upload result has an unexpected continuation")
    upload_url = _validate_https_url(data.get("upload_url"))
    _validate_expiry(data.get("expires_at"))

    headers = data.get("required_headers")
    if not isinstance(headers, dict) or set(headers) != {"Content-Type"}:
        raise UploadError("prepared upload headers are not allowed")
    content_type = headers.get("Content-Type")
    if content_type != media.content_type:
        raise UploadError("prepared Content-Type does not match the local attachment")
    if data.get("media_type") != media.media_type:
        raise UploadError("prepared media type does not match the local attachment")
    if data.get("size_bytes") != media.size_bytes:
        raise UploadError("prepared size does not match the local attachment")

    object_key = data.get("object_key")
    if not isinstance(object_key, str) or not object_key or len(object_key) > 1024:
        raise UploadError("prepared object key is invalid")
    return PreparedUpload(
        upload_url=upload_url,
        object_key=object_key,
        media_type=media.media_type,
        content_type=content_type,
        size_bytes=media.size_bytes,
    )


def _put(media: LocalMedia, prepared: PreparedUpload) -> None:
    opener = build_opener(RejectRedirectHandler())
    try:
        with media.path.open("rb") as source:
            request = Request(
                prepared.upload_url,
                data=source,
                headers={
                    "Content-Type": prepared.content_type,
                    "Content-Length": str(prepared.size_bytes),
                },
                method="PUT",
            )
            with opener.open(request, timeout=120) as response:
                status = response.getcode()
                if status < 200 or status >= 300:
                    raise UploadError("prepared upload endpoint rejected the file")
                if response.geturl() != prepared.upload_url:
                    raise UploadError("prepared upload endpoint changed unexpectedly")
                response.read(1)
    except UploadError:
        raise
    except HTTPError as error:
        raise UploadError(f"prepared upload failed with HTTP {error.code}") from error
    except (OSError, URLError) as error:
        raise UploadError("prepared upload request failed") from error


def _emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inspect", "put"))
    arguments = parser.parse_args()
    try:
        manifest = _load_manifest()
        media = _local_media(manifest)
        if arguments.mode == "inspect":
            _emit(
                {
                    "ok": True,
                    "filename": media.filename,
                    "media_type": media.media_type,
                    "content_type": media.content_type,
                    "size_bytes": media.size_bytes,
                }
            )
            return 0

        prepared = _prepared_upload(manifest, media)
        _put(media, prepared)
        _emit(
            {
                "ok": True,
                "object_key": prepared.object_key,
                "media_type": prepared.media_type,
                "size_bytes": prepared.size_bytes,
            }
        )
        return 0
    except (OSError, UploadError) as error:
        _emit({"ok": False, "error": str(error)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
