# 组卷效率规范（提速执行口径）

> 目标：把「一份 100 分 / 25 题标准卷」的端到端时间，从 **≈4–6 分钟** 压到 **1 分钟级**；小卷（≤10 题）目标 **30–60 秒**。
> 本文件是 SKILL.md「**提速口径**」的**细则与唯一权威正文**（口径表在 SKILL.md，命令与模板在本文件 §2/§3）。**与 SKILL 主流程冲突时，以本文件的提速口径为准**（不改变产物形态与排版约束）。

---

## 1. 为什么慢：机制与瓶颈（2026-10-10 实测结论）

> **反直觉结论**：25 题组卷，**全部 API 纯耗时仅 ≈20 s**，而墙钟花了 **1195 s** —— **≈1175 s 都花在「模型轮次间隙」上**。
> 因此真正要省的是「**轮数**」，不是「调用数」。**减少 API 调用 ≠ 提速。**

**WorkBuddy 执行机制（决定「怎么快」）**
| 机制 | 含义 | 提速杠杆 |
|---|---|---|
| 按轮（turn）执行 | 每条助手消息 = 一次模型往返，**回合之间有推理 + 调度间隙** | **减少轮数**（最强） |
| 同轮并行工具调用 | 同一条消息里的多个工具调用**并发执行** | **同轮并发** |
| 上下文成本 | 注入的大 payload 会**拖慢其后每一轮**并逼近压缩线 | **大数据落盘、不进主上下文** |
| 子代理 | 独立并行循环，但**有启动开销、不可共享缓存** | 仅在需要隔离大 payload 时用（≤2 个） |

**实测延迟基线（同一会话内取样）**
| 操作 | 单次延迟 |
|---|---|
| `mcp__<SERVER>__tkSearchSubjectQuestion` | 0.29–1.35 s（中位 ≈0.5 s） |
| `mcp__<SERVER>__tkQuestionAnalysis` | 0.20–0.45 s（中位 ≈0.25 s） |
| `mcp__<SERVER>__tkPoint(33)`（1.45 MB / 407 节点 / 283 叶） | ≈1.2 s |

**时间去向拆解（子代理 transcript：轮内 API 等待 vs 轮次间隙）**
| 轮次 | 总墙钟 | API 等待 | 轮次间隙 |
|---|---|---|---|
| A（9 单选） | 444 s | 73.6 s | 371 s |
| B（10 多选） | 738 s | 74.7 s | 663 s（最大单间隙 312 s） |
| C（5 解答） | 548 s | 45.1 s | 503 s |
| **v2 整包（25 题）** | **1195 s** | **仅 19.3 s** | **1175 s** |

**Skill 侧瓶颈（按「影响轮数」重排）**
| 级别 | 瓶颈 | 事实 | 对策 |
|---|---|---|---|
| P0 | **轮次过多**（≈26 轮/卷） | S7 五步各占 1 轮、S3.5 三步各 1 轮 | `finish.sh` / `tkpoint_cache.py prep`（各压成 1 轮） |
| P0 | **阶段串行**：全搜完 → 再全取解析 | 搜题轮与解析轮不重叠 | **同轮混合流水线**（pipeline stuffing） |
| P0 | **并发被限流锁死** | 实测：并发 4 → 该卷 **0 次 429**；并发 6 → **5 次 429**。故每轮只能塞 **4–5 次** → 50 次调用硬底 **≈10 轮** | 默认**并发 4**（仅题量 >20 才探 6）、429 退避回落 3 |
| P1 | **上下文膨胀** | 25×(20–30 KB) HTML ≈0.97 MB → 触顶**自动压缩** | 大 payload 落盘、块内 ≤8 题、只留摘要 |
| P1 | 子代理启动开销 | 各自读 SKILL / 重读依赖 / 独立轮次 | 载体选最轻（主线程直发优先，子代理 ≤2） |
| P2 | 渲染 / 转档子进程 | 已用 `render_all` / `render_blocks` 并行（=1 轮） | 保持 |

---


## 2. 铁律（强制）

### 2.1 轮次铁律（第一杠杆）

> 依据：§1 实测——API 仅 20 s、轮次间隙 1175 s。**省轮 = 省墙钟。**

