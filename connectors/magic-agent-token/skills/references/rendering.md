# 结果呈现规范：对话内的两类内联展示

连接器只有两类内容进对话内渲染，两者规则不同，不要互相套用：

| 事件 | 是什么 | 片段从哪来 | 正文规则 |
| --- | --- | --- | --- |
| `result_card` | **业务结果**：企微营销虾查询卡的指标、排行、分类计数 | 你按本文模板生成 | 渲染成功后正文只写一句总结 |
| `dag_snapshot` | **执行状态**：任务分几步、每步状态、步骤之间的依赖 | CLI 已生成，原样传给工具 | **不触发一句话规则**，正文该写什么照写 |

**两类都不适用于以 `answer` 正文返回的长文本**——营销策划案、营销文案、会话存档分析结论、跨渠道内容包——保持 markdown 原样。卡片是给结构化数字用的，装不下成篇的文字，套上去只会丢掉行文结构。

## 一、共用：宿主工具与降级

1. 检查当前宿主实际提供的工具。若工具按需加载且有搜索入口，先搜索 `show_widget` / 内联 HTML 渲染工具；按真实工具定义调用，不假设工具存在、不虚构参数名。
2. 片段内容传给代码参数（旧版工具名为 `widget_code`）。**不传文件路径**，不把含 `<html>` / `<head>` / `<body>` 的完整文件当片段，也不拼接残缺片段。
3. **以宿主工具的返回结果确认渲染成功**，再继续输出。CLI 的 `completed`、生成了 HTML 文件、界面出现「正在渲染组件」、`fallbackText` 里的「已展示」都不是渲染成功的证据。
4. 没有内联工具或调用失败时按统一顺序降级，并简短说明限制；不要静默退回表格，不要反复调用同一种失败的工具，也不要因此重跑已完成的业务查询。

调用参数（以宿主真实定义为准）：`title` 用 `<业务名>_<时间口径>`（执行图用 `<计划名>_执行进度`）；`loading_messages` 工具支持时给 4 条短语。

## 二、结果卡（`result_card`）

**适用范围**：成功且含结构化业务数据的 `result_card`。数据在 `payload`（接口原字段）与 `timeRange` 里，全量在 `dataFile`。错误卡展示真实错误，选择卡先收集真实选择，都不套用下面的指标模板。

### 铁律

1. **宿主提供 `show_widget` 时，必须调用它渲染到当前对话**，布局从下面的模板复制、按真实字段增减指标与明细。生成文件、打开预览、贴 HTML 代码块都不算完成内联渲染。
2. **渲染成功后正文只写一句话总结，不超过 100 字**——核心结论或一条建议。**禁止**再用 Markdown 表格 / 列表 / 段落把卡片里的数字重复一遍。允许简短补充的只有：待答问题、数据缺失说明、口径分歧提示。这条只约束与已渲染结果卡重复的内容。
3. **业务数据只来自 `payload`，时间口径来自 `timeRange` 或结果内的统计期字段**。`payloadTruncated: true` 时先读取 `dataFile`，文件根对象是整张卡片，完整数据仍在它的 `payload` 中。字段名不确定时照接口原名展示；缺失值显示 `—`，**不补 0、不重算、不排序**。
4. `cardFile` 是完整 HTML 文件，`dataFile` 是原始 JSON。仅在用户要求下载，或内联渲染不可用且需要文件预览时，用 `present_files` 展示；默认不附这两个文件。

### 设计约束（违反会显得突兀）

- 扁平：无渐变、无阴影、无发光。
- 颜色 / 圆角 / 字体全部走宿主 CSS 变量（`var(--color-*)`、`var(--border-radius-*)`），跟随宿主主题。
- 外层容器 `--color-background-primary` 底 + 0.5px 边框。
- 字号 ≥ 11px；正文 13px、标题 14px/500、KPI 数字 24px/500；只用 400 / 500 两个字重。
- 主色 ≤ 2 种 ramp（purple / teal / blue）；增长用 `--color-text-success`，下降用 `--color-text-danger`。
- 无 emoji、无 HTML 注释；**片段不含 `<html>` / `<head>` / `<body>` / `<!DOCTYPE>`**。
- 开头加一行视觉隐藏的 `<h2>` 一句话摘要（隐藏样式写在片段里，不要假定宿主定义了 `sr-only` 类）。

### 模板选择

