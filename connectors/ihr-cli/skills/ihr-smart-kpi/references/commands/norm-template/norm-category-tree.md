# `ihr-cli smart-kpi norm-category +tree`

完整路径：`skills/ihr-smart-kpi/references/commands/norm-template/norm-category-tree.md`（瀹屾暣璺緞，ID）。
查询当前公司的指标分类树。省略 --norm-menu-type 时仍请求 CURRENCY_NORMS，保持指标模板导入兼容。指标库流程必须显式传入 CURRENCY_NORMS、COMPETENCE 或 SENSE_OF_WORTH。
## 参数
| 参数 | 类型 | 必填 | 默认值 | 可选值 | 业务说明 |
| --- | --- | --- | --- | --- | --- |
| `--norm-menu-type` | string | 否 | `CURRENCY_NORMS` | `CURRENCY_NORMS` / `COMPETENCE` / `SENSE_OF_WORTH` | 指标库类型；指标模板导入省略时使用通用指标库。 |
不接受 --json 或 --stdin。
查询当前公司的通用指标分类树，用于解析 `NORM_TYPE` 字段。
## 输入
本命令没有业务参数，不接受 `--json` 或 `--stdin`。
```bash
ihr-cli smart-kpi norm-category +tree
```
## 输出与 Agent 规则
- 返回当前公司分类树，使用分类名称、完整路径和 ID 进行解析。
- 仅在待映射字段确实为指标分类且客户提供分类名称时调用。
- 名称唯一匹配时可使用对应 ID；同名节点对应多个路径时必须展示客户可读路径并让客户选择。
- 零匹配或多匹配未解决时阻止预览确认，不能把原始分类文本直接保存成 ID，也不能自行创建分类。
- 不接受公司或用户字段；只读失败不自动重试。
