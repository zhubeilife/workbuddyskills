# 员工档案体系与独立记录对象

只在问题涉及教育经历、工作经历、证书、家庭成员、历史绩效、线上课程、培训考试、学习地图、线下培训或企业自定义档案时读取。

## 先区分主题和对象

“员工档案体系”是围绕员工保存的资料主题，不是一个可查询的万能对象。每一条教育、工作、证书、家庭、绩效或培训记录都是独立业务对象，有自己的记录 ID、字段、时间和命令入口。用户说“查看员工档案”时，必须先确认要看哪一类记录；不能把多个列表拼成一个“完整档案”后再自行补字段。

固定档案和企业自定义档案都使用 Flex Meta 描述结构，但取数入口不同：

| 类型 | 含义 | 取数边界 |
| --- | --- | --- |
| `ENTITY` | iHR 固定档案对象 | 仅允许当前固定白名单 |
| `SUBSET` | 租户配置的自定义档案对象 | 使用真实 `metaCode` 进入通用子集入口 |

`metaDataId` 用于定位元数据配置，`metaCode` 用于定位档案集合；两者不能互换。类型必须来自当前租户真实元数据，不能根据名称、前缀或页面标题猜测。

## 固定档案对象目录

| 对象 | `metaDataCode` | 一条记录代表什么 | 当前命令 |
| --- | --- | --- | --- |
| 教育经历记录 | `tab_staff_education` | 一段学校、专业、学历或学位经历 | `staff +archiveList` |
| 工作经历记录 | `tab_staff_job_history` | 一段历史公司/职位经历 | `staff +archiveList` |
| 证书记录 | `tab_staff_certificate` | 一项证照、资格或认证 | `staff +archiveList` |
| 家庭成员记录 | `tab_staff_family_member` | 员工的一名家庭成员及关系 | `staff +archiveList` |
| 绩效档案记录 | `tab_staff_performance` | 一次历史绩效考核人员记录 | `staff +archiveList` |
| 线上课程记录 | 由培训接口固定定义 | 一次线上课程学习记录 | `staff training course-record-page` |
| 培训考试记录 | 由培训接口固定定义 | 一次培训考试记录 | `staff training exam-record-page` |
| 学习地图记录 | 由培训接口固定定义 | 学习地图/培训项目中的阶段或内容记录 | `staff training learnmap-record-page` |
| 线下培训记录 | 由培训接口固定定义 | 一次线下培训活动记录 | `staff training offline-training-record-page` |

员工基础信息不属于 Archive 列表对象，使用 `staff +search/+get`。历史绩效档案属于 Staff 档案查询边界，但当前绩效结果和评分明细属于 `ihr-smart-kpi`。

## 记录对象与字段

### 教育经历记录

除下表外，记录还可能带有记录标识、所属员工标识和租户配置的动态字段；这些字段是否返回以档案命令契约为准。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 教育记录 ID |
| `staffId` | 文本 | 所属员工 ID |
| `schoolName` | 文本 | 学校 |
| `schoolType` | 文本 | 学校类型 |
| `entryDate` / `graduateDate` | 日期 | 入校/结业时间 |
| `major` | 文本 | 专业 |
| `hasGotDegree` | 布尔值 | 是否取得学位 |
| `diplomaType` | 文本 | 学历 |
| `educationImageId1` / `educationImageId2` | 文本 | 教育证明附件 ID |
| `orderNumber` | 整数 | 展示顺序 |

教育记录中的 `schoolType`、`diplomaType` 可能是租户选项值；未取得对应元数据时保留原值，不猜展示名称。

### 工作经历记录

除下表外，记录还可能带有所属员工标识和租户配置的动态字段；这些字段是否返回以档案命令契约为准。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 工作经历记录 ID |
| `staffId` | 文本 | 所属员工 ID |
| `staffName` | 文本 | 员工姓名快照/展示值 |
| `companyName` | 文本 | 历史任职公司 |
| `enrollDate` / `quitDate` | 日期 | 历史入职/离职时间 |
| `jobTitle` | 文本 | 历史职位名称 |
| `jobDescription` | 文本 | 历史职位描述 |
| `orderNumber` | 整数 | 展示顺序 |

`jobTitle` 是历史职位文本，不是员工主记录的 `jobTitleId`。

### 证书记录

记录还可能返回员工展示信息，但这些信息不改变证书记录的身份。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 证书记录 ID |
| `staffId` | 文本 | 持证员工 ID |
| `certificateName` / `certificateType` | 文本 | 证照名称/类型 |
| `certificateNumber` / `autoCode` | 文本 | 证照编号/系统编号 |
| `certifyingAuthority` | 文本 | 发证机构 |
| `dateOfIssue` / `recordDate` | 日期 | 发证/备案日期 |
| `reminderDate` / `reminderType` | 日期 / 文本 | 提醒日期/类型 |
| `dateOfDue` | 日期 | 到期日期 |
| `major` / `grade` | 文本 | 专业/级别 |
| `remark` | 文本 | 证书备注 |
| `orderNumber` | 整数 | 展示顺序 |
| `flexAttributes` | 动态字段集合 | 证书自定义字段值 |

