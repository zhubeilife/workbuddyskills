# `ihr-cli smart-kpi process +list`

- 共享契约：[`ihr-cli-common-command-contract.md`](../../../../ihr-shared/references/ihr-cli-common-command-contract.md)

查询可用于考核模板权限配置的考核流程候选。

## 何时使用

- 构造权限步骤时按考核对象取流程候选。

## 参数

| 参数 | 类型 | 必填 | 默认值 | 范围 | JSON 字段 | 业务说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `--assessment-target` | string | 是 | 无 | STAFF / ORGANIZATION | `assessmentTarget` | 考核对象 |
| `--data-type` | string | 否 | KPI | KPI / OKR / OBJ | `dataType` | 业务类型，考核模板用 KPI |

flags 与 `--json` / `--stdin` 互斥。禁止身份字段。可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。
只读，不做流程管理写入。

## Agent 安全规则

- 不新增角色或用户列表命令。
- 禁止 raw API。
