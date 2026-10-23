# tchoused-describe-online-query-loads

## 功能说明

调用腾讯云 TCHouse-D 的 `DescribeOnlineQueryLoads` 云 API，获取 Doris 集群当前正在运行的查询负载信息。本接口对应 ClickHouse 的 `DescribeRunningQuery`，但提供了更丰富的过滤和排序能力。

典型用途：

- **集群健康诊断**：定位 CPU 高负载/查询堆积的根因，找出长时间运行的查询
- **慢 SQL 诊断**：分析"正在发生"的慢查询，辅助识别死循环/资源争抢
- **资源管控**：识别异常占用大量 CPU/内存/IO 的查询

> 💡 也可通过 DMS 执行 `SHOW PROCESSLIST` 或查询 `information_schema.processlist`/`information_schema.active_queries` 作为补充。

## 接口信息

- **请求域名**：`cdwdoris.tencentcloudapi.com`
- **接口名称**：`DescribeOnlineQueryLoads`
- **API 版本**：`2021-12-28`
- **请求方式**：POST
- **频率限制**：20次/秒

## 输入参数

| 参数名称 | 必选 | 类型 | 描述 |
|---------|------|------|------|
| Region | 是 | String | 地域，如 `ap-guangzhou` |
| InstanceId | 是 | String | 集群 ID，格式如 `cdwdoris-xxxxxxxx` |
| QueryId | 否 | String | 查询 ID，如 `93af8c44e82c4a9d-a6f9c03287c920f6` |
| ConnectId | 否 | String | 连接 ID |
| SQLDetail | 否 | String | SQL 文本模糊搜索 |
| TableInfo | 否 | String | 查询表信息（如 `internal.information_schema.processlist`） |
| TargetClientIP | 否 | String | 客户端 IP，如 `0.0.0.0:3600` |
| FilterQueryTypeList.N | 否 | Array of String | 过滤查询类型列表 |
| FilterQueryStatusList.N | 否 | Array of String | 过滤查询状态列表 |
| OrderExecuteStartTime | 否 | String | 查询开始时间排序：`asc`/`desc` |
| OrderNetworkIO | 否 | String | 网络 IO 字节数排序 |
| OrderQueryScanRowCount | 否 | String | 查询扫描数据行数排序 |
| OrderQueryScanDataSize | 否 | String | 查询扫描数据大小排序 |
| OrderCPU | 否 | String | CPU 消耗排序 |
| OrderMemory | 否 | String | 内存最大消耗排序 |
| OrderQueryDuration | 否 | String | 查询耗时排序（推荐 `desc`） |
| OnlyColumnsToFilter.N | 否 | Array of String | 仅用于获取下拉选项列表 |
| Offset | 否 | Integer | 偏移量，默认 0 |
| Limit | 否 | Integer | 查询个数限制，默认 100 |
| OnlyDownload | 否 | Boolean | 仅下载，默认 false |

## 输出参数

| 参数名称 | 类型 | 描述 |
|---------|------|------|
| List | Array of [MonitorDrillOnlineQueryLoad] | 在线查询负载列表 |
| TotalCount | Integer | 总数 |
| ErrorMsg | String | 报错信息 |
| DownloadUrl | String | 下载地址 |
| RequestId | String | 唯一请求 ID |

### MonitorDrillOnlineQueryLoad 关键字段（参考）

| 字段 | 描述 |
|------|------|
| QueryId | 查询 ID |
| ConnectId | 连接 ID |
| SQLDetail | SQL 文本 |
| QueryStatus | 查询状态（running / blocked 等） |
| QueryType | 查询类型 |
| ExecuteStartTime | 开始时间 |
| QueryDuration | 已运行时长 |
| CPU | CPU 消耗 |
| Memory | 当前内存消耗 |
| QueryScanRowCount | 扫描数据行数 |
| QueryScanDataSize | 扫描数据大小 |
| NetworkIO | 网络 IO |
| ClientIP | 客户端 IP |
| UserName | 执行用户 |
| Database | 当前数据库 |

## 使用示例

### 请求示例（按耗时降序取 Top 10 长查询）

```json
{
  "Action": "DescribeOnlineQueryLoads",
  "Version": "2021-12-28",
  "Region": "ap-guangzhou",
  "InstanceId": "cdwdoris-xxxxxxxx",
  "OrderQueryDuration": "desc",
  "Offset": 0,
  "Limit": 10
}
```

### 响应示例

```json
{
  "Response": {
    "TotalCount": 25,
    "List": [
      {
        "QueryId": "93af8c44e82c4a9d-a6f9c03287c920f6",
        "ConnectId": "15",
        "SQLDetail": "SELECT count(*) FROM orders WHERE order_time > '2026-06-01' GROUP BY user_id",
        "QueryStatus": "running",
        "QueryType": "SELECT",
        "ExecuteStartTime": "2026-06-13 14:25:30",
        "QueryDuration": 125,
        "CPU": 32500,
        "Memory": 1073741824,
        "QueryScanRowCount": 12000000,
        "QueryScanDataSize": 524288000,
        "NetworkIO": 104857600,
        "ClientIP": "10.0.0.5:34221",
        "UserName": "analyst",
        "Database": "demo_db"
      }
    ],
    "ErrorMsg": "",
    "RequestId": "xxx"
  }
}
```

## 典型使用场景

- **CPU 高负载根因定位**：`OrderCPU=desc` 找出最耗 CPU 的查询
- **内存泄漏排查**：`OrderMemory=desc` 找出大内存查询
- **死循环识别**：`OrderQueryDuration=desc` 找出长时间运行查询
- **客户端定位**：通过 `TargetClientIP` 定位异常客户端
- **慢 SQL 实时诊断**：用户报告"现在查询很慢"时第一时间调用本接口

## 注意事项

1. 仅返回**当前正在运行**的查询，已结束查询请使用 `DescribeSlowQueryRecords`
2. 在 FE 内存不足时，本接口可能返回不完整数据
3. 排序参数（OrderXxx）只能选**一个**生效，如果传多个仅最后一个生效
4. 长时间运行的查询（QueryDuration > 60 秒）通常是优化重点
5. 通过 `QueryId` + `ADMIN KILL QUERY` 可终止异常查询（建议先与业务确认）