1. **能一次脚本做完的，绝不拆成多次调用** —— 每个 `Bash` 调用 = 1 轮。S7 五步用 `finish.sh`（1 轮），S3.5 用 `prep`（1 轮），**不要**分次调用。
2. **同轮混合流水线（pipeline stuffing）** —— 每轮同时发「**新题位的 search + 已选题的 analysis**」，把「搜题轮 + 解析轮」压成 `max(搜题轮, 解析轮)`；不要「先全搜完、再全解析」。
3. **单轮并发：默认 4，仅题量大时才探 6** —— 实测：并发 4 → 该卷 **0 次 429**；并发 6 → 38 次调用命中 **5 次 429**。故默认 **4**；**仅当题量 >20** 且连续无 429 时才探 **6**；命中 429 → `sleep 3` 重试 1 次并**回落 3**；**429 连续 2 次（重试仍败）→ 判定服务级故障 → 立即中止并返回错误**（见 `fault-tolerance.md §6`），**不得**改路径硬跑。
4. **载体选最轻的** —— 优先**主线程直发并同轮并发**；子代理有启动开销，仅用于隔离大 payload，且**≤2 个**。
5. **上下文卫生 / 候选瘦身** —— 搜索返回的大 HTML **落盘**（`raw_s<N>.json`），上下文**只出现紧凑候选表**（`shrink_candidates.py table` 产出的「短ID / 题型 / 五档难度 / 选项数 / 题干前 48 字」）；`mcp__<SERVER>__tkPoint` 全量树一律落盘。「取数与决策分离」见 §2.3。

**轮次预算与 Turn Plan（25 题 · v2.3 修正 = ≈11–14 轮）**

> ⚠️ 早期「7–12 轮」的估算**不成立**：它隐含"每轮 10 次调用"（搜 5 + 析 5），远超限流上限。实测每轮只能塞 **4–5 次** → 50 次调用的硬底 = **≈10 轮**。

| 轮 | 动作 | 构成 |
|---|---|---|
| T1 | 装载 + 归一化 | 批量 `ToolSearch` ‖ `tkpoint_cache.py prep`（同轮并发） |
| T2–T6 | 搜题主攻 | 每轮 **4–5** 个 `mcp__<SERVER>__tkSearchSubjectQuestion`，返回**落盘** |
| T7 | **集中决策** | 跑 `table` → 读紧凑候选表 → 输出全部「题位→短ID」 |
| T8–T12 | 解析主攻 + 补缺 | 每轮 **4–5** 个 `mcp__<SERVER>__tkQuestionAnalysis`，落盘 + `pool` 归并 |
| T13 | 收尾 | `shrink_candidates.py assemble … && finish.sh …`（串联 = **1 轮**） |
| **合计** | | **≈11–14 轮**（v2.1 ≈26 轮） |

- **🛑 停止条件（强制）**：搜题 + 解析**合计 ≤ T13**；补缺**有界重试 ≤2 次**（见 `fault-tolerance.md` §2C）；到顶仍缺 → **转降级交付**；**服务级接口错误（`429`/超时/`5xx`/「系统繁忙」）连续 2 次 → 立即中止并返回错误**（fail-fast，见 `fault-tolerance.md §6`）。**禁止**无休止「生成 → 检查 → 再生成」。
- **滚动式进度**：每 3 题报一次 `已完成 x/N`，便于判断是否卡死或需收口。

### 2.2 效率铁律（执行口径）

1. **同轮并发**：相互独立的 search / analysis 调用**必须在同一条消息里并发发出**，**自适应并发默认 4（可探到 6）**；命中 429 退避回落 3。禁止「一个调用 = 一个轮次」。
2. **搜题合并要谨慎**：⚠️ 实测 `mcp__<SERVER>__tkSearchSubjectQuestion` 传**多个 `point[]`** 时返回**混合列表且 `Points` 为空**，**无法归属回各知识点**。→ **默认每个知识点各发一次**（靠同轮并发提速）；**仅**在"同 (ct,dg,so)、接受混合候选、事后逐题按考点复核"时才可谨慎合并。
3. **搜索↔解析流水线**：题位选定 SID 即刻发起解析，与后续搜题**同轮**并行。
4. **阈值前置**：`dg` 放宽、`so` 兜底做成首轮参数，避免「失败后再重试」。
5. **重活不进主上下文**：`mcp__<SERVER>__tkPoint` 落盘缓存，主会话只读叶名清单；搜索大 HTML 也只留摘要。
6. **一键复用脚本**：`finish.sh`（收尾一条龙）/ `build_questions.py` / `render_all.sh` / `selfcheck_paper.py`（+ 容错脚本，见 §7）。
7. **自适应节流，而非取消节流**：⚠️ 删掉 `1.5s` 间隔改纯并发**更易 429、是回归**。默认保留 ~1.5 s 轻量间隔 + 并发 4；命中 429 → `sleep 3` 重试 1 次并回落 3；仅在长时间无 429 时保守试探更高并发（上限 6）。**429 连续 2 次（重试仍败）→ 立即中止并返回错误**（fail-fast，见 `fault-tolerance.md §6`）。
8. **分块 + 原子落盘**：单代理**不得**整包 25 题且"跑完才写"（会触发上下文压缩丢数据）→ 分块（≤8–9 题/块）+ 逐题原子落盘（见 `fault-tolerance.md`）。

