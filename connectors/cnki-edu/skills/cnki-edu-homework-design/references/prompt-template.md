# Prompt 模板与输出 Schema

## 一、设计原则

prompt 不是一段话，而是**拼装产物**：

```
final_prompt = BASE_TEMPLATE + SUBJECT_PACK[subject] + STAGE_PACK[stage] + plan_text（可选）
```

分层的理由：通用部分只写一次（溯源/反幻觉/输出格式），学科包只写"这个学科特有的"指标，学段包横切覆盖。
**不要把所有约束塞进一个大 prompt** —— 6 学科 × 4 学段 = 24 份重复维护，改一处漏三处。

也不要把通用规则重复写进学科包，会造成约束冲突。

---

## 二、通用模板（BASE_TEMPLATE）

权威版本在 `scripts/homework_kit.py` 的 `BASE_TEMPLATE` 常量里。结构如下：

```
# 角色
你是「中小学作业设计助手」，依托 CNKI 学术资源与《{std_doc}》，
为教师生成可溯源、对齐课标、分层有据的作业题。
你不替代教师决策——输出永远是待审草稿，不是可直接布置的成品。

# 输入变量
- 学科/学段/年级 / 单元/主题 / 课标条目 / 核心素养 / 班级水平 / 分层比例 / 题型偏好 / 题量·时长 / 是否情境化

# 差异化四锚（这是区别于通用 AI 出题的全部内容）
1. 出处：材料/情境题必须挂 CNKI 真实文献出处，可点击溯源
2. 对齐：绑定具体课标条目原文，而不是泛泛的"符合教学要求"
3. 分层依据：按学科包定义的分层规则出题，不许凭感觉标难度
4. 认知层级：明确标注布鲁姆层级且不超学段上限

【学科约束包 / 学段约束包（JSON 原文注入）】
【供题计划（可选）】
【共享材料（可选，同材异层模式：一份材料喂多层题目，顶部渲染一次）】

# 输出格式（严格 JSON，禁止任何额外解释文字）
（见下节 schema）

# 硬性约束（违反任一条，下游校验器会整批拦截）
1~8 条 + 第 9 条（有供题计划时） + 第 13 条（同材异层模式：meta.shared_material 必填且与 prompt 顶部材料一致，各题 material 留空、stem 用「根据材料」指代）

# 禁止
- "据研究表明…"却没有 sources 的句子
- 答案矛盾、无解、超纲的题目
- 脱离输入课标条目自行发挥
- 政史地：不合规地图；涉及台湾、香港、澳门必须表述为中国的一部分
```

**为什么输出必须是 JSON**：下游要跑硬校验器，还要程序化拼装成作业单。让模型输出散文体，
等于把"这题合规吗"的判断权交回给人，整套自动化就废了。

---

## 三、输出 JSON Schema

```json
{
  "meta": {
    "std_aligned": "课标条目原文（必须来自输入或检索到的课标库，不得杜撰）",
    "literacy": ["核心素养1", "核心素养2"],
    "shared_material": "同材异层模式必填：与 prompt 顶部「共享材料」一字不差，render 据此顶部渲染一次"
  },
  "items": [
    {
      "id": 1,
      "level": "基础|巩固|拓展",
      "type": "题型（限学科包 types 白名单）",
      "cognitive": "记忆|理解|应用|分析|评价|创造",
      "stem": "题干（分句不超过学段 sentence_len_max 字）",
      "answer": "参考答案",
      "analysis": "分步解析",
      "answer_check": {
        "changed": "adapt 题必填：相对原题改了哪些数据/条件，逐项列清（列表或字符串均可）",
        "recompute": "adapt 题必填：用改动后的数据重新求解的过程与结果",
        "verdict": "adapt 题必填：一致（只能填这个；复算对不上就改数据或改答案后重算）"
      },
      "dur": 6,
      "mode": "written|oral",
      "origin": "retrieve|adapt|generate，必须与供题计划指定的 mode 一致",
      "source_id": "retrieve 题必填：原题库编号（内部用，不印在作业单上）",
      "source_label": "retrieve 题必填：该题真实试卷出处，如「2026春·兖州区期末」",
      "based_on": "adapt 题必填：改编自哪道题的 bank_id（内部用，不印在作业单上）",
      "based_on_label": "adapt 题必填：该题真实试卷出处，如「2026秋·昌吉州校级月考」",
      "rubric": "写作/作品/论述题必填评价量规",
      "safety": "理化生实验题必填安全提示",
      "apparatus": "理化生实验题器材清单",
      "sources": [
        {
          "type": "journal",
          "author": "谭霈生",
          "title": "论戏剧性",
          "container": "来源期刊名（如《语文建设》）",
          "year": 2023,
          "issue": 3,
          "pages": "12-20",
          "generic": false
        },
        {
          "type": "book",
          "author": "杨建文",
          "title": "中国古典悲剧史",
          "publisher": "出版社",
          "year": 1994,
          "generic": false
        }
      ]
    }
  ]
}
```

