风格 ID：`style-retro-anime`
原目录：`资产-复古日漫`

# 复古日漫 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：日漫2D风格（可大量填充）
- **标准名**：复古日漫
- **原名**（内部标识，不外显）：复古日漫

## 风格参考（Reference）
80 年代赛博科幻与都市动作动画、昭和OVA怀旧风

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Retro Showa-era anime cel |
| 相机/渲染器 Camera/Renderer | cel animation on film, grain + noise, yellowed tone |
| 打光 Lighting | soft flat key, plain limited steps |
| 色彩 Color | plain low-saturation retro palette |
| 构图 Composition | languid poetic staging, hand-painted watercolor bg |
| 画家参照 Painter Ref | 80 年代赛博科幻动画, 昭和OVA美术 |
| 场景/氛围 Scene | nostalgic retro anime mood, hand-drawn texture |

## 结构化提示词（English · 推荐）
```
Retro Showa-era anime cel - cel animation on film, grain + noise, yellowed tone - [soft flat key, plain limited steps] + [plain low-saturation retro palette] + [languid poetic staging, hand-painted watercolor bg] + [80 年代赛博科幻动画, 昭和OVA美术] + [nostalgic retro anime mood, hand-drawn texture], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
复古日漫赛璐璐风格，八九十年代昭和味的怀旧手绘质感，硬朗利落的手绘描边与平涂上色，朴实低饱和的复古色调与暖调泛黄，手绘背景的细腻水彩晕染，轻微的胶片颗粒与噪点质感，含蓄克制的明暗块面与柔和高光，慵懒诗意而怀旧的氛围，经典OVA时代的复古日式动画级渲染
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
