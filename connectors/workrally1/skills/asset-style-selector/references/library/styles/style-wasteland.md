风格 ID：`style-wasteland`
原目录：`资产-废土`

# 写实废土 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：科幻
- **标准名**：写实废土
- **原名**（内部标识，不外显）：废土

## 风格参考（Reference）
末世公路动作电影、末世废土游戏、复古科幻废土绘画

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Post-apocalyptic wasteland |
| 相机/渲染器 Camera/Renderer | dusty 35mm, vintage anamorphic, sun-flared |
| 打光 Lighting | harsh overhead sunlight, dust-scattered haze |
| 色彩 Color | dull yellow, scorched brown, rust, high contrast |
| 构图 Composition | vast desolate horizon, lone figure, gritty foreground |
| 画家参照 Painter Ref | 末世公路动作电影美术, retro-futurist rural sci-fi painting |
| 场景/氛围 Scene | sandstorm ruins, weathered rusted machinery |

## 结构化提示词（English · 推荐）
```
Post-apocalyptic wasteland - dusty 35mm, vintage anamorphic, sun-flared - [harsh overhead sunlight, dust-scattered haze] + [dull yellow, scorched brown, rust, high contrast] + [vast desolate horizon, lone figure, gritty foreground] + [末世公路动作电影美术, retro-futurist rural sci-fi painting] + [sandstorm ruins, weathered rusted machinery], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
废土末世风格，荒凉粗粝的末日质感，风沙弥漫的昏黄褪色调与锈蚀斑驳材质，强烈的烈日硬光与扬尘氛围，破败磨损的做旧肌理，高对比的土黄与焦褐色调，苍茫孤寂的末世氛围，电影级颗粒质感，4K 写实渲染
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
