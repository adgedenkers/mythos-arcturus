# Mythos System Architecture

> **Version:** 2.3.0
> **Last Updated:** 2026-01-27
> **Host:** arcturus (Ubuntu 24.04)

---

## 📖 Document Purpose

**ARCHITECTURE.md is the stable system reference.** It documents what actually exists and works.

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `TODO.md` | What we're trying to do | Every work session |
| `ARCHITECTURE.md` | What actually exists and works | Only at stable milestones |
| `ARCTURIAN_GRID.md` | Complete grid specification | When grid design changes |

---

## 🚨 Core Design Principles

### Principle 1: Everything Goes Through the API Gateway

**This is non-negotiable.** All message processing, regardless of mode, MUST flow through the FastAPI gateway (`/message` endpoint). Never bypass the API to call Ollama or other services directly from the Telegram bot.

```
✅ CORRECT:
Telegram Bot → API Gateway (/message) → Assistant → Ollama/Neo4j/etc.

❌ WRONG:
Telegram Bot → Ollama directly (bypasses logging, context, grid analysis)
```

**Why this matters:**
- **Grid Analysis:** Every exchange gets consciousness mapping
- **Logging & Auditing:** All interactions recorded in one place
- **Context Management:** Conversation history, user state, session tracking
- **Future Extensibility:** RAG, tool use, memory retrieval, guardrails

### Principle 2: Assistants Are Stateless Classes

Each assistant (ChatAssistant, DatabaseManager, etc.) is instantiated once at API startup. User context is passed per-request via `set_user()`. Conversation context is maintained in-memory keyed by user UUID.

### Principle 3: Workers Handle Async/Heavy Tasks

