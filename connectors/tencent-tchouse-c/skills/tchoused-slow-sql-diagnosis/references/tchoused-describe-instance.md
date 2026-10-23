
# tchoused-describe-instance

## 功能说明

调用腾讯云 TCHouse-D（Doris）的 `DescribeInstance` 云 API，根据实例 ID 查询集群的详细信息。

## 接口信息

- **请求域名**：`cdwdoris.tencentcloudapi.com`
- **接口名称**：`DescribeInstance`
- **API 版本**：`2021-12-28`
- **请求方式**：POST
- **频率限制**：20次/秒

## 输入参数

| 参数名称   | 必选 | 类型   | 描述                                       |
| ---------- | ---- | ------ | ------------------------------------------ |
| InstanceId | 是   | String | 集群实例 ID，格式如 `cdwdoris-xxxxxxxx`    |
| Region     | 是   | String | 地域，如 `ap-guangzhou`、`ap-shanghai`     |

## 输出参数

| 参数名称                            | 类型   | 描述                                                              |
| ----------------------------------- | ------ | ----------------------------------------------------------------- |
| InstanceInfo.InstanceId             | String | 集群实例 ID                                                       |
| InstanceInfo.InstanceName           | String | 集群名称                                                          |
| InstanceInfo.Status                 | String | 状态：Init/Serving/Deleted/Deleting/Modify/Isolated/Changing      |
| InstanceInfo.StatusDesc             | String | 状态中文描述，如"运行中"                                          |
| InstanceInfo.Version                | String | Doris 内核版本号                                                  |
| InstanceInfo.BuildVersion           | String | 详细 build 版本，如 `doris-2.0.3-rc06`                            |
| InstanceInfo.Region                 | String | 地域                                                              |
| InstanceInfo.Zone                   | String | 可用区                                                            |
| InstanceInfo.VpcId                  | String | 私有网络 ID                                                       |
| InstanceInfo.SubnetId               | String | 子网 ID                                                           |
| InstanceInfo.PayMode                | String | 付费类型：PREPAID（包年包月）/ POSTPAID_BY_HOUR（按量计费）        |
| InstanceInfo.CreateTime             | String | 集群创建时间                                                      |
| InstanceInfo.ExpireTime             | String | 集群到期时间（包年包月）                                          |
| InstanceInfo.AccessInfo             | String | 访问地址 JSON 字符串，包含 mysql/http 协议的连接地址              |
| InstanceInfo.MasterSummary          | Object | FE（Frontend）节点规格信息                                        |
| InstanceInfo.MasterSummary.Spec     | String | 规格标识，如 `S_4_16_H`                                           |
| InstanceInfo.MasterSummary.NodeSize | Int    | FE 节点数量                                                       |
| InstanceInfo.MasterSummary.Core     | Int    | CPU 核数                                                          |
| InstanceInfo.MasterSummary.Memory   | Int    | 内存大小（GB）                                                    |
| InstanceInfo.MasterSummary.Disk     | Int    | 磁盘大小（GB）                                                    |
| InstanceInfo.MasterSummary.DiskType | String | 磁盘类型，如 `CLOUD_HSSD`（增强型 SSD）                           |
| InstanceInfo.MasterSummary.DiskCount| Int    | 单节点云盘数量                                                    |
| InstanceInfo.MasterSummary.MaxDiskSize| Int  | 单盘最大容量（GB）                                                |
| InstanceInfo.CoreSummary            | Object | BE（Backend）节点规格信息（结构同 MasterSummary）                 |
| InstanceInfo.HA                     | String | 是否高可用（`"true"` / `"false"`，注意为字符串类型）              |
| InstanceInfo.HaType                 | Int    | 高可用类型：0-非HA，1-FE 高可用，2-FE+BE 高可用                   |
| InstanceInfo.Components             | String | 组件描述（JSON 字符串），含 FE/BE/Broker 等组件版本               |
| InstanceInfo.Kind                   | String | 集群类型，如 `STANDARD`（标准）/ `SSC`（存算分离）                |
| InstanceInfo.HasClsTopic            | Bool   | 是否启用日志服务                                                  |
| InstanceInfo.CanAttachCbs           | Bool   | 是否支持挂载云盘                                                  |
| InstanceInfo.RegionId               | Int    | 地域数字 ID                                                       |
| InstanceInfo.StateInfo              | Object | 当前流程状态详情（FlowName/FlowProgress/FlowMsg）                 |

## 使用示例

### 请求示例

```json
{
  "Action": "DescribeInstance",
  "Version": "2021-12-28",
  "Region": "ap-guangzhou",
  "InstanceId": "cdwdoris-xxxxxxxx"
}
```

### 响应示例

```json
{
  "Response": {
    "InstanceInfo": {
      "InstanceId": "cdwdoris-xxxxxxxx",
      "InstanceName": "测试 Doris 集群",
      "Status": "Serving",
      "StatusDesc": "运行中",
      "Version": "2.0",
      "BuildVersion": "doris-2.0.3-rc06",
      "Region": "ap-guangzhou",
      "Zone": "ap-guangzhou-6",
      "VpcId": "vpc-xxxxxxxx",
      "SubnetId": "subnet-xxxxxxxx",
      "PayMode": "PREPAID",
      "CreateTime": "2026-05-28 19:16:50",
      "ExpireTime": "2026-06-28 19:16:50",
      "AccessInfo": "[{\"address\":\"172.x.x.x:9030\",\"protocol\":\"mysql\"},{\"address\":\"172.x.x.x:8030\",\"protocol\":\"http\"}]",
      "MasterSummary": {
        "Spec": "S_4_16_H",
        "NodeSize": 3,
        "Core": 4,
        "Memory": 16,
        "Disk": 100,
        "DiskType": "CLOUD_HSSD",
        "DiskCount": 1,
        "MaxDiskSize": 32000
      },
      "CoreSummary": {
        "Spec": "S_8_32_H",
        "NodeSize": 3,
        "Core": 8,
        "Memory": 32,
        "Disk": 1000,
        "DiskType": "CLOUD_HSSD",
        "DiskCount": 1
      },
      "HA": "true",
      "HaType": 2,
      "Kind": "STANDARD",
      "Components": "{\"FE\":\"2.0.3\",\"BE\":\"2.0.3\"}",
      "RegionId": 1,
      "StateInfo": {
        "InstanceState": "Serving",
        "InstanceStateDesc": "运行中",
        "FlowName": "",
        "FlowProgress": 0
      }
    },
    "RequestId": "xxx-xxx-xxx"
  }
}
```

## 典型使用场景

- **验证集群可用性**：确认集群状态为 `Serving` 才能继续后续操作
- **获取版本信息**：通过 `BuildVersion` 判断 Doris 版本（如 `doris-2.0.3`），不同版本支持的功能集不同
- **获取连接地址**：从 `AccessInfo` 中获取 mysql 协议地址（默认 9030 端口），用于客户端连接
- **了解集群规格**：FE/BE 节点数量、CPU/内存/磁盘配置影响查询并发能力和资源瓶颈判断
- **磁盘类型判断**：`DiskType` 为 `CLOUD_HSSD`（增强型 SSD）或 `CLOUD_PREMIUM`（高性能云盘）直接影响 IO 密集型查询的性能预期
- **高可用判断**：`HA` / `HaType` 字段决定是否启用 FE 多副本/BE 多副本，影响容灾和可用性建议
- **存算分离识别**：`Kind` 为 `SSC` 表示存算分离架构，存在 CN（Compute Node）节点
