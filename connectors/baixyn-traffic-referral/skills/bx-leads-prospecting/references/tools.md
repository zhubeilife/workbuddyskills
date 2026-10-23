# 百型引流工具参数参考

本参考从维护的后端公开工具注册表生成，Skill版本 1.0.6。实际工具清单、权限和 capabilities 返回优先；生成文件不代表全部业务已线上验收。

只有用户请求涉及某个工具时才阅读对应段落。Schema 中 required 是必填；anyOf/oneOf 表示组合条件。不要发送未声明字段。

新增工具成功为 `{ok:true,data,requestId}`，业务失败为 `{ok:false,error,requestId}` 并带 `isError:true`；先判断 ok。六个兼容工具继续返回原业务对象；无资料 profile_get 返回 `{hasProfile:false,profile:null}`。

所有对象 ID、版本、itemId、游标及预览/冲突 revision 来自真实响应。读取与预览不修改正式资料。创建/写入按 Schema 传幂等键；同请求重试同键，变更请求使用新键。

OAuth 从宿主连接器入口完成；不手填 Cookie、不在 Skill 保存令牌。完整连接器所需的11类业务权限来自当前部署允许的scope。配套服务端策略部署后，新OAuth请求省略scope时申请allowedScopes全集，经用户同意授权；显式只读、旧grant及refresh均不会自动扩权。若缺本次动作所需权限，从宿主入口重新授权后核对capabilities_get.scopes/tools，不能靠改URL或聊天中的Token补权。全权限不代表自动执行任何写入或消费。对话启动需当前服务支持confirmation并具备jobs:write；以本会话capabilities和Schema为准。允许宿主生成只读HTML文件供预览；不支持HTML业务按钮/回调，MCP不返回HTML资源。

## capabilities_get

读取当前授权可用能力、额度限制及真实的付费确认能力。

所需权限：有效身份。

data 包含 tools、scopes、limits、limitations、observedAt、agentQuoteConfirmationAvailable、agentQuoteConfirmationMode；权限及模式以真实回执为准。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

价格与权益以真实回执为准：本包于2026-10-10核对prod公开合同，当前新报价政策为20积分/家公司；运行时仍核对真实回执。新报价的单价与上限分别取quote.unitPrice/maxCredits；有credits:read时可读取credits_get.unitPrice/onboarding。新注册正式账号的配置为200+200+200（第三项在首次成功创建任务时奖励），旧账号保留已存政策和领取资格，旧报价/任务按原单价。不要把新账号规则覆盖到旧账号，不承诺补发或重复发奖；缺scope时说明未能读取。

## profile_get

读取已保存的完整企业资料和版本；无资料返回 hasProfile:false。

所需权限：profile:read。

