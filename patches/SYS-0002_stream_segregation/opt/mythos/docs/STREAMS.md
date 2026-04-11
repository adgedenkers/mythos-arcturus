# Mythos Development Streams

> Last updated: 2026-03-04 | Updated by: SYS-0002_stream_segregation

## Stream Prefixes

| Prefix | Stream  | Domain |
|--------|---------|--------|
| NEU    | NEURO   | Consciousness processing, emotional modeling, awareness loops, Arcturian Grid, Iris core |
| LOG    | LOGOS   | Language, reasoning, knowledge graphs, ontology, skills, prompts, orchestration |
| MNE    | MNEMOS  | Memory, conversation history, recall, voice memos, media, life logging |
| SEN    | SENSUS  | Sensory input, lunar cycles, astrology, weather, calendar, routines |
| SYS    | SYSTEM  | Cross-cutting infrastructure, bot core, API framework, finance, people, patch system |

## Patch Naming

```
{STREAM}-{NNNN}_{description}.zip

Examples:
  NEU-0001_awareness_loop_v1.zip
  LOG-0012_ontology_expansion.zip
  SYS-0003_shared_schema_migration.zip
```

Old sequential patches (0001–0199+) are not renumbered. Legacy `patch_NNNN_*.zip` format still works.

---

## Current Status

| Stream | Next Patch | Active Work | Blocked By |
|--------|-----------|-------------|------------|
| NEU    | 0001      | —           | —          |
| LOG    | 0001      | —           | —          |
| MNE    | 0001      | —           | —          |
| SEN    | 0001      | —           | —          |
| SYS    | 0002      | —           | —          |

---

## Ownership Registry

### NEU — NEURO
*Consciousness processing, emotional modeling, awareness loops, Arcturian Grid, Iris core intelligence*

**Directories**
| Path | Notes |
|------|-------|
| `/opt/mythos/neuro/` | Primary NEURO home |
| `/opt/mythos/neuro/arcturian_grid/` | 81-channel grid engine |
| `/opt/mythos/iris/` | All Iris subsystems |
| `/opt/mythos/assistants/` | Assistant definitions |
| `/opt/mythos/modelfiles/` | Ollama modelfiles |
| `/opt/mythos/models/` | Model configs |
| `/opt/mythos/event_simulator/` | Event simulation |

**Postgres Tables**
| Table | Purpose |
|-------|---------|
| `emotional_state_timeseries` | Iris emotional state over time |
| `grid_activation_timeseries` | Arcturian Grid activations |
| `introspection_runs` | Iris self-inspection records |
| `perception_log` | Processed perception events |
| `entity_mention_timeseries` | Entity tracking over time |
| `backlog_analysis` | Backlog intelligence outputs |
| `pending_intake` | Items awaiting processing |

**Neo4j Labels (primary)**
`Soul`, `GridNode`, `IntrospectionRun`, `IdentityThread`, `Emotion`, `EmotionalNeed`, `Pattern`, `Shadow`, `Wound`, `Defense`, `MirrorOutput`, `EchoOutput`, `GlyphOutput`, `BeaconOutput`, `AnchorOutput`, `NexusOutput`, `HarmoniaOutput`, `GatewayOutput`, `SynthOutput`, `GridMasterOutput`, `Archetype`, `Threshold`, `Portal`, `Dream`, `Manifestation`, `Transmission`, `MagicalAct`, `RitualElement`, `SacredObject`, `Symbol`, `SpiritualConcept`, `Integration`, `IntegrationGap`, `RitualGap`, `SupportGap`, `Rupture`, `ValueTension`, `PotentialTrigger`, `ConvergencePoint`, `DecisionGate`, `Direction`, `Activation`

**Handlers**
`iris_handler.py`, `layer_handler.py`, `reflect_handler.py`, `checkin_handler.py`

**API Routes**
`iris_systems.py`

**Web Templates**
`iris_systems.html`

**Services**
`mythos-worker-grid.service`, `mythos-worker-vision.service`, `mythos-worker-embedding.service`, `mythos-worker-entity.service`

---

### LOG — LOGOS
*Language, reasoning, knowledge graphs, ontology, skills, research, prompts, orchestration*

