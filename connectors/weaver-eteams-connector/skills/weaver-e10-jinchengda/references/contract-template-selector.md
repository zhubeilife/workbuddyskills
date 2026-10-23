# 合同类型与模板查询

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


用途：按合同类型定位可选模板，或对指定模板查看详情。四个 operation 全部为 `read`。

## operation 与接口

| operation | 方法 | 路径 | 关键输入 |
|---|---|---|---|
| `contract.type.tree` | GET | `/api/ebd/contract/type/allTypes` | 无（无需传参） |
| `contract.template.tree` | GET | `/api/ebd/contract/tpltree/queryList` | `treeName`、`parentId`、`treeType`、`isSystem`、`useType`、`appId` |
| `contract.template.list` | GET | `/api/ebd/contract/tplinfo/getListPage` | `templateName`、`belongId`、`contractType`、`templateStatus`、`source`、`pageNo`、`pageSize` 等 |
| `contract.template.detail` | GET | `/api/ebd/contract/tplinfo/getById` | `id`（必填，模板 ID） |

分页参数命名：`contract.template.list` 用 `pageNo`（从 1 开始）+ `pageSize`，CLI 默认 `pageNo=1`、`pageSize=10`。不要与其它接口的 `pageNum` 混用。

## 处理链

1. `contract.type.tree` 拿全部合同类型（含收支类型、适用部门）。
2. `contract.template.tree` 拿模板分类树，取目标分类的 `belongId`。
3. `contract.template.list` 传运行时拿到的 `belongId` / `contractType` 列出模板；默认小页，用户要全量时再翻页。
4. `contract.template.detail` 传模板 `id` 看详情。

## 调用示例

Windows PowerShell：

```powershell
weaver-work-cli --json contract run contract.type.tree
weaver-work-cli --json contract run contract.template.tree --input-json '{"treeName":"采购合同"}'
weaver-work-cli --json contract run contract.template.list --input-json '{"belongId":"12345","pageNo":1,"pageSize":10}'
weaver-work-cli --json contract run contract.template.detail --input-json '{"id":"67890"}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.type.tree
weaver-work-cli --json contract run contract.template.tree --input-json '{"treeName":"采购合同"}'
weaver-work-cli --json contract run contract.template.list --input-json '{"belongId":"12345","pageNo":1,"pageSize":10}'
weaver-work-cli --json contract run contract.template.detail --input-json '{"id":"67890"}'
```

## 结果解读

- `/api/ebd/**` 的成功码是顶层 `code = 0`；`code != 0` 时 CLI 抛 `api/business_error` 并带相对路径与脱敏参数摘要。
- 展示模板候选时给名称、状态和推荐理由；**不要伪造"智能评分"**。
- 列表为空时说明"当前分类下没有模板"，不要改用其它接口轮询。
- 分类 ID 与模板 ID 均为环境相关字符串，必须来自上一步运行时结果。

## 注意

- 不要凭模板名称猜测 `id`；`contract.template.detail` 的 `id` 必须来自列表或分类树的返回。
- 用户只问"有哪些模板"时不要直接拉全量，先取小页并说明是否还有更多。
