# 布局族规格（骨架层，生成前必选一族）

> 借鉴 studio `families.md` 的「路线 × 布局族正交」思想并简化落地到 cnki 的 10 类形态。目的：**保证交互槽位齐全、不漏**，且主视觉永远占满可用区。

**每次生成必须恰好选一族。** 族是硬约束，不是建议。路线（学生做什么）与族（屏幕怎么分区）正交，可自由组合。

---

## 0. 所有族共用的四条硬规则（来自 studio，同样适用 cnki）

1. **满屏优先。** 主视觉区必须占满可用视口，不留「页边距白」。允许整页只有一屏，无需滚动条。
2. **禁止文档式布局。** 出现以下任一即跑偏：内容被 `max-width` 居中限制在 800–1200px；白/浅灰底+灰边卡片流；主视觉在首屏之外要滚动才看到。
3. **控件浮在场景上。** 操作面板是悬浮层（半透明/毛玻璃/阴影），不是和场景左右平分的普通列。
4. **槽位齐全。** 选定族的槽位表必须**全部**出现。缺槽位比视觉不精致严重得多。

---

## 1. `stage` · 舞台型

**何时用**：探究 / 演示 / 模拟。要「看一个东西怎么变」。
主视觉用 `data-cnki-visual` 标记（canvas / svg / 舞台 div）。

| 槽位 | 类名 | 契约 |
|---|---|---|
| 外壳 | `.app` / `.stage-shell` | 满屏容器 |
| 主视觉 | `[data-cnki-visual]` | canvas/svg/舞台，**占满可用区** |
| 操作面板 | `.panel-float` | 悬浮在场景一侧，半透明+阴影 |
| 读数 HUD | `.readout` | 读数浮层，**不遮挡主视觉主体** |
| 全屏按钮 | `.fs-btn` | 调用 Fullscreen API，带无障碍名 |
| 重置按钮 | `#reset` / `.reset-btn` | 恢复默认视角与参数 |
| 说明条 | `.hint` / `.stage-caption` | 一句话点出现象 |

禁用：主视觉小于半屏；控件做成普通表单列；主视觉需滚动才看全。

---

## 2. `board` · 板书推演型

**何时用**：step / derive。要「一步接一步讲清楚」。

| 槽位 | 类名 | 契约 |
|---|---|---|
| 外壳 | `.board-shell` | 满屏 |
| 板书主面 | `.board-lines` | 可累积、可回退；已完成步骤降低对比 |
| 单步 | `.derive-step` | 每个推导步骤一个块，有编号 |
| 步骤导航 | `.step-nav` | 上一步 / 下一步 / 第 n/N 步 |
| 高亮 | `.highlight-mark` | 只标当前步，同时只存在一个 |
| 公式块 | `.formula-block` | HTML/CSS 排版，**禁止用图片代替公式** |
| 底部状态 | `.board-footer` | 当前进度 + 当前结论 |

禁用：一次性铺完全部推导；步骤间无视觉差异；公式用图片；返回上一步残留高亮。

---

## 3. `coach` · 教练型

**何时用**：story / guided。要「带学生想一遍」（语文情境、阅读理解、英语对话）。

| 槽位 | 类名 | 契约 |
|---|---|---|
| 外壳 | `.coach-shell` | 满屏 |
| 情境舞台 | `.coach-stage` | 场景插画/角色/情境图 |
| 引导气泡 | `.coach-bubble` | **一次只一个问题或一句提示** |
| 学生选项 | `.learner-choice` | 可点选；触控目标 ≥ 学段要求 |
| 提示栈 | `.hint-stack` | 答错时**逐级**给提示，不直接给答案 |
| 进度点 | `.progress-dots` | 当前在第几个情境 |

禁用：讲解写成对话流水账；选项只有对错没反馈理由；第一轮就给答案；气泡里塞段落。

---

## 4. `arcade` · 计分闯关型

**何时用**：game / drill。要「用几道题把知识点练扎实」（课堂互动游戏、单词闯关）。

| 槽位 | 类名 | 契约 |
|---|---|---|
| 外壳 | `.arcade-shell` | 满屏 |
| 关卡条 | `.round-bar` | 第 n/N 题 + 进度 |
| 计分 HUD | `.score-hud` | 分数、连击 |
| 题目卡 | `.question-card` | 一次一题 |
| 选项网格 | `.choice-grid` | 大触控目标，可用数字键选 |
| 结算横幅 | `.result-banner` | **必须含错题归属的知识点**，不只是分数 |

禁用：只判对错不解释；题目与知识点主体无关；为趣味牺牲正确性；答错后不给正确思路。

---

## 5. `bench` · 建构台型

**何时用**：build / assemble / connect。学生「自己搭一个能跑的东西」（电路连接、杠杆平衡、分子拼装）。

