# Connection and recovery

## Compatibility and evidence

This Windows-only local connector follows the token-free stdio configuration in the supplied NVIDIA App skill v1.1.8, reviewed on 2026-10-11. Its skill card says no external credential is required, and its current connection example omits token/environment fields. The accompanying X64 installer is named `NvidiaAppSetupInt-11.0.9.560-X64.exe`.

Verified baseline on 2026-10-11, refreshed on 2026-10-14: installed NVIDIA App 11.0.9.560 (X64), valid NVIDIA-signed bridge, successful native stdio initialization, 12 discovered tools, and all six read-only tools called successfully with no token supplied. The diagnostic removed any inherited token variable and did not read discovery credentials. On 2026-10-14, the fixed launcher below also passed the installed WorkBuddy 5.8.2 parser and six read-only calls in an isolated launcher test. An actual WorkBuddy session connected at 10:44:01 China time and called driver status at 10:44:20; the user-visible result reported driver information. These observations establish the launcher and that read workflow, not successful import or persistent installation of this new 0.2.2 ZIP, approval, or all WorkBuddy workflows. No mutation was called: write authorization and write behavior remain untested. The previous 11.0.9.528 build also allowed unauthenticated reads; do not interpret read tests as proof of unrestricted writes, or claim that all public NVIDIA App releases support token-free MCP.

The separately supplied older AI-Agent-Integration-Guide still describes a token-based setup and a different endpoint. This adapter follows the v1.1.8 connection reference. If the installed build still requires credentials, stop and resolve the build/documentation mismatch; do not change authentication modes or add a legacy token flow automatically.

## Prerequisites and connection

- Windows with a compatible NVIDIA App MCP build installed through an authorized NVIDIA distribution channel. The archive's broad `11.0.9.5xx or above` troubleshooting wording is not a verified minimum supported version.
- The user completes NVIDIA App setup and enables its MCP access control, if exposed. The prior inspected UI placed it under Settings -> Features -> AI Agents and App Connections -> Allow Agents to control NVIDIA App; UI availability can vary by build and feature rollout. Do not bypass an absent or disabled control.
- The connector expects `C:\Program Files\NVIDIA Corporation\NVIDIA App\McpServer\NvAppMcpServer.exe`. A different install path needs a separately verified configuration; do not download a replacement automatically.
- WorkBuddy starts the Windows executable `cmd.exe` with the fixed arguments `/d`, `/c`, and the complete bridge path above as one argument. `/d` disables Command Processor AutoRun commands; `/c` runs the fixed executable and exits when it completes. The bridge itself receives no arguments. This addresses the WorkBuddy 5.8.2 Agent Plugins parser rejecting an absolute executable path in `command`; adding quote characters to that rejected field is not the fix.
- The package contains only this fixed launcher, not a general shell workflow: never append user text, extra commands, or shell operators. No token entry, environment-token mapping, Node.js, Python, npm package, or bundled installer is part of this connector. `mcp.json` intentionally omits `timeout` and uses only the supported launcher fields.
- The bridge relays to the persistent NVIDIA server's per-user named pipe. It does not start or enable that server. This adapter does not hardcode an HTTP port or read `server.json` for secrets.
- WorkBuddy 4.24.0 or newer is specified for this adapter's bilingual configuration fields; that is not a claim that this launcher was tested on every such release. The launcher and one actual read workflow were checked with WorkBuddy 5.8.2. New-package import, persistence after a restart/refresh, other workflows, and approval remain separate acceptance checks.

## Recovery

1. Missing tools: ask the user to connect the NVIDIA App connector in WorkBuddy and approve its local process/tool access. Importing the skill alone cannot establish that connection.
2. Missing executable: check that a compatible NVIDIA App is installed at the configured location. This package does not install or redistribute it.
3. `service_disabled`: ask the user to check NVIDIA App's MCP setting. Do not repeatedly spawn bridges, start services, edit registries, change feature flags, or reinstall applications as an implicit fix.
4. Authorization/access-level failure: preserve the error and verify build compatibility and intended permissions with the user. Do not request a token, scrape discovery-file secrets, or raise access to make the request succeed.
5. Successful MCP connection but Overlay failures: explain that Overlay readiness is separate and ask the user to check its settings. Do not enable capture or Desktop Capture as a diagnostic.

Use WorkBuddy's managed MCP tools for normal tasks. The fixed `cmd.exe` process-launch configuration does not authorize ad hoc shell commands or an alternate MCP transport. This skill does not authorize editing `%USERPROFILE%\.workbuddy\mcp.json`, modifying installed connector files, or creating a shell/HTTP fallback. An explicit configuration or installation request is a separate workflow.

## Security boundary

Removing the token prompt does not make six state-changing tools read-only, nor does it imply unrestricted access. NVIDIA's service controls, local transport security, access-level ceiling, and WorkBuddy's tool permissions still matter. A no-credential declaration is not a security audit of those controls.

Disconnecting this WorkBuddy connector does not revoke every local process's ability to contact NVIDIA's service. A public submission must disclose local access and confirm that WorkBuddy accepts the token-free design for this integration. Do not expose the local server remotely or create a proxy as part of this skill.

Source and modification notice: attribution.md.
