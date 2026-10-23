# B 端页面验证表

本表只用于为 MCP 查询结果找到人工复核入口，不定义指标，也不替代运行时 Schema。

## 环境地址

- 测试环境：`https://home.test.fanzhi.cn`
- 正式环境：`https://home.fanzhi.cn`

报告中不要只显示下表的相对路由。不含对象标识的页面可分别与两个环境域名组合，输出两个可点击的 Markdown 链接；实际复核只能使用与 MCP 数据相同的环境：

| 复核对象 | 测试环境 | 正式环境 | 等级 | 需保持一致的筛选条件 |
|---|---|---|---|---|
| 当月销售总览 | [打开测试环境](https://home.test.fanzhi.cn/stat/finance/sale) | [打开正式环境](https://home.fanzhi.cn/stat/finance/sale) | B 业务对象可对照 | 店铺、期间、时间基准 |

含 `:projectId`、`:incrementId` 或其他占位符的路由，必须先用已在对应环境确认的真实值替换再生成链接；不能把测试标识直接套入正式环境，反之亦然。另一环境未确认对象时写“需先确认对象”，不得输出占位链接。不能仅凭页面已登录或两个环境的 ID 相同认定是同一数据。

## 对应等级

- **A 直接对应**：后端实现按现有 B 端页面接口复刻，已有字段级联调记录。同环境、同范围及筛选条件一致时，可逐字段核对；历史联调不是本次数据已一致的证明。
- **B 业务对象可对照**：页面查看的是同一业务对象，但接口、字段集合或聚合粒度不完全相同。只核对双方共有字段。
- **C 暂无直接页面**：B 端没有一张能直接对应当前结果的页面。报告中不要写“与 B 端一致”。

## 能力与页面

页面状态最后实查于 2026-09-18，环境为测试 B 端当前登录店铺。标为“当前账号无权限”的页面只确认了前端路由与接口代码，不能写成已实页核对。

| MCP 能力 | B 端页面/路由 | B 端接口 | 等级 | 页面状态 |
|---|---|---|---|---|
| `mcp_access_context_list` | 无直接业务页面 | OAuth 授权上下文 | C | 无页面 |
| `project_search` | 项目管理 `/project/base` | `GET business/project/base/items` | B | 已进页面 |
| `project_report` | 销售报表 `/stat/finance/sale` | `GET business/finance/report/sale` | B | 当前账号无权限 |
| `project_sales_ranking` | 无单独排行页面 | 无直接接口 | C | 无页面 |
| `project_refund_ranking` | 无单独排行页面 | 无直接接口 | C | 无页面 |
| `project_channel_sales_report` | 无同粒度页面 | 无直接接口 | C | 无页面 |
| `project_verification_report` | 项目-核销报表 `/project/base/item/:projectId/reportwriteoff` | `GET business/project/report/verifyTicket` | B | 当前账号无权限；订单“核销记录”不是同口径页面 |
| `project_screening_verification_report` | 项目-核销报表 `/project/base/item/:projectId/reportwriteoff` | `GET business/project/report/verifyTicket` | B | 当前账号无权限；订单“核销记录”不是同口径页面 |
| `project_sku_sales_report` | 项目-销售报表 `/project/base/item/:projectId/reportsale` | `GET business/project/report/sale?v=2` | A | 已进页面 |
| `project_ticket_type_report` | 项目-出票报表 `/project/base/item/:projectId/reportout` | `GET business/project/report/saleTicket?v=2` | A | 已进页面 |
| `project_channel_sku_report` | 项目-渠道报表 `/project/base/item/:projectId/reportchannel` | `GET business/project/report/saleChannel` | A | 已进页面 |
| `project_stock_get` | 项目-场次票档 `/project/base/item/:projectId/screen/ticket` | 未核对 | B | 仅确认前端路由（2026-09-25），未实页核对；余票为实时值，页面刷新前后可能不同 |
| `trade_search` | 订单管理 `/order/base` | `GET business/trade/order/items` | B | 已进页面 |
| `trade_get` | 订单详情 `/order/base/detail/:incrementId` | `GET business/trade/order/item` | B | 已确认详情入口 |
| `ticket_verification_get` | 核销记录 `/order/more/writeoff`、订单详情 `/order/base/detail/:incrementId` | 未核对 | B | 仅确认前端路由（2026-09-25），未实页核对 |
| `trade_filter_options` | 订单管理 `/order/base` 筛选区 | `GET business/trade/order/config` | A | 已进页面 |
| `trade_order_summary` | 订单管理 `/order/base` 汇总区 | `GET business/trade/order/summary` | A | 已进页面，显示订单总金额、支付总金额、订单总数、销售票数、退款金额、退款票数 |
| `sdp_distribution_order_summary` | 分销订单 `/channel/foreigner/distributors/order` | `GET business/sdp/order/summary` | A | 已进页面，显示销售金额、订单总数、销售票数、佣金等汇总 |
| `channel_sales_stat_project_list` | 渠道销售统计 `/stat/data/channel` | `POST business/tongji/channel-sale/projects` | A | 已进页面 |
| `channel_sales_stat_project_detail` | 渠道销售统计 `/stat/data/channel` 项目下钻 | `POST business/tongji/channel-sale/project/detail` | A | 已确认同页项目下钻 |
| `channel_sales_detail_project_list` | 渠道销售明细 `/stat/data/sale_detail` | `POST business/tongji/channel-sale-detail/projects` | A | 已进页面 |
| `channel_sales_detail_project_detail` | 渠道销售明细 `/stat/data/sale_detail` 项目下钻 | `POST business/tongji/channel-sale-detail/project/detail` | B | 已确认同页项目下钻；线上同票档多销售员的合并方式有实现差异，不保证逐字段一致 |
| `channel_ticket_stat_project_list` | 渠道出票统计 `/stat/data/channel_ticket` | `POST business/tongji/channel-ticket/projects` | A | 已进页面 |
| `channel_ticket_stat_project_detail` | 渠道出票统计 `/stat/data/channel_ticket` 项目下钻 | `POST business/tongji/channel-ticket/project/detail` | A | 已确认同页项目下钻 |
| `finance_flow_search` | 票务交易账单 `/stat/finance/trade`、详情 `/stat/finance/trade_detail/:productId` | `business/finance/report/tradeList`、`tradeDetail`、`tradeTotail`、`config` | B | 已进账单页面 |
| `fanzhi_service_fee_report` | 无单一对应页面 | 无直接接口 | C | 无页面 |
| `refund_overview_report` | 退款订单 `/order/base/refund` | 未核对 | B | 仅确认前端路由（2026-09-25），未实页核对；口径按退款申请时间、含全部状态，与后台退款列表同源，但分布与汇总是 MCP 自行聚合 |
| `sales_report` | 销售报表 `/stat/finance/sale` | `GET business/finance/report/sale` | B | 当前账号无权限；不要替换成 `/stat/data/sales` |
| `sales_monthly_trend` | 销售报表 `/stat/finance/sale` | `GET business/finance/report/sale` | B | 当前账号无权限；不要替换成 `/stat/data/sales` |
| `member_search` | 会员列表 `/member/list` | `GET business/member/base/itemsV2` | B | 已进页面 |
| `member_get` | 会员详情 `/member/list/detail/:id` | `GET business/member/base/item/:id` | B | 已进页面 |
| `member_profile_report` | 无直接页面 | 无直接接口 | C | 无页面 |
| `member_insight_report` | 无直接页面 | 无直接接口 | C | 无页面 |

## 报告自检规则

1. 先确认页面与 MCP 数据环境一致，再以响应中的店铺、项目、时间字段、起止时间和筛选条件还原页面筛选；列表核对还需对齐分页或全量范围。
2. A 级逐字段核对；B 级只核对双方同名且业务含义一致的字段；C 级只保留 MCP 结果与数据状态。
3. 页面筛选无法还原、页面接口没有该字段或数据更新时间不同，都不能判定为数据错误。
4. 自检记录只写事实：MCP 值、页面值、双方筛选条件、双方数据时间和是否一致。原因必须有接口字段或后端说明支持，否则写“原因待核实”。
