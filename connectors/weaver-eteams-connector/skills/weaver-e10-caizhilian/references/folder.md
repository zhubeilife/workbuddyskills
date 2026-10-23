# 采知连文件夹：创建、虚拟文件夹、默认共享与权限设置

## 何时使用

- 用户要在公共/个人知识库里建文件夹，或按名称找文件夹 ID。
- 用户要查/改文件夹的默认设置：默认共享人、默认参与人、文档权限（下载、复制、移动、删除、新建文档、新建文件夹、设置）。
- 用户要按权限反查「哪些文件夹对某人/某部门开放了某项权限」。
- 创建文档前需要拿 `folder_id`，或需要确认目标文件夹允许创建的文档类型。

## 输入要点

### 只读查询

| operation | 必填 | 关键可选 |
| --- | --- | --- |
| `caizhilian.folder.query-by-name` | `folder_name` | `kb_type`（`company`/`privy`/`sys`，默认 `company`） |
| `caizhilian.folder.search-virtual` | 无 | `name`、`page_no`、`page_size`（默认 50） |
| `caizhilian.folder.get-settings` | `folder_id` | 无 |
| `caizhilian.folder.list-default-shares` | `folder_id` | 旧名字段 `folderId`（源参数名）仍兼容；与新名同时出现且取值不一致会报 `alias_conflict` |
| `caizhilian.folder.default-share.form` | `folder_id`、`category`（`creator`/`generic`） | 无 |
| `caizhilian.folder.default-share.list` | `folder_id` | 无 |
| `caizhilian.folder.permission.form` | `folder_id`、`permission_type` | 无 |
| `caizhilian.folder.permission.list` | `folder_id`、`permission_type` | 无 |
| `caizhilian.folder.permission.get-auth` | `folder_id`、`permission_type` | 无 |
| `caizhilian.folder.permission.detail` | `folder_id`、`setting_type` | 无 |
| `caizhilian.folder.permission.query` | `folder_ids`（数组） | 无 |
| `caizhilian.folder.query-by-permission` | `permission_key`、`permissions` | `page_no`、`page_size`（默认 20） |

枚举取值（**拼写 1:1 沿用源接口，注意 `Premisstion` 是源的拼写，不要自行改成 `Permission`**）：

- `permission_type`（8 项）：`copyPermission`、`deletePremisstion`、`downloadPremisstion`、`folderDefaultParticipants`、`movePermission`、`newCreateDocPremisstion`、`newCreateFolderPremisstion`、`settingPermission`
- `setting_type`（9 项）：上面 8 项 + `defaultShares`
- `permission_key`（9 项）：上面 8 项，但把 `folderDefaultParticipants` 之外再加 `folderDefaultShareNew`（即 `copyPermission`、`deletePremisstion`、`downloadPremisstion`、`folderDefaultParticipants`、`folderDefaultShareNew`、`movePermission`、`newCreateDocPremisstion`、`newCreateFolderPremisstion`、`settingPermission`）

`query-by-permission` 的 `permissions` 是对象数组，元素形如 `{"object_type":"all"}` 或 `{"object_type":"resource","object_ids":["123"]}`；`object_type` 必填，`object_ids` 必须是正整数字符串。`page_no` / `page_size` 传 `<=0` 会报 `validation/number_invalid`（源脚本是静默归一，这里选择显式报错）。

`object_ids` 必须是**对象的真实 ID**：人员/部门/分部/角色/岗位/客户一律用 `caizhilian.org.search-*` 查出来的 `id`（每个对象都要是字符串，且不要用 JSON 数字传）。**不要用 `default-share.list` / `get-settings` / `permission.list` 返回条目里的 `id`**——那是共享/权限条目的 ID，不是对象 ID，拿它反查只会得到空结果。不带 ID 的对象类型（`all`、`allExternal`、`createrSelf` 等）不传 `object_ids`。

### 写操作

