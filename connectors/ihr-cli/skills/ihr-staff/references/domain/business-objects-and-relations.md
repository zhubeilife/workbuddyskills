# Staff 业务对象与关系

本文件是 Staff 业务对象和关系的详细定义。每个对象都要有自己的身份、粒度、字段、状态和事实来源；“员工档案体系”只是资料主题，不能代替其中的具体记录。入职、转正、调动和离职是四条员工任职业务流程，流程内部的表单、审批、交接和结果记录按各自对象分别建模。

## 对象建模规则

- 业务对象必须能由稳定 ID 或明确的对象 + 类型 + 时点定位。
- 不同对象的 ID、状态、日期、数量和完成证据不能互换。
- 同一个员工可以有多条教育、工作、证书、家庭、绩效或培训记录；记录数不是员工数。
- 字段表紧跟对象定义维护。员工固定字段的全量清单见[员工对象](employee.md)；命令参数和响应路径仍以命令 Help、Schema 或命令导航为准。
- 关系图只作摘要，关系表才是事实来源；缺少公开命令结果或元数据证据的关系标为“未声明”，不得补猜。

## 1. 员工

**定义**：花名册查询返回的员工主记录和任职引用。

**身份**：`id`；部分命令使用同一业务 ID 的输入别名 `staffId`。

**关键字段**：`staffStatus`、`enrollStatus`、`departmentId`、`positionId`、`jobTitleId`、`positionLevelId`、`supervisorId`、`companySiteId`、`enrollInDate`、`leaveDate`、`positiveDate`、`flexAttributes`。

**字段详情**：[员工对象：固定信息与可配置字段](employee.md)。其中 `jobTitleId`、`positionId`、`positionLevelId`、`supervisorId` 和 `companySiteId` 均为文本标识；`departmentId` 为整数标识。

## 2. Flex Meta

**定义**：租户配置的员工字段、档案集合、字段类型、选项和排序能力的元数据。

**身份**：`metaDataId` 定位元数据配置；`metaCode` 定位档案集合；`fieldName` 定位具体字段；三者不能互换。

| 字段/属性 | 含义 | 禁止推断 |
| --- | --- | --- |
| `metaDataType` | `ENTITY` 固定档案或 `SUBSET` 自定义档案 | 不根据名称或前缀猜类型 |
| `fieldName` | 员工或档案数据的真实字段 code | 中文显示名不能直接当 code |
| `fieldType` | 字段值类型和选项来源 | 不能当作查询操作符 |
| `codeValueId` | 平铺选项集合标识 | 不替代 `fieldName` |
| `codeTypeId + groupCode` | 树形选项集合标识 | 两者缺一不可 |

## 3. 员工档案体系中的独立记录

“员工档案体系”只表示一组围绕员工保存的资料。以下对象各自独立，使用不同记录 ID 和命令分支。

### 教育经历记录

**定义**：员工的一段学校、专业、学历或学位经历。

**身份**：记录 `id`；列表也可用员工姓名/工号和档案条件定位。

| 字段 | 字段类型/格式 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 教育记录 ID |
| `staffId` | 文本 | 所属员工 ID |
| `schoolName` | 文本 | 学校 |
| `schoolType` | 文本 | 学校类型 |
| `entryDate` / `graduateDate` | 日期 | 入校/结业时间 |
| `major` | 文本 | 专业 |
| `hasGotDegree` | 布尔值 | 是否取得学位 |
| `diplomaType` | 文本 | 学历 |
| `educationImageId1` / `educationImageId2` | 文本 | 教育证书附件 ID |
| `orderNumber` | 整数 | 展示顺序 |
| `flexAttributes` | 动态字段集合 | 教育档案自定义字段值 |

教育记录可能同时返回所属租户、创建时间、更新时间和动态字段；这些附加值不改变教育经历的业务粒度。记录数不等于员工数，教育经历不替代员工 `highestEducation`。

### 工作经历记录

**定义**：员工入职本公司前或其他任职期间的一段工作经历。

**身份**：记录 `id`，并以 `staffId` 关联员工。