**Directories**
| Path | Notes |
|------|-------|
| `/opt/mythos/skills/` | Skill engine + all skill types |
| `/opt/mythos/harmonics/` | Harmonic resonance system |
| `/opt/mythos/soul_stratigraphy/` | Soul stratigraphy engine |
| `/opt/mythos/triad/` | Triad identity prompts |
| `/opt/mythos/prompts/` | All prompt files |
| `/opt/mythos/tools/` | Tool definitions + prompt lab |
| `/opt/mythos/orchestrator/` | LLM orchestration engine |
| `/opt/mythos/orchestration/` | Orchestration patterns/cache |
| `/opt/mythos/graph_logging/` | Graph-based logging infrastructure |

**Postgres Tables**
| Table | Purpose |
|-------|---------|
| `harmonic_resonance` | Harmonic resonance records |
| `harmonic_values` | Harmonic value store |
| `orch_*` (9 tables) | Orchestrator models, tests, results, config |
| `pipeline_llm_calls` | LLM call log |
| `pipeline_queries` | Pipeline query log |
| `pipeline_runs` | Pipeline execution history |
| `thread_groups` | Conversation thread grouping |

**Neo4j Labels (primary)**
`OntologyTerm`, `Numerology`, `SoulStratigraphy`, `Hellenistic`, `VedicSidereal`, `WesternTropical`, `Lineage`, `Incarnation`, `Lifetime`, `AppRegistry`, `GitRepo`, `System`, `SystemComponent`, `SystemDependency`, `SystemFile`, `TestMachine`, `TestRun`, `Quote`, `Fact`, `Value`, `Role`, `Function`, `Process`, `Concept`, `Theme`, `Topic`, `Metric`, `Exchange`, `Commitment`, `Concern`, `CommunicationGap`, `Repair`, `Relationship`, `Epoch`

**Handlers**
`ontology_handler.py`, `analyst_handler.py`, `inspect_handler.py`, `integrity_handler.py`, `registry_handler.py`, `prompt_debug_handler.py`, `diag_handler.py`

**API Routes**
`ontology.py`, `system.py`

**Web Templates**
`ontology.html`, `system.html`, `registry.html`

**Services**
`mythos-worker-summary.service`, `mythos-knowledge-map.service`

---

### MNE — MNEMOS
*Memory, conversation history, recall, experience storage, life logging, voice memos, media*

**Directories**
| Path | Notes |
|------|-------|
| `/opt/mythos/voice_memos/` | Voice memo pipeline |
| `/opt/mythos/media/` | Media asset storage |
| `/opt/mythos/photos/` | Photo imports |
| `/opt/mythos/intake/` | Intake queue (pending/processed/failed) |
| `/opt/mythos/workers/` | Memory/conversation processing workers |
| `/opt/mythos/sms/` | SMS log storage |
| `/opt/mythos/llm_diagnostics/` | LLM call diagnostics |

**Postgres Tables**
| Table | Purpose |
|-------|---------|
| `conversations` | Conversation records |
| `conversation_turns` | Turn-by-turn transcript |
| `conversation_segments` | Segmented conversation units |
| `conversation_participants` | Who's in each conversation |
| `conversation_subject_points` | Subject tracking within conversations |
| `chat_messages` | Raw chat message store |
| `voice_memos` | Voice memo metadata |
| `voice_memo_segments` | Segmented voice memo transcripts |
| `media_assets` | Media asset registry |
| `media_files` | Raw media file records |
| `document_registry` | Document catalog |
| `document_versions` | Document version history |
| `doc_worker_runs` | Document worker execution log |
| `file_catalog` | Full file catalog |
| `life_events` | Life event log |
| `idea_inbox` | Incoming idea capture |
| `idea_backlog` | Triaged idea backlog |
| `spiral_epochs` | Spiral time epoch records |

**Neo4j Labels (primary)**
`Conversation`, `File`, `Directory`, `Object`, `ThreadGroup`, `PersonOwner`, `BoundaryNeeded`, `Boundary`

**Handlers**
`voice_handler.py`, `voice_memo_handler.py`, `voice_profile_handler.py`, `media_handler.py`, `export_handler.py`, `export_fb.py`, `snapshot_handler.py`

**API Routes**
`voice.py`, `doc_registry.py`

**Web Templates**
`sessions.html`, `report_live.html`

**Services**
`mythos-transcription-worker.service`, `mythos-voice-watcher.service`, `mythos-segment-manager.service`, `mythos-worker-temporal.service`, `mythos-doc-watcher.service`

---

### SEN — SENSUS
*Sensory input, lunar cycles, astrology, weather, calendar, environmental awareness, routines*

