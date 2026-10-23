# 渲染与设计规范（画质核心）

质量差异只来自这里：选对介质、用对设计系统、守住红线。生成时照抄本文件的结构与配方。

---

## 0. 多样性优先原则（本文件第一条红线）

三学段设计系统（§1）只是**基准默认**，不是统一模板。每个动画必须按下面三层派生出**彼此可区分**的视觉，禁止"同色系、同版式、换内容不换皮"：

1. **学科特征**（最强约束）：从 §0.1 学科风格种子取该学科的专属色相 + 母题/图标语言（如小学科学=实验青、小学英语=森林绿动物、高中物理=深空星图）。**同学段不同学科必须明显不同**。
2. **内容情绪**：欢快 / 严谨 / 抒情 / 探究 决定插画气质与动效节奏。
3. **用户显式风格词**（最高优先）：生成前先读提示词，提取"国风 / 科技感 / 手绘 / 低饱和 / 闯关 / 安静演示"等意图，直接覆盖默认。

> 判定标准：同一学段、不同学科的两个动画并排，应能**仅凭配色与母题一眼区分学科**；同一知识点换用户要求应呈现**不同版式**。达不到即返工。

### 0.1 学科风格种子（在学段基准上叠加，不取代学段基底）

| 学段 | 学科 | 专属色相 | 母题 / 图标语言 | 插画气质 |
|---|---|---|---|---|
| 小学 | 语文 | 暖橙 + 墨 | 水墨童趣、笔、卷、星月 | 治愈绘本 |
| 小学 | 数学 | 蓝 + 黄积木 | 七巧板、数线、方块 | 拼搭活泼 |
| 小学 | 英语 | 森林绿 | 动物、树木、对话气泡 | 可爱卡通 |
| 小学 | 科学 | 实验青 | 试管、放大镜、泡泡 | 探索明亮 |
| 初中 | 物理 | 电路橙 | 导线、滑块、场线 | 清晰工程 |
| 初中 | 化学 | 分子紫红 | 原子球棒、火焰 | 反应鲜明 |
| 初中 | 生物 | 叶绿 | 细胞、叶片、DNA | 生命清新 |
| 初中 | 地理 | 地貌棕 | 山脊、洋流、气候带 | 自然沉稳 |
| 高中 | 物理 | 深空蓝 | 星图、矢量场、轨道 | 克制学术 |
| 高中 | 化学 | 反应焰 | 能级、键、焰色 | 冷静锐利 |
| 高中 | 生物 | 细胞青 | 膜、器、流程箭头 | 结构精确 |
| 高中 | 历史 | 卷轴金 | 时间轴、疆域、印章 | 厚重典雅 |
| 高中 | 政治 | 思辨蓝灰 | 关系图、天平、案例卡 | 逻辑清晰 |

（未列学科按"内容情绪 + 用户词"派生，不回退到纯学段默认。）

---

## 1. 三学段设计系统（基准默认，可按 §0 派生变化）

生成前先判学段取**基准**变量（见下表），再按 §0 叠加学科种子与用户风格词。学段基底（深 / 浅 / 彩）仍须一致，但配色与母题必须随学科变化，不锁死成统一模板。

| 维度 | 小学 1–6 | 初中 7–9 | 高中 10–12 |
|---|---|---|---|
| 背景 | 暖白 `#fffbf0` | 浅灰白 `#f8fafc` | 深蓝 `#0f172a` |
| 主色 | 珊瑚红 `#ff6b6b` + 薄荷绿 `#4ecdc4` | 天蓝 `#3b82f6` + 青绿 `#06b6d4` | 淡蓝 `#60a5fa` + 淡紫 `#a78bfa` |
| 强调 | 柠檬黄 `#ffe66d` / 葡萄紫 `#cc5de8` | 琥珀 `#f59e0b` / 水鸭绿 `#14b8a6` | 金黄 `#fbbf24` |
| 卡片 | `#ffffff` 实心 | `#ffffff` 实心 | `rgba(30,41,59,.65)` 毛玻璃 |
| 圆角 | 20px 大阴影 | 14px 轻阴影 | 12px `backdrop-filter: blur(10px)` |
| 标题气质 | emoji + 闯关 / 关卡 / 星星 | 清晰模块标签 + 适度活泼 | 克制学术、少 emoji |
| 练习结构 | 第一关 / 第二关 / BOSS | Level 1 / 2 / 3 | 推导步骤、证据链、公式框 |
| 反馈语气 | 「太棒了！」「没关系，再试一次！」 | 「正确！」「再想想。」 | 简洁诊断，少感叹 |
| 字号正文 | 17–18px 行高 1.8 | 16px 行高 1.8 | 15–16px 行高 1.75 |
| 按钮热区 | ≥ 56px | ≥ 48px | ≥ 44px |

