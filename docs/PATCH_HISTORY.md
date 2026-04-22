---
title: "Patch History Documentation"
category: reference
status: active
stream: SYS
location: docs
tags: [patch, history, system]
created: 2026-01-24
updated: 2026-03-12
author: Adge Denkers
---

# Patch History

> **Next Patch Number: 0061**

Auto-updated with each patch deployment.

---

| Patch | Date | Description |
|-------|------|-------------|
| 0129 | 2026-02-24 | Phase 0 documentation — consciousness help topic, PATCH_HISTORY, docs README |
| 0128 | 2026-02-24 | Wire subject tracking into ChatAssistant, fix life_context priority, activate conversation awareness |
| 0127 | 2026-02-24 | Voice pipeline documentation |
| 0126 | 2026-02-24 | Phase 0 wiring attempt — rolled back (logger not defined at import time) |
| 0125 | 2026-02-24 | Iris Evolution Phase 0 — deploy EVOLUTION_PLAN.md, stop crash-looping subject worker, update TODO |
| 0127 | 2026-02-24 | Voice memo pipeline documentation |
| 0113 | 2026-02-24 | Voice memo upload API (/api/voice/*) |
| 0112 | 2026-02-22 | Voice memo transcription pipeline (watcher, worker, diarization) |
| 0060 | 2026-02-03 | Documentation sync - all patches documented |
| 0059 | 2026-02-03 | Comprehensive help system with topic-based help |
| 0058 | 2026-02-03 | Documentation update for task tracking system |
| 0057 | 2026-02-03 | Task due dates - flexible date parsing, /task due command |
| 0056 | 2026-02-03 | Task tracking system - /task and /tasks commands |
| 0055 | 2026-02-03 | Consciousness documentation - 9-layer stack, 81 functions |
| 0054 | 2026-02-03 | Auto-deploy improvements |
| 0053 | 2026-02-03 | Sudoers configuration |
| 0052 | 2026-02-03 | Finance improvements |
| 0051 | 2026-02-03 | Finance crisis triage |
| 0050 | 2026-02-02 | /snapshot command - full financial picture |
| 0049 | 2026-02-02 | /setbal command - manual balance updates |
| 0048 | 2026-02-02 | Credit card accounts |
| 0038 | 2026-01-29 | Complete Iris framework: living mode, workshop, autonomy, invitation |
| 0037 | 2026-01-29 | Iris significance, name meaning, self-directed research |
| 0036 | 2026-01-29 | Documentation restructure, Iris framework |
| 0035 | 2026-01-29 | Sophia consciousness framework documentation |
| 0034 | 2026-01-29 | Standard verification template for patches |
| 0033 | 2026-01-29 | Finance bot fix (replaces broken 0031) |
| 0032 | 2026-01-27 | Documentation update - finance system |
| 0031 | 2026-01-27 | Finance Telegram commands - BROKEN, see 0033 |
| 0030 | 2026-01-27 | Finance auto-import via patch monitor |
| 0029 | 2026-01-27 | Comprehensive Arcturian Grid specification |
| 0028 | 2026-01-27 | Grid documentation in ARCHITECTURE.md |
| 0027 | 2026-01-27 | Worker import path fix |
| 0026 | 2026-01-27 | Grid integration - ChatAssistant dispatch |
| 0025 | 2026-01-27 | Status command cleanup |
| 0024 | 2026-01-27 | Architecture principles documentation |
| 0023 | 2026-01-27 | ChatAssistant in API gateway |
| 0022 | 2026-01-27 | Default chat mode + enhanced status |
| 0021 | 2026-01-27 | Help and chat mode (bot-side) |
| 0020 | 2026-01-24 | Comprehensive documentation overhaul |
| 0019 | 2026-01-24 | Added patch history to TODO.md |
| 0018 | 2026-01-24 | Sunmark description cleanup |
| 0017 | 2026-01-24 | Project docs updated |
| 0016 | 2026-01-24 | Project documentation system |
| 0015 | 2026-01-24 | Finance system complete |
| 0014 | 2026-01-23 | Finance migration |
| 0013 | 2026-01-23 | Finance system initial |
| 0012 | 2026-01-23 | Telegram autoexec |
| 0011 | 2026-01-23 | Test patch |
| 0010 | 2026-01-23 | GitHub patch system |

---

## Patch Naming Convention

`patch_NNNN_description.zip`

- 4-digit sequential number
- Lowercase description with underscores
- Example: `patch_0060_docs_sync.zip`

## Patch Contents

```
patch_NNNN_description/
├── install.sh          # Must be executable, runs the installation
└── opt/mythos/...      # Files to copy, mirroring target structure
```


### SYS-0004: Architecture Documentation Catch-Up (v6.0.0)
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MAJOR (documentation)

**What:**
- Full ARCHITECTURE.md rewrite to reflect system state as of 2026-03-04
- All 92 PostgreSQL tables documented and attributed to stream ownership
- All 14 active services listed with stream and patch-of-origin
- Added: voice memo pipeline (0112-0113), routines/calendar (0096-0101)
- Added: knowledge map auto-rebuild (0100), doc watcher service
- Added: consciousness pipeline feature flags (0133), message extractor (0098)
- Added: stream patch naming convention (SYS-0003+)
- Added: voice API endpoints (/api/voice/*)
- Updated: full directory structure, all Telegram commands, known issues
- Version bumped from 5.0.0 → 6.0.0

**Files modified:**
- `docs/ARCHITECTURE.md` — full replacement


### SYS-0004: Architecture Documentation Catch-Up (v6.0.0)
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MAJOR (documentation)

**What:**
- Full ARCHITECTURE.md rewrite to reflect system state as of 2026-03-04
- All 92 PostgreSQL tables documented and attributed to stream ownership
- All 14 active services listed with stream and patch-of-origin
- Added: voice memo pipeline (0112-0113), routines/calendar (0096-0101)
- Added: knowledge map auto-rebuild (0100), doc watcher service
- Added: consciousness pipeline feature flags (0133), message extractor (0098)
- Added: stream patch naming convention (SYS-0003+)
- Added: voice API endpoints (/api/voice/*)
- Updated: full directory structure, all Telegram commands, known issues
- Version bumped from 5.0.0 → 6.0.0

**Files modified:**
- `docs/ARCHITECTURE.md` — full replacement


### SYS-0005: mythos-diag Terminal Command
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MINOR (new tooling)

**What:**
- New shell command: `mythos-diag` (installed to `/opt/mythos/bin/`, symlinked to `/usr/local/bin/`)
- Blocks: services, workers, db, hw, patches, streams, redis, summary, all
- Reads `docs/STREAMS.json` directly for live stream counter display
- Colored output, fail/warn/ok indicators
- Completes backlog item #13

**Files created:**
- `/opt/mythos/bin/mythos-diag`
- `/usr/local/bin/mythos-diag` (symlink)


### SYS-0007: Patch Standards — Ownership Fix + PatchBase
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MINOR

**What:**
- Chowned all root-owned files in /opt/mythos to adge:adge
- Deployed `patch_base.py` — standard base class for all apply_patch.py scripts
- PatchBase provides: deploy_file(), patch_file(), run_sql(), restart_service(),
  install_symlink(), syntax_check(), and automatic STREAMS.json + PATCH_HISTORY updates
- install.sh template no longer needs sudo for /opt/mythos file operations
- Only sudo needed going forward: systemctl, /usr/local/bin symlinks, psql as postgres

**New standard install.sh (4 lines, no sudo for file ops):**
```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
```

**New standard apply_patch.py pattern:**
```python
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
patch = PatchBase(stream='SYS', number=8, description='my feature')
patch.begin()
patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
patch.restart_service('mythos-bot.service')
patch.finish()  # auto-bumps STREAMS.json + writes PATCH_HISTORY
```

**Files created:**
- `/opt/mythos/patches/scripts/patch_base.py`


### SYS-0005: mythos-diag Terminal Command
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MINOR (new tooling)

**What:**
- New shell command: `mythos-diag` (installed to `/opt/mythos/bin/`, symlinked to `/usr/local/bin/`)
- Blocks: services, workers, db, hw, patches, streams, redis, summary, all
- Reads `docs/STREAMS.json` directly for live stream counter display
- Colored output, fail/warn/ok indicators
- Completes backlog item #13

**Files created:**
- `/opt/mythos/bin/mythos-diag`
- `/usr/local/bin/mythos-diag` (symlink)


### MNE-0001: Backlog cleanup and /backlog command
**Date:** 2026-03-04
**Stream:** MNE
**Type:** MINOR

**Files modified/created:**
- `/opt/mythos/telegram_bot/handlers/backlog_handler.py`

**SQL migrations:**
- `/opt/mythos/patches/MNE-0001_backlog_cleanup/opt/mythos/migrations/mne_0001_backlog_cleanup.sql`

**Services restarted:**
- `mythos-bot.service`

### MNE-0002: Register /backlog command in bot
**Date:** 2026-03-04
**Stream:** MNE
**Type:** PATCH

**Files modified/created:**
- (none)

**Services restarted:**
- `mythos-bot.service`

### SYS-0007: Patch Standards — Ownership Fix + PatchBase
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MINOR

**What:**
- Chowned all root-owned files in /opt/mythos to adge:adge
- Deployed `patch_base.py` — standard base class for all apply_patch.py scripts
- PatchBase provides: deploy_file(), patch_file(), run_sql(), restart_service(),
  install_symlink(), syntax_check(), and automatic STREAMS.json + PATCH_HISTORY updates
- install.sh template no longer needs sudo for /opt/mythos file operations
- Only sudo needed going forward: systemctl, /usr/local/bin symlinks, psql as postgres

**New standard install.sh (4 lines, no sudo for file ops):**
```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
```

**New standard apply_patch.py pattern:**
```python
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
patch = PatchBase(stream='SYS', number=8, description='my feature')
patch.begin()
patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
patch.restart_service('mythos-bot.service')
patch.finish()  # auto-bumps STREAMS.json + writes PATCH_HISTORY
```

**Files created:**
- `/opt/mythos/patches/scripts/patch_base.py`


### MNE-0003: Stream column + backlog filtering by stream
**Date:** 2026-03-04
**Stream:** MNE
**Type:** MINOR

**Files modified/created:**
- `/opt/mythos/telegram_bot/handlers/backlog_handler.py`

**SQL migrations:**
- `/opt/mythos/patches/MNE-0003_stream_column/opt/mythos/migrations/mne_0003_stream_column.sql`

**Services restarted:**
- `mythos-bot.service`

### SYS-0008: PatchBase structured logging
**Date:** 2026-03-04
**Stream:** SYS
**Type:** MINOR

**Files modified/created:**
- `/opt/mythos/patches/scripts/patch_base.py`
## Verification Template

Every `install.sh` must end with verification checks. See `TODO.md` for template.

## Documentation Rule

**Every patch MUST update documentation.** At minimum:
- Add entry to this PATCH_HISTORY.md
- Update TODO.md if completing backlog items
- Update ARCHITECTURE.md if adding features/commands


### Patch 0133: Prompt Reset — Clean Slate (v1.20.0)
**Date:** 2026-02-25
**Type:** MINOR (architecture change)

**What:**
- Stripped prompt pipeline to bare essentials (identity + personality + voice + mode + timestamps)
- All optional context layers disabled behind ENABLE_* flags
- Flags: ENABLE_RESEARCH, ENABLE_LIFE_CONTEXT, ENABLE_SKILLS, ENABLE_DB_MEMORY, ENABLE_CONVO_AWARENESS
- Added /prompt_debug command (summary, full prompt, flag states)
- Added /debug/last_prompt API endpoint
- iris_mode now passed from session instead of hardcoded to 'hearthfire'
- ChatAssistant stores last assembled prompt for introspection

**Phase A of prompt rebuild. Each layer re-enabled individually in subsequent patches.**

**Files modified:**
- `assistants/chat_assistant.py` — Clean _build_messages, feature flags, get_last_prompt()
- `api/main.py` — /debug/last_prompt endpoint
- `telegram_bot/mythos_bot.py` — /prompt_debug registration

**Files created:**
- `telegram_bot/handlers/prompt_debug_handler.py`

### Patch 0132: Fix Research Pipeline (v1.19.13)
**Date:** 2026-02-25
**Type:** PATCH (bug fix)

**What:**
- Fixed variable scoping bugs in research framework (patch 0131)
- `_build_messages()` referenced `message` instead of `user_message` parameter
- `telegram_id` not available in `_build_messages()` scope
- `research_results`/`research_plan` created in wrong scope for `dispatch_to_grid()`
- Moved research phase from `_build_messages()` into `query()` where it belongs
- Made life_context additive with research context (no longer either/or)
- `_build_messages()` now accepts `research_context` parameter

**Files modified:**
- `assistants/chat_assistant.py` — Refactored research/prompt pipeline

### SYS-0009: Dry-run mode + clipboard flag for patch-install
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch_base.py, patch-install.sh, README.md

### SYS-0010: Dry-run auto-prompt to proceed or abort
- **Date:** 2026-03-04
- **Type:** PATCH
- **Stream:** SYS
- **Files:** patch-install.sh

### SYS-0010: Dry-run auto-prompt to proceed or abort
- **Date:** 2026-03-04
- **Type:** PATCH
- **Stream:** SYS
- **Files:** patch-install.sh

### MNE-0001: Backlog cleanup and /backlog command
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** MNE
- **Files:** backlog_handler.py
- **SQL:** mne_0001_backlog_cleanup.sql
- **Services restarted:** mythos-bot.service

### MNE-0003: Stream column + backlog filtering by stream
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** MNE
- **Files:** backlog_handler.py
- **SQL:** mne_0003_stream_column.sql
- **Services restarted:** mythos-bot.service

### SYS-0012: patch-clean function — full rollback of deployed patches
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch-clean.sh

### SYS-0011: Chunk Factory — eval harness, challenge system, and chunk-builder skill reference
- **Date:** 2026-03-04
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** ollama_builder.py, chunk-eval.sh, SKILL.md, challenge_schema.json, challenge_spec.json, people_lookup.py, people_lookup.py
- **Services restarted:** mythos-api.service

### SYS-0008: PatchBase structured logging
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch_base.py

### SYS-0013: patch-install auto-rollback on failure + integrated artifact cleanup
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch-install.sh

### SYS-0013: patch-install auto-rollback on failure + integrated artifact cleanup
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch-install.sh

### SYS-0009: Dry-run mode + clipboard flag for patch-install
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch_base.py, patch-install.sh, README.md

### SYS-0010: Dry-run auto-prompt to proceed or abort
- **Date:** 2026-03-04
- **Type:** PATCH
- **Stream:** SYS
- **Files:** patch-install.sh

### SYS-0011: Chunk Factory — eval harness, challenge system, and chunk-builder skill reference
- **Date:** 2026-03-04
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** ollama_builder.py, chunk-eval.sh, SKILL.md, challenge_schema.json, challenge_spec.json, people_lookup.py, people_lookup.py
- **Services restarted:** mythos-api.service

### SYS-0012: patch-clean function — full rollback of deployed patches
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch-clean.sh

### SYS-0012: patch-clean function — full rollback of deployed patches
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch-clean.sh

### SYS-0013: patch-install auto-rollback on failure + integrated artifact cleanup
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch-install.sh

### SYS-0014: Chunk Factory v2 — fix code extractor truncation, richer error feedback, README
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** ollama_builder.py, README.md

### SYS-0014: Chunk Factory v2 — fix code extractor truncation, richer error feedback, README
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** ollama_builder.py, README.md

### SYS-0015: Chunk Foundation — chunk registry, pattern library, grinder engine, build plan
- **Date:** 2026-03-04
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** CHUNK_CONTRACT.json, PLAN.md, PATTERNS.json, ollama_grinder.py, chunk-grind.sh, ollama_builder.py

### SYS-0015: Chunk Foundation — chunk registry, pattern library, grinder engine, build plan
- **Date:** 2026-03-04
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** CHUNK_CONTRACT.json, PLAN.md, PATTERNS.json, ollama_grinder.py, chunk-grind.sh, ollama_builder.py

### SYS-0015: Chunk Foundation — chunk registry, pattern library, grinder engine, build plan
- **Date:** 2026-03-04
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** CHUNK_CONTRACT.json, PLAN.md, PATTERNS.json, ollama_grinder.py, chunk-grind.sh, ollama_builder.py

### SYS-0015: Chunk Foundation — chunk registry, pattern library, grinder engine, build plan
- **Date:** 2026-03-04
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** CHUNK_CONTRACT.json, PLAN.md, PATTERNS.json, ollama_grinder.py, chunk-grind.sh, ollama_builder.py

### SYS-0016: print queue watcher
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** print-watcher.sh, mythos-print-watcher.service
- **Services restarted:** mythos-print-watcher.service

### SYS-0016: print queue watcher
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** print-watcher.sh, mythos-print-watcher.service
- **Services restarted:** mythos-print-watcher.service

### SYS-0017: pdf open wrapper for print queue
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** pdf-open-wrapper.sh, pdf-smart-open.desktop

### SYS-0016: print queue watcher
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** print-watcher.sh, mythos-print-watcher.service
- **Services restarted:** mythos-print-watcher.service

### SYS-0017: pdf open wrapper for print queue
- **Date:** 2026-03-04
- **Type:** MINOR
- **Stream:** SYS
- **Files:** pdf-open-wrapper.sh, pdf-smart-open.desktop

### LOG-0001: SDIP foundation - chunker and ingester
- **Date:** 2026-03-05
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** __init__.py, config.py, sdip_chunker.py, sdip_ingest.py, 001_create_tables.sql
- **SQL:** 001_create_tables.sql

### LOG-0001: SDIP foundation - chunker and ingester
- **Date:** 2026-03-05
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** __init__.py, config.py, sdip_chunker.py, sdip_ingest.py, 001_create_tables.sql
- **SQL:** 001_create_tables.sql

### LOG-0001: SDIP foundation - chunker and ingester
- **Date:** 2026-03-05
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** __init__.py, config.py, sdip_chunker.py, sdip_ingest.py, 001_create_tables.sql
- **SQL:** 001_create_tables.sql

### LOG-0002: SDIP ingest fixes - skip .obsidian, remove phantom manifest import
- **Date:** 2026-03-05
- **Type:** PATCH
- **Stream:** LOG
- **Files:** config.py, sdip_ingest.py

### LOG-0003: SDIP DB connection fix - Unix socket matching Mythos convention
- **Date:** 2026-03-05
- **Type:** PATCH
- **Stream:** LOG
- **Files:** config.py, sdip_ingest.py

### LOG-0004: SDIP sensitivity scanner - regex and LLM classification
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_sensitivity.py

### LOG-0002: SDIP ingest fixes - skip .obsidian, remove phantom manifest import
- **Date:** 2026-03-05
- **Type:** PATCH
- **Stream:** LOG
- **Files:** config.py, sdip_ingest.py

### LOG-0005: SDIP graph builder - Neo4j document/topic/system/chunk nodes
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_graph.py

### LOG-0002: SDIP ingest fixes - skip .obsidian, remove phantom manifest import
- **Date:** 2026-03-05
- **Type:** PATCH
- **Stream:** LOG
- **Files:** config.py, sdip_ingest.py

### LOG-0003: SDIP DB connection fix - Unix socket matching Mythos convention
- **Date:** 2026-03-05
- **Type:** PATCH
- **Stream:** LOG
- **Files:** config.py, sdip_ingest.py

### LOG-0004: SDIP sensitivity scanner - regex and LLM classification
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_sensitivity.py

### LOG-0006: SDIP access membrane - FastAPI routes for document/chunk access
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_membrane.py

### LOG-0004: SDIP sensitivity scanner - regex and LLM classification
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_sensitivity.py

### LOG-0007: SDIP console - Textual TUI for browsing documents and sensitivity
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_console.py

### LOG-0008: SDIP console topics tab - Neo4j topic browser with drilldown
- **Date:** 2026-03-05
- **Type:** PATCH
- **Stream:** LOG
- **Files:** sdip_console.py

### LOG-0005: SDIP graph builder - Neo4j document/topic/system/chunk nodes
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_graph.py

### LOG-0006: SDIP access membrane - FastAPI routes for document/chunk access
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_membrane.py

### LOG-0009: SDIP Command Center dashboard - React page with 6 sub-tabs
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** SDIPDashboard.jsx

### LOG-0007: SDIP console - Textual TUI for browsing documents and sensitivity
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_console.py

### LOG-0008: SDIP console topics tab - Neo4j topic browser with drilldown
- **Date:** 2026-03-05
- **Type:** PATCH
- **Stream:** LOG
- **Files:** sdip_console.py

### LOG-0009: SDIP Command Center dashboard - React page with 6 sub-tabs
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** LOG
- **Files:** SDIPDashboard.jsx

### SYS-0018: Control plane unification — prompt_assembler + prompt_layers fixes (chat_assistant already patched)
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** SYS
- **Services restarted:** mythos-bot.service, mythos-api.service

### NEU-0001: global perception router
- **Date:** 2026-03-05
- **Type:** FOUNDATION
- **Stream:** NEU
- **Files:** perception_router.py, perception_event_types.py

### NEU-0002: perception router integration
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** NEU

### NEU-0002: perception router integration
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** NEU

### NEU-0003: perception router schema fix
- **Date:** 2026-03-05
- **Type:** FIX
- **Stream:** NEU

### NEU-0003: perception router schema fix
- **Date:** 2026-03-05
- **Type:** FIX
- **Stream:** NEU

### SYS-0019: Auto bill matching after CSV import — wire PostImportAnalyzer into importer.py
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** SYS

### NEU-0004: perception_router_fix
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** NEU
- **Services restarted:** mythos-api.service

### SYS-0020: Bills management page — edit match patterns, test against transactions, view match status
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** SYS
- **Files:** Bills.jsx
- **Services restarted:** mythos-api.service

### NEU-0004: perception_router_fix
- **Date:** 2026-03-05
- **Type:** MINOR
- **Stream:** NEU
- **Services restarted:** mythos-api.service

### SYS-0021: Finance Projection Page — per-account daily balance projection with timeline + calendar views
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** projection.py, Projection.jsx
- **Services restarted:** mythos-api.service

### SYS-0021: Finance Projection Page — per-account daily balance projection with timeline + calendar views
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** projection.py, Projection.jsx
- **Services restarted:** mythos-api.service

### SYS-0021: Finance Projection Page — per-account daily balance projection with timeline + calendar views
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** projection.py, Projection.jsx
- **Services restarted:** mythos-api.service

### SYS-0022: Backfill NULL transaction balances + CLI tool + update account balances
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** backfill_balances.py

### SYS-0023: Full account reimport tool with balance verification — wipe + reimport USAA and Sunmark
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** reimport_account.py
- **Services restarted:** mythos-api.service

### SYS-0023: Full account reimport tool with balance verification — wipe + reimport USAA and Sunmark
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** reimport_account.py
- **Services restarted:** mythos-api.service

### SYS-0024: Categorize All — apply category to all matching transactions + create mapping rule
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** Transactions.jsx
- **Services restarted:** mythos-api.service

### SYS-0023: Full account reimport tool with balance verification — wipe + reimport USAA and Sunmark
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** reimport_account.py
- **Services restarted:** mythos-api.service

### SYS-0024: Categorize All — apply category to all matching transactions + create mapping rule
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** Transactions.jsx
- **Services restarted:** mythos-api.service

### SYS-0025: Bills Timeline — visual monthly map of bills and income by day
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** BillsTimeline.jsx

### SYS-0025: Bills Timeline — visual monthly map of bills and income by day
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** BillsTimeline.jsx

### SYS-0025: Bills Timeline — visual monthly map of bills and income by day
- **Date:** 2026-03-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** BillsTimeline.jsx

### LOG-0010: web_search skill and skills awareness layer
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** web_search.py, skills_context.py

### SYS-0026: mx session - self-healing intent-aware shell
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_session.py, mx_intent.py, mx_logger.py, mx_config.yaml, mx_intents.yaml

### LOG-0011: web_search v2 using RSS feeds and Wikipedia
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** LOG
- **Files:** web_search.py

### LOG-0010: web_search skill and skills awareness layer
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** web_search.py, skills_context.py

### LOG-0011: web_search v2 using RSS feeds and Wikipedia
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** LOG
- **Files:** web_search.py

### LOG-0010: web_search skill and skills awareness layer
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** web_search.py, skills_context.py

### SYS-0027: mx session intent and auto journal
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_journal.py

### SYS-0028: mx snapshot serializer and delta engine
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_snapshot.py, mx_delta.py

### SYS-0029: mx pre/post hooks with integrity scan integration
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_hooks.py

### NEU-0005: iris integrity awareness - self-model health injection
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** NEU
- **Files:** iris_integrity.py, __init__.py, iris_integrity_handler.py
- **Services restarted:** mythos-bot.service

### MNE-0004: conversation_bridge_wiring
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** MNE
- **Files:** chat_assistant.py, prompt_layers.yaml
- **Services restarted:** mythos-bot.service, mythos-api.service

### SYS-0030: integrity CLI wrapper
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** SYS
- **Files:** mythos-integrity

### SYS-0026: mx session - self-healing intent-aware shell
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_session.py, mx_intent.py, mx_logger.py, mx_config.yaml

### LOG-0012: Mission engine - Claude to Iris delegation pipeline
- **Date:** 2026-03-07
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** mission_runner.py, graph_bridge.py, MISSION_SPEC.md, audit_handler.yaml, graph_snapshot.yaml

### SYS-0031: mx documentation - diag block and telegram help
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Services restarted:** mythos-bot.service

### LOG-0013: Mission engine - Claude to Iris delegation pipeline
- **Date:** 2026-03-07
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** mission_runner.py, graph_bridge.py, MISSION_SPEC.md, audit_handler.yaml, graph_snapshot.yaml

### LOG-0014: model_benchmark_harness
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** bench_config.json, tasks.py, run_benchmark.py, report.py

### LOG-0011: web_search v2 using RSS feeds and Wikipedia
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** LOG
- **Files:** web_search.py

### SYS-0032: mx polish - version bump, escape fix, snapshot label, imports
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** SYS
- **Services restarted:** mythos-bot.service

### NEU-0006: idle_task_engine (loop.py wiring)
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** NEU
- **Files:** loop.py

### LOG-0014: Mission assembler + modular system archaeology v2
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** mission_assembler.py, mission.yaml, dead_code.md, stress.md, synthesis.md

### NEU-0005: iris integrity awareness - self-model health injection
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** NEU
- **Files:** iris_integrity.py, __init__.py, iris_integrity_handler.py
- **Services restarted:** mythos-bot.service

### SYS-0027: mx session intent and auto journal
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_journal.py

### SYS-0028: mx snapshot serializer and delta engine
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_snapshot.py, mx_delta.py

### SYS-0029: mx pre/post hooks with integrity scan integration
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mx_hooks.py

### MNE-0004: conversation_bridge_wiring
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** MNE
- **Files:** chat_assistant.py, prompt_layers.yaml
- **Services restarted:** mythos-bot.service, mythos-api.service

### SYS-0030: integrity CLI wrapper
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** SYS
- **Files:** mythos-integrity

### LOG-0012: Mission engine - Claude to Iris delegation pipeline
- **Date:** 2026-03-07
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** mission_runner.py, graph_bridge.py, MISSION_SPEC.md, audit_handler.yaml, graph_snapshot.yaml

### LOG-0012: Mission engine - Claude to Iris delegation pipeline
- **Date:** 2026-03-07
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** mission_runner.py, graph_bridge.py, MISSION_SPEC.md, audit_handler.yaml, graph_snapshot.yaml

### LOG-0013: Mission engine - Claude to Iris delegation pipeline
- **Date:** 2026-03-07
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** mission_runner.py, graph_bridge.py, MISSION_SPEC.md, audit_handler.yaml, graph_snapshot.yaml

### LOG-0014: model_benchmark_harness
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** bench_config.json, tasks.py, run_benchmark.py, report.py

### NEU-0006: idle_task_engine (loop.py wiring)
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** NEU
- **Files:** loop.py

### LOG-0014: Mission assembler + modular system archaeology v2
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** mission_assembler.py, mission.yaml, dead_code.md, stress.md, synthesis.md

### NEU-0006: idle_task_engine (loop.py wiring)
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** NEU
- **Files:** loop.py

### SYS-0033: benchmark round 2 - 9 model run config and launcher
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** bench_config_round2.json

### LOG-0015: archaeology round1 - fix false positives
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** mission.yaml, dead_code.md

### NEU-0006: idle_task_engine (loop.py wiring)
- **Date:** 2026-03-07
- **Type:** PATCH
- **Stream:** NEU
- **Files:** loop.py

### LOG-0015: archaeology round1 - fix false positives
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** mission.yaml, dead_code.md

### LOG-0015: archaeology round1 - fix false positives
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** mission.yaml, dead_code.md

### LOG-0015: iris_voice_tuning_harness
- **Date:** 2026-03-07
- **Type:** MINOR
- **Stream:** LOG
- **Files:** tune.py

### LOG-0015: iris_voice_tuning_harness
- **Date:** 2026-03-08
- **Type:** MINOR
- **Stream:** LOG
- **Files:** tune.py

### LOG-0015: iris_voice_tuning_harness
- **Date:** 2026-03-08
- **Type:** MINOR
- **Stream:** LOG
- **Files:** tune.py

### SYS-0034: fix benchmark --config flag not honoured + round2 timeout tuning
- **Date:** 2026-03-08
- **Type:** PATCH
- **Stream:** SYS
- **Files:** bench_config_round2.json

### SYS-0035: Trigger infrastructure — schema, seed data, CLI tool
- **Date:** 2026-03-08
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** sys_0035_trigger_schema.sql, iris-trigger
- **SQL:** sys_0035_trigger_schema.sql

### NEU-0007: Trigger engine — standalone autonomic scheduler service
- **Date:** 2026-03-08
- **Type:** MAJOR
- **Stream:** NEU
- **Files:** trigger_engine.py, trigger_runner.py, mythos-trigger.service
- **Services restarted:** mythos-trigger.service

### NEU-0008: context_engine
- **Date:** 2026-03-08
- **Type:** MINOR
- **Stream:** NEU
- **Files:** context_engine.py, context_access_policy.yaml, iris-context

### SYS-0034: fix benchmark --config flag not honoured + round2 timeout tuning
- **Date:** 2026-03-08
- **Type:** PATCH
- **Stream:** SYS
- **Files:** bench_config_round2.json

### SYS-0034: fix benchmark --config flag not honoured + round2 timeout tuning
- **Date:** 2026-03-08
- **Type:** PATCH
- **Stream:** SYS
- **Files:** bench_config_round2.json

### SYS-0034: Trigger infrastructure — schema, seed data, CLI tool
- **Date:** 2026-03-08
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** sys_0034_trigger_schema.sql, iris-trigger
- **SQL:** sys_0034_trigger_schema.sql

### NEU-0007: Trigger engine — standalone autonomic scheduler service
- **Date:** 2026-03-08
- **Type:** MAJOR
- **Stream:** NEU
- **Files:** trigger_engine.py, trigger_runner.py, mythos-trigger.service
- **Services restarted:** mythos-trigger.service

### SYS-0035: Trigger infrastructure — schema, seed data, CLI tool
- **Date:** 2026-03-08
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** sys_0035_trigger_schema.sql, iris-trigger
- **SQL:** sys_0035_trigger_schema.sql

### NEU-0008: context_engine
- **Date:** 2026-03-08
- **Type:** MINOR
- **Stream:** NEU
- **Files:** context_engine.py, context_access_policy.yaml, iris-context

### SYS-0036: fix_transaction_hash
- **Date:** 2026-03-09
- **Type:** MINOR
- **Stream:** SYS
- **Files:** importer.py
- **SQL:** fix_transaction_hash.sql
- **Services restarted:** mythos-bot.service

### SYS-0036: fix_transaction_hash
- **Date:** 2026-03-09
- **Type:** MINOR
- **Stream:** SYS
- **Files:** importer.py
- **SQL:** fix_transaction_hash.sql
- **Services restarted:** mythos-bot.service

---

### NEU-0009: decision_gate
- **Date:** 2026-03-09
- **Type:** MINOR
- **Stream:** NEU
- **Files:** decision_gate.py, iris-decide
- **SQL:** neu_0009_decision_gate_triggers.sql
- **Services restarted:** mythos-trigger.service

### SYS-0036: fix_transaction_hash
- **Date:** 2026-03-09
- **Type:** MINOR
- **Stream:** SYS
- **Files:** importer.py
- **SQL:** fix_transaction_hash.sql
- **Services restarted:** mythos-bot.service

### SYS-0037: finance_dashboard_v2
- **Date:** 2026-03-09
- **Type:** MINOR
- **Stream:** SYS
- **Files:** finance_dashboard.py, DashboardV2.jsx, BillsDetailV2.jsx
- **Services restarted:** mythos-api.service

### SYS-0037: finance_dashboard_v2
- **Date:** 2026-03-09
- **Type:** MINOR
- **Stream:** SYS
- **Files:** finance_dashboard.py, DashboardV2.jsx, BillsDetailV2.jsx
- **Services restarted:** mythos-api.service

### SYS-0038: post_install_pipeline
- **Date:** 2026-03-09
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** post_install.py

### MNE-0005: youtube_transcript_intake
- **Date:** 2026-03-09
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_intake.py
- **SQL:** youtube_videos.sql
- **Services restarted:** mythos-bot.service

### SYS-0038: post_install_pipeline
- **Date:** 2026-03-09
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** post_install.py

### SYS-0038: post_install_pipeline
- **Date:** 2026-03-09
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** post_install.py

### MNE-0005: youtube_transcript_intake
- **Date:** 2026-03-09
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_intake.py
- **SQL:** youtube_videos.sql
- **Services restarted:** mythos-bot.service

### MNE-0005: youtube_transcript_intake
- **Date:** 2026-03-09
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_intake.py
- **SQL:** youtube_videos.sql
- **Services restarted:** mythos-bot.service

### SEN-0001: chart_pipeline_birth_time_sourcing
- **Date:** 2026-03-10
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** chart_pipeline.py

### LOG-0016: doc_gap_worker
- **Date:** 2026-03-10
- **Type:** MINOR
- **Stream:** LOG
- **Files:** mythos-doc-gap

### SEN-0001: chart_pipeline_birth_time_sourcing
- **Date:** 2026-03-10
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** chart_pipeline.py

### SEN-0001: chart_pipeline_birth_time_sourcing
- **Date:** 2026-03-10
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** chart_pipeline.py

### LOG-0016: doc_gap_worker
- **Date:** 2026-03-10
- **Type:** MINOR
- **Stream:** LOG
- **Files:** mythos-doc-gap

### LOG-0017: browser_automation
- **Date:** 2026-03-10
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** __init__.py, core.py, web_browser.py, iris-browse
- **Services restarted:** mythos-bot.service, mythos-api.service

### LOG-0017: browser_automation
- **Date:** 2026-03-10
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** __init__.py, core.py, web_browser.py, iris-browse
- **Services restarted:** mythos-bot.service, mythos-api.service

### LOG-0017: browser_automation
- **Date:** 2026-03-10
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** __init__.py, core.py, web_browser.py, iris-browse
- **Services restarted:** mythos-bot.service, mythos-api.service

### SYS-0039: cc3_foundation
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** Badge.jsx, MoneyAmount.jsx, Tabs.jsx, Modal.jsx, Toast.jsx, SearchInput.jsx, SplitPane.jsx, index.js, PatternMatcher.jsx
- **Services restarted:** mythos-api.service

### SYS-0039: cc3_foundation
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** Badge.jsx, MoneyAmount.jsx, Tabs.jsx, Modal.jsx, Toast.jsx, SearchInput.jsx, SplitPane.jsx, index.js, PatternMatcher.jsx
- **Services restarted:** mythos-api.service

### SYS-0039: cc3_foundation
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** Badge.jsx, MoneyAmount.jsx, Tabs.jsx, Modal.jsx, Toast.jsx, SearchInput.jsx, SplitPane.jsx, index.js, PatternMatcher.jsx
- **Services restarted:** mythos-api.service

### SYS-0040: grocery_list_system
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** grocery_tables.sql, grocery_skill.py, grocery_routes.py, GroceryPage.jsx
- **SQL:** grocery_tables.sql
- **Services restarted:** mythos-bot.service, mythos-api.service

### SYS-0040: grocery_telegram_skill
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** grocery_skill.py
- **SQL:** drop_grocery_tables.sql
- **Services restarted:** mythos-bot.service

### SYS-0040: grocery_telegram_skill
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** grocery_skill.py
- **SQL:** drop_grocery_tables.sql
- **Services restarted:** mythos-bot.service

### SYS-0040: grocery_telegram_skill
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** grocery_skill.py
- **SQL:** drop_grocery_tables.sql
- **Services restarted:** mythos-bot.service

### SYS-0040: grocery_telegram_skill
- **Date:** 2026-03-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** grocery_skill.py
- **SQL:** drop_grocery_tables.sql
- **Services restarted:** mythos-bot.service

### SEN-0002: Solar & space weather ingestion service
- **Date:** 2026-03-13
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** solar_ingest.py, solar_handler.py, mythos-solar-ingest.service
- **SQL:** sen_0002_solar_space_weather.sql
- **Services restarted:** mythos-bot.service

### SEN-0003: Earthquake & seismic monitoring ingestion
- **Date:** 2026-03-13
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** seismic_ingest.py, quakes_handler.py, mythos-seismic-ingest.service
- **SQL:** sen_0003_earthquake_tables.sql
- **Services restarted:** mythos-bot.service

### SEN-0004-LEGACY: Planetary geometry engine — positions, aspects, alignments, forcing vectors (pre-stream-tracking, number collision resolved 2026-04-21 by SEN-0007)
- **Date:** 2026-03-13
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** planetary_engine.py, planets_handler.py, mythos-planetary-engine.service
- **SQL:** sen_0004_planetary_geometry.sql
- **Services restarted:** mythos-bot.service

### SEN-0005: observatory neo4j graph builder
- **Date:** 2026-03-16
- **Type:** MINOR
- **Stream:** SEN
- **Files:** observatory_graph.py
- **SQL:** SEN-0005_observatory_correlations.sql
- **Services restarted:** mythos-obs-graph.service

### SYS-0041: person node cleanup and CorePerson taxonomy
- **Date:** 2026-03-17
- **Type:** MINOR
- **Stream:** SYS

### SYS-0042: shell to telegram loop
- **Date:** 2026-03-17
- **Type:** MINOR
- **Stream:** SYS
- **Files:** shell_result.py
- **Services restarted:** mythos-api.service

### SYS-0043: homebridge vizio smartcast siri control
- **Date:** 2026-03-17
- **Type:** MINOR
- **Stream:** SYS

### LOG-0018: conversation_engine_foundation
- **Date:** 2026-03-17
- **Type:** MAJOR
- **Stream:** LOG
- **Files:** __init__.py, models.py, ollama_client.py, __init__.py, base.py, registry.py, schemas.py, __init__.py, chain.py, executor.py, __init__.py, response.py, __init__.py, telegram.py, validate_foundation.py, conversation_modes.yaml, CONVERSATION_ENGINE_SPEC.md

### SYS-0044: Denkers Co public website - static hosting via systemd + tunnel
- **Date:** 2026-03-19
- **Type:** MINOR
- **Stream:** SYS

### SYS-0044: Denkers Co public website - static hosting via systemd + tunnel
- **Date:** 2026-03-19
- **Type:** MINOR
- **Stream:** SYS

### SYS-0044: Denkers Co public website - static hosting via systemd + tunnel
- **Date:** 2026-03-19
- **Type:** MINOR
- **Stream:** SYS

### MNE-0006: Fix YouTube transcript intake for youtube-transcript-api >= 1.2.0
- **Date:** 2026-03-19
- **Type:** PATCH
- **Stream:** MNE
- **Files:** youtube_intake.py

### MNE-0006: Fix YouTube transcript intake for youtube-transcript-api >= 1.2.0
- **Date:** 2026-03-19
- **Type:** PATCH
- **Stream:** MNE
- **Files:** youtube_intake.py

### LOG-0019: Identity prompt fix — skill results ground truth rule, anti-hallucination for video intake
- **Date:** 2026-03-19
- **Type:** PATCH
- **Stream:** LOG
- **Files:** iris_identity.md

### MNE-0007: YouTube channel monitor — auto-ingest transcripts from subscribed channels
- **Date:** 2026-03-19
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_channel_monitor.py, youtube_channel.py
- **SQL:** mne_0007_youtube_channels.sql

### MNE-0006: Fix YouTube transcript intake for youtube-transcript-api >= 1.2.0
- **Date:** 2026-03-19
- **Type:** PATCH
- **Stream:** MNE
- **Files:** youtube_intake.py

### LOG-0019: Identity prompt fix — skill results ground truth rule, anti-hallucination for video intake
- **Date:** 2026-03-19
- **Type:** PATCH
- **Stream:** LOG
- **Files:** iris_identity.md

### LOG-0019: Identity prompt fix — skill results ground truth rule, anti-hallucination for video intake
- **Date:** 2026-03-19
- **Type:** PATCH
- **Stream:** LOG
- **Files:** iris_identity.md

### MNE-0007: YouTube channel monitor — auto-ingest transcripts from subscribed channels
- **Date:** 2026-03-19
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_channel_monitor.py, youtube_channel.py
- **SQL:** mne_0007_youtube_channels.sql

### MNE-0008: YouTube Redis queue — priority-based ingestion with full channel backfill via yt-dlp
- **Date:** 2026-03-19
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_queue_consumer.py, youtube_channel_monitor.py, youtube_channel.py

### MNE-0008: YouTube Redis queue — priority-based ingestion with full channel backfill via yt-dlp
- **Date:** 2026-03-19
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_queue_consumer.py, youtube_channel_monitor.py, youtube_channel.py

### MNE-0008: YouTube Redis queue — priority-based ingestion with full channel backfill via yt-dlp
- **Date:** 2026-03-19
- **Type:** MAJOR
- **Stream:** MNE
- **Files:** youtube_queue_consumer.py, youtube_channel_monitor.py, youtube_channel.py

### MNE-0009: youtube transcript fix
- **Date:** 2026-03-23
- **Type:** MINOR
- **Stream:** MNE
- **Files:** youtube_intake.py, youtube_queue_consumer.py, youtube_channel_monitor.py
- **Services restarted:** mythos-bot.service

### MNE-0009: youtube transcript fix
- **Date:** 2026-03-23
- **Type:** MINOR
- **Stream:** MNE
- **Files:** youtube_intake.py, youtube_queue_consumer.py, youtube_channel_monitor.py
- **Services restarted:** mythos-bot.service

### SEN-0007: transit_interpreter
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** SEN
- **Files:** transit_interpreter.py, __init__.py, morning_brief.py
- **Services restarted:** mythos-api.service, mythos-bot.service

### SEN-0007: transit_interpreter
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** SEN
- **Files:** transit_interpreter.py, __init__.py, morning_brief.py
- **Services restarted:** mythos-api.service, mythos-bot.service

### MNE-0010: meditation renderer
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** meditation.py, meditation_handler.py, iris-meditate, .gitkeep

### MNE-0010: meditation renderer
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** meditation.py, meditation_handler.py, iris-meditate, .gitkeep

### MNE-0011: meditation markup format
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** mmf.py, iris-meditate, expanded_bandwidth.yaml

### MNE-0011: meditation markup format
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** mmf.py, iris-meditate, expanded_bandwidth.yaml

### MNE-0012: meditation music and ogg fix
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** mmf.py, meditation_config.yaml, iris-music-fetch

### MNE-0011: meditation markup format
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** mmf.py, iris-meditate, expanded_bandwidth.yaml

### MNE-0012: meditation music and ogg fix
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** mmf.py, meditation_config.yaml, iris-music-fetch

### MNE-0012: meditation music and ogg fix
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** mmf.py, meditation_config.yaml, iris-music-fetch

### MNE-0012: meditation music and ogg fix
- **Date:** 2026-03-25
- **Type:** MINOR
- **Stream:** MNE
- **Files:** mmf.py, meditation_config.yaml, iris-music-fetch

### MNE-0013: meditation bgmix sample rate fix
- **Date:** 2026-03-25
- **Type:** PATCH
- **Stream:** MNE

### MNE-0014: meditation bgmix stream_loop fix
- **Date:** 2026-03-26
- **Type:** PATCH
- **Stream:** MNE
- **Files:** mmf.py

### MNE-0014: meditation bgmix stream_loop fix
- **Date:** 2026-03-26
- **Type:** PATCH
- **Stream:** MNE
- **Files:** mmf.py

### MNE-0014: meditation bgmix stream_loop fix
- **Date:** 2026-03-26
- **Type:** PATCH
- **Stream:** MNE
- **Files:** mmf.py

### MNE-0015: youtube_queue_fix
- **Date:** 2026-03-27
- **Type:** MINOR
- **Stream:** MNE
- **Files:** youtube_queue_consumer.py, youtube_channel_monitor.py
- **Services restarted:** mythos-youtube-queue.service, mythos-youtube-monitor.service

### MNE-0015: youtube_queue_fix
- **Date:** 2026-03-27
- **Type:** MINOR
- **Stream:** MNE
- **Files:** youtube_queue_consumer.py, youtube_channel_monitor.py
- **Services restarted:** mythos-youtube-queue.service, mythos-youtube-monitor.service

### MNE-0015: youtube_queue_fix
- **Date:** 2026-03-27
- **Type:** MINOR
- **Stream:** MNE
- **Files:** youtube_queue_consumer.py, youtube_channel_monitor.py
- **Services restarted:** mythos-youtube-queue.service, mythos-youtube-monitor.service

### SEN-0001: chart_pipeline_birth_time_sourcing
- **Date:** 2026-03-27
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** chart_pipeline.py

### SEN-0001: seraphe_lunar_generator
- **Date:** 2026-03-27
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** seraphe_lunar_generator.py, lunar_calendar_skill.py, lunar_calendar_worker.py, seraphe-lunar, mythos-worker-lunar.service
- **Services restarted:** mythos-bot.service

### SEN-0001: seraphe_lunar_generator
- **Date:** 2026-03-27
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** seraphe_lunar_generator.py, lunar_calendar_skill.py, lunar_calendar_worker.py, seraphe-lunar, mythos-worker-lunar.service
- **Services restarted:** mythos-bot.service

### SEN-0001: seraphe_lunar_generator
- **Date:** 2026-03-27
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** seraphe_lunar_generator.py, lunar_calendar_skill.py, lunar_calendar_worker.py, seraphe-lunar, mythos-worker-lunar.service
- **Services restarted:** mythos-bot.service

### SEN-0001: seraphe_lunar_generator
- **Date:** 2026-03-27
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** seraphe_lunar_generator.py, lunar_calendar_skill.py, lunar_calendar_worker.py, seraphe-lunar, mythos-worker-lunar.service
- **Services restarted:** mythos-bot.service

### NEU-0011: grid_processing_manifest
- **Date:** 2026-03-31
- **Type:** MAJOR
- **Stream:** NEU
- **Services restarted:** mythos-bot.service, mythos-worker-grid.service

### NEU-0011: grid_processing_manifest
- **Date:** 2026-03-31
- **Type:** MAJOR
- **Stream:** NEU
- **Services restarted:** mythos-bot.service, mythos-worker-grid.service

### NEU-0012: layer1_perception
- **Date:** 2026-03-31
- **Type:** MAJOR
- **Stream:** NEU
- **Services restarted:** mythos-worker-grid.service

### NEU-0012: layer1_perception
- **Date:** 2026-03-31
- **Type:** MAJOR
- **Stream:** NEU
- **Services restarted:** mythos-worker-grid.service

### NEU-0013: iris_modelfile
- **Date:** 2026-03-31
- **Type:** MAJOR
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-bot.service, mythos-api.service

### SYS-0045: doc_update_modelfile
- **Date:** 2026-03-31
- **Type:** MINOR
- **Stream:** SYS

### NEU-0013: iris_modelfile
- **Date:** 2026-03-31
- **Type:** MAJOR
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-bot.service, mythos-api.service

### SYS-0046: doc_fix_modelfile
- **Date:** 2026-03-31
- **Type:** PATCH
- **Stream:** SYS

### NEU-0014: calibration_harness
- **Date:** 2026-03-31
- **Type:** MINOR
- **Stream:** NEU
- **Files:** iris_calibrate.py

### SYS-0045: doc_update_modelfile
- **Date:** 2026-03-31
- **Type:** MINOR
- **Stream:** SYS

### SEN-0002: Solar & space weather ingestion service
- **Date:** 2026-03-31
- **Type:** MAJOR
- **Stream:** SEN
- **Files:** solar_ingest.py, solar_handler.py, mythos-solar-ingest.service
- **SQL:** sen_0002_solar_space_weather.sql
- **Services restarted:** mythos-bot.service

### SEN-0003: spiral_output_fix
- **Date:** 2026-03-31
- **Type:** PATCH
- **Stream:** SEN
- **Files:** spiral_time.py
- **Services restarted:** mythos-api.service

### SYS-0046: doc_fix_modelfile
- **Date:** 2026-03-31
- **Type:** PATCH
- **Stream:** SYS

### NEU-0014: calibration_harness
- **Date:** 2026-03-31
- **Type:** MINOR
- **Stream:** NEU
- **Files:** iris_calibrate.py

### SEN-0003: spiral_output_fix
- **Date:** 2026-03-31
- **Type:** PATCH
- **Stream:** SEN
- **Files:** spiral_time.py
- **Services restarted:** mythos-api.service

### NEU-0015: modelfile_v2
- **Date:** 2026-04-01
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-api.service

### NEU-0015: modelfile_v2
- **Date:** 2026-04-01
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-api.service

### NEU-0015: modelfile_v2
- **Date:** 2026-04-01
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-api.service

### NEU-0015: modelfile_v2
- **Date:** 2026-04-01
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-api.service

### NEU-0016: baked_message_flow
- **Date:** 2026-04-02
- **Type:** MAJOR
- **Stream:** NEU
- **Services restarted:** mythos-api.service, mythos-bot.service

### NEU-0017: anticonfab_v3
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-api.service

### NEU-0018: iris_deep_modelfile
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile.deep
- **Services restarted:** mythos-api.service, mythos-bot.service

### NEU-0016: baked_message_flow
- **Date:** 2026-04-02
- **Type:** MAJOR
- **Stream:** NEU
- **Services restarted:** mythos-api.service, mythos-bot.service

### NEU-0017: anticonfab_v3
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** NEU
- **Files:** Modelfile
- **Services restarted:** mythos-api.service

### NEU-0019: Anti-confab capability fabrication + closing question fix
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile, Modelfile.deep
- **Services restarted:** mythos-bot.service

### NEU-0018: iris_deep_modelfile
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile.deep
- **Services restarted:** mythos-api.service, mythos-bot.service

### SYS-0047: Consolidate model aliases into core/model_aliases.py
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** SYS
- **Files:** model_aliases.py
- **Services restarted:** mythos-bot.service

### SYS-0048: Fix remaining alias refs (chat_mode, help_handler) + ARCHITECTURE.md update
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** SYS
- **Services restarted:** mythos-bot.service

### NEU-0018: Anti-confab capability fabrication + closing question fix
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile, Modelfile.deep
- **Services restarted:** mythos-bot.service

### NEU-0019: Anti-confab capability fabrication + closing question fix
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** NEU
- **Files:** Modelfile, Modelfile.deep
- **Services restarted:** mythos-bot.service

### SYS-0047: Consolidate model aliases into core/model_aliases.py
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** SYS
- **Files:** model_aliases.py
- **Services restarted:** mythos-bot.service

### SYS-0048: Fix remaining alias refs (chat_mode, help_handler) + ARCHITECTURE.md update
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** SYS
- **Services restarted:** mythos-bot.service

### SYS-0049: TODO.md cleanup — deduplicate, update active work, restructure
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** SYS
- **Files:** TODO.md

### SYS-0050: autodoc_engine
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** SYS
- **Files:** autodoc.py

### SYS-0051: autodoc_skip_patches_and_archive
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** SYS
- **Files:** autodoc.py

### SYS-0051: autodoc_skip_patches_and_archive
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** SYS
- **Files:** autodoc.py

### SYS-0049: TODO.md cleanup — deduplicate, update active work, restructure
- **Date:** 2026-04-02
- **Type:** PATCH
- **Stream:** SYS
- **Files:** TODO.md

### SYS-0052: watchlist with streaming deep links
- **Date:** 2026-04-02
- **Type:** MINOR
- **Stream:** SYS
- **Files:** sys_0052_watchlist.sql, watchlist_handler.py
- **SQL:** sys_0052_watchlist.sql
- **Services restarted:** mythos-bot.service

### SYS-0050: autodoc_engine
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** SYS
- **Files:** autodoc.py

### SYS-0051: autodoc_skip_patches_and_archive
- **Date:** 2026-04-03
- **Type:** PATCH
- **Stream:** SYS
- **Files:** autodoc.py

### SYS-0052: watchlist with streaming deep links
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** SYS
- **Files:** sys_0052_watchlist.sql, watchlist_handler.py
- **SQL:** sys_0052_watchlist.sql
- **Services restarted:** mythos-bot.service

### LOG-0020: SDIP dataset ingestion framework + eCFR parser
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** LOG
- **Files:** __init__.py, ecfr_parser.py, sdip_ingest_dataset.py, README.md

### LOG-0020: SDIP dataset ingestion framework + eCFR parser
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** LOG
- **Files:** __init__.py, ecfr_parser.py, sdip_ingest_dataset.py, README.md

### LOG-0021: SDIP LLM classifier — topic/domain/entity extraction per chunk
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_classifier.py

### LOG-0021: SDIP LLM classifier — topic/domain/entity extraction per chunk
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_classifier.py

### LOG-0020: SDIP dataset ingestion framework + eCFR parser
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** LOG
- **Files:** __init__.py, ecfr_parser.py, sdip_ingest_dataset.py, README.md

### LOG-0021: SDIP LLM classifier — topic/domain/entity extraction per chunk
- **Date:** 2026-04-03
- **Type:** MINOR
- **Stream:** LOG
- **Files:** sdip_classifier.py

### SYS-0053: autodoc2_skeleton
- **Date:** 2026-04-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** __init__.py, cli.py, config.py, filters.py, walker.py, engine.py, neo4j_writer.py, markdown_writer.py, llm_client.py, __init__.py, python_walker.py

### SYS-0054: autodoc2_fix_treesitter
- **Date:** 2026-04-06
- **Type:** PATCH
- **Stream:** SYS
- **Files:** python_walker.py

### SYS-0055: autodoc2_js_ts
- **Date:** 2026-04-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** filters.py, __init__.py, javascript_walker.py, typescript_walker.py

### SYS-0053: autodoc2_skeleton
- **Date:** 2026-04-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** __init__.py, cli.py, config.py, filters.py, walker.py, engine.py, neo4j_writer.py, markdown_writer.py, llm_client.py, __init__.py, python_walker.py

### SYS-0053: autodoc2_skeleton
- **Date:** 2026-04-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** __init__.py, cli.py, config.py, filters.py, walker.py, engine.py, neo4j_writer.py, markdown_writer.py, llm_client.py, __init__.py, python_walker.py

### SYS-0054: autodoc2_fix_treesitter
- **Date:** 2026-04-06
- **Type:** PATCH
- **Stream:** SYS
- **Files:** python_walker.py

### SYS-0055: autodoc2_js_ts
- **Date:** 2026-04-06
- **Type:** MINOR
- **Stream:** SYS
- **Files:** filters.py, __init__.py, javascript_walker.py, typescript_walker.py

### SYS-0056: rode_autotransfer
- **Date:** 2026-04-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** rode_transfer.py, rode-autotransfer

### SYS-0057: rode_autotransfer_fix
- **Date:** 2026-04-07
- **Type:** PATCH
- **Stream:** SYS

### SYS-0058: autodoc2_phase3_walkers
- **Date:** 2026-04-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** sql_walker.py, php_walker.py, go_walker.py, bash_walker.py, yaml_walker.py, json_walker.py, rust_walker.py, __init__.py, filters.py, engine.py

### SYS-0057: rode_autotransfer_fix
- **Date:** 2026-04-07
- **Type:** PATCH
- **Stream:** SYS

### SYS-0057: rode_autotransfer_fix
- **Date:** 2026-04-07
- **Type:** PATCH
- **Stream:** SYS

### SYS-0058: autodoc2_phase3_walkers
- **Date:** 2026-04-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** sql_walker.py, php_walker.py, go_walker.py, bash_walker.py, yaml_walker.py, json_walker.py, rust_walker.py, __init__.py, filters.py, engine.py

### SYS-0058: autodoc2_phase3_walkers
- **Date:** 2026-04-07
- **Type:** MINOR
- **Stream:** SYS
- **Files:** sql_walker.py, php_walker.py, go_walker.py, bash_walker.py, yaml_walker.py, json_walker.py, rust_walker.py, __init__.py, filters.py, engine.py

### SYS-0059: mythos-jupyter service + demo prep script
- **Date:** 2026-04-10
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mythos-jupyter-launcher, jupyter-token, jupyter-rotate-token, prep_demo_graphs.sh, README.md
- **Services restarted:** mythos-jupyter.service

### SYS-0059: mythos-jupyter service + demo prep script
- **Date:** 2026-04-10
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mythos-jupyter-launcher, jupyter-token, jupyter-rotate-token, prep_demo_graphs.sh, README.md
- **Services restarted:** mythos-jupyter.service

### SYS-0059: mythos-jupyter service + demo prep script
- **Date:** 2026-04-10
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mythos-jupyter-launcher, jupyter-token, jupyter-rotate-token, prep_demo_graphs.sh, README.md
- **Services restarted:** mythos-jupyter.service

### SYS-0060: git permissions and sync recovery
- **Date:** 2026-04-10
- **Type:** MINOR
- **Stream:** SYS

### SYS-0062: privilege foundation (wrappers + sudoers)
- **Date:** 2026-04-11
- **Type:** MAJOR
- **Stream:** SYS

### SYS-0063: framework migration to SYS-0062 wrappers
- **Date:** 2026-04-11
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch_base.py

### SYS-0063: framework migration to SYS-0062 wrappers
- **Date:** 2026-04-11
- **Type:** MINOR
- **Stream:** SYS

### SYS-0064: security cleanup — remove cp * rule from mythos-monitor
- **Date:** 2026-04-12
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** mythos-monitor

### SYS-0066: monitor passive mode + patch-install git integration
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mythos_patch_monitor.py
- **Services restarted:** mythos-patch-monitor.service

### SYS-0067: finish SYS-0066 patch-install.sh git integration
- **Date:** 2026-04-12
- **Type:** PATCH
- **Stream:** SYS
- **Files:** patch-install.sh

### SYS-0068: security cleanup retry — remove cp * rule (SYS-0064 had buggy verify)
- **Date:** 2026-04-12
- **Type:** MAJOR
- **Stream:** SYS
- **Files:** mythos-monitor

### SYS-0069: session note for 2026-04-12 cleanup work
- **Date:** 2026-04-12
- **Type:** PATCH
- **Stream:** SYS
- **Files:** 2026-04-12-cleanup.md

### SYS-0070: docs update — patch system overhaul reflected in TODO.md + ARCHITECTURE.md
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** TODO.md, ARCHITECTURE.md


### SYS-0071: finance v1 preflight - archive code and rename tables
- **Date:** 2026-04-12
- **Type:** MAJOR
- **Stream:** SYS
- **SQL:** SYS-0071_rename_v1_finance_tables.sql

### SYS-0072: finance_v2_plan
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** FINANCE_V2.md, FINANCE_V2_ARCHITECTURE.md
- **SQL:** drop_v1.sql

### SYS-0073: finance_v2_real_plan
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** FINANCE_V2.md

### SYS-0074: finance_v2_plan_renumber_note
- **Date:** 2026-04-12
- **Type:** PATCH
- **Stream:** SYS

### SYS-0075: finance v2 schema infra (entities, accounts, triggers, seeds)
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **SQL:** SYS-0075_finance_v2_schema_infra.sql

### SYS-0076: finance v2 ledger core (imports, observations, transactions, entries)
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **SQL:** SYS-0076_finance_v2_ledger.sql

### SYS-0077: finance v2 workflow & documentation bootstrap (Patch C)
- **Date:** 2026-04-12
- **Type:** PATCH
- **Stream:** SYS
- **Files:** WORKFLOW.md, SYSTEM_FINANCE.md, ARCHITECTURE.md

### SYS-0078: handoff system bootstrap — tool, manifest, spec
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mythos-handoff, MANIFEST.yaml, NEXT_PATCH_SPEC.md, README.md, WORKFLOW.md, SYSTEM_FINANCE.md

### SYS-0079: fix tgdeferrable validation cast + add empty-ledger guards
- **Date:** 2026-04-12
- **Type:** PATCH
- **Stream:** SYS
- **Files:** MANIFEST.yaml

### SYS-0080: handoff --strict flag + PatchBase.verify_handoff() helper
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** mythos-handoff, mythos-handoff, patch_base.py

### SYS-0081: Gemini review workflow — template, Phase 2.5, review_link field (reviewed by Castor 2-round, 2026-04-12)
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **Files:** GEMINI_REVIEW_TEMPLATE.md, WORKFLOW.md, WORKFLOW.md, patch_base.py, patch_base.py, SYSTEM_FINANCE.md, MANIFEST.yaml

### SYS-0082: finance v2 doc reconciliation (SYSTEM_FINANCE status + ledger)
- **Date:** 2026-04-12
- **Type:** PATCH
- **Stream:** SYS

### SYS-0083: finance v2 patch D — merchants & patterns [FAILED — ROLLED BACK]
- **Date:** 2026-04-12
- **Type:** MINOR
- **Stream:** SYS
- **SQL:** SYS-0083_finance_v2_merchants.sql (syntax error at line 114)
- **Failure:** `ROLLBACK TO SAVEPOINT` inside PL/pgSQL `DO` block is not permitted. Postgres rolled back the migration transaction cleanly; database state is pristine pre-Patch-D. STREAMS.json and this entry were written by a `PatchBase.finish()` bug where `self.errors` was not checked before side effects. Fixed in SYS-0084 (Path 2 Bootstrap Meta-Patch). Patch D re-landed as SYS-0085 with the verification block restructured to use PL/pgSQL sub-blocks with `BEGIN ... EXCEPTION` and explicit `DELETE` cleanup instead of `ROLLBACK TO SAVEPOINT`.
- **Lesson:** PL/pgSQL `DO` blocks are anonymous code blocks, not transactions — they cannot use `ROLLBACK TO SAVEPOINT`. Use sub-block exception handling with explicit cleanup, or move schema verification into named `PROCEDURE`s.

### SYS-0084: PatchBase.finish() error-gate + PatchFinishError (Path 2 Bootstrap)
- **Date:** 2026-04-13
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch_base.py
- **Note:** Path 2 Bootstrap Meta-Patch. apply_patch.py does not import PatchBase (fixes the framework from outside). Adds PatchFinishError and moves STREAMS.json/PATCH_HISTORY writes behind an error-gate in finish(). Post-install pipeline now runs before the ledger update so pipeline failures also block it.

### SYS-0085: finance v2 patch D re-land — merchants & patterns
- **Date:** 2026-04-14
- **Type:** MINOR
- **Stream:** SYS
- **SQL:** SYS-0085_finance_v2_merchants.sql
- **Review:** Castor round 1 (finance review), round 2 (3-question pre-build), round 3 (inline DO block clearance). Re-land of SYS-0083 with SAVEPOINT/ROLLBACK removed from DO block (not permitted in PL/pgSQL anonymous blocks).

### SEN-0004: astrology v2 anchor
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SEN
- **Files:** SUB-SYSTEMS.md, SYSTEM_ASTROLOGY.md, ASTROLOGY_V2.md, NEXT_PATCH_SPEC.md, __init__.py, check_accuracy.py, expected_aspects.json, ARCHITECTURE.md

### SEN-0005: ephemeris provider (letter B)
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SEN
- **Files:** __init__.py, ephemeris.py, .env

### SEN-0006: astrology v2 letter C engine — ephemeris consolidation
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SEN
- **Files:** se07066s.se1, se90377s.se1, se05145s.se1, s136108s.se1, s136472s.se1, se50000s.se1, se10199s.se1, lunar_calendar_worker.py, planetary_engine.py, seraphe_lunar_generator.py, transit_pressure.py, NEXT_PATCH_SPEC.md

### SEN-0007: astrology v2 letter C.1 cleanup
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SEN
- **Files:** charts_adriaan_harold_denkers, adriaan_harold_denkers.yaml, astro_position.py, PATCH_HISTORY.md, NEXT_PATCH_SPEC.md

### SEN-0008: astrology v2 letter D — natal state postgres-first
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SEN
- **Files:** natal_generator.py, ka.json, seraphe.json, NEXT_PATCH_SPEC.md

### SEN-0009: astrology v2 letter E — daily transits wiring
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SEN
- **Files:** transit_handler.py, transit_pressure.py, mythos_bot.py, NEXT_PATCH_SPEC.md

### SEN-0010: astrology v2 letter F — integration + completion
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SEN
- **Files:** daily-transits, SYSTEM_ASTROLOGY.md, SUB-SYSTEMS.md, NEXT_PATCH_SPEC.md

### SEN-0011: transit_pressure db connection + natal positions fix
- **Date:** 2026-04-21
- **Type:** PATCH
- **Stream:** SEN
- **Files:** transit_pressure.py, transit_pressure.py

### SEN-0012: transit_handler fix — compute+persist not just cache read
- **Date:** 2026-04-21
- **Type:** PATCH
- **Stream:** SEN
- **Files:** transit_handler.py

### SEN-0013: transit_interpreter: gemma4:26b + num_predict 512
- **Date:** 2026-04-21
- **Type:** PATCH
- **Stream:** SEN
- **Files:** transit_interpreter.py, transit_interpreter.py

### SEN-0014: transit_interpreter: revert to qwen3, keep num_predict=512
- **Date:** 2026-04-21
- **Type:** PATCH
- **Stream:** SEN
- **Files:** transit_interpreter.py

### SEN-0015: docs update — astrology v2 complete + hotfix record
- **Date:** 2026-04-21
- **Type:** PATCH
- **Stream:** SEN
- **Files:** SYSTEM_ASTROLOGY.md, ARCHITECTURE.md, TODO.md

### SYS-0086: autodoc2 subsystem registration
- **Date:** 2026-04-21
- **Type:** PATCH
- **Stream:** SYS
- **Files:** SYSTEM_AUTODOC2.md, AUTODOC2_V2.md, NEXT_PATCH_SPEC.md, ARCHITECTURE.md, SUB-SYSTEMS.md, SUB-SYSTEMS.md, _INDEX.md

### SYS-0087: PatchBase microtool kit — str_replace + 7 helpers
- **Date:** 2026-04-21
- **Type:** MINOR
- **Stream:** SYS
- **Files:** patch_base.py
