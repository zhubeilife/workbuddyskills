风格 ID：`style-tim-burton-gothic`
原目录：`资产-蒂姆伯顿哥特`

# 暗黑童话哥特 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：欧美哥特
- **标准名**：暗黑童话哥特
- **原名**（内部标识，不外显）：蒂姆伯顿哥特
- **题材定位**：暗黑童话哥特怪诞美学，苍白拉长的怪诞角色，阴暗却童真的故事书氛围

## 风格参考（Reference）
暗黑童话哥特电影与插画（节日定格动画、哥特奇幻爱情片、冥界喜剧）；强调苍白细长人物、夸张大眼、哥特建筑（尖顶/铁艺）、病态绿与骨白的冷调、怪诞与童真并置的黑白高反差，**区别于普通暗黑恐怖与写实哥特**。

## 第一性拆解（Style Decomposition）
- **打光**：高反差 chiaroscuro（明暗对比），阴森月光/烛光实用光源，强阴影与戏剧性侧光，偶有怪诞体积光
- **色彩**：哥特调色板——深黑、病态绿（sickly green）、暗紫、骨白（bone white），点缀暗红，整体冷沉带诡异
- **构图**：怪诞倾斜角度（dutch tilt），哥特尖顶建筑框景，角色居中拉长，夸张透视，故事书跨页感
- **参照**：dark storybook gothic visual language, stop-motion holiday macabre, gothic whimsy
- **场景/氛围**：怪诞童话——哥特小镇、枯树、铁艺栏杆、雾中墓园，阴暗却温暖童真的矛盾感

## 提示词构成模块
> 完整结构：**风格 - 渲染/笔触参数 - [打光方案] + [色彩调性] + [构图描述] + [美术参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | gothic whimsical style, pale elongated figures, macabre storybook, dark whimsical gothic illustration |
| 渲染/笔触 Render | gothic illustration, stylized 2D, ink-and-wash suggest, stop-motion puppet look |
| 打光 Lighting | high-contrast chiaroscuro, eerie moonlight/candle practicals, strong shadow, dramatic side light, whimsical volumetric |
| 色彩 Color | gothic palette, deep black, sickly green, dark purple, bone white, accent dark red, cold eerie overall |
| 构图 Composition | whimsical dutch tilt, gothic spire framing, elongated centered figure, exaggerated perspective, storybook spread |
| 美术参照 Art Ref | dark storybook gothic visual language, stop-motion holiday macabre, gothic whimsy |
| 场景/氛围 Scene | macabre fairytale, gothic town, bare trees, iron railings, foggy graveyard, dark-yet-warm childlike contradiction |

## 结构化提示词（English · 推荐）
```
gothic whimsical style, pale elongated figures, macabre storybook, dark whimsical gothic illustration - gothic illustration, stylized 2D, ink-and-wash suggest, stop-motion puppet look - [high-contrast chiaroscuro, eerie moonlight/candle practicals, strong shadow, dramatic side light, whimsical volumetric] + [gothic palette, deep black, sickly green, dark purple, bone white, accent dark red, cold eerie overall] + [whimsical dutch tilt, gothic spire framing, elongated centered figure, exaggerated perspective, storybook spread] + [dark storybook gothic visual language, stop-motion holiday macabre, gothic whimsy] + [macabre fairytale, gothic town, bare trees, iron railings, foggy graveyard, dark-yet-warm childlike contradiction], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
暗黑童话哥特怪诞美学，苍白拉长的怪诞角色，阴暗却童真的故事书氛围。高反差明暗对比（chiaroscuro），阴森月光/烛光实用光源，强阴影与戏剧性侧光，偶有怪诞体积光。哥特调色板——深黑、病态绿、暗紫、骨白，点缀暗红，整体冷沉带诡异。怪诞倾斜角度（dutch tilt），哥特尖顶建筑框景，角色居中拉长，夸张透视，故事书跨页感。怪诞童话——哥特小镇、枯树、铁艺栏杆、雾中墓园，阴暗却温暖童真的矛盾感
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是 **暗黑童话哥特怪诞**：苍白拉长角色 + 病态绿/骨白冷调 + 高反差 + 怪诞倾斜；避免普通恐怖的血腥写实、明亮欢快、写实人像。
4. 强化暗黑童话感可加 "pale elongated face, big eyes, stop-motion puppet, gothic spires, sickly green"；想偏节日怪诞可加 "skeleton, Halloween town, pinstripe skeleton figure"。
5. 可按需替换 [打光]/[色彩]/[构图]/[美术参照]/[场景] 模块强化或微调风格倾向。
