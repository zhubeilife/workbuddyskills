# 发起流程

## 什么时候读取

用户要"发起/创建/提交一个 XX 流程""按某工作流填写表单并发起"时读取本文件。覆盖 `workflow.createForm` / `workflow.createRequest` 两条命令。

## Operation

| Operation | 风险 | 固定规则 |
| --- | --- | --- |
| `workflow.createForm` | read | 必传 `workflow`（`名称(ID)` / 名称（**可一次给多个说法**：数组多元素，或一个元素内用英文逗号分隔）/ ID）：内部解析出**可发起**的工作流并载入发起表单，返回字段清单 / 历史参考值 / 续跑句柄（见「返回」）。不落任何业务数据。解析不出唯一目标时回澄清（`NEEDS_CLARIFICATION`，候选见 `candidates`）。**已给 `名称(ID)` / 纯 ID 时不查可发起列表**（名称与可发起性直接由表单载入接口给出），该 ID 不存在 / 无发起权限时同样回澄清，但带 `clarificationReason` 区分 |
| `workflow.createRequest` | high-risk-write | requiresConfirmation；必传 `context`/`data`/`action`；`action` **必填**（`draft` 存草稿 / `submit` 提交审批）；遇 `partial`/`write_uncertain` 禁止重试 |

## 发起流程固定执行流程（三步，不增不减）

| 步 | 命令 | 做什么 |
| --- | --- | --- |
| 1 | `workflow.createForm` | 用用户说法解析可发起的工作流并**加载表单字段**：拿回 `fields`（**每个能填的字段一行**，有默认值的字段带 `initialValue`）、`historyRequestData`（历史参考值）、`continuation`（下一步的 `context`） |
| 2 | `workflow.createRequest` | 按「填值纪律」把值拼进 `data`，`context` 传第 1 步的 `continuation`，`action` 取 `draft` / `submit`，**发起流程** |
| 3 | —（无命令） | **把第 2 步的返回结果输出给用户**：有 `finalMarkdown` 就**原样粘贴**（一字不改）。**小e 环境例外：命令 stdout 整体就是一段 `<browsertool>` 标签块（没有 JSON 信封）**——见到输出以 `<browsertool>` 开头，就把**整段原样输出**（从 `<browsertool>` 到 `</browsertool>`）：**不要用代码块（三反引号）包裹、不要加任何前后说明、不要解析它、也不要去找 `status` / `contextId`**（这一档不打信封）；没有 `finalMarkdown`（如 `NEEDS_CONFIRMATION`）才按「主表（已填内容）展示规则」+「明细表（子表单）展示规则」自己拼。**不要重跑任何命令、不要自己再去查一遍流程。** |

澄清、必填缺失、幂等重放等分支见下「发起链路」。

## 发起链路（两条命令的完整分支）

1. `workflow.createForm`：按用户说法解析可发起的工作流并载入表单，拿回 `continuation`（表单会话短句柄，载荷由 CLI 托管在本机）与 `fields`（**每个能填的字段一行**：`id` + 中文名 `name` + 所属明细 `subFormId`（主表字段省略该键）+ `componentKey`；**有默认值的字段直接带 `initialValue`**）；**同时返回 `historyRequestData`**——本表单**要落值的字段**（口径同 `fields`）在历史流程里的取值参考（`null` = 没有可参考的）。
   - 返回 `NEEDS_CLARIFICATION` 时按 `candidates` 向用户确认（只问完整名称或其它可用于检索的关键词，**不要向用户索取 ID**），确认后由你按 `名称(ID)` 拼好、重发**同一条命令**。
2. 按用户意图把字段值填进 `data`（键用字段 id）：**照「填值纪律」的优先级逐个字段一遍定案**——用户说了的照用户说的填；用户没说到、而该字段带 `initialValue` 的就用默认值（也可以干脆不传，CLI 会自动并入）；其余字段按「历史流程数据参考规则」判断能不能落值。
3. `workflow.createRequest`：`context` 传第 1 步返回的 `continuation`，`action` 按用户意图取 `draft`/`submit`。
   - `action: "submit"` 且仍有必填缺失 → **命令不会创建流程**，返回 `NEEDS_INPUT` + `missingFields` + **渲染好的 `finalMarkdown`**（已填内容 + 明细 + 待补必填项清单；**历史取值一致的待补字段，命令已附一行 `历史推荐值`**）；**不做任何值推断**——**把这份 `finalMarkdown` 原样发出**（与成功时完全同一口径：不弹窗、不挑字段、不自己列待补项、不解释），带同一 `context` 重发 `action: "submit"`。
   - `action: "draft"` 且仍有必填缺失 → 照常建草稿，`missingFields` 只作提醒（必须原样转述给用户）。
   - **不要（也无法）自己判断"必填是否齐"**：缺失与否由命令按**实际所填数据**（含联动带出值）实时算出，照 `missingFields` 走即可。
4. 成功时命令**直接返回 `requestId` / `requestName` / `url`**（`status` 为 `CREATED` = 已建草稿、`CREATED_SUBMITTED` = 已提交审批）——**按返回值汇报即可，不需要再去查询反查**。
   - **发起/查询完成后不要主动打开任何页面**：`url` **只在回复文本里以可点链接给出**，**不要**把它交给浏览器预览面板、也**不要**顺手调 `workflow.open` / `workflow.pageOpen` 去"打开看看"。**只有用户明确说"打开这条 / 打开看看 / 给我链接"时**才打开——用 `workflow.pageOpen`（动态页 `page:"view"` 配 `requestId`）或 `workflow.open` 走正规入口，**地址一律由 CLI 按内置地址表生成，不要自行拼接 OA URL**。
5. 遇 `partial`/`write_uncertain` 停止，先只读回查（detail/summary），不自动重放。
6. 被重复执行时按句柄状态分流（**不要一看到"用过"就重跑整条链路**）：
   - `ok:true` + `data.status = "ALREADY_APPLIED"`：该 `context` 上一次已经**发起成功**，本次没有重复写入——按返回值里的 `requestId` / `previousResult` 作为成功结果汇报，**不要重跑 createForm、不要再 createRequest**；
   - `partial`/`write_uncertain`：上一次已经发出写入、结果未确认——先只读回查（`workflow.search --category mine --requestId <目标ID>`）确认是否已发起，确认没发起才重跑；
   - `validation/continuation_busy`：该 `context` 正被另一次执行占用、上一次还没发出写入——**稍后原样重试同一条命令**即可（不要重跑 createForm、不要换句柄）；
   - `validation/continuation_consumed`：占用该句柄的执行停在无法判定的旧状态——先只读回查确认是否已发起，确认没发起才重跑。

**省时纪律（这几件事一次都别做，每违反一条就多烧一轮工具往返）**：① **字段 id、中文名、默认值都在 `createForm` 的 `fields` 里**（每个能填的字段一行），**不要再为它们做任何额外查询**；只有确实需要某个字段的**选项清单**（`options`）等细节时才看 `fields` 里那一条；② `data` 的键**不要**写 `"字段名(字段ID)"`（只认字段 id）；③ 只读字段**不要**传（`fields` 里带 `readOnly` / `disableEdit` 的，即使出现也不要填）；④ 读命令输出**不要**用 `head`/`tail` 截断；⑤ 输出被宿主截断时**不要**去找宿主的工具结果目录（`~/.workbuddy/projects/**/tool-results/**`：读不了，去了必白跑一轮），按输出最前面的 `resultFile` 取。

