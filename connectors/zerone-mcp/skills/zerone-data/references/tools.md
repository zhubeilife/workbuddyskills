# 正式 MCP 工具参考

读取日期：2026-10-15。来源：正式 MCP 的 tools/list。以下为公开工具定义，不含业务查询结果或凭证。实时 schema 优先。

## model_financing_probability

查询项目公司的融资概率预测模型。

    【使用场景】用户想了解某个项目公司未来获得融资的可能性，或对比多家公司的融资潜力。
    【前置条件】建议先用 entity_search 确认标准公司名称和类型。
    【支持类型】COMPANY（项目公司）、PREIPO（拟上市）、LISTED（上市公司）、NEEQ（新三板）。

    Args:
        entity_name: 公司名称，如"字节跳动"、"美团"。数据库中存储的是标准全称，若用户提供的是简称，建议先用 entity_search 确认。
        entity_type: 实体类型过滤，可选值：COMPANY / PREIPO / LISTED / NEEQ。留空则自动识别，但建议明确指定以减少歧义。

    Returns:
        包含融资概率（百分比）和模型指标的字典，所有字段名为中文。

### 输入 schema

```json
{
  "properties": {
    "entity_name": {
      "title": "Entity Name",
      "type": "string"
    },
    "entity_type": {
      "default": "",
      "title": "Entity Type",
      "type": "string"
    }
  },
  "required": [
    "entity_name"
  ],
  "title": "model_financing_probabilityArguments",
  "type": "object"
}
```

## model_company_match_gp

为指定项目公司匹配潜在适合出资的投资机构。

    【使用场景】用户想知道某个项目公司适合找哪些投资机构融资，或分析某家公司的潜在投资方列表。
    【前置条件】建议先用 entity_search 确认项目公司的标准全称。

    Args:
        company_name: 项目公司名称，如"字节跳动"。数据库中存储的是标准全称，简称需先用 entity_search 确认。
        page: 页码，从 1 开始，默认 1。
        page_size: 每页条数，取值范围 1~5，默认 5。此工具为精准推荐，每页不宜过多。

    Returns:
        包含匹配机构列表（匹配分数、排名、推荐日期）及推荐理由提示词的字典，字段名为中文。
        推荐理由提示词可直接用于生成自然语言推荐理由。

### 输入 schema

```json
{
  "properties": {
    "company_name": {
      "title": "Company Name",
      "type": "string"
    },
    "page": {
      "default": 1,
      "title": "Page",
      "type": "integer"
    },
    "page_size": {
      "default": 5,
      "title": "Page Size",
      "type": "integer"
    }
  },
  "required": [
    "company_name"
  ],
  "title": "model_company_match_gpArguments",
  "type": "object"
}
```

## entity_financial_list

查询上市或拟上市公司的财务数据列表（分页）。

    【使用场景】用户想查看某家上市公司的历史财务指标（营收、利润、资产负债等）。
    【前置条件】建议先用 entity_search 确认标准名称和类型。
    【市场路由】market 留空时，后端根据权威上市证券表识别并查询全部上市标识；指定 market 时查询该市场下的全部标识。
    【支持范围】A 股、新三板和拟上市公司沿用原 OpenAPI；港股和美股使用 ZPE MySQL 数据源。
    【金额展示】港股和美股记录包含后端确定性生成的“金额展示”。终答必须原样使用
    “金额展示”中的值，不得再次调用金额换算工具、不得改写量级或省略币种；
    原始金额字段仅用于计算，不直接用于终答展示。

    Args:
        entity_name: 主体名称，如"贵州茅台"。数据库中存储的是标准全称。
        entity_type: 实体类型，可选值：LISTED / PREIPO / NEEQ。留空则自动识别，建议明确指定。
        page: 页码，从 1 开始。
        page_size: 每页条数，上限 50。
        market: 可选的上市市场约束。未知时必须留空，由后端确定性识别；仅在用户明确指定多地上市市场时传值。

    Returns:
        分页财务数据、完整上市标识列表，以及按上市标识分组的查询结果；多标识查询并发执行。

