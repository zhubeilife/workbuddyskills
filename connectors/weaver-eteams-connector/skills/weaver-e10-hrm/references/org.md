# 组织查询（分部 / 部门）

## 何时使用

按名称/编号/上级组织查分部（subcompany）与部门（department）、按组织节点 id 取详情、按多级路径逐级收敛查询时使用。全部为只读操作。

若用户给的是「**多维名称 + 部门/分部名称**」（例如「1号维度下的第一团队」），**不要**自己先查维度再查组织——直接用 `hrm.org.resolve` 一次调用（见本文末尾「多维解析」）。

## 输入要点

| operation | 必填 | 说明 |
| --- | --- | --- |
| `hrm.org.query` | 至少一个收敛条件 | 按名称/编号/上级组织查询组织（`type` 区分分部/部门） |
| `hrm.org.detail` | `id` | 按组织节点 id 取组织详情（类型由服务端自动判断，含全路径 `fullPath`、上级部门名、所属分部名；**不含人员统计**） |
| `hrm.org.resolve` | `virtual` + `name` | 多维名称 + 部门/分部名称 → 解析组织（精确优先/包含模糊兜底/近似只提示，歧义回候选） |

### `hrm.org.query` 关键字段

| 字段 | 说明 |
| --- | --- |
| `type` | `subcompany` 分部 / `department` 部门；不传默认 `department` |
| `name` | 组织名称（模糊包含匹配） |
| `code` | 组织编号（模糊包含匹配） |
| `parent` | 上级**部门** id 数组（查挂在某部门下的子部门，`department`） |
| `subcompany` | 上级**分部** id 数组（查挂在某分部下的组织，`department`） |
| `supSubDepartment` | 上级**分部** id 数组（查挂在某分部下的分部，`subcompany`） |
| `current`/`pageSize` | 分页（**pageSize 默认 10、最大 100**，见 SKILL.md 分页统一约束；要更多数据用 `current` 翻页） |

> **parent vs subcompany vs supSubDepartment**：`parent` 限定上级部门、`subcompany` 限定上级分部（部门挂在分部下）、`supSubDepartment` 限定上级分部（分部挂在分部下）。三者键名不同，按 `type` 选用，不要混用。

## 命令

按名称查部门：

Windows PowerShell：

```powershell
weaver-work-cli --json hrm run hrm.org.query --input-json '{"name":"示例部门","type":"department"}'
```

macOS/Linux（bash/zsh）：

```bash
printf '%s\n' '{"name":"示例部门","type":"department"}' | weaver-work-cli --json hrm run hrm.org.query --input -
```

按名称查分部：

```powershell
weaver-work-cli --json hrm run hrm.org.query --input-json '{"name":"示例分部","type":"subcompany"}'
```

查某部门下的子部门（drill-down）：

```powershell
weaver-work-cli --json hrm run hrm.org.query --input-json '{"parent":["1000000000000000101"],"type":"department"}'
```

查某分部下的组织：

```powershell
weaver-work-cli --json hrm run hrm.org.query --input-json '{"subcompany":["1000000000000000102"],"type":"department"}'
```

按 id 取组织详情（含全路径与人员统计）：

```powershell
weaver-work-cli --json hrm run hrm.org.detail --input-json '{"id":"1000000000000000101"}'
```

## 多维解析（`hrm.org.resolve`）

> 多维清单（维度名 + id）**不单独暴露成 operation**，全部由 `hrm.org.resolve` 内部获取与处理：匹配时用它、不存在时把 `availableVirtuals` 随结果回给用户。

### 为什么需要它

E10 组织树按**多维**（虚拟组织维度）切分：「行政组织」是真实组织树，其余是各业务维度（「1号维度」「备份维度」…）。**同名部门/分部在不同维度下是不同节点**，浏览接口 `department`/`subcompany` 不带 `companyId` 时会**默认落到「行政组织」维度**（实测：按名称查到的 `virtualid` 全是 `1`）。所以「按名称找部门」必须先定位多维 id，再以 `companyId` 收敛。

这段编排（取维度 → 匹配维度名 → 取多维 id → 带 `companyId` 查组织 → 匹配组织名）**已全部实现在 CLI 内**，Agent **只调一次 `hrm.org.resolve`**，不需要自己分两步推理（也不存在"先列维度再查组织"的第二步可用）。

