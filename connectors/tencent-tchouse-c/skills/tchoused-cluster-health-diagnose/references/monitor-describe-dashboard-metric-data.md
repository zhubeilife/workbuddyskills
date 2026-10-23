# Monitor 监控指标查询接口（Doris 集群）

> 本文件为本 Skill 的本地引用副本。完整接口规范及指标列表参见顶层 references：
>
> [./monitor-describe-dashboard-metric-data.md](./monitor-describe-dashboard-metric-data.md)

## 在本 Skill 中的使用要点

### 调用前置条件

1. 已通过 `TCHouseDDescribeInstanceNodes` 获取 FE/BE/CN 节点列表（含各节点 IP）
2. 已确定 `Region`、`RegionId`、`InstanceId`

### 节点 IP 提取规则（与 SKILL.md 步骤 2 一致）

从 `InstanceNodesList` 中提取：

- `feIps`   = 所有 `Role === "master"` 的 `Ip`            ← FE 节点 IP（含 leader/follower/observer）
- `beIps`   = 所有 `Role === "core"`   的 `Ip`            ← BE 节点 IP
- `cnIps`   = 所有 `Role === "cn"`     的 `Ip`            ← CN 节点 IP（仅存算分离）
- `leaderIp` = 首个 `FeRole ∈ {"MASTER","FOLLOWER","leader"}` 的 `Ip`   ← BusinessData 专用

> ⚠️ 坑：`Role==="master"` 是判别「FE 类节点」（节点角色级历史命名），和 FE 集群是否有 Leader 无关；FE 内部 leader/follower/observer 由 `FeRole` 区分。

### 调用策略（与 SKILL.md 步骤 4 对齐）

> 以下指标名均为 Monitor 的 `CloudMonitorApiName`（驼峰格式），可直接传入 `MetricNames`。
> **所有调用都必须传 `NodeIps`**，不存在「不传 IP」的路径；IP 集合依 aa.json 分组决定。

**第一步：查节点存活与基础资源**（按 `NodeRole` + `NodeIps` 拉取）

- 存活：`FeUp`（FE，`NodeIps=feIps`）、`BeUp`（BE，`NodeIps=beIps`）、`BrokerUp`（随 FE、BE 一同拉取）
- 基础资源（FE 侧 `NodeIps=feIps`，BE 侧 `NodeIps=beIps`）：`CpuUsage,MemUsage,DiskUsage,SystemDiskUsage,NodeLoad1`

**第二步：发现异常后下钻细化**（按 `NodeIps` + `NodeRole` 拉取）

- BE CPU 高 → `CpuUsage,NodeLoad1,NodeLoad5,NodeLoad15`
- BE 内存高 → `MemUsage,DorisBeMemoryAllocatedBytes`
- BE 磁盘高 → `DiskUsage,DorisBeDisksLocalUsedCapacity,DorisBeDisksRemoteUsedCapacity,DorisBeDisksTrashUsedCapacity`
- 磁盘 IO → `NodeDiskReadsCompletedTotal,NodeDiskWritesCompletedTotal,NodeDiskReadBytesTotal,NodeDiskWrittenBytesTotal`
- FE JVM → `JvmHeapSizeBytesUsed,JvmHeapSizeBytesMax,JvmNonHeapSizeBytesUsed,JvmOldGcCountV2,JvmOldGcTimeV2,JvmYoungGcCountV2,JvmYoungGcTimeV2,JvmThreadBlockedCount,JvmThreadWaitingCount`（堆使用率需自行用 used/max 计算）

**第三步：检查 Doris 业务指标**

> 括号内标注为 aa.json 分组 + IP 来源；**【BusinessData】严格走 `leaderIp` 单 IP**。

- FE 查询负载（FeData / `feIps`）：`DorisFeQps,DorisFeRps,DorisFeConnectionTotalV2,DorisFeQueryInstanceNum,DorisFeQueryErrRate`
- FE 查询负载【BusinessData / `leaderIp`】：`DorisFeQuerySlow`
- FE 查询延迟（FeData / `feIps`）：`DorisFeQueryLatencyMsQuantile075,DorisFeQueryLatencyMsQuantile095,DorisFeQueryLatencyMs098,DorisFeQueryLatencyMsQuantile099,DorisFeQueryLatencyMsQuantile0999`
- 副本/Tablet 健康【BusinessData / `leaderIp`】：`DorisFeTabletStatusCountTypeUnhealthy`
- 副本/Tablet 健康（FeData / `feIps`）：`DorisFeScheduledTabletNum,DorisFeReportQueueSize,DorisFePublishTxnNum`
- 副本/Tablet 健康（BeData / `beIps`）：`DorisFeTabletNum`（名字带 Fe 但 aa.json 归属 BeData）
- Compaction（BeData / `beIps`）：`DorisBeTabletCumulativeMaxCompactionScore,DorisBeTabletBaseMaxCompactionScore,DorisBeCompactionWaittingPermits,DorisBeCompactionUsedPermitsV2`
- Compaction（FE 汇总 FeData / `feIps`）：`DorisFeMaxTabletCompactionScore`
- Compaction（BeData / `beIps`）：`DorisFeTabletMaxCompactionScore`（名字带 Fe 但归属 BeData）
- BE 导入压力（BeData / `beIps`）：`DorisBeStreamingLoadCurrentProcessing,DorisBeRoutineLoadTaskCount,DorisBeTabletWriterCount,DorisBeLoadBytesV2,DorisBeLoadRowsV2`
- BE 查询执行（BeData / `beIps`）：`DorisBeFragmentInstanceCount,DorisBeFragmentRequestsTotalV2,DorisBeFragmentThreadPoolQueueSize,DorisBeTimeoutCanceledFragmentCountV2`
- BE 线程池（BeData / `beIps`）：`DorisBeProcessThreadNum,DorisBeLocalScanThreadPoolQueueSize,DorisBeRemoteScanThreadPoolQueueSize,DorisBeHeavyWorkPoolQueueSize,DorisBeLightWorkPoolQueueSize`
- 冷热分层缓存（BeData / `beIps`，如适用）：`FileCacheCapacity,FileCacheCacheSize,FileCacheHitRatio,FileCacheHitRatio5m,DorisBeUploadTotalByte`

> `CcrData` 分组：**本 Skill 未使用**。业务前端监控面板未消费 CCR 指标，且与集群健康诊断主题不相关，不需拉取。

### 时间格式

ISO 8601（`2026-06-11T18:00:00+08:00`），不要与 `TCHouseDDescribeEventTasks` 的 `YYYY-MM-DD HH:MM:SS` 格式混淆。

### 指标阈值判断

参考 [../diagnosis-framework.md#2-监控指标阈值](./diagnosis-framework.md#2-监控指标阈值)。

### 频率控制

每轮诊断 ≤ 5 次调用（每次可批量查多个 MetricNames）。
