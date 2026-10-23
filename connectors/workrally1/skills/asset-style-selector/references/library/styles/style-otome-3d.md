风格 ID：`style-otome-3d`
原目录：`资产-3D乙女-美型`

# 3D乙女美型 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：3D游戏CG
- **标准名**：3D乙女美型
- **原名**（内部标识，不外显）：3D乙女-美型

## 风格参考（Reference）
古风 3D 乙女游戏立绘

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [画家参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | 3D ancient-style otome game |
| 相机/渲染器 Camera/Renderer | 3D render, dreamy bloom, jade-skin subsurface |
| 打光 Lighting | soft cinematic key, dreamy halo, floating particles |
| 色彩 Color | cyan-jade, lotus-pink, flowing gold |
| 构图 Composition | official-artwork beauty staging, flowing robe physics |
| 画家参照 Painter Ref | 女性向游戏美术, 古风乙女立绘 |
| 场景/氛围 Scene | ethereal classical beauty, ornate costume close-up |

## 结构化提示词（English · 推荐）
```
3D ancient-style otome game - 3D render, dreamy bloom, jade-skin subsurface - [soft cinematic key, dreamy halo, floating particles] + [cyan-jade, lotus-pink, flowing gold] + [official-artwork beauty staging, flowing robe physics] + [女性向游戏美术, 古风乙女立绘] + [ethereal classical beauty, ornate costume close-up], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
3D 古风乙女游戏视觉风格，唯美梦幻的次世代古风角色渲染，通透柔润的玉质皮肤与飘逸灵动的发丝、衣袂物理细节，精致华美的古风服饰与珠翠材质，柔美的电影级布光与梦幻光晕、漂浮光粒，淡雅仙气的青碧、藕粉与流金色调，唯美仙气的古典氛围，官方立绘般的高精度古风乙游级渲染
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（人物 / 场景 / 动作）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 末尾「统一质感尾缀」已内置于结构化提示词，单独使用其他描述时也建议手动追加，保证全库风格统一的胶片柔焦质感。
4. 可按需替换 [打光]/[色彩]/[构图]/[画家参照]/[场景] 模块强化或微调风格倾向。