直接返回已保存资料（含 version、产品/行业/领域/国家）；无资料为 {hasProfile:false,profile:null}，不套新 data 包装。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "workspaceId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [],
  "additionalProperties": false
}
```

## routes_prepare

根据已保存的全部产品生成最多三条买方路线。新调用提供idempotencyKey，返回后台任务。

所需权限：routes:write。

直接返回路线任务的 id、kind、status、output等；返回 id 用作后续 routeJobId。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "profileVersion": {
      "type": "integer",
      "minimum": 1,
      "maximum": 9007199254740991
    },
    "markets": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "AL",
          "DZ",
          "AF",
          "AR",
          "AE",
          "AW",
          "OM",
          "AZ",
          "AC",
          "EG",
          "ET",
          "IE",
          "EE",
          "AD",
          "AO",
          "AI",
          "AG",
          "AT",
          "AX",
          "AU",
          "BB",
          "PG",
          "BS",
          "PK",
          "PY",
          "PS",
          "BH",
          "PA",
          "BR",
          "BY",
          "BM",
          "BG",
          "MP",
          "MK",
          "BJ",
          "BE",
          "IS",
          "PR",
          "PL",
          "BA",
          "BO",
          "BZ",
          "BW",
          "BT",
          "BF",
          "BI",
          "BV",
          "KP",
          "GQ",
          "DK",
          "DE",
          "DG",
          "TL",
          "TG",
          "DO",
          "DM",
          "RU",
          "EC",
          "ER",
          "FR",
          "FO",
          "PF",
          "GF",
          "TF",
          "MF",
          "VA",
          "PH",
          "FJ",
          "FI",
          "CV",
          "FK",
          "GM",
          "CG",
          "CD",
          "CO",
          "CR",
          "GD",
          "GL",
          "GE",
          "GG",
          "CU",
          "GP",
          "GU",
          "GY",
          "KZ",
          "HT",
          "KR",
          "NL",
          "BQ",
          "SX",
          "HM",
          "ME",
          "HN",
          "KI",
          "DJ",
          "KG",
          "GN",
          "GW",
          "CA",
          "GH",
          "IC",
          "GA",
          "KH",
          "CZ",
          "ZW",
          "CM",
          "QA",
          "KY",
          "CC",
          "KM",
          "XK",
          "CI",
          "KW",
          "CP",
          "HR",
          "KE",
          "CK",
          "CW",
          "LV",
          "LS",
          "LA",
          "LB",
          "LT",
          "LR",
          "LY",
          "LI",
          "RE",
          "LU",
          "RW",
          "RO",
          "MG",
          "IM",
          "MV",
          "MT",
          "MW",
          "MY",
          "ML",
          "MH",
          "MQ",
          "YT",
          "MU",
          "MR",
          "US",
          "UM",
          "AS",
          "VI",
          "MN",
          "MS",
          "BD",
          "PE",
          "FM",
          "MM",
          "MD",
          "MA",
          "MC",
          "MZ",
          "MX",
          "NA",
          "ZA",
          "AQ",
          "GS",
          "SS",
          "NR",
          "NI",
          "NP",
          "NE",
          "NG",
          "NU",
          "NO",
          "NF",
          "PW",
          "PN",
          "PT",
          "JP",
          "SE",
          "CH",
          "SV",
          "CQ",
          "WS",
          "RS",
          "SL",
          "SN",
          "CY",
          "SC",
          "SA",
          "BL",
          "CX",
          "ST",
          "SH",
          "KN",
          "LC",
          "SM",
          "PM",
          "VC",
          "LK",
          "SK",
          "SI",
          "SJ",
          "SZ",
          "SD",
          "SR",
          "SB",
          "SO",
          "TJ",
          "TW",
          "TH",
          "TZ",
          "TO",
          "TC",
          "TA",
          "TT",
          "TN",
          "TV",
          "TR",
          "TM",
          "TK",
          "WF",
          "VU",
          "GT",
          "VE",
          "BN",
          "UG",
          "UA",
          "UY",
          "UZ",
          "ES",
          "EH",
          "GR",
          "SG",
          "NC",
          "NZ",
          "HU",
          "EA",
          "SY",
          "JM",
          "AM",
          "YE",
          "IQ",
          "IR",
          "IL",
          "IT",
          "IN",
          "ID",
          "GB",
          "VG",
          "IO",
          "JO",
          "VN",
          "ZM",
          "JE",
          "TD",
          "GI",
          "CL",
          "CF",
          "CN",
          "MO",
          "HK"
        ]
      },
      "minItems": 0,
      "maxItems": 8,
      "uniqueItems": true
    },
    "workspaceId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "profileVersion"
  ],
  "additionalProperties": false
}
```

## routes_get

读取已知买方路线任务状态、所有路线及未覆盖产品。

所需权限：jobs:read。

data 返回路线任务的公开状态与 output、pollAfterMs；完成后路线在 output.routes。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "routeJobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "routeJobId"
  ],
  "additionalProperties": false
}
```

## route_get

读取指定路线的产品、买方类型、采购关系和核实信号。

所需权限：jobs:read。

data 含 routeJobId、profileVersion 与 route，保持返回的真实路线ID及产品关联。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "routeJobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "routeId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "routeJobId",
    "routeId"
  ],
  "additionalProperties": false
}
```

## search_draft_create

为同一份已完成路线创建空选择的找客范围草稿。

所需权限：quotes:write。

data 含 draftId、routeJobId、profileVersion、draftVersion、routeIds、targetCount、markets、state、expiresAt、missingFields；变更可能附unchanged。所有路线共享targetCount。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "routeJobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "profileVersion": {
      "type": "integer",
      "minimum": 1,
      "maximum": 9007199254740991
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "routeJobId",
    "profileVersion",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

## search_draft_get