| 字段 | 字段类型/格式 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 工作经历记录 ID |
| `staffId` | 文本 | 所属员工 ID |
| `staffName` | 文本 | 员工姓名快照/展示值 |
| `companyName` | 文本 | 历史任职公司 |
| `enrollDate` / `quitDate` | 日期 | 历史入职/离职时间 |
| `jobTitle` | 文本 | 历史职位名称 |
| `jobDescription` | 文本 | 历史职位描述 |
| `orderNumber` | 整数 | 展示顺序 |
| `flexAttributes` | 动态字段集合 | 工作经历自定义字段值 |

`jobTitle` 是历史职位文本，不是当前员工对象的 `jobTitleId`。

### 证书记录

**定义**：员工持有的一项证照、资格或认证记录。

**身份**：证书记录 `id`，并以 `staffId` 关联员工。

| 字段 | 字段类型/格式 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 证书记录 ID |
| `staffId` | 文本 | 持证员工 ID |
| `certificateName` | 文本 | 证照名称 |
| `certificateType` | 文本 | 证照类型 |
| `certificateNumber` | 文本 | 证照编号 |
| `autoCode` | 文本 | 系统自动编号 |
| `certifyingAuthority` | 文本 | 发证机构 |
| `dateOfIssue` / `recordDate` | 日期 | 发证/备案日期 |
| `reminderDate` / `reminderType` | 日期 / 文本 | 到期提醒日期/类型 |
| `dateOfDue` | 日期 | 到期日期 |
| `major` / `grade` | 文本 | 专业/级别 |
| `remark` | 文本 | 证书备注 |
| `orderNumber` | 整数 | 展示顺序 |
| `flexAttributes` | 动态字段集合 | 证书自定义字段值 |

返回中的 `staffName`、`staffNo`、`mobileNo` 等是员工展示信息，不是证书自身的身份字段。

### 家庭成员记录

**定义**：员工的一名家庭成员及其关系资料。

**身份**：记录 `id`，并以 `staffId` 关联员工。

| 字段 | 字段类型/格式 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 家庭成员记录 ID |
| `staffId` | 文本 | 所属员工 ID |
| `memberName` | 文本 | 家庭成员姓名 |
| `birthDate` | 日期 | 出生日期 |
| `relationship` | 文本 | 与员工关系 |
| `certificateFile` | 文本 | 证件附件引用 |
| `orderNumber` | 整数 | 展示顺序 |
| `flexAttributes` | 动态字段集合 | 家庭成员自定义字段值 |

`formFlexAttributes` 仅是表单转换数据，不应当作家庭成员业务字段解释。

### 绩效档案记录

**定义**：Staff 域保存的一次历史绩效考核人员记录，反映某个绩效考核周期对员工的记录。

**身份**：`id` 与 `kpiAssessmentId`/`kpiTemplateId` 等业务引用组合；具体唯一性以返回契约为准。

| 字段 | 字段类型/格式 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 绩效档案记录 ID |
| `staffId` / `staffNo` | 文本 | 员工 ID / 工号 |
| `kpiAssessmentId` / `kpiTemplateId` | 文本 | 考核实例/模板引用 |
| `kpiAssessmentTitle` / `assessmentName` | 文本 | 考核标题/名称 |
| `kpiAssessmentStartTime` / `kpiAssessmentEndTime` | 日期 | 考核周期 |
| `finalScore` | 小数 | 数字化最终得分（如有） |
| `assessResult` | 文本 | 考核结果文本 |
| `assessmentStatus` | 枚举值 | 考评状态 |
| `assessmentType` / `appraiserType` | 枚举值 | 考核类型/考评人类型 |
| `approvalTime` | 日期 | 审批时间 |
| `currentAppraiserId` | 文本 | 当前考评人 |

它属于 Staff 的历史档案查询边界，不替代 `ihr-smart-kpi` 的当前绩效结果、指标或评分明细。

### 线上课程记录

**定义**：员工参加线上课程形成的一条学习记录。

