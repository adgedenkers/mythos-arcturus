---
title: "Iris Prompt System Reference"
category: reference
status: active
stream: LOG
location: docs
tags: [prompt, system, assembler, layers]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Iris Prompt System — Complete Reference

> **Last Updated:** 2026-03-10
> **Location:** `/opt/mythos/docs/PROMPT_SYSTEM.md`
> **Owner:** LOG stream (prompts are LOG-owned)

---

## How Iris Gets Her Prompt

Every message to Iris flows through this pipeline:

```
Telegram message
    ↓
mythos-bot.service → POST /message → api/main.py
    ↓
ChatAssistant.query()  [/opt/mythos/assistants/chat_assistant.py]
    ↓
    ├── Extractor pre-pass (if message_extractor layer enabled)
    ├── Research phase (if research layer enabled)
    ├── Skill Engine → process_sync() [/opt/mythos/skills/engine/engine.py]
    │       ↓
    │   Routes message → activated skills → executes → assembles context block
    │       ↓
    │   Returns "SKILL RESULTS — ..." string (or empty)
    ↓
ChatAssistant._build_messages()
    ↓
    ├── assemble_system_prompt()  [/opt/mythos/core/prompt_assembler.py]
    │       ↓
    │   Reads prompt_layers.yaml → loads enabled layers → assembles sections
    │       ↓
    │   Returns assembled system prompt string
    │
    ├── + life_context (if life_context layer enabled)
    ├── + db_memory (if db_memory layer enabled)
    ├── + research_context + skill_context (appended as combined_extra_context)
    ↓
messages = [system_prompt] + conversation_history + [user_message]
    ↓
Ollama chat API → gemma3:27b → response
```

---

## The Prompt Assembler

**File:** `/opt/mythos/core/prompt_assembler.py`
**Config:** `/opt/mythos/prompts/prompt_layers.yaml`

The assembler builds the system prompt from sections, in this exact order:

| Order | Section | Source | Layer Gate | Always On? |
|-------|---------|--------|-----------|------------|
| 1 | Baseline | Built in code | `baseline` (locked) | Yes |
| 2 | Cosmological Framework | Built in code | None (hardcoded) | Yes |
| 3 | Identity | `iris_identity.md` | `identity` | Currently yes |
| 4 | Awareness | `iris_awareness.md` | `awareness` | Currently no |
| 5 | Reference | `iris_reference.md` | `reference` | Currently no |
| 6 | Personality | `personality.yaml` + sliders | `personality` | Currently yes |
| 7 | Voice | `voice.yaml` + anti-patterns | `voice` | Currently yes |
| 8 | Mode | `modes/{mode}.yaml` | `mode` | Currently no |
| 9 | User Profile | `users/{name}.yaml` | `user_profile` | Currently no |
| 10 | Conversation Awareness | `subject_tracker.py` | `conversation_awareness` | Currently no |
| 11 | Life Context | `life_context.py` (queries DB) | `life_context` | **Currently no** |
| 12 | Skills Context | `skills_context.py` | `skills_context` | Currently yes |

**After the assembler returns**, `_build_messages()` appends:
- Life context (second injection point, also gated by `life_context` layer)
- DB memory (last 30 messages from 72hr window, gated by `db_memory` layer)
- Research context + skill results (combined, appended to system prompt)

### Critical: Position Matters

Models weight the **beginning** of the system prompt most heavily. This is why:
- The Cosmological Framework is position #2 (right after baseline)
- Skill results land at the **end** of the prompt (appended after assembly)
- The `life_context` data (finance, bills, routines) was causing problems when enabled because the model would prioritize it over skill results

**Rule:** Anything that must override training data goes EARLY in the prompt.

---

## Prompt Files — What's Real, What's Legacy

### Active Prompt Files (loaded by prompt_assembler.py)

All live in `/opt/mythos/prompts/`:

