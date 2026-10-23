# tchoused-describe-ddl

## 功能说明

调用腾讯云 TCHouse-D 的 `DescribeDDL` 云 API，根据库表名获取 Doris 表（或物化视图）的建表 DDL。本接口在以下场景中使用：

- 获取已有表的完整 CREATE TABLE 语句（含数据模型、分区、分桶、索引、PROPERTIES）
- 获取物化视图的定义
- 现有表结构优化诊断（解析 DDL 后给出优化建议）
- NL2SQL 中作为表结构上下文输入

> 💡 **设计说明**：Doris 没有独立的 `DescribeTableSchema` 接口，本接口对应 ClickHouse 的 `DescribeTableSchema`，但返回的是完整 DDL 文本而非结构化字段列表。需要时可通过解析 DDL 提取列定义、KEY 列、分区键、分桶键等信息。

## 接口信息

- **请求域名**：`cdwdoris.tencentcloudapi.com`
- **接口名称**：`DescribeDDL`
- **API 版本**：`2021-12-28`
- **请求方式**：POST
- **频率限制**：20次/秒

## 输入参数

| 参数名称 | 必选 | 类型 | 描述 |
|---------|------|------|------|
| Region | 是 | String | 地域，如 `ap-guangzhou` |
| InstanceId | 是 | String | 集群 ID，格式如 `cdwdoris-xxxxxxxx` |
| Type | 否 | String | 类型：`table`（表）或 `mv`（物化视图） |
| TableName | 否 | String | 表名（三段式：`catalog.database.table`，如 `internal.db1.orders`） |
| MVName | 否 | String | 物化视图名（三段式，如 `internal.db1.mv_8`） |

> 当查询表 DDL 时传 `Type=table` 和 `TableName`；查询物化视图时传 `Type=mv` 和 `MVName`。

## 输出参数

| 参数名称 | 类型 | 描述 |
|---------|------|------|
| DDL | String | 建表 DDL 文本（如 `CREATE TABLE \`db\`.\`tbl\` (...)`） |
| ErrorMsg | String | 报错信息 |
| RequestId | String | 唯一请求 ID |

## 使用示例

### 请求示例（获取表 DDL）

```json
{
  "Action": "DescribeDDL",
  "Version": "2021-12-28",
  "Region": "ap-guangzhou",
  "InstanceId": "cdwdoris-xxxxxxxx",
  "Type": "table",
  "TableName": "internal.demo_db.orders"
}
```

### 响应示例

```json
{
  "Response": {
    "DDL": "CREATE TABLE `demo_db`.`orders` (\n  `order_id` BIGINT NOT NULL COMMENT '订单ID',\n  `user_id` BIGINT NOT NULL COMMENT '用户ID',\n  `order_time` DATETIME NOT NULL COMMENT '下单时间',\n  `amount` DECIMAL(18, 2) NOT NULL COMMENT '订单金额',\n  `channel` VARCHAR(32) NULL COMMENT '渠道'\n) ENGINE=OLAP\nDUPLICATE KEY(`order_id`, `user_id`)\nCOMMENT '订单明细表'\nPARTITION BY RANGE(`order_time`)()\nDISTRIBUTED BY HASH(`user_id`) BUCKETS 32\nPROPERTIES (\n  \"replication_num\" = \"3\",\n  \"dynamic_partition.enable\" = \"true\",\n  \"dynamic_partition.time_unit\" = \"DAY\",\n  \"dynamic_partition.start\" = \"-90\",\n  \"dynamic_partition.end\" = \"3\",\n  \"dynamic_partition.prefix\" = \"p\",\n  \"dynamic_partition.buckets\" = \"32\"\n);",
    "ErrorMsg": "",
    "RequestId": "xxx"
  }
}
```

### 请求示例（获取物化视图 DDL）

```json
{
  "Action": "DescribeDDL",
  "Version": "2021-12-28",
  "Region": "ap-guangzhou",
  "InstanceId": "cdwdoris-xxxxxxxx",
  "Type": "mv",
  "MVName": "internal.demo_db.mv_orders_daily"
}
```

## 典型使用场景

- **现有表结构优化诊断**：分析数据模型选择、分区策略、分桶数、索引等是否合理
- **NL2SQL 表结构感知**：作为列名/类型/Key 的上下文输入
- **SQL 生成时的列名校验**：避免使用不存在的列
- **慢 SQL 诊断**：对照 DDL 判断查询是否命中分区键、分桶键

## 注意事项

1. **三段式表名**：`TableName` 需使用 `catalog.database.table` 三段式（默认 catalog 为 `internal`）
2. **大小写敏感**：库表名大小写敏感，需与实际一致
3. **权限要求**：调用方需要对该表有 `SELECT` 权限或 admin 权限
4. **DDL 文本解析**：需要正则或 SQL Parser 从 DDL 文本中提取关键信息（KEY 列、分区键、分桶键、索引、PROPERTIES）
5. 物化视图查询请使用 `Type=mv` 和 `MVName`，不可与 `TableName` 混用
