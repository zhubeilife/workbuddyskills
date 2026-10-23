# 集群健康诊断分析框架（TCHouseX / Impala）

> **何时使用本文件**：在步骤 3（资源使用量判断）、步骤 4（操作记录严重度判断）、步骤 6（SQL 历史判断）、步骤 7（综合分析与根因定位、评分）时参考。
> **何时不使用**：工具调用参数请参考 `./api-reference.md`；输出报告格式请参考 `report-template.md`。

---

## 目录

- [§1 关键指标与信号](#1-关键指标与信号)
- [§2 关键指标阈值](#2-关键指标阈值)
- [§3 健康评分规则](#3-健康评分规则)
- [§4 常见故障模式与根因分析](#4-常见故障模式与根因分析)

---

## §1 关键指标与信号

X 引擎（Impala）与 C 引擎（ClickHouse）架构差异较大，X 无独立的告警/事件接口，也无 `MonitorDescribeDashboardMetricData` 工具，且本 Skill 不使用需要账号密码的 DMS/SQL 工作区接口。本 Skill 通过以下四方联查代偿：

| 数据源 | 覆盖能力 | 使用接口 |
|--------|---------|---------|
| **实例/计算组状态** | 实例状态、计算组 CN 节点状态、实时 CPU、基础服务节点状态 | `DescribeInstance`（主数据源，`VirtualClusters` 已达节点级粒度）；`DescribeInstanceWarehouse`（仅在 `VirtualClusters` 缺失/需实时数据时条件触发） |
| **资源使用量趋势** | 存储/计算资源用量的时序变化，容量风险预警 | `DescribeInstanceResourceUsage` |
| **变更事件** | 集群升降配/重启/配置变更等操作记录，用于关联"变更是否是故障诱因" | `DescribeInstanceOperationsV1` |
| **SQL 运行情况** | 近期失败/慢 SQL 占比、TopN 异常 QueryID | `DescribeSqlHistoryRecords` |
| **单条 SQL 深入分析** | 具体 QueryID 的算子耗时与执行计划（条件触发） | `DescribeInstanceProfile` |

---

## §2 关键指标阈值

### 2.1 SQL 运行健康（来自 `DescribeSqlHistoryRecords`）

| 指标 | 含义 | 正常 | 警告 | 严重 |
|------|------|------|------|------|
| 近 1 小时失败 SQL 占比 | `State IN ('EXCEPTION', 'CANCELED')` 的占比 | < 5% | 5%~20% | > 20% |
| 近 1 小时慢 SQL 占比 | `Duration > 60000`（毫秒）的占比 | < 5% | 5%~20% | > 20% |
| 单条最长运行时长 | 历史记录中 `max(Duration)` | < 60s | 60~300s | > 300s |
| 同一异常 SQL 的重复次数 | 同一 QueryID/Statement 反复失败次数 | 0 | 1~5 | > 5 |

### 2.2 实例与计算组状态（主要来自 `DescribeInstance.VirtualClusters`，条件时补调 `DescribeInstanceWarehouse`）

| 检查项 | 正常 | 警告 | 严重 |
|--------|------|------|------|
| `InstanceInfo.Status`（字符串枚举，完整映射见 [api-reference.md §2](./api-reference.md#status-枚举清单)） | `Serving` | 变更进行中的瞬态（`Init`/`Starting`/`Restarting`/`Suspending`/`Configuring`/`Changing`/`Scale*`/`GracefulServingScaleCountExpanding`/`Isolating`/`Renew`/`Cancelling`/`PrepareCancelling`）或 `Suspend`（已暂停） | `Isolated` / `CreateFail` / `DeleteFail` / `Deleted` / `Deleting` |
| 基础服务节点（`VirtualCluster == "default-cluster"` 中 `catalogd`/`access-server`/`livy` 等关键组件） | 均运行中且 ≥ 高可用数量 | 1 个非运行 | ≥ 2 个非运行 / 关键服务 0 节点 |
| 用户计算组（`Component="impalad"`）CN 节点数 | 与规格匹配 | 部分节点异常 | 全部节点异常 |
| 计算组 `ClusterStateInfo.InstanceState` | `Serving` | 变更中（有 `FlowProgress`） | `Isolated`/`CreateFail`/`Deleted` 等异常枚举 |
| `WarehouseInfo.CurrentRealtimeCpuResource` | < 60% | 60%~80% | > 80% 持续 |
| 计算组 `Resources[].Status` | 均为运行中 | 部分节点异常 | 多数节点异常 |

### 2.3 资源使用量（来自 `DescribeInstanceResourceUsage`）

> ResourceType 至少查询 `Storage` 与 `Warehouse` 两种。使用率 = 用量 / 规格上限（结合 `DescribeInstance` 中的规格）。

| 检查项 | 正常 | 警告 | 严重 |
|--------|------|------|------|
| `Storage` 使用率 | < 70% | 70%~85% | > 85% |
| `Storage` 24 小时增速 | < 10%/日 | 10%~20%/日 | > 20%/日 |
| `Warehouse` CPU 使用率（时序均值） | < 60% | 60%~80% | > 80% |
| `Warehouse` CPU 使用率峰值 | < 80% | 80%~95% | > 95% |

### 2.4 集群操作记录（来自 `DescribeInstanceOperationsV1`）

| 场景 | 严重程度 | Agent 优先级 |
|------|---------|-------------|
| 24 小时内有升降配/重启操作 | 🟡 中 | 关联故障时间，判断是否为诱因 |
| 存在失败状态（`State` 表示失败）的操作 | 🔴 高 | 立即分析，可能是当前故障的直接原因 |
| 存在正在运行中的操作 | 🟡 中 | 告知用户变更中，建议等待完成后再诊断 |
| 24 小时内无变更操作 | 🟢 低 | 排除变更相关根因 |

---

## §3 健康评分规则

> **原则**：评分必须可追溯，报告里给出的分数必须能对应到下方的扣分项，禁止拍脑袋给分。

### 评分方法：100 分制扣分

起始分 **100 分**，按下列规则逐项扣分，扣完为止（最低 0 分）。所有扣分必须在报告的"扣分明细"表中列出，让用户可以复核。

#### 扣分项 A：实例/节点/计算组异常

| 现象 | 扣分 |
|------|------|
| `InstanceInfo.Status = "Isolated"` / `"CreateFail"` / `"DeleteFail"`（明确异常字符串） | **-30 分** |
| `InstanceInfo.Status = "Suspend"`（已暂停，业务受影响但集群未损坏） | **-20 分** |
| `InstanceInfo.Status = "Deleted"` / `"Deleting"`（已销毁/销毁中） | **-100 分**（直接置 0） |
| 每个非运行状态的**基础服务关键节点**（`default-cluster` 中 `Component` 为 `catalogd`/`access-server`/`livy` 之一） | **-20 分** |
| 每个非运行状态的**基础服务非关键节点**（`default-cluster` 中 `Component` 为 `mysql`/`chdfs`/`cfs`/CLB 等） | **-15 分** |
| 每个非运行状态的**用户计算组**（`ClusterStateInfo.InstanceState` 异常） | **-15 分** |
| 每个非运行状态的**用户计算组 CN 节点**（`Component="impalad"`） | **-8 分**（同一计算组内累计封顶 -20 分） |

#### 扣分项 B：集群操作记录（`DescribeInstanceOperationsV1`，仅统计 24 小时内）

| 严重程度 | 扣分（每条） | 单项封顶 |
|---------|-------------|----------|
| 🔴 高（失败状态的变更操作） | **-15 分** | -30 分 |
| 🟡 中（正在运行中的变更） | **-5 分** | -10 分 |
| 🟢 低（已完成的正常变更） | 不扣分（仅作为诊断线索） | — |

#### 扣分项 C：资源使用量（`DescribeInstanceResourceUsage`）

| 指标 | 达到"严重阈值" | 达到"警告阈值" | 单类别封顶 |
|------|:-------------:|:-------------:|:---------:|
| Storage 使用率（> 85% / 70%） | **-15 分** | **-8 分** | -15 分 |
| Storage 增速（> 20%/日 / 10%~20%/日） | **-10 分** | **-5 分** | -10 分 |
| Warehouse CPU 使用率均值（> 80% / 60%~80%） | **-10 分** | **-5 分** | -15 分 |
| Warehouse CPU 使用率峰值（> 95% / 80%~95%） | **-8 分** | **-4 分** | 与上一行合并封顶 -15 分 |

#### 扣分项 D：SQL 运行健康（`DescribeSqlHistoryRecords`）

| 指标 | 达到"严重阈值" | 达到"警告阈值" | 单类别封顶 |
|------|:-------------:|:-------------:|:---------:|
| 失败 SQL 占比（> 20% / 5%~20%） | **-15 分** | **-6 分** | -15 分 |
| 慢 SQL 占比（> 20% / 5%~20%） | **-10 分** | **-4 分** | -10 分 |
| 单条最长运行时长（> 300s / 60~300s） | **-8 分** | **-4 分** | -8 分 |
| 同一异常 SQL 的重复次数（> 5 / 1~5） | **-6 分** | **-3 分** | -6 分 |

**同一指标的判定规则**：

- 同一指标既触发警告又触发严重 → 按严重阈值扣分，不叠加
- 多个 Warehouse 都触发同一档 CPU 阈值 → 按数量计入，但受"单类别封顶"约束

### 评分等级映射

| 分数区间 | 等级 |
|---------|------|
| 90 – 100 | 🟢 **健康** |
| 70 – 89  | 🟡 **警告** |
| 0  – 69  | 🔴 **异常** |

> 若最终得分与"最严重单项"表现不一致（例如所有扣分累加后仍 ≥ 90 分，但存在基础服务关键节点异常或 `InstanceInfo.Status ∈ {"Isolated","CreateFail","DeleteFail","Deleted","Deleting"}`），**强制降级**为 🔴 异常。规则：出现任一基础服务关键节点（`catalogd`/`access-server`/`livy`）非运行、`InstanceInfo.Status ∈ {"Isolated","CreateFail","DeleteFail","Deleted","Deleting"}`、存在失败状态的变更操作时，评分等级最高为 🔴，与总分独立。

### 数据不充分时的评分调整

当部分诊断数据不可用时，评分需要降级处理：

| 缺失数据 | 评分调整策略 |
|---------|------------|
| `DescribeInstance` 失败 | 不给评分，直接告知用户实例信息无法获取 |
| `DescribeInstanceWarehouse` 失败（仅在条件触发时才会调用） | 回退到 `DescribeInstance.VirtualClusters` 中的已有数据，仅在报告中注明「未能拿到最新瞬实时 CPU」 |
| `DescribeInstanceResourceUsage` 失败 | 扣分项 C 全部不计入，报告中注明"资源用量数据不可用" |
| `DescribeInstanceOperationsV1` 失败 | 扣分项 B 不计入，注明"操作记录不可用" |
| `DescribeSqlHistoryRecords` 失败 | 扣分项 D 全部不计入，仅基于步骤 1-5 给出定性等级（🟢/🟡/🔴），注明"SQL 侧数据不可用" |
| `DescribeSqlHistoryRecords` 返回 0 条记录 | 扣分项 D 全部不计入；报告中注明「当前时间窗口内无 SQL 运行样本，SQL 健康度未纳入评分，建议扩大时间窗口或选择业务高峰时段复测」；与"调用失败"不同，**评分等级不强制降级** |
| `DescribeInstanceProfile` 失败 | 不影响扣分（本身是条件触发的深挖工具），仅注明"具体 QueryID 无法深入分析" |

> **原则**：宁可标注"数据不充分，无法给出准确评分"，也不要基于不完整数据给出过于乐观的评分。

---

## §4 常见故障模式与根因分析

### 4.1 长时间运行查询堆积（CPU/连接异常的常见前兆）

**信号**：`DescribeSqlHistoryRecords` 中出现 `Duration > 60000ms` 的查询多条；`WarehouseInfo.CurrentRealtimeCpuResource` 高

**排查路径**：
1. 用 `DescribeSqlHistoryRecords`（按 `ExecuteTimeOrder=desc` 排序）找出 TopN 慢查询，读取 `QueryID` / `Statement` / `SubmitUser`
2. 对 TopN 慢查询调用 `DescribeInstanceProfile` 获取详细 profile，定位耗时算子（`ScanNode` / `HashJoinNode` / `AggregationNode`）
3. 对比多个 Warehouse 的 `CurrentRealtimeCpuResource`，定位问题计算组

**修复建议**（按优先级）：

| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | Kill 异常长查询：`KILL QUERY <query_id>` | 立即释放资源 | 查询中断，需通知业务方 |
| P1 | 检查 SQL 是否走了笛卡尔积 / 全表扫描 / BROADCAST 大表 | 根本降低 CPU/内存消耗 | 需要 SQL 改写 |
| P1 | 调整 Coordinator/Executor 内存限制（`MEM_LIMIT`） | 防止单查询独占节点 | 大查询可能报错 |
| P2 | 错峰调度批量任务 | 避免高峰期资源争抢 | 需业务方配合 |

### 4.2 大量 SQL 失败（State=EXCEPTION/CANCELED）

**信号**：近 1 小时失败 SQL 占比 > 20%

**排查路径**：
1. 拉取失败 SQL 样本（`State=EXCEPTION` 或 `CANCELED`）
2. 分类失败原因（按 SQL 错误码或 Statement 模式）：
   - `MEMORY_LIMIT_EXCEEDED`：内存不足
   - `AnalysisException` / `ParseException`：SQL 语法或元数据问题
   - `IMPALA-XXXXX`：Impala 已知 Bug
   - 超时 / 客户端取消

**修复建议**：

| 失败类型 | 建议 |
|---------|------|
| `MEMORY_LIMIT_EXCEEDED` | 调高 Coordinator/Executor `MEM_LIMIT`；检查是否有 BROADCAST 大表；建议改用 SHUFFLE JOIN |
| `AnalysisException`（元数据错误） | `INVALIDATE METADATA <db>.<tbl>` 强制刷新 Catalog |
| 客户端取消 | 检查客户端超时配置、Workload 调度策略 |
| Impala Bug | 提工单或升级 Impala 版本 |

### 4.3 元数据延迟 / Catalog 异常

**信号**：新建/修改的表无法被查询；`DescribeSqlHistoryRecords` 中出现较多 `AnalysisException` / `TableLoadingException` / "Could not resolve table reference" 类失败 SQL

**排查路径**：
1. 检查近期是否有大量 DDL 操作（结合 `DescribeInstanceOperationsV1` + 业务方反馈）
2. 从 `DescribeSqlHistoryRecords` 中筛选元数据相关错误的 SQL 样本，识别涉及的库表
3. 观察涉及新表/新分区的查询是否集中失败在 DDL 后短时间内

**修复建议**：

| 优先级 | 操作 | 预期效果 |
|--------|------|---------|
| P0 | `INVALIDATE METADATA <db>.<tbl>` 针对单表刷新 | 立即生效 |
| P1 | 避免高频 DDL（DROP/ADD PARTITION 频率 > 1 次/秒） | 减轻 Catalog 压力 |
| P1 | 避免全库 `INVALIDATE METADATA`，改用 `REFRESH <db>.<tbl>` 增量刷新 | 减轻 Catalog 内存压力 |
| P2 | 联系运维扩容 Catalog 节点内存 | 根本解决 |

### 4.4 计算组（Warehouse）资源不均衡

**信号**：`DescribeInstanceWarehouse` 显示某 Warehouse `CurrentRealtimeCpuResource` 高，其他 Warehouse 空闲；或 SQL 历史中某 Warehouse 出现大量慢/失败查询

**排查路径**：
1. 对每个 Warehouse 调用 `DescribeInstanceWarehouse`，统计各自的实时 CPU 使用与 CN 节点状态
2. 通过 `DescribeSqlHistoryRecords` 按 Warehouse 维度（如 SQL 记录中有 Warehouse 字段）统计慢/失败查询分布
3. 比对各 Warehouse 的节点数和负载

**修复建议**：

| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | 将高负载 Warehouse 中的长查询 `KILL QUERY` 疏散 | 立即缓解 | 业务方查询中断 |
| P1 | 按业务（在线分析 / 批量 ETL）拆分 Warehouse，互不干扰 | 根本消除干扰 | 需业务方配合 |
| P1 | 对受影响 Warehouse 独立扩容（增加 CN 节点或升配） | 提升计算能力 | 需要控制台操作 |
| P2 | 配置 Workload 路由规则，将慢查询统一引到独立 Warehouse | 长期治理 | 需运维配合 |

### 4.5 存储空间不足

**信号**：`DescribeInstanceResourceUsage`（Storage）使用率 > 85%；或用户报告磁盘告警

**排查路径**：
1. 通过 `DescribeInstanceResourceUsage`（ResourceType=Storage）拉取时序数据，判断增速趋势
2. 关联 `DescribeInstanceOperationsV1`，看近期是否有大量导入/建表操作
3. 建议用户在控制台/SQL 客户端手动执行 `SHOW TABLE STATS` / `SHOW FILES IN` 排查大表与小文件问题（本 Skill 不代执行）

**修复建议**（按优先级，均为**建议**由用户在自己的 SQL 客户端执行）：

| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | `ALTER TABLE xxx DROP PARTITION 'yyyymm'` 清理过期分区 | 立即释放空间 | 数据不可恢复，需确认分区确实过期 |
| P1 | `INSERT OVERWRITE TABLE <tbl> PARTITION(...) SELECT ...` 重写分区合并小文件 | 减少 Parquet 小文件、降低元数据压力 | 消耗 IO 与计算，建议低峰期 |
| P1 | 检查并配置表的分区保留策略 | 防止再次堆积 | 需业务方确认 |
| P2 | Core(Executor) 节点扩容或加大磁盘 | 根本解决空间不足 | 需要控制台操作 |

### 4.6 内存 OOM / MEMORY_LIMIT_EXCEEDED

**信号**：SQL 历史中大量 `MEMORY_LIMIT_EXCEEDED` 错误；Warehouse CPU 高伴随查询失败

**排查路径**：
1. 拉取失败 SQL 样本，确认 `Statement` 是否包含大表 JOIN、无 WHERE 过滤的全表扫描等
2. 通过 `DescribeInstanceProfile` 查具体 QueryID 的 ProfileStr，确认大表是否走了 BROADCAST
3. 检查表统计是否过期（导致 CBO 选错 JOIN 顺序）

**修复建议**：

| 优先级 | 操作 | 预期效果 | 风险 |
|--------|------|---------|------|
| P0 | Kill 内存占用过大的查询 | 立即释放内存 | 查询中断 |
| P1 | 调整 SQL：加 `WHERE` 过滤、大表加 `/*+ SHUFFLE */` Hint | 防止单查询耗尽内存 | 需 SQL 改写 |
| P1 | 对高频查询表执行 `COMPUTE STATS <db>.<tbl>` 更新统计 | 优化器选对 JOIN 顺序 | 消耗资源，建议低峰期 |
| P2 | Warehouse 升配（增加单节点内存） | 提高容忍度 | 需要控制台操作 |

### 4.7 集群变更引发的短时故障

**信号**：`DescribeInstanceOperationsV1` 中最近 24 小时内有升降配/重启/配置变更操作，且时间上与用户报告的故障吻合

**排查路径**：
1. 对齐操作时间与故障时间（用户描述 vs `OperateTime`）
2. 检查变更类型（`OperateName`）与 `State`
3. 若变更未完成或失败，通常故障与变更强相关

**修复建议**：

| 优先级 | 操作 | 预期效果 |
|--------|------|---------|
| P0 | 若变更失败，联系运维回滚或续操作 | 恢复变更前状态 |
| P1 | 若变更已完成但集群仍不稳定，观察 30 分钟看是否自愈 | Impala 集群通常需要短暂 warm up |
| P2 | 建议避免高峰期变更 | 长期治理 |

---

> ⚠️ **修复建议仅为建议，不代执行**：`KILL QUERY` / `INVALIDATE METADATA` / `COMPUTE STATS` / `REFRESH` / `DROP PARTITION` / `INSERT OVERWRITE` 等命令由用户在自己的 SQL 客户端执行；本 Skill 仅通过管控面云 API 完成诊断，不调用需要账号密码的 DMS/SQL 工作区接口。