**输出纪律（与上面的省时纪律同理：多写的每一句都在拖长回复，并让用户看不懂）**：① 面向用户**只给三样**——"这次做了什么、结果如何" ＋ "**已填内容预览**"（展示口径见下文「主表（已填内容）展示规则」）＋ "需要用户提供什么"，其余不说——**尤其不要交代"用了哪个流程 / 编号是多少 / 我是怎么判断的"这类内部依据**；② **不要复述自己的判断过程、取舍与推演**，也不要写自我批评或事后反省——用户要的是结果，不是你怎么想的；③ **不要把澄清分支的区别讲给用户**（如"不是有多个候选要挑，而是一条都没命中"）：该报"系统里没有「XX」"就按下文浏览按钮口径直接说结论，**不要解释你是怎么判定出来的**；④ 需要用户给值时**只说清"要什么值"**，不要顺带解释"我为什么判断不出来"。

## 填值纪律（一遍定案，不许回头）

拼 `data` 只走一遍：**按字段逐个落值，每个字段只做一次取舍、取完不再回头看**；落到值就离开这个字段，不在同一字段上比较第二轮。

**一趟走完、一个字段一行**——照这个形状（`<…>` 是占位，实写时换成本次的真字段与真值）：

```text
拼 data。
用户要求：<本次要办的事>；<用户本轮给出的值>。
字段分析（主表 main）：
<字段id-1> <字段名>（文本）：用户本轮说「<原话片段>」→ 填 "<据原话取的值>"
<字段id-2> <字段名>（人员，带默认值）：默认值「<默认值>」，用户未改写 → 不传
<字段id-3> <字段名>（浏览按钮）：历史 5 条取值全同「<名称(ID)>」→ 填 "<名称(ID)>"
<字段id-4> <字段名>（选项）：历史取值互不相同、推不出规律 → 留空
<字段id-5> <字段名>（日期，带默认值）：默认值「<默认值>」，用户未改写 → 不传
<字段id-6> <字段名>（附件）：用户本轮发了文件并指名放这里 → 先上传取 file_id，填 "<file_id>"；没发文件 → 留空
字段分析（明细 details["<子表单id>"] 第 1 行）：
<字段id-7> <字段名>（数字）：用户本轮说「<金额说法>」→ 填 "<金额>"
<字段id-8> <字段名>（选项）：历史 5 条取值全同「<选项值>」→ 填 "<选项值>"
<字段id-9> <字段名>（日期）：历史 <值1> / <值2> / <值3> 逐期往后推一期 → 填 "<代入结果>"
<字段id-10> <字段名>（发票）：用户本轮发了发票文件 / 指名从票夹取 → 先取发票对象再填；否则不复用 → 留空
<字段id-11> <字段名>（浏览按钮）：无原话、无默认值、历史无值 → 留空
字段走完 → 拼 data → createRequest。
```

- **判决只有三种**：`填 "<值>"` / `不传` / `留空`——一行里只出现一个，不并列两个候选、不写"或者 / 可能 / 我倾向"。**唯一例外是附件 / 发票这两类**：它们的判决取决于"用户本轮有没有给文件"，按下面「附件 / 发票字段」写在**同一行**里（条件 ＋ 各自一个结果），不拆成两行、不留到下一轮。
- **一行只看这个字段自己**：依据取用户本轮原话 / 它自己的 `initialValue` / 它自己的历史取值；这个字段的事在这一行里判完就离开，不顺手推演别的字段。
- **要按历史推演的，就在它这一行里推**：推出式子直接代成值写进判决，推完即走。
- **一个字段只出现一次判决**，后面不再回头改；字段过完就拼 `data`（判决为"填"的进 `data`，`不传` / `留空` 都不写），**紧接着 `createRequest`**。

每个字段的来源顺序（**命中即定案，后面的来源不再看**）：

| 顺序 | 来源 | 动作 |
| --- | --- | --- |
| 1 | 用户本轮原话 | 用户说了这个字段 → 按用户说的填，**结束** |
| 2 | 字段默认值（`fields[].initialValue`） | 用户没说到、该字段带 `initialValue` → **用默认值**（不传也行，CLI 会自动并入），**结束** |
| 3 | `historyRequestData` | 用户没说、也没有默认值 → **按「历史流程数据参考规则」只判一次**，能落值就落，**结束** |
| 4 | 规则不适用 | 用户没说、没默认值、历史也落不出值（或**不符合历史数据参考规则**）→ **留空、不填**，**结束**（留给 `missingFields` 一次问齐） |

**每一格的"结束"都是真的结束**——不要因为"再想想会不会更准"而退回上一格。

**字段的 id、中文名、默认值全在 `fields` 里**（`createForm` 返回，每个能填的字段一行）——**不要为了拿名称或默认值再去读 `resultFile`、更不要重跑 `createForm`**（唯一例外：大表单超线时 stdout 里没有 `fields`，那时它只在 `resultFile` 里，按「返回」的大表单超线形态读一次即可）。

- 带 `initialValue` = 该字段**表单初始化时就有值**（OA 预填，或 onLoadForm 联动带出），**CLI 拼 `data` 时会自动并入**：不要显式传、不要逐条复述、也不要再判断一遍——**用户本次明确改写了它才按用户说的覆盖**。
- `fields` **不区分必填**：它就是「可编辑 ∪ 必填且可见」的全集，能出现在这里就是能填的字段。**不要自己推演"哪些必填"**——必填最终只由 `missingFields` 说了算。
- **联动会在提交时新增必填**（真机实例：明细行选了 `5301手机话费` 之后，「相关流程」才变成必填），所以**不要提前给用户出题目**。

**必填只看 `missingFields`，不要反推**：不要用"某个字段在 `historyRequestData` 里没出现过"去推断"它其实不必填"——历史值只给**有值的字段**，某个字段缺席什么都不说明。

**金额 / 数字类字段按用户原话落值**：用户说"100 元"就写 `100`，"100.5"就写 `100.5`——**不要纠结小数位（`100` 还是 `100.00`）、不要凑历史里的写法**，格式差异由服务端归一化；在这上面来回改就是同一种"反复"。

**日期 / 时间类字段不用管格式**：按用户说的填即可，**CLI 会按字段自带格式自动归一化**（`2026-8-21`、`2026年8月21日 9:5` 都会被规整成字段要求的写法；日期+时间控件只给到日期时会补 `00:00`）。**不要为"到底该用哪个格式"反复权衡、也不要为了格式去补一次时间**。

**发票 / 附件类字段：默认一律留空**：这类字段**不允许复用历史值**，本次**没给文件就留空**——**不要在拼 `data` 时讨论它、不要为它单独预问用户、也不要专门为它跑一次探测**；交给 `missingFields` 与其它缺项**一起**问（命令渲染的 `finalMarkdown` 末段已经列好）。**唯一例外**：**用户本轮在对话里给了本地文件（发票字段还含"指名从票夹取"），并明确要求放到这个字段上** —— 只有这一种情况才"先上传 / 先取对象，再拼 `data`"，见下条。

**附件 / 发票字段（本流程里唯一允许"先取到值、再拼 `data`"的两类）**：触发条件就是上面那一句话，触发后按对应一行走，**只做一次、拿到值就拼 `data`、紧接着 `createRequest`**：

