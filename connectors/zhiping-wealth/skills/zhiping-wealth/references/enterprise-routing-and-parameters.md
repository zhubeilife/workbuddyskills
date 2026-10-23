# 主题路由与参数

## 当前常用路由

实时能力始终以 `zhiping_describe_data_contract` 为准。下表用于避免高频误路由。

| 用户需求 | 首选主题/工具 |
|---|---|
| 产品基础信息、产品筛选 | `basic_info` / `zhiping_search_product_basic_info` |
| 新发、募集起止、发行情况 | `issuance` / `zhiping_query_product_issuance` |
| 成立产品、实际募集规模 | `establishment` / `zhiping_query_product_establishment` |
| 收益率、最大回撤、波动率、夏普等表现 | `nav_metrics` / `zhiping_query_product_nav_metrics` |
| APP 销售名称、货架标签、层级、顺序 | `app_shelf` / `zhiping_query_app_shelf` |
| 代销关系、认购申购、赎回 | `purchase_redemption` / `zhiping_query_purchase_redemption` |
| 固定管理费、托管费、销售服务费等 | `fixed_fee` / `zhiping_query_product_fixed_fee` |
| 基础信息与存续规模 | `balance`，仅走服务端导出 |
| 底层资产分布、底层资产详情 | `underlying_asset`，仅走服务端导出 |
| 非标项目、非标变动或月末规模 | `non_standard_asset` / `zhiping_query_non_standard_assets` |
| 当前产品业绩比较基准 | `benchmark` / `zhiping_query_product_benchmark` |
| 山东农信月度 Excel 与 Word | `zhiping_generate_shandong_rural_credit_monthly_report` |

## 容易混淆的表达

- “某理财公司发行的产品”中的“发行”通常只是发行人范围；没有募集日期、发行数量等要求时不要路由到 `issuance`。
- “成立以来收益率”是收益率窗口，路由到 `nav_metrics`，不是 `establishment`。
- “某银行代销”按实际代销机构筛选，优先传 `distributor_org_names=[银行名称]`；不要替换成其理财子公司、集团或发行机构。
- 同时要求代销产品和产品表现时，使用 `nav_metrics` 的代销机构筛选，由服务端组合；不要分别查询后客户端 Join。
- 同时要求基础信息和存续规模时使用 `balance`；只有用户明确要求指标结果附带测算规模时，才在 `nav_metrics` 使用 `include_estimated_balance=true`。
- 现金管理类是产品分类；只有需求包含对应收益率或万份收益时才启用净值指标现金管理分支。

## 机构范围

- “全市场/所有理财产品”：`all_market=true`，`institution_ids=[]`；不要枚举机构 ID。
- “全部理财公司”：只包含理财子公司分类，不等于全市场；用机构类型检索取得完整 ID 后一次提交。
- 指定发行机构：需要时先调用机构检索，再把全部目标 ID 一次提交。
- 指定代销机构：使用 `distributor_org_names` 或已知 `distributor_org_ids`，不要写入发行机构字段。
- 根据理财发行机构查询代销机构 ID：先用 `zhiping_search_institutions` 解析发行机构 ID，再调用 `zhiping_search_distributors_by_issuer`；结果来自实际代销关系，不推断集团或母子公司关系。
- 超过 20 家指定发行机构仍是一个服务端导出任务，不拆批。
- 货架导出可留空 `sale_agency_ids` 表示全部销售机构，也可一次传入任意数量的指定销售机构 ID；不得按 10 家拆批。请求点名发行机构（如渤银）时，把机构解析为 org_id 写入 `issuer_org_ids` 以收敛查询到该发行产品（与 `sale_agency_ids` 正交，非用户确认项）。

## 参数形成

