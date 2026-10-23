风格 ID：`style-70s-vintage-film`
原目录：`资产-美式70年代老胶片质感`

# 70年代复古胶片 · 视觉风格提示词

## 分类定位
- **大类**：【一】仿真人
- **中类**：70年代胶片
- **标准名**：70年代复古胶片
- **原名**（内部标识，不外显）：美式70年代老胶片质感
- **题材定位**：1970 年代美国新好莱坞电影胶片质感，暖褪色柯达胶片，粗颗粒与光晕的年代感

## 风格参考（Reference）
1970 年代美国新好莱坞电影（纽约街头犯罪片、都市情感片、政治悬疑片）、柯达老胶片（Kodak 5247/5294）；强调褪色暖调、重颗粒、镜头光晕与划痕、轻微色彩偏移，**区别于现代数字锐利与干净的调色**。

## 第一性拆解（Style Decomposition）
- **打光**：自然窗光与实用钨丝灯（warm tungsten），柔和的漫射光，无现代 LED 硬光；夜景依赖霓虹与台灯实用光
- **色彩**：褪色柯达暖调——琥珀/sepia 偏色，高光泛黄，暗部沉褐，整体低饱和偏暖，轻微色彩串扰（color shift）
- **构图**：70 年代标志性推拉变焦（zoom）、脏乱取景、亲密近景、非完美水平线，手持呼吸感
- **参照**：1970s American New Wave cinema, vintage Kodak film stock, grainy warm retro
- **场景/氛围**：年代感空间——复古内饰、老式汽车、烟霾空气、午后斜阳，怀旧而粗粝的真实

## 提示词构成模块
> 完整结构：**风格 - 胶片/镜头参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀（强化颗粒/光晕/划痕）。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | 1970s American New Wave cinema look, vintage Kodak film stock, grainy warm retro photoreal |
| 胶片/镜头 Film | 35mm Kodak 5247 stock, anamorphic zoom lens, film grain, halation, lens flare, gate weave, light scratches |
| 打光 Lighting | natural window light, practical tungsten lamps, soft diffuse, no modern LED, neon/night practicals |
| 色彩 Color | faded Kodak warm tone, amber/sepia color cast, yellowed highlights, brown crushed shadows, low-sat warm, slight color shift |
| 构图 Composition | 70s zoom in/out, dirty framing, intimate close-up, imperfect horizon, handheld breathing |
| 美术参照 Art Ref | 1970s American New Wave cinema, gritty New York street crime drama, vintage Kodak |
| 场景/氛围 Scene | period interior, vintage car, smoky air, afternoon raking sun, nostalgic and gritty authenticity |

## 结构化提示词（English · 推荐）
```
1970s American New Wave cinema look, vintage Kodak film stock, grainy warm retro photoreal - 35mm Kodak 5247 stock, anamorphic zoom lens, heavy film grain, halation, lens flare, gate weave, light scratches - [natural window light, practical tungsten lamps, soft diffuse, no modern LED, neon and night practicals] + [faded Kodak warm tone, amber sepia color cast, yellowed highlights, brown crushed shadows, low-saturation warm, slight color shift] + [70s zoom in/out, dirty framing, intimate close-up, imperfect horizon, handheld breathing] + [1970s American New Wave cinema, gritty New York street crime drama, vintage Kodak] + [period interior, vintage car, smoky air, afternoon raking sun, nostalgic and gritty authenticity], heavy film grain, halation on highlights, lens flare, gate weave, light scratches, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
1970 年代美国新好莱坞电影质感，褪色柯达老胶片，粗颗粒暖调复古写实。35mm 柯达 5247 胶片、变形变焦镜头、重颗粒、光晕、镜头光斑、片门抖动与轻微划痕。自然窗光与实用钨丝灯，柔和漫射无现代 LED 硬光，夜景依赖霓虹与台灯。褪色柯达暖调——琥珀/sepia 偏色，高光泛黄，暗部沉褐，整体低饱和偏暖带轻微色彩串扰。70 年代推拉变焦、脏乱取景、亲密近景、非完美水平线、手持呼吸感。年代感空间——复古内饰、老式汽车、烟霾空气、午后斜阳，怀旧而粗粝的真实
```

## 统一质感尾缀
```
heavy film grain, halation on highlights, lens flare, gate weave, light scratches, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **年代胶片感**：重颗粒 + 暖褪色 + 光晕划痕 + 70s 推拉变焦；避免 modern clean digital、oversharp、cool neutral grade。
4. 想强化年代感可加 "Kodak 5247, 1970s telecine, expired film, dust and scratches"；想偏 70 年代纽约夜街可加 "neon noir, rainy night, cigarette smoke"。
5. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