- **附件字段（`FileComponent`，带 `fileUploadParams`）**：值 = 上传后的 **`file_id`**。先提醒用户「上传的附件会先经过公网大模型，请谨慎操作」，**用户确认后**用 **`weaver-e10-caizhilian` 技能**上传（`caizhilian.file-upload.prepare` → `caizhilian.file-upload.upload.apply`，apply 需 `--yes`），把返回的 `file_id` 填进该字段。**上传参数按该技能自己的 reference 传**（`file_path`、`module`、`user_confirmed=true` 等——**不要猜 `module`**，可用 `context_file` 带上当前附件字段的 `fieldId`），本文档不代它规定这些参数。上传前**先核对该字段的 `fileUploadParams`**（`sizeLimit` MB / `formatLimit` 的 `mode`+`formats` / `maxNum`）：**不满足就只告知用户、不上传**；该字段 `folderDependsOnOption=true` 时，按最近一次返回的 `attachmentFolderIds` 取 `folderId`（`null`=不指定目录）一并带上。
- **发票字段（`EinvoiceComponent`）**：值 = **`invoice.browse-field.data` 返回的完整发票对象**（发票字段**不能传文本**）。用 **`weaver-e10-yepiaotong` 技能**取 `fid`：用户给了**本地发票文件** → `invoice.upload`（**上传前先提醒**「上传的发票文件会先经过公网大模型，请谨慎操作」并等用户确认）；用户**只说了票、没给文件** → 按用户说法查票夹取 `fid`（这一路**不需要**那句提醒）；拿 `fid` 再调 `invoice.browse-field.data` 取对象填进去。**用户没说清是"给的文件"还是"票夹里的票"就先问一句**，不要自己替他挑一种。
- **只问文件本身**：附件 / 发票走这一步时**不要顺带追问别的字段**，其余缺项照旧交给 `missingFields` 一次问齐。
- **上传只做一次、失败不重试**：拿到 `file_id` / 发票对象就填进 `data`，**不重传、不改写法重试**；上传失败（连接中断 / `write_uncertain` 一类）直接把结果告诉用户，由用户处理。

**拼完 `data` 立即发 `createRequest`**：中间不自检、不重列必填、不复述、不先把表格打给用户看一遍。

## createRequest 返回后的处置（三条分支，照着做）

命令一返回就按下面分流，**不要跨分支权衡、不要解释自己的判断依据**：

| 返回 | 处置 |
| --- | --- |
| `BROWSER_FILL`（小e 环境） | **这一档没有 JSON 返回**——命令 stdout 直接就是那段 `<browsertool>` 标签块本身（看不到 `status` / `finalMarkdown` 这些键名）。**把命令输出整段作为本轮回复正文**：从 `<browsertool>` 到 `</browsertool>` 原样输出，**不要用代码块（三反引号）包裹、不要加任何前后说明**。它交给宿主浏览器页面去打开新建页并带上字段值；本档**不写服务端、不判必填缺失**。 |
| `NEEDS_INPUT`（必填缺失） | **不做任何值推断**——不看历史值、不用记忆里的常用值、不逐字段推演、不解释"为什么判断不出来"。**原样粘贴返回的 `finalMarkdown`**（命令已渲染好：结论一句 + `**已填内容**` 两列表 + `**明细表**` Excel 列 + `**还需要你提供**` 待补清单）——**一字不改、不弹窗、不自己列待补清单**。清单里带 `历史推荐值：` 的行是**命令按历史值一致性算好的**（全部一致或最近三条一致才会出现）——**不要自己再算一遍、也不要回头去翻历史**；用户认可就直接采用，其余项等用户给值后带同一 `context` 重发。 |
| `CREATED` / `CREATED_SUBMITTED`（成功） | **原样粘贴返回的 `finalMarkdown`**（命令已渲染好：结论一句 + 流程编号/链接 + `**已填内容**` 两列表 + `**明细表**` Excel 列）——**一字不改、不重排、不自己再拼一遍表格**；链接**只出现在回复文本里**，不要打开。 |
| `CREATED_SUBMIT_FAILED`（失败） | 同样**原样粘贴 `finalMarkdown`**（流程信息照常完整给出，末尾带 `**提交失败原因**：…`）；不要读成"什么都没做成"，不要重发同一次提交。 |

**`finalMarkdown` = 命令渲染好的最终回复文本**（与查询侧的 `finalMarkdown` 同口径）：在**「流程已落地」三态**与 **`NEEDS_INPUT`（必填缺失）**返回，**本轮回复正文 = 它的值本身（从第一个字符到最后一个字符，不增不减）**；`BROWSER_FILL`（小e 环境）是**同一份渲染档、换了投递方式**——它不经 JSON 信封，命令 stdout 整体就是那段 `<browsertool>` 标签块，**原样输出、不要包在代码块里**（见处置表，那里看不到 `finalMarkdown` 这个键名）；其余状态字段、表格、待补清单、缺项的类型提示都已渲染在里面，不需要你再组织任何内容。**`**已填内容**` 两列表列的是「用户在表单上看到的、有值的、可编辑的主表字段」**（流程标题在前，业务字段按**表单布局顺序**随后，**含表单默认值**；只读/禁用、联动隐藏、没值的字段不列）——所以**里面会出现你没传过的字段（默认值）**，那是命令按表单实际已填状态渲染的，**照贴、不要删、不要改写、也不要把某个字段挪进待补清单**。它已包含全部要交代的内容——**回复里不出现它之外的任何内容**。`NEEDS_INPUT` 那份的读法：末段「**还需要你提供**」就是要问用户的全部内容（每项已标出在主表还是明细第几行），照它问即可——**不要回去翻历史值、也不要自己再列一遍**；其中带 `历史推荐值：` 的行是命令算好的，照抄即可（不必自己核对、更不要自己另算一条）。`finalMarkdown` 随 CLI **0.1.24** 起返回（`NEEDS_INPUT` 那份从 **0.1.25** 起、其 `历史推荐值` 行从 **0.1.26** 起）；老版本命令没有这个字段时，才按下文「主表（已填内容）展示规则」+「明细表（子表单）展示规则」自己拼。

`NEEDS_CONFIRMATION` / `partial` / `write_uncertain` / `ALREADY_APPLIED` 等其余状态**不给** `finalMarkdown`，按「返回」与「发起链路」里的对应条目处置（`ALREADY_APPLIED` 是"上一次已成功"的幂等回报——按返回值里的 `requestId` / `previousResult` 汇报）。

## 输入

### workflow.createForm

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `workflow` | `string[]` | 是 | 工作流条件——`"名称(ID)"` / 纯名称 / 纯数字 ID；**可一次给多个说法**：数组多元素，或一个元素内用英文逗号分隔（两者完全等价） |
| `relatesTo` | `string` | 否 | 关联对象 id，**仅透传**，不影响表单初始化 |

- **自带显式 ID（`"名称(ID)"` 或纯数字）时不查可发起列表**：流程名与"你能不能发起"都由表单载入接口直接给出，因此比"按名称解析"少一整次往返。该 ID 不可用时仍回澄清，但会带 `clarificationReason` 说明是**哪一种**（见下）。
- **纯名称**按当前用户**可发起**的工作流做模糊匹配，**可一次给多个说法**：数组多个元素（`["<说法1>","<说法2>"]`）与一个元素内用英文逗号分隔（`["<说法1>,<说法2>"]`）**完全等价**，CLI 会把各说法拆成关键词、命中取并集去重。
- **直接选定并载入表单**时，`selectionSource` 标明是如何选定的：`workflowId`（按 ID 命中）/ `single`（唯一命中）/ `exactName`（全名精确匹配）。`exactName` 表示 CLI 已替用户选定，**不要再反问“您指的是哪一个”**。
- **0 命中**，或**多命中且没有与所写完全一致的** → **澄清**：返回 `status: "NEEDS_CLARIFICATION"` + `candidates`（每项含 `id`/`name`/`display`，`display` 是 `名称(ID)`），此时**不返回任何表单数据**。把候选**原样**列给用户（不加 "(Recommended)"/"推荐" 等后缀，由用户明确选择），选定后用 `display` 的 `名称(ID)` 重发同一条命令。
- **自带显式 ID 但该 ID 不可用** → 同样回澄清（`candidates` 为空），并带 `clarificationReason` 标明是**哪一种**——这两句话**必须分开说、不许混**：
  - `clarificationReason = "workflow_not_exist"`：该目标不存在（可能已删除或被停用）。如实告知"这个目标不存在"，请用户改用该流程的**完整名称**（或其它可用于检索的关键词）重发——**不要向用户索取 ID**；**不要**说成"没有可发起的工作流"这类模糊说法。
  - `clarificationReason = "no_create_right"`：流程**存在**，但当前账号**没有发起权限**。**必须明确说出「存在但没有发起权限」**，绝不能转述成"流程不存在"；并给出下一步：改用其他可发起的流程，或联系管理员为该流程授予发起权限。