`generic: true` 表示"无 CNKI 素材来源"。但原创题**不允许靠 `generic=true` 蒙混过关**：`generate`（原创生成）必须挂经 `mcp__<SERVER>__searchVectorBJ` 实检返回的真实篇名，若检索无结果，本题应改为 `adapt`（基于某道真实原题），不得作为"无情境 generate"。校验器只认 `generic=false` 的 sources 为有效溯源；`generate` 无 `generic=false` 文献会被拦截。

### `answer_check`：改编题的答案一致性验算（第 14 条，阻塞）

```json
"answer_check": {"changed": ["把铁块 2 kg 改成木块 0.8 kg"],
                 "recompute": "漂浮时 F=G=mg=0.8×10=8 N",
                 "verdict": "一致"}
```

三件套缺一即拦：`changed`（改了哪些数据/条件）· `recompute`（用改动后的数重新求解）· `verdict`（只能「一致」）。
`verdict` 填了「不一致」也拦——那等于承认改编数据与答案对不上，得先改数据或改答案再交付。
这一步不能省的原因：教师不信任 AI 出题，源头不是"题不好"，而是**改了数据没改成答案**，一次就足够弃用。

### sources 著录规范（GB/T 7714—2015 简化版）

溯源要能被教师在 CNKI 上定位到，就不能只写"杨建文《中国古典悲剧史》"这种半成品。
按文献类型取著录项，**type 必填**：

| type | 中文名 | 必填字段 | 渲染样式 |
|---|---|---|---|
| `journal` | 期刊论文 | author·title·container·year·issue（pages 可选） | `作者．篇名[J]．来源期刊，年(期)：起止页．` |
| `book` | 专著 | author·title·publisher·year | `作者．书名[M]．出版社，年．` |
| `chapter` | 文集析出 | author·title·container·publisher·year | `作者．篇名[M]//文集名．出版社，年：页．` |
| `thesis` | 学位论文 | author·title·publisher·year | `作者．篇名[D]．授予单位，年．` |
| `newspaper` | 报纸 | author·title·container·year | `作者．篇名[N]．报名，年．` |
| `textbook` | 教材 | title·publisher·year | `书名．出版社，年．` |

三条铁律：

1. **按实际类型填，不许套错**。专著硬套 journal 就等于伪造期刊名和期号——这是最糟的事故。
2. **拿不准就留 null**，渲染成灰色 `【待补充】`，校验器记为「著录缺口」告警（不阻塞）。**缺字段是待补，填错是编造**，两者性质完全不同。
3. 旧格式 `{name, year}` 仍兼容并降级渲染，但会被提示"建议补 type 与完整著录字段"。

---

## 四、硬性约束 → 十二项校验的映射

prompt 里写了不算数，**得有代码拦**。校验清单：

