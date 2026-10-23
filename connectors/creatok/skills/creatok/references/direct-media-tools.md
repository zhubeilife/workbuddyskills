# Direct media MCP tools

These operations have no standalone Skills. Apply [execution.md](./execution.md) for the common upload → estimate/confirm → submit → status → delivery sequence where applicable, and [user-experience.md](./user-experience.md) for presentation. Read current capabilities and tool schemas rather than imposing fixed limits.

| User intent | Tool | Estimate service |
|---|---|---|
| Generate images | `creatok_image_generate` | `image_generation` |
| Upscale images | `creatok_image_upscale` | `image_upscale` |
| Upscale video | `creatok_video_upscale` | `video_upscale` |
| Remove watermark | `creatok_video_watermark_remove` | `video_watermark_removal` |
| Remove burned-in subtitles | `creatok_video_subtitle_remove` | `video_subtitle_removal` |
| Explicitly optimize a video prompt | `creatok_prompt_optimize` | None; synchronous, read-only |

## Inputs and options

Resolve exact source media before browsing or importing. Honor an explicitly selected attachment/Asset; otherwise resolve upload versus library and the required selections without defaulting to AI generations. Image generation needs no media selection when text-only. Image upscale supports a batch of selected image Assets up to current capabilities: never impose a single-image restriction. Video processing uses the exact source allowed by its schema. Use formal returned Asset UIDs, not local paths or object keys.

For image generation, read `models.image.models`: `limits.max_prompt_length` (Unicode code points), reference limits, output count, resolution, ratio and quality. Every non-empty supplied prompt is final regardless of length or detail; preserve it verbatim. Ask if absent; do not rewrite or optimize automatically. Confirm the model label, exact prompt, references and normalized output settings.

For image upscale, use current batch size, scale, enhancement model, output format and face enhancement options. Show the selected image set and full estimated batch cost. Do not grade image quality or decide whether the requested operation is worthwhile.

For video upscale, confirm available source metadata and target resolution/fps. Watermark removal must not first detect or verify a watermark; when no options are advertised, the source is the only choice. Subtitle removal must not first detect/read subtitles: preserve the exact normalized `selected_area`, explain the region, and never guess the region. Validate with the tool rather than inspecting content as a preflight.

## Prompt optimization

Call `creatok_prompt_optimize` only when the user explicitly asks to improve or rewrite a video prompt. Read `models.prompt_optimization.max_reference_images`, `supported_locales` and reference roles. Resolve only requested references; ask for a missing raw prompt. The operation deducts no paid-generation credits and needs neither a generation estimate nor task polling.

Present the returned prompt as a proposal. If the user elects to generate it, hand off to installed `creatok-video-generation` with the chosen model, references and text verbatim; do not optimize it again. Seedance syntax packaging belongs to that Skill's Seedance reference, not this optimization tool.

## Multiple video operations

Do not run all three operations by default. Resolve a broad “enhance” request to the user's intended operation. Only for explicitly requested multiple operations, read [video-processing-chain.md](./video-processing-chain.md).
