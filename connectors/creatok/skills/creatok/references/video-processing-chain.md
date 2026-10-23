# Explicit video processing chains

Use only when the user requests multiple video processing operations. A single upscale, watermark-removal or subtitle-removal request goes directly to its tool.

1. Preserve an explicit order. If order materially changes the result and is unresolved, clarify it; do not invent a mandatory cleaning sequence.
2. Resolve the first exact video Asset and operation options using current capabilities.
3. Estimate that step, show source/settings/price and obtain confirmation; submit using the matching receipt and one stable idempotency key. Follow [execution.md](./execution.md) for status and recovery.
4. After success, take a formal Asset UID from the result or resolve/import its returned result URL through the supported Asset tools. Never treat a task ID or URL as an Asset UID. If no supported result-to-Asset path is available, stop at the completed step and explain the missing handoff.
5. Use this actual output as the next step's source, with its own estimate, confirmation and idempotency key. Do not reuse the original video unless the user requested parallel variants.
6. On a later failure, preserve completed results and resume only the failed/unstarted step. Never rerun a successful paid step or promise atomic completion/rollback. Deliver completed results with their processing stage and explain partial completion.