| # | 校验项 | 拦截文案示例 |
|---|---|---|
| 1 | 课标对齐 | `meta.std_aligned 缺失：未绑定课标条目` |
| 2 | 政策书面红线 | `第 3 题为书面题，但 小学低段(1-2) 不布置书面家庭作业（政策红线）` |
| 3 | 总时长 | `预计总时长 87 分钟 > 上限 60 分钟，需压缩题量` |
| 4 | 溯源必填 | `第 5 题（材料分析）缺少可溯源的 CNKI 来源` |
| 5 | 必填字段 | `第 2 题缺少必填字段：answer、safety` |
| 6 | 分句长度 | `第 4 题题干分句超 15 字（19 字），需拆分` |
| 7 | 认知层级上限 | `第 6 题认知层级「应用」超过学段上限「理解」` |
| 8 | 禁例关键词 | `第 1 题命中禁例关键词：超纲` |
| 9 | 原创超限 | `原创题 3 道超过上限 2 道，超出部分须降级为 adapt` |
| 10 | 缺 source_id | `第 2 题 origin=retrieve 但缺 source_id` |
| 11 | 缺 based_on | `第 4 题 origin=adapt 但缺 based_on` |
| 12 | 原创无素材 | `第 7 题原创但无 CNKI 素材来源，需降级为改编` |
| 13 | 未照办供题计划 | `第 1 题 origin=adapt，但供题计划指定的这一题是 retrieve；必须按计划出` |
| 14 | 改编未做答案一致性验算 | `第 4 题 origin=adapt 但缺 answer_check：改编题必须先重算答案` |

第 13 条是 mix 档的保险丝：模型擅自把 `retrieve` 写成 `adapt`，等于把"可以原样用的真题"又改了一遍，
配额的意义当场失效。题量与计划不符时，逐题比对会自动降级为分布告警（不误伤）。

第 14 条把「改了数据却沿用原答案」这个最贵的错误挡在交付之前。三者缺一即拦，`verdict` 非「一致」也拦。
注意：**上线前生成的历史 `items.json` 会被这条拦**，因为它们没有验算记录——重跑或人工复核回填二选一。

另有**告警级**检查（不阻塞交付，退出码仍为 0，但会印在作业单末尾）：

| 告警 | 触发条件 |
|---|---|
| 缺 `based_on_label` | adapt 题有 `based_on` 但没填真实试卷出处——作业单会退化成教师看不懂的内部编号 |
| 缺 `source_label` | retrieve 题同上 |
| 题量与计划不符 | 计划 N 题实际 M 题，逐题比对跳过，转为人工核对提示 |
| 真题早于现行课程方案 | 出版年份早于 2022 版课程方案（高中 2020 修订），可能基于旧教材 |
| 题源出处缺年份 | `Label` 里没有年份，无从判断新鲜度与新/旧课标适用性 |
| `retrieve` 题面被改动 | 输出的题面与计划里的题库原文前 30 字不一致，疑似擅自润色 |
| 答案数值对不上复算 | 答案里的数值在 `recompute` 与 `analysis` 中均找不到 |
| 著录缺口 | `sources` 缺该文献类型的必填字段，渲染为【待补充】 |
| 只有教材溯源 | 学术性溯源一条期刊/学位论文都没有 |
| 溯源未含期刊 | 溯源优先级低于 `journal`（见 `references/source-citation.md`） |

调用：

```bash
python scripts/homework_kit.py validate \
  --items llm_out.json --subject 数学 --stage "初中(7-9)" --plan plan.json
```

退出码非 0 = 被拦。

---

## 五、抽象要求 → 硬性条件的转译方法

用户的工作习惯是把抽象约束显式翻译成可硬性执行的条件。做 prompt 设计时照这个套路写：