通用：响应式 `grid-template-columns: repeat(auto-fit, minmax(260px,1fr))`；所有控件触屏可点；移动端 `@media (max-width:600px)` 单列。

```css
:root{
  --bg:#f8fafc; --primary:#3b82f6; --secondary:#06b6d4; --accent:#f59e0b;
  --card:#ffffff; --text:#1e293b; --muted:#64748b; --line:rgba(0,0,0,.08);
}
```

---

## 2. AI 生图底图规范（插画 / 情境 / 叙事 / 地貌 / 生态类必走此路）

> 这是达到高保真插画质感的关键路径：手搓 Canvas 插画天然"科技抽象"，AI 生图出真插画。

**何时用**：画面主体是场景、人物、地貌、生物、器物、历史场面，且需要"好看"胜过"可精确测量"。

**生图提示词结构**（顺序固定）：
1. 风格锚定（四选一，同教学点多张保持一致）：`扁平矢量插画` / `治愈系绘本水彩` / `3D 质感渲染` / `剪纸拼贴风`
2. 主体与构图：具体场景 + 给交互层留白（如"上方留出大片干净天空用于叠加文字与控件"）
3. 质量词：`构图干净、色彩柔和、无杂乱元素、教学插画质感`
4. 禁项（务必写）：`无文字、无字母、无坐标轴、无数据标注、无 logo、不拼贴`

**尺寸**：课堂横屏用 `1536x1024`（16:9）；竖屏/手机用 `1024x1536`。

**嵌入方式**（断网单文件要求）：生图后转 base64，用 `<img>` 或 `background-image:url(data:image/...;base64,...)` 内嵌；`object-fit:cover`；**绝不引外链 URL**。多帧场景（如一天四时段）一次生成、交叉淡入时，**必须让每帧构图、相机、地平线完全一致，只变天色与光**，否则淡入时会像镜头在跳。生成后若图带水印，裁掉底边即可。

**AI 生图 → 内嵌 的标准三步**：① 按上面结构写英文提示词生图（16:9，`1536x864`）；② 用 Pillow 缩到 1280 宽、转 JPEG（quality 82），体积约 90KB/张；③ base64 内嵌进 HTML。成品单文件约 0.3MB，断网可用。

**文字层分离（硬性）**：所有必须精确的内容——课文原句、公式、标签、读数、按钮——一律用 HTML 文字叠加在图上（绝对定位 + 半透明底衬保证后排可读），**绝不依赖生图里的文字**。生图只负责"美"，文字交给代码保证"准"。

---

## 3. 3D 配方（天体 / 分子 / 立体几何 / 地球运动）

### 3.1 相机与投影（世界 y 向上，相机朝 +z）

```js
var cam={x:0,y:0,z:0,yaw:0,pitch:-0.25,focal:0};
function project(p){
  var cy=Math.cos(cam.yaw),sy=Math.sin(cam.yaw),cp=Math.cos(cam.pitch),sp=Math.sin(cam.pitch);
  var x=p.x-cam.x,y=p.y-cam.y,z=p.z-cam.z;
  var x1=x*cy+z*sy, z1=-x*sy+z*cy, y2=y*cp-z1*sp, z2=y*sp+z1*cp;
  if(z2<0.05) return null;
  var f=cam.focal/z2; return {x:W/2+x1*f, y:H/2-y2*f, z:z2};
}
// resize 时：cam.focal=Math.min(W,H)*1.4; 相机退到 z=-5 左右，避免远场线投影发散
```

### 3.2 球体着色（带大气、晨昏、高光）

