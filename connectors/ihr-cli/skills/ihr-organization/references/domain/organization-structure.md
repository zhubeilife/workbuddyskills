# 组织结构

## 对象

- **部门**：组织结构中的业务单元，使用 `departmentId` 定位；父部门关系使用 `parentDepartmentId`。
- **组织树节点**：组织树中的展示节点，使用 `id/nodeId` 定位，可能代表部门或职位节点；节点是否带有 `departmentId` 以实际返回为准。
- **根节点**：不传 `departmentId` 的 `departmentChildren` 查询返回根节点下直属组织；它不是一个可随意猜测的部门 ID。
- **直属子部门**：只比当前部门多一层；使用 `departmentChildren`，不能用 `orgTree` 的递归结果代替。
- **祖先链**：当前部门及全部父级；使用 `departmentAncestors`，结果包含目标部门自身。

## 查询选择

| 用户表达 | 命令 | 关键确认 |
| --- | --- | --- |
| 看整个组织树 | `organization +orgTree` | 起点、层级、是否包含停用/虚拟节点、生效日期 |
| 看某部门直属下级 | `organization +departmentChildren` | 父部门 ID；不传则是根节点下级 |
| 看某部门所有上级 | `organization +departmentAncestors` | 唯一部门 ID |

## 约束

- 组织树中的 `children` 是部门子节点，不是员工或汇报下属。
- `showLevel` 是向下展示层级，不是分页；不自动追加更深层级查询。
- `showDisable`、`noVirtual` 会改变查询范围，扩大范围前需确认。
- `effectiveDate` 按组织树公开的生效日期参数过滤。回答时说明用了这个日期条件，不要说成已经还原了那天的完整组织。
- 组织节点中的 `onJobHeadCount`、`capacity` 等摘要不能替代 Staff 花名册或编制占用查询。

## 组织节点对象的固定字段

以下字段是当前组织树、直属子部门和父级链结果中已确认的固定字段索引。树节点的 `id/nodeId` 与业务部门 `departmentId` 可能是不同标识，类型以实际结果为准。

