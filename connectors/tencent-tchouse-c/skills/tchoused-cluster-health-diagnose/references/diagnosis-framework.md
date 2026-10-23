# 集群健康诊断分析框架

> **何时使用本文件**：在步骤 3（告警事件分级判断）、步骤 4（监控指标阈值判断）、步骤 7（综合分析与根因定位）时参考。
> **何时不使用**：工具调用参数请参考各工具的 reference 文档；输出报告格式请参考 `report-template.md`。

---

## 目录

- [§1 告警事件分级](#1-告警事件分级)
- [§2 监控指标阈值](#2-监控指标阈值)
- [§3 健康评分规则](#3-健康评分规则)
- [§4 常见故障模式与根因分析](#4-常见故障模式与根因分析)

---

## §1 告警事件分级

| EventCode | 含义 | 严重程度 | Agent 优先级 |
|-----------|------|---------|-------------|
| `DiskHigh` | 磁盘使用率过高 | 🔴 高 | 立即分析，防数据丢失 |
| `BeDown` | BE 节点不可达 | 🔴 高 | 立即分析，可能影响数据可用性 |
| `FeDown` | FE 节点不可达 | 🔴 高 | 立即分析，影响集群对外服务 |
| `BeOom` | BE 进程 OOM | 🔴 高 | 立即分析，查询会受影响 |
| `FeOom` | FE 进程 OOM | 🔴 高 | 立即分析，连接会断 |
| `UnhealthyReplica` | Tablet 副本不健康 | 🔴 高 | 立即分析，数据可用性受损 |
| `AbnormalInstanceDisk` | 实例硬盘异常 | 🔴 高 | 立即分析，可能影响数据完整性 |
| `InstanceDiskAlter` | 实例硬盘预警 | 🟡 中 | 纳入诊断，给出预防建议 |
| `CompactionScoreHigh` | Compaction 评分过高 | 🟡 中 | 纳入诊断，建议优化写入或调高 Compaction 并发 |
| `InstanceRisk` | 实例运行隐患 | 🟡 中 | 纳入诊断，分析具体风险 |
| `EmptyPassword` | 空密码安全隐患 | 🟡 中 | 纳入诊断，建议设置密码 |
| `InstanceMaintenance` | 实例维护升级 | 🟢 低 | 告知用户，通常无需处理 |

### 事件状态说明

| Status 值 | 含义 | Agent 行为 |
|-----------|------|-----------|
| 1 | 待处理 | 重点关注，纳入诊断 |
| 2 | 已处理 | 仅作为历史参考 |
| 3 | 处理中 | 关注进度，告知用户 |
| 4 | 已忽略 | 跳过 |

---

## §2 监控指标阈值

> **接口说明**：监控指标通过 `MonitorGetMonitorData` 接口查询（Monitor 产品，Namespace=`QCE/CDWDRS`），MetricName 使用驼峰格式，一次查一个指标。
> **参数规则**：所有指标都必须传 `NodeIps`（不存在「不传 IP」的调用路径）。`NodeIps` 与 `NodeRole` 的取值依 `aa.json` 指标分组决定：
>
> - `FeData` → `NodeRole=fe`，`NodeIps=feIps`（所有 `Role==="master"` 的节点 IP）
> - `BeData` → `NodeRole=be`，`NodeIps=beIps`（所有 `Role==="core"` 的节点 IP）
> - `BeData`（CN）→ `NodeRole=cn`，`NodeIps=cnIps`（所有 `Role==="cn"` 的节点 IP）
> - `BusinessData` → `NodeRole=fe`，`NodeIps=leaderIp`（`FeRole ∈ {MASTER,FOLLOWER,leader}` 的首个节点 IP）
> - `CcrData` → **本 Skill 未使用**（业务前端监控面板未消费 CCR 指标，与集群健康诊断主题不相关）
>
> ⚠️ 下文「FE 节点级指标」/「BE 节点级指标」/「通用节点系统指标」均按上表传参，不再逐项重复。

### BE 节点级指标（`NodeRole=be`，`NodeIps=beIps`）

> 以下指标名均为 Monitor `CloudMonitorApiName`（驼峰格式）；全部归属 aa.json 的 `BeData` 分组。

| 指标类别 | MetricName | 含义 | 正常范围 | 警告阈值 | 严重阈值 |
|---------|-------------------|------|---------|---------|----------|
| 存活 | `BeUp` | BE 进程存活（0/1） | 1 | — | 0 |
| CPU | `CpuUsage` | BE 节点 CPU 使用率 | < 60% | > 80% 持续 5 分钟 | > 95% 持续 5 分钟 |
| 内存使用率 | `MemUsage` | BE 节点内存使用率 | < 70% | > 85% | > 95% |
| 内存（进程） | `DorisBeMemoryAllocatedBytes` | BE 进程已分配物理内存（字节）| — | — | 接近 mem_limit |
| 磁盘使用率 | `DiskUsage` | BE 数据盘使用率 | < 70% | > 85% | > 90% |
| 本地存储 | `DorisBeDisksLocalUsedCapacity` | BE 本地数据目录已用空间（字节）| — | — | — |
| 远端存储 | `DorisBeDisksRemoteUsedCapacity` | BE 远端数据已用空间（冷热分层）| — | — | — |
| 回收站 | `DorisBeDisksTrashUsedCapacity` | BE trash 已用空间 | — | — | — |
| Cumulative Compaction 分 | `DorisBeTabletCumulativeMaxCompactionScore` | 当前 BE 最大 Cumulative Compaction Score | < 50 | > 100 | > 1000（接近写入拒绝）|
| Base Compaction 分 | `DorisBeTabletBaseMaxCompactionScore` | 当前 BE 最大 Base Compaction Score | < 50 | > 100 | > 1000 |
| Compaction 令牌（等待）| `DorisBeCompactionWaittingPermits` | 等待 Compaction 令牌数 | 0 | > 0 持续 | 持续增长 |
| Compaction 令牌（使用）| `DorisBeCompactionUsedPermitsV2` | 已使用 Compaction 令牌累计值 | — | — | — |
| 线程总数 | `DorisBeProcessThreadNum` | BE 进程线程数 | < 10000 | > 20000 | > 50000 |
| 句柄 | `DorisBeProcessFdNumUsedV2` | BE 进程使用的文件句柄数累计 | — | 接近 ulimit | 达到 ulimit |
| Local Scan 队列 | `DorisBeLocalScanThreadPoolQueueSize` | local scan 线程池队列长度 | 0 | > 0 持续 | 持续增长 |
| Remote Scan 队列 | `DorisBeRemoteScanThreadPoolQueueSize` | remote scan 线程池队列长度 | 0 | > 0 持续 | 持续增长 |
| Fragment 线程池 | `DorisBeFragmentThreadPoolQueueSize` | Fragment 线程池等待队列 | 0 | > 0 持续 | 持续增长 |
| Fragment 实例 | `DorisBeFragmentInstanceCount` | 当前 Fragment 实例数 | — | 过高（>500）| 持续增长且不下降 |
| 超时取消 | `DorisBeTimeoutCanceledFragmentCountV2` | 超时被取消的 Fragment 累计 | — | 斜率增加 | 斜率持续高 |
| Stream Load 并发 | `DorisBeStreamingLoadCurrentProcessing` | 当前 Stream Load 并发任务数 | 业务基线 | 突增 | 接近线程池上限 |
| Routine Load | `DorisBeRoutineLoadTaskCount` | 运行中 Routine Load 任务数 | 业务基线 | 突变 | 与 Routine Load 作业数不匹配 |
| File Cache 命中率 | `FileCacheHitRatio` | 冷热分层文件缓存命中率 | > 80% | < 60% | < 30% |
### FE 节点级指标（`NodeRole=fe`，`NodeIps=feIps`）

> 除下面标注 【BusinessData】的两项外，本表其余指标均归属 aa.json 的 `FeData` 分组。
> 【BusinessData】指标必须改传 `NodeIps=leaderIp`（FE Leader 单 IP）。

| 指标类别 | MetricName | 含义 | 正常范围 | 警告阈值 | 严重阈值 |
|---------|-------------------|------|---------|---------|----------|
| 存活 | `FeUp` | FE 进程存活（0/1）| 1 | — | 0 |
| QPS | `DorisFeQps` | FE 查询 QPS | 业务基线 | 突增 3 倍 | 突增 5 倍 |
| RPS | `DorisFeRps` | FE 请求 RPS（包含非查询）| 业务基线 | 突增 3 倍 | 突增 5 倍 |
| 查询错误 | `DorisFeQueryErrRate` | 查询错误累计值（应看斜率）| 0 | 斜率 > 0 持续 | 斜率持续增长 |
| 慢查询 | `DorisFeQuerySlow` 【BusinessData】 | 慢查询累计值 | 0 | 斜率 > 0 持续 | 斜率持续增长 |
| 延迟 P75 | `DorisFeQueryLatencyMsQuantile075` | 查询 P75 延迟（ms）| < 业务 SLA | > SLA | > 2× SLA |
| 延迟 P95 | `DorisFeQueryLatencyMsQuantile095` | 查询 P95 延迟（ms）| < 业务 SLA | > 2× SLA | > 5× SLA |
| 延迟 P98 | `DorisFeQueryLatencyMs098` | 查询 P98 延迟（ms）| < 业务 SLA | > 2× SLA | > 5× SLA |
| 延迟 P99 | `DorisFeQueryLatencyMsQuantile099` | 查询 P99 延迟（ms）| < 业务 SLA | > 2× SLA | > 5× SLA |
| JVM 堆上限 | `JvmHeapSizeBytesMax` | FE JVM 最大堆内存（字节）| — | — | — |
| JVM 堆已用 | `JvmHeapSizeBytesUsed` | FE JVM 已使用堆内存（字节）| < 70% 上限 | > 80% 上限 | > 90% 上限 |
| JVM 堆外 | `JvmNonHeapSizeBytesUsed` | FE JVM 堆外已用内存 | — | 持续增长 | 接近进程内存 |
| Old GC 次数 | `JvmOldGcCountV2` | FE 老年代 GC 次数累计 | 斜率 ≈ 0 | 斜率 > 0 | 斜率持续高 |
| Old GC 耗时 | `JvmOldGcTimeV2` | FE 老年代 GC 耗时累计（ms）| 斜率 ≈ 0 | 斜率 > 0 | STW 明显 |
| Young GC 次数 | `JvmYoungGcCountV2` | FE 新生代 GC 次数累计 | — | 斜率突增 | 斜率高 |
| Young GC 耗时 | `JvmYoungGcTimeV2` | FE 新生代 GC 耗时累计（ms）| — | 耗时增长 | 耗时过长 |
| 阻塞线程 | `JvmThreadBlockedCount` | JVM Blocked 状态线程数 | < 10 | > 50 持续 | > 100 持平 |
| 等待线程 | `JvmThreadWaitingCount` | JVM Waiting 状态线程数 | 业务基线 | 持续增长 | 持平 |
| 连接数 | `DorisFeConnectionTotalV2` | 当前 MySQL 端口连接数 | < 50% qe_max_connection | > 80% | > 95% |
| 查询实例数 | `DorisFeQueryInstanceNum` | 正在请求的 Fragment 实例数 | 业务基线 | 突增 | 持续高 |
| Compaction 汇总 | `DorisFeMaxTabletCompactionScore` | 集群所有 BE 最大 compaction score | < 50 | > 100 | > 1000 |
| Tablet Score | `DorisFeTabletMaxCompactionScore` | 节点上报的 compaction score | < 50 | > 100 | > 1000 |
| Tablet 总数 | `DorisFeTabletNum` | 集群 Tablet 总数 | 业务基线 | 接近集群上限 | 超出上限 |
| 不健康 Tablet | `DorisFeTabletStatusCountTypeUnhealthy` 【BusinessData】 | 不健康的 Tablet 数量 | 0 | > 0 | > 100 |
| 调度 Tablet | `DorisFeScheduledTabletNum` | 正在调度的 Tablet 数（修复/均衡）| 0 | > 0 持续 | 长期高 |
| Report 队列 | `DorisFeReportQueueSize` | BE 汇报任务在 FE 端队列长度 | < 100 | > 500 | > 1000 |
| Publish 事务 | `DorisFePublishTxnNum` | 正在 Publish 的事务数 | 业务基线 | 突增 | 持续高 |
### 通用节点系统指标（FE/BE/CN 都适用，传参随调用者背景）

> 在 aa.json 中 `FeData`、`BeData` 均各存一份同名记录。**调用时按当前诊断维度选择 IP 集合**：FE 侧诊断 → `feIps`；BE 侧诊断 → `beIps`；CN 侧诊断 → `cnIps`。

| 指标类别 | MetricName | 含义 | 正常范围 | 警告阈值 | 严重阈值 |
|---------|-------------------|------|---------|---------|----------|
| CPU | `CpuUsage` | CPU 使用率（最大瞬时）| < 60% | > 80% | > 95% |
| 负载 1m | `NodeLoad1` | 1 分钟负载 | < CPU 核数 | > 核数×1.5 | > 核数×2 |
| 负载 5m | `NodeLoad5` | 5 分钟负载 | < CPU 核数 | > 核数×1.5 | > 核数×2 |
| 负载 15m | `NodeLoad15` | 15 分钟负载 | < CPU 核数 | > 核数×1.5 | > 核数×2 |
| 内存 | `MemUsage` | 内存使用率 | < 70% | > 85% | > 95% |
| 数据盘 | `DiskUsage` | 数据盘使用率 | < 70% | > 85% | > 90% |
| 系统盘 | `SystemDiskUsage` | 系统盘使用率 | < 70% | > 85% | > 90% |
| 磁盘读次数 | `NodeDiskReadsCompletedTotal` | 磁盘读速度（Count/s）| 视磁盘类型 | 接近规格上限 | 达到规格上限 |
| 磁盘写次数 | `NodeDiskWritesCompletedTotal` | 磁盘写速度（Count/s）| 视磁盘类型 | 接近规格上限 | 达到规格上限 |
| 磁盘读量 | `NodeDiskReadBytesTotal` | 硬盘读流量（Byte/s）| 基线水平 | 接近带宽上限 | 达到带宽上限 |
| 磁盘写量 | `NodeDiskWrittenBytesTotal` | 硬盘写流量（Byte/s）| 基线水平 | 接近带宽上限 | 达到带宽上限 |
| 网络入 | `NodeNetworkReceiveBytesTotal` | 节点接收流量 | 基线水平 | 突增 3 倍 | 突增 5 倍 |
| 网络出 | `NodeNetworkTransmitBytesTotal` | 节点发送流量 | 基线水平 | 突增 3 倍 | 突增 5 倍 |

> ⚠️ aa.json 中不存在 `NodeDiskIoUtil`/`NodeDiskIoWait`/`NodeDiskReadIops`/`NodeDiskWriteIops`/`CpuUsageAvg` 这类指标，请勿使用。需要 IO 类信息时，用上面的 reads/writes/bytes 序列叠加估算。

### 磁盘类型与 IO 性能预期

| 磁盘类型 | 预期 IOPS | 预期吞吐 | 说明 |
|---------|----------|---------|------|
| CLOUD_SSD | 26000 | 260 MB/s | 标准 SSD |
| CLOUD_PREMIUM | 6000 | 150 MB/s | 高性能云硬盘 |
| CLOUD_HSSD | 100000+ | 350 MB/s | 增强型 SSD（推荐） |

### MetricName 转换规则

告警配置中的 `metricName` 使用下划线格式（如 `cpu_usage`），调用 `MonitorGetMonitorData` 时需使用驼峰格式的 `CloudMonitorApiName`（如 `CpuUsage`）。完整指标清单以项目 `aa.json` 中的 `CloudMonitorApiName` 字段为准。

**常见转换示例**：
- `cpu_usage` → `CpuUsage`（节点级，不带 BE 前缀）
- `mem_usage` → `MemUsage`
- `disk_usage` → `DiskUsage`
- `doris_fe_connection_total` → `DorisFeConnectionTotalV2`（注意 V2 后缀）
- `doris_be_tablet_cumulative_max_compaction_score` → `DorisBeTabletCumulativeMaxCompactionScore`
- `jvm_heap_size_bytes{type="used"}` → `JvmHeapSizeBytesUsed`

> ⚠️ 部分指标名后缀 V2，调用时不能遗漏。

---

## §3 健康评分规则

> **原则**：评分必须可追溯，报告里给出的分数必须能对应到下方的扣分项，禁止拍脑袋给分。

### 评分方法：100 分制扣分

起始分 **100 分**，按下列规则逐项扣分，扣完为止（最低 0 分）。所有扣分必须在报告的"扣分明细"表中列出，让用户可以复核。

#### 扣分项 A：节点异常

| 现象 | 扣分 |
|------|------|
| 每个非 `Running` 状态的 BE 节点 | **-20 分** |
| 每个非 `Running` 状态的 FE 节点 | **-20 分** |
| 每个非 `Running` 状态的 CN 节点（存算分离） | **-15 分** |
| 每个 `BeUp = 0` / `FeUp = 0`（存活指标失活） | **-20 分** |
| FE Leader 缺失（`FeRole === "MASTER"` 的节点不存在，`leaderIp` 为空） | **-25 分** |
| FE HA 拓扑不闭环（`M + F < 3` 或 `M + F` 为偶数，`HaType != 0` 时） | **-15 分** |

#### 扣分项 B：告警事件（仅统计 Status=1 待处理 与 Status=3 处理中）

| 严重程度 | 扣分（每条） | 单项封顶 |
|---------|-------------|----------|
| 🔴 高（`DiskHigh` / `BeDown` / `FeDown` / `BeOom` / `FeOom` / `UnhealthyReplica` / `AbnormalInstanceDisk`） | **-15 分** | -45 分 |
| 🟡 中（`InstanceDiskAlter` / `CompactionScoreHigh` / `InstanceRisk` / `EmptyPassword`） | **-8 分** | -24 分 |
| 🟢 低（`InstanceMaintenance` 等） | **-2 分** | -6 分 |

> 已处理（Status=2）/已忽略（Status=4）的事件**不扣分**。

#### 扣分项 C：监控指标（按 §2 表格中的阈值判定）

| 指标类别 | 达到"严重阈值" | 达到"警告阈值" | 单类别封顶 |
|---------|:-------------:|:-------------:|:---------:|
| CPU（`CpuUsage` / `NodeLoad1` / `NodeLoad5`） | **-10 分** | **-5 分** | -15 分 |
| BE 内存（`MemUsage` / `DorisBeMemoryAllocatedBytes` 接近 `mem_limit`） | **-10 分** | **-5 分** | -15 分 |
| FE JVM（`JvmHeapSizeBytesUsed / JvmHeapSizeBytesMax` 使用率 / `JvmOldGcCountV2` 斜率 / `JvmThreadBlockedCount`） | **-10 分** | **-5 分** | -15 分 |
| 磁盘容量（`DiskUsage` / `SystemDiskUsage` / `DorisBeDisksLocalUsedCapacity`） | **-15 分** | **-8 分** | -23 分 |
| 磁盘 IO（`NodeDiskReadBytesTotal` / `NodeDiskWrittenBytesTotal` / `NodeDiskReadsCompletedTotal` / `NodeDiskWritesCompletedTotal` 触及规格上限） | **-8 分** | **-4 分** | -12 分 |
| Compaction 压力（`DorisBeTabletCumulativeMaxCompactionScore` / `DorisBeTabletBaseMaxCompactionScore` / `DorisFeMaxTabletCompactionScore` / `DorisBeCompactionWaittingPermits`） | **-10 分** | **-5 分** | -15 分 |
| Tablet 健康度（`DorisFeTabletStatusCountTypeUnhealthy` / `DorisFeScheduledTabletNum` 长期 > 0） | **-15 分** | **-8 分** | -23 分 |
| 查询相关（`DorisFeQps` 突增 / `DorisFeQueryErrRate` 斜率 / `DorisFeQuerySlow` 斜率 / `DorisFeQueryLatencyMsQuantile099`） | **-8 分** | **-4 分** | -12 分 |
| 连接数（`DorisFeConnectionTotalV2` 占 `qe_max_connection` 比例） | **-8 分** | **-4 分** | -12 分 |
| BE 线程池/Fragment（`DorisBeFragmentThreadPoolQueueSize` / `DorisBeLocalScanThreadPoolQueueSize` / `DorisBeTimeoutCanceledFragmentCountV2` 斜率） | **-8 分** | **-4 分** | -12 分 |
| 冷热分层缓存（`FileCacheHitRatio` 低于阈值，仅 `Kind=SSC` 时计入） | **-6 分** | **-3 分** | -9 分 |

**同一指标的判定规则**：
- 同一指标在多个节点触发同一档阈值 → 按"节点数"计入，但受"单类别封顶"约束（例如 5 个 BE 节点 CPU 都爆到严重阈值，也只扣 15 分）
- 同一指标既触发警告又触发严重 → 按严重阈值扣分，不叠加

### 评分等级映射

| 分数区间 | 等级 |
|---------|------|
| 90 – 100 | 🟢 **健康** |
| 70 – 89  | 🟡 **警告** |
| 0  – 69  | 🔴 **异常** |

> 若最终得分与"最严重单项"表现不一致（例如所有扣分累加后仍 ≥ 90 分，但存在节点宕机），**强制降级**为 🔴 异常。规则：出现任一节点非 Running、`BeUp=0` / `FeUp=0`、FE Leader 缺失、🔴 高严重度未处理告警（如 `BeDown`/`FeDown`/`UnhealthyReplica`）、或 FE HA 拓扑不闭环时，评分等级最高为 🔴，与总分独立。

### 核心维度数据缺失的封顶规则（硬规则）

**核心维度**定义：CPU、内存（含 FE JVM）、磁盘、Tablet 健康度 这 4 项。

- 任一核心维度完全不可用（该维度全部指标拉取失败或空值） → **健康分封顶 75（黄牌），不允许出绿牌**
- 报告中必须显式说明「{维度名} 数据缺失 → 本轮评分封顶 75」
- 多项核心维度同时缺失 → 仍为封顶 75（不需叠加下调，但应在报告中列出全部缺失维度）

### 数据不充分时的评分调整

当部分诊断数据不可用（如监控指标拉取失败）时，评分需要降级处理：

| 缺失数据 | 评分调整策略 |
|---------|------------|
| 监控指标完全不可用 | 不给出具体分数，仅基于节点状态和事件数据给出定性等级（🟢/🟡/🔴），并在报告中注明"因监控数据不可用，评分仅基于节点状态和告警事件" |
| 部分节点指标缺失 | 可给出评分，但标注"部分节点数据缺失（-N 分未计入），评分可能偏乐观" |
| 事件历史不可用 | 可给出评分，但标注"告警事件数据不可用，可能遗漏历史问题" |
| 仅节点状态可用 | 仅给出节点存活性评估，不给出综合健康评分 |

> **原则**：宁可标注"数据不充分，无法给出准确评分"，也不要基于不完整数据给出过于乐观的评分。

---

## §4 常见故障模式与根因分析

### 4.1 磁盘空间不足

**信号**：`DiskHigh` 告警、`DiskUsage` > 90%（BE 节点）、`DorisBeDisksLocalUsedCapacity` 接近磁盘总容量

**排查路径**：
1. 确认哪些 BE 节点磁盘使用率高
2. 检查动态分区是否生效（是否在按预期淘汰旧分区）
3. 检查回收站（trash）是否未清理
4. 检查 Compaction 是否堆积导致大量历史 rowset 未合并

**修复建议**（按优先级）：
| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | 清理过期分区：`ALTER TABLE xxx DROP PARTITION pYYYYMMDD` | 立即释放空间 | 数据不可恢复，需确认分区确实过期 |
| P0 | 清理回收站：`ADMIN CLEAN TRASH ON BACKENDS(...)` | 释放 trash 占用空间 | 已删除数据无法恢复 |
| P1 | 检查并修复动态分区策略 | 防止再次堆积 | 无 |
| P1 | 调高 Compaction 并发清理历史 rowset | 加速空间回收 | 增加 IO 和 CPU 消耗 |
| P2 | 扩容磁盘 | 根本解决空间不足 | 需要控制台操作 |

### 4.2 CPU 持续高负载

**信号**：`CpuUsage`（BE 节点）> 80% 持续 5 分钟以上、`NodeLoad1` 超过核数

**排查路径**：
1. 检查 `DescribeOnlineQueryLoads` 是否有长查询
2. 检查是否有复杂查询占用大量 CPU
3. 检查 Compaction 是否过于频繁
4. 检查 `parallel_fragment_exec_instance_num` 是否过高

**修复建议**（按优先级）：
| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | Kill 异常长查询：`ADMIN KILL QUERY "<QueryId>"` | CPU 立即下降 | 查询中断，需通知业务方 |
| P1 | 调整 session 变量降低单查询并行度 | 减少单查询 CPU 占用 | 单查询变慢 |
| P1 | 优化高频慢查询（转到慢 SQL 诊断 Skill） | 根本降低 CPU 消耗 | 需要 SQL 改写 |
| P2 | 错峰调度批量任务 | 避免高峰期资源争抢 | 需业务方配合 |

### 4.3 内存使用率过高 / OOM

**信号**：`MemUsage`（BE 节点）> 85%、`BeOom` 事件、FE JVM 堆使用率（`JvmHeapSizeBytesUsed` / `JvmHeapSizeBytesMax`）> 90%、`JvmOldGcCountV2` 斜率增加

**排查路径**：
1. 检查 BE：`mem_limit` 配置是否过高
2. 检查是否有大查询无 `exec_mem_limit` 限制
3. 检查 FE：metadata 量、audit log 是否过大
4. 检查物化视图/Tablet 数量

**修复建议**（按优先级）：
| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | Kill 大内存查询 | 立即释放内存 | 查询中断 |
| P1 | 设置 session `exec_mem_limit` 限制单查询内存 | 防止单查询耗尽内存 | 大查询可能报错 |
| P1 | 调整 BE `mem_limit`（建议物理内存 80%） | 留足系统内存，避免 OOM Kill | 无 |
| P2 | FE 调高 JVM 堆（`JAVA_OPTS`） | 缓解 FE OOM | 需要重启 FE |
| P2 | 考虑扩容内存或开启存算分离弹性 CN | 根本解决内存不足 | 需要控制台操作 |

### 4.4 Tablet 副本不健康

**信号**：`DorisFeTabletStatusCountTypeUnhealthy` > 0、`UnhealthyReplica` 告警、`DorisFeScheduledTabletNum` 长期 > 0

**排查路径**：
1. 检查 BE 节点状态（是否 Down）
2. 结合告警事件（`UnhealthyReplica`）与 BE 磁盘监控，定位异常副本集中分布的 BE
3. 检查 BE 磁盘是否故障
4. 检查 `DorisFeScheduledTabletNum` 是否在自愈（> 0 表示调度器正在处理）

**修复建议**（按优先级）：
| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | 恢复异常 BE 节点 | 副本自动调度恢复 | 无 |
| P1 | 等待 Tablet 调度器自动 Clone（通常 30 分钟内） | 自动恢复副本 | 无 |
| P1 | 必要时执行 `ADMIN REPAIR TABLE` 强制触发修复 | 加速副本修复 | 无 |
| P2 | 长期不健康副本检查 BE 磁盘故障 | 发现底层硬件问题 | 需要硬件运维 |

### 4.5 连接数耗尽

**信号**：`DorisFeConnectionTotalV2` 接近 `qe_max_connection`、客户端连接被拒绝

**排查路径**：
1. 检查是否有连接泄漏（大量空闲连接）
2. 检查 SHOW PROCESSLIST 是否有 sleep 状态连接
3. 检查客户端连接池配置

**修复建议**（按优先级）：
| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | Kill 长时间 sleep 的连接 | 立即释放连接数 | 客户端可能重连 |
| P1 | 调高 `qe_max_connection` | 提高上限 | 可能增加 FE 资源压力 |
| P2 | 优化客户端连接池配置 | 减少无效连接 | 需业务方配合 |

### 4.6 Compaction 堆积（写入拒绝）

**信号**：`DorisBeTabletCumulativeMaxCompactionScore` 或 `DorisBeTabletBaseMaxCompactionScore` > 1000、`DorisFeMaxTabletCompactionScore` > 1000、`version count exceeded` 错误、写入失败率上升

**排查路径**：
1. 检查写入频率是否过高（高频小批量）
2. 检查 `compaction_task_num_per_disk` 配置
3. 检查 BE 磁盘 IO 是否成为 Compaction 瓶颈
4. 检查 `tablet_max_compaction_score` 阈值

**修复建议**（按优先级）：
| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | 暂停高频小批量写入 | 给 Compaction 喘息时间 | 需业务方配合 |
| P1 | 合并小批量写入为大批量（建议单批 ≥ 4096 行） | 根本减少 Compaction 压力 | 需业务方改造 |
| P1 | 调高 `compaction_task_num_per_disk` | 加速后台合并 | 增加 CPU/IO 消耗 |
| P2 | 调整 `max_tablet_version_num` 提高容忍度 | 避免写入拒绝 | Compaction 落后会更严重 |

### 4.7 业务查询全 0（QPS / 连接数 = 0）

**信号**：`DorisFeQps` 与 `DorisFeConnectionTotalV2` 在观测窗口内**持续为 0**（含两种子形态：24h 全 0；曾有值但突然掉 0）

**背景**：与其他故障模式不同，本模式的信号本身**不足以判定异常**——日志归档、备用/灾备、离线预处理类集群长期 QPS=0 属正常业务态。因此判定必须走"三态区分 + 用户确认"，禁止把兜底表述直接抛给读者。

**三态判定规则**（Skill 必须自动完成，禁止自由发挥）：

| 观测形态 | 判定 | 处理动作 |
|---------|------|---------|
| 24h `DorisFeQps` 全为 0 **且** `DorisFeConnectionTotalV2` 全为 0 | ⚠️ **集群用途待确认**（非异常也非正常） | 通过 `ask_user` 询问集群实际用途：<br>• 用户答"日志归档 / 备用 / 灾备 / 离线"→ 不计入异常，报告"监控"段标注"业务查询长期为空，用户已确认为 XX 用途"<br>• 用户答"在线业务 / 交互查询"→ 升为 🔴 P1 异常项「业务停摆」，进入下方排查路径 |
| 24h 内曾有 QPS/连接，但**突然掉 0** 且持续 ≥ 15 分钟 | 🔴 **P1 业务侧异常**（无需询问用户） | 独立成项，记录掉零时间点（分钟级），进入下方排查路径 |
| 24h 内 QPS/连接持续有值 | ✅ 正常 | 按常规趋势分析 |

**排查路径**（仅在判定为 P1 异常时执行）：
1. 检查 FE Leader 是否发生切换（`FeRole=MASTER` 的节点在掉零时间点前后是否变化）
2. 检查步骤 3 告警事件在掉零时间点前后是否有 `FeDown` / `BeDown` / 网络类告警
3. 检查客户端侧是否可达 FE（跨可用区网络、VPC 路由、安全组）
4. 检查 `qe_max_connection` 是否被打满导致新连接被拒（结合掉零前的连接数斜率）

**修复建议**（按优先级）：
| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | 恢复异常 FE 节点 / 重新选主 | 服务恢复可用 | 需通过控制台操作 |
| P0 | 通知业务方确认客户端连接状态 | 快速区分服务端 / 客户端问题 | 需业务方配合 |
| P1 | 排查网络链路（VPC / 安全组 / DNS） | 恢复连通性 | 需网络运维介入 |
| P2 | 补齐监控告警：为业务查询掉零 15min 配置告警 | 缩短下次发现时间 | 无 |

> ⚠️ **禁止行为**：不得在报告中输出"如属日志归档正常，否则需排查"这类把判定甩给读者的兜底表述——判定必须由 Skill 自身完成（正常 / 用户用途待确认 / P1 异常 三选一）。
