# SMART-KPI 指标模板导入过程状态

本 reference 规定指标模板文件导入的内部过程状态。它只用于当前 Agent Session 内的多轮确认和上下文压缩恢复，不是客户文档、CLI 入参、业务接口或跨 Session 草稿。状态文件位于项目工作空间，客户可以看到文件，但文件内容仍按最小化和敏感字段禁止规则处理。

## 1. Session 边界与存放位置

1. 每个 Agent Session 同时只允许一个活动指标模板导入。识别到导入意图后，先确认当前运行环境能够提供当前项目工作空间、稳定不透明 `sessionId`、SHA-256 能力以及创建、读取和原子替换文件的工具。
2. 状态文件固定为 `<workspace-root>/ihr-smart-kpi/norm-template-import/<sessionKey>/state.json`。工作空间由当前运行环境提供；`<sessionKey>` 子目录用于隔离不同 Session。不得改写到客户工作簿目录、共享系统临时目录、共享用户目录或业务服务。
3. `sessionKey` 固定为小写十六进制 `SHA-256(UTF-8("smart-kpi:norm-template-import:v1:" + sessionId))`。不得使用其他前缀、编码、大小写或摘要算法。
4. 在第一次业务命令或第一次客户业务确认前，只打开上述固定路径。先递归创建当前 Session 的 `sessionKey` 子目录。文件不存在时创建初始状态；文件存在且是当前 Session 的有效非终态状态时，不得覆盖或创建第二份状态，必须让客户选择继续当前导入或取消后开始新导入；文件存在且是有效终态状态时，先识别上次导入已结束并删除该 `state.json`，再创建新的 `ACTIVE/INIT` 状态。
5. 初始文件写入后必须立即回读，校验 `sessionKey`、`schemaVersion`、`stateVersion=1`、`sharedVersion=1` 和 `sharedPhase=INIT`。创建或回读失败时不得调用业务命令、接受业务确认或继续解析。
6. 只允许拼接当前运行环境提供的项目工作空间、当前 `sessionKey` 和固定相对路径；禁止扫描工作空间、按最近修改时间寻找状态、猜测其他文件名或读取其他 Session 的文件。
7. 当前 Session 发生上下文压缩或暂停后，恢复流程的第一个动作必须是从固定路径回读该文件并完成第 5 节校验；不能依赖压缩后的对话内容恢复路径或确认。开启新 Session 时不得读取、扫描或恢复旧 Session 状态，必须重新开始适用确认。
8. 当前运行环境不能提供当前项目工作空间、稳定 `sessionId`、SHA-256 或必要文件工具时，必须在第一次业务命令和第一次客户业务确认前停止。不得降级为对话记忆、客户文件路径或未绑定 Session 的共享路径，也不得以重新询问客户后仅靠对话继续导入。
9. 过程状态不进入客户回复。Agent 可以正常说明当前业务进度，但不得展示状态路径、Session 标识或摘要、内部 schema、状态 JSON 或载荷指纹。
10. 能力缺失、状态异常或传输失败时，客户回复只使用“当前工具暂时无法继续导入”“当前运行环境暂时无法保存导入进度”等业务语言，并给出客户可执行的下一步；不得展示任何内部实现术语、文件工具、状态路径、Session 标识或存储细节。

## 2. 文档结构

状态使用结构化 JSON，顶层只允许以下字段：

```json
{
  "schemaVersion": 1,
  "sessionKey": "当前 Agent Session 稳定隔离标识的不可逆摘要",
  "stateVersion": 1,
  "sharedVersion": 1,
  "status": "ACTIVE",
  "sharedPhase": "INIT",
  "createdAt": "ISO-8601 时间",
  "updatedAt": "ISO-8601 时间",
  "assessmentTemplate": null,
  "sourceFile": null,
  "candidateDiscovery": null,
  "sources": [],
  "executionSummary": {
    "succeededSourceIds": [],
    "failedSourceIds": [],
    "pendingSourceIds": []
  }
}
```

`status` 只允许：

- `ACTIVE`
- `COMPLETED`
- `CANCELLED`
- `PERMANENTLY_FAILED`

`sharedPhase` 只允许：

- `INIT`
- `ASSESSMENT_CONFIRMED`
- `SOURCE_CONFIRMED`
- `CANDIDATES_INCOMPLETE`
- `CANDIDATES_COMPLETE`

每个 `sources[]` 项的 `sourcePhase` 只允许：

