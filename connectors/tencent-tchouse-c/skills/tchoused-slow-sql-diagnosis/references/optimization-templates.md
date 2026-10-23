# SQL 优化方案模板

> **何时使用本文件**：在步骤 4.3（瓶颈识别后生成优化建议）时，根据识别到的问题类型选择对应的优化方案模板。
> **何时不使用**：瓶颈识别规则请参考 `analysis-framework.md §1`；工具调用参数请参考主文件。

---

## 目录

- [§1 SQL 改写方案](#1-sql-改写方案)
- [§2 索引方案](#2-索引方案)
- [§3 分桶/Colocate 调整方案](#3-分桶colocate-调整方案)
- [§4 物化视图方案](#4-物化视图方案)
- [§5 Session 配置调优方案](#5-session-配置调优方案)

---

## §1 SQL 改写方案

### 1.1 添加分区过滤条件

**适用场景**：分区裁剪失败，WHERE 条件未包含分区键字段。

```sql
-- ❌ 原始（扫描所有分区）
SELECT channel, SUM(amount) FROM orders WHERE status = 'paid' GROUP BY channel;

-- ✅ 改写（添加分区键过滤，假设分区键为 order_date）
SELECT channel, SUM(amount) FROM orders
WHERE order_date >= '2026-05-01' AND status = 'paid'
GROUP BY channel;
```

**改写说明**：添加分区键字段过滤条件，将扫描范围从全量分区收敛至目标时间范围。`EXPLAIN` 中可见 `partitions=A/B`，A 远小于 B 即生效。

### 1.2 调整 JOIN 顺序 / 使用 Hint

**适用场景**：右表过大被 BROADCAST，可能 OOM；或本可 Colocate 但被识别为 Shuffle。

```sql
-- ❌ 原始（小表 LEFT JOIN 大表，但右表是大表，仍被 broadcast）
SELECT * FROM users u LEFT JOIN orders o ON u.id = o.uid;

-- ✅ 改写（大表在左侧，避免大表 broadcast）
SELECT * FROM orders o RIGHT JOIN users u ON o.uid = u.id;

-- ✅ 或使用 Hint 强制 Shuffle
SELECT /*+ SET_VAR(disable_join_reorder=true) */ ...
SELECT * FROM tbl1 JOIN [shuffle] tbl2 ON tbl1.id = tbl2.id;
SELECT * FROM tbl1 JOIN [broadcast] tbl2 ON tbl1.id = tbl2.id;
```

**改写说明**：Doris 默认尽量将右表 BROADCAST，需确保右表是小表；大表对大表用 SHUFFLE 或 Colocate。

### 1.3 避免 SELECT *

**适用场景**：宽表（列数 > 50）上使用 SELECT *。

```sql
-- ❌ 原始
SELECT * FROM wide_table WHERE id = 123;

-- ✅ 改写（只选需要的列）
SELECT id, name, amount, created_at FROM wide_table WHERE id = 123;
```

**改写说明**：Doris 列式存储，每列独立读取，SELECT * 读取所有列文件，IO 开销与列数成正比。AGGREGATE 模型下 SELECT 非 KEY 非聚合列还会关闭 PREAGGREGATION。

### 1.4 子查询改写为 JOIN

**适用场景**：IN (SELECT ...) 子查询。

```sql
-- ❌ 原始
SELECT * FROM order_items WHERE sku_id IN (SELECT sku_id FROM hot_skus WHERE category = 'electronics');

-- ✅ 改写
SELECT oi.* FROM order_items oi
INNER JOIN hot_skus hs ON oi.sku_id = hs.sku_id
WHERE hs.category = 'electronics';
```

### 1.5 使用子查询预过滤

**适用场景**：JOIN 前可以先大幅缩小数据量。

```sql
-- ❌ 原始（先 JOIN 再过滤）
SELECT o.*, u.name FROM orders o JOIN users u ON o.uid = u.id
WHERE o.amount > 1000 AND o.date >= '2026-05-01';

-- ✅ 改写（先过滤再 JOIN）
SELECT o.*, u.name FROM
  (SELECT * FROM orders WHERE amount > 1000 AND date >= '2026-05-01') o
JOIN users u ON o.uid = u.id;
```

### 1.6 增强 RuntimeFilter

**适用场景**：JOIN 探测端扫描数据量大，但小表能过滤大量数据。

```sql
-- 全局 RF 模式（默认 LOCAL）
SELECT /*+ SET_VAR(runtime_filter_mode=GLOBAL) */ ...
```

---

## §2 索引方案

### 2.1 BLOOM_FILTER 索引

**适用场景**：高基数列的等值/IN 查询。

```sql
-- 建表时
CREATE TABLE ... PROPERTIES (
  "bloom_filter_columns" = "user_id, trace_id"
);

-- 已有表
ALTER TABLE db.tbl SET ("bloom_filter_columns" = "user_id, trace_id");
```

**说明**：BLOOM_FILTER 对高基数列等值查询效果好；不适合低基数列。

### 2.2 INVERTED INDEX 倒排索引（Doris 2.0+）

**适用场景**：字符串模糊匹配（LIKE / MATCH_ANY / MATCH_ALL）、JSON 检索、高基数等值。

```sql
-- 建表时
CREATE TABLE logs (
  ...
  message VARCHAR(2048),
  INDEX idx_message (message) USING INVERTED PROPERTIES("parser"="english")
) ...

-- 已有表添加
CREATE INDEX idx_message ON db.logs(message) USING INVERTED PROPERTIES("parser"="english");
-- 必要时对存量数据 BUILD
BUILD INDEX idx_message ON db.logs;
```

**说明**：Doris 2.0+ 引入，相比传统模糊查询性能提升 10-100 倍。`parser` 可选 `none`/`english`/`chinese`/`unicode`。

### 2.3 NGRAM_BF 索引

**适用场景**：字符串 LIKE '%xxx%' 查询，2.0 之前的版本。

```sql
ALTER TABLE db.tbl ADD INDEX idx_content(content) USING NGRAM_BF
PROPERTIES("gram_size"="3", "bf_size"="1024");
```

### 2.4 ZoneMap（自动）

**说明**：Doris 自动为所有列维护每个 Page 的 Min/Max，对范围查询有效。无需手动创建。

### 索引选择决策表

| 查询类型 | 字段特征 | 推荐索引 |
|---------|---------|---------|
| 范围查询（>, <, BETWEEN） | 数值/日期 | ZoneMap（自动）|
| 等值查询（=, IN） | 高基数（>1000） | BLOOM_FILTER |
| 等值查询（=, IN） | 低基数（<100） | 放入 KEY 列前列即可 |
| 模糊查询（LIKE / MATCH） | 字符串 | INVERTED INDEX（2.0+）/ NGRAM_BF |
| JSON 字段检索 | JSON | INVERTED INDEX |

---

## §3 分桶/Colocate 调整方案

**适用场景**：单 Tablet 数据过大或过小、JOIN 频繁但发生 Shuffle。

**注意**：调整分桶需要重建表，高成本操作。

### 分桶设计原则

1. 选高基数列做分桶键（避免数据倾斜）
2. 单 Tablet 大小目标 1-3 GB（过小：调度开销；过大：扫描慢）
3. BUCKETS 数 = 单分区数据量 / 1.5GB（向上取整）

### 重建表示例

```sql
-- 1. 创建新表
CREATE TABLE db.tbl_new (
  ... 同结构 ...
)
DUPLICATE KEY(...)
PARTITION BY RANGE(...)(...)
DISTRIBUTED BY HASH(user_id) BUCKETS 64  -- 调整后的分桶键和数量
PROPERTIES("replication_num"="3");

-- 2. 迁移数据
INSERT INTO db.tbl_new SELECT * FROM db.tbl_old;

-- 3. 原子交换（需用户确认）
ALTER TABLE db.tbl_old RENAME tbl_old_backup;
ALTER TABLE db.tbl_new RENAME tbl_old;
```

### Colocate Group 配置

**适用场景**：两张表频繁 JOIN，希望避免 Shuffle。

```sql
CREATE TABLE orders (...)
DISTRIBUTED BY HASH(user_id) BUCKETS 32
PROPERTIES("colocate_with" = "group_user", "replication_num"="3");

CREATE TABLE users (...)
DISTRIBUTED BY HASH(user_id) BUCKETS 32  -- 必须相同 BUCKETS
PROPERTIES("colocate_with" = "group_user", "replication_num"="3");
```

**约束**：分桶键类型/数量、BUCKETS 数、副本数必须一致。

---

## §4 物化视图方案

### 4.1 同步物化视图（Sync MV）

**适用场景**：单表聚合查询频繁（如日报/小时报）。

```sql
CREATE MATERIALIZED VIEW mv_hourly_stats AS
SELECT
  channel,
  DATE_TRUNC(created_at, 'hour') AS hour,
  SUM(amount) AS total_amount,
  COUNT(*) AS order_count
FROM db.orders
GROUP BY channel, hour;
```

**说明**：同步 MV 对原表写入实时同步，查询自动路由。仅支持单表 + 部分聚合函数。

### 4.2 异步物化视图（Async MV，2.1+）

**适用场景**：多表 JOIN 宽表、复杂查询预计算。

```sql
CREATE MATERIALIZED VIEW mv_order_detail
BUILD IMMEDIATE REFRESH AUTO ON SCHEDULE EVERY 1 HOUR
DISTRIBUTED BY HASH(user_id) BUCKETS 16
AS
SELECT o.order_id, o.order_date, o.amount, u.user_name, u.region
FROM db.orders o LEFT JOIN db.users u ON o.user_id = u.id;
```

**说明**：异步 MV 支持多表 JOIN，按调度刷新；查询透明改写到 MV。

---

## §5 Session 配置调优方案

| 配置项 | 默认值 | 调优建议 | 适用场景 |
|--------|--------|---------|---------|
| `exec_mem_limit` | 2GB | 根据节点内存调整，建议 ≤ 单 BE 内存的 50% | 大查询 OOM |
| `parallel_fragment_exec_instance_num` | 8 | 高并发场景调低（如 4），CPU 争抢严重时调低 | CPU 争抢 |
| `query_timeout` | 300（秒） | 建议设置 300-600 | 防止查询长时间挂起 |
| `disable_join_reorder` | false | 复杂 JOIN 想自定义顺序时设 true | 自定义 JOIN 顺序 |
| `runtime_filter_mode` | LOCAL | 复杂 JOIN 探测端大可设 GLOBAL | RF 增强 |
| `enable_pipeline_engine` | true（2.0+） | 建议保持开启 | 提升并行度 |
| `prefer_join_method` | broadcast | 大表对大表可改为 shuffle | JOIN 算法优化 |

**配置修改注意事项**：
- 配置修改属于写操作，本 Skill 仅给出建议，不直接执行
- 会话级：`SET exec_mem_limit = xxx;`
- 全局级：`SET GLOBAL exec_mem_limit = xxx;`（需 ADMIN 权限）
- 集群级：通过控制台修改 BE/FE 配置文件