证书记录存在不等于证书当前有效；只有返回的状态或日期满足业务口径时才可说明有效性。

### 家庭成员记录

家庭成员记录还可能包含租户配置的动态字段。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 家庭成员记录 ID |
| `staffId` | 文本 | 所属员工 ID |
| `memberName` | 文本 | 家庭成员姓名 |
| `birthDate` | 日期 | 出生日期 |
| `relationship` | 文本 | 与员工关系 |
| `certificateFile` | 文本 | 证件附件引用 |
| `orderNumber` | 整数 | 展示顺序 |
| `flexAttributes` | 动态字段集合 | 家庭成员自定义字段值 |

`formFlexAttributes` 是表单转换数据，不是家庭成员业务字段；没有元数据时不解释动态值。

### 绩效档案记录

该记录表示 Staff 保存的一次历史绩效考核人员记录。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` | 文本 | 绩效档案记录 ID |
| `staffId` / `staffNo` | 文本 | 员工 ID / 工号 |
| `departmentId` / `departmentName` | 整数标识 / 文本 | 考核时使用的部门引用/名称 |
| `kpiAssessmentId` / `kpiTemplateId` | 文本 | 考核实例/模板引用 |
| `kpiAssessmentTitle` / `assessmentName` | 文本 | 考核标题/名称 |
| `kpiAssessmentStartTime` / `kpiAssessmentEndTime` | 日期 | 考核周期 |
| `finalScore` | 小数 | 数字化最终得分（如有） |
| `assessResult` | 文本 | 考核结果文本 |
| `assessmentStatus` | 枚举值 | 考评状态 |
| `assessmentType` / `appraiserType` | 枚举值 | 考核类型/考评人类型 |
| `approvalTime` | 日期 | 审批时间 |
| `currentAppraiserId` | 文本 | 当前考评人 |

绩效档案不替代 `ihr-smart-kpi` 的当前考核结果；两个对象不能合并统计。

### 线上课程记录

该记录由 `staff training course-record-page` 返回，结果中可能附带员工姓名、部门、工号和状态等展示信息；这些信息是查询上下文，不改变课程记录的身份。

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

### 培训考试记录

该记录由 `staff training exam-record-page` 返回。

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

### 学习地图记录

该记录由 `staff training learnmap-record-page` 返回。

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
| `trainerId` / `trainerName` | 文本 | 讲师 ID/名称 |

`children` 是同一学习地图记录的层级结构，不是新的业务对象类型。

### 线下培训记录

该记录由 `staff training offline-training-record-page` 返回。

| 字段 | 字段类型 | 业务含义 |
| --- | --- | --- |
| `id` / `staffId` | 文本 | 线下培训记录/员工 ID |
| `trainId` / `trainName` | 文本 | 培训 ID 与名称 |
| `channel` / `trainingCategoryTitle` | 文本 | 来源/培训分类 |
| `trainingStatus` | 文本 | 培训状态 |
| `trainingSignStatus` / `trainingSignTime` | 文本 | 签到状态/签到时间 |
| `trainingCompletedTime` | 文本 | 完成时间 |
| `courseCredit` / `coursePoint` | 文本 | 学分/积分 |

## 企业自定义档案记录

用户要求企业自定义档案时：

1. `staff +flexMetaList --kind custom` 获取当前租户候选。
2. 只接受明确标记 `metaDataType=SUBSET` 的候选。
3. 使用该候选的真实 `metaCode` 调用 `staff +archiveList` 或 `staff +archiveGet`。
4. 档案字段必须根据对应 Meta 的真实 `fieldName/fieldType` 解释；没有可执行 Meta Detail 或唯一字段 code 时，停止字段级查询，不猜字段名和类型。

`archiveGet` 一次最多五个 `SUBSET` code；固定 `ENTITY` 档案不能改传 `SUBSET`。自定义档案不使用花名册 `--fields`。

## 查询边界与数量口径

- 教育、工作、证书、家庭成员和四类培训记录通常是一名员工多条记录；分页总数是记录数，不是员工人数。
- `training count` 返回课程、考试、学习地图/培训项目、线下培训四类记录数；四个数不能相加后称为培训人数。
- 一次只查询一个已确认档案类别。普通查询只读当前页；该类别的统计分析、明确全量或完整拉取可串行翻页，禁止并发请求或同时枚举其他档案类别。
- “最新一条”只有在命令公开可靠排序字段并实际指定排序后才可判断。
- 多类别查询时分别呈现每类成功、空结果和失败；部分结果不能包装成完整员工档案。
- 参数和返回摘要见[员工档案命令](../commands/archives.md)与[培训命令](../commands/training.md)。
