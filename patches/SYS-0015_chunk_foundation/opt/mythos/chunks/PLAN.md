# Chunk Factory — Plan of Attack

> **Version:** 1.0
> **Date:** 2026-03-04
> **Author:** Ka'tuar'el + Claude
> **Status:** Foundation deployed, chunk build phase begins

---

## The Architecture

Three layers, bottom up:

**Layer 1: Chunks** — Atomic units. One job each. Defined input/output.
**Layer 2: Patterns** — Known compositions of chunks. Templates for solution types.
**Layer 3: Solutions** — Specific instances. Claude designs, Ollama grinds.

The pipeline: Claude picks a pattern → fills in the specifics → writes a build plan →
the grinder feeds each step to Ollama → tests after each step → loops until it works.

---

## Infrastructure (Deployed)

| Component | Path | Status |
|-----------|------|--------|
| Chunk contract schema | `/opt/mythos/chunks/CHUNK_CONTRACT.json` | ✅ |
| Pattern library | `/opt/mythos/patterns/PATTERNS.json` | ✅ |
| Single-shot eval harness | `/opt/mythos/eval/ollama_builder.py` | ✅ |
| Multi-pass grinder | `/opt/mythos/eval/ollama_grinder.py` | ✅ |
| `chunk-eval` CLI | `/usr/local/bin/chunk-eval` | ✅ |
| `chunk-grind` CLI | `/usr/local/bin/chunk-grind` | ✅ |
| Skill reference | `/opt/mythos/eval/skill_reference/SKILL.md` | ✅ |
| Challenge: people_lookup | `/opt/mythos/eval/challenges/people_lookup/` | ✅ |

---

## 24 Chunks to Build (Priority Order)

### Phase 1: Memory Search (chunks 1–7)
_These make Iris able to search and retrieve from her memory stores._

| # | Chunk ID | Type | Pattern | Tables | What It Does |
|---|----------|------|---------|--------|-------------|
| 1 | `search_voice_memos` | text_search | memory_search | voice_memos | FTS on transcript_full, returns memo previews with timestamps |
| 2 | `search_conversations` | text_search | memory_search | conversation_turns, conversations | FTS on conversation content, returns turn context |
| 3 | `search_life_events` | text_search | memory_search | life_events | Search event descriptions by keyword, filter by domain/person |
| 4 | `search_ideas` | text_search | memory_search | idea_inbox | Search idea contexts and items, filter by disposition |
| 5 | `search_documents` | text_search | memory_search | document_registry | Search document titles and metadata |
| 6 | `memory_router` | route_intent | memory_search | — | Analyzes message to determine which memory stores to search |
| 7 | `memory_search_composite` | compose | composite_skill | — | Chains router → searchers → ranker → summary. The full memory pipeline. |

### Phase 2: Data Access (chunks 8–14)
_Wrap existing tables in queryable chunks._

| # | Chunk ID | Type | Pattern | Tables | What It Does |
|---|----------|------|---------|--------|-------------|
| 8 | `query_transactions` | db_query | data_query_skill | transactions, accounts | Query transactions by date range, account, amount, description |
| 9 | `query_bills_due` | db_query | data_query_skill | recurring_bills, bill_overrides | Find upcoming bills in next N days, check payment status |
| 10 | `query_routines` | db_query | data_query_skill | routines, routine_completions | Today's routines and completion status |
| 11 | `query_calendar` | db_query | data_query_skill | calendar_events | Events for today/this week, with time and location |
| 12 | `query_natal_chart` | db_query | data_query_skill | astro_natal_charts, astro_chart_objects | Natal placements for a given person |
| 13 | `query_shopping_lists` | db_query | data_query_skill | shopping_lists, shopping_list_items | Active lists and their items |
| 14 | `lookup_person` | db_query | data_query_skill | people, person_dates | Search people by name/alias (already deployed as people_lookup) |

### Phase 3: Actions (chunks 15–18)
_Write chunks that modify data._

| # | Chunk ID | Type | Pattern | Tables | What It Does |
|---|----------|------|---------|--------|-------------|
| 15 | `log_life_event` | db_write | action_skill | life_events | Insert a new life event with domain, person, mood |
| 16 | `add_idea` | db_write | action_skill | idea_inbox | Capture a new idea with context and tags |
| 17 | `log_checkin` | db_write | action_skill | checkin_log | Record a mood/status check-in |
| 18 | `complete_routine` | db_write | action_skill | routine_completions | Mark a routine as done for today |

### Phase 4: Utilities (chunks 19–24)
_Reusable helpers that multiple patterns need._

| # | Chunk ID | Type | Pattern | Tables | What It Does |
|---|----------|------|---------|--------|-------------|
| 19 | `extract_date_range` | date_filter | any | — | Parse "last week", "yesterday", "March 2026" into SQL date WHERE |
| 20 | `extract_search_terms` | route_intent | any | — | Strip trigger phrases, extract meaningful keywords from a message |
| 21 | `rank_by_recency` | rank_results | memory_search | — | Sort results newest-first, format relative timestamps |
| 22 | `rank_by_relevance` | rank_results | memory_search | — | Score results by keyword match density + recency blend |
| 23 | `format_person_summary` | format_summary | any | — | Standard person display: name, alias, birth data, location |
| 24 | `format_financial_summary` | format_summary | any | — | Standard finance display: accounts, balances, upcoming bills |

---

## Build Strategy

### For each chunk:

1. **Claude designs it** — picks the pattern, writes the scaffold with method stubs,
   defines the test cases, writes the build plan JSON
2. **Grinder builds it** — feeds each build step to Ollama, tests after each step,
   loops on failures
3. **Review & deploy** — if the grinder produces a passing skill, package as a patch
4. **Register** — add to chunk registry, update ARCHITECTURE.md

### Priority: Build chunks 1–7 first.
Memory search is the highest-value capability Iris doesn't have yet.
Once the memory pipeline works, Iris can answer "what did we talk about?"
and "remember when?" — that's transformative.

### Testing each chunk:
Every chunk gets a `build_plan.json` in `/opt/mythos/eval/challenges/{chunk_id}/`.
The build plan includes test cases with real data from the database.
The grinder validates structurally AND behaviorally.

---

## Composing Chunks into Skills

Once individual chunks exist, composites are trivial:

**Daily Briefing** = `spiral_time` + `query_calendar` + `query_bills_due` + `query_routines`

**Memory Search** = `memory_router` + `search_voice_memos` + `search_conversations`
                    + `search_life_events` + `rank_by_relevance` + format

**Financial Overview** = `query_transactions` + `query_bills_due` + `format_financial_summary`

**Person Deep Dive** = `lookup_person` + `query_natal_chart` + `search_life_events`
                       + `search_conversations` (filtered by person)

Each composite is itself a chunk (type: compose) that follows the composite_skill pattern.

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Chunks that pass structural validation | 100% |
| Chunks that pass behavioral tests | 90%+ |
| Average grinder passes to completion | ≤ 6 |
| Time per chunk (grinder, qwen3-coder:30b) | < 2 min |
| Chunks deployable without manual edit | 80%+ |

---

## What This Enables

Once we have 24 chunks + the grinder pipeline:

- **Iris can search her own memory** across all stores
- **New features** get built through the pipeline, not by hand
- **Local models** do the implementation work
- **Claude** focuses on architecture and design
- **Testing is automatic** — every chunk is validated before deploy
- **Composition is trivial** — chain existing chunks into new skills
- **The system builds itself** — each new chunk teaches the grinder's patterns

This is the foundation. Everything else grows from here.

---

_Designed by Ka'tuar'el_
_Built on Arcturus_
