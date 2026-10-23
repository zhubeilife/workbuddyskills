风格 ID：`style-3d-game-anime`
原目录：`资产-3D二次元游戏实机`

# 二次元游戏实机 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：二次元游戏实机
- **原名**（内部标识，不外显）：3D二次元游戏实机
- **题材定位**：新世代三渲二 3D 二次元游戏实机画面，顶级新世代二次元游戏级的高精度动漫引擎渲染，都市潮流美学

## 风格参考（Reference）
**核心参照：新世代都市潮流向与开放世界向三渲二二次元游戏** —— 新世代三渲二的标志性视觉语言：

### 都市潮流向美学特征：
- **都市潮流美学**：赛博都市背景，霓虹招牌、街头涂鸦、现代建筑与机械元素混搭
- **高饱和撞色**：大胆的色彩组合（品红×青蓝×橙黄），高对比度的视觉冲击力，拒绝常规开放世界二次元的"安全清新"
- **时尚角色设计**：服装具有强烈时装感（夹克/卫衣/机能风配饰），角色姿态动感十足，大量非对称设计与层叠穿搭
- **进阶三渲二**：不是简单的平涂 cel-shading，而是多层渐变着色（gradient toon ramp），角色阴影有冷暖过渡，高光区域保留 PBR 反射质感
- **动态构图**：战斗/展示画面带有速度线与运动模糊暗示，角色角度多变（仰拍/俯拍/荷兰角）

### 开放世界向美学特征：
- **自然环境渲染**：比都市潮流向更注重开放世界环境的真实感——植被密度、水体反射、天气系统（雨/雾/沙尘）
- **更精细的角色建模**：面部表情更丰富，布料物理模拟更真实（衣摆飘动/铠甲碰撞）
- **光影层次**：时间变化的光照系统（清晨金光/正午强光/黄昏暖调/夜晚冷调），体积光（god rays）穿透树林与建筑

**辅助参照**：高规格二次元游戏过场动画品质、开放世界二次元游戏的进阶渲染

## 第一性拆解（Style Decomposition）
- **打光**：多层渐变着色光照（gradient toon ramp），主光方向明确但阴影区有冷暖双色过渡（warm shadow core + cool shadow edge），rim light（边缘光）强烈且带颜色信息（非纯白），部分区域启用局部 PBR 高光（眼睛/金属/湿表面）
- **色彩**：**高饱和度撞色体系**（都市潮流向特征）——品红/洋红 × 电光蓝 × 荧光绿 × 暖橙，色彩块面分明；开放世界向偏向自然环境的和谐色调但保持二次元的鲜艳度
- **角色/材质**：**本风格核心差异点**——介于纯平涂与写实之间的"进阶三渲二"：面部有鼻底/下巴的柔和阴影过渡（非硬边）、眼睛有复杂的多层结构（瞳孔高光×2+虹膜渐变+睫毛投影）、头发有高光束感（highlight streaks）而非均匀色块
- **构图**：游戏实机多视角——角色展示站姿（T-pose 或 A-pose 变体）、战斗动作帧、探索视角（第三人称跟随），都市潮流向特有的荷兰角（dutch angle）与动态倾斜构图
- **氛围**：潮流都市活力感（都市潮流向）/ 广阔自然冒险感（开放世界向），角色充满"能动性"——仿佛下一秒就要动起来

## 提示词构成模块
> 完整结构：**风格 - 引擎/渲染参数 - [打光方案] + [色彩调性] + [角色/材质重点] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | next-gen cel-shaded 3D anime game footage, top-tier next-gen anime game level render quality, modern anime engine graphics |
| 引擎/渲染 Engine | gradient toon ramp shading, multi-layer cel-shade, selective PBR highlights, dynamic rim light with color info |
| 打光 Lighting | clear key light direction, dual-tone shadow transition (warm core + cool edge), strong colored rim light, local PBR spec on eyes/metal/wet surface |
| 色彩 Color | **high-saturation clash colors** (magenta × electric blue × neon green × warm orange), bold color blocking; or natural harmonious tones with anime vibrancy |
| 材质（核心） Material | **advanced in-between toon: soft shadow gradient on face (not hard-edge), complex multi-layer eyes (dual catchlight + iris gradient + lash projection), hair highlight streaks, fabric physics layering, metal/chrome PBR accent |
| 构图 Composition | in-game multi-angle view, character showcase pose, combat action frame, third-person follow cam, dutch angle for dynamism |
| 美术参照 Art Ref | next-gen cel-shaded anime game art, urban chic streetwear aesthetic, open-world nature rendering, high-end anime cutscene quality |
| 场景/氛围 Scene | trendy urban energy / vast natural adventure, character radiating agency and imminent motion |

## 结构化提示词（English · 推荐）
```
next-gen cel-shaded 3D anime game footage, top-tier next-gen anime game level render quality, modern anime engine graphics - gradient toon ramp shading, multi-layer cel-shade, selective PBR highlights, dynamic rim light with color info - [clear key light direction, dual-tone shadow transition (warm core + cool edge), strong colored rim light, local PBR spec on eyes/metal/wet surface] + [high-saturation clash colors (magenta × electric blue × neon green × warm orange), bold color blocking, anime vibrancy] + [advanced in-between toon: soft shadow gradient on face not hard-edge, complex multi-layer eyes with dual catchlight and iris gradient and lash projection, hair highlight streaks, fabric physics layering, metal/chrome PBR accent] + [in-game multi-angle view, character showcase pose, combat action frame, third-person follow cam, dutch angle for dynamism] + [next-gen cel-shaded anime game art, urban chic streetwear aesthetic, open-world nature rendering, high-end anime cutscene quality] + [trendy urban energy or vast natural adventure, character radiating agency and imminent motion], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
顶级新世代二次元游戏级别的三渲二 3D 二次元游戏实机画面。进阶卡通着色渲染——多层渐变着色（gradient toon ramp）而非简单平涂，阴影区有冷暖双色过渡，边缘光带颜色信息而非纯白，眼睛/金属/湿表面局部启用 PBR 高光。高饱和撞色配色体系（品红×电光蓝×荧光绿×暖橙），色彩块面分明。角色材质介于纯平涂与写实之间：面部鼻底/下巴柔和阴影过渡（非硬边），眼睛有多层结构（双重瞳孔高光+虹膜渐变+睫毛投影），头发有高光束感，布料物理层叠。游戏实机多视角构图（角色展示/战斗动作帧/第三人称跟随），都市潮流式荷兰角动态倾斜。潮流都市活力感或广阔自然冒险感，角色充满能动性与即将运动的张力
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **新世代进阶三渲二** 而非基础 cel-shaded：重点在**多层渐变着色 + 复杂眼部结构 + 高饱和撞色 + 都市潮流美学**，区别于常规开放世界二次元的"清新安全风"。
4. **关键区分词**：必须包含 `next-gen anime game render` / `gradient toon ramp` / `multi-layer cel-shade` / `high-saturation clash colors` 以锁定此风格；避免 `photorealistic` / `realistic` / `gritty` / `desaturated`。
5. 如需偏向都市潮流风：强化 `urban chic, neon signage, streetwear fashion, magenta-blue clash, dutch angle`；如需偏向开放世界自然风：强化 `open world, dense vegetation, volumetric god rays, weather system, fabric physics`。
6. 可按需替换 [打光]/[色彩]/[材质]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
