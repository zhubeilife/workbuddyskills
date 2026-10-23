# monitor-get-monitor-data

## 功能说明

通过 Monitor 产品的 `GetMonitorData` 接口查询 TCHouse-D（Namespace=`QCE/CDWDRS`）集群的监控指标数据。**一次调用只查询一个指标**（`MetricName` 为单数），按节点维度（`InstanceId` + `ip`）返回时间序列。

## 工具类型

- **实现方式**：MCP tool（由 TCHouseD MCP Server 封装）
- **底层云 API**：`monitor.tencentcloudapi.com / GetMonitorData`（Version `2018-07-24`）
- **Namespace**：`QCE/CDWDRS`（tool 内默认值，无需显式传入）

## MCP Tool 输入参数

| 参数名 | 必选 | 类型 | 描述 |
|--------|------|------|------|
| Region | 是 | String | 地域字符串，如 `ap-guangzhou`、`ap-shanghai`、`ap-chongqing` |
| RegionId | 是 | Number | 地域数字ID（ap-guangzhou=1, ap-shanghai=4, ap-beijing=8, ap-nanjing=33, ap-chengdu=16, ap-chongqing=19, ap-singapore=9, ap-hongkong=5） |
| InstanceId | 是 | String | 集群实例ID，格式如 `cdwdoris-xxxxxxxx` |
| MetricName | 是 | String | **单个**指标名（`CloudMonitorApiName`，驼峰格式）。**一次调用只支持一个指标**；如需多个指标，按指标循环调用 |
| NodeIps | 是 | String | 节点 IP 列表，**英文逗号分隔**，必填、不能为空。BE 指标传 BE 节点 IP（可多选），FE 指标传 FE 节点 IP（可多选），业务监控传 FE Leader 单 IP |
| StartTime | 是 | String | 起始时间，格式 `YYYY-MM-DD HH:mm:ss`，如 `2026-06-22 10:00:00` |
| EndTime | 是 | String | 结束时间，格式 `YYYY-MM-DD HH:mm:ss`，如 `2026-06-22 11:00:00` |
| Period | 否 | Number | 数据粒度（秒），可选 `10/60/300/3600/86400`，默认 `60` |
| Namespace | 否 | String | 监控产品命名空间，默认 `QCE/CDWDRS`（TCHouse-D 固定值，一般无需传入） |

### Period 与时间范围约束

| Period | 含义 | 允许的时间范围 |
|---|---|---|
| `10` | 10 秒 | ≤ 24 小时 |
| `60` | 1 分钟 | ≤ 24 小时 |
| `300` | 5 分钟 | 5 分钟 ~ 3 天 |
| `3600` | 1 小时 | 60 分钟 ~ 30 天 |
| `86400` | 1 天 | ≥ 1 天 |

## NodeIps 选取规则（三种 Tab 对照）

调用前必须先通过 `TCHouseDDescribeInstanceNodes` 获取节点列表。`NodeIps` 的选取规则与业务监控面板（BE 指标 / FE 指标 / 业务监控）保持一致：

| 指标类型 | 数据分组（`DescribeMonitorMeta`） | 节点过滤条件 | `NodeIps` 数量 |
|---|---|---|---|
| **BE 指标** | `BeData` | `Role === "core"` 的节点 | 1 ~ N（可多选，默认全部 BE） |
| **FE 指标** | `FeData` | `Role === "master"` 的节点（含 MASTER/FOLLOWER/OBSERVER） | 1 ~ N（可多选，默认全部 FE） |
| **业务监控** | `BusinessData` | `Role === "master"` 且 `FeRole ∈ {MASTER, FOLLOWER, leader}` 的**第一个**节点 | **恒为 1**（仅 FE Leader） |

> ⚠️ 业务监控指标（如 `DorisFeTabletStatusCountTypeUnhealthy`、`DorisFeQuerySlow`）虽然属于 FE 维度，但只能查 Leader 单 IP，**不能传多个 FE IP**。

## 调用示例

### 示例 1：查询 BE 节点 CPU 空闲率（8 个 BE 节点全选）

```json
{
  "Region": "ap-chongqing",
  "RegionId": 19,
  "InstanceId": "cdwdoris-xfgdipdp",
  "MetricName": "DorisBeCpuIdle",
  "NodeIps": "10.0.0.25,10.0.0.21,10.0.0.37,10.0.0.36,10.0.0.38,10.0.0.35,10.0.0.44,10.0.0.47",
  "StartTime": "2026-06-22 10:00:00",
  "EndTime": "2026-06-22 11:00:00",
  "Period": 60
}
```

### 示例 2：查询 FE 节点 JVM 堆使用率（3 个 FE 节点全选）

```json
{
  "Region": "ap-chongqing",
  "RegionId": 19,
  "InstanceId": "cdwdoris-xfgdipdp",
  "MetricName": "DorisFeJvmHeapUsedPercent",
  "NodeIps": "10.0.0.40,10.0.0.34,10.0.0.18",
  "StartTime": "2026-06-22 10:00:00",
  "EndTime": "2026-06-22 11:00:00",
  "Period": 60
}
```

### 示例 3：查询业务监控指标（恰好 1 个 FE Leader IP）

```json
{
  "Region": "ap-chongqing",
  "RegionId": 19,
  "InstanceId": "cdwdoris-xfgdipdp",
  "MetricName": "DorisFeTabletStatusCountTypeUnhealthy",
  "NodeIps": "10.0.0.40",
  "StartTime": "2026-06-22 10:00:00",
  "EndTime": "2026-06-22 11:00:00",
  "Period": 60
}
```

## 底层 API 实际请求体（由 MCP Server 自动拼装，仅供调试参考）

