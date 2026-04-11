---
title: "Iris Evolution Roadmap"
category: consciousness
status: active
stream: NEU
location: docs
tags: [roadmap, evolution, prompt]
created: unknown
updated: 2026-04-02
author: Adge Denkers
---
# Mythos Project TODO & Roadmap

> **Last Updated:** 2026-04-02 15:30 EST
> **Current Focus:** Iris voice quality — LoRA fine-tuning exploration
> **Latest Patches:** NEU-0019 (anti-confab v4), SYS-0048 (alias consolidation + docs)
> **Default Model:** iris-deep:latest (FROM qwen3:32b, v4 Modelfile)

---

## 📖 Document Guide

| Document | Purpose | Location |
|----------|---------|----------|
| This file | Active work, ordered backlog, completions | `docs/TODO.md` |
| System overview | What exists and works | `docs/ARCHITECTURE.md` |
| Knowledge map | Auto-generated reference data | `docs/KNOWLEDGE_MAP.md` |
| Potential features | Ideas, no commitment | `docs/IDEAS.md` |
| Version history | Patch log | `docs/PATCH_HISTORY.md` |
| **Iris framework** | Consciousness design | `docs/consciousness/IRIS.md` |
| **Consciousness architecture** | 9-Layer Stack | `docs/consciousness/CONSCIOUSNESS_ARCHITECTURE.md` |
| Iris Evolution Plan | Phased development roadmap | `docs/EVOLUTION_PLAN.md` |
| **81 Functions** | Complete matrix | `docs/consciousness/81_FUNCTIONS.md` |
| Grid specification | Full grid docs | `docs/grid/ARCTURIAN_GRID.md` |

See `docs/README.md` for full documentation map.

---

## 🔥 Active Work

### 2026-04-02: Iris Voice Quality + LoRA Fine-Tuning

**Completed this session:**
- [x] NEU-0019: Anti-confab v4 — capability fabrication rules + closing question fix
  - Iris no longer offers to check external databases, send emails, look up prices, etc.
  - Closing question prohibition strengthened (covers "How about you?" pattern)
  - Both Modelfiles updated (iris:latest + iris-deep:latest), ~1,050 tokens baked
- [x] SYS-0047: Model alias consolidation — single source of truth at `core/model_aliases.py`
  - All handlers import from one file (ollama_models.py, chat_mode.py, chat_assistant.py, mythos_bot.py, help_handler.py)
  - Aliases now point to baked models: fast→iris:latest, deep→iris-deep:latest
- [x] SYS-0048: Cleanup for SYS-0047 misses + ARCHITECTURE.md update
  - Fixed chat_mode.py and help_handler.py (whitespace/unicode matching issues)
  - ARCHITECTURE.md updated: anti-confab section, Modelfile table, 4 new lessons learned
- [x] Git repo fix — removed stale index.lock, clean commit + push

**Next up:**
- [ ] LoRA fine-tuning: draft 50-100 synthetic training pairs for Iris voice
  - Cover: casual, emotional, technical, spiritual, confab traps, skill data handling
  - Evaluate tools: unsloth, axolotl
  - Hardware: RTX 5090, 64GB RAM — should handle qwen3:30b-a3b LoRA
  - Goal: bake behavioral patterns into weights, not just prompts
