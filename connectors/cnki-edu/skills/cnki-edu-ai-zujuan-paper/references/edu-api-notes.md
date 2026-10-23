# edu MCP 接口实测笔记（2026-10-08）

> 记录 `edu` 题库 MCP 各 `tk*` 工具的真实行为、参数与坑。
> 状态：✅ 已验证 / ❌ 不可用 / ⛔ 不适用。
> ⚠️ **元数据不外显**：本文档记录**字段语义**（供解析用）；文中一切**示例值均已脱敏**。接口的元数据字段**值**（`SID` / `Label` / `SourceReports` / `Degree` 原值 / `Subject` / `Cate` 等）**不得流入对话输出或任何对外产物**。

## 接口总览与定位

| 接口 | 作用 | 组卷环节 | 状态 |
|---|---|---|---|
| `mcp__<SERVER>__tkSubject` | 学段/学科编码 | S2 | ✅ |
| `mcp__<SERVER>__tkPoint(subjectCode)` | 知识点树（按题材/模块组织，**无年级字段、无单篇课文节点**） | S3 归一化 | ✅ |
| `mcp__<SERVER>__tkBook(subjectCode)` | 教材版本→册(年级学期)→章节树；`data` 为按版本分组的字典 | S2（指定教材版本时） | ✅ |
| `mcp__<SERVER>__tkQuestionType(subjectCode)` | 题型码表 | S2 题型归一化 | ✅ |
| `mcp__<SERVER>__tkQuestionFrom(subjectCode)` | 来源码表 | S2 来源归一化 | ✅ |
| `mcp__<SERVER>__tkSearchSubjectQuestion` | **组卷主力**（指定学科按知识点搜题，支持 ct/dg/so/yr） | S4 | ✅ |
| `mcp__<SERVER>__tkSearchQuestion` | 关键词搜题（**无 so 参数**） | S4 兜底 | ✅ |
| `mcp__<SERVER>__tkQuestionAnalysis` | 单题解析 | S6 | ✅ |
| `mcp__<SERVER>__tkQuestionSame` | 相似题（题找题） | S4 题找题 | ✅ |
| `mcp__<SERVER>__searchVectorBJ` / `mcp__<SERVER>__searchVectorBJPara` | **文献库**向量检索（期刊/学位/会议/报纸） | — | ⛔ 不适用 |

---

## mcp__<SERVER>__tkSearchSubjectQuestion（组卷主力）

**入参**
| 参数 | 必填 | 说明 |
|---|---|---|
| `subjectCode` | 是 | 学科码 |
| `point` | 是 | 考点**中文名数组**（非数字 Key）；粒度到「题材/能力」层 |
| `ct` | 否 | 题型码；**不传默认 = 选择题(1)** |
| `dg` | 否 | 难度码（**离散档**，非连续区间）；0=不限 |
| `so` | 否 | 来源码 |
| `yr` | 否 | 年份字符串（如 `"2023"` 或 `"2023,2024"`）；`"0"`=不限 |
| `pi` / `ps` | 否 | 页码 / 每页条数（**ps 最大 10**） |

**返回**：`data[]`，每题含 `SID` / `Subject` / `Cate`(题型码) / `CateName` / `Label`(来源) / `Content` / `Options[]` / `Points[]` / `Answers[]` / `DisplayAnswer` / `Degree`(0–1 连续难度) / `SourceReports[]` / `PaperCount` / `RealCount`。

**要点**
- `point` 必须中文名；改不了粒度的单篇课文需走关键词接口。
- **`point` 支持多值数组**：可把同 `(ct,dg,so)` 的多个考点**合并进一次调用**（组卷「聚合批量搜题」的主力，返回后按每题 `Points` 归位）；**并发上限 3**。→ 25 次搜题可降到 ~4–6 次。
- `Degree` 是连续值，用于精确难度过滤（`dg` 只是粗桶）。
- **不同题型要配不同 `ct`**：2 分题用 `ct=1`、4 分题用 `ct=2`、6/8/12 分用 `ct=9`；否则默认全是选择题。
- 作图类题用 `ct=1`（选择）会空 → 改 `ct=9`（解答）。
- `dg=15`（最难档）在部分组合下**返回空**属正常（库里此类题少）→ 放宽到 `dg=0` 再按 `Degree` 过滤。

## mcp__<SERVER>__tkSearchQuestion（关键词兜底）

**入参**：`keyword`（必填）；`subjectCode`（不传 = 全学科）；`type`（题型码）；`pi` / `ps`。
**要点**：**无 `so`（来源）筛选参数** → 按来源筛选必须走 `mcp__<SERVER>__tkSearchSubjectQuestion`。用于锁定单篇课文/无标准知识点时。

## mcp__<SERVER>__tkQuestionAnalysis（解析）

**入参**：`SID`（必填）、`subjectCode`（必填）。
**返回**：`Analyse`（分析）/ `Method`（解答）/ `Discuss`（点评）/ `DisplayAnswer` / `Answers[]` / `Points[]` / `Topics[]`。
**要点**：**选择题也应调**（样例卷的选择题都带完整解析）；`Points` 用于生成 `【考点】`。

## mcp__<SERVER>__tkQuestionSame（相似题）—— ✅ 可用

**入参**：`{ SID(string,必填), subjectCode(int,必填), num(int,必填, ≤5) }`。

**返回结构（与 `mcp__<SERVER>__tkSearchQuestion` 一致）**：
```json
{"data":[{"SID":"<内部ID>","Subject":<学科码>,"Cate":<题型码>,"CateName":"解答题","Label":"<题源标注>",
          "Content":"…","Options":[],"Degree":<0–1 连续难度>,"…":""}],"code":200,"msg":"查询成功！"}
```
- `data` 数组即**按系统相似度排序**的结果，直接取前 `num` 条；返回条数 = `num`（题库量足时）。
- 只返回题面（`Content`），**不含解析** → 仍需对每条再调 `mcp__<SERVER>__tkQuestionAnalysis`。

