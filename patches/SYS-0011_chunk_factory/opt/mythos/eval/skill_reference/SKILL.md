---
name: mythos-chunk
description: >
  Build a Mythos radioactive chunk — a self-contained Python skill that plugs into the
  Iris skill engine on Arcturus. Use this skill whenever the user asks to create a new
  Iris skill, build a data skill, add a Telegram-aware query, wrap a database table in
  the skill interface, or when any phrase like "build a chunk", "new skill for Iris",
  "wrap this in a skill", "radioactive chunk", or "add a skill to Mythos" appears.
  Also trigger when the user wants to expose any PostgreSQL, Neo4j, or computed data
  through the skill engine, or when building eval challenges for the Ollama chunk factory.
---

# Mythos Radioactive Chunk Builder

Build a single, self-contained Python skill file that plugs into the Mythos skill engine
on Arcturus. Every chunk subclasses `SkillBase`, lives in `/opt/mythos/skills/data/`,
and is autodiscovered on API restart.

## What Is a Chunk?

A radioactive chunk is:
- **One Python file** in `/opt/mythos/skills/data/`
- **One class** subclassing `SkillBase`
- **One job** — query data, perform an action, or compose other skills
- **Self-describing** — name, version, category, description, triggers
- **Self-testing** — defined inputs produce predictable outputs
- **Composable** — any chunk can call any other chunk via `await OtherSkill().run(request)`

## Required Contract

Every chunk MUST have these class attributes:

```python
name = "snake_case_name"          # Unique across all skills
version = "1.0"                   # Semver
category = "data"                 # data | action | composite | meta
description = "What this does"    # One line, for humans and router
triggers = ["keyword1", "phrase"] # What activates this skill (5-15 entries)
cache_ttl = 300                   # Seconds. 0 = no cache.
```

Every chunk MUST implement:

```python
async def execute(self, request: SkillRequest) -> SkillResponse:
```

Every `SkillResponse` MUST have a non-empty `summary` field. This is non-negotiable —
Iris never reads raw data, only natural language summaries.

## File Template

```python
#!/usr/bin/env python3
"""
{Skill Title}
{'=' * len(title)}

{One paragraph: what this skill does, what data it touches, when it activates.}
"""
import os
import logging
from typing import Any, Dict

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

from engine.base import SkillBase, SkillRequest, SkillResponse

logger = logging.getLogger(__name__)


def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


class {ClassName}(SkillBase):
    name = "{skill_name}"
    version = "1.0"
    category = "{data|action|composite|meta}"
    description = "{one line description}"
    triggers = [
        # 5-15 keywords/phrases that should activate this skill
    ]
    cache_ttl = {ttl}  # seconds

    async def execute(self, request: SkillRequest) -> SkillResponse:
        try:
            conn = _get_conn()
            cur = conn.cursor()

            # --- Your query/logic here ---

            cur.close()
            conn.close()

            # Build natural language summary (MANDATORY)
            summary = "..."

            return SkillResponse(
                skill_name=self.name,
                data={},           # Structured data for other skills/API
                summary=summary,   # What Iris reads
                confidence=0.95,
                sources=["mythos.table_name"],
            )

        except Exception as e:
            logger.error(f"{self.name} failed: {e}", exc_info=True)
            return SkillResponse(skill_name=self.name, error=str(e))
```

## System Context (Arcturus)

The skill runs inside this environment:

- **Python:** `/opt/mythos/.venv/bin/python3`
- **Skill directory:** `/opt/mythos/skills/data/` (autodiscovered)
- **Engine import:** `from engine.base import SkillBase, SkillRequest, SkillResponse`
- **PostgreSQL:** `mythos` database, 92+ tables. Connection via `_get_conn()` pattern above.
- **Neo4j:** `bolt://localhost:7687`. Use `from neo4j import GraphDatabase`.
- **Redis:** `localhost:6379`. Use `import redis`.
- **Ollama:** `http://localhost:11434`. For LLM-powered skills.
- **Environment:** All secrets in `/opt/mythos/.env`, loaded via `dotenv`.

### SkillRequest Fields
```
request.message      → str: Original user message
request.context      → dict: {user_uuid, soul_name, telegram_id, ...}
request.parameters   → dict: Skill-specific params from router
request.calling_skill → str|None: If chained from another skill
request.timestamp    → datetime: When request was made
```

### SkillResponse Fields
```
skill_name    → str: Your skill's name
data          → dict: Structured results (for API/other skills)
summary       → str: MANDATORY natural language (for Iris's prompt)
confidence    → float: 0.0–1.0
sources       → list[str]: Where the data came from
error         → str|None: If something went wrong
suggest_skills → list[str]|None: Related skills to also invoke
```

