# 模板公式保存流程

本流程只修改已有公司薪资模板中的字段公式。保存接口是完整规则替换，不支持局部 patch。

## 1. 读取与定位

读取 `ihr-payroll` 的 `references/commands/company-template-snapshot.md`，用正整数 `payrollConfigId` 获取最新 snapshot。

在完整 `groupList` 和 `noGroupSalaryFieldList` 中按以下顺序定位目标：

1. 用户提供项目名称时按完整名称唯一匹配；
2. 用户明确提供技术 code 时只接受唯一完全相同的 code，并在确认文案中转换为对应项目名称；
3. 零候选或多候选时展示必要项目名称、类型/类别名称和来源名称并询问，不要求用户复制内部 code。

同一项目只能修改一次。用户未列出的项目不是删除目标，也不是公式修改目标。

## 2. 形成字段变更

复制最新 snapshot 的完整 `rules`。每个已完成校验、试算和结果确认的目标只修改：

```json
{
  "source": {"id": "FUNCTION"},
  "valueMeta": {
    "formula": "=<字段 code 表达式>",
    "formulaFrom": "USR"
  }
}
```

上例表示局部差异，不是可提交的局部请求。实际保存对象仍是完整 `rules`。内部 `formula` 由校验返回的 `exprItems` 按前端逻辑拼接生成，不再依赖独立转换结果。

保持目标字段已有的 `originSource`、位置、名称、code、类型、计税、审批显示、公司成本、进位规则、小数位、空值与上下限设置；保持所有非目标字段和分组不变。用户要求同时修改这些非公式设置时，停止并转交相应模板配置流程。

## 3. 预览与确认

读取 `ihr-payroll` 的 `references/commands/company-template-save-rules.md`，用最新 `snapshotHash + 完整 rules` 执行一次 dry-run。

保存确认至少展示：

- 模板 ID 与名称；
- 每个目标项目的名称、类型/类别名称和来源名称；
- 对任一来自 Excel 公式列的目标字段：先展示 Excel 原公式作为来源，同时展示目标字段当前来源和旧公式状态；用户可确认沿用目标设置、改为输入，或改为当前编辑器中的薪资系统公式文本。选择公式时，保存对象里的内部 `formula` 由校验返回的 `exprItems` 拼接生成；选择输入时，将来源改为输入并清空模板公式；选择沿用时不修改该字段。code 公式仅在用户明确要求技术详情时附加展示；
- 校验通过状态、试算结果及已确认预期；
- 完整模板的分组数、项目总数、输入项数和公式项数；
- 这是全量替换，确认只覆盖当前 snapshot 与 payload。

未取得明确保存确认时停在 dry-run。用户只确认翻译、校验或试算不构成保存授权。

## 4. 写入与恢复

确认后去掉 dry-run，只执行一次 `companyTemplate +save-rules`。成功必须包含相同模板 ID、`verified=true` 和非空新快照哈希，并且读回目标公式、`source.id=FUNCTION`、`formulaFrom=USR` 与确认内容一致。

哈希过期时重新 snapshot，在新基线上重放同一组公式差异，重新校验受影响目标、生成 dry-run 并重新确认。网络超时、连接中断、响应丢失或写后读回不一致时写入状态为 `UNKNOWN`；只允许读取 snapshot 对比，不自动再次保存。`save-rules` 返回引用尚未加入当前薪资表时，读取[补齐公式引用项目](../company-template-configure/missing-formula-reference.md)。
