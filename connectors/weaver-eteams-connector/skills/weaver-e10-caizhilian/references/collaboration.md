# 采知连文档协作：标签、参与人、共享

## 何时使用

- 用户要给文档打标签、去掉标签，或问「这篇文档有哪些标签」。
- 用户要加/移除文档参与人，或问「谁能看这篇文档」。
- 用户要把文档共享给某人/某部门/某角色/某客户，或取消共享。

## 输入要点

### 标签（tag）

| operation | 必填 | 关键可选 |
| --- | --- | --- |
| `caizhilian.tag.search` | `type`（`0`=公共标签，`1`=个人标签） | `name`（关键词）、`page_no`、`page_size`（默认 50） |
| `caizhilian.tag.list` | `doc_id` | 无 |
| `caizhilian.tag.add` | `doc_id`、`tags` | 无 |
| `caizhilian.tag.remove` | `doc_id`、`tags` | 无 |

- `tags` 是对象数组，元素形如 `{"id":"1","privacy":false}`：`id` 非空才算有效项，`privacy=true` 走个人标签组（`type=1`），`false` 走公共标签组（`type=0`），空组自动跳过。
- 过滤后没有任何有效标签时报 `validation/field_invalid`（message：`tags 中无有效标签`）。
- `tag.search` 在 `type=0` 时自动限定 `tagModules=["document"]`；返回项已归一为 `{ id, name, privacy }`，可直接作为 `tag.add` 的入参元素。
- `tag.list` 会把公共标签与个人标签两次查询结果合并返回 `{ tags: [{ id, name, privacy }] }`。
- **选择类参数必须让用户拍板**：用户只说「加个标签」时，先 `tag.search` 列出候选（标签名 + 公共/个人），用户选定后再 `tag.add`；用户只说「把张三加进来」时，先用 `org.search-user` 定位（同名时列出来让用户选），确认目标后再 `participant.add`。禁止自行从候选里挑一个、禁止编造 ID。

### 参与人（participant）

| operation | 必填 | 说明 |
| --- | --- | --- |
| `caizhilian.participant.list` | `doc_id` | 返回 `{ participants: [{ share_entry_id, user_id, user_name, can_delete }] }` |
| `caizhilian.participant.add` | `doc_id`、`user_id` | 一次加一个人；`user_id` 用 `caizhilian.org.search-user` 查 |
| `caizhilian.participant.remove` | `share_entry_id`、`doc_id` | 必须传 `participant.list` 返回的 `share_entry_id`，不是 `user_id` |

- `participant.add/remove` 的 prepare 会额外做一次**只读回查**（源脚本没有这一步）：已在列表中 / 找不到目标条目时写进 `warnings`，但**不阻断**，apply 仍按源行为提交。回查本身失败也只降级为告警。
- `participant.add.apply` 返回 `{ share_entry_id, doc_id, user_id, user_name }`；返回的参与人列表为空时报 `validation/empty_response`。

### 共享（share）

| operation | 必填 | 关键可选 |
| --- | --- | --- |
| `caizhilian.share.form` | `doc_id` | 无（返回 `obj_types` 与 `param_options`） |
| `caizhilian.share.list` | `doc_id` | 无（返回 `add_visible` 与 `shares[]`，每条含 `id`、`object_name`、`download`、`can_delete`） |
| `caizhilian.share.add` | `doc_id`、`obj_type`、`share_level` | 11 个 `obj_id*` 数组 + `download`、`department_attribute`、`role_level`、`position_level`、`position_attribute`、`virtualCompany`、`createrPositionLevel` |
| `caizhilian.share.delete` | `doc_id`、`ids` | 无 |

