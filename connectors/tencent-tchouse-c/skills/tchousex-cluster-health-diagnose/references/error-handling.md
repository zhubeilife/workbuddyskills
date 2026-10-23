# TCHouse-X 错误码统一处理规范

> **何时使用本文件**：所有 tchousex 系列 skill 在调用云 API 遇到错误码时，均以本文件为准；SKILL.md 中的「错误码与处理策略」表若与本文冲突，以本文为准。

## 1. `UnsupportedRegion`（该接口不支持此地域访问）

### 1.1 典型错误返回

```json
{
  "code": "UnsupportedRegion",
  "msg": "该接口不支持此地域访问。(\"cdwch.DescribeLangfuseInstances\")",
  "data": {
    "Response": {
      "Error": {
        "Code": "UnsupportedRegion",
        "Message": "该接口不支持此地域访问。"
      }
    }
  }
}
```

### 1.2 语义

- 后端返回该错误码时，含义为：**当前请求的 `Region` 参数所指向的地域，TCHouseX 产品未在该地域开服**。
- 这**不是**参数格式错误、也**不是**权限问题、**不是**限流。
- TCHouseX 相对 C/D 支持地域较少，且随业务发展会新增。因此 skill **不维护"支持地域白名单"**，一律以本错误码作为运行时判定依据 —— 上了新地域后 skill 无需发版即可跟进。

### 1.3 Agent 行为（强约束）

| 行为项 | 要求 |
| --- | --- |
| 是否重试 | ❌ **不重试**（重试无意义，同一地域的下次请求仍会返回同样错误） |
| 是否切换地域 | ❌ **不自行切换**（不要"猜"用户想去的地域） |
| 是否报 error | ❌ **不在最终报告中作为 error 抛出** |
| 必须动作 | ✅ 调用 `ask_user`（WorkBuddy 中为 `AskUserQuestion`）询问用户，让其确认当前指定的地域是否正确 |

### 1.4 询问模板

```text
您指定的地域「{中文地域名}（{Region}）」当前不支持 TCHouseX 产品。可能原因：
  1) 地域填错了 —— 例如把兄弟产品（TCHouseC/TCHouseD）的地域套过来；
  2) 该地域尚未开通 TCHouseX 服务。

请确认：
  A. 目标实例实际所在地域是什么？（例如："广州 ap-guangzhou"）
  B. 如果就是 {中文地域名}，请通过腾讯云控制台确认该地域是否已开通 TCHouseX；
     未开通时，需要走产品申请流程，本 skill 无法绕过。
```

### 1.5 用户答复后的后续动作

- 用户给出**新地域** → 重新调用原工具（新的 `Region` / `RegionId`）。
- 用户确认**就是这个地域** → 输出以下结论并终止流程：
  > "TCHouseX 在地域『{中文地域名}』暂未开通，本次任务无法继续。请通过腾讯云工单或产品经理确认开通计划。"
- 用户未回复 / 超时 → 按 skill 通用规则处理（一般是暂停并告知用户）。

### 1.6 反例（禁止行为）

- ❌ 在 skill 内维护"支持地域列表"并做白名单校验（业务新增地域时 skill 会过时）。
- ❌ 收到该错误码后自动改成 `ap-guangzhou` 之类的默认地域重试。
- ❌ 把该错误码包装成 `InvalidParameter.*` 或"内部错误"上报给用户。

## 2. `BillingCalculatePrice` 已知兼容性问题

### 2.1 现象

Step A（`TCHouseXDescribeGoodsDetail`）返回的 `GoodsDetailStr` 使用 **PascalCase** key（如 `TimeSpan`、`ChargeProperties`、`Resources[].SpecName`），而 Step B（`BillingCalculatePrice`）后端期望 **camelCase** key（如 `timeSpan`、`chargeProperties`、`resources[].specName`）。

直接透传会报：`InvalidParameter: timeSpan 缺失`。

### 2.2 根因

两个接口的命名风格不一致：`DescribeGoodsDetail` 遵循腾讯云 API 的 PascalCase 规范输出，而 `BillingCalculatePrice` 计费侧内部使用 camelCase 解析。此外，Step A 返回的外层对象中包含 `curDeadline` / `newConfig` / `oldConfig` / `sv_tchouse_x_warehouse_hp` 等字段，**必须原样保留全部透传**——其中 `sv_tchouse_x_warehouse_hp` 是计费数量（Warehouse 总 CU 数），删除后会报 `FailedOperation.GetPriceParamError: all price code not match`。

### 2.3 处理方式

必须按 [cost-estimation-guide.md §5.3.1](../skills/tchousex-cluster-sizing-recommendation/references/cost-estimation-guide.md#531-goodsdetailstr--goodsdetail-转换强制步骤不可跳过) 做 key camelCase 转换后（保留所有字段）再传入。**不属于可重试错误，重试无意义**。

### 2.4 `VirtualClusterName` 长度校验

云 API 要求 `VirtualClusterName` 长度 ≥ **6 字符**。传入过短的名称（如"测试" 4 字符）会被拒绝，且错误信息不明确（表现为 `InvalidParameter` 但 message 不直接点出长度问题）。建议使用 ≥ 6 字符的中文名（如"我的Warehouse"）。询价场景下 skill 无需传顶层 `VirtualClusterName`，tool 层自动补占位；但 `Resources[].VirtualClusterName` 仍需 skill 保证 ≥ 6 字符。
