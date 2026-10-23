# PatchXFreeNote WorkBuddy Source Of Truth

Use this reference when links, versions, endpoint claims, or publishing status matter.

## PatchXFreeNote Links

- GitHub repository: `https://github.com/ZsTs119/patchxnote-agent`
- npm package: `https://www.npmjs.com/package/patchxnote-agent`
- Feishu public guide: `https://patchx2025.feishu.cn/wiki/PnVRwYT7IirFPckairGcWPnHnCd`

## WorkBuddy Links

- Connector docs: `https://open.workbuddy.cn/docs/connector`

## WorkBuddy Package

- Connector package version: `0.1.0`
- Source: `patchxfreenote`
- Transport: `streamableHttp`
- Environment: `production`
- MCP URL: `https://freenote.patch-x.cn/mcp`
- Package source directory: `packages/workbuddy/patchxnote-agent/`

The selected endpoint identifies this package's environment. Package generation does not establish marketplace acceptance.

## Status Rules

- npm package publication does not prove WorkBuddy marketplace acceptance.
- Local stdio MCP smoke does not prove WorkBuddy remote MCP auth acceptance.
- WorkBuddy zip upload does not prove browser auth, `tools/list`, or tool-call success.
- Claim `platform_accepted` only after the actual WorkBuddy connector has uploaded, parsed, authenticated, listed tools, and completed at least one safe real PatchXFreeNote tool call.
