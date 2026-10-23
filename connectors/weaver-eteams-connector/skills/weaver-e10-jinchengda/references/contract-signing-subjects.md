# 签约主体：定位与查询

## 请求头 / 认证

本文件描述的 API 请求通过 `weaver-work-cli` 执行，CLI 从 E10 登录会话自动注入以下凭证头（禁止业务输入携带）：

| 请求头 | 值 |
|--------|-----|
| `Cookie` | `<e10-login 返回的完整原始 Cookie 串>`（禁止裁剪/去重/改写） |
| `eteamsid` | `<e10-login 返回的 ETEAMSID>` |
| `User-Agent` | `AgentType=<agentType>,IsAgent=true` |

业务输入（`--input-json` / `--input`）**不得包含** `userid`、`userId`、`token`、`cookie`、`eteamsid` 等字段，用户 ID 由 CLI 从会话注入。


用途：查询我方、客户方或供应商签约主体。全部为 `read`。

## 调用链（每步只能用上一步运行时返回的 ID）

```
① 应用 Tag   ->  contract.subject.app     GET  /api/bs/ebuilder/app/tags/getAppIds   取 appId
② 表单 Tag   ->  contract.subject.form    GET  /api/ebuilder/form/obj/getObjsByTag   取 objId / formId
③ 读字段     ->  contract.subject.fields  POST /api/ebuilder/common/ds/fields        取 fields[].id / name / config.dataKey
④ 读选项     ->  contract.subject.options GET  /api/ebuilder/common/ds/options       取选项 id <-> name
⑤ 查询       ->  contract.subject.query   POST /api/ebuilder/form/dataset/v2/getAllData
```

## 准确的 Tag 字符串

| 步骤 | Tag | 说明 |
|---|---|---|
| 应用 Tag | `合同管理` | 固定值；CLI 默认也是它 |
| 表单 Tag（我方） | `我方签约主体库` | 查我方签约主体 |
| 表单 Tag（客户方） | `客户签约主体库` | 查客户签约主体 |
| 表单 Tag（供应商） | `供应商签约主体库` | 查供应商主体 |

Tag 需要 URL 编码，CLI 已处理；Agent 只需要传原始中文 Tag。

## 各 operation 输入

| operation | 必填 | 可选 |
|---|---|---|
| `contract.subject.app` | 无（默认 `tag=合同管理`） | `tag` |
| `contract.subject.form` | `appId`、`tag` | 无 |
| `contract.subject.fields` | `appId`、`objId` | `detailFieldsGroup`、`enableMerge`、`customParam`、`params` |
| `contract.subject.options` | `appId`、`objId`、`fieldName` | 无 |
| `contract.subject.query` | `objId` | `mainTable`、`pageNo`、`pageSize`、`isReturnDetail` |

请求形状说明（CLI 负责转换，Agent 只按上表传）：

- `contract.subject.fields` 走 `multipart/form-data`：`groupId=appId`、`sourceId=objId`、`sourceType=FORM`。
- `contract.subject.options` 的 query 为 `groupId=appId`、`objId`、`sourceType=FORM`、`fieldName`。
- `contract.subject.query` 的 body 为 `{ datajson: { header: { objId }, mainTable, pageInfo, operationinfo: { isReturnDetail } } }`；`mainTable` 内多个字段之间为 AND 关系。

## 调用示例

Windows PowerShell：

```powershell
weaver-work-cli --json contract run contract.subject.app --input-json '{"tag":"合同管理"}'
weaver-work-cli --json contract run contract.subject.form --input-json '{"appId":"12345","tag":"我方签约主体库"}'
weaver-work-cli --json contract run contract.subject.fields --input-json '{"appId":"12345","objId":"67890"}'
weaver-work-cli --json contract run contract.subject.options --input-json '{"appId":"12345","objId":"67890","fieldName":"111"}'
weaver-work-cli --json contract run contract.subject.query --input-json '{"objId":"67890","mainTable":{"clm_party_name":"XX科技"},"pageNo":1,"pageSize":10}'
```

macOS/Linux（bash/zsh）：

```bash
weaver-work-cli --json contract run contract.subject.app --input-json '{"tag":"合同管理"}'
weaver-work-cli --json contract run contract.subject.form --input-json '{"appId":"12345","tag":"我方签约主体库"}'
weaver-work-cli --json contract run contract.subject.fields --input-json '{"appId":"12345","objId":"67890"}'
weaver-work-cli --json contract run contract.subject.options --input-json '{"appId":"12345","objId":"67890","fieldName":"111"}'
weaver-work-cli --json contract run contract.subject.query --input-json '{"objId":"67890","mainTable":{"clm_party_name":"XX科技"},"pageNo":1,"pageSize":10}'
```

## 结果解读与边界

- ebuilder 元数据接口成功码是顶层 `code = 200` 且 `status` 不为 false；`getAllData` 成功码是 `message.code = "0"`。
- `contract.subject.app` 返回 `appIds`；`contract.subject.form` 只返回 `id`、`objName`、`showName`、`tag`，不输出完整 `appId`、`permissionId`。
- `data` 为空数组表示 Tag 在当前应用中不存在：提示用户确认 Tag 名称或换 Tag，**不使用标准环境 ID 兜底**。
- 查询无结果时如实说明；返回多条时展示候选请用户选择。
- 名称、证件、联系和银行字段不得跨表单猜测；字段键以 `fields` 接口返回为准（系统字段用 `name`，自定义字段用 `config.dataKey`，**不要用 `text`**）。
- 选择类字段的值使用选项 ID（`id`），不要使用选项名称（`name`）。

## 注意

- 新建签约主体不是本文件的范围，见 [`contract-subject-create.md`](contract-subject-create.md)。
- 企业资信、企业变更、企业监控未实现，见 [`contract-disabled-capabilities.md`](contract-disabled-capabilities.md)。
