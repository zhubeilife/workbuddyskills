# 云 API 工具参考

> 本文件描述 tchoused-cluster-sizing-recommendation Skill 依赖的云 API 工具的输入输出参数。

---

## TCHouseDDescribeSpec

### 功能

获取目标地域/可用区的集群可用规格列表（FE/BE/CN 节点规格 + 云盘规格）。

### 输入参数

| 参数名称 | 必选 | 类型 | 说明 |
|---------|------|------|------|
| Region | 是 | String | 地域，如 `ap-guangzhou` |
| Zone | 是 | String | 可用区，如 `ap-guangzhou-1` |
| PayMode | 否 | String | 计费类型：`PREPAID`（包年包月）/ `POSTPAID_BY_HOUR`（按量计费） |
| Zones.N | 否 | Array of String | 多可用区，如 `["ap-guangzhou-1","ap-guangzhou-2"]` |
| SpecName | 否 | String | 机型名称，如 `S_4_16_H` |
| IsSSC | 否 | Boolean | 是否存算分离。**本 Skill 调用时统一固定传 `false`**（即便方案推荐存算分离架构，规格拉取阶段仍以存算一体规格集合为准） |

### 输出参数

| 参数名称 | 类型 | 说明 |
|---------|------|------|
| MasterSpec | Array of ResourceSpec | FE 节点可用规格列表 |
| CoreSpec | Array of ResourceSpec | BE 节点可用规格列表 |
| CNSpec | Array of ResourceSpec | CN 节点可用规格列表（存算分离场景） |
| AttachCBSSpec | Array of DiskSpec | 可挂载云盘规格列表 |
| RequestId | String | 请求唯一 ID |

### ResourceSpec 结构

| 字段 | 类型 | 说明 |
|------|------|------|
| Name | String | 规格名称，如 `S_4_16_H` |
| Cpu | Integer | CPU 核数 |
| Mem | Integer | 内存 GB |
| ComputeSpecDesc | String | 展示名称，如 `4核16G` |
| Type | String | 规格类型（STANDARD 等） |
| Available | Boolean | 是否可用 |
| MaxNodeSize | Integer | 最大节点数 |
| InstanceQuota | Integer | 实例配额 |
| DataDisk | DiskSpec | 数据盘规格约束 |
| SystemDisk | DiskSpec | 系统盘规格约束 |

### DiskSpec 结构

| 字段 | 类型 | 说明 |
|------|------|------|
| DiskType | String | 磁盘类型：`CLOUD_PREMIUM` / `CLOUD_HSSD` / `CLOUD_SSD` |
| DiskDesc | String | 磁盘类型描述 |
| DiskCount | Integer | 最大云盘数量 |
| MaxDiskSize | Integer | 最大单盘容量（GB） |
| MinDiskSize | Integer | 最小单盘容量（GB） |

### 示例输出

```json
{
  "Response": {
    "MasterSpec": [
      {
        "Name": "S_4_16_H",
        "Cpu": 4,
        "Mem": 16,
        "ComputeSpecDesc": "4核16G",
        "Type": "STANDARD",
        "Available": true,
        "MaxNodeSize": 50,
        "DataDisk": {
          "DiskType": "CLOUD_HSSD",
          "DiskDesc": "增强型SSD云硬盘",
          "DiskCount": 10,
          "MaxDiskSize": 320000,
          "MinDiskSize": 200
        }
      }
    ],
    "CoreSpec": [
      {
        "Name": "S_16_64_H",
        "Cpu": 16,
        "Mem": 64,
        "ComputeSpecDesc": "16核64G",
        "Type": "STANDARD",
        "Available": true,
        "MaxNodeSize": 50,
        "DataDisk": {
          "DiskType": "CLOUD_HSSD",
          "DiskDesc": "增强型SSD云硬盘",
          "DiskCount": 10,
          "MaxDiskSize": 320000,
          "MinDiskSize": 200
        }
      }
    ],
    "CNSpec": [
      {
        "Name": "S_8_32_H",
        "Cpu": 8,
        "Mem": 32,
        "ComputeSpecDesc": "8核32G",
        "Type": "STANDARD",
        "Available": true
      }
    ],
    "AttachCBSSpec": [
      {
        "DiskType": "CLOUD_HSSD",
        "DiskDesc": "增强型SSD云硬盘",
        "DiskCount": 1,
        "MaxDiskSize": 32000,
        "MinDiskSize": 1000
      }
    ],
    "RequestId": "10058bc0-40e7-4eb0-9b4d"
  }
}
```