**查询词策略**：

- **优先用记忆别名改写后再传**：用户给出的表达命中记忆别名（如"手机话费报销"含别名"费用报销"）→ **直接传记忆别名**（可与原词并列成一次多关键词，见下条），**不要分两次命令试探**（先只传原词、没命中再换一个词）。
- **一次给多个说法**：`workflow` 同一批次可并列多个说法（数组多元素 或 英文逗号分隔）；**不确定完整名称时，把①用户说法 ②可能的全名/同义说法 ③一个更宽的「上位词」都并列进这一批**（如 `["原说法","同义说法","上位词"]`）。**同一批次加词不额外花往返**：命中取并集去重，某个词命不中只是白给，命中了就多一条线索。
- **上位词可以放进批次，但命中后必须核对**：`"话费"` / `"会议"` 这类宽词可能命中**语义无关**的工作流（如“话费”→“话费补贴标准审批流程”）。载入表单后**先核对 `workflow` 里的名称/类型与用户意图是否一致**（报销类意图 → 名称应含“报销/费用”，不应是“补贴标准/行政事务”类）；**不一致就绝不要往下填字段**，改用记忆别名或更准的说法重发 createForm。**`selectionSource: "single"`（唯一命中即选定、不澄清）是最该核对的一档**。
- **真正被禁的是"分多次命令逐词去撞"**：禁止先甲、再乙、再丙地反复试（把"换词"当检索策略，每试一次多烧一轮往返）；**同一条命令里并列多个词、其中包括一个上位词，都不属于被禁的情形**——那是**补充召回**，不是拿宽泛词当主力检索。
- **不要再继续换词试探**（一次多关键词后仍未定，就反问用户确认）。

**拿到 form 返回后直接按用户已给信息拼 `data` 并立即调用 `createRequest`**——不分析字段、不猜映射、不比对选项，**也不要用空 `data` 先探测必填清单**（用户说了什么字段就填什么、值用用户说过的说法；必填缺失由 `createRequest` 的 `missingFields` 告知）。**填值时按「填值纪律」一遍定案**——每个字段只做一次取舍、取完不再回头。

### workflow.createRequest

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `context` | `string` | 是 | **第 1 步 `createForm` 返回的 `continuation`**（同一值），原样回传；禁止手工构造/修改/复用他处 |
| `data` | `object` | 是 | 表单字段值，结构 `{"main":{...},"details":{"<subFormId>":[{...}]}}`；键**必须是字段 id** |
| `action` | `"draft"` \| `"submit"` | 是 | `submit`=提交审批（必填缺失阻断，返回 `NEEDS_INPUT`，**不创建流程**）；`draft`=仅保存草稿（必填缺失不阻断、状态仍是 `CREATED`，但 `missingFields` 仍随结果返回） |
| `requestName` | `string` | 否 | 流程标题。**通常不用传**——`createForm` 已给出标题、CLI 会自动并入；只有用户本次明确改写了标题时才传 |
| `requestLevel` | `string` | 否 | 紧急程度，取 `systemFields.levelOptions` 的 code |
| `secLevel` | `string` | 否 | 密级，取 `systemFields.secLevelOptions` 的 id |
| `remark` | `string` | 否 | 签字意见 |
| `verificationConfirmed` | `boolean` | 否 | 节点字段校验需用户确认时显式确认继续提交 |

**`requestName` 补充分寸**（不传时的兜底）：`createForm` 返回的 `requestName` 非空（OA 已有标题）时用其值；为空时**只有用户原话明确给了标题**（如"标题叫 X"）才用用户给的；**用户没给就不要自己编**——标题 `ismandatory=true` 且没有可用的默认值时，`createRequest` 会返回 `NEEDS_INPUT`，按 `missingFields` 向用户问一次并补齐。**标题不得用其他字段值（留言内容/工作流名/事由等）替代**：标题是用户可见的流程名称，用别的字段内容做标题会与流程内容耦合，OA 列表里难以辨识。

## 返回

### workflow.createForm

| 键 | 说明 |
| --- | --- |
| `status` | `FORM_READY`（载入成功）/ `NEEDS_CLARIFICATION`（解析不出唯一目标） |
| `contextId` / `continuation` | **同一个值**（会话短句柄 `wc-…`）：第 2 步 `createRequest` 的 `context` 入参 |
| `requestId` | **预生成**的流程请求 ID——只是本次单据的身份标识，**此时流程尚未创建**（不是已存在的流程编号/草稿号） |
| `requestName` | 表单自带的流程标题（可能为空串） |
| `workflow` | `{id, name, description, type_name, selectionSource}`；`selectionSource` 见「输入」 |
| `form` | `{id, layout_id}` |
| `fields` | **字段清单（唯一一份）**：所有「可编辑 ∪ 必填且可见」的字段，每个字段一条记录（**整块在 stdout 上压成单行**，见下），见下 |
| `historyRequestData` | 本表单**要落值的字段**（口径同 `fields`）在历史流程里的取值参考（`null` = 没有可参考的），见下 |
| `systemFields` | `{permissions, defaults, levelOptions, secLevelOptions}`——系统字段的权限与默认值，见下 |
| `systemFieldWarning` | 系统字段权限读取失败时的提示文本（正常为 `null`） |
| `requiredInfoWarning` | OA 未下发静态字段权限时的告警文本（正常为 `null`），见「注意」 |
| `launchPreferences` | 该工作流的发起偏好（`available` + `promptText`），见下 |
| `fileUploadParams` | 附件字段的上传限制，挂在对应字段的 `fields[].fileUploadParams` 上 |

**stdout 紧凑形态**：`fields` / `historyRequestData` / `systemFields` 这三个键在 stdout 上是**压成单行的**——只去掉缩进空白，**内容、结构、键序一字不改**（`parse` 出来与多行版完全一致，可以直接读）。所以 `fields` 那一行字段多时可能上万字符：**这是正常的，不是被截断、也不是数据缺失**，照常按 JSON 解析即可。**不要**因为"这一行太长 / 看着不像完整 JSON"就去读 `resultFile` 或重跑命令；`contextId` / `workflow` 等其余键仍是正常的多行缩进。

**`fields[]` 每个字段的键**（**能出现在这里就是能填的字段**）：

| 键 | 说明 |
| --- | --- |
| `id` / `name` | 字段 id（拼 `data` 用的键）与中文名 |
| `subFormId` | **只在明细字段上出现**（主表字段省略该键）；它是 `data.details` 的键 |
| `componentKey` | 控件类型（`RichText` = 富文本、`EmployeeScope` = 人员范围、`EinvoiceComponent` = 发票…） |
| `initialValue` | **只有带默认值的字段才有**：表单初始化时就有的值（OA 预填 / onLoadForm 联动带出）。CLI 会自动并入，**不必显式传**；用户本次明确改写了才按用户说的覆盖 |
| `options` | 选项类字段的可选项（选项值传 `name`） |
| `fileUploadParams` | 附件字段的上传限制：`sizeLimit`（MB）/ `formatLimit`（`mode` + `formats`）/ `maxNum` |
| `isBrowser` / `browserType` / `browserModule` | 浏览按钮类字段（值可写 `名称` 或 `名称(ID)`） |
| `isSelect` / `isMultiple` | 选项类字段 / 是否允许多选 |
| `isEmployeeScope` / `isEinvoice` | 人员范围字段 / 发票字段（赋值方式见「注意」） |
| `readOnly` / `disableEdit` | 只读 / 禁止编辑标记（**正常不会出现在本清单里**，只在降级场景下出现） |
| `folderDependsOnOption` | 附件目录联动（配合最近一次的 `attachmentFolderIds` 用） |
| `format` | 日期 / 时间字段自带的形式标记——**不用你管**，CLI 会按它自动归一化 |

