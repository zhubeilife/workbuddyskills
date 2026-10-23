# 数据模型选择与诊断指南

> **何时使用本文件**：设计新表需要选择数据模型时；诊断现有表结构是否合理时。
> **何时不使用**：SQL 性能优化（参考 tchoused-slow-sql-diagnosis）；数据查询分析（参考 tchoused-nl2sql-analysis）。

## 目录

- [§1 数据模型选择决策树](#1-数据模型选择决策树)
- [§2 各模型详解与适用场景](#2-各模型详解与适用场景)
- [§3 分区策略设计指南](#3-分区策略设计指南)
- [§4 分桶（Distribution）设计指南](#4-分桶distribution设计指南)
- [§5 索引设计指南](#5-索引设计指南)
- [§6 诊断检查清单](#6-诊断检查清单)

---

## §1 数据模型选择决策树

```
用户需求分析
    │
    ├─ 数据是否需要按主键去重 / 更新？
    │   ├─ 否（纯追加写入）
    │   │   ├─ 是否需要预聚合（写入时即聚合）？
    │   │   │   ├─ 否 → DUPLICATE KEY 模型（明细模型）
    │   │   │   └─ 是 → AGGREGATE KEY 模型（SUM/MAX/MIN/REPLACE/HLL_UNION/BITMAP_UNION）
    │   │   └─ 适用场景：日志、订单流水、事件流
    │   │
    │   └─ 是（需要按主键去重 / 更新）
    │       ├─ 是否需要部分列更新？
    │       │   ├─ 否 → UNIQUE KEY 模型（默认 Merge-on-Read 或 Merge-on-Write）
    │       │   └─ 是 → UNIQUE KEY + Partial Update（2.0+，需 Merge-on-Write）
    │       └─ 适用场景：用户画像、维度表、CDC 同步、订单状态实时更新
    │
    └─ 特殊场景
        ├─ 高 QPS 点查（按主键查） → UNIQUE KEY + Merge-on-Write + Row Store
        ├─ 高基数 UV 计算 → AGGREGATE + BITMAP_UNION 列
        ├─ 近似 UV 计算 → AGGREGATE + HLL_UNION 列
        └─ 多表 JOIN 频繁 → Colocate Group + 物化视图
```

## §2 各模型详解与适用场景

### DUPLICATE KEY（明细模型）

| 属性 | 说明 |
|------|------|
| 适用场景 | 日志、事件流、订单明细等纯追加写入场景 |
| 数据特点 | 不去重不聚合，KEY 列仅用于排序和前缀索引 |
| 查询模式 | 按时间范围 + 维度过滤，按维度聚合 |
| 优势 | 写入性能最高，明细数据完整保留 |
| 劣势 | 占用空间大，无去重 |
| 建表关键字 | `DUPLICATE KEY(...)` |

### UNIQUE KEY（主键模型）

| 属性 | 说明 |
|------|------|
| 适用场景 | 需要按主键去重，保留最新版本 |
| 去重时机 | Merge-on-Read（查询时合并）/ Merge-on-Write（写入时合并，2.0+） |
| 推荐 | 2.0+ 强烈推荐 Merge-on-Write（查询性能更好） |
| 部分列更新 | 2.0+ MoW 支持 Partial Update |
| 典型用例 | 用户画像表、维度表、CDC 同步 |
| 建表关键字 | `UNIQUE KEY(...)` + `enable_unique_key_merge_on_write=true` |

```sql
CREATE TABLE user_profile (
  user_id BIGINT,
  name VARCHAR(64),
  city VARCHAR(64),
  update_time DATETIME
)
UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 32
PROPERTIES(
  "replication_num"="3",
  "enable_unique_key_merge_on_write"="true"
);
```

### AGGREGATE KEY（聚合模型）

| 属性 | 说明 |
|------|------|
| 适用场景 | 需要预聚合，只关心聚合结果 |
| 聚合方式 | 按 KEY 列分组，VALUE 列指定聚合函数 |
| 聚合时机 | 写入和 Compaction 时聚合 |
| 支持函数 | SUM / MAX / MIN / REPLACE / HLL_UNION / BITMAP_UNION |
| 典型用例 | 实时报表、UV 计算、汇总指标 |

```sql
CREATE TABLE daily_stats (
  dt DATE,
  channel VARCHAR(32),
  pv BIGINT SUM,
  uv BITMAP BITMAP_UNION,
  amount DECIMAL(20,4) SUM
)
AGGREGATE KEY(dt, channel)
PARTITION BY RANGE(dt)(...)
DISTRIBUTED BY HASH(channel) BUCKETS 16
PROPERTIES("replication_num"="3");
```

### Merge-on-Write vs Merge-on-Read（UNIQUE KEY）

| 维度 | MoR | MoW |
|------|-----|-----|
| 查询性能 | 较慢（需运行时合并） | 快（写入时已合并） |
| 写入性能 | 快 | 略慢 |
| 部分列更新 | 不支持 | 支持（2.0+） |
| 适用 | 旧版本/对写入要求极高 | 推荐生产使用 |

## §3 分区策略设计指南

### 分区类型

Doris 支持两种分区：
- **RANGE 分区**：按时间/数值范围（最常用）
- **LIST 分区**：按枚举值列表

### 分区粒度选择

| 日增数据量 | 推荐分区粒度 | 分区表达式 | 备注 |
|-----------|-------------|-----------|------|
| < 100 万行 | 按月 | `RANGE(dt) ... PARTITION p202601 VALUES LESS THAN ('2026-02-01')` | — |
| 100 万 ~ 1 亿行 | 按天 | `RANGE(dt)` 按天 | 推荐 |
| > 1 亿行 | 按天，必要时按小时 | RANGE(dt) | 谨慎使用小时级 |

### 动态分区（推荐）

对时间序列表，强烈推荐启用动态分区，自动创建/淘汰分区：

```sql
PROPERTIES(
  "dynamic_partition.enable"="true",
  "dynamic_partition.time_unit"="DAY",
  "dynamic_partition.start"="-90",       -- 保留 90 天
  "dynamic_partition.end"="3",           -- 预创建 3 天
  "dynamic_partition.prefix"="p",
  "dynamic_partition.buckets"="32"
);
```

### 分区设计原则

1. **单分区数据量**：建议单分区单副本 1-100 GB
2. **活跃分区数**：建议 < 1000（过多影响 FE 元数据）
3. **查询必须命中分区键**：WHERE 条件必须包含分区字段
4. **冷热分层**：超过 N 天的分区可设置冷热策略迁移到 COS

### 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 按小时分区 | 分区数过多 | 改为按天 + 合理分桶 |
| 不分区 | 全表扫描 | 添加时间分区 |
| 分区键不在 WHERE 中 | 查询扫描所有分区 | 调整查询或分区策略 |
| 未启用动态分区 | 历史数据无人维护 | 启用 dynamic_partition |

## §4 分桶（Distribution）设计指南

### 分桶设计原则

1. **选高基数列做分桶键**：避免数据倾斜（如 user_id、order_id）
2. **JOIN 频繁则按 JOIN 列分桶**：开启 Colocate Join
3. **单 Tablet 大小目标 1-3 GB**：过小→调度开销大；过大→扫描慢
4. **BUCKETS 数公式**：`单分区压缩后大小 / 1.5 GB`，向上取整

### §4.1 从行数估算单分区字节数（用户只给行数时使用）

用户描述业务时通常只给「日增行数」，不会给出「单行字节数」或「单分区 GB」。此时 **不要凭空拍脑袋**，按以下三步换算：

**Step 1：按业务类型查单行字节参考表**（Doris 压缩后估算值，已考虑列存 + ZSTD/LZ4 压缩，压缩比按 3-5× 折算）：

| 业务类型 | 典型列构成 | 单行原始大小 | 单行**压缩后**估算 | 备注 |
|---------|-----------|-------------|------------------|------|
| 埋点/行为日志 | 10-20 列，多短字符串 + 少量数值 | 400-800 B | **80-150 B** | event_id、user_id、ts、page、若干属性 |
| 订单/交易流水 | 20-40 列，含金额/状态/时间 | 500-1000 B | **150-250 B** | order_id、user_id、金额、状态、多时间戳 |
| 用户画像/维度表 | 30-80 列，标签为主 | 1-3 KB | **300-600 B** | 高基数字符串多 |
| IoT/监控指标 | 5-15 列，数值为主 | 100-300 B | **30-80 B** | ts、device_id、指标值 |
| CDC 同步表（宽表） | 50-200 列，混合类型 | 2-8 KB | **500 B-1.5 KB** | 与源库字段数强相关 |
| 文本/内容表（含长文本） | 5-20 列，含 TEXT/JSON | 2-20 KB | **1-5 KB** | 长文本压缩比高但总量大 |
| 广告曝光/点击 | 15-30 列，多枚举 + ID | 300-600 B | **60-120 B** | 枚举列压缩比极高 |

> ⚠️ 参考表给的是**压缩后**大小（Doris 磁盘占用），可直接用于分桶容量测算。若用户能提供实际的 `SHOW DATA` 或历史表磁盘占用，**优先用实测值**。

**Step 2：估算单分区压缩后大小**

```
单分区压缩后大小(GB) = 日增行数 × 单行压缩字节 / 1024³
```

按天分区时"单分区数据量" = 日增数据量；按月分区时 × 30；按小时分区时 ÷ 24。

**Step 3：套 BUCKETS 公式**

```
buckets = ceil(单分区压缩后大小 / 1.5 GB)
```

边界规则：
- 单分区 < 1 GB → `buckets = 1`（维度表可考虑 `RANDOM` 或单分桶）
- 单分区 1-100 GB → 按公式计算
- 单分区 > 100 GB → 优先考虑**收细分区粒度**（如日改小时、或加二级 LIST 分区），而不是把 buckets 无限调大

**换算示例**（用户输入："订单表，日增 5000 万行，按天分区，按 order_id 分桶"）：

1. 查表：订单/交易流水 → 单行压缩后取中位 **200 B**
2. 单分区大小 = 5000 万 × 200 B / 1024³ ≈ **9.3 GB**
3. buckets = ceil(9.3 / 1.5) = **7** → 建议取 **8**（凑 2 的幂或对齐 BE 数量倍数）

> 💡 **不确定时的表达方式**：若用户业务与参考表都对不上，或字段数偏离典型值 ±50%，Agent 应在 DDL 说明里**明确写出**："单行按 XXX B 估算（假设：{列数/是否含长文本}），若实测偏差 >30% 请调整 BUCKETS"，而不是给出一个看似精确的数字。

### 分桶设计示例

| 业务场景 | 分桶键 | BUCKETS | 说明 |
|---------|--------|---------|------|
| 订单表 | HASH(order_id) | 16-64 | order_id 高基数 |
| 用户表 | HASH(user_id) | 16-32 | user_id 高基数，与订单表 Colocate |
| 日志表 | HASH(server_id) 或 RANDOM | 32-128 | 大数据量 |
| 维度表 | RANDOM 或单分桶 | 1-8 | 数据量小 |

### Colocate Join 配置

```sql
-- 表 A 与表 B 配置同一 Colocate Group
PROPERTIES("colocate_with"="group_user", "replication_num"="3");
```

**约束**：
- 分桶键类型与数量一致
- BUCKETS 数相同
- 副本数相同

## §5 索引设计指南

### Doris 内置自动索引

| 索引 | 范围 | 说明 |
|------|------|------|
| 前缀索引（Sort Key） | KEY 列前 36 字节 | 自动维护，对前缀过滤极快 |
| ZoneMap | 所有列 | 自动维护每个 Page 的 Min/Max |
| BloomFilter | 通过 PROPERTIES 指定 | 高基数等值过滤 |

### 手动索引选择

| 索引类型 | 适用场景 | 示例 |
|---------|---------|------|
| BLOOM_FILTER | 高基数等值/IN | `"bloom_filter_columns"="user_id, trace_id"`（**必须放在 PROPERTIES；不支持 `INDEX ... USING BLOOM_FILTER` 语法**） |
| INVERTED INDEX（2.0+） | 文本模糊匹配/JSON | `INDEX idx_msg(message) USING INVERTED PROPERTIES("parser"="english")` |
| NGRAM_BF | 字符串 LIKE，2.0 之前 | `INDEX idx_url(url) USING NGRAM_BF PROPERTIES("gram_size"="3", "bf_size"="1024")` |

### 何时不需要额外索引

- 字段已在 KEY 列前缀（前缀索引足够）
- 字段为低基数（< 100），且为 KEY 列
- 查询频率极低的字段

## §6 诊断检查清单

对现有表结构进行诊断时，按以下清单逐项检查：

| # | 检查项 | 良好设计 | 需要优化 | 优化建议 |
|---|--------|---------|---------|---------|
| 1 | 数据模型 | 匹配业务需求（明细/去重/聚合） | 模型与业务不匹配 | 重建表使用正确模型 |
| 2 | 分区粒度 | 单分区 1-100 GB | 过细（小时级）或不分区 | 调整分区表达式 |
| 3 | 动态分区 | 时间序列表已启用 | 未启用，历史数据堆积 | ALTER TABLE SET dynamic_partition |
| 4 | KEY 列顺序 | 高频 WHERE 字段在前 | 高基数字段在前 | 重建表调整 KEY 列 |
| 5 | KEY 列数量 | 3-5 个 | > 8 个 | 精简 KEY 列 |
| 6 | 分桶键 | 高基数列，无倾斜 | 低基数或倾斜 | ALTER TABLE 重建 |
| 7 | BUCKETS 数 | 单 Tablet 1-3GB | Tablet 过大或过小 | ALTER TABLE 调整 |
| 8 | UNIQUE KEY 模型 | 启用 MoW（2.0+） | 仍是 MoR | 升级配置 |
| 9 | BLOOM_FILTER | 高基数等值过滤列已配置 | 缺少必要 BF | ALTER TABLE SET |
| 10 | INVERTED INDEX | 文本模糊匹配列已配置 | 缺少倒排索引（2.0+） | ALTER TABLE ADD INDEX |
| 11 | 副本数 | replication_num=3 | 仅 1 副本（生产） | ALTER 调整 |
| 12 | 冷热分层 | 历史分区配置冷数据策略 | 全部使用 SSD | 配置 STORAGE_POLICY |

### 诊断输出格式

```markdown
## 表结构诊断报告

### 基本信息
- 表名：{database}.{table}
- 数据模型：DUPLICATE / UNIQUE / AGGREGATE
- 分区：{partition_expr}
- 分桶：DISTRIBUTED BY HASH({col}) BUCKETS {N}
- 副本数：{N}

### 诊断结果

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | 数据模型 | ✅/⚠️/❌ | {说明} |
| ... |

### 优化建议（按优先级排序）

1. **[高]** {建议1}
   ```sql
   ALTER TABLE ...
   ```
2. **[中]** {建议2}
   ...
```
