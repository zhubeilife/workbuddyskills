# SMART-KPI 公共公式规则

本文件复制指标模板导入已验证的标准公式协议和两级校验顺序，供指标库及后续流程使用。指标模板导入继续使用独立的 formula-conversion.md，本期不得改成引用本文件。

不新增转换命令，复用 \smart-kpi formula +check\ 和 \ormula +field-check\。公共层不决定公式角色；调用流程先确认是评分公式还是字段公式。

## 标准协议
只存右侧表达式；去掉 Excel 开头一个 =，不删除表达式内部等号。变量使用最终 showName，showName 为空才用 fieldName，不输出 SMART_KPI{id}。不支持的函数、参数个数、Excel 引用、不安全空白、过深 IF、非数值结果，在保存前拦截。

## 变量
展示名与 okrFieldLibraryId 一一对应。完全重复去重，冲突则阻断。

## 四字段配置
ratingFormula、carryRule、digit、allowEditFormula。缺省时新建/新改公式使用 carryRule=rule_1、digit=digit_3。新切换字段公式默认 allowEditFormula=true；更新保留底稿布尔值。

## 字段公式切换
只有最终 NUMBER/PROGRESS（及动态数值）可改为 FORMULA_CALCULATION。切换后 value 和 fetchDataRuleId 为 null。

## 校验顺序
1. 流程确认角色和字段映射
2. 本地协议检查
3. formula +check
4. 有字段公式时 formula +field-check，且仅一项 currentField=true
5. dry-run/保存必须使用同一份已校验公式；任何变化使原校验和确认失效
后端校验请求成功但 hasError/hasCycle 视为失败。

## 指标库准入
仅 CURRENCY_NORMS + RATION + AUTOMATIC_SCORING 可构造评分公式。定性、能力素质、价值观不创建评分公式。