**`fields` 为什么不区分必填**（2026-10-14 口径）：它就是「可编辑 ∪ 必填且可见」的全集，**「哪些字段可以落值」= 本清单，「哪个必填还没值」= `createRequest` 的 `missingFields`**，只有这两句口径。用户看不到、改不了的字段（只读 / 禁止编辑 / 联动隐藏 / 落在布局隐藏行上 / 落在明细表隐藏列上 / 落在多内容单元格的隐藏格上 / 不在当前布局的展示配置里）**不下发**——所以**条数不多是正常的**，不要拿它当"页面上肉眼可见的字段数"，也不要因为"表单上看着没这么多"就怀疑字段清单不对。

**`historyRequestData`（历史参考值）**：范围是**本工作流**、**近一年、非草稿、按发起时间倒序的前 5 条**「我发起的」流程——不是"所有流程混在一起"，所以里面每条都是同一张表单的单据，字段可直接对照；形如 `[{requestName, requestId, createdatetime, fieldValues: {<字段id>: <值>}}]`——`fieldValues` 是**「字段id → 值」的映射**（字段名不随每条记录重复下发：同一个名字要在每条记录里打印一遍，要名字请用 `fields`）；值已按字段类型给出**可直接复用**的写法——浏览按钮 / 选项类为 `名称(id)`（多值以 `、` 分隔）；**附件类为对象**（形如 `{"formField":{"id":"<字段id>"},"dataOptions":[{"optionId":"<附件ID>","content":"<文件名>","type":"<文件类型>"}]}`，可整块放进 `data`，见「历史流程数据参考规则」第三条）；其余为普通字符串。**`null` 表示没有可参考的历史数据**（不返回空数组）；某条历史流程在这批字段上一个值都没命中时会被整条剔除（所以条数可能少于 5）。**你不需要自己再去查历史流程。** 它给的是**本表单要落值的字段**（口径同 `fields`）的取值——填 `data` 时用它把能补的字段补上，判断口径见「历史流程数据参考规则」。
- **`createRequest` 一侧不再返回它**（V12.1.102 起撤出）：`NEEDS_INPUT` / `NEEDS_CONFIRMATION` 时**手上没有任何历史值**，必填缺失直接**一次问齐用户**（`NEEDS_INPUT` 用命令给的 `finalMarkdown`，见「createRequest 返回后的处置」）——**不要**回头翻 `createForm` 阶段那份历史值、也不要凭印象补值。（命令**内部**仍会用这份缓存给缺失字段算 `历史推荐值`，但原始历史始终不回给模型——一致性判断不外包给你。）

**`systemFields`**：`permissions` 给各系统字段的 isview/isedit/ismandatory，`defaults` 是默认值，`levelOptions`/`secLevelOptions` 是紧急程度/密级选项。**只有 `isview=true` 且 `isedit=true` 的系统字段才需要填**；紧急程度/密级**只从这两个 options 取**（不得使用记忆、表单字段或其他来源）；**`defaults` 已有非空值即视为已满足，不要询问用户、直接采用**；仅当 ismandatory=true 且默认值为空时才需要用户提供。

**`launchPreferences`**：该工作流的发起偏好（`available` + `promptText`）。`promptText` **只是「该工作流维度」那一段记忆**——全局画像 / 全局别名（`user.md` / `memory.md`）已由入口的 `workflow.memoryPrompt`（无参）给过，这里不再重复下发，所以**不要再调一次无参 `memoryPrompt` 来"补全"、也不要把两份拼接**（会重复）。`available: true` 时，**只能用它补用户没提到的非必填字段或口径类信息**（如签字意见口径、展示偏好）；**必填字段一律不得用它里面的"常用值"补**——必填缺失只由 `missingFields` 告知、直接一次问齐用户（见「createRequest 返回后的处置」），不要为"能不能用记忆里的值"反复权衡；与用户本次明说的冲突时以用户本次为准。`available: false`（或带 `note`）说明该工作流还没有偏好或读取失败——**按新用户处理，不要重试读取**。

**大表单超线形态**（`createForm` 输出**超过 20,000 字符**时才有）：此时 stdout **只回一句话**——「当前表单内容较大，已临时写入文件 `resultFile路径`，请直接读取 `resultFile路径` 获取完整结果」。**`fields`、`contextId`、`historyRequestData` 一个都不在 stdout 里**，它们全都在那个文件里（**未裁剪的完整 pretty JSON**，与 stdout 同口径）：`fields` / `historyRequestData` / `systemFields` / `contextId` / `continuation` 一样不少。所以：**先按 `resultFile` 把该文件一次读完**（整份读，不要只给个小的 `limit` 再分段；宿主若报单次读取超限，按报错提示调整），拿到字段清单与 `contextId` 之后再拼 `data`、走 `createRequest`。**不要重跑 `createForm`、不要分段读、不要用 `head`/`tail` 截断、也不要用脚本去挖文件。**
- 结果里 `persistedResult: true` 表示走了落盘档；`outputChars` 是**本次输出那份最终文本的字符数**（判线量的就是它——口径 = 已压掉 `fields` / `historyRequestData` / `systemFields` 缩进空白后的整段 stdout，与小e 侧宿主那条 20,000 字符限制同源）。
- **输出被宿主截断时**（只看到一小段预览、出现「已截断…字符」字样）：**不要去读宿主的工具结果目录**（`~/.workbuddy/projects/**/tool-results/**`：没有读权限，去了必白跑一轮），按同一份输出里的 `resultFile` 取完整结果。

`status` 为 `NEEDS_CLARIFICATION` 时只给 `candidates` / `clarificationKeyword` / `clarificationReason`（存在时，见「输入」里的 `workflow_not_exist` / `no_create_right`）/ `candidateCount` / `clarificationQuestion` / `note`，**不含任何表单数据**——它不是失败（`ok:true`），也不代表查询已执行。

### workflow.createRequest

**小e 环境（`BROWSER_FILL`）档不走 JSON 信封**：stdout 整体就是一段 `<browsertool>` 标签块（见「createRequest 返回后的处置」），所以下表这些键**这一档在 stdout 上都看不到**——见到 `<browsertool>` 开头就照处置表处理，不要去找 `status` / `contextId`。

| 键 | 说明 |
| --- | --- |
| `status` | `CREATED` / `CREATED_SUBMITTED` / `CREATED_SUBMIT_FAILED` / `NEEDS_INPUT` / `NEEDS_CONFIRMATION` / `ALREADY_APPLIED` / `BROWSER_FILL` |
| `requestId` / `requestMark` / `requestName` / `url` | 落地后的流程标识与链接（`NEEDS_INPUT` 时没有） |
| `contextId` | 本次用的句柄（原样回显） |
| `fields` | 本次所填字段的落库结果回显（"我填的值到底存成了什么"就看这里） |
| `previewDetails` | 明细表按列组织：`columns` 表头 + `rows` 每行明细 |
| `missingFields` | **恒有值**：submit 成功时是空数组，draft 时是"提交前还需补齐"的提醒 |
| `missingFieldsNotice` | draft 且有缺失时的一段可直接转述的提醒文本 |
| `linkageResult` | 联动带出/清空，原样转述 |
| `verification` | 节点字段校验结果 |
| `attachmentFolderIds` | 附件目录 id（配合 `folderDependsOnOption` 用） |
| `submitResult` / `submitFailReason` | 提交结果（`success`/`failed`）；**只在本命令真正发起过提交（`action:submit`）时出现**，`action:draft` 不带 |
| `finalMarkdown` | 命令渲染好的最终回复文本，见「createRequest 返回后的处置」 |