### 2.3 取数与决策分离（压上下文 + 一次决策）

> **为什么**：搜题/解析的原始返回含完整题干/选项/公式/解析 HTML。原样留在对话里会 ① 每轮变慢 ② 逼近压缩线（**早期版本根因**）③ 模型要**复述一遍**才能落盘（纯浪费 token）。

**四步（强制）**

| 步 | 谁做 | 动作 | 产物 |
|---|---|---|---|
| ① 取数 | MCP 调用方 | 原始返回**立刻落盘** `raw_s<N>.json` / `raw_a<N>.json`，不解析、不复述 | 原始池 |
| ② 瘦身 | `shrink_candidates.py table` | 原始返回 → 紧凑候选表（一行一题：短ID / 题型 / 五档难度 / 选项数 / 题干前 48 字）+ `*_sidmap.json` + `*_pool.json` | `cand_table.md` |
| ③ 决策 | **模型** | **只回「题位→短ID」**（`{"1":"s03",…}`） | `sel.json` |
| ④ 装配 | `shrink_candidates.py assemble` | 从池**自动回填**题干/选项/答案/考点/解析 | `picks_*.json` |

- **禁止**手抄完整内部 ID（长串、贵且易错）→ 一律用**短 ID**（`s01`/`s02`…）。
- `assemble` 输出的 `stem/opts/analyse/method` **保留原始 HTML**（公式线性化交给下游 `build_questions`/`render_paper`）。
- 载体：payload 小（≤10 题）→ 主线程直发；payload 大（长材料 / 带图解答 / 题量大）→ **取数交子代理**（上下文独立，落盘后主线程只读紧凑表）。

### 2.4 输出与会话纪律

> 依据十项原则：「输出精简」+「批读参考资料」+「会话管理」。**模型输出越短，每轮越快；同一份资料读两次，等于白付一轮。**

1. **🔇 输出收口（强制）**：决策步**只输出 JSON**（`{"1":"s03",…}`），**不解释、不复述题干、不展开推理**；校验 / 自检失败**只回报错片段与必要上下文**（用 `validate_picks.py --quiet`），不重述全文。
2. **📌 批读纪律（强制）**：同一份 reference **在同一任务内只读一次**；需要多份时**在该阶段首轮一次性批量读**；**禁止**在后续步骤重复读同一份。
3. **📌 会话纪律（强制）**：一次任务在**一个会话内**完成；中间态一律落盘，跨阶段**从文件恢复**，不依赖会话记忆。**禁止**用「每步压缩上下文」续命。
4. **🛑 停止条件（强制）**：见 §2.1（搜题+解析 ≤T13 / 补缺重试 ≤2 次 / 到顶转降级交付）。

---

## 3. 调用模式（照抄）

### 3.0 装载（T1 · 1 轮）
```
# 一次装载本卷全部工具（ToolSearch 支持 tool_names 传数组）——不要分多次
ToolSearch(tool_names=[tkSubject, tkPoint, tkSearchSubjectQuestion, tkQuestionAnalysis,
                       tkQuestionSame, tkQuestionFrom, tkQuestionType])
```

### 3.1 S3.5 取知识点（缓存优先 · `prep` 一次到位 —— 1 轮）
```bash
# 一次调用同时拿「缓存状态 + 叶名」；给了 --points 则同时返回「映射候选」
python3 scripts/tkpoint_cache.py prep --subject-code 33
python3 scripts/tkpoint_cache.py prep --subject-code 33 --points "光合作用,细胞呼吸,血糖调节"
# 仅当 prep 报 cached=false：拉 mcp__<SERVER>__tkPoint 落盘（建议交子代理做）后再 prep 一次
python3 scripts/tkpoint_cache.py save raw_tkpoint_33.json --subject-code 33
```

