# 公式处理产物

产物保存本次公式处理的可恢复状态。默认目录是系统临时目录 `ihr-cli/payroll-formula-edit/<唯一运行 ID>/artifact-vNNN/formula-edit.json`；每次输入、确认、校验、试算或保存状态变化都写新版本，不覆盖旧版本。

```json
{
  "schemaVersion": "1.0",
  "runId": "唯一运行标识",
  "mode": "TRANSLATE|VALIDATE|CALCULATE|SAVE",
  "status": "IN_PROGRESS|READY_TO_CONFIRM_SAVE|COMPLETE|BLOCKED|UNKNOWN",
  "payrollConfig": {
    "id": "可选模板 ID",
    "name": "可选模板名称",
    "snapshotHash": "可选最新快照哈希"
  },
  "targets": [
    {
      "field": {"code": "字段 code", "name": "字段名称"},
      "sourceKind": "EXCEL|BUSINESS_RULE|IDEOGRAPHIC|CODE",
      "codeFormula": "由校验 exprItems 拼接出的内部 code 公式",
      "ideographicFormula": "当前编辑器中的薪资系统公式正文",
      "references": [{"input": "C列", "fieldCode": "baseSalary", "fieldName": "基本工资"}],
      "validation": {"status": "NOT_RUN|PASSED|FAILED", "otherFieldCount": 0},
      "calculation": {
        "status": "NOT_RUN|PASSED|FAILED",
        "dependencyCodes": ["baseSalary"],
        "roundingMode": "ROUND",
        "decimalPlaces": 2,
        "result": "试算结果",
        "expectedConfirmed": false
      },
      "change": {"oldFormula": "旧公式", "newFormula": "新公式"}
    }
  ],
  "save": {
    "status": "NOT_REQUESTED|DRY_RUN|CONFIRMED|SAVED|FAILED|UNKNOWN",
    "payloadHash": "可选保存负载哈希",
    "verified": false,
    "newSnapshotHash": "可选写后快照哈希"
  },
  "issues": [{"severity": "BLOCKING|WARNING", "code": "稳定问题代码", "message": "问题说明"}],
  "nextAction": "下一步或 null"
}
```

## 约束

- JSON 使用 UTF-8，模板 ID 保持字符串，避免跨运行时整数精度变化。
- `targets` 只包含用户本次明确范围；不复制完整模板规则。
- 默认不记录试算的原始样例值，只记录依赖 code、设置和结果。用户明确要求可恢复样例时，先说明其中可能包含敏感薪资数据并确认输出位置。
- 公式、字段名、试算结果和错误文本属于敏感业务数据；只在用户指定范围内展示。
- 用户确认摘要使用目标项目名称、依赖项目名称、公式来源名称、公式格式名称、进位规则名称和结果状态；`field.code`、依赖 code、`mode/sourceKind/validation.status/calculation.status/save.status` 等机器值只保留在产物内部。code 公式只有在用户明确要求技术公式时展示。
- `COMPLETE` 只用于用户目标对应阶段全部满足完成条件；写入未知或读回不一致使用 `UNKNOWN`。