| 数据形态 | 模板 |
| --- | --- |
| 业绩 / 资产 / 排行（团队业绩、客户资产、我的排行） | 模板 1：KPI 四宫格 + Top 排行 |
| 待办 / 任务清单（今日待办、团队待办） | 模板 2：分类计数条 |
| 其他小数据集（客户分析、群资产明细） | 模板 3：指标两列表 |

### 模板 1：KPI 四宫格 + Top 排行

```html
<h2 style="position:absolute;left:-9999px;">替换为真实数据的一句话摘要</h2>
<div style="background: var(--color-background-primary); border: 0.5px solid var(--color-border-tertiary); border-radius: var(--border-radius-lg); padding: 1rem 1.25rem; max-width: 640px;">
  <div style="display:flex; align-items:center; justify-content:space-between; padding-bottom:12px; border-bottom:0.5px solid var(--color-border-tertiary);">
    <span style="font-size:14px; font-weight:500;">团队业绩</span>
    <span style="font-size:11px; color:var(--color-text-tertiary);">时间口径说明</span>
  </div>
  <div style="display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:12px; margin:16px 0;">
    <div style="background:var(--color-background-secondary); border-radius:var(--border-radius-md); padding:12px;">
      <div style="font-size:12px; color:var(--color-text-secondary);">指标名</div>
      <div style="font-size:24px; font-weight:500; margin-top:4px;">数值</div>
    </div>
  </div>
  <div style="display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:12px;">
    <div style="border:0.5px solid var(--color-border-tertiary); border-radius:var(--border-radius-md); padding:12px;">
      <div style="font-size:13px; font-weight:500;">接口返回的排行名称</div>
      <div style="margin-top:8px;">
        <div style="display:flex; align-items:center; gap:8px; padding:6px 0; border-bottom:0.5px solid var(--color-border-tertiary);">
          <span style="width:20px; height:20px; border-radius:50%; background:#CECBF6; color:#3C3489; font-size:11px; display:flex; align-items:center; justify-content:center;">1</span>
          <span style="font-size:13px; flex:1;">姓名</span>
          <span style="font-size:13px; color:var(--color-text-secondary);">数值</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

按接口返回顺序复制排行行。只有接口明确提供名次时，才展示名次圆点；普通列表不自行排名。前 3 名圆点：底 `#CECBF6` / 字 `#3C3489`；第 4 名起用 `background:var(--color-background-tertiary); color:var(--color-text-secondary)`。末行去掉 `border-bottom`。

### 模板 2：分类计数条

```html
<h2 style="position:absolute;left:-9999px;">替换为真实待办数据的一句话摘要</h2>
<div style="background: var(--color-background-primary); border: 0.5px solid var(--color-border-tertiary); border-radius: var(--border-radius-lg); padding: 1rem 1.25rem; max-width: 640px;">
  <div style="display:flex; align-items:center; justify-content:space-between; padding-bottom:12px; border-bottom:0.5px solid var(--color-border-tertiary);">
    <span style="font-size:14px; font-weight:500;">今日个人待办</span>
    <span style="font-size:11px; color:var(--color-text-tertiary);">统计日期</span>
  </div>
  <div style="display:flex; margin:16px 0; height:24px; border-radius:6px; overflow:hidden;">
    <div style="flex-grow:21; background:#AFA9EC;"></div>
    <div style="flex-grow:11; background:#5DCAA5;"></div>
    <div style="flex-grow:4; background:#85B7EB;"></div>
  </div>
  <div style="display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:12px;">
    <div style="background:var(--color-background-secondary); border-radius:var(--border-radius-md); padding:12px;">
      <div style="display:flex; align-items:center; gap:6px;">
        <span style="width:8px; height:8px; border-radius:50%; background:#AFA9EC;"></span>
        <span style="font-size:12px; color:var(--color-text-secondary);">分类名</span>
      </div>
      <div style="font-size:24px; font-weight:500; margin-top:4px;">数值</div>
    </div>
  </div>
</div>
```

示例中的 `21` / `11` / `4` 仅演示布局，必须全部替换。堆叠条按实际分类 `count` 设 `flex-grow`，色点与堆叠条一一对应；值为 0 的分类仍保留计数块，缺失值显示 `—` 且不参与堆叠条。总数与百分比只展示接口已提供的值，不从当前页自行汇总。

### 模板 3：指标两列表

