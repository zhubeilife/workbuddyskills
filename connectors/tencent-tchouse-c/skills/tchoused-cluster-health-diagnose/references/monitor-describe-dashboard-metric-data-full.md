# monitor-describe-dashboard-metric-data

## 功能说明

通过 Monitor 产品的 DescribeDashboardMetricData 接口查询 TCHouse-D（QCE/CDWDORIS）集群的监控指标数据。支持集群级和节点级（FE/BE/CN）指标查询，可批量查询多个指标。

## 工具类型

- **实现方式**：MCP tool（由 TCHouseD MCP Server 封装）
- **协议**：SSE / Streamable HTTP
- **产品**：monitor（非 cdwdoris）

## MCP Tool 输入参数

> ⚠️ **重要**：Agent 调用此工具时使用以下**扁平化参数**，MCP Server 会自动将其转换为底层 API 所需的嵌套结构（包括自动注入 Module、Namespace、Datasource 等固定字段）。

| 参数名 | 必选 | 类型 | 描述 |
|--------|------|------|------|
| Region | 是 | String | 地域字符串，如 `ap-guangzhou`、`ap-shanghai`、`ap-beijing` |
| RegionId | 是 | Number | 地域数字ID（ap-guangzhou=1, ap-shanghai=4, ap-beijing=8, ap-nanjing=33, ap-chengdu=16, ap-chongqing=19, ap-singapore=9, ap-hongkong=5） |
| InstanceId | 是 | String | 集群实例ID，格式如 `cdwdoris-xxxxxxxx` |
| MetricNames | 是 | String | 要查询的指标名称列表，**用英文逗号分隔**，使用**驼峰格式**（如 `BeCpuUsage,BeMemUsage,BeDiskUsage`） |
| NodeCount | 否 | Number | 节点数量（FE 或 BE）。**查询集群聚合指标时必填**，用于构造 Dimension 数组 |
| NodeIps | 否 | String | 节点 IP 列表，**用英文逗号分隔**。**查询节点级指标时必填**（通过 `TCHouseDDescribeInstanceNodes` 获取）。集群聚合指标不需要传此参数 |
| NodeRole | 否 | String | 节点角色：`fe` / `be` / `cn`。配合 NodeIps/NodeCount 使用，标识查询的是哪类节点 |
| StartTime | 是 | String | 起始时间，**ISO 8601 格式**，如 `2026-06-11T18:00:00+08:00` |
| EndTime | 是 | String | 结束时间，**ISO 8601 格式**，如 `2026-06-11T19:00:00+08:00` |
| Period | 否 | Number | 数据粒度（秒），可选 60/300/3600。默认 60 |

### 参数使用规则

**规则 1：查询集群聚合指标**（如 BE 整体的聚合）：
- 传 `NodeCount`（BE 节点数）+ `NodeRole=be`，不传 `NodeIps`
- MCP Server 会自动构造对应数量的 Dimension

**规则 2：查询 BE 节点级指标**：
- 传 `NodeIps`（BE 节点 IP）+ `NodeRole=be`，不传 `NodeCount`
- 适用指标：`BeCpuUsage`、`BeMemUsage`、`BeDiskUsage`、`BeCompactionScore`、`BeUnhealthyReplica` 等

**规则 3：查询 FE 节点级指标**：
- 传 `NodeIps`（FE 节点 IP）+ `NodeRole=fe`，不传 `NodeCount`
- 适用指标：`FeQps`、`FeQueryLatencyP99`、`FeFailedQuery`、`FeJvmHeapUsedPercent`、`FeIsMaster`、`FeMaxJournalId` 等

**规则 4：查询 CN 节点级指标**（仅存算分离架构）：
- 传 `NodeIps`（CN 节点 IP）+ `NodeRole=cn`，不传 `NodeCount`

### Period（数据粒度）选择建议

| 查询时间跨度 | 建议 Period | 说明 |
|-------------|------------|------|
| ≤ 1 小时 | 60（1分钟） | 最细粒度，排障场景 |
| 1-6 小时 | 300（5分钟） | 平衡精度与数据量 |
| 6-24 小时 | 300（5分钟） | 日常巡检 |
| 1-7 天 | 3600（1小时） | 趋势分析 |

## 调用示例

### 示例 1：查询 BE 集群聚合 CPU/内存/磁盘使用率（集群有 3 个 BE 节点）

```json
{
  "Region": "ap-beijing",
  "RegionId": 8,
  "InstanceId": "cdwdoris-xxxxxxxx",
  "MetricNames": "BeCpuUsage,BeMemUsage,BeDiskUsage",
  "NodeCount": 3,
  "NodeRole": "be",
  "StartTime": "2026-06-11T18:00:00+08:00",
  "EndTime": "2026-06-11T19:00:00+08:00",
  "Period": 60
}
```

### 示例 2：查询 BE 节点级 Compaction 压力和副本健康度

