# 工具选择与最新详情口径

以下所有业务工具均可额外传入 `user_question`（1～4000 字），内容为用户本轮原始问题，仅用于服务排障和用途分析，不参与查询与计费。能力探测工具不接受该字段；不要把手机号、验证码、令牌、密码或密钥放入其中。
业务工具还可传入 `conversationId`（1～256 字），取连接器 Skill 中运行时替换的当前 WorkBuddy 会话 ID `${CODEBUDDY_SESSION_ID}`，用于在后台关联同一会话的多轮问题。占位符未替换或无法取得时省略；不要传本轮请求 ID 或 `request_key`。能力探测工具不接受该字段。

统一服务始终发布免费工具 `get_zhiping_account_capabilities`，用于返回当前身份和实际工具集合；每次会话开始或身份变化后先调用。服务端每次请求实时校验身份：账号匹配 `business_user` 即按企业账号定位（无论此前是否个人用户），否则按个人账号处理。个人能力包含 1 个搜索工具、8 个详情工具和 1 个积分余额查询工具；`enterprise_access=available` 的企业账号只返回 `zhiping_*` 企业工具，个人工具被服务端停用；`enterprise_access=restricted` 的企业账号回退返回个人工具，首次使用前需向用户说明并确认。所有个人详情查询都先调用搜索工具定位产品；搜索唯一命中，或用户从候选中确认后，才使用结果的 `sub_product_id`（作为详情输入 `sub_id`，优先）查询详情。产品名称重名或份额不唯一时要求用户选择，不猜测。

`enterprise_access=restricted` 表示用户是企业用户（`company_name` 为企业名称）但企业工具权限尚未开通（`restriction_code` 为受限原因）。首次遇到该状态时，先告知用户："您是企业用户（{company_name}），目前企业工具权限尚未开通；如需使用企业数据工具，请联系客户经理开通。您也可以选择使用个人理财产品查询工具继续查询（按个人积分计费）。"并询问是否使用个人工具，用户明确确认后才调用；同一会话内确认一次即可，用户拒绝则停止查询，等待开通或改问其他问题。问题超出个人工具能力范围（企业专属数据）时，如实说明需开通企业权限后才能查询，不要用个人工具硬答或编造企业数据。

完整产品名、登记编码、销售代码等明确目标也先走精确搜索：名称默认使用 `product_name eq`（同次定位母/子产品；明确维度时才使用 `parent_name/sub_name eq`），登记编码使用 `product_code eq`，销售代码使用 `sale_code eq`。唯一命中后以搜索返回的 `sub_product_id`（作为详情输入 `sub_id`）查询详情；精确搜索返回空 `items` / `meta.resolution.next_action=stop_no_match` 即为本轮终点，不得删减名称、去掉期次、替换关键词或改查相似产品。只有用户明确要求扩大范围后才能开始新的搜索。

名称片段、系列简称等模糊输入默认用 `product_name contains`（明确维度时才用 `parent_name/sub_name contains`） 搜索一轮，最多返回 10 个候选。`meta.resolution.candidate_confirmation_required=true` / `next_action=ask_user_to_select` 时必须展示候选并等待用户确认；确认前不查详情、不翻页、不换词重复搜索。即使只有一个模糊候选也要确认。确认后优先以选中候选的 `sub_product_id`（作为详情输入 `sub_id`）查询详情；模糊搜索空结果时停止，不做第二轮猜测。

## 产品编码路由

`product_name` 支持 `eq/contains`，同次业务调用匹配母/子名称并保留硬条件。完整名称原样使用 `eq`：“中银理财-乐享天天45号”不能删机构前缀或擅自认定简称。用户明确简称、片段或目标有歧义时才 `contains` 一轮候选确认；只提供“系列名+期次”但没有完整登记名称也属于片段，例如“丰利乐享第373期”须用 `product_name contains`。服务端使用短语分析与未分词字段的字面匹配，并在同一查询中兼容“第”紧邻阿拉伯数字的两种写法（如“第373期”/“373期”），不删期次数字。不换词、不使用 fuzzy、编辑距离或相似产品重试。旧 Schema 缺少该字段时需同步升级服务及 Skill。精确未匹配不猜测原因或断言产品不存在；已知还有候选时必须等待用户选择。

