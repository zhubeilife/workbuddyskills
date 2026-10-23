# AI 报销单自动填单 — 工作流编排

> 本文件是报销自动填单的完整工作流参考。
> CLI 命令用法见 [`invoice-reim.md`](invoice-reim.md)。
> 实际调用通过 `weaver-work-cli --json invoice run <operation>` 执行，不能直接 curl E10 接口。

---

## ⚠️⚠️⚠️ 最高优先级规则：严禁篡改任何原始数据值 ⚠️⚠️⚠️

**所有从 CLI 返回、用户提供、或上下文已有的数据值，都必须逐字符原样使用，严禁做任何修改。**
**这包括但不限于：ID、日期、金额、名称等一切字段值。**

已知反复出现的错误：

| 类型 | 正确值 | 错误值（被AI篡改） | 错误原因 |
|------|--------|-------------------|---------|
| ID | `100003720000076271` | `100003720000000076271` | 中间被插入了 `000` |
| ID | `100003720000077896` | `100003720000000077896` | 中间被插入了 `000` |
| 日期 | `2026-07-19` | `2026-00000000007-19` | 月份被篡改，插入了多余的 `0` |
| 金额 | `108.2` | 不得修改 | — |

**处理规则：**
1. 从 CLI 返回的 JSON 中获取的值 → **逐字符原样复制**，一个字符都不能改
2. 用户提供的值 → 原样使用
3. **绝不做"对齐位数"、"补零"、"格式化"、"规范化"等任何处理**
4. 日期值从 CLI 获取后直接使用，不要尝试拆分再拼接
5. 如果不确定某个值是否正确，回溯到原始数据源重新复制

---

## 报销共享常量（所有 reference 统一引用本节）

以下常量在报销 reference 中多处出现，**统一以本节为准**，其余文件引用本节不再重复定义。

| 常量 | 值 | 说明 |
|------|-----|------|
| 默认合同编号 | `"20260999"` | 快速路径 `template.build`/`auto-prepare` 与手工路径统一使用；CLI 0.1.19 起未传入时自动填充并产生 warning |
| 非出差相关客户 | `"100504500000311504"` | 泛微上海；出差流程必须由用户提供具体客户 |
| 兜底费用科目 | `"100502270000000104"` | 其他-管理费用；所有匹配策略均未命中时使用 |
| 人民币币种 ID | `"100001050000000001"` | — |
| 报销方式默认值 | optionValue `"7"` | 银行（个人报销） |
| 全额红冲状态值 | `status = 8` | `comm_info.pro.status`；此类发票必须过滤，不允许报销 |
| 相关凭证 typeCode | 17, 18, 57, 58 | 不能独立成行，必须与发票配对 |
| directSuperior 取值 | `directSuperior.id` | ⚠️ **不是 `allSuperiors[0]`**（后者是上级链最高层） |
| continuation 有效期 | 600 秒 | 过期后重新 prepare 即可，无需重新征询用户确认 |

> **continuation 过期处理**：`prepare`/`auto-prepare` 签发的 continuation 有 600 秒有效期。中间若用户核对耗时过长导致过期（返回 `validation/continuation_expired`），**重新 `prepare` 后立即 `apply` 即可**（用户已确认过的内容无需重新征询）。不要重放旧 continuation。

---

## 时间戳内联计算（零工具调用）

> **所有日期 → 秒级时间戳的转换由 AI 直接计算，无需调用外部脚本。**

### 计算公式（UTC+8 时区）

```
日期 → 秒级时间戳：
  起始时间 = Date("YYYY-MM-DD 00:00:00 +08:00") 的 Unix 秒数
  结束时间 = Date("YYYY-MM-DD 23:59:59 +08:00") 的 Unix 秒数

默认查询（最近一周）：
  begin = 今天00:00:00秒时间戳 - 7 * 86400
  end   = 今天23:59:59秒时间戳

扩大到一个月（fallback）：
  begin = 今天00:00:00秒时间戳 - 30 * 86400
  end   = 今天23:59:59秒时间戳

用户指定日期范围：
  begin = 指定起始日 00:00:00 秒时间戳
  end   = 指定结束日 23:59:59 秒时间戳
```