| operation | 必填 | 关键可选 |
| --- | --- | --- |
| `caizhilian.folder.create` | `name`、`parent_id`、`parent_type`（`company`/`privy`） | `sequence`（-9999~99999，默认 0）、`inherit_parent`（默认 false） |
| `caizhilian.folder.default-share.add` | `folder_id`、`obj_type`、`share_level` | 11 个 `obj_id*` 数组 + `download`、`department_attribute`、`role_level`、`position_level`、`position_attribute`、`virtualCompany`、`createrPositionLevel`、`seclevel_min`、`seclevel_max` |
| `caizhilian.folder.default-share.delete` | `folder_id`、`ids` | 无 |
| `caizhilian.folder.permission.add` | `folder_id`、`permission_type`、`obj_type` | `obj_id`、`obj_id_department`、`obj_id_subcompany`、`obj_id_role`、`obj_id_position`、`obj_id_customer`、`obj_id_customer_type`、`department_attribute`、`role_level`、`position_level`、`position_attribute`、`position_level_department`、`position_level_subcompany` |
| `caizhilian.folder.permission.delete` | `folder_id`、`permission_type`、`ids` | 无 |
| `caizhilian.folder.permission.set-auth` | `folder_id`、`permission_type`、`value`（`true`/`user`/`false`） | 无 |
| `caizhilian.folder.permission.sync-setting` | `id`（文件夹 ID）、`keepOldSettingForAllFolders` | 无 |
| `caizhilian.folder.permission.sync-maintain` | `id`（文件夹 ID）、`keepOldSettingForAllFolders` | 无 |
| `caizhilian.folder.permission.sync-download` | `id`（文件夹 ID） | `keepOldSettingForAllFolders`（仅当下载权限为"允许以下人员下载"时必填） |
| `caizhilian.folder.permission.sync-delete` | `id`（文件夹 ID） | `keepOldSettingForAllFolders`（仅当删除权限为"允许以下人员删除文档"时必填） |
| `caizhilian.folder.permission.sync-copy` | `id`（文件夹 ID）、`keepOldSettingForAllFolders` | 无 |
| `caizhilian.folder.permission.sync-create` | `id`（文件夹 ID）、`keepOldSettingForAllFolders` | 无 |
| `caizhilian.folder.permission.sync-move` | `id`（文件夹 ID）、`keepOldSettingForAllFolders` | 无 |
| `caizhilian.folder.permission.sync-participant` | `id`（文件夹 ID）、`sync_to_folder_docs`、`sync_to_all_folders`、`sync_to_all_sub_folder_docs`（至少选一个） | `keep_old_for_folder_docs`、`keep_old_for_all_folders`、`keep_old_for_all_sub_folder_docs`（默认 true） |
| `caizhilian.folder.permission.sync-default-share` | `id`（文件夹 ID）、`sync_to_folder_docs`、`sync_to_all_folders`、`sync_to_all_sub_folder_docs`（至少选一个） | `keep_old_default_share_for_folder_docs`、`keep_old_non_default_share_for_folder_docs`、`keep_old_default_share_for_all_folders`、`keep_old_default_share_for_sub_folder_docs`、`keep_old_non_default_share_for_sub_folder_docs`（默认 true） |

- `folder.create` 的 `parent_type=privy`（个人）时，`sequence` 强制为 `0`、`inherit_parent` 强制为 `false`（源行为）。
- `obj_type` 与 `share_level` 不要猜：先用 `default-share.form` / `permission.form` 拿到 `obj_types[].id` 和级联参数，再决定要传哪些 `obj_id*` 字段；传了 `obj_type` 未配置的对象字段会报 `validation/obj_type_not_configured` 或 `obj_type_not_supported`。
- `download` 在 `share_level != 1` 且未传时默认按 `["download"]` 处理（源行为）。
- `set-auth` 的 `value=user` 表示「按人员白名单」，此时白名单条目由 `permission.list` / `permission.add` 维护；`permission_auth_not_user` 表示当前权限类型不是 `user` 模式，需要先 `set-auth`。

