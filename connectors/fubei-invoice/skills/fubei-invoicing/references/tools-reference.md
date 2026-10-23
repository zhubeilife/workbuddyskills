# 付呗智能开票 MCP · 工具参数速查（v1.0.1，共 11 个工具）

> 商户身份一律来自 OAuth 授权凭证上下文，所有工具入参均不携带商户标识；但**商户号（subMchid）除外**——登录商户关联多个商户号时，开票前须由商户选择并通过 `issue_invoice` 的 `subMchid` 参数传入。
> 金额单位：元。状态流转：SUBMITTED → INVOICING → INVOICED / FAIL；红冲后 REVERSED。

## 1. get_auth_status — 查询开票功能状态

无入参。返回 `status`：`enabled` / `not_enabled` / `unknown`（unknown 时放行开票，由网关真实结果判定）；`subMchids`：授权商户的商户号列表（多于 1 个时开票前须让商户选择，见 issue_invoice 的 subMchid）。开票、红冲前应先调用。

## 2. issue_invoice — 开具数电发票

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| subMchid | string | 多商户时必填 | 商户号。`get_auth_status` 返回的 subMchids 只有 1 个时不传（默认该商户号）；多于 1 个时必须传入商户选定的商户号，未传会报错并列出候选 |
| invoiceBillType | enum | 是 | `COMMON_INVOICE` 普票 / `VAT_INVOICE` 专票（专票仅可开给企业） |
| buyerType | enum | 是 | `INDIVIDUAL` 个人 / `ORGANIZATION` 企业 |
| buyerName | string | 是 | 购买方名称（个人为姓名或"个人"；企业为全称） |
| buyerTaxpayerId | string | 企业必填 | 购买方纳税人识别号 |
| buyerAddress / buyerTelephone / buyerBankName / buyerBankAccount | string | 否 | 购买方地址 / 电话 / 开户行 / 账号 |
| buyerEmail / buyerPhone | string | 否 | 接收发票的邮箱 / 手机号 |
| items | array | 是 | 明细行，至少 1 行，见下 |
| personId | string | 否 | 开票人ID，不填取第一位开票员 |
| remark | string | 否 | 发票备注 |
| userApplyMessage | string | 否 | 用户开票留言 |
| transaction | object | 否 | 交易信息（不填默认现金）：payChannel（`OTHER`/`WECHAT_PAY`/`ALIPAY`，必填）、transactionId、outTradeNo、amount |

items 明细行：`goodsName`*（名称）、`taxCode`*（19 位税收分类编码）、`taxRate`*（百分比数值，13 = 13%）、`itemTotalAmount`*（单行含税金额）、quantity（默认 1）、specification、unit、preferentialPolicyCode（3 免税 / 4 不征税）。

成功返回 `invoiceApplyId`（发票申请单号，后续查询/红冲/取文件的主键）。

## 3. query_invoice — 查询发票

`invoiceApplyId`*。返回 applyStatus、invoiceType（BLUE/RED）、invoiceNumber、invoiceTime、totalAmount、buyerName、items、errorCode/errorMessage。

## 4. get_invoice_file — 获取发票文件下载地址

`invoiceApplyId`*（蓝票/红票）。返回 `downloadUrl`（付呗 OSS 托管 PDF，数电发票版式文件）。

## 5. apply_reversal — 红字冲销（不可逆，发起前必须与商户确认）

| 参数 | 必填 | 说明 |
|---|---|---|
| invoiceApplyId | 是 | 原蓝票申请单号 |
| reverseReason | 是 | `ISSUE_ERROR` 开票有误 / `SALES_RETURN` 销货退回 / `SERVICE_SUSPENSION` 服务中止 / `SALES_DISCOUNT` 销售折让 |

返回 `reverseInvoiceApplyId`。已冲红重复发起返回 ALREADY_REVERSED。

## 6. query_reversal — 查询红冲进度

`reverseInvoiceApplyId`*。返回红票状态、红票号码、冲红原因。

## 7. get_issue_options — 获取开票基础选项

无入参。返回 taxRates（可用税率）、invoiceTypes（普票/专票）、preferentialPolicies（优惠政策）、reverseReasons（冲红原因枚举）。填表前调用。

## 8. search_tax_code — 搜索税收分类编码

`keyword`（名称关键词，如：餐饮、住宿、汽油）。返回候选列表（编码+名称+简称），供商户确认后填入 issue_invoice 的 taxCode。

## 9. list_billing_persons — 查询开票员列表

无入参。返回商户配置的开票员（personId、personName）。

## 10. list_invoices — 查询最近开票列表

| 参数 | 说明 |
|---|---|
| days | 最近 N 天（默认 30） |
| startDate / endDate | yyyy-MM-dd，含当日；同时提供时以 startDate 为准 |
| status | SUBMITTED / INVOICING / INVOICED / FAIL / REVERSED |
| buyerName | 购买方名称模糊过滤 |
| page / pageSize | 默认 1 / 20，最大 100 |

返回 invoices[]（含 invoiceApplyId、invoiceType、status、invoiceNumber、totalAmount、buyerName、goodsSummary）+ summary 合计。仅覆盖通过本 MCP 开具的发票。

## 11. get_invoice_form — 获取开票表单链接

无入参。返回 `formUrl`（一次性 H5 表单，15 分钟内有效，提交一次即失效）与 `subMchids`（商户号列表；多于 1 个时表单页顶部渲染商户号选择，由商户自行勾选）。表单页含税收分类编码可搜索下拉（内置官方编码表 3558 条）、税率/发票类型真实选项、自动算价税合计。适用于要素多、商户或顾客自行填写的场景。
