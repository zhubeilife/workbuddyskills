风格 ID：`style-robot-scifi-exmachina`
原目录：`资产-机器人科幻（机械姬）`

# 仿生人科幻 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：科幻
- **标准名**：仿生人科幻
- **原名**（内部标识，不外显）：机器人科幻（机械姬）

## 风格参考（Reference）
人形 AI 心理惊悚电影、赛博朋克续作的极简场景、机器人伦理科幻；核心是**人形 AI 的冷峻精密与克制情绪张力**——透明机械躯体、极简高科技建筑、精密工业设计感，**区别于生物科幻的湿润有机与超英的暴力动作**。

## 第一性拆解（Style Decomposition）
- **打光**：柔和均匀的科技柔光 + 冷暖对比（冷蓝科技光 vs 暖木质室内），机械躯体内部透光发光，克制低反差
- **色彩**：极简高级灰调，冷钢蓝 + 暖木原色 + 纯白，机械内部 LED 冷光点缀，低饱和精密感
- **构图**：对称精密的极简构图，玻璃隔断反射，人机对视的心理张力，透明机械关节局部特写，建筑几何线条
- **参照**：冷静精密布光、极简高级光影、极简主义工业设计
- **场景/氛围**：隐世高科技别墅、玻璃与混凝土建筑、人形机器人透明躯体、克制悬念与人工智能觉醒的冷峻理性

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数 - [打光方案] + [色彩调性] + [构图描述] + [摄影师参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Robot AI sci-fi, humanoid android, photorealistic cinematic |
| 相机/胶片 Camera/Film | 35mm digital cinema, clean minimal grain, precise symmetrical framing |
| 打光 Lighting | soft even tech light, cool-warm contrast (cold-blue tech vs warm-wood interior), glowing translucent mechanical body, restrained low contrast |
| 色彩 Color | minimalist high-end greys, cool steel-blue + warm natural wood + pure white, cold LED accents, desaturated precision |
| 构图 Composition | symmetrical minimalist framing, glass-partition reflections, human-machine eye-contact tension, macro of translucent joints, architectural geometry |
| 摄影师参照 DP Ref | cool precise clinical lighting, minimalist high-end monolithic light |
| 场景/氛围 Scene | secluded high-tech villa, glass and concrete architecture, humanoid android with transparent body, restrained suspense and cold rational AI awakening |

## 结构化提示词（English · 推荐）
```
Robot AI sci-fi, humanoid android, photorealistic cinematic - 35mm digital cinema, clean minimal grain, precise symmetrical framing - [soft even tech light, cool-warm contrast (cold-blue tech vs warm-wood interior), glowing translucent mechanical body, restrained low contrast] + [minimalist high-end greys, cool steel-blue + warm natural wood + pure white, cold LED accents, desaturated precision] + [symmetrical minimalist framing, glass-partition reflections, human-machine eye-contact tension, macro of translucent joints, architectural geometry] + [cool precise clinical lighting, minimalist high-end monolithic light] + [secluded high-tech villa, glass and concrete architecture, humanoid android with transparent body, restrained suspense and cold rational AI awakening], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
人形机器人科幻风格，人形 AI 的冷峻精密与克制情绪张力，柔和均匀的科技柔光与冷暖对比（冷蓝科技光对比暖木质室内），机械躯体内部透光发光与克制低反差，极简高级灰调（冷钢蓝＋暖木原色＋纯白）与机械内部 LED 冷光点缀，对称精密的极简构图与玻璃隔断反射，人机对视的心理张力与透明机械关节特写，隐世高科技别墅与玻璃混凝土建筑，人工智能觉醒的冷峻理性与克制悬念氛围
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（人物 / 机器人 / 场景）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格主打**极简冷峻高级感**：避免 chaotic/gritty/colorful-neon 破坏克制精密；想强化设计感可加 "industrial design, exposed transparent mechanics, precise CNC surfaces"。
4. 可按需替换 [打光]/[色彩]/[构图]/[参照]/[场景] 模块强化或微调风格倾向。
