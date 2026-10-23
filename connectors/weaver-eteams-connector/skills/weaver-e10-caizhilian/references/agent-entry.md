# 采知连 CLI 入口与调用约定

## 何时使用

- 本轮会话第一次使用采知连能力，需要先确认 operation 名、字段、必填项和风险等级。
- 用户问「采知连能做什么 / 能不能做 X」，需要先查能力目录再回答。
- 入参较复杂（嵌套对象、数组、中文引号），需要落成 UTF-8 文件再用 `--input` 传。
- 需要判断成功/失败 envelope 结构，或需要知道 `warnings`、`meta` 怎么用。

## 输入要点

- 业务调用统一走 `weaver-work-cli --json caizhilian run <operation>`；高频动作有薄包装：`caizhilian search` / `caizhilian get` / `caizhilian health`。
- 简单 JSON 优先 `--input-json '<json>'`；多行或含中文引号的复杂 JSON 先写成 UTF-8 文件再 `--input <path>`；只有确认当前 shell 管道稳定时才用 `--input -`。
- `--input` 与 `--input-json` 不能同时传，否则 `validation/input_conflict`。
- 字段名必须与 `caizhilian schema` 完全一致：多传字段报 `validation/unknown_field`，入参不是对象报 `validation/input_not_object`，出现 `__proto__` / `constructor` / `prototype` 报 `validation/forbidden_key`。
- ID 类字段（`doc_id`、`folder_id`、`user_id` 等）统一是纯数字字符串，**一律用字符串传**（如 `"5818986505368959471"`）：19 位 ID 写成 JSON 数字会在解析阶段被截断，查不到却看不出原因；超出安全整数范围的数字入参直接报 `validation/number_out_of_range`。不是数字报 `validation/id_invalid`。
- 分页统一 `page_no`（1 起）+ `page_size`；`<=0` 报 `validation/number_invalid`。返回的 `has_next` 按「本页条数 >= page_size」判定，不要依赖 `total`。
- 业务入参禁止携带 Cookie、ETEAMSID、Token、Authorization 或任何内部控制字段；认证只通过 `weaver-work-cli auth ...`，CLI 运行时会剥离保留请求头。
- 写操作 `.apply` 额外必须传 `confirm: true`（CLI 用 `--yes`）与 `continuation`（CLI 用 `--continuation <token>`）。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli caizhilian schema
weaver-work-cli caizhilian operations
weaver-work-cli --json caizhilian health
weaver-work-cli --json caizhilian search --keywords "季度报告" --page-size 10
weaver-work-cli --json caizhilian get --doc-id 1234567890
weaver-work-cli --json caizhilian run caizhilian.document.search --input .\search.json
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli caizhilian schema
weaver-work-cli caizhilian operations
weaver-work-cli --json caizhilian health
weaver-work-cli --json caizhilian search --keywords "季度报告" --page-size 10
weaver-work-cli --json caizhilian get --doc-id 1234567890
weaver-work-cli --json caizhilian run caizhilian.document.search --input ./search.json
```

`search.json` 示例：

```json
{ "keywords": "季度报告", "folder_id": "200", "include_sub_folder": true, "page_no": 1, "page_size": 20 }
```

## 输出处理

成功 envelope 写 stdout：

```json
{
  "schemaVersion": 1,
  "ok": true,
  "operation": "caizhilian.document.search",
  "data": { "total": 128, "page_no": 1, "page_size": 10, "has_next": true, "documents": [] },
  "warnings": []
}
```

失败 envelope 写 stderr，并设置非 0 退出码：

```json
{
  "schemaVersion": 1,
  "ok": false,
  "error": { "type": "validation", "subtype": "field_required", "message": "缺少必填参数: doc_id", "retryable": false }
}
```

- `data` 是业务结果；`meta` 只在有上下文时出现（例如 prepare 的 `status: "PREPARED"`、下载的 `doc_id` / `attachment_id`、`health` 的 `profile` / `tenantKey`）。
- `caizhilian health`（`caizhilian.system.health`）返回 `{ environment, healthy, base_url, url, status_code, business_code, diagnosis, elapsed_ms, message? }`：`healthy=false` 时按 `diagnosis` 定位原因（`network_error` / `http_error` / `http_status_mismatch` / `business_code_mismatch` / `request_failed`，多项用逗号连接），`ok` 表示各项正常；未登录时改为报 `authentication/session_unavailable`，先按共享规则完成登录。
- `warnings` 是非阻断提醒（共享兜底被覆盖、只读回查发现差异、批量上传部分失败等），必须原样转述给用户，不要静默丢弃。
- 当前输出层只有完整 JSON，没有 `--jq` / `--format table` / `--page-all`。回复时不要原样贴完整 JSON：先摘要关键字段与条数，列表默认小页（`page_size=10`），需要完整内容时落本地文件再给路径。

## 注意

- `caizhilian schema` 是 operation、字段与风险等级的合约来源；`caizhilian operations` 是按 resource 分组的能力目录，并带 `withheldOperations`（明确不提供的能力与替代命令）。
- 涉及附件、封面图片、正文文件、上传或下载落盘的操作，执行前必须提醒用户：本地文件内容可能被上传到 E10 采知连文档中心或文件服务器，下载内容会写入本地磁盘，且文件内容可能进入大模型上下文；必须等用户明确确认后再执行。
- 本 Skill 不自行发起 HTTP 请求：禁止 curl / fetch / 浏览器自动化直接访问 `/api/doc/**`、`/api/file/**`、`/api/hrm/**`、`/api/crm/**`，禁止读取或复制 CLI runtime 内部的 Cookie、ETEAMSID、Token。
- 查询类 operation 返回空结果只表示「当前条件下没有匹配」：先核对入参（尤其 ID 是否来自真实查询、取值是否在枚举内），再如实把结果告诉用户。**不要改用自己的方式绕行**——逐个对象扫描、按命名规律枚举、自写循环/脚本批量调用等方式都不允许；也不要在回复或结论里断言「某接口不支持某能力」。仍不符合预期就如实报告现象并停下，等用户指示。

## 失败处理

| error.type / subtype | 含义 | Agent 处理 |
| --- | --- | --- |
| `validation/field_required` | 缺必填参数 | 按 message 里的字段名补齐后重试一次 |
| `validation/unknown_field` | 传了 schema 外字段 | 删除该字段，先查 `caizhilian schema` |
| `validation/id_invalid` | ID 不是纯数字 | 用查询类 operation 重新取真实 ID |
| `validation/list_required` / `list_invalid` | 数组必填或非数组 | 修正结构后重试一次 |
| `validation/enum_invalid` | 取值不在枚举内 | 用对应 `*.form` / `schema` 查合法取值 |
| `validation/number_invalid` | 分页等数字非法 | 用正整数重试 |
| `validation/number_out_of_range` | 大整数（ID）用 JSON 数字传入，已超出可精确表示的范围 | 改成字符串传一次；不要原样重试，数字形式已经被截断 |
| `validation/input_invalid` / `input_conflict` / `input_unreadable` | JSON 入参问题 | 修正文件或改用 `--input-json` |
| `validation/operation_unknown` | operation 名写错或未暴露 | 用 `caizhilian operations` 校对，withheld 能力按提示改用框架命令 |
| `authentication/session_unavailable` | 本地无可用登录态 | 按共享规则引导用户登录，禁止猜域名或用示例域名 |
| `authentication/session_expired` | 登录态失效（HTTP 401/302） | 停止重试，引导重新登录后再执行原操作 |
| `network/*` | 网络或协议错误 | `retryable=true` 时最多重试一次，仍失败即停止 |
| `api/http_error` | HTTP 非 2xx | 把 `code` 与 message 交给用户，写操作不要重复提交 |
| `api/business_error` | 业务失败（code != 200） | 原样转述服务端 message，判断是否需要换参数 |
| `confirmation/required` | apply 缺 `confirm` | 先向用户摘要并确认，再加 `--yes` |
| `partial/write_uncertain` | 写结果不确定 | 立即停止，最多补一次只读回查，禁止自动重放 |