风格 ID：`style-otome-2d`
原目录：`资产-2D乙女`

# 2D乙女 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：国漫2D风格
- **标准名**：2D乙女
- **原名**（内部标识，不外显）：2D乙女

## 风格参考（Reference）
古风乙女游戏官方立绘

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | 2D ancient-style otome illustration |
| 相机/渲染器 Camera/Renderer | 2D illustration, dewy highlight, soft focus |
| 打光 Lighting | soft halo, dreamy floating light |
| 色彩 Color | cyan-jade, lotus-pink, glowing gold |
| 构图 Composition | official-artwork portrait staging, ornate detail |
| 画家参照 Painter Ref | 古风乙女立绘, ip 美型插画 |
| 场景/氛围 Scene | ethereal romantic beauty, jade-pearl ornaments |

## 结构化提示词（English · 推荐）
```
2D ancient-style otome illustration - 2D illustration, dewy highlight, soft focus - [soft halo, dreamy floating light] + [cyan-jade, lotus-pink, glowing gold] + [official-artwork portrait staging, ornate detail] + [古风乙女立绘, ip 美型插画] + [ethereal romantic beauty, jade-pearl ornaments], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
2D古风乙女游戏视觉风格，唯美梦幻的官方立绘式角色作画，通透柔润的细腻皮肤与灵动多情的眼神刻画，飘逸华美的古风服饰与珠翠发饰，梦幻浪漫的青碧、藕粉与流光金色调，柔美的光晕与漂浮光粒氛围，精致厚涂的细腻笔触与水润高光，仙气唯美而心动的恋爱氛围，高精度乙女游戏插画级渲染
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
