# 岗位查询

## 何时使用

按名称/编号查岗位、按岗位 id 取详情（含职务/职级）、按组织/名称/编号批量查岗位时使用。全部为只读操作。

## 输入要点

| operation | 必填 | 说明 |
| --- | --- | --- |
| `hrm.position.query` | 至少一个收敛条件 | 按名称/编号查岗位（快捷搜索名称编号合一；显式 name/code 走高级条件） |
| `hrm.position.detail` | `id` | 按岗位 id 取详情（只读 `type=info`；含**上级岗位名 / 职务序列 / 职务类型 / 职级**；不含全称与所属部门） |
| `hrm.position.list` | 至少一个过滤或 `all=true` | 按组织/名称/编号批量查岗位（岗位地址簿，一次性 + 自动翻页） |

### `hrm.position.query` 关键字段

| 字段 | 说明 |
| --- | --- |
| `keyword` | 快捷搜索关键词，名称与编号合一匹配，**包含**匹配（模糊找岗位只能用这个字段） |
| `name` | 岗位名称（**精确匹配**，不支持模糊） |
| `code` | 岗位编号（精确匹配） |

`keyword` 与 `name`/`code` 互斥：传 `name`/`code` 时走高级条件，否则走快捷搜索。

⚠️ **`name` 是精确匹配，不是包含匹配**（实测：`name:"测试"` → 0 条；`name:"测试组长"` → 命中多条同名岗位）。要模糊找岗位必须先知道完整岗位名，或改用 `keyword`（实测 `keyword:"EBU"` → 1334 条）。

### `hrm.position.list` 关键字段

| 字段 | 说明 |
| --- | --- |
| `org` | 组织 id（限定该组织下岗位） |
| `name` | 岗位名称过滤（**包含**匹配，与 `code` 二选一） |
| `code` | 岗位编号过滤（与 `name` 二选一） |
| `all` | 显式确认全量拉取（无 `org`/`name`/`code` 过滤时必填 `true`） |
| `pageSize` | 分页大小（**上限 100**，见 SKILL.md 分页统一约束；本接口自带自动翻页取全 total，通常无需显式传） |

> `hrm.position.query` **不接受 `pageSize`**（schema 里没有该参数，传了会被忽略，固定按 200 返回）；只有 `hrm.position.list` 支持分页。

## 命令

按名称查岗位：

Windows PowerShell：

```powershell
weaver-work-cli --json hrm run hrm.position.query --input-json '{"name":"示例岗位"}'
```

macOS/Linux（bash/zsh）：

```bash
printf '%s\n' '{"name":"示例岗位"}' | weaver-work-cli --json hrm run hrm.position.query --input -
```

按编号查岗位：

```powershell
weaver-work-cli --json hrm run hrm.position.query --input-json '{"code":"POS001"}'
```

按 id 取岗位详情（含职务/职级）：

```powershell
weaver-work-cli --json hrm run hrm.position.detail --input-json '{"id":"1000000000000000201"}'
```

批量查某组织下岗位：

```powershell
weaver-work-cli --json hrm run hrm.position.list --input-json '{"org":"1000000000000000101"}'
```

按名称批量查岗位：

```powershell
weaver-work-cli --json hrm run hrm.position.list --input-json '{"name":"行政"}'
```

## 输出处理

- `position.query` 返回 `data.rows`（轻量行：`id`/`name`/`code`/`title`/`leaf`）+ `data.total`；每行含派生字段 `link`（岗位卡片链接 `/sp/hrm/positionCard/{id}`），Agent 输出用 `[岗位名](link)` 呈现。
- `position.list` 返回 `data.rows`（结构化行：`id`/`name`/`fullName`/`code`/`parent`/`department`/`userCount`/`partTimeCount`/`cancelStatus`/`jobsetid`）+ `data.total`；每行含 `link`。
- `position.detail` 返回 `data`，业务字段**直接挂在 envelope 的 `data` 下，没有 `data.data` 嵌套**（上游 `getEditOrAddPostForm` 的 `data.data` 已被 CLI 展平上移）。CLI **只透出这些字段**：
  `id` / `name` / `code` / `parentName`（上级岗位名，无则省略）/ `jobsetName`（职务序列名，无则省略）/ `jobsetTypeName`（职务类型名，无则省略）/ `grade`（职级名称数组，无则省略）/ `link`。
  - ⚠️ **不返回 `fullName`（全称）与 `department`（所属部门）**。要看岗位所属部门，改用 `hrm.position.list` 的行字段 `department`；要看全称同样走 `position.list` 的 `fullName`。
- 岗位名/上级岗位名/职务序列名/职务类型名/职级名已转多语言，直接呈现（**全称与所属部门不在 `position.detail` 里**，见上）。

## 注意

- **🔴 无条件禁止全量拉取**：`position.query` 必须带至少一个收敛条件；`position.list` 无 `org`/`name`/`code` 过滤时必须显式 `all=true`，否则 `full_pull_blocked`。
- **批量禁止循环单查**：批量一律走 `position.list` 一次性返回，禁止按 id 逐个调 `position.detail`。
- 两个列表接口返回字段不同：`position.query`（浏览按钮）返回轻量行，`position.list`（岗位地址簿）返回结构化行（含全名/上级/人员数）。
- **`name` 匹配语义两处不同，别混用**：`position.query` 的 `name` 是**精确匹配**，`position.list` 的 `name` 是**包含匹配**。需要模糊查岗位时，`position.query` 走 `keyword`，或改用 `position.list` 的 `name`。
- 岗位 id 是长整型，按字符串传递。
- `cancelStatus`：1=封存 / 0=未封存。

## 失败处理

- `empty_condition`：空条件拉取被拦截，先询问用户补条件。
- `full_pull_blocked`：`position.list` 无过滤，补 `org`/`name`/`code` 或显式 `all=true`。
- `permission_denied`（`code=403`）：HRM 读接口开关未开启，提示用户联系管理员开启。
- 认证类错误：引导用户执行 `weaver-work-cli auth login`。
