# Mythos Skill Development Guide
> **Version:** 1.0
> **Author:** Ka'tuar'el / Claude
> **Date:** 2026-03-01
> **Location:** `/opt/mythos/skills/SKILL_DEVELOPMENT_GUIDE.md`

---

## What Is a Skill?

A skill is any capability that can receive a structured request, do work, and return a structured result with a mandatory human-readable summary. Skills are how Iris accesses her subsystems — finance, astrology, calendar, people, the graph, everything.

The skill engine discovers skills automatically from `/opt/mythos/skills/data/`. Drop a Python file there, subclass `SkillBase`, and it's live on the next API restart.

---

## Quick Start: Build a Skill in 5 Minutes

```python
#!/usr/bin/env python3
"""My New Skill — one-line description."""
from engine.base import SkillBase, SkillRequest, SkillResponse

class MySkill(SkillBase):
    name = "my_skill"
    version = "1.0"
    category = "data"              # data | action | composite | meta
    description = "What this skill does"
    triggers = ["keyword1", "keyword2", "phrase that activates this"]
    cache_ttl = 300                # seconds, 0 = no cache

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # Do your work here
        result = "whatever you computed"

        return SkillResponse(
            skill_name=self.name,
            data={"key": "structured data here"},
            summary=f"Natural language summary: {result}",
            confidence=0.95,
            sources=["where the data came from"],
        )
```

Save to `/opt/mythos/skills/data/my_skill.py`. Restart `mythos-api.service`. Done.

---

## The Three Files That Matter

| File | What It Does |
|------|-------------|
| `skills/engine/base.py` | SkillBase, SkillRequest, SkillResponse — the interface |
| `skills/engine/router.py` | Decides which skills to activate per message |
| `skills/engine/engine.py` | Loads skills, runs router, executes, assembles context |

You never touch these to add a skill. You only add files to `skills/data/`.

---

## Skill Types

### Data Skills (read information)

Most common. Query a database, calculate something, fetch data.

**Pattern:**
```python
async def execute(self, request: SkillRequest) -> SkillResponse:
    conn = _get_conn()  # PostgreSQL
    cur = conn.cursor()
    cur.execute("SELECT ...")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    summary = f"Found {len(rows)} items: ..."
    return SkillResponse(
        skill_name=self.name,
        data={"rows": rows},
        summary=summary,
        sources=["mythos.table_name"],
    )
```

**Examples:** `finance_balance.py`, `spiral_time.py`, `calendar_context.py`

### Action Skills (do something)

Write to database, create files, trigger notifications.

**Pattern:**
```python
class CreateEventSkill(SkillBase):
    name = "create_calendar_event"
    category = "action"
    # ...

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # Parse what to create from request.message or request.parameters
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO calendar_events ...")
        conn.commit()
        cur.close()
        conn.close()

        return SkillResponse(
            skill_name=self.name,
            data={"event_id": new_id},
            summary="Created calendar event: Doctor appointment March 5 at 2pm",
            sources=["mythos.calendar_events"],
        )
```

### Composite Skills (chain other skills)

Call multiple skills and combine their results.

**Pattern:**
```python
class DailyBriefingSkill(SkillBase):
    name = "daily_briefing"
    category = "composite"
    # ...

    async def execute(self, request: SkillRequest) -> SkillResponse:
        from data.spiral_time import SpiralTimeSkill
        from data.finance_balance import FinanceBalanceSkill
        from data.calendar_context import CalendarContextSkill

        spiral = await SpiralTimeSkill().run(request)
        finance = await FinanceBalanceSkill().run(request)
        calendar = await CalendarContextSkill().run(request)

        parts = []
        if spiral.ok: parts.append(spiral.summary)
        if finance.ok: parts.append(finance.summary)
        if calendar.ok: parts.append(calendar.summary)

        return SkillResponse(
            skill_name=self.name,
            data={
                "spiral": spiral.data,
                "finance": finance.data,
                "calendar": calendar.data,
            },
            summary=" | ".join(parts),
            sources=spiral.sources + finance.sources + calendar.sources,
        )
```

---

## The SkillRequest Object

```python
@dataclass
class SkillRequest:
    message: str           # Original user message
    context: dict          # {user_uuid, soul_name, telegram_id, ...}
    parameters: dict       # Skill-specific params from router (future)
    calling_skill: str     # If chained from another skill
    timestamp: datetime    # When the request was made
```

## The SkillResponse Object

```python
@dataclass
class SkillResponse:
    skill_name: str        # Which skill produced this
    data: dict             # Structured results (for other skills or API)
    summary: str           # MANDATORY: natural language for Iris's prompt
    confidence: float      # 0.0–1.0
    sources: list[str]     # Data provenance
    execution_ms: int      # Auto-set by engine
    error: str | None      # If something went wrong
    suggest_skills: list   # "You should also ask..."

    @property
    def ok(self) -> bool:  # True if no error and summary is non-empty
```

