# 费用估算指南（TCHouseX）

> **何时使用本文件**：在步骤 4（费用估算）时参考本文件。**主路径**为 §5 两步实时询价链路；两步询价失败时**兜底**至 §2 公开 CU 单价表 + §3 估算公式。
> **何时不使用**：选型规则请参考 `spec-recommendation-rules.md`；MCP 工具入参请参考 `./api-reference.md`。

---

## 目录

- [§1 费用模型概览](#1-费用模型概览)
- [§2 地域 CU 单价表](#2-地域cu单价表)
- [§3 估算公式](#3-估算公式)
- [§4 多方案费用对比展示](#4-多方案费用对比展示)
- [§5 实时询价：两步链路（主路径）](#5-实时询价两步链路主路径)
- [§6 常见陷阱](#6-常见陷阱)

---

## §1 费用模型概览

TCHouse-X **仅支持按量计费**，**按秒计费（起步 60 秒），仅在运行时产生费用，任务结束即可关停**；**账单周期为每小时生成一份**。费用由以下部分组成：

| 计费项           | 说明                                                                       | 是否在本 Skill 估算范围 |
| ---------------- | -------------------------------------------------------------------------- | ----------------------- |
| 接入服务节点     | 认证 / SQL 解析 / 执行计划 / 调度节点                                       | ✅ 不计费               |
| Warehouse 节点   | 在线计算资源，**按秒计费（起步 60 秒）**，按 `CU × 单价 × 实际运行时长` 计费；每小时出一份账单                                    | ✅ 是                   |
| Serverless 节点  | 离线计算资源，按 `CU × 单价 × 实际运行小时` 计费；起步 60 秒                | ✅ 是（估算）           |
| 大模型 Token     | AI Functions 触发时产生；输入 / 输出分别计费                                 | ⚠️ 独立计费，仅提示     |
| TCLake 存储      | 底层统一存储，按实际存储量独立计费                                          | ❌ 独立计费             |
| 网络流量         | 跨 AZ / 公网出网流量                                                        | ❌ 独立计费             |

> ⚠️ **邀测期免费**：TCHouse-X 官网明确「邀测期间面向受邀用户开放免费使用」。报告中给出的费用估算是**正式商用后**的按量费用参考。

---

## §2 地域 CU 单价表

> 数据来源：官网《计费概述》。**若与官网现价不一致，以官网页面为准**。

### 2.1 Warehouse 计算资源单价

| 地域              | 单价（元/CU/小时） |
| ----------------- | ------------------ |
| 北京 / 上海 / 广州 | 0.355              |
| 中国香港          | 0.478              |
| 新加坡            | 0.478              |

### 2.2 Serverless 计算资源单价

| 地域              | 单价（元/CU/小时） |
| ----------------- | ------------------ |
| 北京 / 上海 / 广州 | 0.292              |
| 中国香港          | 0.450              |
| 新加坡            | 0.468              |

### 2.3 大模型 Token 单价

| Token 方向 | 地域                              | 单价                          |
| ---------- | --------------------------------- | ----------------------------- |
| 输入       | 北京 / 上海 / 广州 / 中国香港 / 新加坡 | 0.004 元 / 1000 Token / 小时  |
| 输出       | 北京 / 上海 / 广州 / 中国香港 / 新加坡 | 0.016 元 / 1000 Token / 小时  |

### 2.4 CU 定义

> `1 CU = 1 vCPU + 4 GiB RAM`
>
> 标准 Warehouse 节点规格与 CU 换算：
>
> | 规格     | 单节点 CU |
> | -------- | --------- |
> | 2X-Small | 4         |
> | X-Small  | 8         |
> | Small    | 16        |
> | Medium   | 32        |
> | Large    | 64        |

> 📌 **已开放地域（邀测阶段）**：北京、重庆、广州、香港、上海、新加坡；实时以 `TCHouseXDescribeRegionZone` 返回为准，其他地域需联系 TCHouse-X 产研团队。

---

## §3 估算公式

### 3.1 Warehouse 月费用（无弹性）

```
Warehouse 月费 = 总 CU × 单价(元/CU/小时) × 720(小时/月)

其中：
- 总 CU = 节点规格 CU × 节点个数
- 单价按目标地域查 §2.1
- 720 小时/月 = 30 天 × 24 小时
```

**示例**：广州 `Small × 3` 全月常驻

```
总 CU = 16 × 3 = 48 CU
月费 = 48 × 0.355 × 720 = ¥12,268.80 ≈ ¥12,269
```

### 3.2 Warehouse 月费用（带弹性）

```
Warehouse 月费 ≈ Σ(各时段总 CU × 单价 × 该时段小时数)
```

**示例（分时弹性）**：广州 Small × 5 白天 12 小时 + Small × 2 夜间 12 小时，全月运行

```
白天：16 × 5 × 0.355 × 12 × 30 = ¥10,224
夜间：16 × 2 × 0.355 × 12 × 30 = ¥4,090
月费 ≈ ¥14,314
```

**示例（定时启停）**：广州 Small × 3 工作日 8-20 点（12 小时 × 22 天 = 264 小时/月）

```
月费 = 16 × 3 × 0.355 × 264 = ¥4,499
（相比全月常驻 ¥12,269，节省约 63%）
```

### 3.3 Serverless 月费用

```
Serverless 月费 ≈ 平均 CU × 单价 × 实际运行小时数

其中：
- 平均 CU = Driver CU + Executor CU × Executor 个数
- 实际运行小时数 = 作业次数 × 单次平均时长
```

**示例**：广州 Serverless（Driver 2X-Small × 1 + Executor X-Small × 2），每天跑 4 小时 ETL

```
平均 CU = 4 + 8 × 2 = 20 CU
月费 = 20 × 0.292 × 4 × 30 = ¥700.80 ≈ ¥701
```

### 3.4 大模型 Token 月费用（AI Functions 场景）

```
Token 月费 ≈ (输入 Token/千 × 0.004 + 输出 Token/千 × 0.016) × 使用小时数
```

> 大部分选型场景无需估算 Token 费用；仅在用户明确使用 AI Functions 时提示独立计费。

### 3.5 单位换算

- 720 小时/月（按 30 天计）
- 8760 小时/年
- 264 小时/月（工作日 8-20 点，工作日 22 天）
- 168 小时/月（工作日 8-16 点或类似 8 小时/工作日）

---

## §4 多方案费用对比展示

```markdown
## 费用对比

| 方案       | Warehouse 拓扑              | 总 CU | Warehouse 月费（720h/月）     | Serverless 月费（估算） | 备注                         |
| ---------- | --------------------------- | ----- | ----------------------------- | ------------------------ | ---------------------------- |
| A（推荐）  | wh_default: Small × 3       | 48    | 48 × 0.355 × 720 = ¥12,269   | 按需触发 ¥0-500          | 无弹性，负载稳定             |
| B（性能）  | wh_online: Medium × 3<br/>wh_etl: Small × 2（定时启停 22-06） | 96 + 32 | wh_online: ¥24,538<br/>wh_etl: 32 × 0.355 × 8h × 30d = ¥2,726<br/>合计 ¥27,264 | ETL 走 Serverless ¥1,000-3,000 | 多 Warehouse 隔离            |
| C（经济）  | wh_default: X-Small × 2（定时启停 工作日 8-20） | 16 | 16 × 0.355 × 264 = ¥1,500    | 按需触发 ¥0-200          | 仅工作时段使用，最省成本      |

> 💡 价格说明
> - 上述价格按官网公开 CU 单价（广州 Warehouse 0.355 元/CU/小时 / Serverless 0.292 元/CU/小时）估算
> - **TCLake 存储、网络流量、大模型 Token 均未包含**（独立按量计费）
> - **邀测期免费**，此估算为正式商用后的按量参考
> - Serverless 费用取决于作业实际运行时长；上述范围为经验估算
> - 最终价格以腾讯云控制台账单为准
```

---

## §5 实时询价：两步链路（主路径）

TCHouse-X 的实时询价走**两步链路**（与 tchousec 一致）：

1. **Step A：`TCHouseXDescribeGoodsDetail`** —— 获取商品配置（`GoodsCategoryId` + `GoodsDetailStr` + `GoodsNum` + `PayMode`），**本接口不返回金额**
2. **Step B：`BillingCalculatePrice`** —— 通用 billing 询价，把 Step A 的返回结果透传，拿到真实金额（含折扣）

本 Skill **主路径走两步实时询价**（返回含折扣的真实金额，与控制台报价一致）；只有在两步任一步重试 3 次仍失败时，才**兜底回退到 §3 公开单价估算**。

### 5.1 何时回退公开单价估算

默认对每个推荐方案都调用一遍两步询价链路；仅在以下情形回退到 §3 的公开单价估算：

1. Step A / Step B 任一步重试 3 次后仍失败（`InvalidParameter` / `InternalError` / `RequestLimitExceeded` 等）
2. 用户明确要求「不需要真实询价，直接给估算即可」
3. 处于邀测期且用户已知免费，仅需参考量级不需精确金额（可与用户确认后切公开单价）

### 5.2 Step A：调用 `TCHouseXDescribeGoodsDetail`

**入参组装（Warehouse 场景示例，广州 + Small × 1 按量计费）**：

```json
{
  "Case": "create_instance",
  "IsQueryPrice": true,
  "Version": "2023-04-11",
  "Language": "zh-CN",
  "Region": "ap-chongqing",
  "Zone": "ap-chongqing-1",
  "InstanceType": "warehouse",
  "Type": "sp_cdwch_cn",
  "InstanceName": "我的TCHouse-X实例",
  "VirtualClusterName": "我的Warehouse",
  "ProductVersion": "2.2.3_DEV",
  "WarehouseType": 0,
  "TCIMode": 1,
  "CipherMode": "1",
  "SupportLoginType": [2],
  "IsSecondaryZone": false,
  "SecondaryZoneInfo": [],
  "UserVPCId": "<用户 VPC ID>",
  "UserSubnetId": "<用户 Subnet ID>",
  "UserSubnetIPNum": 24,
  "TCLakeSpec": {
    "CatalogType": "LAKEHOUSE",
    "CatalogNameType": "SYSTEM"
  },
  "ServerlessSpec": {},
  "LdapConfig": {},
  "ChargeProperties": {
    "TimeSpan": 1,
    "TimeUnit": "h",
    "ChargeType": "POSTPAID_BY_HOUR",
    "RenewFlag": 0
  },
  "Resources": [
    {
      "Component": "impalad",
      "Cpu": 16,
      "Memory": 64,
      "SpecName": "Small",
      "Count": 1,
      "DeployMode": 0,
      "VirtualClusterName": "我的Warehouse"
    },
    {
      "Component": "impalad",
      "SpecName": "CLB",
      "Cpu": 0,
      "Memory": 0,
      "Count": 1,
      "DeployMode": 2,
      "VirtualClusterName": "我的Warehouse"
    }
  ]
}
```

> 📌 **参数说明**：
>
> - `IsQueryPrice: true`：询价标记，透传即可
> - `Resources` 只需提供用户可见的**数据计算节点**（`Component: "impalad"`，`DeployMode: 0`）与其 **CLB**（`DeployMode: 2`）；`access-server` / `livy-meson` / `tccatalog` 等接入服务/元数据节点由服务端自动补齐，无需用户传入
> - `DeployMode`：0=计算节点，2=CLB（负载均衡）
> - `WarehouseType=1`（自适应 Warehouse）场景需带 `ServerlessSpec: {WarehouseMaxCuCount, WarehouseMaxClusterSize}`（弹性伸缩上限，默认均为 64）；`WarehouseType=0`（标准 Warehouse）时传 `{}` 或不传

**响应关键字段（真实样例）**：

```json
{
  "Response": {
    "Type": "sp_tchouse_x_v2",
    "GoodsCategoryId": 2023483,
    "GoodsDetailStr": "{\"TimeSpan\":1,\"Type\":\"sp_tchouse_x_v2\",\"context\":{...省略...,\"Resources\":[...],\"Zone\":\"ap-chongqing-1\",...}}",
    "GoodsDetail": "",
    "GoodsNum": 1,
    "PayMode": 0,
    "RegionId": 19,
    "ZoneId": 190001,
    "ResourceId": "instance-9j52swf5",
    "RequestId": "49191fa1-e65a-44a9-bb0c-ba8b7abda3e4",
    "ErrorMsg": ""
  }
}
```

**核心字段速查**：

| 字段              | 类型    | 说明                                                                      |
| ----------------- | ------- | ------------------------------------------------------------------------- |
| `Type`            | String  | 子商品码。**请求传 `sp_cdwch_cn`**，服务端会自动映射并在响应中回填为 `sp_tchouse_x_v2` |
| `GoodsCategoryId` | Integer | 商品类目 ID，**Step B 必填**                                              |
| `GoodsDetailStr`  | String  | 商品完整明细 JSON 字符串，**Step B 必填**（作为 `GoodsDetail` 参数透传）  |
| `GoodsNum`        | Integer | 商品数量，通常为 1，**Step B 必填**                                       |
| `PayMode`         | Integer | 付费模式数值，0=后付费（TCHouse-X 当前仅按量）                             |
| `RegionId`        | Integer | 地域数字 ID                                                               |
| `ZoneId`          | Integer | 可用区数字 ID                                                             |
| `ResourceId`      | String  | 资源标识符                                                                |
| `ErrorMsg`        | String  | 错误信息（成功时为空）                                                     |

> ⚠️ **响应中不含金额字段**（无 `Price` / `TotalCost` / `RealTotalCost`）。所有金额来自 Step B 的 `BillingCalculatePrice` 返回。

### 5.3 Step B：调用 `BillingCalculatePrice`

**入参组装**：

| 参数              | 值来源                                              | 说明                                       |
| ----------------- | --------------------------------------------------- | ------------------------------------------ |
| `GoodsCategoryId` | Step A 返回                                         | 商品类目 ID                                |
| `GoodsDetail`     | Step A 返回的 `GoodsDetailStr` **经透传改造后**的字符串（见下方 ⚠️ 提示） | 商品明细 JSON 字符串             |
| `GoodsNum`        | Step A 返回（通常为 1）                              | 商品数量                                   |
| `PayMode`         | `"postPay"`                                         | TCHouse-X 仅按量计费，固定 `postPay`       |
| `Region`          | 目标地域 ap code                                    | 如 `ap-guangzhou`                          |
| `Zone`            | 目标可用区 ap code                                  | 如 `ap-guangzhou-7`                        |

> ⚠️ **严禁原样透传 `GoodsDetailStr`**：必须先按 [§5.3.1 转换清单](#531-goodsdetailstr--goodsdetail-转换强制步骤不可跳过) 完成 **key camelCase 化（所有字段全部保留，不做删除）** 后，才能作为 `BillingCalculatePrice` 的 `GoodsDetail` 参数传入。**直接透传会报 `InvalidParameter: timeSpan 缺失`**。


**响应关键字段**：

| 字段              | 类型    | 说明                                                             |
| ----------------- | ------- | ---------------------------------------------------------------- |
| `Price`                             | Integer | 原价（单位：**分**）                                              |
| `TotalCost`                         | Integer | 总费用（单位：**分**）                                            |
| `RealTotalCost`                     | Integer | 折后实付金额（单位：**分**，整型有四舍五入，可能损失精度）        |
| `HighPrecisionPrice.RealTotalCostHigh` | String  | 折后实付金额（单位：**分**，高精度字符串，**优先使用**）        |
| `Policy`                            | Number  | 折扣率                                                            |
| `TimeSpan`                          | Integer | 时长                                                              |
| `TimeUnit`                          | String  | 时长单位（`h` / `m`）                                             |

> 💰 **单位换算（关键）**：所有金额字段单位均为「分」，展示给用户前必须**除以 100** 转换为「元」。忘记换算会导致报价虚高 100 倍。
>
> 🎯 **精度优先**：展示折后实付金额时**优先取 `HighPrecisionPrice.RealTotalCostHigh`**（字符串，高精度），回退到整型 `RealTotalCost`。整型字段存在四舍五入，例如实付原本是 `190.848 分`，整型会取 `191`，直接展示会有 ~0.08% 误差。
>
> **展示示例**：`HighPrecisionPrice.RealTotalCostHigh = "190.848"` → `190.848 / 100 = 1.90848 元/小时`；月费估算 = `1.90848 × 720 ≈ 1,374.1 元/月`。

### 5.3.1 GoodsDetailStr → GoodsDetail 转换（强制步骤，不可跳过）

调用 `BillingCalculatePrice` 前，必须对 Step A 返回的 `GoodsDetailStr` 执行以下 **4 步转换**，**按顺序执行，任何一步不可省略**：

```
【必做清单】
□ Step 1: 将 GoodsDetailStr JSON 字符串 parse 为对象
□ Step 2: 递归遍历所有层级，将每个对象 key 的首字母改为小写（其余字符不变）
           - TimeSpan → timeSpan
           - ChargeProperties → chargeProperties
           - Resources[].SpecName → resources[].specName
           - 连续大写只改首字母：SRContext → sRContext, TCIMode → tCIMode, VIPType → vIPType, InstanceID → instanceID
           - TCLakeSpec.CatalogType → tCLakeSpec.catalogType
           - 非 key 的字符串值不动（如 "POSTPAID_BY_HOUR", "ap-guangzhou-7", "sv_cdwch_node_sv_cdwch_32c128g"）
□ Step 3: 保留所有字段原样透传，不删除任何字段。
           特别注意以下字段必须保留：
           - sv_tchouse_x_warehouse_hp（计费 CU 数量，删除会导致 "all price code not match" 报错）
           - curDeadline
           - newConfig（值为 null 也要保留）
           - oldConfig（值为 null 也要保留）
□ Step 4: 将处理后的对象 JSON.stringify 为字符串 → 作为 BillingCalculatePrice 的 GoodsDetail 参数
```

⚠️ **不执行此转换的后果**：`BillingCalculatePrice` 后端期望 camelCase key（如 `timeSpan`），而 `DescribeGoodsDetail` 返回 PascalCase key（如 `TimeSpan`），直接透传会报 `InvalidParameter: timeSpan 缺失`。

> ⚠️ **严禁删除 `sv_tchouse_x_warehouse_hp`**：该字段是计费数量（对应 Warehouse 的总 CU 数），删除后价格中心匹配不到计价项，会报 `FailedOperation.GetPriceParamError: all price code not match`。`curDeadline`、`newConfig`、`oldConfig` 同理保留。

> 附加提醒：Step A 响应字段名是 `GoodsDetailStr`（带 `Str` 后缀），Step B 请求字段名是 `GoodsDetail`（不带后缀），别搞混。

### 5.4 兜底与交叉验证流程

```
Step A: 调用 TCHouseXDescribeGoodsDetail
   ├── 成功 → 提取 GoodsCategoryId / GoodsDetailStr / GoodsNum / PayMode → 进入 Step B
   └── 失败（InvalidParameter / InternalError）
       → 最多重试 3 次（每次间隔 3 秒）
       → 仍失败 → 兜底 §3 公开单价估算，报告中注明「实时询价接口暂不可用」

Step B: 调用 BillingCalculatePrice
   ├── 成功 → 优先读取 HighPrecisionPrice.RealTotalCostHigh（分，字符串）
   │         → 回退整型 RealTotalCost（分）→ ÷ 100 转换为元
   │         → 以实时询价金额为主展示，附带按 720 小时/月 推算的月费
   │         → 可选：与 §3 公开单价估算交叉验证，若差异 > 10% 同时展示两个数值并说明
   └── 失败 → 最多重试 3 次 → 仍失败 → 兜底 §3 公开单价估算，报告中注明
```

**关于折扣**：`BillingCalculatePrice` 返回的 `RealTotalCost` 为折后实付金额，不同账户可能享有不同折扣（合同折扣、活动折扣等）。报价时应以 `RealTotalCost` 为准展示，并提示「实际折扣因账户而异，最终价格以下单页面为准」。

**关于邀测期**：TCHouse-X 邀测期免费，即使 `BillingCalculatePrice` 返回金额也仅为**正式商用后**的按量参考。报告必须明确标注邀测期免费。

---

## §6 常见陷阱

| 陷阱                                        | 提醒                                                                                                    |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 把 TCHouseC 的「包年包月折扣」搬过来          | **TCHouse-X 仅按量计费**，没有包年包月，没有时长折扣表                                                     |
| 忘记 TCLake 存储费用独立计费                  | 报告必须明示 TCLake 不含在 Warehouse 报价内                                                              |
| 用 CU 单价 × 720 后没提示「实际按运行小时计费」| 弹性策略（分时/定时启停/自动弹性）会显著降低实际费用，必须在报告中说明                                        |
| 邀测期给用户报了正常费用没说邀测免费          | 官网明确「邀测期间面向受邀用户开放免费使用」，报告必须提示                                                    |
| 两步询价任一步报错就直接放弃报价              | 应该重试 3 次后回退到公开单价估算，不要不给报价                                                                       |
| 拿 `BillingCalculatePrice` 的分展示，忘记除 100 | `Price` / `TotalCost` / `RealTotalCost` 单位均为「分」，展示前必须除以 100 转换为「元」                     |
| 误以为 `TCHouseXDescribeGoodsDetail` 直接返金额 | 该接口只返商品配置（`GoodsCategoryId` + `GoodsDetailStr`），金额必须走 `BillingCalculatePrice` 二次询价       |
| 报错「所有地域都支持」                        | TCHouse-X 邀测期已开放北京/重庆/广州/香港/上海/新加坡；实际售卖以 `TCHouseXDescribeRegionZone` 与官网公告为准 |
| 把大模型 Token 费用算进 Warehouse 月费         | 大模型 Token 是**独立计费**项，仅使用 AI Functions 时产生，不应加进 Warehouse 报价                          |
| 用「小时费用 × 8760」算年费而不提示弹性收益    | 常驻用户很少 24×7 全速跑，务必提示分时/定时启停能带来 30-70% 节省                                            |

### 6.1 提示用户的免责声明模板

**主路径（两步实时询价成功）**：

```
> 💰 价格说明
> - 上述价格由 `BillingCalculatePrice` 实时询价返回，为折后实付金额（含折扣），与控制台下单页一致
> - 实际折扣因账户而异（合同折扣 / 活动折扣等），最终价格以下单页面为准
> - TCHouse-X 目前处于邀测中，邀测期间免费；此报价为正式商用后按量费用参考
> - TCLake 存储、网络流量、大模型 Token 未包含（独立按量计费）
> - 若开启分时弹性 / 定时启停 / 自动弹性，实际费用会显著低于 720 小时/月 全速估算
> - 最终价格以腾讯云控制台账单为准
```

**兜底路径（两步询价失败 → 公开单价估算）**：

```
> 💰 价格说明
> - 实时询价接口暂不可用，上述价格按官网公开 CU 单价估算（广州 Warehouse 0.355 元/CU/小时 / Serverless 0.292 元/CU/小时）
> - TCHouse-X 目前处于邀测中，邀测期间免费；此报价为正式商用后按量费用参考
> - TCLake 存储、网络流量、大模型 Token 未包含（独立按量计费）
> - 若开启分时弹性 / 定时启停 / 自动弹性，实际费用会显著低于 720 小时/月 全速估算
> - 最终价格以腾讯云控制台账单为准
```
---

## §7 快速估算速查表

### 广州 Warehouse 常驻月费（720 小时）

| 规格 × 数量        | 总 CU | 月费          |
| ------------------ | ----- | ------------- |
| 2X-Small × 1       | 4     | ¥1,022        |
| 2X-Small × 2       | 8     | ¥2,045        |
| X-Small × 1        | 8     | ¥2,045        |
| X-Small × 2        | 16    | ¥4,090        |
| Small × 1          | 16    | ¥4,090        |
| Small × 2          | 32    | ¥8,179        |
| Small × 3          | 48    | ¥12,269       |
| Small × 5          | 80    | ¥20,448       |
| Medium × 2         | 64    | ¥16,358       |
| Medium × 3         | 96    | ¥24,538       |
| Medium × 5         | 160   | ¥40,896       |
| Large × 3          | 192   | ¥49,075       |
| Large × 5          | 320   | ¥81,792       |

> 上述为不启用弹性、7×24 常驻的最大月费。启用定时启停 / 分时弹性后按实际运行小时数打折。
