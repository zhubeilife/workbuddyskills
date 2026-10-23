风格 ID：`style-unreal-engine-military`
原目录：`资产-虚幻引擎`

# 硬核战场实时渲染 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：硬核战场实时渲染
- **原名**（内部标识，不外显）：虚幻引擎

## 风格参考（Reference）
现代军事射击游戏、次世代军事渲染

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Next-gen military realistic render |
| 相机/渲染器 Camera/Renderer | Unreal Engine, PBR, volumetric, film grain + chromatic aberration |
| 打光 Lighting | cinematic GI + volumetric light, dust and fire glow |
| 色彩 Color | cold grey-blue dark battlefield + explosion warm pop |
| 构图 Composition | hard taut framing, lens flare, depth of field |
| 画家参照 Painter Ref | 现代军事射击游戏美术, 战地纪实 |
| 场景/氛围 Scene | grim high-intensity battlefield, mud and wear |

## 结构化提示词（English · 推荐）
```
Next-gen military realistic render - Unreal Engine, PBR, volumetric, film grain + chromatic aberration - [cinematic GI + volumetric light, dust and fire glow] + [cold grey-blue dark battlefield + explosion warm pop] + [hard taut framing, lens flare, depth of field] + [现代军事射击游戏美术, 战地纪实] + [grim high-intensity battlefield, mud and wear], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
次世代军事写实渲染，高精度 PBR 物理材质，金属、布料、泥污与磨损细节逼真，电影化全局光照与体积光，烟尘、火光、镜头眩光与景深营造临场感，冷峻的青灰与暗调战场色调点缀爆炸暖光，画面硬朗紧绷，胶片颗粒与轻微色差强化纪实感，氛围肃杀、压迫而高强度。
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