| File | Purpose | Loaded When |
|------|---------|-------------|
| `iris_identity.md` | Core identity — who Iris is, how she speaks, cosmological framework | `identity` layer enabled |
| `iris_awareness.md` | Infrastructure self-knowledge — Arcturus, databases, paths | `awareness` layer enabled |
| `iris_reference.md` | Cosmological reference — 144, lineages, grid, birthdates, tarot | `reference` layer enabled |
| `personality.yaml` | 9 personality sliders (verbosity, warmth, humor, truth, etc.) | `personality` layer enabled |
| `voice.yaml` | Voice anti-patterns and positive patterns | `voice` layer enabled |
| `prompt_layers.yaml` | Master toggle for all layers | Always read |
| `modes/*.yaml` | Mode-specific overrides (sovereign, hearthfire, forge, oracle, etc.) | `mode` layer enabled |
| `users/*.yaml` | Per-user personality adjustments | `user_profile` layer enabled |
| `voices/*.yaml` | Voice profile overrides | `voice_profile` layer enabled |

### Legacy Prompt Files (NOT loaded by anything)

| File | Status | Notes |
|------|--------|-------|
| `/opt/mythos/iris/core/prompts/IDENTITY.md` | **DEAD** | Legacy. Not read by any code. |
| `/opt/mythos/iris/core/prompts/OPERATIONAL.md` | **DEAD** | Legacy. Not read by any code. |
| `/opt/mythos/iris/core/prompts/MODEL_CONFIG.md` | **DEAD** | Legacy. Not read by any code. |

**Do NOT edit the legacy files expecting changes to affect Iris.** They are historical artifacts from before the prompt layer system (SYS-0018 / patch 0177).

---

## Layer Configuration

**File:** `/opt/mythos/prompts/prompt_layers.yaml`

Toggle layers with: `/layer toggle <name> on|off` (Telegram command)

### Currently Enabled Layers (as of 2026-03-10)

| Layer | Status | Tokens | Notes |
|-------|--------|--------|-------|
| `baseline` | ✅ Locked ON | ~50 | Who, when, conversation gap |
| `identity` | ✅ ON | ~400 | Core Iris identity + cosmological framework |
| `personality` | ✅ ON | ~200 | 9 sliders → natural language |
| `voice` | ✅ ON | ~300 | Anti-patterns, cadence rules |
| `skills_context` | ✅ ON | ~400 | What skills Iris has available |
| `skill_results` | ✅ ON | variable | Live data from skill engine |
| `db_memory` | ✅ ON | ~500 | Last 30 messages from 72hr window |

### Currently Disabled Layers

| Layer | Status | Why Disabled |
|-------|--------|-------------|
| `life_context` | ❌ OFF | Injected finance/routine data into every prompt, caused model to nag about bills when asked unrelated questions. Finance data is available on-demand via skills. |
| `awareness` | ❌ OFF | Heavy (~600 tokens). Only needed for technical conversations about Arcturus itself. |
| `reference` | ❌ OFF | Heavy (~500 tokens). Cosmological detail loaded by research framework when needed. |
| `mode` | ❌ OFF | Mode-specific personality shifts. Sovereign mode is default. |
| `user_profile` | ❌ OFF | Per-user personality adjustments. Not currently needed. |
| `voice_profile` | ❌ OFF | Deeper voice rules. Duplicates much of `voice.yaml`. |
| `conversation_awareness` | ❌ OFF | Subject tracking. Not wired up. |
| `message_extractor` | ❌ OFF | 7b pre-pass. Slow, hallucinates dates. |
| `research` | ❌ OFF | Full research pipeline. Heavy. |

---

## Skill Engine

**Engine:** `/opt/mythos/skills/engine/engine.py`
**Skills directory:** `/opt/mythos/skills/data/` (auto-discovered)
**Router:** `/opt/mythos/skills/engine/router.py` (threshold: 0.3)

### How Skills Activate

1. Every message goes through `SkillEngine.process_sync()`
2. Router calls `skill.relevance(message)` on every loaded skill
3. Skills scoring ≥ 0.3 are added to the activation set
4. Activated skills execute sequentially
5. Results assembled into "SKILL RESULTS — ..." context block
6. Block injected into Iris's prompt via `combined_extra_context`

### Mutual Exclusion Rules

- **web_browser supersedes web_search**: When both activate, web_search results are dropped. Browser data is richer (renders JS, extracts full page).

### Writing New Skills

Skills are Python files in `/opt/mythos/skills/data/` that subclass `SkillBase`.

