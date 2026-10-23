# TCHouseX MCP 工具参考（API Reference）

> **何时使用本文件**：在调用任意 TCHouseX MCP 工具前，先在此查阅工具的**入参字段、必填项、取值范围、典型用法**；调用失败或参数错误时回到本文件核对。
> **何时不使用**：业务诊断/SQL 生成/可视化/选型规则等业务知识请参考各 skill 自己的 references 文档；本文件**只描述工具自身**。

---

## 0. 通用约定

### 0.1 命名规则
- MCP 工具统一前缀：`TCHouseX*`
- X 云 API（域名 `tchousex.tencentcloudapi.com`）`Action` 字段对应 X 引擎的真实 API 名（**不一定与 MCP tool 名完全一致**），请以"X 云 API Action"列为准。

### 0.2 公共必填参数
- `Region`：地域代码，详见 [region-mapping.md](./region-mapping.md)。TCHouseX 实际支持地域以接口返回为准（`TCHouseXDescribeRegionZone` 或运行时 `UnsupportedRegion` 错误码），skill **不做**离线白名单校验。
- `InstanceId`：X 实例 ID，**统一使用 `instance-` 前缀**（如 `instance-n2wrhcjh`）。

### 0.3 实例 ID 格式
| 产品 | 前缀 | 示例 |
|------|------|------|
| TCHouseX（Impala） | `instance-` | `instance-n2wrhcjh` |
| TCHouseX（warehouse 老版） | `warehouse-` | `warehouse-ooj2s44q`（仅历史接口出现，新接口统一 `instance-`） |

---

## 1. TCHouseXDescribeRegionZone — 获取支持的地域、可用区与内核版本列表

- **X 云 API Action**：`DescribeRegionZone`（对应 `tchousex-2023-04-11/信息查询相关接口/获取大地域信息等.md`）
- **用途**：控制台/购买页拉取 X 支持的大地域、地域、可用区，以及**可用内核版本**、白名单规则、前端规则。
- **何时调用**：用户提到地域但不确定是否支持时；选型推荐前确定可用 Zone；**读取 `Versions` 决定推荐的内核版本**。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 公共参数。传实际业务地域即可（如 `ap-guangzhou`、`ap-shanghai`、`ap-beijing`、`ap-chongqing`），接口返回内容为全量地域列表 |
| InstanceType | 是 | String | 产品类型。**TCHouse-X 选型固定传 `warehouse`**；若不传或传错会导致返回的 `Versions` 为空，进而后续询价失败 |

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| Items | Array of RegionAreaInfo | 大地域列表，含 `Name`（大区名，如 `china`）/ `Desc` / `Regions[]` |
| Items[].Regions[] | Array | 地域列表，每项含 `Name`（如 `ap-guangzhou`）/ `Desc` / `RegionID`（数字 ID）/ `Count` / `OfflineResource` / `OfflineResourceLimit` / `RealtimeResource` / `RealtimeResourceLimit` / `Zones[]` |
| Items[].Regions[].Zones[] | Array | 可用区列表，每项含 `Name`（如 `ap-guangzhou-3`）/ `Desc` / `ZoneID`（数字 ID）/ `Encrypt` |
| Versions | Array of String | **当前可用的内核版本列表**（如 `["1.1.0_REL", "1.0.0_REL"]`），选型推荐时**优先取该字段的最新稳定版本**作为 `ProductVersion` |
| VersionInfos | Array of VersionInfo | 按 `ClusterType` 分组的内核版本（每项含 `ClusterType` + `Versions[]`） |
| ClusterTypes | Array of Integer | 支持的集群类型 |
| IsYunti | Boolean | 是否云梯 |
| ErrorMsg | String | 错误信息 |

---

## 2. TCHouseXDescribeInstance — 查询 X 实例详情

