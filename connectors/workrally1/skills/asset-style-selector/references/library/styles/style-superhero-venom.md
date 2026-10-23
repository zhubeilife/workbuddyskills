风格 ID：`style-superhero-venom`
原目录：`资产-超级英雄（毒液）`

# 暗黑反英雄 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：科幻超英
- **标准名**：暗黑反英雄
- **原名**（内部标识，不外显）：超级英雄（毒液）
- **题材定位**：真人写实黑暗超英大片，共生体/反英雄基调，强戏剧化都市夜战

## 风格参考（Reference）
共生体反英雄电影系列、暗黑超英宇宙；强调 symbiote 湿黑黏液质感、反英雄粗粝暴力美学，**区别于明亮的主流超英与卡通超英**。

## 第一性拆解（Style Decomposition）
- **打光**：高反差硬光 + 霓虹夜色，湿滑高光沿黑色黏液流动，边缘冷蓝/毒绿描边光
- **色彩**：极暗基调，漆黑主体 + 都市霓虹（毒绿、赛博蓝、警灯红）点缀，去饱和阴影
- **构图**：低角度仰拍强化压迫感，广角变形，动态倾斜，湿地面反射霓虹
- **参照**：高反差硬光摄影；暗黑超英美术
- **场景/氛围**：symbiote 触手黏液缠绕、獠牙巨口、雨夜后巷与集装箱码头、暴力张力

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数 - [打光方案] + [色彩调性] + [构图描述] + [摄影师参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Dark superhero blockbuster, symbiote anti-hero, photorealistic cinematic |
| 相机/胶片 Camera/Film | 35mm anamorphic, film grain, low-angle wide lens |
| 打光 Lighting | high-contrast hard light, neon night glow, wet specular highlights, cold rim light |
| 色彩 Color | near-black base, toxic-green and cyber-blue neon accents, desaturated shadows |
| 构图 Composition | low-angle intimidation, wide-lens distortion, dynamic tilt, rain-slick reflections |
| 摄影师参照 DP Ref | high-contrast hard-light cinematography, dark anti-hero art direction |
| 场景/氛围 Scene | glossy black symbiote tendrils, fanged maw, rainy back alleys and shipyards, violent tension |

## 结构化提示词（English · 推荐）
```
Dark superhero blockbuster, symbiote anti-hero, photorealistic cinematic - 35mm anamorphic, film grain, low-angle wide lens - [high-contrast hard light, neon night glow, wet specular highlights, cold rim light] + [near-black base, toxic-green and cyber-blue neon accents, desaturated shadows] + [low-angle intimidation, wide-lens distortion, dynamic tilt, rain-slick reflections] + [high-contrast hard-light cinematography, dark anti-hero art direction] + [glossy black symbiote tendrils, fanged maw, rainy back alleys and shipyards, violent tension], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
黑暗超级英雄大片写实风格，共生体湿黑黏液的流动高光与触手缠绕质感，漆黑主体搭配都市霓虹（毒绿、赛博蓝、警灯红）点缀，高反差硬光与雨夜霓虹，低角度仰拍广角变形的压迫感构图，湿滑地面的霓虹反射，反英雄的粗粝暴力张力，雨夜后巷与码头集装箱的都市战场氛围
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（人物 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格为**真人写实黑暗超英**：避免 anime/cartoon/bright-marvel 等词；想强化质感可加 "shot on film, wet glossy skin, chromatic neon reflections"。
4. 可按需替换 [打光]/[色彩]/[构图]/[参照]/[场景] 模块强化或微调风格倾向。
