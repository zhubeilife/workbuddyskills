# Flex Meta 命令

本文件补充 Flex Meta Shortcut 和已注册 metadata command 的返回和业务边界。完整 flags 以各命令 `--help` 为准，Shortcut 使用对应的精确 Shortcut Schema，metadata command 的输入输出结构以 `schema` 为准。

## 当前公开命令

| 命令 | 关键输入 | 业务返回 |
| --- | --- | --- |
| `staff +flexMetaList` | `--kind all/basic/fixed/custom`，默认 `all` | 当前租户过滤后的 Flex Meta 列表 |
| `staff flex-meta get` | `--meta-data-id`，必须来自已确认的 Flex Meta 列表 | 一份 FlexMetaData 详情及字段配置；业务 payload 位于 metadata response body 中 |
| `staff +flexMetaGet` | `--meta-data-id`，必须来自已确认的 Flex Meta 列表 | 一份 FlexMetaData 详情及字段配置；使用 Shortcut envelope |
| `staff +flexMetaSortableFields` | 已知 `--meta-data-id` | 该元数据的可排序字段列表 |
| `staff +flexMetaValueList` | 已知 `--code-value-id`；可选 `--parent/--filter-disable` | 平铺选项数据，通常位于 `response.data[]` |
| `staff +flexMetaValueTree` | 已知 `--code-type-id` 与 `--group-code` | 服务端树形选项结构 |

Shortcut 使用公共 `success/command/request/response` envelope。返回可能包含未声明字段，未声明字段只作为业务数据，不能用于推导新的命令能力。

## 选项使用规则

- 平铺选项以 `codeValue` 作为业务协议值，以 `displayName` 作为展示名；不能用选项记录 `id` 或展示名替代协议值。
- 需要后续写入时优先显式过滤停用项，并再次检查 `isValid`。
- 名称无匹配时停止；多匹配时展示最小候选并请用户确认，不取第一条。
- 树形选项保持服务端父子关系，不递归补查其他组。

## 详情与字段发现

- `staff flex-meta get` 是当前 ACTIVE 的 metadata command；执行前必须使用已确认的 `metaDataId`，不能把 `metaCode`、`entityName` 或字段展示名当作 ID。
- `staff +flexMetaGet` 是兼容的 Shortcut 入口，与 metadata command 使用同一业务详情目标，但 envelope 不同。
- 详情返回的字段定义、`fieldName`、`fieldType` 和选项来源用于后续动态字段查询；返回中包含的内部或敏感字段仍按 Shared 数据保护规则处理。
- 已有真实 `fieldName` 时仍可通过花名册 `--fields` 查询员工值；只有字段中文名、Meta ID 或 `fieldType` 无法唯一确认时才停止。
- `+flexMetaSortableFields` 只证明排序字段，不等于完整字段详情。

## 详情查询的安全边界

`staff flex-meta get` 和 `staff +flexMetaGet` 使用同一详情目标，均按 `MEDIUM / CONFIRM_REQUIRED` 处理。执行前必须取得用户对本次具体 `metaDataId` 查询的明确确认；不能因为该 ID 来自当前租户的列表，就跳过确认或把它当作已完成授权。

当前详情接口没有独立的功能权限或员工数据范围保护，响应可能包含 `updateOperatorMobile` 等更新操作人信息。Agent 必须：

- 在执行前说明上述风险和查询目的；
- 只展示用户请求所需的元数据字段，手机号等敏感值不得原样回显；
- 不把租户上下文、单 ID 确认或 CLI 的只读属性解释为后端授权；
- 权限、结构或返回范围无法解释时停止，不改走 raw API、完整 URL、裸 HTTP 或自写客户端。

## 共同边界

- 这些命令均为租户级只读能力，一次只查询当前目标，不批量枚举 Meta 或选项类型。
- JSON/stdin 与分项 flags 互斥；身份上下文由会话注入。
- 远端或结构错误不自动重试，不改走 raw API。