### 输入 schema

```json
{
  "properties": {
    "entity_name": {
      "title": "Entity Name",
      "type": "string"
    },
    "entity_type": {
      "default": "",
      "title": "Entity Type",
      "type": "string"
    },
    "page": {
      "default": 1,
      "title": "Page",
      "type": "integer"
    },
    "page_size": {
      "default": 50,
      "title": "Page Size",
      "type": "integer"
    },
    "market": {
      "anyOf": [
        {
          "enum": [
            "A_SHARE",
            "HK_SHARE",
            "US_SHARE"
          ],
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Market"
    }
  },
  "required": [
    "entity_name"
  ],
  "title": "entity_financial_listArguments",
  "type": "object"
}
```

## entity_profile

查询实体的综合画像（全景档案）。

    【使用场景】用户想了解某个机构/公司/基金的完整信息，如"红杉中国投资了哪些公司"、
    "字节跳动的融资历史"、"某家基金的规模和管理人"等。此工具聚合了多个数据源，一站式返回。
    【前置条件】建议先用 entity_search 确认标准名称和类型，类型正确可大幅提升查询准确性。
    【支持类型】8 种业务类型：GP（投资机构）、FUND（基金）、LP（出资方）、COMPANY（项目公司）、
    FUND_MANAGER（基金管理人）、PREIPO（拟上市）、LISTED（上市公司）、NEEQ（新三板）；以及
    ENTITY（仅存在于工商实体库的主体，仅返回工商基本信息）。

    【返回内容】根据实体类型自动聚合不同模块：
    - 基本信息：名称、成立日期、注册地区、赛道/行业等
    - 标签画像：业务标签、机构标签等
    - 概览统计：累计投资数、IPO数、管理基金数、AUM 等
    - 关联实体：股东列表、管理基金列表、出资人列表、融资历史等
    - 上市/申报信息：辅导信息、申报进程（仅 PREIPO/LISTED/NEEQ）

    【融资轮次规则】COMPANY 的“最新融资轮次”与“融资历史”中的“融资轮次”均为明细轮次（如 A1轮、A2轮），仅用于展示。如需按轮次筛选、统计或分组，请使用通用查询工具的聚合轮次字段。

    【金额展示】上市公司基本信息包含总市值时，后端会同时返回确定性生成的“金额展示”。
    终答必须原样使用“金额展示”中的值，不得根据原始人民币金额再次换算量级。

    Args:
        entity_name: 主体名称，如"红杉中国"、"字节跳动"。数据库中存储的是标准全称。
        entity_type: 实体类型，可选值：GP / FUND / LP / COMPANY / FUND_MANAGER / PREIPO / LISTED / NEEQ / ENTITY。
                   留空则自动识别，但强烈建议明确指定，不同类型返回的数据模块差异很大。

    Returns:
        综合画像数据字典，按模块组织，所有字段名为中文。

### 输入 schema

```json
{
  "properties": {
    "entity_name": {
      "title": "Entity Name",
      "type": "string"
    },
    "entity_type": {
      "default": "",
      "title": "Entity Type",
      "type": "string"
    }
  },
  "required": [
    "entity_name"
  ],
  "title": "entity_profileArguments",
  "type": "object"
}
```

## entity_search

