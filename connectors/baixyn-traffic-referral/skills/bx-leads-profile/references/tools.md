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

## profile_options_get

读取合法国家、公司身份与资料字段限制。

所需权限：profile:read。

data 包含 markets、roles 与 limits；以它们作为国家、身份和字段边界。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

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

## company_analysis_start

调用百型自己的联网公司解析，受理后返回后台任务ID；名称或官网至少一项，受理消耗一次免费解析次数。

所需权限：analysis:write。

data 返回本人后台解析的 analysisId、状态与 pollAfterMs；保存ID后读取同一任务，不把受理当报告完成。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "website": {
      "type": "string",
      "minLength": 1,
      "maxLength": 500
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "idempotencyKey"
  ],
  "additionalProperties": false,
  "anyOf": [
    {
      "required": [
        "name"
      ]
    },
    {
      "required": [
        "website"
      ]
    }
  ]
}
```

## company_analysis_get

读取本人公司解析状态和完整报告。needs_input为终态，应补充输入后新建解析。

所需权限：analysis:read。

data 返回解析状态；completed 才读取完整报告与稳定 itemId，needs_input 为终态；遵循真实 pollAfterMs/usage/warnings。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "analysisId"
  ],
  "additionalProperties": false
}
```

## profile_draft_create

按当前正式资料版本创建可恢复草稿；空资料baseProfileVersion为0。

所需权限：profile:write。

data 含 draftId、draftVersion、baseProfileVersion、state、草稿 data、missingFields、expiresAt、updatedAt；patch可能附unchanged。这是草稿，尚非正式资料。

输入 JSON Schema：

