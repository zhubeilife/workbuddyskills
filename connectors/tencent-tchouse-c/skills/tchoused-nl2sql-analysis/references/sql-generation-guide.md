# SQL 生成规范与模板

> **何时使用本文件**：在步骤 3（理解需求与生成 SQL）时参考，确保生成的 SQL 符合 Doris（MySQL 兼容）最佳实践。
> **何时不使用**：图表可视化和结论生成请参考 `visualization-guide.md`；工具调用参数请参考各工具的 reference 文档。

---

## 目录

- [§1 生成规范](#1-生成规范)
- [§2 时间处理函数](#2-时间处理函数)
  - [§2.5 分区覆盖预校验（生成时间过滤前必做）](#25-分区覆盖预校验生成时间过滤前必做)
- [§3 常见分析模式模板](#3-常见分析模式模板)
- [§4 性能优化要点](#4-性能优化要点)
- [§5 常见错误与修正](#5-常见错误与修正)

---

## §1 生成规范

### 基本原则

1. **只生成 SELECT 语句**：严禁生成任何 DDL/DML（INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE）
2. **必须使用分区键过滤**：WHERE 条件中必须包含分区键字段，避免全表扫描
3. **只选需要的列**：禁止 `SELECT *`，明确列出需要的字段
4. **结果集控制**：非聚合查询必须添加 `LIMIT`（默认 1000）
5. **使用 Doris/MySQL 函数**：Doris 兼容 MySQL 协议与函数集

### SQL 格式规范

```sql
-- 标准格式
SELECT
    维度列,
    聚合函数(指标列) AS 指标别名
FROM 数据库.表名
WHERE 分区键过滤条件
  AND 其他过滤条件
GROUP BY 维度列
ORDER BY 排序列 DESC
LIMIT N
```

### 别名规范

- 聚合结果必须有中文别名（方便业务人员理解）
- 别名使用反引号包裹：`` AS `支付金额` ``
- 时间维度别名统一为：`日期`、`月份`、`小时` 等

---

## §2 时间处理函数

### 常用时间函数映射

| 用户表述 | Doris 函数 | 示例 |
|---------|-----------|------|
| 按天 | `DATE(时间列)` 或 `DATE_TRUNC(时间列, 'day')` | `` DATE(create_time) AS `日期` `` |
| 按周 | `DATE_TRUNC(时间列, 'week')` | `` DATE_TRUNC(create_time, 'week') AS `周起始日` `` |
| 按月 | `DATE_TRUNC(时间列, 'month')` 或 `DATE_FORMAT(...,'%Y-%m')` | `` DATE_TRUNC(create_time, 'month') AS `月份` `` |
| 按小时 | `DATE_TRUNC(时间列, 'hour')` 或 `HOUR(时间列)` | `` HOUR(create_time) AS `小时` `` |
| 按年 | `YEAR(时间列)` | `` YEAR(create_time) AS `年份` `` |

### 时间范围过滤

| 用户表述 | SQL 条件 | 优先级 |
|---------|---------|--------|
| 过去 7 天 | `WHERE date >= CURDATE() - INTERVAL 7 DAY AND date < CURDATE()` | ⭐⭐⭐（优先） |
| 过去 30 天 | `WHERE date >= CURDATE() - INTERVAL 30 DAY AND date < CURDATE()` | ⭐⭐⭐（优先） |
| 本月 | `WHERE date >= DATE_TRUNC(CURDATE(), 'month') AND date < CURDATE() + INTERVAL 1 DAY` | ⭐⭐⭐（优先） |
| 上个月 | `WHERE date >= DATE_TRUNC(CURDATE(), 'month') - INTERVAL 1 MONTH AND date < DATE_TRUNC(CURDATE(), 'month')` | ⭐⭐⭐（优先） |
| 今天 | `WHERE date = CURDATE()` | ⭐⭐⭐（优先） |
| 昨天 | `WHERE date = CURDATE() - INTERVAL 1 DAY` | ⭐⭐⭐（优先） |
| 本周 | `WHERE date >= DATE_TRUNC(CURDATE(), 'week') AND date < CURDATE() + INTERVAL 1 DAY` | ⭐⭐⭐（优先） |
| 今年 | `WHERE date >= DATE_TRUNC(CURDATE(), 'year') AND date < CURDATE() + INTERVAL 1 DAY` | ⭐⭐⭐（优先） |
| 2026-06-09 至 2026-06-16 | `WHERE date BETWEEN '2026-06-09' AND '2026-06-16'` | ⭐（仅用户指定精确日期时） |

### 日期处理规则

#### 1. 动态函数优先原则

**核心规则**：优先使用 Doris 动态时间函数，避免硬编码日期

- ✅ **推荐**：使用 `CURDATE()`、`NOW()`、`DATE_TRUNC(CURDATE(), 'month')` 等动态函数
- ❌ **避免**：硬编码日期字符串如 `'2026-06-09'`，除非用户明确指定

#### 2. 时间范围推断规则

| 用户表述 | 推断规则 | SQL 实现 |
|---------|---------|---------|
| "最近"、"近期" | 默认 7 天 | `CURDATE() - INTERVAL 7 DAY` |
| "这个月"、"本月" | 当月 1 号至今 | `DATE_TRUNC(CURDATE(), 'month')` |
| "上个月" | 上月完整月 | `DATE_TRUNC(CURDATE(), 'month') - INTERVAL 1 MONTH` |
| "本周" | 本周一至今 | `DATE_TRUNC(CURDATE(), 'week')` |
| "上周" | 上周完整周 | `DATE_TRUNC(CURDATE(), 'week') - INTERVAL 1 WEEK` |

#### 3. 精确日期处理

**仅当用户明确指定精确日期时**才使用硬编码：

```sql
-- 用户明确说："查询2026年6月9日到6月16日的数据"
WHERE date BETWEEN '2026-06-09' AND '2026-06-16'

-- 用户明确说："查看6月10号的数据"
WHERE date = '2026-06-10'
```

#### 4. 日期格式规范

- 日期格式：`'YYYY-MM-DD'`
- 时间格式：`'YYYY-MM-DD HH:MM:SS'`
- 必要时用 `STR_TO_DATE('2026-06-10', '%Y-%m-%d')` 显式转换

### 注意事项

- 时间比较使用 `>=` 和 `<`（左闭右开），避免边界问题
- 当前时间使用 `NOW()`，当前日期使用 `CURDATE()`
- Doris 兼容 MySQL `INTERVAL` 语法，但 `DATE_TRUNC` 是 Doris 扩展函数

### §2.5 分区覆盖预校验（生成时间过滤前必做）

> ⚠️ 本节配套 SKILL.md 步骤 3.2.1。在把用户表述的时间窗（如"过去 7 天"、"本月"）翻译成 WHERE 条件之前，必须先与 DDL 中现有分区的时间区间做**交集校验**；分区未覆盖用户时间窗时，禁止静默生成 SQL 返回 0 行。

#### 分区元信息读取

分区信息唯一来源为 `TCHouseDDescribeDDL` 返回的建表语句，重点识别：

| DDL 片段 | 语义 |
|---|---|
| `PARTITION BY RANGE(<col>)` | 分区键与分区类型（RANGE 分区） |
| `PARTITION pXXX VALUES [(...), (...))` | 每个分区的**左闭右开**区间 |
| `PARTITION BY LIST(<col>)` | LIST 分区，逐值枚举 |
| 无 `PARTITION BY` | 非分区表，跳过本校验 |

**示例**：

```sql
-- 从 DDL 中提取到：
PARTITION BY RANGE(dt) (
  PARTITION p202606 VALUES [('2026-06-01'), ('2026-07-01'))
)
```

对应分区区间并集为 `[2026-06-01, 2026-07-01)`。

#### 校验流程

```
用户时间窗 U = [u_start, u_end)
表分区区间并集 P = ⋃ 各分区区间
交集 I = U ∩ P

CASE:
  I == U          → 通过，用用户时间窗生成 SQL
  I ⊂ U 且 I ≠ ∅  → 告知用户"分区仅覆盖 X~Y，将按实际分区区间生成"，用 I 生成
  I == ∅          → 禁止静默生成 SQL，必须提供方案 A/B 请用户确认
  表无分区键       → 跳过本校验（走全表扫描或按业务列过滤）
```

#### 交集为空时的兜底方案

**方案 A（推荐 · 让用户重选时段）**：

告知用户实际可查时段，并请其重新指定：

> 当前表 `<catalog.db.table>` 仅有 `<分区列表>` 分区，覆盖 `<起, 止>`；您所询问的"<原始描述>"落在 `<用户区间>` 内，与现有分区无交集。
> 请确认：
> 1. 是否改为查询 `<可查最近区间>`？
> 2. 或您使用的是另一张表？

**方案 B（兜底 · 自动收窄到最新可用区间）**：

当用户明确"要看最近的数据 · 不限具体时段"时，把时间窗自动收窄到分区并集内的**最新时段**，并在 SQL 前的说明中标注：

> ⚠️ 表现有分区不覆盖"过去 N 天"，已改为查询 `<实际使用区间>`（该表最新可用分区）

#### 案例

**场景**：用户 2026-07-10 询问"过去 7 天 UV"，表 `orders` 分区为 `p202606 [2026-06-01, 2026-07-01)`。

- 用户区间：`[2026-07-03, 2026-07-10)`
- 分区区间：`[2026-06-01, 2026-07-01)`
- 交集：∅ → 命中方案 A/B 分支

**错误生成**（禁止）：

```sql
-- ❌ 静默按"过去7天"翻译，会返回 0 行且用户不知原因
SELECT DATE(dt) AS `日期`, COUNT(DISTINCT user_id) AS `UV`
FROM internal.demo.orders
WHERE dt >= CURDATE() - INTERVAL 7 DAY
  AND dt < CURDATE()
GROUP BY `日期`;
```

**正确处理（方案 B 兜底）**：

```sql
-- ✅ 已与用户确认改为查询表内最新分区区间 [2026-06-01, 2026-07-01)
SELECT DATE(dt) AS `日期`, COUNT(DISTINCT user_id) AS `UV`
FROM internal.demo.orders
WHERE dt >= '2026-06-01'
  AND dt <  '2026-07-01'
GROUP BY `日期`
ORDER BY `日期` ASC;
```

#### 禁止行为

- ❌ 未读 DDL 就凭"过去 N 天"直接拼 `CURDATE() - INTERVAL N DAY`
- ❌ 返回 0 行时不查分区、直接归因为"业务无数据"
- ❌ 依赖 `INFORMATION_SCHEMA.PARTITIONS` 或其他系统表推断分区（本 Skill 不直连集群，只信 `TCHouseDDescribeDDL` 返回的 DDL）
- ❌ 表无分区键（如小表 / DUPLICATE 无分区）时反过来强制加分区条件

---

## §3 常见分析模式模板

### 3.1 趋势分析（按时间维度汇总）

```sql
-- 用户需求："统计过去7天每天的订单量和支付金额"
SELECT
    DATE(pay_time) AS `日期`,
    COUNT(*) AS `订单量`,
    SUM(pay_amount) AS `支付金额`
FROM db.orders
WHERE pay_time >= CURDATE() - INTERVAL 7 DAY
  AND pay_time < CURDATE()
GROUP BY `日期`
ORDER BY `日期` ASC
```

### 3.2 分组对比（按分类维度汇总）

```sql
-- 用户需求："各渠道的用户数和支付金额对比"
SELECT
    channel AS `渠道`,
    COUNT(DISTINCT user_id) AS `用户数`,
    SUM(pay_amount) AS `支付金额`
FROM db.orders
WHERE date >= CURDATE() - INTERVAL 30 DAY
  AND date < CURDATE()
GROUP BY `渠道`
ORDER BY `支付金额` DESC
```

### 3.3 TOP N 排名

```sql
-- 用户需求："支付金额最高的前10个商品"
SELECT
    product_name AS `商品名称`,
    SUM(pay_amount) AS `支付金额`,
    COUNT(*) AS `订单量`
FROM db.orders
WHERE date >= CURDATE() - INTERVAL 30 DAY
  AND date < CURDATE()
GROUP BY `商品名称`
ORDER BY `支付金额` DESC
LIMIT 10
```

### 3.4 占比分析

```sql
-- 用户需求："各支付方式的订单占比"
SELECT
    pay_method AS `支付方式`,
    COUNT(*) AS `订单量`,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS `占比(%)`
FROM db.orders
WHERE date >= CURDATE() - INTERVAL 7 DAY
  AND date < CURDATE()
GROUP BY `支付方式`
ORDER BY `订单量` DESC
```

### 3.5 同比/环比分析

```sql
-- 用户需求："本月与上月的GMV对比（环比）"
SELECT '本月' AS `时间段`, SUM(pay_amount) AS `GMV`
FROM db.orders
WHERE date >= DATE_TRUNC(CURDATE(), 'month')
  AND date < CURDATE() + INTERVAL 1 DAY

UNION ALL

SELECT '上月' AS `时间段`, SUM(pay_amount) AS `GMV`
FROM db.orders
WHERE date >= DATE_TRUNC(CURDATE(), 'month') - INTERVAL 1 MONTH
  AND date < DATE_TRUNC(CURDATE(), 'month')
```

### 3.6 多维交叉分析

```sql
-- 用户需求："过去7天各渠道每天的支付金额趋势"
SELECT
    DATE(pay_time) AS `日期`,
    channel AS `渠道`,
    SUM(pay_amount) AS `支付金额`
FROM db.orders
WHERE pay_time >= CURDATE() - INTERVAL 7 DAY
  AND pay_time < CURDATE()
GROUP BY `日期`, `渠道`
ORDER BY `日期` ASC, `支付金额` DESC
```

### 3.7 漏斗分析（简化版）

```sql
-- 用户需求："注册-下单-支付的转化漏斗"
SELECT '注册' AS `步骤`, COUNT(DISTINCT user_id) AS `用户数`
FROM db.user_events
WHERE event = 'register' AND date >= CURDATE() - INTERVAL 7 DAY

UNION ALL

SELECT '下单', COUNT(DISTINCT user_id)
FROM db.user_events
WHERE event = 'create_order' AND date >= CURDATE() - INTERVAL 7 DAY

UNION ALL

SELECT '支付', COUNT(DISTINCT user_id)
FROM db.user_events
WHERE event = 'pay_success' AND date >= CURDATE() - INTERVAL 7 DAY
```

### 3.8 BITMAP 高效去重计数（如有 BITMAP 列）

```sql
-- 当 user_id 以 BITMAP 类型存储时，去重计数极快
SELECT
    DATE(event_time) AS `日期`,
    BITMAP_UNION_COUNT(user_id_bitmap) AS `UV`
FROM db.user_bitmap_table
WHERE event_time >= CURDATE() - INTERVAL 7 DAY
GROUP BY `日期`
```

---

## §4 性能优化要点

| 优化项 | 说明 | 示例 |
|--------|------|------|
| 分区裁剪 | WHERE 必须包含分区键 | `WHERE date >= '2026-06-01'` |
| 避免 SELECT * | 只选需要的列 | `SELECT user_id, amount` |
| 谓词下推 | Doris 自动下推过滤到存储层 | — |
| 小表放右侧 | JOIN 时小表做右表（Broadcast Join） | `big_table JOIN small_table` |
| Colocate Join | 同 Colocate Group 的表 JOIN 不 Shuffle | 见 smart-table-design |
| RUNTIME FILTER | Doris 自动开启，可手动 hint 增强 | `/*+ SET_VAR(runtime_filter_mode=GLOBAL) */` |
| 物化视图 | 高频聚合查询使用 MV 加速 | `CREATE MATERIALIZED VIEW ...` |
| LIMIT 控制 | 非聚合查询加 LIMIT | `LIMIT 1000` |

---

## §5 常见错误与修正

| 错误场景 | 错误写法 | 正确写法 | 说明 |
|---------|---------|---------|------|
| 中文列名未转义 | `SELECT 支付金额` | `` SELECT `支付金额` `` | 中文列名必须用反引号 |
| ClickHouse 函数误用 | `uniqExact(user_id)` | `COUNT(DISTINCT user_id)` | Doris 兼容 MySQL 函数集 |
| ClickHouse 时间函数误用 | `today()` | `CURDATE()` | Doris 用 MySQL 风格函数 |
| ClickHouse 函数误用 | `toDate(x)` | `DATE(x)` | — |
| GROUP BY 缺少维度 | `SELECT a, b, sum(c)` | `SELECT a, b, SUM(c) ... GROUP BY a, b` | 非聚合列必须在 GROUP BY 中 |
| LIMIT 位置错误 | `SELECT ... LIMIT 10 ORDER BY ...` | `SELECT ... ORDER BY ... LIMIT 10` | LIMIT 在 ORDER BY 之后 |
| 除零错误 | `a / b` | `a / NULLIF(b, 0)` | 使用 NULLIF 避免除零 |
| 字符串拼接 | `a + b`（数字会变加法） | `CONCAT(a, b)` | 显式使用 CONCAT |