- **X 云 API Action**：`DescribeInstance`
- **用途**：根据 `InstanceId` 获取 X 实例的版本、规格、节点拓扑、网络信息、状态等。
- **何时调用**：所有诊断 / 选型 / SQL 执行类任务的**第一步**，用于确认实例是否存在、版本与拓扑。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| InstanceId | 是 | String | 实例 ID（`instance-xxx`） |

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| InstanceInfo.Version | String | Impala 内核版本（如 `1.10.0_REL`） |
| InstanceInfo.Status | **String** | 状态枚举字符串。**注意：此字段已从旧版 Int 变更为 String**，取值见下方「Status 枚举清单」 |
| InstanceInfo.StatusDesc | String | 状态的中文描述（如「运行中」「已暂停」） |
| InstanceInfo.VirtualClusters[] | Array | **计算组列表（替代旧版 `WarehouseList`）**，每个元素结构与 `DescribeInstanceWarehouse.VirtualCluster` **完全等价**，含 `VirtualCluster`（VC 标识）/ `VirtualClusterName`（展示名）/ `Resources[]`（节点级 IP/Cpu/Memory/Storage/Status/Component/DeployMode 等）/ `ClusterStateInfo`（`InstanceState`/`InstanceStateDesc`/`FlowProgress`/`FlowMsg`）/ `WarehouseInfo.CurrentRealtimeCpuResource`（实时 CPU 资源占用）等 |
| InstanceInfo.VirtualClusterCount | Int | 计算组数量 |
| InstanceInfo.Tags | Array | 标签 |

### Status 枚举清单

| 枚举值 | 中文含义 | 后端码 | 备注 |
|--------|---------|-------|------|
| `Init` | 创建中 | 1 | — |
| `Serving` | 运行中 | 2 | 允许操作 |
| `Starting` | 启动中 | 3 | — |
| `Restarting` | 重启中 | 4 | — |
| `Suspending` | 暂停中 | 5 | — |
| `Suspend` | 已暂停 | -1 | 业务受影响，可恢复 |
| `Isolated` | 已隔离 | 6 | — |
| `Deleting` | 销毁中 | -2 | — |
| `ScaleChanging` | 节点变更中（规格 & 节点） | 7 | — |
| `ScaleCountExpanding` | 扩容中（节点个数变更） | 8 | 允许操作 |
| `ScaleCountReducing` | 缩容中 | 9 | — |
| `ScaleSpecUpgrading` | 升配中（节点规格变更） | 10 | — |
| `ScaleSpecDescending` | 降配中 | 11 | — |
| `GracefulServingScaleCountExpanding` | 优雅扩容且服务中 | — | 允许操作 |
| `Deleted` | 已销毁 | — | — |
| `Renew` | 续费 | — | — |
| `Changing` | 集群变更中 | — | 当前实际使用的「变更中」（旧 `Modify` 已废弃） |
| `CreateFail` | 创建失败 | — | — |
| `DeleteFail` | 销毁失败 | — | — |
| `Isolating` | 隔离中 | — | — |
| `Configuring` | 配置中 | — | — |
| `PrepareCancelling` / `Cancelling` | 取消中 | — | — |

### `VirtualClusters` 内部约定

- 每个实例都会有一个 `VirtualCluster="default-cluster"` 的元素，其 `Resources[]` 承载 **基础服务节点**（`Component` 为 `catalogd`/`access-server`/`livy`/`livy-meson`/`chdfs`/`cfs`/`mysql`/CLB 等），不是用户可见的计算组。
- 用户创建的 **计算组（Warehouse）** 在 `VirtualClusters[]` 中以 `Component="impalad"` 的元素出现，`VirtualCluster` 形如 `vw-xxx`，`VirtualClusterName` 为用户命名。
- 诊断时应按 `VirtualCluster == "default-cluster"` vs. 其他值区分「基础服务组」和「用户计算组」。

> 📌 **字段变更说明**：`DescribeInstance` 接口已升级：
> - 旧字段 `WarehouseList` → 现为 `VirtualClusters`，且**已从汇总升级为节点级完整详情**（与 `DescribeInstanceWarehouse` 等价）；
> - 旧字段 `MasterSummary` / `CoreSummary` **已下线**，实例的节点拓扑统一从 `VirtualClusters` 中读取；
> - `Status` 类型从 `Int` 变更为 `String`；旧数值码可通过上表映射。

---

## 3. TCHouseXDescribeSpec — 获取可选购集群规格档位

