# 事井然未暴露能力

## 何时使用

用户要求的动作在本 Skill 的 operation 列表里没有对应命令时，先读本文，如实说明「当前 CLI 未提供该能力」，并给出可行的替代路径；**不要猜测 operation 名，不要直接调用 E10 原始接口，也不要用别的 operation 硬凑**。

## 当前未纳入 CLI 的能力

| 用户诉求 | 现状 | 处理方式 |
| --- | --- | --- |
| 给任务/项目上传或替换附件 | `project.attachment.upload` 未暴露。源资料只说明 `attachment` 字段接受**已上传文件 ID**，未提供事井然模块自己的上传接口与文件安全确认链 | 不要把本地文件当作附件直接写入。先告知用户需在 E10 页面完成上传，再提供已上传文件 ID；本 Skill 不代办上传 |
| 按字段类型自动解析名称到 ID | `project.field.auto-resolve` 未暴露。CLI 只提供分步解析 operation，由 Agent 按字段类型显式编排 | 按 [`field-resolution.md`](field-resolution.md) 分步解析：人员/部门/分部用 `project.employee/department/subcompany.resolve`；项目/任务名称用 `project.project.list` / `project.task.list`；Ebuilder 关联字段用 `project.form.fields` + `project.form.data.page`；字典字段用 `project.dictionary.*` |
| 修改系统状态 `sys_status` | `sys_status` 是系统维护字段，只能用于查询过滤 | 不接受写入。用户要变更系统状态时，说明需在 E10 页面操作 |
| 跨表单批量导入 / 批量删除 | 未暴露 | 创建可用 `records` 数组在单次 `create.prepare` 里传 1-100 条；删除只能逐条 `delete.prepare/apply`，不要并发刷接口 |
| 直接把某个字段的全部选项元数据一次性拉全 | `project.form.options` 可用，但必须先确定 `table` 与 `fieldName` | 按 [`field-resolution.md`](field-resolution.md) 的「Select 与字典字段」先定位字段，再查选项 |
| 附件内容下载、OCR、文件内容解析 | 未暴露 | 不属于本 Skill；不要用其他模块的接口代替 |

## 注意

- 未暴露 ≠ 用户不能做：优先给出 E10 页面路径或已支持的分步替代方案，不要为了"完成"而编造 operation、字段或接口路径。
- 任何写入都必须走 `prepare -> apply` 确认链；不用"能力未暴露"当作跳过用户确认的理由。
- 与 operation、字段、风险等级有关的最终依据是 `weaver-work-cli project schema`，不是本文；本文只说明缺口与替代路径。
