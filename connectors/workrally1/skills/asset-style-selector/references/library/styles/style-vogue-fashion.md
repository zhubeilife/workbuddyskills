风格 ID：`style-vogue-fashion`
原目录：`资产-Vogue杂志`

# 高级时装大片 · 视觉风格提示词

## 分类定位
- **大类**：【四】艺术家风格
- **中类**：时尚&广告
- **标准名**：高级时装大片
- **原名**（内部标识，不外显）：Vogue杂志

## 风格参考（Reference）
高端时装杂志大片、戏剧化人像摄影、黑白情欲时装摄影

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | High-end fashion editorial |
| 相机/渲染器 Camera/Renderer | Hasselblad H6D medium format, 80mm, studio strobe |
| 打光 Lighting | soft studio key + hard rim light, refined modeling |
| 色彩 Color | low-saturation high-fashion grey or rich dramatic color |
| 构图 Composition | bold tense editorial framing, refined negative space |
| 画家参照 Painter Ref | dramatic narrative portrait photography, provocative high-contrast fashion photography |
| 场景/氛围 Scene | luxurious edgy fashion shoot, confident attitude |

## 结构化提示词（English · 推荐）
```
High-end fashion editorial - Hasselblad H6D medium format, 80mm, studio strobe - [soft studio key + hard rim light, refined modeling] + [low-saturation high-fashion grey or rich dramatic color] + [bold tense editorial framing, refined negative space] + [dramatic narrative portrait photography, provocative high-contrast fashion photography] + [luxurious edgy fashion shoot, confident attitude], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
高端时尚大片摄影质感，电影级布光与精致的明暗塑形，柔和的影棚光与硬质轮廓光结合，画面考究高级、构图大胆而富张力，低饱和的高级灰调或浓郁戏剧化色彩，皮肤与材质细节细腻通透，质感奢华、edgy 而充满态度，氛围冷艳、摩登、自信而极具镜头表现力，弥漫国际大刊的精致与高级感。
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
