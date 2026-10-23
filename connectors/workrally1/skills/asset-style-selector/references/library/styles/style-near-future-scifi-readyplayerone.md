风格 ID：`style-near-future-scifi-readyplayerone`
原目录：`资产-近未来科幻（头号玩家）`

# 近未来虚拟科幻 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：科幻
- **标准名**：近未来虚拟科幻
- **原名**（内部标识，不外显）：近未来科幻（头号玩家）

## 风格参考（Reference）
近未来 VR 冒险电影、游戏世界喜剧、发光矢量数字世界电影；强调触手可及的**近未来消费科技 + VR 虚拟世界**，霓虹全息、虚拟乐园式赛博世界，**区别于遥远硬科幻太空与末世废土**。

## 第一性拆解（Style Decomposition）
- **打光**：高饱和霓虹与全息屏发光，虚拟世界内自发光边缘，现实层则偏昏暗贫民窟暖光对比
- **色彩**：电光蓝 + 品红 + 青柠绿的高能霓虹三角，虚拟层鲜亮、现实层灰暗形成反差
- **构图**：广阔纵深的虚拟空间、悬浮全息 UI 叠层、速度感竞速视角、堆叠拖车贫民窟仰视
- **参照**：高光晕浪漫光效、发光矢量数字美学、流畅冒险调度
- **场景/氛围**：VR 头显与体感装备、数字化身、无限赛博乐园、流行文化彩蛋、乐观冒险感

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数 - [打光方案] + [色彩调性] + [构图描述] + [摄影师参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Near-future sci-fi, VR virtual world, photorealistic cinematic |
| 相机/胶片 Camera/Film | 35mm digital cinema, subtle glow bloom, dynamic tracking shot |
| 打光 Lighting | high-saturation neon and holographic screen glow, self-illuminated virtual edges, dim slum ambient contrast |
| 色彩 Color | electric blue, magenta, lime-green high-energy neon, vivid virtual vs grey reality contrast |
| 构图 Composition | vast virtual depth, floating holographic UI layers, high-speed racing POV, stacked-trailer slum low angle |
| 摄影师参照 DP Ref | blooming high-glow adventure lighting, glowing vector digital-world aesthetic, fluid adventure staging |
| 场景/氛围 Scene | VR headsets and haptic rigs, digital avatars, endless cyber playground, pop-culture easter eggs, optimistic adventure |

## 结构化提示词（English · 推荐）
```
Near-future sci-fi, VR virtual world, photorealistic cinematic - 35mm digital cinema, subtle glow bloom, dynamic tracking shot - [high-saturation neon and holographic screen glow, self-illuminated virtual edges, dim slum ambient contrast] + [electric blue, magenta, lime-green high-energy neon, vivid virtual vs grey reality contrast] + [vast virtual depth, floating holographic UI layers, high-speed racing POV, stacked-trailer slum low angle] + [blooming high-glow adventure lighting, glowing vector digital-world aesthetic, fluid adventure staging] + [VR headsets and haptic rigs, digital avatars, endless cyber playground, pop-culture easter eggs, optimistic adventure], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
近未来虚拟现实科幻风格，触手可及的近未来消费科技与 VR 虚拟世界，电光蓝/品红/青柠绿的高能霓虹与全息屏发光，虚拟层鲜亮绚烂与现实贫民窟灰暗昏黄的强烈反差，广阔纵深的虚拟空间与悬浮全息 UI 叠层，速度感竞速视角与堆叠拖车贫民窟仰视构图，数字化身、体感装备与无限赛博乐园，流行文化彩蛋与乐观冒险的氛围
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（人物 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格主打**近未来 + 虚拟现实**：避免 deep-space、medieval、wasteland 等词破坏"近未来可及感"；想强化虚拟层可加 "glowing wireframe, holographic overlay, digital particle FX"。
4. 可按需替换 [打光]/[色彩]/[构图]/[参照]/[场景] 模块强化或微调风格倾向。