实体模糊搜索 — 所有涉及名称查询的前置步骤。

    【使用场景】用户提供简称/别称（如"红杉"、"字节"）、拼写不确定、或名称有歧义时，
    先调用此工具获取标准全称和实体类型，再代入其他工具进行精确查询。
    【为什么必须先用】数据库中存储的是标准全称（如"红杉资本中国基金"而非"红杉中国"），
    直接使用简称可能导致查询无结果或结果不准确。

    【支持类型】8 种业务实体类型，以及工商兜底类型：
    - GP：投资机构（如红杉资本、高瓴资本）
    - FUND：基金（如红杉中国基金 IV）
    - LP：出资方（如全国社保基金）
    - COMPANY：项目公司（如字节跳动、美团）
    - FUND_MANAGER：基金管理人（如红杉资本股权投资管理（上海）有限公司）
    - PREIPO：拟上市公司
    - LISTED：上市公司
    - NEEQ：新三板公司
    - ENTITY：未命中业务主体但存在于工商实体库的主体；仅可继续查询工商基本信息

    Args:
        keyword: 搜索关键词，支持模糊匹配。如"红杉"可匹配到"红杉资本中国基金"；
                "字节"可匹配到"字节跳动"。支持中英文、简称、别称。

    Returns:
        包含以下字段的字典：
        - entity_name: 标准全称（用于代入其他工具）
        - entity_id: 实体唯一标识
        - entity_identity: 实体类型（GP/FUND/LP/COMPANY/FUND_MANAGER/PREIPO/LISTED/NEEQ/ENTITY）
        - other_matches: 其他可能的匹配结果列表（当存在多个相似名称时）

### 输入 schema

```json
{
  "properties": {
    "keyword": {
      "title": "Keyword",
      "type": "string"
    }
  },
  "required": [
    "keyword"
  ],
  "title": "entity_searchArguments",
  "type": "object"
}
```

## get_available_tables

获取当前可查询的数据表列表。

    【使用场景】通用数据查询的第一步。当用户的问题无法通过业务专题工具（entity_profile 等）
    直接回答时，先调用此工具了解有哪些表可用，再决定用哪张表进行 execute_query/execute_aggregate_query。

    【为什么是第一步】此工具返回的表列表已包含每张表的描述和适用场景，帮助你快速判断
    "该用 company 表还是 company_financing 表"。一个复合问题可能需要多个数据集；不得只选择名称最相似的
    单个数据集，而应按完整母集与关联关系拆分查询。

    Returns:
        可查询表列表，每项包含：
        - table_name: 表名（如 company、company_financing）
        - description: 表的中文描述
        - description_for_llm: AI 友好的完整使用说明与跨数据集约束
        - category: 分类（实体 / 交易事件 / 关联关系）
        - grain: 服务端固定的结果行粒度
        - description_for_llm: AI 友好的使用说明（包含典型场景）

### 输入 schema

```json
{
  "properties": {},
  "title": "get_available_tablesArguments",
  "type": "object"
}
```

## get_table_schema

获取指定数据表的字段结构、类型、可筛选性和允许的操作类型。

    【使用场景】通用数据查询的第二步。在确定要查哪张表后，调用此工具确认：
    1. 目标表有哪些字段可用
    2. 每个字段是什么类型（string/date/decimal/int/array）
    3. 每个字段支持哪些操作（equal/like/range/list_or）
    4. 字段的中文映射名（用于向用户展示）

    【前置条件】table_name 必须从 get_available_tables 返回的列表中选择，不可随意构造。

    【特别重要】此工具返回的 schema 是 execute_query / execute_aggregate_query 的唯一有效字段来源。
    未在 schema 中出现的字段名传入查询会报错。

    Args:
        table_name: 表名，如"company"、"company_financing"。必须从 get_available_tables 返回的列表中选择。

    Returns:
        表结构信息，包含：
        - columns: 字段列表，每项包含 column_key（英文，用于传入查询）、column_name（中文，用于展示）、
                  type（数据类型）、operations（支持的操作列表）、description（字段说明）
        - description_for_llm: 数据集完整使用说明；若要求先查询其他数据集，必须遵守
        - grain: 固定结果行粒度
        - primary_key: 主表一条记录的唯一键
        - business_event_id: 业务事件 ID；一对多事件可能重复
        - semantic_metrics: 标准语义指标；事件数据集提供 event_count，固定按 business_event_id 去重
        - relation_unique_key: 关联关系两端的固定唯一键（仅关系数据集）
        - predicate_capabilities: 数据集已挂载的存在性筛选能力及逻辑字段；
          仅用于理解字段语义，不包含物理表、连接键或 JOIN 细节
        - schema_version: 启动期 Frozen Schema 版本

