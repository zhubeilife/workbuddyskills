# CNKI 基础教育 MCP 数据接入（题库 + 学术文献）

## 零、先说清楚：数据只能从这里来

本 skill 的**题库候选题**与**学术溯源文献**，唯一数据源是 WorkBuddy 连接器里的
**「CNKI 基础教育」MCP**（工具名前缀 `mcp__<SERVER>__`）。

| 数据 | 走哪个接口 | 谁负责调用 |
|---|---|---|
| 候选题（真题底座） | `mcp__<SERVER>__tkSearchQuestion` 等 `tk*` 系列 | Agent 在会话里调，原始 JSON 落盘后交给 `mcp_adapters.py bank` |
| 学术溯源（期刊论文） | `mcp__<SERVER>__searchVectorBJ` | Agent 在会话里调，原始 JSON 落盘后交给 `mcp_adapters.py lit` |
| 学科码 / 知识点 / 教材 | `mcp__<SERVER>__tkSubject` / `mcp__<SERVER>__tkPoint` / `mcp__<SERVER>__tkBook` | 同上 |

**不允许**用本地文件、模型记忆或公开网页检索去拼题库和文献列表。
原因不是"不够真实"，而是这套方案的全部差异化在于**每条题源可点开核验**——
一旦掺进无法回溯的来源，教师抽查一次就不再信任整套东西。

### 前置条件：连接器要先启用

`edu` 连接器默认可能处于禁用状态。诊断时**先把"未连接"和"接口报错"分开**——
它们症状完全不同，但在没有经验的排查里经常被当成同一件事：

| 现象 | 真正的原因 | 怎么确认 |
|---|---|---|
| `ToolSearch` 精确查 `mcp__<SERVER>__*` 一个都返回不了 | **未连接**（配置里 `disabled: true`，或从未启用） | 看 `~/.workbuddy/mcp.json` 里 `edu` 的 `disabled` 字段 |
| 工具名查得到，但调用返回鉴权/500 | **已连接但业务报错** | 看返回的 `code` / `msg` |
| 端点直连返回 `Missing access token` | 服务活着，在等客户端 token | 正常，说明传输层没问题 |

未连接时**本会话无法自愈**：工具列表是会话启动时加载的，改完配置要**重开会话**才生效。

---

## 一、接口登记表

跑 `python scripts/mcp_adapters.py endpoints` 可随时打印当前这张表（含状态与坑）。

> **工具名前缀 = 连接器显示名，不是 `mcp.json` 里的 key，而且会随用户重命名而变。**
> 当前显示名与 key 同为 `edu`，但历史上已变过两次（`edu` → `知网基教` → `edu`），
> 而 `mcp.json` 里的 key 始终叫 `edu`。全名形如 `mcp__<SERVER>__tkSearchQuestion`。
> 适配层里只存短名，前缀由 `MCP_PROVIDER` 一个常量决定——**改前缀改一行，不要全文替换**。
> 不确定当前前缀时跑 `reconcile`，它会反推真实前缀（见一·五节）。