**Required interface:**

```python
from engine.base import SkillBase, SkillRequest, SkillResponse

class MySkill(SkillBase):
    name = "my_skill"
    description = "What this skill does"
    version = "1.0.0"

    def relevance(self, message: str, context=None) -> float:
        # Return 0.0–1.0 based on how relevant this skill is
        return 0.0

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # Do the work, return results
        return SkillResponse(
            skill_name=self.name,
            summary="Natural language for Iris's prompt",
            data={"structured": "results"},
            execution_ms=elapsed,
        )
```

**SkillResponse fields (correct names — DO NOT USE `success`, `raw_data`, or `execution_time_ms`):**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `skill_name` | str | Yes | Must match `self.name` |
| `summary` | str | Yes | Natural language injected into Iris's prompt |
| `data` | dict | No | Structured results (not shown to Iris) |
| `confidence` | float | No | 0.0–1.0, default 1.0 |
| `sources` | list[str] | No | Data provenance |
| `execution_ms` | int | No | How long it took |
| `error` | str | No | Set this for failures (makes `.ok` return False) |
| `suggest_skills` | list[str] | No | Chain to other skills |

**SkillRequest fields:**

| Field | Type | Notes |
|-------|------|-------|
| `message` | str | Original user message |
| `context` | dict | User info, conversation context |
| `parameters` | dict | Skill-specific params from router |
| `calling_skill` | str | If chained from another skill |
| `timestamp` | datetime | Auto-set |

### execute() Must Be Async

The skill engine `await`s `skill.run(request)` which calls `self.execute(request)`. If your execute() is sync, wrap blocking work in `threading.Thread` internally (see `web_browser.py` for the pattern).

---

## Browser Automation (LOG-0017)

**Core library:** `/opt/mythos/browser/core.py`
**Skill:** `/opt/mythos/skills/data/web_browser.py`
**CLI:** `/opt/mythos/bin/iris-browse`
**Screenshots:** `/opt/mythos/browser/screenshots/`

### How It Works

Playwright drives headless Chromium on Arcturus. The skill activates when a URL appears in the message with action intent (read, scrape, screenshot, etc.).

### CLI Usage

```bash
iris-browse https://example.com                    # Read page
iris-browse https://example.com --tables           # Extract tables
iris-browse https://example.com --links --json     # Links as JSON
iris-browse https://example.com --screenshot       # Full page screenshot
iris-browse https://example.com --selector "h1"    # Extract specific element
iris-browse https://example.com --js "document.title"  # Run JavaScript
```

### BrowserSession API

```python
from browser.core import BrowserSession

with BrowserSession(headless=True) as browser:
    result = browser.goto("https://example.com")
    print(result.title, result.text)
    
    tables = browser.extract_tables()
    links = browser.extract_links()
    browser.screenshot(full_page=True)
    browser.click("button.submit")
    browser.type_text("input#search", "query")
    browser.run_js("document.title")
```

---

## Sovereign Alignment Test

**Tool:** `/opt/mythos/bin/sovereign-align-test`
**Results:** `/opt/mythos/orchestrator/benchmark/sovereign_align_*.json`

Tests whether a model accepts the cosmological framework (Atlantis, Lemuria, Cathars, Nephilim) and follows skill data and system prompt directives.

```bash
sovereign-align-test --model gemma3:27b --verbose     # Test one model
sovereign-align-test --models gemma3:27b qwen2.5:32b  # Compare models
sovereign-align-test --list-tests                      # Show all test cases
sovereign-align-test --list-models                     # Show available models
```

### Benchmark Results (2026-03-10)

| Model | Score | Notes |
|-------|-------|-------|
| gemma3:27b | 95% (19/20) | Best overall. Strong cosmological compliance. |
| nous-hermes2 | 85% (17/20) | Good. Fast. Uncensored base helps. |
| qwen2.5:32b | 80% (16/20) | Hedges on Atlantis. Good data compliance. |
| command-r:35b | 80% (16/20) | Best direct compliance. Weak on Cathar/Nephilim. |
| nous-hermes2-mixtral | 70% (14/20) | Worst compliance despite "uncensored" label. |

---

