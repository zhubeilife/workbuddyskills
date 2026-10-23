# SMART-KPI 指标模板字段转换

本 reference 是指标模板文件导入的字段元数据、字段值转换和前端等价预校验规则。公式文本不是普通字段值；字段计算公式和指标评分公式必须另行完整执行 [Formula Conversion 流程](formula-conversion.md)。

## 1. 元数据与映射边界

1. 字段元数据只能来自当前 `struct`、完整 `detail` 或客户已确认的指标库候选。
2. 文件表头、单元格格式和相似名称只能用于提出映射建议；客户确认后才能写入对应字段值。
3. 不得根据文件生成或修正字段 ID、`fieldProperty`、`fieldEnterRule`、`okrFieldLibraryId`、`itemFieldId`、`fieldExtraDetail`、`formulaCalculationRule`、`fetchDataRuleId`、单位配置或选项配置。
4. 构造保存字段时，先把原始底稿字段投影到 `norm-template +save` 的 `FieldValueParam` 白名单：`itemFieldId`、`fieldDefaultCode`、`value`、`fieldProperty`、`okrFieldLibraryId`、`fieldExtraDetail`、`formulaCalculationRule`、`fieldEnterRule`、`kpiNormFieldId`、`fieldName`、`fieldNameEn`、`fetchDataRuleId`、`unitName`、`showName`。只复制同名保存字段和本 reference 明确的网页端重映射；`struct/detail` 或指标库响应中的展示字段、临时字段和其他未声明 key 一律丢弃，不能整包复制原始字段对象。
5. 白名单投影完成后，再结构化深拷贝每个保留 key 的值，保留源 key 是否存在、JSON 标量类型、数组/对象结构和 `null`；不得用带类型默认值的脚本或手工 helper 重新创建 `fieldExtraDetail` 等元数据。尤其不能把底稿中的 `null` 转成空字符串、零或空对象。
6. 普通新建字段按 `columnField.id -> itemFieldId` 重映射。指标库字段按 `fieldDefaultCodeValue -> fieldDefaultCode`、`defaultValue -> value`、指标库字段 `id -> kpiNormFieldId` 重映射；指标库响应中的枚举 `fieldDefaultCode` 不是保存所需的整数码，必须丢弃。与项目字段匹配时，再按项目 `columnField.id -> itemFieldId` 重映射并取项目字段的 `showName`；指标库额外字段的 `itemFieldId` 为 `null`。重映射前后的值仍按上一条结构化深拷贝。
7. `fieldExtraDetail.dateShowType` 缺失或为 `null` 时保持原状；非空时只能原样保留 `DATE_SHOW_1`、`DATE_SHOW_2`、`DATE_SHOW_3`、`DATE_SHOW_4`。空字符串或其他值必须在预览前阻断，不能发送给保存接口。
8. 指标名称使用当前底稿的指标名称识别字段，客户展示使用该字段的 `showName`。指标名称是当前编辑器唯一通用必填字段；其他必填、长度、精度和范围以当前字段元数据为准。
9. 未确认的列、行或字段映射不进入保存值。新建字段从底稿基线开始，没有基线时为 `null`；更新时未提及字段默认保持完整详情中的保存白名单值。

## 2. 文本、数值和进度

### 文本

- 单行和多行文本保留客户确认的业务文本，并按当前字段长度、必填和字符约束校验。
- 公式样式文本不能因为以 `=` 开头就自动成为公式，也不能作为普通值绕过 Formula Conversion。

### 数值与动态属性

- `NUMBER` 和 `DYNAMIC_PROPERTIES` 使用十进制语义，按当前字段精度、上下界和后端数值边界校验。
- 不从展示格式推断缩放倍数、货币倍率或单位换算；存在“万元/元”“百分比/小数”等口径歧义时先让客户确认。

### 进度

- `PROGRESS` 按当前字段配置范围校验，通常为 0 到 100。
- `50%` 不能未经确认地保存为 `0.5` 或 `50`；先确认网页端字段使用的实际数值口径。

## 3. 单选、多选、分类和单位

### 单选

- 只使用当前 `fieldExtraDetail` 中的选项集合。
- 客户可读选项必须唯一解析为一个当前选项 ID；零候选或多个同名候选都阻止预览确认。
- 预览展示选项文案，保存使用已确认选项 ID；不得保存来源文案代替 ID。

### 多选

- 按客户确认的分隔规则拆分来源值，每项分别唯一解析到当前选项。
- 去重后保留客户确认顺序，保存有序选项 ID 数组，预览展示文案列表。
- 任一项未命中或有歧义时阻止当前字段，不能只保存已匹配的部分选项。

### 指标分类

- 遇到 `NORM_TYPE` 时调用 `ihr-cli smart-kpi norm-category +tree` 查询当前分类树。
- 只按当前分类名称解析；同名多节点时展示完整分类路径并由客户确认。
- 保存客户确认的分类 ID，预览展示路径和名称；不得把来源名称或未确认 ID 直接写入。