读取本人找客范围草稿、选择和缺项。

所需权限：quotes:write。

data 含 draftId、routeJobId、profileVersion、draftVersion、routeIds、targetCount、markets、state、expiresAt、missingFields；变更可能附unchanged。所有路线共享targetCount。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "draftId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId"
  ],
  "additionalProperties": false
}
```

## search_route_add

加入一条路线；所有路线共享一个总量任务。

所需权限：quotes:write。

data 含 draftId、routeJobId、profileVersion、draftVersion、routeIds、targetCount、markets、state、expiresAt、missingFields；变更可能附unchanged。所有路线共享targetCount。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "draftId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "expectedDraftVersion": {
      "type": "integer",
      "minimum": 1,
      "maximum": 9007199254740991
    },
    "routeId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "routeId",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

## search_route_remove

移除一条路线；所有路线共享一个总量任务。

所需权限：quotes:write。

data 含 draftId、routeJobId、profileVersion、draftVersion、routeIds、targetCount、markets、state、expiresAt、missingFields；变更可能附unchanged。所有路线共享targetCount。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "draftId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "expectedDraftVersion": {
      "type": "integer",
      "minimum": 1,
      "maximum": 9007199254740991
    },
    "routeId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "routeId",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

## search_scope_set

修改本次总量（1–20家）或国家；不更改长期公司资料。空国家数组表示全球。

所需权限：quotes:write。

data 含 draftId、routeJobId、profileVersion、draftVersion、routeIds、targetCount、markets、state、expiresAt、missingFields；变更可能附unchanged。所有路线共享targetCount。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "draftId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "expectedDraftVersion": {
      "type": "integer",
      "minimum": 1,
      "maximum": 9007199254740991
    },
    "targetCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20
    },
    "markets": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "AL",
          "DZ",
          "AF",
          "AR",
          "AE",
          "AW",
          "OM",
          "AZ",
          "AC",
          "EG",
          "ET",
          "IE",
          "EE",
          "AD",
          "AO",
          "AI",
          "AG",
          "AT",
          "AX",
          "AU",
          "BB",
          "PG",
          "BS",
          "PK",
          "PY",
          "PS",
          "BH",
          "PA",
          "BR",
          "BY",
          "BM",
          "BG",
          "MP",
          "MK",
          "BJ",
          "BE",
          "IS",
          "PR",
          "PL",
          "BA",
          "BO",
          "BZ",
          "BW",
          "BT",
          "BF",
          "BI",
          "BV",
          "KP",
          "GQ",
          "DK",
          "DE",
          "DG",
          "TL",
          "TG",
          "DO",
          "DM",
          "RU",
          "EC",
          "ER",
          "FR",
          "FO",
          "PF",
          "GF",
          "TF",
          "MF",
          "VA",
          "PH",
          "FJ",
          "FI",
          "CV",
          "FK",
          "GM",
          "CG",
          "CD",
          "CO",
          "CR",
          "GD",
          "GL",
          "GE",
          "GG",
          "CU",
          "GP",
          "GU",
          "GY",
          "KZ",
          "HT",
          "KR",
          "NL",
          "BQ",
          "SX",
          "HM",
          "ME",
          "HN",
          "KI",
          "DJ",
          "KG",
          "GN",
          "GW",
          "CA",
          "GH",
          "IC",
          "GA",
          "KH",
          "CZ",
          "ZW",
          "CM",
          "QA",
          "KY",
          "CC",
          "KM",
          "XK",
          "CI",
          "KW",
          "CP",
          "HR",
          "KE",
          "CK",
          "CW",
          "LV",
          "LS",
          "LA",
          "LB",
          "LT",
          "LR",
          "LY",
          "LI",
          "RE",
          "LU",
          "RW",
          "RO",
          "MG",
          "IM",
          "MV",
          "MT",
          "MW",
          "MY",
          "ML",
          "MH",
          "MQ",
          "YT",
          "MU",
          "MR",
          "US",
          "UM",
          "AS",
          "VI",
          "MN",
          "MS",
          "BD",
          "PE",
          "FM",
          "MM",
          "MD",
          "MA",
          "MC",
          "MZ",
          "MX",
          "NA",
          "ZA",
          "AQ",
          "GS",
          "SS",
          "NR",
          "NI",
          "NP",
          "NE",
          "NG",
          "NU",
          "NO",
          "NF",
          "PW",
          "PN",
          "PT",
          "JP",
          "SE",
          "CH",
          "SV",
          "CQ",
          "WS",
          "RS",
          "SL",
          "SN",
          "CY",
          "SC",
          "SA",
          "BL",
          "CX",
          "ST",
          "SH",
          "KN",
          "LC",
          "SM",
          "PM",
          "VC",
          "LK",
          "SK",
          "SI",
          "SJ",
          "SZ",
          "SD",
          "SR",
          "SB",
          "SO",
          "TJ",
          "TW",
          "TH",
          "TZ",
          "TO",
          "TC",
          "TA",
          "TT",
          "TN",
          "TV",
          "TR",
          "TM",
          "TK",
          "WF",
          "VU",
          "GT",
          "VE",
          "BN",
          "UG",
          "UA",
          "UY",
          "UZ",
          "ES",
          "EH",
          "GR",
          "SG",
          "NC",
          "NZ",
          "HU",
          "EA",
          "SY",
          "JM",
          "AM",
          "YE",
          "IQ",
          "IR",
          "IL",
          "IT",
          "IN",
          "ID",
          "GB",
          "VG",
          "IO",
          "JO",
          "VN",
          "ZM",
          "JE",
          "TD",
          "GI",
          "CL",
          "CF",
          "CN",
          "MO",
          "HK"
        ]
      },
      "minItems": 0,
      "maxItems": 8,
      "uniqueItems": true
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

## quote_create

用searchDraftId+draftVersion+idempotencyKey创建合计报价，或兼容route/query参数；两组输入互斥。不代表确认消费，按capabilities返回的真实确认能力处理。

所需权限：quotes:write。

直接返回不可变报价对象；记录其 id、数量范围、maxCredits和expiresAt等实际字段。报价不是已消费或已确认。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "searchDraftId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "draftVersion": {
      "type": "integer",
      "minimum": 1,
      "maximum": 9007199254740991
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "workspaceId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "routeJobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "routeId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "routeIds": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 128
      },
      "minItems": 1,
      "maxItems": 3,
      "uniqueItems": true
    },
    "query": {
      "type": "string",
      "minLength": 1,
      "maxLength": 4000
    },
    "targetCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 20
    },
    "mode": {
      "type": "string",
      "enum": [
        "strict",
        "hybrid"
      ]
    },
    "allowWeb": {
      "type": "boolean"
    }
  },
  "required": [],
  "additionalProperties": false
}
```