### 发票查询默认入参

CLI 已默认 `sreim="3"`、`bill_type=0`、`page_size=10`。报销查票时只传日期范围：

```json
{
  "page_size": 20,
  "start_pos": 0,
  "date_begin": "{begin}",
  "date_end": "{end}"
}
```

可选筛选参数（按用户意图添加）：
- `"content"`: 消费内容关键词（如 `"滴滴"`、`"住宿"`）
- `"number"`: 发票号码精确匹配
- `"types"`: 发票类型 ID 数组

> 按发票号码查询时不设 `date_begin` / `date_end`。
> 不要传 `flag`、`fylxs`、`consumption_tm_begin`、`consumption_tm_end`（CLI 不接受这些字段）。

---

## 核心行为准则（必须遵守）

### 1. 立即获取数据，展示后确认

当用户表达报销意图时（如"帮我报销"、"我要报销"、"报销一下"等），**必须立即调用 `invoice.list` 获取发票数据，展示发票汇总信息后询问用户确认，确认后再自动执行后续填单流程**。禁止反问用户要求提供发票信息、事前申请信息、报销用途等。

**禁止的行为：**

- 问用户"请提供发票信息"
- 问用户"是否有事前申请"
- 问用户"报销用途是什么"
- 列出一堆需要用户提供的信息清单
- 任何形式的"请先提供XX"
- **输出内部推理过程**（如"我需要引导确认"、"我现在要调用 XX CLI"、"我需要先获取XX数据"），直接对用户说话

**正确的行为：**

- 按内联公式计算时间戳参数，调用 `invoice.list` 获取发票数据
- 最近一周无结果 → 自动用一个月参数再查
- 直接调用 `invoice.reim.requests.list` 获取用户的事前申请
- **获取到发票后，先展示发票汇总信息（张数、基础信息），明确告知用户查询范围，询问用户确认是否报销**
- 用户确认后，自动执行匹配 → 获取表单结构 → 组装填单 JSON → `invoice.reim.flow.create.prepare` → 用户确认 → `.apply` 生成报销单

### 2. 根据用户意图智能构建查询条件

#### 报销填单意图

| 用户说的话 | AI 应该做的 |
|------------|-------------|
| "帮我报销" / "我要报销" | 查**最近一周**发票 → 无结果则查**最近一个月** → **展示发票汇总，询问确认** → 确认后走后续流程 |
| "报销打车费" | 设置 `content="滴滴"` 筛选交通类 → **展示发票汇总，询问确认** → 确认后走后续流程 |
| "报销上周的发票" | 设置时间范围为上周 → **展示发票汇总，询问确认** → 确认后走后续流程 |
| "报销发票号码 xxx" | 设置 `number="xxx"` 精确匹配 → **展示发票汇总，询问确认** → 确认后走后续流程 |
| 用户直接提供了发票数据 | **跳过 Step 1A** → **展示发票汇总，询问确认** → 确认后继续后续流程 |
| 用户提供了 fileId | 先调用 `invoice.reim.file-ocr.preview`（Step 0）→ **展示发票汇总，询问确认** → 确认后继续 |

#### 纯查询意图

> **纯查询操作**（查发票、查流程、查申请等）不走本工作流，直接用对应的查询 operation。

#### 查询结果上下文复用（重要）

如果上下文中已有查询过的数据，报销时**直接复用**：

- 已有事前申请 → 用 `createTime` 筛选发票
- 已有发票 → 用 `invoiceDate` 筛选事前申请
- 两者都有 → 直接跳过 Step 1A/1B，进入 Step 2 匹配

### 3. 用户操作场景全覆盖

#### 直接报销

| 用户输入 | 起始步骤 |
|----------|---------|
| "帮我报销" | 1A → **1C（发票确认）→ 用户确认** → 1B → 2 → 2.5 → 3 → 3.5 → 4 → 5 |
| "报销打车费" / "报销上周的" | 1A（加筛选条件）→ **1C → 用户确认** → 后续同上 |
| 提供 fileId | Step 0 → **1C → 用户确认** → 1B → 后续同上 |
| 直接给发票数据 | **1C → 用户确认** → 1B → 后续同上 |

