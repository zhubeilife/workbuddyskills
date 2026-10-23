# 统一匹配评分卡 v0.1

rubric 必须包含 version、summary、scoreRanges、hardRules、softWeighting、evidenceRequirement、tieBreakers 和 rubricVersion。

默认软权重：preferred 60、core_neutral 30、bonus 10，总和为 100。硬规则先判定，软评分后判定；评分不能掩盖硬条件缺失；相同岗位候选人必须使用同一份 rubric。

仅有 active 要求的软组参与计分；空组权重为 0，其余组按默认权重比例归一化，并公开有效权重。全部软组为空时不生成总分。组内维度等分或明确说明权重依据，不为填满权重虚构要求。

证据不足记录为未知，不按不满足或零分处理；在缺失证据会影响判断时不输出确定总分。scoreRanges 未经业务校准时标记“待校准，不用于推荐阈值”，可以不设置数值区间。

上述默认权重仅是可选校准起点，不是已验证的业务权重。没有业务确认的权重和证据评分锚点时，softWeighting 标记为“待校准”，仅输出定性维度核验，不输出候选人数值总分；需要展示计算示例时明确标为示例，不用于推荐决策。