### 输入 schema

```json
{
  "properties": {
    "table_name": {
      "title": "Table Name",
      "type": "string"
    }
  },
  "required": [
    "table_name"
  ],
  "title": "get_table_schemaArguments",
  "type": "object"
}
```

## execute_query

执行单表结构化查询（列表/明细查询）。

    【使用场景】当业务专题工具无法满足需求时，使用此工具进行任意筛选、排序、分页查询。
    典型场景：按多个条件组合筛选（如"2023年北京人工智能赛道获融资的公司"）、
    获取特定字段列表（如"只返回公司名称和融资轮次"）、分页浏览大量数据。

    【分页限制】每页最多 50 条，仅支持访问排序后的前 500 条结果，最大页数随 pageSize 变化。
    翻页时递增 page，并保持筛选条件、排序和 pageSize 一致。根据 metadata.hasMore
    判断是否继续；到达数据末尾或 500 条边界后停止，如需其他数据请缩小筛选范围。

    【强制前置条件】必须先调用 get_table_schema(table_name=xxx) 确认可用字段，
    select_columns 和 filters 中的 field 必须来自 schema 中的 column_key。

    【操作类型说明】
    - equal: 等于，value 为单个值。例：{"field": "is_ipo", "type": "equal", "value": 1}
    - like: 模糊匹配，value 为字符串，自动前后加 %。例：{"field": "company_name", "type": "like", "value": "字节"}
    - range: 区间，value 为 [start, end] 列表。例：{"field": "financing_date", "type": "range", "value": ["2023-01-01", "2023-12-31"]}
      【注意】所有日期字段只能用 range，不能用 equal/like/list_or。
    - list_or: 多值匹配任一，value 为列表。例：{"field": "financing_round", "type": "list_or", "value": ["A轮", "B轮"]}

    【filters 格式】
    每项为 {"field": "字段名", "type": "操作类型", "value": "值"}。
    filter_operator 控制本次查询中所有条件的连接关系，只支持 AND 或 OR，默认 AND。
    一次查询不能混合使用 AND 和 OR。
    例：查询注册地为北京或上海的公司时，传入两个地区条件并设置 filter_operator="OR"。
    历史 connector 字段仅兼容 AND；传入 connector="OR" 会报参数错误，避免被静默忽略。

    【同一子表成员筛选】
    get_table_schema 返回相同 same_item_scope 的数组字段可使用同一个 same_item_group，
    这些条件会合并到一个 EXISTS，保证命中同一条子表记录。
    例如查询“深创投作为卖方”的老股转让：
    {"field":"deal_party_genealogy_names","type":"equal","value":"深创投","same_item_group":"seller"}
    与 {"field":"deal_party_roles","type":"equal","value":"卖方","same_item_group":"seller"}。
    查询“2026年备案基金作为卖方”时，deal_party_fund_amac_record_date 与
    deal_party_roles 也必须使用相同 same_item_group。仅出现一个交易方身份时，
    服务端会自动把遗漏分组的同作用域条件绑定到该身份；同时查询买方和卖方时，
    必须为双方条件显式设置不同的 same_item_group。
    并购事件的实际角色为“收购方/出售方”，传入通用“买方/卖方”时会自动兼容转换。
    不同业务角色必须使用不同的 same_item_group。

    【融资轮次规则】展示公司最新融资或融资事件明细时，在 select_columns 中使用明细字段 latest_financing_round 或 financing_round（如 A1轮、A2轮）。按轮次筛选时，filters 必须使用聚合字段 latest_financing_round_consol 或 financing_round_consol（如 A轮、B轮）。

    【子表字段限制】
    - select_columns 中可以包含子表字段（如 company_tags、gp_names），会自动聚合为数组返回
    - filters 中可以按子表字段筛选，底层会生成 JOIN 聚合子查询
    - order_by 中不支持子表字段排序

    【明细去重】
    - distinct_by 可指定一个或多个主表/关联表字段，数据库会按这些字段分组，每组只保留 order_by 排序后的第一条。
    - 例如退出项目按公司去重：distinct_by=["company_id"]、order_by=["exit_date DESC"]。
    - 去重在 LIMIT 之前完成，metadata.total_count 与返回明细采用相同口径。

    【金额展示】查询总市值字段时，结果会同时包含后端确定性生成的“金额展示”。
    终答必须原样使用“金额展示”中的值，不得根据原始人民币金额再次换算量级。

    Args:
        table: 表名，必须从 get_available_tables 返回的列表中选择。
        select_columns: 需要返回的字段列表，每项为 schema 中的 column_key，最多 20 个。
                       建议只选需要的字段，避免返回过多数据。
        filters: 筛选条件列表，每项为 {field, type, value, same_item_group?}，
                 不能为空列表（至少一个条件）。
        order_by: 排序规则列表，如 ["financing_date DESC", "estimated_financing_amount_cny DESC"]。
                  子表字段不支持排序。可选，默认按主键倒序；指定排序时追加主键保证顺序稳定。
        limit: 旧版每页条数兼容参数，默认 50，限制在 1～50；新调用优先使用 pageSize。
        filter_operator: filters 之间的连接关系，只支持 AND 或 OR，默认 AND。
        distinct_by: 明细去重字段列表。仅支持主表或关联表的非表达式字段；默认不去重。
        page: 页码，从 1 开始，默认 1。仅允许访问前 500 条，最大页数随 pageSize 变化。
        pageSize: 每页条数，范围 1～50，默认 50；未指定时兼容 limit，显式指定时优先。

    Returns:
        查询结果列表及元数据：
        - data: 结果列表，每个元素为字典（字段名为中文）
        - metadata.total_count: 符合条件的真实总记录数
        - metadata.returned_rows: 本页实际返回行数
        - metadata.accessible_count: 可访问记录数，最多 500
        - metadata.page/pageSize/maxPage/hasMore: 当前页、每页条数、可访问最大页码、是否可继续翻页
        - metadata.limit: 本次 SQL 条数上限，500 条边界页可能小于 pageSize