1. 使用实时工具 Schema 中的字段键，不根据中文名称猜英文参数。
2. 产品维度、统计日期、存续模式、字段范围、排序和唯一键最终必须与确认答案一致。
3. 用户明确列出字段时，将其映射到 `query.fields` 并保留用户要求的顺序；不要留空后导出所有列。
4. 业务字段筛选写入服务端支持的 `filters` 或专用参数，不能先全量取数后客户端筛选。
5. 指标名称只使用数据契约返回的枚举；无法识别时先查询契约，不猜测近似名称。
6. 用户没有给出会改变业务结果的必要条件时先询问；不要用当前日期、最近日期或默认机构静默补齐。

## 底层资产导出

`underlying_asset` 固定使用子产品维度，且只允许通过 `zhiping_get_export_confirmations`、`zhiping_create_export`、`zhiping_get_export_status` 完成服务端导出。不要用在线查询或客户端合并模拟。

- `dimension="sub_product"`。
- `statistic_date="YYYY-MM-DD"` 精确匹配资产统计日，不自动回退到最近日期，也不能晚于当前日期。
- `export_type="prop"|"details"|"both"`；`details` 表示全部资产详情，不是前十。
- `invest_type="direct"|"penetrating"|"both"`。
- `display_mode="merge"|"separate"`；只有同时选择直接和间接投资时才需要确认，`merge` 在同类工作表增加投资方式列，`separate` 分成工作表。
- 机构、产品编码、销售代码、字段和存续范围沿用基础信息参数；未命中资产记录的范围内产品仍保留基础信息行。
- 分布金额、资产成本和资产市值以万元输出并保留 4 位小数；占比沿用数据库百分比原值。

## 组合边界

优先使用服务端原生组合主题。不存在原生组合时：

- 对话中的少量分析可以分别调用在线工具，但必须说明各自仅为单页预览，并避免把不同粒度结果强行关联。
- 完整文件不得在客户端合并；说明当前组合导出尚未开放。
- 不使用知识库中的本地 `task_router`、适配器、合并脚本或任意 SQL 作为兜底。


## 机构名称匹配边界

用户直接点名发行机构时，默认精确匹配机构全称或简称：个人路径使用 `issuer eq`，企业机构检索使用 `zhiping_search_institutions(keyword="工银理财", match_mode="exact")`。只有用户明确要求“名称包含”“模糊匹配”等范围时，才使用个人 `contains` 或企业 `match_mode="contains"`。不把机构名当成产品名称片段搜索；不得把“工银理财”自动扩大到“高盛工银理财”，也不按母行、集团、合作关系或同名片段补充其他机构。精确无匹配时直接说明本次机构未匹配，不自动改为包含查询。例句“上周到期的工银理财产品中，有多少达到了业绩比较基准要求？”只查询精确匹配的工银理财机构；该问题没有授权扩大机构范围。机构类型列举仍可 keyword 留空，不附加名称条件。


## 原始净值数据（nav_data）

单页查询 `zhiping_query_product_nav_data(query)`；完整下载使用 `topic="nav_data"` 的服务端导出链路。query 支持 dimension=parent_product/sub_product、institution_ids/product_codes/sale_codes、all_market、filters、survival_mode；子产品还可按 sub_product_ids 定位，母产品禁止销售代码/子产品ID条件。不同范围条件按 AND 筛选。

快照：`mode="snapshot",statistic_date="2026-09-18",lookback_mode="to_2019"`；必须明确追溯范围，不自动默认。recent_years 使用 lookback_value 年数；to_year/custom 使用起始年份。历史：`mode="history",date_range={start:"2025-01-01",end:"2025-12-31"}`，区间含首尾，不传快照或追溯参数。fields 留空，输出固定基础信息+净值日期/初始净值标识/单位净值/累计净值/万份收益/披露7日年化。

initial_filter 默认 prefer_disclosed，全部追溯年份披露优先，缺失回退初始；initial_only 仅初始，all 不筛标识但仍每产品每天一条。无净值产品保留空值；母产品使用初始份额优先的代表份额净值。按登记编码/销售代码升序、净值日期降序，强制去重，当前不支持自定义排序或保留同日重复行。限定日期权限的账号必须使追溯起始年份也在允许范围内；限定子产品账号必须显式指定允许的 sub_product_ids。
