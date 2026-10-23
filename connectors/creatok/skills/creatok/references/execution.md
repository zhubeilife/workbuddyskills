# Common MCP execution

Read for direct media tools, uploads, estimates, recovery and result delivery. Apply only the sections required by the current operation.

## Attachments and media

Use formal CreatOK `asset_uid` values returned by tools. Never accept or construct internal object keys.

For a WorkBuddy attachment or public URL, pass its server-accessible HTTPS URL to `creatok_asset_import_from_url`, with media type, optional filename/expected size/SHA-256, and one stable idempotency key. Never forward WorkBuddy identity or authentication headers. If WorkBuddy exposes an explicit image/video attachment only as a local absolute path, follow [`./local-media-upload.md`](./local-media-upload.md) to inspect required file metadata, prepare the upload, run the packaged PUT helper, and finalize it as a formal Asset. Header-protected remote URLs and local audio remain unsupported. Do not move media through JSON Base64.

The upload prepare/finalize path may use either a host-native HTTPS PUT or the packaged local upload helper. Never emulate PUT with curl, an improvised shell command/script, a browser, or a generic HTTP tool.

Signed resource URLs expire after about a day. Give every user-facing media item its link as a Markdown link with a short visible label, say that the link is temporary, and refresh an expired one through the relevant get/list tool. Never print the bare URL as visible text, persist it, or reconstruct it. When a sidebar preview also helps, present the whole set through one native resource-presentation action rather than one sidebar per item.

## Local delivery of successful media

When `creatok_task_get` returns `status: "succeeded"` and a non-empty `result_assets` array, downloading every returned media result into the current local workspace is mandatory. Use WorkBuddy's local execution only for this delivery step:

1. Run the packaged `__SKILL_DIR__/scripts/download_creatok_results.py` helper with the current workspace as its working directory, pass the exact returned `task_id` through `--task-id`, and send the complete, unmodified `result_assets` array as JSON on stdin. Use `python3`, or `python` when that is the available Python 3 command. Do not write a replacement downloader if the packaged helper is missing.
2. The helper must produce files only under `creatok_output/<task_id>/`. It accepts only the server-returned `media_url`/`resource_link.uri`, follows HTTPS redirects, sends no authentication, validates media and size, and writes atomically. Never construct a URL, add headers, pass a key, or use local execution to call any CreatOK API or MCP endpoint.
3. After the helper returns, require each reported local file to exist and be non-empty. Call WorkBuddy `present_files` exactly once with all successfully downloaded absolute paths so the complete ordered result set appears in one sidebar. Reuse or replace the active sidebar, never call `present_files` once per file, and do not duplicate the media inline in chat. Then tell the user the actual local paths and any failed result indices.
4. A download failure is not a generation failure. Never resubmit or recreate a paid task to repair delivery. If a URL is expired, query the same `task_id` with `creatok_task_get` to obtain refreshed result URLs and retry only the failed downloads. If local execution, Python, the workspace, or `present_files` is unavailable, report that limitation and the completed `task_id`; never claim the files were downloaded or displayed.

Do not persist the manifest after delivery.

This procedure covers the results of a paid task and nothing else. Never download media on any other path: an Asset listing, an analysis source video, a browse or cleanup flow, or a media choice for a later step is answered with its link, not with a copy on the user's disk. A cleanup flow in particular exists because the user is short on space.

## Mutations, money, and recovery

For every paid operation, call `creatok_credits_estimate`, show in the user's language the exact normalized parameters using visible labels, price, remaining credits, and expiry, and obtain explicit confirmation. Submit the exact same options with `cost_confirmation: {estimate_id, max_credits}` and one stable idempotency key.

Use stable idempotency keys for every non-read operation. Reuse the same key after a timeout or `RESULT_UNKNOWN`; never create a new key merely to retry an uncertain operation. When parameters or user intent change, create a new estimate/confirmation/key as applicable.

Poll only the returned task/job identifier and follow `retry_after_seconds`. Never resubmit because a task is queued/running. All IDs, refs, receipts, cursors, URLs, and recovery handles must come verbatim from MCP results. When structured output is unavailable, use the complete serialized JSON in the first text result. Never guess a handle.

For deletion, distinguish recycle from permanent deletion. Batch/conditional Asset deletion and recycle-bin purge require preview → display exact count/bytes/release semantics → explicit confirmation → execute with the same preview and expected count. Permanent deletion always requires a second explicit confirmation.

For TikTok publication, explicit confirmation must cover connection/account, publish kind, media, caption/title/description, products, music, privacy/interaction settings, disclosure flags, post mode, and schedule. Do not infer consent from an earlier generation or upload confirmation.

For every scheduled publication, read `publishing_capabilities.schedule_at_unit`, `publishing_capabilities.schedule.min_lead_ms`, and the platform-specific `max_lead_ms` from the current capabilities result. Read `publishing_capabilities.text_length_unit` before enforcing any title, caption, or description limit. Do not copy the current lead-time or text-length rules into the Skill.

Explain failures in product language and give the next safe action before adding the stable failure `code` and `request_id` as diagnostic references. For `RESULT_UNKNOWN`, keep `operation_id`, `task_id`, `job_id`, or `asset_uid` internal unless needed for recovery or requested for debugging, and use the corresponding status/get tool. Never expose provider IDs, internal object keys, signed handles, or raw diagnostics.