### 入参

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `virtual` | 首调必填 | 多维名称（如 `行政组织` / `1号维度`）；精确优先，未命中按**包含**模糊匹配 |
| `name` | 首调必填 | 部门或分部名称；精确优先，未命中按**包含**模糊匹配 |
| `type` | 否 | `department` 部门 / `subcompany` 分部；**不传时同时检索两者、按部门优先定位**，并把同名另一类型节点回在 `alsoMatched` |
| `virtualId` | 复调用 | 多维 id（长整型字符串）；用户确认后复调直接传，跳过维度名称匹配 |
| `orgId` | 复调用 | 组织节点 id（长整型字符串）；用户确认后复调直接传，跳过名称匹配（改走组织详情） |
| `maxCandidates` | 否 | 歧义时最多回传的候选条数，**1~200，默认 20**；超限抛 `number_invalid` |

首调至少要有 `virtual` + `name`；只给 `virtualId` + `orgId` 也可以（纯 id 定位）。缺 `virtual`/`virtualId` 抛 `virtual_required`，缺 `name`/`orgId` 抛 `name_required`。

### 匹配规则（两级同名匹配，三级判定）

名称匹配分**三级**，它们的「能否自动往下走」完全不同：

| 级别 | 判定方式 | CLI 行为 |
| --- | --- | --- |
| ① 精确 | 忽略大小写与多余空白的**全等**（服务端条件 `eq`/等于） | 唯一 → 继续；多个 → `ambiguous` |
| ② 包含（模糊） | 名称是关键字**子串**（服务端条件 `in`/包含）；返回行再做一次客户端「忽略大小写全等」优先，兜住服务端 `eq` 漏判（全角/空格差异） | 唯一 → 继续；多个 → `ambiguous` |
| ③ **近似** | 编辑距离阈值内（`相似度 ≥ 0.6`，只认**打字/口误级**差异，如「客服维度」→「客户维度」） | **只回 `suggestions` + `status: not_found`，绝不自动继续** |

- ①② 属于系统收敛，命中即可往下走；③ **绝不参与解析**，只能作为「是不是指这个？」的提示交回用户。
- 维度级：③ 在**本地全量维度清单**上算相似度（`listCompanyVirtual` 一次返回全部）。
- 组织级：③ 用「关键字**末 2 字 / 首 2 字**」各做一次包含查询（≤2 次，中文名后缀信息量最大：经理/部/科/中心…），命中即作为 `suggestions` 回传。
- 未命中且无近似项时，组织级回 `availableVirtuals`（仅维度级）或提示补充关键字。

### 结果契约（🔴 只看 `data.status`，不要只看 `ok`）

三种结果都是 `ok: true`、退出码 `0`：

| `data.status` | 附带字段 | Agent 该做什么 |
| --- | --- | --- |
| `resolved` | `org`（`id`/`name`/`type`/`fullPath`/`parentPath`/`parentId`/`subcompanyId`/`virtualId`/`virtualName`/`link` 等）、`virtual`、`matchType`（`exact`/`fuzzy`/`id`）；不传 `type` 且存在**同名另一类型**节点时另回 `alsoMatched[]` | 直接用 `org` 回答，按 `[名称](link)` 呈现；**有 `alsoMatched` 时必须一并告知用户**（如同一客户下既有同名部门又有同名分部） |
| `ambiguous` | `stage`（`virtual`=多维歧义 / `org`=组织歧义）、`virtual`、`candidates[]`、`candidateTotal`、`truncated`、`message` | **停下问用户**：把 `candidates` 列表（名称 / `fullPath` / link）给用户选，**禁止自动取第一条** |
| `not_found` | `stage`、`virtual`、`suggestions[]`/`suggestionTotal`（近似名称）、`availableVirtuals`（`stage=virtual` 时）、`message` | **原样转述给用户**（含"不存在"这一事实 + 近似名称 + 可用多维），**禁止自行替换名称后重试**；用户确认后再用 `virtualId`/`orgId` 复调 |