- **`finalMarkdown`（命令渲染好的最终回复文本，与查询侧同名同口径）**：在**流程已落地的三个状态**（`CREATED` / `CREATED_SUBMITTED` / `CREATED_SUBMIT_FAILED`）与 **`NEEDS_INPUT`（必填缺失）**出现——**有它就原样粘贴、一字不改**（见「createRequest 返回后的处置」），不要再自己挑字段、拼主表/明细表格，也不要自己拼待补清单。`BROWSER_FILL`（小e 环境）用的是**同一份渲染档**，但**不经信封、没有这个键名**：那段文本直接就是命令的 stdout。`NEEDS_INPUT` 那份的末段「**还需要你提供**」就是待补必填项清单，其中**历史取值一致**的字段会带一行 `历史推荐值：…（依据）`——**由命令算好，模型不参与判断**；该分支**不再返回** `resolvedValues`（渲染素材已在命令内部用过）。
- **`BROWSER_FILL`（小e 环境）**：本次**一个写请求都没发**（也没做必填判定）。这一段 `<browsertool>`（`arguments` 里带工作流名称 `title`、新建页地址 `src` 与 `sdkOptions`——PC / 移动两套路由与参数，`params.customParams` 里是这次要填的**字段 id → 值**，另有 `fieldAssignKeys` 列出全部字段 id）**就是命令 stdout 的全部内容**（不套信封，所以 `status` / `contextId` 这一档在输出里看不到）。**处置：把命令输出整段作为本轮回复正文**（不要包在代码块里），宿主会拿这段标签去打开新建页并把字段值带进去；`contextId` 未被消费，需要时由用户再发起一次即可。
- `NEEDS_CONFIRMATION`（`ambiguities` 非空）时同时给 `resolvedValues`（"我传的值 → 服务端最终值"的回显）与 `missingFields`——先把 `ambiguities` 解决掉，再用同一 `context` 重发。
- `needVerificationConfirm: true` 时流程**已创建但未提交**：向用户确认后，用本次返回的 `requestId` 走提交（`workflow operateApply action=submit`）；**不要用同一个 `context` 重发**——该句柄已消费，重发只会拿到 `ALREADY_APPLIED`。
- **`CREATED_SUBMIT_FAILED`（提交结果＝失败）**：流程**已创建为草稿**，但提交被服务端拒绝、**未进入审批**——表单数据已经落库，`requestId` / `requestName` / `url` 与成功时一样都给了（可直接打开查看或编辑），差别只在提交结果。此时 `submitResult: "failed"`、`submitFailReason` 是接口给出的失败原因。**处置：把失败原因原样转述给用户，并给出 `url`**；**不要**读成"什么都没做成"，也**不要**原样重发同一次提交（会再堆一份草稿）。
- `submitResult`：`CREATED_SUBMITTED` 时为 `"success"`（不带 `submitFailReason`）；`CREATED_SUBMIT_FAILED` 时为 `"failed"`；**被节点字段校验拦下或未确认校验（`needVerificationConfirm`）时本就未提交，不返回该字段**。

## 历史流程数据参考规则

本节**只适用于 `createForm` 之后组装首次 `data` 那一步**——`createRequest` 返回 `missingFields`（必填缺失）后**一律不看历史值、直接问用户**（见「createRequest 返回后的处置」）。历史流程数据有两个来源：命令随 `createForm` 给的 `historyRequestData`，以及你自己按它的范围说明核对过的同类历史流程。**历史流程里的字段值只能按下面六条使用**——六条之外一律不推算、不拼接、不凭印象补值：

1. **取值一致、且能推断与本次业务同类 → 可直接采用**：某个字段在**命中的历史流程里取值完全一致**（**一条也算**），并且对照这些历史流程的**其他字段值**，能推断它们和本次要填写的表单属于同一类业务时，直接把这个值填进 `data`，不必再问用户；**取值不一致**时，才需要**三条及以上**取值相同（同样要满足"能推断与本次同类业务"），否则按规则 2 处理或问用户。
2. **看得出规律 → 按规律生成新值**：历史取值呈现可推断的规律（如编号递增、日期递推、金额分档）时，按该规律生成本次的新值；**规律推不出来就不要用**，照常问用户。
3. **附件对象 → 直接复用，不要重新上传**：`historyRequestData` 里附件字段的**值**（`fieldValues` 里以该字段 id 为键的那一项）**就是可直接使用的完整对象**（形如 `{"formField":{"id":"<字段id>"},"dataOptions":[{"optionId":"<附件ID>","content":"<文件名>","type":"<文件类型>"}]}`）——**把它整块放进 `data` 里该字段的位置**（主表字段进 `main`，明细字段进对应行的对象）即可，**不要自己拆解或改造**。两条硬要求：① `optionId` 只能用历史值里给的这个 ID，**不要拿文件名或其它字符串去拼**——拼出来的 ID 指向不存在的文件，命令不会报错、但附件是坏的；② `type` 照抄历史值（图片是 `image`、普通文件是 `file`），**不要改成别的**。这样复用就**不需要重新上传本地文件**（因此也不触发附件上传前的那句提醒）；只有用户本次要换成新附件时，才走上文的上传流程。
4. **发票字段 → 一律不允许复用**：历史流程里填过的发票**不得**用作本次的发票值，任何情形下都要按用户本次提供的发票重新取值（见「注意」的发票字段条目）。
5. **存在固定规则 → 按规则填写当前字段值**：该字段存在固定规则时，按规则填写当前字段值。
6. **不符合上面任何一条 → 不填**：某个字段的历史值既不一致、又推不出规律、又不是可直接复用的附件对象，就**留空不填**——**不要"折中"取一个看起来最像的值、不要拿历史里最常见的那条来凑**。留空是明确动作：它交给 `missingFields` 与其它缺项**一次问齐用户**。

## 注意

