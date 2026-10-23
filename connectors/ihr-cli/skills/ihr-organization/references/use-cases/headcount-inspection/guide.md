# Use Case：编制检查

## 目标定义

用户希望核对编制方案、某部门编制记录或控编维度占编数，例如“查看 2026 年研发部门的计划编制和按职级维度的占编数”。目标对象是编制记录和服务端计算结果，不是普通组织树人数。

## 业务判断

1. 使用 `headcount-department search` 按年度、周期或管控条件查找当前用户可见的编制部门记录。
2. 从 search 返回中唯一确认编制记录 `id`、对应 `departmentId`、方案和周期；不能将普通部门 ID 直接传给维度命令。
3. 需要维度定义时调用 `headcount-dimension by-id`；需要计算时只提交已确认的 `hcDepartmentId` 和明确的 `controlDimensions`。
4. 计划编制人数、直属编制数、预算和占编数量分别报告；不把它们合并为一个“部门人数”。

## 执行与验证

```text
headcount-department search
  -> 确认编制部门记录 ID
  -> headcount-dimension by-id（需要解释维度时）
  -> headcount-dimension occupy-count（需要占编计算时）
```

metadata command 执行前读取对应 Schema；业务 payload 位于 `response.body.data`。成功证据是返回结果中与确认 ID、年度/周期和维度条件一致的字段。超时或结构无法解释时不自动重试。

## 停止条件

- 编制年度、部门记录 ID 或控编条件无法确认。
- 用户要求 `child-hc-count`，该命令仍是 DRAFT/未注册。
- 用户把普通组织树节点人数当作编制占用，且未明确需要哪一种口径。
- `by-id`/`occupy-count` 的 ID 不是当前 search 返回的已授权记录。
