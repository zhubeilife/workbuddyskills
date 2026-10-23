# 共享画像输入说明

匹配必须读取完整岗位画像，至少包括岗位摘要、要求维度、等级、要求值、证据要求、权重和 rubric。画像可由用户直接提供，不依赖任何内部数据接口。

候选人证据建议记录 candidateId、sourceText、dim、evidence、evidenceType、matchState 和 confidence。

evidenceType：fact / inference / missing。
matchState：matched / not_matched / uncertain / not_applicable。