#### 模糊意图引导

| 用户输入特征 | 处理方式 |
|-------------|---------|
| 含"报销"关键词 | 直接执行报销流程 |
| 含"出差"/"采购"/"买了"等间接关键词，不含"报销" | 直接问用户"需要我帮您创建报销单吗？" |
| 用户确认 | 进入全自动报销流程 |
| 用户否认 | 正常回应，不执行报销 |

> **⚠️ 禁止输出内部推理过程**。直接对用户说话，不要解释自己在做什么。

#### 报销后修正（`invoice.reim.flow.update`）

用户确认 `need_user_confirm`、补充 `unable_to_fill`、修改字段值、删除/追加明细行 → 均通过 `invoice.reim.flow.update.prepare/apply` 完成。

### 4. 自动化决策原则

- **用户已提供发票数据 → 跳过 Step 1A，直接用已有数据继续**
- 发票列表有数据 → **先展示发票汇总信息（Step 1C），告知用户查询范围，等用户确认后再往下走**
- 最近一周无结果 → **自动 fallback 到最近一个月再查一次，不需要问用户**
- 事前申请有数据 → 自动匹配，不需要用户确认"是否关联"
- 事前申请为空 → 跳过匹配，直接用发票数据填单，不需要问用户
- 匹配到唯一结果 → 直接使用，不需要用户确认
- **只有在必须用户做选择时才暂停**（如：多候选需要选一个、发票列表为空无法继续、**出差流程必须填写相关客户**）
- **⚠️ 严禁篡改任何原始数据值**

---

## 整体工作流程

```
前置: CLI 认证（由 weaver-e10-shared 处理）
         ↓
Step 0 (可选): invoice.reim.file-ocr.preview → 识别发票
         ↓
Step 1A: invoice.list (可跳过) ←→ Step 1B: invoice.reim.requests.list
         ↓
Step 1C: 展示发票汇总 → 用户确认是否报销
         ↓ (用户确认)
Step 2: 发票 ↔ 事前申请匹配绑定 (reim-matching-rules.md)
         ↓
Step 2.5: invoice.reim.workflow.resolve → 获取工作流ID
         ↓
Step 2.6: 按工作流ID分组（多个工作流 → 多组，各组独立执行后续步骤）
         ↓  ↓  ↓ (每组)
  ┌──────────────────────────────────────────┐
  │ ▼ 并行组 A（同时发起）                      │
  │ Step 3:   invoice.reim.form.structure    │
  │ Step 3.5: invoice.reim.row-info × N      │
  │ Step 3.6: invoice.reim.employee-superiors │
  │ 交通类额外: invoice.get × M               │
  └──────────────────────────────────────────┘
         ↓ (全部返回后)
Step 4: 组装填单 JSON (reim-form-fill-rules.md)
         ↓
Step 4.5: 出差流程 → 提醒用户填写相关客户（未提供则不允许报销）
         ↓
Step 5: invoice.reim.flow.create.prepare → 用户确认 → .apply → 展示汇总
         ↓
Step 6 (可选): invoice.reim.flow.update.prepare/apply → 用户修正
```

### ⚡ 并行调用策略（必须遵守）

| 并行组 | 可并行的操作 | 说明 |
|--------|------------|------|
| **Step 1 并行** | `invoice.reim.requests.list` 与 Step 1C 发票展示 | 用户确认期间预取事前申请 |
| **Step 3 并行** | `form.structure` + `row-info` × N + `employee-superiors` + `invoice.get` × M | 全部互相独立，**必须同时发起** |
| **多张发票** | 多张发票的 `row-info` | 各发票独立，强制并行 |
| **交通类行程** | 多张交通发票的 `invoice.get` | 各发票独立，强制并行 |

> **缓存策略**：`form.structure` 和 `employee-superiors` 在同一会话、同一 workFlowId 下只需调用一次，结果可跨多组报销单复用。

---

## Step 0（可选）: fileId → 发票识别

当用户提供了 `fileId`（文件/附件ID）时，调用 `invoice.reim.file-ocr.preview` 一步完成识别。

