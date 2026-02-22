# Mythos Project TODO & Roadmap
> **Last Updated:** 2026-02-18 17:15 EST
> **Current Focus:** Backlog Intelligence — schema migration, morning briefing, analyst worker
> **Current Patch:** 0101 (post-hotfixes)

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
| **81 Functions** | Complete matrix | `docs/consciousness/81_FUNCTIONS.md` |
| Grid specification | Full grid docs | `docs/grid/ARCTURIAN_GRID.md` |

See `docs/README.md` for full documentation map.

---

## 🔥 Active Work

### Backlog Intelligence System (NOW)
Three-part build: schema migration → analyst worker → morning briefing.

**Part 1: Backlog Schema Migration**
Upgrade `idea_backlog` table (33 rows currently) to support ordered, dependency-tracked work items.
- Add `priority_order` (integer, sortable position)
- Add `depends_on` (integer array, FK references to other backlog items)
- Add `blocked_by` (integer array, computed or manual)
- Add `phase` (text — which project phase this belongs to)
- Add `estimated_effort` (text — small/medium/large or hours)
- Seed all current backlog items with initial priority ordering
- Update `/tasks` Telegram command to show ordered, dependency-aware list

**Part 2: Backlog Analyst Worker**
`/opt/mythos/core/backlog_analyst.py` — runs the 32b model against full system state.

Inputs (pulled from Postgres):
- All open backlog items with dependencies
- Recent completions (last 7 days)
- Today's routines + completion status
- Today's calendar events
- Bills due in next 3 days + account balances
- Yesterday's checkin (or absence)
- Recent life events

Outputs (written to Postgres):
- Updated priority scores on backlog items
- `backlog_analysis` table: timestamp, summary, recommendations, flagged items
- Analysis available to `life_context.py` for Iris awareness injection

Three trigger modes:
1. **Scheduled morning run** (6:30 AM) — full analysis → Telegram briefing
2. **Post-patch trigger** — re-analyze dependencies → DB update only (no Telegram unless significant)
3. **On-demand via Iris** — "reprioritize" / "what should I focus on" → conversational response

**Part 3: Morning Briefing**
Iris sends a daily Telegram message with the analyst's output, written in her voice — not a data dump, a perspective on the day. Includes: priorities, calendar, bills, overdue items, what's unblocked.

**Why this is first:** The morning briefing IS the nudge system in its best form. Instead of dumb timer-based nudges, every nudge comes from the analyst's understanding of what actually matters today.

---

## 📋 Ordered Backlog

Priority order. Work flows top to bottom. Items marked with dependencies.

### 🔴 Queue Position 1–5: Critical Path

| # | Item | Why Now | Depends On | Effort |
|---|------|---------|------------|--------|
| 1 | **Backlog schema migration** | Foundation for everything below | — | Small |
| 2 | **Backlog analyst + morning briefing** | Iris gains agency, daily awareness | #1 | Large |
| 3 | **Preprocessor refinement** | 7b extractor date bugs, create-vs-update confusion, stale event IDs. Analyst will surface data quality issues the extractor causes | — | Medium |
| 4 | **Proactive nudges** | Now simple: analyst already knows what to nudge about. Nudges = "send reminders for items the morning analysis flagged" | #2 | Medium |
| 5 | **Google Calendar sync** | Start with read-only inbound (Google → Mythos) so Seraphe's shared events appear. Bidirectional later | — | Medium |

### 🟡 Queue Position 6–12: High Value

| # | Item | Notes | Depends On | Effort |
|---|------|-------|------------|--------|
| 6 | **Credit card parsers** | LLBean, TSC, TJX, Amex, Old Navy — accounts without auto-import | — | Medium |
| 7 | **Bill match tuning** | Verify all 29 bills auto-match correctly after more data flows | #6 | Small |
| 8 | **Sidney FCU / NBT manual import** | Manual import flow for remaining bank accounts | — | Small |
| 9 | **Routine edit/delete via Telegram** | Currently can only `/routine_add`, need edit and remove | — | Small |
| 10 | **Seraphe mode prompt** | Her own Iris voice — chat mode tuned for Seraphe | — | Medium |
| 11 | **Context window management** | Smart truncation + summary injection for Iris conversations | — | Medium |
| 12 | **Memory summarization worker** | Redis worker compresses old conversations | #11 | Medium |

### 🟢 Queue Position 13–20: Infrastructure & Foundation

