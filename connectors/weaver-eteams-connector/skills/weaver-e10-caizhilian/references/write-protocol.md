# 采知连写操作确认协议（prepare → apply）

## 何时使用

- 要执行任何**会产生服务端副作用**的操作：创建/修改文档、替换正文、改作者、文件夹创建、权限与默认共享增删改、标签增删、参与人增删、共享增删、附件上传替换、封面设置移除、比对文件上传与提交。
- 收到 `confirmation/required` 或任何 `continuation_*` / `plan_changed` 报错，需要判断下一步。
- 写操作结果不确定（超时、连接中断、返回结构异常），需要决定「查一次还是重放」。

## 输入要点

### 四步链路

1. **只读定位**：先用查询类操作拿到真实 ID 与合法枚举值（`document.search` / `document.get` / `folder.query-by-name` / `*.form` / `*.list` / `org.search-*`）。ID 一律不要猜。
2. **prepare**：`weaver-work-cli --json caizhilian run <name>.prepare --input-json '<json>'`。这一步**不产生副作用**，只做只读回查、组装请求体、计算指纹，并签发 `continuation`。
3. **向用户摘要并取得明确确认**：必须写清「对哪个对象（名称 + ID）、做什么、影响范围、是否可撤销」。涉及本地文件时还要写清文件路径、文件名、大小。用户没有明确同意，不得进入第 4 步。
4. **apply**：`weaver-work-cli --json caizhilian run <name>.apply --input-json '<与 prepare 完全相同的 json>' --continuation TOKEN --yes`。`--yes` 会注入 `confirm: true`，`--continuation` 注入票据。

### 票据（continuation）约束

- 有效期 **10 分钟**（`expires_in_ms`），过期报 `continuation_expired`，必须重新 prepare。
- 票据里绑定了 **baseUrl + 登录账号**：换环境或换账号后复用会报 `continuation_context_mismatch`。
- 票据绑定 **目标 apply 操作名**：把 A 操作的票据用于 B 操作报 `continuation_mismatch`。
- 票据里存了 prepare 时的**入参指纹**（排除 `confirm` / `continuation`）：apply 入参与 prepare 不一致报 `continuation_args_changed`；关键字段（如 `doc_id`）单独漂移报 `continuation_target_changed`。
- 票据里还存了**请求体指纹**与（文件类）**文件 MD5 + 大小**：表单级联结果变化报 `plan_changed`，本地文件被改动报 `file_changed`。
- 票据签名校验失败或无法解析报 `continuation_invalid`；缺失报 `continuation_required`；apply 未带 `--yes` 报 `confirmation/required`（`error.type = "confirmation"`）。
- 结论：**apply 的 `--input-json` 必须与 prepare 逐字一致**。要改任何参数，就重新走一遍 prepare，不要「改一个字段再 apply」。

### prepare 返回体

```json
{
  "schemaVersion": 1,
  "ok": true,
  "operation": "caizhilian.folder.create.prepare",
  "data": {
    "request": { "method": "POST", "path": "/api/doc/folder/create", "body": {} },
    "continuation": "TOKEN",
    "expires_in_ms": 600000,
    "hint": "确认无误后调用 caizhilian.folder.create.apply（必须回传本次 continuation 且 confirm=true，CLI 加 --yes）"
  },
  "meta": { "status": "PREPARED", "requiresConfirmation": true, "expires_in_ms": 600000 },
  "warnings": []
}
```

