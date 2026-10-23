# 当前企业分析

本页是 2026-10-09 核对的 16 个企业工具静态基线。企业身份由当前 OAuth 授权绑定，部门、媒介、店铺只会进一步收窄权限。字段以当前工具 Schema 为准；查询不传筛选也不代表公司全量数据。切换企业后重新解析其目录对象。

日期均为上海时区 `YYYY-MM-DD` 字符串，起止包含当天。下面未列为必填的参数可省略；没有说明的默认值不自行补造。

## 企业目录

| 工具 | 参数类型、必填与默认 | 返回及使用规则 |
| --- | --- | --- |
| `corp_dept_list` | 无参数，arguments 为 `{}` | 可见部门树，`id/name/sub_dept`；“全部部门”用省略筛选或对应字段 0，不造虚拟 ID |
| `corp_medium_list` | 必填 `business_scope:string=commerce/content`；可选 `dept_id:integer≥0` 默认 0 | 可见启用员工，包含子部门；`user_id` 是媒介用户 ID，不是达人 UID，不返回手机号 |
| `corp_author_tag_list` | 可选 `keyword:string` ≤100 字符；`group_id:integer≥0=0` | 带货达人标签组与 `child` 子标签；0 为全部可见组，目录不是达人名单 |
| `corp_subscribed_brand_list` | 可选 `page:integer=1`、`size:integer=20`；非正数按默认处理，当前 Schema 未声明 size 上限 | 已开内容监控的我的品牌/竞对品牌，保留 `brand_code`；按任务取适量页 |
| `corp_subscribed_industry_list` | 同上述订阅列表分页 | 已启用行业、`category_id`、层级及完整路径；用于行业内容工具 |

当前企业授权店铺另用 `shop_auth_list`，参数见 @references/public-data-tools.md。需要订单筛选时员工目录选 `business_scope="commerce"`；内容业务员工用 `content`。已取得且企业未变的有效目录可复用，不需要每次查一遍。

## 出单达人和团长

| 工具 | 必填 | 可选、默认与返回 |
| --- | --- | --- |
| `corp_order_author_summary` | `start_time:string`、`end_time:string`；首尾合计 ≤186 天 | 下面的汇总公共参数及 `exclude_self_sale:integer=1`（0 同默认，1 剔除商家自卖，2 恢复原汇总口径）；返回概览、分层/圈层、投放模型、环比与佣金分布，不含分页明细 |
| `corp_order_colonel_summary` | 同汇总必填日期与 ≤186 天 | 汇总公共参数；没有 `exclude_self_sale`；返回团长概览、团长和活动 Top，团长仅抖音/快手，活动仅抖音 |
| `corp_order_author_detail` | `start_time:string`、`end_time:string`、`platform:string=dy/ks/xhs/sph` | 下面的明细参数；返回九项概览与按成交金额倒序的达人聚合明细，不是逐笔订单。SaaS 日期差 ≤32 天（含首尾最多 33 天），私有化日期差 ≤186 天；以实际部署定义为准 |

汇总公共参数：

| 参数 | 类型 / 默认 | 语义 |
| --- | --- | --- |
| `platform` | string=`"all"` | `all/dy/ks/xhs/sph`；all 下按平台和达人 UID 区分 |
| `belong_type` | integer=2 | 1 全部出单达人，2 团队建联达人；达人汇总的 1 仅管理员可选 |
| `dept_id` | integer≥0=0 | 不额外指定部门；正数须为可见部门 |
| `user_ids` | array<integer> | 每项正整数；省略或 `[]` 为权限和部门下可见媒介，普通媒介限本人 |
| `shop_ids` | array<string> | 每项非空授权店铺 ID，须匹配企业、权限与平台；省略或 `[]` 使用当前授权范围 |

达人汇总 `exclude_self_sale` 仅影响 `belong_type=1`；2 不表示补入此前已排除的无达人订单。团队建联口径始终不含商家自卖。不要将汇总参数对象直接复制给明细，尤其 `belong_type` 的类型与语义不同。

明细可选参数：