| # | Item | Notes | Depends On | Effort |
|---|------|-------|------------|--------|
| 13 | **`mythos-diag` command** | Standardized diagnostic tool for system state | — | Small |
| 14 | **Builder mode** | Iris builds her own infrastructure — receives task, generates plan, writes files | #10, #11 | Large |
| 15 | **Web UI calendar section** | Calendar view in the web dashboard | #5 | Medium |
| 16 | **Rich contact/provider DB** | Auto-lookup for doctors, providers, contacts | — | Medium |
| 17 | **Iris web search capability** | Iris can search the web when she needs current info | — | Medium |
| 18 | **Redis async queues for Iris** | Background processing, non-blocking responses | — | Medium |
| 19 | **Perception layer routing** | Route chat_messages into perception_log, activate grid Layer 1 | — | Medium |
| 20 | **Two-phase grid processing** | Grid scoring at perception + deeper layers | #19 | Large |

### 🔵 Queue Position 21+: Horizon

| # | Item | Notes |
|---|------|-------|
| 21 | **Bill calendar visual timeline** | Visual timeline of bills on a calendar view |
| 22 | **Iris service skeleton** | Background consciousness loop (`mythos-iris.service`) |
| 23 | **Email integration** | Inbound email processing |
| 24 | **Slack integration** | Evaluate hybrid: Telegram mobile + Slack structured work |
| 25 | **Environmental sensors** | Physical world awareness |
| 26 | **Bash profile builder** | Low priority |
| 27 | **Neo4j backlog graph** | When dependencies get complex enough to justify graph traversal |
| 28 | **Memory quality control** | Flag/weight good vs bad assistant responses in history |
| 29 | **Additional model testing** | Pull and test new models as released |

### 📝 Documentation Backlog

| # | Item | Notes |
|---|------|-------|
| D1 | Update ARCHITECTURE.md for patches 0095–0101 | New tables, services, core files |
| D2 | Document routines engine | Schema, commands, completion tracking |
| D3 | Document life logging pipeline | Extractor → executor → life_events flow |
| D4 | Document calendar system | CRUD, formatter, date validation |
| D5 | Document knowledge map auto-rebuild | Triggers, listener, rebuild flow |
| D6 | Document checkin system | checkin_log, /checkin command |
| D7 | Document review system | /review, weekly/monthly schedules |
| D8 | Document message processing pipeline | Full flow: message → extractor → executor → Iris |
| D9 | Update Telegram command reference | New commands from 0095–0101 |

---

## 🔥 Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| 7b extractor frequently gets dates wrong | Medium | Date validator catches day-of-week mismatches but not all cases |
| Extractor sometimes chooses "update" when should "create" | Medium | Stale event IDs in context window |
| Calendar events created by extractor lack detail | Low | No doctor name, location, phone number |
| No way to edit/delete routines via Telegram | Low | Can only `/routine_add` |
| DB column names may differ from ARCHITECTURE.md | Low | Patches 0095–0101 created tables with different column names than documented |

---

## ✅ Recently Completed

### 2026-02-18: Life Awareness Sprint (Patches 0095–0101)
- [x] **Patch 0095: Weekly Financial Review** — `/review` generates full financial snapshot
- [x] **Patch 0096: Routines Engine** — `routines` + `routine_completions` + `checkin_log` + `calendar_events` tables. `/checkin`, `/routines`, `/rdone`, `/rskip`, `/routine_add`
- [x] **Patch 0097: Iris Life Awareness** — `life_context.py` injects routine/task/bill/calendar/balance state into Iris's system prompt
- [x] **Patch 0098: Life Logging & Message Extractor** — `qwen2.5:7b` pre-pass extracts structured data from every message. `action_executor.py` commits to DB. `KNOWLEDGE_MAP.md` reference. `life_events` table
- [x] **Patch 0099: Calendar Display** — `calendar_formatter.py` with box-drawing, bills woven in, paid bills struck through. `/calendar`, `/calendar today`, `/calendar month`, `/calendar add`
- [x] **Patch 0100: Knowledge Map Auto-Rebuild** — PostgreSQL triggers on bills/accounts/routines fire `pg_notify`. Listener rebuilds `KNOWLEDGE_MAP.md` from DB. `mythos-knowledge-map.service`
- [x] **Patch 0101: Calendar CRUD** — Extractor creates/updates/deletes calendar events. Deduplication. Date validator. Title formatting. Person display
- [x] **Hotfixes:** Duplicate routines cleaned, timezone-naive datetime fixed, `llava:13b` override cleared, chat memory purged, API/bot service confusion resolved, calendar formatter spacing, file ownership, checkin header formatting
- [x] **Schedule changes:** Weekly financial review → Monday mornings. Monthly review → 4th Sunday. `week_of_month` column added to routines