| 用途 | 工具名 | 关键参数 | 状态 | 要点 |
|---|---|---|---|---|
| **按关键词搜题** | `mcp__<SERVER>__tkSearchQuestion` | keyword(必填) / subjectCode / type / pi / ps | ✅ ok | ① 关键词含空格会 400，**必须拆成单个词**；② `ps` 上限 10 |
| **按考点搜题（推荐）** | `mcp__<SERVER>__tkSearchSubjectQuestion` | subjectCode(必填) / point(必填,数组) / dg / yr / so / ct / pi / ps | ✅ ok | **比关键词准**：`point` 先从 `mcp__<SERVER>__tkPoint` 拿；`dg`/`yr`/`so` 在服务端筛完再返回。比关键词检索**多返回** `SourceReports`（完整试卷名）、`RealCount`、`PaperCount`，见 2.1 |
| 同考点相似题 | `mcp__<SERVER>__tkQuestionSame` | SID(必填) / subjectCode(必填) / num(必填,≤5) | 未接 | 服务端算的相似，不用我们猜难度；可直接喂 `variants` |
| **试题官方解析** | `mcp__<SERVER>__tkQuestionAnalysis` | SID(必填) / subjectCode(必填) | ✅ ok | **补上最大短板**：搜题接口只带回答案、解析字段全空。回填 `Method`/`Analyse`/`Discuss`/`Points`/`Topics`，见 2.2。合并后校验器做官方答案交叉校验 |
| 题型字典 | `mcp__<SERVER>__tkQuestionType` | subjectCode | 未接 | `mcp__<SERVER>__tkSearchQuestion.type` 需要题型**数字**标识；有字典才能按题型精确取题 |
| 试题来源字典 | `mcp__<SERVER>__tkQuestionFrom` | subjectCode | 未接 | id→来源名（月考/期末/中考）。配 `so` 用；**对「真题新鲜度」标签直接有用**，不必再从 Label 字符串猜 |
| 学科码 | `mcp__<SERVER>__tkSubject` | 无 | ✅ ok | 学科名带学段前缀（"初中物理"而非"物理"），必须学段+学科二维查表 |
| 知识点树 | `mcp__<SERVER>__tkPoint` | subjectCode | ⚠ weak | **返回极大**（30 万字符级会触发截断落盘），只能用 `point` 子命令抽命中项 |
| 教材目录 | `mcp__<SERVER>__tkBook` | subjectCode | 未接 | 标注教材章节、核对"讲到哪一课"时用 |
| **学术文献检索** | `mcp__<SERVER>__searchVectorBJ` | text(必填) / query_type / type / maxRecallNumber / nprobe | ✅ ok | **唯一的篇级文献入口**。返回不含作者/刊名/卷/页码，见第三节 |
| 段落级检索 | `mcp__<SERVER>__searchVectorBJPara` | text / query_type / type | ⚠ weak | 做教辅溯源**不要用**，见第三节末 |
| **账号权益** | `mcp__<SERVER>__userState` | 无 | 建议用 | true/false。**应放在链路最前面**：false 就别往下检索，否则"查不到题"会被误判成题库无覆盖 |

> **没有 `searchLiteratureKnowledge`**。这个工具名在早期文档里出现过，但当前连接器里不存在
> （`ToolSearch` 精确查名返回无结果），已登记在 `mcp_adapters.py` 的 `DEPRECATED_TOOLS` 里。
> **文献检索请用 `mcp__<SERVER>__searchVectorBJ`。**

> **改接口名**：只改 `scripts/mcp_adapters.py` 顶部的 `MCP_ENDPOINTS`
> （tool 存短名 / params / returns / status / note / feeds），改完跑 `endpoints` 验证。

---

## 一·五、登记表会滞后——用 reconcile 对账

`MCP_ENDPOINTS` 必须**手写**（参数、返回、坑都只能人来写清），所以它天然滞后于连接器：
**连接器新增接口，脚本自己感知不到，照着这张表干就会一直用老办法做题。**

这是被坑出来的：第一次把连接器实际暴露的工具全列出来时是 **12 个**，而登记表里只写了 8 个，
漏了 `mcp__<SERVER>__tkQuestionAnalysis` / `mcp__<SERVER>__tkQuestionType` / `mcp__<SERVER>__tkQuestionFrom` / `mcp__<SERVER>__userState` 四个——
其中前三个能直接提升出题质量（`mcp__<SERVER>__tkQuestionAnalysis` 尤其重要，它补上了"题库只有答案没有解析"的短板）。

补救机制是**双向对账**，升级连接器或怀疑漏了接口时就跑一次：

```bash
# 1) Agent 侧列出连接器当前暴露的全部工具，落盘
#    ToolSearch(queries=["题库 试题", "文献 检索", "知识点 学科", "解析 题型 来源"], top_k=20)  ->  tools.json
#    用关键词搜比用连接器名搜稳：名字可能已被重命名

# 2) 与本表比对
python scripts/mcp_adapters.py reconcile --tools tools.json
```

报告把偏差分成五类：

| 段 | 含义 | 怎么处置 |
|---|---|---|
| **`PREFIX-DRIFT`** | 前缀不对 | **会直接打印「把 MCP_PROVIDER 改成 X」**，照改第 39 行一处即可。这个名字随连接器显示名变，已实测变过两次 |
| `PREFIX-OK` | 前缀正确 | 不用管 |
| `OK` | 登记了，连接器里也有 | 不用管 |
| **`BLOCKER`** | 登记了但连不上 | **先看上面 `PREFIX-DRIFT`**（历史踩过的坑：写了 key `edu` 而不是当时的显示名，12 个全军覆没还误判成接口 500） |
| **`NEW`** | 连得上但没登记 | 这就是"新接口会不会漏"的答案。① 查它的参数 ② 判断有没有用 ③ 有用就补进 `MCP_ENDPOINTS` 并写清 params/returns/note/feeds |
| `INFO` | 曾判为不存在又出现了 | 把 `DEPRECATED_TOOLS` 里那条删掉 |
| `IGNORED` | 不属于本连接器 | 忽略 |

