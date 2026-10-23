风格 ID：`style-moebius`
原目录：`资产-莫比斯插画`

# 清线科幻漫画 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：欧美漫画2D风格
- **标准名**：清线科幻漫画
- **原名**（内部标识，不外显）：莫比斯插画
- **题材定位**：2D 手绘插画，清晰墨线（ligne claire）欧洲科幻漫画，标志蓝青/赭石淡彩与梦境超现实

## 风格参考（Reference）
欧洲清线科幻漫画（西部冒险、无对白奇幻短篇、超现实科幻）、清线科幻概念设定；强调 crisp ink line work、均匀平光、蓝青与赭石沙色淡彩、流动曲线与精致奇异细节，**区别于美漫网点阴影与日漫赛璐璐**。

## 第一性拆解（Style Decomposition）
- **打光**：均匀平光，无强阴影，线稿主导，细微渐变
- **色彩**：标志性清线科幻调色——蓝/青 + 赭石/沙色，淡彩水彩感，梦幻轻盈
- **构图**：流动有机曲线，精致细密细节，自由透视的超现实科幻构图，疏密有致
- **参照**：欧洲清线科幻线稿语言、欧洲 bande dessinée
- **场景/氛围**：沙漠星球、奇异生物、科幻机械与有机融合，梦境般的空灵氛围

## 提示词构成模块
> 完整结构：**风格 - 媒材 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | European clear-line illustration style, ligne claire sci-fi comic art, 2D hand-drawn |
| 媒材 Medium | crisp ink line work, flat even light, no harsh shadows |
| 打光 Lighting | even flat lighting, line-driven, subtle gradient |
| 色彩 Color | signature clear-line sci-fi palette, muted blue and cyan with ochre and sand, delicate watercolor wash |
| 构图 Composition | flowing organic curves, intricate fine detail, surreal sci-fi composition, free perspective |
| 画家参照 Artist Ref | European clear-line sci-fi line art, European bande dessinée |
| 场景/氛围 Scene | desert planets, strange creatures, sci-fi machinery fused with organic forms, dreamlike atmosphere |

## 结构化提示词（English · 推荐）
```
European clear-line illustration style, ligne claire sci-fi comic art, 2D hand-drawn - crisp ink line work, flat even light, no harsh shadows - [even flat lighting, line-driven, subtle gradient] + [signature clear-line sci-fi palette, muted blue and cyan with ochre and sand, delicate watercolor wash] + [flowing organic curves, intricate fine detail, surreal sci-fi composition, free perspective] + [European clear-line sci-fi line art, European bande dessinée] + [desert planets, strange creatures, sci-fi machinery fused with organic forms, dreamlike atmosphere], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
欧洲清线科幻插画风格，清晰墨线（ligne claire）的欧洲科幻漫画，均匀平光与线稿主导，标志性的蓝青与赭石沙色淡彩渐变，流动曲线与精致的奇异细节，自由透视的超现实科幻构图，沙漠星球、奇异生物与有机融合的机械，梦境般的氛围
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 物件）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格为**2D 手绘线稿插画**：避免 3D / photorealistic / cel-shaded 等词；想强化墨线感可加 "clean ink outline, no screentone, flat color wash"。
4. 可按需替换 [打光]/[色彩]/[构图]/[画家参照]/[场景] 模块强化或微调风格倾向。
