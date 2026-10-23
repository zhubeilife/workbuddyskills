风格 ID：`style-cyberpunk`
原目录：`资产-赛博朋克`

# 赛博朋克 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：科幻
- **标准名**：赛博朋克
- **原名**（内部标识，不外显）：赛博朋克

## 风格参考（Reference）
经典赛博朋克电影、开放世界赛博朋克游戏、赛博义体科幻动画

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Cyberpunk high-tech low-life |
| 相机/渲染器 Camera/Renderer | anamorphic 40mm, heavy neon bloom, rain flare |
| 打光 Lighting | magenta-cyan neon, holographic ad glow, wet bounce |
| 色彩 Color | magenta + electric cyan, warm-cool clash |
| 构图 Composition | dense vertical city, foreground rain, layered signage |
| 画家参照 Painter Ref | futurist concept design, cyber-noir anime |
| 场景/氛围 Scene | rain-slick night street, holographic ads, smoke haze |

## 结构化提示词（English · 推荐）
```
Cyberpunk high-tech low-life - anamorphic 40mm, heavy neon bloom, rain flare - [magenta-cyan neon, holographic ad glow, wet bounce] + [magenta + electric cyan, warm-cool clash] + [dense vertical city, foreground rain, layered signage] + [futurist concept design, cyber-noir anime] + [rain-slick night street, holographic ads, smoke haze], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
赛博朋克风格，霓虹迷离的高科技低生活质感，浓郁的品红与电光青霓虹光晕，雨夜湿滑街面的反光，全息广告与烟雾弥漫的氛围，强烈的明暗对比与冷暖撞色，潮湿压抑的未来都市氛围，电影级动态光影，超清细节
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