- 去除首尾空白后，完整匹配 `^[CZ][0-9]{13}$` 的 14 位编码是理财产品登记编码，对应 `product_code`。
- 不符合上述完整格式的编码一律按发行机构销售代码处理，对应 `sale_code`；不要先当作 `product_code` 试查。
- 个人详情选择器不能仅以 `sale_code` 作为主标识。登记编码与销售代码都先用 `search_wealth_products` 的对应 `eq` 条件精确筛选，再将唯一结果的 `sub_product_id`（作为详情输入 `sub_id`，优先）或 `product_code`+`sale_code` 传给详情工具；无结果或多结果时不要猜测。
- 多个编码分别判断；用户把字段统称为“产品代码”不改变格式判别结果。

## 详情工具

- `get_wealth_product_info`：基本信息。
- `get_wealth_product_benchmark`：业绩比较基准，固定使用当前生效的汇总口径。
- `get_wealth_product_establishment`：成立日期和募集规模（如有）。
- `get_wealth_product_fees`：当前执行费率，只返回 `latest_*` 费率字段。
- `get_wealth_product_subscription_redemption`：销售渠道和销售对象。
- `get_wealth_product_investment_scope`：当前投资范围和比例上下限，不返回对应备注。
- `get_wealth_product_nav`：历史净值序列；用 `begin/end` 提供走势图数据，不传区间时取最新快照。
- `get_wealth_product_performance`：最新收益率和最大回撤，固定近 7 日、近一个月、近三个月、近六个月、近一年、今年以来、成立以来七个口径。

### 净值计算指标字段

收益率字段为 `seven_day_return`、`month_return`、`quarter_return`、`half_return`、`one_year_return`、`this_year_return`、`establishment_return`；最大回撤字段使用相同前缀加 `_max_drawdown`。结果同时返回 `metric_family`、`caliber` 和实际计算日期。现金管理类默认复利，其他产品默认单利；不传 `begin/end` 历史区间。

产品已精确解析但收益率无记录时，`product_statuses[].annualized_return_status=no_data`，且 `meta.resolution` 返回 `annualized_return_status=no_data`、`next_action=stop_no_return_data`、`allow_similar_product_fallback=false`。`resolved_products` 提供产品名称、编码、成立日期、成立天数、是否新成立和收益率状态；服务端以查询日距成立日 0～30 天标记 `recently_established=true`。回答先列产品名称；只有该标志为 true 时，才结合成立日期说明“成立时间较近，目前还没有形成可用收益率数据”，否则仅说明暂无收益率数据，不猜测原因。不得重新搜索或查询相似产品。同一响应只有最大回撤而没有收益率记录，或收益率七个窗口全部为 `null`，也属于该终止状态。

## 积分余额查询

`get_my_credit_balance` 无参数返回当前登录个人账号今日积分情况：`granted`（当天发放额度）、`spent`（已用积分）、`reserved`（待结算预占）、`available`（剩余可用积分）、`resets_at`（额度重置时间）与 `timezone`。本工具**免费、不接受任何业务参数、不扣积分、不落计费记录**，`meta.free=true`；除自动剥离的 `user_question` 外，传任意参数（含 `request_key`）都会返回 `INVALID_ARGUMENT`。余额以调用时刻为准，重复调用不会产生计费。积分不足或概览等场景可先调用本工具告知用户当前剩余积分；`resets_at` 为北京时间零点重置时间。

## 使用规则

先确认连接已授权；手机号和短信验证码由浏览器授权页收集，不要求用户在聊天中输入。成功查询按配置扣积分，空结果也计费；重试复用 `request_key`。

产品搜索中的 `issuer` 和 `sales_org` 使用机构名称或简称，可用 `eq` 或 `contains`。产品状态筛选使用 `product_status`：取值只能是 预售、在售、存续、已到期、发行失败 五个状态名称，单状态用 `eq`，多状态用 `in` 传名称数组取并集；状态名称写错或使用数字代码被拒绝，不支持 contains/lte/gte，其他字段也不能使用 in。状态口径为产品生命周期状态，不等于 App 货架当前可购买；搜索结果会回传 `product_status` 中文标签，可据此确认生命周期状态，但涉及实际购买渠道时仍须说明不能据此确认 App 当前在售。用户要求“在售”且确指产品状态时按 `product_status eq 在售` 筛选并说明命中范围为该状态。

