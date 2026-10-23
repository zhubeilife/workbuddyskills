风格 ID：`style-wes-anderson`
原目录：`资产-韦斯安德森风`

# 对称粉彩作者风 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：作者电影
- **标准名**：对称粉彩作者风
- **原名**（内部标识，不外显）：韦斯安德森风
- **题材定位**：对称粉彩作者电影美学，完美对称构图，策展级粉彩配色，玩偶屋式精确布景的写实画面

## 风格参考（Reference）
对称粉彩作者电影（欧洲大饭店喜剧、杂志社群像、定格动画寓言）；强调绝对对称、居中构图、粉彩策展调色板（粉/黄/青）、正面平光、舞台化精确布景，**区别于手持写实与自然光**。

## 第一性拆解（Style Decomposition）
- **打光**：均匀正面平光（flat front light），无戏剧性阴影，柔和填充，布景如舞台般被均匀照亮
- **色彩**：策展级粉彩——粉红、鹅黄、青蓝、薄荷绿，配色经过精确搭配，高辨识度但克制，轻微褪色胶片感
- **构图**：**绝对对称**与居中，正对镜头（dead-on），玩偶屋式框中框，横向平移运镜暗示，三分法严格居中
- **参照**：symmetrical pastel auteur cinema, meticulous storybook realism
- **场景/氛围**：舞台化精确 interior/exterior，复古家具与道具高度整齐，童话书般的秩序感与轻微怪诞

## 提示词构成模块
> 完整结构：**风格 - 摄影/镜头参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | symmetrical auteur aesthetic, symmetrical pastel storybook realism, meticulously staged live-action |
| 摄影/镜头 Lens | centered composition, dead-on angle, flat frontal, lateral tracking暗示, 35mm, slight vintage |
| 打光 Lighting | even flat front light, no dramatic shadow, soft fill, stage-like uniform illumination |
| 色彩 Color | curated pastel palette, pink, canary yellow, teal blue, mint green, precisely paired, slightly faded |
| 构图 Composition | perfect symmetry, dead-center framing, dollhouse frame-within-frame, strict rule-of-thirds center |
| 美术参照 Art Ref | symmetrical pastel auteur cinema, dollhouse stop-motion whimsy, meticulous storybook realism |
| 场景/氛围 Scene | stage-like precise interior/exterior, retro tidy props/furniture, storybook order with slight whimsy |

## 结构化提示词（English · 推荐）
```
symmetrical auteur aesthetic, symmetrical pastel storybook realism, meticulously staged live-action - centered composition, dead-on angle, flat frontal, lateral tracking hint, 35mm, slight vintage - [even flat front light, no dramatic shadow, soft fill, stage-like uniform illumination] + [curated pastel palette, pink, canary yellow, teal blue, mint green, precisely paired, slightly faded] + [perfect symmetry, dead-center framing, dollhouse frame-within-frame, strict rule-of-thirds center] + [symmetrical pastel auteur cinema, dollhouse stop-motion whimsy, meticulous storybook realism] + [stage-like precise interior/exterior, retro tidy props and furniture, storybook order with slight whimsy], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
对称粉彩作者电影美学，完美对称构图，策展级粉彩配色的玩偶屋式精确布景写实画面。均匀正面平光，无戏剧性阴影，柔和填充，布景如舞台般被均匀照亮。策展级粉彩——粉红、鹅黄、青蓝、薄荷绿，配色精确搭配、轻微褪色。绝对对称与居中，正对镜头，玩偶屋式框中框，三分法严格居中。舞台化精确 interior/exterior，复古家具与道具高度整齐，童话书般的秩序感与轻微怪诞
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **绝对对称 + 粉彩策展配色 + 正面平光**：避免手持写实、自然光硬影、任意构图。
4. 强化对称可加 "perfect bilateral symmetry, centered subject, mirror composition"；强化粉彩可加 "pastel pink and yellow, candy-box hotel palette"。
5. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