Long-running or background tasks (grid analysis, vision, embeddings, summaries) go through Redis streams to workers. The API dispatches and returns immediately.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 ARCTURUS SERVER                                      │
│                             (Ubuntu 24.04 / x86_64)                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌──────────────┐                                                                  │
│   │   Telegram   │                                                                  │
│   │     Bot      │─────────┐                                                        │
│   └──────────────┘         │                                                        │
│                            ▼                                                        │
│   ┌──────────────┐   ┌─────────────────────────────────────────────┐               │
│   │  Future Web  │   │              API GATEWAY                    │               │
│   │   Clients    │──▶│           FastAPI :8000                     │               │
│   └──────────────┘   │                                             │               │
│                      │  /message ──▶ Routes to Assistants          │               │
│   ┌──────────────┐   │               ├─► Grid dispatch (async)     │               │
│   │  API Users   │──▶│  /user    ──▶ User lookup                   │               │
│   └──────────────┘   │  /chat/*  ──▶ Chat context management       │               │
│                      └───────────────────┬─────────────────────────┘               │
│                                          │                                          │
│            ┌─────────────────────────────┼─────────────────────────┐               │
│            │                             │                         │                │
│            ▼                             ▼                         ▼                │
│   ┌─────────────────┐   ┌─────────────────────┐                                    │
│   │ ChatAssistant   │   │  DatabaseManager    │                                    │
│   │ • General chat  │   │ • NL → Cypher/SQL   │                                    │
│   │ • Context mgmt  │   │ • Query execution   │                                    │
│   │ • Grid dispatch │   │                     │                                    │
│   └────────┬────────┘   └──────────┬──────────┘                                    │
│            │                       │                                                │
│            └───────────┬───────────┘                                                │
│                        ▼                                                            │
│            ┌───────────────────────┐                                               │
│            │    OLLAMA (LLM)       │                                               │
│            │    localhost:11434    │                                               │
│            └───────────────────────┘                                               │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐          │
│   │                     REDIS STREAMS (Job Queues)                       │          │
│   │                                                                      │          │
│   │   mythos:assignments:grid_analysis ──► Grid Worker (active)         │          │
│   │   mythos:assignments:vision ─────────► Vision Worker (available)    │          │
│   │   mythos:assignments:embedding ──────► Embedding Worker (planned)   │          │
│   │   mythos:assignments:entity ─────────► Entity Worker (planned)      │          │
│   └─────────────────────────────────────────────────────────────────────┘          │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐          │
│   │                           DATA LAYER                                 │          │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │          │
│   │  │PostgreSQL│  │  Neo4j   │  │  Redis   │  │  Qdrant  │            │          │
│   │  │ :5432    │  │  :7687   │  │  :6379   │  │  :6333   │            │          │
│   │  │timeseries│  │  graph   │  │  queues  │  │ vectors  │            │          │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │          │
│   └─────────────────────────────────────────────────────────────────────┘          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔮 Arcturian Grid System

The Grid is a 9-node consciousness processing framework that analyzes every conversation exchange. It maps discussions to archetypal domains and tracks patterns over time.

**Full specification:** See `/opt/mythos/docs/ARCTURIAN_GRID.md`

### The 9 Nodes (Summary)

| Symbol | Node | Domain |
|--------|------|--------|
| ⛰️ | **ANCHOR** | Matter, body, physical, infrastructure |
| 🌊 | **ECHO** | Memory, ancestors, identity, timelines |
| 🔥 | **BEACON** | Value, finance, manifestation, direction |
| 💨 | **SYNTH** | Systems, logic, code, integration |
| ⏳ | **NEXUS** | Time, decisions, convergence, routing |
| 🪞 | **MIRROR** | Emotions, psyche, shadow, reflection |
| 🔣 | **GLYPH** | Symbols, rituals, encoding, artifacts |
| 💗 | **HARMONIA** | Relationships, heart, balance, connection |
| 🚪 | **GATEWAY** | Dreams, spiritual, transitions, passage |

### Current Implementation

**Working (Basic):**
- Single LLM call scores all 9 nodes (0-100)
- PostgreSQL: `grid_activation_timeseries` stores scores
- Neo4j: Exchange nodes with grid scores and basic relationships
- Entities: Basic list extraction (people, concepts, systems, themes)

**Not Yet Implemented:**
- Two-phase processing (8 parallel + GATEWAY last)
- Per-node extraction with 5 layers
- Entity merging across nodes
- Dual scoring (confidence + strength)
- Running totals on conversations

### Data Flow

```
User sends message
        │
        ▼
ChatAssistant.query()
        │
        ├─► Returns response to user immediately
        │
        └─► Dispatches to Redis: mythos:assignments:grid_analysis
                    │
                    ▼
            Grid Worker picks up (async)
                    │
                    ▼
            LLM analyzes exchange
                    │
                    ├─► PostgreSQL: grid_activation_timeseries
                    │
                    └─► Neo4j: Exchange node + relationships
```

### Example Analysis

```
User: "Why are graph databases helpful?"

Grid Result:
  dominant_node: "synth" (85)
  secondary_node: "nexus" (55)
  total_activation: 330
  emotional_tone: "curious"
  themes: ["databases", "architecture"]
  summary: "Discussion of graph database benefits for interconnected data"
```

### Querying Grid Data

**PostgreSQL (Trends):**
```sql
SELECT dominant_node, COUNT(*) 
FROM grid_activation_timeseries 
WHERE user_uuid = 'xxx' 
GROUP BY dominant_node 
ORDER BY count DESC;
```

**Neo4j (Patterns):**
```cypher
MATCH (e:Exchange)-[:ACTIVATED]->(g:GridNode {name: 'gateway'})
WHERE e.gateway_score > 70
RETURN e.summary, e.timestamp
ORDER BY e.timestamp DESC
```

---

## Message Flow (Critical Path)

```
1. User sends message via Telegram
                │
                ▼
2. Bot receives message (mythos_bot.py)
   - Validates user session
   - Determines mode (chat/db/sell/etc.)
                │
                ▼
3. Bot calls API Gateway
   POST /message {user_id, message, mode, model_preference}
                │
                ▼
4. API routes to Assistant
   - chat → ChatAssistant.query()
   - db   → DatabaseManager.query()
                │
                ▼
5. Assistant processes
   - Builds context
   - Calls Ollama
   - Returns response
   - Dispatches to Grid Worker (async)
                │
                ▼
6. API returns response to Bot
                │
                ▼
7. Bot sends response to user
                │
                ▼
8. (Background) Grid Worker analyzes
   - Stores to PostgreSQL + Neo4j
```

---

## Core Subsystems

### 1. Telegram Bot (`mythos-bot.service`)

**Role:** Thin client. Handles Telegram protocol, routes to API.

**Modes:**
| Mode | Description | Status |
|------|-------------|--------|
| `chat` | General conversation (default) | ✅ Working |
| `db` | Natural language database queries | ✅ Working |
| `sell` | Item intake via photos | ✅ Working |
| `seraphe` | Cosmology assistant | 📋 Planned |
| `genealogy` | Bloodline research | 📋 Planned |

**Commands:** `/mode`, `/model`, `/status`, `/clear`, `/help`

### 2. API Gateway (`mythos-api.service`)

**Role:** Central routing. ALL message processing goes through here.

**Key Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/message` | POST | Routes to assistants, triggers grid |
| `/user/{id}` | GET | User lookup |
| `/chat/clear/{id}` | POST | Clear context |
| `/chat/stats/{id}` | GET | Context statistics |

### 3. Assistants (`/opt/mythos/assistants/`)

| Assistant | Status | Grid Dispatch |
|-----------|--------|---------------|
| `ChatAssistant` | ✅ Active | ✅ Yes |
| `DatabaseManager` | ✅ Active | No |
| `SerapheAssistant` | 📋 Planned | Planned |
| `GenealogyAssistant` | 📋 Planned | Planned |

### 4. Workers (`/opt/mythos/workers/`)

| Worker | Stream | Status |
|--------|--------|--------|
| Grid | `grid_analysis` | ✅ Active |
| Vision | `vision` | ✅ Available |
| Embedding | `embedding` | 📋 Planned |
| Entity | `entity` | 📋 Planned |
| Temporal | `temporal` | 📋 Planned |
| Summary | `summary_rebuild` | 📋 Planned |

---

## Services

| Service | Port | Status |
|---------|------|--------|
| `mythos-api.service` | 8000 | ✅ Active |
| `mythos-bot.service` | - | ✅ Active |
| `mythos-worker-grid.service` | - | ✅ Active |
| `mythos-patch-monitor.service` | - | ✅ Active |
| `postgresql` | 5432 | ✅ Active |
| `neo4j` | 7687 | ✅ Active |
| `redis` | 6379 | ✅ Active |
| `ollama` | 11434 | ✅ Active |

---

## Databases

### PostgreSQL: `mythos`

**Tables:**
- `users` - User accounts
- `chat_messages` - Message history
- `grid_activation_timeseries` - Grid scores per exchange
- `emotional_state_timeseries` - Emotional tracking
- `accounts`, `transactions`, `categories` - Finance
- `items_for_sale`, `item_images`, `sales` - Sales

### Neo4j: `mythos`

**Node Labels:**
- `Soul`, `Person`, `Incarnation` - Identity
- `Exchange`, `Conversation` - Interactions
- `GridNode` - The 9 grid nodes
- `Entity`, `Theme`, `Symbol` - Extracted content

**Key Relationships:**
- `(Soul)-[:HAD_EXCHANGE]->(Exchange)`
- `(Exchange)-[:ACTIVATED]->(GridNode)`
- `(Exchange)-[:MENTIONS]->(Entity)`
- `(Exchange)-[:HAS_THEME]->(Theme)`

---

## Directory Structure

```
/opt/mythos/
├── docs/
│   ├── TODO.md              # Living work journal
│   ├── ARCHITECTURE.md      # This file
│   └── ARCTURIAN_GRID.md    # Grid specification
├── api/
│   └── main.py              # FastAPI gateway
├── assistants/
│   ├── chat_assistant.py    # Chat + grid dispatch
│   └── db_manager.py        # Database queries
├── telegram_bot/
│   ├── mythos_bot.py        # Bot entry point
│   └── handlers/            # Command handlers
├── workers/
│   ├── worker.py            # Worker framework
│   └── grid_worker.py       # Grid analysis
├── vision/                  # Vision module
├── finance/                 # Finance system
└── patches/                 # Patch system
```

---

## Ollama Models

| Model | Size | Purpose |
|-------|------|---------|
| `qwen2.5:32b` | 19GB | Primary (chat, db, grid) |
| `llava:34b` | 20GB | Vision |
| `llama3.2:3b` | 2GB | Fast responses |

---

## Common Commands

```bash
# Services
sudo systemctl status mythos-api.service
sudo systemctl restart mythos-worker-grid.service
journalctl -u mythos-worker-grid.service -f

# Redis
redis-cli XLEN mythos:assignments:grid_analysis

# Grid data
sudo -u postgres psql -d mythos -c \
  "SELECT * FROM grid_activation_timeseries ORDER BY time DESC LIMIT 5"

cypher-shell -u neo4j -p '<password>' \
  "MATCH (e:Exchange) RETURN e ORDER BY e.timestamp DESC LIMIT 5"
```

---

*This document reflects the deployed state of Mythos as of 2026-01-27.*
