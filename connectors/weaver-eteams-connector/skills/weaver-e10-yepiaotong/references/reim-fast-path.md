# 报销快速路径（0.1.13 新增 operation）

> 三个新 operation 把「查票 → 分类 → 组 payload → prepare」压成两步，人工只保留确认 + apply。
> 固化映射来自 2026-09-14 / 2026-09-21 两次真实 apply 成功的「总部费用报销」单据，只覆盖该流程。

## 1. `invoice.reim.candidates.list`（read）— 票夹候选分类

自动翻页拉取未报销（sreim=3）发票，并按 `oreim.list_reim` / 红冲状态分成三组，**不再需要手动翻页和逐条剔重**：

macOS/Linux（bash）：

```bash
weaver-work-cli --json invoice run invoice.reim.candidates.list --input-json '{"date_begin":"2026-09-14","date_end":"2026-09-21"}'
```

Windows PowerShell：

```powershell
weaver-work-cli --json invoice run invoice.reim.candidates.list --input-json '{"date_begin":"2026-09-14","date_end":"2026-09-21"}'
```

- 入参（全部可选）：`date_begin`/`date_end`（YYYY-MM-DD，开票日期范围）、`page_size`（10-200，默认 50）、`max_items`（1-500，默认 200，超出截断并产生 warning）、`include_red_reversed`（默认 `false`）。
- **红冲票默认已过滤**：全额红冲发票（`status=8`）不可报销，默认**不出现在结果里任何一组**，被过滤的张数由 `summary.filteredRedReversedCount` 告知（不会静默丢弃）。需要看红冲票时传 `include_red_reversed: true`，此时它们进 `redReversed` 组。
- 过滤发生在翻页循环内部：即使某一页全是红冲票也会继续翻页，直到凑够 `max_items` 张**可用**发票或数据取完，因此 `fetched` 只计保留下来的发票数、`total` 仍是接口返回的符合条件的总张数。
- 输出：`available` / `assigned` / `redReversed` 三组（后一组默认恒为空），每组元素含 `fid`、`number`、`date`、`total`、`buyer`、`payer`、`typeName`、`status`、`valid`、`reimRequests`；`summary` 给出三组的张数与金额合计，外加 `filteredRedReversedCount`；`warnings` 含截断与金额解析告警。
- **报销范围永远从 `available` 里选**；`assigned` 是已挂单的（重复提交 = 重复报销）。
- **⚠️ 关于"两次连续查询之间 assigned↔available 翻转"（2026-09-21 已定位，结论：分类是准的，不是误判）**：同一天内观察到 25 张发票从 `assigned` 翻到 `available`，一度被怀疑是 `oreim.list_reim` 缓存滞后。最终用 `workflow.detail` 逐个复核 requestId 后定案：`1313947830149185538`（报销单 2026-09-11）、`1314910388070170941`（2026-09-14）、`1317591500119752761`（当天新建）**均返回"流程已被删除"**，10+15+2 张发票随之释放。⇒ **翻转的根因是报销单被删除，发票真实释放，`candidates.list` 的三分类如实反映了状态变化。**
  - **因此不要每次报销都对每张入选票再跑一次 `invoice.get` 复核 `oreim.list_reim`** —— 那会让快速路径失去意义。只有在**观察到异常翻转**（或对某张票的归属存疑）时才做核实，正确顺序是：`weaver-work-cli workflow run workflow.detail --input-json '{"requestId":"<id>"}'` 查单据是否还存在（被删的单会明确返回"流程已被删除"）→ 再用 `invoice.get` 看 `oreim.list_reim`。
  - **已知局限**：`list_reim` 元素只有报销单**名称**（无 requestId、无单号、无单据状态），`reimRequests` 里拿不到能直接喂给 `workflow.detail` 的 id。要核实只能先按名称用 `workflow.search` 找 requestId —— 注意**被删除的单在 `workflow.search` 里搜不到**，这本身就是一个"单可能已被删"的信号，但无法区分"从未存在"与"已被删除"。
  - 另一个易踩点：`sreim="3"`（未报销）**不会**把挂单中的发票排除掉（实测 13 张挂单票仍出现在 `sreim=3` 的 39 张结果里），所以不能靠 `sreim` 判断是否已挂单，分类必须看 `list_reim`。

## 2. `invoice.reim.template.build`（read）— 固化模板组装 payload