**建议节奏**：不做日常检查，只在两种时机跑——① 连接器提示升级/新增工具时；② 遇到"按理应该有这个能力"却发现要绕路实现时（这时大概率是已经有新接口了，只是没登记）。

---

## 二、题库链路

```
① mcp__<SERVER>__tkSubject（一次即可，学科码已固化在适配层）
        ↓
② 检索（两条路，优先按考点）
   ├─ mcp__<SERVER>__tkSearchSubjectQuestion(subjectCode, point=["浮力"], yr="2025", dg=<难度档，11~15区间取值>)  ← 推荐
   │     服务端直接按考点/年份/难度/来源筛完再返回，比事后按 Degree 分档准
   └─ mcp__<SERVER>__tkSearchQuestion(单个关键词, subjectCode, ps=10)   ← 兜底，多词就多次调，别塞空格
        ↓ 原始 JSON 落盘 raw_bank.json
③ （改编题建议）mcp__<SERVER>__tkQuestionAnalysis(SID, subjectCode) -> raw_analysis.json
   mcp_adapters.py analysis --raw raw_analysis.json --out analysis.json
        ↓
④ mcp_adapters.py bank --raw raw_bank.json --analysis raw_analysis.json --out bank.json
        ← HTML 清洗 + 难度映射 + 官方解析/考点合并 + 候选体检
        ↓
⑤ homework_kit.py route --params params.json                 ← 按用途分配 原题/改编/原创
        ↓
⑥ 生成 + validate + render
```

**知识点（`mcp__<SERVER>__tkPoint`）按需用**：只在教师没给课标条目、需要补全 `std_aligned` 时才调；调完立刻用
`mcp_adapters.py point --raw <落盘文件> --keyword 一元一次方程` 抽命中项，
**不要把整棵树读进上下文**。抽出来的考点名可直接喂 `mcp__<SERVER>__tkSearchSubjectQuestion` 的 `point`。

**候选数必须 ≥ 题量 × 1.5**。不足时路由会标 `reused:true` 并告警，校验器也会拦「孪生题」
（两题同 `based_on`）——但那只是兜底，正解是先把候选补足（拆成多个考点分别检索，比换关键词有效）。

### 2.1 按考点检索多返回什么（关键词检索没有）

实测同一学科同一考点，`mcp__<SERVER>__tkSearchSubjectQuestion` 比 `mcp__<SERVER>__tkSearchQuestion` 多三个字段：

| 字段 | 实测值 | 用途 |
|---|---|---|
| `SourceReports` | `[{"Key":"k1","Value":"2025-2026学年湖南省衡阳市衡阳县八年级（下）期末物理试卷"}, …]` | 完整试卷名。比 `Label` 简称「（2026春•衡阳县期末）」信息量大得多，真题新鲜度以此为准 |
| `RealCount` | `5` | 真实考试引用次数——「考过的题」含金量的量化参考，选原题时优先取高的 |
| `PaperCount` | `74` | 收录试卷数 |

`Label` 仍保留（它是印在作业单上的那行简称）。

### 2.2 官方解析：`mcp__<SERVER>__tkQuestionAnalysis`

**为什么必须单独取**：两个搜题接口返回的 `Analyse` / `Method` / `Discuss` **全是空字符串**，
只有这个接口回填。没有它，作业单的解析只能靠模型写，第 14 条验算就成了模型自证。

实测返回（2026-09-30，初中物理选择题）：

| 字段 | 内容 |
|---|---|
| `Method` | 详解正文：「解：A．…故A错误；B．…故B正确；…故选：B。」（含 HTML，已由 `strip_html` 清洗） |
| `Analyse` | 简析，要点式，比 Method 短 |
| `Discuss` | 考点点评 |
| `Points` | 考点（带 ID）：`[{"Key":"241932","Value":"阿基米德原理的定性分析"}, …]`——**只有这里回填** |
| `Topics` | 专题（带 ID）：`[{"Key":"584","Value":"浮沉的应用"}, …]` |

