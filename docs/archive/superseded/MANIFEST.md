# Mythos System — Documentation Manifest
> **Purpose:** Tell any LLM exactly what files to read before working on a given area.
> **Location:** `/opt/mythos/docs/MANIFEST.md`
> **Rule:** Before working on ANY subsystem, read this file first. Then pull the listed files.

---

## Quick Start (Every Session)

```
/opt/mythos/docs/TODO.md              — What we're working on right now
/opt/mythos/docs/ARCHITECTURE.md      — What exists and is stable
/opt/mythos/docs/MANIFEST.md          — This file (what to pull for what)
```

---

## By Task Area

### Prompt System / Voice / Personality
```
/opt/mythos/core/prompt_assembler.py          — THE single source of truth for all prompts
/opt/mythos/prompts/iris_identity.md           — Layer 1: Who Iris is
/opt/mythos/prompts/personality.yaml           — Layer 2: Slider values (verbosity, warmth, etc.)
/opt/mythos/prompts/voice.yaml                 — Layer 3: Voice anti-patterns (base)
/opt/mythos/prompts/voices/                    — Voice profiles (claude.yaml, gpt4o.yaml, iris.yaml)
/opt/mythos/prompts/modes/                     — Layer 4: Mode configs (hearthfire, forge, oracle, etc.)
/opt/mythos/prompts/users/                     — Layer 5: Per-user profiles (ka_tuar_el.yaml, seraphe.yaml)
/opt/mythos/prompts/iris_reference.md          — Cosmology & lineage reference (loaded conditionally)
```

### Telegram Bot
```
/opt/mythos/telegram_bot/mythos_bot.py                    — Main bot entry point, handler registration
/opt/mythos/telegram_bot/handlers/chat_mode.py            — Core chat handler (calls prompt_assembler)
/opt/mythos/telegram_bot/handlers/                        — All command handlers
```
Handler index (check file for actual commands):
- `finance_handler.py` — /balance, /bills, /spend, /income, /budget
- `astrology_handler.py` — Chart calculations, aspects
- `checkin_handler.py` — /checkin
- `calendar_handler.py` — /calendar
- `shopping_handler.py` — /shop, shopping lists
- `people_handler.py` — /people, contacts
- `snapshot_handler.py` — /snapshot
- `pulse_handler.py` — /pulse
- `quote_handler.py` — /quote
- `analyst_handler.py` — /analyst
- `review_handler.py` — /review
- `inspect_handler.py` — /inspect
- `diag_handler.py` — /diag
- `iris_handler.py` — /iris (Iris agency interface)
- `media_handler.py` — Photo/media processing
- `voice_memo_handler.py` — Voice memo handling
- `voice_handler.py` — Voice command interface
- `weather_handler.py` — /weather
- `ontology_handler.py` — /ontology
- `export_handler.py` — /export
- `ollama_models.py` — /models, model switching
- `prompt_debug_handler.py` — /prompt_debug
- `help_handler.py` — /help
- `task_handler.py` — Task management
- `forecast_handler.py` — /forecast
- `sell_mode.py` — /sell
- `patch_handlers.py` — /patch_status, patch management

### Finance System
```
/opt/mythos/finance/                           — Finance subsystem root
/opt/mythos/core/life_context.py               — Builds life state (includes finance data)
```
Postgres tables: accounts, transactions, budgets, bill_payments, bill_overrides, category_mappings, category_rules

### Consciousness Pipeline (Grid / Triad / Workers)
```
/opt/mythos/core/node_executor.py              — Grid node execution
/opt/mythos/workers/grid_worker.py             — Grid analysis worker
/opt/mythos/workers/embedding_worker.py        — Embedding generation
/opt/mythos/workers/entity_worker.py           — Entity resolution
/opt/mythos/workers/summary_worker.py          — Conversation summaries
/opt/mythos/workers/temporal_worker.py         — Temporal analysis
/opt/mythos/workers/vision_worker.py           — Image analysis
/opt/mythos/workers/transcription_worker.py    — Whisper transcription
/opt/mythos/workers/worker.py                  — Base worker class
/opt/mythos/triad/                             — Triad extraction (grid, akashic, prophetic)
/opt/mythos/triad/prompts/                     — Extraction prompt templates
```

