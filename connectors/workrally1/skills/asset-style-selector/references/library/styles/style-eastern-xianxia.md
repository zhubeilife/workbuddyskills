风格 ID：`style-eastern-xianxia`
原目录：`资产-东方仙侠`

# 写实东方仙侠 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：奇幻/神话/魔幻现实
- **标准名**：写实东方仙侠
- **原名**（内部标识，不外显）：东方仙侠

## 风格参考（Reference）
仙侠游戏与仙侠剧仙境、宋代青绿山水

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Eastern xianxia immortal-fantasy |
| 相机/渲染器 Camera/Renderer | soft 50mm, dreamy diffusion, glowing bloom |
| 打光 Lighting | ethereal spiritual glow, floating light particles, volumetric |
| 色彩 Color | cyan-jade, pale violet, flowing gold |
| 构图 Composition | floating mountains, layered cloud-sea depth, airy negative space |
| 画家参照 Painter Ref | 宋代山水, 古典人物工笔 |
| 场景/氛围 Scene | cloud-sea fairy mountains, jade pavilions, spirit aura |

## 结构化提示词（English · 推荐）
```
Eastern xianxia immortal-fantasy - soft 50mm, dreamy diffusion, glowing bloom - [ethereal spiritual glow, floating light particles, volumetric] + [cyan-jade, pale violet, flowing gold] + [floating mountains, layered cloud-sea depth, airy negative space] + [宋代山水, 古典人物工笔] + [cloud-sea fairy mountains, jade pavilions, spirit aura], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
东方仙侠风格，缥缈梦幻的仙气质感，云海仙山与琼楼玉宇的瑰丽幻境，流光溢彩的灵气光效与飘浮光粒，通透的青碧、淡紫与流金色调，柔美梦幻的光晕与体积光，飘逸灵动的仙灵氛围，唯美瑰丽的东方幻想美学，电影级梦幻渲染
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