`warnings` 是 prepare 阶段的非阻断提醒（例如共享兜底覆盖了文件夹兜底、参与人已在列表中、待删条目已消失），**必须原样转述给用户**，不要静默丢弃。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json caizhilian run caizhilian.document.create-markdown.prepare --input-json '{"name":"周报","folder_id":"456","folder_type":"company","file_path":"C:\data\weekly.md"}'
weaver-work-cli --json caizhilian run caizhilian.document.create-markdown.apply --input-json '{"name":"周报","folder_id":"456","folder_type":"company","file_path":"C:\data\weekly.md"}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.share.add.prepare --input-json '{"doc_id":"1234567890","obj_type":"resource","share_level":"1","obj_id":["789"]}'
weaver-work-cli --json caizhilian run caizhilian.share.add.apply --input-json '{"doc_id":"1234567890","obj_type":"resource","share_level":"1","obj_id":["789"]}' --continuation TOKEN --yes
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json caizhilian run caizhilian.document.create-markdown.prepare --input-json '{"name":"周报","folder_id":"456","folder_type":"company","file_path":"/tmp/data/weekly.md"}'
weaver-work-cli --json caizhilian run caizhilian.document.create-markdown.apply --input-json '{"name":"周报","folder_id":"456","folder_type":"company","file_path":"/tmp/data/weekly.md"}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.share.add.prepare --input-json '{"doc_id":"1234567890","obj_type":"resource","share_level":"1","obj_id":["789"]}'
weaver-work-cli --json caizhilian run caizhilian.share.add.apply --input-json '{"doc_id":"1234567890","obj_type":"resource","share_level":"1","obj_id":["789"]}' --continuation TOKEN --yes
```

## 输出处理

- prepare 成功：把 `data` 里的请求预览翻译成**人话摘要**（对象、动作、范围、可撤销性），连同 `warnings` 一起给用户，然后等确认。不要把 `continuation` 当业务结果展示，也不要截断或改写它。
- apply 成功：`data` 是服务端返回的业务结果（新文档 ID、新文件夹 ID、上传后的 `file_id`、共享列表等）。摘要关键 ID 与名称，并说明「已生效」。
- apply 失败：按 `error.type` / `error.subtype` 判断。**只要错误发生在请求已发出之后，一律不得自动重放**。
- 多步写入（`cover.set` = 上传 + 改字段、`document.replace-content` = 上传 + 替换 + 通知、`document.create-by-upload` = 批量上传）失败时，先看 `data.summary` 与 `warnings` 判断已完成到哪一步，再决定是否需要人工在 E10 页面复核。

## 写结果不确定的决策树

出现「请求已发出但结果未知」的情形（网络超时、连接被重置、`response_shape` / `empty_response`、进程被中断），按顺序执行：

1. **立即停止**，不要重试同一个 apply，也不要用同一个 `continuation` 再跑一次。
2. **最多做一次只读回查**确认实际状态：
   - 文档创建 → `caizhilian.document.search`（按名称 + `folder_id` + 创建时间）
   - 文档字段/正文/作者 → `caizhilian.document.get`
   - 文件夹 → `caizhilian.folder.query-by-name`
   - 权限/默认共享 → `caizhilian.folder.permission.list` / `caizhilian.folder.default-share.list`
   - 标签/参与人/共享 → `caizhilian.tag.list` / `caizhilian.participant.list` / `caizhilian.share.list`
   - 附件/比对文件 → `caizhilian.compare.list-file-objects`
3. **回查结果二选一**：
   - 已生效 → 告知用户「操作已成功」，不再重放。
   - 未生效 → 告知用户失败原因，**重新 prepare**（拿新票据）后再由用户确认执行；不要复用旧票据。
4. 回查本身也失败 → 停止，把原始错误交给用户，建议在 E10 页面人工核对。

> 说明：`partial/write_uncertain` 是错误分类里保留的「写结果不确定」类型；采知连模块当前把批量与多步写入的部分失败通过 `warnings` + `data.summary` 表达，遇到上述网络类不确定情形时按本节决策树处理。

## 注意

- **绝不允许跳过 prepare 直接 apply**，也不允许由 Agent 自行编造 `continuation`。没有票据就没有写权限。
- `--yes` 只能在**用户已经明确同意**之后使用。用户说「先看看」或没有回应，都等于未确认。
- 删除类操作（`folder.default-share.delete`、`folder.permission.delete`、`share.delete`、`participant.remove`、`tag.remove`、`cover.remove`）**不可撤销**，确认摘要必须列出被删对象的名称与 ID，并明示不可恢复。
- 扩大可见范围的操作（`share.add`、`folder.permission.set-auth` 从 `user` 改成 `true`、`folder.permission.add` 给 `all`）属于**信息暴露面扩大**，必须在摘要里写明「谁会因此看到什么」。
- 一次确认只对一次 apply 有效：票据用过即失效语义上不应复用，重复 apply 同一票据属于误用，需重新 prepare。
- 不要把票据、Cookie、ETEAMSID、Token 写进回复、日志或提交到仓库。

## 失败处理

| error.type / subtype | 含义 | 处理 |
| --- | --- | --- |
| `confirmation/required` | apply 缺 `confirm: true` | 先向用户摘要并取得确认，再加 `--yes` 重跑 apply |
| `validation/continuation_required` | apply 缺 `continuation` | 先跑 prepare 拿票据 |
| `validation/continuation_invalid` | 票据签名校验失败或无法解析 | 重新 prepare；不要修改票据字符串 |
| `validation/continuation_expired` | 超过 10 分钟有效期 | 重新 prepare |
| `validation/continuation_mismatch` | 票据被用于别的 apply 操作 | 用对应操作的 prepare 重新签发 |
| `validation/continuation_context_mismatch` | 环境（baseUrl）或登录账号已变 | 确认目标环境后重新 prepare |
| `validation/continuation_target_changed` | 关键字段（如 `doc_id`）与 prepare 不一致 | 重新 prepare |
| `validation/continuation_args_changed` | 整体入参指纹与 prepare 不一致 | 用与 prepare 完全相同的入参，或重新 prepare |
| `validation/plan_changed` | 组装出的请求体指纹与 prepare 不一致（表单级联结果或服务端状态已变） | 重新 prepare，并把变化告知用户 |
| `validation/file_changed` | prepare 后本地文件 MD5/大小变化 | 与用户确认文件后重新 prepare |
| `authentication/session_expired` | 登录态失效 | 停止，引导重新登录，然后从 prepare 重新开始 |
| `api/business_error` | 服务端业务拒绝 | 原样转述 message；写操作不要重复提交 |
| `network/*`（retryable） | 请求未确认送达 | 按上文决策树：停止 → 一次只读回查 → 必要时重新 prepare |
| `partial/write_uncertain` | 写结果不确定 | 同上决策树，禁止自动重放 |