- `candidates` 每项为 `{id, name, type, fullPath, code?, link}`；**默认最多 20 条**，`truncated: true` 表示还有更多。`candidateTotal` 是服务端匹配总数（模糊时可能大于所列条数）。
  - 要把候选一次列全：用 `maxCandidates` 复调（1~200），如 `{"virtual":"客户维度","name":"客户经理","maxCandidates":100}` → `candidateTotal: 29, truncated: false`。上游浏览分页会同步放宽到 `max(100, maxCandidates)`，因此上限 200 内都能取全。
- **`suggestions`（`not_found` 才可能出现）**：近似名称，**最多 5 条**；维度级每项 `{id, name}`，组织级每项与 `candidates` 同结构。`suggestionTotal` 为该级近似匹配总数（组织级来自宽松探测）。
  - 🔴 **它只是给用户看的提示，不是给 Agent 用的参数**：不得据此改名重试，也不得因此省略「用户给的名称不存在」这一事实。
  - 实测：`{"virtual":"客服维度","name":"云桥测试"}` → `not_found` + `suggestions: [{id:"100001569000010000", name:"客户维度"}]` + 5 个可用多维；正确回复是「本租户没有『客服维度』，最接近的是『客户维度』，要用它继续查吗？」，而**不是**直接返回客户维度下的结果。
- `fullPath` 含多维名并逐级到本节点（如 `1号维度/超级组织66/第一团队`），同名不同层级靠它区分。
  - ⚠️ **不同租户上游的层级分隔符不一致**（实测：木林泉用 `/`、泛微网络租户的 `supDepartment` 用 `|`）；CLI 已统一归一化为 `/`，所以 `fullPath`/`parentPath` 跨环境格式一致。需要精确定位时用 `id`/`parentId`，不要反解析字符串。
  - 直属多维根节点的候选 `fullPath` 就是名称本身（无上级路径），可用于识别「标准节点 vs 各客户下的同名子节点」。
- **`alsoMatched`（resolved 才可能出现）**：不传 `type` 时，若同一多维下**既有一个同名部门、又有一个同名分部**，本操作不会静默二选一 —— 按部门优先给出 `org`，同时把另一类型节点放进 `alsoMatched`（结构与 `candidates` 相同，含 `id`/`type`/`fullPath`/`link`），并在 `message` 里提示。**Agent 必须把两者都告诉用户**，用户要另一个就用它的 `id` 当 `orgId` 复调（或显式传对应 `type`）。要避免这种双命中，直接在首调传 `type`。

### 用户确认后的复调

把候选的 `id` 作为 `orgId` 传回；若是**多维**歧义（`stage: "virtual"`），把维度的 `id` 作为 `virtualId` 传回：

```powershell
weaver-work-cli --json hrm run hrm.org.resolve --input-json '{"virtual":"1号维度","name":"第一团队","orgId":"9163142909607938"}'
```

`not_found` 时若用户**确认**了 `suggestions` 里的近似名称，同样复调：维度近似 → 传 `virtualId`；组织近似 → 传 `orgId`（或按用户确认后的准确名称重查一次）。**但确认之前绝不能自己走这一步。**

复调一次即定位，**不要再用名称反复重试**。

### 命令示例

首调（多维名称 + 部门名称；分部同理，传 `"type":"subcompany"` 或省略让它自动识别）：

```powershell
weaver-work-cli --json hrm run hrm.org.resolve --input-json '{"virtual":"1号维度","name":"第一团队"}'
```

macOS/Linux（bash/zsh）：

```bash
printf '%s\n' '{"virtual":"1号维度","name":"第一团队"}' | weaver-work-cli --json hrm run hrm.org.resolve --input -
```

多维名不存在时（自动给出近似名称 + 该租户全部多维，不自动继续）：

```powershell
weaver-work-cli --json hrm run hrm.org.resolve --input-json '{"virtual":"客服维度","name":"云桥测试"}'
```

### 注意

