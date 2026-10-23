# DDL 模板与设计模式

> **何时使用本文件**：生成 CREATE TABLE DDL 时参考模板；MySQL 迁移时参考类型映射。
> **何时不使用**：选择数据模型/分区/分桶（参考 engine-selection-guide.md）；SQL 查询优化。

## 目录

- [§1 通用 DDL 模板](#1-通用-ddl-模板)
- [§2 典型业务场景模板](#2-典型业务场景模板)
- [§3 MySQL 迁移类型映射](#3-mysql-迁移类型映射)
- [§4 动态分区与冷热分层](#4-动态分区与冷热分层)
- [§5 ALTER TABLE 优化语句](#5-alter-table-优化语句)

---

## §1 通用 DDL 模板

### DUPLICATE KEY 模板（明细模型）

```sql
CREATE TABLE `{database}`.`{table_name}`
(
    -- 时间字段（分区键 + KEY 列首字段）
    `{date_col}` DATE COMMENT '数据日期',
    -- 维度字段（KEY 列）
    `{dim_col}` VARCHAR(64) COMMENT '维度字段',
    -- 业务主键
    `{id_col}` BIGINT COMMENT '业务主键',
    -- 指标字段
    `{metric_col}` DECIMAL(20,4) COMMENT '指标字段',
    -- 时间戳
    `{ts_col}` DATETIME COMMENT '事件时间'
)
DUPLICATE KEY(`{date_col}`, `{dim_col}`, `{id_col}`)
COMMENT '表注释说明'
PARTITION BY RANGE(`{date_col}`)()
DISTRIBUTED BY HASH(`{id_col}`) BUCKETS 32
PROPERTIES(
    "replication_num" = "3",
    "bloom_filter_columns" = "{id_col}",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-90",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "32"
);
```

### UNIQUE KEY 模板（去重模型，推荐 MoW）

```sql
CREATE TABLE `{database}`.`{table_name}`
(
    `{id_col}` BIGINT COMMENT '业务主键（去重键）',
    `{date_col}` DATE COMMENT '数据日期',
    `{field1}` VARCHAR(255) COMMENT '字段1',
    `{field2}` DECIMAL(20,4) COMMENT '字段2',
    `update_time` DATETIME COMMENT '更新时间'
)
UNIQUE KEY(`{id_col}`)
COMMENT '主键去重表'
DISTRIBUTED BY HASH(`{id_col}`) BUCKETS 32
PROPERTIES(
    "replication_num" = "3",
    "enable_unique_key_merge_on_write" = "true"
);
```

### AGGREGATE KEY 模板（预聚合模型）

```sql
CREATE TABLE `{database}`.`{table_name}`
(
    `{date_col}` DATE COMMENT '统计日期',
    `{dim1}` VARCHAR(64) COMMENT '维度1',
    `{dim2}` VARCHAR(64) COMMENT '维度2',

    -- VALUE 列（聚合函数）
    `{metric1}` BIGINT SUM DEFAULT "0" COMMENT '计数指标',
    `{metric2}` DECIMAL(20,4) SUM DEFAULT "0" COMMENT '金额指标',
    `uv_bitmap` BITMAP BITMAP_UNION COMMENT '去重 UV'
)
AGGREGATE KEY(`{date_col}`, `{dim1}`, `{dim2}`)
COMMENT '预聚合汇总表'
PARTITION BY RANGE(`{date_col}`)()
DISTRIBUTED BY HASH(`{dim1}`) BUCKETS 16
PROPERTIES(
    "replication_num" = "3",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "MONTH",
    "dynamic_partition.start" = "-12",
    "dynamic_partition.end" = "1",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "16"
);
```

## §2 典型业务场景模板

### 电商订单明细表

```sql
CREATE TABLE `analytics`.`orders`
(
    `order_date` DATE COMMENT '订单日期',
    `channel` VARCHAR(32) COMMENT '渠道来源',
    `user_id` BIGINT COMMENT '用户ID',
    `order_id` BIGINT COMMENT '订单ID',
    `product_id` BIGINT COMMENT '商品ID',
    `category` VARCHAR(64) COMMENT '商品类目',
    `amount` DECIMAL(18,2) COMMENT '订单金额',
    `quantity` INT COMMENT '商品数量',
    `status` VARCHAR(32) COMMENT '订单状态',
    `pay_time` DATETIME COMMENT '支付时间',
    `create_time` DATETIME COMMENT '创建时间'
)
DUPLICATE KEY(`order_date`, `channel`, `user_id`, `order_id`)
COMMENT '电商订单明细表，日增约5000万条，按天分区'
PARTITION BY RANGE(`order_date`)()
DISTRIBUTED BY HASH(`order_id`) BUCKETS 32
PROPERTIES(
    "replication_num" = "3",
    "bloom_filter_columns" = "user_id, product_id, order_id",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-365",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "32"
);
```

### 用户行为日志表（含倒排索引）

```sql
CREATE TABLE `analytics`.`user_events`
(
    `event_date` DATE COMMENT '事件日期',
    `event_type` VARCHAR(32) COMMENT '事件类型',
    `user_id` BIGINT COMMENT '用户ID',
    `event_time` DATETIME(3) COMMENT '事件时间（毫秒精度）',
    `page` VARCHAR(512) COMMENT '页面路径',
    `referrer` VARCHAR(512) COMMENT '来源页面',
    `device` VARCHAR(32) COMMENT '设备类型',
    `os` VARCHAR(32) COMMENT '操作系统',
    `city` VARCHAR(64) COMMENT '城市',
    `properties` VARIANT COMMENT '事件属性（半结构化）',

    INDEX idx_page(`page`) USING INVERTED PROPERTIES("parser"="english") COMMENT '页面路径倒排索引'
)
DUPLICATE KEY(`event_date`, `event_type`, `user_id`, `event_time`)
COMMENT '用户行为日志表，保留90天，按天分区'
PARTITION BY RANGE(`event_date`)()
DISTRIBUTED BY HASH(`user_id`) BUCKETS 64
PROPERTIES(
    "replication_num" = "3",
    "bloom_filter_columns" = "user_id",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",
    "dynamic_partition.start" = "-90",
    "dynamic_partition.end" = "3",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "64"
);
```

### 用户画像表（去重更新，UNIQUE KEY MoW）

```sql
CREATE TABLE `analytics`.`user_profiles`
(
    `user_id` BIGINT COMMENT '用户ID（去重键）',
    `nickname` VARCHAR(64) COMMENT '昵称',
    `gender` VARCHAR(8) COMMENT '性别',
    `age` TINYINT COMMENT '年龄',
    `city` VARCHAR(64) COMMENT '城市',
    `level` VARCHAR(16) COMMENT '会员等级',
    `total_orders` INT COMMENT '累计订单数',
    `total_amount` DECIMAL(18,2) COMMENT '累计消费金额',
    `last_login_time` DATETIME COMMENT '最后登录时间',
    `tags` ARRAY<VARCHAR(64)> COMMENT '用户标签',
    `update_time` DATETIME COMMENT '更新时间'
)
UNIQUE KEY(`user_id`)
COMMENT '用户画像表，按 user_id 去重保留最新版本'
DISTRIBUTED BY HASH(`user_id`) BUCKETS 32
PROPERTIES(
    "replication_num" = "3",
    "enable_unique_key_merge_on_write" = "true",
    "store_row_column" = "true"  -- 启用行存以加速点查
);
```

### 实时统计汇总表（AGGREGATE + BITMAP UV）

```sql
CREATE TABLE `analytics`.`daily_channel_stats`
(
    `stat_date` DATE COMMENT '统计日期',
    `channel` VARCHAR(32) COMMENT '渠道',
    `product_category` VARCHAR(64) COMMENT '商品类目',

    `order_count` BIGINT SUM DEFAULT "0" COMMENT '订单数',
    `uv_bitmap` BITMAP BITMAP_UNION COMMENT '用户去重 UV',
    `total_amount` DECIMAL(18,2) SUM DEFAULT "0" COMMENT '总金额',
    `refund_count` BIGINT SUM DEFAULT "0" COMMENT '退款数'
)
AGGREGATE KEY(`stat_date`, `channel`, `product_category`)
COMMENT '每日渠道统计汇总表'
PARTITION BY RANGE(`stat_date`)()
DISTRIBUTED BY HASH(`channel`) BUCKETS 8
PROPERTIES(
    "replication_num" = "3",
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "MONTH",
    "dynamic_partition.start" = "-24",
    "dynamic_partition.end" = "1",
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "8"
);
```

## §3 MySQL 迁移类型映射

### 数据类型映射表

| MySQL 类型 | Doris 类型 | 说明 |
|-----------|-----------|------|
| `TINYINT` | `TINYINT` | 1 字节 |
| `SMALLINT` | `SMALLINT` | 2 字节 |
| `INT` | `INT` | 4 字节 |
| `BIGINT` | `BIGINT` | 8 字节 |
| `FLOAT` | `FLOAT` | |
| `DOUBLE` | `DOUBLE` | |
| `DECIMAL(P,S)` | `DECIMAL(P,S)` / `DECIMALV3` | 精度一致；推荐 V3 |
| `VARCHAR(N)` | `VARCHAR(N)` | N 表示字节数 |
| `TEXT` | `STRING` | 不超过 2GB |
| `CHAR(N)` | `CHAR(N)` | 定长 |
| `DATE` | `DATE` / `DATEV2` | 推荐 V2 |
| `DATETIME` | `DATETIME` / `DATETIMEV2(0)` | 秒精度 |
| `DATETIME(3)` | `DATETIMEV2(3)` | 毫秒精度 |
| `TIMESTAMP` | `DATETIME` | |
| `BOOLEAN` / `TINYINT(1)` | `BOOLEAN` | |
| `ENUM(...)` | `VARCHAR(N)` | Doris 无 ENUM 类型 |
| `JSON` | `JSON` 或 `VARIANT`（2.1+） | VARIANT 支持半结构化 |
| `BLOB` / `BINARY` | `STRING` | |

### 迁移注意事项

| MySQL 特性 | Doris 处理方式 |
|-----------|---------------|
| AUTO_INCREMENT | 不直接支持，业务侧生成 ID（雪花算法等）；2.1+ 支持 AUTO_INCREMENT 列 |
| NULL 值 | 显式声明 NULL/NOT NULL，建议给默认值减少 NULL 列 |
| 外键约束 | 不支持，应用层保证 |
| 唯一索引 | 用 UNIQUE KEY 模型实现 |
| 事务 | 单表导入是原子的；多表事务通过 Stream Load 2PC 或不支持 |
| UPDATE/DELETE | UNIQUE 模型支持 UPDATE / DELETE；DUPLICATE 模型仅支持 DELETE 按 KEY |

### MySQL DDL 转换示例

**MySQL 原表**：
```sql
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_status (status)
);
```

**Doris 转换后**（业务有更新需求，选 UNIQUE KEY MoW）：
```sql
CREATE TABLE `analytics`.`orders`
(
    `id` BIGINT COMMENT '订单ID',
    `user_id` BIGINT COMMENT '用户ID',
    `amount` DECIMAL(10,2) DEFAULT "0" COMMENT '订单金额',
    `status` VARCHAR(32) DEFAULT 'pending' COMMENT '订单状态',
    `created_at` DATETIME COMMENT '创建时间',
    `updated_at` DATETIME COMMENT '更新时间'
)
UNIQUE KEY(`id`)
COMMENT '订单表'
DISTRIBUTED BY HASH(`id`) BUCKETS 32
PROPERTIES(
    "replication_num" = "3",
    "enable_unique_key_merge_on_write" = "true",
    "bloom_filter_columns" = "user_id"
);
```

**转换要点**：
1. 主键 + 更新场景 → UNIQUE KEY 模型 + MoW
2. AUTO_INCREMENT 由业务生成，或使用 Doris 2.1+ AUTO_INCREMENT
3. MySQL 二级索引（user_id/status）→ BLOOM_FILTER（高基数）或 KEY 列前列（低基数）
4. 如纯追加写入则改用 DUPLICATE KEY，并以 created_at 做分区键

## §4 动态分区与冷热分层

### 动态分区配置

```sql
PROPERTIES(
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "DAY",          -- HOUR/DAY/WEEK/MONTH/YEAR
    "dynamic_partition.start" = "-90",              -- 保留过去 90 天
    "dynamic_partition.end" = "3",                  -- 预创建未来 3 天
    "dynamic_partition.prefix" = "p",
    "dynamic_partition.buckets" = "32",
    "dynamic_partition.replication_num" = "3"
);
```

### 冷热分层（迁移到 COS）

```sql
-- 1) 创建冷数据存储策略（DBA 操作，需 ADMIN）
CREATE STORAGE POLICY cool_policy
PROPERTIES(
    "storage_resource" = "cos_resource",
    "cooldown_ttl" = "604800"   -- 7 天后变冷
);

-- 2) 表上启用
ALTER TABLE `analytics`.`orders`
SET("storage_policy" = "cool_policy");
```

## §5 ALTER TABLE 优化语句

### 添加 BLOOM_FILTER

```sql
ALTER TABLE `{db}`.`{table}` SET("bloom_filter_columns" = "user_id, trace_id");
```

> ⚠️ **语法限制**：Bloom Filter **不能**使用 `CREATE INDEX ... USING BLOOM_FILTER` 或在 CREATE TABLE 里写 `INDEX xxx USING BLOOM_FILTER` 语法（这是从 INVERTED INDEX 误推的常见写法）。Doris 中 Bloom Filter **只能**通过表级 `PROPERTIES` 中的 `bloom_filter_columns` 配置，可在 CREATE TABLE 的 PROPERTIES 里设置，也可后续用上述 ALTER TABLE SET 改动。
>
> ❌ 错误写法：
> ```sql
> -- 以下三种都会报语法错误
> CREATE INDEX idx_uid ON tbl(user_id) USING BLOOM_FILTER;
> ALTER TABLE tbl ADD INDEX idx_uid(user_id) USING BLOOM_FILTER;
> -- CREATE TABLE ... ( ..., INDEX idx_uid(user_id) USING BLOOM_FILTER ) ...
> ```
>
> ✅ 正确写法：见本节上方 ALTER 语句，以及§2.1 / §2.2 / §2.3 模板中 `PROPERTIES ("bloom_filter_columns" = "...")` 的示例。

### 添加倒排索引（INVERTED INDEX，2.0+）

```sql
CREATE INDEX idx_message ON `{db}`.`{table}`(`message`)
USING INVERTED PROPERTIES("parser"="english") COMMENT '消息倒排';

-- 对存量数据 BUILD（异步）
BUILD INDEX idx_message ON `{db}`.`{table}`;
```

### 修改动态分区

```sql
ALTER TABLE `{db}`.`{table}` SET("dynamic_partition.start"="-180");
```

### 修改副本数

```sql
ALTER TABLE `{db}`.`{table}` SET("default.replication_num"="3");
ALTER TABLE `{db}`.`{table}` MODIFY PARTITION (p20260616) SET("replication_num"="3");
```

### 添加列

```sql
ALTER TABLE `{db}`.`{table}` ADD COLUMN `{col}` {TYPE} DEFAULT "{default}" COMMENT '{comment}';
```

### 启用 UNIQUE KEY 行存（点查加速）

```sql
ALTER TABLE `{db}`.`{table}` SET("store_row_column" = "true");
```

### 调整分桶（需重建表）

> Doris 不支持在线调整 BUCKETS 数（除少数版本支持 BUCKETS 重新分布），通常通过新建表 + INSERT 迁移完成。
