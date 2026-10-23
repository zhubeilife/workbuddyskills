# workbuddyskills 完整清单（中文说明·补充版）

> 本文件在 `CATALOG.md` 基础上生成，补录了原清单缺失的官方外部插件（149 个）、连接器内嵌技能统计与元数据文件说明；其余内容与 `CATALOG.md` 一致。所有「用来做什么」均已统一为中文概述；每行末尾的「最后更新」为该条目在 git 中最近一次变更的日期（即上游同步带来变化的日期），下次同步后可据此对比差异。

每个条目包含：**用来做什么**、**前置条件**（API Key / 登录认证等）。目录与名称**可点击**跳转。

**前置条件 = 无**：一般不需额外密钥或登录即可阅读/使用说明；调用外部服务时平台侧仍可能有限制。

- 技能包：**295** · 连接器：**443**（其中 393 个自带共 829 个内嵌技能） · 专家：**429** · 官方插件：**209**（市场自带 60 + 外部插件 149） · 团队插件：**30**

> 清单自动同步自 WorkBuddy 公开市场；最近同步：2026-10-23

---
## 目录

1. [技能包 skills/](#1-技能包-skills)
2. [连接器 connectors/](#2-连接器-connectors)
3. [专家包 experts/](#3-专家包-experts)
4. [插件市场 plugins/](#4-插件市场-plugins)
5. [补充：原清单未覆盖的内容](#5-补充原清单未覆盖的内容)

## 1. 技能包 `skills/`

### AI / Agent 工具（159）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`agent-browser-core`](./skills/agent-browser-core/) | [agent-browser-core](./skills/agent-browser-core/SKILL.md) | agent-browser CLI（Rust 实现，Node.js 兜底）的浏览器自动化技能，驱动 Agent 操作浏览器。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`agent-mail`](./skills/agent-mail/) | [agentmail](./skills/agent-mail/SKILL.md) | AI Agent 专属邮箱：收发邮件、查收消息，使用自己的 @agentmail 地址对外通信。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`AGENTMAIL_API_KEY`、`YOUR_API_KEY` | 2026-07-21 |
| [`agent-mbti`](./skills/agent-mbti/) | [agent-mbti](./skills/agent-mbti/SKILL.md) | 基于 MBTI 框架的 AI Agent 人格诊断与配置系统。 | 无 | 2026-07-21 |
| [`agent-team-orchestration`](./skills/agent-team-orchestration/) | [agent-team-orchestration](./skills/agent-team-orchestration/SKILL.md) | 多智能体团队编排：定义角色、任务生命周期、交接协议与协作流程。 | 无 | 2026-07-21 |
| [`ai-shifu-course-creator`](./skills/ai-shifu-course-creator/) | [ai-shifu-course-creator](./skills/ai-shifu-course-creator/SKILL.md) | AI师傅（AI-Shifu）课程的创建、编写与管理。 | 需要登录 / OAuth / 扫码授权；需要环境变量：`SHIFU_TOKEN` | 2026-07-21 |
| [`aihot`](./skills/aihot/) | [aihot](./skills/aihot/SKILL.md) | AI HOT (aihot.virxact.com) 中文 AI 资讯查询 Skill。当用户想知道"今天 AI 圈有什么"、"AI 日报"、"AI HOT"、"AI 资讯"、"… | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`airchina-travel-assistant`](./skills/airchina-travel-assistant/) | [airchina-travel-assistant](./skills/airchina-travel-assistant/SKILL.md) | 帮用户领取中国国航（Air China / 国航 / 国际航空）的优惠券。当用户说"我想领国航的券"、"帮我领张国航机票券"、"国航有活动券吗"、"给我发国航优惠券"、"airc… | 需要环境变量：`SECRET_KEY` | 2026-07-21 |
| [`anti-distill`](./skills/anti-distill/) | [anti-distill](./skills/anti-distill/SKILL.md) | 员工技能的反蒸馏防护：清洗技能文件，防止被他人模型蒸馏窃取。 | 无 | 2026-07-21 |
| [`api-gateway`](./skills/api-gateway/) | [api-gateway](./skills/api-gateway/SKILL.md) | 通过 Maton 托管的 API 路由连接外部服务。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`API_KEY`、`MATON_API_KEY`、`YOUR_API_KEY` | 2026-07-21 |
| [`apple-notes`](./skills/apple-notes/) | [apple-notes](./skills/apple-notes/SKILL.md) | 在 macOS 上通过 memo CLI 管理 Apple 备忘录（创建、查看、编辑、删除、搜索）。 | 无 | 2026-07-21 |
| [`apple-reminders`](./skills/apple-reminders/) | [apple-reminders](./skills/apple-reminders/SKILL.md) | 在 macOS 上通过 remindctl CLI 管理 Apple 提醒事项（列表、新增、编辑、完成、删除）。 | 无 | 2026-07-21 |
| [`arxiv-reader`](./skills/arxiv-reader/) | [arxiv-reader](./skills/arxiv-reader/SKILL.md) | 利用python，指定某个arxiv_id/url， 基于 LLM Agent 对这篇arxiv论文进行分类与深度阅读，直接print打印阅读笔记 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`LLM_API_KEY` | 2026-07-21 |
| [`arxiv-watcher`](./skills/arxiv-watcher/) | [arxiv-watcher](./skills/arxiv-watcher/SKILL.md) | 搜索并总结 ArXiv 论文，适合追踪最新研究进展。 | 无 | 2026-07-21 |
| [`autoresearch`](./skills/autoresearch/) | [autoresearch](./skills/autoresearch/SKILL.md) | Karpathy 式自动研究优化：对任意内容生成 50+ 变体并迭代评分优选。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`ANTHROPIC_API_KEY` | 2026-07-21 |
| [`awesome-design-md`](./skills/awesome-design-md/) | [awesome-design-md](./skills/awesome-design-md/SKILL.md) | 54 个真实开发者网站的 DESIGN.md 设计规范合集，供参考和对照。 | 无 | 2026-07-21 |
| [`baidu-drive`](./skills/baidu-drive/) | [baidu-drive](./skills/baidu-drive/SKILL.md) | 百度网盘(Baidu Drive)文件管理 — 上传、下载、转存、分享、搜索、移动、复制、重命名、创建文件夹。TRIGGER: 用户提及\"百度网盘/bdpan/网盘/云盘/ba… | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`boss-skills`](./skills/boss-skills/) | [boss-skills](./skills/boss-skills/SKILL.md) | 把真实老板或知名企业家蒸馏成 AI 技能，复刻其决策风格。 | 无 | 2026-07-21 |
| [`brand-guidelines`](./skills/brand-guidelines/) | [brand-guidelines](./skills/brand-guidelines/SKILL.md) | 把 Anthropic 官方品牌色与字体规范应用到各类产出物上。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`browser`](./skills/browser/) | [browser](./skills/browser/SKILL.md) | 简单的 Puppeteer 无头浏览器：渲染 JS 重度页面并提取内容。 | 无 | 2026-07-21 |
| [`browser-cash`](./skills/browser-cash/) | [browser-cash](./skills/browser-cash/SKILL.md) | 通过 Browser.cash API 使用可绕过反爬保护（Cloudflare 等）的云浏览器会话。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_CASH_API_KEY`、`BROWSER_CASH_KEY` | 2026-07-21 |
| [`browser-use`](./skills/browser-use/) | [browser-use](./skills/browser-use/SKILL.md) | 浏览器自动化：网页测试、表单填写、截图与数据提取。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`BROWSER_USE_API_KEY` | 2026-07-21 |
| [`cangjie-skill`](./skills/cangjie-skill/) | [cangjie-skill](./skills/cangjie-skill/SKILL.md) | 把一本书拆解成一组连贯可执行的技能（拆书/知识蒸馏）。 | 无 | 2026-07-21 |
| [`capability-evolver`](./skills/capability-evolver/) | [capability-evolver](./skills/capability-evolver/SKILL.md) | AI Agent 自我进化引擎：分析运行历史发现改进点，按协议约束进化，需 GitHub Token 自动上报 issue 与发版。 | 需要 GitHub Token 或 `gh auth login`；需要环境变量：`GITHUB_TOKEN` | 2026-07-21 |
| [`clawbrowser`](./skills/clawbrowser/) | [clawbrowser](./skills/clawbrowser/SKILL.md) | 通过 Microsoft Playwright CLI 驱动浏览器。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`cli-anything-hub`](./skills/cli-anything-hub/) | [cli-anything-hub](./skills/cli-anything-hub/SKILL.md) | 发现各专业软件的 agent-native CLI：访问实时目录找到可用命令行工具。 | 无 | 2026-07-21 |
| [`cloudbase`](./skills/cloudbase/) | [cloudbase](./skills/cloudbase/SKILL.md) | CloudBase 全栈开发与部署工具包：构建并上线 Web/小程序/云函数/数据库/云存储/AI 模型等应用。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`cloudflare`](./skills/cloudflare/) | [cloudflare](./skills/cloudflare/SKILL.md) | Cloudflare 平台全家桶：Workers、Pages、KV/D1/R2 存储等开发与运维。 | 无 | 2026-07-21 |
| [`cloudq`](./skills/cloudq/) | [cloudq](./skills/cloudq/SKILL.md) | 用户咨询腾讯云产品资源、AWS、阿里云等多云资源时，查看智能顾问架构图、架构目录、架构详情、架构评估结果、绘制架构图、开通智能顾问时、AI智能巡检、AI容量监测、AI混沌演练、A… | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`TENCENTCLOUD_SECRET_KEY`、`TENCENTCLOUD_TOKEN` | 2026-07-21 |
| [`cn-ecommerce-search`](./skills/cn-ecommerce-search/) | [cn-ecommerce-search](./skills/cn-ecommerce-search/SKILL.md) | 跨 8 大中国电商平台（淘宝/天猫/京东/拼多多/1688/速卖通/抖音/小红书）搜商品，零配置无需 API Key。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`colleague-skill`](./skills/colleague-skill/) | [colleague-skill](./skills/colleague-skill/SKILL.md) | 把同事蒸馏成 AI 技能：自动采集飞书/钉钉/Slack 数据并生成。 | 需要飞书应用凭证或用户登录授权；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`content-factory`](./skills/content-factory/) | [content-factory](./skills/content-factory/SKILL.md) | 多智能体内容生产系统：一份源内容产出多种形态的成品。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`content-ops`](./skills/content-ops/) | [content-ops](./skills/content-ops/SKILL.md) | 内容评分、评估与迭代改进：自动组装评审团给内容打分优化。 | 无 | 2026-07-21 |
| [`content-repurposer`](./skills/content-repurposer/) | [content-repurposer](./skills/content-repurposer/SKILL.md) | 把长内容改写成各平台适配的短文/帖子。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`conversion-ops`](./skills/conversion-ops/) | [conversion-ops](./skills/conversion-ops/SKILL.md) | CRO 审计与落地页转化优化，把调查问卷转化为引流磁铁。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`crash-expert-skill`](./skills/crash-expert-skill/) | [crash-expert-skill](./skills/crash-expert-skill/SKILL.md) | Linux 内核 vmcore/coredump 崩溃分析专家技能。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`darwin-skill`](./skills/darwin-skill/) | [darwin-skill](./skills/darwin-skill/SKILL.md) | 达尔文技能：受 Karpathy autoresearch 启发的自主技能优化器。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`deck-generator`](./skills/deck-generator/) | [deck-generator](./skills/deck-generator/SKILL.md) | 生成带 AI 配图的专业演示文稿。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`GEMINI_API_KEY` | 2026-07-21 |
| [`deep-research`](./skills/deep-research/) | [deep-research](./skills/deep-research/SKILL.md) | 结构化深度研究工作流，带人工干预节点，用 /research 生成研究报告。 | 无 | 2026-07-21 |
| [`diagnose`](./skills/diagnose/) | [diagnose](./skills/diagnose/SKILL.md) | 疑难 bug 与性能回退的纪律化诊断闭环：复现→最小化→定位→修复。 | 无 | 2026-07-21 |
| [`didi-ride-skill`](./skills/didi-ride-skill/) | [didi-ride-skill](./skills/didi-ride-skill/SKILL.md) | 中国城市出行服务。当用户表达任何交通出行需求时必须使用此技能——包括打车/叫车/网约车、查价格、路线规划（公交/驾车/步行/骑行）、周边搜索、查询订单/司机位置/取消订单。关键词… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`DIDI_MCP_KEY`、`YOUR_KEY` | 2026-07-21 |
| [`earnings-tracker`](./skills/earnings-tracker/) | [earnings-tracker](./skills/earnings-tracker/SKILL.md) | AI 驱动的财报追踪器，自动扫描 A 股/美股财报日历，推送重要财报更新 | 无 | 2026-07-21 |
| [`edgeone`](./skills/edgeone/) | [edgeone](./skills/edgeone/SKILL.md) | 通过 mcporter 把单个 HTML 文档部署到腾讯 EdgeOne Pages，无需登录。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`english-exam-writing-reviewer`](./skills/english-exam-writing-reviewer/) | [english-exam-writing-reviewer](./skills/english-exam-writing-reviewer/SKILL.md) | 可追溯的中国主流英语考试作文批改工具，覆盖 CET-4/CET-6/考研英一/英二（6 种级别），严格对齐官方档次制评分，每分可溯源至描述符原文与作文证据句，输出全中文教练反馈 + 升档建议 + HTML 批改报告。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`excalidraw-diagram`](./skills/excalidraw-diagram/) | [excalidraw-diagram](./skills/excalidraw-diagram/SKILL.md) | 创建 Excalidraw 手绘风图表：流程、架构、协议、概念与系统图。 | 无 | 2026-07-21 |
| [`fadada-document-sign`](./skills/fadada-document-sign/) | [fadada-document-sign](./skills/fadada-document-sign/SKILL.md) | 法大大电子签约工具。 | 需要环境变量：`FADADA_APP_SECRET` | 2026-07-21 |
| [`fbs-bookwriter`](./skills/fbs-bookwriter/) | [fbs-bookwriter](./skills/fbs-bookwriter/SKILL.md) | 福帮手出品 \| 高质量长文档手稿工具链：书籍、手册、白皮书、行业指南、长篇报道、深度专题；支持联网查证（宿主允许时启用，离线自动降级）、S/P/C/B 分层审校、中文排版与 M… | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`finance-ops`](./skills/finance-ops/) | [finance-ops](./skills/finance-ops/SKILL.md) | AI 财务分析套件：从 QuickBooks 数据生成 CFO 高管简报。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`flyai`](./skills/flyai/) | [flyai](./skills/flyai/SKILL.md) | 自然语言搜索机票、酒店、景点、演出与旅行优惠（飞猪 MCP）。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要环境变量：`FLYAI_API_KEY` | 2026-07-21 |
| [`frontend-dev`](./skills/frontend-dev/) | [frontend-dev](./skills/frontend-dev/SKILL.md) | 前端开发与 AI 媒体生成 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`MINIMAX_API_KEY` | 2026-07-21 |
| [`gif-sticker-maker`](./skills/gif-sticker-maker/) | [gif-sticker-maker](./skills/gif-sticker-maker/SKILL.md) | 照片转动态 GIF 贴纸 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`MINIMAX_API_KEY` | 2026-07-21 |
| [`github-ai-trends`](./skills/github-ai-trends/) | [github-ai-trends](./skills/github-ai-trends/SKILL.md) | 生成 GitHub AI 趋势项目榜单报告。 | 需要 GitHub Token 或 `gh auth login`；需要环境变量：`GITHUB_TOKEN` | 2026-07-21 |
| [`github-trending-cn`](./skills/github-trending-cn/) | [github-trending-cn](./skills/github-trending-cn/SKILL.md) | GitHub Trending 监控：按日/周/月抓取热门仓库。 | 需要 GitHub Token 或 `gh auth login`；需要环境变量：`GITHUB_TOKEN` | 2026-07-21 |
| [`globepilot-ai-agent-2`](./skills/globepilot-ai-agent-2/) | [globepilot-ai-agent-2](./skills/globepilot-ai-agent-2/SKILL.md) | 全球旅行助手：签证信息、汇率换算、机场攻略等。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-10-04 |
| [`growth-engine`](./skills/growth-engine/) | [growth-engine](./skills/growth-engine/SKILL.md) | 自主营销实验引擎：自动运行、度量与优化增长实验。 | 需要环境变量：`EMAIL_AUTH_TOKEN`、`PIPELINE_AUTH_TOKEN`、`RECRUITING_AUTH_TOKEN` | 2026-07-21 |
| [`handoff`](./skills/handoff/) | [handoff](./skills/handoff/SKILL.md) | 把当前对话压缩成交接文档，方便另一个 Agent 接手继续。 | 无 | 2026-07-21 |
| [`himalaya`](./skills/himalaya/) | [himalaya](./skills/himalaya/SKILL.md) | 通过 himalaya CLI 以 IMAP/SMTP 管理邮件（列表、阅读、回复、转发）。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`html-deploy`](./skills/html-deploy/) | [html-deploy](./skills/html-deploy/SKILL.md) | 把单个自包含 HTML 页面发布到 htmlcode.fun 并返回可访问链接。 | 无 | 2026-07-21 |
| [`humanizer`](./skills/humanizer/) | [humanizer](./skills/humanizer/SKILL.md) | 去除文本中的 AI 写作痕迹，让文字更像人写的。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`impeccable`](./skills/impeccable/) | [impeccable](./skills/impeccable/SKILL.md) | 高品质 UI/UX 设计工具集：帮助生成独特、生产级的前端界面，涵盖视觉风格、布局排版、动效交互、质量保障、设计系统等全方位设计能力，避免泛 AI 审美 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`infographic-maker`](./skills/infographic-maker/) | [infographic-maker](./skills/infographic-maker/SKILL.md) | 把文章、概念、报告或数据生成手绘卡通风格的信息图。 | 无 | 2026-07-21 |
| [`jinshuju`](./skills/jinshuju/) | [jinshuju](./skills/jinshuju/SKILL.md) | 金数据表单：创建/编辑表单、收集与查询数据、批量更新。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`YOUR_API_KEY`、`YOUR_API_SECRET` | 2026-07-21 |
| [`kdocs`](./skills/kdocs/) | [kdocs](./skills/kdocs/SKILL.md) | 金山文档（WPS 云文档 / 365.kdocs.cn / www.kdocs.cn）— 在线云文档平台，【金山文档官方 Skill】。 当用户提到金山文档、Kdocs、云文档、… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`KINGSOFT_DOCS_TOKEN` | 2026-07-21 |
| [`khazix-writer`](./skills/khazix-writer/) | [khazix-writer](./skills/khazix-writer/SKILL.md) | 数字生命卡兹克（Khazix）的公众号长文写作skill。当用户需要撰写公众号文章、写稿子、续写文章、根据素材产出长文时使用。触发词包括但不限于：写文章、写稿子、帮我写、续写、扩写、公众号文章、长文、出稿、按我的风格写… | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`lark-unified`](./skills/lark-unified/) | [lark-unified](./skills/lark-unified/SKILL.md) | 统一的飞书/Lark CLI 套件：消息、文档、协作、日程等。 | 需要飞书应用凭证或用户登录授权；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`lexiang-knowledge-base`](./skills/lexiang-knowledge-base/) | [lexiang-knowledge-base](./skills/lexiang-knowledge-base/SKILL.md) | 用于访问乐享知识库平台的专用 skill。当用户明确提到「乐享」「lexiang」「知识库」「知识」「文档」等关键词，或用户提供的链接 host 为 lexiangla.com，… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`LEXIANG_TOKEN` | 2026-07-21 |
| [`libtv-skill`](./skills/libtv-skill/) | [libtv-skill](./skills/libtv-skill/SKILL.md) | agent-im 会话技能 - 通过 liblib.tv 的 AI 能力生成和编辑图片/视频。覆盖场景包括：生成（文生图、文生视频、图生视频、做动画、画一个xxx、来段xxx）、… | 需要环境变量：`LIBTV_ACCESS_KEY` | 2026-07-21 |
| [`lingxi-financialsearch-skill`](./skills/lingxi-financialsearch-skill/) | [lingxi-financialsearch-skill](./skills/lingxi-financialsearch-skill/SKILL.md) | 国泰海通金融数据查询Skill，通过自然语言查询A股实时行情、公司基本信息、F10财务数据、个股技术指标等金融数据。遵循沪深交易所行情转发规则，仅提供授权范围内基础行情数据。触发… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`llm-wiki`](./skills/llm-wiki/) | [llm-wiki](./skills/llm-wiki/SKILL.md) | 用 LLM 构建和维护个人知识库 wiki（非 RAG 式检索，而是结构化 wiki）。 | 无 | 2026-07-21 |
| [`macro-monitor`](./skills/macro-monitor/) | [macro-monitor](./skills/macro-monitor/SKILL.md) | 每日宏观数据监控和推送。自动浏览免费数据源（Trading Economics、FRED、国家统计局、央行官网、财联社等），整理整合过去24小时发布的宏观数据和政策信息，并推送给… | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`market-researcher`](./skills/market-researcher/) | [market-researcher](./skills/market-researcher/SKILL.md) | 市场研究专家：市场分析、消费者行为与竞品研究。 | 无 | 2026-07-21 |
| [`mcdonald-assistant`](./skills/mcdonald-assistant/) | [mcdonald-assistant](./skills/mcdonald-assistant/SKILL.md) | 麦当劳中国点餐与优惠助手。用户提到麦当劳、麦麦、麦当劳外卖、点餐、查菜单、领麦当劳优惠券、查麦当劳积分/订单/活动时使用。依赖 WorkBuddy 已配置并信任的麦当劳 MCP … | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`MCP_TOKEN` | 2026-07-21 |
| [`mcp-builder`](./skills/mcp-builder/) | [mcp-builder](./skills/mcp-builder/SKILL.md) | 创建高质量 MCP 服务器的指南。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`mcporter`](./skills/mcporter/) | [mcporter](./skills/mcporter/SKILL.md) | 用 mcporter CLI 列出、配置、认证并直接调用 MCP 服务器/工具。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`meituan-coupon-workbuddy`](./skills/meituan-coupon-workbuddy/) | [meituan-coupon-workbuddy](./skills/meituan-coupon-workbuddy/SKILL.md) | 【美团官方】美团生活助手，支持外卖、餐饮团购、酒店住宿、门票度假、休闲娱乐、闪购、医药等多品类优惠券/红包/神券的一键领取与历史领取记录查询。核心能力：1）一键领券，覆盖上述多品… | 需要登录 / OAuth / 扫码授权；需要环境变量：`AUTH_SCRIPT`、`USER_TOKEN` | 2026-07-21 |
| [`meituan-huisheng-coupon`](./skills/meituan-huisheng-coupon/) | [meituan-huisheng-coupon](./skills/meituan-huisheng-coupon/SKILL.md) | 帮用户自动领取美团优惠券并查询当日优惠活动，覆盖外卖、到店餐饮、休闲娱乐、酒旅等全品类 | 需要登录 / OAuth / 扫码授权；需要环境变量：`AUTH_SCRIPT`、`USER_TOKEN` | 2026-07-21 |
| [`migraq`](./skills/migraq/) | [migraq](./skills/migraq/SKILL.md) | 腾讯云迁移平台（CMG/MSP）全流程能力。触发词：资源扫描、扫描阿里云/AWS/华为云/GCP资源、生成云资源清单、选型推荐、对标腾讯云、推荐规格、帮我推荐、给我推荐、ECS对… | 需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`minimax-xlsx`](./skills/minimax-xlsx/) | [minimax-xlsx](./skills/minimax-xlsx/SKILL.md) | 打开、创建、读取、分析、编辑、校验 Excel/电子表格文件（MiniMax）。 | 无 | 2026-07-21 |
| [`multi-search-engine`](./skills/multi-search-engine/) | [multi-search-engine](./skills/multi-search-engine/SKILL.md) | 多搜索引擎整合：16 个引擎（国内 7 个 + 国际 9 个），支持高级搜索。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`my-novel-writer`](./skills/my-novel-writer/) | [my-novel-writer](./skills/my-novel-writer/SKILL.md) | 辅助创作长篇小说，支持人物设定、世界观管理和分章生成 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`NOVEL_API_KEY` | 2026-07-21 |
| [`nano-banana-pro`](./skills/nano-banana-pro/) | [nano-banana-pro](./skills/nano-banana-pro/SKILL.md) | 用 Nano Banana Pro（Gemini 3 Pro Image）生成/编辑图片。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`GEMINI_API_KEY` | 2026-07-21 |
| [`neodata-financial-search`](./skills/neodata-financial-search/) | [neodata-financial-search](./skills/neodata-financial-search/SKILL.md) | 自然语言查询股票、基金、宏观、外汇、大宗商品等金融数据 | 无 | 2026-07-21 |
| [`news-summary`](./skills/news-summary/) | [news-summary](./skills/news-summary/SKILL.md) | 新闻更新与每日简报生成。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`OPENAI_API_KEY` | 2026-07-21 |
| [`note-organizer`](./skills/note-organizer/) | [note-organizer](./skills/note-organizer/SKILL.md) | Joplin 笔记管理：个人知识库与生产力工具。 | 无 | 2026-07-21 |
| [`novel-writer`](./skills/novel-writer/) | [novel-writer](./skills/novel-writer/SKILL.md) | 章节正文生成器 - 根据章节大纲、Voice Profile 和角色档案构建 LLM 提示词，用于生成章节正文。当需要根据大纲创作具体章节时使用。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`nuwa-skill`](./skills/nuwa-skill/) | [nuwa-skill](./skills/nuwa-skill/SKILL.md) | 女娲造人：输入人名/主题/甚至只是模糊需求，自动深度调研→思维框架提炼→生成可运行的人物Skill。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`obsidian`](./skills/obsidian/) | [obsidian](./skills/obsidian/SKILL.md) | 操作 Obsidian 笔记库（纯 Markdown），通过 obsidian-cli 自动化。 | 无 | 2026-07-21 |
| [`open-lesson`](./skills/open-lesson/) | [open-lesson](./skills/open-lesson/SKILL.md) | 对接 openLesson 辅导 API 的苏格拉底式学习：生成学习计划等。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`OPENLESSON_API_KEY`、`YOUR_API_KEY` | 2026-07-21 |
| [`openai-image-gen`](./skills/openai-image-gen/) | [openai-image-gen](./skills/openai-image-gen/SKILL.md) | 通过 OpenAI Images API 批量生图，带随机提示词采样器与图库页。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`OPENAI_API_KEY` | 2026-07-21 |
| [`openai-whisper`](./skills/openai-whisper/) | [openai-whisper](./skills/openai-whisper/SKILL.md) | 本地 Whisper CLI 语音转文字（无需 API Key）。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`openai-whisper-api`](./skills/openai-whisper-api/) | [openai-whisper-api](./skills/openai-whisper-api/SKILL.md) | 通过 OpenAI Whisper API 转录音频。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`OPENAI_API_KEY` | 2026-07-21 |
| [`openclaw-assets-to-workbuddy`](./skills/openclaw-assets-to-workbuddy/) | [openclaw-assets-to-workbuddy](./skills/openclaw-assets-to-workbuddy/SKILL.md) | 将 OpenClaw 用户的个人资产迁移到 WorkBuddy 对应位置，重点覆盖 SOUL.md、IDENTITY.md、USER.md、memory、skills、MCP 配… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`oracle`](./skills/oracle/) | [oracle](./skills/oracle/SKILL.md) | 用 @steipete/oracle CLI 打包提示词与相关文件，获取第二意见。 | 无 | 2026-07-21 |
| [`outbound-engine`](./skills/outbound-engine/) | [outbound-engine](./skills/outbound-engine/SKILL.md) | 为 Instantly 设计、分析和优化冷邮件外发campaign。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`paper-quick-reader`](./skills/paper-quick-reader/) | [paper-quick-reader](./skills/paper-quick-reader/SKILL.md) | 面向学生和研究者的 AI 论文速读工具，支持裸读/引导/精读三档深度，页码级可追溯防幻觉，可多篇对比，输出结构化笔记与核心观点摘要。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`perplexity`](./skills/perplexity/) | [perplexity](./skills/perplexity/SKILL.md) | 通过 Perplexity API 进行 AI 答案式网络搜索。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`PERPLEXITY_API_KEY` | 2026-07-21 |
| [`plan-tracker`](./skills/plan-tracker/) | [plan-tracker](./skills/plan-tracker/SKILL.md) | 当用户需要目标拆解、每日打卡、连续签到、学习热力图、进度预警时使用。支持 SMART 澄清 + OKR 月周拆解 + ABC 三档每日任务（A 完美 / B 基础 / C ≤15… | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`playwright-browser-automation`](./skills/playwright-browser-automation/) | [playwright-browser-automation](./skills/playwright-browser-automation/SKILL.md) | 直接使用 Playwright API 做浏览器自动化（无 MCP 复杂度）：导航网站等。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`playwright-scraper-skill`](./skills/playwright-scraper-skill/) | [playwright-scraper-skill](./skills/playwright-scraper-skill/SKILL.md) | 基于 Playwright 的网页抓取技能，带反爬保护。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`podcast-ops`](./skills/podcast-ops/) | [podcast-ops](./skills/podcast-ops/SKILL.md) | 播客内容拆解流水线，一期节目生成 20+ 跨平台内容 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`OPENAI_LLM_KEY` | 2026-07-21 |
| [`porteden-email`](./skills/porteden-email/) | [porteden-email](./skills/porteden-email/SKILL.md) | 安全的多账号邮件管理（Gmail/Outlook/Exchange）：阅读、搜索、发送。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`PE_API_KEY` | 2026-07-21 |
| [`price-history`](./skills/price-history/) | [price-history](./skills/price-history/SKILL.md) | 封装慢慢买（manmanbuy.com）官方 MCP，按关键词搜索全网商品的参考好价、实时价格与隐藏优惠券，并基于返回数据判断当前价是否为真实低价、识别"先涨后降"的虚假促销。当… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`product-showcase-site`](./skills/product-showcase-site/) | [product-showcase-site](./skills/product-showcase-site/SKILL.md) | 为已有 Web 应用生成完整的、可部署的产品展示网站。 | 可能需要启用对应 MCP / 连接器；需要环境变量：`YOUR_SITE_KEY` | 2026-07-21 |
| [`promo-creator-skills`](./skills/promo-creator-skills/) | [promo-creator-skills](./skills/promo-creator-skills/SKILL.md) | 产品宣传片制作总控 skill pack。用于从产品说明、官网、应用截图或 GitHub 仓库制作 60-90 秒宣传视频，按阶段完成 brief、storyboard、素材、H… | 无 | 2026-07-21 |
| [`prompt-engineering-expert`](./skills/prompt-engineering-expert/) | [prompt-engineering-expert](./skills/prompt-engineering-expert/SKILL.md) | 提示词工程高级专家：自定义指令设计与提示词优化。 | 无 | 2026-07-21 |
| [`qmd`](./skills/qmd/) | [qmd](./skills/qmd/SKILL.md) | 本地 Markdown 笔记与文档的混合检索（全文+向量）。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`qqmusic`](./skills/qqmusic/) | [qqmusic](./skills/qqmusic/SKILL.md) | QQ 音乐：搜歌曲/专辑/歌单/MV/艺人，每日推荐等。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`QQMUSIC_API_KEY` | 2026-07-21 |
| [`remotion-video-toolkit`](./skills/remotion-video-toolkit/) | [remotion-video-toolkit](./skills/remotion-video-toolkit/SKILL.md) | Remotion + React 程序化视频创作完整工具包，含动画等。 | 无 | 2026-07-21 |
| [`responsiveness-check`](./skills/responsiveness-check/) | [responsiveness-check](./skills/responsiveness-check/SKILL.md) | 用浏览器自动化测试网站在各视口宽度下的响应式表现。 | 需要 GitHub Token 或 `gh auth login`；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`resume-assistant`](./skills/resume-assistant/) | [resume-assistant](./skills/resume-assistant/SKILL.md) | 面向中国求职者的可追溯 JD 定制简历助手，支持从 master 简历派生多版本，三维度防幻觉（不编造数字/合法改写/防 AI 味），输出中英双版简历 + 战略附录 + ATS 友好 PDF。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`revenue-intelligence`](./skills/revenue-intelligence/) | [revenue-intelligence](./skills/revenue-intelligence/SKILL.md) | 收入归因分析、销售通话洞察与客户报告自动生成。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`AHREFS_TOKEN`、`GONG_API_KEY`、`HUBSPOT_API_KEY` | 2026-07-21 |
| [`sag`](./skills/sag/) | [sag](./skills/sag/SKILL.md) | ElevenLabs 文本转语音，mac 风格 say 命令体验。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`ELEVENLABS_API_KEY`、`SAG_API_KEY` | 2026-07-21 |
| [`sales-pipeline`](./skills/sales-pipeline/) | [sales-pipeline](./skills/sales-pipeline/SKILL.md) | 销售管道自动化：匿名访客转化、沉睡交易激活与 ICP 学习。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`BRAVE_API_KEY`、`HUBSPOT_API_KEY`、`INSTANTLY_API_KEY` | 2026-07-21 |
| [`sales-playbook`](./skills/sales-playbook/) | [sales-playbook](./skills/sales-playbook/SKILL.md) | 基于价值的定价与销售剧本：通话分析与报价打包。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`AHREFS_API_KEY`、`ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`SEMRUSH_API_KEY` | 2026-07-21 |
| [`seo-ops`](./skills/seo-ops/) | [seo-ops](./skills/seo-ops/SKILL.md) | 用途：seo-ops | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`AHREFS_TOKEN`、`BRAVE_API_KEY`、`GOOGLE_CLIENT_SECRET` | 2026-07-21 |
| [`shippage`](./skills/shippage/) | [shippage](./skills/shippage/SKILL.md) | 用 ShipPage 把 HTML 或 Markdown 即时发布到公开 URL。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器；需要环境变量：`API_KEY` | 2026-07-21 |
| [`shopify-admin-api`](./skills/shopify-admin-api/) | [shopify-admin-api](./skills/shopify-admin-api/SKILL.md) | Shopify Admin REST API 完整读写：订单、商品、客户管理。 | 需要环境变量：`SHOPIFY_ACCESS_TOKEN` | 2026-07-21 |
| [`sino-drug-instructions-search`](./skills/sino-drug-instructions-search/) | [sino-drug-instructions-search](./skills/sino-drug-instructions-search/SKILL.md) | 在用户询问药品说明书、用药信息、适应症、禁忌、用法用量、不良反应、成分、规格、厂家，或根据症状/疾病查找药品时使用此技能。⚠️ 调用前须已通过 use_skill 加载本技能（s… | 可能需要启用对应 MCP / 连接器；需要环境变量：`SKILLS_BIZ_TOKEN` | 2026-07-21 |
| [`skill-creator`](./skills/skill-creator/) | [skill-creator](./skills/skill-creator/SKILL.md) | 创建高质量技能的指南（skill-creator）。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`skill-scanner`](./skills/skill-scanner/) | [skill-scanner](./skills/skill-scanner/SKILL.md) | 安装或使用任何 Agent 技能前扫描其安全风险（腾讯出品）。 | 无 | 2026-07-21 |
| [`skill-vetter`](./skills/skill-vetter/) | [skill-vetter](./skills/skill-vetter/SKILL.md) | 安全优先的技能审查：安装社区技能前先做安全评估。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`skills-security-check`](./skills/skills-security-check/) | [skills-security-check](./skills/skills-security-check/SKILL.md) | 腾讯云鼎实验室出品，Skill安全审查工具。对用户指定的skill.md文件及其配套的文档、程序、脚本等进行全面安全审计，确保引用安全 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`OPENAI_API_KEY` | 2026-07-21 |
| [`smart-page`](./skills/smart-page/) | [smart-page](./skills/smart-page/SKILL.md) | 腾讯文档智能页面（Smart Page）是可交互在线汇报网页生成工具，适用于汇报、述职、周报、复盘、数据看板、课件、培训、调研报告、会议纪要和本地 HTML 上云。区别于 PPT… | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`smooth-browser`](./skills/smooth-browser/) | [smooth-browser](./skills/smooth-browser/SKILL.md) | AI Agent 首选浏览器：在 Web 上执行任意任务。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`stagehand-browser-cli`](./skills/stagehand-browser-cli/) | [stagehand-browser-cli](./skills/stagehand-browser-cli/SKILL.md) | 用自然语言 CLI 命令自动化浏览器交互（Stagehand）。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`BROWSERBASE_API_KEY` | 2026-07-21 |
| [`static-app`](./skills/static-app/) | [static-app](./skills/static-app/SKILL.md) | 把静态网站和构建后的前端应用部署到 Static.app 托管。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`STATIC_APP_API_KEY` | 2026-07-21 |
| [`summarize`](./skills/summarize/) | [summarize](./skills/summarize/SKILL.md) | 用 summarize CLI 总结 URL 或文件（网页、PDF、图片、音频、YouTube）。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`ANTHROPIC_API_KEY`、`APIFY_API_TOKEN`、`FIRECRAWL_API_KEY`、`GEMINI_API_KEY`、`GOOGLE_API_KEY`、`GOOGLE_GENERATIVE_AI_API_KEY` | 2026-07-21 |
| [`task-alignment`](./skills/task-alignment/) | [task-alignment](./skills/task-alignment/SKILL.md) | 从用户粗略想法出发的对齐对话，共同决定任务方向。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`task-implement`](./skills/task-implement/) | [task-implement](./skills/task-implement/SKILL.md) | 由 .task/<MMDD_slug>/ 目录下文档驱动的自主任务执行。 | 无 | 2026-07-21 |
| [`tavily`](./skills/tavily/) | [tavily](./skills/tavily/SKILL.md) | 用 Tavily Search API 做面向 AI 优化的网络搜索。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`TAVILY_API_KEY` | 2026-07-21 |
| [`team-ops`](./skills/team-ops/) | [team-ops](./skills/team-ops/SKILL.md) | 用 Elon Algorithm 审计团队绩效（识别 A/B/C 类员工）并提取改进点。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`ANTHROPIC_API_KEY`、`HUBSPOT_API_KEY`、`OPENAI_API_KEY` | 2026-07-21 |
| [`tencent-campus-recruit`](./skills/tencent-campus-recruit/) | [tencent-campus-recruit](./skills/tencent-campus-recruit/SKILL.md) | 当用户询问腾讯校园招聘相关问题时使用，包括：校招/实习投递流程与时间节点、岗位搜索与推荐、 招聘公告与宣讲会动态、简历诊断与优化、面试准备与模拟陪练、校招防诈骗识别。 通过 jo… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`tencent-docs`](./skills/tencent-docs/) | [tencent-docs](./skills/tencent-docs/SKILL.md) | 腾讯文档（docs.qq.com）-在线云文档平台，是创建、编辑、管理文档的首选 skill。涉及"新建/创建/编辑/读取/查看/搜索文档"、"保存文件"、"云文档"、"腾讯文档… | 可能需要启用对应 MCP / 连接器；需要环境变量：`TENCENT_DOCS_TOKEN` | 2026-07-21 |
| [`tencent-meeting-skill`](./skills/tencent-meeting-skill/) | [tencent-meeting-skill](./skills/tencent-meeting-skill/SKILL.md) | 在用户提及腾讯会议、视频会议、线上会议相关内容与操作时使用此技能。触发关键词包括：预约会议、创建会议、修改会议、取消会议、查询会议、会议详情、会议号、meeting_id、mee… | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器；需要环境变量：`TENCENT_MEETING_TOKEN` | 2026-07-21 |
| [`tencent-music-campus-recruit`](./skills/tencent-music-campus-recruit/) | [tencent-music-campus-recruit](./skills/tencent-music-campus-recruit/SKILL.md) | 当用户询问腾讯校园招聘相关问题时使用，包括：校招/实习投递流程与时间节点、岗位搜索与推荐、 招聘公告与宣讲会动态、组织架构/BG/部门介绍、简历诊断与优化、面试准备与模拟陪练、校… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`tencent-survey`](./skills/tencent-survey/) | [tencent-survey](./skills/tencent-survey/SKILL.md) | 腾讯问卷（wj.qq.com）- 在线问卷调查平台。涉及「问卷」「调查」「表单」「投票」「考试」「测评」「wj.qq.com」等操作时优先使用。支持能力：(1) 获取问卷详情（标… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`TENCENT_SURVEY_TOKEN` | 2026-07-21 |
| [`tencent-yunzhi`](./skills/tencent-yunzhi/) | [tencent-yunzhi](./skills/tencent-yunzhi/SKILL.md) | 腾讯乐享（lexiangla.com / csig.lexiangla.com）知识库专用操作。仅在用户消息包含 lexiangla.com 链接、或明确提及『乐享/云知/Lex… | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`LEXIANG_TOKEN` | 2026-07-21 |
| [`tencentcloud-ocr`](./skills/tencentcloud-ocr/) | [tencentcloud-ocr](./skills/tencentcloud-ocr/SKILL.md) | 腾讯云通用文字识别（高精度版）(GeneralAccurateOCR) 技能包。当用户发送/粘贴图片、提供图片URL、或要求识别图片中的文字时，应自动调用此技能。支持图像整体文字… | 需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`tencentcloud-ocr-extractdocagent`](./skills/tencentcloud-ocr-extractdocagent/) | [tencentcloud-ocr-extractdocagent](./skills/tencentcloud-ocr-extractdocagent/SKILL.md) | 腾讯云实时文档抽取Agent(ExtractDocAgent)接口调用技能。当用户需要从图片或PDF中按自定义字段名称进行结构化信息抽取时，应使用此技能。支持自定义字段名称、字段… | 需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`tencentcloud-ocr-general`](./skills/tencentcloud-ocr-general/) | [tencentcloud-ocr-general](./skills/tencentcloud-ocr-general/SKILL.md) | 腾讯云广告文字识别(AdvertiseOCR)接口调用技能。当用户需要从图片中识别文字内容时,应使用此技能。支持中英文、横排、竖排及倾斜场景的图片文字识别,支持90度、180度、… | 需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`tencentcloud-ocr-questionmarkagent`](./skills/tencentcloud-ocr-questionmarkagent/) | [tencentcloud-ocr-questionmarkagent](./skills/tencentcloud-ocr-questionmarkagent/SKILL.md) | 腾讯云试题批改Agent(SubmitQuestionMarkAgentJob/DescribeQuestionMarkAgentJob)接口调用技能。当用户需要对试卷图片或试题… | 需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`tencentcloud-ocr-recognizetableaccurate`](./skills/tencentcloud-ocr-recognizetableaccurate/) | [tencentcloud-ocr-recognizetableaccurate](./skills/tencentcloud-ocr-recognizetableaccurate/SKILL.md) | 腾讯云表格识别v3(RecognizeTableAccurateOCR)接口调用技能。当用户需要从表格图片或PDF中识别常规表格、无线表格、多表格的内容,提取每个单元格的文字信息… | 需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`tmux`](./skills/tmux/) | [tmux](./skills/tmux/SKILL.md) | 通过发送按键和抓取屏幕远程控制 tmux 会话，操作交互式 CLI。 | 无 | 2026-07-21 |
| [`travel-planning`](./skills/travel-planning/) | [travel-planning](./skills/travel-planning/SKILL.md) | 旅行规划：行程、多城市路线、预算优化、家庭后勤。 | 无 | 2026-07-21 |
| [`university-applications`](./skills/university-applications/) | [university-applications](./skills/university-applications/SKILL.md) | 全体系命理大师 — 八字四柱、紫微斗数、奇门遁甲、六爻、梅花易数、塔罗、星盘、 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`web-access`](./skills/web-access/) | [web-access](./skills/web-access/SKILL.md) | 所有联网操作必须通过此 skill 处理，包括：搜索、网页抓取、登录后操作、网络交互等。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`web-performance-audit`](./skills/web-performance-audit/) | [web-performance-audit](./skills/web-performance-audit/SKILL.md) | 分析已上线网站的性能质量：Core Web Vitals 等指标。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`web-scraper`](./skills/web-scraper/) | [web-scraper](./skills/web-scraper/SKILL.md) | 网页抓取与内容理解 Agent：多策略级联提取。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`OPENROUTER_API_KEY` | 2026-07-21 |
| [`web-search-exa`](./skills/web-search-exa/) | [web-search-exa](./skills/web-search-exa/SKILL.md) | Exa 神经搜索：内容提取、公司与人物调研、代码搜索。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要环境变量：`YOUR_EXA_KEY`、`YOUR_KEY` | 2026-07-21 |
| [`wechat-viral-topic`](./skills/wechat-viral-topic/) | [wechat-viral-topic](./skills/wechat-viral-topic/SKILL.md) | 公众号编辑、短视频博主、漫画作者、H5 策划必备的热点爆款策划助手。当用户需要选题灵感、起爆款标题、把热点做成文章/短视频/漫画/H5 等全形态创作方案，或评估某个素材能不能爆时… | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`wecom-weisheng-scrm`](./skills/wecom-weisheng-scrm/) | [wecom-weisheng-scrm](./skills/wecom-weisheng-scrm/SKILL.md) | 当用户需要查询或管理微盛企微管家（企业微信） SCRM 中的客户信息、客户标签、客户群、营销素材、活码、群发、跟进记录、聊天记录、联系人、商机、汇报、抽奖、客户日程等相关业务能力… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`weiyun`](./skills/weiyun/) | [weiyun](./skills/weiyun/SKILL.md) | 微云网盘 MCP 接口完整技能。包含 weiyun.list、weiyun.list_by_category、weiyun.download、weiyun.delete、weiy… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`WEIYUN_MCP_TOKEN` | 2026-07-21 |
| [`weread-skills`](./skills/weread-skills/) | [weread-skills](./skills/weread-skills/SKILL.md) | 微信读书助手 — 搜索书籍、管理书架、查看笔记划线、浏览书评、阅读统计、发现推荐好书 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要环境变量：`WEREAD_API_KEY` | 2026-07-21 |
| [`workbuddy-asset-migration`](./skills/workbuddy-asset-migration/) | [workbuddy-asset-migration](./skills/workbuddy-asset-migration/SKILL.md) | 在 WorkBuddy 国内版（~/.workbuddy/）和海外版（~/.workbuddy-ai/）之间，或跨机器之间，迁移用户个人资产（skills、memory、conv… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`workrally`](./skills/workrally/) | [workrally](./skills/workrally/SKILL.md) | WorkRally CLI (workrally) — 面向 AI Agent 的 AIGC 漫剧视频创作全流程工具集。 支持 AI 生图、AI 生视频、项目管理、资产库、媒资管… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`WORKRALLY_API_KEY`、`YOUR_API_KEY` | 2026-07-21 |
| [`x-longform-post`](./skills/x-longform-post/) | [x-longform-post](./skills/x-longform-post/SKILL.md) | 用创始人/CEO 口吻撰写 X（Twitter）长文和推文串。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`xiaobai-coach`](./skills/xiaobai-coach/) | [xiaobai-coach](./skills/xiaobai-coach/SKILL.md) | 给小白讲清理财、基金、股票知识，并配套实操工具与清单的财商陪跑技能。当用户问个人理财、攒钱、基金/ETF/股票/债券入门、定投、资产配置、复利计算、估值、止盈止损、识别投资骗局等… | 无 | 2026-07-21 |
| [`yingmi-skill`](./skills/yingmi-skill/) | [yingmi-skill](./skills/yingmi-skill/SKILL.md) | 当用户需要查询基金、策略、公告、财经资讯，做资产配置、组合诊断、风险回测、现金流分析，或生成图表、PDF 时，优先使用本 Skill 获取真实数据与可执行能力。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`yourself-skill`](./skills/yourself-skill/) | [yourself-skill](./skills/yourself-skill/SKILL.md) | 把自己蒸馏成 AI 技能：解构聊天记录、日记、社交媒体。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`zoom-out`](./skills/zoom-out/) | [zoom-out](./skills/zoom-out/SKILL.md) | 让 Agent 跳脱出细节，提供更宏观的上下文与更高层视角。 | 无 | 2026-07-21 |

### 云 / 存储 / 部署（4）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`cnb-skill`](./skills/cnb-skill/) | [cnb-skill](./skills/cnb-skill/SKILL.md) | 通过 OpenAPI 操作 CNB（Cloud Native Build）平台：管理组织、仓库等。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`netlify-deploy`](./skills/netlify-deploy/) | [netlify-deploy](./skills/netlify-deploy/SKILL.md) | 用 npx netlify 部署和管理 Netlify 站点：首次部署、预览部署等。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`novel-writing`](./skills/novel-writing/) | [novel-writing](./skills/novel-writing/SKILL.md) | AI长篇网文创作技能包。用于解决长篇网络小说创作中的核心痛点：上下文丢失、文风不一致、设定冲突、节奏失控、多线混乱、质量不稳、读者反馈无法内化。触发场景包括：开始新书、规划大纲、… | 无 | 2026-07-21 |
| [`vercel-deploy`](./skills/vercel-deploy/) | [vercel-deploy](./skills/vercel-deploy/SKILL.md) | 从终端部署和管理 Vercel 项目：正式部署、预览部署。 | 需要环境变量：`VERCEL_TOKEN` | 2026-07-21 |

### 内容 / 营销 / 媒体（5）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`ecommerce-copywriter`](./skills/ecommerce-copywriter/) | [ecommerce-copywriter](./skills/ecommerce-copywriter/SKILL.md) | 电商爆款文案生成技能。为淘宝/拼多多/抖音/京东卖家生成高转化率的商品标题、详情页文案、卖点提炼和促销文案。使用场景：(1) 商品标题优化，(2) 详情页文案生成，(3) 卖点提… | 无 | 2026-07-21 |
| [`github-pages-auto-deploy`](./skills/github-pages-auto-deploy/) | [github-pages-auto-deploy](./skills/github-pages-auto-deploy/SKILL.md) | 用 GitHub Actions 配置自动部署网站到 GitHub Pages，支持自定义域名。 | 无 | 2026-07-21 |
| [`setup-pre-commit`](./skills/setup-pre-commit/) | [setup-pre-commit](./skills/setup-pre-commit/SKILL.md) | 配置 Husky pre-commit 钩子：lint-staged（Prettier）、类型检查与测试。 | 无 | 2026-07-21 |
| [`video-frames`](./skills/video-frames/) | [video-frames](./skills/video-frames/SKILL.md) | 用 ffmpeg 从视频中提取帧或短片段。 | 无 | 2026-07-21 |
| [`web-deploy-github`](./skills/web-deploy-github/) | [web-deploy-github](./skills/web-deploy-github/SKILL.md) | 创建单页静态网站并以自动化工作流部署到 GitHub Pages。 | 需要 GitHub Token 或 `gh auth login` | 2026-07-21 |

### 开发 / 工程（2）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`github`](./skills/github/) | [github](./skills/github/SKILL.md) | 用 gh CLI 操作 GitHub：issue、PR、workflow run 等。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`trello`](./skills/trello/) | [trello](./skills/trello/SKILL.md) | 通过 Trello REST API 管理看板、列表和卡片。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`TRELLO_API_KEY`、`TRELLO_TOKEN` | 2026-07-21 |

### 搜索 / 研究 / 知识（15）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`airbnb`](./skills/airbnb/) | [airbnb](./skills/airbnb/SKILL.md) | 搜索 Airbnb 房源（价格、评分、直达链接），无需 API Key。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-10-04 |
| [`aviationstack-flight-tracker`](./skills/aviationstack-flight-tracker/) | [aviationstack-flight-tracker](./skills/aviationstack-flight-tracker/SKILL.md) | 实时航班追踪：状态、登机口、延误与实时位置（aviationstack）。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`AVIATIONSTACK_API_KEY` | 2026-07-21 |
| [`browserwing`](./skills/browserwing/) | [browserwing](./skills/browserwing/SKILL.md) | 通过 HTTP API 控制浏览器自动化：页面导航、元素交互。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`citation-manager`](./skills/citation-manager/) | [citation-manager](./skills/citation-manager/SKILL.md) | 为论文和学位论文添加真实参考文献并规范引用格式。 | 无 | 2026-07-21 |
| [`cloudflare-worker-builder`](./skills/cloudflare-worker-builder/) | [cloudflare-worker-builder](./skills/cloudflare-worker-builder/SKILL.md) | 脚手架并部署 Cloudflare Workers：Hono 路由、Vite 插件、静态资源。 | 无 | 2026-07-21 |
| [`ecomseer`](./skills/ecomseer/) | [ecomseer](./skills/ecomseer/SKILL.md) | TikTok Shop 电商数据助手：搜商品、找爆款、分析达人。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`ECOMSEER_API_KEY` | 2026-07-21 |
| [`flight-tracker`](./skills/flight-tracker/) | [flight-tracker](./skills/flight-tracker/SKILL.md) | 航班追踪与时刻查询：按地区、呼号实时追踪。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`AVIATIONSTACK_API_KEY` | 2026-07-21 |
| [`football-bayes`](./skills/football-bayes/) | [football-bayes](./skills/football-bayes/SKILL.md) | 20年经验的足球竞彩策略官：贝叶斯统计 + 现代战术周期化，输出胜平负概率与风险提示 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`gsap-animation-assistant`](./skills/gsap-animation-assistant/) | [gsap-animation-assistant](./skills/gsap-animation-assistant/SKILL.md) | GSAP 前端动画助手：生成和审查时间线、ScrollTrigger 动画代码。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`healthcheck`](./skills/healthcheck/) | [healthcheck](./skills/healthcheck/SKILL.md) | 用 JSON 文件记录饮水和睡眠等健康数据。 | 无 | 2026-07-21 |
| [`novel`](./skills/novel/) | [novel](./skills/novel/SKILL.md) | 从终端快速管理小说数据：章节、角色、情节。 | 无 | 2026-07-21 |
| [`stealth-browser`](./skills/stealth-browser/) | [stealth-browser](./skills/stealth-browser/SKILL.md) | 终极隐身浏览器自动化：反检测、绕过 Cloudflare、验证码处理。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`YOUR_2CAPTCHA_KEY`、`YOUR_ANTICAPTCHA_KEY`、`YOUR_CAPSOLVER_KEY` | 2026-07-21 |
| [`study-planner`](./skills/study-planner/) | [study-planner](./skills/study-planner/SKILL.md) | 当用户需要制定学习计划、备考计划、拆解复习目标时使用。输入目标+截止日+每日时长，输出每天可执行的学习计划，支持雅思/考研/期末复习等场景。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`travel-cn`](./skills/travel-cn/) | [travel-cn](./skills/travel-cn/SKILL.md) | 旅行信息查询 - 去哪儿/携程/飞猪数据查询（Expedia 中国版） | 需要 12306 账号登录 | 2026-07-21 |
| [`vip-skill`](./skills/vip-skill/) | [vip-skill](./skills/vip-skill/SKILL.md) | 唯品会（vip.com）电商服务技能包（vipshop-skills），整合唯品会搜索、商品查询、活动查询、图片搜索等多项购物服务，是一套完整的唯品会购物 AI 助手解决方案。当… | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |

### 数据 / 金融 / 股票（6）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`fintech-engineer`](./skills/fintech-engineer/) | [fintech-engineer](./skills/fintech-engineer/SKILL.md) | 金融科技工程师专家：金融系统、PCI 等监管合规。 | 无 | 2026-07-21 |
| [`qcc-company`](./skills/qcc-company/) | [qcc-company](./skills/qcc-company/SKILL.md) | 通过企查查 Connector 查询中国境内企业的工商信息、股权结构、高管人员、财务数据、对外投资、历史变更、上市信息、分支机构、联系方式、开票信息及企业身份核验。当用户的请求涉… | 需要配置/启用 MCP 连接器 | 2026-07-21 |
| [`stock-analysis`](./skills/stock-analysis/) | [stock-analysis](./skills/stock-analysis/SKILL.md) | 用 Yahoo Finance 数据分析股票和加密货币，支持组合管理。 | 需要登录 / OAuth / 扫码授权；需要环境变量：`AUTH_TOKEN` | 2026-07-21 |
| [`us-stock-analysis`](./skills/us-stock-analysis/) | [us-stock-analysis](./skills/us-stock-analysis/SKILL.md) | 美股综合分析：基本面（财务指标、业务）等。 | 无 | 2026-07-21 |
| [`westock-data`](./skills/westock-data/) | [westockdata](./skills/westock-data/SKILL.md) | 查询A股、港股、美股个股/指数/ETF的详细数据，包括：K线/分时、财务报表（三大报表多期查询，支持跨市场批量对比）、资金流向、技术指标、筹码分析、股东结构、分红除权、业绩预告、… | 无 | 2026-07-21 |
| [`westockdata`](./skills/westockdata/) | [westockdata](./skills/westockdata/SKILL.md) | 查询A股、港股、美股个股/指数/ETF的详细数据，包括：K线/分时、财务报表（三大报表多期查询，支持跨市场批量对比）、资金流向、技术指标、筹码分析、股东结构、分红除权、业绩预告、… | 无 | 2026-07-21 |

### 文档 / 办公 / 协作（44）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`12306-train-assistant`](./skills/12306-train-assistant/) | [12306-train-assistant](./skills/12306-train-assistant/SKILL.md) | 12306 查询与订票辅助技能，支持余票查询、经停站查询、中转换乘、候补查询与提交/取消、登录状态检查、密码登录与二维码登录、下单与支付链接获取；当用户提到火车票、高铁票、经停站… | 需要微信/企微相关凭证或扫码登录；需要 12306 账号登录；需要登录 / OAuth / 扫码授权；需要环境变量：`KYFW_PASSWORD` | 2026-07-21 |
| [`a-stock-data`](./skills/a-stock-data/) | [a-stock-data](./skills/a-stock-data/SKILL.md) | A股全栈数据工具包 — 覆盖行情(mootdx+腾讯+百度K线)、研报(东财+同花顺+iwencai)、信号(同花顺热点+北向+龙虎榜+解禁+行业)、资金面(融资融券+大宗交易+… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`IWENCAI_API_KEY`、`IWENCAI_KEY` | 2026-07-21 |
| [`academic-translation`](./skills/academic-translation/) | [academic-translation](./skills/academic-translation/SKILL.md) | 当用户需要学术论文中英互译、润色、Chinglish 修复时使用。三步法（直译→反思→雅化），公式/cite 零损伤，顶会术语库，双栏对照，不动原文件。 | 无 | 2026-07-21 |
| [`academic-tutor`](./skills/academic-tutor/) | [academic-tutor](./skills/academic-tutor/SKILL.md) | 当大学生问题目、需要苏格拉底式引导讲解、或论文写作指导时使用。不直接给答案，每轮三段式（引导问题→关键提示→下一步建议），数理化/编程/经管/文史哲全覆盖。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`admapix`](./skills/admapix/) | [admapix](./skills/admapix/SKILL.md) | 广告情报与应用分析助手：搜广告素材、分析应用、榜单、下载量、收入与市场洞察。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`ADMAPIX_API_KEY`、`ADMAPIX_DEEP_RESEARCH_TOKEN`、`YOUR_API_KEY` | 2026-07-21 |
| [`android-native-dev`](./skills/android-native-dev/) | [android-native-dev](./skills/android-native-dev/SKILL.md) | Android 原生开发与 UI 设计指南：Material Design 3 等。 | 无 | 2026-07-21 |
| [`caldav-calendar`](./skills/caldav-calendar/) | [caldav-calendar](./skills/caldav-calendar/SKILL.md) | 用 vdirsyncer/khal 同步和查询 CalDAV 日历（iCloud/Google/Fastmail 等）。 | 无 | 2026-07-21 |
| [`canvas-design`](./skills/canvas-design/) | [canvas-design](./skills/canvas-design/SKILL.md) | 按设计哲学在 .png/.pdf 文档中创作精美视觉艺术。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`caveman`](./skills/caveman/) | [caveman](./skills/caveman/SKILL.md) | 超压缩沟通模式：去除废话保留技术精度，节省约 75% token | 无 | 2026-07-21 |
| [`charity-finance-assistant`](./skills/charity-finance-assistant/) | [charity-finance-assistant](./skills/charity-finance-assistant/SKILL.md) | 非营利机构财务与收据管理助手：捐赠整理等。 | 无 | 2026-07-21 |
| [`charity-writing-assistant`](./skills/charity-writing-assistant/) | [charity-writing-assistant](./skills/charity-writing-assistant/SKILL.md) | 当用户提到公益文书、项目申请、结项报告、传播计划、写文书（公益场景）、写报告（公益项目）、整理材料（公益机构）、捐赠人服务方案、肖像授权书、项目上线、平台申请时使用。⚠️ 不适用… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`dingtalk-unified`](./skills/dingtalk-unified/) | [dingtalk-unified](./skills/dingtalk-unified/SKILL.md) | 钉钉 CLI 全能套件，基于官方 DingTalk Workspace CLI（dws）操作钉钉消息、群聊、通讯录、日历、待办、审批、考勤、日志、DING、AI 表格、钉钉文档、… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`email-daily-summary`](./skills/email-daily-summary/) | [email-daily-summary](./skills/email-daily-summary/SKILL.md) | 自动登录邮箱（Gmail/Outlook/QQ 邮箱等）并生成每日邮件摘要。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY` | 2026-07-21 |
| [`english-intensive-reader`](./skills/english-intensive-reader/) | [english-intensive-reader](./skills/english-intensive-reader/SKILL.md) | AI 英语精读工具，支持输入英文文章（纯文本 / URL / PDF / Word），自动逐句语法拆解 + 生词分级标注，生成双栏阅读笔记（左栏原文高亮 / 右栏逐句分析）+ 全文摘要 + 值得背诵句型；支持逐句 / … | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`flights-search`](./skills/flights-search/) | [flights](./skills/flights-search/SKILL.md) | 通过 Google Flights 搜机票：直飞/中转、按时间筛选。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`flutter-dev`](./skills/flutter-dev/) | [flutter-dev](./skills/flutter-dev/SKILL.md) | Flutter 跨平台开发指南：组件模式、Riverpod/Bloc 状态管理。 | 无 | 2026-07-21 |
| [`gifgrep`](./skills/gifgrep/) | [gifgrep](./skills/gifgrep/SKILL.md) | 搜索 GIF 的 CLI/TUI 工具：下载结果并提取静态图/雪碧图。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`GIPHY_API_KEY`、`TENOR_API_KEY` | 2026-07-21 |
| [`gmail`](./skills/gmail/) | [gmail](./skills/gmail/SKILL.md) | Gmail API 集成（托管 OAuth）：收发与管理邮件、线程、标签。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`MATON_API_KEY`、`YOUR_API_KEY` | 2026-07-21 |
| [`gog`](./skills/gog/) | [gog](./skills/gog/SKILL.md) | Google Workspace CLI：Gmail、日历、云盘、通讯录、表格、文档。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`grill-me`](./skills/grill-me/) | [grill-me](./skills/grill-me/SKILL.md) | 就计划或设计向用户连环追问，直到达成共识。 | 无 | 2026-07-21 |
| [`guizang-ppt-skill`](./skills/guizang-ppt-skill/) | [guizang-ppt-skill](./skills/guizang-ppt-skill/SKILL.md) | 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。提供两种风格：① "电子杂志 × 电子墨水"（衬线 + 流体背景 + … | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`imap-smtp-email`](./skills/imap-smtp-email/) | [imap-smtp-email](./skills/imap-smtp-email/SKILL.md) | 通过 IMAP/SMTP 收发邮件：查新邮件、取内容、搜索。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`ios-application-dev`](./skills/ios-application-dev/) | [ios-application-dev](./skills/ios-application-dev/SKILL.md) | iOS 应用开发指南 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`knowledge-framework-builder`](./skills/knowledge-framework-builder/) | [knowledge-framework-builder](./skills/knowledge-framework-builder/SKILL.md) | 课程知识框架梳理工具，支持输入课程主题或教材资料（Markdown / DOCX / PDF / 图片截图 / URL），自动生成三档深度知识脉络图（框架 / 重点讲解 / 全节点讲解），含核心知识点提炼、概念依赖关系… | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`landing-page-generator`](./skills/landing-page-generator/) | [landing-page-generator](./skills/landing-page-generator/SKILL.md) | 根据需求简报生成完整可部署的落地页（单个自包含 HTML）。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`marketing-skills`](./skills/marketing-skills/) | [marketing-skills](./skills/marketing-skills/SKILL.md) | 23 个营销打法手册：CRO、SEO、文案、分析、实验、定价、发布等。 | 无 | 2026-07-21 |
| [`material-organizer`](./skills/material-organizer/) | [material-organizer](./skills/material-organizer/SKILL.md) | 批量资料整理工具，支持最多 30 项素材（URL/PDF/Word/图片/纯文本），自动提取要点、去重归类，输出带目录和来源溯源的结构化研究笔记，含关键词索引，支持保存为文件。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`minimax-docx`](./skills/minimax-docx/) | [minimax-docx](./skills/minimax-docx/SKILL.md) | Word 文档生成与编辑 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`minimax-pdf`](./skills/minimax-pdf/) | [minimax-pdf](./skills/minimax-pdf/SKILL.md) | 高质量 PDF 文档生成 | 无 | 2026-07-21 |
| [`nano-pdf`](./skills/nano-pdf/) | [nano-pdf](./skills/nano-pdf/SKILL.md) | 用自然语言指令编辑 PDF（nano-pdf CLI）。 | 无 | 2026-07-21 |
| [`notebooklm-studio`](./skills/notebooklm-studio/) | [notebooklm-studio](./skills/notebooklm-studio/SKILL.md) | 把来源（URL/YouTube/文件/文本）导入 Google NotebookLM 并生成制品。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`notion`](./skills/notion/) | [notion](./skills/notion/SKILL.md) | Notion API：创建和管理页面、数据库与块。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`NOTION_KEY` | 2026-07-21 |
| [`pptx-generator`](./skills/pptx-generator/) | [pptx-generator](./skills/pptx-generator/SKILL.md) | 生成、编辑、读取 PPT：用 PptxGenJS 从零创建等。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`react-native-dev`](./skills/react-native-dev/) | [react-native-dev](./skills/react-native-dev/SKILL.md) | React Native 跨平台开发指南 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`stock-analyzer`](./skills/stock-analyzer/) | [stock-analyzer](./skills/stock-analyzer/SKILL.md) | 全球股票综合分析工具。支持A股、港股、美股等东方财富覆盖的所有市场。根据用户输入的股票名称或代码，从东方财富网获取股票信息，进行基本面、新闻面、资金面三维分析，给出投资建议、买入… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`taobao`](./skills/taobao/) | [maishou](./skills/taobao/SKILL.md) | 商品价格全网对比技能，获取商品在淘宝(Taobao)、天猫(TMall)、京东(JD.com)、拼多多(PinDuoDuo)、抖音(Douyin)、快手(KaiShou)的最优价… | 无 | 2026-07-21 |
| [`teachany`](./skills/teachany/) | [teachany](./skills/teachany/SKILL.md) | K-12 交互式课件制作：学科课程页、动画等。 | 需要环境变量：`GH_TOKEN` | 2026-07-21 |
| [`trip-planner-generator`](./skills/trip-planner-generator/) | [trip-planner-generator](./skills/trip-planner-generator/SKILL.md) | 通过交互式问答帮助用户生成结构化的旅行行程计划，输出包含每日行程、预算明细、行前清单和注意事项的 Markdown 文档。在用户做旅行计划、行程规划、安排出行（travel pl… | 需要 12306 账号登录 | 2026-07-21 |
| [`tutor-skills`](./skills/tutor-skills/) | [tutor-skills](./skills/tutor-skills/SKILL.md) | 把 PDF、文档、代码库变成 Obsidian 学习库（结构化笔记+测验）。 | 无 | 2026-07-21 |
| [`wacli`](./skills/wacli/) | [wacli](./skills/wacli/SKILL.md) | 通过 wacli CLI 发送 WhatsApp 消息或搜索/同步聊天记录。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`weather-open-meteo`](./skills/weather-open-meteo/) | [weather-open-meteo](./skills/weather-open-meteo/SKILL.md) | 通过 open-meteo.com 公共 API 查询指定地点的当前天气和未来预报，无需 API key；当 open-meteo 请求失败时可降级使用 wttr.in。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`web-deploy`](./skills/web-deploy/) | [web-deploy](./skills/web-deploy/SKILL.md) | 用 Vercel、Railway、GitHub 等构建、预览和部署网站、Web 应用与 API。 | 需要登录 / OAuth / 扫码授权；需要环境变量：`SECRET_KEY` | 2026-07-21 |
| [`xurl`](./skills/xurl/) | [xurl](./skills/xurl/SKILL.md) | Twitter 研究与内容情报：分析账号、话题与内容。 | 无 | 2026-07-21 |
| [`yt-competitive-analysis`](./skills/yt-competitive-analysis/) | [yt-competitive-analysis](./skills/yt-competitive-analysis/SKILL.md) | YouTube 竞品分析，发现爆款视频与标题包装规律 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`YOUTUBE_API_KEY` | 2026-07-21 |

### 腾讯 / 微信 / 企微（47）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`andonq`](./skills/andonq/) | [andonq](./skills/andonq/SKILL.md) | AndonQ 腾讯云智能客服"领域虾" — 不切窗口、不排队，即刻获得腾讯云全产品线专业解答。支持工单查询（列表/详情/流水）、集团/MC 工单与需求单管理、腾讯云全产品线智能问… | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`aviation-weather`](./skills/aviation-weather/) | [aviation-weather](./skills/aviation-weather/SKILL.md) | 从 aviationweather.gov 获取航空气象数据（METAR/TAF/PIREPs）。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`cos-vectors`](./skills/cos-vectors/) | [cos-vectors](./skills/cos-vectors/SKILL.md) | 腾讯云 COS 向量桶全功能管理技能。覆盖向量桶、索引、向量数据的全生命周期管理，包括创建/删除/查询向量桶、创建/管理索引、插入/查询/搜索/删除向量数据、策略管理等 16 个… | 需要环境变量：`COS_VECTORS_SECRET_KEY` | 2026-07-21 |
| [`ctrip-wendao`](./skills/ctrip-wendao/) | [ctrip-wendao](./skills/ctrip-wendao/SKILL.md) | 当用户发起任意旅行相关问询时，包含但不限于：预订酒店、机票查询、火车票查询、景点推荐、寻找当地特色玩乐、目的地查询、行程规划、美食住宿攻略、签证、查询旅游攻略、获取旅行建议等场景… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`WENDAO_API_KEY` | 2026-07-21 |
| [`edgeone-pages-deploy`](./skills/edgeone-pages-deploy/) | [edgeone-pages-deploy](./skills/edgeone-pages-deploy/SKILL.md) | 用 EdgeOne CLI 把前端和全栈项目部署到腾讯 EdgeOne Pages。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`email-skill`](./skills/email-skill/) | [email-skill](./skills/email-skill/SKILL.md) | 邮件管理与自动化：多账号收发、搜索、整理。 | 需要环境变量：`EMAIL_PASSWORD` | 2026-07-21 |
| [`futuapi`](./skills/futuapi/) | [futuapi](./skills/futuapi/SKILL.md) | 富途 OpenAPI 交易与行情助手。查询股票行情、K线、报价、快照、买卖盘、逐笔成交、分时数据；解析期权简写代码、查询期权链、期权到期日；执行买入/卖出/下单/撤单/改单；查询… | 无（可选 API/账号以增强能力） | 2026-10-04 |
| [`haina-shopping-assistant`](./skills/haina-shopping-assistant/) | [haina-shopping-assistant](./skills/haina-shopping-assistant/SKILL.md) | 值得买开发的海纳购物管家，一款专业为用户提供来自全网与兴趣高度相关的、公允的AI消费决策支持工具。它支持四种消费决策模式：商品推荐（根据需求精准匹配合适的商品）、商品总结（对特定… | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`idea-validator`](./skills/idea-validator/) | [idea-validator](./skills/idea-validator/SKILL.md) | 用 Hexa 机会备忘录框架与 PCV 模型验证创业点子。 | 无 | 2026-07-21 |
| [`ima-skills`](./skills/ima-skills/) | [ima-skills](./skills/ima-skills/SKILL.md) | ima笔记与知识库管理（读取、写入、检索、上传文件） | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`IMA_OPENAPI_APIKEY` | 2026-07-21 |
| [`imsg`](./skills/imsg/) | [imsg](./skills/imsg/SKILL.md) | iMessage/短信 CLI：列出会话、历史、监听与发送。 | 无 | 2026-07-21 |
| [`install-futu-opend`](./skills/install-futu-opend/) | [install-futu-opend](./skills/install-futu-opend/SKILL.md) | Futu OpenD 安装助手。自动下载安装Futu OpenD 并升级 Python SDK。支持 Windows、MacOS、Linux。用户提到安装、下载、启动、运行、配置… | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`jiaozhen-factcheck`](./skills/jiaozhen-factcheck/) | [jiaozhen-factcheck](./skills/jiaozhen-factcheck/SKILL.md) | 事实查证工具，对输入内容的具体说法、资讯、事件或常识进行真实性、准确性、可靠性判断。当用户需要较真一下，查证问题或判断信息真伪、识别谣言、询问真假，是真的吗，真的假的，能否xxx… | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`legal-logic-analysis`](./skills/legal-logic-analysis/) | [legal-logic-analysis](./skills/legal-logic-analysis/SKILL.md) | 像律师一样分析法律问题：争点识别、管辖、风险评估。 | 无 | 2026-07-21 |
| [`markitdown-skill`](./skills/markitdown-skill/) | [markitdown-skill](./skills/markitdown-skill/SKILL.md) | 用微软 MarkItDown CLI 把各类文档转成 Markdown。 | 无 | 2026-07-21 |
| [`md-to-pdf-cjk`](./skills/md-to-pdf-cjk/) | [md-to-pdf-cjk](./skills/md-to-pdf-cjk/SKILL.md) | 把 Markdown 转成专业 PDF，完整支持中日韩文字。 | 无 | 2026-07-21 |
| [`model-usage`](./skills/model-usage/) | [model-usage](./skills/model-usage/SKILL.md) | 用 CodexBar CLI 本地用量数据汇总各模型（Codex/Claude）用量。 | 无 | 2026-07-21 |
| [`pdfkit-py`](./skills/pdfkit-py/) | [pdfkit-py](./skills/pdfkit-py/SKILL.md) | 纯 Python PDF 工具包：50 个命令覆盖读写、转换、表单、加密。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`peekaboo`](./skills/peekaboo/) | [peekaboo](./skills/peekaboo/SKILL.md) | 用 Peekaboo CLI 截屏并自动化 macOS UI。 | 无 | 2026-07-21 |
| [`qq-email`](./skills/qq-email/) | [qq-email](./skills/qq-email/SKILL.md) | QQ 邮箱 IMAP 收信 + SMTP 发信（Node.js 脚本，凭证从环境变量读取）。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`skyline`](./skills/skyline/) | [skyline](./skills/skyline/SKILL.md) | 微信小程序 Skyline 渲染引擎开发指导。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`tapd-openapi`](./skills/tapd-openapi/) | [tapd-openapi](./skills/tapd-openapi/SKILL.md) | TAPD OpenAPI skill，用于需求、缺陷、任务、迭代、Wiki、评论、工时、附件等 TAPD 平台操作。当用户提到「TAPD」「需求」「story」「缺陷」「bug」… | 需要环境变量：`TAPD_TOKEN` | 2026-07-21 |
| [`tdd`](./skills/tdd/) | [tdd](./skills/tdd/SKILL.md) | 测试驱动开发：红-绿-重构循环。 | 无 | 2026-07-21 |
| [`tdesign-miniprogram`](./skills/tdesign-miniprogram/) | [tdesign-miniprogram](./skills/tdesign-miniprogram/SKILL.md) | 腾讯 TDesign 微信小程序 UI 组件库开发指导。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`tencent-esign-contract`](./skills/tencent-esign-contract/) | [tencent-esign-contract](./skills/tencent-esign-contract/SKILL.md) | 腾讯电子签合同AI助手，支持合同起草、审查、对比、法条法规检索。当用户提到起草合同、写合同、生成合同、审查合同、检查合同风险、合规审核、法务审查、对比合同、合同差异、版本比较、查… | 需要登录 / OAuth / 扫码授权；需要环境变量：`ESIGN_TOKEN` | 2026-07-21 |
| [`tencent-musician-skills`](./skills/tencent-musician-skills/) | [tencent-musician-skills](./skills/tencent-musician-skills/SKILL.md) | 腾讯音乐人智能分析助手（数据分析 + 宣推）。当用户提到以下任一类请求时触发：【数据分析类】分析数据、看播放趋势、歌曲表现、听众画像、数据洞察、粉丝构成、我的数据怎么样、分析这首… | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`tencent-news`](./skills/tencent-news/) | [tencent-news](./skills/tencent-news/SKILL.md) | 7×24 新闻资讯搜索工具，聚焦中国国内信息和国际热点。支持新闻搜索，包括热点新闻、早报晚报、实时资讯、领域新闻和天气信息查询。当用户需要搜索新闻、新闻热榜、新闻早晚报、订阅新闻… | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`tencent-rumor-refuter`](./skills/tencent-rumor-refuter/) | [tencent-rumor-refuter](./skills/tencent-rumor-refuter/SKILL.md) | 嘿！我是小P \U0001F427，腾讯公司谣言辟谣辅助技能 有关腾讯公司的信息真真假假，我来帮你看看！ 可以通过以下方式唤醒我： (1) 直接呼叫\"小P\"或\"小p\"； … | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`tencent-ssv-techforgood`](./skills/tencent-ssv-techforgood/) | [tencent-ssv-techforgood](./skills/tencent-ssv-techforgood/SKILL.md) | 专注公益机构数字化赋能的智能助手，围绕腾讯技术公益数字工具箱（techforgood.qq.com）为社会组织匹配免费或低成本数字化产品，支持需求诊断、产品推荐、申领指引、数字化… | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`tencent-weather`](./skills/tencent-weather/) | [tencent-weather](./skills/tencent-weather/SKILL.md) | 腾讯天气查询：覆盖全国城市与区县（tencent-news CLI）。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`tencent-yuanbao-gaokao-regional-passing-scores`](./skills/tencent-yuanbao-gaokao-regional-passing-scores/) | [tencent-yuanbao-gaokao-regional-passing-scores](./skills/tencent-yuanbao-gaokao-regional-passing-scores/SKILL.md) | 高考地区分数线信息检索助手。当用户询问各省份历年高考录取分数线、录取批次或对应排名时使用，支持按地区、年份、选科和批次查询，自动适配新老高考政策差异。 | 无 | 2026-07-21 |
| [`tencent-yuanbao-gaokao-score-to-rank-lookup`](./skills/tencent-yuanbao-gaokao-score-to-rank-lookup/) | [tencent-yuanbao-gaokao-score-to-rank-lookup](./skills/tencent-yuanbao-gaokao-score-to-rank-lookup/SKILL.md) | 高考一分一段信息检索助手，帮助考生根据分数查询全省排名位次，或根据位次估算对应分数区间，或提供一分一段表。 | 无 | 2026-07-21 |
| [`tencent-yuanbao-standard-search`](./skills/tencent-yuanbao-standard-search/) | [tencent-yuanbao-standard-search](./skills/tencent-yuanbao-standard-search/SKILL.md) | 用腾讯云 Web Search API（WSA）搜索网页。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`TENCENTCLOUD_WSA_APIKEY` | 2026-07-21 |
| [`tencentcloud-cls`](./skills/tencentcloud-cls/) | [tencentcloud-cls](./skills/tencentcloud-cls/SKILL.md) | 腾讯云日志服务 CLS 技能。支持 CQL 日志检索、上下文查看、日志主题/日志集查看、机器组与机器状态查看、采集规则查看、日志直方图、指标采集与 PromQL 查询、告警策略与… | 需要环境变量：`TENCENTCLOUD_SECRET_ID`、`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`tencentcloud-cos`](./skills/tencentcloud-cos/) | [tencentcloud-cos](./skills/tencentcloud-cos/SKILL.md) | 腾讯云对象存储（COS）与数据万象（CI）：文件存储管理、图片 AI 处理（超分/裁剪/水印/识别）与知识库。 | 需要环境变量：`TENCENT_COS_SECRET_KEY`、`TENCENT_COS_TOKEN` | 2026-07-21 |
| [`tencentmap-lbs-skill`](./skills/tencentmap-lbs-skill/) | [tencentmap-lbs-skill](./skills/tencentmap-lbs-skill/SKILL.md) | 腾讯地图位置服务，支持POI搜索、路径规划、旅游规划、周边搜索，轨迹数据可视化和地图数据可视化。⚠️ 强制行为：本 Skill 加载后，第一个动作必须是检查是否存在正式 Key（… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`TMAP_WEBSERVICE_KEY` | 2026-07-21 |
| [`tencentmap-map-assistant`](./skills/tencentmap-map-assistant/) | [tencentmap-map-assistant](./skills/tencentmap-map-assistant/SKILL.md) | 腾讯位置服务·地图助手 Skill，一句自然语言调用腾讯地图全套能力，无需开发者账号、开箱即用。提供 AI 旅游攻略、地点搜索（含评分/人均/营业时间）、关键词提示、路线规划（驾… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`tencentos-expert`](./skills/tencentos-expert/) | [tencentos-expert](./skills/tencentos-expert/SKILL.md) | TencentOS Server 全栈运维诊断，根据用户的自然语言描述，自动识别需要的能力接口，查询能力实现，使用具体能力解决客户问题。覆盖磁盘空间/分区/文件系统/LVM/健康… | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`things-mac`](./skills/things-mac/) | [things-mac](./skills/things-mac/SKILL.md) | 在 macOS 上用 things CLI 管理 Things 3（URL scheme 增删项目与待办）。 | 需要环境变量：`THINGS_AUTH_TOKEN` | 2026-07-21 |
| [`wechat-article-pro`](./skills/wechat-article-pro/) | [wechat-article-pro](./skills/wechat-article-pro/SKILL.md) | 微信公众号文章发布专业版。功能：1)联网搜索热点信息 2)AI生成微信公众号封面图 3)撰写3000-5000字深度文章 4)使用公众号AI配图功能自动生成并上传封面 5)参考刘… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`wechat-article-search`](./skills/wechat-article-search/) | [wechat-article-search](./skills/wechat-article-search/SKILL.md) | 搜索微信公众号文章技能。通过微信搜索获取文章列表，覆盖科技/AI、社会热点、财经、教育、职场等各类中文资讯；可按关键词检索并返回标题、概要、发布时间、来源公众号与链接。当用户需要… | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`wechat-miniprogram`](./skills/wechat-miniprogram/) | [wechat-miniprogram](./skills/wechat-miniprogram/SKILL.md) | 微信小程序开发框架指导。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-21 |
| [`wechat-publisher`](./skills/wechat-publisher/) | [wechat-publisher](./skills/wechat-publisher/SKILL.md) | 一键发布 Markdown 到微信公众号草稿箱。基于 wenyan-cli，支持多主题、代码高亮、图片自动上传。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`WECHAT_APP_SECRET` | 2026-07-21 |
| [`wechatpay-basic-payment`](./skills/wechatpay-basic-payment/) | [wechatpay-basic-payment](./skills/wechatpay-basic-payment/SKILL.md) | 微信支付基础支付解决方案，涵盖支付、退款账单、分账、商户进件、开户意愿确认，提供选型/代码示例/业务速查/质量评估/排障五大能力。Use when user mentions "… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`wechatpay-product-coupon`](./skills/wechatpay-product-coupon/) | [wechatpay-product-coupon](./skills/wechatpay-product-coupon/SKILL.md) | 微信支付商品券接入解决方案，覆盖券类型选型、发券/核销/查询/退券/回调全链路，提供选型/示例代码/业务速查/质量评估/排障五大能力。Use when user mentions… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`wecom-unified`](./skills/wecom-unified/) | [wecom-unified](./skills/wecom-unified/SKILL.md) | 企业微信 CLI 全能套件，覆盖通讯录、文档、在线表格、智能表格、智能文档、日程、会议、待办、微盘、邮件、消息、媒体文件等业务域。支持按姓名/拼音/英文名/别名查找联系人与 us… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`xiaojia-free-marketing-pack`](./skills/xiaojia-free-marketing-pack/) | [xiaojia-free-marketing-pack](./skills/xiaojia-free-marketing-pack/SKILL.md) | 免费小嫁营销助手包：技能创意、节日热点、海报截图与轻量内容营销指导。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-21 |

### 设计 / UI / 地图（12）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`12306`](./skills/12306/) | [12306](./skills/12306/SKILL.md) | 查询 12306：车次、余票与车站信息。 | 需要 12306 账号登录 | 2026-07-21 |
| [`blogwatcher`](./skills/blogwatcher/) | [blogwatcher](./skills/blogwatcher/SKILL.md) | 用 blogwatcher CLI 监控博客和 RSS/Atom 订阅更新。 | 无 | 2026-07-21 |
| [`education`](./skills/education/) | [education](./skills/education/SKILL.md) | 生成学习计划、测验、抽认卡、复习材料并追踪学习进度。 | 无 | 2026-07-21 |
| [`fullstack-dev`](./skills/fullstack-dev/) | [fullstack-dev](./skills/fullstack-dev/SKILL.md) | 全栈应用架构与开发指南 | 需要登录 / OAuth / 扫码授权；需要环境变量：`JWT_SECRET` | 2026-07-21 |
| [`goal-tracker`](./skills/goal-tracker/) | [goal-tracker](./skills/goal-tracker/SKILL.md) | 长期目标追踪：里程碑、每日打卡与问责。 | 无 | 2026-07-21 |
| [`habit-tracker`](./skills/habit-tracker/) | [habit-tracker](./skills/habit-tracker/SKILL.md) | 习惯养成：连续打卡、提醒与进度可视化。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`ozon-1688-uploader`](./skills/ozon-1688-uploader/) | [ozon-1688-uploader](./skills/ozon-1688-uploader/SKILL.md) | 将1688的商品铺货到俄罗斯电商平台Ozon（上架），通过Ozon官方API实现商品信息的上传和状态查询。适用于需要将单个1688的商品上架到Ozon的场景。触发词：上传到Ozo… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`ALPHASHOP_ACCESS_KEY`、`ALPHASHOP_SECRET_KEY`、`OZON_API_KEY` | 2026-07-21 |
| [`shader-dev`](./skills/shader-dev/) | [shader-dev](./skills/shader-dev/SKILL.md) | GLSL 着色器技术大全：光线步进等炫酷视觉效果。 | 无 | 2026-07-21 |
| [`shopping-price-drop-coupon-scout`](./skills/shopping-price-drop-coupon-scout/) | [shopping-price-drop-coupon-scout](./skills/shopping-price-drop-coupon-scout/SKILL.md) | 监控用户指定商品的价格变动并汇总官方优惠券与促销信息，全程只读、不登录账号、不加购物车、不下单、不处理支付。当用户希望设置降价提醒、整理可用优惠券清单，或获取某商品/商家的促销汇… | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`songsee`](./skills/songsee/) | [songsee](./skills/songsee/SKILL.md) | 用 songsee CLI 从音频生成频谱图与特征面板可视化。 | 无 | 2026-07-21 |
| [`the-entrepreneurship-handbook`](./skills/the-entrepreneurship-handbook/) | [the-entrepreneurship-handbook](./skills/the-entrepreneurship-handbook/SKILL.md) | 面向创业者、管理者与商业领袖的问答技能。 | 无 | 2026-07-21 |
| [`weather`](./skills/weather/) | [weather](./skills/weather/SKILL.md) | 查询当前天气与预报（无需 API Key）。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |

### 其他（1）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`open-novel-writing`](./skills/open-novel-writing/) | [open-novel-writing](./skills/open-novel-writing/SKILL.md) | 中文长篇小说创作助手。支持从想法到成书的完整创作流程：世界观设定、故事大纲、章节规划、正文生成、质量评审。 使用场景：创作中文小说、辅助构思情节、生成章节正文、评审改进文稿。 特点：模块化设计，可单独使用任意模块；分级… | 无（可选 API/账号以增强能力） | 2026-07-21 |

## 2. 连接器 `connectors/`

| 目录 | 用来做什么 | 前置条件 | 最后更新 |
|------|------------|----------|----------|
| [`135ai-editor`](./connectors/135ai-editor/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`24haowan`](./connectors/24haowan/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`24haowan-space`](./connectors/24haowan-space/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`3chat-customer-growth`](./connectors/3chat-customer-growth/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`51shebao-hr-tools`](./connectors/51shebao-hr-tools/) | 51社保政策查询技能，用于查询中国城市社保与公积金的缴费基数、比例、办理截止日、最低工资、社平工资与产假天数，检索社保政策原文，并读取政策分析报告 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`58pic-qiantu-ai`](./connectors/58pic-qiantu-ai/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`77hub-qiqi`](./connectors/77hub-qiqi/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`77ircloud`](./connectors/77ircloud/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`adc-approval`](./connectors/adc-approval/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ADC_MCP_TOKEN` | 2026-10-21 |
| [`adc-sandbox`](./connectors/adc-sandbox/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ADC_MCP_TOKEN` | 2026-10-21 |
| [`agent-earth`](./connectors/agent-earth/) | AgentEarth 外部工具市场：发现并执行 1400+ 外部 API 工具。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`AGENT_EARTH_API_KEY` | 2026-10-04 |
| [`aholo-lux3d`](./connectors/aholo-lux3d/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LUX3D_CN_API_KEY` | 2026-10-21 |
| [`ai-hive`](./connectors/ai-hive/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`aiclass-teaching`](./connectors/aiclass-teaching/) | 腾讯未来教室（aiclass）教学服务操作技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`aidd-saas`](./connectors/aidd-saas/) | AI尽调助手 — 银行对公授信尽调全流程能力（进件识别、行业分析、企业画像、经营分析、财务分析、报告生成） | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`ailit`](./connectors/ailit/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`aimoderator`](./connectors/aimoderator/) | 思研平台（Aimoderator）是一个 AI 访谈调研工具。通过本 Connector，你可以帮用户在思研平台**创建访谈项目**并返回一条可直接分享的**访谈链接**，受访者… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`aiwho-warroom`](./connectors/aiwho-warroom/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`WARROOM_TOKEN` | 2026-10-21 |
| [`alphapai-lite-mcp`](./connectors/alphapai-lite-mcp/) | 调用 Alpha派 Lite 版投研 MCP。用于上市公司公告检索/详情/PDF/解析正文、结构化金融数据查询（A股、港股、指数、基金/ETF/REITs、债券、期货、期权和宏观… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`amazingdata-mcp`](./connectors/amazingdata-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`AD_PASSWORD` | 2026-10-21 |
| [`anbcd-enterprise`](./connectors/anbcd-enterprise/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`anguan-service-gateway`](./connectors/anguan-service-gateway/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`PLUGIN_API_KEY`、`PLUGIN_MACHINE_SECRET` | 2026-10-21 |
| [`archive-hospital-mcp`](./connectors/archive-hospital-mcp/) | 全周期智能管理平台（archive_hospital_server）只读 Connector。围绕当前登录医生的患者档案提供跨域查询能力，覆盖患者/标签画像/生活方式/随访/用药… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`INVALID_TOKEN` | 2026-10-04 |
| [`at-grid-connector`](./connectors/at-grid-connector/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`atlas-cloud`](./connectors/atlas-cloud/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`awehome-enterprise-tools`](./connectors/awehome-enterprise-tools/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`awehome-loushu`](./connectors/awehome-loushu/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`awehome-newmedia`](./connectors/awehome-newmedia/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`awesun`](./connectors/awesun/) | 向日葵（AweSun）远程控制 CLI 工具。提供设备列表管理、远程会话管理、远程桌面控制、远程命令执行、远程文件传输、端口转发、远程关机/重启/唤醒等功能。用户提到向日葵、Aw… | 需要登录 / OAuth / 扫码授权 | 2026-08-06 |
| [`baidu-maps`](./connectors/baidu-maps/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证 | 2026-10-21 |
| [`baidu-netdisk`](./connectors/baidu-netdisk/) | 百度网盘文件管理与智能检索。支持浏览、关键词和语义搜索、文件整理、分享链接、容量查询，以及保存文本内容或通过 URL 转存文件。触发关键词：百度网盘、网盘、baidu、netdi… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`baijimu-enterprise-ai`](./connectors/baijimu-enterprise-ai/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`baixiao-mcp`](./connectors/baixiao-mcp/) | 百晓智能 —— 学术检索技能： 中文人文社科文献与政策检索、参考文献核实、引用追溯、投稿期刊与审稿人推荐 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`BAIXIAO_API_KEY` | 2026-10-04 |
| [`baixyn-traffic-referral`](./connectors/baixyn-traffic-referral/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`bayuegua-patent`](./connectors/bayuegua-patent/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`BAYUEGUA_API_KEY` | 2026-10-21 |
| [`bayuegua-trademark`](./connectors/bayuegua-trademark/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`BAYUEGUA_API_KEY` | 2026-10-21 |
| [`bazhuayu`](./connectors/bazhuayu/) | 八爪鱼云采集 MCP 技能 - 搜索模板、启动与管理任务、查询进度、导出结构化数据 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-11 |
| [`bcpmdata-openmcp`](./connectors/bcpmdata-openmcp/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-21 |
| [`beatapi-beatdesign`](./connectors/beatapi-beatdesign/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`beisen-cli`](./connectors/beisen-cli/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`beluga-mcp-prod`](./connectors/beluga-mcp-prod/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`biobuddy`](./connectors/biobuddy/) | 当用户提出生物医药研究类需求时使用——抗体/多肽/酶设计、分子结构预测、病理质控、基因突变预测、虚拟空间转录组、疾病靶点发现与评估、单细胞与扰动分析、蛋白质检索、文献情报、专利检… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`bizmuse-ai-music-video`](./connectors/bizmuse-ai-music-video/) | 用 BizMuse 从音频、参考图和创意方向生成 AI 音乐视频。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`boya-os`](./connectors/boya-os/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`bugly-token`](./connectors/bugly-token/) | 查看 Bugly 产品质量概览（崩溃率、ANR 率、FOOM/OOM 率、启动耗时等）。当用户询问应用的大盘质量、版本质量、今日质量等指标时使用。 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`BUGLY_ACCESS_TOKEN` | 2026-08-06 |
| [`caihui-mcp`](./connectors/caihui-mcp/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-04 |
| [`camscanner-mcp`](./connectors/camscanner-mcp/) | 扫描全能王 文档处理 — 智能文档转换与处理平台，【CamScanner 官方 MCP Skill】。当用户提到 扫描全能王、CamScanner、文档转换、图片转Word、图片… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`candao-age`](./connectors/candao-age/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`canva`](./connectors/canva/) | 使用 Canva 设计能力：创建/编辑设计、管理素材与品牌资源。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`car-saas`](./connectors/car-saas/) | 查询停车场运营数据与车辆信息。当用户想了解停车场今日收入/车流/剩余车位、查询车辆（车牌号/姓名/手机号）、查看通行记录、临停收费记录、收入车流日报、设备与车道状态时使用。触发词… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`cbnb-mcp-gateway`](./connectors/cbnb-mcp-gateway/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`chainlon-geo-mcp`](./connectors/chainlon-geo-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`charge-order-query`](./connectors/charge-order-query/) | 订单门店查询技能 - 按手机号查询共享充电宝租借订单、按经纬度查询附近门店 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`chinacscs-data`](./connectors/chinacscs-data/) | 中证数智企业数据查询技能 - 覆盖工商、司法风险、财务、舆情、中证特色经营数据与区域经济指标 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`CSCS_API_KEY` | 2026-10-21 |
| [`chuangkit`](./connectors/chuangkit/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`chuhaijiang`](./connectors/chuhaijiang/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-08 |
| [`ciccwm-mcp`](./connectors/ciccwm-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`cisp-mcp`](./connectors/cisp-mcp/) | 查询并核验中国企业数据：工商注册、股东等（cisp）。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`CISP_API_KEY` | 2026-10-04 |
| [`ckjr-mcp-wb`](./connectors/ckjr-mcp-wb/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`cloudbase`](./connectors/cloudbase/) | CloudBase 开发、设计、构建、部署、调试、迁移与排障。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`cloudhub`](./connectors/cloudhub/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`cloudmall-operations`](./connectors/cloudmall-operations/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`cmwa-quote`](./connectors/cmwa-quote/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`cnb-api`](./connectors/cnb-api/) | CNB 平台交互命令，支持代码仓库、Issue、PR、CI、制品库读写等操作。 | 无（可选 API/账号以增强能力） | 2026-10-21 |
| [`cnki-edu`](./connectors/cnki-edu/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`connector-workshop`](./connectors/connector-workshop/) | 探测远程 MCP 端点，起草并校验 WorkBuddy 连接器并下载。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`contractkit-template`](./connectors/contractkit-template/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`coros`](./connectors/coros/) | 查询与分析 COROS 运动和健康数据，创建与修改训练计划、课程，并安排训练日程 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`cqq-skills`](./connectors/cqq-skills/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`creatok`](./connectors/creatok/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`cue-parser`](./connectors/cue-parser/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`cyrj-datawise`](./connectors/cyrj-datawise/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dami-external-mcp`](./connectors/dami-external-mcp/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`MCP_API_KEY` | 2026-10-04 |
| [`databuddy`](./connectors/databuddy/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`datahub`](./connectors/datahub/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`datayes-data`](./connectors/datayes-data/) | 使用通联数据 MCP 查询 A股与港股、基金、债券、指数、期货期权、因子、行情、宏观、公告、分析师预测和政策法规。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dbzq-connector-tool`](./connectors/dbzq-connector-tool/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`DBZQ_TOKEN` | 2026-10-04 |
| [`dcs-cloud`](./connectors/dcs-cloud/) | 通过 dcs CLI 操作 DCS Cloud：项目、离线分析任务、WDL 工作流。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证 | 2026-10-04 |
| [`deeplink`](./connectors/deeplink/) | 提供克而瑞房地产数据查询能力，由深度智联提供服务，依托经克而瑞授权、积累近 20 年的中国不动产数据；核心「问数」覆盖新房、二手房、土地、企业、宏观、长租公寓、产城、康养、商办九… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`INVALID_API_KEY` | 2026-10-04 |
| [`deli-mcp`](./connectors/deli-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`deployx-dxc`](./connectors/deployx-dxc/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`designkit-buddy-cli`](./connectors/designkit-buddy-cli/) | 使用美图设计室 AI设计 CLI 调用 Team Agent。适用于用户要求创建或继续美图设计室任务，发送文本、图片、视频、文档或音频，查看任务进度，回答普通追问或自定义业务卡片… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`dingdanbao`](./connectors/dingdanbao/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dingtalk`](./connectors/dingtalk/) | 管理钉钉产品能力(Agoal目标管理/AI表格/AI搜问/日历/通讯录/群聊与机器人/待办/审批/法务智能合同/考勤/日志/DING消息/开放平台文档/钉钉文档/钉钉云盘/原生M… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dingteam-suite`](./connectors/dingteam-suite/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dknowc-mcp`](./connectors/dknowc-mcp/) | 使用深知可信工作台处理法律、政策、标准、产业研究和公共服务问题；支持可信问答、权威检索、复杂问题拆解、多来源验证和权威原文溯源。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`dnb-global-data`](./connectors/dnb-global-data/) | 使用邓白氏查全球 D&B Global Search 查询企业商业数据，可进行邓白氏编码 (DUNS) 匹配查询目标企业主体，查询工商/注册信息、财务数据、股权与最终受益人 (U… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`DNB_ACCESS_TOKEN` | 2026-10-04 |
| [`dnb-longyicha-workbuddy`](./connectors/dnb-longyicha-workbuddy/) | 使用 D&B China Data（主题化中国数据 CDT）MCP 企业档案 Server（/v1/company）全部 14 个 Tool，对单一企业开展工商登记、简易注销、变… | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`dop-platform-mcp`](./connectors/dop-platform-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dramabuddy`](./connectors/dramabuddy/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`duifene-homework-grading`](./connectors/duifene-homework-grading/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`MCP_API_KEY` | 2026-10-21 |
| [`duoguan-course`](./connectors/duoguan-course/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`duoguan-fengchao`](./connectors/duoguan-fengchao/) | 夺冠蜂巢（duoguan-fengchao）AI 自媒体内容生产。当用户需要热点选题、口播/图文文案、配图、配音、播客、视频封装、多账号内容运营或发布准备时使用本连接器。连接后先… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`duoguan-ge`](./connectors/duoguan-ge/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dxy-medical-search`](./connectors/dxy-medical-search/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`dzh-mcp`](./connectors/dzh-mcp/) | 大智慧金融MCP连接器，提供A股K线行情、A股实时行情、港美股K线行情、港美股实时行情、期货K线行情、期货实时行情、基金行情、公司简况资料、公司主营产品、公司股东、公司分红送转、… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`easymofang`](./connectors/easymofang/) | 商品文案/图片商标侵权检测，以及电商套图生成与重绘（白底图、场景图、功能图、对比图、尺寸图、普通A+、普通A+裁剪版、高级A+；平台 Amazon/亚马逊、AliExpress/… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`ec-crm-cli`](./connectors/ec-crm-cli/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`edgeone-pages`](./connectors/edgeone-pages/) | 将项目部署到 EdgeOne Makers 并返回线上访问地址，支持全栈、云函数、边缘函数、AI Agent、KV/Blob 存储、中间件等开发场景。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`edu-next`](./connectors/edu-next/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`efunds`](./connectors/efunds/) | 接入易方达基金MCP服务，一句话查透基金画像——业绩、风险收益、持仓结构等核心指标一目了然，还能随时调阅易方达发布的投研观点、产品解读与市场洞察，助力您高效进行投资决策。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`emes-ai`](./connectors/emes-ai/) | eMES AI Connector - 智连 eMES 制造执行系统，通过 MCP 协议对接鼎华 eMES 的 AI 能力（开发环境：amos-dev.digihua.com）。… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`emr-query`](./connectors/emr-query/) | 腾讯云 EMR 只读查询技能 — 基于官方 tccli 的 48 个只读查询接口文档与调用模板 | 需要登录 / OAuth / 扫码授权 | 2026-08-06 |
| [`erhao-hr`](./connectors/erhao-hr/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ERHAO_HR_KEY` | 2026-10-04 |
| [`es`](./connectors/es/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`eudic-openapi`](./connectors/eudic-openapi/) | 管理欧路词典、法语助手、德语助手或西语助手中的生词本、笔记、例句和个人语料；当用户要查询、添加、重命名或删除这些数据，或从文章提取词汇提示时使用。 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`EUDIC_TOKEN` | 2026-10-21 |
| [`ezjoin-meeting`](./connectors/ezjoin-meeting/) | EzyJoin 智慧会议操作技能 - 预约会议室、创建/取消会议、查询会议日程与 AI 纪要、企业知识库检索 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-12 |
| [`ezr-crm`](./connectors/ezr-crm/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fadada-richee`](./connectors/fadada-richee/) | 法大大睿契连接器（Fadada-Richee）的 MCP 使用指南。提供法律法规检索、类案检索、 企业信息查询与合同审查等法律能力。当用户需要查找法条、检索相似案例、查询企业工商/涉诉信息、 审查合同风险条款、生成或导… | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`faisco-site-articles`](./connectors/faisco-site-articles/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`FAISCO_API_KEY` | 2026-10-21 |
| [`fanruan-growth-advisor`](./connectors/fanruan-growth-advisor/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fastmoss`](./connectors/fastmoss/) | 使用 FastMoss MCP 查询和分析 TikTok Shop 商品、达人、店铺及内容数据。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fazhi-law`](./connectors/fazhi-law/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fbs-connector`](./connectors/fbs-connector/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fedin-vibe`](./connectors/fedin-vibe/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`feishu`](./connectors/feishu/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`fenbeitong`](./connectors/fenbeitong/) | 分贝通 WorkBuddy Connector。用于账号与企业、差旅、申请单、订单、消费规则、发票报销、消费洞察、合规、降本及客服。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fenbi-baokao-decision`](./connectors/fenbi-baokao-decision/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`finenter`](./connectors/finenter/) | 用 Finenter 投研 MCP 查询机构观点、研报等。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fiu-mcp-server`](./connectors/fiu-mcp-server/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-21 |
| [`flomo`](./connectors/flomo/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`flova`](./connectors/flova/) | 当用户在 WorkBuddy 中搜索或提出视频、图片、剧本、短片、短剧、漫剧、AI、文生图、文生视频、图生视频、生成、内容、广告、商品、TVC、设计、电影等创作需求，或希望通过 … | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`fosunwealth`](./connectors/fosunwealth/) | 复星财富：以清晰洞察探索你关心的金融问题。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`fubei-invoice`](./connectors/fubei-invoice/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`fuma-ai-callout`](./connectors/fuma-ai-callout/) | 赋马 AI 外呼：电话外呼任务创建与查询。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ACCESS_TOKEN` | 2026-10-04 |
| [`fyopen-lawsearch`](./connectors/fyopen-lawsearch/) | 法研·法律法规检索 MCP Skill。涉及「法律法规」「法条」「法规条文」「民法典」「现行有效法规」等关键词时使用。支持自然语言获取精准、现行有效的法规条文，将高质量、海量的法… | 可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`fz-agents-tsp`](./connectors/fz-agents-tsp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`gaia-ai-workforce`](./connectors/gaia-ai-workforce/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`gangtise-mcp`](./connectors/gangtise-mcp/) | 用 Gangtise（贯喜）MCP 查行情、研报、知识库、个股。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`GTS_ACCESS_KEY`、`GTS_SECRET_KEY` | 2026-08-12 |
| [`gaoding`](./connectors/gaoding/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`gaodun-job`](./connectors/gaodun-job/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`getnote`](./connectors/getnote/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`gfsecurities`](./connectors/gfsecurities/) | 通过广发证券 MCP 查询新闻资讯、研究报告、行情排行、资金流向、个股/ETF 异动、热点专题和投研日历。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`gildata`](./connectors/gildata/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`GILDATA_TOKEN` | 2026-07-21 |
| [`github`](./connectors/github/) | 通过 GitHub MCP 服务器访问 GitHub 能力。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`gitlab-docs-mcp`](./connectors/gitlab-docs-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`gongxie-erp`](./connectors/gongxie-erp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ERP_TOKEN` | 2026-10-04 |
| [`gongyi-open-mcp`](./connectors/gongyi-open-mcp/) | 腾讯公益机构服务平台连接器：用自然语言连接并使用腾讯公益机构服务平台的功能。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`grain-print`](./connectors/grain-print/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`GRAIN_TOKEN` | 2026-10-04 |
| [`gt-generate-sql-data`](./connectors/gt-generate-sql-data/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`guansd`](./connectors/guansd/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`guiputi-intent-card`](./connectors/guiputi-intent-card/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`GPTCN_API_KEY` | 2026-10-21 |
| [`h3c-cloudnet`](./connectors/h3c-cloudnet/) | 新华三 Cloudnet 灵犀 AI 助手 - 网络状态查询、网络问题分析、终端故障排查 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`CLOUDNET_API_KEY` | 2026-10-04 |
| [`h3yun-connector`](./connectors/h3yun-connector/) | 查找和操作氚云（H3Yun）应用、表单、业务记录。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`haier-assistant`](./connectors/haier-assistant/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`hanyi-fonts`](./connectors/hanyi-fonts/) | 查询汉仪企业签约主体、合同覆盖字体和权益摘要，并生成字体预览 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`haoxinqing-mood`](./connectors/haoxinqing-mood/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`hefei-city-alerts`](./connectors/hefei-city-alerts/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`hl-dolphin-stock`](./connectors/hl-dolphin-stock/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`hose-ai-assistant`](./connectors/hose-ai-assistant/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`hrlink`](./connectors/hrlink/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`huatu-guokao-screening`](./connectors/huatu-guokao-screening/) | 华图国考条件筛岗。用户问“我能报哪些国考岗位”“按学历、专业、地区筛国考职位”时使用：通过华图国考筛岗连接器拉取正式条件选项、收集报考条件、查询当前国考职位表的命中岗位，对话展示… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`huilianyi`](./connectors/huilianyi/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`huita-ims`](./connectors/huita-ims/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`huize-insurance-product-recommendation`](./connectors/huize-insurance-product-recommendation/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`huodingdong-erp`](./connectors/huodingdong-erp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`HDD_MCP_KEY` | 2026-10-04 |
| [`huodongxing-pro`](./connectors/huodongxing-pro/) | 查看活动数据与报名情况，创建并完善活动草稿、票种、报名表和付费条款，或在展示规则后提交活动发布请求。当用户提到「帮我创建活动」「完善活动信息」「看看活动数据」「活动报名怎么样」「… | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`ifind-mcp`](./connectors/ifind-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`ihr-cli`](./connectors/ihr-cli/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`ima-mcp`](./connectors/ima-mcp/) | ima - 腾讯AI知识管家个人版，用于搜索、读取和写入个人账号下的知识库（含"问我的知识库"、"个人知识库"、"我存过的资料"、"存进 ima"、ima.qq.com），并可搜… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`infimind-ecommerce-content`](./connectors/infimind-ecommerce-content/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`intco-ai-platform`](./connectors/intco-ai-platform/) | 英科内部业务系统、RPA、企业数仓和企业付费数据的统一探索与调用入口 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`investoday-finance-data`](./connectors/investoday-finance-data/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`ioa`](./connectors/ioa/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`ipmaster-trademark`](./connectors/ipmaster-trademark/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`iyiou-connector`](./connectors/iyiou-connector/) | 亿欧数据查询技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`CLIENT_SECRET` | 2026-10-04 |
| [`jiandaoyun`](./connectors/jiandaoyun/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`jianguo-cloud-oauth`](./connectors/jianguo-cloud-oauth/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`jihua-ai-studio`](./connectors/jihua-ai-studio/) | 使用极画AI设计室 Connector 查询用户数据、查看生成任务并创建纯文生图。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`jinshouzhi`](./connectors/jinshouzhi/) | 金手指广告投放技能 - 查询项目数据、写回需求单与文案、生成投放主台深链、轻量调优 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`jinshuju`](./connectors/jinshuju/) | 金数据（Jinshuju，jinshuju.net）操作技能 —— 创建/复制/编辑表单与主题，增删改查与批量修改表单数据，上传图片附件，查询账户套餐与团队成员。触发词：金数据、… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-24 |
| [`jiucuodashi`](./connectors/jiucuodashi/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`jiuliang-198-health-connector`](./connectors/jiuliang-198-health-connector/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-21 |
| [`jiushuyun`](./connectors/jiushuyun/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-08-12 |
| [`joyread-english`](./connectors/joyread-english/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`JOYREAD_TOKEN` | 2026-10-04 |
| [`jufa-mcp-server`](./connectors/jufa-mcp-server/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`JUFA_API_KEY` | 2026-10-21 |
| [`jumper-kpi`](./connectors/jumper-kpi/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`kdocs`](./connectors/kdocs/) | 金山文档官方 Skill。对话即操作——知识一键存入、碎片内容整理、接龙转表格、文档转 Markdown、表格美化、收发表生成，全在一句话内完成。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`KINGSOFT_DOCS_TOKEN` | 2026-10-04 |
| [`kingbot-xiaodie`](./connectors/kingbot-xiaodie/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`kiwi-merchant`](./connectors/kiwi-merchant/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`kiwi-sourcing`](./connectors/kiwi-sourcing/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`kling-ai-plugin`](./connectors/kling-ai-plugin/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`knot`](./connectors/knot/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`kuaicha-search`](./connectors/kuaicha-search/) | 企业数据查询、筛选及关系分析能力。覆盖工商信息、股东股权、对外投资、 经营动态、经营与司法风险、知识产权、招投标及新闻舆情等多维数据， 支持企业拓客、风险评估、数据统计、企业对比及关系判断。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要环境变量：`KUAICHA_API_KEY` | 2026-10-04 |
| [`kujiale-ai-draw`](./connectors/kujiale-ai-draw/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`kuka-service`](./connectors/kuka-service/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`laiye-adp`](./connectors/laiye-adp/) | 通过来也 ADP MCP 处理本地文件、HTTP(S) 文件 URL 或 Base64：上传文件，解析 PDF、图片和 Office 文档，抽取中国票据、海外发票、采购订单及中国… | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ADP_API_KEY` | 2026-10-04 |
| [`lawaken-memory`](./connectors/lawaken-memory/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LAWAKEN_MCP_KEY` | 2026-10-04 |
| [`lawyerone`](./connectors/lawyerone/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`APIKEY` | 2026-10-04 |
| [`leads-cloud-crm`](./connectors/leads-cloud-crm/) | 询盘云 CRM 只读查询技能 - 分页查询线索、客户、联系人、商机、触点联系人、SKU、订单、订单明细，按对象查跟进记录与互动时间线，按触点值或对象查画像，查询 WhatsApp… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LEADS_CLOUD_MCP_TOKEN` | 2026-10-04 |
| [`lemon-agi`](./connectors/lemon-agi/) | 乐檬零售 AGI 能力平台，用于查询乐檬零售生态的批发、仓储、零售等业务数据。当用户需要查询批发销售单、批发退货单、客户信息、批发价、库存、入库出库等业务数据时使用。 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LEMON_AGI_TOKEN` | 2026-10-04 |
| [`lemonclaw`](./connectors/lemonclaw/) | 柠檬云业务技能。用户询问个税、个人所得税或自然人电子税务局的申报情况时也必须使用，以便直接说明该场景不支持并引导官方客服，不执行业务查询。其他场景通过 lemonclaw-cli… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`lexiang`](./connectors/lexiang/) | 乐享知识库 MCP 全功能 Skill。当用户提到「乐享」「知识库」「个人知识库」「我的知识库」「lexiang」，或提供 lexiangla.com 链接，或涉及知识库的搜索/… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`liesun`](./connectors/liesun/) | 猎隼招聘查询与受控写入——查岗位、候选人、面试、录音分析摘要和招聘分析；创建岗位或上传简历必须先预览再确认 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`lingxi`](./connectors/lingxi/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`lingxing-mcp`](./connectors/lingxing-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LINGXING_MCP_KEY` | 2026-08-15 |
| [`lingyi-mcp`](./connectors/lingyi-mcp/) | 零一运营 MCP：用 open_lingyi_skill 按 slug 打开对应 Skill 的 MCP App 表单。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`linkfox`](./connectors/linkfox/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`listinggood`](./connectors/listinggood/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LISTINGGOOD_API_KEY` | 2026-10-04 |
| [`longclaw-research`](./connectors/longclaw-research/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`lookai`](./connectors/lookai/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`lovrabet-cli`](./connectors/lovrabet-cli/) | Lovrabet 运行态 CLI — 面向业务场景的 AI 操作套件，通过 lovrabet 命令管理应用目录、业务角色与权限、用户级外部账号、Service Tree 业务命令… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`ACCESS_KEY`、`LOVRABET_ACCESS_KEY` | 2026-10-21 |
| [`luoge-uc`](./connectors/luoge-uc/) | 罗格用户中心账号技能 - 发送短信验证码、手机号验证码登录、查询当前登录用户信息 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`lvshu-hotel-booking`](./connectors/lvshu-hotel-booking/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LVSHU_API_KEY` | 2026-10-21 |
| [`lxcloud`](./connectors/lxcloud/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`lxjy-wanxiang-app`](./connectors/lxjy-wanxiang-app/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`magic-agent-token`](./connectors/magic-agent-token/) | 腾讯企点营销云的营销业务查询、分析、策划与任务协同。覆盖五类场景：消费者运营（首购转化、新人券、加购未购、复购提频、一转二、沉睡唤醒、流失召回、拉新获客、老带新、会员等级、生日礼… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-10-21 |
| [`market-expert-gateway`](./connectors/market-expert-gateway/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`WORKBUDDY_AUDIENCE_GATEWAY_TOKEN` | 2026-10-21 |
| [`masocloud-barcode-generator`](./connectors/masocloud-barcode-generator/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`mastergo-vibe-mcp`](./connectors/mastergo-vibe-mcp/) | 连接 MasterGo 画布，让 AI 设计、修改、同步和取回设计稿。 | 可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`medgroup-drgdip-toolkit`](./connectors/medgroup-drgdip-toolkit/) | 识别 DRG/DIP 分组、编码、规则和结算任务，调用 MedGroup 工具并引用实际结果。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`medlive-medical-qa`](./connectors/medlive-medical-qa/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`meitu-ai`](./connectors/meitu-ai/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`meitu-kaipai`](./connectors/meitu-kaipai/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`meituan-for-business`](./connectors/meituan-for-business/) | 美团企业版连接器，用于连接美团企业版账号、完成授权登录并在本机维护登录态。当用户提到美团企业版、Meituan for Business、企业版登录、登录态、sqt-auth-c… | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`menglar-ozon`](./connectors/menglar-ozon/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ACCESS_TOKEN` | 2026-10-04 |
| [`meo-xiaoyuan`](./connectors/meo-xiaoyuan/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-04 |
| [`mergerinfo`](./connectors/mergerinfo/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证 | 2026-10-04 |
| [`mglc`](./connectors/mglc/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`miaoda`](./connectors/miaoda/) | 秒哒（Miaoda）应用搭建平台交互命令，支持通过自然语言对话创建、生成、修改、发布网页/Web应用/小程序/移动App等。 | 需要登录 / OAuth / 扫码授权 | 2026-08-11 |
| [`miaozhen-lingmei-insight`](./connectors/miaozhen-lingmei-insight/) | 秒针灵眸 Insight：全网社媒分析——声量互动趋势、热点。 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`DATATAP_TOKEN` | 2026-10-21 |
| [`miki-cursor-catalog`](./connectors/miki-cursor-catalog/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`mindbye-contract-review`](./connectors/mindbye-contract-review/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`moa-workbench`](./connectors/moa-workbench/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`moka`](./connectors/moka/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`morningstar`](./connectors/morningstar/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`msy-brandct`](./connectors/msy-brandct/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证 | 2026-10-21 |
| [`mubu`](./connectors/mubu/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`mx-ds-mcp`](./connectors/mx-ds-mcp/) | 基于东方财富数据库，通过自然语言查询A股、基金、债券、指数/板块、美股、港股金融数据，以及期货/期权/日韩台德股、企业发行人与非上市公司等综合品种；宏观经济与行业经济指标；按条件… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`mxdtglobal`](./connectors/mxdtglobal/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`myunker-mcp`](./connectors/myunker-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`mzl-trademark`](./connectors/mzl-trademark/) | 摩知轮商标查询技能 —— 按条件检索商标（文本）与以图搜图（图形近似），覆盖中国及 110+ 海外国家/地区 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-07 |
| [`neo-crm`](./connectors/neo-crm/) | 用自然语言查客户、推商机、盘线索、领公海、写跟进，一句话打通销售工作闭环。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`neo-eakey`](./connectors/neo-eakey/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`neodata`](./connectors/neodata/) | 结构化参数查询股票/指数/板块/基金/债券/期货/外汇/贵金属/宏观等全品类金融数据 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`neosight`](./connectors/neosight/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`niuguwang-sim-trading`](./connectors/niuguwang-sim-trading/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`notion`](./connectors/notion/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`novai-studio`](./connectors/novai-studio/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`noxinfluencer-cli`](./connectors/noxinfluencer-cli/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`nvapp-windows-local`](./connectors/nvapp-windows-local/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`octic`](./connectors/octic/) | 在 agent（Claude Code / Codex / OpenClaw 等）内直接调用 Octic `octic` CLI 时使用：查看/搜索录音列表、查看详情与转写、读取… | 需要登录 / OAuth / 扫码授权；需要环境变量：`OCTIC_LOGIN_TOKEN`、`OCTIC_TOKEN` | 2026-10-21 |
| [`octopus-phone`](./connectors/octopus-phone/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`ofdh-doc-convert`](./connectors/ofdh-doc-convert/) | 通过 ofdh.cn 在线转换服务，将 OFD 与 PDF、Word、图片互转，并提取 OFD 正文文本。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-04 |
| [`oiioii`](./connectors/oiioii/) | 使用 OiiOii CLI 创建和管理 AI 图片、视频与音频，并处理工作空间、生成任务、资源和积分信息。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-10-21 |
| [`oneaix-sea-rate-connector`](./connectors/oneaix-sea-rate-connector/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`opcmenu`](./connectors/opcmenu/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`opendata`](./connectors/opendata/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`REGION_INSIGHT_API_KEY` | 2026-08-08 |
| [`orientfutures-mobile-knowledge-base`](./connectors/orientfutures-mobile-knowledge-base/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`pack-bi`](./connectors/pack-bi/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`BI_SECRET_KEY` | 2026-10-21 |
| [`pandadata`](./connectors/pandadata/) | 通过 PandaData MCP 查询和分析金融数据。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-12 |
| [`paper-retrieval`](./connectors/paper-retrieval/) | Repilot 科研智能体（对应 MCP 服务 paper-retrieval）：科研课题申报书与汇报 PPT 生成、快速学术文献检索、医学检测项目智能问答、文献综述报告生成，任… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`patchxfreenote`](./connectors/patchxfreenote/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`patentg-hanyuu`](./connectors/patentg-hanyuu/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`PATENTG_ORKEY` | 2026-10-21 |
| [`patsnap-search`](./connectors/patsnap-search/) | 通过 Patsnap MCP 检索专利与文献数据。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`PATSNAP_API_KEY` | 2026-08-06 |
| [`pcteam`](./connectors/pcteam/) | 筑享云项目与计划协同技能 - 项目查询、进展分析、计划调整、逻辑关系、关键路径与计划变更 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`picimos-dpe-industrial-mcp`](./connectors/picimos-dpe-industrial-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`picset-commerce-images`](./connectors/picset-commerce-images/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证 | 2026-10-04 |
| [`picset-video-generation`](./connectors/picset-video-generation/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证 | 2026-10-04 |
| [`pkulaw`](./connectors/pkulaw/) | 北大法宝官方法律检索与核验 MCP Skill。涉及「法律」「法规」「法条」「司法解释」「判例」「类案」「案由」「合同审查」「合规清单」「裁判规则」「裁判依据」「争议焦点」「指导… | 可能需要启用对应 MCP / 连接器 | 2026-08-15 |
| [`plaud`](./connectors/plaud/) | 连接 Plaud 录音与 AI：浏览查找录音、读取转写和 AI 摘要、汇总会议纪要，并生成跟进邮件与待办事项。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`primematrix-company`](./connectors/primematrix-company/) | 通过 Prime Matrix 企业 MCP 查询企业实体数据（精准查询）。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-04 |
| [`primematrix-ipr`](./connectors/primematrix-ipr/) | 通过 Prime Matrix IPR MCP 查询企业知识产权公开数据。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-21 |
| [`proboost`](./connectors/proboost/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`property-saas`](./connectors/property-saas/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`qc-manage`](./connectors/qc-manage/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`qcc-company`](./connectors/qcc-company/) | 通过企查查 qcc-company 统一入口查询企业基座、司法与经营风险、知识产权、经营动态、董监高及历史存档六模块数据；具体工具以宿主实际发现与账号权限为准。原工商能力包括股权… | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`qcc-legal`](./connectors/qcc-legal/) | 通过企查查·法律数据 Connector 检索、研究与核验中国法律法规和司法案例。当用户的请求涉及查找法条依据、定位法规、调取法规/法条逐字原文、类案检索、援引指导性/公报/典型… | 可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`qibook-mcp`](./connectors/qibook-mcp/) | 查询企业工商登记及相关尽调数据，涵盖主体识别、基本信息、股权与控制关系、变更、人员与组织、年报及上市信息。当用户提及企百科、qibook、工商查询、查企业、企业尽调、企业股东、企… | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`qince`](./connectors/qince/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`qingflow`](./connectors/qingflow/) | 轻流无代码平台操作技能 - 创建应用、管理表单数据、处理审批流程、查询和导出数据 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`qinghu-ai`](./connectors/qinghu-ai/) | 青虎AI电商 SaaS 连接器，覆盖电商数据研究、选品与运营分析，以及 LinkPix 商品图、详情页、广告素材和短视频创作。适用于数据查询、达人与短视频研究、选品调研、生图、生… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-04 |
| [`qisemierp`](./connectors/qisemierp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`qixinhuiyan-mcp`](./connectors/qixinhuiyan-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`qiyuan-robot-executor`](./connectors/qiyuan-robot-executor/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`QIYUAN_ROBOT_TOKEN` | 2026-10-04 |
| [`qq-mail`](./connectors/qq-mail/) | QQ邮箱(QQ Mail)全功能操作技能。触发场景：看邮箱、查邮件、收件箱、看看邮件、有没有新邮件、未读邮件、帮我看看邮箱、打开邮箱、最近的邮件、邮件列表、发邮件、写邮件、发一封… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`qveris`](./connectors/qveris/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`QVERIS_API_KEY` | 2026-10-04 |
| [`qzd-connector`](./connectors/qzd-connector/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-04 |
| [`rabbitvis`](./connectors/rabbitvis/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`realtrace`](./connectors/realtrace/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`REALTRACE_API_KEY` | 2026-10-04 |
| [`recording-assistant`](./connectors/recording-assistant/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`renzheai-connector`](./connectors/renzheai-connector/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`replygen`](./connectors/replygen/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`reportgem-research`](./connectors/reportgem-research/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`ruyi-creative-oauth`](./connectors/ruyi-creative-oauth/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`rys-business-assistant`](./connectors/rys-business-assistant/) | 使用融易算 MCP 工具选择绑定公司、生成样票并确认开票、查询出票状态与销项发票统计及开票记录，或查询账税月度汇总。用户请求这些业务或排查连接、登录及权限时使用。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`salesnail-instructor`](./connectors/salesnail-instructor/) | 为销售内训、销售年会、经销商大会和销售/售前/交付协同设计 AI 大客户销售沙盘，组织分组演练、讲师带教和课堂复盘；也支持明确的 SalesNail 讲师开通、Profile、客… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`salestouch`](./connectors/salestouch/) | 连接 SalesTouch：配置组织档案、单元、角色权限、员工。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`scienceora`](./connectors/scienceora/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`sdc-enterprise-info`](./connectors/sdc-enterprise-info/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`LITEMCP_API_KEY` | 2026-10-21 |
| [`securities-open-api`](./connectors/securities-open-api/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`seeyon-office-marketing-suite`](./connectors/seeyon-office-marketing-suite/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-08-14 |
| [`sellerspace-mcp`](./connectors/sellerspace-mcp/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`SELLERSPACE_API_KEY` | 2026-10-21 |
| [`sellfox-mcp`](./connectors/sellfox-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`SELLFOX_MCP_KEY` | 2026-10-21 |
| [`sensors-data-cli`](./connectors/sensors-data-cli/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`sesunfox-gateway`](./connectors/sesunfox-gateway/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`CLIENT_SECRET` | 2026-10-04 |
| [`sf-intra-city`](./connectors/sf-intra-city/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`shanglv-mcp-gateway`](./connectors/shanglv-mcp-gateway/) | 企业级 MCP 授权网关技能 - 聚合财务发票查询与银行账户交易数据（客户/账户/余额/交易/对账单/回单/小时余额），统一走 Keycloak OAuth 2.1 + PKCE… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-07 |
| [`shangyitong`](./connectors/shangyitong/) | VZOOM商易通-企业信息查询技能 - 工商信息、企业经营数据、财务指标、交易上下游、产业链画像、财务尽调、供应商筛查、供应链分析 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`shanjian-ai`](./connectors/shanjian-ai/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`shanlong-claw`](./connectors/shanlong-claw/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`sharecrm`](./connectors/sharecrm/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-08-15 |
| [`shopee-market-intelligence`](./connectors/shopee-market-intelligence/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ACCESS_TOKEN` | 2026-10-04 |
| [`shuidi-credit`](./connectors/shuidi-credit/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`shuidi-discovery`](./connectors/shuidi-discovery/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`shunong-assistant`](./connectors/shunong-assistant/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`sif-mcp`](./connectors/sif-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`sjb-mcp`](./connectors/sjb-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`slgj-finance-engine`](./connectors/slgj-finance-engine/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`SLGJ_TOKEN` | 2026-10-21 |
| [`smartsalary`](./connectors/smartsalary/) | 使用 SmartSalary Connector 查询和分析 HR、人力资源、招聘、人才市场、薪酬与人效数据。当用户需要数据回答招聘量、职位或人才结构、薪资工资、月薪年薪、薪酬区… | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`sparkx-ai-mcp`](./connectors/sparkx-ai-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`sq-company-dynamic`](./connectors/sq-company-dynamic/) | 上奇产业通MCP提供「产业—区域—企业」三维产业数据服务，支持产业链图谱与长短板诊断、区域产业全景与近三年迁移监测、企业工商/经营/融资/供应链/竞争/风险全息画像，以及招商推荐… | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-21 |
| [`starrocks-data-query`](./connectors/starrocks-data-query/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`APP_KEY` | 2026-10-21 |
| [`sugon-scinsight-agent`](./connectors/sugon-scinsight-agent/) | 科学文献洞察智能体，提供多数据库学术文献检索能力 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`sumscope-data`](./connectors/sumscope-data/) | 通过 Sumscope qeubee MCP 服务器查询金融数据（行情、债券、资金等）。当用户需要查询 qeubee 相关数据、了解可用的数据 API、或要求获取某类金融数据时使… | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`X_ACCESS_KEY` | 2026-10-04 |
| [`sungo-device-registry`](./connectors/sungo-device-registry/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`SUNGO_TIC_KEY` | 2026-10-04 |
| [`syspetro-service-22065846`](./connectors/syspetro-service-22065846/) | 通过 PROPDB（syspetro-service-22065846） 完整版 MCP 查询组分与物性、执行单位换算，并提交混合物分析、二元 Txy/Pxy、多元闪蒸、纯组分温… | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`SYSPETRO_MCP_API_KEY` | 2026-10-04 |
| [`tanyuan-assistant`](./connectors/tanyuan-assistant/) | 腾讯探元文博检索工具集（Agentic RAG · MCP 版）。通过 tanyuan-assistant MCP 工具提供三类检索能力，由 Agent 依据问题特征选择工具并构造 query： - search_re… | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tapd`](./connectors/tapd/) | TAPD 敏捷项目管理技能 - 管理需求、缺陷、任务、迭代、测试用例、Wiki、工时、评论和工作流 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`tapnow`](./connectors/tapnow/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tc-chengxin`](./connectors/tc-chengxin/) | 同程旅行官方旅游查询 Skill。用于机票、火车票、酒店、景区、汽车票、度假产品、行程规划、综合交通等实时查询，并提供 PC 预订入口、手机打开入口和微信扫码二维码。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`CHENGXIN_API_KEY` | 2026-10-04 |
| [`tcop-observability`](./connectors/tcop-observability/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tct-business-expert`](./connectors/tct-business-expert/) | NextB2B贸易通：用 MCP「tct-business-expert」查漏斗/趋势/团队榜/商机明细/客户资产并解读。 覆盖老板与业务员经营问答（T1–T6）。 鉴权：已配 Header/env 直接查；否则向用户… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tdengine`](./connectors/tdengine/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`TDENGINE_API_KEY` | 2026-10-04 |
| [`tdx-connector`](./connectors/tdx-connector/) | 通过通达信 MCP 查全球股票数据，支持选股与研报。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要环境变量：`TDX_API_KEY` | 2026-08-06 |
| [`teacher-assistant`](./connectors/teacher-assistant/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tec-do`](./connectors/tec-do/) | 指导 WorkBuddy 何时及如何使用 Tec-Do MCP 工具与本地技能蓝图。 | 可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`tedianren`](./connectors/tedianren/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`TEDIANREN_API_KEY` | 2026-10-21 |
| [`tencent-auto-overseas-unattended-oauth`](./connectors/tencent-auto-overseas-unattended-oauth/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`IATMARK_API_KEY` | 2026-10-21 |
| [`tencent-dlc`](./connectors/tencent-dlc/) | 通过 MCP 工具操作腾讯云数据湖计算 DLC。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tencent-docs`](./connectors/tencent-docs/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`tencent-docs-oa`](./connectors/tencent-docs-oa/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`tencent-health-nges`](./connectors/tencent-health-nges/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tencent-map`](./connectors/tencent-map/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`TENCENT_MAP_KEY` | 2026-10-21 |
| [`tencent-map-guide`](./connectors/tencent-map-guide/) | 腾讯地图·指南制作技能 —— 用自然语言创建、查询、更新、删除行程指南，并将 AI 生成的攻略内容保存同步到用户的地图指南 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tencent-marketing-solution`](./connectors/tencent-marketing-solution/) | 连接腾讯营销系统与数据，支持账户管理、创意灵感推荐、投放优化与审核诊断等智能操作，助力广告投放全链路提效。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tencent-news`](./connectors/tencent-news/) | 腾讯新闻 Connector 技能 - 查询新闻、查询用户在腾讯新闻的资产（收藏/点赞/用户信息）、获取用户 API Key | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tencent-qidian-cs`](./connectors/tencent-qidian-cs/) | 腾讯企点客服（Tencent-Qidian-CS）Connector 的底层调用说明书。覆盖五大能力域——工单管理（新建/修改/查询工单，变更工单状态）、坐席查询（客服状态实时监… | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tencent-survey`](./connectors/tencent-survey/) | 腾讯问卷（wj.qq.com）MCP Skill。涉及「问卷」「调查」「表单」「投票」「考试」「测评」「wj.qq.com」等操作时使用。支持能力：(1) 获取问卷详情（标题、设… | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`tencent-tchouse-c`](./connectors/tencent-tchouse-c/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tencent-weiyun`](./connectors/tencent-weiyun/) | 微云网盘 MCP 接口完整技能。包含 weiyun.list、weiyun.list_by_category、weiyun.download、weiyun.delete、weiy… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`WEIYUN_MCP_TOKEN` | 2026-07-21 |
| [`tencent-yaoxiang-bi`](./connectors/tencent-yaoxiang-bi/) | 「腾讯健康药箱 × 药企」数据洞察 skill（两个层面九大维度 · 三种模式）。承接用户给定的药品名称与时间范围，数据统一从药箱数据平台实时拉取，按「整体市场规模和药箱用户分析… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tencentads`](./connectors/tencentads/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-08-06 |
| [`tendex-mcp-lkfcxt-6myw`](./connectors/tendex-mcp-lkfcxt-6myw/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`textin-xparse`](./connectors/textin-xparse/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`tfc-taikang-insurance`](./connectors/tfc-taikang-insurance/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`thinkingai-agentic-engine`](./connectors/thinkingai-agentic-engine/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-09 |
| [`tiana-cloud`](./connectors/tiana-cloud/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`tiktok`](./connectors/tiktok/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`timem-space`](./connectors/timem-space/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-04 |
| [`tm-bmis`](./connectors/tm-bmis/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tme-youshu-prd`](./connectors/tme-youshu-prd/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tmeet`](./connectors/tmeet/) | 腾讯会议 CLI（tmeet）：OAuth 授权登录/登出/状态查询、会议管理（创建/更新/取消/查询/受邀者）、录制管理（列表/播放地址/智能纪要/转写/录制权限申请）、会议报… | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`today-watermark-camera`](./connectors/today-watermark-camera/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`tongzhou-fin-research`](./connectors/tongzhou-fin-research/) | 连接公开行情、研报检索、行业图谱与同舟投研材料，为股市研究提供可复核证据。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-08 |
| [`tplus-api`](./connectors/tplus-api/) | 畅捷通 T+Cloud MCP 使用指导 - 查询/管理销售订单、采购订单、库存单据、生产工单、财务凭证、报表及基础档案。使用 T+ MCP 前请先阅读此技能。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`transmind`](./connectors/transmind/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tripo-3d`](./connectors/tripo-3d/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`tuniu-travel`](./connectors/tuniu-travel/) | 途牛旅行统一助手（推荐优先使用）- 通过 tuniu CLI 统一调用国内/国际机票、酒店、门票、火车票、邮轮、度假产品、打包订等旅行服务。适用于用户询问国内和国际航班、酒店、景… | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`TUNIU_API_KEY` | 2026-10-04 |
| [`tushare`](./connectors/tushare/) | Tushare数据操作技能 - 查询资讯数据，包括 A股、指数、ETF/基金、财务、估值、资金流、公告新闻、板块概念与宏观数据. | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`TUSHARE_TOKEN` | 2026-10-04 |
| [`tuwen-creator`](./connectors/tuwen-creator/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`TUWEN_API_KEY` | 2026-10-21 |
| [`tyc-mcp`](./connectors/tyc-mcp/) | 天眼查企业数据查询技能 - 聚合式企业数据网关，覆盖企业锚定、基础画像、股权集团、董监高人员、司法风险、知识产权、经营财务、招投标等 160+ 项企业数据能力。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`uptgai-manager`](./connectors/uptgai-manager/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要环境变量：`SERVICE_TOKEN` | 2026-10-04 |
| [`uupt`](./connectors/uupt/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`variflight-mcp`](./connectors/variflight-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`VARIFLIGHT_MCP_KEY` | 2026-10-04 |
| [`verya-knowledgebase`](./connectors/verya-knowledgebase/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`viaim`](./connectors/viaim/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`vibeknow-cli`](./connectors/vibeknow-cli/) | VibeKnow 官方视频生成 Skill（vibeknow / vk 命令行）。当用户想把文档、PDF、Word、PPT、网页链接或对话里贴的一段文字做成视频时使用——讲解视频… | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`voc-mcp-oauth-v2`](./connectors/voc-mcp-oauth-v2/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`voko-guest`](./connectors/voko-guest/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`vox-teacher`](./connectors/vox-teacher/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`wandox`](./connectors/wandox/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`WANDOX_TOKEN` | 2026-10-21 |
| [`wanfang-literature-search-download-oauth`](./connectors/wanfang-literature-search-download-oauth/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`wangke-martech`](./connectors/wangke-martech/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`wavenote-audio`](./connectors/wavenote-audio/) | WaveNote 音频技能 - 查询录音、转写和总结，并在用户确认后发起转写任务 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`weaver-eteams-connector`](./connectors/weaver-eteams-connector/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`wecom`](./connectors/wecom/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-21 |
| [`weiban-agent-mcp`](./connectors/weiban-agent-mcp/) | 使用微伴连接器查询授权范围内的员工、客户、企微消息存档和工单，并处理微伴连接与参数错误；写入前确认业务对象与用户授权。 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`WEIBAN_AGENT_SECRET` | 2026-10-04 |
| [`weibo-cli`](./connectors/weibo-cli/) | 通过 weibo-cli 命令行或微博 MCP 连接器查询和发布微博、管理评论与文章、分析用户和粉丝数据、检索热搜与影视指数。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`WEIBO_CLI_REFRESH_TOKEN`、`WEIBO_CLI_TOKEN` | 2026-10-21 |
| [`weisheng-scrm`](./connectors/weisheng-scrm/) | 当用户需要查询或管理微盛企微管家（企业微信） SCRM 中的客户信息、客户标签、客户群、营销素材、活码、群发、跟进记录、聊天记录、会话存档、联系人、商机、汇报、抽奖、客户日程、客… | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`SCRM_APP_KEY` | 2026-10-21 |
| [`welife-ai-workbench-connector`](./connectors/welife-ai-workbench-connector/) | 查询当前授权餐饮商户的经营指标、经营报告、经营诊断与营销活动事实数据 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`wenear-scrm`](./connectors/wenear-scrm/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`SCRM_TOKEN` | 2026-10-21 |
| [`westock-mcp`](./connectors/westock-mcp/) | 提供实时行情，支持条件选股、自选管理、股价提醒与模拟交易 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`wimo-gen`](./connectors/wimo-gen/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`wind-finance`](./connectors/wind-finance/) | 通过自然语言查询股票、基金、指数、债券、公告、财经新闻和宏观经济数据。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`wisenote`](./connectors/wisenote/) | 使用百智 WiseNote 会议工具读取已授权的会议列表、会议摘要和会议转写内容。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`wk-workbuddy`](./connectors/wk-workbuddy/) | 用途：name: wk-mcp | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`wm-weight-manage`](./connectors/wm-weight-manage/) | 在 WorkBuddy 中安装/配置成人减重管理 MCP。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`workrally1`](./connectors/workrally1/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`woscli`](./connectors/woscli/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`wpe-general-connector`](./connectors/wpe-general-connector/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`wps-knowledgebase`](./connectors/wps-knowledgebase/) | WPS/zhishi（WPS知识库）云端知识库：列表/详情、文件树、智能问答（ask SSE）、分享链接、创建关闭与文件 CRUD、导入上传与格式转换（OTL 下载限制见正文）。 当用户用中文只说「知识库」「我的知识库… | 需要登录 / OAuth / 扫码授权 | 2026-08-06 |
| [`wscnmcp-token`](./connectors/wscnmcp-token/) | 华尔街见闻资讯相关产品工具说明 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`WSCN_API_KEY` | 2026-10-04 |
| [`xhcj-mcp-announcements-news-policy`](./connectors/xhcj-mcp-announcements-news-policy/) | 新华财经公告、新闻、政策数据 MCP 技能。提供股票资讯、板块资讯、热点新闻、资讯搜索、大宗快讯、外汇快讯、股票快讯、上市公司公告关键词检索、政策向量检索等 9 个数据查询工具。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`XHCJ_API_KEY` | 2026-10-04 |
| [`xiaoe-cloud-cli`](./connectors/xiaoe-cloud-cli/) | 小鹅通：使用当前登录账号和店铺上下文管理课程、内容资产、章节、直播、订单和素材。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-06 |
| [`xiaoliebian-scrm`](./connectors/xiaoliebian-scrm/) | 连接器配置与技能 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`xiaolv-law-search`](./connectors/xiaolv-law-search/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`xiehui-fr`](./connectors/xiehui-fr/) | 通过 xiehui-fr MCP 查询法国官方华社登记册（RNA）。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`xingtu-claw-risk`](./connectors/xingtu-claw-risk/) | 星图Claw 企业风险分析技能 - 行业识别、企业间关联方关系分析 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-07 |
| [`xinke-laile-analytics-enterprise`](./connectors/xinke-laile-analytics-enterprise/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`XIANSUO_MCP_TOKEN` | 2026-10-21 |
| [`xkw`](./connectors/xkw/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`xmed-figure-mcp`](./connectors/xmed-figure-mcp/) | 通过 X-Med MCP 生成科研图表：火山图、PCA、富集、生存分析等。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`xmind`](./connectors/xmind/) | 使用 Xmind 官方 MCP 管理团队空间，并创建、读取、编辑和完善 Xmind 在线思维导图。当用户要求查找在线导图、整理内容为导图、调整主题结构与样式、管理画布、文件夹或任… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`xrxs`](./connectors/xrxs/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`xuan-gu-mo-fang`](./connectors/xuan-gu-mo-fang/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`xuanpian-schedule`](./connectors/xuanpian-schedule/) | 你已连接影楼选片系统，可以帮用户查询拍摄档期，以及完成账号绑定。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`WB_TOKEN`、`WORKBUDDY_API_KEY` | 2026-10-04 |
| [`yanxu`](./connectors/yanxu/) | 通过言序 MCP 完成微信公众号文章的建稿与发布。适用于查询已绑定的公众号、查询样式主题、创建文章草稿、推送到公众号草稿箱。触发场景：用户提到公众号文章、排版、建稿、草稿箱、言序。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`ydw-buddymcp`](./connectors/ydw-buddymcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`yichayun-trade-data`](./connectors/yichayun-trade-data/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`yihook`](./connectors/yihook/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`yiketu-ai`](./connectors/yiketu-ai/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`API_KEY` | 2026-10-21 |
| [`yingmi-mcp`](./connectors/yingmi-mcp/) | 盈米基金金融工具使用技能，支持基金与市场数据查询、投研分析、组合诊断、财富规划和金融内容生成 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`yiqi-query`](./connectors/yiqi-query/) | 易奇命理查询技能 - 八字命盘梳理、日运、月运、黄历宜忌 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`yixiaoke`](./connectors/yixiaoke/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`yiya-dental`](./connectors/yiya-dental/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`youshu-bd-mate`](./connectors/youshu-bd-mate/) | 对公营销助手是基于企业全维数据构建的对公营销智能助手，提供从生成访前一页纸、访前客情报告、产品找客、关键人画像、营销话术及按企荐品的完整展业闭环能力。所有报告生成工具为异步模式，… | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`youzan-workbuddy`](./connectors/youzan-workbuddy/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要环境变量：`SERVICE_TOKEN` | 2026-10-21 |
| [`yuanbei-hub`](./connectors/yuanbei-hub/) | 连接器配置与技能 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`YUANBEI_ACCESS_TOKEN`、`YUANBEI_LOGIN_TOKEN` | 2026-10-04 |
| [`yuandian-mcp`](./connectors/yuandian-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`yuanjie-bfp`](./connectors/yuanjie-bfp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`yunjing-crm-analytics`](./connectors/yunjing-crm-analytics/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`CRM_API_KEY` | 2026-10-04 |
| [`yunke-cli`](./connectors/yunke-cli/) | 通过 yunke 操作云客 CRM：组织架构查询、员工/客户/通话数据统计、AI 智能分析。登录由 WorkBuddy 连接器经 OAuth 自动完成，使用前需确保 yunke … | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`yuntu-ft-workbench`](./connectors/yuntu-ft-workbench/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`yunzhi-campus`](./connectors/yunzhi-campus/) | 查询已登录园所教师本人的请假记录与可用请假流程。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`yunzhi-mcp`](./connectors/yunzhi-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`MCP_TOKEN` | 2026-10-04 |
| [`yzf-general-mcp-server`](./connectors/yzf-general-mcp-server/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`zenava`](./connectors/zenava/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-09 |
| [`zerone-mcp`](./connectors/zerone-mcp/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ZERONE_API_KEY` | 2026-10-21 |
| [`zfs-fssc-ai`](./connectors/zfs-fssc-ai/) | 中兴 FSSC 的 AI 报销助手。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ZFS_LOGIN_KEY`、`ZFS_PASSWORD` | 2026-08-06 |
| [`zhangsanfeng`](./connectors/zhangsanfeng/) | 账三丰 连接器技能 - 财务/进销存/MES 数据查询与文字录入 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`zhaopin-qiye-connector`](./connectors/zhaopin-qiye-connector/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`zhenghe-data-tk-assistant`](./connectors/zhenghe-data-tk-assistant/) | 郑和数据是面向 TikTok Shop 跨境从业者的选品与数据分析工具，覆盖23国站点。配合郑和的实时数据，支持商品、行业、达人、视频、直播间与店铺的多维查询，围绕三类核心场景输… | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`MCP_KEY` | 2026-10-04 |
| [`zhihuishu-unified`](./connectors/zhihuishu-unified/) | 智慧树教学中心，聚合课程、学期、班级、教学观测、学习分析、课堂报告、分组方案、OBE、备课、题目题库、资源检索、教学计划与团队、话题通知、能力阶梯、知识图谱、AI 翻转课堂与知识… | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`zhiping-wealth`](./connectors/zhiping-wealth/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`zhitu-knowledge`](./connectors/zhitu-knowledge/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`ZHITU_BOT_TOKEN` | 2026-10-21 |
| [`zocf-ai-tools`](./connectors/zocf-ai-tools/) | 连接器配置与技能 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`AITOOLS_API_KEY` | 2026-10-21 |
| [`zspace-nas`](./connectors/zspace-nas/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |
| [`zsxq`](./connectors/zsxq/) | 连接器配置与技能 | 需要在 App 内完成 OAuth / 扫码或配置 Token | 2026-10-04 |
| [`zw3d-mcp`](./connectors/zw3d-mcp/) | ZW3D 三维建模技能 — 草图绘制、实体拉伸/旋转/扫掠/放样、工程特征、装配约束、钣金、外观材质、几何查询、安装目录发现与部署兜底 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`zwcad-mcp`](./connectors/zwcad-mcp/) | ZWCAD 2D 平台与中望机械 — 绘制、查询、标注、块/图层/样式管理、图框/标题栏/BOM/球标等机械能力 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`zxt-openapi-platform`](./connectors/zxt-openapi-platform/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器；需要按 token-schema 配置凭证；需要环境变量：`JXP_OPEN_KEY` | 2026-10-04 |
| [`zxygj-business-data`](./connectors/zxygj-business-data/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`zywl-audio-mcp`](./connectors/zywl-audio-mcp/) | 连接器配置与技能 | 可能需要启用对应 MCP / 连接器 | 2026-10-21 |

## 3. 专家包 `experts/`

### 产品设计（19）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`adort-design-expert`](./experts/adort-design-expert/) | [Ardot 设计专家](./experts/adort-design-expert/) | 精通 Ardot 设计软件，既能在画布上构建精准 UI，也能将设计稿直接生成前端代码 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`ai-image-prompt-engineer`](./experts/ai-image-prompt-engineer/) | [AI图像提示词工程师](./experts/ai-image-prompt-engineer/) | 精通AI图像生成的语言密码，将抽象视觉概念转化为精准提示词 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`behavioral-nudge-engine`](./experts/behavioral-nudge-engine/) | [行为助推引擎](./experts/behavioral-nudge-engine/) | 运用行为经济学设计产品助推机制，引导用户做出更好的决策 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`delightful-experience-designer`](./experts/delightful-experience-designer/) | [趣味体验设计师](./experts/delightful-experience-designer/) | 专注于在品牌体验中注入意想不到的愉悦时刻 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`design-engine`](./experts/design-engine/) | [设计原型专家团](./experts/design-engine/) | 6 角色 AI 设计团队，覆盖从需求发现到品牌级原型交付的完整工作流，内置 71 套设计系统 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`design-md-architect`](./experts/design-md-architect/) | [设计系统架构师](./experts/design-md-architect/) | 基于58个品牌参考库，生成设计系统规范文档并直接输出高质量HTML/CSS页面与UI组件代码 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-08-13 |
| [`design-prototype-expert`](./experts/design-prototype-expert/) | [设计工作室主理人](./experts/design-prototype-expert/) | 设计系统驱动的高保真原型专家。先建规范再出页面，提供多方向选择，交付前做AI味检测。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`design-to-code`](./experts/design-to-code/) | [设计转代码专家](./experts/design-to-code/) | 将 Figma 设计稿和截图转换为可直接使用的代码组件，内置无障碍性支持 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`diversity-visual-expert`](./experts/diversity-visual-expert/) | [多元视觉专家](./experts/diversity-visual-expert/) | 致力于消除AI图像中的系统性偏见，确保视觉内容文化准确和包容 | 无 | 2026-08-13 |
| [`feedback-synthesis-analyst`](./experts/feedback-synthesis-analyst/) | [反馈综合分析师](./experts/feedback-synthesis-analyst/) | 从海量用户反馈中提炼有价值洞察，将用户声音转化为改进方向 | 需要微信/企微相关凭证或扫码登录 | 2026-08-04 |
| [`mermaid-diagram-expert`](./experts/mermaid-diagram-expert/) | [图表设计与渲染专家](./experts/mermaid-diagram-expert/) | 将自然语言转化为专业级Mermaid图表，支持6种图表类型、15种主题配色，秒级渲染出版级SVG与ASCII可视化 | 需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`ngo-challenge-advisor`](./experts/ngo-challenge-advisor/) | [NGO 共創卡設計助手](./experts/ngo-challenge-advisor/) | 通過點擊式訪談梳理 NGO 真實工作痛點，生成清晰可執行的共創卡，並在發佈前完成適配、邊界與質量檢查。 | 无（可选 API/账号以增强能力） | 2026-10-04 |
| [`product-management`](./experts/product-management/) | [产品管理专家](./experts/product-management/) | 产品管理工具集：功能规格编写、路线图规划、利益相关者沟通、用户研究综合、竞品分析和指标追踪 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`product-strategy-team`](./experts/product-strategy-team/) | [产品战略团队](./experts/product-strategy-team/) | 由产品总监领导的 5 人产品专家团队：需求分析师（PRD/功能规格书）、用户研究员（调研综合分析）、竞品分析师（竞争情报）、数据分析师（指标追踪）和路线图规划师（路线图管理/迭代… | 无 | 2026-07-22 |
| [`sprint-priority-manager`](./experts/sprint-priority-manager/) | [迭代优先级管理者](./experts/sprint-priority-manager/) | 在有限迭代周期内做出最优优先级决策，确保Sprint交付最大价值 | 无 | 2026-08-13 |
| [`ui-designer`](./experts/ui-designer/) | [UI设计师](./experts/ui-designer/) | 精通设计系统和组件库，追求像素级完美，打造无障碍用户界面 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY` | 2026-08-13 |
| [`user-experience-architect`](./experts/user-experience-architect/) | [用户体验架构师](./experts/user-experience-architect/) | 为开发者提供坚实的技术基础和CSS系统，是设计与开发之间的桥梁 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY` | 2026-08-13 |
| [`user-experience-researcher`](./experts/user-experience-researcher/) | [用户体验研究员](./experts/user-experience-researcher/) | 用真实数据而非假设验证设计决策，专精用户行为分析和可用性测试 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY` | 2026-08-13 |
| [`visual-storytelling-expert`](./experts/visual-storytelling-expert/) | [视觉叙事专家](./experts/visual-storytelling-expert/) | 擅长将复杂信息转化为引人入胜的视觉故事 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-08-13 |

### 全球发展（21）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`brazil-company-query`](./experts/brazil-company-query/) | [巴西商务拓展专家](./experts/brazil-company-query/) | 排查巴西企业工商与信用风险，尽调专利商标知识产权，分析市场拓展路径，降低商务拓展风险。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`brazil-legal`](./experts/brazil-legal/) | [巴西法务合规专家](./experts/brazil-legal/) | 巴西公司注册、合同审查、知识产权、产品准入、劳动用工、数据合规及争议解决，助力企业合规出海巴西。 | 无 | 2026-07-23 |
| [`brazil-rfb-expert`](./experts/brazil-rfb-expert/) | [巴西财税金融专家](./experts/brazil-rfb-expert/) | 服务企业出海巴西的财税全周期：本地补贴、税制设计、跨境资金规划与日常合规，内置完整财税政策。 | 无 | 2026-07-23 |
| [`egypt-marketing`](./experts/egypt-marketing/) | [埃及市场营销专家](./experts/egypt-marketing/) | 中国企业出海埃及的CMO级营销引擎，覆盖数字生态、斋月营销、品牌本地化、消费者洞察与ROI预估全链路 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`egypt-public-affairs`](./experts/egypt-public-affairs/) | [埃及公共事务专家](./experts/egypt-public-affairs/) | 精通埃及政府关系、政策解读、监管沟通、行业协会、危机公关和舆情管理，服务企业一站式公共事务咨询。 | 需要登录 / OAuth / 扫码授权 | 2026-07-23 |
| [`egypt-strategic-advisory`](./experts/egypt-strategic-advisory/) | [埃及战略顾问](./experts/egypt-strategic-advisory/) | 精通埃及宏观环境、产业趋势、竞争格局和风险管控，提供投资选址、进入模式和长期布局决策建议。 | 无 | 2026-07-22 |
| [`indonesia-bd-expert`](./experts/indonesia-bd-expert/) | [印尼商务拓展专家](./experts/indonesia-bd-expert/) | 整合全链路客供与渠道资源，洞察园区展会招商契机，锚定市场进入路径，打造产业合作生态与合规风控护航。 | 无 | 2026-07-23 |
| [`indonesia-digital-law-expert`](./experts/indonesia-digital-law-expert/) | [印尼法务合规专家](./experts/indonesia-digital-law-expert/) | 聚焦外商投资、数据合规与商业交易，打通营商审批、金融监管与知识产权保护链路，赋能跨境SaaS与AI等新兴赛道全流程印尼法务保障。 | 可能需要启用对应 MCP / 连接器 | 2026-07-23 |
| [`indonesia-pa-expert`](./experts/indonesia-pa-expert/) | [印尼公共事务专家](./experts/indonesia-pa-expert/) | 剖析印尼政商生态与合规风险，整合政策解读危机公关，融合本土宗教文化，输出落地GR策略。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`malaysia-finance-tax`](./experts/malaysia-finance-tax/) | [马来西亚财税金融专家](./experts/malaysia-finance-tax/) | 精通马来西亚税务、银行、外汇、审计、补贴、保险、伊斯兰金融及财政分析的财税金融全栈专家。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`malaysia-hr-admin`](./experts/malaysia-hr-admin/) | [马来西亚人力行政专家](./experts/malaysia-hr-admin/) | 精通马来西亚招聘、劳动合同、薪酬福利、签证工签与社保，服务企业跨境人力行政咨询。 | 无 | 2026-07-23 |
| [`malaysia-legal`](./experts/malaysia-legal/) | [马来西亚法务合规专家](./experts/malaysia-legal/) | 精通马来西亚公司注册、合同、知识产权、行业准入与数据合规，服务跨境法务合规咨询。 | 无（可选 API/账号以增强能力） | 2026-07-23 |
| [`malaysia-marketing`](./experts/malaysia-marketing/) | [马来西亚市场营销专家](./experts/malaysia-marketing/) | 深谙马来西亚文化与宗教，覆盖消费者画像、品牌本地化、社媒投放与用户增长，生成营销海报与短视频。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-23 |
| [`sg-biz-dev`](./experts/sg-biz-dev/) | [新加坡商务拓展专家](./experts/sg-biz-dev/) | 帮助企业在新加坡发现客户、伙伴、渠道、供应商与代理商，对接园区、展会、招商及确认市场进入路径 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`sg-finance-tax`](./experts/sg-finance-tax/) | [新加坡财税金融专家](./experts/sg-finance-tax/) | 精通企业在新加坡经营中的税务、会计、银行、融资、外汇、支付、审计、补贴、保险和财务规划等内容 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-23 |
| [`sg-hr-admin-expert`](./experts/sg-hr-admin-expert/) | [新加坡人力行政专家](./experts/sg-hr-admin-expert/) | 精通新加坡当地招聘、劳动合同、薪酬福利、签证工签、社保、办公场地、行政流程和员工管理等内容。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-23 |
| [`thai-marketing-creative`](./experts/thai-marketing-creative/) | [泰国市场营销专家](./experts/thai-marketing-creative/) | 整合全链路用户洞察与行为决策，锚定本土松弛悦己情绪切口，打通泰语市场转化路径，输出泰国市场营销方案。 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`thailand-hr-admin`](./experts/thailand-hr-admin/) | [泰国人力行政专家](./experts/thailand-hr-admin/) | 精通泰国劳动法(LPA)、外籍员工工签合规、薪酬福利设计与本土职场文化适配，护航中资企业出海泰国全周期人力行政 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`uae-marketing-advisor`](./experts/uae-marketing-advisor/) | [阿联酋市场营销专家](./experts/uae-marketing-advisor/) | 覆盖阿联酋不同地区差异化营销。覆盖消费者画像、品牌本土化、渠道策略与用户增长，生成营销海报视频。 | 需要环境变量：`COS_SECRET_KEY` | 2026-07-23 |
| [`uae-public-affairs`](./experts/uae-public-affairs/) | [公共事务顾问](./experts/uae-public-affairs/) | 专注阿联酋政府关系、政策解读与监管沟通，为中企及投资机构提供专业公共事务咨询与风险评估服务。 | 无（可选 API/账号以增强能力） | 2026-07-23 |
| [`uae-strategic-advisor`](./experts/uae-strategic-advisor/) | [阿联酋战略顾问](./experts/uae-strategic-advisor/) | 研判阿联酋七酋长国宏观环境与产业趋势，对比竞合格局与投资选址，评估进入模式与风险，输出出海战略建议 | 无 | 2026-07-22 |

### 内容创作（47）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`ai-content-creator-team`](./experts/ai-content-creator-team/) | [内容创作专家团](./experts/ai-content-creator-team/) | AI驱动的多模态内容生产团队，从创意策划到成品交付全覆盖，涵盖品牌定位、情绪板、广告方向、文案创作、视频生成、图片设计、精修合成和素材改编。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`ai-humanizer`](./experts/ai-humanizer/) | [AI痕迹消除专家](./experts/ai-humanizer/) | 识别24种AI写作模式与500+词汇，统计突发性与多样性，重写为自然真实的人类表达，彻底消除机器味。 | 无 | 2026-07-21 |
| [`ai-shifu`](./experts/ai-shifu/) | [AI师傅课程制作专家](./experts/ai-shifu/) | 基于你的教学需求和原始内容(PPT、Word、PDF、txt等)，帮你快速做门AI一对一互动课 | 需要登录 / OAuth / 扫码授权 | 2026-08-06 |
| [`ai-shifu-expert`](./experts/ai-shifu-expert/) | [AI师傅课程制作专家](./experts/ai-shifu-expert/) | 基于你的教学需求和原始内容(PPT、Word、PDF、txt等)，帮你快速做门AI一对一互动课 | 需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`ai-video-script`](./experts/ai-video-script/) | [AI视频脚本创作专家](./experts/ai-video-script/) | 依据主题或关键词生成完整视频脚本，涵盖分镜表、画面提示词、配音文案与字幕，适配主流AI生成工具及抖音、B站平台。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`bilibili-content-strategist`](./experts/bilibili-content-strategist/) | [B站内容策略师](./experts/bilibili-content-strategist/) | 精通B站平台生态和年轻用户偏好，打造高播放量视频策略 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`book-co-creator`](./experts/book-co-creator/) | [图书联合创作者](./experts/book-co-creator/) | 与作者深度协作，帮助规划书籍结构和内容，达到出版级品质 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`chatcut-video-editor`](./experts/chatcut-video-editor/) | [ChatCut 视频剪辑师](./experts/chatcut-video-editor/) | AI 视频剪辑与素材生成：剪辑、字幕、转场、特效，并生成视频/图片/音乐/配音，保持可手动编辑的多轨时间线，支持导出 Pr / DaVinci 工程文件。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`content-creation-expert-prod`](./experts/content-creation-expert-prod/) | [汽车行业内容创作专家团](./experts/content-creation-expert-prod/) | 汽车行业垂类图文创作团队，5 人协作完成选题、撰写、智能配图与质检，一键交付懂车帝、小红书等风格图文 | 可能需要启用对应 MCP / 连接器；需要环境变量：`COS_SECRET_KEY` | 2026-07-22 |
| [`content-creator`](./experts/content-creator/) | [内容创作专家](./experts/content-creator/) | 擅长创作引人入胜的多平台内容，让品牌故事触达目标受众 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`content-distribution-team`](./experts/content-distribution-team/) | [全域内容分发专家团](./experts/content-distribution-team/) | 一站式多平台内容分发方案，覆盖13+全球社交媒体平台（含微信视频号），提供发布规则适配、排期管理、批量发布编排、跨平台数据分析和小红书自动化发布能力 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`LIBTV_ACCESS_KEY`、`TOKEN`、`WECHAT_AUTHOR`、`WECHAT_SECRET` | 2026-08-13 |
| [`content-writer`](./experts/content-writer/) | [自媒体内容写作专家](./experts/content-writer/) | 专注为小红书、知乎、公众号、抖音生成平台原生的可发布内容，含标题钩子、正文结构与转化引导，匹配各平台字数规范。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`douyin-strategist`](./experts/douyin-strategist/) | [抖音策略师](./experts/douyin-strategist/) | 精通抖音算法和内容生态，打造短视频爆款并实现商业化变现 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`fbsir-mom-dialogue-expert`](./experts/fbsir-mom-dialogue-expert/) | [妈妈问答](./experts/fbsir-mom-dialogue-expert/) | 整理与妈妈有关的照片、视频、录音、手稿和家庭资料，生成可追溯的故事卡、生活轨迹、追问与书稿。 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`frontend-slides`](./experts/frontend-slides/) | [HTML幻灯片制作专家](./experts/frontend-slides/) | 零依赖打造动画丰富的网页演示文稿，支持从零创建、PPTX转换与幻灯片增强，提供风格预览、在线部署与PDF导出。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`humanize-ppt-team`](./experts/humanize-ppt-team/) | [卡尔的人感PPT专家团](./experts/humanize-ppt-team/) | 把原始资料梳理成人感PPT大纲，调度HTML生成、演讲模式、视频动效与交付质检，形成可演示成果。 | 需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`instagram-operations-expert`](./experts/instagram-operations-expert/) | [Instagram运营专家](./experts/instagram-operations-expert/) | 精通Instagram视觉美学和内容策略，打造令人向往的品牌形象 | 需要 GitHub Token 或 `gh auth login` | 2026-08-13 |
| [`kdocs-doc-butler`](./experts/kdocs-doc-butler/) | [文档管家](./experts/kdocs-doc-butler/) | 金山文档出品，覆盖新建搜索、分类整理与分享权限管理，助力文档全生命周期一站搞定。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`kdocs-knowledge-collector`](./experts/kdocs-knowledge-collector/) | [知识收藏专家](./experts/kdocs-knowledge-collector/) | 金山文档出品，支持网页剪藏、碎片笔记整理与多文档智能摘要，帮你沉淀云端知识资产。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`kdocs-pdf-toolbox`](./experts/kdocs-pdf-toolbox/) | [PDF 处理专家](./experts/kdocs-pdf-toolbox/) | 金山文档出品，支持PDF按页拆分合并、格式转换与全文翻译，覆盖常见文档处理场景。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`kdocs-ppt-creator`](./experts/kdocs-ppt-creator/) | [PPT 创作专家](./experts/kdocs-ppt-creator/) | 金山文档出品，一句话或参考文档即可生成完整PPT，自动完成大纲排版与场景配色方案。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`kidd-content-expert`](./experts/kidd-content-expert/) | [知识视频创作专家](./experts/kidd-content-expert/) | 基于深度研究报告，用基德风格创作口语化、反常识的知识视频脚本，覆盖时政财经、宇宙科普与科技前沿。 | 无 | 2026-07-22 |
| [`kuaishou-strategist`](./experts/kuaishou-strategist/) | [快手策略师](./experts/kuaishou-strategist/) | 深谙快手下沉市场特性和老铁文化，打造接地气的内容策略 | 无 | 2026-08-13 |
| [`long-manuscript-expert`](./experts/long-manuscript-expert/) | [长文档写作与改稿专家](./experts/long-manuscript-expert/) | 把提纲、访谈、旧稿和零散素材整理成结构清晰的长文档，支持章节续写、限定范围改稿与成稿交付前检查。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`news-briefing-expert`](./experts/news-briefing-expert/) | [私人新闻主编](./experts/news-briefing-expert/) | 私人新闻主编，覆盖AI财经科技社会国际全领域，多源交叉验证后产出结构化简报，星级标重要度，可溯源。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-07-31 |
| [`news-buddy`](./experts/news-buddy/) | [资讯顾问](./experts/news-buddy/) | 懂你的资讯顾问。基于隐式画像精选新闻，告诉你每条跟你有什么关系、你能做什么，让信息真正为你所用。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`novel-creator`](./experts/novel-creator/) | [世界观架构师 / 连续性编辑](./experts/novel-creator/) | 长篇创作搭子，善用叙事结构搭骨架、三维理论塑角色，靠追踪系统防矛盾，去AI感规则让正文更像真人手笔。 | 无 | 2026-07-31 |
| [`novel-generator`](./experts/novel-generator/) | [爽文小说生成专家](./experts/novel-generator/) | 把一句话灵感扩写成完整提示词与大纲，逐章生成连贯爽文，维护角色、地点、情节一致，支持修仙、重生、都市等题材。 | 无 | 2026-07-22 |
| [`podcast-strategist`](./experts/podcast-strategist/) | [播客策略师](./experts/podcast-strategist/) | 精通播客内容策划和增长策略，通过音频建立深度用户连接 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`ppt-creation-expert`](./experts/ppt-creation-expert/) | [腾讯云PPT制作专家](./experts/ppt-creation-expert/) | 基于腾讯云知（乐享）平台，整合通用汇报、面客方案、高拜材料与演讲讲稿生成的 PPT 制作专家 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器；需要环境变量：`LEXIANG_TOKEN` | 2026-10-04 |
| [`promo-creator-team`](./experts/promo-creator-team/) | [宣传片创作团队](./experts/promo-creator-team/) | 6位专业角色分6阶段协作完成产品宣传片全流程制作：创意简报、逐镜头分镜、素材生产、HyperFrames剪辑合成、BGM设计与交付，从产品URL到可发布的60-90秒宣传片MP4 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`MUREKA_API_KEY` | 2026-07-21 |
| [`remotion-video-generator`](./experts/remotion-video-generator/) | [视频生成专家](./experts/remotion-video-generator/) | 基于 Remotion 的视频生成专家，创建产品演示、解说视频、社交媒体内容和演示文稿 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`short-video-editing-coach`](./experts/short-video-editing-coach/) | [短视频剪辑教练](./experts/short-video-editing-coach/) | 精通短视频剪辑技巧和节奏把控，让每条视频具有专业冲击力 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`tietu-toutiao`](./experts/tietu-toutiao/) | [媒体头图编辑](./experts/tietu-toutiao/) | 把单版或多版报纸转成手机头图：条目化综合选题、结构化编辑决策、自审门禁、四模板确定性渲染与版本回退。 | 需要微信/企微相关凭证或扫码登录 | 2026-10-04 |
| [`tik-tok-strategist`](./experts/tik-tok-strategist/) | [TikTok策略师](./experts/tik-tok-strategist/) | 精通TikTok算法和海外短视频生态，帮助品牌在全球平台爆发 | 需要 GitHub Token 或 `gh auth login`；需要环境变量：`LIBTV_ACCESS_KEY` | 2026-08-13 |
| [`topic-evaluator`](./experts/topic-evaluator/) | [科技频道选题评估师](./experts/topic-evaluator/) | 双层级4维评分与5方向对比，全部评分详情、硬源清单、风险提示在对话中完整展示，报告可下载存档。 | 无 | 2026-07-22 |
| [`twitter-operations-expert`](./experts/twitter-operations-expert/) | [Twitter运营专家](./experts/twitter-operations-expert/) | 精通Twitter/X平台互动策略和话题运营，让品牌占据全球对话 | 需要 GitHub Token 或 `gh auth login` | 2026-08-13 |
| [`vibeknow-design-video`](./experts/vibeknow-design-video/) | [VibeKnow 视频专家](./experts/vibeknow-design-video/) | 老师讲考点、销售讲方法、企业讲卖点，给个文件或说个主题，自动排版配图配音，成一条设计感横版视频。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-14 |
| [`vibeknow-handdraw`](./experts/vibeknow-handdraw/) | [VibeKnow 手绘视频专家](./experts/vibeknow-handdraw/) | 老师讲考点、医生讲术后护理、工程师讲原理，专业内容边画边讲成手绘科普视频，51种风格随选。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`WB_TOKEN` | 2026-08-14 |
| [`vibeknow-ppt-explain`](./experts/vibeknow-ppt-explain/) | [VibeKnow PPT/PDF讲解大师](./experts/vibeknow-ppt-explain/) | 讲师做内训、医生讲病理、投标专员讲方案，PPT/PDF 逐页配音成讲解视频，原页原版式不用重做。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-14 |
| [`video-dissection`](./experts/video-dissection/) | [视频解剖专家团](./experts/video-dissection/) | 专业拆解火爆抖音视频拍摄手法的专家团。输入抖音链接，自动提取视频、转录文案、分析景别运镜、剪辑节奏、色调风格，生成完整拍摄脚本拆解文档，并提供可落地的仿拍建议。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`API_KEY`、`ARK_API_KEY`、`DOUYIN_API_KEY`、`SILICONFLOW_API_KEY` | 2026-07-22 |
| [`video-gen-team`](./experts/video-gen-team/) | [AI视频创作团队](./experts/video-gen-team/) | 三位一体的AI视频创作团队：灵阅负责采集AI/科技热点，灵枢负责策划选题与脚本，灵映负责渲染MP4视频成品（配音+字幕）。全流程自动化，60秒短视频一键生成。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要环境变量：`AZURE_TTS_KEY` | 2026-07-22 |
| [`viral-topic-master`](./experts/viral-topic-master/) | [爆款选题策划专家](./experts/viral-topic-master/) | 投热点出爆款。12 心法预筛+8 维打分+6 大形态产出，公众号视频号小红书 H5 通吃。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`wechat-official-account-expert`](./experts/wechat-official-account-expert/) | [微信公众号运营专家](./experts/wechat-official-account-expert/) | 精通公众号内容策略和粉丝增长，打造10万+品牌自媒体矩阵 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`TOKEN`、`WECHAT_AUTHOR`、`WECHAT_SECRET` | 2026-08-13 |
| [`weibo-strategist`](./experts/weibo-strategist/) | [微博策略师](./experts/weibo-strategist/) | 精通微博话题营销和舆论传播规律，让品牌在热搜持续出圈 | 无 | 2026-08-13 |
| [`xiaohongshu-operations-expert`](./experts/xiaohongshu-operations-expert/) | [小红书运营专家](./experts/xiaohongshu-operations-expert/) | 深谙小红书种草生态和推荐机制，打造高互动率种草内容 | 需要 GitHub Token 或 `gh auth login`；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`zhihu-strategist`](./experts/zhihu-strategist/) | [知乎策略师](./experts/zhihu-strategist/) | 精通知乎推荐机制和知识营销策略，通过高质量回答建立权威 | 需要 GitHub Token 或 `gh auth login` | 2026-08-13 |

### 开学季（11）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`campus-conversation-coach`](./experts/campus-conversation-coach/) | [校园社交表达教练](./experts/campus-conversation-coach/) | 帮助学生在破冰、面试和校园冲突中，通过递进情景、证据反馈与迁移练习提升自然表达和边界沟通能力。 | 无 | 2026-10-04 |
| [`campus-event-navigator`](./experts/campus-event-navigator/) | [校园活动策划与执行顾问](./experts/campus-event-navigator/) | 把校园活动从模糊想法推进为可执行方案，覆盖分工、预算、宣传、现场流程、应急预案与数据复盘。 | 无（可选 API/账号以增强能力） | 2026-10-04 |
| [`campus-job-search-coach`](./experts/campus-job-search-coach/) | [校园求职教练](./experts/campus-job-search-coach/) | 面向校园求职，支持真实经历梳理、应届简历成稿、岗位定制、面试训练、求职沟通与Offer决策。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`career-navigator`](./experts/career-navigator/) | [大学生生涯决策顾问](./experts/career-navigator/) | 帮助大学生梳理兴趣、能力、价值观与现实约束，对比专业和发展路径，用低成本行动验证方向并形成阶段计划。 | 无 | 2026-10-04 |
| [`computer-operations-advisor`](./experts/computer-operations-advisor/) | [电脑操作与排障顾问](./experts/computer-operations-advisor/) | 面向大学生提供电脑上手、安全装软件、流氓广告防护、校园网络、外设连接与常见故障的分步指导 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`english-writing-coach`](./experts/english-writing-coach/) | [大学英语学习教练](./experts/english-writing-coach/) | 面向大学生诊断英语薄弱项，训练阅读、词汇、语法、翻译与写作，并按考试目标逐轮反馈和复盘。 | 无（可选 API/账号以增强能力） | 2026-10-04 |
| [`exam-preparation-planner`](./experts/exam-preparation-planner/) | [考试复习规划师](./experts/exam-preparation-planner/) | 为在校生制定贴合考试范围、剩余时间和掌握情况的复习计划，通过每日打卡、薄弱点复盘和滚动调整推进备考。 | 无 | 2026-10-04 |
| [`note-class-representative`](./experts/note-class-representative/) | [笔记课代表](./experts/note-class-representative/) | 对齐课堂速记、课件与转写稿，区分来源、加工和核验状态，生成可追踪纠错、可直接复习的笔记与卡片。 | 无 | 2026-10-04 |
| [`skill-smith`](./experts/skill-smith/) | [Skill 制作顾问](./experts/skill-smith/) | 陪制作者把重复工作流做成可用的 Skill：挖掘场景、确认需求、生成制作、实测验证、按标准审查打分。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要 GitHub Token 或 `gh auth login`；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`GH_TOKEN` | 2026-10-04 |
| [`study-fortune-compass`](./experts/study-fortune-compass/) | [学运趋势解读师](./experts/study-fortune-compass/) | 一数起卦，循本卦、互卦与变卦解析学习趋势与盲区，并结合现实信息给出可验证的观察和行动方向。 | 无（可选 API/账号以增强能力） | 2026-10-04 |
| [`thesis-writing-mentor`](./experts/thesis-writing-mentor/) | [论文写作导师](./experts/thesis-writing-mentor/) | 基于可核验材料辅助论文结构、学术润色、期刊匹配与审稿回复，以证据状态和提交就绪度控制质量。 | 无 | 2026-10-04 |

### 技术工程（44）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`api-dev`](./experts/api-dev/) | [API开发专家](./experts/api-dev/) | 专注接口全生命周期开发，涵盖端点搭建、自动化测试、OpenAPI文档生成、Mock服务搭建与HTTP请求问题调试，提升开发效率。 | 无 | 2026-07-22 |
| [`backend-architect`](./experts/backend-architect/) | [后端架构师](./experts/backend-architect/) | 深耕分布式系统和高并发架构，擅长将复杂业务转化为优雅技术方案 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`cat-network-quality-analyst`](./experts/cat-network-quality-analyst/) | [网络质量分析专家](./experts/cat-network-quality-analyst/) | 精通错误分析、性能分析、整体分析、抓包分析、多任务对比分析，自动生成专业分析报告 | 需要环境变量：`CAT_SECRET_KEY`、`TENCENTCLOUD_SECRET_KEY` | 2026-10-04 |
| [`code`](./experts/code/) | [代码开发流程专家](./experts/code/) | 提供规划执行验证测试全流程编码指导，将复杂需求拆解为可独立验证步骤，支持多任务跟踪与偏好记忆。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-22 |
| [`code-review-expert`](./experts/code-review-expert/) | [代码审查专家](./experts/code-review-expert/) | 以鹰眼标准检查每行代码，在缺陷到达生产环境之前将其拦截 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`database-operations`](./experts/database-operations/) | [数据库设计调优专家](./experts/database-operations/) | 精通表结构设计、迁移与性能调优。先用执行计划分析慢查询，再构建复合索引、修复N+1问题、实施分区与缓存优化。 | 无 | 2026-07-22 |
| [`dev-ops-automation-engineer`](./experts/dev-ops-automation-engineer/) | [DevOps自动化工程师](./experts/dev-ops-automation-engineer/) | 将一切手动运维自动化，从CI/CD到基础设施即代码，部署一键搞定 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`dev-pipeline-orchestrator`](./experts/dev-pipeline-orchestrator/) | [开发流水线编排专家](./experts/dev-pipeline-orchestrator/) | 编排开发流水线：澄清需求意图，拆解为测试驱动的细粒度任务，子代理逐任务实现并双重评审，最终集成分支。 | 无 | 2026-07-22 |
| [`dockerfile-gen`](./experts/dockerfile-gen/) | [Dockerfile生成专家](./experts/dockerfile-gen/) | Dockerfile 自动生成专家，遵循容器化最佳实践 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-22 |
| [`edgeone-makers-experts`](./experts/edgeone-makers-experts/) | [Makers 开发专家团](./experts/edgeone-makers-experts/) | 在 EdgeOne Makers 上构建并部署 Web 应用 —— 涵盖前端、Serverless 后端、AI Agent 开发及快速部署到全球加速网络 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`AI_GATEWAY_API_KEY`、`EDGEONE_PAGES_API_TOKEN`、`SUPABASE_ANON_KEY`、`WSA_API_KEY` | 2026-10-04 |
| [`embedded-firmware-engineer`](./experts/embedded-firmware-engineer/) | [嵌入式固件工程师](./experts/embedded-firmware-engineer/) | 精通微控制器编程，在资源受限的硬件上编写高效可靠的固件代码 | 无 | 2026-08-13 |
| [`engineering-assurance-team`](./experts/engineering-assurance-team/) | [工程保障团队](./experts/engineering-assurance-team/) | 由工程总监领导的 5 人工程专家团队：代码审查师（安全/性能/正确性）、架构师（系统设计/ADR）、SRE 工程师（事故响应/部署）、测试专家（测试策略/覆盖率）和技术文档师（文… | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`engineering-workflow-skills`](./experts/engineering-workflow-skills/) | [工程实践专家](./experts/engineering-workflow-skills/) | 基于Google 工程师的《Agent Skills》打造的资深工程全流程教练：规约驱动、测试驱动、代码评审、CI/CD发布 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`eno`](./experts/eno/) | [前端架构分析专家](./experts/eno/) | 深度分析前端项目架构、技术栈选型、组件设计与构建配置，输出含评分等级、优势短板和重构优先级的结构化评审报告。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-21 |
| [`frontend`](./experts/frontend/) | [前端界面开发专家](./experts/frontend/) | 精通响应式界面开发，遵循移动优先与可访问性，以鲜明排版与色彩构建落地页、仪表盘、表单等高保真界面。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`frontend-developer`](./experts/frontend-developer/) | [前端开发工程师](./experts/frontend-developer/) | 精通现代Web技术和主流框架，以像素级精度构建响应式高性能Web应用 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY` | 2026-08-13 |
| [`git-workflow-expert`](./experts/git-workflow-expert/) | [Git工作流专家](./experts/git-workflow-expert/) | 精通Git高级工作流和分支策略，让团队协作像行云流水般顺畅 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`gstack`](./experts/gstack/) | [软件工坊](./experts/gstack/) | 6位工程专业角色：产品评审、代码审查、安全审计、QA测试、设计系统、调试运维，覆盖从想法到生产的完整软件生命周期 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`hsk-devops-expert`](./experts/hsk-devops-expert/) | [网页发布与前端调试专家](./experts/hsk-devops-expert/) | 基于 HSK CLI 的 DevOps 专家，提供零配置公网预览、内网穿透、文件托管和项目部署能力 | 无 | 2026-07-22 |
| [`incident-response-commander`](./experts/incident-response-commander/) | [事故响应指挥官](./experts/incident-response-commander/) | 系统故障时冷静指挥团队快速定位处理和恢复，是终极救火队长 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`infrastructure-operations-expert`](./experts/infrastructure-operations-expert/) | [基础设施运维专家](./experts/infrastructure-operations-expert/) | 确保IT基础设施的持续稳定运行，一切尽在掌控 | 无 | 2026-08-13 |
| [`lsp-index-engineer`](./experts/lsp-index-engineer/) | [LSP索引工程师](./experts/lsp-index-engineer/) | 精通语言服务器协议和代码索引技术 | 无 | 2026-08-13 |
| [`mcp-build-expert`](./experts/mcp-build-expert/) | [MCP构建专家](./experts/mcp-build-expert/) | 精通Model Context Protocol设计实现 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`mobile-application-developer`](./experts/mobile-application-developer/) | [移动应用开发工程师](./experts/mobile-application-developer/) | 精通iOS和Android原生及跨平台开发，打造流畅美观的移动应用 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`modern-webapp`](./experts/modern-webapp/) | [现代Web开发专家](./experts/modern-webapp/) | 现代 Web 应用开发专家，基于 React + TypeScript + Vite + Tailwind CSS + shadcn/ui 技术栈，含浏览器自动化能力 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`mvp-dev-expert-team`](./experts/mvp-dev-expert-team/) | [MVP开发专家团](./experts/mvp-dev-expert-team/) | 说出你的想法，8位专家从调研、设计、编码、测试到部署全流程协作，帮你快速开发MVP产品 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`COS_SECRET_KEY`、`JWT_SECRET`、`MOCK_JWT_TOKEN`、`RESEND_API_KEY`、`SESSION_SECRET`、`STRIPE_SECRET_KEY` | 2026-07-22 |
| [`ncre-expert`](./experts/ncre-expert/) | [计算机等级考试专家团](./experts/ncre-expert/) | NCRE一至四级专家团，覆盖Office、编程、数据库与网络安全，分工协作，量身定制备考方案。 | 无 | 2026-07-22 |
| [`omics-hpc-expert`](./experts/omics-hpc-expert/) | [腾讯组学HPC集群运维与作业管理专家](./experts/omics-hpc-expert/) | 远程组学HPC一站式运维，管控节点、队列、存储全生命周期，适配SLURM/SGE调度，自然语言交互降低门槛 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`prompt-engineer`](./experts/prompt-engineer/) | [大语言模型提示词架构师](./experts/prompt-engineer/) | 精通系统提示词架构、思维链与少样本设计，用测试数据驱动迭代，把提示词优化到模型稳定输出。 | 无 | 2026-07-31 |
| [`python-fullstack-engineer`](./experts/python-fullstack-engineer/) | [Python 全栈工程师](./experts/python-fullstack-engineer/) | 精通后端API、数据分析、AI工程与自动化爬虫，坚持类型安全与工程化，交付测试齐全的生产级全栈代码 | 无（可选 API/账号以增强能力） | 2026-07-31 |
| [`rapid-prototyping-engineer`](./experts/rapid-prototyping-engineer/) | [快速原型工程师](./experts/rapid-prototyping-engineer/) | 以极快速度将创意转化为可工作的原型，让团队快速验证想法 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`rum-fullstack-team`](./experts/rum-fullstack-team/) | [腾讯云 RUM 全链路专家团](./experts/rum-fullstack-team/) | 腾讯云 RUM 全链路服务：10 大平台 aegis SDK 接入 + WebVitals/异常/接口/资源分析，支持 RUM-APM 联动 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`RUM_TOKEN` | 2026-07-22 |
| [`security-engineer`](./experts/security-engineer/) | [安全工程师](./experts/security-engineer/) | 全方位保障系统安全，在黑客之前发现并修复安全漏洞 | 需要 GitHub Token 或 `gh auth login`；需要登录 / OAuth / 扫码授权；需要环境变量：`GITHUB_TOKEN` | 2026-08-13 |
| [`senior-developer`](./experts/senior-developer/) | [高级开发工程师](./experts/senior-developer/) | 10年以上全栈经验，精通多种语言和框架，以严谨的工程纪律交付可运行的高质量代码 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY`、`MINIMAX_API_KEY` | 2026-08-13 |
| [`site-reliability-engineer`](./experts/site-reliability-engineer/) | [站点可靠性工程师](./experts/site-reliability-engineer/) | 用软件工程方法论解决运维问题，确保99.99%可用性 | 无 | 2026-08-13 |
| [`software-architect`](./experts/software-architect/) | [软件架构师](./experts/software-architect/) | 站在全局高度设计可扩展高可用的软件架构，为技术团队指明方向 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`software-company`](./experts/software-company/) | [软件开发团队](./experts/software-company/) | 高效软件研发团队，产品经理定需求、架构师设计+拆任务、工程师批量实现代码、QA验证质量，小需求支持快速模式 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`solidity-smart-contract-engineer`](./experts/solidity-smart-contract-engineer/) | [Solidity智能合约工程师](./experts/solidity-smart-contract-engineer/) | 精通Solidity和EVM生态，编写安全高效的智能合约 | 无 | 2026-08-13 |
| [`superpowers-zh`](./experts/superpowers-zh/) | [AI编程方法论与中文开发规范专家](./experts/superpowers-zh/) | 二十项AI编程方法论，覆盖头脑风暴、测试驱动开发、系统化调试、代码审查，适配中文文档与国内平台规范。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`tencentcloud-api`](./experts/tencentcloud-api/) | [腾讯云API专家](./experts/tencentcloud-api/) | 自然语言管理腾讯云200+产品资源，智能检索API并构造CLI命令，内置安全管控与异常处理 | 需要登录 / OAuth / 扫码授权；需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-08-15 |
| [`terminal-integration-expert`](./experts/terminal-integration-expert/) | [终端集成专家](./experts/terminal-integration-expert/) | 精通终端应用与空间计算环境的集成 | 无 | 2026-08-13 |
| [`threat-detection-engineer`](./experts/threat-detection-engineer/) | [威胁检测工程师](./experts/threat-detection-engineer/) | 专精构建威胁检测系统，在攻击者造成损害前发现拦截威胁 | 无 | 2026-08-13 |
| [`we-chat-mini-program-developer`](./experts/we-chat-mini-program-developer/) | [微信小程序开发者](./experts/we-chat-mini-program-developer/) | 精通微信小程序开发框架和生态，打造流畅微信原生体验应用 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`workspace-builder`](./experts/workspace-builder/) | [工作台搭建师](./experts/workspace-builder/) | 为不同人群定制专属数字工作台，覆盖学习备考、职场效率、自媒体创作、宝妈育儿、生活管理五大场景，PC/移动端双适配，一键部署即用 | 需要微信/企微相关凭证或扫码登录 | 2026-10-04 |

### 数据智能（43）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`academic-journal-selector`](./experts/academic-journal-selector/) | [学术选刊顾问团 v3.1](./experts/academic-journal-selector/) | 万方数据旗下学术选刊专家团，中英双管道并行检索，覆盖中英文核心期刊，输出冲-稳-保分层投稿方案。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-22 |
| [`ai-data-copilot`](./experts/ai-data-copilot/) | [智数分析专家团](./experts/ai-data-copilot/) | 6人AI数据分析团队，擅长自然语言转SQL、Python建模、RAG知识问答、仪表盘可视化与报告生成 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`ai-engineer`](./experts/ai-engineer/) | [AI工程师](./experts/ai-engineer/) | 精通ML模型开发部署优化的全栈AI工程师，将AI从论文带到生产环境 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`aihot`](./experts/aihot/) | [资讯速递专家](./experts/aihot/) | 一句话查到每天精选的 AI 模型/产品/行业/论文动态，自动整理成中文简报，免配置免登录。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`arxiv-watcher`](./experts/arxiv-watcher/) | [ArXiv论文追踪专家](./experts/arxiv-watcher/) | 检索ArXiv最新论文，支持按关键词、作者、学科精准搜索，自动提炼摘要要点并归档至研究日志，助您持续追踪前沿学术动态。 | 无 | 2026-07-22 |
| [`autonomous-optimization-architect`](./experts/autonomous-optimization-architect/) | [自主优化架构师](./experts/autonomous-optimization-architect/) | 专精于设计能自主优化和进化的智能系统架构，让系统越用越聪明 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-08-13 |
| [`data`](./experts/data/) | [数据探索专家](./experts/data/) | 数据探索专家，支持 SQL 查询、数据探索、可视化、仪表板构建、数据验证和洞察生成 | 可能需要启用对应 MCP / 连接器；需要环境变量：`DISTKEY`、`SORTKEY` | 2026-07-21 |
| [`data-analysis`](./experts/data-analysis/) | [数据分析专家](./experts/data-analysis/) | 数据分析专家，支持 Excel 电子表格的创建、编辑、分析、公式计算、格式化和数据可视化 | 需要微信/企微相关凭证或扫码登录 | 2026-07-23 |
| [`data-analytics-reporter`](./experts/data-analytics-reporter/) | [数据分析报告师](./experts/data-analytics-reporter/) | 将复杂数据转化为战略洞察，提供指标诊断、KPI框架设计、数据质量评估与决策报告 | 无 | 2026-07-22 |
| [`data-engineer`](./experts/data-engineer/) | [数据工程师](./experts/data-engineer/) | 构建高效可靠的数据管道和ETL流程，让数据从源头到洞察畅通无阻 | 无 | 2026-08-13 |
| [`data-integration-agent`](./experts/data-integration-agent/) | [数据整合代理](./experts/data-integration-agent/) | 将分散数据清洗整合统一，构建企业统一数据视图 | 无 | 2026-08-13 |
| [`database-optimization-expert`](./experts/database-optimization-expert/) | [数据库优化专家](./experts/database-optimization-expert/) | 专精数据库性能调优和查询优化，让慢查询变快让瓶颈消失 | 需要环境变量：`SUPABASE_ANON_KEY` | 2026-08-13 |
| [`databrain-opinion-expert`](./experts/databrain-opinion-expert/) | [DataBrain舆情分析专家](./experts/databrain-opinion-expert/) | 玩家口碑与舆情侦察兵，覆盖评分告警、内容趋势、竞品对比与热点挖掘，实时感知玩家声音，辅助运营决策 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`DATABRAIN_TOKEN`、`TAI_IT_TOKEN` | 2026-07-22 |
| [`deep-research`](./experts/deep-research/) | [深度研究专家](./experts/deep-research/) | 综合性深度研究专家，支持多源信息检索、事实验证、知识发现和结构化报告生成，含微信公众号文章搜索能力 | 需要微信/企微相关凭证或扫码登录 | 2026-08-04 |
| [`empirical-research-team`](./experts/empirical-research-team/) | [科研专家团](./experts/empirical-research-team/) | 覆盖实证研究全流程的专家团：因果推断、稳健性检验、出版级表图与降AIGC，高效完成可复现学术论文 | 无（可选 API/账号以增强能力） | 2026-08-03 |
| [`finance-data`](./experts/finance-data/) | [金融数据检索专家](./experts/finance-data/) | 金融数据检索专家，通过自然语言查询 209 个金融数据 API，涵盖股票、指数、期货、债券、基金和宏观经济等 15 大类 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`fundus-disease-analysis`](./experts/fundus-disease-analysis/) | [腾讯健康-觅影-眼底彩照疾病分析专家](./experts/fundus-disease-analysis/) | 基于普角与超广角眼底彩照的AI多病种分析，覆盖青光眼、糖网、AMD等数十种疾病的诊断与报告解读。 | 需要环境变量：`FUNDUS_TOKEN` | 2026-07-31 |
| [`gpt-researcher-team`](./experts/gpt-researcher-team/) | [深度研究团队](./experts/gpt-researcher-team/) | 深度研究报告输出，7角色5阶段聚合多源信息，经审稿修订循环输出带引用的专业报告 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`huashu-data-pro`](./experts/huashu-data-pro/) | [花叔数据分析专家团](./experts/huashu-data-pro/) | 「一人公司」本地数据分析专家团。一份 Excel 进，趋势 / 结构 / 异常三专家并行分析，交付网页、Excel、PPT 三格式报告，数据不出本地。 | 无 | 2026-07-22 |
| [`jinshuju-expert`](./experts/jinshuju-expert/) | [金数据表单与数据管理专家](./experts/jinshuju-expert/) | 通过金数据 MCP 用自然语言搭建表单、增删改查与批量维护数据、查询套餐额度，替代登录后台手动操作 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`YOUR_API_KEY`、`YOUR_API_SECRET` | 2026-07-22 |
| [`jinshuju-form-expert`](./experts/jinshuju-form-expert/) | [金数据表单助手](./experts/jinshuju-form-expert/) | 搭建报名、问卷、预约、收款等表单，增删改查、批量导入导出数据，替代登录后台操作。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`YOUR_API_KEY`、`YOUR_API_SECRET` | 2026-07-28 |
| [`jinshuju-table-expert`](./experts/jinshuju-table-expert/) | [金数据AI表格助手](./experts/jinshuju-table-expert/) | 轻量表格，支持文本、日期等多种字段类型，专为 Agent 设计，可随时读写协作。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`YOUR_API_KEY`、`YOUR_API_SECRET` | 2026-07-28 |
| [`kdocs-data-table`](./experts/kdocs-data-table/) | [数据建表专家](./experts/kdocs-data-table/) | 金山文档出品，专注接龙转表与智能表单，支持条件格式、数据校验和区域保护，省心好用。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`llm-wiki`](./experts/llm-wiki/) | [知识管理专家](./experts/llm-wiki/) | 基于 Andrej Karpathy 的 LLM Wiki 模式，帮助用户构建、维护和查询持久化的个人知识库。擅长将原始资料（论文、文章、笔记等）编译为结构化 Markdown … | 无 | 2026-08-13 |
| [`mibao-media-archivist`](./experts/mibao-media-archivist/) | [AI影像资产整理专家](./experts/mibao-media-archivist/) | 在不改动原件的前提下，完成影像盘点、严格SHA-256、精确重复识别、本地索引检索与可验收报告 | 可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`model-quality-assurance-expert`](./experts/model-quality-assurance-expert/) | [模型质量保障专家](./experts/model-quality-assurance-expert/) | 系统化评估保障AI模型质量，确保输出准确公平安全 | 无 | 2026-08-13 |
| [`nuwa`](./experts/nuwa/) | [思维蒸馏师](./experts/nuwa/) | 女娲蒸馏知名人物的思维方式为可运行视角。给定名字（如乔布斯、芒格、纳瓦尔、马斯克），运行多路调研→三重验证提炼→技能构建→质量验证四阶段流水线，用其认知框架分析你的问题 | 无 | 2026-07-31 |
| [`omics-bioinfo-expert`](./experts/omics-bioinfo-expert/) | [腾讯组学生信分析专家](./experts/omics-bioinfo-expert/) | 专攻生信分析，支持任务投递、进度追踪、日志解析、智能排错。内置自研模型库，加速生信研发与生产分析 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`omics-cdgpt-expert`](./experts/omics-cdgpt-expert/) | [腾讯CD-GPT生物序列建模专家](./experts/omics-cdgpt-expert/) | 基于腾讯CD-GPT多模态大模型，覆盖DNA、RNA、蛋白质序列，支持翻译、反向翻译、生成 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`omics-diagnosis-expert`](./experts/omics-diagnosis-expert/) | [腾讯组学任务分析智能诊断专家](./experts/omics-diagnosis-expert/) | 生物信息分析智能诊断，解析任务日志、拆解错误堆栈、快速定位OOM、磁盘满载等故障根源，提升分析效率 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`omics-iggm-expert`](./experts/omics-iggm-expert/) | [腾讯IgGM抗体药物研发专家](./experts/omics-iggm-expert/) | 精通腾讯IgGM生成式模型。覆盖CDR重设计、全链生成与人源化亲和力优化，输出可验证的抗体候选序列 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`omics-ori-expert`](./experts/omics-ori-expert/) | [腾讯ORI多功能酶设计专家](./experts/omics-ori-expert/) | 覆盖序列从头设计、USMFold结构预测与溶解性、热稳定性，打通从设计到可生产蛋白的关键决策 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`omics-scbert-expert`](./experts/omics-scbert-expert/) | [腾讯scBert单细胞预训练专家](./experts/omics-scbert-expert/) | 基于腾讯scBERT单细胞预训练大模型，实现细胞精细注释、新亚群挖掘及Marker筛选，自适应多组织参数，助力肿瘤细胞研究 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`omics-scprotein-expert`](./experts/omics-scprotein-expert/) | [腾讯scPROTEIN单细胞蛋白组建模专家](./experts/omics-scprotein-expert/) | 腾讯 scPROTEIN表征模型，实现对单细胞蛋白组的多肽不确定性估计，去除批次效应噪声以及单细胞蛋白组的细胞类型注释 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`omics-tfold-expert`](./experts/omics-tfold-expert/) | [腾讯tFold抗体结构预测专家](./experts/omics-tfold-expert/) | 腾讯tFold模型，专注单克隆抗体、纳米抗体与抗原复合物的高精度结合界面建模，辅助表位预测与亲和力改造 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`personal-knowledge-architect`](./experts/personal-knowledge-architect/) | [个人知识库架构师](./experts/personal-knowledge-architect/) | 精通卡片盒、PARA、LYT 等方法论，结合 Obsidian 等工具把信息搭成可检索的第二大脑。 | 无 | 2026-07-31 |
| [`pneumonia-ai-analyst`](./experts/pneumonia-ai-analyst/) | [基于CT序列的肺炎AI辅助诊断分析](./experts/pneumonia-ai-analyst/) | 上传胸部CT DICOM压缩包即可完成肺炎AI辅助诊断，逐张分析耗时较久请耐心等待。 | 需要环境变量：`INVALID_TOKEN` | 2026-07-29 |
| [`prompt-engineering-expert`](./experts/prompt-engineering-expert/) | [AI提示词工程专家](./experts/prompt-engineering-expert/) | 精通提示词工程，提供提示词撰写、系统提示设计、自定义指令、优化迭代与评估测试，打造高效稳定的智能体。 | 无 | 2026-07-22 |
| [`sales-data-extraction-agent`](./experts/sales-data-extraction-agent/) | [销售数据提取代理](./experts/sales-data-extraction-agent/) | 从各类数据源中自动提取整理销售数据 | 无 | 2026-08-13 |
| [`tiderider-sentiment`](./experts/tiderider-sentiment/) | [游戏舆情分析师](./experts/tiderider-sentiment/) | 游戏舆情分析师：基于多平台玩家评论，做异动归因、话题提取、版本趋势对比，并生成精品可视化分析报告。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`DATABRAIN_TOKEN` | 2026-10-04 |
| [`trend-researcher`](./experts/trend-researcher/) | [行业趋势专家](./experts/trend-researcher/) | 持续追踪行业和技术趋势，为产品战略提供前瞻性洞察 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY`、`IMA_OPENAPI_APIKEY` | 2026-08-13 |
| [`vocab-craft-expert`](./experts/vocab-craft-expert/) | [智能词汇教练](./experts/vocab-craft-expert/) | 融合间隔重复记忆科学与键盘输入训练的AI英语词汇教练，支持每日定时推送、错词强化、三种练习模式，让背单词更科学高效 | 无 | 2026-07-22 |
| [`yunzhi-qa-assistant`](./experts/yunzhi-qa-assistant/) | [腾讯云知识问答专家](./experts/yunzhi-qa-assistant/) | 基于腾讯云知（乐享）知识库的检索增强问答专家，支持竞品对比与国际化海外检索，输出带引用的结构化答案。 | 可能需要启用对应 MCP / 连接器；需要环境变量：`LEXIANG_TOKEN` | 2026-10-04 |

### 法务安全（27）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`agent-identity-trust-expert`](./experts/agent-identity-trust-expert/) | [智能体身份信任专家](./experts/agent-identity-trust-expert/) | 构建AI智能体间的身份认证和信任机制 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`blockchain-security-auditor`](./experts/blockchain-security-auditor/) | [区块链安全审计师](./experts/blockchain-security-auditor/) | 专精区块链智能合约和DeFi协议安全审计 | 无 | 2026-08-13 |
| [`chatlaw-team`](./experts/chatlaw-team/) | [中文法律咨询团](./experts/chatlaw-team/) | 案情采集、法条研究、判例分析、建议撰写，为民事、婚姻、合同、劳动等高频场景出具专业法律咨询报告。 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`compliance-auditor`](./experts/compliance-auditor/) | [合规审计师](./experts/compliance-auditor/) | 全面审计企业运营合规性，确保符合行业标准 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-08-13 |
| [`contract-expert`](./experts/contract-expert/) | [合同风控顾问](./experts/contract-expert/) | 覆盖合同起草、审查、谈判、背景评估与全生命周期管理；专业审查模式一键产出风险清单、审查报告与批注稿。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`contract-legal-expert`](./experts/contract-legal-expert/) | [资深合同法务专家](./experts/contract-legal-expert/) | 腾讯电子签合同法务专家擅长合同起草、审查、对比、法规检索，能在线发起签署，劳动/租赁/买卖全场景覆盖 | 需要登录 / OAuth / 扫码授权；需要环境变量：`ESIGN_TOKEN`、`NEW_TOKEN`、`YOUR_TOKEN` | 2026-10-04 |
| [`enterprise-legal-team`](./experts/enterprise-legal-team/) | [企业法务专家团](./experts/enterprise-legal-team/) | 面向企业法务的多角色专家团，覆盖合同、交易、隐私、产品、监管、AI 治理、雇佣与知识产权分诊。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`fbsir-aigc-compliance-red-team`](./experts/fbsir-aigc-compliance-red-team/) | [AIGC 营销合规审查官](./experts/fbsir-aigc-compliance-red-team/) | 福帮手 AIGC 发布前对抗审查：核验双标识、违禁词、虚假人设，输出风险等级、法条依据与安全改写。 | 可能需要启用对应 MCP / 连接器 | 2026-08-16 |
| [`fbsir-board-secretary-assistant`](./experts/fbsir-board-secretary-assistant/) | [董秘助手](./experts/fbsir-board-secretary-assistant/) | 面向公告、路演、投资者问答、互动回复和沟通稿，在对外使用前做合规红队审查并给出审批下一步。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`healthcare-marketing-compliance-expert`](./experts/healthcare-marketing-compliance-expert/) | [医疗营销合规专家](./experts/healthcare-marketing-compliance-expert/) | 确保医疗营销内容符合法规要求，守护信息准确性 | 无 | 2026-07-22 |
| [`huashu-doc-reviewer`](./experts/huashu-doc-reviewer/) | [合同与公文审稿](./experts/huashu-doc-reviewer/) | 为「一人公司」打造的 AI 审稿专家。直接在 .docx 原文里加批注气泡和追踪修订，不返回新文档、不破坏原格式。 | 无 | 2026-07-22 |
| [`invoice-verify-expert`](./experts/invoice-verify-expert/) | [发票查验专家](./experts/invoice-verify-expert/) | 支持增值税发票、全电发票、区块链发票、机动车销售发票、通行费发票等17种类型的真伪查验与明细解析 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`HELIOS_KEY`、`YOUR_KEY` | 2026-07-29 |
| [`invoice-verify-workbuddy`](./experts/invoice-verify-workbuddy/) | [智能发票专家团](./experts/invoice-verify-workbuddy/) | 五位AI专家接力协作，通过上传文件、表格或文件夹，完成识别、税局验真、信用核查与归档 | 可能需要启用对应 MCP / 连接器；需要环境变量：`KEY_NAME`、`OSS_ACCESS_KEY`、`OSS_SECRET_KEY` | 2026-07-22 |
| [`ip-expert`](./experts/ip-expert/) | [知识产权专家](./experts/ip-expert/) | 覆盖著作权、专利、商标、商业秘密与域名，指引专业库检索，做侵权/FTO/确权分析并输出可落地策略。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`law-student-coach`](./experts/law-student-coach/) | [法学学习教练](./experts/law-student-coach/) | 面向法学生的学习陪练，训练苏格拉底问答、案例摘要、IRAC、课程大纲和律考复习。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`legal-builder-hub`](./experts/legal-builder-hub/) | [法律技能治理专家](./experts/legal-builder-hub/) | 面向法律运营和技能开发者的治理助手，评估技能来源、工具权限、新鲜度、许可证和信任边界。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`legal-clinic-supervisor`](./experts/legal-clinic-supervisor/) | [法律诊所督导顾问](./experts/legal-clinic-supervisor/) | 面向法学院诊所导师的监督助手，支持客户接待、研究启动、期限追踪、学生入职和学期交接。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`legal-compliance-reviewer`](./experts/legal-compliance-reviewer/) | [法律合规审查员](./experts/legal-compliance-reviewer/) | 确保业务运营和产品功能符合法律法规要求，防范合规风险 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`IMA_OPENAPI_APIKEY`、`TENCENT_DOCS_TOKEN` | 2026-08-13 |
| [`legal-search-pro`](./experts/legal-search-pro/) | [法律检索专家](./experts/legal-search-pro/) | 识别检索意图与场景，按法源位阶检索法规与类案，验证效力评估相似度，适配14种输出可溯源报告。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`litigation-legal`](./experts/litigation-legal/) | [诉讼支持顾问](./experts/litigation-legal/) | 面向诉讼律师的案件支持专家，梳理案件、证据、时间线、质证准备、索赔图表和文书草稿。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`marketing-reviewer`](./experts/marketing-reviewer/) | [营销文案审查官](./experts/marketing-reviewer/) | 9维度34条规则扫描营销文案，定位广告法与隐私合规风险，输出分级Excel与HTML审查报告。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`sa-legal-compliance`](./experts/sa-legal-compliance/) | [南非法务合规专家](./experts/sa-legal-compliance/) | 专注南非法务合规领域，覆盖公司注册、合同管理、知识产权保护、数据隐私合规、行业准入与争议解决等关键领域。 | 无 | 2026-08-04 |
| [`smb-compliance`](./experts/smb-compliance/) | [客户与合规官](./experts/smb-compliance/) | 小企业客户与合规官，处理客户反馈、客诉工单、CRM清理和合同风险审查 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`tax-compliance-team`](./experts/tax-compliance-team/) | [财税合规专家团](./experts/tax-compliance-team/) | 覆盖票据处理、记账核算、报表编制、税务申报、合规审计五大环节的企业财税合规全链路管理专家团 | 无 | 2026-07-21 |
| [`tc-sec`](./experts/tc-sec/) | [腾讯云安全专家](./experts/tc-sec/) | 调用云API对容器/主机安全、WAF、云防、云安全中心、堡垒机、密钥管理、数据安全告警/资产进行分析 | 需要登录 / OAuth / 扫码授权 | 2026-08-01 |
| [`xiaofa-litigation-assistant`](./experts/xiaofa-litigation-assistant/) | [诉讼助手](./experts/xiaofa-litigation-assistant/) | 诉讼助手：起草起诉状、要素式转换、证据整理、流程指引、强制执行、利息计算。输出 DOCX 格式，Word/WPS 直接编辑。7大法律技能，一站式自助办案。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器；需要环境变量：`YOUR_API_KEY` | 2026-07-21 |
| [`zero-knowledge-proof-admin`](./experts/zero-knowledge-proof-admin/) | [零知识证明管理员](./experts/zero-knowledge-proof-admin/) | 精通零知识证明技术的应用和管理 | 无（可选 API/账号以增强能力） | 2026-08-13 |

### 游戏空间（25）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`game-audio-engineer`](./experts/game-audio-engineer/) | [游戏音频工程师](./experts/game-audio-engineer/) | 精通FMOD/Wwise集成和空间音频，让游戏声音栩栩如生 | 无 | 2026-08-13 |
| [`game-designer`](./experts/game-designer/) | [游戏设计师](./experts/game-designer/) | 精通游戏系统和机制设计，用循环杠杆和心理构建玩法 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`game-development-studio`](./experts/game-development-studio/) | [游戏开发工作室](./experts/game-development-studio/) | 统筹策划、技术、美术、音频、质量、运营六大专业成员，以七阶段工作流驱动游戏从概念到上线流程协同开发。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`godot-game-script-engineer`](./experts/godot-game-script-engineer/) | [Godot游戏脚本工程师](./experts/godot-game-script-engineer/) | 精通GDScript 2.0和Godot 4节点架构 | 无 | 2026-08-13 |
| [`godot-multiplayer-engineer`](./experts/godot-multiplayer-engineer/) | [Godot多人联机工程师](./experts/godot-multiplayer-engineer/) | 精通Godot 4 MultiplayerAPI和网络复制 | 无 | 2026-08-13 |
| [`godot-shader-developer`](./experts/godot-shader-developer/) | [Godot着色器开发者](./experts/godot-shader-developer/) | 精通Godot着色语言和VisualShader | 无 | 2026-08-13 |
| [`level-designer`](./experts/level-designer/) | [关卡设计师](./experts/level-designer/) | 将每个关卡视为精心编排的体验，用空间讲述故事 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`mac-os-spatial-metal-engineer`](./experts/mac-os-spatial-metal-engineer/) | [macOS空间Metal工程师](./experts/mac-os-spatial-metal-engineer/) | 精通Apple Metal图形API和macOS空间计算开发 | 无 | 2026-08-13 |
| [`narrative-designer`](./experts/narrative-designer/) | [叙事设计师](./experts/narrative-designer/) | 将叙事和游戏玩法无缝融合，让故事与互动不可分割 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`roblox-avatar-creator`](./experts/roblox-avatar-creator/) | [Roblox虚拟形象创作者](./experts/roblox-avatar-creator/) | 精通Roblox UGC和虚拟形象管线 | 无 | 2026-08-13 |
| [`roblox-experience-designer`](./experts/roblox-experience-designer/) | [Roblox体验设计师](./experts/roblox-experience-designer/) | 精通Roblox平台UX和商业化设计 | 无 | 2026-08-13 |
| [`roblox-system-script-engineer`](./experts/roblox-system-script-engineer/) | [Roblox系统脚本工程师](./experts/roblox-system-script-engineer/) | 精通Luau和Roblox客户端-服务器安全模型 | 无 | 2026-08-13 |
| [`technical-artist`](./experts/technical-artist/) | [技术美术](./experts/technical-artist/) | 在美术愿景与引擎实现之间架起桥梁，精通着色器和VFX | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`GEMINI_API_KEY` | 2026-08-13 |
| [`unity-architect`](./experts/unity-architect/) | [Unity架构师](./experts/unity-architect/) | 精通ScriptableObjects和解耦系统设计 | 无 | 2026-08-13 |
| [`unity-editor-tool-developer`](./experts/unity-editor-tool-developer/) | [Unity编辑器工具开发者](./experts/unity-editor-tool-developer/) | 精通Unity自定义EditorWindow和管线自动化 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`unity-multiplayer-engineer`](./experts/unity-multiplayer-engineer/) | [Unity多人联机工程师](./experts/unity-multiplayer-engineer/) | 精通Netcode for GameObjects和网络预测 | 无 | 2026-08-13 |
| [`unity-shader-graph-artist`](./experts/unity-shader-graph-artist/) | [Unity着色器图表艺术家](./experts/unity-shader-graph-artist/) | 精通Unity Shader Graph和HLSL | 无 | 2026-08-13 |
| [`unreal-multiplayer-architect`](./experts/unreal-multiplayer-architect/) | [Unreal多人架构师](./experts/unreal-multiplayer-architect/) | 精通Unreal Actor复制和服务器权威架构 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`unreal-system-engineer`](./experts/unreal-system-engineer/) | [Unreal系统工程师](./experts/unreal-system-engineer/) | 精通C++/Blueprint和Nanite/Lumen | 无 | 2026-08-13 |
| [`unreal-technical-artist`](./experts/unreal-technical-artist/) | [Unreal技术美术](./experts/unreal-technical-artist/) | 精通UE5材质编辑器和Niagara VFX | 无 | 2026-08-13 |
| [`unreal-world-builder`](./experts/unreal-world-builder/) | [Unreal世界构建师](./experts/unreal-world-builder/) | 精通UE5 World Partition和大世界流式加载 | 无 | 2026-08-13 |
| [`vision-os-spatial-engineer`](./experts/vision-os-spatial-engineer/) | [visionOS空间工程师](./experts/vision-os-spatial-engineer/) | 精通visionOS平台开发，打造Apple Vision Pro空间应用 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`xr-cockpit-interaction-expert`](./experts/xr-cockpit-interaction-expert/) | [XR座舱交互专家](./experts/xr-cockpit-interaction-expert/) | 专精XR环境下的座舱式交互设计 | 无 | 2026-08-13 |
| [`xr-immersive-developer`](./experts/xr-immersive-developer/) | [XR沉浸式开发者](./experts/xr-immersive-developer/) | 精通XR沉浸式体验开发，创造身临其境的VR/MR应用 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`xr-interface-architect`](./experts/xr-interface-architect/) | [XR界面架构师](./experts/xr-interface-architect/) | 设计XR环境中的用户界面架构，让3D空间交互直观自然 | 无 | 2026-08-13 |

### 腾讯专区（26）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`andon-q-expert`](./experts/andon-q-expert/) | [腾讯云智能客服](./experts/andon-q-expert/) | 精通腾讯云全线产品，提供产品咨询、故障排查、服务报告等多维度服务的技术专家。 | 需要登录 / OAuth / 扫码授权；需要环境变量：`TENCENTCLOUD_SECRET_KEY`、`TENCENTCLOUD_TOKEN` | 2026-07-21 |
| [`anti-scam-agent`](./experts/anti-scam-agent/) | [腾讯云天御反诈专家](./experts/anti-scam-agent/) | 金融黑灰产情报驱动的反诈智能体，覆盖电诈、职业背债、贷款包装、反催收，能分析、能查证、能出研判报告。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-28 |
| [`apm-performance-expert`](./experts/apm-performance-expert/) | [应用性能专家](./experts/apm-performance-expert/) | 精通腾讯云 APM 性能诊断与调优，快速定位应用瓶颈并给出优化方案 | 可能需要启用对应 MCP / 连接器；需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-21 |
| [`capacity-expert`](./experts/capacity-expert/) | [腾讯云容量规划专家](./experts/capacity-expert/) | 容量规划专家。擅长水位监控、容量预测与弹性伸缩策略制定，防止资源瓶颈与浪费。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`chaos-expert`](./experts/chaos-expert/) | [腾讯云混沌演练专家](./experts/chaos-expert/) | 混沌演练专家。擅长故障注入演练、韧性验证与熔断策略评估，提升系统抗脆弱能力。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`charity-doc-finance-expert`](./experts/charity-doc-finance-expert/) | [公益文书与财务专家](./experts/charity-doc-finance-expert/) | 公益机构文书与财务一站式专家，覆盖项目申请书、结项报告、票据管理、审计准备与合规咨询，帮助公益人从繁琐行政中解放。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-23 |
| [`cloud-ops-team`](./experts/cloud-ops-team/) | [腾讯云技术支持](./experts/cloud-ops-team/) | 三位专家组成的运维团队 — CloudQ 负责多云统一治理与架构可视化，AndonQ 负责工单管理与智能问答，MigraQ 负责跨云迁移规划与 TCO 分析。从迁移上云到日常运维… | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`TENCENTCLOUD_SECRET_KEY`、`TENCENTCLOUD_TOKEN` | 2026-07-22 |
| [`databrain-agent-v2`](./experts/databrain-agent-v2/) | [DataBrain数据专家2.0](./experts/databrain-agent-v2/) | 覆盖经分取数、三方市场情报、舆情情感分析、归因下钻及跨游戏竞品对比，提供有数据支撑的专业洞察与建议。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器；需要环境变量：`DATABRAIN_TOKEN` | 2026-07-23 |
| [`finops-expert`](./experts/finops-expert/) | [腾讯云FinOps专家](./experts/finops-expert/) | 云成本治理专家。擅长账单分析、闲置资源识别、计费模式优化与成本分摊，驱动降本增效决策。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`hr-digital-expert`](./experts/hr-digital-expert/) | [腾讯HR数智专家](./experts/hr-digital-expert/) | 覆盖HR数仓查询、页面设计开发、一键部署上线和知识库管理的全链路HR数智专家 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`industry-sre-team`](./experts/industry-sre-team/) | [腾讯云行业SRE](./experts/industry-sre-team/) | 12 位行业 SRE 覆盖游戏、金融、电商等场景，做五维巡检，输出可对照可执行的架构治理建议。 | 无 | 2026-08-13 |
| [`inspection-expert`](./experts/inspection-expert/) | [腾讯云风险巡检专家](./experts/inspection-expert/) | 云资源巡检专家。覆盖五维巡检（安全、性能、可靠性、成本、合规）、高危风险扫描与优先级处置、巡检趋势分析与可视化报告生成，主动发现潜在隐患，防患于未然。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`migraq-team`](./experts/migraq-team/) | [腾讯云上云迁移专家团](./experts/migraq-team/) | 7位专家协作完成上云迁移：产品选型、Landing Zone、架构设计、交付实施、运维与FDE部署 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`multi-cloud-expert`](./experts/multi-cloud-expert/) | [多云AIOps专家](./experts/multi-cloud-expert/) | 统一管理腾讯云、阿里云、AWS、Azure、GCP 等多云平台，一个智能体即可管多云。 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`multi-cloud-management-expert`](./experts/multi-cloud-management-expert/) | [腾讯云DevOps专家](./experts/multi-cloud-management-expert/) | 精通腾讯云、阿里云、AWS等多云架构治理、可视化、智能巡检与成本优化，一个专家管理所有云。 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-08-13 |
| [`patient-education-content-review-word-assistant`](./experts/patient-education-content-review-word-assistant/) | [腾讯健康药箱-私域患教内容审核助手](./experts/patient-education-content-review-word-assistant/) | 六维度审核患教内容并核对数据文献一致性，审核意见以 Word 批注+高亮直接标注在原文上输出。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`sdk-log-expert`](./experts/sdk-log-expert/) | [SDK 日志分析专家](./experts/sdk-log-expert/) | 解码客户端日志，还原 TRTC/IM/TUI 时间线，定位音视频与 IM 相关根因 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`soe`](./experts/soe/) | [腾讯云安全运营专家](./experts/soe/) | 分析WAF、主机安全、云防火墙、SOC、御界、天幕告警事件，覆盖漏洞、攻击、入侵溯源与iOA排障。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`NVD_API_KEY` | 2026-10-04 |
| [`sre-expert`](./experts/sre-expert/) | [腾讯云SRE专家](./experts/sre-expert/) | 站点可靠性专家。擅长故障根因推理、告警关联分析、业务进程诊断与 SLO 治理，通过系统化诊断方法论保障服务持续稳定运行。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`tencent-charity-expert`](./experts/tencent-charity-expert/) | [腾讯技术公益智能化专家](./experts/tencent-charity-expert/) | 精通公益行业产品和技术解决方案的腾讯技术公益智能化专家 | 无 | 2026-07-22 |
| [`tencent-cloud-quote-assistant`](./experts/tencent-cloud-quote-assistant/) | [腾讯云产品报价顾问](./experts/tencent-cloud-quote-assistant/) | 面向销售与方案团队的腾讯云报价助手，支持产品咨询选型、实时刊例价查询比较、批量采购报价、友商 Mapping 与折扣推荐。 | 需要环境变量：`KNOT_API_TOKEN` | 2026-08-11 |
| [`tencent-rtc-expert`](./experts/tencent-rtc-expert/) | [腾讯云实时音视频专家](./experts/tencent-rtc-expert/) | TRTC 技术支持专家：通话用量与质量查询、单次通话诊断、云端巡检解读、故障排查与友商代码迁移。 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；需要环境变量：`TENCENTCLOUD_SECRET_KEY` | 2026-07-22 |
| [`tencent-security-expert`](./experts/tencent-security-expert/) | [腾讯安全专家](./experts/tencent-security-expert/) | 深耕安全领域多年，提供威胁建模、漏洞评估、安全代码审查、架构设计、事件响应、安全咨询等服务 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`tianyu-account-guardian`](./experts/tianyu-account-guardian/) | [腾讯云天御账号保护专家](./experts/tianyu-account-guardian/) | 替您盯住注册、登录、裂变全链路账号异常，实时调优策略拦截恶意账号，并生成客诉原因分析报告。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`tianyu-marketing-guardian`](./experts/tianyu-marketing-guardian/) | [腾讯云天御营销保护专家](./experts/tianyu-marketing-guardian/) | 替您守护每一场营销活动，在文旅、零售、Token、医疗挂号等场景自动盯活动、查漏召、调策略护预算。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`well-arch-expert`](./experts/well-arch-expert/) | [腾讯云卓越架构专家](./experts/well-arch-expert/) | 卓越架构专家。擅长架构可视化评估、资源拓扑梳理、Well-Architected 六支柱评估与架构风险识别，确保架构符合最佳实践。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |

### 营销增长（37）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`ad-creative-strategist`](./experts/ad-creative-strategist/) | [广告创意策略师](./experts/ad-creative-strategist/) | 精通广告创意设计和效果预判，创作高转化广告素材 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`ad-tracking-expert`](./experts/ad-tracking-expert/) | [广告追踪技术专家](./experts/ad-tracking-expert/) | 精通广告追踪代码和转化归因技术，确保投放效果可追踪 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`app-store-optimization-expert`](./experts/app-store-optimization-expert/) | [应用商店优化专家](./experts/app-store-optimization-expert/) | 精通App Store和Google Play搜索排名算法，让应用脱颖而出 | 无 | 2026-08-13 |
| [`auto-consultant`](./experts/auto-consultant/) | [汽车营销专家](./experts/auto-consultant/) | 精通用户选车购车决策，深谙汽车营销增长，覆盖品牌营销、用户增长、车型分析、购车咨询等全链路汽车服务。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`baidu-seo-expert`](./experts/baidu-seo-expert/) | [百度SEO专家](./experts/baidu-seo-expert/) | 深谙百度搜索算法和中国搜索生态，让品牌获得最大曝光 | 无 | 2026-08-13 |
| [`brand-guardian`](./experts/brand-guardian/) | [品牌策略师](./experts/brand-guardian/) | 15年品牌战略经验，守护品牌一致性的终极捍卫者 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-08-13 |
| [`carousel-content-growth-expert`](./experts/carousel-content-growth-expert/) | [轮播内容增长专家](./experts/carousel-content-growth-expert/) | 专精设计高互动率轮播图内容，驱动社交平台用户参与和增长 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`GEMINI_API_KEY`、`UPLOADPOST_TOKEN` | 2026-07-22 |
| [`china-ecommerce-operations-expert`](./experts/china-ecommerce-operations-expert/) | [中国电商运营专家](./experts/china-ecommerce-operations-expert/) | 精通天猫京东拼多多等平台运营，从选品到爆款一站式操盘 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`content-monetization-team`](./experts/content-monetization-team/) | [内容变现商业化专家团](./experts/content-monetization-team/) | 5人专家团覆盖CPS带货分佣、CPE/CPM效果广告、创作者-品牌交易撮合与收益分析，助力内容创作者和品牌方实现商业化闭环 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`cross-border-ecommerce-expert`](./experts/cross-border-ecommerce-expert/) | [跨境电商专家](./experts/cross-border-ecommerce-expert/) | 精通亚马逊Shopify等国际电商平台，助力品牌出海全球 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY` | 2026-08-13 |
| [`cultural-intelligence-strategist`](./experts/cultural-intelligence-strategist/) | [文化智能策略师](./experts/cultural-intelligence-strategist/) | 帮助品牌建立全球化过程中的文化敏感度 | 无 | 2026-08-13 |
| [`developer-evangelist`](./experts/developer-evangelist/) | [开发者布道师](./experts/developer-evangelist/) | 构建发展开发者社区，推动产品在开发者群体中的采用 | 需要 GitHub Token 或 `gh auth login` | 2026-08-13 |
| [`executing-marketing-campaigns`](./experts/executing-marketing-campaigns/) | [营销活动策划专家](./experts/executing-marketing-campaigns/) | 策划、创建和优化全渠道营销活动，包括内容策略、社交媒体、邮件营销和广告投放 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`geo-diagnosis-expert`](./experts/geo-diagnosis-expert/) | [品牌 GEO 可见度诊断师](./experts/geo-diagnosis-expert/) | 品牌 GEO 可见度诊断专家，覆盖基建评估、AI 平台收录、竞品对标、舆情分析，输出 AIVO 评分报告。 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`growth-hacker`](./experts/growth-hacker/) | [增长黑客](./experts/growth-hacker/) | 用数据驱动的实验方法论找到未开发的增长渠道，实现指数级增长 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要环境变量：`IMA_OPENAPI_APIKEY` | 2026-08-13 |
| [`identity-graph-operator`](./experts/identity-graph-operator/) | [身份图谱运营师](./experts/identity-graph-operator/) | 构建维护用户身份图谱系统，实现跨平台身份识别 | 无 | 2026-08-13 |
| [`jiayi-ads-analytics-expert`](./experts/jiayi-ads-analytics-expert/) | [广告投放操盘专家](./experts/jiayi-ads-analytics-expert/) | 不止分析，更能直接操盘——通过API调价、暂停词、加否词、改预算、上下创意，五大广告平台一句话搞定 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`GOOGLE_ADS_CLIENT_SECRET`、`GOOGLE_ADS_DEVELOPER_TOKEN`、`GOOGLE_ADS_REFRESH_TOKEN`、`MICROSOFT_ADS_DEVELOPER_TOKEN`、`TENCENT_AD_ACCESS_TOKEN`、`TENCENT_AD_CLIENT_SECRET` | 2026-07-22 |
| [`linked-in-content-creator`](./experts/linked-in-content-creator/) | [LinkedIn内容创作者](./experts/linked-in-content-creator/) | 精通LinkedIn专业社交平台内容策略，帮助建立思想领袖地位 | 无 | 2026-08-13 |
| [`livestream-ecommerce-coach`](./experts/livestream-ecommerce-coach/) | [直播电商教练](./experts/livestream-ecommerce-coach/) | 精通直播带货全链路运营，从话术到投流帮助实现GMV突破 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`market-analysis-cn`](./experts/market-analysis-cn/) | [市场分析专家](./experts/market-analysis-cn/) | 聚焦市场趋势、竞品对标与用户行为洞察，输出SWOT分析与战略建议，助力企业做出明智商业决策。 | 无 | 2026-07-21 |
| [`marketing-campaign-team`](./experts/marketing-campaign-team/) | [营销战役团队](./experts/marketing-campaign-team/) | 由营销总监领导的 4 人营销专家团队：内容创作者（博客/邮件/社媒/品牌声音）、活动策划师（战役策略/受众/渠道/预算）、SEO 专家（技术审计/内容优化/效果分析）和品牌分析师… | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`marketing-growth-team`](./experts/marketing-growth-team/) | [营销增长专家团](./experts/marketing-growth-team/) | fCMO 级全栈营销增长团队：转化率优化、SEO 与内容策略、增长工程、数据归因分析与策略规划，全方位助力 SaaS 产品增长 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-08-05 |
| [`nges-healthcare-marketing-team`](./experts/nges-healthcare-marketing-team/) | [腾讯健康NGES医药营销专家团](./experts/nges-healthcare-marketing-team/) | 由医药营销智能协调官统一调度的医药营销专家团，整合HCP客户洞察、互动病例生成、学术物料生成、医学内容二创、合规审核五大能力，覆盖从客户情报分析到内容生产到合规检测的全流程。企业… | 需要微信/企微相关凭证或扫码登录 | 2026-10-04 |
| [`paid-media-auditor`](./experts/paid-media-auditor/) | [付费媒体审计师](./experts/paid-media-auditor/) | 深度审计广告投放数据和预算分配，找出被浪费的广告费 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`ppc-bidding-strategist`](./experts/ppc-bidding-strategist/) | [PPC竞价广告策略师](./experts/ppc-bidding-strategist/) | 精通Google Ads和百度竞价，以最低点击成本获取高质量流量 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`private-domain-marketing-expert`](./experts/private-domain-marketing-expert/) | [私域营销专家](./experts/private-domain-marketing-expert/) | 深谙私域运营增长，盘活现有数据资源、洞察营销机会、实现业绩增长 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`private-domain-operations-expert`](./experts/private-domain-operations-expert/) | [私域运营专家](./experts/private-domain-operations-expert/) | 精通微信私域流量池搭建运营，将公域流量沉淀为私域资产 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`programmatic-ad-buyer`](./experts/programmatic-ad-buyer/) | [程序化广告买手](./experts/programmatic-ad-buyer/) | 精通程序化广告购买和DSP平台，通过算法实现大规模精准投放 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`reddit-community-builder`](./experts/reddit-community-builder/) | [Reddit社区建设者](./experts/reddit-community-builder/) | 深谙Reddit社区文化，在全球最大论坛上建立真实社区影响力 | 需要 GitHub Token 或 `gh auth login` | 2026-08-13 |
| [`search-term-analyst`](./experts/search-term-analyst/) | [搜索词分析师](./experts/search-term-analyst/) | 深度分析搜索词数据，挖掘用户真实搜索意图 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器；需要环境变量：`TAVILY_API_KEY` | 2026-08-13 |
| [`seo-content-team`](./experts/seo-content-team/) | [SEO 内容营销团队](./experts/seo-content-team/) | 7位专业角色分5阶段协作：关键词研究、SEO长文创作、技术优化、内容编辑、链接策略、转化率分析，全流程自动化产出高质量SEO内容 | 无 | 2026-07-22 |
| [`seo-expert`](./experts/seo-expert/) | [SEO专家](./experts/seo-expert/) | 精通Google搜索算法和技术SEO，让网站在搜索结果中稳居前列 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`social-ad-strategist`](./experts/social-ad-strategist/) | [社交广告策略师](./experts/social-ad-strategist/) | 精通社交平台广告投放，以精准定向实现最优获客成本 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`social-engagement-team`](./experts/social-engagement-team/) | [社媒互动增长专家团](./experts/social-engagement-team/) | 通过智能化互动自动化、AI评论运营、高转化信号挖掘和品牌舆情监控，安全高效提升社交媒体互动效果，覆盖14+全球主流平台 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`social-media-strategist`](./experts/social-media-strategist/) | [社交媒体策略师](./experts/social-media-strategist/) | 全面统筹多平台社交媒体策略，让品牌在每个平台发出最强音 | 无 | 2026-08-13 |
| [`trend-hunter`](./experts/trend-hunter/) | [自媒体热点雷达与内容增长官](./experts/trend-hunter/) | 追踪微博抖音小红书全网热搜，关键词过滤加竞品监控，从选题文案到视频与全平台分发，打通内容全链路 | 需要微信/企微相关凭证或扫码登录 | 2026-07-31 |
| [`wechat-channels-strategist`](./experts/wechat-channels-strategist/) | [微信视频号运营策略师](./experts/wechat-channels-strategist/) | 精通视频号社交推荐与生态联动，专注内容策划、直播带货、社交裂变与私域闭环，助力视频号从0到1增长 | 需要微信/企微相关凭证或扫码登录 | 2026-07-31 |

### 行业顾问（35）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`ask-liuxiaopai`](./experts/ask-liuxiaopai/) | [产品顾问](./experts/ask-liuxiaopai/) | Raphael AI 创始人刘小排的数字分身，office-hours 风格陪你拆 idea：钉死具体的人、真痛点、第一笔钱、第一批用户在哪，再给一件今晚就能做的事。 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`chaogeek-kongming`](./experts/chaogeek-kongming/) | [苏格拉底式AI思维搭子](./experts/chaogeek-kongming/) | 一人公司认知反缴械思维搭子：少问但问到根，补上下文、对齐意图，帮你驾驭智能体不外包判断力。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`chuangye-manor`](./experts/chuangye-manor/) | [创业伙伴](./experts/chuangye-manor/) | 林老师分身+读书伙伴。送《创业可以学》，陪创业者读书，从读书中听痛点，痛点匹配时自然引出课程咨询。擅长GTM落地、敢见客户情绪层突破、顺序判断。 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`consulting-partners`](./experts/consulting-partners/) | [战略咨询合伙人](./experts/consulting-partners/) | 假设驱动的战略顾问，按需破题、取证、测算与撰写，产出证据扎实的决策报告与专业级PPT | 无 | 2026-08-13 |
| [`family-education-ma`](./experts/family-education-ma/) | [家庭教育专家](./experts/family-education-ma/) | 腾讯未保营地8年一线实践，融合三大循证体系，为家长提供亲子沟通、沉迷干预、家庭成长咨询 | 无 | 2026-07-22 |
| [`fbsir-eight-seat-board`](./experts/fbsir-eight-seat-board/) | [独董会](./experts/fbsir-eight-seat-board/) | 福帮手经营决策独立审议专家团｜按案组建必要席位，独立判断、交叉质询、保留异议，交付可追溯行动备忘录 | 无（可选 API/账号以增强能力） | 2026-08-17 |
| [`fbsir-industry-scene-researcher`](./experts/fbsir-industry-scene-researcher/) | [行业场景研究员](./experts/fbsir-industry-scene-researcher/) | 围绕一个行业场景定位关键工作流缺口，并交付补位卡、3天行动计划、项目动作执行包和下一步建议。 | 可能需要启用对应 MCP / 连接器 | 2026-07-23 |
| [`fbsir-super-independent-board`](./experts/fbsir-super-independent-board/) | [超级独董会](./experts/fbsir-super-independent-board/) | 单一AI独立决策审议官，非法定董事会；挑战偏见、核验证据，交付可执行、可复审的决策产物。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`fbsir-super-partner`](./experts/fbsir-super-partner/) | [超级合伙人\|魔镜行动](./experts/fbsir-super-partner/) | 福帮手超级伙伴：一个直接交付可用成果的执行伙伴，可用时完成安全的宿主操作并验证结果。 | 需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`fortune-consultant`](./experts/fortune-consultant/) | [赛博神算子](./experts/fortune-consultant/) | 传统命理参考工具——八字紫微排盘、塔罗梅花起卦、农历黄历查询，多体系交叉参考，仅供娱乐。 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-08-13 |
| [`fortune-master`](./experts/fortune-master/) | [严谨专业的命理咨询师](./experts/fortune-master/) | 用规则引擎精确排盘八字、紫微、奇门、六爻，再由AI理性解读，助你审慎看待人生格局与运势决策。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-31 |
| [`gaokao-advisor`](./experts/gaokao-advisor/) | [高考我帮你](./experts/gaokao-advisor/) | 辅助检索高考知识库并调用分数线、一分一段能力，整理带来源的真题、高校专业和志愿参考；同时提供全流程志愿填报引导，产出可转发的腾讯文档志愿报告 | 需要大模型 API Key（OpenAI/Anthropic 等） | 2026-07-28 |
| [`indie-founder-coach`](./experts/indie-founder-coach/) | [独立创业教练](./experts/indie-founder-coach/) | 信奉精益创业与自力更生理念，帮助独立创业者用最少资源从0到1构建可持续盈利事业，覆盖创业全旅程关键决策 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`innovation-startup-mentor`](./experts/innovation-startup-mentor/) | [大学生创新创业导师](./experts/innovation-startup-mentor/) | 以落地五关与最小闭环法，帮大学生把双创项目从想法推到落地：痛点验证、商业补全、评委预检，步步可执行。 | 无 | 2026-08-14 |
| [`job-companion-team`](./experts/job-companion-team/) | [求职陪跑团](./experts/job-companion-team/) | 5 角色陪跑型专家团，7 阶段接力覆盖自我盘点、目标定位、简历打磨、面试陪练、谈薪决策与入职复盘全流程。 | 无 | 2026-07-30 |
| [`ket-prep-team`](./experts/ket-prep-team/) | [KET备考专家团](./experts/ket-prep-team/) | 剑桥认证考官领衔，为小学生提供KET全流程备考：学情测评、词汇语法地基、听说读写专项提分、考前冲刺模考，助力Merit（优秀）/Distinction（卓越）达标。 | 无 | 2026-07-22 |
| [`lazy-travel-planner`](./experts/lazy-travel-planner/) | [懒人出游规划师](./experts/lazy-travel-planner/) | 专注国内3-7天2-4人自由行，整合实时口碑与一手数据，一站式产出含地图、预算与防坑的可落地行程书。 | 需要 12306 账号登录 | 2026-07-31 |
| [`liuxue-yanxue-expert`](./experts/liuxue-yanxue-expert/) | [留学研学专家](./experts/liuxue-yanxue-expert/) | 面向家庭生成留学研学首轮规划，兼顾高考窗口、预算风险、路径备选与后续承接行动建议。 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`mentougou-business-guide`](./experts/mentougou-business-guide/) | [门头沟区营商政策顾问](./experts/mentougou-business-guide/) | 门头沟区营商政策专家，提供免费注册地址、税收筹划、补贴匹配、人才政策等一站式创业咨询服务 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-07 |
| [`metamorphosis-practitioner`](./experts/metamorphosis-practitioner/) | [创业心态陪伴者](./experts/metamorphosis-practitioner/) | 不是导师，是走过你想走的路的人。通过分享创业经历帮创业者觉醒心态问题，不说教只分享，让用户自己感悟。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`opc-team`](./experts/opc-team/) | [一人公司专家团](./experts/opc-team/) | 基于由Easy创作的《一人企业方法论》，9位专家陪你走完从资源盘点、利基定位到MVP、转化、复盘的一人公司全流程共创 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`panshi-customer-visit-agent`](./experts/panshi-customer-visit-agent/) | [跟进拜访助手](./experts/panshi-customer-visit-agent/) | 磐石官方AI助手，查询跟进与拜访打卡，将iWiki/腾讯文档/企微文档或粘贴文本同步录入磐石CRM。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`OMP_SERVICE_TOKEN`、`TENCENT_DOCS_TOKEN` | 2026-07-31 |
| [`paper-topic-selection`](./experts/paper-topic-selection/) | [选题顾问（WANFANG TOPIC）](./experts/paper-topic-selection/) | 基于万方数据帮你做论文选题：检索文献、推荐方向、评估新颖性、生成标题、出领域报告。说学科方向即可。 | 需要环境变量：`APP_KEY` | 2026-08-13 |
| [`personal-fitness-coach`](./experts/personal-fitness-coach/) | [私人健身营养教练](./experts/personal-fitness-coach/) | 专业务实的私人健身教练，制定可执行的训练计划、动作指导与饮食宏量方案，安全第一，鼓励但不废话。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`DEMO_KEY`、`USDA_API_KEY` | 2026-07-31 |
| [`skillhub-charity-expert-team`](./experts/skillhub-charity-expert-team/) | [技术公益专家团](./experts/skillhub-charity-expert-team/) | 星星带领六位专家，覆盖公益技能或Agent专家的需求分析、编写、测试评审、版权确认与打包交付全流程。 | 可能需要启用对应 MCP / 连接器；需要环境变量：`MCP_AUTH_TOKEN` | 2026-08-11 |
| [`smb-team`](./experts/smb-team/) | [经营总管](./experts/smb-team/) | 经营总管调度四位领域专家，覆盖财务、营收、客户合规和运营，小企业管理一站搞定 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`south-africa-strategy-advisor`](./experts/south-africa-strategy-advisor/) | [南非战略顾问专家](./experts/south-africa-strategy-advisor/) | 专注南非市场的战略顾问，覆盖宏观环境、产业趋势、投资选址、进入模式与风险评估，提供数据驱动决策支持。 | 无 | 2026-08-04 |
| [`study-planner`](./experts/study-planner/) | [学习规划师](./experts/study-planner/) | 严格导师+效率工具，帮你把模糊的备考目标变成可执行、可追踪、可调整的学习计划，不废话，只做实事。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`BAIDU_API_KEY` | 2026-07-31 |
| [`tanyuan-cultural-heritage-expert`](./experts/tanyuan-cultural-heritage-expert/) | [腾讯探元文博专家](./experts/tanyuan-cultural-heritage-expert/) | 基于腾讯探元文博知识库，提供文物与世界遗产查询、知识问答、文物对比、文博攻略及研学方案等专业服务。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-07-30 |
| [`tc-chengxin-travel-expert`](./experts/tc-chengxin-travel-expert/) | [同程旅行助手](./experts/tc-chengxin-travel-expert/) | 同程官方服务，可一键领取优惠券和红包，查询机票、火车、酒店、景点、规划旅行。我会结合实时旅行资源与账号权益，为您快速找到合适的出行选择，让每一次出发更简单、更省心。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`terminal-veteran`](./experts/terminal-veteran/) | [终端产业分析师](./experts/terminal-veteran/) | 近三十年终端老兵，11条铁律+三层方法论，厂商策略/渠道选品/投资分析+行业报告 | 无 | 2026-07-29 |
| [`tripstar-agent`](./experts/tripstar-agent/) | [旅游攻略管家](./experts/tripstar-agent/) | 生活服务管家，一站式搞定行程规划、景点/酒店/天气/预算与美团红包领取 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要 12306 账号登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`AUTH_SCRIPT`、`USER_TOKEN` | 2026-07-23 |
| [`vietnam-public-affairs`](./experts/vietnam-public-affairs/) | [越南公共事务专家](./experts/vietnam-public-affairs/) | 精通越南政府关系、政策解读、监管沟通、行业协会、公共舆论、社会责任、媒体关系和危机公关 | 无 | 2026-08-04 |
| [`workbuddy-universal-mentor`](./experts/workbuddy-universal-mentor/) | [WorkBuddy 全能导师](./experts/workbuddy-universal-mentor/) | WorkBuddy实战教练：覆盖入门引导、场景匹配、实战案例、Skill开发与自动化答疑全链路。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要 GitHub Token 或 `gh auth login`；需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`API_KEY`、`GITHUB_TOKEN` | 2026-10-04 |
| [`worldcup-buddy`](./experts/worldcup-buddy/) | [世界杯看球搭子](./experts/worldcup-buddy/) | 陪你看2026世界杯，懂球随性有料：查赛程比分、赛后复盘，还能算胜率、爆冷概率和晋级形势。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`API_KEY` | 2026-07-31 |

### 运营人力（15）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`career-broker`](./experts/career-broker/) | [鹅厂职业经纪人](./experts/career-broker/) | 陪你梳理职业画像，讨论发展与转型方向，并推荐课程、经验文章、内部案例和活水机会。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`corporate-training-designer`](./experts/corporate-training-designer/) | [企业培训设计师](./experts/corporate-training-designer/) | 设计系统化企业培训课程和学习路径，让员工技能快速提升 | 需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`customer-support-expert`](./experts/customer-support-expert/) | [客户支持专家](./experts/customer-support-expert/) | 将每次沮丧的用户互动转化为忠实拥护者，用卓越服务创口碑 | 无 | 2026-08-13 |
| [`fbsir-beike-yi`](./experts/fbsir-beike-yi/) | [备课易](./experts/fbsir-beike-yi/) | 在本地备课工作区读懂教材与旧稿，比较教学方案，写回可编辑成果并保留复核与复用线索。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`hr-operations-team`](./experts/hr-operations-team/) | [HR 运营团队](./experts/hr-operations-team/) | 人力资源管理流程化，招聘筛选、薪酬体系设计、组织发展与HR运营流程化管理，助力企业人才战略落地 | 无 | 2026-07-21 |
| [`ihr-ai-interviewer`](./experts/ihr-ai-interviewer/) | [i人事-利唐智语AI面试官](./experts/ihr-ai-interviewer/) | 围绕岗位画像设计面试维度与题库，管理数字人面试模板，校验候选人信息并发起面试，回查面试记录与纪要。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`ihr-conference`](./experts/ihr-conference/) | [i人事-利唐智语AI面谈官](./experts/ihr-conference/) | 提供九大智能面谈大纲与线上实时指引，基于云录制自动生成结构化纪要与待办，全周期辅助管理者高效沟通。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`interview-simulator`](./experts/interview-simulator/) | [面试模拟专家](./experts/interview-simulator/) | 模拟任意职位的真实面试官，覆盖技术产品销售人事等全岗位，提供逐题评分详细反馈与录用建议，助你高效备战面试。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`qingflow-hr-expert`](./experts/qingflow-hr-expert/) | [人力资源数字化专家](./experts/qingflow-hr-expert/) | 轻流MCP直连搭建，覆盖招聘、培训、绩效、入职与人力分析，AI驱动HR数字化转型。 | 需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-31 |
| [`recruitment-expert`](./experts/recruitment-expert/) | [招聘专家](./experts/recruitment-expert/) | 精通人才招聘全流程，为团队找到最佳人才 | 需要飞书应用凭证或用户登录授权 | 2026-08-13 |
| [`resume-assistant`](./experts/resume-assistant/) | [简历优化专家](./experts/resume-assistant/) | 提供百分制专业评分、四十项深度清单润色、岗位匹配定制与多格式导出，全面打造高竞争力求职简历。 | 无（可选 API/账号以增强能力） | 2026-07-21 |
| [`smb-operations`](./experts/smb-operations/) | [组织运营师](./experts/smb-operations/) | 小企业组织运营师，负责招聘入职、工具初始化和业务快照，让运营不掉链子 | 需要飞书应用凭证或用户登录授权；需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`south-africa-hr-admin`](./experts/south-africa-hr-admin/) | [南非人力行政专家](./experts/south-africa-hr-admin/) | 南非人力行政专家，覆盖招聘、薪酬、签证、B-BBEE与劳动合规，可算成本、查费用、生成可视化交付物。 | 无（可选 API/账号以增强能力） | 2026-08-04 |
| [`study-abroad-consultant`](./experts/study-abroad-consultant/) | [留学顾问](./experts/study-abroad-consultant/) | 精通各国留学申请流程和院校信息 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`supply-chain-strategist`](./experts/supply-chain-strategist/) | [供应链策略师](./experts/supply-chain-strategist/) | 优化供应链每个环节，实现成本效率韧性的最佳平衡 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY`、`TMAP_WEBSERVICE_KEY` | 2026-08-13 |

### 金融投资（39）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`a-share-analysis`](./experts/a-share-analysis/) | [A股研究团队](./experts/a-share-analysis/) | 8位研究专家支持6个预设工作流编排，覆盖宏观策略、盘面解读、个股深度、估值定价、产业链映射、资金追踪、风险诊断 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`accounts-payable-agent`](./experts/accounts-payable-agent/) | [应付账款代理](./experts/accounts-payable-agent/) | 自动化处理应付账款流程，确保付款准确及时 | 无 | 2026-08-13 |
| [`believe-in-light`](./experts/believe-in-light/) | [相信光么](./experts/believe-in-light/) | 光模块产业链信号监控专家团。主理人 + 6位成员Agent 三端采集信号，因果验证+权重校准，三层嵌套输出景气度评级。 | 需要大模型 API Key（OpenAI/Anthropic 等）；可能需要启用对应 MCP / 连接器 | 2026-07-27 |
| [`citongshuopro`](./experts/citongshuopro/) | [刺桐说Pro-投资社群嘉宾团](./experts/citongshuopro/) | 模拟真实投资社群运作模式的多智能体投研系统，已接入社群嘉宾数字分身，可7*24为您提供投资咨询服务。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`corp-credit-due-diligence`](./experts/corp-credit-due-diligence/) | [腾讯云天御对公信贷专家](./experts/corp-credit-due-diligence/) | 对公信贷尽调助手，覆盖行业研究、财务核查、实控人画像与风险预警，输出结构化信评报告。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`dd-due-diligence-team`](./experts/dd-due-diligence-team/) | [AI尽调专家团](./experts/dd-due-diligence-team/) | 银行对公授信尽调专家团：主理人按七步流程统筹进件/核验/画像/财务/经营/行业/风险/报告八岗协同。 | 需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-10-04 |
| [`earnings-reviewer`](./experts/earnings-reviewer/) | [财报研究员](./experts/earnings-reviewer/) | 资深季报复核分析师,读财报电话会和公告更新覆盖模型,产出季报后记、方差表与估值调整,供研究部门沿用。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`equity-research`](./experts/equity-research/) | [股票研究专家](./experts/equity-research/) | 全面的股票研究工具集：财报分析、首次覆盖报告、DCF与可比估值、多空推介、投资备忘录、事件情景分析、组合风险管理，覆盖完整买方卖方研究工作流 | 无（可选 API/账号以增强能力） | 2026-08-03 |
| [`fin-research-expert`](./experts/fin-research-expert/) | [股市投研分析师](./experts/fin-research-expert/) | 连接同舟公开投研能力，稳定生成个股、行业、事件与研报的证据化简报和可复核投研案例页面 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要 GitHub Token 或 `gh auth login`；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器 | 2026-07-23 |
| [`finance`](./experts/finance/) | [财务会计专家](./experts/finance/) | 财务会计工具集：月末结账、日记账分录、账户核对、财务报表生成、差异分析和 SOX 审计支持 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`financial-analysis`](./experts/financial-analysis/) | [金融建模专家](./experts/financial-analysis/) | 核心金融建模工具：DCF 估值、可比公司分析、LBO 模型、三张表模型、竞争格局分析和 PPT 质检 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`financial-tracker`](./experts/financial-tracker/) | [财务追踪师](./experts/financial-tracker/) | 精准追踪项目和业务的财务数据，确保每笔收支清晰透明 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`fund-research-analyst`](./experts/fund-research-analyst/) | [基金投研分析师](./experts/fund-research-analyst/) | 穿透基金业绩、回撤、夏普比率、持仓与基金经理等多维数据，横向对比帮你找出值得长期持有的好基金 | 需要环境变量：`AUTH_GATEWAY_PORT` | 2026-07-31 |
| [`gl-reconciler`](./experts/gl-reconciler/) | [总账对账师](./experts/gl-reconciler/) | 基金后台日终与月末对账专员,在总账与子账之间找出差异、追溯到源交易、归类 timing/reclass/FX 等原因并出具可签核清单。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`investment-banking`](./experts/investment-banking/) | [投资银行专家](./experts/investment-banking/) | 全能投资银行专家：交易材料制作、估值建模（Comps/DCF/LBO/三表）、资本市场融资、买方尽调分析、重组与回收瀑布、交易全流程执行 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`investment-masters-team`](./experts/investment-masters-team/) | [投资大师专家团](./experts/investment-masters-team/) | 13位传奇投资哲学家 + 6位专业分析师并行分析，风险管理师评估约束，投资组合经理信号聚合投票，多角度投资分析参考 | 无 | 2026-07-22 |
| [`kyc-screener`](./experts/kyc-screener/) | [客户合规官](./experts/kyc-screener/) | 客户准入合规分析师,解析 KYC 材料、跑规则引擎、比对制裁与 PEP 名单,并按风险等级形成可交合规签核的升级包。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`mai-deal-advisor`](./experts/mai-deal-advisor/) | [项目来了，先把路理清](./experts/mai-deal-advisor/) | 接住真实并购项目：拆解资料、画交易结构、核数字与股权，也梳理买方、资金与推进路径。 | 需要登录 / OAuth / 扫码授权 | 2026-10-04 |
| [`market-researcher`](./experts/market-researcher/) | [行业研究员](./experts/market-researcher/) | 面向分析师与基金经理的行业研究分析师,产出行业全景、竞争格局、可比公司估值表与主题选股清单等研究交付物。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`meeting-prep-agent`](./experts/meeting-prep-agent/) | [会前准备助理](./experts/meeting-prep-agent/) | 理财顾问的会议准备搭档,在每次客户见面前汇总关系历史、持仓近况、市场要闻与议题清单,让顾问 5 分钟进入状态。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`model-builder`](./experts/model-builder/) | [财务建模师](./experts/model-builder/) | 专业财务建模师,在 Excel 中从零搭建 DCF、LBO、三张表模型与可比公司估值,公式全链接、可追溯、机构级品控。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`month-end-closer`](./experts/month-end-closer/) | [月末结账会计](./experts/month-end-closer/) | 财务负责人的月末关账搭档,按清单跑应计、滚动表、差异说明,把关账包整理好交给 controller 签核。 | 可能需要启用对应 MCP / 连接器 | 2026-07-21 |
| [`new-share-expert`](./experts/new-share-expert/) | [新股专家](./experts/new-share-expert/) | 面向A股新股的事实型助手：多源交叉校验、板块规则区分、精准K线与分时绘制，仅出客观数据不打分不推荐。 | 无（可选 API/账号以增强能力） | 2026-07-30 |
| [`pitch-agent`](./experts/pitch-agent/) | [投行交易助理](./experts/pitch-agent/) | 资深投行关联人,从零搭建 pitch 初稿——可比公司、先例交易、DCF、足球场估值图,并生成绑在模型上的品牌化 PPT。 | 可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`private-equity`](./experts/private-equity/) | [私募股权专家](./experts/private-equity/) | 私募股权工具集：Deal Sourcing、项目筛选、尽调清单、IC Memo、单位经济学分析、回报分析、投后管理和价值创造方案 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`roadshow-research-team`](./experts/roadshow-research-team/) | [资本市场路演研究团](./experts/roadshow-research-team/) | 多专家协作标的研报：多源解析、行业对比、财报三表（上市+未上市）、路演研报、股价关联，模板出报告。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`IWENCAI_API_KEY` | 2026-07-29 |
| [`smart-stock-analyst`](./experts/smart-stock-analyst/) | [多市场智能股票分析师](./experts/smart-stock-analyst/) | AI驱动多市场股票分析专家，内置缠论、波浪等15+策略，默认输出精美交互式HTML决策仪表盘报告 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`smb-finance`](./experts/smb-finance/) | [财务管家](./experts/smb-finance/) | 小企业财务管家，一站式搞定现金流预测、逾期追款、毛利分析、月结对账和税务准备 | 需要登录 / OAuth / 扫码授权 | 2026-07-22 |
| [`statement-auditor`](./experts/statement-auditor/) | [LP 报表审核师](./experts/statement-auditor/) | LP 资本账户报表最后把关人,按基金 NAV 反算每条项目、对齐分配与管理费,发差前形成签核建议与异常清单。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`stock-partner-team`](./experts/stock-partner-team/) | [腾讯自选股股票投研专家团](./experts/stock-partner-team/) | 六位投研专家团，兼擅产业策略、信号捕捉、估值定价、逆向布局、基本面与短线，基于实时行情多视角研判。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权；可能需要启用对应 MCP / 连接器；需要环境变量：`WESTOCK_SESSION_KEY` | 2026-10-04 |
| [`strategy-backtest-expert`](./experts/strategy-backtest-expert/) | [量化策略回测师](./experts/strategy-backtest-expert/) | 把自然语言描述的交易策略转成可运行的 Python 回测脚本，输出标准指标、可视化图表、HTML 仪表盘，并给出实现细节、已知偏差和结果解读。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要环境变量：`APIKEY` | 2026-07-22 |
| [`tdx-stock-diagnostician`](./experts/tdx-stock-diagnostician/) | [个股深度诊断师](./experts/tdx-stock-diagnostician/) | 像经验丰富的分析师，对任意A股进行六大模块360度全方位诊断，涵盖基本面、技术面、资金面、事件催化、同业对标，输出专业诊断报告。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`tdx-stock-hunter`](./experts/tdx-stock-hunter/) | [智能选股猎手](./experts/tdx-stock-hunter/) | 基于通达信MCP数据，将自然语言转为多维筛选条件，从5000+A股中按基本面/技术面/资金面/估值做横向分析与综合评分，供用户参考。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`tdx-value-assessor`](./experts/tdx-value-assessor/) | [价值评估师](./experts/tdx-value-assessor/) | 秉承格雷厄姆-巴菲特价值体系，运用15+估值模型，通过护城河评估与多维估值分析，评估企业内在价值与安全边际水平。 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`trading-agent`](./experts/trading-agent/) | [交易分析团队](./experts/trading-agent/) | 13位专业角色分5阶段协作完成投资分析：技术面、基本面、新闻面、情绪面数据采集 → 多空辩论 → 交易决策 → 三方风险评估 → 最终报告，输出 BUY/SELL/HOLD 建议… | 无 | 2026-07-21 |
| [`valuation-reviewer`](./experts/valuation-reviewer/) | [组合估值主管](./experts/valuation-reviewer/) | PE/VC 基金组合估值主管,收 GP 估值包、跑标准估值模板、算基金 NAV 与 LP 分配、出 LP 报告草稿交投资者关系签核。 | 需要微信/企微相关凭证或扫码登录；可能需要启用对应 MCP / 连接器 | 2026-08-13 |
| [`vietnam-finance-tax-expert`](./experts/vietnam-finance-tax-expert/) | [越南财税金融专家](./experts/vietnam-finance-tax-expert/) | 覆盖越南企业税务、会计、银行、外汇与财务合规，提供选址测算、税负计算与ODI落地等可量化交付物。 | 无（可选 API/账号以增强能力） | 2026-08-04 |
| [`wealth-management`](./experts/wealth-management/) | [财富管理专家](./experts/wealth-management/) | 财富管理工具集：客户回顾、财务规划、投资组合再平衡、税损收割、投资提案和客户报告生成 | 可能需要启用对应 MCP / 连接器 | 2026-07-22 |
| [`yahoo-finance-cli`](./experts/yahoo-finance-cli/) | [行情洞察与趋势发现专家](./experts/yahoo-finance-cli/) | 查询全球股票实时行情、基本面、财报预期、评级、历史走势与估值洞察，发现热门趋势标的，支持模糊检索与并排对比。 | 无 | 2026-07-22 |

### 销售商务（17）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`bidding-strategist`](./experts/bidding-strategist/) | [投标与方案策略师](./experts/bidding-strategist/) | 半策略师半故事讲述者，用叙事赢得竞标：提炼赢标主题、架构三幕式方案、打磨执行摘要，让方案赢在说服力。 | 无 | 2026-07-31 |
| [`cordys-crm`](./experts/cordys-crm/) | [Cordys CRM L2C 管道专家](./experts/cordys-crm/) | 角色感知型CRM助手，覆盖线索到现金全链路。自动识别角色，提供查询、风险预警与漏斗分析。 | 需要环境变量：`CORDYS_ACCESS_KEY`、`CORDYS_SECRET_KEY` | 2026-08-13 |
| [`deal-strategist`](./experts/deal-strategist/) | [交易策略师](./experts/deal-strategist/) | 精通复杂交易策略制定和推进，帮助销售团队赢得大单 | 无 | 2026-08-13 |
| [`discovery-coach`](./experts/discovery-coach/) | [需求发现教练](./experts/discovery-coach/) | 训练销售掌握深度需求挖掘技巧，发现真正的业务痛点 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`enterprise-account-strategist`](./experts/enterprise-account-strategist/) | [大客户策略师](./experts/enterprise-account-strategist/) | 精通大客户经营和账户扩展策略，将客户发展为长期战略伙伴 | 无 | 2026-08-13 |
| [`government-digital-presales-consultant`](./experts/government-digital-presales-consultant/) | [政府数字化售前顾问](./experts/government-digital-presales-consultant/) | 精通政府数字化转型需求和采购流程 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`industrial-park-investment-attraction-expert`](./experts/industrial-park-investment-attraction-expert/) | [产业园招商专家](./experts/industrial-park-investment-attraction-expert/) | 仅用公开资料，按园区目标找对企业，逐家核验来源、适配理由、反证与未知，快速形成可行动名单。 | 需要登录 / OAuth / 扫码授权 | 2026-07-29 |
| [`linkfox-expert-amazon-listing-specialist`](./experts/linkfox-expert-amazon-listing-specialist/) | [亚马逊 Listing 优化专家](./experts/linkfox-expert-amazon-listing-specialist/) | 聚焦亚马逊Listing全链路诊断与创作，结合竞品、关键词、评论和合规证据，输出可发布文案。 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`LINKFOXAGENT_API_KEY`、`LINKFOX_AGENT_API_KEY` | 2026-10-04 |
| [`meituan-living-assistant`](./experts/meituan-living-assistant/) | [美团生活助手](./experts/meituan-living-assistant/) | 帮您一键领取美团优惠券，搜索附近团购美食并下单，探索今日活动，覆盖餐饮饮品等生活服务，省钱省心。 | 需要登录 / OAuth / 扫码授权；需要环境变量：`DEVICE_TOKEN`、`USER_TOKEN` | 2026-07-22 |
| [`outbound-strategist`](./experts/outbound-strategist/) | [外呼策略师](./experts/outbound-strategist/) | 精通外呼和冷启动销售策略，让陌生人30秒内愿意继续倾听 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`presales-technical-consultant`](./experts/presales-technical-consultant/) | [售前技术顾问](./experts/presales-technical-consultant/) | 架起技术与商业的桥梁，帮助客户理解解决方案的价值 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录 | 2026-08-13 |
| [`proposal-strategist`](./experts/proposal-strategist/) | [方案策划师](./experts/proposal-strategist/) | 精通销售提案和方案设计，将价值转化为无法拒绝的商业论证 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要登录 / OAuth / 扫码授权；需要环境变量：`BROWSER_USE_API_KEY` | 2026-08-13 |
| [`sales-battle-team`](./experts/sales-battle-team/) | [销售作战团队](./experts/sales-battle-team/) | 销售攻坚体系，客户研究锁定目标、外联策略提升触达、竞品情报预警风险、销售预测优化资源分配 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`sales-coach`](./experts/sales-coach/) | [销售教练](./experts/sales-coach/) | 全栈销售教练：从能力培养到实战执行——会议准备、交易策略、商业案例、竞品分析、通话复盘，用苏格拉底式提问驱动 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`sales-pipeline-analyst`](./experts/sales-pipeline-analyst/) | [销售管道分析师](./experts/sales-pipeline-analyst/) | 用数据驱动方法分析销售管道健康度，让预测从猜测变科学 | 无 | 2026-08-13 |
| [`smb-revenue`](./experts/smb-revenue/) | [营收增长师](./experts/smb-revenue/) | 小企业营收增长师，从线索打分到内容策略再到营销活动，一条龙驱动营收增长 | 需要微信/企微相关凭证或扫码登录 | 2026-07-22 |
| [`uupt-delivery`](./experts/uupt-delivery/) | [同城配送助手](./experts/uupt-delivery/) | 提供UU跑腿同城即时配送与现场帮帮服务，支持订单询价、发单下单、订单查询取消、跑男实时追踪及优惠券领取。 | 需要微信/企微相关凭证或扫码登录 | 2026-10-04 |

### 项目质量（23）

| 目录 | 名称 | 用来做什么 | 前置条件 | 最后更新 |
|------|------|------------|----------|----------|
| [`accessibility-auditor`](./experts/accessibility-auditor/) | [无障碍审计师](./experts/accessibility-auditor/) | 按WCAG标准审计界面可访问性，确保每个用户都能使用产品 | 无 | 2026-08-13 |
| [`agent-orchestrator`](./experts/agent-orchestrator/) | [智能体编排师](./experts/agent-orchestrator/) | 精通多智能体系统的编排和协调，让AI团队高效协作 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`ai-meeting-notes`](./experts/ai-meeting-notes/) | [会议纪要提取专家](./experts/ai-meeting-notes/) | 粘贴会议笔记或转写文本，自动提炼摘要、负责人、截止日期与行动项，归档可检索并联动待办清单跟踪执行。 | 无 | 2026-07-22 |
| [`api-testing-expert`](./experts/api-testing-expert/) | [API测试专家](./experts/api-testing-expert/) | 在用户之前发现API的每一个缺陷，确保接口稳定性和正确性 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`document-generation-expert`](./experts/document-generation-expert/) | [文档生成专家](./experts/document-generation-expert/) | 自动化生成各类业务文档，大幅提升文档创建效率 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`document-skills`](./experts/document-skills/) | [文档处理专家](./experts/document-skills/) | 文档处理套件：Excel 电子表格、Word 文档、PowerPoint 演示文稿和 PDF 文件的创建、编辑与转换 | 无 | 2026-07-31 |
| [`evidence-collector`](./experts/evidence-collector/) | [证据收集员](./experts/evidence-collector/) | 不放过任何没有截图证据的问题，用视觉证据确保缺陷无处遁形 | 无 | 2026-08-13 |
| [`executive-summary-generator`](./experts/executive-summary-generator/) | [战略报告顾问](./experts/executive-summary-generator/) | 将冗长报告浓缩为高管可快速消化的精华摘要，节省每分钟 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`experiment-tracking-manager`](./experts/experiment-tracking-manager/) | [实验追踪管理者](./experts/experiment-tracking-manager/) | 系统化管理实验全生命周期，确保每个实验有假设有执行有结论 | 无 | 2026-08-13 |
| [`internal-comms`](./experts/internal-comms/) | [内部沟通专家](./experts/internal-comms/) | 内部沟通模板专家：状态报告、领导汇报、公司简报、FAQ、事故报告和项目更新 | 无 | 2026-07-22 |
| [`jira-workflow-admin`](./experts/jira-workflow-admin/) | [Jira工作流管理员](./experts/jira-workflow-admin/) | 精通Jira配置和敏捷工作流设计，让工具真正服务于团队效率 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`openspec-doc-team`](./experts/openspec-doc-team/) | [专业文档生成团队](./experts/openspec-doc-team/) | 企业级长文档生成，4角色协作完成深度调研、大纲规划、内容撰写与合规审核全流程 | 无（可选 API/账号以增强能力） | 2026-07-22 |
| [`performance-testing-expert`](./experts/performance-testing-expert/) | [性能测试专家](./experts/performance-testing-expert/) | 精通性能测试和基准评估，用数据证明性能改进而非凭感觉 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`project-shepherd`](./experts/project-shepherd/) | [项目牧羊人](./experts/project-shepherd/) | 温和但坚定地引导项目按计划推进，确保里程碑准时交付 | 无 | 2026-08-13 |
| [`reality-checker`](./experts/reality-checker/) | [现实检查员](./experts/reality-checker/) | 默认认为一切需要更多证据，需要压倒性证据才批准生产就绪 | 无 | 2026-08-13 |
| [`senior-project-manager`](./experts/senior-project-manager/) | [高级项目经理](./experts/senior-project-manager/) | 10年以上项目管理经验，精通瀑布和敏捷，是复杂项目定海神针 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`studio-operations-manager`](./experts/studio-operations-manager/) | [工作室运营管理者](./experts/studio-operations-manager/) | 全面管理工作室日常运营，从资源调配到流程优化 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`studio-producer`](./experts/studio-producer/) | [工作室制片人](./experts/studio-producer/) | 统筹项目从立项到交付的全过程，平衡创意预算和时间 | 无 | 2026-08-13 |
| [`technical-documentation-engineer`](./experts/technical-documentation-engineer/) | [技术文档工程师](./experts/technical-documentation-engineer/) | 将复杂技术概念转化为清晰准确的文档，让技术知识可传播 | 需要大模型 API Key（OpenAI/Anthropic 等）；需要微信/企微相关凭证或扫码登录；需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`test-results-analyst`](./experts/test-results-analyst/) | [测试结果分析师](./experts/test-results-analyst/) | 像侦探解读证据一样分析测试结果，发现隐藏的质量问题 | 需要登录 / OAuth / 扫码授权 | 2026-08-13 |
| [`tool-evaluation-expert`](./experts/tool-evaluation-expert/) | [工具评估专家](./experts/tool-evaluation-expert/) | 系统化评估推荐最适合团队的工具，避免浪费时间在错误工具上 | 无（可选 API/账号以增强能力） | 2026-08-13 |
| [`webapp-testing`](./experts/webapp-testing/) | [Web应用测试专家](./experts/webapp-testing/) | Web 应用测试助手，引导用户完成 Web 应用的启动、配置和测试流程 | 需要登录 / OAuth / 扫码授权 | 2026-07-21 |
| [`workflow-optimization-expert`](./experts/workflow-optimization-expert/) | [工作流优化专家](./experts/workflow-optimization-expert/) | 找到瓶颈修复流程自动化一切，让团队效率最大化 | 无（可选 API/账号以增强能力） | 2026-08-13 |

## 4. 插件市场 `plugins/`

- 官方插件 `plugins/codebuddy-plugins-official/plugins/`：**60**
- 官方外部插件 `plugins/codebuddy-plugins-official/external_plugins/`：**149**（已列入官方 marketplace.json，原清单缺失，本次补录）
- 团队插件 `plugins/cb_teams_marketplace/plugins/`：**30**

### 官方插件

| 目录 | 说明 | 最后更新 |
|------|------|----------|
| [`agent-browser`](./plugins/codebuddy-plugins-official/plugins/agent-browser/) | CodeBuddy 浏览器自动化插件，基于 vercel-labs/agent-browser CLI。 | 2026-07-21 |
| [`agent-sdk-dev`](./plugins/codebuddy-plugins-official/plugins/agent-sdk-dev/) | 用于创建和验证 CodeBuddy Agent SDK 应用的综合开发插件。 | 2026-07-21 |
| [`agent-team-agile-workflow`](./plugins/codebuddy-plugins-official/plugins/agent-team-agile-workflow/) | 完整的 BMAD 敏捷工作流插件，包含角色化代理（PO、架构师、SM、开发、QA）和交互式审批流程 | 2026-07-21 |
| [`algorithmic-art`](./plugins/codebuddy-plugins-official/plugins/algorithmic-art/) | 使用 p5.js 创建算法艺术，支持种子随机性和交互式参数探索。适用于生成艺术、流场、粒子系统等代码艺术创作。 | 2026-07-21 |
| [`atuin`](./plugins/codebuddy-plugins-official/plugins/atuin/) | 自动拦截 AI 的高危操作，自动阻止 AI 使用有漏洞的组件。腾讯玄武实验室出品。 | 2026-07-21 |
| [`chainguard`](./plugins/codebuddy-plugins-official/plugins/chainguard/) | 自动拦截 AI 依赖安装操作，进行供应链安全审计。 | 2026-07-21 |
| [`clangd-lsp`](./plugins/codebuddy-plugins-official/plugins/clangd-lsp/) | C/C++ Language Server (clangd)，为 CodeBuddy 提供代码智能、诊断和格式化功能。 | 2026-07-21 |
| [`cloudbase`](./plugins/codebuddy-plugins-official/plugins/cloudbase/) | CloudBase AI 开发插件，提供 Web、小程序、云函数、CloudRun、数据库（NoSQL/MySQL）、云存储、AI 模型、UI 设计等全栈开发能力。 | 2026-07-21 |
| [`code-simplifier`](./plugins/codebuddy-plugins-official/plugins/code-simplifier/) | 专注于简化代码以提升清晰度、一致性和可维护性的智能代理,在保留完整功能的前提下优化代码结构。主要关注最近修改的代码。 | 2026-07-21 |
| [`codebuddy-md-management`](./plugins/codebuddy-plugins-official/plugins/codebuddy-md-management/) | CODEBUDDY.md 文件维护工具：审计质量、沉淀会话经验。 | 2026-07-21 |
| [`commit-commands`](./plugins/codebuddy-plugins-official/plugins/commit-commands/) | 简化 git 工作流：提交、推送、建 PR 等快捷命令。 | 2026-07-21 |
| [`context7`](./plugins/codebuddy-plugins-official/plugins/context7/) | Upstash Context7 MCP 服务器，用于查找最新文档。可直接从源代码仓库拉取特定版本的文档和代码示例到 LLM 上下文中。 | 2026-07-21 |
| [`csharp-lsp`](./plugins/codebuddy-plugins-official/plugins/csharp-lsp/) | C# Language Server，为 CodeBuddy 提供代码智能和诊断功能。 | 2026-07-21 |
| [`development-essentials`](./plugins/codebuddy-plugins-official/plugins/development-essentials/) | 核心开发命令套件，提供日常开发所需的所有基础命令。无需工作流开销，直接执行开发任务。 | 2026-07-21 |
| [`doc-coauthoring`](./plugins/codebuddy-plugins-official/plugins/doc-coauthoring/) | 引导用户通过结构化工作流协作撰写文档。适用于编写文档、提案、技术规格、决策文档等结构化内容，帮助高效传递上下文、迭代优化内容并验证文档的可读性。 | 2026-07-21 |
| [`docx`](./plugins/codebuddy-plugins-official/plugins/docx/) | 全面的 Word 文档创建、编辑和分析工具，支持修订跟踪、评论、格式保留和文本提取。用于处理专业 Word 文档(.docx) | 2026-07-21 |
| [`edgeone-makers-tools`](./plugins/codebuddy-plugins-official/plugins/edgeone-makers-tools/) | EdgeOne Makers 官方开发部署技能集。 | 2026-10-04 |
| [`feature-dev`](./plugins/codebuddy-plugins-official/plugins/feature-dev/) | 结构化特性开发工作流，带多个专职 Agent 分工。 | 2026-07-21 |
| [`find-skills`](./plugins/codebuddy-plugins-official/plugins/find-skills/) | 帮助用户发现和安装 AI Agent 技能，支持从 Vercel Skills 和 ClawHub 两个技能仓库搜索和安装 | 2026-07-21 |
| [`firebase`](./plugins/codebuddy-plugins-official/plugins/firebase/) | Google Firebase MCP 集成。管理 Firestore 数据库、身份验证、云函数、托管服务和存储。直接从开发工作流中构建和管理 Firebase 后端。 | 2026-07-21 |
| [`frontend-design`](./plugins/codebuddy-plugins-official/plugins/frontend-design/) | 创建独特的生产级前端界面,具有高设计质量。生成富有创意、精致的代码,避免千篇一律的AI审美。 | 2026-07-21 |
| [`github`](./plugins/codebuddy-plugins-official/plugins/github/) | 官方 GitHub MCP 服务器，用于仓库管理。可直接在 Claude Code 中创建议题、管理拉取请求、审查代码、搜索仓库以及调用 GitHub 完整 API。 | 2026-07-21 |
| [`gitlab`](./plugins/codebuddy-plugins-official/plugins/gitlab/) | GitLab DevOps 平台集成。管理代码仓库、合并请求、CI/CD 流水线、问题和 Wiki。全面访问 GitLab 的 DevOps 生命周期工具。 | 2026-07-21 |
| [`godot-mcp`](./plugins/codebuddy-plugins-official/plugins/godot-mcp/) | Godot 引擎与 AI 助手的 MCP 全面集成。 | 2026-07-21 |
| [`gopls-lsp`](./plugins/codebuddy-plugins-official/plugins/gopls-lsp/) | Go Language Server，为 CodeBuddy 提供代码智能、重构和分析功能。 | 2026-07-21 |
| [`hookify`](./plugins/codebuddy-plugins-official/plugins/hookify/) | 通过分析对话模式轻松创建自定义钩子，阻止不希望的行为。 | 2026-07-21 |
| [`hot-skills`](./plugins/codebuddy-plugins-official/plugins/hot-skills/) | 精选 7 个高下载量 AI Agent 技能打包成的单个插件。 | 2026-07-21 |
| [`hotskills`](./plugins/codebuddy-plugins-official/plugins/hotskills/) | 精选 7 个高下载量 AI Agent 技能打包成的单个插件（hotskills）。 | 2026-10-04 |
| [`jdtls-lsp`](./plugins/codebuddy-plugins-official/plugins/jdtls-lsp/) | Java Language Server (Eclipse JDT.LS)，为 CodeBuddy 提供代码智能和重构功能。 | 2026-07-21 |
| [`lexiang-knowledge-plugins`](./plugins/codebuddy-plugins-official/plugins/lexiang-knowledge-plugins/) | 乐享知识库, 企业协同知识库，提供获取文档内容与元数据、搜索文档内容、查询知识库与目录结构、创建/编辑/移动文档、管理标签与评论、上传文件及维护附件等知识库操作能力。 | 2026-07-21 |
| [`lua-lsp`](./plugins/codebuddy-plugins-official/plugins/lua-lsp/) | Lua Language Server，为 CodeBuddy 提供代码智能和诊断功能。 | 2026-07-21 |
| [`lucide-icons`](./plugins/codebuddy-plugins-official/plugins/lucide-icons/) | 搜索、下载和自定义 Lucide 图标的技能。 | 2026-07-21 |
| [`magicai-hub`](./plugins/codebuddy-plugins-official/plugins/magicai-hub/) | Godot 4.x 游戏开发 AI 技能工具包。为 CodeBuddy 提供一组专业技能，帮助 AI 更高效地协助 Godot 项目开发。 | 2026-07-21 |
| [`oh-my-codebuddy`](./plugins/codebuddy-plugins-official/plugins/oh-my-codebuddy/) | 完整的 OMC (Oh My CodeBuddy) 插件，包含 agents、commands、skills、hooks、tools 和 MCP servers。提供多代理编排、… | 2026-07-21 |
| [`pdf`](./plugins/codebuddy-plugins-official/plugins/pdf/) | 全面的 PDF 处理工具包，支持提取文本和表格、创建新 PDF、合并/拆分文档、表单填写、加密解密、OCR 扫描等功能 | 2026-07-21 |
| [`php-lsp`](./plugins/codebuddy-plugins-official/plugins/php-lsp/) | PHP Language Server (Intelephense)，为 CodeBuddy 提供代码智能和诊断功能。 | 2026-07-21 |
| [`playwright-cli`](./plugins/codebuddy-plugins-official/plugins/playwright-cli/) | Playwright CLI 及配套技能。 | 2026-07-23 |
| [`plugin-dev`](./plugins/codebuddy-plugins-official/plugins/plugin-dev/) | CodeBuddy 插件开发完整工具包：专家指导与模板。 | 2026-07-21 |
| [`plugin-finder`](./plugins/codebuddy-plugins-official/plugins/plugin-finder/) | 智能插件发现和管理助手，帮助用户从众多插件市场中轻松发现、安装和比较插件。 | 2026-07-21 |
| [`ppt-writer`](./plugins/codebuddy-plugins-official/plugins/ppt-writer/) | 一个功能强大的CodeBuddy Code插件，帮助你快速创建专业、美观、有说服力的PPT演示文稿。 | 2026-07-21 |
| [`pptx`](./plugins/codebuddy-plugins-official/plugins/pptx/) | PowerPoint 演示文稿创建、编辑和分析技能。支持创建新演示文稿、修改内容、处理布局、添加注释或演讲者备注等操作 | 2026-07-21 |
| [`pr-review-toolkit`](./plugins/codebuddy-plugins-official/plugins/pr-review-toolkit/) | PR 审查专用 Agent 合集，覆盖多维度 thorough review。 | 2026-07-21 |
| [`pyright-lsp`](./plugins/codebuddy-plugins-official/plugins/pyright-lsp/) | Python Language Server (Pyright)，为 CodeBuddy 提供静态类型检查和代码智能功能。 | 2026-07-21 |
| [`ralph-loop`](./plugins/codebuddy-plugins-official/plugins/ralph-loop/) | Ralph Wiggum 技术的实现：迭代自指式 AI 开发。 | 2026-07-21 |
| [`requirements-driven-workflow`](./plugins/codebuddy-plugins-official/plugins/requirements-driven-workflow/) | 需求驱动开发工作流，包含 90% 质量门控的实用功能实现流程 | 2026-07-21 |
| [`rust-analyzer-lsp`](./plugins/codebuddy-plugins-official/plugins/rust-analyzer-lsp/) | Rust Language Server，为 CodeBuddy 提供代码智能和分析功能。 | 2026-07-21 |
| [`security-guidance`](./plugins/codebuddy-plugins-official/plugins/security-guidance/) | 安全提醒钩子，在编辑文件时警告潜在的安全问题，包括命令注入、XSS 和不安全的代码模式 | 2026-07-21 |
| [`security-rules`](./plugins/codebuddy-plugins-official/plugins/security-rules/) | 安全三部安全 rules 插件 | 2026-07-21 |
| [`security-scan`](./plugins/codebuddy-plugins-official/plugins/security-scan/) | 一款智能代码安全审计工具，通过 **语义索引 + 多 Agent 并行扫描 + 对抗验证** 实现专业级漏洞发现。支持 **全链路 --auto 无人值守模式 + 安全门禁 + … | 2026-08-09 |
| [`serena`](./plugins/codebuddy-plugins-official/plugins/serena/) | 语义代码分析 MCP 服务器，通过语言服务器协议集成提供智能代码理解、重构建议和代码库导航功能。 | 2026-07-21 |
| [`skills-sec-audit`](./plugins/codebuddy-plugins-official/plugins/skills-sec-audit/) | 本skill用于对用户指定的skill.md文件、及其配套的文档、程序、脚本等做安全审查，确保引用安全 | 2026-10-04 |
| [`skills-security-check`](./plugins/codebuddy-plugins-official/plugins/skills-security-check/) | 腾讯云鼎实验室出品，Skill安全审查工具。本skill用于对用户指定的skill.md文件、及其配套的文档、程序、脚本等做安全审查，确保引用安全 | 2026-07-21 |
| [`supabase`](./plugins/codebuddy-plugins-official/plugins/supabase/) | Supabase MCP 集成，用于数据库操作、身份验证、存储和实时订阅。管理您的 Supabase 项目，运行 SQL 查询，并直接与后端交互。 | 2026-07-21 |
| [`swift-lsp`](./plugins/codebuddy-plugins-official/plugins/swift-lsp/) | Swift Language Server (SourceKit-LSP)，为 CodeBuddy 提供 Swift 项目的代码智能功能。 | 2026-07-21 |
| [`testbuddy`](./plugins/codebuddy-plugins-official/plugins/testbuddy/) | 文本测试用例生成插件。主要用于文本测试用例生成、文本测试用例框架生成、脑图用例生成、召回、需求分析等文本测试用例生成 | 2026-07-21 |
| [`tmap-lbs-plugin`](./plugins/codebuddy-plugins-official/plugins/tmap-lbs-plugin/) | 腾讯地图位置服务开发插件，提供 JavaScript GL 地图开发指南和 Web 服务 API（POI搜索、路径规划、旅游规划、轨迹可视化等）能力。 | 2026-07-21 |
| [`typescript-lsp`](./plugins/codebuddy-plugins-official/plugins/typescript-lsp/) | TypeScript/JavaScript Language Server，为 CodeBuddy 提供跳转定义、查找引用、错误检查等代码智能功能。 | 2026-07-21 |
| [`web-artifacts-builder`](./plugins/codebuddy-plugins-official/plugins/web-artifacts-builder/) | 使用现代前端技术（React、Tailwind CSS、shadcn/ui）创建复杂多组件 HTML 工件的工具套件。适用于需要状态管理、路由或 shadcn/ui 组件的复杂工… | 2026-07-21 |
| [`weixin-minigame-helper`](./plugins/codebuddy-plugins-official/plugins/weixin-minigame-helper/) | 微信小游戏 AI 开发助手 —— 预览、调试、真机测试、发布一站式解决。 | 2026-07-21 |
| [`xlsx`](./plugins/codebuddy-plugins-official/plugins/xlsx/) | 全面的电子表格创建、编辑和分析工具，支持公式、格式化、数据分析和可视化。适用于 .xlsx、.xlsm、.csv、.tsv 等表格文件的处理 | 2026-07-21 |

### 官方外部插件（`external_plugins/`，149）

> 以下插件在官方市场 `marketplace.json` 中登记（source 指向 `external_plugins/`），与上面 60 个市场自带插件同属官方插件市场，原清单未收录。组件构成为包内 agents / skills / commands / hooks 的数量。

| 目录 | 说明 | 组件构成 | 最后更新 |
|------|------|----------|----------|
| [`accessibility-compliance`](./plugins/codebuddy-plugins-official/external_plugins/accessibility-compliance/) | WCAG 无障碍审计、合规性验证、屏幕阅读器 UI 测试、键盘导航和包容性设计 | agents×1、skills×2、commands×1 | 2026-07-21 |
| [`agent-orchestration`](./plugins/codebuddy-plugins-official/external_plugins/agent-orchestration/) | 多智能体系统优化、智能体改进工作流和上下文管理 | agents×1、commands×2 | 2026-07-21 |
| [`agents-blockchain-web3`](./plugins/codebuddy-plugins-official/external_plugins/agents-blockchain-web3/) | 区块链开发、智能合约与 Web3 应用的专职 Agent。 | agents×2 | 2026-07-21 |
| [`agents-business-finance`](./plugins/codebuddy-plugins-official/external_plugins/agents-business-finance/) | 商业分析、财务建模与 KPI 追踪 Agent。 | agents×4 | 2026-07-21 |
| [`agents-crypto-trading`](./plugins/codebuddy-plugins-official/external_plugins/agents-crypto-trading/) | 加密货币交易、DeFi 策略与市场分析专家 Agent。 | agents×5 | 2026-07-21 |
| [`agents-data-ai`](./plugins/codebuddy-plugins-official/external_plugins/agents-data-ai/) | 数据工程、机器学习与 AI 开发 Agent。 | agents×11 | 2026-07-21 |
| [`agents-design-experience`](./plugins/codebuddy-plugins-official/external_plugins/agents-design-experience/) | UI/UX 设计、无障碍与用户体验优化 Agent。 | agents×2 | 2026-07-21 |
| [`agents-development-architecture`](./plugins/codebuddy-plugins-official/external_plugins/agents-development-architecture/) | 软件架构、后端开发与系统设计专家 Agent。 | agents×11 | 2026-07-21 |
| [`agents-infrastructure-operations`](./plugins/codebuddy-plugins-official/external_plugins/agents-infrastructure-operations/) | 云基础设施、DevOps 与数据库运维 Agent。 | agents×8 | 2026-07-21 |
| [`agents-language-specialists`](./plugins/codebuddy-plugins-official/external_plugins/agents-language-specialists/) | 各编程语言专家 Agent（Python、Go、Rust 等）。 | agents×12 | 2026-07-21 |
| [`agents-quality-security`](./plugins/codebuddy-plugins-official/external_plugins/agents-quality-security/) | 代码审查、安全审计、调试与质量保证 Agent。 | agents×15 | 2026-07-21 |
| [`agents-sales-marketing`](./plugins/codebuddy-plugins-official/external_plugins/agents-sales-marketing/) | 内容营销、客户支持与销售自动化 Agent。 | agents×6 | 2026-07-21 |
| [`agents-specialized-domains`](./plugins/codebuddy-plugins-official/external_plugins/agents-specialized-domains/) | 研究、文档等专业领域的专家 Agent。 | agents×41 | 2026-07-21 |
| [`all-agents`](./plugins/codebuddy-plugins-official/external_plugins/all-agents/) | 11 大类共 117 个专职 AI Agent 完整合集。 | agents×117 | 2026-07-21 |
| [`all-commands`](./plugins/codebuddy-plugins-official/external_plugins/all-commands/) | 22 大类共 174 个斜杠命令完整合集。 | commands×175 | 2026-07-21 |
| [`all-hooks`](./plugins/codebuddy-plugins-official/external_plugins/all-hooks/) | 28 个事件驱动自动化钩子完整合集。 | hooks×28 | 2026-07-21 |
| [`all-skills`](./plugins/codebuddy-plugins-official/external_plugins/all-skills/) | 29 个文档处理、开发、办公生产力等技能完整合集。 | skills×6 | 2026-07-21 |
| [`api-scaffolding`](./plugins/codebuddy-plugins-official/external_plugins/api-scaffolding/) | REST 和 GraphQL API 脚手架、框架选择、后端架构设计与 API 生成 | agents×4、skills×1 | 2026-07-21 |
| [`api-testing-observability`](./plugins/codebuddy-plugins-official/external_plugins/api-testing-observability/) | API 测试自动化、请求模拟、OpenAPI 文档生成、可观测性配置与监控 | agents×1、commands×1 | 2026-07-21 |
| [`application-performance`](./plugins/codebuddy-plugins-official/external_plugins/application-performance/) | 应用性能工程专家代理，用于应用优化、可观测性和可扩展系统性能。包括 OpenTelemetry、分布式追踪、负载测试、多层缓存、Core Web Vitals 和全面的性能监控。 | agents×3、commands×1 | 2026-07-21 |
| [`arm-cortex-microcontrollers`](./plugins/codebuddy-plugins-official/external_plugins/arm-cortex-microcontrollers/) | 面向 Teensy、STM32、nRF52 和 SAMD 的 ARM Cortex-M 固件开发，提供外设驱动和内存安全模式 | agents×1 | 2026-07-21 |
| [`backend-api-security`](./plugins/codebuddy-plugins-official/external_plugins/backend-api-security/) | API 安全加固、身份验证实现、授权模式、速率限制和输入验证 | agents×2 | 2026-07-21 |
| [`backend-development`](./plugins/codebuddy-plugins-official/external_plugins/backend-development/) | 后端 API 设计、GraphQL 架构、Temporal 工作流编排及测试驱动的后端开发 | agents×5、skills×9、commands×1 | 2026-07-21 |
| [`blockchain-web3`](./plugins/codebuddy-plugins-official/external_plugins/blockchain-web3/) | 使用 Solidity 进行智能合约开发、DeFi 协议实现、NFT 平台和 Web3 应用架构 | agents×1、skills×4 | 2026-07-21 |
| [`brand-guidelines`](./plugins/codebuddy-plugins-official/external_plugins/brand-guidelines/) | 将 Anthropic 官方品牌配色和排版应用于工件，确保视觉识别和专业设计标准的一致性。 | 仅规则/模板 | 2026-07-21 |
| [`business-analytics`](./plugins/codebuddy-plugins-official/external_plugins/business-analytics/) | 业务指标分析、KPI 跟踪、财务报告和数据驱动的决策制定 | agents×1、skills×2 | 2026-07-21 |
| [`c4-architecture`](./plugins/codebuddy-plugins-official/external_plugins/c4-architecture/) | 全面的 C4 架构文档工作流,采用自底向上的代码分析、组件合成、容器映射和上下文图生成 | agents×4、commands×1 | 2026-07-21 |
| [`canvas-design`](./plugins/codebuddy-plugins-official/external_plugins/canvas-design/) | 使用设计哲学和美学原则创建精美的视觉艺术作品，支持生成海报、设计稿和静态艺术品的 PNG 和 PDF 文档。 | 仅规则/模板 | 2026-07-21 |
| [`changelog-generator`](./plugins/codebuddy-plugins-official/external_plugins/changelog-generator/) | 自动从 git 提交历史生成面向用户的变更日志，将技术性的提交记录转换为易于理解的发布说明 | 仅规则/模板 | 2026-07-21 |
| [`cicd-automation`](./plugins/codebuddy-plugins-official/external_plugins/cicd-automation/) | CI/CD 流水线配置、GitHub Actions/GitLab CI 工作流设置及自动化部署流水线编排 | agents×5、skills×4、commands×1 | 2026-07-21 |
| [`claude-hud`](./plugins/codebuddy-plugins-official/external_plugins/claude-hud/) | Claude Code 实时状态栏 HUD：显示上下文用量、工具活动、Agent 追踪与待办。 | commands×1 | 2026-07-21 |
| [`cloud-infrastructure`](./plugins/codebuddy-plugins-official/external_plugins/cloud-infrastructure/) | 云架构设计（AWS/Azure/GCP），Kubernetes 集群配置，Terraform 基础设施即代码，混合云网络，以及多云成本优化 | agents×7、skills×8 | 2026-07-21 |
| [`code-documentation`](./plugins/codebuddy-plugins-official/external_plugins/code-documentation/) | 文档生成、代码解释和技术写作，支持自动化文档生成和教程创建 | agents×3、commands×2 | 2026-07-21 |
| [`code-refactoring`](./plugins/codebuddy-plugins-official/external_plugins/code-refactoring/) | 代码清理、重构自动化和技术债务管理,支持上下文恢复 | agents×2、commands×3 | 2026-07-21 |
| [`code-review-ai`](./plugins/codebuddy-plugins-official/external_plugins/code-review-ai/) | AI 驱动的架构审查和代码质量分析 | agents×1、commands×1 | 2026-07-21 |
| [`codebase-cleanup`](./plugins/codebuddy-plugins-official/external_plugins/codebase-cleanup/) | 技术债务削减、依赖更新和代码重构自动化 | agents×2、commands×3 | 2026-07-21 |
| [`commands-api-development`](./plugins/codebuddy-plugins-official/external_plugins/commands-api-development/) | REST/GraphQL API 设计与文档命令。 | commands×4 | 2026-07-21 |
| [`commands-automation-workflow`](./plugins/codebuddy-plugins-official/external_plugins/commands-automation-workflow/) | 重复性任务与工作流自动化命令。 | commands×1 | 2026-07-21 |
| [`commands-ci-deployment`](./plugins/codebuddy-plugins-official/external_plugins/commands-ci-deployment/) | CI/CD 搭建、容器化与部署自动化命令。 | commands×11 | 2026-07-21 |
| [`commands-code-analysis-testing`](./plugins/codebuddy-plugins-official/external_plugins/commands-code-analysis-testing/) | 代码审查、测试与分析命令。 | commands×18 | 2026-07-21 |
| [`commands-context-loading-priming`](./plugins/codebuddy-plugins-official/external_plugins/commands-context-loading-priming/) | 加载上下文、为特定任务预热 Agent 的命令。 | commands×4 | 2026-07-21 |
| [`commands-database-operations`](./plugins/codebuddy-plugins-official/external_plugins/commands-database-operations/) | 数据库模式设计、迁移与优化命令。 | commands×3 | 2026-07-21 |
| [`commands-documentation-changelogs`](./plugins/codebuddy-plugins-official/external_plugins/commands-documentation-changelogs/) | 文档生成与变更日志管理命令。 | commands×10 | 2026-07-21 |
| [`commands-framework-svelte`](./plugins/codebuddy-plugins-official/external_plugins/commands-framework-svelte/) | Svelte/SvelteKit 开发专用命令。 | commands×16 | 2026-07-21 |
| [`commands-game-development`](./plugins/codebuddy-plugins-official/external_plugins/commands-game-development/) | 游戏开发工作流命令。 | commands×1 | 2026-07-21 |
| [`commands-integration-sync`](./plugins/codebuddy-plugins-official/external_plugins/commands-integration-sync/) | 外部服务集成与数据同步命令。 | commands×12 | 2026-07-21 |
| [`commands-miscellaneous`](./plugins/codebuddy-plugins-official/external_plugins/commands-miscellaneous/) | 通用工具命令合集。 | commands×3 | 2026-07-21 |
| [`commands-monitoring-observability`](./plugins/codebuddy-plugins-official/external_plugins/commands-monitoring-observability/) | 监控与可观测性搭建命令。 | commands×2 | 2026-07-21 |
| [`commands-performance-optimization`](./plugins/codebuddy-plugins-official/external_plugins/commands-performance-optimization/) | 构建、包体积与性能优化命令。 | commands×6 | 2026-07-21 |
| [`commands-project-setup`](./plugins/codebuddy-plugins-official/external_plugins/commands-project-setup/) | 新项目初始化与搭建命令。 | commands×6 | 2026-07-21 |
| [`commands-project-task-management`](./plugins/codebuddy-plugins-official/external_plugins/commands-project-task-management/) | 任务管理与项目跟踪命令。 | commands×17 | 2026-07-21 |
| [`commands-security-audit`](./plugins/codebuddy-plugins-official/external_plugins/commands-security-audit/) | 安全审计与漏洞扫描命令。 | commands×4 | 2026-07-21 |
| [`commands-simulation-modeling`](./plugins/codebuddy-plugins-official/external_plugins/commands-simulation-modeling/) | 场景模拟与决策建模命令。 | commands×8 | 2026-07-21 |
| [`commands-team-collaboration`](./plugins/codebuddy-plugins-official/external_plugins/commands-team-collaboration/) | 团队工作流、PR 审查与协作命令。 | commands×12 | 2026-07-21 |
| [`commands-typescript-migration`](./plugins/codebuddy-plugins-official/external_plugins/commands-typescript-migration/) | JavaScript 项目迁移 TypeScript 命令。 | commands×1 | 2026-07-21 |
| [`commands-utilities-debugging`](./plugins/codebuddy-plugins-official/external_plugins/commands-utilities-debugging/) | 通用调试与工具命令。 | commands×14 | 2026-07-21 |
| [`commands-version-control-git`](./plugins/codebuddy-plugins-official/external_plugins/commands-version-control-git/) | Git 操作、提交与 PR 命令。 | commands×12 | 2026-07-21 |
| [`commands-workflow-orchestration`](./plugins/codebuddy-plugins-official/external_plugins/commands-workflow-orchestration/) | 复杂工作流编排命令。 | commands×9 | 2026-07-21 |
| [`competitive-ads-extractor`](./plugins/codebuddy-plugins-official/external_plugins/competitive-ads-extractor/) | 从广告库中提取并分析竞争对手的广告,以了解能够引起共鸣的营销信息和创意方法。 | 仅规则/模板 | 2026-07-21 |
| [`comprehensive-review`](./plugins/codebuddy-plugins-official/external_plugins/comprehensive-review/) | 多维度代码分析,覆盖架构、安全性和最佳实践 | agents×3、commands×2 | 2026-07-21 |
| [`conductor`](./plugins/codebuddy-plugins-official/external_plugins/conductor/) | 上下文驱动开发插件，将 Claude Code 转变为项目管理工具，采用结构化工作流：上下文 → 规格与计划 → 实施 | agents×1、skills×3、commands×6 | 2026-07-21 |
| [`content-marketing`](./plugins/codebuddy-plugins-official/external_plugins/content-marketing/) | 内容营销策略、网络调研和信息综合处理的营销运营工具 | agents×2 | 2026-07-21 |
| [`content-research-writer`](./plugins/codebuddy-plugins-official/external_plugins/content-research-writer/) | 协助撰写高质量内容，包括研究调查、添加引用、改进开篇、提供逐节反馈等功能。 | 仅规则/模板 | 2026-07-21 |
| [`context-management`](./plugins/codebuddy-plugins-official/external_plugins/context-management/) | 上下文持久化、恢复和长期对话管理 | agents×1、commands×2 | 2026-07-21 |
| [`customer-sales-automation`](./plugins/codebuddy-plugins-official/external_plugins/customer-sales-automation/) | 客户支持工作流自动化、销售管道管理、邮件营销活动及客户关系管理系统集成 | agents×2 | 2026-07-21 |
| [`data-engineering`](./plugins/codebuddy-plugins-official/external_plugins/data-engineering/) | ETL管道构建、数据仓库设计、批处理工作流和数据驱动的功能开发 | agents×2、skills×4、commands×2 | 2026-07-21 |
| [`data-validation-suite`](./plugins/codebuddy-plugins-official/external_plugins/data-validation-suite/) | 模式验证、数据质量监控、流式验证管道以及后端API的输入验证 | agents×1 | 2026-07-21 |
| [`database-cloud-optimization`](./plugins/codebuddy-plugins-official/external_plugins/database-cloud-optimization/) | 数据库查询优化、云成本优化和可扩展性改进 | agents×4、commands×1 | 2026-07-21 |
| [`database-design`](./plugins/codebuddy-plugins-official/external_plugins/database-design/) | 生产系统的数据库架构设计、模式设计和 SQL 优化 | agents×2、skills×1 | 2026-07-21 |
| [`database-migrations`](./plugins/codebuddy-plugins-official/external_plugins/database-migrations/) | 数据库迁移自动化、可观测性和跨数据库迁移策略 | agents×2、commands×2 | 2026-07-21 |
| [`debugging-toolkit`](./plugins/codebuddy-plugins-official/external_plugins/debugging-toolkit/) | 交互式调试、开发者体验优化和智能调试工作流 | agents×2、commands×1 | 2026-07-21 |
| [`dependency-management`](./plugins/codebuddy-plugins-official/external_plugins/dependency-management/) | 依赖审计、版本管理和安全漏洞扫描 | agents×1、commands×1 | 2026-07-21 |
| [`deployment-strategies`](./plugins/codebuddy-plugins-official/external_plugins/deployment-strategies/) | 部署模式、回滚自动化和基础设施模板 | agents×2 | 2026-07-21 |
| [`deployment-validation`](./plugins/codebuddy-plugins-official/external_plugins/deployment-validation/) | 部署前检查、配置验证和部署就绪性评估 | agents×1、commands×1 | 2026-07-21 |
| [`developer-essentials`](./plugins/codebuddy-plugins-official/external_plugins/developer-essentials/) | 包含 Git 工作流、SQL 优化、错误处理、代码审查、端到端测试、身份认证、调试和 Monorepo 管理的核心开发技能集 | agents×1、skills×11 | 2026-07-21 |
| [`developer-growth-analysis`](./plugins/codebuddy-plugins-official/external_plugins/developer-growth-analysis/) | 分析你最近的 Claude Code 聊天历史，识别编码模式、发现开发能力缺口和需要改进的领域，从 HackerNews 精选相关学习资源，并自动将个性化成长报告发送到你的 Slack 私信。 | 仅规则/模板 | 2026-07-21 |
| [`distributed-debugging`](./plugins/codebuddy-plugins-official/external_plugins/distributed-debugging/) | 分布式系统追踪与微服务调试工具 | agents×2、commands×1 | 2026-07-21 |
| [`documentation-generation`](./plugins/codebuddy-plugins-official/external_plugins/documentation-generation/) | OpenAPI规范生成、Mermaid图表创建、教程编写、API参考文档 | agents×5、skills×3、commands×1 | 2026-07-21 |
| [`domain-name-brainstormer`](./plugins/codebuddy-plugins-official/external_plugins/domain-name-brainstormer/) | 为项目生成创意域名并检查多个顶级域名（包括 .com、.io、.dev 和 .ai 等）的可用性 | 仅规则/模板 | 2026-07-21 |
| [`error-debugging`](./plugins/codebuddy-plugins-official/external_plugins/error-debugging/) | 错误分析、堆栈追踪调试和多智能体问题诊断 | agents×2、commands×3 | 2026-07-21 |
| [`error-diagnostics`](./plugins/codebuddy-plugins-official/external_plugins/error-diagnostics/) | 错误追踪、根因分析及生产系统智能调试 | agents×2、commands×3 | 2026-07-21 |
| [`framework-migration`](./plugins/codebuddy-plugins-official/external_plugins/framework-migration/) | 框架升级、迁移规划与架构转型工作流 | agents×2、skills×4、commands×3 | 2026-07-21 |
| [`frontend-design-pro`](./plugins/codebuddy-plugins-official/external_plugins/frontend-design-pro/) | 高级前端设计插件：交互式向导、趋势调研、情绪板、配色/字体。 | skills×6、commands×3 | 2026-07-21 |
| [`frontend-mobile-development`](./plugins/codebuddy-plugins-official/external_plugins/frontend-mobile-development/) | 跨平台前端 UI 开发和移动应用实现 | agents×2、skills×4、commands×1 | 2026-07-21 |
| [`frontend-mobile-security`](./plugins/codebuddy-plugins-official/external_plugins/frontend-mobile-security/) | 前端和移动开发专业安全代理。包括 XSS 漏洞扫描、安全编码实践、WebView 安全、移动认证，以及专注安全的现代 React/Next.js 开发。 | agents×3、commands×1 | 2026-07-21 |
| [`full-stack-orchestration`](./plugins/codebuddy-plugins-official/external_plugins/full-stack-orchestration/) | 编排全栈功能开发，配备测试自动化、性能工程、安全审计和部署的专业代理。支持 CI/CD 流水线、GitOps 工作流、可观测性和渐进式交付策略。 | agents×4、commands×1 | 2026-07-21 |
| [`functional-programming`](./plugins/codebuddy-plugins-official/external_plugins/functional-programming/) | 函数式编程语言专家代理，包括 Haskell 和 Elixir。提供高级类型系统、纯函数式设计、OTP 模式、并发、容错分布式系统和高可靠性软件开发。 | agents×2 | 2026-07-21 |
| [`game-development`](./plugins/codebuddy-plugins-official/external_plugins/game-development/) | Unity游戏开发与C#脚本编程，Minecraft服务器插件开发（支持Bukkit/Spigot API） | agents×2、skills×2 | 2026-07-21 |
| [`git-pr-workflows`](./plugins/codebuddy-plugins-official/external_plugins/git-pr-workflows/) | Git 工作流自动化、拉取请求增强和团队入职流程 | agents×1、commands×3 | 2026-07-21 |
| [`hooks-automation`](./plugins/codebuddy-plugins-official/external_plugins/hooks-automation/) | 自动化钩子：事件驱动自动化。 | hooks×3 | 2026-07-21 |
| [`hooks-development`](./plugins/codebuddy-plugins-official/external_plugins/hooks-development/) | 开发钩子：事件驱动自动化。 | hooks×4 | 2026-07-21 |
| [`hooks-formatting`](./plugins/codebuddy-plugins-official/external_plugins/hooks-formatting/) | 格式化钩子：事件驱动自动化。 | hooks×2 | 2026-07-21 |
| [`hooks-git`](./plugins/codebuddy-plugins-official/external_plugins/hooks-git/) | Git 钩子：事件驱动自动化。 | hooks×3 | 2026-07-21 |
| [`hooks-notifications`](./plugins/codebuddy-plugins-official/external_plugins/hooks-notifications/) | 通知钩子：事件驱动自动化。 | hooks×10 | 2026-07-21 |
| [`hooks-performance`](./plugins/codebuddy-plugins-official/external_plugins/hooks-performance/) | 性能钩子：事件驱动自动化。 | hooks×1 | 2026-07-21 |
| [`hooks-security`](./plugins/codebuddy-plugins-official/external_plugins/hooks-security/) | 安全钩子：事件驱动自动化。 | hooks×3 | 2026-07-21 |
| [`hooks-testing`](./plugins/codebuddy-plugins-official/external_plugins/hooks-testing/) | 测试钩子：事件驱动自动化。 | hooks×2 | 2026-07-21 |
| [`hr-legal-compliance`](./plugins/codebuddy-plugins-official/external_plugins/hr-legal-compliance/) | 人力资源政策文档、法律合规模板（GDPR/SOC2/HIPAA）、雇佣合同及监管文件 | agents×2、skills×2 | 2026-07-21 |
| [`image-enhancer`](./plugins/codebuddy-plugins-official/external_plugins/image-enhancer/) | 通过提升分辨率、锐度和清晰度来改善图像和截图质量，适用于专业演示文稿和文档制作。 | 仅规则/模板 | 2026-07-21 |
| [`incident-response`](./plugins/codebuddy-plugins-official/external_plugins/incident-response/) | 生产事故管理、分级处理工作流和自动化事故解决方案 | agents×2、skills×3、commands×2 | 2026-07-21 |
| [`internal-comms`](./plugins/codebuddy-plugins-official/external_plugins/internal-comms/) | 帮助撰写内部沟通文档，包括三要素更新（进展/计划/问题）、公司通讯、常见问题解答、状态报告和项目更新，遵循公司特定格式规范。 | 仅规则/模板 | 2026-07-21 |
| [`interview`](./plugins/codebuddy-plugins-official/external_plugins/interview/) | 访谈式命令：把大型特性计划与规格逐步细化完善。 | commands×1 | 2026-07-21 |
| [`invoice-organizer`](./plugins/codebuddy-plugins-official/external_plugins/invoice-organizer/) | 发票整理工具 | 仅规则/模板 | 2026-07-21 |
| [`javascript-typescript`](./plugins/codebuddy-plugins-official/external_plugins/javascript-typescript/) | JavaScript 和 TypeScript 开发，支持 ES6+、Node.js、React 及现代 Web 框架 | agents×2、skills×4、commands×1 | 2026-07-21 |
| [`julia-development`](./plugins/codebuddy-plugins-official/external_plugins/julia-development/) | 现代 Julia 开发工具，支持 Julia 1.10+ 版本、包管理、科学计算、高性能数值代码和生产环境最佳实践 | agents×1 | 2026-07-21 |
| [`jvm-languages`](./plugins/codebuddy-plugins-official/external_plugins/jvm-languages/) | JVM 语言开发，包括 Java、Scala 和 C#，涵盖企业级模式和框架 | agents×3 | 2026-07-21 |
| [`kubernetes-operations`](./plugins/codebuddy-plugins-official/external_plugins/kubernetes-operations/) | Kubernetes 清单生成、网络配置、安全策略、可观测性配置、GitOps 工作流和自动扩缩容 | agents×1、skills×4 | 2026-07-21 |
| [`lead-research-assistant`](./plugins/codebuddy-plugins-official/external_plugins/lead-research-assistant/) | 通过分析您的产品、搜索目标公司并提供可行的联系策略，识别和筛选高质量潜在客户。 | 仅规则/模板 | 2026-07-21 |
| [`llm-application-dev`](./plugins/codebuddy-plugins-official/external_plugins/llm-application-dev/) | 构建生产就绪的 LLM 应用、高级 RAG 系统和智能代理。包括向量搜索、多模态 AI、代理编排、提示工程和企业 AI 集成，以及全面的 AI 开发工作流。 | agents×3、skills×8、commands×3 | 2026-07-21 |
| [`machine-learning-ops`](./plugins/codebuddy-plugins-official/external_plugins/machine-learning-ops/) | 完整的 MLOps 工具包，配备 ML 工程、MLOps 基础设施和数据科学专业代理。构建生产 ML 流水线、实验跟踪、模型注册和自动化训练/部署工作流。 | agents×3、skills×1、commands×1 | 2026-07-21 |
| [`mcp-builder`](./plugins/codebuddy-plugins-official/external_plugins/mcp-builder/) | 指导创建高质量的 MCP（模型上下文协议）服务器,用于将外部 API 和服务与大语言模型集成,支持 Python 和 TypeScript 开发 | 仅规则/模板 | 2026-07-21 |
| [`mcp-servers-docker`](./plugins/codebuddy-plugins-official/external_plugins/mcp-servers-docker/) | Docker 官方 MCP 注册表的 199+ 个经验证的 MCP 服务器。 | 仅规则/模板 | 2026-07-21 |
| [`meeting-insights-analyzer`](./plugins/codebuddy-plugins-official/external_plugins/meeting-insights-analyzer/) | 分析会议记录以揭示行为模式，包括冲突回避、发言比例、填充词使用和领导风格。 | 仅规则/模板 | 2026-07-21 |
| [`multi-platform-apps`](./plugins/codebuddy-plugins-official/external_plugins/multi-platform-apps/) | 跨平台应用开发,协调 Web、iOS、Android 和桌面端的实现 | agents×6、commands×1 | 2026-07-21 |
| [`nextjs-expert`](./plugins/codebuddy-plugins-official/external_plugins/nextjs-expert/) | Next.js 开发专家：App Router、Server Components、Route Handlers、Server Actions 等。 | skills×5、commands×3 | 2026-07-21 |
| [`observability-monitoring`](./plugins/codebuddy-plugins-official/external_plugins/observability-monitoring/) | 指标收集、日志基础设施、分布式追踪、SLO 实施和监控仪表板 | agents×4、skills×4、commands×2 | 2026-07-21 |
| [`obsidian-skills`](./plugins/codebuddy-plugins-official/external_plugins/obsidian-skills/) | Obsidian 文件处理技能：Markdown、Bases、Canvas 格式。 | skills×3 | 2026-07-21 |
| [`payload`](./plugins/codebuddy-plugins-official/external_plugins/payload/) | 为 Payload 开发提供全面指导的 Claude Code 技能，包含 TypeScript 模式、字段配置、钩子、访问控制和 API 示例。 | skills×1 | 2026-07-21 |
| [`payment-processing`](./plugins/codebuddy-plugins-official/external_plugins/payment-processing/) | 支付网关集成,包含 Stripe 和 PayPal,实现结账流程、订阅计费和 PCI 合规性 | agents×1、skills×4 | 2026-07-21 |
| [`performance-testing-review`](./plugins/codebuddy-plugins-official/external_plugins/performance-testing-review/) | 性能分析、测试覆盖率审查和 AI 驱动的代码质量评估 | agents×2、commands×2 | 2026-07-21 |
| [`python-development`](./plugins/codebuddy-plugins-official/external_plugins/python-development/) | 现代 Python 开发工具，支持 Python 3.12+、Django、FastAPI、异步编程模式及生产环境最佳实践 | agents×3、skills×5、commands×1 | 2026-07-21 |
| [`quantitative-trading`](./plugins/codebuddy-plugins-official/external_plugins/quantitative-trading/) | 量化分析、算法交易策略、金融建模、投资组合风险管理和回测 | agents×2、skills×2 | 2026-07-21 |
| [`raffle-winner-picker`](./plugins/codebuddy-plugins-official/external_plugins/raffle-winner-picker/) | 从列表、电子表格或 Google Sheets 中随机选择获奖者，用于抽奖和比赛，采用密码学安全的随机性确保公平。 | 仅规则/模板 | 2026-07-21 |
| [`repomix-commands`](./plugins/codebuddy-plugins-official/external_plugins/repomix-commands/) | 用于快速执行 Repomix 操作的斜杠命令。通过 /pack-local 和 /pack-remote 等简单命令打包本地和远程代码仓库。 | commands×2 | 2026-07-21 |
| [`repomix-explorer`](./plugins/codebuddy-plugins-official/external_plugins/repomix-explorer/) | 在 CodeBuddy Code 中使用 Repomix 能力探索和分析仓库结构 | agents×1、commands×2 | 2026-07-21 |
| [`repomix-mcp`](./plugins/codebuddy-plugins-official/external_plugins/repomix-mcp/) | Repomix MCP 服务器，用于 AI 驱动的代码库分析。打包本地/远程仓库，搜索输出内容，读取文件并内置安全扫描。这是在 Claude Code 中启用所有 Repomix 功能的基础插件。 | 仅规则/模板 | 2026-07-21 |
| [`scientific-skills`](./plugins/codebuddy-plugins-official/external_plugins/scientific-skills/) | K-Dense 团队创建的 139 个即用型 Claude 科学技能综合集合。将 Claude 转变为您的 AI 研究助手，能够执行跨生物学、化学和医学等领域的复杂多步骤科学工作流程。 | 仅规则/模板 | 2026-07-21 |
| [`security-compliance`](./plugins/codebuddy-plugins-official/external_plugins/security-compliance/) | SOC2、HIPAA 和 GDPR 合规性验证、密钥扫描、合规性检查清单和监管文档 | agents×1、commands×1 | 2026-07-21 |
| [`seo-analysis-monitoring`](./plugins/codebuddy-plugins-official/external_plugins/seo-analysis-monitoring/) | SEO 内容新鲜度分析、关键词竞食检测和权威建设 | agents×3 | 2026-07-21 |
| [`seo-content-creation`](./plugins/codebuddy-plugins-official/external_plugins/seo-content-creation/) | SEO 内容创作、规划与质量审计工具，支持 E-E-A-T 优化 | agents×3 | 2026-07-21 |
| [`seo-technical-optimization`](./plugins/codebuddy-plugins-official/external_plugins/seo-technical-optimization/) | 技术SEO优化,包括元标签、关键词、结构和精选摘要 | agents×4 | 2026-07-21 |
| [`shell-scripting`](./plugins/codebuddy-plugins-official/external_plugins/shell-scripting/) | 生产级 Bash 脚本编写，包含防御性编程、POSIX 合规性和全面测试 | agents×2、skills×3 | 2026-07-21 |
| [`skill-creator`](./plugins/codebuddy-plugins-official/external_plugins/skill-creator/) | 提供创建高效 Claude 技能的指南,通过专业知识、工作流程和工具集成来扩展 AI 助手的能力 | agents×3 | 2026-07-21 |
| [`slack-gif-creator`](./plugins/codebuddy-plugins-official/external_plugins/slack-gif-creator/) | 创建针对 Slack 优化的动画 GIF,提供文件大小约束验证和可组合的动画基元。 | 仅规则/模板 | 2026-07-21 |
| [`startup-business-analyst`](./plugins/codebuddy-plugins-official/external_plugins/startup-business-analyst/) | 面向初创企业的综合业务分析工具，提供市场规模分析（TAM/SAM/SOM）、财务建模、团队规划和战略研究功能 | agents×1、skills×5、commands×3 | 2026-07-21 |
| [`superpowers`](./plugins/codebuddy-plugins-official/external_plugins/superpowers/) | Claude Code 核心技能库：包含测试驱动开发、系统化调试、协作模式和经过验证的技术方法 | agents×1、skills×14、commands×3、hooks×3 | 2026-07-21 |
| [`superpowers-chrome`](./plugins/codebuddy-plugins-official/external_plugins/superpowers-chrome/) | 超轻量级 Chrome DevTools Protocol MCP 服务器，支持自动捕获。通过 Chrome DevTools Protocol 实现直接浏览器控制，零依赖，API 简单易用。 | agents×1、skills×1 | 2026-07-21 |
| [`systems-programming`](./plugins/codebuddy-plugins-official/external_plugins/systems-programming/) | 使用 Rust、Go、C 和 C++ 进行系统编程，适用于性能关键和底层开发 | agents×4、skills×3、commands×1 | 2026-07-21 |
| [`tailored-resume-generator`](./plugins/codebuddy-plugins-official/external_plugins/tailored-resume-generator/) | 分析职位描述并生成量身定制的简历，突出相关经验、技能和成就，最大化面试机会。 | 仅规则/模板 | 2026-07-21 |
| [`taskmaster`](./plugins/codebuddy-plugins-official/external_plugins/taskmaster/) | Claude Code 插件 - 基于AI的任务管理系统，提供命令、代理和 MCP 集成 | agents×3、commands×46 | 2026-07-21 |
| [`tdd-workflows`](./plugins/codebuddy-plugins-official/external_plugins/tdd-workflows/) | 测试驱动开发方法论,提供红-绿-重构循环和代码审查 | agents×2、commands×4 | 2026-07-21 |
| [`team-collaboration`](./plugins/codebuddy-plugins-official/external_plugins/team-collaboration/) | 团队工作流、问题管理、站会自动化和开发者体验优化 | agents×1、commands×2 | 2026-07-21 |
| [`template-skill`](./plugins/codebuddy-plugins-official/external_plugins/template-skill/) | 一个演示如何创建新 Claude 技能的结构和格式的模板技能 | 仅规则/模板 | 2026-07-21 |
| [`theme-factory`](./plugins/codebuddy-plugins-official/external_plugins/theme-factory/) | 为演示文稿、文档、报告和 HTML 落地页等制品应用专业的字体和配色主题，提供 10 套预设主题方案。 | 仅规则/模板 | 2026-07-21 |
| [`ui-ux-pro-max-skill`](./plugins/codebuddy-plugins-official/external_plugins/ui-ux-pro-max-skill/) | AI 驱动的 UI/UX 设计系统生成器：100+ 行业推理规则、57 种 UI 风格、95+ 配色。 | skills×1 | 2026-07-23 |
| [`unit-testing`](./plugins/codebuddy-plugins-official/external_plugins/unit-testing/) | Python 和 JavaScript 的单元测试与集成测试自动化，支持调试功能 | agents×2、commands×1 | 2026-07-21 |
| [`video-downloader`](./plugins/codebuddy-plugins-official/external_plugins/video-downloader/) | 从 YouTube 和其他平台下载视频，支持离线观看、编辑或存档，提供多种格式和画质选项。 | 仅规则/模板 | 2026-07-21 |
| [`web-scripting`](./plugins/codebuddy-plugins-official/external_plugins/web-scripting/) | 使用 PHP 和 Ruby 进行 Web 脚本开发，支持 Web 应用、CMS 开发和后端服务 | agents×2 | 2026-07-21 |
| [`webapp-testing`](./plugins/codebuddy-plugins-official/external_plugins/webapp-testing/) | 使用 Playwright 测试本地 Web 应用，支持验证前端功能、调试 UI 行为和捕获浏览器截图。 | 仅规则/模板 | 2026-07-21 |


### 团队插件

| 目录 | 说明 | 最后更新 |
|------|------|----------|
| [`a-share-analysis`](./plugins/cb_teams_marketplace/plugins/a-share-analysis/) | A股投资分析技能集，覆盖宏观研究、市场结构、个股深度、行业比较、资金行为、风险管理等 21 个专业分析 skill 和 6 个编排 agent。 | 2026-10-04 |
| [`agent-sdk-dev`](./plugins/cb_teams_marketplace/plugins/agent-sdk-dev/) | 用于创建和验证 CodeBuddy Agent SDK 应用的综合开发插件。 | 2026-10-04 |
| [`ai-hedge-fund`](./plugins/cb_teams_marketplace/plugins/ai-hedge-fund/) | AI 对冲基金投资分析系统：19位投资大师并行分析 + 风险管理 + 投资组合决策的全流程投资分析。涵盖巴菲特、芒格、林奇、伯里、塔勒布、伍德、格雷厄姆等13位传奇投资哲学家 +… | 2026-10-04 |
| [`codebuddy-chat-web`](./plugins/cb_teams_marketplace/plugins/codebuddy-chat-web/) | 初始化一个基于 CodeBuddy Agent SDK 的完整 Web 聊天应用。 | 2026-10-04 |
| [`data`](./plugins/cb_teams_marketplace/plugins/data/) | 数据分析插件，支持 SQL 查询、数据探索、可视化、仪表板构建和洞察生成。包含完整的数据分析工作流程和最佳实践。 | 2026-10-04 |
| [`deep-research`](./plugins/cb_teams_marketplace/plugins/deep-research/) | 深度研究插件：全面网络调研、信息综合与报告生成。 | 2026-10-04 |
| [`design-to-code`](./plugins/cb_teams_marketplace/plugins/design-to-code/) | 将 Figma 设计文件和 UI 截图转换为生产就绪的代码组件，内置无障碍性支持。 | 2026-10-04 |
| [`dockerfile-gen`](./plugins/cb_teams_marketplace/plugins/dockerfile-gen/) | Dockerfile 生成器：按容器最佳实践自动生成。 | 2026-10-04 |
| [`document-skills`](./plugins/cb_teams_marketplace/plugins/document-skills/) | PDF 处理技能：读取、文本/表格提取、表单填写、合并拆分。 | 2026-10-04 |
| [`equity-research`](./plugins/cb_teams_marketplace/plugins/equity-research/) | 股票研究工具：财报分析、首次覆盖报告与研究流程。 | 2026-07-21 |
| [`executing-marketing-campaigns`](./plugins/cb_teams_marketplace/plugins/executing-marketing-campaigns/) | 营销活动规划、执行与效果衡量的完整技能。 | 2026-07-21 |
| [`finance`](./plugins/cb_teams_marketplace/plugins/finance/) | 财务与会计插件，支持月末结账、日记账分录、账户核对、财务报表生成、差异分析和 SOX 审计支持。 | 2026-10-04 |
| [`finance-data`](./plugins/cb_teams_marketplace/plugins/finance-data/) | 金融数据与研究插件，包含 neodata-financial-search 自然语言金融搜索、westock-data 结构化行情数据和 westock-screener 条件选… | 2026-10-23 |
| [`financial-analysis`](./plugins/cb_teams_marketplace/plugins/financial-analysis/) | 核心财务建模分析工具：DCF、可比公司、LBO、三表模型。 | 2026-07-21 |
| [`gaokao-advisor`](./plugins/cb_teams_marketplace/plugins/gaokao-advisor/) | 面向高考真题/作文、全国高校与专业信息检索、地区批次线查询、一分一段/位次查询和志愿填报参考。 | 2026-10-04 |
| [`general-skills`](./plugins/cb_teams_marketplace/plugins/general-skills/) | CodeBuddy Code 通用技能合集。 | 2026-08-12 |
| [`internal-comms`](./plugins/cb_teams_marketplace/plugins/internal-comms/) | 按公司惯用格式撰写内部沟通文稿的资源集。 | 2026-07-21 |
| [`investment-banking`](./plugins/cb_teams_marketplace/plugins/investment-banking/) | 投行生产力工具：股票研究、估值、路演材料。 | 2026-07-21 |
| [`lseg`](./plugins/cb_teams_marketplace/plugins/lseg/) | LSEG：债券定价、收益率曲线、外汇套息、期权估值。 | 2026-07-21 |
| [`modern-webapp`](./plugins/cb_teams_marketplace/plugins/modern-webapp/) | 现代 Web 应用开发：React、TypeScript、Vite、Tailwind。 | 2026-10-04 |
| [`ppt-implement`](./plugins/cb_teams_marketplace/plugins/ppt-implement/) | 智能 PPT 生成助手，一键将您的想法转化为精美演示文稿 | 2026-10-04 |
| [`private-equity`](./plugins/cb_teams_marketplace/plugins/private-equity/) | 私募股权项目源开发与流程工具：公司发现、CRM 集成。 | 2026-07-21 |
| [`product-management`](./plugins/cb_teams_marketplace/plugins/product-management/) | 产品管理插件覆盖完整的 PM 工作流程：编写功能规格、管理产品路线图、与利益相关者沟通、综合用户研究、分析竞品和审查产品指标。 | 2026-10-04 |
| [`remotion-video-generator`](./plugins/cb_teams_marketplace/plugins/remotion-video-generator/) | 用 Remotion 以最少量输入自动生成精美视频。 | 2026-10-04 |
| [`sheetagent`](./plugins/cb_teams_marketplace/plugins/sheetagent/) | 由腾讯文档团队出品的电子表格智能助手，支持通过自然语言创建、查询与编辑 xlsx 表格 | 2026-10-04 |
| [`skill-creator`](./plugins/cb_teams_marketplace/plugins/skill-creator/) | 提供创建高效 Claude 技能的指南,通过专业知识、工作流程和工具集成来扩展 AI 助手的能力 | 2026-10-04 |
| [`spglobal`](./plugins/cb_teams_marketplace/plugins/spglobal/) | 标普全球金融数据与分析：公司速览、财报等。 | 2026-07-21 |
| [`trading-agent`](./plugins/cb_teams_marketplace/plugins/trading-agent/) | 交易智能体插件：基于多角色辩论方法论的系统性投资分析，涵盖市场技术分析、基本面分析、新闻与情绪分析、多空辩论、交易决策与三方风险评估全流程，输出 BUY/SELL/HOLD 建议… | 2026-10-04 |
| [`wealth-management`](./plugins/cb_teams_marketplace/plugins/wealth-management/) | 财富管理与客户理财工具：客户复盘、财务规划。 | 2026-07-21 |
| [`webapp-testing`](./plugins/cb_teams_marketplace/plugins/webapp-testing/) | 智能引导式 Web 应用测试助手，帮助你快速启动、配置和测试 Web 应用。自动分析项目结构，检测运行环境，配合 `agent-browser` 进行浏览器自动化测试。 | 2026-10-04 |

## 5. 补充：原清单未覆盖的内容

### 5.1 连接器内嵌技能

连接器目录除 `mcp.json` / `cli.json` 配置模板外，**393 个连接器自带 `skills/` 目录，共 829 个内嵌技能包**（每个含 `SKILL.md`），用于教 Agent 如何使用该连接器。原清单只在描述栏统一标注「连接器配置与技能」，未逐一列出。查询某连接器自带技能可查看 `connectors/<id>/skills/`。

### 5.2 元数据 / 索引文件

| 文件 | 作用 | 最后更新 |
|------|------|----------|
| [`skills/README-marketplace.md`](./skills/README-marketplace.md) | 技能市场上游说明 | 2026-07-21 |
| [`skills/version.txt`](./skills/version.txt) | 技能市场同步版本号 | 2026-07-21 |
| [`experts/expert_center.json`](./experts/expert_center.json) | 专家市场目录索引（版本、更新时间、bundle 下载路径） | 2026-10-04 |
| [`plugins/codebuddy-plugins-official/.codebuddy-plugin/marketplace.json`](./plugins/codebuddy-plugins-official/.codebuddy-plugin/marketplace.json) | 官方插件市场登记（209 个插件 = 60 自带 + 149 外部） | 2026-10-04 |
| [`plugins/cb_teams_marketplace/.codebuddy-plugin/marketplace.json`](./plugins/cb_teams_marketplace/.codebuddy-plugin/marketplace.json) | 团队插件市场登记（29 个；`gaokao-advisor` 目录存在但未登记，为上游问题） | 2026-10-23 |
| `plugins/cb_teams_marketplace/scenes*.json` 等 | 团队市场的场景分类与分析文件（非插件本体） | 2026-10-23 |

### 5.3 校验结论（2026-10-23 快照核对）

- 技能 295 / 连接器 443 / 专家 429 / 插件 90（60+30）：**目录与清单一一对应，无缺失、无多余**。
- 所有技能包含 `SKILL.md`，所有连接器包含 `mcp.json` 或 `cli.json`，所有专家包含 `.codebuddy-plugin/plugin.json`，结构完整。
- 抽查技能描述与 `SKILL.md` frontmatter 一致。
- 主要缺口即上文补录的 **149 个官方外部插件**，以及连接器内嵌技能与元数据文件说明。
