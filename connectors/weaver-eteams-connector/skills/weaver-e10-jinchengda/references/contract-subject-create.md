# 新建签约主体（写操作）

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


- operation：`contract.subject.create.prepare` -> `contract.subject.create.apply`
- 方法/路径：`POST /api/ebuilder/form/dataset/v2/saveFormData`
- 风险：`read-before-write` / `high-risk-write`

## 输入

| 字段 | 必填 | 说明 |
|---|---|---|
| `objId` | 是 | 表单对象 ID，来自 [`contract-signing-subjects.md`](contract-signing-subjects.md) 第 ② 步 |
| `mainTable` | 是 | 主表字段对象，键使用实际数据键，至少 1 个字段 |
| `details` | 否 | 明细表数据，键按 `detail1`、`detail2`… 传入 |
| `fieldNoFindIgnore` | 否 | 字段不存在是否忽略，默认 `"true"` |
| `doAction` | 否 | 是否执行 action，默认 `"false"` |
| `verify` | 否 | `{ field, value }`，写前查重条件 |

CLI 会把输入转成 `{ datajson: { header: { objId }, datas: [{ mainTable, ...details }], operationinfo: { fieldNoFindIgnore, doAction } } }`。

## 写前确认

`prepare` 会返回脱敏摘要 `preview`（字段数量 + 每个字段值的掩码），**必须先展示给用户并获得明确确认**后才执行 `apply`。

若传入 `verify`，`prepare` 会先用 `getAllData` 按 `field=value` 查重；命中记录时抛 `policy/already_exists` 并停止，提示用户复用已有记录而不是重复新建。

## 调用示例

Windows PowerShell：

```powershell
weaver-work-cli --json contract run contract.subject.create.prepare --input-json '{"objId":"67890","mainTable":{"clm_party_name":"XX科技有限公司"},"verify":{"field":"clm_party_name","value":"XX科技有限公司"}}'
weaver-work-cli --json contract run contract.subject.create.apply --input-json '{"objId":"67890","mainTable":{"clm_party_name":"XX科技有限公司"},"continuation":"PREPARE_CONTINUATION","confirm":true}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.subject.create.prepare --input-json '{"objId":"67890","mainTable":{"clm_party_name":"XX科技有限公司"},"verify":{"field":"clm_party_name","value":"XX科技有限公司"}}'
weaver-work-cli --json contract run contract.subject.create.apply --input-json '{"objId":"67890","mainTable":{"clm_party_name":"XX科技有限公司"},"continuation":"PREPARE_CONTINUATION","confirm":true}'
```

## 成功判定

1. HTTP 200 且 `message.code = "0"`。
2. `data.datajson.status` 为 `true` 且 `data.datajson.dataIds` 非空。
3. CLI 在 `apply` 中校验这两项；不满足时返回 `partial/write_uncertain`（退出码 11），此时先用 `contract.subject.query` 确认是否已创建，**不盲目重试**。

成功后保存返回的 `dataIds`，用于后续详情、修改和删除操作。

## 错误与边界

| 场景 | 表现 | 处理 |
|---|---|---|
| `mainTable` 为空 | `policy/empty_main_table` | 停止，补齐主表字段 |
| 查重命中 | `policy/already_exists` | 停止，与用户确认是否复用已有记录 |
| `apply` 缺少 `confirm` | `confirmation/required`，退出码 10 | 带 `confirm: true` 重新调用 |
| 输入与 `prepare` 不一致 | `validation/target_changed` | 重新 `prepare` |
| 网络中断 | `partial/write_uncertain`，退出码 11 | 停止，只补一次查询确认 |

## 注意

- 字段键规则：系统字段直接用 `name`；自定义字段（`name` 等于 `id`）改用 `config.dataKey`；**禁止用字段 `text` 作为键**。选择字段值用选项 ID。
- 主体名称、证件号、联系方式、银行账号属于敏感信息；CLI 的 `preview` 已脱敏，回复用户时也不要贴完整证件号或银行账号。
- 测试数据命名建议使用 `WB-SKILL-TEST-<日期>-<随机串>`，便于识别和清理。