| 槽位 | 类名 | 契约 |
|---|---|---|
| 外壳 | `.bench-shell` | 满屏 |
| 元件盘 | `.tray` + `.tray-item` | 可拖元件，标明关键参数 |
| 工作台 | `.workbench` | 放置与连线的画布 |
| 节点层 | `.node-layer` | 可命中点**必须是 DOM 元素**叠在画布上 |
| 连线层 | `.wire-layer` | 已建立的连接，**可删除** |
| 求解面板 | `.solve-panel` | 实时读数 + 是否满足条件 |
| 撤销栈 | `.undo-stack` | 撤销/重做/清空 |
| 提示教练 | `.hint-coach` | 卡住时给方向，不直接给答案 |

交互契约（供 verify 校验「拖了真的有用」）：
```html
<div class="tray-item" data-cnki-drag data-mass="100">…</div>
<button class="hook" data-cnki-drop data-side="left">…</button>
<div class="solve-panel" data-cnki-state>…读数…</div>
```
禁用：用滑块代替拖拽；拖了读数不变（装饰性拖拽）；只允许一种正确搭法；连线不可删除。

---

## 6. 可用区与遮挡（所有族，来自 studio §6）

浮层面板不能压住关键信息。生成后自查：
1. 面板不得遮挡主视觉主体——焦点元素留安全区。
2. 面板之间不得重叠。
3. 窄屏（≤640px）：主视觉仍第一位，面板改底部抽屉/折叠；不变成上下堆叠卡片流。
4. 投影场景：关键标签 ≥18px，对比度按 WCAG AA 留余量。
5. **画布内容也必须避开面板**（canvas 是 JS 画的，不会自动让位）。面板不重叠 ≠ 内容没被挡。

计算安全区（每个 canvas 场景内联这段，按几何位置判断，别按选择器猜）：
```js
function computeSafe(){
  var cr = canvas.getBoundingClientRect(), pad = 14;
  var W0 = cr.width, H0 = cr.height;
  var s = { x0: pad, y0: pad, x1: W0 - pad, y1: H0 - pad };
  var els = document.querySelectorAll('.panel-float,.panel-dock,.readout,.stage-caption,.hint');
  for (var i = 0; i < els.length; i++){
    var el = els[i], cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    var r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    var x0 = r.left - cr.left, y0 = r.top - cr.top, x1 = x0 + r.width, y1 = y0 + r.height;
    if (x1 <= 0 || y1 <= 0 || x0 >= W0 || y0 >= H0) continue;
    if (r.width > W0 * 0.55){
      if ((y0 + y1) / 2 < H0 * 0.5) s.y0 = Math.max(s.y0, y1 + pad);
      else s.y1 = Math.min(s.y1, y0 - pad);
    } else if (x1 < W0 * 0.5) s.x0 = Math.max(s.x0, x1 + pad);
    else if (x0 > W0 * 0.5) s.x1 = Math.min(s.x1, x0 - pad);
    else if ((y0 + y1) / 2 < H0 * 0.5) s.y0 = Math.max(s.y0, y1 + pad);
    else s.y1 = Math.min(s.y1, y0 - pad);
  }
  s.x0 = Math.max(0, Math.min(s.x0, W0 - 140));
  s.x1 = Math.min(W0, Math.max(s.x1, s.x0 + 140));
  s.y0 = Math.max(0, Math.min(s.y0, H0 - 140));
  s.y1 = Math.min(H0, Math.max(s.y1, s.y0 + 140));
  s.w = s.x1 - s.x0; s.h = s.y1 - s.y0;
  return s;
}
```

---

## 7. 族 × 路线 组合速查

| 组合 | 典型课题 | 主要动作 |
|---|---|---|
| 探究 + stage | 凸透镜成像、浮力、欧姆定律 | 拖参数，看舞台与读数 |
| 探究 + arcade | 化学式配平闯关、语法练习 | 答题 → 看解析 |
| 演示 + stage | 有丝分裂、水循环、昼夜交替 | 一镜一镜推进过程 |
| 演示 + board | 面积公式推导、定理证明 | 逐步累积推导 |
| 演示 + coach | 课文情境、阅读理解 | 先选再给提示 |
| 探究 + board | 先推导再验证关系 | 推完一步代值验证 |
| 演示 + arcade | 古诗词填空、单词记忆 | 分镜回顾+闯关 |
| 探究 + bench | 杠杆平衡、电路连接 | 拖元件 → 实时求解 |

> 标记为 `data-cnki-route` / `data-cnki-family` 的声明（写在 `<html>` 标签）会被 `verify_render.py` 读取做提示性校验；不写也不报错，但写了更利于自检与一致性。
