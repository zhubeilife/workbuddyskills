---
name: weaver-file-collection
description: "泛微E10采知连文件服务 FTP/SFTP 文件采集技能。用于选择仅采集文件或采集到档案、按需选择全宗、查询或创建 FTP/SFTP 资源、检索并校验已有动作流、动态新建动作流、创建或维护采集任务，以及校验、扫描、运行和查看文件级结果。"
license: Proprietary
compatibility: 泛微E10采知连配套使用，内部可自由使用与修改，禁止对外分发
metadata:
  maintainer: unknown
  type: capability
  version: 1.0.0
  updated: 2026-08-19
  tags: [文件采集, FTP, SFTP, 动作流, 采集任务, 全宗, 档案]
---

# 文件采集 FTP/SFTP

本 Skill 通过 `scripts/collection_cli_tool.py` 管理文件采集生命周期。正式 API 请求、动作流设计物化和任务 Payload 均由脚本生成，不手写正式结构。

## 前置依赖

### 认证前置（必须）

本模块通过 CLI 托管的认证获取凭证（base_url + Cookie + eteamsid + User-Agent），凭证契约见共享规则 [`../../weaver-e10-shared/SKILL.md`](../../weaver-e10-shared/SKILL.md)，不依赖手动配置文件，Agent 不得自己读取或输出凭证。

**使用前必须确保**：
1. CLI 已安装：`weaver-work-cli --version` 能正常输出版本号
2. 已完成登录：`weaver-work-cli auth status` 显示已登录

**首次登录**：
```text
# OAuth2.0 浏览器授权（推荐）
weaver-work-cli auth login

# 或手动写入 ETEAMSID（从浏览器 DevTools 复制）
weaver-work-cli auth set --eteamsid "PCACCOUNT_xxx"
```

**凭证过期处理**：操作返回认证错误时，提示用户通过 `weaver-work-cli auth login` 或 `weaver-work-cli auth set` 重新登录。

## First Move

1. 读取 `rule-index.md`。
2. 确认 CLI 已完成登录（`weaver-work-cli auth status` 显示已登录）。
3. 任务分支和阶段门禁读取 `task-workflow.md`。
4. 动作流检索、检测与动态创建读取 `action-flow.md`。
5. 只有用户选择采集到档案时，才读取 `fonds-selection.md`。
6. 宿主执行还必须读取 `host-executor-prompt.md` 和 `host-platform-integration.md`。

## Hard Rules

- 认证凭证统一由 CLI 托管（`weaver-work-cli auth ...`）；不得写死域名或输出 Cookie。
- `init-session` 后先执行 `choose-file-only` 或 `choose-archive`。仅归档分支查询和确认全宗；仅文件分支不得要求或写入 `fondsId`。
- 新建任务前选择已有或新建 FTP/SFTP 资源，再选择已有或新建动作流。
- 新建任务时先确定是否维持原目录结构；该值必须原样传给动作流 inspect/create 和 `save-task`。维持模式使用动态 `folderId` 动作流，非维持模式使用固定目录动作流，二者不得混用。
- `search-action-flows` 的候选仅用于展示。用户确认 ID 后必须执行 `inspect-action-flow`，回读应用、活动版本和设计并通过兼容性检测，才能生成关联凭据。
- `create-action-flow` 使用 `file_collection_action_flow_design.v1` 动态创建；禁止上传、迁入或依赖固定动作流包。
- 标准 `create-action-flow` 由 CLI 生成仅文件/归档两种完整草稿；普通执行不得让 Agent 手写触发字段或设计文件，`--design-file` 仅用于明确的高级定制。
- 标准 `create-ftp-resource` 在未传 `systemPk` 时自动生成连接器元数据并创建 FTP 连接器；不得通过失败重试发现确定性参数。
- 初始化后的命令携带同一 `chatId`；阶段会原子保存，重复初始化恢复进度，只有显式 `--restart` 才重新开始。
- `save-task` 和 `update-task-workflow` 只接受 `inspect-action-flow` 或 `create-action-flow` 生成的 `file_collection_workflow_selection.v1` 文件。归档凭据还必须绑定归档兼容检测，并携带已确认全宗。
- 默认任务名按 UTC+8 生成 `文件采集（yyyyMMdd HHmmss）`。
- `scan` 默认增量；只有用户明确要求全量时使用 `--full-coll`。
- `run` 只证明启动。只有 `file_collection_result.v1` 为 `collection_succeeded`、`file_collection_ok=true` 且失败数为 0，才能报告采集成功。
- 用户可见输出不展示长 ID、完整 Cookie、明文 FTP 密码或大段请求体。

## Workflow

1. 确认 CLI 已完成登录（`weaver-work-cli auth status`），然后执行 init-session --chat-id <chatId>。
2. 执行 `choose-file-only --phase collection_target_selection`；或执行 `choose-archive`，再调用全宗工具、`normalize-fonds` 和 `confirm-fonds`。
3. 执行 `choose-new-task` 或 `choose-existing-task`。已有任务的全宗更新仅适用于归档分支。
4. 新建任务时执行 `choose-existing-resource` 或 `create-new-resource`；标准新建直接调用 `create-ftp-resource`，缺少 `systemPk` 时 CLI 内部创建连接器并返回 `taskSourceId`。
5. 确定 `retainDirStruct=0|1`；执行 `choose-existing-workflow` 后 `search-action-flows`、用户确认、`inspect-action-flow --retain-dir-struct <0|1>`；或执行 `create-new-workflow` 后直接调用标准 `create-action-flow --retain-dir-struct <0|1> [--archive]`。
6. 用相同目录选项和关联凭据执行 `save-task --retain-dir-struct <0|1> --source-id ... --workflow-selection-file ...`；归档分支额外传全宗确认文件。
7. 依次执行 `check-storage`、`scan --wait`、`run`；需要等待文件级结果时使用 `run --wait` 或 `run-progress`。

