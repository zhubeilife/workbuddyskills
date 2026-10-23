# 发票输出投影与渲染（--format / --view / --fields）

## 什么时候读取

用户要**查询票夹、看发票清单、按条件筛票**，或者需要把发票列表交给用户阅读时读取本文件。

不读本文件的场景：写操作（导入/新增/编辑/删除/报销填单）——这些按各自 reference 处理；单张发票详情见 `invoice-detail.md`。

## 三层出口：渲染档 / 语义视图 / 点路径投影

| 出口 | 用途 | 输出形态 |
|---|---|---|
| `--format markdown` | **要在对话里展示给用户时首选** | markdown 文本（表格/卡片），非 JSON |
| `--view summary`（列表）/ `--view detail`（`invoice.get`） | 要给程序消费的语义化数据 | JSON envelope，字段口径已固化 |
| `--fields a,b.c` | 精确控制字段或用于无视图的 operation | JSON envelope，保持原嵌套 |

三者的取舍：**给人看 → `--format markdown`；给下游代码看 → `--view`；只在特殊字段需求下才用 `--fields`。**

## 为什么需要投影

`invoice.list` / `invoice.enterprise.list` 的默认输出是**面向程序的完整包络**：单条发票 40+ 字段（`custom_field_*`、`oa`、`suser`、`rb`、`agricultural_*` 等），10 条约 35KB，而真正要看的只有 8 个字段（约 3KB）。

**不要**因此自己现写解析脚本，也不要把完整 JSON 贴给用户。CLI 已原生提供上面三层出口。

## 首选展示：`--format markdown`

一次调用直接得到可读表格，列顺序、千分位、票种简称、挂单状态都已内置：

```bash
weaver-work-cli invoice list --format markdown
weaver-work-cli invoice get --fid 1310817108299735054 --format markdown
```

票夹列表渲染为标题行（票夹口径 + 总数 + 合计金额）+ 8 列表格；发票详情渲染为「标头 + 字段表」（含附件、费用说明、开票人、查验标记）。

规则：

- **自带字段口径**，不必也不能再传 `--view`（`invoice.list` 固定 summary、`invoice.get` 固定 detail）；传了不一致的视图返回 `validation/input_conflict`
- **与 `--fields` 互斥**（要自定义字段就用 `--fields` 出 JSON）
- **与全局 `--json` 互斥**：markdown 是渲染档不是数据档，同时传返回 `validation/input_conflict`，提示去掉 `--json`
- 只支持 `invoice.list` / `invoice.enterprise.list` / `invoice.get`；其他 operation 返回 `validation/format_unsupported`
- 仍要自行拼表时用下面的 `--view`，不要退回完整 JSON

### 拿到输出后怎么展示：贴进正文，别包代码围栏

`--format markdown` 产出的是 **markdown 源码字符串**，表格、加粗、可点链接都要靠消费端的 markdown 渲染器解析。因此 Agent 拿到后要把它**作为消息正文原样输出**：

- **不要用代码围栏（三个反引号）包裹**：围栏的语义是「原样照录、不解析」，包上就退化成等宽纯文本 —— 发票号码的链接变死文本、表格散架，等于把渲染档降级回 plaintext。
- **不要改写、不要重新拼表**：CLI 给的就是成品，转录要保真；别自行加反斜杠转义（把 `*` 写成 `\*`）、别调整字符或列顺序。
- 在终端里直接执行只能看到源码，这属正常；要预览渲染效果，用支持 markdown 的客户端（浏览器、聊天界面），或在本地用 markdown 渲染器（如 `glow`、`mdcat`）。

## 语义视图：`--view summary`（列表）/ `--view detail`（详情）

`--view summary` 给出语义平表，字段口径与 `invoice.reim.candidates.list` 的 items 一致。

字段集（**省略空值**，所以某条票可能少几个键）：

| 字段 | 含义 |
|---|---|
| `fid` | 发票主键，也是详情页跳转参数 |
| `number` / `code` | 发票号码 / 代码 |
| `typeName` | 票种名称，如"电子发票（增值税专用发票）" |
| `date` | 开票日期 |
| `amount` / `total` / `taxAmount` | 不含税金额 / 价税合计 / 税额 |
| `buyer` / `buyerTaxNo` | 购买方名称 / 税号 |
| `payer` / `payerTaxNo` | 销售方名称 / 税号 |
| `valid` | 查验状态原始值（`1`=已查验） |
| `status` | 发票状态原始值 |
| `reimState` | 票面 `comm_info.pro.sreim` 原始值，**语义未定义，不要自行解读** |
| `reimRequests` | 关联报销单名称数组，空数组表示未挂报销单 |
| `fileName` | 附件文件名 |
| `detailUrl` | 发票详情页链接，展示时必须转成可点击超链接 |

