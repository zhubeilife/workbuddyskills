风格 ID：`style-low-poly`
原目录：`资产-低多边形`

# 低多边形 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D风格化
- **标准名**：低多边形
- **原名**（内部标识，不外显）：低多边形
- **题材定位**：3D 风格化低面数渲染，分明面片与几何化简洁造型，游戏低模美术

## 风格参考（Reference）
Low-poly 3D 艺术、几何解谜独立游戏、独立游戏低模风格、Blender low-poly 社区；强调 faceted 面片感、flat shading 平面着色、块状纯色，**区别于高模写实与平滑曲面**。

## 第一性拆解（Style Decomposition）
- **打光**：平面着色（flat shading），柔和均匀环境光 + 轻方向光，无复杂反射与高光，哑光表面
- **色彩**：块状纯色，高饱和或柔和粉彩，色块分明、边界清晰
- **构图**：几何化简洁，等距视角（isometric）或低角度，可见多边形面片，留白克制
- **参照**：low-poly 游戏美术、极简 3D 设计
- **场景/氛围**：低面数地形、低模植被与角色、风格化低多边形世界，清新或梦幻

## 提示词构成模块
> 完整结构：**风格 - 渲染器/参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Low poly 3D render, stylized faceted geometry, 3D game art |
| 渲染器 Renderer | Blender / Unreal Engine low-poly, flat shading, isometric low angle |
| 打光 Lighting | soft ambient light, gentle directional fill, matte flat surfaces, no reflections |
| 色彩 Color | block color palette, saturated or pastel color blocks, clean color separation |
| 构图 Composition | geometric simplified forms, isometric or low-angle view, visible polygon facets |
| 美术参照 Art Ref | low-poly game art direction, minimalist 3D |
| 场景/氛围 Scene | low-poly terrain, faceted characters, stylized low-poly environment |

## 结构化提示词（English · 推荐）
```
Low poly 3D render, stylized faceted geometry, 3D game art - Blender / Unreal Engine low-poly, flat shading, isometric low angle - [soft ambient light, gentle directional fill, matte flat surfaces, no reflections] + [block color palette, saturated or pastel color blocks, clean color separation] + [geometric simplified forms, isometric or low-angle view, visible polygon facets] + [low-poly game art direction, minimalist 3D] + [low-poly terrain, faceted characters, stylized low-poly environment], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
低多边形 3D 渲染风格，平面着色与分明面片感，几何化简洁造型，等距或低角度视角，块状纯色与柔和粉彩分明色块，无复杂反射的哑光表面，低面数地形与低模角色构成的风格化世界
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 物件）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格为**3D 风格化低模**：避免 photorealistic / high-poly / smooth surface 等词；想强化低模感可加 "hard edges, visible triangles, low mesh count"。
4. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