| 识别结果 | 处理方式 |
|----------|----------|
| 全部成功 | **跳过 Step 1A**，用识别结果继续 |
| 部分成功 | 用成功的继续，提示失败项 |
| **全部失败** | **暂停询问用户**，确认后才继续 |

> CLI 详情见 [reim-api-reference.md](reim-api-reference.md#0-文件ID转发票识别)

---

## Step 1A: 获取发票数据

> **如果用户已提供发票数据或已通过 Step 0 获取，则跳过此步骤。**

通过 `invoice.list` 查询。

### 默认查询策略（用户未指定日期时）

1. 按内联公式计算最近一周时间戳 → 调用
2. 有结果 → Step 1C 展示汇总，告知"查询的是最近一周"
3. 无有效发票 → 计算最近一个月时间戳 → 再次调用
4. 有结果 → Step 1C 展示汇总，告知"最近一周没找到，已扩大到一个月"
5. 仍无结果 → 告知用户未找到发票，建议指定日期范围

### 日期筛选参数

| 参数 | 用途 | 使用时机 |
|------|------|----------|
| `date_begin` / `date_end` | 开票日期范围 | 默认使用 |
| `create_tm_begin` / `create_tm_end` | 录入/创建日期范围 | 用户明确说"录入日期"/"创建日期"时 |

**⚠️ 数据过滤（红冲票排除）：**
- **快速路径**：`candidates.list` **自动过滤** `status=8` 的全额红冲发票（过滤张数在 `summary.filteredRedReversedCount` 中报告），无需手动处理。
- **手动路径**：使用 `invoice.list` 获取发票后，**必须在进入任何后续流程前先过滤掉 `info.comm_info.pro.status == 8` 的发票**。过滤后向用户报告："已自动排除 N 张全额红冲发票"。
- 全额红冲发票不允许报销，**两条路径都不能让红冲票进入匹配/组装环节**。

关键返回字段映射见 [reim-api-reference.md](reim-api-reference.md#1-获取发票数据)。

---

## Step 1C: 展示发票汇总，等待用户确认

获取到发票数据后，**必须先展示发票汇总信息，询问用户确认后才继续后续流程**。

### 展示格式

展示时必须包含：**查询范围说明** + **发票汇总表格** + **确认提示**。

| 场景 | 开头说明 |
|------|----------|
| 默认查一周有结果 | "已为您查询最近一周（{起始} ~ {结束}）..." |
| 一周无结果、一个月有结果 | "最近一周未找到，已扩大到最近一个月（{起始} ~ {结束}）..." |
| 一个月也无结果 | "均未找到未报销发票。您可以指定日期范围或检查是否已录入。"（结束） |
| 用户指定日期范围 | "共找到 N 张（{用户指定的范围描述}）..." |

表格列：`# | 发票类型 | 开票日期 | 发票号码 | 金额 | 销方名称 | 费用类型`

尾部：「请确认是否使用以上发票进行报销？如需查询其他日期范围，请告诉我。」

### 用户响应处理

| 用户响应 | 处理方式 |
|----------|----------|
| 确认 | 继续 Step 1B → Step 2 → 后续流程 |
| 选择部分发票（"只报第1、3张"） | 按用户指定筛选发票，继续后续流程 |
| 否认 | 结束报销流程 |
| 补充条件 | 调整查询条件重新查询，再次展示确认 |

---

## Step 1B: 获取事前申请流程

通过 `invoice.reim.requests.list` 获取。

默认入参：`{"pageNo": 1, "pageSize": 20}`

### Step 1 执行顺序与预筛选策略

> **核心时间关系：事前申请日期一定在开票日期之前。**

| 场景 | 筛选方式 |
|------|----------|
| 先有发票 → 筛选事前申请 | `cusCreateDateEnd` = 最晚 invoiceDate，`cusCreateDateStart` = 最早 invoiceDate - 90天 |
| 先有发票 → **话费报销** | `cusCreateDateEnd` = 最晚 invoiceDate，`cusCreateDateStart` = 最早 invoiceDate - **1095天（3年）**，且加 `requestname="话费"` 缩小范围（见 [reim-phone-subsidy-rules.md](reim-phone-subsidy-rules.md)） |
| 先有事前申请 → 筛选发票 | `date_begin` = 最早 createTime 秒时间戳 |
| 并行获取 | 不做预筛选，Step 2 匹配时统一过滤 |

---

## Step 2: 发票与事前申请匹配绑定

> **详细匹配规则见 [reim-matching-rules.md](reim-matching-rules.md)**

匹配完成后产出绑定关系数据结构：

```json
[
  {
    "invoiceId": "INV001",
    "preApprovalId": "1298294241967177729",
    "preApprovalWorkflowId": "1181057526276915214",
    "matchConfidence": "high",
    "matchReasons": ["时间范围匹配", "费用类型一致"]
  }
]
```

### Step 2 匹配结果展示（推荐）

匹配完成后，**建议向用户展示匹配结果**，而不是静默进入下一步。展示格式：

```markdown
发票与事前申请匹配结果：

| # | 发票号码 | 金额 | 匹配到的事前申请 | 置信度 | 匹配原因 |
|---|----------|------|------------------|--------|----------|
| 1 | 36901189 | ¥108.20 | 交通费报销-后端开发111-2026-07-25 | ✅ 高 | 费用类型匹配、时间匹配 |
| 2 | 36901201 | ¥380.00 | （未匹配） | — | 无匹配的事前申请 |

确认后将自动进入后续填单流程。如需调整匹配关系，请告诉我。
```

- 匹配到 high 置信度的直接标记 ✅ 高
- medium 置信度标记 ⚠️ 中（建议核实）
- 未匹配的标记 —，说明将跳过事前申请关联
- **只有全部都是 high 且用户已在 Step 1C 确认过 → 可以静默跳过本展示直接继续**
- medium 或 low 出现时**必须展示并等用户确认**

---

## Step 2.5: 获取报销单工作流ID

通过 `invoice.reim.workflow.resolve` 获取。

**⚠️ 核心逻辑：当存在多个工作流时，需要将发票/事前申请按工作流分组，每组各创建一个报销单。**

| 场景 | 处理方式 |
|------|----------|
| 有事前申请 → 同一 workFlowId | 创建 1 个报销单 |
| 有事前申请 → 不同 workFlowId | 按 workFlowId 分组，每组各创建一个报销单 |
| 无事前申请 → 候选工作流只有 1 个 | 创建 1 个报销单 |
| 无事前申请 → 候选工作流有多个 | 发票按匹配规则分组，每组各创建一个报销单 |

### 发票 → 工作流匹配规则（按优先级）

1. **事前申请绑定**：发票已匹配到事前申请 → 使用该事前申请对应的 workFlowId
2. **话费专项**：通讯/话费类发票优先匹配 `workFlowName` 含「话费补贴标准审批流程」或「话费报销」的工作流，命中后必须按 [reim-phone-subsidy-rules.md](reim-phone-subsidy-rules.md) 核算
3. **发票费用类型匹配**：用 `expenseType` 与候选 `workFlowName` 做关键词匹配
4. **通用兜底**：归入 workFlowName 含"日常"/"通用"/"报销"的；仍无法区分归入第一个

每组独立执行 Step 3 → 3.5 → 3.6 → 4 → 5，不能省略任何字段。

---

## Step 3: 获取报销单表单字段结构

通过 `invoice.reim.form.structure` 获取。

> **可缓存**：同一 workFlowId 下只需调用一次。

返回 `mainFields`（主表）和 `subTables`（明细表），每个字段含 `fieldId`、`fieldName`、`fieldType`、`single`、`marked`、`options`。

> 完整返回示例见 [reim-api-reference.md](reim-api-reference.md#3-获取报销单表单字段结构)

---

## Step 3.5: 获取发票预填信息（`invoice.reim.row-info`）

通过 `invoice.reim.row-info` 获取。

> **⚠️ 多张发票的 row-info 调用必须并行发起。**

- 入参：`cdzt`=当前用户ID，`requestid`=事前申请ID（无则留空），`invoiceId`=发票ID
- 返回的 `date`、`fysm`、`itinerary`、`subjectId` **在 Step 4 中优先使用**
- 某字段返回空/null → 回退到 AI 推断逻辑

### 交通类发票额外处理

交通类发票（`expenseType` 含交通/出行/打车，或 `consumeContent` 含客运服务费/运输服务，或 `sellerName` 含滴滴/享道等）→ **额外并行调用 `invoice.get`** 获取出发地和目的地。

> 详细精简规则见 [reim-form-fill-rules.md](reim-form-fill-rules.md#地名精简规则)

---

## Step 3.6: 获取当前人员及上级信息

通过 `invoice.reim.employee-superiors` 获取。

> **可缓存**：同一会话只需调用一次。

- `directSuperior.id` → "报销人上级" + "承担人直接上级"（⚠️ 必填。**注意不是 `allSuperiors[0]`** —— `allSuperiors[0]` 是上级链最高层，与直接上级不是同一人）
- `allSuperiors` 全部 `id` 逗号拼接 → "承担人所有上级"（⚠️ 必填）

---

## Step 4: 组装填单结构化 JSON

> **详细填单规则见 [reim-form-fill-rules.md](reim-form-fill-rules.md)**
> **费用科目匹配规则见 [reim-expense-subject-rules.md](reim-expense-subject-rules.md)**
>
> **⚠️ 费用类型（科目）字段必须有值。匹配不到时直接填兜底值 `"100502270000000104"`。**
> **⚠️ 合同编号固定填 `"20260999"`**（除用户当次明确给出别的合同号）：主表 `合同号(100003720000001376)` 不能留空、不能放进 `unable_to_fill`；走快速路径 `template.build`/`auto-prepare` 时同样必须显式传 `contractNo`，否则该字段静默缺失。口径见 [reim-form-fill-rules.md](reim-form-fill-rules.md) 主表字段映射。
> **⚠️ 出差流程相关客户规则见 Step 4.5。**
> **⚠️ 话费补贴 / 话费报销必须遵守 [reim-phone-subsidy-rules.md](reim-phone-subsidy-rules.md)，见 Step 4.6。**

核心结构概览：

```json
{
  "work_flow_id": "报销流程工作流ID（Step 2.5）",
  "mainFormId": "主表formId（Step 3）",
  "request_name": "流程标题",
  "main_fields": [{"fieldId": "...", "value": "...", "fieldName": "..."}],
  "detail_rows": [{"dataIndex": 1, "subFormId": "...", "invoiceId": "...", "fields": [...]}],
  "need_user_confirm": [],
  "unable_to_fill": []
}
```

**关键约束：**
- **发票 vs 相关凭证分类**：`invoiceTypeCode` 为 17/18/57/58 的是相关凭证，不能独立成行，必须与对应发票配对放在同一行明细中
- 每行 `fields` 中有两个 `EinvoiceComponent` 字段：`single=false` 填**发票** `invoiceId`，`single=true` 填**配对凭证** `invoiceId`
- `dataIndex` 从 1 递增，`subFormId` 用「费用明细」表的（按名称定位明细表，**不要机械取 `subTables[0]`** —— 总部费用报销的 `subTables[0]` 是「外包订单」，「费用明细」`100003690000000011` 排第 3）

---

## Step 4.5: 出差流程必须确认相关客户

> **出差报销未拿到用户提供的具体相关客户前，禁止进入 Step 5。**
> 完整规则见 [reim-form-fill-rules.md - 出差流程相关客户](reim-form-fill-rules.md#出差流程相关客户硬拦截)。

简要规则：
- `workFlowName` 或 `requestname` 含「差旅」「出差」→ 暂停，提醒用户提供具体客户名称
- 用户给出客户名称 → `invoice.reim.field.search` 搜索 ID → 填入主表和明细
- 用户拒绝 / 不提供 → **结束报销，禁止调用 `invoice.reim.flow.create.prepare`**
- 非出差流程：相关客户固定填 `"100504500000311504"`

---

## Step 4.6: 话费补贴 / 话费报销必须按月度标准核算

> **命中「话费补贴标准审批流程」或「话费报销」时，未齐备账单材料和岗位标准前，禁止进入 Step 5。**
> 完整规则见 [reim-phone-subsidy-rules.md](reim-phone-subsidy-rules.md)。

简要规则：
- `workFlowName` 或事前申请名称含「话费补贴标准审批流程」「话费报销」，或用户明确说话费报销 → 先暂停
- 必须提供本人实名制当月手机账单截图及账单构成
- 必须确认岗位对应月度上限（350 / 200 / 100），禁止猜测岗位
- 剔除手机设备赠送套餐、家庭宽带套餐后，实报金额 = `min(可报销账单金额, 上限)`
- 低于标准按实际支付，超过上限按上限支付
- 材料不齐 / 岗位未确认 / 用户拒绝 → **结束报销，禁止调用 `invoice.reim.flow.create.prepare`**

---

## Step 4.7: 预览展示规则 —— 字典类 ID 必须带中文名

> **向用户展示单据预览、汇总、确认清单时，凡是字典/选择类 ID 值，一律渲染成 `中文名(ID)`，禁止只给裸 ID。**
> 用户要靠中文名核对金额、科目、上级和客户；裸 ID 无法复核，属于无效展示。

### 优先：直接用 CLI 已渲染好的展示字段（快速路径 / `auto-prepare` / `template.build`）

`invoice.reim.template.build` 与 `invoice.reim.flow.create.auto-prepare` 的返回已包含渲染完成的展示数据。**返回里有 `preview.mainFields` / `labels` 就直接用，不要再自己调 `field.search` / `row-info` 查名。**

| 返回字段 | 内容 | 怎么用 |
| --- | --- | --- |
| `preview.mainFields[]` | `{ fieldId, fieldName, value \| optionValue, text }` | **主表预览直接读 `text`**。人员/客户渲染成 `温明刚(6490972696771260615)`；选择类渲染成 `银行（个人报销）(optionValue=7)`；逗号列表（承担人所有上级）逐项带名 |
| `preview.detailRows[]` | `{ dataIndex, invoiceId, invoiceNumber, amount, expenseNote, subject, currency }` | **明细表预览直接读 `subject` / `currency`**，已带中文名 |
| `labels` | `employees` / `subjects` / `currencies` / `customers` / `selectOptions` / `customer` / `detailSubForm` / `workflow` | 需要自己拼其它展示时取字典 |
| `labels.unresolved`、`preview.unresolvedLabels` | 未取到中文名的 ID 清单 | 非空时按下方兜底口径如实展示，并放进 `need_user_confirm` 提醒用户核对 |

相关客户只给名称也能用：传 `relatedCustomerName`（不传 ID 时 CLI 会自动反查 ID；ID 与名称同时传则不额外请求，只用于渲染）。

### 兜底：返回里没有上述字段时（旧版 CLI、或手工组装路径）按来源表自查

| 展示项 | 中文名来源 | 兜底 |
| --- | --- | --- |
| 费用类型（科目） | `invoice.reim.row-info` 的 `subjectName`（与 `subjectId` 同源，**同一行数据直接取**） | 用 `reim-expense-subject-rules.md` 查找表反查；仍无则保留 `未知科目(ID)` |
| 币种 | `invoice.reim.row-info` 的 `bz[].name` | `人民币(100001050000000001)` |
| 申请人 / 提单人员 / 承担主体 | `invoice.reim.employee-superiors` 的 `currentEmployee.name` | — |
| 报销人上级 / 承担人直接上级 | 同命令 `directSuperior.name` | — |
| 承担人所有上级 | 同命令 `allSuperiors[].name`，按原顺序逗号拼接，**每个都带 ID** | — |
| 报销方式等 Select 字段 | `invoice.reim.form.structure` 主表该字段 `options` 里 `optionValue` → `optionName` | 保留 `optionValue=7` |
| 相关客户 | `invoice.reim.field.search` 返回项的 `name` | 见下方警告 |

⚠️ **相关客户无法用 ID 反查**（实测）：`invoice.reim.field.search` 把待查的那个 ID 当 `keywords` 传，一律返回 `[]`（例如 `keywords="100504500000311504"` → 空）。必须改用**关键词模糊搜索**再按 `id` 匹配：

```text
keywords="泛微"  →  命中 {"name":"泛微上海","id":"100504500000311504"}
```

关键词取不准时按 2-3 个候选词依次试（公司字号、简称）；仍查不到就显示 `未知来源(100504500000311504)` 并放进 `need_user_confirm` 让用户核对，**禁止编造名称**。

展示格式示例：

```markdown
| 项目 | 值 |
| --- | --- |
| 相关客户 | 泛微上海(100504500000311504) |
| 报销人上级 / 承担人直接上级 | 温明刚(6490972696771260615) |
| 承担人所有上级 | 熊学武(8005823778783571762), 章宏武(4270809363797382452), 周军锋(9080972482706531342), 温明刚(6490972696771260615), 韦利东(8005823776035471761) |
| 报销方式 | 银行（个人报销）(optionValue=7) |
| 费用科目（每行） | 日常消费(1256664958132969489) |
```

纯数值/文本字段（金额、日期、张数、费用说明）保持原样，不加 ID。

---

## Step 5: 生成报销单流程

通过 `invoice.reim.flow.create.prepare` → 用户确认 → `invoice.reim.flow.create.apply` 完成。

> **⚠️ 禁止重复调用：同一组发票数据只能调用一次。调用成功后，修改已创建的报销单使用 Step 6 的 update。**
> **⚠️ 出差流程拦截：相关客户未由用户提供具体信息前，禁止调用。**
> **⚠️ 话费报销拦截：账单截图、账单构成或岗位标准未确认前，禁止调用。**

### 创建成功后

CLI 返回 `requestId` 和 `viewUrl`，**用结构化汇总信息展示给用户**（链接用 CLI 返回的 `viewUrl`，不要自己拼接）：

```markdown
✅ 报销单创建成功！

---

**报销标题**：交通费报销-后端开发111-2026-08-04（共2笔）
**报销事由**：2026-07-30 市内交通 - 滴滴出行
**汇总金额**：¥185.80
**查看链接**：[点击查看报销单](viewUrl)

| # | 发票号码 | 发票金额 | 费用类型 | 发生地点 | 关联凭证 |
|---|----------|----------|----------|----------|----------|
| 1 | 36901189 | ¥108.20 | 市内交通 | 仁济医院南院→浦江瑞和城 | ✅ 已关联 |
| 2 | 36901200 | ¥77.60 | 市内交通 | 虹桥机场T2→人民广场 | ❌ 无凭证 |

---
```

---

## Step 6（可选）: 更新报销单流程

通过 `invoice.reim.flow.update.prepare/apply` 完成。

- 支持 `deleteDetailRows` + `main_fields` + `detail_rows` 三种操作组合
- 删除先于更新执行，删除失败不阻断更新

---

## 异常处理

**需暂停询问用户的情况：**
- 发票列表为空 → 提示"未找到未报销的发票"，结束
- 出差/差旅流程缺少相关客户 → 见 Step 4.5
- 话费报销缺少账单截图、账单构成或岗位标准 → 见 Step 4.6
- 模糊搜索返回多结果 → 放入 `need_user_confirm` 让用户选择

**严禁重复调用：**
- **`create.apply` 已调用成功 → 严禁再次调用，后续修改一律使用 `update`**

**自动继续（不问用户）：**
- 事前申请为空 / 匹配失败 → 跳过事前关联，直接用发票填单
- 匹配结果唯一 / 模糊搜索唯一结果 → 直接使用

**用户中途取消：**
- 用户说"取消"/"不报了"/"算了" → 立即停止
- 已调用 create 成功 → 告知用户可通过链接手动删除

---

## 参考文档

- [reim-api-reference.md](reim-api-reference.md) - 所有 CLI operation 入参与返回值
- [reim-matching-rules.md](reim-matching-rules.md) - 发票与事前申请匹配逻辑
- [reim-form-fill-rules.md](reim-form-fill-rules.md) - 表单字段填充策略与填单 JSON 组装规则
- [reim-expense-subject-rules.md](reim-expense-subject-rules.md) - 费用科目自动匹配规则（JSON 查找表）
- [reim-phone-subsidy-rules.md](reim-phone-subsidy-rules.md) - 话费补贴 / 话费报销月度标准与实报金额
- [reim-examples.md](reim-examples.md) - 完整端到端示例
