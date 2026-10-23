# 采知连组织人员浏览器：人员/部门/分部/岗位/角色/客户检索

## 何时使用

- 用户说的是人名、部门名、分部名，但共享、参与人、文件夹权限、作者变更都要 **ID**：先用本 reference 的浏览器检索把名称解析成 ID，再传给写操作。
- 需要确认「当前登录人是谁」（个人知识库 `folder_id=300`、个人标签 `type=1`、创建人过滤 `creator_user_id` 都依赖它）。
- `folder.default-share.form` / `folder.permission.form` / `share.form` 返回的 `obj_types[].id` 指明了要传哪一类对象，用对应的浏览器操作取该类对象的真实 ID。

## 输入要点

8 个浏览器检索操作入参完全一致，全部只读、无写操作：

| operation | 源 operation | 解析对象 | 输出列表键 |
| --- | --- | --- | --- |
| `caizhilian.org.search-user` | `search_user` | 内部人员 | `users[]` |
| `caizhilian.org.search-department` | `search_department` | 部门 | `departments[]` |
| `caizhilian.org.search-subcompany` | `search_subcompany` | 分部/子公司 | `subcompanies[]` |
| `caizhilian.org.search-external` | `search_external` | 外部人员 | `externals[]` |
| `caizhilian.org.search-position` | `search_position` | 岗位 | `positions[]` |
| `caizhilian.org.search-role` | `search_role` | 角色 | `roles[]` |
| `caizhilian.org.search-customer` | `search_customer` | CRM 客户 | `customers[]` |
| `caizhilian.org.search-customer-type` | `search_customer_type` | CRM 客户类型字典 | `customer_types[]` |

公共入参：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `keyword` | 否 | 快搜关键词。源按对象类型用不同的快搜字段（人员 `username`、角色 `role_name`、客户 `customer_name`、其余 `name`），CLI 已封装，调用方只传 `keyword` |
| `page_no` | 否 | 页码，1-indexed，默认 `1` |
| `page_size` | 否 | 每页条数，默认 `50` |

另有 `caizhilian.user.current`（源 `fetch_current_user_info`）：**无入参**，返回 `{ employeeId, employeeName }`。

`keyword` 留空等于「不按名称过滤」，服务端会返回该浏览器的默认首页数据，可用于让用户从列表里挑。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json caizhilian run caizhilian.org.search-user --input-json '{"keyword":"张三","page_size":20}'
weaver-work-cli --json caizhilian run caizhilian.org.search-department --input-json '{"keyword":"财务"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-subcompany --input-json '{"keyword":"上海"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-position --input-json '{"keyword":"经理"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-role --input-json '{"keyword":"文档管理员"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-customer --input-json '{"keyword":"泛微"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-customer-type --input-json '{"keyword":"重点"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-external --input-json '{"keyword":"顾问"}'
weaver-work-cli --json caizhilian run caizhilian.user.current
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json caizhilian run caizhilian.org.search-user --input-json '{"keyword":"张三","page_size":20}'
weaver-work-cli --json caizhilian run caizhilian.org.search-department --input-json '{"keyword":"财务"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-subcompany --input-json '{"keyword":"上海"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-position --input-json '{"keyword":"经理"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-role --input-json '{"keyword":"文档管理员"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-customer --input-json '{"keyword":"泛微"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-customer-type --input-json '{"keyword":"重点"}'
weaver-work-cli --json caizhilian run caizhilian.org.search-external --input-json '{"keyword":"顾问"}'
weaver-work-cli --json caizhilian run caizhilian.user.current
```

## 输出处理

- 统一分页外壳：`{ page_no, page_size, has_next, <列表键>: [...] }`。
- `has_next` 的判定是**本页条数 >= page_size**（源行为；服务端 `total` 不可信，不要用它算总页数）。要翻页就 `page_no + 1` 再查一次，直到 `has_next=false`。
- 各列表元素字段（源 `response_templates` 归一后的结果）：

| 列表键 | 元素字段 |
| --- | --- |
| `users` | `id`、`name`、`department` |
| `departments` | `id`、`name`、`sup_department`（上级部门名）、`parent_id`、`has_sub` |
| `subcompanies` | `id`、`name`、`parent_id`、`sup_department` |
| `externals` | `id`、`name` |
| `positions` | `id`、`name`、`code` |
| `roles` | `id`、`name` |
| `customers` | `id`、`name` |
| `customer_types` | `id`、`name` |

- 回复用户时用 Markdown 表格摘要「名称 + 所属部门/上级 + ID」，**同名必须全部列出让用户选**，不要默认取第一条：同名人员、同名部门在不同分部下非常常见。
- `caizhilian.user.current` 返回 `{ employeeId, employeeName }`，这就是当前登录人的 `user_id`，可直接用于 `document.search` 的 `creator_user_id`、`share.add` 的 `obj_id`、`tag.search` 的个人标签查询。
- 解析出的 ID 一律按**字符串**传递（`obj_id`、`obj_ids`、`creator_user_id`、`user_id` 的 schema 都是 `^\d+$`）。

## 注意

- 本 reference 全是只读检索，不产生服务端副作用，可以放心多查几次；但**不要把整页 50 条原始 JSON 贴给用户**，只摘要前若干条 + 总数提示。
- 浏览器检索结果受当前登录人的数据权限限制：查不到不等于不存在，可能是无权可见。此时应提示用户换一个更精确的关键词，或改由有权限的账号操作，不要反复重试。
- `search-customer` / `search-customer-type` 走 CRM 接口，未启用 CRM 的环境会返回业务错误，转述给用户即可，不要当成「客户不存在」。
- 不要把这些 ID 当成永久有效：组织架构调整后 ID 可能失效，写操作失败提示对象不存在时应重新检索。
- 解析 ID 只是准备步骤；真正的共享/参与人/权限写入仍必须走 `prepare -> apply` 确认链，见 `write-protocol.md`。

## 失败处理

| error.subtype | 触发场景 | 处理 |
| --- | --- | --- |
| `field_empty` / `field_invalid` | `keyword` 传了非字符串 | 改成字符串或整条省略 |
| `number_invalid` | `page_no` / `page_size` 不是正整数 | 用正整数重试一次 |
| `empty_response` / `response_shape` | 服务端返回结构与预期不符 | 停止，把原始 message 交给用户 |
| `session_unavailable` / `session_expired` | 未登录或登录态失效 | 按 `agent-entry.md` 引导重新登录，不要在业务侧猜 |
| `http_error` / `business_error` | 接口返回非成功码 | 转述服务端 message，不要重试写操作 |
| `network` (retryable) | 网络抖动 | 最多重试一次，仍失败则停止并告知用户 |