# Attribution and modification notice

Based on the user-supplied `nvidiaapp-skills.zip`, path `nvidiaapp-skills-main/skills/nvidia-app`, version 1.1.8. Upstream frontmatter attributes this version to NVIDIA CORPORATION <info@nvidia.com>. Earlier adapter versions were based on supplied v1.1.4, attributed to Sahil Singh, NVIDIA.

Source archive: https://drive.google.com/file/d/12cjQHtnf94CDC-NS93PuBNVSlkHoLzUw/view . Retrieved 2026-10-11. SHA-256: `959fc59e9ae7f6b1db6653f2cac8d7e78f801cc7da122255972898671d746e47`.

Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

The supplied upstream LICENSE states that documentation/skills/assets are CC-BY-4.0 and source code is Apache-2.0. The full supplied license text, including its warranty disclaimers, is preserved in `../LICENSE.upstream.txt`. The documentation license is also available at https://creativecommons.org/licenses/by/4.0/ . No NVIDIA executable or source code is included in this adapter.

Changes in adapter 0.1.0, 2026-09-15: WorkBuddy bilingual frontmatter and connector metadata; native-stdio token form; compatibility notes corrected to the installed build; reorganized 12-tool guidance; explicit WorkBuddy-managed tool access; clarified ambiguous application names, uncertain mutation retries, unsupported capture qualifiers, and data handling. Added an original neutral GPU icon.

Changes in adapter 0.1.1, 2026-09-15: clearer English/Chinese descriptions and 16 paired connector examples.

Changes in adapter 0.1.2, 2026-09-15: replaced the neutral SVG with a square PNG adaptation of the NVIDIA badge supplied by the user, using image generation. The badge source is `nvidia-rtx-spark-badge-green_CMYK-for-print1.png`. The icon uses NVIDIA's eye and wordmark; it is not original NVIDIA-independent branding or a vendor-approved master asset. The upstream skill's documentation license does not establish permission for this separately supplied brand asset. Confirm brand-use authorization before marketplace publication.

Changes in adapter 0.1.3, 2026-09-15: resampled that icon to a 64×64 PNG without regenerating the artwork. The high-resolution master was retained outside the upload package.

Changes in adapter 0.2.0, 2026-10-11: adapted supplied upstream skill v1.1.8; removed the token form/environment mapping and token acquisition guidance; described the token-free setup and its verification limits; updated the expected quality preset to `Quality`, optional power-source behavior, six documented driver selectors gated by live schema, and optimization prerequisites that also block `Revert`; routed Optimize All to NVIDIA App's Graphics page. Retained bilingual descriptions/examples, 64×64 icon, WorkBuddy-managed tool access, conservative retry rules, user-intent boundaries, and privacy disclosure. This adaptation intentionally omits upstream automatic-registration/direct-HTTP fallback instructions because normal WorkBuddy tasks should use the managed connector.

Changes in adapter 0.2.1, 2026-10-11: recorded successful token-free initialization, 12-tool discovery and six read-only calls on installed NVIDIA App 11.0.9.560 X64; distinguished that evidence from untested writes and WorkBuddy UI behavior; clarified the three release-note selectors actually advertised on this host and the live Battery Boost support prerequisite for Battery optimization. No NVIDIA setting was changed during verification.

Changes in adapter 0.2.2, 2026-10-14: changed the WorkBuddy launch configuration to the fixed Windows `cmd.exe /d /c` launcher for the installed NVIDIA bridge, removed the optional timeout field, and retained the existing connector asset ID. The bridge itself still receives no arguments; credentials remain absent. Recorded refreshed six-read native evidence, a separate isolated launcher/parser test, and one observed driver-status read in WorkBuddy 5.8.2. Updated connection and privacy wording without changing the 12-tool scope, bilingual examples, icon, or upstream license. New-ZIP import, persistent installation, mutation behavior, and marketplace approval are not certified by those observations.

The upstream `skill.oms.sig`, benchmark claims, internal CI configuration, and evaluation bundle are not distributed as certification of these modified instructions. NVIDIA and WorkBuddy/Tencent names identify compatibility, not endorsement. Publisher identity, privacy/support details, runtime acceptance evidence, and public-distribution authorization remain the submitter's responsibility.
