# 达人、商品、品牌与平台内容

静态基线核对日期：2026-10-09；来源为 CQQ MCP 已注册工具的输入/输出 Schema。本页列出首版 12 个工具，其中 `shop_auth_list` 是企业权限目录。参数类型写为 string / integer / number / boolean / array；未列为必填的字段可省略，未说明的默认值不自行填造。调用使用 WorkBuddy 暴露的同名工具定义。

## 通用日期与分页

下表的「可选周期」表示 `start_time`、`end_time` 均为 string，成对传入 `YYYY-MM-DD`；均省略时为上海时区截至昨天近 30 个自然日，首尾包含。这里的达人/品牌周期 Schema 没有声明固定跨度上限，不能套用企业接口的 31/62 天规则。

「标准分页」表示可选 integer `page` 默认 1、最小 1；integer `size` 默认 20、范围 1..50。分页只取任务所需，每次调用可能单独计费；上游总数不等于已获取条数。

| 工具 | 必填 / 条件必填 | 可选与默认 | 返回与边界 |
| --- | --- | --- | --- |
| `author_detail` | `keyword:string`，一个非空昵称或抖音号 | 无 | 最多 20 个候选，含基础资料、粉丝画像、带货/直播/视频指标；核对身份后继续 |
| `author_sale_video_list` | `author_id:string`，已核实的抖音达人 ID | 可选周期；标准分页 | 周期动销视频、达人/商品、互动及累计/周期成交 |
| `author_recommend` | 无 | 见下节；`page:integer=1`，`size:integer=10` 且 1..10 | 候选达人及匹配指标；不是企业公海/完整达人库，不返回联系方式 |
| `brand_search` | 无 | `keyword:string` 可空；标准分页 | 品牌编码与名称，用真实 `brand_code` 继续查询 |
| `brand_product_basic_data` | `brand_code:string` 非空 | 可选周期 | 销售额、销量、日均、达人、带货内容、商品与店铺等指标 |
| `brand_sale_video_list` | `brand_code:string` 非空 | 可选周期；标准分页 | 品牌周期动销视频、达人/商品、成交与互动 |
| `categories_search` | 无 | `deep:integer=4`；非正数也按 4 处理 | 抖音类目树的 `category_id/category_name/category_level/children`、`shop_authorized`；不支持关键词或指定类目范围输入 |
| `product_detail` | `product_ids:array<string>` 与 `product_name:string` 二选一 | ID 模式 1..1000 个非空抖音商品 ID；名称非空 | 名称搜索最多 10 个候选；返回基础、价格、佣金、销售、品牌、店铺、类目 |
| `shop_detail` | `shop_ids:array<string>`，1..100 个非空抖音店铺 ID | 无 | 店铺名、体验分、类目及品牌等详情 |
| `shop_auth_list` | 无 | `shop_id:string` 精确匹配；`shop_name:string` 模糊匹配；省略不加该筛选 | 当前企业授权店铺，`resource` 为 1 抖店、3 快小店、18 微信小店、19 小红书；不是任意店铺搜索 |
| `video_detail` | `keyword:string`，非空视频 ID 或链接 | `platform:string="dy"`，枚举 `dy/ks` | 视频互动/作者；抖音可含累计成交和商品，不是口播逐字稿 |
| `video_comment_list` | `video_id:string` 或 `video_url:string` 至少一个；`top_n:integer` 1..100；`page_num:integer` ≥1；`page_size:integer` 1..20 | 无分页默认；同时给 ID 与 URL 时优先 ID | 发布日起连续 31 个自然日的 TopN 热评；不是最近 31 天或全部评论 |

`video_id` 为 1..64 位数字字符串；`video_url` 最长 2048 字符，可为作品页、短链或带链接分享文案。热门评论保留源排序、`has_next`、空数组与 `null`；空结果不说明视频下架。

## 推荐筛选

所有字段直接放在 arguments 顶层，不套嵌套筛选对象。可选 `product_id:string` 用真实抖音商品 ID 增强画像；空白按未提供处理。`exclude_followed:boolean=false` 控制是否额外排除当前企业有效跟进达人；企业黑名单始终排除。

| 字段 | 类型 / 默认 | 约束与口径 |
| --- | --- | --- |
| `product_category` | array<object>，默认 `[]` | 每项可含 `id:integer≥0`、`level:integer≥0`、`name:string`；使用类目结果，不猜 ID |
| `bring_product_type` | integer，默认 0 | 0 不筛选、1 主视频、2 主直播 |
| `live_sale` / `video_sale` | string，默认 `"0-0"` | 非负数 `下限-上限`，分别为直播场均/视频平均销售额；默认不筛选，金额单位以实时定义为准 |
| `aov_min` / `gmv` | number≥0，默认 0 | 单位元；前者为最低客单价，后者大于 0 时覆盖商品店铺评分档位，0 不覆盖 |
| `bring_level` | array<integer>，默认 `[]` | 每项 1..5 |
| `follower_count` | string，默认 `"0-0"` | 非负整数 `下限-上限`、`>下限` 或 `<上限`；默认不筛选 |
| `fans_age` | array<string>，默认 `[]` | 每项 `-18/18-23/24-30/31-40/41-50/50-` |
| `fans_gender` | integer，默认 0 | 0 不筛选、1 女性；无男性枚举值 |
| `fans_province` / `fans_city` | array<string>，默认 `[]` | 非空省份/城市名，可带行政区后缀 |

候选取自上游前 1000 个，稳定去重后分页；当前页详情缺失会跳过且不补位。`author_count/total_count` 保留上游首屏总数，不据此宣称全量可获取或保证每页满额。用户只给商品名时先搜并核对商品，再推荐；已有有效 ID 可直接用。

## 调用与返回示例

以下 JSON 是 `tools/call` 的 params 格式示例；宿主负责协议传输。示例名称、ID、数值和返回均为演示数据，不是实际查询结果；执行时替换为用户条件和真实来源值。

```json
{"name":"author_detail","arguments":{"keyword":"已确认的达人昵称"}}
```

```json
{"name":"author_recommend","arguments":{"product_id":"1234567890123456789","exclude_followed":true,"page":1,"size":10}}
```

```json
{"name":"brand_sale_video_list","arguments":{"brand_code":"已确认的品牌编码","start_time":"2026-10-01","end_time":"2026-10-07","page":1,"size":20}}
```

```json
{"name":"video_comment_list","arguments":{"video_id":"1234567890123456789","top_n":20,"page_num":1,"page_size":20}}
```

评论工具的成功 `structuredContent` 示例：

```json
{"code":0,"message":"success","data":{"top_n":20,"page_num":1,"page_size":20,"items":[{"video_id":"1234567890123456789","total":1,"has_next":false,"comments":[{"rank":1,"comment_id":"9876543210123456789","comment_time":"2026-10-01 12:00:00","comment":null,"digg_count":12}]}]}}
```

## 数据口径

达人 `amount30`、动销视频 `total_amount/period_amount`、品牌 `amount/day_avg_amount` 等已定义为元的区间保留原值；销量区间单位件。`total_*` 是累计，`period_*` 是请求周期，不能混用。商品价格等可能是数字，按字段 Schema 解释，不把所有数值都按分转元。推荐输入中 `gmv` 是画像筛选条件，不是返回的成交事实。

跨达人或品牌比较必须使用相同平台、日期、范围和单位。公开品牌搜索不能替代企业订阅品牌目录；类目树中的 `shop_authorized` 不能证明已取得行业内容订阅。连接、错误与收费处理见 @references/mcp-contract.md。
