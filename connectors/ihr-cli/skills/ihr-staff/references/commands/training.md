# 培训查询命令

培训使用 metadata command。具体命令 Help 只描述通用 body 输入，当前 `schema` 暴露的结构仍不完整，因此本文件补充已确认的业务请求和返回边界。

## 命令

| 命令 | 业务输入 | 业务返回 |
| --- | --- | --- |
| `staff training count` | 可选 `staffStatuses` 列表 | 四类培训记录数量对象 |
| `staff training course-record-page` | `staffId`、`page`、`size` | 线上课程记录分页 |
| `staff training exam-record-page` | 同上 | 考试记录分页 |
| `staff training learnmap-record-page` | 同上 | 学习地图或培训项目分页 |
| `staff training offline-training-record-page` | 同上 | 线下培训记录分页 |

metadata command 通过 `--data/--json/--stdin` 提交业务 body。四类明细的 body 白名单只有 `staffId/page/size`；`staffId` 必填，页码默认 1、大小默认 20，用户侧和后端都从 1 开始。不得提交 `criteria/orders/specification/sort`。

## 返回

- 业务 payload 位于 `response.body.data`。
- `training count` 的已声明字段为 `courseRecordCount/examRecordCount/learnmapRecordCount/trainingRecordCount`，分别表示四类记录数。
- 四类明细的列表位于 `dataList`，分页位于 `pageInfo.totalCount/totalPages/pageNo/pageSize`；列表元素字段仍是开放的部分契约，只解释实际返回且业务含义明确的字段。

## 边界

- 汇总受培训查看权限和员工数据范围约束；未传员工状态时使用后端默认口径，回答中必须说明没有显式状态筛选。
- 明细只查询一个已确认 `staffId`，不自动组合四类记录或枚举员工。普通查询只读当前页；单个员工的培训明细统计可按 `pageInfo` 串行翻页，禁止并发请求。
- 记录数不是去重员工数、培训学时或完成率。
- Help/Schema/本 Reference 冲突时按导航规则报告契约漂移并停止使用冲突字段。