- 覆盖关系：`hrm.org.resolve` 是「多维 + 名称」的**一步到位**入口；已有明确收敛条件（编号 `code`、上级组织 id 等）或已知组织 id 时，仍用 `hrm.org.query` / `hrm.org.detail`。
- 多维清单来自 `/api/bs/hrm/companyVirtual/listCompanyVirtual`（一次返回全量，无分页）；`行政组织` 也在清单里（id 为 `1`）。
- 🔴 **「列多维」暂不支持，且不暴露入口**：`hrm.org.virtuals` 已下线（`hrm schema --full` 的 `withheldOperations` 中有声明），Agent 拿不到独立的维度清单接口。
  - `not_found.availableVirtuals` 是**纠错辅助**（用户给的名字对不上时，顺手告知本租户有哪些维度），不是列维度能力——**不要故意构造一个不存在的维度名去套它**。
  - 用户明确问「这个租户有哪些多维」→ 直接回答**暂不支持**，请其改用「维度名 + 组织名」查询。
  - 维度 id 的唯一来源：`not_found.availableVirtuals`（全量）或维度歧义时的 `candidates`。
- 名称匹配不做拼音/别名/简称展开（`shortname` 只回显不参与匹配）。

## 多级路径查询（drill-down 编排）

路径形如 `总部/研发部/产品组`，逐级用「父节点 id 作为上级条件 + 下一段名称」调用 `org.query`：

1. 首段名称查 `org.query`（`name`），得到根节点（看返回 `type` 判断是分部还是部门）。
2. 父为**部门** → `parent=[父部门id]` + 下一段 `name`；父为**分部** → `subcompany=[父分部id]`（查部门）或 `supSubDepartment=[父分部id]`（查分部）+ 下一段 `name`。
3. 逐级收敛至末段；先根→叶，空则叶→根（两者等价）。

## 输出处理

- `org.query` 返回 `data.rows`（组织数组）+ `data.total` + `meta`（current/pageSize）；每行含派生字段 `link`（组织卡片链接 `/sp/hrm/orgCard/{id}`），Agent 输出用 `[组织名](link)` 呈现。
- `org.detail` 返回 `data`，业务字段**直接挂在 envelope 的 `data` 下，没有 `data.data` 嵌套**（上游 `organization/getForm` 的 `data.data` 已被 CLI 展平上移）。CLI **只透出这些字段**：
  `id` / `name` / `type` / `code` / `fullPath`（全路径）/ `status` / `parentName`（上级部门名，无则省略）/ `subcompanyName`（所属分部名，无则省略）/ `description` / `remark`（有值才回）/ `link`。
  - ⚠️ **`parent` / `subcompany` 已由「对象数组」改为 `parentName` / `subcompanyName` 字符串**（只要名字，不要 id/元数据）。
  - 🔴 **`employee_count`（人员统计）不再返回**，本接口也**没有 `full` 开关**。要看某组织有多少人、有哪些人，只能用 `hrm.dept.members`（注意其 `data.total` 是本页行数，且只算直属成员）。
- 名称/全路径 `fullPath` 已转多语言，直接呈现。

## 注意

- **🔴 无条件禁止全量拉取**：`org.query` 必须带至少一个收敛条件。
- 分部与部门是两个不同接口（`browser/data/subcompany` 与 `browser/data/department`），CLI 用 `type` 区分；不传 `type` 默认查部门。
- `org.detail` 详情查询**只需传 `id`**，服务端按记录自动判断分部/部门，无需传 `type`。
- 组织节点 id 是长整型，按字符串传递。
- 浏览按钮行含 `title`（`名称|上级路径`），行上另有 `supDepartment`（部门）/ `supSubDepartment`（分部）给同一信息；本节点全路径由 CLI 合成在 `fullPath`（`上级路径/名称`）。
- `hrm.org.resolve` 的行内字段还含 `virtualid`（所属多维 id）、`subcompanyid`（所属分部 id）、`hasSub`（是否有下级），已投影进 `org`。

## 失败处理

- `empty_condition`：空条件拉取被拦截，先询问用户补条件。
- `enum_invalid`：`type` 取值非法（仅 `subcompany`/`department`）。
- `permission_denied`（`code=403`）：HRM 读接口开关未开启，提示用户联系管理员开启。
- `virtual_required`/`name_required`：`hrm.org.resolve` 少传了多维（`virtual`/`virtualId`）或名称（`name`/`orgId`）。
- **「未找到 / 命中多个」不是错误**：`hrm.org.resolve` 仍 `ok: true`、退出 0，按 `data.status` 分派（`not_found` / `ambiguous`），不要当异常重试。
- 认证类错误：引导用户执行 `weaver-work-cli auth login`。