### 3.2 S4 搜题主攻（分块 + 同轮并发 + 返回落盘）
```
# ① 分块：题位按连续题号切 3 块（①1-9 ②10-18 ③19-25）
#    —— 优先「主线程直发并同轮并发」；确需隔离大 payload 才用子代理，且总数 ≤2
#
# ② 每轮并发 4 个调用（仅题量 >20 才探 6；保留 ~1.5s 轻量间隔）：
mcp__<SERVER>__tkSearchSubjectQuestion(subjectCode=33, point=["A"], ct=1, dg=11, so=4, ps=10)
mcp__<SERVER>__tkSearchSubjectQuestion(subjectCode=33, point=["B"], ct=1, dg=12, so=4, ps=10)
mcp__<SERVER>__tkSearchSubjectQuestion(subjectCode=33, point=["C"], ct=1, dg=11, so=4, ps=10)
mcp__<SERVER>__tkQuestionAnalysis(SID=<上几轮已选题>, subjectCode=33)      # ← 与搜题同轮混合
#    ⚠️ 不要把 ["A","B","C"] 合并成一次（返回混合列表、Points 为空、无法归属）
#
# ③ 选中即原子落盘：选定 SID + 取到解析 -> 立刻把该题追加写入 picks_<块>.json
# ④ 每 3 题报进度；补搜：dg=0 -> 去 so -> 关键词兜底
# ⑤ 上下文卫生：原始返回落盘 raw_s<N>.json；随后 shrink_candidates.py table 出紧凑候选表
# ⑥ 搜题阶段先不选题 —— 候选拉齐后走「集中决策轮」（§3.5 / Turn Plan T7）
```

### 3.3 S6 取解析（并发 4 · 与补缺同轮）
```
# 每轮并发 4 个解析调用（仅题量 >20 才探 6）；选定的 SID 就发，不等全搜完
# 原始返回落盘 raw_a<N>.json，收尾前用 `pool` 归并成 analysis_pool.json
mcp__<SERVER>__tkQuestionAnalysis(SID=…, subjectCode=33)
mcp__<SERVER>__tkQuestionAnalysis(SID=…, subjectCode=33)
mcp__<SERVER>__tkQuestionAnalysis(SID=…, subjectCode=33)
mcp__<SERVER>__tkQuestionAnalysis(SID=…, subjectCode=33)
```

### 3.4 S7 收尾（**一条命令 = 1 轮**）
```bash
# ★ 首选：校验 → 幂等合并/补缺 → 组装 → 渲染导出 → 自检，一次跑完
bash scripts/finish.sh --spec spec.json --prefix <out_prefix> --work-dir . \
     [--split-blocks "1-9,10-18,19-25"] [--allow-missing] picks_1.json picks_2.json picks_3.json
#   退出码 0=齐全通过 / 1=缺题待补 / 2=降级交付 / 3=自检失败

# —— 以下为 finish.sh 内部步骤，仅在需要「单环节」时手动调用 ——
python3 scripts/validate_picks.py --spec spec.json picks_1.json picks_2.json picks_3.json
python3 scripts/merge_and_gap.py --spec spec.json --existing picks_merged.json --out picks_merged.json picks_*.json
python3 scripts/build_questions.py --spec spec.json --picks picks_merged.json [--split-blocks "1-9,10-18,19-25"]
bash   scripts/render_all.sh    questions.json blueprint.json <out_prefix> <out_dir>      # 常规一键
bash   scripts/render_blocks.sh <out_prefix> questions_block1.json questions_block2.json  # 分块重叠
python3 scripts/selfcheck_paper.py <试卷.docx> <解析.docx> --blueprint <bp.html> --questions questions.json
```

### 3.5 候选瘦身与 picks 装配（v2.3 核心 · 大 HTML 不进上下文）
```bash
# ① 原始返回 → 紧凑候选表（模型只看这张表；一行一题）
python3 scripts/shrink_candidates.py table --in raw_s1.json raw_s2.json --out-dir . --prefix cand
#   产出 cand_table.md（短ID/题型/五档难度/选项数/题干前48字）+ cand_sidmap.json + cand_pool.json
#
# ② 模型决策：只输出「题位→短ID」写进 sel.json，例如 {"1":"s03","2":"s11"}
#
# ③ 解析池归并（多个 raw_a*.json）
python3 scripts/shrink_candidates.py pool --in raw_a1.json raw_a2.json --out analysis_pool.json
#
# ④ 装配 picks（题干/选项/答案/考点/解析全部自动回填）
python3 scripts/shrink_candidates.py assemble --sidmap cand_sidmap.json --pool cand_pool.json \
     --analysis-pool analysis_pool.json --spec spec.json --map sel.json --out picks_1.json
```

---

## 4. 缓存策略与元数据可见性（合规）

| 可缓存（元数据） | 不可缓存（试题内容） |
|---|---|
| `mcp__<SERVER>__tkPoint` 知识点树（`~/.workbuddy/cache/cnki-edu-ai-zujuan-paper/tkpoint/`） | 题干 / 选项 / 答案 / 解析 / 试题图片 |
| `mcp__<SERVER>__tkSubject` / `mcp__<SERVER>__tkQuestionType` / `mcp__<SERVER>__tkQuestionFrom` 码表 | —— |
| 「教材知识点 → 库考点名」映射表 | —— |

