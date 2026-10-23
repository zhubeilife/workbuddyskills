风格 ID：`style-luxury-car-ad`
原目录：`资产-高端汽车广告`

# 高端汽车广告 · 视觉风格提示词

## 分类定位
- **大类**：【四】艺术家风格
- **中类**：时尚&广告
- **标准名**：高端汽车广告
- **原名**（内部标识，不外显）：高端汽车广告

## 风格参考（Reference）
豪华汽车品牌广告大片、CG汽车渲染

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Luxury automotive ad render |
| 相机/渲染器 Camera/Renderer | CG render / Phase One, cinematic studio light |
| 打光 Lighting | cinematic light outlining curves, cold-warm gradient ambient |
| 色彩 Color | cold high-end palette, strong contrast, deep dark bg |
| 构图 Composition | reflection bands on sculpted surfaces, dynamic hero angle |
| 画家参照 Painter Ref | 高端汽车广告CG, 工业产品美学 |
| 场景/氛围 Scene | premium car in deep dark studio, precise industrial beauty |

## 结构化提示词（English · 推荐）
```
Luxury automotive ad render - CG render / Phase One, cinematic studio light - [cinematic light outlining curves, cold-warm gradient ambient] + [cold high-end palette, strong contrast, deep dark bg] + [reflection bands on sculpted surfaces, dynamic hero angle] + [高端汽车广告CG, 工业产品美学] + [premium car in deep dark studio, precise industrial beauty], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
高端汽车广告级渲染质感，极致精致的金属漆面与曲面反射光带，电影化布光勾勒流畅线条与体积感，深邃暗调背景中点缀冷暖渐变的环境光，CG 级高光、倒影与材质细节逼真，画面充满力量与精密工业美感，色调冷峻高级、对比强烈，氛围奢华、动感、震撼而极具科技感，弥漫高端品牌的精致与张力。
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
