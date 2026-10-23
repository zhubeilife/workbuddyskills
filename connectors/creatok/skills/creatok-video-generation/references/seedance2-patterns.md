# Seedance 2 Construction and Failure Patterns

Read this file when the request includes a duration or timed sequence, needs a stable construction pattern, requires failure diagnosis, or matches a high-risk problem. Apply only the relevant section.

## Current capabilities

Use the selected model's current duration and reference constraints from MCP capabilities, never a fixed duration or people-count assumption. Do not silently truncate, accelerate, omit or redesign content to fit. If a requested plan exceeds the available single generation duration, resolve compression versus segmentation. Duration stays optional when it does not affect faithful packaging.

Examples below are expression patterns, not permission to add events, imagery, dialogue or creative decisions absent from the user's content.

## Stable construction patterns

### Separate the role of each image reference

```text
@图片 1 锁定角色面部，@图片 2 锁定服装和身形，@图片 3 作为场景和画面风格参考。
```

Each image has one role, so references do not compete.

### Express a complex video as ordered shots

```text
镜头1：中景平稳跟拍，[主体]走到门口，停顿、深呼吸。
镜头2：镜头切到室内中景，[主体]推门进入，与其他人对视。
镜头3：近景，[主体]低头停顿后抬头笑出声，镜头缓慢拉远。
```

Ordered shots control sequence without forcing exact seconds.

### Show emotion through visible behavior

Prefer:

```text
她微微低头，肩膀放松，手指松开衣角，长长舒了一口气。
```

Instead of:

```text
她很释然。
```

### Use one main camera movement per shot

Prefer:

```text
镜头缓慢推近到人物近景。
```

Avoid stacking:

```text
镜头推近、拉远、环绕、摇移、俯冲。
```

### Specify a text layer clearly

```text
画面结尾中部显示文字“Light Up Every Moment”，以柔和淡入方式出现，字体为细长无衬线体，颜色为暖白色。
```

When the user has supplied them, include content, timing, position, and appearance or entry.

## Failure and high-risk patterns

- **ID drift**: use an independent face close-up and a full-body or style reference; define the face and styling sources; avoid human multi-view sheets.
- **Real-human reference rejection**: follow the current Avatar/readiness and model constraints in the video workflow. Do not automatically transform faces or use a workaround to bypass provider rejection; explain the returned limitation and resolve a supported alternative with the user.
- **Duplicate or twin people**: define each role with a unique label and source, add a no-duplicate constraint, and avoid three-view or multi-view character references.
- **Unwanted subtitles or text**: add `保持无字幕，避免生成任何文字或字幕`; remove text from source media if it is not needed.
- **Logo or watermark appears**: add `不要生成Logo，不要生成水印`; for an exact logo, use a logo reference and simplify the scene.
- **Style drift**: state the target style explicitly; restyle conflicting reference assets before video generation when possible.
- **Too many reference people**: follow current model constraints; discuss a supported grouping if needed rather than assuming a fixed number.
- **Ending audio noise**: regenerate or plan an audio fade-out in post; prompting alone is not reliable.
- **Pronunciation error**: replace rare or polyphonic characters with common homophones when acceptable.
- **Voice mismatch**: describe timbre, age impression, texture, pace, and emotion in text.
