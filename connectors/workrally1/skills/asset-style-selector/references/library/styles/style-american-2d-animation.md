风格 ID：`style-american-2d-animation`
原目录：`资产-美系二维动画`

# 美式经典手绘动画 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：美漫2D风格
- **标准名**：美式经典手绘动画
- **原名**（内部标识，不外显）：美系二维动画
- **题材定位**：美式黄金期手绘二维动画，夸张表演、圆润流畅线条、丰富表情，**区别于日漫赛璐璐的锐利分色与美漫网点阴影**

## 风格参考（Reference）
美式手绘动画黄金时代（童话歌舞长片）、美式经典短篇卡通、古典音乐动画；核心是 **hand-drawn 2D cel animation**——柔和圆润的轮廓线、squash-and-stretch 夸张表演、水彩/水粉背景、明快饱满的角色配色与富有生命力的表情。

## 第一性拆解（Style Decomposition）
- **打光**：柔和的动画平光，简化的分区上色（cel shading），高光与阴影为块面化色块而非渐变
- **色彩**：明快饱满的角色主色 + 水彩/水粉质感的柔和背景，温暖友好的色调
- **构图**：角色为绝对主体，squash-and-stretch 夸张姿态与丰富表情，动态而富戏剧张力
- **参照**：美式黄金期 hand-drawn animation、经典角色作画
- **场景/氛围**：童话奇幻/歌舞叙事场景，温暖、欢快、富有生命力与情感表达

## 提示词构成模块
> 完整结构：**风格 - 媒材 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | classic American hand-drawn 2D animation, golden-age studio cel animation |
| 媒材 Medium | hand-drawn 2D cel, smooth rounded ink outline, painted watercolor background |
| 打光 Lighting | soft flat animation light, simplified cel shading, block-shaped highlights and shadows |
| 色彩 Color | bright saturated character colors, soft watercolor-gouache background, warm friendly palette |
| 构图 Composition | character as hero subject, squash-and-stretch expressive pose, dynamic dramatic staging |
| 画家参照 Artist Ref | golden-age American feature animation, expressive classic character drawing, classic slapstick cartoon shorts |
| 场景/氛围 Scene | fairytale fantasy musical scenes, warm cheerful lively emotional expression |

## 结构化提示词（English · 推荐）
```
classic American hand-drawn 2D animation, golden-age studio cel animation - hand-drawn 2D cel, smooth rounded ink outline, painted watercolor background - [soft flat animation light, simplified cel shading, block-shaped highlights and shadows] + [bright saturated character colors, soft watercolor-gouache background, warm friendly palette] + [character as hero subject, squash-and-stretch expressive pose, dynamic dramatic staging] + [golden-age American feature animation, expressive classic character drawing, classic slapstick cartoon shorts] + [fairytale fantasy musical scenes, warm cheerful lively emotional expression], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
经典美系手绘二维动画风格，对标美式手绘动画黄金期的童话歌舞长片与经典卡通短片，柔和圆润的墨线轮廓与水彩/水粉手绘背景，简化分区上色（cel shading）的块面化高光阴影，明快饱满的角色主色与温暖友好的背景色调，squash-and-stretch 夸张表演姿态与丰富生动的表情，角色为绝对主体的动态戏剧化构图，童话奇幻歌舞场景，欢快而富有生命力的情感表达
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 物件）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格为**手绘 2D 赛璐璐动画**：保留 "hand-drawn 2D cel, cel shading, ink outline"；避免 3D / photorealistic / cel-shaded-anime（日漫）破坏美系手绘感；想强化可加 "squash and stretch, painted background, golden-age American animation look"。
4. 可按需替换 [打光]/[色彩]/[构图]/[画家参照]/[场景] 模块强化或微调风格倾向。