**身份**：记录 `id`；`staffId` 是所属员工 ID。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` / `staffId` | 文本 | 课程记录/员工 ID |
| `trainId` / `trainName` | 文本 | 培训/课程 ID 与名称 |
| `channel` / `courseCategory` | 文本 | 来源/课程分类 |
| `courseLearnStatus` | 文本 | 学习状态 |
| `courseProgress` | 文本 | 学习进度 |
| `courseStartTime` / `courseCompletedTime` | 文本 | 学习开始/完成时间文本 |
| `courseLearningTimeSecond` | 文本 | 学习用时 |
| `courseCredit` / `coursePoint` | 文本 | 学分/积分 |

由 `staff training course-record-page` 查询；记录数不是学习人数。

### 培训考试记录

**定义**：员工参加培训考试形成的一条考试记录。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` / `staffId` | 文本 | 考试记录/员工 ID |
| `trainId` / `trainName` | 文本 | 培训/考试 ID 与名称 |
| `channel` / `examCategoryTitle` | 文本 | 来源/考试分类 |
| `examPassStatus` | 文本 | 考试状态 |
| `examTotalScore` / `examPassScore` / `examLastScore` | 文本 | 总分/及格分/得分 |
| `examAttemptTimes` | 文本 | 补考次数 |
| `examAvgUsedTime` | 文本 | 考试用时 |
| `examCompletedTime` | 文本 | 考试完成时间 |
| `courseCredit` / `coursePoint` | 文本 | 学分/积分 |

由 `staff training exam-record-page` 查询。

### 学习地图记录

**定义**：员工在学习地图或培训项目中的阶段、内容和完成状态记录。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` / `staffId` | 文本 | 学习地图记录/员工 ID |
| `trainId` / `trainName` | 文本 | 培训项目 ID 与名称 |
| `parentTrainId` / `parentTrainName` | 文本 | 父培训项目 |
| `learningMapCategoryTitle` | 文本 | 学习地图分类 |
| `learningMapLearnStatus` / `learningMapProgress` | 文本 | 总体完成状态/进度 |
| `learningMapTitle` / `learningMapTargetTitle` | 文本 | 阶段/内容名称 |
| `learningMapType` / `learningMapStudyStatus` | 文本 | 内容类型/学习状态 |
| `learningMapStudyProgress` | 文本 | 内容进度 |
| `learningMapStartTime` / `learningMapFinishTime` | 文本 | 开始/完成时间 |
| `learningMapAvgUsedTime` / `learningMapScore` | 文本 | 用时/得分 |
| `children` | 对象集合 | 子阶段或子内容 |
| `seqNo` | 整数 | 排序序号 |
| `trainerId` / `trainerName` | 文本 | 讲师引用/名称 |

由 `staff training learnmap-record-page` 查询。`children` 是记录层级，不是新的培训对象类型。

### 线下培训记录

**定义**：员工参加线下培训活动形成的一条培训记录。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` / `staffId` | 文本 | 线下培训记录/员工 ID |
| `trainId` / `trainName` | 文本 | 培训 ID 与名称 |
| `channel` / `trainingCategoryTitle` | 文本 | 来源/培训分类 |
| `trainingStatus` | 文本 | 培训状态 |
| `trainingSignStatus` / `trainingSignTime` | 文本 | 签到状态/签到时间 |
| `trainingCompletedTime` | 文本 | 完成时间 |
| `courseCredit` / `coursePoint` | 文本 | 学分/积分 |

由 `staff training offline-training-record-page` 查询。

### 企业自定义档案记录

**定义**：租户通过 Flex Meta 配置的 `SUBSET` 档案中的一条记录。

**身份**：`metaCode + staffId + 记录标识`；`metaDataId` 只定位元数据配置。

**字段**：由该 `SUBSET` 的真实 Flex Meta 动态定义，不能在通用文档中伪造字段名、类型或选项。

**查询**：先用 `staff +flexMetaList --kind custom` 确认 `metaDataType=SUBSET` 和 `metaCode`，再用 `staff +archiveList/+archiveGet`；自定义档案不使用花名册 `--fields`。

## 4. 入职流程中的业务对象