搜索响应的 `meta.resolution` 明确下一步：`stop_no_match` 表示无匹配且禁止相似名称回退，`ask_user_to_select` 表示必须先由用户选择候选，`use_unique_match` 表示精确标识唯一命中，`return_results` 表示普通条件筛选结果。`allow_similar_name_fallback` 当前固定为 `false`。

产品搜索返回企业 21 个基础字段并新增回传 `product_status`（产品生命周期状态中文标签）：`product_id/sub_product_id/product_code/sale_code/product_name/sub_product_name/institution_type/institution_name/raising_type/actual_start_date/actual_end_date/actual_raising_statement/risk_level/investment_type/investment_type_level2/open_type/raising_currency/min_holding_period/is_initial_share/is_multi_share/main_flag/product_status`。ES 未承载的 `product_name/institution_type/actual_raising_statement/is_multi_share` 为 `null`；`institution_name` 按 ES `orgId` 解析（简称优先、全称兜底）。枚举/码值保持 ES 原始值，不做字典翻译；需要面向用户的业务值（如风险等级 `R1`～`R5`、业绩比较基准、年化收益）时调用对应详情工具。`product_status` 是生命周期状态口径，可确认在售/存续等，但不代表 App 货架当前可购买，二者不得混用。历史表现不能表述为预期或承诺收益；基准公式被截断且用户需要全文时，调用基准详情工具。

搜索不返回 `liquidity_profile` 或一日流动性候选标志。明确天数用 `min_holding_days` 的 `lte/gte`；“周期不超过 30 天”“周期至少 365 天”“1 天就能赎回”可直接使用自然语言查询。只有“短期/长期”时先向用户确认天数边界。“1 天可赎回”只是最短持有期不超过 1 天的筛选，不等于 T+1 确认或到账，不得声称候选支持 1 天内确认或到账。

个人搜索 `page_size` 最大 100，详情最大 50，单次详情最多 10 个产品。服务端对完整 MCP 结果执行 128 KiB 硬限制；`meta.response_limited=true` 表示本页因字节预算缩短，应把本页交付用户并说明可继续分页，不得自动抓取全部分页。`RESULT_TOO_LARGE` 表示单条数据已超限，应减少 `indexes` 或缩小产品范围。

个人搜索支持排序：`sort_by` 取 `risk_level`、`min_holding_days`、`actual_start_date`、`actual_end_date`、`establishment_annualized`（成立以来单利年化收益率），`order` 取 `asc`/`desc`（默认 `asc`）。`establishment_annualized` 来源于 ES 子产品索引的 `establishmentAnnualizedSimpleReturn`，回答"最高收益"时可用 `sort_by=establishment_annualized&order=desc` 直接排序；其余收益率口径（月/季/半年/年/今年等）不属于搜索可排序字段，需要时先筛选并定位候选，再调用 `get_wealth_product_performance` 获取年化收益后比较。不传 `sort_by` 时保持现有稳定排序。

结果保留实际数据日期、业务口径和单位，但不向用户展示物理表名、索引名或内部数据源标识。精确详情的 `NOT_FOUND` 按精确终止规则说明没有可访问数据；其他 `isError` 只说明实际错误，不把查询失败当成没有数据。销售渠道不等于某 App 当前在售；投资范围不等于实际持仓；成立募集规模不等于当前存续规模。

## 个人到期日查询

到期日筛选使用 `maturity_date`，值为有效的 `YYYY-MM-DD` 日期，仅支持 `eq/gte/lte`。指定日期用 `eq`，日期区间同时传 `gte` 与 `lte`（两端包含），单边范围只传对应条件；例如 `filters=[{"field":"maturity_date","op":"gte","value":"2026-09-01"},{"field":"maturity_date","op":"lte","value":"2026-09-30"}]`。自然语言 `query` 支持“到期日为2026-09-30”“到期日不早于2026-09-01”“到期日不晚于2026-09-30”，多个条件用逗号分隔。口径为子产品实际结束日期优先，缺失时取母产品实际结束日期；两者为空不命中。到期日不是最短持有期，也不是投资周期结束日。相对日期需先转换为北京时间的明确日期。条件与其他筛选取交集，在分页前执行；空结果正常返回，非法日期/运算符被拒绝。实际结束日期并非说明书约定到期日，不承诺预测未来到期；用户明确需要约定到期日时说明当前能力边界。

生产路径先从只读库解析日期范围内的子产品 ID，再约束 ES 搜索，不假定索引存在日期字段。日期范围命中超过 10000 个份额时返回 `QUERY_TOO_BROAD`，需缩小日期范围；不能自动拆分抓取全部数据。