---

## TCHouseDDescribeRegionZone

### 功能

获取 TCHouse-D 支持的地域与可用区列表，用于地域/可用区可用性校验、以及跨 AZ 部署可行性判断。

### 输入参数

| 参数名称 | 必选 | 类型 | 说明 |
|---------|------|------|------|
| Region | 否 | String | 地域，如 `ap-guangzhou`；不传时返回全部地域 |

### 输出参数

| 参数名称 | 类型 | 说明 |
|---------|------|------|
| Items | Array of AreaGroup | 按大区分组的地域列表 |
| Versions | Array of String | 该地域支持的内核版本号列表，如 `["4.1","3.1","3.0","2.1","2.0","1.2","1.1","1.0","0.15"]` |
| VpcRule | String | VPC 规则说明（通常为空） |
| ErrorMsg | String | 错误消息（正常返回时为空） |
| RequestId | String | 请求唯一 ID |

### AreaGroup 结构（大区）

| 字段 | 类型 | 说明 |
|------|------|------|
| Name | String | 大区标识，如 `china` / `d_asia_pacific` / `europe_us` |
| Desc | String | 大区中文名，如 `中国` / `亚太` / `欧美` |
| Regions | Array of RegionItem | 该大区下的地域列表 |

### RegionItem 结构（地域）

| 字段 | 类型 | 说明 |
|------|------|------|
| Name | String | 地域标识，如 `ap-guangzhou` |
| Desc | String | 地域中文名，如 `广州` |
| RegionId | Integer | 地域数值 ID，如 `1` |
| Zones | Array of ZoneItem | 该地域下的可用区列表 |
| Count | Integer | 该地域已存在的集群数量（历史存量，非可部署容量） |
| SSCCount | Integer | 该地域已存在的存算分离集群数量 |
| EnableSSC | Boolean | 该地域是否支持存算分离架构 |
| Bucket | String | COS 桶信息（存算分离相关，通常为空） |

### ZoneItem 结构（可用区）

| 字段 | 类型 | 说明 |
|------|------|------|
| Name | String | 可用区标识，如 `ap-guangzhou-6` |
| Desc | String | 可用区中文名，如 `广州六区` |
| ZoneId | Integer | 可用区数值 ID，如 `100006` |
| Encrypt | Integer | 是否支持加密（`1`=支持 / `0`=不支持） |
| **Main** | Boolean | **是否为主推可用区**：`true`=主推、支持新购下单；`false`=非主推（可能为存量/退服中/边缘区） |
| **ContainerEnabled** | Integer | **是否已开通容器化部署**：`1`=已开通、可下单；`0`=未开通、无法在该可用区新建 TCHouse-D 集群 |

### 「真正可部署可用区」判定规则（强约束）

> ⚠️ **本 Skill 判定一个可用区是否可用于新购的**唯一硬校验**：`Main === true` **且** `ContainerEnabled === 1`。**
>
> - 只满足 `Main=true` 但 `ContainerEnabled=0` → 容器化未开通，**不可下单**
> - 只满足 `ContainerEnabled=1` 但 `Main=false` → 非主推区（多为存量灰度/边缘区），**不推荐新购**
> - 二者兼具 → 可作为新购候选可用区
>
> **禁止使用 `Available` / `Count>0` 等其他字段作为可部署性判断依据**：`Count` 表达的是已有集群数（历史存量），并不代表当下能否新建；本接口返回体也不存在 `Available` 字段。

### 跨 AZ（3 副本）部署可行性判定

**规则**：只有当某个地域内 `Main=true && ContainerEnabled=1` 的可用区数量 **≥ 3** 时，该地域才支持 3 副本跨 AZ 部署。

**参考现状**（基于当前接口返回的样本统计，仅作示例，实际以实时返回为准）：