```js
function drawSphere(cx,cy,R,base){
  var atmo=ctx.createRadialGradient(cx,cy,R*0.92,cx,cy,R*1.18);
  atmo.addColorStop(0,'rgba(120,180,255,.35)'); atmo.addColorStop(1,'rgba(120,180,255,0)');
  ctx.fillStyle=atmo; ctx.beginPath(); ctx.arc(cx,cy,R*1.18,0,7); ctx.fill();
  var g=ctx.createRadialGradient(cx-R*0.34,cy-R*0.38,R*0.08,cx,cy,R*1.05);
  g.addColorStop(0,base.hi); g.addColorStop(0.55,base.mid); g.addColorStop(1,base.lo);
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,R,0,7); ctx.clip();
  ctx.fillStyle=g; ctx.fillRect(cx-R,cy-R,R*2,R*2);
  // 贴图（大陆/条纹）：在 clip 内按经纬度投点，只画正面半球
  if(base.paint) base.paint(ctx,cx,cy,R);
  var term=ctx.createLinearGradient(cx-R*0.1,cy-R*0.1,cx+R,cy+R);
  term.addColorStop(0,'rgba(0,0,0,0)'); term.addColorStop(1,'rgba(2,8,20,.5)');
  ctx.fillStyle=term; ctx.fillRect(cx-R,cy-R,R*2,R*2);
  ctx.restore();
  ctx.beginPath(); ctx.arc(cx,cy,R,0,7); ctx.strokeStyle='rgba(180,220,255,.22)'; ctx.lineWidth=1.2; ctx.stroke();
}
```

### 3.3 曲线 + 深度排序（场线 / 轨道 / 磁力线）

参数方程生点列 → 逐点投影 → 以球心深度为界分"球前/球后"两遍绘制（球后先画、球前后画）→ 箭头沿切线方向。完整可运行样板见 `templates/geomagnetic-3d.html`。

**预算**：同屏 ≤ 400 面；低多边形（纯色面 + 2 档明暗）即可，不追纹理。**深空氛围**：径向渐变深蓝黑底 + 220 颗抖动星点。

---

## 4. 2D 分层场景配方（代码绘制场景类）

五层从后往前：天空渐变 → 远景（山/云，越远越淡越偏蓝）→ 中景（水面 + 倒影）→ 近景（3–5 个克制元素）→ 氛围（雾 `lighter` 光、粒子）。

- **倒影**：主体沿水面线翻转、纵向压 0.45、透明度 0.32、轻微波动。
- **材质光影**：每个物体 ≥ 3 明度档；圆柱水平渐变（暗-亮-暗），球径向渐变；玻璃/金属加一条半透明白高光条；底部椭圆落影 `rgba(0,0,0,.2)`。
- **状态切换**：改插值目标，400–600ms 内平滑过渡，绝不跳变闪白。

---

## 5. SVG 配方（数据 / 图表 / 游戏 / 工具）

- 用 `<svg>` + `<defs>` 渐变 / `feGaussianBlur` / `feDropShadow` 做干净矢量视觉，比手绘 Canvas 更"产品感"。
- 动效用 CSS `@keyframes` / `transition` 或 `requestAnimationFrame` 驱动 SVG 属性；交互命中区用透明 `<rect>` / 大热区。
- 游戏/分类/配对：用真实 DOM 按钮 + 拖拽（Pointer 事件），命中即变色 + 反馈文案。

---

## 6. 交互完整度清单（每作品必过）

1. **全屏**按钮（右上，调用 `requestFullscreen`）。
2. **选中态**：当前项高亮描边/底色，未选灰显。
3. **操作提示**：常驻一行「拖动…／点击…／滑动…」。
4. **即时反馈**：操作后 300ms 内出文字/视觉反馈（对/错、数值变化）。
5. **重置**：回到初始状态（视角/参数/进度）。
6. **触屏可用**：所有控件 Pointer 事件，热区 ≥ 学段下限。
7. **最小学习闭环**：引入问题 → 操作探究 → 即时反馈 → 小结迁移（哪怕只有 4 屏内的小闭环）。

---

## 7. 内容丰富度红线（出现即返工）

- ❌ 纯色块 / 几何形状做无意义运动（"科技感"伪装）。
- ❌ 只放一张静态图再缩放 / 旋转当动画。
- ❌ 只有标题文字飞入飞出，无实质视觉演示。
- ❌ 多场景"换色不换内容"、视觉高度雷同。
- ❌ UI 用紫蓝对角渐变、发光描边、emoji 当图标（场景里的光/辉光是绘画手段，UI 装饰禁用）。
- ❌ 把精确文字（课文原句/公式/标签）烤进生图，导致看不清或出错。

**分学科动画必含元素**：