| 字段 | 字段类型 | 业务含义 | 适用结果 | 关键约束 |
| --- | --- | --- | --- | --- |
| `id` / `nodeId` | `string` | 组织树展示节点标识 | `+orgTree` | 当前结果为字符串；不直接当作 `departmentId` |
| `parentId` | `string` | 直接父树节点 | `+orgTree` | 当前结果为字符串；不表示员工汇报上级 |
| `departmentId` | `number` | 业务部门标识 | 三类组织查询 | 当前结果为整数；名称不能替代 ID |
| `parentDepartmentId` | `number` | 业务部门的直接父部门标识 | `+orgTree`、`+departmentAncestors`（若返回） | 不等于组织树展示节点 `parentId`，也不表示员工汇报上级 |
| `text` / `departmentName` | `string` | 节点或部门名称 | 三类组织查询 | 仅用于展示和消歧 |
| `departmentCode` | `string` | 部门编码 | 组织树、父级链 | 不保证全局唯一 |
| `type` / `organizationChartNodeType` | `string` | 节点业务类型 | `+orgTree` | 只按返回值解释 |
| `depth` | `integer` | 树节点层级 | `+orgTree` | 不等于汇报层级 |
| `departmentStatus` | `string` | 部门状态 | `+orgTree`、`+departmentAncestors`（若返回） | `+departmentChildren` 当前不公开该字段；不代替员工状态 |
| `isVirtual` | `boolean` | 是否虚拟组织 | `+orgTree` | 不等于停用 |
| `principalId` | `string` | 部门负责人标识 | `+orgTree` | 当前结果为字符串；受权限影响 |
| `principalName` | `string` | 部门负责人名称 | `+orgTree` | 负责人不等于汇报上级 |
| `principalImg` | `string` | 部门负责人头像标识 | `+orgTree`（若返回） | 仅作为展示引用，不据此定位员工 |
| `principalPosition` | `string` | 部门负责人职位名称 | `+orgTree`（若返回） | 不等于部门或汇报关系 |
| `principalIds` | `array<string>` | 部门负责人标识集合 | `+orgTree`（若返回） | 多负责人展示数据，不替代单个 `principalId` |
| `companySiteId` | `string` | 组织引用的工作地点标识 | `+orgTree` | 当前结果为字符串；不表示实际打卡地点 |
| `companySiteName` | `string` | 组织引用的工作地点名称 | `+orgTree` | 名称不能替代地点 ID |
| `costCenterCode` | `string` | 组织引用的成本中心标识或编码 | `+orgTree`（若返回） | 必须按返回字段语义解释，不把它当成本中心分组 ID |
| `costCenterCodeName` | `string` | 组织引用的成本中心名称 | `+orgTree`（若返回） | 仅为名称摘要 |
| `storeNumber` | `string` | 组织或门店编号 | `+orgTree`（若返回） | 不等于部门编码 |
| `positionNum` | `integer` | 组织节点关联的职位数量 | `+orgTree`（若返回） | 不等于员工人数或职位容量 |
| `capacity` / `totalCapacity` | `number` | 节点自身/含下级容量摘要 | `+orgTree` | 不等于编制计划数 |
| `onJobHeadCount` / `onJobTotalHeadCount` | `integer` | 节点自身/含下级在职人数摘要 | `+orgTree` | 不等于跨页去重人数 |
| `inServiceNumber` / `inServiceTotalNumber` | `integer` | 直属子部门自身/含下级在职人数摘要 | `+departmentChildren`（若返回） | 不与组织树的 `onJobHeadCount` / `onJobTotalHeadCount` 混用 |
| `establishDate` / `effectiveDate` | `string(date)` | 设立日/结果生效日 | `+orgTree` | 生效日用于过滤，不等于完整历史还原 |
| `departmentDesc` | `string` | 部门描述 | `+orgTree`（若返回） | 描述文本不改变查询策略 |
| `departmentProperty` / `departmentPropertyName` | `string` / `string` | 组织属性值及名称 | `+orgTree`（若返回） | 名称缺失时不猜测属性值 |
| `abbreviation` | `string` | 部门简称 | `+orgTree`（若返回） | 不替代正式名称或编码 |
| `remark` | `string` | 部门备注 | `+orgTree`（若返回） | 仅作业务数据展示 |
| `customField01` ... `customField10` | `string` | 租户配置的组织扩展字段槽位 | `+orgTree`（若返回） | 当前没有公开动态标签/字段定义命令；不得猜测字段名称或含义 |
| `staffInfo` | `object` | 负责人扩展信息 | `+orgTree`（若返回） | 子字段以实际返回为准，不把展示对象当员工档案 |
| `hasAuth` / `hasPrincipalAuth` | `boolean` | 节点/负责人信息是否有权限查看 | `+orgTree`（若返回） | `false` 不证明对象不存在 |
| `assignedCount` | `integer` | 组织节点兼任人数摘要 | `+orgTree`（若返回） | 不等于在职人数 |
| `showHorizontal` / `showHorizontalMap` | `boolean` / `object` | 组织图展示方向设置 | `+orgTree`（若返回） | 展示配置，不是业务关系 |
| `subDepartments` | `array<object>` | 直属下级部门集合 | `+departmentChildren` | 只多一层 |
| `data` | `array<object>` | 父级链部门集合 | `+departmentAncestors` | 通常包含目标部门自身 |
| `children` | `array<object>` | 递归下级组织节点 | `+orgTree` | 完整度受 `showLevel` 影响 |

`source`、`className` 等内部来源或展示字段不作为业务对象属性；`children` 内节点沿用同一字段规则。字段类型和容器路径属于 `PARTIAL` 过渡索引，执行前仍读取对应命令的 Help 和命令 Reference。组织自定义槽位只有原始值可见，当前不提供动态定义解析。