价格与权益以真实回执为准：本包于2026-10-10核对prod公开合同，当前新报价政策为20积分/家公司；运行时仍核对真实回执。新报价的单价与上限分别取quote.unitPrice/maxCredits；有credits:read时可读取credits_get.unitPrice/onboarding。新注册正式账号的配置为200+200+200（第三项在首次成功创建任务时奖励），旧账号保留已存政策和领取资格，旧报价/任务按原单价。不要把新账号规则覆盖到旧账号，不承诺补发或重复发奖；缺scope时说明未能读取。

## job_start

用户明确要求找客并确定合计数量后，用confirmation传入报价的targetCount、unitPrice、maxCredits，原子确认、冻结积分并启动；数量缺失先询问，不默认推断。仅报价不启动。已网页确认的报价兼容省略confirmation。同键同内容恢复原任务。

所需权限：jobs:write。

直接返回已启动任务公开对象，其 id 是后续 jobId。用户明确找客意图及数量后，传与报价一致的confirmation，由服务端原子确认、冻结和启动。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "quoteId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "workspaceId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "confirmation": {
      "type": "object",
      "properties": {
        "targetCount": {
          "type": "integer",
          "minimum": 1,
          "maximum": 20
        },
        "unitPrice": {
          "type": "integer",
          "minimum": 1,
          "maximum": 9007199254740991
        },
        "maxCredits": {
          "type": "integer",
          "minimum": 1,
          "maximum": 9007199254740991
        }
      },
      "required": [
        "targetCount",
        "unitPrice",
        "maxCredits"
      ],
      "additionalProperties": false
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "quoteId",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

缺数量时用宿主AskQuestion说明当前20积分/家公司并询问合计数量，等待真实回答；宿主无此组件则普通提问。用户已经明确数量和找客意图时，无需另开网页或重复确认。先生成报价并核对范围；传confirmation:{targetCount,unitPrice,maxCredits}，值必须匹配用户选择与真实报价。仅报价不启动；能力false或无jobs:write时停止并说明未启动。报价金额超出已说明价格/用户上限时先补问，不偷偷扩大消费。找客奖励的触发时点以当前账号政策为准，由后端一次性处理，失败或重试不重复发奖。

## job_get

读取已知的本人找客任务进度，不提供取消。

所需权限：jobs:read。

直接返回公开任务 id、kind、status、progress、output及提示等；以实际状态判断是否终结。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "jobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "jobId"
  ],
  "additionalProperties": false
}
```

## job_results

分页读取本人已交付公司，每页10条；运行中为空不代表失败。

所需权限：jobs:read。

直接返回 items、nextCursor、summary。把 nextCursor 原样传入下次 after；只有已交付 items 可展示为结果。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "jobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "after": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "jobId"
  ],
  "additionalProperties": false
}
```