- `SOURCE_CONFIRMED`
- `OPERATION_CONFIRMED`
- `DRAFT_READY`
- `PAYLOAD_VALIDATED`
- `PREVIEW_CONFIRMED`
- `SAVE_SUCCEEDED_VERIFY_PENDING`
- `SAVE_SUCCEEDED_VERIFY_FAILED`
- `SAVE_FAILED_REVIEW_REQUIRED`
- `SAVED`
- `CANCELLED`
- `PERMANENTLY_FAILED`

`stateVersion` 是整份文件的并发写入版本，每次成功原子替换并回读后递增。`sharedVersion` 标识考核模板、来源文件和完整指标模板候选等共享依赖版本。每个 `sources[]` 项还必须维护独立的 `sourceVersion` 和 `sourcePhase`；校验、预览和确认记录对应的 `sharedVersion + sourceVersion`，只允许版本组合完全一致的来源范围继续保存。`sharedPhase` 达到 `CANDIDATES_COMPLETE` 后不再由任一来源进度覆盖。

## 3. 白名单字段

### 考核模板

`assessmentTemplate` 只记录：

- `templateBasicId`
- 客户可读模板名称
- 客户确认状态和确认时间

### 来源文件

`sourceFile` 只记录：

- 当前 Session 内可重新读取的文件引用
- 客户可读文件名
- 文件类型
- 用于识别内容变化的文件摘要

不得复制工作簿、Sheet 全文、原始二进制、单元格全集或附件内容。

### 指标模板候选

`candidateDiscovery` 只记录：

- `templateBasicId`
- 已读取页码、响应声明的总页数/总数和分页完成状态
- 失败页及脱敏错误摘要
- 最小候选字段：`normTemplateId`、客户可读名称和用于比对的必要业务摘要

任一页失败时必须把 `sharedPhase` 设为 `CANDIDATES_INCOMPLETE`，不得把部分候选写成完整结果。

### 多个来源范围

`sources[]` 每个 Sheet/区域使用独立 `sourceId`，至少记录：

- 当前来源范围的 `sourceVersion` 和 `sourcePhase`
- Sheet/区域或文本段落位置，以及客户确认的范围顺序
- 客户确认的模板名称来源、项目、指标行和列语义
- Skill 的新增/更新建议及名称、项目、指标内容等可读依据
- 客户确认的 `CREATE/UPDATE`；更新时记录确切 `normTemplateId` 和客户可读名称
- `struct/detail` 底稿类型、读取时间、底稿摘要和构造所需的业务 ID；不保存完整原始响应
- 项目、指标和字段映射，以及每项客户确认状态
- 指标库查询条件、最小候选、客户选择和确认状态
- 字段转换决定、公式转换决定和明确不导入原因
- 本地校验、单公式校验、字段公式集合校验的状态版本和客户可读结果摘要
- stdin 传输类型（`WINDOWS_POWERSHELL_5_UTF8`、`POWERSHELL_7_UTF8` 或 `POSIX_UTF8`）、传输校验对应的 `sharedVersion + sourceVersion`、原载荷指纹、dry-run 完整 `request` 指纹、是否一致和校验时间；不保存命令文本、完整载荷或完整 CLI envelope
- 完整预览摘要、规范化最终载荷的 SHA-256 指纹、确认状态和确认时间
- 最终确认绑定：当前 `sourceId`、目标指标模板 ID/名称、规范化最终载荷 SHA-256、确认时的 `sharedVersion + sourceVersion`；一次客户确认只能写入一个来源
- 当前模板保存结果或脱敏失败摘要
- 保存成功返回的 `normTemplateId`、保存后详情回读状态/时间、实际详情摘要和脱敏回读失败摘要；不得保存完整详情或完整保存响应

多个来源范围可以共享同一次完整候选列表，但不能共享操作决定、更新目标、底稿、字段映射、校验、预览或保存确认。多模板客户可读汇总不写成任何来源的最终预览或确认记录。

## 4. 禁止字段

状态文件禁止写入：

- token、cookie、Authorization、密码或其他凭据
- `companyId`、`userId`、当前登录人、权限对象或数据范围表达式
- 手机号、证件号、完整员工卡片或与导入无关的人员信息
- 源文件副本、工作簿二进制、Sheet 全文或未确认的整包解析结果
- 完整 `struct/detail` 原始响应、完整待保存载荷或完整 CLI JSON envelope
- 附件 URL、下载/预览地址、附件内容或附件 token
- raw API、gateway URL、内部 endpoint 或可执行命令文本

每次创建或更新都必须按顶层和嵌套白名单重新构造状态，不能把 CLI 响应或保存对象整体序列化后再删字段。发现禁止字段、未知字段或白名单校验失败时，拒绝本次状态更新，保留上一个有效版本并停止后续保存流程。