## Process

### Step 1: Understand the Requirement

Before writing any code, determine:

1. **What data source?** PostgreSQL table(s), Neo4j labels, computed, or external?
2. **What query?** What SQL/Cypher does this skill run?
3. **What output?** What should the `data` dict contain? What should `summary` say?
4. **What triggers?** What words/phrases should activate this skill?
5. **What category?** `data` (read), `action` (write), `composite` (chains others), `meta` (system)
6. **Cache TTL?** How often does this data change?

### Step 2: Check the Schema

If touching PostgreSQL, verify the actual table schema:
```sql
\d+ table_name
SELECT * FROM table_name LIMIT 5;
```

Never guess column names. Use the real schema.

### Step 3: Write the Skill

Follow the template above. Key rules:

- **One class per file.** The filename should match the skill name: `my_skill.py` → `name = "my_skill"`.
- **Always close database connections** in a `try/finally` block.
- **Summary must be human-readable.** Not "Found 3 rows" but "3 people match: Alice, Bob, Charlie."
- **Data must be structured.** Lists of dicts, not raw tuples.
- **Triggers should include common variations.** If the skill handles "people", also include "person", "who is", "find person", etc.
- **Error handling wraps the entire execute() body.**

### Step 4: Validate

The skill must pass these checks:

1. **Parses:** `python3 -c "import ast; ast.parse(open('file.py').read())"`
2. **Imports:** The class can be imported without error
3. **Subclasses SkillBase:** `issubclass(MyClass, SkillBase)` is True
4. **Has all required attributes:** name, version, category, description, triggers, cache_ttl
5. **execute() exists:** It's an async method returning SkillResponse
6. **Summary is non-empty:** For any valid input, `response.summary` is truthy
7. **No crashes:** Handles missing data, empty results, connection failures gracefully

### Step 5: Deploy

The skill file goes into a Mythos patch:

```
SYS-NNNN_new_skill_name/
├── install.sh
├── apply_patch.py
└── opt/mythos/skills/data/skill_name.py
```

After deploy: `sudo systemctl restart mythos-api.service`

## Category-Specific Patterns

### Data Skills (most common)
Query PostgreSQL or Neo4j, return structured results.
- Always use `RealDictCursor` for Postgres
- Close connections in `finally`
- Build summary from actual data, not generic messages

### Action Skills
Write to database, create files, trigger external actions.
- Return confirmation in summary: "Created event: Doctor March 5 at 2pm"
- Include the created/modified record ID in data
- Consider idempotency

### Composite Skills
Chain multiple skills together.
- Import and instantiate other skills: `from data.other_skill import OtherSkill`
- Call via `await OtherSkill().run(request)`
- Check `.ok` before using results
- Combine summaries from sub-skills

## Anti-Patterns (Never Do These)

- ❌ Hardcode database credentials
- ❌ Return empty summary (Iris can't use the skill)
- ❌ Leave database connections open
- ❌ Put multiple classes in one file
- ❌ Use `print()` instead of `logger`
- ❌ Assume table columns exist without checking schema
- ❌ Forget error handling around database calls
- ❌ Use synchronous `def execute()` (must be `async def`)

## Examples

### Example 1: Simple Data Skill

**Requirement:** Look up a person by name from the `people` table.

See `/opt/mythos/eval/challenges/people_lookup/gold/people_lookup.py` for the
complete gold standard implementation.

### Example 2: Composite Skill

**Requirement:** Daily briefing combining spiral time + finance + calendar.

```python
class DailyBriefingSkill(SkillBase):
    name = "daily_briefing"
    category = "composite"
    triggers = ["good morning", "daily briefing", "what's today"]
    cache_ttl = 300

    async def execute(self, request: SkillRequest) -> SkillResponse:
        from data.spiral_time import SpiralTimeSkill
        from data.finance_balance import FinanceBalanceSkill
        parts, all_sources = [], []
        for SkillCls in [SpiralTimeSkill, FinanceBalanceSkill]:
            result = await SkillCls().run(request)
            if result.ok:
                parts.append(result.summary)
                all_sources.extend(result.sources)
        return SkillResponse(
            skill_name=self.name,
            data={},
            summary=" | ".join(parts) if parts else "No data available.",
            sources=all_sources,
        )
```

---
_Skill format: Mythos SkillBase v1.0_
_System: Arcturus (Ubuntu 24.04)_
_Author: Ka'tuar'el_
