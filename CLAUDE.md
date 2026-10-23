# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **content archive**, not a software project: a mirror of WorkBuddy / CodeBuddy public marketplace packages (skills, connectors, experts, plugins) kept for offline study and searching. There is no build, lint, or test system, and no sync scripts are checked in (the daily sync runs externally). Content is third-party; copyright belongs to the original authors / Tencent products.

## Layout

- `skills/<name>/` — skill packs; each has a `SKILL.md`, often with `references/` and `scripts/` (~295 packs).
- `connectors/<id>/` — connector config templates: `mcp.json` (or `cli.json`) plus bundled `skills/` (~103). Enabling a connector requires OAuth/QR in the app; only templates live here.
- `experts/<name>/` — expert plugins: `.codebuddy-plugin/plugin.json`, `agents/`, `skills/`, avatars, sometimes `contracts/`, `examples/`. `experts/expert_center.json` is the catalog with categories.
- `plugins/codebuddy-plugins-official/` and `plugins/cb_teams_marketplace/` — plugin marketplaces (`plugins/`, `external_plugins/`, index txt/md files).
- `CATALOG.md` — Chinese-language listing of every skill/connector/expert with purpose, prerequisites, and links. `README.md` — counts and category breakdowns.

## Working conventions

- Commits follow `chore: sync WorkBuddy marketplace YYYY-MM-DD (connectors +N/~M; experts +N/-N/~M)` for syncs. Sync commits touch `CATALOG.md`, `README.md` counts, and `experts/expert_center.json` alongside content, so keep those consistent if you add/remove packages by hand.
- Treat package contents as upstream mirrors: avoid "fixing" or reformatting them, since the next sync overwrites changes. Per-package LICENSE files may exist in subdirectories.
- Search across the corpus with `rg`/`grep`; the repo is large (~28k tracked files). Rebuildable retrieval indexes (`*.npz`, `*.faiss`, `*.npy`, `faiss_index.bin`) are gitignored because they can exceed GitHub's 100MB blob limit — don't commit them.
- Install-back paths (from README): skills → `~/.workbuddy/skills/<name>/`; experts → `~/.workbuddy/plugins/marketplaces/experts/plugins/<name>/`; connectors → `~/.workbuddy/connectors-marketplace/connectors/<id>/`.
- Upstream sources: `download.codebuddy.cn/skill-marketplace/skill-marketplace.zip`, `download.codebuddy.cn/plugin-marketplace/*.zip`, the connectors-config COS zip, and the `expert-marketplace` `expert_center.json` plus `bundles/<name>.tar.gz`.
