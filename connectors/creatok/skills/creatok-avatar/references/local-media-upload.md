# Secure local media upload for WorkBuddy

Read this reference only when WorkBuddy exposes a user-selected image or video as a local absolute path instead of a server-accessible HTTPS attachment URL. This is transport preparation, not content analysis. Never inspect the media to decide whether the user's requested operation is needed.

## Boundaries

- Use only the packaged `__SKILL_DIR__/scripts/upload_creatok_asset.py` helper. Never replace it with curl, PowerShell, a generic HTTP tool, a browser request, or an improvised script.
- The exact local path must come from the current user-selected WorkBuddy attachment or an explicit path in the user's current request. Never discover files, scan directories, follow symlinks, or substitute another path.
- The helper supports only the image/video extensions and size limits reported by its `inspect` mode and current `creatok_capabilities_get`/`upload_limits.asset`. Local audio still requires a server-accessible HTTPS URL because staged audio upload is not supported.
- The helper never receives an API key, connector configuration, identity header, or CreatOK endpoint. It may PUT only to the exact short-lived HTTPS URL returned by `creatok_asset_upload_prepare`, with the exact permitted content type and declared byte size.
- Keep the upload URL, required headers, object key, operation ID, and resulting Asset UID private. Never print them in conversation or persist the prepare manifest.

## Procedure

1. Run `__SKILL_DIR__/scripts/upload_creatok_asset.py inspect` through WorkBuddy local execution and send exactly `{ "file_path": <the selected absolute local path> }` as UTF-8 JSON on stdin. This reads only filename, extension, and byte size; it performs no media-content detection or analysis.
2. Compare the returned media type, content type, and size with current `upload_limits.asset`. Call `creatok_asset_upload_prepare` with exactly that `media_type`, base `filename`, `content_type`, and `size_bytes`. Do not add model context or alter the filename.
3. Immediately run `__SKILL_DIR__/scripts/upload_creatok_asset.py put` and send `{ "file_path": <the same exact path>, "prepare": <the complete unmodified successful prepare result> }` as UTF-8 JSON on stdin. Do not put the JSON or signed URL in the shell command line.
4. Only when the helper returns `ok: true`, call `creatok_asset_upload_finalize` with the returned `object_key`, `media_type`, and one stable `idempotency_key`. Supply `model` only when the owning workflow explicitly requires current model context. Reuse the same finalization key after timeout or `RESULT_UNKNOWN`; never finalize the same staged object with a new key.
5. Continue the user's originally requested workflow with the formal Asset UID returned by finalize. Uploading the attachment does not authorize a different generation, processing, publishing, or deletion operation.

If inspect fails, report the local-file limitation without trying another file. If prepare expires before PUT, obtain one fresh prepare result and retry the PUT; never reuse an expired URL. If PUT fails, do not finalize. If finalize is uncertain, follow its same-key recovery path and do not upload the file again unless the server definitively says the staged object is unavailable.