```json
{
  "type": "object",
  "properties": {
    "baseProfileVersion": {
      "type": "integer",
      "minimum": 0,
      "maximum": 9007199254740991
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "baseProfileVersion",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

## profile_draft_get

读取本人草稿、版本、缺项和有效期。

所需权限：profile:read。

data 含 draftId、draftVersion、baseProfileVersion、state、草稿 data、missingFields、expiresAt、updatedAt；patch可能附unchanged。这是草稿，尚非正式资料。

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

## profile_draft_patch

仅修改草稿指定字段；集合用operation+values，条目按稳定ID修改；不接受伪造来源。

所需权限：profile:write。

data 含 draftId、draftVersion、baseProfileVersion、state、草稿 data、missingFields、expiresAt、updatedAt；patch可能附unchanged。这是草稿，尚非正式资料。

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
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "detachEvidence": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200
      },
      "minItems": 0,
      "maxItems": 75
    },
    "changes": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "minLength": 0,
          "maxLength": 200
        },
        "website": {
          "type": "string",
          "minLength": 0,
          "maxLength": 500
        },
        "overview": {
          "type": "string",
          "minLength": 0,
          "maxLength": 4000
        },
        "markets": {
          "type": "object",
          "properties": {
            "operation": {
              "type": "string",
              "enum": [
                "replace",
                "add",
                "remove"
              ]
            },
            "values": {
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
            }
          },
          "required": [
            "operation",
            "values"
          ],
          "additionalProperties": false
        },
        "roles": {
          "type": "object",
          "properties": {
            "operation": {
              "type": "string",
              "enum": [
                "replace",
                "add",
                "remove"
              ]
            },
            "values": {
              "type": "array",
              "items": {
                "type": "string",
                "enum": [
                  "Manufacturer",
                  "Factory",
                  "Manufacturer/Factory",
                  "Plant",
                  "Manufacturer/Plant",
                  "Factory/Plant",
                  "Manufacturer/Factory/Plant",
                  "Parts & Components Supplier",
                  "Distributor",
                  "Wholesaler",
                  "Retailer",
                  "Chain Store",
                  "Independent Store",
                  "Shop",
                  "Independent Store/Shop",
                  "Franchisee",
                  "Supermarket",
                  "Department Store",
                  "Supermarket/Department Store",
                  "Online",
                  "E-commerce shop",
                  "Online/E-commerce shop",
                  "Agent",
                  "Importer",
                  "Trader",
                  "Importer/Trader",
                  "Purchaser",
                  "Buyer",
                  "Purchaser/Buyer",
                  "Warehouser",
                  "Logistics Provider",
                  "Service Provider",
                  "Solution Provider",
                  "Integrator",
                  "Consultant",
                  "Operator",
                  "MRO",
                  "Installer",
                  "Designer",
                  "Studio",
                  "Project delivery",
                  "Engineering Contractor",
                  "Subcontractor",
                  "Brand Owner",
                  "Licensor",
                  "Supplier",
                  "Supplier Manager",
                  "Channel Partner",
                  "Others"
                ]
              },
              "minItems": 0,
              "maxItems": 24,
              "uniqueItems": true
            }
          },
          "required": [
            "operation",
            "values"
          ],
          "additionalProperties": false
        }
      },
      "required": [],
      "additionalProperties": false
    },
    "items": {
      "type": "object",
      "properties": {
        "productItems": {
          "type": "object",
          "properties": {
            "upsert": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "id": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 128
                  },
                  "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 180
                  },
                  "description": {
                    "type": "string",
                    "minLength": 0,
                    "maxLength": 1000
                  }
                },
                "required": [],
                "additionalProperties": false
              },
              "minItems": 0,
              "maxItems": 24
            },
            "removeIds": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "minItems": 0,
              "maxItems": 24
            }
          },
          "required": [],
          "additionalProperties": false
        },
        "industryItems": {
          "type": "object",
          "properties": {
            "upsert": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "id": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 128
                  },
                  "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 180
                  },
                  "description": {
                    "type": "string",
                    "minLength": 0,
                    "maxLength": 1000
                  }
                },
                "required": [],
                "additionalProperties": false
              },
              "minItems": 0,
              "maxItems": 24
            },
            "removeIds": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "minItems": 0,
              "maxItems": 24
            }
          },
          "required": [],
          "additionalProperties": false
        },
        "businessAreas": {
          "type": "object",
          "properties": {
            "upsert": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "id": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 128
                  },
                  "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 180
                  },
                  "description": {
                    "type": "string",
                    "minLength": 0,
                    "maxLength": 1000
                  }
                },
                "required": [],
                "additionalProperties": false
              },
              "minItems": 0,
              "maxItems": 24
            },
            "removeIds": {
              "type": "array",
              "items": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "minItems": 0,
              "maxItems": 24
            }
          },
          "required": [],
          "additionalProperties": false
        }
      },
      "required": [],
      "additionalProperties": false
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

## profile_adoption_preview

比较本人完成的解析报告与草稿，返回逐项采用决策和previewRevision；不改正式资料。

所需权限：profile:write, analysis:read。

data 含 draftId、draftVersion、analysisId、options 与 previewRevision；options表达逐项新增/相同/替换/缺项。

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
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "itemIds": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 128
      },
      "minItems": 0,
      "maxItems": 100
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "analysisId"
  ],
  "additionalProperties": false
}
```

## profile_adopt_website

从本人已完成报告采用官网到草稿。批量采用需逐项调用并接续新版本，最后一次保存。替换现有内容需有效previewRevision。

所需权限：profile:write, analysis:read。

