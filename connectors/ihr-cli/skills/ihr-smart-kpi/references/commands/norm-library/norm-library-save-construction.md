# 指标库保存构造

以前端 formSubmit 和后端 KpiNormParam/KpiNormFieldParam 为事实源。

顶层公开字段：id、normName、normCode、normType、normCategoryId、departmentIds（数组，CLI join 成逗号字符串）、normScope、ratingType、ratingFormula、carryRule、digit、allowEditFormula、normMenuType、kpiNormFieldParamList。

不传：companyId、staffId、enabled、normFillProperty、四个 use-value、normExplain、normStandard、顶层 unitId/unitName、normScopeDisplay。

空编码转 null。能力素质/价值观固定定性手工评分。自动评分必须有评分公式。字段三种录入方式互斥。名称隐藏字段 defaultValue=normName，类型隐藏字段 defaultValue=normCategoryId。

附件字段：`fieldProperty=ATTACHMENT` 时，`defaultValue` 只保留附件 ID。对象形态取 `fieldId` 或 `response.data`，已是 ID 的值原样保留；缺少可提取 ID 时本地拒绝。不提交 fileName、url 或完整上传对象。