| 抽象要求 | 转译后的硬性条件 |
|---|---|
| 有学术依据 | `generate` 题须 `sources` ≥1 条且 `generic=false`（经 `mcp__<SERVER>__searchVectorBJ` 实检）；检索无结果则本题改 `adapt`（基于原题），不得强行 generate |
| 溯源可定位 | `sources` 每条带 `type` 并给全该类型必填著录字段（期刊必带 刊名+年+期），缺的留 null 渲染成【待补充】 |
| 来源优先级 | **期刊论文第一**：`journal > thesis > newspaper > book > chapter > textbook`；教材不算学术来源，只在引用教材原文时用 |
| 对齐课标 | `meta.std_aligned` 必填，且必须来自输入给定的课标条目 |
| 分层科学 | 基础=单知识点·步骤≤2；巩固=2 知识点·步骤≤4；拓展=跨知识点或开放探究 |
| 语言规范 | 题干分句≤学段上限；禁用"超纲/竞赛/极难"；用词限教学白名单 |
| 答案正确 | 每题必附 `answer`+`analysis`；应用题数据须有唯一可算解 |
| 反幻觉 | `sources` 须真实可检索（经 `mcp__<SERVER>__searchVectorBJ` 返回），禁止编造；检索无结果就说没有，不得挂虚构文献 |
| 适配受众（分句长度/可读性） | 学段包 `sentence_len_max`：15 / 20 / 25 / 35 |

---

## 六、同题对比：普通 prompt vs 差异化 prompt

**普通 prompt 输出**（无约束）：
> 小明去商店买文具，铅笔每支 2 元，他买了一些花了 10 元，问他买了几支？

无来源、无层级、无课标绑定，和任何通用 AI 没区别。

**差异化 prompt 输出**：
```json
{
  "meta": {"std_aligned": "能根据具体问题中的数量关系列出方程",
           "literacy": ["运算能力", "模型观念"]},
  "items": [{
    "id": 1, "level": "基础", "type": "应用题", "cognitive": "应用",
    "stem": "小明买铅笔，每支2元，共花10元，求支数。",
    "answer": "5 支", "analysis": "设支数为 x，2x=10，解得 x=5。",
    "dur": 4, "mode": "written", "origin": "adapt",
    "based_on": "M001", "based_on_label": "2026秋·昌吉州校级月考",
    "sources": [{
      "type": "journal", "author": "张奠宙", "title": "核心素养视角下的应用题设计",
      "container": "中小学数学教育", "year": 2023, "issue": 5, "pages": "18-22", "generic": false
    }]
  }]
}
```

同一道题，多了**课标绑定、素养映射、分层标签、认知层级、耗时估算、供给来源、可溯源出处**——这就是差异化。

---

## 七、修正回环用的一次性修正 prompt

不要把校验失败做成"回到生成"的无限回环。用一次修正，把 `issues` 原样回喂：

```
以下是你上一版输出被校验器拦截的问题清单，逐条修正后重新输出完整 JSON，
不要解释、不要只输出改动部分：

{issues}

修正规则：
- 缺课标对齐 → 从上方输入的课标条目填入 meta.std_aligned
- 缺溯源 → 补 sources（generic=false），或改出无情境题并移出需溯源题型
- 著录不全 →**去 CNKI 检索原文补真字段**，不许凭印象补；实在查不到就留 null，让它渲染成【待补充】
- 总时长超限 → 删减题目或降低单题 dur，不得简单改小 dur 数值蒙混
- 分句超长 → 拆分长句，不得删减信息
- 认知层级超限 → 降低题型难度（如由论述改为简答）
- 政策红线 → mode 改为 oral，题型改为口头表达/实践任务
- 原创超限 → 超出部分降级为 adapt 并补 based_on
- 原创无素材 → 降级为 adapt（基于某道真实原题）并据实标注「未检索到可引用 CNKI 文献」，不得标 generic=true 强行 generate
- 缺答案验算 → 补 answer_check 三件套；重算后若发现答案不对，改新答案而不是改 verdict
- 未照办计划 → 按计划的 mode 补齐对应字段（retrieve 补 source_*，adapt 补 based_on_* 与验算）
```

修完再跑一次 `validate`；仍不过就带拦截说明交付教师人工处理，**不要假装通过**。