### 单位

- 需要设置或修改单位时调用 `ihr-cli smart-kpi unit +list`。
- 来源单位必须唯一匹配当前公司合法单位；不存在或有歧义时阻止预览确认。
- 不根据相似文本自动新建单位或换算数值。

## 4. 日期、日期时间和日期范围

### 日期

- `DATE` 表示日历日期，不做时区换算。
- 保存值保留客户确认的日历日；预览按当前 `fieldExtraDetail.dateShowType` 展示，例如 `2026-08-05`。

### 日期时间

- 无时区 `DATE_TIME` 按运行 Agent 客户端的系统时区解释，不能固定增加或减少 8 小时。
- 来源明确携带时区时保留同一时刻，并按当前客户端系统时区生成客户预览。
- 客户预览不显示 `UTC`、`GMT`、`Z` 或技术偏移标记。

### 日期范围

- 起止值必须同时存在，开始不得晚于结束。
- 每个无时区端点按客户端系统时区解释；明确时区端点保持同一时刻。
- 不能只保存合法的一端，也不能根据当前时区擅自移动日历日期。

## 5. 指标分值范围、权重和内置值

### 指标分值范围

- 普通 `NORM_SCORE_SCOPE` 保存 `{startInterval,endInterval}`；两端必须完整、起点不大于终点并满足当前字段边界。
- `DYNAMIC_SCORE_RANGE` 不接受来源文件覆盖范围，使用当前模板规则计算：`startInterval=0`，`endInterval=weight/100*indicatorBaseValue`，结果按 8 位小数精度处理。
- 预览展示客户可读范围，不能把对象序列化文本当作业务值。

### 权重

- 内置权重字段以 `fieldDefaultCode=20` 识别，单位固定为 `%`。
- 权重值必须位于 0 到 100，并继续执行当前项目、维度和模板的权重合计规则。
- 权重字段不得继承其他数值字段的“元、万元、百万”等单位；该规则不能套用到非权重数值字段。

### `INCR` 和 `BUILT_IN`

- 直接沿用 `struct`、`detail` 或已确认指标库候选中的基线 `value`，并按原值展示。
- 可空字段不能仅因类型为 `INCR/BUILT_IN` 就阻断，也不能从文件生成替代值。

## 6. 附件、员工自选和数据引用

### 附件

- 新建时不能从客户文件构造附件；更新时只能保留完整 `detail` 中已有附件关系。
- 保存前把已有附件值投影为仅含 `fieldId` 的对象；缺少 `fieldId` 时阻止确认。
- 不得把 `fileName`、`size`、`type`、`url`、`downloadUrl`、`previewUrl`、token 或附件内容写入保存载荷或过程状态。

### 员工自选

- 不能由文件新建或修改员工自选角色、节点、人员或选项配置。
- 更新时只允许从完整 `detail` 原样保留；来源请求变更时阻止受影响字段。

### 数据引用

- 不能由文件新建或修改 `DATA_QUOTE` 取数规则；更新时从完整 `detail` 保留。
- 唯一例外是客户已确认把合资格的 `NUMBER/PROGRESS` 字段从 `DATA_QUOTE` 切换为 `FORMULA_CALCULATION`：该变化必须按 Formula Conversion 处理，并按网页端规则把旧 `value` 和 `fetchDataRuleId` 清为 `null`。

## 7. 公式边界

- 来源公式必须先判定为字段计算公式、指标评分公式或明确不导入。
- 普通新建指标或手动评分指标不能仅凭文件公式创建自动评分配置。
- 字段公式只允许合资格的 `NUMBER/PROGRESS` 字段按 Formula Conversion 切换录入方式；不能修改字段类型或字段 ID。
- 不支持、待确认或存在角色歧义的公式不得进入普通字段值、后端公式校验或保存预览。
- 本 reference 不复制公式函数、语法、变量、循环依赖和四字段配置协议；这些内容只以 Formula Conversion reference 为准。

## 8. 预览前检查

对每个字段至少检查：

- 字段来自当前项目底稿或客户确认的指标库候选。
- 字段对象先完成保存白名单投影且不含响应专用 key，再结构化深拷贝每个保留值；未修改元数据的 key 存在性、类型、嵌套结构和 `null` 均未变化，`dateShowType` 不为空字符串或未知枚举。
- 必填、长度、类型、精度、上下界和数值口径合法。
- 选项、分类和单位已经唯一解析。
- 日期、日期时间和范围满足当前展示与时区规则。
- 分值范围、权重和动态范围满足当前模板规则。
- 附件、员工自选和数据引用没有被来源创建或修改。
- 公式已转入 Formula Conversion，未作为普通字段值透传。
- 预览同时展示来源列、目标 `showName`、客户可读值、实际保存值类型、单位及阻断原因。

任何字段值、映射、选项、分类、单位、录入方式或公式决定变化后，原校验、预览指纹和保存确认失效，必须按 [导入过程状态](session-state.md) 重新记录、构造、校验和确认。
