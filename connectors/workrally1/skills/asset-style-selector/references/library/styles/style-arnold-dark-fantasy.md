风格 ID：`style-arnold-dark-fantasy`
原目录：`资产-游戏CG（阿诺德）`

# 暗黑奇幻游戏CG · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：暗黑奇幻游戏CG
- **原名**（内部标识，不外显）：游戏CG（阿诺德）

## 风格参考（Reference）
暗黑魂系动作游戏、波兰暗黑超现实绘画、Arnold 渲染

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Dark-fantasy next-gen render |
| 相机/渲染器 Camera/Renderer | Arnold renderer, cinematic 50mm, fog depth |
| 打光 Lighting | soft melancholic natural light + golden-hour backlight |
| 色彩 Color | grey-brown, moss-green, dark gold + cold highlight |
| 构图 Composition | vast fog-shrouded depth, solemn lonely scale |
| 画家参照 Painter Ref | 暗黑魂系游戏美术, dystopian surreal decay painting |
| 场景/氛围 Scene | decayed sublime ruins, weathered stone, organic mutation |

## 结构化提示词（English · 推荐）
```
Dark-fantasy next-gen render - Arnold renderer, cinematic 50mm, fog depth - [soft melancholic natural light + golden-hour backlight] + [grey-brown, moss-green, dark gold + cold highlight] + [vast fog-shrouded depth, solemn lonely scale] + [暗黑魂系游戏美术, dystopian surreal decay painting] + [decayed sublime ruins, weathered stone, organic mutation], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
暗黑奇幻次世代渲染，宏大苍凉的写实质感，斑驳金属、风化石材、腐朽织物与有机异变细节精微，柔和而忧郁的自然光与黄金时刻逆光交织，雾气弥漫的辽阔景深，低饱和的灰褐、青苔绿与暗金调点缀幽冷高光，氛围庄严、孤寂、衰败而崇高，弥漫宿命与神性的史诗感。
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