入职过程由多个相互关联但身份不同的业务对象承载，各对象负责不同阶段：

| 对象 | 定义 | 标识 | 当前公开能力 |
| --- | --- | --- | --- |
| 待入职表单 | 归档为员工前保存拟入职资料和办理状态 | `entryFormId` | 查询、单条创建/编辑/确认 |
| 入职信息 | 候选人入职资料载体 | `entryInfoId` | 查询或作为登记关联 |
| 入职登记表 | 候选人提交、供 HR 审核的资料对象 | `registrationId` | 查询、审核通过 |
| 入职审批记录 | 入职审批过程记录 | 审批实例标识 | 仅查询当前用户可见待审批列表 |

入职表单的状态、预计日期、归档结果和登记表的审核状态分别解释；登记表审核通过不自动等于员工已归档，必须按确认响应和花名册回读验证。

## 5. 转正流程中的业务对象

**定义**：转正流程中用于承载试用期转正式任职办理的转正单据及其过程对象。

**身份**：转正单据或过程对象 ID；没有唯一 ID 时使用员工、状态和时间范围形成候选。

**关键属性**：转正业务状态、审批状态、试用期考核状态、转正日期、员工引用。

**状态边界**：`STAY_CONFIRM`、`HAS_CONFIRM`、`COMPLETED`、`GIVE_UP`、`QUIT_GIVE_UP` 只解释转正办理状态；`completed` 列表分支不自动证明审批、考核或员工主表均已完成。

**当前能力**：`staff positive +search` 只读列表；没有详情、创建、提交、审批、确认或生效命令。

## 6. 调动流程中的业务对象

**定义**：调动流程中用于承载员工任职内容变更安排、审批和结果的调动单及其过程对象。

**身份**：调动单或过程对象 ID；没有唯一 ID 时使用员工、状态和时间范围形成候选。

**关键属性**：原任职引用、目标任职引用、调动办理状态、调动审批状态、计划调动日期、确认调动日期和实际生效日期（如该对象或命令已公开）。

**状态边界**：业务状态和审批状态是两个独立维度；例如 `positiveStatus=COMPLETED` 与 `entryApplicationStatus=ABANDONED` 可以同时出现，不能自行判定冲突。

**当前能力**：`staff transfer +search` 只读列表；`transfer-setting +get` 读取租户调动规则，不是调动记录。

## 7. 离职流程中的业务对象

**定义**：离职流程中用于承载离职安排、审批、交接和结果归档的离职单及其过程对象。它可以处于办理中，不表示员工已经结束任职。

**身份**：离职单或过程对象 ID；没有唯一 ID 时使用员工、状态和时间范围形成候选。

**关键属性**：离职办理状态、离职审批状态、工作交接状态、离职类型、预计离职日期、确认离职日期、最后工作日和计薪截止日期。统一的“离职生效时间”当前没有公开契约。

**状态边界**：离职办理、离职审批和工作交接是三个独立维度；它们的代码和业务名称见[入职、转正、调动与离职业务流程](lifecycle.md)。审批通过或业务完成不自动证明花名册已变为 `QUIT`，也不证明工资、福利、考勤和账号回收完成。

**当前能力**：`staff quit +search` 只读列表；没有详情、创建、提交、审批、确认或生效命令。

## 8. 其他业务对象

### 员工标签记录

记录员工当前被赋予的标签，使用员工 ID 和返回的标签标识定位。`staff +tags` 不返回标签定义或维护能力；标签命中不构成风险结论。

### 合同记录

记录员工劳动关系合同，按合同记录和员工条件查询。合同记录数不等于员工数，合同有效期不自动证明员工离职或续签。

### 协议记录

记录员工除劳动合同以外的其他协议，和合同使用独立命令及字段。协议存在不自动证明业务事项完成。

### 已发生异动记录

记录已经形成的员工变化事实，类型可包括 `ADJUST`、`QUIT`、`ENTRY`、`POSITIVE`、`REINSTATED`。事件时间、生效时间、创建时间和操作时间分别解释；异动记录不是调动或离职过程单据。

### 员工黑名单记录

