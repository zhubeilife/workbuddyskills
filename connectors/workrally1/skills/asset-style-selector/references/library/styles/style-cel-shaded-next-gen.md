风格 ID：`style-cel-shaded-next-gen`
原目录：`资产-三渲二（原神，鸣潮）`

# 三渲二开放世界 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：三渲二开放世界
- **原名**（内部标识，不外显）：三渲二（原神，鸣潮）

## 风格参考（Reference）
新世代开放世界三渲二二次元游戏

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Cel-shaded next-gen anime render |
| 相机/渲染器 Camera/Renderer | 3D cel-shade render, anime-style bloom |
| 打光 Lighting | clean key + rim, holographic volumetric fog |
| 色彩 Color | magenta, electric blue, acid green, warm orange neon |
| 构图 Composition | open-world vista, layered neon depth |
| 画家参照 Painter Ref | 新世代二次元游戏美术, 二次元开放世界 |
| 场景/氛围 Scene | vibrant anime open-world, neon future city |

## 结构化提示词（English · 推荐）
```
Cel-shaded next-gen anime render - 3D cel-shade render, anime-style bloom - [clean key + rim, holographic volumetric fog] + [magenta, electric blue, acid green, warm orange neon] + [open-world vista, layered neon depth] + [新世代二次元游戏美术, 二次元开放世界] + [vibrant anime open-world, neon future city], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
赛博朋克次世代写实渲染，霓虹浸染的高密度未来都市质感，潮湿街面与玻璃幕墙强烈反射光污染，品红、电蓝、酸绿与暖橙霓虹交织，全息广告与体积光雾营造层层纵深，高对比暗调中点缀刺目高光，PBR 金属、皮革与全息材质精细，胶片颗粒与色差强化反乌托邦质感，氛围华丽、躁动、迷离而冷酷。
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