| 地域 | 可部署可用区数（Main=true && ContainerEnabled=1） | 3 副本跨 AZ 可行性 |
|------|--------------------------------------------------|-------------------|
| `ap-beijing` | 3（-6/-7/-8） | ✅ 满足 |
| `ap-guangzhou` | 2（-6/-7） | ❌ 不满足，只能单 AZ 或降为 2 副本 |
| `ap-shanghai` | 2（-5/-8） | ❌ 不满足 |
| `ap-nanjing` | 2（-3/-1） | ❌ 不满足 |
| `ap-chengdu` / `ap-chongqing` | 0-1 | ❌ 不满足 |
| `eu-frankfurt` | 2（-1/-3） | ❌ 不满足 |

> 上表仅为使用示范，Agent 必须**每次实时调用本接口并即时判定**，禁止基于此表做长期缓存决策。

### 示例返回（片段）

```json
{
  "Items": [
    {
      "Name": "china",
      "Desc": "中国",
      "Regions": [
        {
          "Name": "ap-guangzhou",
          "Desc": "广州",
          "RegionId": 1,
          "Zones": [
            { "Name": "ap-guangzhou-3", "Desc": "广州三区", "ZoneId": 100003, "Encrypt": 1, "Main": false, "ContainerEnabled": 0 },
            { "Name": "ap-guangzhou-4", "Desc": "广州四区", "ZoneId": 100004, "Encrypt": 1, "Main": false, "ContainerEnabled": 0 },
            { "Name": "ap-guangzhou-6", "Desc": "广州六区", "ZoneId": 100006, "Encrypt": 1, "Main": true,  "ContainerEnabled": 1 },
            { "Name": "ap-guangzhou-7", "Desc": "广州七区", "ZoneId": 100007, "Encrypt": 1, "Main": true,  "ContainerEnabled": 1 }
          ],
          "Count": 17,
          "SSCCount": 0,
          "EnableSSC": true,
          "Bucket": ""
        }
      ]
    }
  ],
  "Versions": ["4.1","3.1","3.0","2.1","2.0","1.2","1.1","1.0","0.15"],
  "VpcRule": "",
  "ErrorMsg": "",
  "RequestId": "be2524bb-5911-415a-933e-03ad53e4cd37"
}
```

上述返回中：广州共 4 个可用区，但 `Main=true && ContainerEnabled=1` 的只有 `ap-guangzhou-6` 与 `ap-guangzhou-7` 两个，**不满足 3 副本跨 AZ 至少 3 个可部署可用区的硬约束**。

---

## TCHouseDDescribeGoodsDetail

### 功能

询价两步流程的第一步：根据集群配置生成商品详情（GoodsDetail），用于后续 billing `CalculatePrice` 询价。

> 对应 cdwdoris 接口 `DescribeGoodsDetail`；存算分离场景对应 `DescribeSSCGoodsDetail`；CN 节点单独询价对应 `DescribeCNGoodsDetail`。

### 输入参数（关键字段）

| 参数名称 | 必选 | 类型 | 说明 |
|---------|------|------|------|
| Case | 是 | String | 操作类型：`CREATE_QUERYPRICE`（创建询价）/ `MODIFY_QUERYPRICE`（变配询价）/ `RENEW_QUERYPRICE`（续费询价） |
| Region | 是 | String | 地域 |
| Zone | 否 | String | 可用区，如 `ap-guangzhou-3` |
| HaFlag | 否 | Boolean | 是否高可用 |
| HaType | 否 | Integer | 高可用类型：0=非高可用 / 1=读高可用 / 2=读写高可用 |
| ProductVersion | 否 | String | 内核版本。目前支持的取值（未来可能扩展）：`3.1-new` / `3.0-new` / `4.1` / `starrocks-3.3` / `3.1` / `3.0` / `2.1` / `2.0` / `1.2` / `1.1` / `1.0` / `0.15` |
| InstanceId | 否 | String | 集群 ID（创建场景为空，变配/续费时必填） |
| Resources.N | 否 | Array of ResourceNodeSpec | 集群资源规格列表（FE/BE/CN 通过 `Type` 区分） |
| ChargeProperties | 否 | ChargeProperties | 计费信息 |
| InstanceName | 否 | String | 创建集群时填写的实例名 |
| UserVPCId | 否 | String | VPC ID |
| UserSubnetId | 否 | String | 子网 ID |
| EnableMultiZones | 否 | Boolean | 是否多可用区。⚠️ **白名单限制**：跨 AZ 询价受后端白名单控制，非白名单账户传 true 会返回 `InvalidParameter`。若遇到该错误，请回退到 false（单 AZ 询价）：跨 AZ 与单 AZ 的计费单价一致，仅架构部署形式不同，跨 AZ 不会引入额外费用 |
| UserMultiZoneInfos.N | 否 | Array of NetworkInfo | 多可用区网络信息，**EnableMultiZones=true 时必传**，示例：`[{"Zone":"ap-shanghai-2"},{"Zone":"ap-shanghai-5"},{"Zone":"ap-shanghai-8"}]` |
| Details | 否 | Object | 商品额外属性。**控制台真实下单会传 `{"EnableAlarmStrategy":true}`，本接口调用建议一并传入**，否则计费中心会因 billingHashCode 不匹配报 `FailedOperation.GetPriceParamError` |
| TimeZone | 否 | String | 时区，默认 `UTC+8`，与控制台保持一致 |

