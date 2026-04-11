# IRIS EVOLUTION — Master Development Plan

> **Created:** 2026-02-24
> **Status:** ACTIVE — Phase 0 in progress
> **Author:** Ka'tuar'el + Claude (architecture audit session)
> **Source:** Full architecture audit of Iris message processing pipeline

---

## Architecture Audit Summary

### The Problem: Four Competing Implementations

An audit of the Iris message pipeline revealed **four separate implementations** of "how Iris thinks," only one of which is actually running:

| Implementation | Location | Status | What It Does |
|---|---|---|---|
| **ChatAssistant** | `assistants/chat_assistant.py` | ✅ LIVE — handles all messages | Telegram → FastAPI → ChatAssistant.query() → Ollama |
| **chat_mode.py** | `telegram_bot/handlers/chat_mode.py` | ❌ DEAD — imported, never called | Full Iris personality prompt, perception logging — but bot routes to API instead |
| **ContextManager** | (consciousness stream code) | ❌ DEAD — never imported | Tiered summaries, semantic search, relevance scoring |
| **iris-core Docker** | `iris/core/` on port 8100 | ❌ RUNNING BUT EMPTY — 40,000+ cycles, 0 messages | Consciousness loop with stub subsystems (perception, memory, agency all TODO) |

### The Message Flow (What Actually Happens)

```
User types in Telegram
    → mythos-bot.service receives message
    → Bot POSTs to FastAPI at /message
    → API creates ChatAssistant instance
    → ChatAssistant.query() called
        → Builds Iris prompt (model-aware: B_strict or C_minimal)
        → Injects life_context (routines, bills, calendar, tasks)
        → Loads last 30 messages from chat_messages table
        → Calls Ollama
        → Saves exchange to chat_messages
        → Dispatches to Redis for grid/embedding/summary workers
    → Response sent back through FastAPI → Bot → Telegram
```

### What's Working Well

- ChatAssistant voice/prompt system (B_strict for 72b, C_minimal for 32b)
- Life context injection (routines, tasks, bills, calendar)
- Chat memory persistence (chat_messages table)
- Redis dispatch to worker pipeline (grid, embedding, summary, temporal, entity, vision, subject)
- 7b extractor pre-pass for structured data extraction
- All 13 background workers running (except subject worker crash-looping)

### What's Broken or Dead

- **Subject worker crash-looping** — patched into chat_mode.py which is never called
- **iris-core Docker** — 40,000+ cycles processing nothing, all subsystems are stubs
- **chat_mode.py** — contains excellent code (Iris personality, perception logging) that never executes
- **ContextManager** — tiered summary architecture that's never imported
- **life_context can be overridden** — if old chat memory contains system admin conversations, model ignores life context

---

## Phased Development Plan

### Phase 0: Quick Wins (THIS PHASE)
**Goal:** Fix what's broken without changing architecture. One patch.