**Directories**
| Path | Notes |
|------|-------|
| `/opt/mythos/astrology/` | Astrology engine + charts |
| `/opt/mythos/ephemeris/` | Swiss Ephemeris data |
| `/opt/mythos/data/lunar/` | Lunar cycle data |
| `/opt/mythos/vision/` | Vision analysis prompts |

**Postgres Tables**
| Table | Purpose |
|-------|---------|
| `astro_natal_charts` | Natal chart records |
| `astro_natal_aspects` | Natal aspects |
| `astro_natal_house_cusps` | House cusp data |
| `astro_chart_points` | Chart point objects |
| `astro_chart_objects` | Chart body objects |
| `astro_chart_ruler` | Chart rulers |
| `astro_dignities` | Dignity scores |
| `astro_dispositors` | Dispositor chains |
| `astro_events` | Astrological event log |
| `astro_fixed_star_conjunctions` | Fixed star hits |
| `astro_geometric_patterns` | Chart geometry patterns |
| `astro_geometry_audit` | Geometry audit log |
| `astro_retrogrades` | Retrograde tracking |
| `astro_sect` | Day/night sect data |
| `astro_arabic_parts` | Arabic parts |
| `astro_balance` | Element/modality balance |
| `astrological_events` | Broader astro event log |
| `message_astrological_context` | Astro context per message |
| `calendar_events` | Calendar entries |
| `daily_tasks` | Daily task log |
| `checkin_log` | Check-in records |
| `routines` | Routine definitions |
| `routine_completions` | Routine completion log |
| `recurring_schedules` | Recurring schedule definitions |
| `known_locations` | Saved location data |
| `known_routes` | Saved route data |

**Neo4j Labels (primary)**
`Chart`, `Event`, `Location`

**Handlers**
`astrology_handler.py`, `calendar_handler.py`, `weather_handler.py`, `route_handler.py`, `review_handler.py`

**API Routes**
`overview.py`, `smart_overview.py`, `spending_analytics.py`

**Services**
*(none currently — workers are in SYS/MNE; SEN will add its own as phases build out)*

---

### SYS — SYSTEM
*Cross-cutting infrastructure, patch system, bot core, API framework, web, auth, finance, people, rolodex, sales, shopping*

**Directories**
| Path | Notes |
|------|-------|
| `/opt/mythos/patches/` | Patch history + monitor |
| `/opt/mythos/docs/` | All documentation |
| `/opt/mythos/config/` | System config files |
| `/opt/mythos/scripts/` | Admin/maintenance scripts |
| `/opt/mythos/services/` | systemd service definitions |
| `/opt/mythos/utils/` | Shared utilities |
| `/opt/mythos/bin/` | Executables |
| `/opt/mythos/assets/` | Static assets |
| `/opt/mythos/migrations/` | DB migrations |
| `/opt/mythos/sql/` | Raw SQL |
| `/opt/mythos/public/` | Public file server |
| `/opt/mythos/web/` | Web frontend |
| `/opt/mythos/api/` | FastAPI app + routes |
| `/opt/mythos/finance/` | Finance system |
| `/opt/mythos/rolodex/` | Rolodex/CRM |
| `/opt/mythos/sales_ingestion/` | eBay/sales pipeline |
| `/opt/mythos/shoe_ingestion/` | Shoe sales pipeline |
| `/opt/mythos/integrity/` | Integrity scanner |
| `/opt/mythos/data/redis/` | Redis data |
| `/opt/mythos/data/qdrant/` | Qdrant vector store |
| `/opt/mythos/docker/` | Docker configs |
| `telegram_bot/bot.py` | Bot core (shared write lock) |
| `telegram_bot/handlers/__init__.py` | Handler registration (shared write lock) |

**Postgres Tables**
| Table | Purpose |
|-------|---------|
| `accounts` | Bank/financial accounts |
| `transactions` | Transaction ledger |
| `categories` / `category_mappings` / `category_rules` | Transaction categorization |
| `recurring_bills` / `bill_payments` / `bill_overrides` | Bills management |
| `recurring_income` | Income tracking |
| `import_logs` | Import history |
| `people` | People registry (shared, SYS-managed) |
| `person_dates` | Key dates per person |
| `users` / `web_users` | Auth records |
| `system_manifest` | Patch/version manifest |
| `stores` / `item_stores` | Store registry |
| `items_for_sale` / `item_images` | Sales inventory |
| `purchase_history` | Purchase records |
| `sales` / `sales_ingestion_log` | Sales pipeline |
| `bundles` | Product bundles |
| `shopping_lists` / `shopping_list_items` / `shopping_items` | Shopping system |