### ResourceNodeSpec 结构

```json
{
  "Type": "MASTER",          // MASTER（FE）/ CORE（BE）/ CN
  "SpecName": "S_16_64_H",
  "Count": 6,
  "DiskSpec": {
    "DiskType": "CLOUD_HSSD",
    "DiskSize": 1000,
    "DiskCount": 4
  }
}
```

### ChargeProperties 结构

```json
{
  "ChargeType": "PREPAID",
  "TimeSpan": 12,
  "TimeUnit": "m",
  "RenewFlag": 0
}
```

### 完整请求示例（包年包月 + 广州 + 高可用 + 存算一体）

```json
{
  "Case": "CREATE_QUERYPRICE",
  "Region": "ap-guangzhou",
  "Zone": "ap-guangzhou-6",
  "HaFlag": true,
  "ProductVersion": "2.0",
  "ChargeProperties": {
    "ChargeType": "PREPAID",
    "TimeSpan": 12,
    "TimeUnit": "m",
    "RenewFlag": 0
  },
  "Resources": [
    {
      "Type": "MASTER",
      "SpecName": "S_4_16_H",
      "Count": 3,
      "DiskSpec": {"DiskType": "CLOUD_HSSD", "DiskSize": 100, "DiskCount": 1}
    },
    {
      "Type": "CORE",
      "SpecName": "S_16_64_H",
      "Count": 6,
      "DiskSpec": {"DiskType": "CLOUD_HSSD", "DiskSize": 1000, "DiskCount": 4}
    }
  ],
  "Details": {"EnableAlarmStrategy": true},
  "TimeZone": "UTC+8"
}
```

### 输出参数

| 字段 | 类型 | 说明 |
|------|------|------|
| GoodsDetail | String | 商品详情字符串（直接传给 `CalculatePrice`） |
| GoodsCategoryId | Integer | 商品类目 ID（直接传给 `CalculatePrice`） |
| Type | String | 子商品码 |
| PayMode | String | 付费模式（供参考） |
| RegionId | Integer | 地域 ID |
| ZoneId | Integer | 可用区 ID |
| ResourceId | String | 资源标识符 |
| GoodsNum | Integer | 商品数目 |
| RequestId | String | 请求 ID |

### 节点角色与必填关系（通过 Resources 数组的 Type 字段表达）

| HaFlag | IsSSC | 必填 Resource Type 组合 |
|--------|-------|------------------------|
| false | false | MASTER(1) + CORE(≥1) |
| true | false | MASTER(≥3) + CORE(≥3，建议为副本数整数倍) |
| true | true | MASTER(≥3) + CORE(≥3) + CN(可选) |

**关键约束**：
- HA 模式下 MASTER 节点 Count ≥ 3（推荐 1 master + 2 follower）
- CORE 节点 Count ≥ 副本数（默认 3）且建议为副本数的整数倍
- 存算分离场景（IsSSC）：BE 仅作本地缓存，CN 节点处理纯计算请求；建议改用 `DescribeSSCGoodsDetail`
- ProductVersion 推荐选择最新稳定版（如 `2.0` / `3.0`）
- **`Details.EnableAlarmStrategy=true` 与 `TimeZone=UTC+8` 建议始终传入**，与控制台下单保持一致，避免 `CalculatePrice` 报 `all price code not match`
- 多 AZ 部署时 `EnableMultiZones=true` 与 `UserMultiZoneInfos` 必须一起传