| 参数 | 类型 / 默认 | 约束 |
| --- | --- | --- |
| `belong_type` | string=`"all"` | `all/assigned/unassigned`，不限/有归属/未归属 |
| `author_type` | string=`"all"` | `all/merchant/colonel`；xhs/sph 不支持 colonel |
| `content_type` | string=`"all"` | `all/video/live`；非抖音只支持 all |
| `dept_id` / `user_ids` / `shop_ids` | 同上述类型与默认 | 仍限本企业可见范围 |
| `author_keyword` | string | ≤100 字符；昵称包含匹配，达人 UID 或平台达人号按接口定义匹配 |
| `tag_ids` | array<integer> | 企业带货子标签 ID，每项正整数，自动去重 |
| `tag_match_type` | string=`"any"` | `any/all`，任一标签/全部标签 |
| `page` / `size` | integer=1 / integer=20 | page≥1，size=1..50 |

先明确日期和平台，再解析必要的部门/媒介/店铺。只要概览时不追加全部明细；用户要复盘和名单时完成两者。汇总与明细的默认归属口径不同，核对前显式对齐适用条件，不能强行配平。团长 Top 不等于完整团长名单；不支持平台的零概览/空榜不等于企业没有业务。

达人汇总 `order_amount` 单位元、未扣退款；佣金与退款金额单位元，人数单位人。环比相对紧邻上个等长周期，数值为百分数；Schema 声明的 `2147483647` 哨兵表示“全新增长”，不能展示为巨大百分比。首次/新增出单达人数有各自统计范围，不能直接相减推出留存。直播与视频人数可重叠；非抖音的直播/视频出单数为 `null` 时保留。

## 企业带货与监控视频

| 工具 | 必填 | 可选与默认 | 返回与限制 |
| --- | --- | --- | --- |
| `corp_sale_video_data` | 无 | `content_order_type:integer=2`，枚举 1 新发布/2 动销/4 投流；可选成对 `start_time/end_time:string` | 企业带货概览 `summary`、分类排行 `label_rank`、GMV 分布 `gmv_distribution`；非管理员仅 summary |
| `corp_sale_video_list` | 无 | 可选成对日期；`platform:string="dy"`（dy/ks）；`content_order_type:integer`；`page:integer=1`、`size:integer=20`，1..50；`sort:string`、`order:string="desc"`（asc/desc） | 视频、达人、商品、互动增量及累计/周期销售；dy 默认类型2/排序 order_volume，ks 仅类型1且默认排序 push_time；sort 支持 order_volume/push_time |
| `corp_competitor_summary_video_list` | `brand_code:string` 非空、`start_time/end_time:string` | `page:integer=1`、`size:integer=20`，1..100 | 企业已监控品牌视频、成交与内容标签；日期首尾合计 ≤62 天 |
| `corp_industry_summary_video_list` | `category_id:integer≥1`、`start_time/end_time:string` | 同上分页 | 已订阅行业视频、类目路径、成交与标签；日期首尾合计 ≤62 天 |

企业带货两个工具的日期省略时默认截至昨天近 30 天；显式查询日期必须晚于当前时刻往前 31 天，这是历史窗口约束，早期的单日也可能不允许。不能把此限制误写成“任意历史区间只要 ≤31 天”。`label_rank/gmv_distribution` 为最新快照，不随请求日期变化；`content_order_type` 影响筛选，summary 其余类型的零值是该接口保留字段的行为，不能当作已查询其他类型的证据。

监控品牌使用订阅目录的 `brand_code`，行业使用订阅目录的 `category_id`，公开搜索和类目树不能证明内容监控权限。结论分别标注企业带货、监控品牌或订阅行业的样本范围。

## 品牌和行业内容策略

以下 `tag_types` 是非空 array<string>，允许值为 `video_type`、`golden_opening`、`selling_points`、`selling_point_visuals`、`pain_points`、`audience_segments`、`scenarios`、`trust_endorsements`、`action_calls`、`personas`。