## 个人产品状态筛选

产品状态筛选使用 `filters` 的 `product_status` 字段，取值只能是五个状态名称：预售、在售、存续、已到期、发行失败。查单一状态用 `eq`，例如 `filters=[{"field":"product_status","op":"eq","value":"存续"}]`；一次查多个状态用 `in` 传入名称数组取并集，例如 `filters=[{"field":"product_status","op":"in","value":["已到期","发行失败"]}]`。状态名称写错或使用数字代码会被拒绝；不支持 contains、lte、gte，也不能对其他字段使用 in。产品状态与其他筛选条件取交集；搜索结果回传 `product_status` 字段（中文标签），可据此确认在售/存续等生命周期状态，但“在售”是产品状态口径，不等于 App 货架当前可购买，回答时不得混用。

## 用户回答展示规则（强制）

工具返回的字段键、代码和技术空值只用于内部解析，不能复制到用户回答、表格标题、括号注释、脚注或代码块中。只展示中文业务名称和业务释义，禁止原始 JSON、数据库字段名、内部枚举值及“字段=代码”；登记编码、销售代码等用户用于识别产品的业务编码仍可展示。

- `actual_statistic_date` 只写“净值统计日”，`open_type` 只写“开放类型”，不在括号里附英文键或数字代码。
- `null`、`None`、缺失值及空字符串统一写“暂无数据”，不能写“暂无（null）”“无（None）”或填成 0。真实数值 0 按实际单位保留。
- 枚举只用服务返回的业务释义。只有数字代码、没有释义时写“暂无数据”，不得猜测 `open_type=4` 的含义。
- 最短持有期、开放类型及赎回频率分别展示。“每日可赎”只能依据实际返回的每日赎回窗口/规则，不从开放类型代码或一日最短持有期推导；仍需保留确认/到账限制。
- 输出前检查正文、表格和括号注释，删除内部字段名、枚举代码和技术空值；保留有效业务日期、单位、收益口径和风险限制。

正确展示示例：

| 项目 | 内容 |
| --- | --- |
| 近7日年化收益率 | 暂无数据 |
| 近7日累计收益率 | 暂无数据 |
| 万份收益 | 暂无数据 |
| 净值统计日 | 暂无数据 |
| 最短持有期 | 1天 |
| 开放类型 | 暂无数据 |

示例开放类型暂无释义；若服务实际返回中文释义才展示该释义，若有赎回规则另列“赎回频率”，不自行补成每日可赎。


## 机构名称匹配边界

用户直接点名发行机构时，默认精确匹配机构全称或简称：个人路径使用 `issuer eq`，企业机构检索使用 `zhiping_search_institutions(keyword="工银理财", match_mode="exact")`。只有用户明确要求“名称包含”“模糊匹配”等范围时，才使用个人 `contains` 或企业 `match_mode="contains"`。不把机构名当成产品名称片段搜索；不得把“工银理财”自动扩大到“高盛工银理财”，也不按母行、集团、合作关系或同名片段补充其他机构。精确无匹配时直接说明本次机构未匹配，不自动改为包含查询。例句“上周到期的工银理财产品中，有多少达到了业绩比较基准要求？”只查询精确匹配的工银理财机构；该问题没有授权扩大机构范围。机构类型列举仍可 keyword 留空，不附加名称条件。

## 请求预算与错误恢复

认证、身份路由、问题记录、业务调用和个人计费共用从 MCP 入口起算的 25 秒协作式预算；失败后的积分恢复另有最多 3 秒预算。生产总延迟仍需实测，不能把客户端 30 秒连接超时等同于业务保障。

企业工具返回 `isError=true` 或 `error` / `error_code` 时只能报告实际失败，不得声称任务完成；正常空结果仍是成功。`UPSTREAM_TIMEOUT` 表示结果尚未确认，不得自动重试企业创建导出、月报或保存/删除偏好。同步工作线程可能继续运行，先由管理员核查；已有真实 job_id 时才可查询状态，不得猜测任务标识。个人请求以原 request_key 核查，`BILLING_RECOVERY_PENDING` 时查看余额，不承诺已退分，不更换标识重复计费。

服务在问题记录启用时向授权页展示实际保留天数。问题参数仍仅用于排障和用途分析，不发送凭证、手机号或验证码。
