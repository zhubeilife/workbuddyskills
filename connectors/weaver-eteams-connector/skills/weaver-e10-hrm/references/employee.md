# 员工查询

## 何时使用

按工号/姓名/手机/邮箱查员工、按人员 id 查当前登录人或任意员工的下属、查部门/分部下成员、按 id 列表批量查人员精简详情、按人员 id 取人员卡片（默认精简、`full` 可回完整）时使用。全部为只读操作。

## 输入要点

| operation | 必填 | 说明 |
| --- | --- | --- |
| `hrm.employee.query` | 至少一个收敛条件 | 按工号/姓名/手机/邮箱/状态分页查询员工；**默认每行只回人员信息（6 键）**，`full: true` 回完整行 |
| `hrm.employee.batch` | `ids` | 按人员 id 列表批量查精简详情（每批 ≤100 自动分批，不含部门/岗位/上级名称） |
| `hrm.employee.detail` | `id` | 按人员 id 取**人员卡片**：默认只回核心业务字段（组织/上级/助理/职称/职级/办公地点等）；`full: true` 才回完整卡片 |
| `hrm.subordinate.mine` | `scope`（默认 all） | 查当前登录人的下属（direct/indirect/all），基于当前会话身份；**默认每行只回 `id`/`name`/`link`**（`full: true` 回完整行） |
| `hrm.subordinate.by-id` | `id`（`scope` 默认 direct） | 按目标人员 id 查直接/间接下属（**无需切换会话**）；所有下属 = direct + indirect 两次并集；**默认每行只回 `id`/`name`/`link`**（`full: true` 回完整行） |
| `hrm.dept.members` | `dept` | 按部门/分部名或 id 查其下直接成员（组织名需唯一）；**默认每行只回 `id`/`name`/`link`**（`full: true` 回完整行） |

### 按组织反查人员（部门/岗位 → 有哪些人）

需要"这个部门/岗位下有哪些人"时，先按下表判断，**不要默认认为 hrm 做不到**：

| 起点 | 支持情况 | 走哪里 |
| --- | --- | --- |
| 部门 / 分部 | ✅ 支持 | `hrm.dept.members`（同模块，`dept` 传名称或 id） |
| 岗位 | ❌ 本技能不支持 | `position.*` 只给 `userCount` 人数，`employee.query` 也不支持按岗位过滤；需跨到聚才林通讯录高级搜索 `ehr.hr.contact.search` + `saCondition` |

⚠️ `hrm.dept.members` 只返回**直属**该组织的成员，**不含子部门人员**（实测：上级部门「基础服务研发部」→ 0 条，其子部门「组织权限组」→ 8 条）。需要连子部门一起取时，只能按组织树逐层调用。

⚠️ 只有**岗位反查**才需要跨到聚才林 `saCondition`。该路径有两个反直觉点，执行前必须先读聚才林技能（`weaver-e10-jucailin`，连接器版为 `weaver-e10-jucailin-connector`）的通讯录高级搜索条件文档：

1. `saCondition` 是完整条件对象，**不会继承便捷字段的"默认在职"**——不写 `personnel_status` 就是不限状态（含离职），与便捷字段默认在职相反；
2. 条件元素漏写算子键/字段键会被服务端**静默忽略**，表现为"有结果但根本没过滤"（例如只给裸 id 不给字段键，会返回全量人员）。

跨模块拿到结果后，**必须**按 [`../SKILL.md`](../SKILL.md) 的「反查人员的能力边界」执行结果自检：先取全量基线 N（`personnel_status: ["all"]`），`total` 等于或接近 N 即判定"条件被吞"，不得直接把该数字回复用户。

### `hrm.employee.query` 关键字段

| 字段 | 说明 |
| --- | --- |
| `keyword` | 查询关键词，自动推断字段：含 `@`→邮箱；11 位纯数字→手机；纯数字或字母开头含数字→工号；其余→姓名（模糊） |
| `username` | 姓名（模糊匹配） |
| `job_num` | 工号（模糊匹配） |
| `mobile` | 手机号（模糊匹配） |
| `email` | 邮箱（模糊匹配） |
| `status` | `["normal"]` 在职（默认）/ `["6"]` 离职。**不能单独使用**，必须搭配其它条件 |
| `current`/`pageSize` | 分页（**pageSize 默认 10、最大 100**，见 SKILL.md 分页统一约束；要更多数据用 `current` 翻页） |

`keyword` 与 `username`/`job_num`/`mobile`/`email` 互斥，显式字段优先。

## 返回字段

### 🔴 三套 id 不要混用（最高频踩坑点）

人员行里可能出现 3 个长得都像 id 的字段，**它们不是一回事**：

| 字段 | 含义 | 用在哪 |
| --- | --- | --- |
| `id` | **人员 id**（驼峰 `userId` 与它同值） | ✅ 唯一该用的：拼卡片链接、`employee.detail`、`employee.batch` 的 `ids`、`subordinate.by-id` 的 `id`、IM 之外的所有人员定位 |
| `userid` | **登录信息 id**（登录账号维度） | 登录账号场景；**不要当人员 id 用** |
| `cid` | **IM 联系人 id**（`employee.batch` 里叫 `imCid`） | IM 聊天 / 在线状态；**不要当人员 id 用** |