列表级字段：`total`（票夹总数）、`totalAmount`（价税合计）、`totalAmountExcludingTax`、`hasMore`、`scope`、`itemCount`（本次返回张数）。

`--view summary` 只对 `invoice.list` 与 `invoice.enterprise.list` 生效；`invoice.get` 用 `--view detail`（见 `invoice-detail.md`，在 summary 字段上多出 `attachments` / `expenseNote` / `issuer` / `checkState`）。对其他 operation 传视图参数会返回 `validation/view_unsupported`，此时改用 `--fields`、`--format markdown`（若该 operation 有模板）或默认完整输出。

## 备用：`--fields` 点路径投影

需要精确控制字段（例如只要号码和金额），或用于非列表 operation 时使用。点路径按**原始 JSON 结构**书写，输出保持原嵌套形状。

- 作用于 `data.items` 数组时逐项投影，列表级汇总字段（`total` / `hasMore` 等）原样保留
- 作用于其他 operation 时投影 `data` 本身
- 未命中的路径出现在 `meta.projection.missingFields`；**全部**未命中时返回 `validation/field_not_found`
- 与 `--view` **互斥**，同时传返回 `validation/input_conflict`

> ⚠️ **`--fields` 里不要写裸 `total` 取金额。** 发票对象顶层的 `total` 是 E10 的独立字段（实测恒为 `0`），**价税合计在 `comm_info.price.total`**，不含税金额在 `comm_info.price.amount`，税额在 `comm_info.price.dtax`。要金额就用 `--fields comm_info.price.total`，或直接用 `--view summary`（那里的 `total` 已是价税合计）。

三个参数都不属于 operation 的 `inputSchema`，它们只裁剪/渲染输出、不改变任何请求参数，因此不违反"列表查询不支持字段"的白名单校验。
参数错误会在**发起业务请求之前**就返回（`view_unsupported` / `view_invalid` / `format_unsupported` / `format_invalid` / `input_conflict`），不会先打一次网络请求；只有 `field_not_found` 需要拿到结果才能判断。

## 回执：`meta.projection`

投影过的响应会在 `meta.projection` 里说明本次裁剪：

```json
{
  "meta": {
    "status": "COMPLETE",
    "projection": { "view": "summary", "omittedEmpty": true }
  }
}
```

出现 `missingFields` 说明字段名写错了，按提示改正后重试，不要在缺失字段上继续加逻辑。

## 兜底：CLI 版本低于 0.1.17

旧版 CLI 没有 `--view` / `--fields` / `--format`（可用 `weaver-work-cli --version` 确认）。此时用随本 reference 提供的脚本 `invoice-summarize.py`，字段口径与 `--view summary` 完全一致：

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json invoice list > list.json
python3 ~/.workbuddy/skills/weaver-e10-yepiaotong/references/invoice-summarize.py list.json
python3 ~/.workbuddy/skills/weaver-e10-yepiaotong/references/invoice-summarize.py list.json --format table
weaver-work-cli --json invoice list | python3 ~/.workbuddy/skills/weaver-e10-yepiaotong/references/invoice-summarize.py -
```

Windows PowerShell：

```powershell
weaver-work-cli --json invoice list | Out-File -Encoding UTF8 list.json
python "$env:USERPROFILE\.workbuddy\skills\weaver-e10-yepiaotong\references\invoice-summarize.py" list.json
python "$env:USERPROFILE\.workbuddy\skills\weaver-e10-yepiaotong\references\invoice-summarize.py" list.json --format table
```

脚本要求 Python 3，只用标准库；输入接受完整 envelope、`data` 对象、`{items:[...]}` 或 E10 原生 `{infos:[...]}`；`--format table` 输出 markdown 表格，适合直接贴给用户。

## 注意事项

- **发票号码必须用 `detailUrl` 渲染成可点击超链接**，格式为 `[号码](detailUrl)`；`--view summary` 已保留该字段，`--fields` 时记得把它列进字段表，否则详情链接会丢失。
- 需要完整票面字段（`ext` 里的商品明细、`flist` 附件列表等）时不要用投影，走 `invoice.get`。
- 统计金额以 `totalAmount` / `totalAmountExcludingTax` 为准，不要用单条 `total` 相加去"复核"服务端汇总——两者口径可能不同（作废票、红冲票的处理方式未在契约中定义）。
- `reimState` 与列表筛选参数 `sreim` **不是同一套语义**：`sreim` 是筛选入参（`"0"`=全部、`"1"`=报销中、`"2"`=报销完成、`"3"`=未报销、`"4"`=不可报销），而票面 `comm_info.pro.sreim` 的取值含义未在 CLI 契约里定义，只能原样呈现。