输入发票 ID 列表 + 标题，一条命令产出完整 `payload`（19 个主表字段 + N 行明细）。内部自动完成：取上级（`directSuperior`）→ 解析候选工作流（或用传入 `workflowId`）→ 取表单结构并**按名称定位「费用明细」子表** → 批量取发票详情与行预填。

macOS/Linux（bash）：

```bash
weaver-work-cli --json invoice run invoice.reim.template.build --input-json '{"invoiceIds":["1317524773561163780","1317524747581644831"],"requestName":"烧烤调料及托盘采购报销-龚为明-2026-09-21（共2笔）","relatedCustomerId":"100504500000311504","contractNo":"20260999"}'
```

Windows PowerShell：

```powershell
weaver-work-cli --json invoice run invoice.reim.template.build --input-json '{"invoiceIds":["1317524773561163780","1317524747581644831"],"requestName":"烧烤调料及托盘采购报销-龚为明-2026-09-21（共2笔）","relatedCustomerId":"100504500000311504","contractNo":"20260999"}'
```

- 入参：`invoiceIds`（必填，1-100 个，顺序 = 明细行顺序）、`requestName`（必填，≤100 字）；可选 `workflowId`（不传则自动解析唯一候选流程）、`reason`（报销事由，缺省用 requestName）、`relatedCustomerId`、`relatedCustomerName`、`contractNo`（**默认值 `"20260999"`，视为必传**）。
- **⚠️ `contractNo` 默认填 `"20260999"`，不能省略**：主表 `合同号(100003720000001376)` 只有在入参给了 `contractNo` 时才写进 `payload.main_fields`（不传时该字段**整条缺失**，实测同一票同参数：不传 18 个主表字段，传 `"contractNo":"20260999"` 后 19 个），报销单里它会留空**且 `warnings` 不会提示**，属于静默漏填。
- **默认值口径与 [`reim-form-fill-rules.md`](reim-form-fill-rules.md) 的主表字段映射表一致**：合同编号 = 固定值 `"20260999"`。**除非用户明确给出别的合同号，否则一律填 `"20260999"`** —— 快速路径也必须遵守这条，不能因为「入参可选」就留空。
- 用户另有指定时以用户指定为准；用户明确说"不填合同号"时才允许留空。
- 输出：`payload`（可直接喂给 `flow.create.prepare` / apply）、`preview`、`labels`、`warnings`。
  - `preview.mainFields[]` / `preview.detailRows[]`：**已把字典类 ID 渲染成「中文(id)」，预览直接展示这两项即可，不必再查名**（详见 `reim-workflow.md` Step 4.7）。
  - `labels`：`employees` / `subjects` / `currencies` / `customers` / `selectOptions` / `customer` / `detailSubForm` / `workflow` 字典；`labels.unresolved` 为没取到中文名的 ID 清单，非空时如实展示并提醒用户核对。
  - 相关客户只给名称也行：传 `relatedCustomerName`（不传 ID 时 CLI 反查 ID；ID + 名称同传则不额外请求，仅用于渲染）。
- 行为细节（与 2026-09 实测口径一致）：
  - 报销人上级 / 承担人直接上级 = `directSuperior.id`（**不是 allSuperiors[0]**）；承担人所有上级 = allSuperiors 全部 id 逗号拼接。
  - 费用明细子表优先按名称「费用明细」匹配，兜底按「相关发票」字段结构签名匹配。
  - 费用说明自动去掉 `*`；科目缺省「日常消费」；币种人民币；报销方式银行（optionValue "7"）。
  - 发票已挂单 → warning；发票全额红冲（status=8）或金额合计为 0 → **直接报错拒绝组装**。
  - `relatedCustomerId` 不传会留空并产生 warning（E10 apply 时可能因必填校验失败，非出差场景建议传）。
- 模板只固化了「总部费用报销」(`100003460000000060`) 的字段映射。若解析到的候选流程不是它，字段映射可能不适用 —— 此时**改走 `reim-workflow.md` 的手工组装路径**。

## 3. `invoice.reim.flow.create.auto-prepare`（read-before-write）— 一站式 prepare

与 `template.build` 相同的入参，组装 payload 后**直接签发 `flow.create.apply` 的 continuation**，一步到 `AWAITING_CONFIRMATION`：

macOS/Linux（bash）：