> `employee.query` 默认行**只保留人员 `id`**，另两套已被精简掉——正因如此，看到默认行时不存在混用风险；一旦传 `full: true` 就必须自己分清。

### `employee.query` 的行字段

**默认只回人员信息（6 键）**：

| 字段 | 说明 |
| --- | --- |
| `id` | 人员 id（见上表） |
| `name` | 姓名 |
| `department` | 部门名称 |
| `position` | 岗位名称 |
| `statusCode` | 人员状态（`normal` 等） |
| `link` | 人员卡片链接（派生） |

**传 `full: true` 时额外回（+5 键）**：`userid`、`cid`、`mobile`（本接口**恒为空串**）、`departmentId`、`deptLink`。

> 精简后单行约 186B（原 368B，省 49%）。**注意默认行没有工号和手机号**：工号要 `employee.batch`（`jobNum`）或 `full: true`，手机号只有 `employee.batch` 有脱敏值。

## 命令

按姓名查员工：

Windows PowerShell：

```powershell
weaver-work-cli --json hrm run hrm.employee.query --input-json '{"keyword":"张三"}'
```

macOS/Linux（bash/zsh）：

```bash
printf '%s\n' '{"keyword":"张三"}' | weaver-work-cli --json hrm run hrm.employee.query --input -
```

查离职人员（须搭配其它条件）：

```powershell
weaver-work-cli --json hrm run hrm.employee.query --input-json '{"keyword":"李四","status":["6"]}'
```

按 id 列表批量查人员：

```powershell
weaver-work-cli --json hrm run hrm.employee.batch --input-json '{"ids":["1000000000000000001","1000000000000000002"]}'
```

按 id 取人员卡片（**默认精简**，体积约为完整卡片的 1/5）：

```powershell
weaver-work-cli --json hrm run hrm.employee.detail --input-json '{"id":"1000000000000000001"}'
```

仅在确实需要完整卡片（`password`/`last_android`/`hideFieldList`/`setting`/各类 `*_admin` 等登录与管理元数据）时才加 `full`：

```powershell
weaver-work-cli --json hrm run hrm.employee.detail --input-json '{"id":"1000000000000000001","full":true}'
```

查当前登录人的所有下属（默认每行只回 `id`/`name`/`link`）：

```powershell
weaver-work-cli --json hrm run hrm.subordinate.mine --input-json '{"scope":"all"}'
```

查某人的直接下属（无需切换会话；默认每行只回 `id`/`name`/`link`）：

```powershell
weaver-work-cli --json hrm run hrm.subordinate.by-id --input-json '{"id":"1000000000000000001","scope":"direct"}'
```

需要下属的部门/岗位/电话等完整行时加 `full`（**仅当确实要展示这些列时才加**）：

```powershell
weaver-work-cli --json hrm run hrm.subordinate.mine --input-json '{"scope":"all","full":true}'
weaver-work-cli --json hrm run hrm.subordinate.by-id --input-json '{"id":"1000000000000000001","scope":"direct","full":true}'
```

查部门下成员（默认每行只回 `id`/`name`/`link`；要部门/岗位/手机等列时加 `full: true`）：

```powershell
weaver-work-cli --json hrm run hrm.dept.members --input-json '{"dept":"示例部门"}'
weaver-work-cli --json hrm run hrm.dept.members --input-json '{"dept":"示例部门","full":true}'
```

## 输出处理

- 查询类返回 `data.rows`（行数组）+ `data.total` + `meta`（current/pageSize）；批量/下属返回 `data.rows` + `data.total`。
  - ⚠️ **`data.total` 是「本页行数」，不是真实总数**（源码用返回行数当 total）。实测同一个 `job_num:"WS"`：`pageSize=5` → `total=5`、`pageSize=50` → `total=50`、不传 → `total=20`。要真实总数只能按 `current` 逐页翻到 `rows.length < pageSize` 为止。**例外**：`subordinate.by-id` 的 `total` 是真实总数（另有 `data.page.hasNext/totalPages`）。
  - ⚠️ **不传 `pageSize` 时 `meta.pageSize` 会显示 200，但服务端实际只回 20 行**；别用 meta 判断"拿到了多少条"。
