风格 ID：`style-2d-realism`
原目录：`资产-二维写实风`

# 二维写实绘画 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：写实绘画2D
- **标准名**：二维写实绘画
- **原名**（内部标识，不外显）：二维写实风
- **题材定位**：二维手绘/数字绘制的写实风格，接近照片的比例结构与光影，但保留可见的绘画笔触与手绘感，**区别于 3D 渲染的物理精确与卡通2D的简化夸张**

## 风格参考（Reference）
古典写实油画肖像、当代半写实数字绘画、写实素描；核心是 **2D painted realism**——精确的解剖与透视、真实的明暗关系与质感，但通过笔触、涂层与颜料肌理表明这是"画出来的"而非"拍出来/渲染出来的"。

## 第一性拆解（Style Decomposition）
- **打光**：真实可信的单一主光 + 环境补光，柔和的明暗过渡（sfumato），高光与反光符合物理直觉
- **色彩**：自然真实的肤色与环境色，低饱和写实色调，微妙的冷暖色温变化
- **构图**：写实的解剖比例与透视，肖像/半身/场景写实取景，focal 主体清晰
- **参照**：古典写实油画、当代半写实数字绘画
- **场景/氛围**：真实可信的人物/静物/场景，沉静、细腻、有绘画温度的写实氛围

## 提示词构成模块
> 完整结构：**风格 - 媒材 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | 2D realistic painting, semi-realistic hand-painted illustration |
| 媒材 Medium | painterly realism, visible brushwork, oil-paint or digital-paint texture |
| 打光 Lighting | believable single key light with ambient fill, soft sfumato value transition, physically plausible highlights |
| 色彩 Color | natural realistic skin and environment colors, low-saturation lifelike palette, subtle warm-cool temperature shift |
| 构图 Composition | accurate anatomy and perspective, realistic portrait or scene framing, clear focal subject |
| 画家参照 Artist Ref | classical realist oil portraiture with fluid brushwork and deep chiaroscuro, contemporary semi-realistic digital painting |
| 场景/氛围 Scene | believable lifelike figures still-life or scenes, calm refined painterly realism |

## 结构化提示词（English · 推荐）
```
2D realistic painting, semi-realistic hand-painted illustration - painterly realism, visible brushwork, oil-paint or digital-paint texture - [believable single key light with ambient fill, soft sfumato value transition, physically plausible highlights] + [natural realistic skin and environment colors, low-saturation lifelike palette, subtle warm-cool temperature shift] + [accurate anatomy and perspective, realistic portrait or scene framing, clear focal subject] + [classical realist oil portraiture with fluid brushwork and deep chiaroscuro, contemporary semi-realistic digital painting] + [believable lifelike figures still-life or scenes, calm refined painterly realism], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
二维写实绘画风格，二维手绘/数字绘制的半写实插画，接近照片的解剖比例与透视但保留可见笔触与颜料肌理，真实可信的单一主光加环境补光与柔和 sfumato 明暗过渡，符合物理直觉的高光反光，自然真实的肤色与环境色、低饱和写实色调与微妙的冷暖色温变化，肖像/半身/场景写实取景与清晰的焦点主体，对标古典写实油画与当代半写实数字绘画，沉静细腻而有绘画温度的写实氛围
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 物件）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格为**2D 写实绘画**：核心是"画出来的写实"——保留 "painterly, visible brushwork, painting"；避免 photograph / 3D render / cel-shaded 破坏绘画感；想更偏素描可加 "graphite pencil realism"，更偏油画可加 "oil on canvas, impasto"。
4. 可按需替换 [打光]/[色彩]/[构图]/[画家参照]/[场景] 模块强化或微调风格倾向。