- 不传凭据：业务输入禁止出现 Cookie/ETEAMSID/Token/`header.operator`（CLI 托管）。
- **`data` 的键只能取 `fields` 里的字段 id**（那就是可写字段的全集）。**唯一例外：`missingFields` 点名的字段**——`missingFields` 是**按你本次实际填的值、结合显示属性（联动）规则实时算出来的"最新缺失必填项"**，而 `fields` 是 `createForm` 那一刻的**静态快照**：那时联动还没跑，联动命中后才变成必填的字段当时可能既不在 `fields` 里（若原被联动隐藏）、也不在你的视野里。所以补值**一律以 `missingFields` 为准**，不要因为"它不在 `fields` 里"就把用户给的这条值丢掉。`readOnly` / `disableEdit` / 不可见字段**一个都不要传**——传了整单会被拒（`notEditable`），得把只读字段全部摘掉重跑一轮。**看到 `notEditable` 不要重试、不要换字段 id 绕过**，移除这些字段后重跑。
- 大表单超线时（stdout 只有一句话、没有 `fields`），**先按 `resultFile` 把那个文件一次读完**再拼 `data`（见「返回」的大表单超线形态）；未超线时 `fields` 就在 stdout 里，不必读文件。
- 附件/文件：附件字段需上传本地文件时，口径见「填值纪律」的「附件 / 发票字段」——先提醒用户"上传的附件会先经过公网大模型，请谨慎操作"，用户确认后用 **`weaver-e10-caizhilian` 技能**（`caizhilian.file-upload.*`）上传取 `file_id`。**不要另走独立的文件上传技能**（那套双登录模式不属于本 CLI 上传接口）。
- 附件上传限制：上传前核对该字段的上传限制，不满足先告知用户、不执行上传。看该字段的 `fileUploadParams` 三项——`sizeLimit`（MB）、`formatLimit`（`mode` + `formats`；`formats` 为 `*.*` / `*` 表示不限制后缀）、`maxNum`（数量上限），在 `fields` 里该字段那一条上。
- 发票字段（componentKey `EinvoiceComponent`）：口径见「填值纪律」的「附件 / 发票字段」，支持两种赋值方式：① 从票夹选取：使用 `weaver-e10-yepiaotong` 技能查询票夹里已有的发票对象（拿 `fid` 后 `invoice.browse-field.data` 取对象）；② 使用 `weaver-e10-yepiaotong` 技能上传本地发票文件（`invoice.upload`）并取上传后的发票对象。方式 ② 在真正上传前必须先提醒用户"上传的发票文件会先经过公网大模型，请谨慎操作"，用户明确确认后才执行；方式 ① 无需这句提醒。用户未明确发票字段如何赋值时，先反问用户，不需要提前检测 `weaver-e10-yepiaotong` 技能是否可用，真正需要使用上述两种方式给发票赋值时，workbuddy环境下可直接到技能市场搜索【泛微E10业票通发票管理】并自动安装，搜索不到时反馈给用户，其余环境遇到技能缺失时直接反馈给用户。
- 发票类字段的历史值不可照抄。
- 发票值拿不到时直接问用户。
- **日期 / 时间字段按用户说的填即可，不要管格式**：CLI 会按字段自带格式自动归一化（`2026-8-21` / `2026年8月21日 9:5` 都会规整成字段要求的写法；日期+时间控件只给到日期时补 `00:00`）。**不要为格式反复权衡，也不要手工补时间**。
- **富文本字段（componentKey `RichText`）**：支持 HTML 内容、不受 maxLength 限制。**内容来自本地文档（docx/pptx/md 等）或结构化材料时，必须先把源内容转成 HTML（保留 h1-h3 层级、table 表格、ul/ol 列表结构）再填入，禁止直接填纯文本**；用户明确只要纯文本时除外。文本 / 富文本字段直接传字符串即可（CLI 按字段元数据落库），不需要也不允许把它包装成 `{id,name}` 之类的浏览按钮结构。
- **字段键**：`main` 的键、`details[subFormId]` 行对象的键**都必须是字段 id**（`fields[].id`）。`"字段名(字段ID)"` 这种写法**表单 data 不支持**（那是查询条件 `filterFields` 的写法），混用会报「存在重名或无法识别的表单字段，请改用字段 id」并白跑一轮。
- 字段**值**格式：选项传 `name`；人员范围（EmployeeScope）传对象数组 `{"name":名称,"type":类型}`，类型取 user/dept/subcompany/group/role/position/external/all/allExternal。
- **浏览按钮 / 人员 / 部门类字段**（值传字符串，CLI 自动转 ID）：可写 `名称`，也可写 `名称(ID)`（括号内是纯数字时按 ID 用、不再查名）；纯名称**首轮就该一次给多个说法**（与上面 `workflow` 同口径：**同一字符串内用英文逗号分隔**，如 `"全称写法,简称写法"`；说不出完整名称时的展开口径见下文「必填的浏览 / 人员 / 发票类字段」那条），CLI 会把这些说法拆开、连同整串一起拿候选：**只有命中唯一、或某个候选与整串／某个说法完全同名时才会自动采用**，否则会把所有候选列出来让你向用户确认（不会拿一个“最接近”的结果蒙过去）。**该字段允许多选时，多值用数组**（每个元素各自可以带多个说法）。**不支持裸 ID**——只写数字会被当名称去查，查不到就是 `NOT_FOUND`。
- **澄清时一律不向用户索取 ID**：任何"名称没对上 / 候选要确认"的场合，只问该对象的**完整名称**，或**其它可用于检索的关键词**；确认候选后的回传值（`{"id":…,"name":…}`）由你按候选自行拼好，**不要让用户提供 ID**。
- **人员范围（EmployeeScope）解析失败**：`createRequest` 返回 `NEEDS_CONFIRMATION`，`ambiguities` 里 `kind = "EMPLOYEE_SCOPE"`：
  - `reason = "NOT_FOUND"` → 系统里没有该名称，**一次明确告知用户**“没找到「XX（类型）」，请给出该对象的完整名称，或其它可用于检索的关键词”，最多重试 1 次；
  - `reason = "MULTIPLE_MATCHES"` → 列出候选（`candidates`）让用户选，选定后按 `{"optionId","content","type"}` 回传；
  - `reason = "NOT_RESOLVED"` → 名称/类型齐了但没拿到 ID，通常上一次解析没成功，按上面两种口径让用户确认；
  - **禁止**因为"命令返回 ok"就当作字段已填好——出现 `ambiguities` 时必须先解决，否则该字段不会进入保存体。
- **静态字段权限未下发（`requiredInfoWarning`）**：`createForm` 返回的 `requiredInfoWarning` 非空时，说明 OA 没下发该表单的**静态**字段权限配置（`fields` 里的只读 / 禁止编辑判定可能偏保守）——**不代表该表单没有业务必填项**（本租户的业务必填多为**条件必填**：OA 的联动规则只在字段组合命中时才要求必填）。处置一句话：**照常调 `createRequest`，按 `missingFields` 补齐**。
  - **不要自己推演"必填是否齐"**：`createForm` **不下发** OA 的联动（显示属性）规则——规则的触发条件往往取决于你还没填的字段，**发起前无从判断**（本文档不列任何具体条件；**也不要把你从文档或记忆里看到的任何条件样例当作本次的命中原因**）。缺失与否由 `createRequest` 按**实际所填数据**实时算出，看它返回的 `missingFields` 即可，**禁止**为了"提前问齐必填"去猜条件、也**禁止**逐个字段推演。
  - **`missingFields` 可信**：条件命中与否由 `createRequest` 按**实际所填数据**（含联动带出值）实时计算，`missingFields` 就是当前真实缺失的必填项——照常调用，按它的返回补齐。**禁止**对用户说"系统不会校验必填项"，也**禁止**用 `requiredInfoWarning` 非空当作"无法校验必填"的理由跳过校验。
  - 只有需要向用户交代"OA 页面上带红色星号的字段"时，才提示用户对照表单红星核对（含明细表里的列，如费用明细的「发票」）。
