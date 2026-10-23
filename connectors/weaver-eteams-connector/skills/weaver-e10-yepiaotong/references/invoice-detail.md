# 查看发票详情

## 什么时候读取

用户给出 `fid`、发票号码，或需要查看完整票面、附件、可编辑状态、可删除状态时读取本文件。

## Operation

| Operation | 固定规则 |
| --- | --- |
| `invoice.get` | 优先用 `fid`；没有 `fid` 时可用 `number` 查询 |

## 要展示给用户时：`--format markdown`（首选）

```bash
weaver-work-cli invoice get --fid 12345 --format markdown
weaver-work-cli invoice get --number 26342000002783695141 --format markdown
```

用户直接给发票号码时，**不必先查列表**：`invoice get --number <号码> --format markdown` 可一次拿到同样的标头 + 字段表（已实测 0.1.20 可用）。

直接得到「标头 + 字段表」的 markdown：标头是 `**[发票号码](详情链接)** · 票种`（**号码本身即可点击**，直达 E10 发票详情页，不再单列 `[打开详情]` 行），字段表首两行固定为 `发票号码`（同一链接）与 `发票代码` —— 票面标识必须在「项目」列里可核对、可复制；数电票（全电发票）没有发票代码，如实显示 `—`，不要伪造。其后依次是开票日期、不含税金额、税额、价税合计、购销方、费用说明、开票人、查验标记、报销挂单、附件。**不要**再自己拼这些行；贴给用户时把这整段作为消息正文直接输出，不要用代码围栏包裹（包上会退化成纯文本，号码链接失效）。

需要给下游代码读时用 `--view detail`：语义字段平表（`data.items[]`），比 summary 多出 `attachments`（附件清单）、`expenseNote`（费用说明）、`issuer`（开票人）、`checkState`（查验标记，`0`=未做过查验登记，**与票面 `valid` 不是一个口径，不要混读**）。

```bash
weaver-work-cli --json invoice get --fid 12345 --view detail
```

`--view detail` 只对 `invoice.get` 生效；`--format markdown` 与 `--json`、`--fields` 互斥（返回 `validation/input_conflict`）。

## 示例

Windows PowerShell：

```powershell
weaver-work-cli --json invoice run invoice.get --input-json '{"fid":"12345"}'

weaver-work-cli --json invoice run invoice.get --input-json '{"number":"00188205"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json invoice run invoice.get --input-json '{"fid":"12345"}'

weaver-work-cli --json invoice run invoice.get --input-json '{"number":"00188205"}'
```

## 返回

`invoice.get` 返回服务端详情响应本身。每条 `infos[]` 项包含 `detailUrl`（如 `https://xxx/sp/inc/incDetail?fid=<fid>`），用于生成可点击的发票详情链接。常见字段包括 `infos[].info.fid`、`code`、`number`、`comm_info.pro`、`comm_info.price`、`comm_info.buyer`、`comm_info.payer`、`flist` 和 `modify_info`。交通类发票还可从 `infos[].info.from` / `infos[].info.to`（或 `ext.passengersService`）取出发地和目的地。

向用户展示发票详情时，**发票号码必须用 markdown 链接格式** `[号码](detailUrl)` 展示，让用户点击直接打开发票详情页。

## 注意

用户已经给出 `fid` 时不要先查列表再过滤。找不到或无权查看时按失败 envelope 处理，不要自动扩大数据范围。
