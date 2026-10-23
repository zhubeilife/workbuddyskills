风格 ID：`style-european-misty`
原目录：`资产-欧洲朦胧雾风`

# 欧洲雾感写实 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：欧洲氛围写实
- **标准名**：欧洲雾感写实
- **原名**（内部标识，不外显）：欧洲朦胧雾风
- **题材定位**：欧洲艺术电影式朦胧雾气氛围，柔和漫射光中的层叠景深，静谧诗意的写实质感

## 风格参考（Reference）
欧洲艺术电影（诗意公路片、乡愁长镜头、现代主义悬疑片）、阿尔卑斯与北欧雾中村落、新表现主义式灰调地景；强调漫射柔光、空气透视（atmospheric perspective）、极低反差、冷灰调，**区别于美式硬光都市与日系清透高调**。

## 第一性拆解（Style Decomposition）
- **打光**：阴天/晨雾的均匀漫射光，无明确方向硬光，雾气散射柔化一切边缘，微弱逆光勾出轮廓
- **色彩**：去饱和冷灰体系——灰绿、雾蓝、骨白、淡褐，整体低对比，色彩被雾气"洗白"
- **构图**：大气透视层叠（近景清晰→中景灰→远景消融），留白式空旷构图，地平线偏低营造苍茫
- **参照**：European art cinema, contemplative long-take haze, foggy Alpine/Nordic village, muted landscape
- **场景/氛围**：静谧诗意的欧洲地景——雾中森林、湖畔、石桥古镇、旷野，时间仿佛凝固的孤独感

## 提示词构成模块
> 完整结构：**风格 - 摄影/镜头参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀（强调柔焦/低对比/雾气）。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | European misty atmospheric cinema, foggy dreamy European landscape, contemplative long-take haze |
| 摄影/镜头 Lens | soft-focus lens, moderate DOF, atmospheric perspective, low contrast, 35mm |
| 打光 Lighting | overcast/dawn fog diffuse light, no hard directional, mist scattering softens edges, faint backlight rim |
| 色彩 Color | desaturated cool-grey palette, grey-green, mist-blue, bone white, pale umber, washed-out low contrast |
| 构图 Composition | atmospheric perspective layering, negative-space empty framing, low horizon for vastness |
| 美术参照 Art Ref | European art cinema, contemplative long-take haze, foggy Alpine/Nordic village, neo-expressionist grey landscape |
| 场景/氛围 Scene | silent poetic European terrain, misty forest, lakeside, stone-bridge old town, frozen-time solitude |

## 结构化提示词（English · 推荐）
```
European misty atmospheric cinema, foggy dreamy European landscape, contemplative long-take haze - soft-focus lens, moderate DOF, atmospheric perspective, low contrast, 35mm - [overcast/dawn fog diffuse light, no hard directional, mist scattering softens edges, faint backlight rim] + [desaturated cool-grey palette, grey-green, mist-blue, bone white, pale umber, washed-out low contrast] + [atmospheric perspective layering, negative-space empty framing, low horizon for vastness] + [European art cinema, contemplative long-take haze, foggy Alpine/Nordic village, neo-expressionist grey landscape] + [silent poetic European terrain, misty forest, lakeside, stone-bridge old town, frozen-time solitude], soft focus edges, gentle edge falloff, heavy atmospheric haze, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
欧洲艺术电影式朦胧雾气氛围，柔和漫射光中的层叠景深，静谧诗意的写实质感。阴天或晨雾的均匀漫射光，无明确方向硬光，雾气散射柔化一切边缘，微弱逆光勾出轮廓。去饱和冷灰体系——灰绿、雾蓝、骨白、淡褐，整体低对比，色彩被雾气洗白。大气透视层叠（近景清晰→中景灰→远景消融），留白式空旷构图，地平线偏低营造苍茫。静谧诗意的欧洲地景——雾中森林、湖畔、石桥古镇、旷野，时间仿佛凝固的孤独感
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, heavy atmospheric haze, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **朦胧雾气 + 低反差冷灰 + 大气透视**：避免美式硬光青橙、日系高调过曝、强对比。
4. 想强化雾气可加 "thick fog, volumetric mist, aerial perspective, whiteout haze"；想偏北欧冷峻可加 "Nordic noir, frozen lake, pine forest"。
5. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
