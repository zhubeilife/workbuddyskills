# tchoused-describe-cluster-configs

## 功能说明

调用腾讯云 TCHouse-D（Doris）的 `DescribeClusterConfigs` 云 API，获取集群配置文件（`fe.conf`、`be.conf` 等）的内容。

## 接口信息

- **请求域名**：`cdwdoris.tencentcloudapi.com`
- **接口名称**：`DescribeClusterConfigs`
- **API 版本**：`2021-12-28`
- **请求方式**：POST
- **频率限制**：20次/秒

## 输入参数

| 参数名称          | 必选 | 类型    | 描述                                                                |
| ----------------- | ---- | ------- | ------------------------------------------------------------------- |
| InstanceId        | 是   | String  | 集群实例 ID，格式如 `cdwdoris-xxxxxxxx`                             |
| Region            | 是   | String  | 地域                                                                |
| ConfigType        | 否   | Integer | 0-公有云查询；1-青鹅查询（显示所有）                                |
| FileName          | 否   | String  | 模糊搜索关键字文件名                                                |
| ClusterConfigType | 否   | Integer | 0-集群维度；1-节点维度；2-启动脚本；3-计算组维度                    |
| IPAddress         | 否   | String  | eth0 的 IP 地址（节点维度查询时使用）                               |
| ComputeGroupId    | 否   | String  | 计算组 ID（计算组维度查询时使用）                                   |

## 输出参数

| 参数名称                                | 类型    | 描述                                       |
| --------------------------------------- | ------- | ------------------------------------------ |
| ClusterConfList                         | Array   | 配置文件信息列表                           |
| ClusterConfList[].FileName              | String  | 文件名（如 `fe.conf` / `be.conf`）         |
| ClusterConfList[].FileConf              | String  | 文件内容（明文）                           |
| ClusterConfList[].FilePath              | String  | 文件路径，如 `/usr/local/service/doris/conf` |
| ClusterConfList[].OriParam              | String  | base64 编码后的原始配置内容                |
| ClusterConfList[].NeedRestart           | Integer | 修改后是否需要重启：0-不需要；1-需要       |
| ClusterConfList[].FileKeyValuesNew      | Array   | 文件中所有 key-value 列表                  |
| ClusterConfList[].FileKeyValuesNew[].KeyName        | String  | 配置项名                          |
| ClusterConfList[].FileKeyValuesNew[].Value          | String  | 当前值                            |
| ClusterConfList[].FileKeyValuesNew[].Message        | String  | 配置说明                          |
| ClusterConfList[].FileKeyValuesNew[].SupportHotUpdate| Integer | 是否支持热更新：0-否；1-是       |
| ClusterConfList[].ComputeGroupId        | String  | 所属计算组 ID                              |
| BuildVersion                            | String  | 当前内核版本（如 `doris-2.0.3-rc06`）      |
| HasCN                                   | Boolean | 是否包含 CN 节点（存算分离架构）           |
| ExistingJarConfList                     | Array   | 实例已存在的 jar 包列表                    |
| ErrorMsg                                | String  | 错误信息                                   |

## 使用示例

### 请求示例

```json
{
  "Action": "DescribeClusterConfigs",
  "Version": "2021-12-28",
  "Region": "ap-guangzhou",
  "InstanceId": "cdwdoris-xxxxxxxx",
  "ConfigType": 0,
  "ClusterConfigType": 0
}
```

### 响应示例

```json
{
  "Response": {
    "ClusterConfList": [
      {
        "FileName": "fe.conf",
        "FilePath": "/usr/local/service/doris/conf",
        "FileConf": "priority_networks = 10.0.0.0/24\nhttp_port = 8030\nrpc_port = 9020\nquery_port = 9030\nedit_log_port = 9010\n...",
        "NeedRestart": 0,
        "FileKeyValuesNew": [
          { "KeyName": "priority_networks", "Value": "10.0.0.0/24", "Message": "FE 节点对外服务的网段", "SupportHotUpdate": 0 },
          { "KeyName": "query_port", "Value": "9030", "Message": "MySQL 协议端口", "SupportHotUpdate": 0 }
        ]
      },
      {
        "FileName": "be.conf",
        "FilePath": "/usr/local/service/doris/conf",
        "FileConf": "be_port = 9060\nbrpc_port = 8060\nwebserver_port = 8040\nheartbeat_service_port = 9050\n...",
        "NeedRestart": 0,
        "FileKeyValuesNew": [
          { "KeyName": "be_port", "Value": "9060", "Message": "BE 节点 thrift 服务端口", "SupportHotUpdate": 0 },
          { "KeyName": "storage_root_path", "Value": "/data/doris-storage", "Message": "BE 数据存储路径", "SupportHotUpdate": 0 }
        ]
      }
    ],
    "BuildVersion": "doris-2.0.3-rc06",
    "HasCN": false,
    "ErrorMsg": "",
    "ExistingJarConfList": [],
    "RequestId": "xxx-xxx"
  }
}
```

## 关键配置项说明（性能/容量诊断常用）

### FE 配置（`fe.conf`）

| KeyName | 含义 | 诊断关注点 |
| --- | --- | --- |
| `query_port` | MySQL 协议端口（默认 9030） | 客户端连接 |
| `http_port` | FE Web UI 端口（默认 8030） | 监控查看 |
| `qe_max_connection` | FE 最大连接数（默认 1024） | 连接数告警时检查是否需要调大 |
| `max_running_txn_num_per_db` | 单个 db 的最大运行事务数 | 写入吞吐瓶颈定位 |
| `default_replication_num` | 默认副本数 | 表设计阶段建议 ≥3 |

### BE 配置（`be.conf`）

| KeyName | 含义 | 诊断关注点 |
| --- | --- | --- |
| `mem_limit` | BE 进程内存上限 | OOM 风险评估，建议 ≤ 物理内存 80% |
| `storage_root_path` | 数据存储路径 | 多盘配置时关注 |
| `write_buffer_size` | 写缓冲区大小 | 写入慢时关注 |
| `query_cache_max_size_mb` | 查询缓存上限 | 重复查询命中率优化 |
| `tablet_max_compaction_score` | Tablet compaction 阈值 | 合并不及时诊断 |
| `compaction_task_num_per_disk` | 每个磁盘 compaction 并发 | IO 瓶颈调优 |

## 典型使用场景

- **性能调优诊断**：检查 `mem_limit`、`write_buffer_size`、`query_cache_max_size_mb` 等是否合理
- **容量规划**：通过 `default_replication_num` 判断副本数对存储成本的影响
- **故障定位**：检查 `qe_max_connection` 是否过低导致连接拒绝
- **版本识别**：从 `BuildVersion` 获取精确的 Doris 内核版本号

## 与 ClickHouse 配置文件差异

| 维度 | ClickHouse | Doris |
| --- | --- | --- |
| 主配置文件 | `config.xml` / `users.xml` / `metrika.xml` | `fe.conf` / `be.conf` |
| 配置格式 | XML | properties (key=value) |
| 热更新 | 大部分支持 | 通过 `ADMIN SET FRONTEND CONFIG` / `ADMIN SET BACKEND CONFIG` 命令；部分需重启 |
| 协调服务 | 依赖 ZooKeeper（zookeeper.xml） | FE 自身通过 BDB-JE 完成元数据共识，无需 ZK 配置 |