**可用性说明**：该接口**偶发返回** `"系统繁忙，请稍后再试。"`（纯字符串、无 `code`），属**服务端偶发故障**而非限流或鉴权问题；伪造 SID 会明确报 `"试题Id错误！（字符串解密失败）"`，说明接口链路本身完好。调用时按下方主备切换处理即可。

**主备切换（规范见 `similar-question.md` §S3g）**：
1. 首选 `mcp__<SERVER>__tkQuestionSame`；返回"系统繁忙"→ **退避重试 1 次**；
2. 仍失败 → **不走默认 fail-fast，先执行本链路文档化的等价降级**（`mcp__<SERVER>__tkSearchQuestion` 关键词召回）；切换**须显式标注已降级**，不得静默改道；
3. **降级路径自身也连续 2 次失败** → **此时才按 `fault-tolerance.md §6` 中止并返回错误**；
4. 计数分开：两接口失败计数各自独立，切到降级后从 0 重新计数；单次组卷最多探测 2 次，不因该接口故障反复无效调用。

## mcp__<SERVER>__searchVectorBJ / mcp__<SERVER>__searchVectorBJPara —— ⛔ 本产品不适用

**实测**：属**文献库（北京文献库）向量检索**，返回 CJFD 期刊/学位/会议/报纸的题录 + 正文/段落。输入「一元二次方程的解法」返回《一种微分方程的通解的简单形式》等**学术文献**。
**结论**：与题库试题、与 `mcp__<SERVER>__tkPoint` 知识点**均无关** → **不用于**相似题、**不用于**知识点语义归一化。

---

## 通用坑与工程约束

1. **限流**：并行调用会触发 `"对不起，您的请求频率过快！"`。**实测口径（2026-10-10）**：并发 **4 → 该卷 0 次 429**；并发 **6 → 38 次调用命中 5 次 429**。→ **默认并发 4**；**仅题量 >20** 才试探 6；命中 429 则 `sleep 3` 重试 1 次并**回落 3**。
2. **合规红线**：试题不可本地缓存、不可后台程序调用、有调用次数限制 → 组卷须**实时拉题、会话内完成、不落库**。「我的组卷历史」一期不做。
3. **题图**：题库图片域名（见 `render_paper.IMG`，可用 `ZJ_IMG_HOST` 覆盖）的图，服务端无防盗链（带/不带 Referer 都 200）。嵌入时用 **`https://`**（避免混合内容拦截）+ **`referrerpolicy="no-referrer"`** + **`loading="lazy"`**（错峰、降并发限流）。不落地缓存。
4. **填空题"空"**：用 `<!--BA--><div class="quizPutTag">…</div><!--EA-->` 标记，展示时替换为 `____`；答案在 `Answers[]` 有序数组（第 N 空 ↔ `Answers[N-1]`）。
5. **HTML 片段**：`Content`/`Options` 含 HTML（`<sup>` 上标、嵌套 table 表示分式、`MathJye` 包裹）。渲染时保留必要标签，剥离脚本/样式噪音。

## HTML → docx 转换（配套工具）

- 走 `tencent-docx` 插件的 `html-to-docx` 转换器（封装在 `scripts/to_docx.sh`）。
- 转换时**自动下载并内嵌**远程题图（docx 内 `word/media/imageN.*`）→ 产物自包含、可离线分发。
- **转换器的排版行为（实测，2026-10-08 审计）**——每条都对应一个"必须这么写"的约束：
  1. **不读 CSS `@page` 边距** → 页边距用 CLI 显式传参。
  2. **元素级 `line-height:1.5` → `w:line=360`（真 1.5 倍）**；**`body` 级 `line-height:1.5` → 注入 Normal 样式并 ×0.85 → `line=306`（1.275 倍）**。→ 行距必须钉在元素上。
  3. **`margin-left` 单属性 → `w:ind w:left`**；**`margin` 四值简写里的左边距会丢**；**`padding-left` 与负 `text-indent` 一律忽略**。→ 悬挂缩进需 `fix_hanging_indent.py` 后处理补 `w:hanging`。
  4. **表格单元格行距**转成段前/段后间距（`(line-height−1)/2 × font-size`），`w:line` 保持 240。
  5. **不继承 `body` 的 `font-size`** 到所有场景（卷名/正文需在元素上显式写），但 body 的 `font-size` 会被注入 Normal 样式（`w:sz=21`）。
  6. 选项表总宽被归一化为 **432pt**；`A` 与 `．` 之间会被插入空格（约 11pt）。
  7. 把"文字`____`"误判为**表单域**并丢弃其后整段 → 填空一律用 `<u>　　　　</u>`。
  8. `white-space:nowrap` 不翻译为 `w:noWrap` → 不折行只能靠列宽反算。
- 必须显式传页边距；字号须钉在元素上（详见 `layout-standard.md` §6-10、§6-11）。
- ⚠️ **填空线不能用连续下划线 `____`**：转换器会把"文字____"误判为「表单域」，并**丢弃该空之后整段文字**（实测：Q6 只剩前半句、Q8 丢大段）。改用 `<u>　　　　</u>`（下划线标签 + 全角空格）→ 生成真实下划线且不丢字。`render_paper.py` 的 `fix_blanks()` 已自动完成此转换（把 `_{3,}` 替换为该标记）。
- 内嵌图片属**用户交付物**，与「组卷过程不缓存试题内容」不冲突。