- 缓存目录可用环境变量 `ZJ_CACHE_DIR` 覆盖。
- 导出的 docx 内嵌图片属「用户交付物」，与「不缓存试题内容」不冲突。

### 4.1 元数据不外显（强制）

> **口径**：接口**字段名**（`SID`/`Label`/`Degree`…）用于解析，属内部知识，可留在 `references/`；接口**字段值**属题库元数据，**一律不外显**。

| 层面 | 红线 |
|---|---|
| **对话输出** | 不呈现 `SID` / 题源标注 / 原始难度系数；难度只说**五档** |
| **三份交付物** | 细目表**不渲染**「库标准考点名」列与「库：」标注；解析【考点】**只取教师侧命名**（模型给定 / 细目表 `point`）——**不回退接口 `Points[].Value`**，取不到就留空不渲染；【考点】**不加**平台名 / 版权尾缀；链路 B **不渲染**题源标注；不落款平台名 |
| **中间态** | 紧凑候选表**只给五档**（不带 `Label`、不带原始 `Degree`）；`assemble` **不写** `sid` / `source`；会话状态只存**会话内短引用** |
| **例外（必须保留）** | ① `raw_*.json` / `*_pool.json` 是「大 HTML 不进上下文」的落盘载体，**必然含接口原始字段**——它们**只在工作目录、不进对话、不作交付物、不缓存**；② 题图地址由 `render_paper.IMG` 生成（`ZJ_IMG_HOST` 可覆盖），**过程 HTML 会带图片域名**，故 HTML 仅作转档中间物、**不交付** |

---

## 5. 轻量模式（≤10 题）

1. **跳过** S3.5 全量 `mcp__<SERVER>__tkPoint`（已知单点直接搜；名词不确定才 `tkpoint_cache.py prep`）。
2. 每题各发一次搜题，**同轮并发 4**（题少、无需分块；仍保留 ~1.5 s 轻量间隔）。
3. 选中即原子落盘 + 同轮并发取解析（4）。
4. 收尾**直接一条命令**：`finish.sh --spec spec.json --prefix <p> --work-dir . picks_*.json`（内部含 validate/build/render/selfcheck）。
> 实测单卷可达 **≈30–60 秒**。

---

## 6. 预期收益

**（a）轮次视角（决定墙钟）**

| 措施 | 模型轮次（25 题） |
|---|---|
| 反例：S3.5 三步 + S4/S6 分段串行 + S7 五步 | ≈ **26 轮** |
| 理论值：`prep`(1) + S4/S6 同轮混合(≈5–9) + `finish.sh`(1) | ≈ **7–12 轮**（⚠️ 偏乐观，被限流证伪） |
| **修正值**：装载+归一化(1) + 搜题(5–6) + 集中决策(1) + 解析(5–6) + 收尾(1) | ≈ **11–14 轮** |

**（b）墙钟视角（估算，随题库响应波动）**

| 措施 | 预估墙钟（25 题） |
|---|---|
| 基线 | 约 4–6 分钟 |
| P0（同轮并发 + 并发解析 + 混合流水线） | 约 1.5–2.5 分钟 |
| P0 + P1（缓存 + `prep` + 自适应并发 / 节流） | 约 1–1.5 分钟 |
| 全量 + `finish.sh` + 分块重叠转档（**理想估算，未计轮次间隙**） | ≈ 40–90 秒 |

> ⚠️ **估算必须计入「执行载体可靠性」**：把 50 次调用塞进"单个代理一次性大产出"时，**失败概率极高**（2026-10-10 实测：预估 1.5–2 min，实际 >1 h 且 0 可用）。
> 故真实耗时预估应拆两层 =「**API 理论下限**（调用数 / 并发 × 单程延迟；实测 25 题**仅 ≈20 s**）」+「**轮次编排余量**」（靠 §2.1 轮次铁律压到最小）。

---

## 7. 容错与续跑（与提速并列的硬约束）

提速**不能**以"长任务一次性大产出"为代价。四层防护（预防/检测/恢复/兜底）、断点续跑协议、分块重叠转档的完整口径见 **`references/fault-tolerance.md`**。要点：
- 进 build 前**必跑** `validate_picks.py`；
- 缺题**只补 missing**（`merge_and_gap.py`，绝不覆盖好题）；
- 仍缺题 → **降级交付**（缺题清单），绝不 0 交付。