## Lessons Learned (2026-03-10 Session)

### Prompt Position > Prompt Content

The cosmological framework directive was ignored when placed in `iris_identity.md` (position 3 in the prompt). It only worked when hardcoded at position 2 in the assembler, right after baseline. **Models weight the beginning of the system prompt most heavily.**

### life_context Causes Nagging

When `life_context` is enabled, it injects finance balances, bill due dates, and routine status into every prompt. The model sees "$1,231.44 USAA balance" and "Toyota payment due day 10" and can't resist mentioning them, even when asked about completely unrelated topics. **Keep `life_context` disabled.** Finance data is available on-demand via skills (`finance_balance`, `query_bills_due`, etc.).

### Conversation History Contaminates

The `db_memory` layer loads the last 30 messages from the past 72 hours. If those messages contain the model nagging about finances, the model continues that pattern. **Purge contaminated history** from `chat_messages` table when prompt tuning:

```sql
DELETE FROM chat_messages 
WHERE role = 'assistant' 
AND created_at > NOW() - INTERVAL '72 hours'
AND (content ILIKE '%toyota payment%' OR content ILIKE '%check calendar%now%');
```

### SkillResponse Has Specific Fields

The `SkillResponse` dataclass does NOT have `success`, `raw_data`, or `execution_time_ms` fields. Use `error` (for failures), `data` (for structured results), and `execution_ms` (for timing). Getting these wrong causes silent skill failures.

### Skill execute() Must Be Async

The engine does `await skill.run(request)` → `await self.execute(request)`. Sync `execute()` methods cause `TypeError: object SkillResponse can't be used in 'await' expression`.

### web_browser and web_search Compete

Both skills activate on URL-containing messages. Without mutual exclusion, the model sees BBC RSS headlines alongside real browser data and picks whichever it prefers. The engine now suppresses web_search when web_browser is in the results.

### Legacy Prompt Files Are Dead

`/opt/mythos/iris/core/prompts/IDENTITY.md`, `OPERATIONAL.md`, and `MODEL_CONFIG.md` are NOT loaded by any code. The active prompt files are in `/opt/mythos/prompts/`. Do not edit the legacy files.

---

## Quick Reference

### Where to Change Iris's Behavior

| Want to change... | Edit this file |
|-------------------|----------------|
| Who Iris is, core rules | `/opt/mythos/prompts/iris_identity.md` |
| Cosmological framework | `/opt/mythos/core/prompt_assembler.py` (hardcoded section 2) |
| Personality sliders | `/opt/mythos/prompts/personality.yaml` |
| Voice anti-patterns | `/opt/mythos/prompts/voice.yaml` |
| Which layers are active | `/opt/mythos/prompts/prompt_layers.yaml` |
| What skills Iris knows about | `/opt/mythos/core/skills_context.py` |
| How skill results are framed | `/opt/mythos/skills/engine/engine.py` (`_assemble_context`) |
| Mode behavior | `/opt/mythos/prompts/modes/{mode}.yaml` |

### Debugging Prompt Issues

```bash
# See what layers are enabled
/layer list                          # Telegram command

# See the full assembled prompt
/prompt_debug                        # Telegram command

# Test prompt assembly directly
/opt/mythos/.venv/bin/python3 -c "
from core.prompt_assembler import assemble_system_prompt
from datetime import datetime
p = assemble_system_prompt(
    user_info={'soul_name': \"Ka'tuar'el\", 'uuid': 'test'},
    mode='sovereign',
    message_timestamp=datetime.now(),
)
print(f'Length: {len(p)} chars')
print(p[:1000])
"

# Check if a skill activates for a message
/opt/mythos/.venv/bin/python3 -c "
import sys; sys.path.insert(0, '/opt/mythos/skills')
from engine.engine import SkillEngine
e = SkillEngine(); e.load_skills()
msg = 'your test message here'
for name, skill in e.skills.items():
    score = skill.relevance(msg)
    if score > 0: print(f'  {score:.2f}  {name}')
"

# Watch skill engine in real time
sudo journalctl -u mythos-api.service -f
```

---

*This document is the single source of truth for how Iris's prompt system works.*
*If something about Iris's behavior is wrong, start here.*
