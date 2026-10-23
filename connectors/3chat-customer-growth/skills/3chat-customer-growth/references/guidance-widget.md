# WorkBuddy 启动引导跳转组件

本文件只规定配置入口的呈现方式。何时检查、展示哪些缺失步骤和是否重复引导，遵循 `SKILL.md` 与 [startup-readiness.md](startup-readiness.md)。

## 文字与组件的顺序

保留能力介绍、启动原因和持续优化建议的正文文字。配置步骤使用有序列表，每一步先写标题和操作说明，有入口的步骤再紧接一个独立跳转组件：

1. 输出“1. 创建并发布 Agent”及操作说明，再渲染 3Chat 搭建助手 入口。
2. 输出“2. 接入消息渠道”及操作说明，再渲染渠道入口。
3. 输出“3. 体验真实接待”及操作说明。没有返回相应入口时不渲染组件。

按上述顺序交替输出文字和组件，不把三个步骤全部放入 HTML，不先输出全部组件再补步骤文字。组件只承载入口，不重复正文中的序号、步骤说明或产品介绍。

只缺一个里程碑时，只输出该步骤及入口，列表从 1 开始。重新检查没有进展且只需简短提醒时，不自动重绘组件；用户要求再次提供入口时可以展示。

## 运行时能力与降级

`show_widget` 属于 WorkBuddy 宿主能力，不是 3Chat MCP 工具，也不保证每个版本或客户端都提供。只调用运行时实际存在的工具，并以它的参数说明及组件规范为准；若要求先读取组件规范，先读取再渲染。

- 支持 `show_widget` 时，每个有链接的步骤调用一次，完整三步引导通常共两次；只缺一个里程碑时一次。不要沿用“三步合成一个组件、只调用一次”的约束。
- 若宿主只能把组件集中展示、无法将组件放在对应文字步骤后，则使用逐步骤 Markdown 链接，优先保留文字与入口的对应关系。
- 工具不存在、调用失败或已知外链无法打开时，在对应步骤下使用 `[操作名称](工具返回的完整 URL)`。不要输出 HTML 源码或虚构渲染成功，也不要反复尝试渲染。
- 不自动调用 `present_files` 打开配置网页；链接供用户选择是否进入，不用文件预览替代导航。
- 渲染成功不代表用户已经完成配置，不据此更新里程碑或重新执行启动检查。

## Action 匹配

| 步骤 | `data.actions[].code` | 链接与文案 |
| --- | --- | --- |
| 创建并发布 Agent | `BUILD_OR_PUBLISH_AGENT` | 同一对象的 `url` 和 `label` |
| 接入消息渠道 | `CONNECT_CHANNEL` | 同一对象的 `url` 和 `label` |

按 code 选择 action。文案优先使用非空 `label`；缺少 label 时使用上表步骤名称。不要用已完成步骤的 action 代替缺失入口；缺少有效 HTTP/HTTPS URL 时，保留步骤文字并说明入口暂不可用。

URL 不得拼接、缩短、追加参数或重新编码。嵌入 HTML 时仅做必要的属性转义（例如 `&` 写成 `&amp;`），浏览器解析后的链接必须与原始 URL 一致；label 按 HTML 文本转义，不作为 HTML 执行。

## 单入口 HTML 模板

将以下裸 HTML 片段作为组件内容，参数名以实际 `show_widget` 定义为准。替换占位符后再调用，不把模板直接展示给用户。

```html
<div style="box-sizing:border-box;width:100%;max-width:560px;">
  <a href="{action_url_html_escaped}" target="_blank" rel="noopener noreferrer" style="box-sizing:border-box;display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%;padding:12px 16px;border:0.5px solid var(--color-border-secondary,rgba(0,0,0,0.25));border-radius:10px;background:var(--color-background-primary,#ffffff);text-decoration:none;overflow-wrap:anywhere;">
    <span style="display:flex;flex-direction:column;gap:2px;min-width:0;">
      <span style="font-size:13px;font-weight:500;color:var(--color-text-primary,#111111);">{action_label_html_escaped}</span>
      <span style="font-size:12px;color:var(--color-text-secondary,#666666);">{action_hint_html_escaped}</span>
    </span>
    <span aria-hidden="true" style="flex:0 0 auto;font-size:15px;color:var(--color-text-tertiary,#999999);">&#8599;</span>
  </a>
</div>
```

使用 `<a>` 实现导航，保留键盘聚焦能力；不使用仅有样式但不能导航的 `<button>`。入口占满一行、整行可点，但不给外层包裹容器另加独立的点击区域。3Chat 搭建助手 与渠道入口采用相同样式，不添加重复的步骤序号。

`{action_hint_html_escaped}` 是一句不超过约 20 字的入口提示（例如“进入 3Chat 搭建助手，创建并发布 Agent”），只说明点进去能做什么；不复制正文中的步骤说明、序号或产品介绍。提示中统一使用“3Chat 搭建助手”，不使用 Builder 或 Agent Builder。

入口提示出现“3Chat 搭建助手”时，使用独立的 `<strong>` 元素突出该名称，其余文字仍作为转义后的文本节点；不要把 Markdown 的 `**` 写入 HTML，也不要把 action 文案作为 HTML 执行。

**所有颜色变量都必须写兜底值**，形如 `var(--color-text-primary,#111111)`。组件沙箱不保证注入主题变量：实测中仅写 `var(--color-text-info)` 而不带兜底的元素会因变量未定义而完全透明，表现为“没有样式”。兜底值按浅色主题取值。

**外层容器必须保持透明**：不得自加底色、边框或内边距把它做成卡片。宿主会为每次 `show_widget` 输出自动包一层卡片容器，模板再包一层带底色的卡片，实际渲染就会变成三层嵌套（宿主卡片 → 模板卡片 → 按钮）。背景由宿主提供，底色只允许出现在组件内部的分组元素上。

模板不依赖外部资源或 JavaScript，不包含 `DOCTYPE`、`html`、`head`、`body`。保留响应式宽度和长文案换行，不使用固定定位、渐变、阴影、模糊或 emoji。宿主实际组件规范与模板有差异时，按宿主规范调整样式，同时保留链接目标和文字加组件的输出顺序。