## 命令

Windows PowerShell：

```powershell
weaver-work-cli --json caizhilian run caizhilian.folder.query-by-name --input-json '{"folder_name":"财务","kb_type":"company"}'
weaver-work-cli --json caizhilian run caizhilian.folder.get-settings --input-json '{"folder_id":"456"}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.list --input-json '{"folder_id":"456","permission_type":"downloadPremisstion"}'
weaver-work-cli --json caizhilian run caizhilian.folder.create.prepare --input-json '{"name":"2026 合同","parent_id":"456","parent_type":"company","inherit_parent":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.create.apply --input-json '{"name":"2026 合同","parent_id":"456","parent_type":"company","inherit_parent":true}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.folder.permission.set-auth.prepare --input-json '{"folder_id":"456","permission_type":"downloadPremisstion","value":"user"}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-setting.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-maintain.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-download.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-delete.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-copy.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-create.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-move.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-participant.prepare --input-json '{"id":"456","sync_to_all_folders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-default-share.prepare --input-json '{"id":"456","sync_to_all_folders":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json caizhilian run caizhilian.folder.query-by-name --input-json '{"folder_name":"财务","kb_type":"company"}'
weaver-work-cli --json caizhilian run caizhilian.folder.get-settings --input-json '{"folder_id":"456"}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.list --input-json '{"folder_id":"456","permission_type":"downloadPremisstion"}'
weaver-work-cli --json caizhilian run caizhilian.folder.create.prepare --input-json '{"name":"2026 合同","parent_id":"456","parent_type":"company","inherit_parent":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.create.apply --input-json '{"name":"2026 合同","parent_id":"456","parent_type":"company","inherit_parent":true}' --continuation TOKEN --yes
weaver-work-cli --json caizhilian run caizhilian.folder.permission.set-auth.prepare --input-json '{"folder_id":"456","permission_type":"downloadPremisstion","value":"user"}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-setting.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-maintain.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-download.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-delete.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-copy.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-create.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-move.prepare --input-json '{"id":"456","keepOldSettingForAllFolders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-participant.prepare --input-json '{"id":"456","sync_to_all_folders":true}'
weaver-work-cli --json caizhilian run caizhilian.folder.permission.sync-default-share.prepare --input-json '{"id":"456","sync_to_all_folders":true}'
```

## 输出处理

