# 未实现能力（withheldOperations）

以下能力出现在源资料的能力清单里，但源资料**没有给出可用的接口路径、方法、参数或响应结构**，因此未纳入 CLI manifest，也没有对应 operation。遇到这些意图时直接说明不可用，不要尝试用其它接口替代或猜测接口。

| 能力 | 源资料状态 | 处理方式 |
|---|---|---|
| `contract.credit.query`（相对方工商资信查询，CM-018） | `references/enterprise-credit/api-enterprise-credit.md` 只有 9 行索引，指向的 `api-credit-info.md`、`api-enterprise-change.md`、`api-monitor-config.md` 三个子文档在源资料中不存在 | 告知用户当前不可用；如确需使用，请先提供完整的接口文档 |
| `contract.credit.change`（企业变更查询） | 同上，接口文档缺失 | 同上 |
| `contract.credit.monitor`（企业监控开启/修改） | 同上；且属于写操作，缺少确认与回查契约 | 同上；不得在未拿到契约前实现写操作 |
| `contract.workflow.withdraw`（撤回/退回流程） | 源资料只提到"除非调用撤回/退回接口"，未给出路径、方法和参数 | 告知用户当前不可用；如需撤回请到 E10 前台操作 |

## 已知的源资料状态冲突

- `SKILL.md` 能力清单把 CM-005 ~ CM-015 多数标注为"可用"，但 `feature-map.json` 的 `not_released` 里写着 CM-005 ~ CM-015 未完成，且 `features` 只列出 CM-001、CM-002、CM-004、CM-018、CM-043、CM-044、CM-045。
- 本 CLI 的实现以"接口文档完整可读"为准：只有能拿到路径、方法、参数和响应结构的接口才生成 operation，其余一律列入 `withheldOperations`。
- 如果用户后续补齐了文档，需要同步更新 CLI 与 Skill，并更新 `references/source-manifest.json` 的指纹。

## 其它边界

- 12 类合同审批流程（销售、采购、协议、变更、解除、关闭、开票、收款、付款、履约计划、进度提报、供应商准入）共用同一组接口；流程差异体现在运行时解析出的 `workflowId` 与表单字段，而不是不同的接口路径。
- 企业资信与合同审批是两条互不相干的链：不要把"查一下某公司资信"路由到 `contract.request.*`。
- 提交审批后流程不可撤回（撤回接口未实现），执行前必须让用户清楚这一点。

## 注意

- 不要为了"完成任务"而猜测未文档化的接口路径或字段名。
- 涉及未实现能力的用户请求，回复中应说明缺什么（路径/参数/响应/确认契约），并给出需要用户提供的材料。