| 学科 | 必含动态元素 | 禁止敷衍 |
|---|---|---|
| 数学 | 函数曲线动态绘制、坐标变换、参数滑块联动 | 只显示公式 |
| 物理 | 力/运动/场的向量动画、器材操作过程 | 只放结果截图 |
| 化学 | 分子/原子运动、反应过程、实验现象变化 | 只显示方程式 |
| 生物 | 细胞/器官/生态的动态过程 | 只放教科书插图 |
| 语文 | 意境画面渐入 + 原文逐句出现 + 氛围 | 只放文字幻灯片 |
| 历史 | 时间线推进、疆域变化、因果链 | 只列年份事件 |
| 地理 | 地形/气候/洋流自然过程动态演示 | 只放静态地图 |
| 英语 | 对话场景演示、语法结构拆解 | 只列单词表 |

---

## 8. 生活化实验规范（物理 / 化学 / 生物探究必守）

交互载体必须是学生**亲身经历或见过**的生活场景，禁止抽象示意图或纯数值面板。

| 知识点 | ❌ 抽象 | ✅ 生活化 |
|---|---|---|
| 浮力 | 量筒+物块示意图 | 游泳池：拖不同物体（乒乓球/硬币/橡皮泥船），调水的密度（清水→盐水→死海） |
| 大气压 | "1cm²≈一个苹果" | 马德堡半球：拖学生到两侧，看需几人拉开；切山顶/山脚对比 |
| 液体压强 | 公式+表格 | 深海探索：拖深度滑块，看鱼身形变与压强数值 |
| 杠杆 | 支点+力臂图 | 跷跷板：拖不同体重孩子到不同位置看平衡 |
| 电阻 | 电路符号 | 水管类比：粗/细管对应低/高电阻，拖阀门调"水压"看"水流" |

类比参照用学生能掂量的东西（书包5kg、同学50kg、小汽车1.5吨、大卡车10吨），避免直接用牛顿/帕斯卡做类比。

---

## 9. 渲染档 T1 / T2 / T3（性能与保真分级）

> T1/T2/T3 渲染档（性能与保真分级）。目的：**按设备与课题选对保真度**，低端机不卡、高保真不廉价。在 `<html>` 上用 `data-cnki-tier` 声明；`verify_render.py` 会读取做提示性校验。

| 档 | 适用 | 主视觉做法 | 硬要求 |
|---|---|---|---|
| **T1 轻量** | 旧机 / 弱网 / 纯 SVG 图表游戏 | 纯 CSS + SVG，无逐帧 canvas 重绘 | 必须带 `data-cnki-fallback` 降级说明；有重置 + 旋转/缩放输入（若有 3D） |
| **T2 标准（默认）** | 绝大多数课堂动画 | canvas/SVG 五层法（§4），带光影材质 | 主视觉 ≥ 3 处**渐变创建调用**（禁纯色平涂）；带分层光影 + 接触阴影 |
| **T3 高保真** | 公开课 / 地理地球 / 分子 / 器官 | AI 生图底图 + 代码交互层，或复杂 3D | 同屏 ≤ 400 面预算；深空/具形/贴图地球按 §10 配方 |

**降级路径（硬要求，闸门会查）**：任何动效都必须能在 `prefers-reduced-motion: reduce` 下**功能完整**地运行——不自动播放，但仍能手动步进、仍能拖动参数。CSS 里加：

```css
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{
    animation-duration:.01ms !important;
    animation-iteration-count:1 !important;
    transition-duration:.01ms !important;
  }
}
```

> 写法说明：reduced-motion 同时要在 `<style>` 里出现（G8 闸门查的就是这个），不要只写进 JS 注释。

---

## 10. 真实感渲染配方（拉高 3D / 空间 / 具形类上限）

> 地球等天体禁止"代码渐变球"平涂。本节给出可直接抄的高保真配方（贴图地球 / 具形器官 / T3 渲染档）。

### 10.1 贴图地球（程序化，无需外图）

在 §3.2 `drawSphere` 之上加一个 `paint` 函数：经纬网格 + 大陆斑块 + 晨昏线，全部用经纬度投影点，只画正面半球。