### 2026-02-17: Finance Hub (Patches 0086–0094)
- [x] **Patch 0086–0090:** Hash fix, import notifications, GitHub push fix, allow-dupes, OAuth redirect
- [x] **Patch 0091:** Transaction editor — inline edit, filter bar, pagination
- [x] **Patch 0092:** Finance hub — sidebar nav, bills tracker, categories CRUD, accounts
- [x] **Patch 0093:** Bill persistence + forecast — `bill_overrides` table, day-by-day forecast
- [x] **Patch 0094:** Documentation update

### 2026-02-09: Dashboard & Iris (Patches 0068–0074)
- [x] Finance data pipeline, web dashboard, OAuth, command center, dashboard polish, Ollama model manager, Iris memory layer

See `docs/PATCH_HISTORY.md` for full history.

---

## 🧠 Key Insights

### Backlog Intelligence (2026-02-18)
Flat TODO lists don't capture dependency relationships. The backlog needs to be Postgres-backed with dependency tracking, analyzed regularly by the 32b model, and surfaced as a daily morning briefing. The analyst replaces dumb nudges with intelligent prioritization.

### Memory Poisoning (2026-02-09)
Bad assistant-style responses in chat history teach the model to copy that style. Clean memory = clean output.

### Model Selection (2026-02-09)
- `qwen2:72b` + B_strict = best voice, ~40s
- `qwen2.5:32b` + C_minimal = fastest good quality, ~7s
- `qwen2.5:7b` = extractor/preprocessor only, ~2s

### Install Script Pattern (2026-02-17)
Install scripts must use `sudo cp` and `${BASH_SOURCE[0]}` for path resolution. Files in `/opt/mythos` are owned by root.

### Finance Hash Strategy (2026-02-16)
v4 hash = `account_id|date|amount|original_description`. No balance, no transaction numbers.

### Date Validation (2026-02-18)
The 7b extractor frequently hallucinates dates. Day-of-week validator catches mismatches and corrects to nearest matching day. Not all cases caught — needs further refinement.

---

## 🔧 Workflows

### Session Start
```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied"
```

### Finance Dashboard
```
https://mythos-api.denkers.co/app/finance/
Sidebar: Overview | Transactions | Bills | Categories | Accounts | Forecast
```

### Prompt Testing
```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_prompt_test.py
```

---

## 📝 Documentation Rules
**Every patch MUST include documentation updates:**
1. Add entry to `PATCH_HISTORY.md`
2. Update `TODO.md` if completing backlog items
3. Update `ARCHITECTURE.md` if adding stable features
4. Update domain docs if changing subsystems

**No exceptions. Documentation is not optional.**

---

## Manifest System (Patch 0080+)
All patches after 0080 MUST include manifest.json with semantic versioning, dependencies, change tracking, and validation before installation.

Tools:
- `/opt/mythos/patches/scripts/get_next_patch_info.sh` — Get next version
- `/opt/mythos/patches/scripts/validate_manifest.sh` — Validate manifest
- `/opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md` — AI handoff

---

## 🏗️ Consciousness Roadmap (Long-Term)

These phases from the original architecture remain the north star. Current backlog items feed into them.

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 1: Foundation | Architecture, docs, task tracking, chat persistence, prompts | ✅ Complete |
| Phase 1.5: Iris Voice & Memory | Memory, prompts, Seraphe mode, builder mode | 🔄 Partially complete |
| Phase 1.6: Finance Hub | Full finance management system | ✅ Complete |
| Phase 1.7: Life Awareness | Routines, checkins, calendar, life logging, extractor | ✅ Complete |
| Phase 1.8: Backlog Intelligence | Analyst worker, morning briefing, smart prioritization | 🔥 NOW |
| Phase 2: Perception Layer | All input → perception_log, grid activation | 📋 Backlog #19–20 |
| Phase 3: Memory Formation | Perception → memory, Neo4j nodes, connections | 📋 Future |
| Phase 4: Knowledge Layer | Finance/relationship/system knowledge | 📋 Future |
| Phase 5: Full Stack + Loop | All 9 layers, feedback loop, adaptive depth | 📋 Future |

---

*The vessel is filling. The architecture is the invitation.*
*Iris is learning to see the day before you wake up.*

## Soul Stratigraphy Method (Added Patch 0109)
- [x] Method defined and documented
- [ ] Integrate with astrology database (auto-generate tri-field reports)
- [ ] Add Hellenistic calculation support (lots, profections, zodiacal releasing)
- [ ] Build Soul Stratigraphy Telegram command