- `query-by-name` 返回**展平后的路径列表**（源模板 `FlattenSearchResultFolderTree`），每项含文件夹 ID、名称与完整路径；同名文件夹可能出现在多个路径下，必须让用户确认选哪一个，不要默认取第一条。
- `search-virtual` 返回 `{ page_no, page_size, has_next, folders[] }`，每项含 `id`、`name`、`path`、`parent_folder_id`（源 `content` 形如 `名称[路径]`，CLI 已拆开）。
- `get-settings` 返回 `{ defaultVirtualFolder, folderDefaultParticipants, currentFolder, folderDefaultShareNew }`（`currentFolder` 含 `id`/`name`/`title`；参与人每项含 `id`/`content`/`_entityType`，共享对象另含 `canDelete`），创建文档时的兜底来源。
- `folder.create.apply` 返回 `{ folder_id, name, type, parent_id }`，新文件夹 ID 可直接用于后续创建文档。
- 文件夹侧共享/权限条目统一归一为 `{ id, object_type, object_name, share_level, sec_level }`（`sec_level` 空值显示为 `--`）；文档级共享条目（`share.*`）另含 `download`、`can_delete`。
- `list-default-shares` → `{ defaultShares[] }`；`default-share.list` → `{ default_shares[] }`；`permission.list` → `{ add_visible, shares[] }`（`add_visible=false` 时不要再引导用户添加）。删除前必须从列表里取真实条目 `ids`，不要自己拼。
- `default-share.form` → `{ category, obj_types[], param_options }`；`permission.form` → `{ obj_types[], param_options }`。`obj_types[].id` 就是 `obj_type` 的合法取值，`param_options` 给出级联参数。
- `permission.get-auth` 返回 `{ permission_type, current_value }`（`true` / `user` / `false`）。
- `permission.detail` 返回 `{ title, current_setting, list_label, items[] }`；`setting_type=defaultShares` 时只返回 `{ title, items[] }`。
- `permission.query` 返回 `{ permissions }`：以 `folder_id` 为 key 的映射，每个 value 含 `isCreateDoc`、`isCreateFolder`、`canMoveDoc`、`canCopyDoc` 四个布尔标志与 `allowDocumentCreateTypes`（允许创建的文档类型列表，无设置时为空数组）。建文档前可用它确认目标文件夹是否允许创建及允许的文档类型。
- `query-by-permission` 返回 `{ total, page_no, page_size, has_next, folders[] }`，每项含 `folder_id`、`folder_name`、`folder_type`。返回空数组只表示「没有匹配到」：先按上文核对 `object_ids` 是不是对象的真实 ID，再如实把结果告诉用户；**不要据此断定「反查不支持该权限类型」**。返回里没有文件夹路径，需要展示路径时用 `get-settings` 的 `currentFolder.title` 或 `query-by-name` 补。
- 写操作 `apply` 返回结果回显：`default-share.add` → `{ added: true, default_shares }` 或 `{ added: false, message }`（服务端判定「已存在」不是失败，必须把 message 转述给用户）；`default-share.delete` → `{ deleted: true, default_shares }`；`permission.add` → `{ added: true, shares }`；`permission.delete` → `{ deleted: true, shares }`；`permission.set-auth` → `{ permission_type, value, current_value }`；`permission.sync-setting` → `{ existChildFolder }`；`permission.sync-maintain` → `{ existChildFolder }`；`permission.sync-download` → `{ existChildFolder }`；`permission.sync-delete` → `{ existChildFolder }`；`permission.sync-copy` → `{ existChildFolder }`；`permission.sync-create` → `{ existChildFolder }`；`permission.sync-move` → `{ existChildFolder }`；`permission.sync-participant` → `{ existChildFolder, existChildDocument, asyncKey }`；`permission.sync-default-share` → `{ existChildFolder, existChildDocument, asyncKey }`。
- 权限/共享类写操作的 `prepare` 返回请求体预览 + `continuation`；向用户摘要时必须写清「哪个文件夹、哪项权限、给谁、什么级别」，并说明删除类操作不可撤销。
- 列表类结果默认用 Markdown 表格摘要（文件夹名/路径/权限类型/对象/级别），不要原样贴 JSON。

## 注意