### 输入 schema

```json
{
  "properties": {
    "table": {
      "title": "Table",
      "type": "string"
    },
    "select_columns": {
      "items": {
        "type": "string"
      },
      "title": "Select Columns",
      "type": "array"
    },
    "filters": {
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Filters",
      "type": "array"
    },
    "order_by": {
      "default": null,
      "items": {
        "type": "string"
      },
      "title": "Order By",
      "type": "array"
    },
    "limit": {
      "default": 50,
      "title": "Limit",
      "type": "integer"
    },
    "filter_operator": {
      "default": "AND",
      "enum": [
        "AND",
        "OR"
      ],
      "title": "Filter Operator",
      "type": "string"
    },
    "distinct_by": {
      "default": null,
      "items": {
        "type": "string"
      },
      "title": "Distinct By",
      "type": "array"
    },
    "page": {
      "default": 1,
      "description": "页码，从 1 开始，默认 1。仅支持访问前 500 条结果，最大可访问页数随 pageSize 变化。",
      "minimum": 1,
      "title": "Page",
      "type": "integer"
    },
    "pageSize": {
      "anyOf": [
        {
          "maximum": 50,
          "minimum": 1,
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "description": "每页条数，范围 1～50；未指定时使用旧 limit，默认 50。显式指定时优先于 limit。连续翻页保持筛选、排序和 pageSize 一致，500 条边界页可能不足一页。",
      "title": "Pagesize"
    }
  },
  "required": [
    "table",
    "select_columns",
    "filters"
  ],
  "title": "execute_queryArguments",
  "type": "object"
}
```

## execute_aggregate_query

