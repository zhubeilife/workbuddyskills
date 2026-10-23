# 微电网 MCP 工具完整参考

数据服务由微电网平台 MCP 连接器提供。所有业务查询前必须先调用 `microgrid_list_user_data_scopes`，并将返回的 `spaceId` / `dataUnitId` 原样传入。

## 公共约定

| 约定项 | 说明 |
|--------|------|
| 时区 | Asia/Shanghai 业务时间 |
| 缺数 vs 零值 | 缺失日/时不补零（不返回）；返回 0 = 有记录但值为 0 |
| 当日值 | 日级/小时级当天数据随统计任务运行持续更新 |
| 日/时关系 | 不承诺日级与小时级严格相等 |
| 前置要求 | 先调 list_user_data_scopes，spaceId/dataUnitId 原样传入 |

## 1. microgrid_list_user_data_scopes

- **类别**：scope × discovery
- **用途**：列出账号被授权的微电网数据范围（spaceId + 可选 dataUnitId）
- **参数**：无
- **返回**：`{"scopes":[{"spaceId":"...","name":"..."},{"spaceId":"...","dataUnitId":"...","name":"..."}]}`
- **规则**：默认优先全空间 scope（无 dataUnitId）；用户明确指定数据单元时才用带 unit 的 scope

## 2. microgrid_query_daily_load_electricity

- **类别**：load × daily（kWh）
- **用途**：日级一级负荷电量，口径排除其他(100)/PV(102)/ESS(101) 电表
- **参数**：`spaceId`（必填）、`dataUnitId`（可选）、`startDate`、`endDate`
- **格式**：YYYY-MM-DD，含两端，≤366 天，允许未来日期
- **返回**：`{"days":[{"date":"2026-08-01","loadEp":123.4}]}`

## 3. microgrid_query_hourly_load_electricity

- **类别**：load × hourly（kWh）
- **用途**：小时级一级负荷电量（日级对应物）
- **参数**：`spaceId`（必填）、`dataUnitId`（可选）、`startHour`、`endHour`
- **格式**：yyyyMMddHH，含两端，≤168 点（7 天）
- **返回**：`{"hours":[{"hour":"2026080115","loadEp":0.01}]}`

## 4. microgrid_query_pv_daily_generation_energy

- **类别**：pv × daily（kWh）
- **用途**：日级光伏发电量（所有并网模式合计，无 gridMergeType 过滤）
- **参数**：同 daily_load；≤366 天，允许未来日期
- **返回**：`{"days":[{"date":"2026-08-01","generationEnergyKwh":8.4}]}`

## 5. microgrid_query_pv_hourly_generation_energy

- **类别**：pv × hourly（kWh）
- **用途**：小时级光伏发电量
- **参数**：同 hourly_load；≤168 点
- **返回**：`{"hours":[{"hour":"2026080115","generationEnergyKwh":2.4}]}`

## 6. microgrid_query_ess_daily_charge_discharge_energy

- **类别**：ess × daily（kWh）
- **用途**：日级储能充电量 + 放电量
- **参数**：同 daily_load；≤366 天，允许未来日期
- **返回**：`{"days":[{"date":"2026-08-01","chargeEnergyKwh":3.2,"dischargeEnergyKwh":4.1}]}`

## 7. microgrid_query_ess_hourly_charge_discharge_energy

- **类别**：ess × hourly（kWh）
- **用途**：小时级储能充/放电量
- **参数**：同 hourly_load；≤168 点
- **返回**：`{"hours":[{"hour":"2026080115","chargeEnergyKwh":1.2,"dischargeEnergyKwh":0.8}]}`

## 8. microgrid_get_load_power

- **类别**：load × current（kW）
- **用途**：当前聚合负荷功率快照
- **参数**：`spaceId`（必填）、`dataUnitId`（可选）、`meterFilter`（可选）
- **meterFilter**：省略时默认排除 100/102/101；可自定义 `includeLevel`、`excludeElecLoadTypes`、`includeElecLoadTypes`
- **返回**：`{"loadPowerKw":12.192,"meterFilter":{...}}`
- **语义**：上游无值返回 0，无采样时间戳，0 不能证明实测为 0 或数据新鲜

## 9. microgrid_get_pv_generation_power

- **类别**：pv × current（kW）
- **用途**：当前聚合光伏发电功率快照
- **参数**：`spaceId`（必填）、`dataUnitId`（可选）、`gridMergeType`（可选：Self=自发自用 / Surplus=余电上网 / Full=全额上网，缺省为全部模式）
- **返回**：`{"generationPowerKw":86.2}`
- **语义**：上游无值返回 0，无采样时间戳

## 10. microgrid_get_ess_charge_discharge_power

- **类别**：ess × current（kW）
- **用途**：当前储能充电/放电功率快照（非负绝对值）
- **参数**：`spaceId`（必填）、`dataUnitId`（可选）
- **返回**：`{"chargePowerKw":0.0,"dischargePowerKw":35.0}`
- **语义**：⚠️ 无匹配快照时返回 **null/null**（区别于 load/PV 返回 0）；无采样时间戳

## 已知口径细节

- 日级负荷 `loadEp` 排除其他/PV/ESS 电表，是"一级负荷"口径。
- 日级/小时级返回的缺失日期是"无统计记录"而非 0，不能与 0 值日混算。
- `meterFilter` 中 `leafNode` 字段无效（sumSpaceCurrentPower 忽略该上游字段）。
- 小时格式 `yyyyMMddHH` 中 HH 为 00-23 的整点，含两端端点。