适配层取 `body = Method or Analyse or Solutions[0]`；`has_official` 标有没有解析。
**不是每道题都有解析**，返回空的题不要编解析。

合并后 `bank` 项多出 `official_analysis` / `official_answer` / `points` / `topics`，
校验器据此做交叉校验（retrieve 答案不符阻塞，adapt 改答案未说明提醒，见 SKILL.md 第 14 条）。

### 2.3 `dg` 难度档：只用来筛，不用来定档

接口文档标注「11=易(0.8~1.0) … 15=难(0.0~0.2)」，但返回里的 `Degree` 是**越大越难**
（0.6 以下基础、0.85 以上拓展），两者方向相反——推测 `dg` 的区间指的是**正确率**而非难度。
**未实测校准前，只用 `dg` 做服务端筛选，定档一律用返回的 `Degree`。**

校准方法：同一考点分别取难度档区间的低端与高端各取一批，比较返回 `Degree` 的均值方向即可判定。

---

## 三、文献链路（重点：接口只给一半字段）

### 3.1 `mcp__<SERVER>__searchVectorBJ` 到底返回什么

```
{
  "code": 200, "msg": "检索成功！",
  "data": [{
    "product": "CJFD",            # CJFD=正式出版；CAPJ=优先出版（未定刊期，尽量不用）
    "resource": "JOURNAL",
    "相关度": "38.1%", "距离": "0.7257",
    "SYS_TABLENAME": "<内部数据表名>",
    "文件名": "<刊码+年份+期号+序号>",     # ← 刊码 + 年份 + 期号 + 序号
    "篇名": "促进认知发展的阿基米德原理探究教学",
    "正文": "科学探究教学应以促进学生的科学认知为核心…",   # 实为摘要
    "小标题": "1 问题的提出 …"                              # 可缺
  }]
}
```

**它不返回作者、刊名、卷号、页码。** 这四个字段是 GB/T 7714 五要素里的大头，
缺了就成了「有篇名没出处」，教师照样没法核。

### 3.2 文件名是唯一能机器读出的著录

`文件名` = 刊码 + 年份 + 期号 + 序号，**只对 `product=CJFD` 成立**：

| 文件名 | 解析 |
|---|---|
| `<刊码>+2023+10+004` | 2023 年 · 第 10 期 |
| `<刊码>+2017+31+022` | 2017 年 · 第 31 期（周刊，期号可 >12） |
| `<刊码>+2001+S2+051` | 2001 年 · S2 增刊 |

`mcp_adapters.py` 的 `parse_lit_filename()` 负责解析，年份与期号直接进入输出记录。
`CAPJ`（优先出版）编码规则不同，期号不可信，一律不解析。

### 3.3 补齐流程（四步，缺一不可）

```
① 调 mcp__<SERVER>__searchVectorBJ 拿候选        -> raw_lit.json
② mcp_adapters.py lit --raw raw_lit.json --out sources.json
   → 得到篇名/摘要/年份/期号，author/container/volume/pages 为 None 并记进 need_fields
③ 针对每条的【篇名】去核实作者、刊名、卷、页码，写进 fill.json
   （格式：{篇名: {author, container, volume, pages}}）
④ mcp_adapters.py lit --raw raw_lit.json --fill fill.json --out sources.json
```

**用第 ② 步解析出的年份 + 期号交叉校验第 ③ 步的核实结果**。两边对不上时，
`fill_lit()` 保留 **CNKI 文件名的值**（它是 CNKI 自己的编码，可信度更高），
并在 `notes` 里记下冲突交人工确认。

**绝对不能做**：凭印象补一个作者或刊名。缺字段留 `None` 渲染成灰色【待补充】——
**缺 = 待补，填错 = 编造**，后者直接毁掉这套方案的地基。

### 3.4 段落库不要用

`mcp__<SERVER>__searchVectorBJPara` 是段落级检索。实测检索「控制变量法」大量命中计量经济学、
图像处理类论文（它们也讲"控制变量"），与中学教学无关。
只有要定位某篇**已知文献**的某个章节时才值得用。

---

## 四、降级策略（拿不到数据时怎么办）

