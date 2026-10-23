风格 ID：`style-wuxia`
原目录：`资产-武侠`

# 写实武侠 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：历史/古装/年代正剧
- **标准名**：写实武侠
- **原名**（内部标识，不外显）：武侠

## 风格参考（Reference）
唯美古装仙侠剧、明代仕女图、新艺术运动装饰画

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Ancient-style feminine wuxia |
| 相机/渲染器 Camera/Renderer | softened 85mm portrait lens, diffusion filter, shallow DOF |
| 打光 Lighting | soft dreamy warm light, gentle halation backlight |
| 色彩 Color | rouge-pink, lotus-violet, pale gold |
| 构图 Composition | poetic shallow-focus portrait, flowing fabric foreground |
| 画家参照 Painter Ref | 明代仕女图, Art Nouveau decorative illustration |
| 场景/氛围 Scene | misty courtyard, silk gauze, jade and pearl ornaments |

## 结构化提示词（English · 推荐）
```
Ancient-style feminine wuxia - softened 85mm portrait lens, diffusion filter, shallow DOF - [soft dreamy warm light, gentle halation backlight] + [rouge-pink, lotus-violet, pale gold] + [poetic shallow-focus portrait, flowing fabric foreground] + [明代仕女图, Art Nouveau decorative illustration] + [misty courtyard, silk gauze, jade and pearl ornaments], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
古风女频风格，唯美柔媚的古典娇丽质感，柔和梦幻的暖光与浅景深虚化，淡雅清丽的胭脂粉、藕荷与淡金色调，细腻的丝绸纱幔与珠翠材质质感，朦胧诗意的氛围光晕，精致唯美的人物刻画，高清细腻的古风电影级渲染
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