记录当前租户黑名单中的员工及状态，属于敏感只读查询；不提供标签或黑名单维护。

## 9. 关系清单

| 来源对象 | 关系 | 目标对象 | 数量 | 成立条件/时点 | 事实来源 | 禁止推断 |
| --- | --- | --- | --- | --- | --- | --- |
| 员工 | 当前任职引用 | Organization 部门/职位/职务/职级/地点 | N:1，可空 | 花名册查询时点 | 员工真实引用字段 | 不推出历史任职或调动目标已生效 |
| Flex Meta | 定义 | 员工固定/动态字段 | 1:N | 当前租户配置有效 | Flex Meta 与字段值结果 | 元数据存在不等于员工有值 |
| Flex Meta | 定义 | 各类档案集合 | 1:N | `ENTITY`/`SUBSET` 类型已确认 | 元数据结果 | `metaDataId` 不等于 `metaCode` |
| 员工 | 具有 | 教育经历记录 | 1:N | 记录在权限范围内可见 | `archiveList` | 记录数不等于员工数 |
| 员工 | 具有 | 工作经历记录 | 1:N | 记录在权限范围内可见 | `archiveList` | 历史经历不等于当前任职 |
| 员工 | 具有 | 证书记录 | 1:N | 记录在权限范围内可见 | `archiveList` | 证书存在不等于资格当前有效 |
| 员工 | 具有 | 家庭成员记录 | 1:N | 记录在权限范围内可见 | `archiveList` | 家庭成员数量不等于家庭关系结论 |
| 员工 | 具有 | 绩效档案记录 | 1:N | 对应绩效档案可见 | `archiveList` | 不替代 Smart KPI 当前结果 |
| 员工 | 具有 | 线上课程记录 | 1:N | 课程命令结果可见 | course-record-page | 记录数不等于培训人数 |
| 员工 | 具有 | 培训考试记录 | 1:N | 考试命令结果可见 | exam-record-page | 记录数不等于培训人数 |
| 员工 | 具有 | 学习地图记录 | 1:N | 学习地图命令结果可见 | learnmap-record-page | 记录数不等于培训人数 |
| 员工 | 具有 | 线下培训记录 | 1:N | 线下培训命令结果可见 | offline-training-record-page | 记录数不等于培训人数 |
| 待入职表单 | 承载/关联 | 入职信息、入职登记表、入职审批等流程对象 | 1:N | 入职对象在权限范围内可见 | entry commands | 任一过程对象存在不等于已归档 |
| 员工 | 参与/关联 | 转正流程业务对象 | 1:N | 转正列表返回对象 | positive search | 对象状态不直接改写员工状态 |
| 员工 | 参与/关联 | 调动流程业务对象 | 1:N | 调动列表返回对象 | transfer search | 目标任职不等于当前任职 |
| 员工 | 参与/关联 | 离职流程业务对象 | 1:N | 离职列表返回对象 | quit search | 审批通过不等于离职已生效 |
| 待入职表单 | 确认归档为 | 员工 | 未声明 | 确认成功且花名册可回读 | confirm + roster get | 单一响应不证明归档完成 |
| 调动流程对象 | 目标任职引用 | Organization 定义对象 | N:1，可空 | 单据返回目标引用 | transfer result | 目标 ID 不等于已生效关系 |
| 调动/离职流程对象 | 生效后可能形成 | 已发生异动记录 | 未声明 | 业务生效且历史记录生成 | change-record result | 审批通过不保证异动已形成 |

## 10. 结果判断

- 员工主记录、档案记录、四条业务流程中的过程对象和异动记录必须分别陈述。
- `staffId`、`entryFormId`、`entryInfoId`、`registrationId`、单据 ID、`metaDataId`、`metaCode`、`fieldName` 只定位各自对象。
- 空列表、字段缺失、脱敏和分页结果可能由权限、筛选、租户配置或请求投影造成，不能直接证明对象不存在。
- 查询成功、审批状态、业务状态、生效结果和下游完成分别需要对应事实来源；只有目标规定的证据全部满足时才报告完成。