### Conversation Analysis
```
/opt/mythos/core/segment_manager.py            — Conversation segmentation
/opt/mythos/core/subject_tracker.py            — Subject tracking / awareness
/opt/mythos/core/message_extractor.py          — 7b model pre-pass on messages
/opt/mythos/core/action_executor.py            — Executes extractor actions
```
Postgres tables: conversation_segments, conversation_subject_points, exchanges, messages

### Astrology Engine
```
/opt/mythos/astrology/                         — Full astrology subsystem
```
Postgres tables: astro_natal_charts, astro_natal_aspects, astro_chart_objects, astro_natal_house_cusps, astro_chart_points, astro_chart_ruler, astro_arabic_parts, astro_balance, astro_dignities, astro_dispositors, astro_fixed_star_conjunctions, astro_geometric_patterns, astro_retrogrades, astro_sect

### Harmonics
```
/opt/mythos/harmonics/engine.py                — Harmonic resonance engine
/opt/mythos/utils/harmonic_pyramid.py          — Harmonic pyramid calculations
```
Postgres tables: harmonic_resonance (14,541 rows), harmonic_values (457 rows)

### Soul Stratigraphy
```
/opt/mythos/soul_stratigraphy/                 — SS method, numerology, chart comparison
```
Neo4j nodes: SoulStratigraphy, Chart (Western/Vedic/Hellenistic), Numerology

### Genealogy
```
(ingestion pipeline — check /opt/mythos for GEDCOM tools)
```
Neo4j nodes: GenPerson (1,490), GenPlace (1,280), GenFamily (653), GenSurname (449)

### Neo4j Graph (General)
```
Labels: Soul, Person, Incarnation, Exchange, Conversation, GridNode, Entity, Theme,
        Concept, OntologyTerm, Alias, Process, File, Service, Directory,
        Wound, Shadow, Defense, Rupture, Repair, Lineage, Transmission, Activation, MagicalAct
```

### Patch System
```
/opt/mythos/patches/                           — Patch archive and monitor
```
Current: Patch 0153. Next: 0154.
Pattern: `/home/claude/patch_NNNN_description/` with `install.sh` + files under `opt/mythos/...`

### API
```
/opt/mythos/api/                               — FastAPI gateway
/opt/mythos/api/orchestrator.py                — Model orchestration
```

### Orchestration / Benchmarking
```
/opt/mythos/orchestrator/                      — Orchestration system
/opt/mythos/tools/iris_ab_sweep.py             — A/B testing tool
/opt/mythos/tools/iris_test_rig.py             — Test rig
```
Postgres tables: orch_models, orch_role_assignments, orch_config_snapshots, orch_model_benchmarks

### Services (systemd)
```
mythos-api.service                    — FastAPI gateway
mythos-bot.service                    — Telegram bot
mythos-worker-grid.service            — Grid analysis
mythos-patch-monitor.service          — Patch auto-deploy
mythos-voice-watcher.service          — Voice memo file watcher
mythos-transcription-worker.service   — Whisper transcription
mythos-knowledge-map.service          — Knowledge map rebuilder
mythos-segment-manager.service        — Conversation segmentation
mythos-worker-embedding.service       — Embedding generation
mythos-worker-entity.service          — Entity resolution
mythos-worker-summary.service         — Conversation summaries
mythos-worker-temporal.service        — Temporal analysis
mythos-worker-vision.service          — Image analysis
```

---

## Diagnostic Dump Template

When starting a session, use this to pull current state:

```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
echo -e "\n\n=== MANIFEST ===" >> "$D"
cat /opt/mythos/docs/MANIFEST.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

For specific subsystems, add the relevant files from the lists above.
