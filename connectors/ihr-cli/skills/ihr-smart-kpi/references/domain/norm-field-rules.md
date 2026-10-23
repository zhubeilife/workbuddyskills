# SMART-KPI 公共字段规则

本文件是从指标模板导入已验证规则复制出来、供指标库及后续流程共用的字段值语义。指标模板导入继续使用独立的 field-conversion.md，本期不得改成引用本文件。

公共层只定义值、展示和失败语义，不定义保存 DTO。指标库保存使用 KpiNormFieldParam（defaultValue、fieldDefaultCode 枚举名）；指标模板保存仍用 FieldValueParam 及其映射。

规则按后端 FieldPropertyEnum 匹配：SINGLE_LINE_TEXT、MULTILINE_TEXT、NUMBER、DYNAMIC_PROPERTIES、PROGRESS、DATE、DATE_TIME、DATE_RANGE、SINGLE_OPTION、MULTIPLE_OPTION、NORM_TYPE、NORM_SCORE_SCOPE、ATTACHMENT、EMPLOYEE_SELF_SELECTION、BUILT_IN、INCR。

## 结构保持
深拷贝允许的结构化值，保留标量/数组/对象、key 存在性和 null。禁止 stringify 或仅按标签重建元数据。dateShowType 非空时只允许 DATE_SHOW_1/2/3/4。

## 文本、数值、进度
单行 <=2000，多行 <=10000。NUMBER/DYNAMIC_PROPERTIES/PROGRESS 不推断缩放。缺 decimalCount 时精度按 4。权重字段 okrFieldLibraryId=20 固定 0-100，单位 %。50% 这种写法有歧义时询问，不自行换算。以 = 开头的文本按公式处理。

## 选项与分类
单选/多选必须解析到当前元数据中的唯一选项 ID。分类重名展示完整路径后由客户选择。

## 日期
DATE 只展示日历日，不转换时区。DATE_TIME 有时区则保留同一瞬间并按客户时区显示；无时区按客户时区解释，不加固定 8 小时。客户可见输出禁止 UTC/GMT/Z。日期范围两端都要，开始不晚于结束。

## 范围、内置、附件、员工自选
NORM_SCORE_SCOPE 保存 {startInterval,endInterval}。BUILT_IN/INCR 展示可信 value。附件只保留文件 ID。员工自选：展示角色名、隐藏节点、相同角色合并；文件不得新建该配置。

## 指标库投影
保存使用 KpiNormFieldParam。禁止套用模板映射 fieldDefaultCodeValue -> fieldDefaultCode、defaultValue -> value。
