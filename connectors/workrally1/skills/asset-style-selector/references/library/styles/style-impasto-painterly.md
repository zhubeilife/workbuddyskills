风格 ID：`style-impasto-painterly`
原目录：`资产-厚涂插画风格`

# 厚涂插画 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：数字绘画
- **标准名**：厚涂插画
- **原名**（内部标识，不外显）：厚涂插画风格
- **题材定位**：厚重笔触堆叠的数字绘画插画，弱化线稿、以体积光影塑形，**区别于赛璐璐分色平涂与线稿主导的清线插画**

## 风格参考（Reference）
概念设计厚涂、游戏原画立绘、当代厚涂数字插画；核心是 **impasto painterly rendering**——几乎不用清晰线稿，靠成块的笔触与色彩堆叠塑造体积，笔触方向即结构，明暗交界锐利有力，质感厚重、绘画感强烈。

## 第一性拆解（Style Decomposition）
- **打光**：强烈的体积光影，明确的明暗交界线，戏剧性主光塑造立体感，冷暖对比
- **色彩**：饱满厚重的颜料色块，笔触间的色彩混合与破色，低频大色块 + 高频点睛笔触
- **构图**：弱线稿/无线稿，以块面塑形，笔触方向顺应结构，主体体积感突出
- **参照**：概念设计厚涂、游戏原画立绘、contemporary digital painterly
- **场景/氛围**：角色立绘/幻想场景/概念设计，厚重、有力、质感强烈的绘画氛围

## 提示词构成模块
> 完整结构：**风格 - 媒材 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | thick-paint impasto digital illustration, painterly concept-art rendering |
| 媒材 Medium | chunky bold brushstrokes, minimal-to-no line art, volume built by paint blocks |
| 打光 Lighting | strong volumetric light, defined terminator line, dramatic key light modeling form, warm-cool contrast |
| 色彩 Color | rich thick paint color blocks, color mixing and broken-color in strokes, low-frequency masses plus high-frequency accent strokes |
| 构图 Composition | lineless form sculpting, brushstroke direction following structure, strong volumetric subject |
| 画家参照 Artist Ref | bold concept-art impasto, game key-art splash, contemporary digital painterly |
| 场景/氛围 Scene | character key-art fantasy scenes concept design, thick powerful painterly mood |

## 结构化提示词（English · 推荐）
```
thick-paint impasto digital illustration, painterly concept-art rendering - chunky bold brushstrokes, minimal-to-no line art, volume built by paint blocks - [strong volumetric light, defined terminator line, dramatic key light modeling form, warm-cool contrast] + [rich thick paint color blocks, color mixing and broken-color in strokes, low-frequency masses plus high-frequency accent strokes] + [lineless form sculpting, brushstroke direction following structure, strong volumetric subject] + [bold concept-art impasto, game key-art splash, contemporary digital painterly] + [character key-art fantasy scenes concept design, thick powerful painterly mood], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
厚涂数字绘画插画风格，厚重成块的笔触堆叠、弱化或无清晰线稿、以色彩体积塑形，对标概念设计厚涂与游戏原画立绘，强烈的体积光影与明确的明暗交界线、戏剧性主光塑造立体感与冷暖对比，饱满厚重的颜料色块与笔触间的破色混色、低频大色块加高频点睛笔触，笔触方向顺应结构的无线稿块面塑形与突出的主体体积感，角色立绘/幻想场景/概念设计题材，厚重有力而质感强烈的绘画氛围
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 物件）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是**厚涂笔触塑形**：保留 "impasto, bold brushstrokes, painterly, lineless"；避免 clean line art / cel-shaded / flat-color（会破坏厚涂感）；想更强笔触可加 "visible impasto, palette-knife texture"，更偏概念设计可加 "concept art splash, matte painting"。
4. 可按需替换 [打光]/[色彩]/[构图]/[画家参照]/[场景] 模块强化或微调风格倾向。
