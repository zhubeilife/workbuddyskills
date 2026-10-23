风格 ID：`style-lego-brick`
原目录：`资产-乐高积木`

# 积木玩具 · 视觉风格提示词

## 分类定位
- **大类**：【二】3D风格
- **中类**：玩具积木
- **标准名**：积木玩具
- **原名**（内部标识，不外显）：乐高风格
- **题材定位**：一切由塑料积木块拼搭而成的 3D 玩具世界，标志性 stud 凸点与 minifigure 小人，**区别于粘土动画的手工肌理与合家欢 3D 动画的有机圆润**

## 风格参考（Reference）
积木玩具 3D 动画电影、积木玩具产品渲染；核心是 **everything built from injection-molded plastic bricks**——圆柱凸点(stud)、方块化几何、minifigure 的 C 型手掌与筒状躯干、光滑注塑塑料的镜面高光，物件之间以标准砖块接口拼接。

## 第一性拆解（Style Decomposition）
- **打光**：明亮均匀的玩具影棚柔光，注塑塑料的光滑镜面高光与清晰环境反射，轻微 AO 接触阴影，欢快通透
- **色彩**：高饱和积木标准色（正红、亮黄、宝蓝、草绿、纯白、亮橙）大色块拼接，鲜明玩具感
- **构图**：一切物体由积木块搭建、stud 凸点清晰可见，方块化几何世界，微缩摆拍浅景深，minifigure 小人居中
- **参照**：积木玩具动画电影级 CG、积木玩具产品广告级 3D 渲染
- **场景/氛围**：minifigure 角色、砖块拼搭的建筑与载具、玩具微缩世界、欢乐童趣的拼搭感

## 提示词构成模块
> 完整结构：**风格 - 相机胶片参数/渲染器 - [打光方案] + [色彩调性] + [构图描述] + [渲染参照] + [场景/氛围]**，末尾统一追加质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | plastic brick-built 3D render, injection-molded plastic toy aesthetic |
| 相机/渲染器 Camera/Renderer | macro on miniature brick set, studio softbox, shallow DOF, glossy CG render |
| 打光 Lighting | bright even toy-studio soft light, glossy plastic specular highlights, crisp reflections, subtle AO contact shadows, cheerful clarity |
| 色彩 Color | high-saturation toy-brick standard palette (bright red, yellow, blue, green, white, orange), large color blocks |
| 构图 Composition | everything built from bricks with visible studs, blocky geometric world, miniature-set shallow DOF, minifigure centered |
| 渲染参照 Render Ref | brick-toy animated feature CG, toy-brick product advertising 3D render |
| 场景/氛围 Scene | toy-brick minifigure characters, brick-built buildings and vehicles, toy miniature world, joyful playful construction |

## 结构化提示词（English · 推荐）
```
plastic brick-built 3D render, injection-molded plastic toy aesthetic - macro on miniature brick set, studio softbox, shallow DOF, glossy CG render - [bright even toy-studio soft light, glossy plastic specular highlights, crisp reflections, subtle AO contact shadows, cheerful clarity] + [high-saturation toy-brick standard palette (bright red, yellow, blue, green, white, orange), large color blocks] + [everything built from bricks with visible studs, blocky geometric world, miniature-set shallow DOF, minifigure centered] + [brick-toy animated feature CG, toy-brick product advertising 3D render] + [toy-brick minifigure characters, brick-built buildings and vehicles, toy miniature world, joyful playful construction], soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 中文提示词（原始描述）
```
积木玩具 3D 渲染风格，对标积木玩具动画电影与积木产品渲染，一切物体由注塑塑料积木块拼搭而成、标志性圆柱凸点(stud)清晰可见与方块化几何世界，minifigure 小人的 C 型手掌与筒状躯干，光滑注塑塑料表面的镜面高光与清晰环境反射，明亮均匀的玩具影棚柔光与轻微 AO 接触阴影，高饱和积木标准色（正红、亮黄、宝蓝、草绿、纯白、亮橙）的大色块拼接，微缩摆拍浅景深，砖块拼搭的建筑与载具，欢乐童趣的玩具微缩世界拼搭感
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 使用说明
1. 文生图时，将上方「结构化提示词」整段作为风格底，拼接你的主体内容（角色 / 场景 / 载具）。
2. 结构化提示词适合 Midjourney / Stable Diffusion 等；需要中文模型可改用「中文提示词」。
3. 本风格核心是**积木拼搭感**：务必保留 "brick-built, visible studs, minifigure, injection-molded plastic"；避免 realistic-human / organic / soft-clay 破坏积木质感；想强化可加 "everything made of plastic toy bricks, glossy plastic sheen"。
4. 可按需替换 [打光]/[色彩]/[构图]/[渲染参照]/[场景] 模块强化或微调风格倾向。
