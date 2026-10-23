风格 ID：`style-bw-cinema`
原目录：`资产-黑白电影风格`

# 黑白经典电影 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：黑白经典电影
- **标准名**：黑白经典电影
- **原名**（内部标识，不外显）：黑白电影风格
- **题材定位**：真人写实经典黑白电影，强反差低调照明与灰阶戏剧张力，悬疑/黑色电影基调

## 风格参考（Reference）
经典黑白深焦摄影、表现主义夜景、经典 Film Noir 黑色电影、当代黑白电影摄影；强调 chiaroscuro 明暗分割、硬光硬阴影、纯灰阶高反差，**区别于彩色电影与低饱和彩色片**。

## 第一性拆解（Style Decomposition）
- **打光**：强反差硬光，单一主光源（三角光 / 顶光），低调照明（low-key），锐利硬阴影，百叶窗/栅格投影
- **色彩**：纯黑白灰阶，无色彩，深黑阴影与亮白高光，高反差银盐质感
- **构图**：低角度仰拍强化压迫感，明暗分割（chiaroscuro）构图，框架式取景，纵深透视与深焦
- **参照**：经典深焦摄影、经典 noir 摄影、银盐胶片美学
- **场景/氛围**：雨夜湿街、烟雾、阴影中的面孔、百叶窗光影、悬疑与张力

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数 - [打光方案] + [色彩调性] + [构图描述] + [摄影参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Black and white film noir, monochrome photorealistic cinematic |
| 相机/胶片 Camera/Film | 35mm black-and-white film, high-contrast silver gelatin, deep-focus wide lens |
| 打光 Lighting | hard low-key lighting, single key light, triangle-cheek key lighting, sharp hard shadows |
| 色彩 Color | pure grayscale, high-contrast black and white, deep blacks and bright whites, no color |
| 构图 Composition | low-angle dramatic framing, chiaroscuro light-split, frame-within-frame, deep perspective |
| 摄影参照 DP Ref | classic deep-focus cinematography, classic noir cinematography |
| 场景/氛围 Scene | rain-slick streets, face in shadow, venetian blind shadows, cigarette smoke, suspense tension |

## 结构化提示词（English · 推荐）
```
Black and white film noir, monochrome photorealistic cinematic - 35mm black-and-white film, high-contrast silver gelatin, deep-focus wide lens - [hard low-key lighting, single key light, triangle-cheek key lighting, sharp hard shadows] + [pure grayscale, high-contrast black and white, deep blacks and bright whites, no color] + [low-angle dramatic framing, chiaroscuro light-split, frame-within-frame, deep perspective] + [classic deep-focus cinematography, classic noir cinematography] + [rain-slick streets, face in shadow, venetian blind shadows, cigarette smoke, suspense tension], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
经典黑白电影写实风格，纯灰阶高反差，强反差硬光与三角光低调照明，深黑阴影与亮白高光，单一主光源切割明暗，低角度戏剧化构图与框架式取景，纵深透视与焦内清晰，雨夜湿街、阴影中的面孔、百叶窗光影与香烟烟雾的悬疑氛围，35mm 黑白银盐胶片质感
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（人物 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格为**纯黑白写实**：避免 color / saturated 等词；想强化胶片感可加 "shot on Kodak Tri-X 400, silver grain, optical vignette"。
4. 可按需替换 [打光]/[色彩]/[构图]/[摄影参照]/[场景] 模块强化或微调风格倾向。
