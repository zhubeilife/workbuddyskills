风格 ID：`style-voxel-pixel-3d`
原目录：`资产-14 像素`

# 体素像素3D · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：体素像素3D
- **原名**（内部标识，不外显）：14 像素

## 风格参考（Reference）
几何解谜独立游戏、体素休闲游戏、体素低多边形

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Low-poly voxel pixel-3D |
| 相机/渲染器 Camera/Renderer | 3D render, isometric, flat shading |
| 打光 Lighting | soft even ambient light, slight gradient shadow |
| 色彩 Color | bright clean flat high-saturation palette |
| 构图 Composition | tidy isometric geometry, clean negative space |
| 画家参照 Painter Ref | 体素休闲游戏 / 几何解谜游戏美术 |
| 场景/氛围 Scene | playful minimal voxel world, geometric blocks |

## 结构化提示词（English · 推荐）
```
Low-poly voxel pixel-3D - 3D render, isometric, flat shading - [soft even ambient light, slight gradient shadow] + [bright clean flat high-saturation palette] + [tidy isometric geometry, clean negative space] + [体素休闲游戏 / 几何解谜游戏美术] + [playful minimal voxel world, geometric blocks], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
低多边形极简像素-3D 视觉风格，简约几何化的多边形块面与体素方块质感，清晰的棱面切割与平滑着色，明快纯净的扁平高饱和配色，柔和均匀的环境光与轻微渐变阴影，干净通透的极简空间氛围，规整讨喜的几何与像素美感，俏皮简约的高清三维渲染
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