```html
<h2 style="position:absolute;left:-9999px;">摘要一句话</h2>
<div style="background: var(--color-background-primary); border: 0.5px solid var(--color-border-tertiary); border-radius: var(--border-radius-lg); padding: 1rem 1.25rem; max-width: 640px;">
  <div style="font-size:14px; font-weight:500; padding-bottom:12px; border-bottom:0.5px solid var(--color-border-tertiary);">标题</div>
  <div style="display:grid; grid-template-columns:repeat(2, minmax(0,1fr)); gap:0; margin-top:4px;">
    <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 4px; border-bottom:0.5px solid var(--color-border-tertiary);">
      <span style="font-size:13px; color:var(--color-text-secondary);">指标名</span>
      <span style="font-size:14px; font-weight:500;">数值</span>
    </div>
  </div>
</div>
```

### 配色速查（亮色主题）

| 用途 | 底色 | 文字 / 描边 |
| --- | --- | --- |
| 主 ramp（排行、图表主色） | `#CECBF6` / `#AFA9EC` | `#3C3489` / `#534AB7` |
| 辅 ramp（第二分类） | `#9FE1CB` / `#5DCAA5` | `#085041` |
| 中性容器 | `var(--color-background-secondary)` | `var(--color-text-secondary)` |
| 正向 / 负向语义 | — | `var(--color-text-success)` / `var(--color-text-danger)` |

### 结果卡流程

```text
chat start --skill ... --query ...
  → 收到成功的 result_card，从 payload 取结构化数字（截断则先读 dataFile）
  → 按数据形态选模板（业绩→1 / 待办→2 / 兜底→3）
  → 复制模板，替换数据，颜色不变
  → 按宿主真实定义调用 show_widget(title=业务名_时间口径, widget_code=片段, loading_messages=4 条)
  → 确认渲染成功，正文只写一句话总结（≤100 字）
  → 无工具或渲染失败：说明限制，再以 Markdown 展示结果
```

## 三、执行图（`dag_snapshot`）

**片段由 CLI 生成，不要自己画。** `widgetCode` 就是完整片段：内联 SVG、节点状态文字、图例和降级说明都已经在里面，按真实节点与依赖排好版。

### 铁律

1. **原样传 `widgetCode`**，不重排节点、不改写依赖、不改配色、不加也不删节点。`widgetCodeTruncated: true` 时读取 `files.widget`，文件内容就是同一段片段；路径只是读取入口，不能当 HTML 传给工具。
2. **没有模板可选**。结果卡的 `payload` / `timeRange`、指标模板和配色速查都不适用于执行图。
3. **不触发一句话规则**。执行图只说明执行到哪一步，不代表业务结果已经展示：独立的 `answer` 正文、HITL 决策资料、文件交付说明都要完整保留，不因为出了图就压缩。
4. **展示时机**：每收到一版新的 `dag_snapshot` 就渲染一次，包括进行中的节点状态推进；只有同一 `(executionId, version)` 已展示过才用一句话带过。完整规则见 [事件与 HITL 指引](events-and-hitl.md) 的 DAG 规则。
5. **notices 要转达**：片段里已写明的降级说明（未识别状态、被忽略的依赖、排版失败）也要在正文提一句。
6. 片段里不含脚本、外链、表单和按钮，**不能在图上作答**；HITL 仍然走宿主真实提问工具。

### 降级顺序

```text
show_widget(widgetCode)          → 成功即止
  ↓ 无工具 / 调用失败 / widgetCode 缺失
present_files(files.svg)         → 说明「未能内联渲染，以下是执行图文件」
  ↓ 无 present_files / 文件缺失
Markdown 表格：编号 | 步骤 | 状态 | 直接依赖
  数据取自事件的 nodes / edges（或 files.data），依赖写真实节点 ID，
  不按任务顺序猜依赖，notices 一并说明
```

### 主题说明

片段用宿主 token（`--color-background-primary`、`--color-text-primary`、`--color-text-tertiary`、`--color-border-tertiary`、`--color-text-success`、`--color-text-danger`、`--border-radius-lg`），**并对没有对应 token 的蓝 / 紫状态色使用组件自有变量**（`--dag-*`），自带浅色值与 `prefers-color-scheme: dark` 覆盖。不要替换这些变量，也不要给它们编造宿主变量名。`files.svg` 是独立文件，配色自带默认值，脱离宿主打开也能看。

### 状态与文案

| 状态 | 文案 | 视觉 |
| --- | --- | --- |
| `pending` | 待执行 | 中性灰 |
| `working` | 进行中 | 蓝 |
| `waiting_input` | 等待回答 | 紫 + 虚线 |
| `completed` | 已完成 | success 语义色 |
| `failed` | 失败 | danger 语义色 |
| `cancelled` | 未执行 | 灰 + 虚线 |

等待回答或失败**不能**说成完成；部分节点完成不能说成整体完成。