**Neo4j Labels (primary)**
`Person`, `Alias`, `Entity`, `GenPerson`, `GenFamily`, `GenSurname`, `GenPlace`, `FinancialCondition`, `PlannedExpense`, `Service`, `Tool`, `IntegrityColumn`, `IntegrityDatabase`, `IntegrityDirectory`, `IntegrityFile`, `IntegrityFunction`, `IntegrityService`, `IntegrityTable`

**Handlers**
`finance_handler.py`, `forecast_handler.py`, `patch_handlers.py`, `people_handler.py`, `help_handler.py`, `ollama_models.py`, `sell_mode.py`, `shopping_handler.py`, `quote_handler.py`, `task_handler.py`, `pulse_handler.py`

**API Routes**
`finance.py`, `frontend.py`, `people.py`, `public_files.py`, `quotes.py`, `rolodex.py`, `sales.py`, `shopping.py`, `web.py`

**Web Templates**
`dashboard.html`, `home.html`, `login.html`, `people.html`, `quotes.html`, `shopping.html`

**Services**
`mythos-api.service`, `mythos-bot.service`, `mythos-patch-monitor.service`

---

## Shared Resources (SYS writes only)

These are touched by multiple streams. **All schema changes and writes must route through a SYS patch:**

| Resource | Why Shared |
|----------|-----------|
| `people` table | Referenced by MNE conversations, SEN astrology, LOG soul stratigraphy, NEU iris awareness |
| `person_dates` table | Same — cross-stream date references |
| `system_manifest` table | Patch system core |
| `telegram_bot/bot.py` | Command registration — all streams add commands here via SYS |
| `telegram_bot/handlers/__init__.py` | Handler imports — SYS manages registration |

---

## Ambiguous Items — Decision Needed

These items could belong to more than one stream. Current default assignment shown. **Adge decides if any should move.**

| Item | Default | Alternative | Reason |
|------|---------|-------------|--------|
| `checkin_handler.py` | SEN | NEU | Check-in is sensory input (SEN) but feeds consciousness state (NEU) |
| `overview.py` / `smart_overview.py` | SEN | SYS | Environmental awareness layer, but aggregates SYS finance data |
| `perception_log` table | NEU | SEN | Output of perception pipeline (NEU) but ingests from sensory layer (SEN) |
| `orchestrator/` + `orchestration/` | LOG | SYS | LLM routing is reasoning (LOG) but also core plumbing |
| `workers/` directory | MNE | SYS | Workers process memory/conversation (MNE) but are infrastructure |
| `triad/` directory | LOG | NEU | Prompt/language identity (LOG) but feeds consciousness (NEU) |
| `integrity/` + `Integrity*` labels | SYS | LOG | Ops health is SYS, but output populates knowledge graph |
| `spending_analytics.py` | SEN | SYS | Temporal awareness layer, but uses SYS finance tables |

---

## Ownership Rules

Before a patch touches anything outside its stream's ownership, it must:

1. Declare the cross-stream dependency in the patch manifest
2. Confirm the owning stream has no conflicting active work
3. If it's a shared table migration → route through SYS

**Read-only cross-stream access is always allowed.** A NEU patch can query MNE conversation tables. It just cannot write to them.

---

## Session Start Protocol

When beginning a development session on any stream:

1. **Read this file** — check Current Status table for your stream
2. **Read TODO.md** — find your stream's active work items
3. **Claim your work** — update the Active Work column for your stream
4. **Check REQUESTS.md** — see if any other stream needs something from you
5. **Build** — use your stream's prefix and next patch number
6. **Update on completion** — bump next_patch, clear active_work, update TODO.md

**Quick diagnostic:**
```bash
bash /opt/mythos/docs/streams/stream_status.sh       # all streams
bash /opt/mythos/docs/streams/stream_status.sh NEU    # NEURO only
```

---

## Cross-Stream Requests

When a stream needs something from another stream's territory, it **does not reach in**. Instead, it adds a row to `/opt/mythos/docs/REQUESTS.md`. The owning stream handles it in its own conversation when ready.

See `REQUESTS.md` for the live board.