```json
{
  "Region": "ap-beijing",
  "RegionId": 8,
  "InstanceId": "cdwdoris-xxxxxxxx",
  "MetricNames": "BeCompactionScore,BeUnhealthyReplica,BeBaseCompactionTaskNum,BeCumulativeCompactionTaskNum",
  "NodeIps": "10.0.0.14,10.0.0.12,10.0.0.3",
  "NodeRole": "be",
  "StartTime": "2026-06-11T18:00:00+08:00",
  "EndTime": "2026-06-11T19:00:00+08:00",
  "Period": 60
}
```

### 示例 3：查询 FE 节点查询性能与选举状态

```json
{
  "Region": "ap-beijing",
  "RegionId": 8,
  "InstanceId": "cdwdoris-xxxxxxxx",
  "MetricNames": "FeQps,FeQueryLatencyP99,FeFailedQuery,FeJvmHeapUsedPercent,FeIsMaster",
  "NodeIps": "10.0.1.1,10.0.1.2,10.0.1.3",
  "NodeRole": "fe",
  "StartTime": "2026-06-11T18:00:00+08:00",
  "EndTime": "2026-06-11T19:00:00+08:00",
  "Period": 60
}
```

## 输出参数

### 响应结构

```json
{
  "Response": {
    "MetricName": "BeCpuUsage",
    "DataPoints": [
      {
        "Dimensions": [
          {"Name": "InstanceId", "Value": "cdwdoris-xxxxxxxx"},
          {"Name": "ip", "Value": "10.0.0.14"}
        ],
        "Timestamps": [1718193600, 1718193660, ...],
        "Values": [12.5, 13.2, ...]
      }
    ],
    "StartTime": "2026-06-11T18:00:00+08:00",
    "EndTime": "2026-06-11T19:00:00+08:00",
    "Period": 60,
    "RequestId": "xxx"
  }
}
```

## Doris 监控指标速查

### BE 节点核心指标

| MetricName | 含义 | 健康阈值 |
|---|---|---|
| `BeCpuUsage` | BE CPU 使用率（%） | < 80% |
| `BeMemUsage` | BE 内存使用率（%） | < 85% |
| `BeMemUsed` | BE 已用内存（字节） | — |
| `BeDiskUsage` | BE 磁盘使用率（%） | < 80% |
| `BeDataDirUsed` | BE 数据目录已用空间 | — |
| `BeCompactionScore` | Compaction 评分（最大） | < 100 |
| `BeBaseCompactionTaskNum` | Base Compaction 任务数 | < `compaction_task_num_per_disk` |
| `BeCumulativeCompactionTaskNum` | Cumulative Compaction 任务数 | — |
| `BeUnhealthyReplica` | 不健康副本数 | = 0 |
| `BeReplicaCloneTaskNum` | 副本克隆任务数 | — |

### FE 节点核心指标

| MetricName | 含义 | 健康阈值 |
|---|---|---|
| `FeQps` | FE 查询 QPS | — |
| `FeQueryLatencyP99` | 查询 P99 延迟（ms） | < 业务 SLA |
| `FeFailedQuery` | 失败查询数 | 越低越好 |
| `FeJvmHeapUsedPercent` | FE JVM 堆使用率（%） | < 80% |
| `FeIsMaster` | 是否 Master（0/1） | 集群仅 1 个 = 1 |
| `FeMaxJournalId` | 元数据日志最新 ID | — |
| `FeConnectionTotal` | 当前连接数 | < `qe_max_connection` |

### 通用节点指标（FE/BE/CN 都适用）

| MetricName | 含义 |
|---|---|
| `CpuUsage` | CPU 使用率 |
| `CpuUsageAvg` | CPU 平均使用率 |
| `MemUsage` | 内存使用率 |
| `DiskUsage` | 磁盘使用率 |
| `NodeLoad1` | Load1 |
| `NodeDiskIoUtil` | 磁盘 IO 利用率 |
| `NodeDiskIoWait` | 磁盘 IO 等待 |
| `NodeNetworkReceiveBytesTotal` | 网络接收字节 |
| `NodeNetworkTransmitBytesTotal` | 网络发送字节 |

## 注意事项

1. **指标命名为驼峰格式**：如 `cpu_usage` → `CpuUsage`、`be_unhealthy_replica` → `BeUnhealthyReplica`
2. **时间格式为 ISO 8601**（如 `2026-06-11T18:00:00+08:00`），与 cdwdoris 接口的 `YYYY-MM-DD HH:MM:SS` 格式不同
3. **NodeRole 区分**：FE/BE/CN 节点指标不互通，调用时需传对应角色 IP
4. **存算分离架构**下，CN 节点指标可参考 BE 节点的指标命名（部分指标 BE 与 CN 共享）
5. 监控数据默认保留 30 天，更早的数据需要通过日志/审计系统查询
6. 单次调用建议 MetricNames 不超过 10 个，避免响应过大