- **必填缺失一次问齐**：`createRequest` 返回 `NEEDS_INPUT`（`missingFields`）时，**原样粘贴它给的 `finalMarkdown`**——末段「**还需要你提供**」就是全部待补项（每项已标出在主表还是明细第几行）；**禁止逐字段推演或逐个追问**（也不要去翻历史值或记忆里的常用值——清单里带 `历史推荐值：` 的那几项就是**命令**从历史里算出来的，照它转述/采用即可），**也不要把它塞进弹窗**（弹窗需要给候选选项，而这里**不许对值做任何推断**）。**`action: draft` 时缺失不阻断、状态是 `CREATED`，但 `missingFields` 同样会返回——必须原样转述（提交前需补齐），不要把 `CREATED` 读成"没有缺失"**（此时命令还会附一段 `missingFieldsNotice`，可直接用它）。
- **必填的浏览 / 人员 / 发票类字段：值来自用户的话 ＋ 服务端解析（这里不存在"猜"）**：从用户本轮说过的话里**取线索**——**含指路性的模糊线索**（楼层 / 楼栋 / 区域 / 简称等只有部分信息的说法）——**第一次调用就传进 `data`**。**线索不是完整名称时，首轮就把它的多种写法一次并列传完**（同 `workflow` 名的「一次给多个说法」口径，同一字符串内用英文逗号分隔）：写法展开＝**保留用户原话作锚点**，再补**全称 / 简称、去掉或补上单位词、数字写法变体**（如 `"全称写法,简称写法,去掉单位词的写法"`）——**只做同一个对象的写法变体，不要换另一个对象去试**。服务端只会有三种结果，按结果处置：**唯一命中**（直接可用，并按「主表（已填内容）展示规则」说明它命中成了什么）／**`MULTIPLE_MATCHES`**（列出 `candidates` 让用户点选，选定后按 `{"id":"候选id","name":"候选名称"}` 回传）／**`NOT_FOUND`**（明确告知"系统里没有「XX」，请提供该对象的完整名称，或其它可用于检索的关键词"，最多重试 1 次）。**只有用户本轮完全没提到该字段时才留空**——留空是为了让 `missingFields` 把它列出来、连同其它缺失项**一次问齐**，这是**省往返手段，不是"不许传"**。真正**禁止**的只有两条：① **编造用户没说过的值**，或**凭空构造 `{id,name}` 绕过澄清**（就算被服务端接受，你也不知道它解析成了哪个对象）——**对用户原话做写法展开不算编造**（展开里始终留着用户原话作锚点）；② 把多个说法拆成**一轮一轮重发**（同一条命令里并列多个说法属"补充召回"，不额外花往返）。发票类走外部技能（`weaver-e10-yepiaotong`）。
- **特例 · 会议室字段（`browserType = mt_room`）**：房间名里**没有楼层 / 区域这类描述**，所以用户口里的楼层线索**本身不是房间名的子串**——只传带描述后缀的说法会 0 命中（`NOT_FOUND`、`candidates` 为空）。该字段首轮必须把线索的**最小可检索片段**（去掉描述性后缀后剩下的那部分）与**用户原话**一起**并列**传；命中多个候选时照常把 `candidates` 原样列给用户选。
  - 这个字段**不做值推演**：最小可检索片段按上一条口径取定即可，**一次并列传完就下发命令**，不要在下发前反复比较"哪种写法更可能命中"；**拿到候选就停**——照常把 `candidates` 原样列给用户选，不为"再试一次能否唯一命中"改写或收窄写法重发。
  - 其它浏览按钮字段出现同类问题时，在本条下按同一格式**追加同级「特例 · <字段>（<browserType>）」小条**：只写该字段特有的匹配口径，**不写示例**。
- **`finalMarkdown` / `resolvedValues` 既用来自查解析结果、也是「已填内容预览」的数据源**：`NEEDS_INPUT` 与成功三态**直接看命令给的 `finalMarkdown`**——其中的「已填内容」就是"我传的值 → 服务端最终值"的回显（选项/浏览/人员/部门都给名称），不必再去拼一遍；只有 `NEEDS_CONFIRMATION` 才看 `resolvedValues`（该分支要继续解决 `ambiguities`）。**解析结果与预期不符就不要往下走**（例如传「泛微」被解析成了另一个主体），按上面的口径向用户确认，后续用完整名称。
- **浏览按钮值匹配不上（BROWSER NOT FOUND）**：`createRequest` 返回 `NEEDS_CONFIRMATION`（`ambiguities` 里 `kind = "BROWSER"`）时按 `reason` 分别处理。`candidates` 里**只会出现按你写的说法真实命中的值**，不会混进与该说法无关的系统默认清单：
  - `reason = "MULTIPLE_MATCHES"` → 列出 `candidates` 让用户选，选定后按 `{"id":"候选id","name":"候选名称"}` 回传；
  - `reason = "NOT_FOUND"`（`candidatesAvailable = false`、`candidates` 为空）→ **一次明确告知用户"系统里没有「XX」，请提供该对象的完整名称，或其它可用于检索的关键词"**，用户给出后最多重试 1 次；
  - 一个值有多种叫法时，**首轮就把这些写法一次用英文逗号串起来传**（展开口径见上文「必填的浏览 / 人员 / 发票类字段」那条）——同一条命令里并列多个说法属"补充召回"，不额外花往返。**禁止的是拿一个说法试一次、失败后再换一个说法重发**（那是多轮逐词去撞），也**禁止凭空构造 `{id,name}` 绕过澄清**。
- 明细表：`details` 的 key 是 subFormId，value 是行对象数组。
- **明细表（子表单）展示规则（Excel 列展示）——只在命令没给 `finalMarkdown` 时自己拼**（`NEEDS_CONFIRMATION` 这类命令没给渲染档的状态，或老版本命令）：以 `previewDetails`（明细表按列组织：`columns` 表头 + `rows` 每行明细）为准——明细表**必须用 Excel 列展示**（表头 + 每行一条明细，形如 `| 序号 | 费用日期 | 费用类型 | 费用说明 | 申请金额 |`，每行一行），**禁止把明细字段按"字段\|内容"平铺**；`previewDetails` 为空时才用 `fields` 平铺兜底。多条明细时逐行展示（序号递增）。
- **主表（已填内容）展示规则（字段 / 值两列，单独成表）——只在命令没给 `finalMarkdown` 时自己拼**（`NEEDS_CONFIRMATION` 这类命令没给渲染档的状态，或老版本命令）：面向用户回显"这次填了什么"时，用**「字段 / 值」两列表格**展示，**只列用户在表单上看到的、有值的字段**：本次实际填写的字段——成功时取 `fields`、`NEEDS_CONFIRMATION` 时取 `resolvedValues`，再带上 **`createForm` 的 `fields` 里带 `initialValue` 的字段（表单默认值）**；`requestName`（流程标题）已确定时在表内一并列出（放第一行）；只读 / 禁用、联动隐藏、没值的字段不列。**主表表格与明细表表格必须分开列**（先主表、后明细表），**禁止**把两表合成一张、也**禁止**用 bullet 列表代替表格；`missingFields` / `ambiguities` 里等用户确定的字段列为"未确定"，并照常向用户询问。
- 目录联动：附件字段 `folderDependsOnOption=true` 时，按最近一次返回的 `attachmentFolderIds` 取 `folderId`（null=不指定目录）再上传。
- 初始化值：`createForm` 的 `fields[].initialValue`（OA 预填值，含 onLoadForm 联动带出）——**不要逐个传**（默认值由 CLI 自动并入主表与明细行，漏带不会缺必填）；只有用户本次明确改写了某个初始值时才显式传。`missingFields` 里出现它就是真的没值，按上面口径问用户。
- 不重试：saveFormData/flow/create 失败、超时或结果不确定（`SAVE_UNCERTAIN`/`PARTIAL_SAVED`/`CONTEXT_ALREADY_WRITTEN`/`WRITE_UNCERTAIN`）禁止重试，返回恢复信息并让用户人工检查。
- 写操作遇登录失效：禁止自动重登重放，返回 `WRITE_UNCERTAIN` 停止，先只读回查。
- `context` 与工作流强绑定：只用最终选定工作流那次 `createForm` 返回的 `continuation`；澄清后换了工作流就要重新 `createForm` 拿新句柄。
- **记忆保存（发起流程口径）**：本轮发起过程中，**只有用户有新的明确澄清**——① 工作流名称；② 字段名称；③ 浏览按钮字段值；④ 选项字段的选项值——才做记忆保存。**这四类之外一律不保存**：用户只是给出普通文本 / 日期 / 金额等字段的本次取值，或只是正常走完一次填单，都不构成记忆。满足条件时按 memory 规则在任务结束时**实际调用** `workflow.memoryExtract` 保存（见 workflow-memory.md）。

## 示例

### ① 解析工作流并载入表单（拿到 fields / historyRequestData / continuation）

Windows PowerShell：

```powershell
weaver-work-cli --json workflow run workflow.createForm --input-json '{"workflow":["<工作流名称>"]}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json workflow run workflow.createForm --input-json '{"workflow":["<工作流名称>"]}'
```

### ② 填好字段后一次完成发起（action 必填）

Windows PowerShell：

```powershell
weaver-work-cli --json workflow run workflow.createRequest --input-json '{"context":"<createForm返回的continuation>","data":{"main":{"<字段id>":"<字段值>"}},"action":"submit"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json workflow run workflow.createRequest --input-json '{"context":"<createForm返回的continuation>","data":{"main":{"<字段id>":"<字段值>"}},"action":"submit"}'
```