- **X 云 API Action**：`DescribeSpec`（对应 `tchousex-2023-04-11/信息查询相关接口/云原生获取集群规格.md`）
- **用途**：购买页拉取集群的**数据节点规格档位（Warehouse）** 与 **离线任务规格档位（Serverless/Spark）**。
- **何时调用**：集群选型推荐时；用于交叉验证经验档位表是否与售卖状态一致。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 公共参数，地域 |
| InstanceType | 否 | String | 产品类型，示例值 `warehouse`（TCHouse-X 场景传 `warehouse`） |

> ⚠️ **注意**：本接口**没有** `Zone`、`PayMode` 参数；且**不返回**内核版本。内核版本请从 `TCHouseXDescribeRegionZone.Versions` 获取。

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| Specs | Array of SpecMap | Warehouse 数据节点规格档位数组 |
| Specs[].Id | Integer | 规格 ID |
| Specs[].Type | Integer | 规格类型 |
| Specs[].Name | String | 规格名（如 `2X-Small` / `X-Small` / `Small` / `Medium` / `Large`） |
| Specs[].Desc | String | 规格描述 |
| Specs[].Cpu | Integer | 单节点 vCPU 数 |
| Specs[].Memory | Integer | 单节点内存（GiB） |
| Specs[].MinStorage | Integer | 最小存储（GiB，对象存储场景可能为 0） |
| Specs[].MaxStorage | Integer | 最大存储（GiB） |
| Specs[].BillingParam | String | 计费参数标识 |
| Specs[].Disabled | Boolean | 是否禁用（true 表示该档位当前不可售） |
| SparkSpecMaps | Array of SparkSpecMap | **Serverless / Spark 离线任务规格档位**（Executor / Driver 可选规格） |
| SparkSpecMaps[].ID | Integer | Spark 规格 ID |
| SparkSpecMaps[].Type | String | Spark 规格类型 |
| SparkSpecMaps[].Name | String | Spark 规格名 |
| SparkSpecMaps[].Desc | String | Spark 规格描述 |
| SparkSpecMaps[].Cpu | Integer | Spark 规格 vCPU 数 |
| SparkSpecMaps[].Disabled | Boolean | 是否禁用 |
| ErrorMsg | String | 错误信息 |

---

## 4. TCHouseXDescribeGoodsDetail — 询价「两步链路」的 Step A（获取商品配置）

- **X 云 API Action**：`DescribeGoodsDetail`（对应 `tchousex-2023-04-11/信息查询相关接口/生成CNGoodsDetail.md`）
- **用途**：生成计费相关接口的 **商品配置（GoodsDetail 结构）**；**本接口不返回金额**，必须把返回的 `GoodsCategoryId` + `GoodsDetailStr` + `GoodsNum` + `PayMode` 透传给 `BillingCalculatePrice`（Step B）拿到真实金额。
- **何时调用**：集群选型推荐 / 升降配建议的费用估算第 1 步。

