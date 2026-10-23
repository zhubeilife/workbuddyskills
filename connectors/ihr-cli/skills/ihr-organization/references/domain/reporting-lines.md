# 汇报关系

## 对象和关系

汇报关系树以员工为节点，不以部门为节点。一个员工可能存在不同汇报类型的关系；“直属上级”“行政汇报”“专业汇报”等显示名称必须解析为当前租户有效的 `reportToType` 协议值。

## 查询前提

- 必须有唯一目标员工 `staffId`（或命令兼容的 `reportStaffId`）。姓名、工号等自然语言线索先在员工领域解析为唯一员工。
- 必须有有效 `reportToType`。用户给显示名称时，使用当前租户的 `Enum.DirectManagerType` 选项查询做精确匹配；唯一匹配后提交 `codeValue`。
- `showLevel` 是向下员工节点层级，`showParentLevel` 是向上员工节点层级；二者不是部门层级，也不是分页。

## 禁止推断

- 部门父子关系不能推导员工汇报关系，汇报关系也不能改写组织树。
- 返回 `hasAuth=false`、空树或缺少节点时，不能推断员工不存在或没有上级；可能是数据权限范围。
- 不能把 `DIRECT` 等历史或猜测值当作当前协议值，也不能把中文显示名称直接传给命令。

## 汇报关系对象的固定字段

| 字段 | 字段类型 | 业务含义 | 适用结果 | 关键约束 |
| --- | --- | --- | --- | --- |
| `staffId` | `string` | 关系树节点员工标识 | `+reportToTree` | 当前结果为字符串；不能与部门 ID 互换 |
| `parentStaffId` | `string` | 当前节点的父员工标识 | `+reportToTree`（若返回） | 只解释当前汇报树，不是部门父节点 |
| `staffName` | `string` | 员工名称 | `+reportToTree` | 受员工数据权限影响 |
| `departmentId` | `number` | 员工节点所属部门标识 | `+reportToTree`（若返回） | 不把它当作汇报关系标识 |
| `departmentName` | `string` | 员工节点所属部门名称 | `+reportToTree`（若返回） | 名称仅作展示和消歧 |
| `positionName` | `string` | 员工节点职位名称 | `+reportToTree`（若返回） | 不等于职务定义 |
| `jobTitleName` / `positionLevelName` | `string` / `string` | 员工节点职务/职级名称摘要 | `+reportToTree`（若返回） | 不据此替代 Organization 定义查询 |
| `staffNo` | `string` | 员工工号 | `+reportToTree`（若返回） | 仅用于展示和消歧 |
| `staffType` / `sex` | `string` / `string` | 员工类型/性别 | `+reportToTree`（若返回） | 受权限影响，不改变关系判断 |
| `enrollInDate` | `string(date)` | 入职日期 | `+reportToTree`（若返回） | 不等于汇报关系生效日期 |
| `enrollWorkYears` | `number` | 入职本公司工龄摘要 | `+reportToTree`（若返回） | 仅作返回摘要 |
| `workPhone` / `workEmail` / `mobileNo` | `string` | 工作联系方式/手机号 | `+reportToTree`（若返回） | 按共享数据保护规则展示 |
| `companySiteName` | `string` | 员工工作地点名称摘要 | `+reportToTree`（若返回） | 不等于实际打卡地点 |
| `staffImageId` | `string` | 员工头像标识 | `+reportToTree`（若返回） | 仅作展示引用 |
| `isGroup` | `boolean` | 是否为多人组节点 | `+reportToTree`（若返回） | 不表示组织部门 |
| `reportToType` | `string` | 当前租户汇报类型协议值 | 请求上下文 | 必须从有效选项或用户协议值确认；`ReportToTree` 节点不返回该字段 |
| `showLevel` | `integer` | 向下员工层级 | 请求上下文 | 不等于部门树深度 |
| `showParentLevel` | `integer` | 向上员工层级 | 请求上下文 | 不等于祖先部门数 |
| `hasAuth` | `boolean` | 当前节点是否可见 | `+reportToTree` | `false` 不证明员工不存在 |
| `children` | `array<object>` | 当前汇报类型下的下级员工 | `+reportToTree` | 不自动扩大层级 |

`children` 的扩展节点仍是同一关系结果；`className` 等展示字段不属于业务语义。当前返回的是汇报关系树结果，没有公开独立关系 ID；不能混用其他服务结果中的 `id` 字段，也不能由节点字段推断部门父子关系或员工完整组织权限。