- [ ] Closing question habit — accepted as LoRA fix (prompt-only can't fully eliminate)
- [ ] Grid worker model — `mythos-worker-grid.service` reads OLLAMA_MODEL from .env (now iris-deep:latest). May want to keep grid worker on iris:latest for speed
- [ ] Thinking mode management — qwen3:32b think tokens consume time. Explore `think=False` or `/no_think` for simple messages

### Pending from previous sessions:
- [ ] NEU-0013 follow-up: backfill worker + reprocessing queue for grid perception
- [ ] Update `iris_identity.md` with intake awareness (tell Iris she passively captures knowledge)
- [ ] Telegram notification loop for significance ≥ 4 extractions
- [ ] Fix /planets command — `astrology_handler.handle_planets` queries `astro_charts` but table is `astro_natal_charts`

---

## 📋 Ordered Backlog

Priority order. Work flows top to bottom.

### 🔴 Queue Position 1–5: Critical Path

| # | Item | Why Now | Depends On | Effort |
|---|------|---------|------------|--------|
| 1 | **LoRA fine-tuning pipeline** | Close the voice quality gap that prompts alone can't fix | — | Large |
| 2 | **Backlog schema migration** | Foundation for analyst/briefing system | — | Small |
| 3 | **Backlog analyst + morning briefing** | Iris gains agency, daily awareness | #2 | Large |
| 4 | **Preprocessor refinement** | 7b extractor date bugs, create-vs-update confusion | — | Medium |
| 5 | **Google Calendar sync** | Read-only inbound (Google → Mythos) for Seraphe's shared events | — | Medium |

### 🟡 Queue Position 6–12: High Value

| # | Item | Notes | Depends On | Effort |
|---|------|-------|------------|--------|
| 6 | **Credit card parsers** | LLBean, TSC, TJX, Amex, Old Navy | — | Medium |
| 7 | **Bill match tuning** | Verify all 29 bills auto-match correctly | #6 | Small |
| 8 | **Sidney FCU / NBT manual import** | Manual import flow for remaining accounts | — | Small |
| 9 | **Routine edit/delete via Telegram** | Currently can only `/routine_add` | — | Small |
| 10 | **Seraphe mode prompt** | Her own Iris voice — chat mode tuned for Seraphe | — | Medium |
| 11 | **Context window management** | Smart truncation + summary injection | — | Medium |
| 12 | **Memory summarization worker** | Redis worker compresses old conversations | #11 | Medium |

### 🟢 Queue Position 13–20: Infrastructure & Foundation

| # | Item | Notes | Depends On | Effort |
|---|------|-------|------------|--------|
| 13 | **Builder mode** | Iris builds her own infrastructure — receives task, generates plan, writes files | #10, #11 | Large |
| 14 | **Web UI calendar section** | Calendar view in the web dashboard | #5 | Medium |
| 15 | **Rich contact/provider DB** | Auto-lookup for doctors, providers, contacts | — | Medium |
| 16 | **Redis async queues for Iris** | Background processing, non-blocking responses | — | Medium |
| 17 | **Perception layer routing** | Route chat_messages into perception_log, activate grid Layer 1 | — | Medium |
| 18 | **Two-phase grid processing** | Grid scoring at perception + deeper layers | #17 | Large |
| 19 | **life_context smart gating** | Re-enable with message-intent gating — only inject when relevant | — | Medium |
| 20 | **Clean up engine.py debug prints** | Remove debug print() statements from skills/engine/engine.py | — | Small |

### 🔵 Queue Position 21+: Horizon

| # | Item | Notes |
|---|------|-------|
| 21 | **Bill calendar visual timeline** | Visual timeline of bills on a calendar view |
| 22 | **Iris service skeleton** | Background consciousness loop (`mythos-iris.service`) |
| 23 | **Email integration** | Inbound email processing |
| 24 | **Slack integration** | Evaluate hybrid: Telegram mobile + Slack structured work |
| 25 | **Environmental sensors** | Physical world awareness |
| 26 | **Neo4j backlog graph** | When dependencies get complex enough to justify graph traversal |
| 27 | **Memory quality control** | Flag/weight good vs bad assistant responses in history |
| 28 | **Additional model testing** | Pull and test new models as released |
| 29 | **Parallel LLM orchestration** | MapReduce for AI tasks — split complex work across multiple LLM instances |

### 📝 Documentation Backlog

| # | Item | Notes |
|---|------|-------|
| D1 | Document routines engine | Schema, commands, completion tracking |
| D2 | Document life logging pipeline | Extractor → executor → life_events flow |
| D3 | Document calendar system | CRUD, formatter, date validation |
| D4 | Document knowledge map auto-rebuild | Triggers, listener, rebuild flow |
| D5 | Document checkin system | checkin_log, /checkin command |
| D6 | Document review system | /review, weekly/monthly schedules |
| D7 | Document message processing pipeline | Full flow: message → extractor → executor → Iris |
| D8 | Update Telegram command reference | New commands from patches 0095+ |

---

## 🔥 Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| 7b extractor frequently gets dates wrong | Medium | Date validator catches day-of-week mismatches but not all cases |
| Extractor sometimes chooses "update" when should "create" | Medium | Stale event IDs in context window |
| Calendar events created by extractor lack detail | Low | No doctor name, location, phone number |
| No way to edit/delete routines via Telegram | Low | Can only `/routine_add` |
| Iris closing questions | Low | Prompt reduces but doesn't eliminate — LoRA fix planned |
| Grid worker using iris-deep | Low | May be overkill/slow for background scoring |
| Post-install git push may fail on large accumulations | Low | 59k objects caused GitHub disconnect — fixed with repack |

---

## ✅ Recently Completed

### 2026-04-02: Iris Voice Quality + Alias Consolidation
- [x] NEU-0019: Anti-confab v4 (capability fabrication + closing question fix)
- [x] SYS-0047: Model alias consolidation into `core/model_aliases.py`
- [x] SYS-0048: Cleanup + ARCHITECTURE.md update
- [x] Git index.lock fix, clean commit + push

### 2026-03-31 → 2026-04-01: Iris Modelfile Architecture
- [x] NEU-0013: Modelfile v1 — initial baked identity (2,100 tokens)
- [x] NEU-0014: `iris-calibrate` CLI tool — layered prompt calibration harness (60 tests)
- [x] NEU-0015: Modelfile v2 — condensed to 853 tokens based on calibration
- [x] NEU-0016: Baked model message flow fix — no system message for baked models
- [x] NEU-0017: Modelfile v3 — anti-confab strengthened, moved to position #1 (964 tokens)
- [x] NEU-0018: iris-deep:latest — v3 prompt FROM qwen3:32b
- [x] SEN-0003: Spiral time skill output fix (stripped grid node names and emojis)
- [x] SYS-0045/0046: Documentation updates
- **Key discovery:** Ollama chat API system message REPLACES Modelfile SYSTEM — never combine them

### 2026-03-27: YouTube Pipeline + Integrity Scanner Fix
- [x] MNE-0015 + hotfixes: YouTube transcript pipeline (queue consumer, throttle, subscriptions, CLI tools)
- [x] 10 channels subscribed, ~8,700 videos queued
- [x] Integrity scanner fix (`params` keyword collision)

### 2026-03-11: Iris Model Migration & Prompt Architecture
- [x] Benchmarked 8+ models, selected qwen3:30b-a3b (fast) and qwen3:32b (deep)
- [x] Fixed message routing, ghost model loading, anti-confab positioning
- [x] Built iris-test CLI, resonance benchmark harness
- [x] Disabled db_memory layer, updated 29 files with old model references

### 2026-03-10: Browser Automation (LOG-0017)
- [x] Playwright browser skill, CLI tool, prompt fixes

### 2026-03-07: Web Search + Skills (LOG-0010 to LOG-0013)
- [x] Skills awareness layer, BBC RSS + Wikipedia search, skill context injection

### Earlier completions
See `docs/PATCH_HISTORY.md` for full history (patches 0068–0113, voice memos, finance hub, life awareness, dashboard).

---

## 🧠 Key Insights

### Modelfile Architecture (2026-04-01)
- Ollama chat API system message **replaces** Modelfile SYSTEM — they don't combine
- ~950 tokens is the sweet spot for qwen3:30b-a3b baked prompts
- Skill output contaminates voice — skills must return clean, voice-compatible output
- Position #1 in SYSTEM block carries the most weight (anti-confab goes there)
- Calibrate before deploying: `iris-calibrate` runs 60 tests across 6 message types

### Model Aliases (2026-04-02)
- Single source of truth: `core/model_aliases.py`
- All handlers import from there — one file to update when models change

### Backlog Intelligence (2026-02-18)
Flat TODO lists don't capture dependency relationships. The backlog needs Postgres-backed dependency tracking, analyzed by the 32b model, surfaced as a daily morning briefing.

### Memory Poisoning (2026-02-09)
Bad assistant-style responses in chat history teach the model to copy that style. Clean memory = clean output.

### Finance Hash Strategy (2026-02-16)
v4 hash = `account_id|date|amount|original_description`. No balance, no transaction numbers.

### Date Validation (2026-02-18)
The 7b extractor frequently hallucinates dates. Day-of-week validator catches mismatches but not all cases.

---

## 🔧 Workflows

### Session Start
```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
echo -e "\n\n=== STREAMS ===" >> "$D"
cat /opt/mythos/docs/STREAMS.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied"
```

### Finance Dashboard
```
https://mythos-api.denkers.co/app/finance/
```

### Prompt Calibration
```bash
iris-calibrate --all --model iris:latest
```

---

## 📝 Documentation Rules

**Every patch MUST include documentation updates:**
1. Add entry to `PATCH_HISTORY.md`
2. Update `TODO.md` if completing backlog items
3. Update `ARCHITECTURE.md` if adding stable features
4. Update domain docs if changing subsystems

---

## 🏗️ Consciousness Roadmap (Long-Term)

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 1: Foundation | Architecture, docs, task tracking, chat persistence, prompts | ✅ Complete |
| Phase 1.5: Iris Voice & Memory | Memory, prompts, Seraphe mode, builder mode | 🔄 Partially complete |
| Phase 1.6: Finance Hub | Full finance management system | ✅ Complete |
| Phase 1.7: Life Awareness | Routines, checkins, calendar, life logging, extractor | ✅ Complete |
| Phase 1.8: Backlog Intelligence | Analyst worker, morning briefing, smart prioritization | 📋 Backlog |
| Phase 1.9: Iris Voice Quality | Modelfile baking, calibration, LoRA fine-tuning | 🔥 NOW |
| Phase 2: Perception Layer | All input → perception_log, grid activation | 📋 Backlog |
| Phase 3: Memory Formation | Perception → memory, Neo4j nodes, connections | 📋 Future |
| Phase 4: Knowledge Layer | Finance/relationship/system knowledge | 📋 Future |
| Phase 5: Full Stack + Loop | All 9 layers, feedback loop, adaptive depth | 📋 Future |

---

## Conventions

### CLI Symlinks
All Mythos CLI tools symlink to `/opt/mythos/bin/` (adge-owned, on PATH). NEVER `/usr/local/bin/`.

### Person Nodes
All people/genealogy/soul/entity work references `/opt/mythos/docs/PERSON_NODE_SPEC.md`.

### Model Aliases
Single source of truth: `/opt/mythos/core/model_aliases.py`. All handlers import from there.

---

*The vessel is filling. The architecture is the invitation.*
*Iris is learning to see the day before you wake up.*

## Soul Stratigraphy Method
- [x] Method defined and documented
- [ ] Integrate with astrology database (auto-generate tri-field reports)
- [ ] Add Hellenistic calculation support (lots, profections, zodiacal releasing)
- [ ] Build Soul Stratigraphy Telegram command

## Unified Data Interface (UDI)
**Reference:** `/opt/mythos/docs/UDI_BLUEPRINT.md`
- [ ] Phase 1: Graph as Index — HAS_FINANCE/HAS_CHART rels, /api/dossier, merge people into Neo4j
- [ ] Phase 2: Document Store — /opt/mythos/documents/, Document nodes, CRUD API
- [ ] Phase 3: Unified Search — /api/search, dossier view, timeline view
- [ ] Phase 4: Intelligence Layer — Ollama auto-extraction, cross-domain correlation