## References

| Need | Read |
| --- | --- |
| 规则与 owner | `rule-index.md` |
| 认证 | `auth-and-session.md` |
| 主流程 | `task-workflow.md` |
| 动作流合同 | `action-flow.md` |
| 可选全宗 | `fonds-selection.md` |
| API 路由 | `api_docs.md` |
| API 端点 | `api-endpoints.md` |
| Payload | `api-payloads.md` |
| 宿主提示词 | `host-executor-prompt.md` |
| 宿主集成 | `host-platform-integration.md` |

# API Endpoints

## Connector And Resource

| Operation | Method | Path |
| --- | --- | --- |
| Save connector | POST | `/api/bs/esb/setting/systemPool/save` |
| Query connectors | GET | `/api/bs/esb/setting/connector/getConnectorListPage` |
| Query resources | GET | `/api/bs/esb/setting/resource/getResourceListPage` |
| Save FTP/SFTP resource | POST | `/api/bs/esb/setting/resource/ftp/save` |

The selected resource `id` becomes `taskSourceId`.

## Action Flow

| Operation | Method | Path |
| --- | --- | --- |
| Search applications | POST | `/api/bs/esb/setting/application/getApplicationListPage` |
| Read application | GET | `/api/bs/esb/setting/application/getAppById/{appId}` |
| Read versions | GET | `/api/bs/esb/setting/application/version/versionList/{appId}` |
| Read design | GET | `/api/bs/esb/setting/flow/design/getDesignBySceneId/{sceneId}` |
| Create application | POST | `/api/bs/esb/setting/application/save` |
| Register optional variable | POST | `/api/bs/esb/setting/application/variable/addVariable` |
| Check design | POST | `/api/bs/esb/setting/flow/design/check` |
| Save design | POST | `/api/bs/esb/setting/flow/design/saveDesign` |
| Enable application | GET | `/api/bs/esb/setting/application/startUseApp/{appId}` |

Search results are not association credentials. Inspect or create must complete full read-back validation.

## File Collection Task

| Operation | Method | Path | Result |
| --- | --- | --- | --- |
| List tasks | GET | `/api/file/coll/taskTable` | candidates |
| Read form | GET | `/api/file/coll/taskForm` | task form |
| Save task | POST | `/api/file/coll/save` | task ID |
| Save as | POST | `/api/file/coll/saveAs` | copied task |
| Check storage | GET | `/api/file/coll/checkStorageConnect` | connection result |
| Scan | POST | `/api/file/coll/scan` | runtime ID |
| Scan progress | GET | `/api/file/coll/scan/progress` | scan state |
| Run or pause | POST | `/api/file/coll/run` | accepted state |
| Run progress | GET | `/api/file/coll/run/progress` | execution state |
| Detail | GET | `/api/file/coll/detailTable` | successful or failed rows |
| Cancel | POST | `/api/file/coll/cancel` | cancelled task |
| Delete | POST | `/api/file/coll/delete` | boolean result |

`scan` is 默认增量 and sends `fullColl=false`; `--full-coll` is explicit. `finish=true` is not file success. Read `detailType=true` and `detailType=false`, then normalize `file_collection_result.v1`.

## CLI 操作

### 新建采集任务

使用 `caizhilian.file-collection.task.save.prepare/apply` 创建新的采集任务：

**参数**：
- `source_id`（必填）：FTP/SFTP 资源 ID
- `workflow_id`（必填）：动作流 ID
- `task_name`（可选）：任务名称，不传时自动生成
- `retain_dir_struct`（可选）：是否维持原目录结构，默认 true
- `task_file_path`（可选）：采集路径，默认 /

**示例**：

Windows PowerShell：
```powershell
weaver-work-cli --json caizhilian run caizhilian.file-collection.task.save.prepare --input-json '{"source_id":"123","workflow_id":"456","task_name":"测试采集任务"}'
```

macOS/Linux（bash/zsh）：
```bash
weaver-work-cli --json caizhilian run caizhilian.file-collection.task.save.prepare --input-json '{"source_id":"123","workflow_id":"456","task_name":"测试采集任务"}'
```

### 其他操作

| 操作 | CLI 命令 |
| --- | --- |
| 列出任务 | `caizhilian.file-collection.task.list` |
| 查看任务详情 | `caizhilian.file-collection.task.form` |
| 检查存储连接 | `caizhilian.file-collection.storage.check` |
| 扫描任务 | `caizhilian.file-collection.scan.prepare/apply` |
| 运行任务 | `caizhilian.file-collection.run.prepare/apply` |
| 取消任务 | `caizhilian.file-collection.cancel.prepare/apply` |
| 删除任务 | `caizhilian.file-collection.delete.prepare/apply` |