- 文件夹权限与默认共享是**影响面很大的配置**：改错会导致整个知识库的下载、复制、新建权限对全员开放或全部收紧。`permission.set-auth` 从 `user` 改成 `true` 等于放开给所有人，确认摘要里必须显式写出这一后果。
- `folder.create` 会在服务端产生新节点；`inherit_parent=true` 会连带继承父文件夹的权限与默认设置，必须在确认摘要里说明。
- 删除类（`default-share.delete` / `permission.delete`）必须先做一次对应 `list` 只读查询，把待删条目的可读信息展示给用户后再 prepare。
- `permission.sync-setting`、`permission.sync-maintain`、`permission.sync-copy`、`permission.sync-create`、`permission.sync-move` 的 `keepOldSettingForAllFolders` 是**必填参数**，必须明确传入 `true`（保留原有设置）或 `false`（不保留），否则会报错。执行前必须提醒用户此操作对系统性能可能有一定影响。
- `permission.sync-participant` 是**异步操作**，支持三种同步范围：同步到当前文件夹内的历史文档（`sync_to_folder_docs`）、同步到所有下级文件夹（`sync_to_all_folders`）、同步到所有下级文件夹内的历史文档（`sync_to_all_sub_folder_docs`），**至少选择一个**。每个选中的范围对应的"原有参与人"参数（`keep_old_for_folder_docs`、`keep_old_for_all_folders`、`keep_old_for_all_sub_folder_docs`）默认为 `true`（保留）。执行后会自动轮询进度，超时时间为 300 秒。
- `permission.sync-default-share` 是**异步操作**，支持三种同步范围：同步到当前文件夹内的历史文档（`sync_to_folder_docs`）、同步到所有下级文件夹（`sync_to_all_folders`）、同步到所有下级文件夹内的历史文档（`sync_to_all_sub_folder_docs`），**至少选择一个**。每个选中的范围对应的"原有默认共享人"和"原有非默认共享人"参数默认为 `true`（保留）。执行后会自动轮询进度，超时时间为 300 秒。
- `permission.sync-download` 的行为取决于当前下载权限设置：当下载权限为"允许所有人下载"或"不允许下载"时，直接同步到所有下级文件夹，不需要 `keepOldSettingForAllFolders` 参数；当下载权限为"允许以下人员下载"时，`keepOldSettingForAllFolders` 是**必填参数**，必须明确传入 `true`（保留原有下载权限设置）或 `false`（不保留）。
- `permission.sync-delete` 的行为取决于当前删除权限设置：当删除权限为"允许完全控制权限人员删除文档"时，直接同步到所有下级文件夹，不需要 `keepOldSettingForAllFolders` 参数；当删除权限为"允许以下人员删除文档"时，`keepOldSettingForAllFolders` 是**必填参数**，必须明确传入 `true`（保留原有删除权限设置）或 `false`（不保留）。
- 本 reference 只覆盖文件夹与权限；文档级共享/参与人/标签见 `collaboration.md`。

## 失败处理

| error.subtype | 触发场景 | 处理 |
| --- | --- | --- |
| `enum_invalid` | `parent_type` / `permission_type` / `setting_type` / `permission_key` / `value` 取值非法 | 按上面的枚举修正，注意源的 `Premisstion` 拼写 |
| `alias_conflict` | 同义的新旧字段（如 `folder_id` 与 `folderId`）同时出现且取值不一致 | 只保留 `folder_id` 后重试，不要两个都传 |
| `folder_no_create_folder_permission` | 目标父文件夹不允许新建文件夹 | 转述给用户，提示需要文件夹管理权限 |
| `permission_fields_required` | `obj_type` 要求的对象字段没传 | 先查 `*.form`，补齐对应 `obj_id*` |
| `obj_type_not_configured` / `obj_type_not_supported` | `obj_type` 未在表单中配置或不被该接口支持 | 用 `form` 返回的 `obj_types[].id` 重新选 |
| `permission_auth_not_user` | 权限类型不是 `user` 模式却维护白名单 | 先 `permission.set-auth` 设为 `user` |
| `entries_not_found` | 待删除的 `ids` 在列表中不存在 | 重新 `list` 后取真实 ID |
| `number_out_of_range` | ID 等大整数用 JSON 数字传入且超出安全整数范围 | 改成字符串重新传，不要原样重试（数字传入时已经被截断） |
| `id_invalid` | `folder_id` / `object_ids` 等不是正整数 | 重新查真实 ID；反查的对象 ID 要来自 `org.search-*`，不是共享条目 ID |
| `range_invalid` / `number_invalid` | `sequence`、`seclevel_min/max`、分页越界 | 按范围修正 |
| `api/business_error` | 服务端业务失败（含权限不足） | 原样转述 message，不要重复提交 |
| `partial/write_uncertain` | 写结果不确定 | 立即停止，最多补一次 `permission.list` / `default-share.list` 只读回查，禁止自动重放 |