- 列表行分两种形态：**默认精简行只有 `link`**（人员卡片链接 `/sp/hrm/profileInfo/{id}`）；**完整行（`employee.query` 传 `full: true`、`dept.members`/下属传 `full: true`）额外有 `deptLink`（部门卡片链接）与 `departmentId`**，这时可同时输出 `[部门名](deptLink)`。两种形态都用 `[姓名](link)` 呈现人名。
- `employee.detail` 的 `data` **本身就是**人员卡片业务字段，并附 `data.id` + `data.link`。**默认只回核心字段**（26 键：`id`/`name`/`username`/`job_num`/`sex`/`avatar`/`personnel_status`/`status`/`type`/`department`/`subcompany`/`organization`/`position`/`jobsetid`/`jobset_level`/`superior`/`other_superior`/`only_superior`/`subordinate`/`assistant`/`mobile`/`email`/`telephone`/`office`/`location`/`active_date`），实测体积 5.3KB → 1.2KB。
  - 精简规则：实体数组（`department`/`subcompany`/`position`/`personnel_status`/`jobsetid`/`jobset_level`/`location`）只留 `{id, name}`；人员数组（`superior`/`other_superior`/`assistant`）只留 `{id, name, statusCode, avatar}`；`avatar` 只留 1 个 `url`（原响应重复给了 7 个等价 URL + `p1..p5`）。
  - 完整卡片（85 个顶层键，含 `password`/`last_android`/`hideFieldList`/`setting`/`formdata`/各类 `*_admin`）需显式传 `full: true`。**默认不要传**：那些是登录/管理元数据，回答业务问题时无用，且会显著撑大上下文。
  - ⚠️ **没有 `data.data` 这一层**：上游 `card/get` 响应里的业务字段位于其 `data.data`，CLI 已把它**展平上移一层**，所以最终 CLI 输出里业务字段**直接挂在 envelope 的 `data` 下**。按 `j.data.data` 取值会得到 `undefined`。
  - CLI envelope 统一为 `{ schemaVersion, ok, operation, data, meta?, warnings }`；判断成功看 `ok=true`（不是 `code`），业务数据只看 `data`。`items`/`groups`/`layout` 等前端表单元数据已丢弃（传 `full: true` 也不会回）。
  - 若要从卡片里取上级：`data.superior` 是数组（元素含 `id`/`name`/`avatar`/`statusCode`），另有 `data.other_superior`、`data.only_superior`、`data.assistant`、`data.subordinate`（布尔，是否带下属）。
- `subordinate.by-id` 返回 `data.rows` + `data.total` + `data.page`（hasNext/totalPages）。
- **三个「人员列表」接口默认精简**：`subordinate.mine` / `subordinate.by-id` / `dept.members` 的每行默认只回 `id` / `name` / `link`（对比原始行：`dept.members` 与 `subordinate.mine` 走 `formatMember` 单行 366B、`by-id` 原始行 960B——其中上游 `superior` 对象一项独占 485B；精简后约 116~120B/行）。要部门/岗位/电话/上级等列时传 `full: true`。
  - 默认行的 `id` 就是人员 id，可直接喂给 `employee.detail`；`link` 用来渲染 `[姓名](link)`。
  - 若回答里确实要展示"某人属于哪个部门/什么岗位"，要么传 `full: true`，要么对感兴趣的人再调 `employee.detail`（默认精简卡片里含 `department`/`position` 的 `{id,name}`）。**不要为了列表好看就默认传 `full: true`**。
  - `employee.query` 默认行也精简了，但**保留人员信息**（`id`/`name`/`department`/`position`/`statusCode`/`link` 6 键，单行 368B → 186B）；它裁掉的是另两套 id（`userid`/`cid`）、恒空的 `mobile`、以及 `departmentId`+`deptLink`。要看这两套 id 或部门卡片链接时传 `full: true`。
- `mobile` 已由 CLI 脱敏（3 位前缀 + `****` + 末 4 位），直接呈现。

## 注意

- **🔴 无条件禁止全量拉取**：`employee.query` 必须带至少一个收敛条件。
- **🔴 `status` 不能单独使用**：必须搭配其它条件，否则 `empty_condition`。
- 在职查询未命中时，CLI 会在 `data.hint` 提示"可能已离职"，Agent 应据此询问用户是否要查离职人员，不要直接答复"查无此人"。
- `employee.batch` 不含部门/岗位/上级**名称**（返回纯字符串），需要这些信息时改用 `employee.query`（列表行）或 `employee.detail`（人员卡片，含组织/上级/助理等；完整卡片需加 `full: true`）。
- `subordinate.by-id` 的 `scope` 两值：`direct`（直接）/`indirect`（间接）；"所有下属"需两次调用并集（无 `all` 接口，实测 404）。
- `subordinate.mine` 返回的是**当前登录人**的下属，查"某人的下属"请用 `subordinate.by-id`。
- 人员 id 是长整型，按字符串传递。
- **代理商查询禁用**：`hrm.employee.dls`（`containsDls=true`）仅泛微自用系统支持，未实现，不得编造或绕过。

## 失败处理

- `empty_condition`：空条件拉取被拦截，先询问用户补条件。
- `enum_invalid`：`status`/`scope` 取值非法。
- `dept_not_found`/`dept_ambiguous`：`dept.members` 组织未找到或重名，改用组织 id。
- `permission_denied`（`code=403`）：HRM 读接口开关未开启，提示用户联系管理员开启，不要盲目重试。
- 认证类错误：引导用户执行 `weaver-work-cli auth login`。
