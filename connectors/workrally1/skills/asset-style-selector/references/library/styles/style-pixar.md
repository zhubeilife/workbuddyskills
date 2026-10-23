风格 ID：`style-pixar`
原目录：`资产-皮克斯`

# 温情合家欢3D动画 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：美式3D风格
- **标准名**：温情合家欢3D动画
- **原名**（内部标识，不外显）：皮克斯

## 风格参考（Reference）
温情合家欢 3D 动画长片、中世纪现代主义插画色彩

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | heartwarming family 3D animated film |
| 相机/渲染器 Camera/Renderer | 3D render, RenderMan, cinematic lighting |
| 打光 Lighting | soft global illumination, fine ambient occlusion, expressive key |
| 色彩 Color | warm bright richly-layered palette |
| 构图 Composition | appealing rounded character staging, clear read |
| 画家参照 Painter Ref | family feature animation art direction, mid-century modernist illustration color |
| 场景/氛围 Scene | heartwarming character moment, healing narrative |

## 结构化提示词（English · 推荐）
```
heartwarming family 3D animated film - 3D render, RenderMan, cinematic lighting - [soft global illumination, fine ambient occlusion, expressive key] + [warm bright richly-layered palette] + [appealing rounded character staging, clear read] + [family feature animation art direction, mid-century modernist illustration color] + [heartwarming character moment, healing narrative], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
温情合家欢 3D 动画电影风格，圆润讨喜的角色造型设计，细腻柔润的次表面散射皮肤质感，温暖明快而富有层次的色彩，柔和的全局光照与细腻的环境光遮蔽，富有表现力的电影级布光，精致的材质纹理与微妙高光，温馨治愈的叙事氛围，顶级电影工业级的高品质渲染
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
