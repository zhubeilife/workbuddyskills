风格 ID：`style-aaa-game-realism`
原目录：`资产-3A游戏-主流写实`

# 写实游戏CG · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：写实游戏CG
- **原名**（内部标识，不外显）：3A游戏-主流写实

## 风格参考（Reference）
3A 叙事动作游戏过场、写实末世与神话动作游戏、次世代实时渲染质感

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | AAA game cinematic CG |
| 相机/渲染器 Camera/Renderer | Unreal Engine 5, Lumen + ray tracing, cinematic 35mm |
| 打光 Lighting | global illumination, cinematic dynamic light, volumetric |
| 色彩 Color | dramatic high-contrast immersive grade |
| 构图 Composition | dramatic hero composition, 8K detail |
| 画家参照 Painter Ref | 顶级叙事 3A 美术 |
| 场景/氛围 Scene | cinematic game cutscene, immersive realistic world |

## 结构化提示词（English · 推荐）
```
AAA game cinematic CG - Unreal Engine 5, Lumen + ray tracing, cinematic 35mm - [global illumination, cinematic dynamic light, volumetric] + [dramatic high-contrast immersive grade] + [dramatic hero composition, 8K detail] + [顶级叙事 3A 美术] + [cinematic game cutscene, immersive realistic world], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
3A 游戏过场 CG 画质，超写实电影级渲染，虚幻引擎 5 质感，全局光照与光线追踪，电影级动态光影，丰富的材质细节与微表面反射，戏剧化构图，高对比沉浸氛围，8K 超清，体积光
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