执行聚合查询（统计/分析）。

    【使用场景】适用于所有统计、分析、汇总类需求，典型场景：
    - 整体统计："总共有多少条记录"、"总托管行规模"、"整体平均值"
    - 按维度统计数量："各赛道有多少家公司"、"各省份有多少支基金"
    - 按维度求和/平均："各省份基金的平均规模"、"各投资机构累计投资金额"
    - 按维度求最大/最小："每个赛道最新的融资日期"
    - 去重计数："每个投资机构投资了多少家不同公司"
    - 按时间趋势："近年融资事件数量走势"、"各季度投资金额" —— 需配合 date_granularity

    【强制前置条件】必须先调用 get_table_schema(table_name=xxx) 确认可用字段。

    【支持的聚合函数】
    - sum: 求和。例：{"field": "reg_cap_cny", "func": "sum", "alias": "总注册资本"}
    - avg: 平均值。例：{"field": "reg_cap_cny", "func": "avg", "alias": "平均注册资本"}
    - max/min: 最大/最小值。例：{"field": "latest_financing_date", "func": "max", "alias": "最新融资日期"}
    - count: 对具体字段生成 COUNT(字段)，不统计 NULL。例：{"field": "company_id", "func": "count", "alias": "非空公司数"}
    - count_distinct: 生成 COUNT(DISTINCT 字段)，用于显式去重计数。
    - count(*): 统计行数请传 {"field": "*", "func": "count", "alias": "总数"}
    - event_count: 事件数据集的标准业务事件数指标。传
      {"metric": "event_count", "alias": "事件数"}，服务端根据 get_table_schema 返回的
      business_event_id 自动生成 COUNT(DISTINCT 业务事件ID)。统计事件数必须优先使用此指标。

    【group_by 说明】
    group_by 是可选参数，不是所有聚合查询都需要填写。

    一、全局聚合
    当用户只要求筛选结果的整体统计值，没有要求按某个维度拆分时，使用全局聚合：
    - 可以省略 group_by，也可以传 group_by=[]；
    - 不要为了填写 group_by 而虚构字段；
    - 全局聚合正常返回一行，只包含 metrics 指标列。
    - 全局聚合最多返回一行，服务端不会生成 LIMIT；limit 只对带 group_by 的分组结果生效。

    全局聚合示例：
    group_by=[]
    metrics=[
      {"field": "*", "func": "count", "alias": "总数"},
      {"field": "托管行规模", "func": "sum", "alias": "规模总和"}
    ]

    二、分组聚合
    当用户要求按省份、机构、基金类型、年份、季度等维度分别统计时，必须将对应真实字段放入 group_by。
    - group_by 字段可以是主表字段或子表字段。
    - 子表字段作为 group_by 时，是按底层原始值聚合（如 gp.gp_name），不是按数组聚合。
      例：group_by=["investor_names"] 会按每个投资机构名称单独分组，而不是按投资机构列表分组。

    三、字段来源与统计计算
    - 所有 table、group_by、metrics.field 和 filters.field 必须先通过 get_table_schema 确认。
    - 不得填写不存在、无关或虚构的 group_by 字段。
    - 总数、总和、平均值、最大值、最小值、分布或趋势应由 execute_aggregate_query 在 Doris 中计算，
      不要使用 execute_query 拉取明细后在模型侧自行累加。
    - 占比、增长率、差值等二次计算，应先获取数据库聚合结果，不要伪装成 group_by。

    【融资轮次规则】按融资轮次筛选、统计、分组或透视时，filters 和 group_by 必须使用聚合轮次字段 latest_financing_round_consol 或 financing_round_consol。不得使用明细轮次字段 latest_financing_round 或 financing_round 作为分析维度。

    【date_granularity 说明】
    - 可选。对 group_by 中的 date 字段按年/半年/季/月分桶，值为 year / halfyear / quarter / month。
    - 例：group_by=["financing_date"], date_granularity={"financing_date": "year"}
      → 返回 "2023"、"2024" 等年度桶，而非按天分组。
    - 例：date_granularity={"financing_date": "halfyear"} → 返回 "2024-H1"、"2024-H2"（上/下半年）
    - 例：date_granularity={"financing_date": "quarter"} → 返回 "2024-Q1"、"2024-Q2"
    - 例：date_granularity={"financing_date": "month"} → 返回 "2024-01"、"2024-02"
    - 字段必须同时在 group_by 中，且类型为 date；未指定粒度的日期字段仍按天分组。

    【metrics 说明】
    - alias 由调用方传入，原样返回（不自动映射中文）。如需中文展示，请在 alias 中直接传入中文。
    - metrics 中的字段可以是主表字段或子表字段。
    - 事件数据集统计事件数时使用 {"metric": "event_count", "alias": "事件数"}；
      不得用 COUNT(*) 代替。包含一对多子表分组时，服务端会拒绝 COUNT(*)。

    【filters 说明】
    - 格式同 execute_query，可选。有 filters 时可提升查询精度。
    - 支持 same_item_group，同组数组字段会在聚合前合并为一个成员级 EXISTS。
    - 交易方角色与基金、LP、地区、金额等交易方属性必须命中同一成员；仅有一个
      交易方身份时服务端自动补全遗漏分组，同时包含多个身份时必须显式分组。
    - 无 filters 时 limit 自动限制为 20，防止全表扫描。

    【order_by 说明】
    - 支持引用 group_by 字段或 metrics 的 alias。
    - 全局聚合只能引用 metrics 的 alias。
    - 例：["总规模 DESC"] 表示按聚合指标 "总规模" 降序排列。
    - 对带 date_granularity 的日期字段排序时，按分桶字符串的字典序（即时间序）。

    Args:
        table: 表名，必须从 get_available_tables 返回的列表中选择。
        group_by: 可选分组字段列表。整体统计时省略或传空数组；分组统计时传真实维度字段。
        metrics: 聚合指标列表。普通指标格式为
                 {"field": "字段名", "func": "聚合函数", "alias": "返回别名"}；
                 业务事件数格式为 {"metric": "event_count", "alias": "事件数"}。
                 至少 1 个指标，alias 不可重复。
        filters: 筛选条件列表（可选），格式同 execute_query。用于在聚合前过滤数据。
        order_by: 排序规则列表（可选），支持引用 group_by 字段或 metrics alias，如 ["alias_name DESC"]。
        limit: 返回最大分组数，默认 50，最大 50。仅对带 group_by 的查询生效；
               无 group_by 的全局聚合不生成 LIMIT。无过滤条件的分组查询自动限制为 20。
        date_granularity: 日期分桶映射（可选），如 {"financing_date": "year"}，取值 year/halfyear/quarter/month。

    Returns:
        success/data/metadata 结构。全局聚合正常返回一行指标；分组聚合每行包含
        group_by 字段值和 metrics alias。metadata 包含 table、returned_rows 和 limit。

### 输入 schema

```json
{
  "properties": {
    "table": {
      "title": "Table",
      "type": "string"
    },
    "group_by": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Group By"
    },
    "metrics": {
      "anyOf": [
        {
          "items": {
            "additionalProperties": true,
            "type": "object"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null,
      "title": "Metrics"
    },
    "filters": {
      "default": null,
      "items": {
        "additionalProperties": true,
        "type": "object"
      },
      "title": "Filters",
      "type": "array"
    },
    "order_by": {
      "default": null,
      "items": {
        "type": "string"
      },
      "title": "Order By",
      "type": "array"
    },
    "limit": {
      "default": 50,
      "title": "Limit",
      "type": "integer"
    },
    "date_granularity": {
      "additionalProperties": true,
      "default": null,
      "title": "Date Granularity",
      "type": "object"
    }
  },
  "required": [
    "table"
  ],
  "title": "execute_aggregate_queryArguments",
  "type": "object"
}
```
