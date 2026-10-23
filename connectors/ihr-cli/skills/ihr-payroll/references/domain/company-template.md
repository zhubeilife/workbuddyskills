# 公司薪资模板

公司薪资模板使用 `payrollConfigId` 定位；用户只给名称时按第 3 节精确匹配。当前公开能力覆盖按名称列出已有模板、来源选择与创建、完整薪资项目配置保存，以及页面默认考勤计薪规则保存。三个阶段各自验证，不能压缩成一个“模板已完成”状态。

## 1. 分步业务模型

| 阶段 | 目标 | 主要命令 | 完成证据 |
| --- | --- | --- | --- |
| 第一步：创建模板 | 创建空白模板或基于系统模板创建公司模板 | `companyTemplate +system-list`、`+create` | 返回正整数 `payrollConfigId`，且创建结果与确认的名称和来源一致 |
| 第二步：保存项目 | 以最新快照为基线保存完整分组和项目集合 | `companyTemplate +list`（仅名称时）、`+snapshot`、`+addable-fields`、`+save-rules` | 返回 `verified=true`，模板身份和最新保存内容一致 |
| 第三步：保存默认考勤规则 | 保存页面当前默认的考勤计薪配置 | `companyTemplate +attendance-default` | 返回 `saved=true`、`savedCount=1`、相同模板 ID 和 `settingsSource=PAGE_DEFAULTS` |

第一步成功不等于第二步已配置；第二步成功不等于第三步已保存；三个阶段完成也不证明模板已经关联员工、参与核算或产生台账。

## 2. 创建规则

- 创建来源只使用 Help/Reference 当前公开的 `EMPTY_TEMPLATE` 或 `SYSTEM_TEMPLATE`。
- 选择系统模板前先查询候选；唯一候选可自动绑定 ID，多候选必须按名称确认。
- 当前公开创建固定 `salarySplit=false`。不允许通过额外 JSON 字段覆盖租户、用户或未公开配置。
- dry-run 后确认模板名称、来源、系统模板名称（如有）和“按工时拆分工资：关闭”，然后只执行一次。
- 创建超时或连接中断时结果未知。可执行 `companyTemplate +list --name <模板名称>` 按名称回读；零命中时停止并提示用户在页面核验，不自动重试创建。

## 3. 按名称定位已有公司模板

用户提供已有模板名称，或选择使用公司中已有模板继续配置时，执行 `companyTemplate +list`（可带 `--name`），从返回列表按完整名称精确匹配：

- 唯一命中：内部绑定后继续第二步或用户指定阶段
- 多命中：展示模板名称、配置阶段名称和按工时拆分工资状态，请用户选择
- 零命中：当前公司没有该名称的启用中公司模板，停止

命中项 `salarySplit=true` 时按 snapshot/save-rules 现有规则停止。选择项使用模板名称。

## 4. 保存完整项目集合

1. 使用当前 `payrollConfigId` 读取最新 snapshot，保留完整 `rules` 和 `snapshotHash`。
2. 如需增减项目，读取 `companyTemplate +addable-fields --for-rules` 返回的可用项目和 `ruleField`。
3. 在内存或受控产物中生成新的完整集合；不得把局部项目数组当作增量提交。
4. dry-run 后向用户说明分组数、项目数、增加项、删除项和会改变的公式/设置。
5. 用户确认后只执行一次 `companyTemplate +save-rules`。哈希冲突必须重新读取、重新展示差异并重新确认。返回引用尚未加入当前薪资表时，读取[补齐公式引用项目](../use-cases/company-template-configure/missing-formula-reference.md)。

模板名称、调薪调整、其他批量操作、月标准计薪天数和任意考勤参数不属于当前第二步公开输入。

## 5. 默认考勤计薪规则

第三步只保存页面当前默认设置，不向用户询问或推断具体考勤计划、计薪天数和其他参数。它不查询考勤日报、月报或月结，也不改变 Attendance Domain 的任何业务状态。

## 6. 复杂目标导航

公司模板有两条不能混用的创建路径：空白/系统来源的分步配置，以及把工作簿转换成完整模板。先判断工作簿是不是本次模板的输入，再读对应 Guide。`route-index.yaml` 的 useWhen/avoidWhen 与本节一致。

工作簿是本次模板输入，当且仅当当前请求要用一份 `.xlsx`/`.xlsm` 生成或填写公司模板。新上传、路径，或沿用对话里已给出、且本轮仍在使用的文件，都算输入；用户怎么称呼该文件不影响判断。

工作簿不是本次模板输入，当且仅当没有工作簿，或用户明确不用表头/公式来填模板。

| 判断 | 读取 |
| --- | --- |
| 工作簿是输入，目标是可用的完整公司模板 | [从 Excel 创建模板](../use-cases/template-from-excel/guide.md) |
| 工作簿不是输入，创建或分步配置空白/系统模板 | [公司模板配置](../use-cases/company-template-configure/guide.md) |
| 工作簿是输入，明确只要识别主表 | [表格识别](../use-cases/table-identify/guide.md) |
| 工作簿是输入，明确只要匹配表头、不生成模板 | [薪资项目匹配](../use-cases/salary-field-match/guide.md) |
| 明确只要修改已有模板公式 | [公式编辑](../use-cases/formula-edit/guide.md) |

空白 CREATE 只建立模板记录，不会映射工作簿列。因此「要一个新模板名称」「另做一份」「不改已有模板」只决定模板身份，不能把已是输入的工作簿降级为无关附件。

工作簿是输入、也要处理公司模板，但上表不唯一时，只问一个分流问题，列出仍可能的流程。选定前不执行 `companyTemplate +create`。进入 Excel 建模板后，第一停点是三张全量确认表，不是 CREATE。

这些 Use Case 依赖本 Domain 的业务语义、规则约束和 CLI 契约。它们是按需加载的目标指南，不是可独立安装的 Skill；Agent 最终执行公开 CLI 命令。
