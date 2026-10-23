风格 ID：`style-hardcore-wasteland-3d`
原目录：`资产-硬核废土3D`

# 硬核废土3D · 视觉风格提示词

> 融合来源：`资产-CG角色资产建立`（CG-3D-CHARACTER-RENDER-v5.0 九层结构化方法论）＋ `21-hardcore-wasteland-3d`（硬核废土视觉调性）。
> 风格锚点：国产顶级末世 3D 动画——末世废土科幻、高精度 3D CG、NPR+PBR 混合、定帧像素级清晰。

## 分类定位
- **大类**：【二】3D风格
- **中类**：国漫3D风格
- **标准名**：硬核废土3D
- **原名**（内部标识，不外显）：硬核废土3D（灵笼级 CG 角色渲染）

## 风格参考（Reference）
国产末世废土 3D 动画（主对标）、成人向科幻动画短片废土篇、硬核机械概念设定、赛博朋克动画机械设计。**对标国产顶级末世 3D 动画的定帧画质：像素级清晰、光影分明、明暗鲜明、极致高清**，末世废土的冷峻硬核质感。

## 提示词构成模块
> 完整结构：**风格 - 渲染引擎 - [打光方案] + [色彩调性] + [构图描述] + [概念参照] + [场景/氛围]**，末尾统一追加画质约束 + 质感尾缀。

| 模块 | 内容 |
| --- | --- |
| 风格 Style | Hardcore wasteland sci-fi 3D, top-tier Chinese 3D animation-grade CG character render |
| 渲染引擎 Renderer | UE5 path tracing, NPR+PBR 混合（面部 NPR 赛璐璐 + 服饰道具 PBR），SSS skin, AO, GI |
| 打光 Lighting | strong hard key, heavy shadow, cold-blue tech glow, rim light on metal |
| 色彩 Color | cold grey, dark green, rust brown + cold-blue tech light |
| 构图 Composition | gritty mechanical depth, oppressive industrial scale, cinematic character staging |
| 概念参照 Concept Ref | 末世 3D 动画美术, 硬核机甲设定, hard-surface sci-fi concept design |
| 场景/氛围 Scene | dim wasteland, distressed metal, wet concrete, apocalypse survivor |

## 九层结构化提示词核心框架（强制顺序）
> 融合 CG-3D-CHARACTER-RENDER-v5.0 方法论。前置内容权重更高，每层仅描述眼睛可直接看到的视觉事实，禁用抽象形容词。

1. **主风格锚定**：首句锁定渲染引擎与对标，国产顶级末世 3D 动画级定帧画质，NPR+PBR 混合
2. **角色核心外貌**：性别年龄→体型比例→面部特征→发型发色→眼瞳→皮肤 SSS 质感
3. **服装与装备**：PBR 物理材质，名称→款式→颜色→材质→纹理→装饰（布料/皮革/金属/做旧锈蚀）
4. **姿态与表情**：身体朝向→重心→脊柱→四肢手势→面部表情→气场
5. **场景与环境**：从远到近，废土环境精简到核心视觉锚点
6. **光影系统**：主光源方向+色温+强度、轮廓光、环境光遮蔽、体积光、GI
7. **镜头规格**：焦距、光圈、景深、构图、视角
8. **技术画质参数**：8K, ray tracing GI, SSS, AO, PBR metalness/roughness, path tracing, micro-detail, noise-free
9. **约束与输出**：必须元素、禁止元素、宽高比、解剖学约束

## 结构化提示词（English · 推荐）
```
A UE5 path-traced cinematic 3D CG character render, benchmarked to top-tier Chinese post-apocalyptic 3D animation frame quality, NPR+PBR hybrid architecture (NPR cel-shaded face + PBR wardrobe/metal) - [strong hard key light, heavy shadow, cold-blue tech glow, rim light on distressed metal] + [cold grey, dark green, rust brown + cold-blue tech light] + [gritty mechanical depth, oppressive industrial scale, cinematic character staging] + [post-apocalyptic 3D animation art direction, hardcore mecha concept, hard-surface sci-fi concept design] + [dim wasteland, distressed weathered metal, wet concrete, apocalypse survivor], 8K ultra high resolution, ray tracing global illumination, subsurface scattering, ambient occlusion, PBR metalness/roughness workflow, micro-detail texture maps, noise-free render, soft focus edges, gentle edge falloff, film-like softness, halation on highlights, no digital sharpening, subdued micro-detail.
```

强制画质尾缀（不可修改）：
```
Clean and polished image, controlled details, smooth and consistent texture, clear subject-background separation, no over-sharpening, no color blotches, no noise, no broken patterns, no artifacts, no distortion.
```

## 中文提示词（原始描述）
```
硬核废土科幻 3D 动画风格，对标国产顶级末世 3D 动画定帧画质，冷峻写实的末世硬核质感，精密粗粝的机械结构与做旧金属材质（PBR 物理材质），灰暗压抑的废土环境与潮湿混凝土肌理，低饱和的冷灰、暗绿与锈褐色调点缀冷蓝科技光，强烈的硬光与厚重阴影对比，次表面散射的皮肤通透质感，NPR+PBR 混合渲染（面部赛璐璐 + 服饰道具物理材质），沉重压迫的末世氛围，像素级清晰的高精度硬核国漫三维渲染
```

## 统一质感尾缀
```
soft focus edges, gentle edge falloff, film-like softness, halation on highlights, photochemical softness, analog edge bloom, no digital sharpening, restrained detail, minimalist texture, large color blocks, negative space, graphic simplicity, hierarchy of focus, single focal point, unified material, smooth surfaces, clean rendering, matte finish, cohesive texture language, subdued micro-detail
```

## 角色锚点系统（多图一致性，精简九维）
面部结构 / 眼瞳特征 / 发型 / 身体比例 / 肤色材质 / 服装 / 装备 / 表情 / 特殊独有特征。生成多图时固定引用锚点串，锁定核心特征实现跨图一致。

## 质量分层
- **L1 快速预览**（80-150字）：验证造型构图
- **L2 标准产出**（200-350字）：常规配图
- **L3 商业精稿**（400-600字）：海报/角色主视觉
- **L4 影视顶级**（600-1000字）：动画定帧/设定集（顶级 3D 动画级）

## 标准布光方案（可直接复用）
三角光 / 分光（亦正亦邪）/ 轮廓光主导（神秘）/ 三点布光（展示）/ 顶光（神圣压迫）/ 底光（反派诡异）/ 黄金时刻暖光（唯美）/ 冷白月光（冷峻）—— 废土首选：轮廓光主导 + 冷白月光 + 分光。

## 使用说明
1. 文生图时，将「结构化提示词」整段作为风格底，按九层框架拼接你的角色主体内容。
2. 末尾强制画质尾缀不可省略；质感尾缀保证全库统一胶片柔焦。
3. 本风格为**顶级 3D 动画级 CG 写实**：避免使用 illustration、anime cel（纯2D）、watercolor 等词，会偏离 3D 渲染观感。
4. 角色多图一致性：固定「角色锚点串」复用到每张，仅改姿态/场景/镜头。
5. 单轮迭代仅改 1-2 个元素，并声明"严格保持其他所有元素不变"。
