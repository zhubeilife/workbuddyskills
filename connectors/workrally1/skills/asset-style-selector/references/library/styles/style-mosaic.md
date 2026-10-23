风格 ID：`style-mosaic`
原目录：`资产-马赛克风格`

# 马赛克拼贴 · 视觉风格提示词

## 分类定位
- **大类**：【三】2D风格
- **中类**：拼贴马赛克
- **标准名**：马赛克拼贴
- **原名**（内部标识，不外显）：马赛克风格
- **题材定位**：由离散色块/瓷砖拼贴而成的图像，可见清晰的砖块分割与灰缝，**区别于像素画的规整网格与厚涂的连续笔触**

## 风格参考（Reference）
拜占庭/罗马镶嵌壁画、新艺术运动金色拼贴、玻璃马赛克艺术、现代瓷砖拼贴肖像；核心是 **image made of discrete tiles**——每块瓷砖是一个独立色块，砖块间有可见灰缝，整体在远看时组成图像、近看是抽象色块拼接。

## 第一性拆解（Style Decomposition）
- **打光**：整体均匀光照，每块瓷砖有轻微反光与立体高光，玻璃/石质材质光泽
- **色彩**：有限调色板中的色块拼接，相邻瓷砖色彩渐变过渡，金箔/宝石色点缀，装饰性强
- **构图**：图像由成千上万小瓷砖 tessellation 构成，砖块沿形体轮廓流向排布，灰缝(grout)可见
- **参照**：拜占庭/罗马镶嵌艺术、新艺术运动金色装饰拼贴、玻璃马赛克工艺
- **场景/氛围**：装饰壁画/肖像/图腾，庄重华丽、手工工艺感、拼贴的抽象秩序美

## 提示词构成模块
> 完整结构：**风格 - 媒材 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | mosaic tile art, tessellated tile artwork, image made of discrete tiles |
| 媒材 Medium | glass and stone tesserae, visible grout lines between tiles |
| 打光 Lighting | even overall light, slight per-tile specular reflection, glass-stone material sheen |
| 色彩 Color | limited palette color-block tiles, gradient tile-to-tile transition, gold-leaf and gemstone accents, decorative |
| 构图 Composition | thousands of small tiles tessellation, tiles flowing along form contours, visible grout, subject readable at distance |
| 画家参照 Artist Ref | Byzantine Roman mosaic, Art Nouveau gold-leaf decorative collage, glass mosaic craft |
| 场景/氛围 Scene | decorative mural portrait or totem, solemn ornate handcrafted abstract tiled order |

## 结构化提示词（English · 推荐）
```
mosaic tile art, tessellated tile artwork, image made of discrete tiles - glass and stone tesserae, visible grout lines between tiles - [even overall light, slight per-tile specular reflection, glass-stone material sheen] + [limited palette color-block tiles, gradient tile-to-tile transition, gold-leaf and gemstone accents, decorative] + [thousands of small tiles tessellation, tiles flowing along form contours, visible grout, subject readable at distance] + [Byzantine Roman mosaic, Art Nouveau gold-leaf decorative collage, glass mosaic craft] + [decorative mural portrait or totem, solemn ornate handcrafted abstract tiled order], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
马赛克镶嵌拼贴风格，图像由成千上万块离散瓷砖(tesserae)拼贴而成、砖块间有清晰可见的灰缝(grout)，玻璃与石质瓷砖的轻微反光与材质光泽，整体均匀光照，有限调色板的色块拼接与相邻瓷砖的渐变过渡、金箔与宝石色点缀的装饰性色调，瓷砖沿形体轮廓流向排布、远看组成图像近看是抽象色块，对标拜占庭/罗马镶嵌壁画与新艺术运动金色装饰拼贴，庄重华丽而富手工工艺感的拼贴抽象秩序美
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 物件）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是**离散瓷砖拼贴**：务必保留 "mosaic tesserae, visible grout, tessellation"；避免 smooth gradient / photorealistic / pixel-grid（像素画）破坏手工拼贴感；想更古典可加 "Byzantine gold mosaic"，更现代可加 "modern glass tile mosaic"。
4. 可按需替换 [打光]/[色彩]/[构图]/[画家参照]/[场景] 模块强化或微调风格倾向。
