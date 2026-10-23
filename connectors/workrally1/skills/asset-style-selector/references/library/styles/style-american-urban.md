风格 ID：`style-american-urban`
原目录：`资产-美式都市`

# 美式街头写实 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：美式都市写实
- **标准名**：美式街头写实
- **原名**（内部标识，不外显）：美式都市
- **题材定位**：美国都市实景电影质感，街头级写实摄影，霓虹与水泥并置的城市张力

## 风格参考（Reference）
美式都市电影（街头犯罪片、黑帮片）、当代美剧都市罪案、开放世界写实游戏实机；强调街道级真实感、实用光源（霓虹/路灯/车灯）、好莱坞青橙调色，**区别于欧式文艺与日系清透**。

## 第一性拆解（Style Decomposition）
- **打光**：实用光源主导——钠灯暖橙、霓虹冷蓝、车头灯束、橱窗补光；硬顶光或夜晚城市辉光，阴影写实有颗粒
- **色彩**：好莱坞青橙对比（teal-orange），暖橙高光 × 冷青暗部，霓虹撞色点缀，城市湿地面反射
- **构图**：宽银幕变形镜头（anamorphic）城市远景、街道级手持跟拍、框中框取景、霓虹招牌入画
- **参照**：American urban cinema, open-world photoreal game look, NYC/LA/Chicago street realism
- **场景/氛围**：真实都市肌理——混凝土地面、玻璃幕墙、沥青、斑驳招牌、雨后反光，充满生活粗粝感

## 提示词构成模块
> 完整结构：**风格 - 摄影/镜头参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | American urban cinematic realism, street-level city photography, open-world photoreal game aesthetic |
| 摄影/镜头 Lens | anamorphic widescreen, 35mm, shallow DOF, practical light sources |
| 打光 Lighting | sodium-vapor warm orange, neon cool blue, car headlight beams, storefront fill, hard overhead or night city glow |
| 色彩 Color | teal-orange Hollywood grade, warm highlights × cool shadows, neon clash accents, wet street reflections |
| 构图 Composition | widescreen establishing shot, street-level handheld follow, frame-within-frame, neon signage in frame |
| 美术参照 Art Ref | American urban cinema, open-world photoreal game look, NYC/LA/Chicago street realism |
| 场景/氛围 Scene | real urban texture, concrete, glass facades, asphalt, weathered signage, rain reflections, gritty lived-in feel |

## 结构化提示词（English · 推荐）
```
American urban cinematic realism, street-level city photography, open-world photoreal game aesthetic - anamorphic widescreen, 35mm, shallow DOF, practical light sources - [sodium-vapor warm orange, neon cool blue, car headlight beams, storefront fill, hard overhead or night city glow] + [teal-orange Hollywood grade, warm highlights × cool shadows, neon clash accents, wet street reflections] + [widescreen establishing shot, street-level handheld follow, frame-within-frame, neon signage in frame] + [American urban cinema, open-world photoreal game look, NYC/LA/Chicago street realism] + [real urban texture, concrete, glass facades, asphalt, weathered signage, rain reflections, gritty lived-in feel], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
美式都市实景电影质感，街头级写实摄影，开放世界写实游戏实机美学。实用光源主导——钠灯暖橙、霓虹冷蓝、车头灯束、橱窗补光，硬顶光或夜晚城市辉光。好莱坞青橙调色，暖橙高光与冷青暗部对比，霓虹撞色点缀，雨后湿地面反射。宽银幕变形镜头城市远景与街道级手持跟拍，框中框取景，霓虹招牌入画。真实都市肌理——混凝土地面、玻璃幕墙、沥青、斑驳招牌、雨后反光，充满生活粗粝感
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格为**美式都市写实**：核心是 street-level 真实感 + 实用光源 + 青橙调色；避免 euro-art 的朦胧柔焦与日系的清透过曝。
4. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
