风格 ID：`style-otome-glow-realistic`
原目录：`资产-乙女真人发光`

# 乙女柔光写真 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：乙女发光写实
- **标准名**：乙女柔光写真
- **原名**（内部标识，不外显）：乙女真人发光
- **题材定位**：乙女游戏 CG 质感但转为真人写实，角色被柔光与光晕包裹的浪漫发光肖像，梦幻糖系氛围

## 风格参考（Reference）
乙女游戏（Otome，女性向）的高光 CG 美学，但主体为**真人演员/写实人物**；强调发光皮肤、背光天使环、柔焦 bokeh 光斑、星屑闪粒、粉金浪漫调，**区别于暗调写实与硬光商业写真**。

## 第一性拆解（Style Decomposition）
- **打光**：**发光感核心**——柔和背光/边缘光在人物周围形成光晕（halo），正面补光极柔，皮肤自带 luminous 内透光，眼神有星光反射
- **色彩**：浪漫糖系——粉金（pink-gold）、淡紫、奶白、浅桃，高调明亮，光斑带暖色，梦幻过度曝光感
- **构图**：近距离肖像（胸像/半身），浅景深大 bokeh 背景，光斑与星屑漂浮于人物四周，轻微仰拍神圣感
- **参照**：otome-game glowing CG but photorealistic, luminous real-person portrait, dreamy bloom
- **场景/氛围**：浪漫梦幻——花园/教堂光窗/星空，花瓣与光粒飘浮，恋爱心跳的甜美悬浮感

## 提示词构成模块
> 完整结构：**风格 - 摄影/镜头参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀（强化 bloom/glow/柔焦）。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | otome-game glowing romantic realism, luminous real-person portrait, dreamy bloom skin, photorealistic otome CG |
| 摄影/镜头 Lens | 85mm portrait, very shallow DOF, big bokeh, soft glow, sparkle, 35mm film |
| 打光 Lighting | **glowing halo back/rim light around figure**, ultra-soft front fill, luminous subsurface skin, starlight catchlight in eyes |
| 色彩 Color | romantic sugar palette, pink-gold, lilac, cream white, peach, high-key bright, warm light spots, dreamy overexposed |
| 构图 Composition | close portrait (bust/half), shallow-DOF big bokeh bg, light particles and sparkles floating around, slight low-angle sacred |
| 美术参照 Art Ref | otome-game glowing CG but photorealistic, luminous real-person portrait, dreamy bloom |
| 场景/氛围 Scene | romantic dreamy, garden/church light-window/starry sky, petals and light motes drifting, sweet suspended heartbeat |

## 结构化提示词（English · 推荐）
```
otome-game glowing romantic realism, luminous real-person portrait, dreamy bloom skin, photorealistic otome CG - 85mm portrait, very shallow DOF, big bokeh, soft glow, sparkle, 35mm film - [glowing halo back/rim light around figure, ultra-soft front fill, luminous subsurface skin, starlight catchlight in eyes] + [romantic sugar palette, pink-gold, lilac, cream white, peach, high-key bright, warm light spots, dreamy overexposed] + [close portrait (bust/half), shallow-DOF big bokeh bg, light particles and sparkles floating around, slight low-angle sacred] + [otome-game glowing CG but photorealistic, luminous real-person portrait, dreamy bloom] + [romantic dreamy, garden/church light-window/starry sky, petals and light motes drifting, sweet suspended heartbeat], soft focus edges, gentle edge falloff, heavy bloom, luminous glow, halation on highlights, photochemical softness, analog edge bloom, light leak, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
乙女游戏 CG 质感但转为真人写实的浪漫发光肖像。发光感核心——柔和背光/边缘光在人物周围形成光晕（halo），正面补光极柔，皮肤自带 luminous 内透光，眼神有星光反射。浪漫糖系配色——粉金、淡紫、奶白、浅桃，高调明亮，光斑带暖色，梦幻过度曝光感。近距离肖像（胸像/半身），浅景深大 bokeh 背景，光斑与星屑漂浮人物四周，轻微仰拍神圣感。浪漫梦幻——花园/教堂光窗/星空，花瓣与光粒飘浮，恋爱心跳的甜美悬浮感
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, heavy bloom, luminous glow, halation on highlights, photochemical softness, analog edge bloom, light leak, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **真人写实 + 乙女发光氛围**：发光 halo + 粉金糖系 + 大 bokeh 星屑；避免暗调写实、硬光商业、低饱和灰雾。
4. 强化发光可加 "glowing halo, luminous skin, bloom, starlight particles, sparkle bokeh"；想偏神圣感可加 "cathedral light, angelic, soft backlight"。
5. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
