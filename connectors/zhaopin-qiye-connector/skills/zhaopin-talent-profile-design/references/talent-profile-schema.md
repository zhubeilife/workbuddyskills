# 通用人才画像 Schema v0.2

画像主体建议包含 profileVersion、title、summary、requirements、evidencePolicy、rubric 和 openQuestions。所有字段均为通用文本结构，不要求连接任何后端服务。

每个维度至少包含：

- dimension：通用维度名称
- level：must、not_want、preferred、core_neutral 或 bonus
- weight：软评分权重
- value：标准化值
- text：面向用户的展示文本
- detail：具体解释
- evidenceRequirement：证据要求
- source：jd、recruiter_input、candidate_feedback 或 human_confirmed
- sourceTrace：原始输入或位置
- originalText：原始表达
- status：active、pending 或 excluded
- confidence：high、medium 或 low

来源优先级默认是实际招聘行为/明确人工确认 > 招聘者对话 > JD。跨来源冲突时保留冲突说明，不得静默覆盖。

来源优先级用于解释冲突，不授权自动升级偏好：从招聘行为或单个候选人推断出的新要求先标 pending，用户确认后才可激活或升级为硬门槛。confidence 仅说明提取/解释的证据把握，须附依据；不是候选人匹配概率，也不能代替用户确认。

建议从岗位实际语义选择维度：岗位职责、业务场景、核心能力、技术/专业技能、行业经验、公司/项目经验、职级与协作范围、成果证据、工作地点、薪资和到岗要求等。只有岗位明确要求时才加入学历、证书等门槛；不为追求结构完整而虚构字段。