### ⚠️ 跨可用区询价的白名单限制

**背景**：`EnableMultiZones=true` 的询价能力受后端白名单控制，非白名单账户无论如何组合 `UserMultiZoneInfos` / `HaFlag` 等参数，都会得到 `InvalidParameter`。

**处理策略**：

1. **首次遇到 `InvalidParameter` 且确认参数无误时，直接回退到单可用区询价**：设 `EnableMultiZones=false`、不传 `UserMultiZoneInfos`，其他参数（规格、磁盘、节点数、计费方式）保持不变。
2. **不需要让用户先去申请白名单**才能完成询价：跨 AZ 与单 AZ 部署的计费单价相同，仅为架构层面差异（多可用区容灾），跨 AZ 本身不引入额外价格。
3. **在报告中明确提示**：跨 AZ 部署的计费单价 = 单 AZ 部署单价，跨 AZ 不会额外收费；仅在架构上为多可用区容灾。
4. 若用户确需获取真实的跨 AZ 询价，引导其前往 [TCHouse-D 控制台](https://console.cloud.tencent.com/cdwdoris) 或联系商务开白名单后重试。

---

## BillingCalculatePrice

### 功能

询价两步流程的第二步：基于 `DescribeGoodsDetail` 返回的商品详情，调用 billing 接口获取真实价格（含折扣）。

> 对应公共 billing 接口 `CalculatePrice`，TCHouse-C / TCHouse-D 共用同一询价模型。

### 输入参数（关键字段）

| 参数名称 | 必选 | 类型 | 说明 |
|---------|------|------|------|
| GoodsCategoryId | 是 | Integer | 来自 `DescribeGoodsDetail` 返回 |
| GoodsDetail | 是 | String | 来自 `DescribeGoodsDetail` 返回 |
| GoodsNum | 是 | Integer | 来自 `DescribeGoodsDetail` 返回 |
| PayMode | 是 | String | `prePay`（包年包月）或 `postPay`（按量计费） |
| Region | 是 | String | 地域 ap code，如 `ap-guangzhou` |
| Zone | 否 | String | 可用区 ap code，如 `ap-guangzhou-6` |

### 输出参数

| 字段 | 类型 | 说明 |
|------|------|------|
| Price | Integer | 单价（单位：分） |
| TotalCost | Integer | 原价总费用（单位：分） |
| RealTotalCost | Integer | 折后实付金额（单位：分） |
| Policy | Integer | 折扣率（100=无折扣，85=85折） |
| TimeSpan | Integer | 计费时长 |
| TimeUnit | String | 时长单位（m=月，h=小时） |
| GoodsNum | Integer | 商品数量 |
| ProductCode | String | 产品编码 |
| SubProductCode | String | 子产品编码 |
| Currency | String | 币种（CNY/USD） |
| RequestId | String | 请求 ID |

> ⚠️ 价格单位为**分**，需除以 100 转换为元。不同账户折扣策略不同（合同折扣/大客户折扣/活动折扣），报价以 `RealTotalCost` 为准，并在报告中提示「实际价格以下单页面为准」。

---

## TCHouseDCreateInstance

### 功能

创建 TCHouse-D 集群（**本 Skill 不会调用此接口，仅作为部署参数生成参考**）。

### 关键输入参数

| 参数名称 | 必选 | 类型 | 说明 |
|---------|------|------|------|
| Zone | 是 | String | 主可用区 |
| HaFlag | 是 | Boolean | 是否高可用 |
| UserVPCId | 是 | String | VPC ID |
| UserSubnetId | 是 | String | 子网 ID |
| ProductVersion | 是 | String | 内核版本 |
| ChargeProperties | 是 | ChargeProperties | 计费属性 |
| InstanceName | 是 | String | 集群名称 |
| DorisUserPwd | 是 | String | Doris 用户密码（base64） |
| Resources.N | 是 | Array of ResourceNodeSpec | FE/BE/CN 资源配置（通过 Type 区分） |
| EnableMultiZones | 否 | Boolean | 是否多可用区 |
| UserMultiZoneInfos | 否 | Array | 多可用区子网信息 |

> **本 Skill 不会执行此接口**。仅用于在推荐方案中给出"控制台创建参数参考"。