## 5. 创建、写入与恢复

1. 初次创建时使用当前文件工具递归创建当前 `sessionKey` 子目录，把第 2 节初始状态写入固定路径，并立即回读校验。没有成功的创建和回读轨迹，不得进入考核模板查询或任何客户业务确认。
2. 每次客户确认、CLI 查询完成、映射变化、业务校验完成、stdin 传输校验完成、预览确认、保存响应产生或保存后详情回读完成后，先读取当前有效版本，再按白名单构造下一版本；状态成功落盘并回读校验后才能进入下一步。
3. 更新必须使用同目录临时文件和原子替换：写入下一版本临时文件，回读校验其 JSON、白名单、`sessionKey` 和预期版本，再原子替换正式文件并再次回读。失败时删除临时文件、保留上一个有效正式版本，不得留下多个可被恢复的候选版本。终态后的新导入先删除已确认结束的旧 `state.json`，再创建新的状态文件。整个过程只使用当前文件工具，不新增或调用状态脚本。
4. 每次成功更新将 `stateVersion` 增加 1。共享依赖变化时同时增加 `sharedVersion`；单个来源变化时只增加对应 `sourceVersion`。回读值与预期版本不一致时停止，不能覆盖或合并未知并发状态。
5. 一次客户最终确认事件只能修改一个 `sources[]` 项，并且最多把该来源从 `PAYLOAD_VALIDATED` 推进到 `PREVIEW_CONFIRMED`。拟写状态如果使用同一确认事件推进多个来源，必须拒绝本次更新、保留上一个有效正式版本并停止保存；不能拆成连续多次写回规避该约束。
6. 保存命令返回业务成功后，先把返回的 `normTemplateId` 写回为 `SAVE_SUCCEEDED_VERIFY_PENDING`，原子替换并回读状态成功后再调用 `norm-template +detail`。详情回读成功后进入 `SAVED`；缺少/无效 ID 或详情失败时进入 `SAVE_SUCCEEDED_VERIFY_FAILED`，保留脱敏摘要和已知 ID（如有），不得自动再次保存。详情不与确认载荷做业务字段一致性比较。
7. `PREVIEW_CONFIRMED` 记录必须同时匹配该来源的 `sourceId`、目标指标模板、规范化最终载荷 SHA-256、`sharedVersion` 和 `sourceVersion`。缺少任一绑定项、绑定到多来源或版本不一致时，确认无效且不得保存。
8. 上下文压缩或暂停后恢复时，必须先读取固定路径，校验 `sessionKey`、`schemaVersion`、状态结构、状态版本、文件摘要、阶段依赖、`sharedVersion`、目标来源的 `sourceVersion` 和确认记录。任一项不匹配时，不使用旧确认，也不能以压缩后的对话摘要补齐文件。
9. 状态只保存底稿摘要和必要业务 ID。恢复到构造、预览或保存阶段时，重新执行相应只读命令取得当前底稿并重建最终载荷。
10. 最终载荷使用“对象键稳定排序、数组保持业务顺序、UTF-8、无无关空白”的规范化 JSON 计算 SHA-256。进入最终预览前，使用同一规范化规则计算 CLI dry-run 完整 `request` 指纹并要求与原载荷指纹一致。重建后的载荷指纹、传输类型、dry-run 请求指纹、`sharedVersion + sourceVersion` 和已确认记录全部一致时，原传输校验和确认才仍然有效；否则按失效规则重新 dry-run、完整比较、预览和确认。
11. 当前 Session 状态文件缺失、损坏、版本不兼容、文件变化或来源文件不可重新读取时，停止当前导入并说明需要重新确认的最早业务节点。只有客户选择重新开始后，才创建并回读新的有效初始状态；不能猜测、自动选择、复用旧载荷或直接保存。

恢复阶段只按以下顺序决定：

1. `sharedPhase != CANDIDATES_COMPLETE` 时，只继续共享发现阶段，不进入任一来源底稿、校验、预览或保存。
2. `sharedPhase == CANDIDATES_COMPLETE` 时，按 `sources[]` 中客户确认的稳定顺序逐项检查。
3. `SAVED/CANCELLED/PERMANENTLY_FAILED` 来源直接跳过；遇到 `SAVE_SUCCEEDED_VERIFY_PENDING` 时先使用已记录 ID 回读详情，遇到 `SAVE_SUCCEEDED_VERIFY_FAILED` 或 `SAVE_FAILED_REVIEW_REQUIRED` 时停止并等待客户决定；否则继续第一个未完成来源的 `sourcePhase`。
4. 不使用顶层字段推断或覆盖来源进度。
5. 恢复到 `PREVIEW_CONFIRMED` 时只允许处理该确认绑定的一个来源；保存成功后必须先完成保存后详情回读并写回/回读 `SAVED`，下一来源才能展示自己的完整最终预览并取得新的确认。