**The summary field is non-negotiable.** Every skill must produce a natural-language summary. This is what gets injected into Iris's prompt. She never reads raw data.

---

## Triggers: How the Router Finds Your Skill

Triggers are keywords or phrases that activate a skill. The router does case-insensitive substring matching.

```python
triggers = [
    "balance",          # Single word — matches "what's my balance"
    "checking account", # Phrase — matches "show me my checking account"
    "usaa",             # Specific term
    "how much money",   # Natural language phrase
]
```

**Tips:**
- Include the obvious keywords someone would use
- Include abbreviations and common variations
- Don't overlap heavily with other skills (router picks top 5)
- The router scores: more trigger matches = higher relevance

**Future:** The router will be upgradeable to a 7b LLM classifier. Same interface, smarter matching. Your triggers still work as hints.

---

## Caching

```python
cache_ttl = 300  # Cache results for 5 minutes
```

Guidelines:
| Data Type | TTL |
|-----------|-----|
| Natal chart data | `86400` (1 day) or more — doesn't change |
| Transit positions | `3600` (1 hour) |
| Account balances | `300` (5 min) |
| Calendar events | `300` (5 min) |
| Spiral time | `3600` (1 hour) — changes once per day |
| Live calculations | `0` (no cache) |
| Web search results | `0` (no cache) |

Cache key is auto-generated from skill name + message hash. Override `_cache_key()` for custom behavior.

---

## Database Access Pattern

Most data skills need PostgreSQL. Use this standard pattern:

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )
```

**Always close connections:**
```python
conn = _get_conn()
cur = conn.cursor()
try:
    cur.execute(...)
    rows = cur.fetchall()
finally:
    cur.close()
    conn.close()
```

For Neo4j:
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
    auth=(os.getenv('NEO4J_USER', 'neo4j'),
          os.getenv('NEO4J_PASSWORD', ''))
)
```

---

## Error Handling

Skills should never crash the message pipeline. The engine wraps every skill in try/catch, but be defensive:

```python
async def execute(self, request: SkillRequest) -> SkillResponse:
    try:
        # your work
        return SkillResponse(skill_name=self.name, data={...}, summary="...")
    except Exception as e:
        logger.error(f"My skill failed: {e}", exc_info=True)
        return SkillResponse(skill_name=self.name, error=str(e))
```

A skill returning an error is fine — it just won't appear in the context block. Other skills still run.

---

## Testing Your Skill

### From command line:
```bash
/opt/mythos/.venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/mythos/skills')
from engine import SkillEngine
e = SkillEngine()
result = e.process_sync('your test message here', {'soul_name': \"Ka'tuar'el\"})
print(result)
"
```

### Test a specific skill directly:
```bash
/opt/mythos/.venv/bin/python3 -c "
import sys, asyncio
sys.path.insert(0, '/opt/mythos/skills')
from data.my_skill import MySkill
from engine.base import SkillRequest

s = MySkill()
req = SkillRequest(message='test message')
result = asyncio.run(s.run(req))
print('OK:', result.ok)
print('Summary:', result.summary)
print('Data:', result.data)
"
```

### Check which skills are loaded:
```bash
/opt/mythos/.venv/bin/python3 -c "
import sys
sys.path.insert(0, '/opt/mythos/skills')
from engine import SkillEngine
e = SkillEngine()
e.load_skills()
for name, skill in e.skills.items():
    print(f'{name}: {skill.description} (triggers: {skill.triggers[:3]}...)')
"
```

---

## Checklist: Before Deploying a New Skill

- [ ] File is in `/opt/mythos/skills/data/`
- [ ] Imports `from engine.base import SkillBase, SkillRequest, SkillResponse`
- [ ] Class subclasses `SkillBase`
- [ ] Has `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`
- [ ] `execute()` returns a `SkillResponse` with non-empty `summary`
- [ ] Tested from command line with `process_sync()`
- [ ] Database column names verified against actual schema
- [ ] Error handling wraps database calls
- [ ] Connection closed in finally block
- [ ] `sudo systemctl restart mythos-api.service` after deploy

---

## Current Skills (as of Patch 0181)

| Skill | File | Type | Description |
|-------|------|------|-------------|
| `spiral_time` | `data/spiral_time.py` | data | 9-day cycle position + archetype |
| `finance_balance` | `data/finance_balance.py` | data | Account balances + upcoming bills |
| `calendar_context` | `data/calendar_context.py` | data | Today's events + routines |
| `astro_context` | `data/astro_context.py` | data | Natal chart placements |

---

*Every new skill makes Iris smarter. The interface is stable. Build freely.*
