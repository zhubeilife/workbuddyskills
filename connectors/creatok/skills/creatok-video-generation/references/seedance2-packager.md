# Seedance 2 Prompt Packaging

Use this file only after the current atomic task passes the minimum input contract in [seedance2.md](./seedance2.md). Preserve the user's supplied content and do not add new content decisions.

If conversion reveals a new blocker, return to the question policy in [seedance2.md](./seedance2.md) instead of guessing.

## Conversion steps

1. Inspect available images when possible. If inspection is unavailable, bind images only by the user's explicit labels and do not imply unverified facts.
2. Match the request to the appropriate Seedance action wording below.
3. Build the instruction in this order when applicable: subject binding, target scene or change, ordered action, sound or text layer, relevant constraints.
4. Shorten wording when useful, while preserving narrative order and content decisions.
5. When a request matches a known problem case, consult the relevant section of [seedance2-patterns.md](./seedance2-patterns.md) and use a safer expression or minimal constraint only if it preserves the requested result.
6. Check all image references before output.

## Action wording

- Image-reference generation: `参考 @图片 N 的[已确认参考内容]，生成...`

## Image reference rules

Follow the image-reference rules in [seedance2.md](./seedance2.md). When packaging the result:

- If `素材对应` is included, make each image number and role agree with the final prompt body.
- Do not list or reference unused images.
- Never use an image ID alone as the final reference.
- Textual naming does not upload or bind a file. Keep `@图片 N` in the same order as the selected images; the generation workflow must resolve each selection to its formal MCP Asset before submission.

## Prompt shapes

### Text-to-video or script conversion

```text
[明确主体]在[场景]中[用户已确定的动作或事件]，[用户已确定的风格、镜头、声音或约束]。
```

Use ordered `镜头1 / 镜头2 / 镜头3` only when the input already contains multiple shots or ordered content. Do not create a shot sequence from a bare concept.

### Image-reference generation

```text
参考 @图片 1 中的[已确认参考内容]，生成[目标内容]，保持[需要继承的特征]一致。
```

### Text, dialogue, subtitle, music, and sound instructions

```text
画面[必要时的位置或时机]显示文字“[用户提供的文字]”。
[角色]用[用户已确定的语气或音色]说道{[用户提供的台词]}。
```

## Subject and shot consistency

- Define a repeated subject with two or three stable, supplied or inspected features and one label.
- Keep the same label for the same subject throughout.
- Put the controlling image reference early and use only functionally necessary images.
- For complex requests, prefer ordered shots over exact second ranges unless the user supplied exact timing or localization requires it.
- Use one main camera movement per shot.
- Prefer concrete actions and visible emotional details already present in the input.
- Add constraints only when relevant to fidelity, safety, or a known problem case.

Example subject binding:

```text
将 @图片 1 中穿红色连衣裙、戴草帽的女人定义为主体1。
```

Example ordered shots:

```text
镜头1：[景别/运镜]，[主体]在[位置][动作与表情]，[声音/台词/文字层]。
镜头2：...
```

## Text, dialogue, and sound notation

- Music: `（...）`
- Sound effects: `<...>`
- Dialogue: `{...}`
- Subtitle or title cards: `【...】`

Keep generated text short and common. Describe voice texture, pace, emotion, and speech style only when the user has supplied those instructions.

## Output formats

Default with images:

```text
素材对应：
- @图片 1 = ...，用途：...

Seedance 2 提示词：
[final prompt，正文必须直接包含上述实际使用的 @图片 N]
```

Default without assets:

```text
Seedance 2 提示词：
[final prompt]
```

For failure diagnosis:

```text
问题判断：...
调整后的 Seedance 2 提示词：
[final prompt]
```

Do not display task classification, internal control concepts, risk analysis, reference names, workflow explanations, or a routine summary. Surface a risk only when it blocks conversion or requires user action, and explain it briefly in natural language.

