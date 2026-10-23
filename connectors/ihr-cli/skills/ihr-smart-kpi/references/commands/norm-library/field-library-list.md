# `ihr-cli smart-kpi field-library +list`

查询当前公司可用于新建指标的字段基础列表。

## 何时使用

- 新建指标前必须调用，用当前字段定义构造底稿。
- 不进入指标模板导入流程。

## 参数

无业务参数。不接受 `--json`、`--stdin`、筛选或分页。

可使用通用 `--pretty`、`--output-file`、`--expected-env` 和 `--dry-run`。

## Agent 安全规则

- 字段 ID 和元数据只能来自本命令结果，禁止硬编码或猜测。
- 字段缺失、重名或元数据不完整时停止。
- 禁止身份字段注入、raw API 和自写 HTTP。