## 6. 失效规则

以下任一内容变化时，清除受影响来源范围的底稿之后状态、校验结果、预览指纹和保存确认，并把对应的 `sharedPhase` 或 `sourcePhase` 回退到最早受影响节点：

- 考核模板、文件、Sheet/区域或来源顺序
- 新增/更新决定或更新目标
- `struct/detail` 底稿或候选分页完整度
- 项目、指标、字段映射或指标库候选选择
- 指标顺序、单位、分类、选项、字段值、录入方式或数据引用
- 公式角色、公式文本、转换决定、公式配置或依赖字段
- stdin 传输类型、当前命令行环境编码或 dry-run 完整请求比较结果

一个来源范围变化时只递增该范围的 `sourceVersion` 并使该范围失效；其他来源范围的有效确认不受影响。共享考核模板、来源文件身份或完整候选列表变化时递增 `sharedVersion`，回退 `sharedPhase` 并使所有依赖范围同时失效。`stateVersion` 只用于防止并发覆盖，不能单独作为所有来源确认失效的依据。

## 7. 终态与生命周期

- 所有来源范围均进入终态后，先把顶层 `status` 原子写回并回读为 `COMPLETED`，按成功、失败和未执行分别报告；完成报告后删除当前 `state.json`。
- 客户取消整个导入或流程发生无法继续的永久失败时，先把顶层 `status` 原子写回并回读为 `CANCELLED` 或 `PERMANENTLY_FAILED`，完成必要的客户可读报告后删除当前 `state.json`。
- 可恢复保存失败使用 `SAVE_FAILED_REVIEW_REQUIRED`，保留到客户决定继续、取消或当前 Session 结束；不得自动重试。
- 保存请求成功但详情回读失败使用 `SAVE_SUCCEEDED_VERIFY_FAILED`，保留已知 `normTemplateId` 和脱敏失败摘要；恢复时只能重新回读/分析或由客户取消，不能自动再次保存。
- 当前 Session 异常结束时工作空间中的状态文件可能残留；新 Session 仍不得扫描或恢复旧状态。残留文件不作为业务完成条件，后续可由用户或工作空间管理策略处理。

## 8. 与业务流程的关系

过程状态只记录既有流程，不改变业务顺序。每个编号步骤完成后必须先按第 5 节原子写回并回读状态，再进入下一步：

1. `ihr-cli smart-kpi template +list` 查询并由客户确认考核模板。
2. 解析文件并由客户确认 Sheet/区域和来源语义。
3. `ihr-cli smart-kpi norm-template +list` 串行读取全部必要分页。
4. Skill 提供新增/更新建议，客户分别确认每个来源范围的操作类型；更新必须确认具体指标模板。
5. 新建执行 `ihr-cli smart-kpi norm-template +struct`，更新执行 `ihr-cli smart-kpi norm-template +detail`。
6. 构造、转换和业务校验；使用当前运行环境的 UTF-8 stdin 对同一不可变 JSON 执行保存 dry-run，完整 `request` 指纹一致并完成状态写回/回读后，才展示逐模板最终预览。
7. 客户确认当前不可变载荷后，只把当前一个来源推进到 `PREVIEW_CONFIRMED`；复用已验证的同一 JSON 和 UTF-8 传输方式执行一次 `ihr-cli smart-kpi norm-template +save --stdin --confirm`。一次确认不得推进其他来源或授权其他保存。
8. 保存返回成功 ID 后，先写回/回读 `SAVE_SUCCEEDED_VERIFY_PENDING`，再调用现有 `ihr-cli smart-kpi norm-template +detail`；详情回读成功后写回/回读 `SAVED`，直接展示回读内容，才展示下一来源的完整最终预览并请求新的客户确认。多模板汇总不产生确认；客户要求“全部确认”时说明边界并从第一个未完成来源开始。

状态文件不能替代任何客户确认、后端权限、CLI 确认门或错误停止规则。不得为批量确认、状态推进或自动保存创建 helper 脚本、载荷文件或解析中间文件；唯一允许的内部文件是本 reference 规定的按 `sessionKey` 隔离的 `state.json`。
