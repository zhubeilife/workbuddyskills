风格 ID：`style-plush`
原目录：`资产-毛绒`

# 毛绒玩偶3D · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：毛绒玩偶3D
- **原名**（内部标识，不外显）：毛绒

## 风格参考（Reference）
高端毛绒玩偶、潮玩毛绒、治愈系萌物

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Plush-toy 3D render |
| 相机/渲染器 Camera/Renderer | 3D render, macro fur shader, studio softbox |
| 打光 Lighting | soft even studio light, fine ambient occlusion |
| 色彩 Color | warm healing high-saturation candy palette |
| 构图 Composition | centered adorable kawaii subject, clean backdrop |
| 画家参照 Painter Ref | 高端毛绒玩偶质感, 萌系IP设计 |
| 场景/氛围 Scene | cozy kawaii plush character, stitched fabric detail |

## 结构化提示词（English · 推荐）
```
Plush-toy 3D render - 3D render, macro fur shader, studio softbox - [soft even studio light, fine ambient occlusion] + [warm healing high-saturation candy palette] + [centered adorable kawaii subject, clean backdrop] + [高端毛绒玩偶质感, 萌系IP设计] + [cozy kawaii plush character, stitched fabric detail], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
毛绒玩偶3D渲染风格，柔软蓬松的绒毛纤维质感，根根分明的细腻毛发与微妙绒光，圆润讨喜的萌系造型，温暖治愈的高饱和糖果色调，柔和均匀的影棚柔光与细腻环境光遮蔽，针线缝合与布料肌理的手作细节，软萌温馨而治愈的氛围，触感真实的高精度毛绒材质渲染
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