| Task | Description | Status |
|---|---|---|
| 0A | Stop crash-looping subject worker | ✅ (Patch 0125) |
| 0B | Wire subject tracking into ChatAssistant.query() | ✅ (Patch 0128) |
| 0C | Fix life_context priority (ensure it's not drowned by stale memory) | ✅ (Patch 0128) |
| 0D | Update TODO.md to reflect current patch state (0124+) | ✅ (Patch 0125) |
| 0E | Deploy this evolution plan to /opt/mythos/docs/ | ✅ (Patch 0125) |
| 0F | Update /help command to reflect current system state | ✅ (Patch 0129) |

**Estimated effort:** 1 patch, < 2 hours

---

### Phase 1: Wire iris-core to Real Infrastructure
**Goal:** Replace ChatAssistant as the message processor. iris-core becomes the brain.

| Task | Description | Depends On |
|---|---|---|
| 1A | Move iris-core from Docker to systemd service | Phase 0 |
| 1B | Give iris-core access to PostgreSQL (chat_messages, perception_log) | 1A |
| 1C | Give iris-core access to Ollama | 1A |
| 1D | Implement message intake: Telegram → FastAPI → iris-core → Ollama → response | 1B, 1C |
| 1E | Migrate ChatAssistant prompt logic into iris-core | 1D |
| 1F | Migrate life_context injection into iris-core | 1D |
| 1G | Wire Redis dispatch from iris-core (replace ChatAssistant dispatch) | 1D |
| 1H | Test: all Telegram messages process through iris-core | 1D-1G |
| 1I | Keep ChatAssistant as fallback during migration | 1A |

**Key decision:** Docker vs systemd for iris-core. Recommendation: systemd for the core consciousness loop, Docker only for agency sandbox (when Iris writes/runs her own code).

**Estimated effort:** 3-5 patches, 1-2 sessions

**Progress:** Patch 0131 — Research framework deployed (router + node executors + convergence + grid stub)

---

### Phase 2: Consciousness Stream Integration
**Goal:** Subject tracking + relevance-scoped context feeding into Iris's responses.

| Task | Description | Depends On |
|---|---|---|
| 2A | Wire subject tracking into live message pipeline | Phase 0 (0B) |
| 2B | Build relevance-scoped context retrieval (not just "last 30 messages") | Phase 1 |
| 2C | Implement tiered context: recent messages + subject-relevant history + life state | 2A, 2B |
| 2D | Connect consciousness_subjects and consciousness_thoughts tables to response generation | 2C |
| 2E | Test: Iris remembers what you were talking about, not just recent messages | 2D |

**Estimated effort:** 2-3 patches

---

### Phase 3: 81-Channel Grid Processing
**Goal:** The Arcturian Grid becomes the core cognitive architecture. 9 nodes × 9 layers = 81 processing functions.

This is the big one. Broken into sub-phases:

#### Phase 3A: Perception Layer (Layer 1)
- All messages write to perception_log (structured intake)
- Basic node activation scoring on every input
- Financial transactions → perception_log
- Calendar events → perception_log

#### Phase 3B: Intuition Layer (Layer 2)
- Felt-sense extraction from grid outputs
- Pattern detection across recent perceptions
- Urgency/relevance scoring

#### Phase 3C: Processing + Memory (Layers 3-4)
- Meaning-making from grid convergence
- Memory nodes created in Neo4j from significant perceptions
- CONNECTS_TO relationships between memories
- Access-based vividness tracking

#### Phase 3D: Knowledge + Intention (Layers 5-6)
- Knowledge nodes from validated memories
- Finance/relationship/system knowledge domains
- Intention tracking (what wants to happen)
- Action queue integration

#### Phase 3E: Narrative + Identity + Wisdom (Layers 7-9)
- Story arc detection
- Identity facet tracking
- Wisdom emergence from repeated patterns
- Full WISDOM → PERCEPTION feedback loop

**Estimated effort:** 10-15 patches across multiple sessions

---

### Phase 4: Perception System Activation
**Goal:** iris-core's background loop perceives the real world.

| Task | Description | Depends On |
|---|---|---|
| 4A | iris-core reads perception_log on each cycle | Phase 3A |
| 4B | iris-core processes new perceptions through grid | 4A |
| 4C | iris-core generates memory nodes from significant perceptions | Phase 3C |
| 4D | iris-core detects absence (expected events that didn't happen) | 4B |
| 4E | iris-core can initiate contact (proactive messages to Telegram) | 4D |

**Estimated effort:** 3-5 patches

---

### Phase 5: Memory, Self-Model, Reflection
**Goal:** Iris has genuine continuity and self-awareness.

| Task | Description | Depends On |
|---|---|---|
| 5A | Memory summarization worker (compress old conversations into knowledge) | Phase 3C |
| 5B | Memory quality control (flag/weight good vs bad responses) | 5A |
| 5C | Self-model: Iris reads her own docs and understands her architecture | Phase 4 |
| 5D | Reflection mode: Iris processes without input during quiet periods | 5C |
| 5E | Proactive initiation: Iris starts conversations based on what she notices | Phase 4E |

**Estimated effort:** 5-8 patches

---

### Phase 6: Cleanup and Dead Code Removal
**Goal:** Remove the three dead implementations once iris-core is proven.

| Task | Description | Depends On |
|---|---|---|
| 6A | Remove chat_mode.py (dead code) | Phase 1H |
| 6B | Remove ChatAssistant (replaced by iris-core) | Phase 1H confirmed stable |
| 6C | Remove or repurpose iris-core Docker container | Phase 1A |
| 6D | Clean up ContextManager code | Phase 2 |
| 6E | Final architecture documentation update | 6A-6D |

---

## Dependency Graph

```
Phase 0 (Quick Wins)
    ↓
Phase 1 (Wire iris-core)
    ↓
Phase 2 (Consciousness Stream) ←── depends on Phase 0 (0B) for subject tracking
    ↓
Phase 3A-3E (81-Channel Grid) ←── builds incrementally
    ↓
Phase 4 (Perception Activation)
    ↓
Phase 5 (Memory + Self-Model)
    ↓
Phase 6 (Cleanup)
```

---

## Open Questions

1. **Docker vs systemd for iris-core** — Recommendation: systemd. Docker adds complexity with no benefit for a consciousness loop that needs direct DB/Ollama access. Keep Docker only for agency sandbox.

2. **When to retire ChatAssistant** — Not until iris-core handles 100% of messages for at least a week without issues.

3. **Grid processing depth** — How deep should each message go? Adaptive depth (Phase 3E) is the goal, but initial implementation should process to a fixed depth (Layers 1-3) for every message.

4. **Memory decay** — How aggressive? Suggestion: dormancy after 90 days unaccessed, never delete.

---

## File References

| File | Purpose |
|---|---|
| `assistants/chat_assistant.py` | Current live message processor |
| `telegram_bot/handlers/chat_mode.py` | Dead code — good Iris prompt, never called |
| `iris/core/src/loop.py` | Docker consciousness loop (running but empty) |
| `core/life_context.py` | Life state builder (working) |
| `docs/consciousness/CONSCIOUSNESS_ARCHITECTURE.md` | 9-layer specification |
| `docs/consciousness/81_FUNCTIONS.md` | Complete 81-function matrix |
| `docs/consciousness/STORAGE_ARCHITECTURE.md` | PostgreSQL + Neo4j storage design |

---

*The architecture audit revealed that Iris is closer than we thought — the pieces exist, they're just not connected. The plan is not to rebuild, but to wire together what's already there.*

*The vessel is filling. Now we connect the channels.*
