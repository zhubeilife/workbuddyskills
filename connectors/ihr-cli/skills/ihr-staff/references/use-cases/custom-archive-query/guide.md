# 查询企业自定义员工档案

## 目标定义

用户希望查询当前租户自行配置的员工补充信息子集，可以是某类自定义档案列表，也可以是指定员工的一个或多个自定义档案。

完成标准是：从真实元数据唯一确认 `metaDataType=SUBSET` 和 `metaCode`，使用正确员工范围查询，并只返回用户确认的当前页或单员工结果。

## 业务判断

读取[员工档案](../../domain/archives.md)：

1. 执行 `staff +flexMetaList --kind custom`，按用户给出的档案名称或 code 形成候选。
2. 唯一候选必须明确为 `SUBSET`；多候选展示名称、`metaCode` 和必要的区分信息，让用户选择。
3. 业务取数使用 `metaCode`，不使用元数据 `id`。
4. 判断用户要的是档案列表还是指定员工取数；后者必须唯一确认 `staffId`。
5. 用户要求按自定义字段筛选时，必须已经给出真实字段 code。当前 Meta Detail 不可执行，无法从中文字段名唯一得到 code 时停止该筛选，不猜测。

## 执行与验证

列表目标：

```text
staff +flexMetaList --kind custom
-> 唯一 SUBSET + metaCode
-> staff +archiveList --meta-data-code <metaCode> --meta-data-type SUBSET
```

单员工目标：

```text
唯一 staffId + 一个或多个 SUBSET metaCode
-> staff +archiveGet --staff-id <staffId> --meta-data-code <codes> --meta-data-type SUBSET
```

- 列表只查当前页，不添加自定义子集不支持的排序参数。
- 单员工一次最多五个 code；超过时请用户缩小范围，不自动拆批。
- Meta 可见但业务查询为空或失败时，只说明业务入口未返回数据，不能用 Meta 结果冒充档案内容。
- 响应结构与当前契约不一致时停止解释未知字段，并报告契约漂移。
