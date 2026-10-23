# 条款查询与推荐

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


用途：按标签、分类或关键词查找合同条款，供用户挑选。五个 operation 全部为 `read`。

## operation 与接口

| operation | 方法 | 路径 | 关键输入 |
|---|---|---|---|
| `contract.clause.tags` | GET | `/api/ebd/contract/clauseinfo/getClausesConfig` | `label`、`value`、`pageNum`、`pageSize` |
| `contract.clause.tree` | GET | `/api/ebd/contract/tree/queryList` | 无（无需传参） |
| `contract.clause.search` | GET | `/api/ebd/contract/clauseinfo/getClauses` | `id`、`title`、`tagId`、`content`、`group`、`mark`、`pageNum`、`pageSize` |
| `contract.clause.list` | GET | `/api/ebd/contract/clauseinfo/getListPage` | `belongId`、`clauseName`、`clauseNum`、`clauseStatus`、`clauseGroup`、`contractType`、`pageNo`、`pageSize` |
| `contract.clause.group.list` | GET | `/api/ebd/contract/clausegroup/getListPage` | `belongId`、`clauseName`、`clauseNum`、`clauseStatus`、`contractType`、`pageNo`、`pageSize` |

分页参数命名差异（源资料原文，不要统一）：
- `contract.clause.list` / `contract.clause.group.list` 用 `pageNo`（默认 1）+ `pageSize`（默认 10）。
- `contract.clause.search` / `contract.clause.tags` 用 `pageNum`（默认 **0**）+ `pageSize`（默认 10）。

## 处理链

1. `contract.clause.tags` 是**语义匹配的关键前置接口**，先拿 `tagId`。
2. `contract.clause.tree` 拿条款分类树，取 `belongId`。
3. `contract.clause.search` 是核心查询接口，传 `tagId`、`title` 或 `content`。
4. 需要按分类浏览时用 `contract.clause.list`；需要按条款组浏览时用 `contract.clause.group.list`。

## 调用示例

Windows PowerShell：

```powershell
weaver-work-cli --json contract run contract.clause.tags --input-json '{"pageNum":0,"pageSize":10}'
weaver-work-cli --json contract run contract.clause.tree
weaver-work-cli --json contract run contract.clause.search --input-json '{"tagId":"12345","title":"违约金","pageNum":0,"pageSize":10}'
weaver-work-cli --json contract run contract.clause.list --input-json '{"belongId":"12345","pageNo":1,"pageSize":10}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.clause.tags --input-json '{"pageNum":0,"pageSize":10}'
weaver-work-cli --json contract run contract.clause.tree
weaver-work-cli --json contract run contract.clause.search --input-json '{"tagId":"12345","title":"违约金","pageNum":0,"pageSize":10}'
weaver-work-cli --json contract run contract.clause.list --input-json '{"belongId":"12345","pageNo":1,"pageSize":10}'
```

## 结果解读

- 成功码为顶层 `code = 0`。
- 展示候选时给条款名称、状态和推荐理由；**不伪造"智能评分"**。
- 命中多条时先展示候选请用户选择，不要把第一条当成唯一答案。
- 标签 ID、分类 ID、条款 ID 均为环境相关字符串，必须运行时解析。

## 注意

- 只做查询和推荐，不写入。要把条款真正插入合同文档，必须先走 [`contract-clause-reference-save.md`](contract-clause-reference-save.md) 的确认链。
- 推荐前先用 `contract.clause.reference.get` 查已引用条款，避免推荐用户已经插入过的条款。