> ⚠️ **询价链路一律走两步**：`TCHouseXDescribeGoodsDetail` → `BillingCalculatePrice`。详见 [tchousex-cluster-sizing-recommendation/references/cost-estimation-guide.md §5](../skills/tchousex-cluster-sizing-recommendation/references/cost-estimation-guide.md#5-实时询价两步链路主路径)。

### 入参（核心）
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| Case | 是 | String | 操作类型（注意大小写不完全一致）：`create_instance`（新建实例）/ `create_warehouse`（已有实例下新建 Warehouse）/ `scale_instance`（变配）/ `regular_start`（定时启动）/ `RENEW`（续费，大写）。**选型/询价 skill 场景固定传 `create_instance`** |
| IsQueryPrice | 是 | Boolean | 是否询价，选型场景固定 `true` |
| InstanceType | 是 | String | 产品类型，TCHouse-X 传 `warehouse` |
| Type | 是 | String | 子商品码。**请求传 `sp_cdwch_cn`**（与购买页一致）；服务端会自动映射并在响应中回填为 `sp_tchouse_x_v2` |
| Zone | 否 | String | 可用区，如 `ap-guangzhou-3` |
| UserVPCId | 否 | String | 用户 VPC ID。询价场景（`IsQueryPrice=true`）**无需传入**，tool 会自动填占位以通过云API校验；创建集群时必须传真实值 |
| UserSubnetId | 否 | String | 用户子网 ID。询价场景（`IsQueryPrice=true`）**无需传入**，tool 会自动填占位以通过云API校验；创建集群时必须传真实值 |
| UserSubnetIPNum | 否 | Integer | 用户子网剩余可用 IP 数（**必须 > 6**） |
| ProductVersion | 否 | String | 内核版本，如 `2.2.3_DEV`；**优先取 `TCHouseXDescribeRegionZone.Versions` 的最新稳定版本** |
| InstanceName | 否 | String | 创建集群时的实例名。询价场景（`IsQueryPrice=true`）**无需传入**，tool 会自动填占位 |
| VirtualClusterName | 否 | String | Warehouse 名称（云API 要求中文格式，**最少 6 个字符**）。询价场景（`IsQueryPrice=true`）**无需传入**，tool 会自动填占位以通过云API校验；创建集群时必须传真实值且长度 ≥ 6 字符 |
| InstanceId | 否 | String | 集群 ID（`CREATE` 时为空，`MODIFY`/`RENEW` 必填） |
| Resources.N | 否 | Array of ResourceSpec | 集群资源规格描述，见下方注释 |
| ModifySpec | 否 | ResourceSpec | 集群规格修改参数（`MODIFY` 场景） |
| ChargeProperties | 否 | ChargeProperties | 计费信息，`{ChargeType: "POSTPAID_BY_HOUR", TimeSpan: 1, TimeUnit: "h", RenewFlag: 0}`；TCHouse-X 仅按量，`ChargeType` 固定 `POSTPAID_BY_HOUR` |
| TCLakeSpec | 否 | TCLakeSpec | `{CatalogType: "LAKEHOUSE", CatalogNameType: "SYSTEM"}` |
| WarehouseType | 否 | Integer | **`0`=标准 Warehouse（标准版），`1`=弹性 Warehouse（弹性版，即自适应/Adaptive Warehouse）**。本 Skill 中的「自适应 Warehouse」在本字段中对应 `1` |
| ServerlessSpec | 否 | ServerlessSpec | `WarehouseType=1`（自适应/弹性 Warehouse）时必填，含 `{WarehouseMaxCuCount, WarehouseMaxClusterSize}`（Warehouse 弹性伸缩上限：单集群最大 CU 数、最大并发集群数），默认均为 64；`WarehouseType=0` 时不传或传空对象 `{}` |
| SparkSpec | 否 | SparkSpecV1 | Spark 规格 |
| RegularPlan | 否 | RegularPlan | 定时启停执行计划 |
| ElasticPlan | 否 | ElasticPlan | 分时弹性执行计划 |
| AutoScalePlan | 否 | AutoScalePlan | 自动扩缩容参数 |
| TCIMode | 否 | Integer | `1`=共享模式，`2`=独占模式。询价场景（`IsQueryPrice=true`）**无需传入**，tool 会默认填 `1` |
| CipherMode | 否 | Integer | 加密存储方式：`1`=不加密 / `2`=cos / `3`=kms |
| SupportLoginType.N | 否 | Array of Integer | 登录方式：`1`=非 CAM / `2`=CAM |
| LdapConfig | 否 | LdapConfig | LDAP 配置 |
| EnableSSL | 否 | Boolean | 是否开启 SSL |
| IsSecondaryZone | 否 | Boolean | 是否多可用区 |
| SecondaryZoneInfo.N | 否 | Array of SecondaryZoneInfo | 多可用区信息 |
| Tags.N | 否 | Array of Tag | 标签 |

> 📌 **`Resources.N` 只需提供用户可见的**数据计算节点**（`Component: "impalad"`，`DeployMode: 0`）与其 CLB（`Component: "impalad"`，`SpecName: "CLB"`，`DeployMode: 2`）。`access-server` / `livy-meson` / `tccatalog` 等接入服务/元数据节点由服务端自动补齐，无需调用方传入。`DeployMode`：`0`=计算节点，`1`=普通独立部署，`2`=CLB 负载均衡。

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| Type | String | 子商品码，TCHouse-X 为 `sp_tchouse_x_v2` |
| GoodsCategoryId | Integer | 商品类目 ID，**Step B (`BillingCalculatePrice`) 必填** |
| GoodsDetailStr | String | 商品完整明细 JSON 字符串。**⚠️ 传给 Step B 前必须做 key camelCase 转换（所有字段全部保留、严禁删除 `sv_tchouse_x_warehouse_hp` 等字段），详见 [cost-estimation-guide.md §5.3.1](../skills/tchousex-cluster-sizing-recommendation/references/cost-estimation-guide.md#531-goodsdetailstr--goodsdetail-转换强制步骤不可跳过)**，严禁原样透传 |
| GoodsDetail | String | 商品明细（通常为空） |
| GoodsNum | Integer | 商品数量，通常为 1，**Step B 必填** |
| PayMode | Integer | 付费模式：`0`=后付费，`1`=预付费（TCHouse-X 当前仅返回 `0`） |
| RegionId | Integer | 地域数字 ID |
| ZoneId | Integer | 可用区数字 ID |
| ResourceId | String | 资源标识符（预生成的 `instance-xxx`） |
| ErrorMsg | String | 错误信息（成功时为空） |
| RequestId | String | 请求 ID |

> 💰 **关键说明**：**本接口响应中不含 `Price` / `TotalCost` / `RealTotalCost` 等金额字段**。所有金额来自 Step B `BillingCalculatePrice` 的返回；`BillingCalculatePrice` 的入参、金额单位（分）与精度处理详见 [cost-estimation-guide.md §5.3](../skills/tchousex-cluster-sizing-recommendation/references/cost-estimation-guide.md#53-step-b调用-billingcalculateprice)。

---

## 5. TCHouseXDescribeSqlHistoryRecords — 查询在线 SQL 运行记录（替代 C 的 SlowQueryRecords）

- **X 云 API Action**：`DescribeSqlHistoryRecords`
- **对应 C 工具**：`TCHouseCDescribeSlowQueryRecords`
- **用途**：拉取 X 实例上**已运行的 SQL 历史记录**（含 QueryID、SQL、用户、状态、开始时间、耗时）。
- **何时调用**：慢 SQL 诊断时拉取慢查询样本；同时也可作为"慢查询趋势"的数据源——对返回结果按时间桶聚合即可得到趋势。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| InstanceId | 是 | String | 实例 ID |
| QueryOnlineLogReq | 否 | Object | 查询过滤条件（见下） |

### `QueryOnlineLogReq` 子字段
| 字段 | 类型 | 说明 |
|------|------|------|
| StartTime | Int | 起始时间（Unix 秒） |
| EndTime | Int | 结束时间（Unix 秒） |
| Offset | Int | 偏移量（分页） |
| Limit | Int | 每页大小（建议 ≤ 100） |
| QueryID | String | 指定 QueryID（精确） |
| SubmitUser | String | 提交用户 |
| State | String | 状态（`FINISHED`/`RUNNING`/`EXCEPTION`/`CANCELED` 等） |
| StartTimeOrder | String | 按开始时间排序（`asc`/`desc`） |
| ExecuteTimeOrder | String | 按耗时排序（`asc`/`desc`） |

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| QueryOnlineLogRes[].QueryID | String | Impala QueryID |
| QueryOnlineLogRes[].Statement | String | SQL 文本 |
| QueryOnlineLogRes[].State | String | 状态 |
| QueryOnlineLogRes[].SubmitUser | String | 提交用户 |
| QueryOnlineLogRes[].StartTime | String | 开始时间 |
| QueryOnlineLogRes[].Duration | Int | 耗时（毫秒） |
| Count | Int | 总数 |

### 用法示例
```text
# 拉取过去 1 小时耗时 > 10 秒的慢 SQL Top 50
QueryOnlineLogReq = {
  "StartTime": now - 3600,
  "EndTime": now,
  "Limit": 50,
  "ExecuteTimeOrder": "desc"
}
# 客户端再过滤 Duration > 10000 ms
```

---

## 6. ⚠️ 慢查询趋势（无独立工具，需聚合得到）

> X **无独立的慢查询趋势接口**。要绘制"按小时/按天的慢查询数量趋势"，请：
> 1. 调用 `TCHouseXDescribeSqlHistoryRecords` 拉取目标时间窗口的全部记录（必要时分页）；
> 2. 在客户端按 `StartTime` 取整（如 `floor(StartTime/3600)*3600` 按小时分桶），按 `Duration > 阈值` 过滤；
> 3. 聚合 count 后输出折线图。

---

## 7. TCHouseXDescribeInstanceProfile — 查询单条 SQL 的详细 Profile

- **X 云 API Action**：`DescribeInstanceProfile`
- **用途**：根据 `QueryId` 拉取单条 SQL 的详细 Query Profile（含每个算子的 CPU/IO 时间、行数、内存），用于定位单条 SQL 的性能瓶颈。
- **何时调用**：慢 SQL 深度分析——已通过 `TCHouseXDescribeSqlHistoryRecords` 拿到 QueryID 后，用本接口深挖执行细节。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| InstanceId | 是 | String | 实例 ID |
| QueryId | 是 | String | Impala QueryId，例如 `9744fcb875d5cf7c:73e1f09a00000000`。**注意入参字段名是小写 d 的 `QueryId`**，与 `DescribeSqlHistoryRecords` 出参 `QueryOnlineLogRes[].QueryID`（大写 D）不同，需要做映射 |

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| ProfileStr | String | 多行文本形式的 Query Profile，含 `Query Compilation` / `Query Timeline` / `ImpalaServer` / 各 Fragment 的算子统计（ScanNode / HashJoinNode / AggregationNode / ExchangeNode 等） |
| ErrorMsg | String | 错误信息 |

### 用法
1. 用户给定具体慢 SQL → 用 `TCHouseXDescribeSqlHistoryRecords` 找到对应 QueryID
2. 用 `DescribeInstanceProfile` 拉取 ProfileStr → 解析定位耗时算子

---

## 8. TCHouseXDescribeImpalaObjectNew — 查询库 / 表 / 列元数据（替代 C 的 TableSchema）

- **X 云 API Action**：`DescribeImpalaObjectNew`
- **对应 C 工具**：`TCHouseCDescribeTableSchema`
- **用途**：查询 X 实例下的**数据库列表 / 表列表 / 列元数据**等元信息。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| InstanceId | 是 | String | 实例 ID |
| Version | 是 | String | 固定 `2023-04-11` |
| Language | 否 | String | `zh-CN` / `en-US` |
| ApiType | 是 | String | **决定查询对象**，详见下表 |

### `ApiType` 取值
| ApiType | 含义 | 额外参数 |
|---------|------|---------|
| `GetDatabases` | 列出所有数据库 | 无 |
| `GetTables` | 列出所有库下所有表（按库分组返回） | 无 |
| `GetColumns` | 查询某表的列结构 | `Database`、`Table` |

### 出参格式
- 返回为 JSON 对象，**key 为数据库名**，value 为该库下的对象列表（每行格式：`db|object|TYPE`，TYPE 包含 `TABLE`、`SYSTEM TABLE`、`VIEW` 等）。
- 真实示例（`GetTables`）：
  ```json
  {
    "default": [
      "default|datatype_test|TABLE",
      "default|student|TABLE"
    ],
    "information_schema": [
      "information_schema|columns|SYSTEM TABLE",
      "information_schema|processlist|SYSTEM TABLE",
      "information_schema|tables|SYSTEM TABLE"
    ]
  }
  ```

### 用法
- **建表前 / 选型前**：用 `GetDatabases` / `GetTables` 检查是否已存在同名库表。
- **优化分析前**：用 `GetColumns` 拉取表结构（列名、类型、是否分区键、是否主键等）。

---

## 9. TCHouseXDescribeInstanceWarehouse — 查询单个计算组详情

- **X 云 API Action**：`DescribeInstanceWarehouse`
- **用途**：查询实例下**单个计算组（Warehouse / VirtualCluster）**的节点资源列表、状态与实时 CPU 资源使用。
- **何时调用**：⚠️ **自 API 升级后，`DescribeInstance.InstanceInfo.VirtualClusters` 已返回与本接口等价的节点级完整详情，绝大多数诊断场景无需再调用本接口**。仅在以下情况才建议调用：
  1. `DescribeInstance.VirtualClusters` 字段缺失（旧版接口回退）；
  2. 需要拿最新一刻的 `CurrentRealtimeCpuResource`，避免 `DescribeInstance` 可能存在的缓存滞后；
  3. 只关心单个 VC 且想减少响应体积。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| InstanceId | 是 | String | 实例 ID |
| VirtualCluster | 否 | String | 计算组名称。为空时接口行为以实际返回为准（建议逐个 Warehouse 传入以拿到完整详情） |

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| VirtualCluster.VirtualCluster | String | 计算组名称 |
| VirtualCluster.Resources[] | Array | 该计算组下的节点资源列表（IP/Cpu/Memory/Storage/Status/Component/DeployMode/ResourceIP 等） |
| VirtualCluster.ClusterStateInfo | Object | 计算组状态（InstanceState / InstanceStateDesc / FlowName / FlowProgress / FlowMsg） |
| VirtualCluster.WarehouseInfo.CurrentRealtimeCpuResource | Int | 实时 CPU 资源占用（用于负载评估） |
| VirtualCluster.WarehouseInfo.SparkSpecName | String | Spark 规格名（若启用 Spark） |
| ErrorMsg | String | 错误信息 |

### 用法示例
```text
# 默认路径：直接从 DescribeInstance 拿完整节点级详情
for w in InstanceInfo.VirtualClusters:
  analyze(w.Resources, w.ClusterStateInfo, w.WarehouseInfo.CurrentRealtimeCpuResource)

# 条件触发：VirtualClusters 缺失或需要最新瞬时数据时，才补调本接口
DescribeInstanceWarehouse(InstanceId=..., VirtualCluster=w.VirtualCluster)
```

---

## 10. TCHouseXDescribeInstanceResourceUsage — 查询资源使用量

- **X 云 API Action**：`DescribeInstanceResourceUsage`
- **用途**：查询实例的**时序资源使用量**，用于容量趋势分析与预警（如存储用量是否接近上限、Warehouse CPU 均值是否偏高）。
- **何时调用**：集群健康诊断步骤 3；分析存储 / 计算容量风险时。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| InstanceID | 是 | String | 实例 ID（**注意字段名是 `InstanceID`，全大写 ID，与其他接口的 `InstanceId` 不同**） |
| Period | 是 | String | 聚合粒度：`Hour` / `Day` / `Month` / `Year` |
| ResourceType | 是 | String | 资源类型：`Warehouse` / `Serverless` / `BasicService` / `Storage` |
| StartTime | 是 | String | 起始时间，格式 `YYYY-MM-DD HH:MM:SS` |
| EndTime | 是 | String | 结束时间，格式 `YYYY-MM-DD HH:MM:SS` |

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| ResourceType | String | 资源类型（回显） |
| StartTime / EndTime | String | 起止时间（回显） |
| DataPoints[] | Array | 时序数据点：`Dimensions`（对象，可能为空）+ `Timestamps[]`（Unix 秒数组）+ `Values[]`（数值数组，与 Timestamps 一一对应） |
| ErrorMsg | String | 错误信息 |

### 用法示例
```text
# 拉取最近 24 小时的存储用量
DescribeInstanceResourceUsage(
  InstanceID=..., Period="Hour", ResourceType="Storage",
  StartTime="2026-07-12 10:00:00", EndTime="2026-07-13 10:00:00"
)
# 用同样参数，ResourceType="Warehouse" 再调用一次，拿计算 CPU 用量
```

### 注意
- 时间跨度过大时（> 7 天）建议 `Period=Day`；跨月建议 `Month`，避免响应过大。
- Storage 返回的 `Values` 单位为字节；换算为 GB 时除以 1024^3。
- Warehouse 返回的 `Values` 为 CPU 使用率（0~100 或 0~1，以实际接口返回为准，须结合实例规格判断使用率）。

---

## 11. TCHouseXDescribeInstanceOperationsV1 — 查询集群操作记录

- **X 云 API Action**：`DescribeInstanceOperationsV1`
- **用途**：查询实例的**集群操作记录**（升降配 / 重启 / 配置变更 / 权限变更等）。X 没有独立的告警/事件接口，本接口是识别"变更是否引发故障"的主要数据源。
- **何时调用**：集群健康诊断步骤 4；用户提到"最近做过某某变更后集群不稳"时。

### 入参
| 字段 | 必选 | 类型 | 说明 |
|------|------|------|------|
| Region | 是 | String | 地域 |
| InstanceId | 是 | String | 实例 ID |
| Offset | 否 | Int | 偏移量（分页） |
| Limit | 否 | Int | 每页大小（建议 ≤ 50） |
| StartTime | 否 | String | 起始时间 |
| EndTime | 否 | String | 结束时间 |
| OperateUin | 否 | String | 按操作人过滤，支持模糊搜索，多个用 `|` 分割 |
| OperateObject | 否 | String | 按操作对象过滤，支持模糊搜索，多个用 `|` 分割 |
| State | 否 | String | 按状态过滤 |
| OperateTimeOrder | 否 | String | 按创建时间排序：`asc` / `desc`（默认 `desc`） |
| ExecuteTimeOrder | 否 | String | 按运行时间排序：`asc` / `desc` |

### 出参（核心字段）
| 字段 | 类型 | 说明 |
|------|------|------|
| TotalCount | Int | 总数 |
| Operations[].InstanceId | String | 实例 ID |
| Operations[].OperateUin | String | 操作人 UIN |
| Operations[].OperateTime | String | 操作时间 |
| Operations[].OperateObject | String | 操作对象（如 Warehouse 名/节点名） |
| Operations[].OperateName | String | 操作名称（升配/重启/配置变更等） |
| Operations[].State | String | 操作状态（成功/失败/进行中） |
| Operations[].ExecuteTime | Int | 执行耗时 |
| ErrorMsg | String | 错误信息 |

### 用法示例
```text
# 拉取最近 24 小时的操作记录，按时间倒序
DescribeInstanceOperationsV1(
  InstanceId=..., StartTime="2026-07-12 10:00:00", EndTime="2026-07-13 10:00:00",
  Limit=50, OperateTimeOrder="desc"
)
```

---

## 速查表（C → X 工具映射）

| C MCP tool | X MCP tool | X 云 API Action |
|------------|------------|-----------------|
| TCHouseCDescribeRegionZone | TCHouseXDescribeRegionZone | DescribeRegionZone |
| TCHouseCDescribeInstance | TCHouseXDescribeInstance | DescribeInstance |
| TCHouseCDescribeSpec | TCHouseXDescribeSpec | DescribeSpec |
| TCHouseCDescribeGoodsDetail | TCHouseXDescribeGoodsDetail | DescribeGoodsDetail |
| TCHouseCDescribeSlowQueryRecords | TCHouseXDescribeSqlHistoryRecords | DescribeSqlHistoryRecords |
| TCHouseCDescribeSlowQueryTrend | （无对应工具，用 DescribeSqlHistoryRecords 客户端聚合） | — |
| TCHouseCDescribeCkSqlApis | TCHouseXDescribeInstanceProfile（仅覆盖已执行 SQL 的 Profile 分析） | DescribeInstanceProfile |
| TCHouseCDescribeTableSchema | TCHouseXDescribeImpalaObjectNew | DescribeImpalaObjectNew |
| TCHouseCDescribeInstanceShards | TCHouseXDescribeInstanceWarehouse | DescribeInstanceWarehouse |
| （C 无对应，等价于监控指标趋势） | TCHouseXDescribeInstanceResourceUsage | DescribeInstanceResourceUsage |
| TCHouseCDescribeEventTasks（部分） | TCHouseXDescribeInstanceOperationsV1（仅覆盖"操作变更"，X 无独立告警接口） | DescribeInstanceOperationsV1 |

> 📌 **未映射说明**：C 侧的 `TCHouseCDescribeRunningQuery`、`TCHouseCActionDmsAuthority`、`TCHouseCExecuteDmsSql`、`TCHouseCDescribeDmsSqlHistory` 等依赖 SQL 工作区（需用户输入账号/密码）的接口，本 Skill **不映射到 X 侧对应工具**，避免在 Skill 中打扰用户输入凭据。若需运行 SQL，请由用户在控制台 SQL 工作区自行执行。
