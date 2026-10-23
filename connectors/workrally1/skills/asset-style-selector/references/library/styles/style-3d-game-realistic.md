风格 ID：`style-3d-game-realistic`
原目录：`资产-3D真人游戏实机`

# 拟真叙事游戏实机 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：拟真叙事游戏实机
- **原名**（内部标识，不外显）：3D真人游戏实机
- **题材定位**：拟真交互电影级 3D 游戏实机画面，交互电影式细腻拟真渲染，情感驱动的电影化实时渲染

## 风格参考（Reference）
**核心参照：旗舰级拟真交互电影游戏** —— 交互电影类游戏的标志性视觉语言：
- **非传统 3A 硬核写实**：区别于神话动作 3A 的史诗战争质感，走的是「交互式电影」路线——以人物面部表情和情感传达为核心
- **毛孔级皮肤细节**：可见皮肤纹理、细微色斑、眼周细纹、唇纹、面部微血管，subsurface scattering（次表面散射）模拟真实皮肤透光
- **摄影级调色**：自然光感，不过度饱和，偏向纪录片/独立电影的克制色调，暖调室内与冷调室外形成情绪对比
- **电影化近景构图**：大量面部特写与肩部以上镜头，浅景深虚化背景突出人物情绪，模拟手持摄影的微妙呼吸感
- **眼神光与湿润感**：角色眼睛有真实的角膜反射（catchlight）与泪膜反光，传达情感状态

**辅助参照**：顶级叙事 3A 游戏的人物过场渲染品质

## 第一性拆解（Style Decomposition）
- **打光**：自然光源优先（窗户侧光 / 室外漫射日光），柔和全局光照，关键光来自环境逻辑位置，阴影边缘有真实半影（penumbra），无硬边卡通阴影
- **色彩**：电影级调色（color grading），低饱和基底 + 局部色彩强调（如肤色偏暖、衣物保留本色），对比度适中，避免高对比游戏感
- **皮肤/材质**：**本风格核心差异点**——皮肤必须呈现毛孔级细节（pore-level skin detail）、微小瑕疵（freckles, mole, uneven tone）、次表面散射（SSS）让耳朵/鼻尖透出暖红，头发有独立发丝物理
- **构图**：电影叙事镜头为主——过肩镜头（OTS）、面部特写、双人对话构图，景深控制在 f/2.8–f/4 模拟电影镜头，背景适度虚化但保留环境信息
- **氛围**：沉浸式情感叙事空间，每一帧都像电影剧照，角色处于可感知的情绪状态中

## 提示词构成模块
> 完整结构：**风格 - 引擎/渲染参数 - [打光方案] + [色彩调性] + [皮肤/材质重点] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | interactive-drama style realistic 3D game footage, interactive movie render, flagship-level facial fidelity |
| 引擎/渲染 Engine | real-time subsurface scattering, pore-level skin shader, ray-traced ambient occlusion, cinematic depth of field |
| 打光 Lighting | natural window light or outdoor diffused daylight, soft global illumination, logical key light placement, realistic penumbra shadows |
| 色彩 Color | film-grade color grading, low-saturation base with selective warm accents on skin, moderate contrast, documentary-style palette |
| 材质（核心） Material | **pore-level skin detail, visible skin texture, micro-imperfections (freckles/moles), SSS ear/nose warm glow, individual hair strand physics, fabric weave texture** |
| 构图 Composition | cinematic narrative framing, over-the-shoulder shots, face close-ups, two-shot dialogue composition, f/2.8-f/4 DOF |
| 美术参照 Art Ref | interactive-drama game visual language, flagship narrative game cutscene quality |
| 场景/氛围 Scene | emotionally charged narrative space, every frame feels like a film still, character in perceptible emotional state |

## 结构化提示词（English · 推荐）
```
interactive-drama style realistic 3D game footage, interactive movie render, flagship-level facial fidelity - real-time subsurface scattering, pore-level skin shader, ray-traced ambient occlusion, cinematic depth of field - [natural window light or outdoor diffused daylight, soft global illumination, logical key light placement, realistic penumbra shadows] + [film-grade color grading, low-saturation base with selective warm accents on skin, moderate contrast, documentary-style palette] + [pore-level skin detail, visible skin texture, micro-imperfections like freckles and moles, SSS ear and nose warm glow, individual hair strand physics, fabric weave texture] + [cinematic narrative framing, over-the-shoulder shots, face close-ups, two-shot dialogue composition, f/2.8-f/4 DOF] + [interactive-drama game visual language, flagship narrative game cutscene quality] + [emotionally charged narrative space, every frame feels like a film still, character in perceptible emotional state], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
旗舰级拟真交互电影 3D 游戏实机画面，交互电影式细腻拟真渲染风格。毛孔级皮肤细节与可见皮肤纹理（色斑/细纹/微瑕），次表面散射让耳尖鼻头透出真实暖红，独立发丝物理与织物编织纹理。自然窗光或室外漫射日光为光源，柔和全局光照与真实半影阴影。电影级低饱和调色，肤色区域选择性暖调增强，纪录片式克制配色。电影叙事镜头（过肩/面部特写/双人对话构图），f/2.8-f/4 电影景深虚化。每帧如电影剧照般呈现角色的可感知情绪状态
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **交互电影式拟真** 而非传统 3A 硬核写实：重点在**皮肤细腻度 + 情绪表达 + 电影构图**，而非铠甲反光/爆炸粒子/战场宏大场景。
4. **关键区分词**：必须包含 `pore-level skin` / `subsurface scattering` / `micro-imperfections` / `interactive-drama realism` 以锁定此风格；避免 `cel-shaded` / `anime` / `stylized` / `oversaturated`。
5. 可按需替换 [打光]/[色彩]/[材质]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