| 情况 | 做法 |
|---|---|
| **edu 连接器未启用** | 先去连接器管理页启用并信任，重开会话。不要绕开它用别的来源凑数据 |
| **题库无学科覆盖**（如音体美） | 全部走 `generate`，交付说明写明"原创占比 100%，答案须教师逐题复核" |
| **文献检索无命中** | ① 优先把情境题改为无情境题（纯计算/技能题不要求溯源，校验器不拦）；<br>② 或 `gen_cap=0` 全走题库，用 `Label`（试卷出处）替代学术溯源；<br>③ 不摘编造文献 |
| **候选题不足** | 扩大关键词、翻 `pi`、按知识点拆分多次检索，补足到 ≥ 题量×1.5 |

> 第 3 级的③会被校验器拦（原创无素材 / 溯源必填），因此**必须**同时把该题改成无情境题
> 或降级为改编题，否则流程走不完。

---

## 五、字段映射（题库原始 → 内部格式）

| 原始字段 | 内部字段 | 说明 |
|---|---|---|
| `SID` | `bank_id` | 全局唯一，用作 `source_id` / `based_on`。**只是内部流水号，不得直接印在作业单上** |
| `Content` | `content`（已清洗） | 含 `<del>` 高亮、`<sup>` 角标、MathJye 分数表格、填空占位 |
| `Degree` (0–1) | `level` | <0.6 基础 / 0.6–0.85 巩固 / >0.85 拓展（阈值 `DEGREE_THRESHOLDS` 可调） |
| `Label` | `source_label`（retrieve）<br>`based_on_label`（adapt） | 试卷出处。**这才是要印在作业单上的** |
| `DisplayAnswer` / `Answers` | `answer` | 优先 `DisplayAnswer`（如 "D"） |
| `CateName` | `qtype` | 选择题/填空题/… |
| `Date` (ms) | `year` | 毫秒时间戳转年份 |

> **陷阱**：`bank_id`（常顺手编成 `Q01`…）对外毫无意义，教师既看不懂也无从核题。
> 作业单上的「改编自」必须显示 `Label`（真实试卷出处）；缺 `based_on_label` 时校验器会告警。
> 落盘 `bank.json` 务必保留 `metadata.label`，否则事后无法回填。

**HTML 清洗效果**：`<table>1/x</table>`→`1/x`；`x<sup>2</sup>`→`x^2`；
`<del>一元一次方程</del>`→`一元一次方程`（去搜索高亮）；`<!--BA-->…<!--EA-->`→`____`（填空位）。

---

## 六、学科码解析规则

| skill 学科包 | 学段 | subjectCode |
|---|---|---|
| 数学 | 小学 / 初中 / 高中 | 10 / 20 / 30 |
| 语文 | 小学 / 初中 / 高中 | 11 / 26 / 36 |
| 英语 | 小学 / 初中 / 高中 | 12 / 27 / 37 |
| 理化生 | 小学(科学) / 初中 / 高中 | 14 / 物理21·化学22·生物23 / 31·32·33 |
| 政史地 | 小学(道法) / 初中 / 高中 | 15 / 道法28·历史29·地理25 / 政治38·历史39·地理35 |
| 音体美 | — | **无覆盖** → 全部 generate |

**复合学科包必须确认二级学科**：`code --subject 理化生 --stage "初中(7-9)"` 会返回
`{"need_confirm": true, "candidates": ["化学","物理","生物"]}`，要求用 `--sub` 指定。
物理题和化学题混在一起是典型事故，不能靠猜。

**直接传细分学科名同样要能解析**：`code --subject 物理 --stage "初中(7-9)"` → `21`
（靠 `_SUBJECT_PARENT` 归一化）。旧版只认复合包键，传"物理"会返回 `null`
并被误判成"题库无该学科覆盖"而整批降级成纯原创——实测踩过。

**题库无年级粒度**：小学数学只有 `subjectCode=10`，不区分一二年级和五六年级。
所以小学低段的书面红线**只能靠校验器兜底**，题库侧拦不住。

---

## 七、运行环境

脚本只依赖 Python 标准库，无需 pip 安装。用当前环境可用的 `python` 或 `python3` 调用即可：

```bash
python scripts/mcp_adapters.py endpoints
python scripts/mcp_adapters.py code --subject 物理 --stage "初中(7-9)"
```

若 `python` / `python3` 都不可用（部分 Windows 环境），改用绝对路径
（如 WorkBuddy 托管的 `binaries/python/versions/*/python.exe`）。