- `obj_type` 取 `share.form` 返回的 `obj_types[].id`（如 `resource`、`department`、`subcompany`、`role`、`group`、`external`、`customer`、`customer_type`、`position`），CLI 会按源的映射表自动补 `targetType`。
- `obj_id*` 字段传数组或单个字符串都可以（单值会被包成 `[值]`），第一个非空值会作为 `targetId`。
- `share_level != "1"` 且没传 `download` 时，CLI 按源行为自动补 `download: ["download"]`（即允许下载），确认摘要里必须写明这一点。
- `share.delete` 的 prepare 会先回读共享列表做存在性与 `can_delete` 校验：条目不存在报 `validation/share_not_found`，不可删除报 `validation/share_not_deletable`（message 用条目名称）。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json caizhilian run caizhilian.tag.search --input-json '{"type":0,"name":"合同","page_size":20}'
weaver-work-cli --json caizhilian run caizhilian.tag.list --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.tag.add.prepare --input-json '{"doc_id":"1234567890","tags":[{"id":"11","privacy":false}]}'
weaver-work-cli --json caizhilian run caizhilian.tag.add.apply --input-json '{"doc_id":"1234567890","tags":[{"id":"11","privacy":false}]}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.participant.list --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.share.form --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.share.add.prepare --input-json '{"doc_id":"1234567890","obj_type":"resource","share_level":"1","obj_id":["789"]}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json caizhilian run caizhilian.tag.search --input-json '{"type":0,"name":"合同","page_size":20}'
weaver-work-cli --json caizhilian run caizhilian.tag.list --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.tag.add.prepare --input-json '{"doc_id":"1234567890","tags":[{"id":"11","privacy":false}]}'
weaver-work-cli --json caizhilian run caizhilian.tag.add.apply --input-json '{"doc_id":"1234567890","tags":[{"id":"11","privacy":false}]}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.participant.list --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.share.form --input-json '{"doc_id":"1234567890"}'
weaver-work-cli --json caizhilian run caizhilian.share.add.prepare --input-json '{"doc_id":"1234567890","obj_type":"resource","share_level":"1","obj_id":["789"]}'
```

## 输出处理

- `tag.search` / `tag.list` 返回归一后的 `{ id, name, privacy }`，回复时只展示标签名，`id` 留给后续 `tag.add` / `tag.remove`。
- `tag.add.apply` / `tag.remove.apply` 返回 `{ doc_id, tag_ids, count }`；标签是**批量两次请求**（公共组 + 个人组），部分组失败会抛错，此时不要自动重放，先用 `tag.list` 回查实际结果。
- `participant.list` 返回 `{ participants[] }`，每项含 `share_entry_id`、`user_id`、`user_name`、`can_delete`；`participant.add.apply` 返回 `{ share_entry_id, doc_id, user_id, user_name }`，`participant.remove.apply` 返回 `{ share_entry_id, doc_id }`。
- `share.list` → `{ add_visible, shares[] }`，条目含 `id`、`object_type`、`object_name`、`share_level`、`sec_level`、`download`、`can_delete`；`share.delete.apply` 返回 `{ deleted: true, shares[] }`。
- `share.form` → `{ obj_types[], param_options }`，`obj_types[].id` 是 `obj_type` 的合法取值。
- `participant.list` / `share.list` 默认用 Markdown 表格摘要（姓名/类型/是否可下载/是否可删除），条目 ID 只作为入参。
- `share.add.apply` 有两种成功形态：`{ added: true, shares: [...] }`（新增成功并回读列表）与 `{ added: false, message: "..." }`（服务端判定「已存在」，源用 `code=500 + status=true` 表达）。`added:false` 不是失败，必须把 message 转述给用户；其他业务失败会抛 `api/business_error`。
- `share.add.apply` 成功后回读共享列表失败时仍算成功，只是 `shares` 为空数组——这种情况要提示用户稍后自行复核。
- 所有 prepare 返回 `continuation` + `expires_in_ms` + `hint`，`meta.status = "PREPARED"`。

## 注意

- 共享与参与人直接决定文档可见范围，属于**扩大信息暴露面**的写操作：确认摘要必须写明「哪篇文档（标题 + doc_id）、共享给谁、什么级别、是否允许下载」。
- `share_level` 的语义由服务端表单决定，不要凭字面猜测；不确定时先 `share.form` 查 `param_options`。
- 移除参与人 / 删除共享会立刻收回访问权，且不可撤销；必须先 `list` 再 prepare，并在确认摘要里列出被移除对象的名称。
- 标签写操作只改标签关联，不改文档正文，但仍走 prepare/apply 确认链，不要跳过。
- 不要把 `participant.remove` 的 `share_entry_id` 与 `user_id` 混用。

## 失败处理

| error.subtype | 触发场景 | 处理 |
| --- | --- | --- |
| `field_required` / `field_empty` | `doc_id` / `user_id` / `obj_type` / `share_level` / `ids` 为空 | 补齐后重试一次 |
| `field_invalid` | `tags` 中没有有效标签 | 先用 `tag.search` 拿真实 `id` |
| `number_invalid` / `enum_invalid` | `type` 不是整数或不是 0/1 | 只传 `0` 或 `1` |
| `doc_no_add_share_permission` | 当前账号没有该文档的共享权限 | 转述给用户，不要重试 |
| `obj_type_not_supported` | `obj_type` 不在映射表内 | 用 `share.form` 的 `obj_types[].id` |
| `share_not_deletable` | 条目无删除权限（受文档或文件夹权限设置限制，重试不会改变结果） | **直接告知用户无删除权限即可**，不要重试、不要等待后再试、不要建议替代做法 |
| `share_not_found` | 待删条目已不存在（可能已被删除） | 重新查询共享列表，把最新情况告知用户 |
| `entries_not_found` | 批量删除里有条目已消失 | 重新 `list` 后再 prepare |
| `empty_response` / `response_shape` | 服务端返回结构与预期不符 | 停止，把原始 message 交给用户，不要重放写请求 |
| `plan_changed` | prepare 与 apply 之间请求体指纹变化（表单级联或共享条目已变） | 重新 prepare |
| `continuation_*` | 票据缺失/过期/串用/入参漂移 | 见 `write-protocol.md` |
| `partial/write_uncertain` | 写结果不确定 | 立即停止，最多补一次 `tag.list` / `participant.list` / `share.list` 只读回查 |