```bash
weaver-work-cli --json invoice run invoice.reim.flow.create.auto-prepare --input-json '{"invoiceIds":["1317524773561163780","1317524747581644831"],"requestName":"烧烤调料及托盘采购报销-龚为明-2026-09-21（共2笔）","relatedCustomerId":"100504500000311504","contractNo":"20260999"}'
```

Windows PowerShell：

```powershell
weaver-work-cli --json invoice run invoice.reim.flow.create.auto-prepare --input-json '{"invoiceIds":["1317524773561163780","1317524747581644831"],"requestName":"烧烤调料及托盘采购报销-龚为明-2026-09-21（共2笔）","relatedCustomerId":"100504500000311504","contractNo":"20260999"}'
```

输出含 `payload` + `preview` + `labels` + `continuation` + `expiresInSeconds: 600`。**用户确认后**，把 payload 的字段**展开到顶层**（即 `work_flow_id` / `mainFormId` / `request_name` / `main_fields` / `detail_rows` / `need_user_confirm` / `unable_to_fill`），再补 `continuation` 与 `confirm: true`，交给 `invoice.reim.flow.create.apply` 提交。**不要写成 `{"payload": {...}, "continuation": ...}` 的嵌套结构**（`reim-api-reference.md` 第 7 节已明确「不要再包一层通用 payload」）。

## 推荐流程（快速路径）

```
candidates.list（选 available）
  → 向用户展示汇总并确认范围
  → auto-prepare（或 template.build + flow.create.prepare）  ← 必带 relatedCustomerId + contractNo:"20260999"（用户另有指定时用其值）
  → 展示 preview + warnings（**ID 一律带中文名，见 `reim-workflow.md` Step 4.7**），等用户确认
  → flow.create.apply（展开 payload 到顶层 + continuation + confirm=true）
  → 回查验证（candidates.list 或 invoice.list）
```

人工确认环节不可跳过：apply 是 high-risk-write，金额、抬头、明细、上级必须经过用户核对。

> **apply 入参改用 `--input <path>` 时的解析坑（0.1.18 实测）**：stdout 会在 JSON **之前多出一行** `[weaver-work-cli] 使用 --input <path> 读取 JSON 文件；多步传递请优先用 --input-ref，简单数据请用 --input-json。`。脚本解析必须先定位第一个 `{` 再 `JSON.parse`，直接解析会抛 `Unexpected token 'w'`。

> **continuation 只有 600 秒有效期**：`prepare` / `auto-prepare` 签发后要尽快 `apply`，中间不要插入文档查询、多轮确认或其它耗时命令，否则会返回 `validation/continuation_expired`。遇到过期**重新 `prepare` 后立即 `apply`** 即可（用户已确认过的内容无需重新征询），**不要重放旧 continuation**。

## 快速路径适用判断

Agent 在决定走快速路径还是手工路径时，按以下规则判断：

| 条件 | 走快速路径 | 走手工路径 |
|------|------------|------------|
| `workflow.resolve` 返回的 workFlowId = `100003460000000060`（总部费用报销） | ✅ | — |
| workFlowId 不是 `100003460000000060` | — | ✅ |
| `template.build` 返回 error 含 `structure_invalid` 或字段映射异常 | — | ✅（自动回退） |
| 需要逐字段精细控制（如手动指定某行的费用科目） | — | ✅ |
| 有事前申请需要绑定 | — | ✅（模板不做事前绑定） |
| 无事前申请 + 总部费用报销流程 | ✅（优先） | — |

> **⚠️ 快速路径的 `template.build` 和 `auto-prepare` 已内置挂单检查**：如果某张发票已挂在其他报销单上，`warnings` 会明确告知"继续组装存在重复报销风险"，Agent 应展示给用户确认。

> **⚠️ 0.1.19 起 `contractNo` 默认值**：CLI 未收到 `contractNo` 入参时自动使用 `"20260999"` 并产生 warning，不再静默缺失。但仍建议显式传入以确保意图明确。

## 与手工路径的关系

- `invoice.reim.requests.list`（事前申请匹配）仍按 `reim-matching-rules.md` 走，模板不做事前申请绑定。
- 其他流程（出差报销等）或需要逐字段精细控制的场景，仍走 `reim-workflow.md` / `reim-form-fill-rules.md` 的手工组装路径。
