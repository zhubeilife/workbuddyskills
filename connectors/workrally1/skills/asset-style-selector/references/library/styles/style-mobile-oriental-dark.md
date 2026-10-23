风格 ID：`style-mobile-oriental-dark`
原目录：`资产-手游unity`

# 东方暗黑手游 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：东方暗黑手游
- **原名**（内部标识，不外显）：手游unity

## 风格参考（Reference）
东方神魔动作游戏、和风妖怪手游、中式神魔次世代

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Chinese dark mytho-demonic next-gen render |
| 相机/渲染器 Camera/Renderer | Unreal-grade render, cinematic GI, volumetric buddha-light |
| 打光 Lighting | volumetric light piercing smoke, strong chiaroscuro |
| 色彩 Color | crimson, indigo, gilt, dark black |
| 构图 Composition | layered temple/cliff/cloud depth, divine majesty staging |
| 画家参照 Painter Ref | 中式神魔美术, 古典人物工笔 + 超写实 |
| 场景/氛围 Scene | ancient temple and cliffs, divine-demonic majesty |

## 结构化提示词（English · 推荐）
```
Chinese dark mytho-demonic next-gen render - Unreal-grade render, cinematic GI, volumetric buddha-light - [volumetric light piercing smoke, strong chiaroscuro] + [crimson, indigo, gilt, dark black] + [layered temple/cliff/cloud depth, divine majesty staging] + [中式神魔美术, 古典人物工笔 + 超写实] + [ancient temple and cliffs, divine-demonic majesty], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
中式暗黑神魔次世代写实渲染，虚幻引擎级毛发、皮革、青铜、岩石与丝绸材质精雕，电影化全局光照与体积光穿透烟雾佛光，浓郁东方质感的丹红、青黛、鎏金与玄黑交织，明暗对比强烈塑造神魔威仪，古刹、山岩、云海层叠景深，氛围庄严肃穆、瑰丽诡谲而磅礴沉郁，兼具东方水墨意境与超写实细节。
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
