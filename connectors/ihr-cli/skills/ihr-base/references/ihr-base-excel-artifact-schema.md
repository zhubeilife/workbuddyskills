# Excel 提取产物 Schema

当前支持的 `schemaVersion` 为 `1.0.0`。

## 目录结构

```text
<output-dir>/
|-- manifest.json
|-- workbook.json
|-- issues.json
`-- worksheets/
    `-- NNN-cells.jsonl
```

`manifest.json` 最后写入，是完成标记。每个 worksheet 文件按工作簿顺序使用三位序号；JSONL 每行对应一个实际存储在 OOXML 中的单元格，包括只有样式而没有值的单元格。

## `manifest.json`

- `schemaVersion`：必须为受支持版本。
- `status`：完整成功时必须为 `complete`。
- `source`：`fileName`、`absolutePath`、`sizeBytes`、`modifiedAt`、`format`、`sha256`、`hasMacros`。
- `workbook`：活动工作表索引、定义名称数、外部链接数和数据连接数。
- `worksheets[]`：顺序、名称、可见性、范围、`cellsFile`、单元格/公式/合并区域/批注/图片数量。
- `artifacts`：`workbook.json` 与 `issues.json` 的相对路径。
- `totals`：工作表、单元格、公式和警告总数。

## `workbook.json`

包含文档属性、应用属性、自定义属性、工作簿与计算属性、定义名称、OOXML 部件索引，以及每张工作表的以下元数据：

- 可见性、已用范围、冻结窗格和合并区域；
- 显式行高、列宽、隐藏行列及行列样式；
- Table、自动筛选、数据验证、条件格式、批注、图片和表单控件。

个别可选元数据读取失败时记录 `WARNING`，不得自行补值。

## worksheet JSONL

每行包含：

- 工作表索引/名称、单元格地址、行号、列号和 OOXML 存储类型；
- `rawValue`、`resolvedValue`、`displayedValue`；
- `styleId`、数字格式 ID 与自定义数字格式；
- 公式文本、公式类型/范围、缓存值、引用列表和外部引用标记；
- 所属合并区域和超链接。

`rawValue` 或 `formulaCachedValue` 为 `null` 表示源 OOXML 没有对应值，不能推断为空字符串或计算结果。公式不会在提取时重新计算。

## `issues.json`

包含 `schemaVersion` 和 `issues[]`。每个问题有 `severity`、`code`、`message`、可选 sheet/location。

- `WARNING`：提取已完成，但对应可选元数据不可用。
- `BLOCKING`：提取不完整，禁止继续使用任何部分产物。

## 校验流程

1. 解析 `manifest.json`，验证 `status=complete` 与 Schema 版本。
2. 使用当前环境可用的本地只读哈希能力计算源文件 SHA-256，与 `manifest.source.sha256` 比较。无法计算时停止并说明未能完成校验。
3. 解析所有相对路径，拒绝绝对路径和逃逸出产物目录的路径；确认文件全部存在。
4. 验证 `workbook.json`、`issues.json` 的 Schema 版本与 manifest 一致。
5. 验证 worksheet 索引连续且不重复；逐个读取 JSONL，确认合法行数等于 `cellCount`，公式记录数等于 `formulaCount`。
6. 汇总 worksheet 计数，与 `totals` 比较；确认 `issues.json` 不含 `BLOCKING`。

不要因为文件较大而只抽样后宣称完整。可以流式校验 JSONL，但必须遍历全部记录。
