# tchoused-describe-instance-nodes

## 功能说明

调用腾讯云 TCHouse-D（Doris）的 `DescribeInstanceNodes` 云 API，获取指定集群的节点信息列表，包括 FE（Frontend）、BE（Backend）和可选的 CN（Compute Node）节点。

## 接口信息

- **请求域名**：`cdwdoris.tencentcloudapi.com`
- **接口名称**：`DescribeInstanceNodes`
- **API 版本**：`2021-12-28`
- **请求方式**：POST
- **频率限制**：20次/秒

## 输入参数

| 参数名称      | 必选 | 类型    | 描述                                                                                  |
| ------------- | ---- | ------- | ------------------------------------------------------------------------------------- |
| InstanceId    | 是   | String  | 集群实例 ID，格式如 `cdwdoris-xxxxxxxx`                                               |
| Region        | 是   | String  | 地域，如 `ap-guangzhou`                                                               |
| NodeRole      | 否   | String  | 节点角色类型：`fe`（FE 节点）、`be`（BE 节点）、`cn`（CN 节点），默认 `data`（即 BE） |
| Offset        | 否   | Integer | 分页偏移量，第一页为 0，第二页为 10                                                   |
| Limit         | 否   | Integer | 分页步长，默认为 10                                                                   |
| DisplayPolicy | 否   | String  | 展现策略，`All` 时显示所有                                                            |

## 输出参数

| 参数名称                          | 类型    | 描述                                       |
| --------------------------------- | ------- | ------------------------------------------ |
| TotalCount                        | Integer | 节点总数                                   |
| NodeRoles                         | Array   | 节点角色列表，如 `["FE","BE"]`             |
| InstanceNodesList                 | Array   | 节点信息列表                               |
| InstanceNodesList[].Ip            | String  | 节点内网 IP                                |
| InstanceNodesList[].Spec          | String  | 规格标识，如 `S_4_16_H`                    |
| InstanceNodesList[].Core          | Integer | CPU 核数                                   |
| InstanceNodesList[].Memory        | Integer | 内存大小（GB）                             |
| InstanceNodesList[].DiskSize      | Integer | 磁盘大小（GB）                             |
| InstanceNodesList[].DiskType      | String  | 磁盘类型，如 `CLOUD_SSD`/`CLOUD_HSSD`      |
| InstanceNodesList[].Role          | String  | 节点角色：`master`/`core`/`observer`/`follower` 等 |
| InstanceNodesList[].FeRole        | String  | FE 节点角色（仅 FE 节点有）                |
| InstanceNodesList[].Status        | String  | 节点状态：`Running`/`Stopped`/`Unknown`    |
| InstanceNodesList[].Rip           | String  | 内网 IP（同 Ip 字段）                      |
| InstanceNodesList[].UUID          | String  | 节点唯一标识                               |

## 使用示例

### 请求示例

```json
{
  "Action": "DescribeInstanceNodes",
  "Version": "2021-12-28",
  "Region": "ap-guangzhou",
  "InstanceId": "cdwdoris-xxxxxxxx",
  "NodeRole": "be",
  "DisplayPolicy": "All"
}
```

### 响应示例

```json
{
  "Response": {
    "TotalCount": 3,
    "NodeRoles": ["FE", "BE"],
    "InstanceNodesList": [
      {
        "Ip": "10.0.0.1",
        "Spec": "S_8_32_H",
        "Core": 8,
        "Memory": 32,
        "DiskType": "CLOUD_HSSD",
        "DiskSize": 1000,
        "Role": "core",
        "FeRole": "",
        "Status": "Running",
        "Rip": "10.0.0.1",
        "UUID": "xxx-xxx-1"
      },
      {
        "Ip": "10.0.0.2",
        "Spec": "S_8_32_H",
        "Core": 8,
        "Memory": 32,
        "DiskType": "CLOUD_HSSD",
        "DiskSize": 1000,
        "Role": "core",
        "FeRole": "",
        "Status": "Running",
        "Rip": "10.0.0.2",
        "UUID": "xxx-xxx-2"
      }
    ],
    "RequestId": "abc-xxx-xxx"
  }
}
```

## 典型使用场景

- **节点健康检查**：遍历所有节点，确认 `Status` 是否全部为 `Running`，发现异常节点
- **资源瓶颈判断**：通过 `Core`/`Memory`/`DiskSize` 了解节点规格，结合监控指标判断资源是否充足
- **拓扑确认**：分别用 `NodeRole=fe` / `be` / `cn` 拉取各角色节点，确认 FE Master/Follower/Observer 数量、BE 数量等
- **故障定位**：当监控指标异常时，通过节点 IP 定位具体是哪个节点出问题
- **FE 选举状态**：通过 `FeRole`（如 `master`/`follower`/`observer`）判断 FE 高可用状态

## Doris 与 ClickHouse 节点角色差异说明

| 维度 | ClickHouse (cdwch) | Doris (cdwdoris) |
| --- | --- | --- |
| 协调/元数据 | ZooKeeper（独立 Common 节点） | FE 内置 BDB-JE，无独立 ZK |
| 计算/存储 | Data 节点（合一） | BE 节点（合一），存算分离架构下额外有 CN 节点 |
| 高可用 | 通过 ReplicatedMergeTree + ZK | FE 多副本 + BE 多副本（默认 3 副本） |

> ⚠️ **注意**：Doris 没有 ClickHouse 的"shard"概念，分片对应 Doris 中的 Tablet/Bucket，副本通过 BE 节点上的 Replica 实现。健康诊断时不需要查询 shard 拓扑接口，使用 `DescribeReplicationInfo` 或 SQL 查询 `SHOW REPLICA STATUS` 获取副本健康度。