`categories` 为 array<object>，每项必填 `category_id:integer≥1` 与 `category_level:integer=1..5`。`tags` 为非空 array<object>，每项必填 `tag_type:string`（同上枚举）及 `tag_name:string` 非空，当前接口只使用第一项；一次查一个已返回的真实标签，不能把数组当作多标签 AND/OR 筛选。

| 工具 | 必填 | 可选与默认 | 返回 |
| --- | --- | --- | --- |
| `corp_content_strategy_top` | `brandCodes:array<string>` 非空、`start_time/end_time:string`、`tag_types` | 无；注意 brandCodes 大小写 | 已监控品牌的内容要素 Top 标签及发布/动销/成交/曝光/点赞汇总 |
| `corp_industry_content_strategy_top` | 非空 `categories`、`start_time/end_time:string`、`tag_types` | 无 | 已订阅行业内容要素 Top 标签及指标 |
| `corp_content_strategy_tag_aweme_list` | `start_date/end_date:string`、`tags` | `brand_codes:array<string>` 省略或 [] 为全部已监控品牌；`categories`；`filter_type:string=low_follower_hot/hot_video/image_text` 可省略；下述分页与排序 | 标签对应品牌视频、达人/商品及表现 |
| `corp_industry_content_strategy_tag_aweme_list` | 非空 `categories`、`start_date/end_date:string`、`tags` | 下述分页与排序；不支持 filter_type | 标签对应行业视频、达人/商品及表现 |

两个标签明细均要求首尾合计 ≤31 天；`page:integer=1` 最小1，`size:integer=20` 范围1..100；`sort:string="sale_amount"`，允许 sale_amount/sale_volume/like_count/aweme_create_time/play_count；`order:string="desc"`，允许 asc/desc。Top 查询当前 Schema 不声明固定最大跨度，不把明细 31 天上限套用到 Top。

路线：订阅目录定位 → Top 选择内容维度 → 用同次结果的标签和同一对象范围下钻视频。Top 的日期字段是 start_time/end_time，明细为 start_date/end_date。多个标签可能命中同一视频，按真实视频 ID 去重后才计算独立视频数；标签数相加不能代表整体贡献。内容标签不是逐字稿或因果证据。

比较涨幅时，明确指标和对照周期，用相同品牌/行业、标签维度与筛选查询两期。Top 输出没有直接环比；只对可比较的精确数值计算变化，分母为0时说明新增或无法计算。某标签未进入一期 Top 不等于该期为0；成交区间不取中点推算精确涨幅。结论区分数据变化与未经验证的原因。

## 调用与返回示例

示例仅展示 `tools/call` params 与输出形状，不是实际数据。示例 ID、标签和日期在执行时必须替换为真实查询上下文。

```json
{"name":"corp_dept_list","arguments":{}}
```

对应成功 `structuredContent` 示例：

```json
{"code":0,"message":"success","data":[{"id":1,"parent_id":-1,"name":"示例部门","sort":0,"status":1,"created_at":1790784000,"sub_dept":[]}]}
```

```json
{"name":"corp_order_author_summary","arguments":{"start_time":"2026-10-01","end_time":"2026-10-07","platform":"dy","belong_type":2}}
```

```json
{"name":"corp_order_author_detail","arguments":{"start_time":"2026-10-01","end_time":"2026-10-07","platform":"dy","belong_type":"assigned","page":1,"size":20}}
```

```json
{"name":"corp_content_strategy_top","arguments":{"brandCodes":["已订阅的品牌编码"],"start_time":"2026-10-01","end_time":"2026-10-07","tag_types":["selling_points"]}}
```

```json
{"name":"corp_content_strategy_tag_aweme_list","arguments":{"brand_codes":["已订阅的品牌编码"],"start_date":"2026-10-01","end_date":"2026-10-07","tags":[{"tag_type":"selling_points","tag_name":"Top 返回的真实标签"}],"page":1,"size":20}}
```

分析交付保留企业/平台、日期、筛选和实际取得页数/条数。部分页失败时只报告成功范围，不把样本求和替换接口全量总额。收费、错误和结果读取见 @references/mcp-contract.md。
