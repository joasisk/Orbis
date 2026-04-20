# Obsidian Vault Integration Plan (API-first)

Date: 2026-04-20  
Owner: Integrations track (notes ingestion)

## Why this plan exists
This proposal defines how Orbis should integrate with Obsidian vaults while staying inside existing MVP guardrails:
- keep approval-first behavior for AI-extracted items,
- keep core orchestration in `apps/api`,
- preserve low-friction UX.

It also evaluates parser/library options for Obsidian markdown so implementation can start with minimal parsing risk.

## Requirement and MVP mapping
- **`docs/REQUIREMENTS.md` §7 Notes integration** requires:
  - manual import of selected notes,
  - periodic vault/folder scanning,
  - extraction into candidate tasks/projects with accept/edit/dismiss control.
- **`docs/MVP_PLAN.md`** includes one note ingestion path for MVP.

### Scope decision
- **MVP-compatible baseline:** add robust Obsidian ingestion support for one or more configured vaults, but keep extraction approval-first.
- **No scope creep:** avoid two-way sync/editing of notes in MVP.

## Proposed user-facing capabilities

### 1) Connect one or more Obsidian vaults
Each owner can add multiple vault connections, each with:
- local path or mounted path,
- enable/disable toggle,
- scan mode (`manual_only`, `scheduled`),
- include/exclude folder globs,
- optional default mapping target:
  - Area of Life, and/or
  - Project.

### 2) Route vaults to life areas/projects
Allow binding a vault (or subfolder rule) to:
- a specific `area_of_life_id`,
- an optional `project_id`.

Routing rule precedence:
1. explicit per-note override (future UI),
2. folder rule,
3. vault default,
4. no mapping (suggestions remain unmapped drafts).

### 3) Keep existing accept/edit/dismiss review flow
Ingestion and extraction create **suggestions only**. Nothing mutates tasks/projects without explicit user action.

## API-first architecture proposal

### New API domain objects (MVP-safe)
1. `obsidian_vault_connections`
   - `id`, `owner_user_id`, `label`, `vault_path`, `enabled`, `scan_mode`, `timezone`,
   - `default_area_id` (nullable), `default_project_id` (nullable),
   - `created_at`, `updated_at`, `last_scan_at`, `last_scan_status`.

2. `obsidian_vault_folder_rules`
   - `id`, `vault_connection_id`, `folder_glob`,
   - `target_area_id` (nullable), `target_project_id` (nullable),
   - `priority`, `enabled`.

3. Extend existing note-source metadata in extraction records with:
   - `vault_connection_id`,
   - `source_relative_path`,
   - `source_hash` (for idempotent rescans),
   - `obsidian_uri` (optional deep link).

### Endpoint sketch
- `POST /integrations/obsidian/vaults`
- `GET /integrations/obsidian/vaults`
- `PATCH /integrations/obsidian/vaults/{id}`
- `DELETE /integrations/obsidian/vaults/{id}`
- `POST /integrations/obsidian/vaults/{id}/scan` (manual trigger)
- `GET /integrations/obsidian/vaults/{id}/scan-runs`
- `PUT /integrations/obsidian/vaults/{id}/folder-rules`

### Worker flow
1. Scheduler reads enabled vault configs from API DB.
2. Worker enumerates candidate note files.
3. Parser extracts frontmatter, wikilinks, tags, tasks/checklists, headings.
4. Hash-based dedupe skips unchanged files.
5. Extraction pipeline emits candidate items linked to source note and vault.
6. Existing review actions (accept/edit/dismiss) remain authoritative.

## Available parser options for Obsidian format

## Python candidates (best fit for `apps/api`)

### Option A — `obsidianmd-parser` (PyPI)
- Purpose-built for Obsidian vault parsing.
- Supports wikilinks, tags, tasks, callouts, and vault-level relationships.
- Requires Python 3.12+, which matches current API runtime.
- Tradeoff: relatively new package; should be validated with fixture tests.

Reference: https://pypi.org/project/obsidianmd-parser/

### Option B — `obsidiantools` (PyPI)
- Established Python tooling for vault graph/link/tag analysis.
- Useful when backlink graph analytics are needed.
- Tradeoff: broader analysis toolkit than needed for MVP ingestion; may add complexity.

Reference: https://pypi.org/project/obsidiantools/

### Option C — composable parser stack
- `python-frontmatter` for YAML frontmatter.
- standard markdown parsing + custom wikilink tokenizer.
- Tradeoff: highest implementation/control effort; lowest external coupling.

## JS/TS ecosystem options (useful for web/SDK tooling, not primary API parser)
- `@moritzrs/mdast-util-ofm-wikilink`
- `@flowershow/remark-wiki-link`
- `mdast-util-wiki-link`

These are useful if we later parse or preview Obsidian markdown in `apps/web`, but API ingestion should stay Python-first for MVP consistency.

## Recommended parser decision
Use a **two-layer approach**:
1. Start with `obsidianmd-parser` for fast MVP delivery.
2. Wrap it behind an internal `ObsidianParser` interface so we can swap implementations if reliability issues appear.

## Obsidian format realities to support
Based on Obsidian Help docs, ingestion should correctly handle:
- Wikilinks `[[Note]]` and alias form `[[Note|Alias]]`.
- Standard markdown links as internal note links.
- Section/block references and embeds where possible.
- URL-encoded markdown link targets.

References:
- https://help.obsidian.md/Linking%20notes%20and%20files/Internal%20links
- https://help.obsidian.md/syntax

## Data governance and privacy guardrails
- Vault access is owner-scoped only.
- Parsed content should not be shown in spouse views unless accepted into non-private schedule/task records.
- Keep owner priority and spouse influence as separate fields (no merge).
- All extraction and accept/edit/dismiss actions should emit audit events.

## Rollout plan

### Milestone 1 (smallest viable)
- Add vault connection model + CRUD.
- Manual scan endpoint for one vault.
- Parser adapter + extraction pipeline integration.
- Reuse existing candidate review endpoints.

### Milestone 2
- Scheduled scans using existing settings cadence model.
- Incremental hashing/idempotency.
- Folder rules for area/project mapping.

### Milestone 3
- Multiple vault UX in settings (connection health, last scan, errors).
- Source deep-link display using Obsidian URI.

## Acceptance criteria
- Owner can register **multiple** vault connections.
- Owner can tie each vault (or folder rule) to a life area/project.
- Scan run creates candidate items linked to exact source note + vault.
- No automatic task/project creation without explicit owner action.
- Private boundaries and spouse visibility rules remain intact.

## Testing strategy
- Unit tests: parser adapter fixtures for wikilinks, aliases, frontmatter, embedded links.
- Integration tests: scan endpoint, dedupe behavior, suggestion review lifecycle.
- Security tests: role checks on vault CRUD and scans.
- Regression tests: ensure approval gates are unchanged.

## Open questions
- Should `vault_path` allow network mounts only, or arbitrary host paths?
- Should folder routing support regex or glob only (glob recommended for simplicity)?
- Should a note map to both area and project simultaneously when both defaults exist (recommended: yes)?
