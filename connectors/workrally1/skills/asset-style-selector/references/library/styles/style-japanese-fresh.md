风格 ID：`style-japanese-fresh`
原目录：`资产-日系小清新`

# 日系清新写真 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：日系写真
- **标准名**：日系清新写真
- **原名**（内部标识，不外显）：日系小清新
- **题材定位**：日系清新写真质感，明亮通透的日常瞬间，柔和高调与淡彩的呼吸感

## 风格参考（Reference）
日系胶片写真（光感日常摄影）、日系电视剧（晨间剧/dorama）、富士胶卷（Fuji Provia/Velvia）清新调；强调明亮高调、柔光、淡彩、轻微漏光与颗粒、生活化随意构图，**区别于美式硬光与欧式灰雾**。

## 第一性拆解（Style Decomposition）
- **打光**：柔和的漫射自然日光（窗边/树荫/阴天），高调明亮，无硬阴影，偶有逆光发丝光
- **色彩**：清新淡彩——奶油白、淡粉、天蓝、嫩绿，低对比柔和过渡，Fuji 绿的轻微偏色，高光干净
- **构图**：生活化随意（snap shot），浅景深特写，留白透气，日常小物与人物自然交融，非刻意摆拍
- **参照**：Japanese fresh film photography, luminous everyday snapshot, Fuji Provia, airy pastel everyday
- **场景/氛围**：清新日常——樱花、和室、咖啡馆、海边、制服少女，宁静治愈的呼吸感

## 提示词构成模块
> 完整结构：**风格 - 摄影/镜头参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀（强调柔光/高调/轻微漏光）。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Japanese fresh light photography, airy pastel everyday moment, luminous everyday snapshot style, soft high-key |
| 摄影/镜头 Lens | 35mm/50mm, shallow DOF, soft daylight, Fuji film emulation, slight light leak |
| 打光 Lighting | soft diffuse natural daylight (window/shade/overcast), high-key bright, no hard shadow, occasional backlight hair light |
| 色彩 Color | fresh pastel, cream white, pale pink, sky blue, tender green, low-contrast soft transition, Fuji green tint, clean highlights |
| 构图 Composition | lifestyle candid snap, shallow-DOF close-up, breathable negative space, daily objects with natural figure |
| 美术参照 Art Ref | Japanese fresh film photography, luminous everyday snapshot, Fuji Provia/Velvia, airy pastel everyday |
| 场景/氛围 Scene | fresh daily life, cherry blossom, tatami room, cafe, seaside, school-uniform girl, calm healing breath |

## 结构化提示词（English · 推荐）
```
Japanese fresh light photography, airy pastel everyday moment, luminous everyday snapshot style, soft high-key - 35mm/50mm, shallow DOF, soft daylight, Fuji film emulation, slight light leak - [soft diffuse natural daylight (window/shade/overcast), high-key bright, no hard shadow, occasional backlight hair light] + [fresh pastel, cream white, pale pink, sky blue, tender green, low-contrast soft transition, Fuji green tint, clean highlights] + [lifestyle candid snap, shallow-DOF close-up, breathable negative space, daily objects with natural figure] + [Japanese fresh film photography, luminous everyday snapshot, Fuji Provia/Velvia, airy pastel everyday] + [fresh daily life, cherry blossom, tatami room, cafe, seaside, school-uniform girl, calm healing breath], soft focus edges, gentle edge falloff, light leak, soft film grain, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
日系清新写真质感，明亮通透的日常瞬间，柔和高调与淡彩的呼吸感。柔和的漫射自然日光（窗边/树荫/阴天），高调明亮无硬阴影，偶有逆光发丝光。清新淡彩——奶油白、淡粉、天蓝、嫩绿，低对比柔和过渡，富士绿轻微偏色，高光干净。生活化随意抓拍，浅景深特写，留白透气，日常小物与人物自然交融。清新日常——樱花、和室、咖啡馆、海边、制服少女，宁静治愈的呼吸感
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, light leak, soft film grain, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **明亮高调 + 淡彩柔光 + 生活化随意**：避免美式硬光青橙、欧式低反差灰雾、强对比。
4. 强化清新可加 "Fuji Provia, high-key, airy, soft daylight, light leak"；想偏少女感可加 "school uniform, cherry blossom, candid smile"。
5. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
