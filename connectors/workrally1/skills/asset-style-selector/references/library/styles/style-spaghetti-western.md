风格 ID：`style-spaghetti-western`
原目录：`资产-经典西部牛仔`

# 西部牛仔 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：西部/荒野/公路
- **标准名**：西部牛仔
- **原名**（内部标识，不外显）：经典西部牛仔

## 风格参考（Reference）
意式西部片、西部题材写实油画

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Spaghetti western |
| 相机/渲染器 Camera/Renderer | Techniscope 35mm, vintage anamorphic, sun flare |
| 打光 Lighting | harsh blinding sun, heavy raking shadow |
| 色彩 Color | scorched amber, rust-red, dark brown |
| 构图 Composition | extreme close-up vs wide vista juxtaposition |
| 画家参照 Painter Ref | 意式西部片构图, western frontier realist painting |
| 场景/氛围 Scene | sun-baked desert town, dust and sweat tension |

## 结构化提示词（English · 推荐）
```
Spaghetti western - Techniscope 35mm, vintage anamorphic, sun flare - [harsh blinding sun, heavy raking shadow] + [scorched amber, rust-red, dark brown] + [extreme close-up vs wide vista juxtaposition] + [意式西部片构图, western frontier realist painting] + [sun-baked desert town, dust and sweat tension], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
意式西部片视觉风格，戏剧化高反差的凝滞张力质感，强烈刺目的烈日硬光与浓重阴影，焦黄、铁锈红与暗褐的灼热色调，凝滞紧绷的极端特写与广角并置，粗犷的尘土与汗渍质感，浓烈的胶片颗粒与压迫感氛围，里昂式西部的电影级渲染
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（人物 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 末尾「统一质感尾缀」已内置于结构化提示词，单独使用其他描述时也建议手动追加，保证全库风格统一的胶片柔焦质感。
4. 可按需替换 [打光]/[色彩]/[构图]/[画家参照]/[场景] 模块强化或微调风格倾向。