data 含 draftId、最新draftVersion、itemId、采用的item或value、status、unchanged与counts；每次接续该版本，最后统一正式保存。

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
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "replaceExisting": {
      "type": "boolean"
    },
    "previewRevision": {
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
    "analysisId",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

## profile_adopt_overview

从本人已完成报告采用公司介绍到草稿。批量采用需逐项调用并接续新版本，最后一次保存。替换现有内容需有效previewRevision。

所需权限：profile:write, analysis:read。

data 含 draftId、最新draftVersion、itemId、采用的item或value、status、unchanged与counts；每次接续该版本，最后统一正式保存。

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
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "replaceExisting": {
      "type": "boolean"
    },
    "previewRevision": {
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
    "analysisId",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```

## profile_adopt_product

从本人已完成报告采用一项产品及说明到草稿。批量采用需逐项调用并接续新版本，最后一次保存。替换现有内容需有效previewRevision。

所需权限：profile:write, analysis:read。

data 含 draftId、最新draftVersion、itemId、采用的item或value、status、unchanged与counts；每次接续该版本，最后统一正式保存。

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
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "replaceExisting": {
      "type": "boolean"
    },
    "previewRevision": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "itemId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "analysisId",
    "idempotencyKey",
    "itemId"
  ],
  "additionalProperties": false
}
```

## profile_adopt_industry

从本人已完成报告采用一项行业及说明到草稿。批量采用需逐项调用并接续新版本，最后一次保存。替换现有内容需有效previewRevision。

所需权限：profile:write, analysis:read。

data 含 draftId、最新draftVersion、itemId、采用的item或value、status、unchanged与counts；每次接续该版本，最后统一正式保存。

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
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "replaceExisting": {
      "type": "boolean"
    },
    "previewRevision": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "itemId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "analysisId",
    "idempotencyKey",
    "itemId"
  ],
  "additionalProperties": false
}
```

## profile_adopt_business_area

从本人已完成报告采用一项业务领域及说明到草稿。批量采用需逐项调用并接续新版本，最后一次保存。替换现有内容需有效previewRevision。

所需权限：profile:write, analysis:read。

data 含 draftId、最新draftVersion、itemId、采用的item或value、status、unchanged与counts；每次接续该版本，最后统一正式保存。

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
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "replaceExisting": {
      "type": "boolean"
    },
    "previewRevision": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "itemId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "analysisId",
    "idempotencyKey",
    "itemId"
  ],
  "additionalProperties": false
}
```

## profile_adopt_role

从本人已完成报告采用一个身份到草稿。批量采用需逐项调用并接续新版本，最后一次保存。替换现有内容需有效previewRevision。

所需权限：profile:write, analysis:read。

data 含 draftId、最新draftVersion、itemId、采用的item或value、status、unchanged与counts；每次接续该版本，最后统一正式保存。

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
    "analysisId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "replaceExisting": {
      "type": "boolean"
    },
    "previewRevision": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "idempotencyKey": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    },
    "itemId": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion",
    "analysisId",
    "idempotencyKey",
    "itemId"
  ],
  "additionalProperties": false
}
```

## profile_draft_preview

预览草稿与网页最新正式资料的三方合并，不写正式资料。

所需权限：profile:write。

data 含 draftId、draftVersion、profileVersion、候选 data、changedFields、itemIdMap、missingFields、conflicts 和必要时 conflictRevision；尚未写入正式资料。

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
    }
  },
  "required": [
    "draftId",
    "expectedDraftVersion"
  ],
  "additionalProperties": false
}
```

## profile_draft_save

原子保存草稿净变更；保留其他端不相关修改，同字段冲突需按revision选择。

所需权限：profile:write。

data 含 state:saved、profile、version、changedFields、itemIdMap、unchanged；出现业务错误时没有部分正式保存。

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
    "resolution": {
      "type": "object",
      "properties": {
        "conflictRevision": {
          "type": "string",
          "minLength": 1,
          "maxLength": 128
        },
        "choices": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "conflictId": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128
              },
              "choice": {
                "type": "string",
                "enum": [
                  "keep_current",
                  "use_draft"
                ]
              }
            },
            "required": [
              "conflictId",
              "choice"
            ],
            "additionalProperties": false
          },
          "minItems": 0,
          "maxItems": 100
        }
      },
      "required": [
        "conflictRevision",
        "choices"
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
    "draftId",
    "expectedDraftVersion",
    "idempotencyKey"
  ],
  "additionalProperties": false
}
```
