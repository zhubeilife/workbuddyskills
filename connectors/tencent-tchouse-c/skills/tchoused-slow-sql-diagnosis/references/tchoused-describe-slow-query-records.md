# tchoused-describe-slow-query-records

## 功能说明

调用腾讯云 TCHouse-D（Doris）的 `DescribeSlowQueryRecords` 云 API，获取指定集群的慢查询记录列表，用于分析查询性能问题。

## 接口信息

- **请求域名**：`cdwdoris.tencentcloudapi.com`
- **接口名称**：`DescribeSlowQueryRecords`
- **API 版本**：`2021-12-28`
- **请求方式**：POST
- **频率限制**：20次/秒

## 输入参数

| 参数名称          | 必选 | 类型           | 描述                                                                          |
| ----------------- | ---- | -------------- | ----------------------------------------------------------------------------- |
| InstanceId        | 是   | String         | 集群实例 ID，格式如 `cdwdoris-xxxxxxxx`                                       |
| Region            | 是   | String         | 地域                                                                          |
| QueryDurationMs   | 是   | Integer        | 慢查询时间阈值（毫秒），只返回执行时间 ≥ 该值的查询，建议从 3000 开始         |
| StartTime         | 是   | String         | 开始时间（格式：`YYYY-MM-DD HH:MM:SS`）                                       |
| EndTime           | 是   | String         | 结束时间（格式：`YYYY-MM-DD HH:MM:SS`）                                       |
| PageSize          | 是   | Integer        | 分页大小                                                                      |
| PageNum           | 是   | Integer        | 页码                                                                          |
| DurationMs        | 否   | String         | DurationMs 排序方式：`ASC` / `DESC`                                           |
| ReadRows          | 否   | String         | ReadRows 排序方式：`ASC` / `DESC`                                             |
| ResultBytes       | 否   | String         | ResultBytes 排序方式：`ASC` / `DESC`                                          |
| MemoryUsage       | 否   | String         | MemoryUsage 排序方式：`ASC` / `DESC`                                          |
| SortField         | 否   | String         | 排序字段，如 `MemoryUsage`/`DurationMs`                                       |
| SortOrder         | 否   | String         | 排序方式：`ASC` / `DESC`                                                      |
| DbName.N          | 否   | Array of Str   | 数据库名称过滤                                                                |
| CatalogName.N     | 否   | Array of Str   | Catalog 名称过滤                                                              |
| IsQuery           | 否   | Integer        | 是否是查询：`0`-否（DDL/DML），`1`-是（SELECT），`-1`-全部                    |
| Sql               | 否   | String         | SQL 文本模糊搜索                                                              |
| UserName          | 否   | String         | 执行用户过滤                                                                  |
| ComputeGroups.N   | 否   | Array of Str   | 计算组列表（仅存算分离架构有效）                                              |

## 输出参数

| 参数名称                                | 类型    | 描述                                              |
| --------------------------------------- | ------- | ------------------------------------------------- |
| TotalCount                              | Integer | 慢查询总数                                        |
| DBNameList                              | Array   | 时间范围内涉及的所有数据库名                      |
| CatalogNameList                         | Array   | 时间范围内涉及的所有 Catalog 名                   |
| SlowQueryRecords                        | Array   | 慢查询记录列表                                    |
| SlowQueryRecords[].InitialQueryId       | String  | 查询的全局唯一 ID（QueryId）                      |
| SlowQueryRecords[].OsUser               | String  | 执行用户                                          |
| SlowQueryRecords[].Sql                  | String  | SQL 文本                                          |
| SlowQueryRecords[].QueryStartTime       | String  | 查询开始时间                                      |
| SlowQueryRecords[].DurationMs           | Integer | 查询执行时长（毫秒）                              |
| SlowQueryRecords[].ReadRows             | Integer | 读取行数                                          |
| SlowQueryRecords[].ResultRows           | Integer | 返回行数                                          |
| SlowQueryRecords[].ResultBytes          | Integer | 返回字节数                                        |
| SlowQueryRecords[].MemoryUsage          | Integer | 内存峰值使用量（字节）                            |
| SlowQueryRecords[].InitialAddress       | String  | 发起节点 IP                                       |

## 使用示例

### 请求示例

```json
{
  "Action": "DescribeSlowQueryRecords",
  "Version": "2021-12-28",
  "Region": "ap-guangzhou",
  "InstanceId": "cdwdoris-xxxxxxxx",
  "QueryDurationMs": 3000,
  "StartTime": "2026-06-16 00:00:00",
  "EndTime": "2026-06-16 23:59:59",
  "PageSize": 20,
  "PageNum": 1,
  "SortField": "DurationMs",
  "SortOrder": "DESC",
  "IsQuery": 1
}
```

### 响应示例

```json
{
  "Response": {
    "TotalCount": 156,
    "DBNameList": ["db_order", "db_log"],
    "CatalogNameList": ["internal"],
    "SlowQueryRecords": [
      {
        "InitialQueryId": "2a3b4c-xxxx-xxxx-xxxx",
        "OsUser": "report_user",
        "Sql": "SELECT order_id, sum(amount) FROM db_order.t_order WHERE dt='2026-06-15' GROUP BY order_id LIMIT 1000",
        "QueryStartTime": "2026-06-16 14:23:12",
        "DurationMs": 18234,
        "ReadRows": 12345678,
        "ResultRows": 1000,
        "ResultBytes": 51200,
        "MemoryUsage": 524288000,
        "InitialAddress": "10.0.0.1"
      }
    ],
    "RequestId": "abc-xxx-xxx"
  }
}
```

## 典型使用场景

- **慢 SQL Top N**：按 `DurationMs` 倒序排，取最慢的 N 条 SQL，作为重点优化对象
- **大内存查询识别**：按 `MemoryUsage` 倒序排，识别内存消耗高的查询，避免触发 OOM
- **大扫描量识别**：按 `ReadRows` 倒序排，识别扫描行数巨大的查询，可能是缺索引或缺分区裁剪
- **指定库表分析**：通过 `DbName` 过滤具体业务库，定位特定业务的慢查询
- **用户维度分析**：通过 `UserName` 过滤具体用户，分析单个业务方的查询模式

## 注意事项

- `Sql` 字段可能被截断，完整 SQL 需通过其他接口获取
- `InitialQueryId` 是 Doris 中 `query_id` 的全称，可用于在 FE audit log 或 BE Profile 中精确定位
- 时间范围建议不超过 7 天，否则数据量过大可能导致超时
- `IsQuery=1` 仅查询 SELECT 类语句，DDL/DML 类设为 `0`，全部设为 `-1`
- 排序参数 `SortField` 优先级高于 `DurationMs`/`ReadRows` 等单独排序参数

## 与 ClickHouse 慢查询对比

| 维度 | ClickHouse (cdwch) | Doris (cdwdoris) |
| --- | --- | --- |
| 查询日志来源 | system.query_log | FE audit log |
| 数据可见性 | 节点本地（需 cluster() 函数聚合） | FE 全局可见 |
| 内存字段 | `memory_usage` 字节 | `MemoryUsage` 字节 |
| 行数字段 | `read_rows` | `ReadRows` |