## credits_get

纯读积分和新手奖励状态，不发放或修复积分。

所需权限：credits:read。

data 含 availableCredits、heldCredits、unitPrice、onboarding、observedAt；availableCredits 不需再扣 heldCredits。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

价格与权益以真实回执为准：本包于2026-10-10核对prod公开合同，当前新报价政策为20积分/家公司；运行时仍核对真实回执。新报价的单价与上限分别取quote.unitPrice/maxCredits；有credits:read时可读取credits_get.unitPrice/onboarding。新注册正式账号的配置为200+200+200（第三项在首次成功创建任务时奖励），旧账号保留已存政策和领取资格，旧报价/任务按原单价。不要把新账号规则覆盖到旧账号，不承诺补发或重复发奖；缺scope时说明未能读取。

## credits_ledger

只读积分账本，消费与冻结分开；支持任务过滤和游标。

所需权限：credits:read。

data 含 items、nextCursor、consumptionTypes、notice；空过滤页仍可能有下一游标，冻结不作为交付消费。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "jobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100
    },
    "cursor": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [],
  "additionalProperties": false
}
```

## job_export

导出本人已交付公司快照，最多500行；通过MCP resources/read取得文件，不新增扣费。

所需权限：jobs:read。

data 为 {id,jobId,status:"ready",rowCount,mimeType,resourceUri,expiresAt}。通过宿主实际可用的 MCP resources/read 以原始 resourceUri 读取文件。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "jobId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "jobId",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

resources/read 输入 {uri:resourceUri}，返回 {contents:[{uri,mimeType,blob}]}；blob 是 XLSX 的 base64。用宿主真实文件能力解码为 .xlsx 并验证后交付。资源有账号归属与到期检查；宿主没有资源读取/文件交付能力时明确尚未取得文件，不拼下载URL、不泄露或把base64粘贴成正文。

## sales_inquiry_submit

登记全链路服务咨询，recorded仅表示已记录，未承诺销售已收到。

所需权限：sales:write。

data 为 {id,status:"recorded",createdAt}；仅登记，不代表消息已发送给销售。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "scale": {
      "type": "string",
      "enum": [
        "solo",
        "2-10",
        "11-50",
        "51-200",
        "201+"
      ]
    },
    "services": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "lead_generation",
          "outreach_strategy",
          "customer_operations",
          "social_media",
          "website",
          "advertising"
        ]
      },
      "minItems": 1,
      "maxItems": 6,
      "uniqueItems": true
    },
    "goal": {
      "type": "string",
      "minLength": 1,
      "maxLength": 2000
    },
    "contact": {
      "type": "string",
      "minLength": 1,
      "maxLength": 254
    },
    "companyName": {
      "type": "string",
      "minLength": 0,
      "maxLength": 200
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "scale",
    "services",
    "goal",
    "contact",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

用户仅问服务不提交。明确要求登记后才提交；recorded 只表示保存回执，不等于销售已收到通知。

## sales_inquiry_get

读取本人咨询回执；recorded不等于已通知销售。

所需权限：sales:read。

data 为 {id,status,createdAt}，仅能读取本人咨询回执。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "inquiryId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "inquiryId"
  ],
  "additionalProperties": false
}
```