```js
function paintGlobe(ctx, cx, cy, R){
  // 经纬网格
  ctx.strokeStyle = 'rgba(255,255,255,.12)'; ctx.lineWidth = 1;
  for (var lat = -60; lat <= 60; lat += 30){
    ctx.beginPath();
    for (var lon = -180; lon <= 180; lon += 6){
      var p = ll2xy(lon, lat, cx, cy, R);
      if (p) (lon === -180) ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
    }
    ctx.stroke();
  }
  for (var lon = -180; lon < 180; lon += 30){
    ctx.beginPath();
    for (var lat = -90; lat <= 90; lat += 6){
      var p = ll2xy(lon, lat, cx, cy, R);
      if (p) (lat === -90) ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
    }
    ctx.stroke();
  }
  // 大陆斑块（示例：几个经纬度 blob，按真实海陆大致位置）
  var land = [[-100,-40,42],[20,-10,55],[110,55,40],[10,50,26],[135,-25,34]];
  ctx.fillStyle = 'rgba(76,140,72,.9)';
  for (var i = 0; i < land.length; i++){
    var b = land[i], c = ll2xy(b[0], b[1], cx, cy, R);
    if (!c) continue;
    ctx.beginPath(); ctx.ellipse(c.x, c.y, b[2], b[2]*0.7, 0, 0, 7); ctx.fill();
  }
}
// 经纬度 → 屏幕（球面投影，背面剔除）
function ll2xy(lon, lat, cx, cy, R){
  var la = lat * Math.PI/180, lo = lon * Math.PI/180;
  var x = Math.cos(la) * Math.sin(lo);
  var y = Math.sin(la);
  var z = Math.cos(la) * Math.cos(lo);   // 正对相机为 +z
  if (z < -0.05) return null;             // 背面
  var f = R * 1.1;
  return { x: cx + x * f, y: cy - y * f };
}
// 使用：drawSphere(cx,cy,R, {hi:'#bfe3ff',mid:'#3b82c4',lo:'#0b3a66', paint: paintGlobe});
```

### 10.2 具形器官 / 分子（SVG，带材质）

器官/管腔/分子**禁止纯色几何块平涂**。用 SVG 渐变 + 深描边 + 接触阴影画体积：

```html
<defs>
  <radialGradient id="tube" cx="35%" cy="30%">
    <stop offset="0" stop-color="#ffd2c2"/><stop offset="1" stop-color="#c0504d"/>
  </radialGradient>
  <filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<!-- 接触阴影 -->
<ellipse cx="160" cy="250" rx="90" ry="16" fill="rgba(0,0,0,.18)" filter="url(#soft)"/>
<!-- 管腔（半透明） -->
<path d="M60 160 Q160 120 260 160" stroke="url(#tube)" stroke-width="34"
      fill="none" stroke-linecap="round" opacity=".9"/>
<!-- 深描边勾轮廓 -->
<path d="M60 160 Q160 120 260 160" stroke="rgba(120,30,30,.55)" stroke-width="2" fill="none"/>
```

分子（球棒模型）：每个原子 = `radialGradient` 球 + 白高光点；键 = 半透明圆柱（两条平行线 + 顶部高光）。

### 10.3 矢量场（物理：力 / 场线）

```js
function drawField(ctx, fn, x0, y0, w, h, step){
  ctx.strokeStyle = 'rgba(120,160,255,.7)'; ctx.fillStyle = 'rgba(120,160,255,.9)';
  for (var y = y0; y < y0 + h; y += step)
    for (var x = x0; x < x0 + w; x += step){
      var v = fn(x, y);                       // 返回 {vx, vy} 单位向量
      var m = Math.hypot(v.vx, v.vy) || 1;
      var ux = v.vx/m, uy = v.vy/m, L = step*0.42;
      var ex = x + ux*L, ey = y + uy*L, sx = x - ux*L, sy = y - uy*L;
      ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex, ey); ctx.stroke();
      // 箭头
      ctx.beginPath();
      ctx.moveTo(ex, ey);
      ctx.lineTo(ex - ux*6 - uy*4, ey - uy*6 + ux*4);
      ctx.lineTo(ex - ux*6 + uy*4, ey - uy*6 - ux*4);
      ctx.closePath(); ctx.fill();
    }
}
// 示例：点电荷径向场 fn = (x,y)=>{var dx=x-cx,dy=y-cy,d=Math.hypot(dx,dy)||1;return{vx:dx/d,vy:dy/d};}
```

### 10.4 天体氛围（深空）

径向渐变深蓝黑底 + 220 颗抖动星点（§3.3 已给），叠加 §10.1 的贴图地球即可达到高保真深空质感。
