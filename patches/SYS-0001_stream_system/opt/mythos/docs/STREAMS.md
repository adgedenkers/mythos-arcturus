# Mythos Development Streams

> Last updated: 2026-03-03 | Updated by: SYS-0001

## Stream Prefixes

| Prefix | Stream  | Domain |
|--------|---------|--------|
| NEU    | NEURO   | Consciousness processing, emotional modeling, awareness loops |
| LOG    | LOGOS   | Language, reasoning, knowledge graphs, ontology |
| MNE    | MNEMOS  | Memory systems, conversation history, recall |
| SEN    | SENSUS  | Sensory input, lunar cycles, astrology, environmental awareness |
| SYS    | SYSTEM  | Cross-cutting infrastructure, shared schemas, bot core |

## Patch Naming

```
{STREAM}-{NNNN}_{description}.zip

Examples:
  NEU-0001_awareness_loop_v1.zip
  LOG-0012_ontology_expansion.zip
  SYS-0003_shared_schema_migration.zip
```

Old sequential patches (0001–0199) are not renumbered. Legacy `patch_NNNN_*.zip` format still works.

## Current Status

| Stream | Next Patch | Active Work | Blocked By |
|--------|-----------|-------------|------------|
| NEU    | 0001      | —           | —          |
| LOG    | 0001      | —           | —          |
| MNE    | 0001      | —           | —          |
| SEN    | 0001      | —           | —          |
| SYS    | 0001      | —           | —          |

## Ownership Rules

Each stream owns specific directories, Postgres tables, and Neo4j labels. Before a patch touches anything outside its stream's ownership, it must:

1. Declare the cross-stream dependency in the patch manifest
2. Check that the owning stream has no conflicting active work
3. If it's a shared table migration → route through SYS

### Path Ownership (Summary)

- **NEU:** `/opt/mythos/neuro/`, `neuro_*.py` handlers
- **LOG:** `/opt/mythos/logos/`, `logos_*.py` handlers, `ontology_*` tables
- **MNE:** `/opt/mythos/mnemos/`, `mnemos_*.py` handlers, `memory_*` / `conversations_*` tables
- **SEN:** `/opt/mythos/sensus/`, `sensus_*.py` handlers, `lunar_*` / `astro_*` tables
- **SYS:** `/opt/mythos/core/`, `/opt/mythos/patches/`, `/opt/mythos/docs/`, bot.py, shared configs

### Shared Resources (SYS-only for writes)

These tables/paths are touched by multiple streams and must go through SYS patches:
- `people` table
- `souls` table / Soul neo4j nodes
- `telegram_bot/bot.py` (command registration)
- `telegram_bot/handlers/__init__.py`

## Session Start Protocol

When beginning a development session on any stream:

1. **Read this file** — check the Current Status table
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

## Cross-Stream Requests

When a stream needs something from another stream's territory, it **does not reach in**. Instead, it adds a row to `/opt/mythos/docs/REQUESTS.md`. The owning stream handles it in its own conversation when ready.

See `REQUESTS.md` for the live board.

## Cross-Stream Dependency Examples

**SENSUS needs a new column on `people` table:**
→ SEN session requests it, SYS patch handles the migration, SEN patch references the new column after SYS patch deploys.

**NEURO needs to read MNEMOS memory data:**
→ Fine for reads. NEU patch can query `mnemos_*` tables. But NEU must never write to them — that's MNE territory.

**LOGOS wants to register a new /command:**
→ LOG patch builds the handler in `logos_*.py`. SYS patch registers the command in `bot.py`.