MCP Server 会把上述扁平化参数转换为 `GetMonitorData` 接口要求的嵌套结构：

```json
{
  "Namespace": "QCE/CDWDRS",
  "MetricName": "DorisBeTabletCumulativeMaxCompactionScore",
  "Period": 60,
  "StartTime": "2026-06-22 10:02:29",
  "EndTime": "2026-06-22 11:02:29",
  "Instances": [
    { "Dimensions": [
        { "Name": "InstanceId", "Value": "cdwdoris-xfgdipdp" },
        { "Name": "ip",         "Value": "10.0.0.25" }
    ]},
    { "Dimensions": [
        { "Name": "InstanceId", "Value": "cdwdoris-xfgdipdp" },
        { "Name": "ip",         "Value": "10.0.0.21" }
    ]}
    // ... 其余 IP
  ]
}
```

每个 IP 拼装为一个 `Instances[i]`，`Dimensions` 固定包含 `InstanceId` 和 `ip` 两条（顺序固定）。

## Doris 监控指标速查

> 完整指标列表以 `DescribeMonitorMeta` 返回的 `CloudMonitorApiName` 字段为准，下表仅列常用项。

### BE 节点级（`BeData` 分组）

| MetricName | 含义 | 健康阈值 |
|---|---|---|
| `BeUp` | BE 进程存活（0/1） | = 1 |
| `CpuUsage` | BE CPU 使用率（%） | < 80% |
| `MemUsage` | BE 内存使用率（%） | < 85% |
| `DiskUsage` | BE 数据盘使用率（%） | < 80% |
| `DorisBeTabletCumulativeMaxCompactionScore` | Cumulative Compaction 评分 | < 100 |
| `DorisBeTabletBaseMaxCompactionScore` | Base Compaction 评分 | < 100 |
| `DorisBeCompactionWaittingPermits` | Compaction 等待令牌数 | 0 |
| `DorisBeDisksLocalUsedCapacity` | BE 本地数据已用空间（字节） | — |

### FE 节点级（`FeData` 分组）

| MetricName | 含义 | 健康阈值 |
|---|---|---|
| `FeUp` | FE 进程存活（0/1） | = 1 |
| `DorisFeQps` | FE 查询 QPS | — |
| `DorisFeQueryLatencyMsQuantile099` | 查询 P99 延迟（ms） | < 业务 SLA |
| `DorisFeConnectionTotalV2` | 当前连接数 | < `qe_max_connection` |
| `JvmHeapSizeBytesUsed` | FE JVM 已用堆内存（字节） | — |
| `JvmHeapSizeBytesMax` | FE JVM 堆上限（字节） | — |
| `JvmOldGcCountV2` | Old GC 次数累计 | 斜率 ≈ 0 |

### 业务监控（`BusinessData` 分组，仅取 FE Leader 单 IP）

| MetricName | 含义 | 健康阈值 |
|---|---|---|
| `DorisFeTabletStatusCountTypeUnhealthy` | 不健康 Tablet 数量 | = 0 |
| `DorisFeQuerySlow` | 慢查询累计值（看斜率） | 斜率 ≈ 0 |

### 通用节点系统指标（FE/BE/CN 都适用，按当前诊断维度选 IP）

| MetricName | 含义 |
|---|---|
| `CpuUsage` | CPU 使用率 |
| `MemUsage` | 内存使用率 |
| `DiskUsage` | 数据盘使用率 |
| `SystemDiskUsage` | 系统盘使用率 |
| `NodeLoad1` / `NodeLoad5` / `NodeLoad15` | 1/5/15 分钟负载 |
| `NodeDiskReadsCompletedTotal` / `NodeDiskWritesCompletedTotal` | 磁盘读/写次数累计 |
| `NodeDiskReadBytesTotal` / `NodeDiskWrittenBytesTotal` | 磁盘读/写字节累计 |
| `NodeNetworkReceiveBytesTotal` / `NodeNetworkTransmitBytesTotal` | 网络接收/发送字节累计 |

## 输出参数

### 响应结构（GetMonitorData 标准响应）

```json
{
  "Response": {
    "MetricName": "DorisBeCpuIdle",
    "Period": 60,
    "StartTime": "2026-06-22 10:00:00",
    "EndTime":   "2026-06-22 11:00:00",
    "DataPoints": [
      {
        "Dimensions": [
          {"Name": "InstanceId", "Value": "cdwdoris-xfgdipdp"},
          {"Name": "ip",         "Value": "10.0.0.25"}
        ],
        "Timestamps": [1750557600, 1750557660, ...],
        "Values":     [98.5, 97.2, ...]
      }
      // ... 其余节点
    ],
    "RequestId": "xxx"
  }
}
```

## 调用前置依赖

1. **`TCHouseDDescribeInstanceNodes`** —— 获取节点 IP、Role、FeRole，作为 `NodeIps` 选取依据
2. （可选）`DescribeMonitorMeta` —— 获取 `CloudMonitorApiName` 与单位元数据；若已知指标名可跳过

## 注意事项

1. **指标命名为 `CloudMonitorApiName`（驼峰格式）**，如 `DorisBeCpuIdle`、`DorisFeJvmHeapUsedPercent`
2. **时间格式为 `YYYY-MM-DD HH:mm:ss`**（不是 ISO 8601）
3. **`NodeIps` 必填且不能为空**；IP 维度永远不能省
4. **一次调用只查一个指标**；多指标需循环调用
5. **业务监控指标 `Instances` 恒为 1 条**（FE Leader），不要给业务监控传多个 FE IP
6. **Namespace 固定 `QCE/CDWDRS`**（TCHouse-D 监控产品命名空间）
7. 监控数据保留期视 Period 不同而不同，更早数据需通过日志/审计系统查询
