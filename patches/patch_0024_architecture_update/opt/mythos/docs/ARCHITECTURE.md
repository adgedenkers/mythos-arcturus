# Mythos System Architecture

> **Version:** 2.1.0
> **Last Updated:** 2026-01-27
> **Host:** arcturus (Ubuntu 24.04)

---

## 📖 Document Purpose

**ARCHITECTURE.md is the stable system reference.** It documents what actually exists and works.

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `TODO.md` | What we're trying to do | Every work session |
| `ARCHITECTURE.md` | What actually exists and works | Only at stable milestones |

---

## 🚨 Core Design Principles

### Principle 1: Everything Goes Through the API Gateway

**This is non-negotiable.** All message processing, regardless of mode, MUST flow through the FastAPI gateway (`/message` endpoint). Never bypass the API to call Ollama or other services directly from the Telegram bot.

```
✅ CORRECT:
Telegram Bot → API Gateway (/message) → Assistant → Ollama/Neo4j/etc.

❌ WRONG:
Telegram Bot → Ollama directly (bypasses logging, context, future features)
```

**Why this matters:**
- **Logging & Auditing:** All interactions recorded in one place
- **Context Management:** Conversation history, user state, session tracking
- **Future Extensibility:** RAG, tool use, memory retrieval, guardrails
- **Consistency:** Same code path for all clients (Telegram, web, API consumers)

### Principle 2: Assistants Are Stateless Classes

Each assistant (ChatAssistant, DatabaseManager, etc.) is instantiated once at API startup. User context is passed per-request via `set_user()`. Conversation context is maintained in-memory keyed by user UUID.

### Principle 3: Workers Handle Async/Heavy Tasks

Long-running or background tasks (vision analysis, embeddings, summaries) go through Redis streams to workers. The API dispatches and returns immediately.

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
│   │              │         │                                                        │
│   └──────────────┘         │                                                        │
│                            ▼                                                        │
│   ┌──────────────┐   ┌─────────────────────────────────────────────┐               │
│   │  Future Web  │   │              API GATEWAY                    │               │
│   │   Clients    │──▶│           FastAPI :8000                     │               │
│   └──────────────┘   │                                             │               │
│                      │  /message ──▶ Routes to Assistants          │               │
│   ┌──────────────┐   │  /user    ──▶ User lookup                   │               │
│   │  API Users   │──▶│  /sales   ──▶ Sales endpoints               │               │
│   └──────────────┘   │  /chat/*  ──▶ Chat context management       │               │
│                      └───────────────────┬─────────────────────────┘               │
│                                          │                                          │
│            ┌─────────────────────────────┼─────────────────────────┐               │
│            │                             │                         │                │
│            ▼                             ▼                         ▼                │
│   ┌─────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐          │
│   │ ChatAssistant   │   │  DatabaseManager    │   │  (Future Assistants)│          │
│   │                 │   │                     │   │                     │          │
│   │ • General chat  │   │ • NL → Cypher/SQL   │   │ • SerapheAssistant  │          │
│   │ • Context mgmt  │   │ • Query execution   │   │ • GenealogyAssistant│          │
│   │ • Model routing │   │ • Result formatting │   │ • etc.              │          │
│   └────────┬────────┘   └──────────┬──────────┘   └─────────────────────┘          │
│            │                       │                                                │
│            └───────────┬───────────┘                                                │
│                        ▼                                                            │
│            ┌───────────────────────┐                                               │
│            │    OLLAMA (LLM)       │                                               │
│            │    localhost:11434    │                                               │
│            └───────────────────────┘                                               │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐          │
│   │                     ORCHESTRATOR (Redis Streams)                     │          │
│   │                                                                      │          │
│   │   For async/heavy tasks only:                                       │          │
│   │   • Vision analysis (photos)                                        │          │
│   │   • Embedding generation                                            │          │
│   │   • Summary rebuilds                                                │          │
│   │   • Entity resolution                                               │          │
│   └─────────────────────────────────────────────────────────────────────┘          │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐          │
│   │                           DATA LAYER                                 │          │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │          │
│   │  │PostgreSQL│  │  Neo4j   │  │  Redis   │  │  Qdrant  │            │          │
│   │  │ :5432    │  │  :7687   │  │  :6379   │  │  :6333   │            │          │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │          │
│   └─────────────────────────────────────────────────────────────────────┘          │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Message Flow (Critical Path)

Every user message follows this exact path:

```
1. User sends message via Telegram
                │
                ▼
2. Bot receives message (mythos_bot.py)
   - Validates user session
   - Determines mode (chat/db/sell/etc.)
   - Does NOT process LLM requests directly
                │
                ▼
3. Bot calls API Gateway
   POST /message
   {
     "user_id": "123456",
     "message": "why is the sky blue?",
     "mode": "chat",
     "model_preference": "auto"
   }
                │
                ▼
4. API Gateway routes to Assistant
   - chat → ChatAssistant.query()
   - db   → DatabaseManager.query()
   - etc.
                │
                ▼
5. Assistant processes request
   - Builds context (conversation history)
   - Calls Ollama
   - Returns response
                │
                ▼
6. API returns response to Bot
                │
                ▼
7. Bot sends response to user via Telegram
```

**The bot is a thin client.** It handles Telegram-specific concerns (photos, commands, session state) but delegates all LLM processing to the API.

---

## Core Subsystems

### 1. Telegram Bot (`mythos-bot.service`)

**Role:** Thin client / interface layer. Handles Telegram protocol, routes to API.

**Modes:**
| Mode | Description | API Route |
|------|-------------|-----------|
| `chat` | General conversation (default) | `/message` → ChatAssistant |
| `db` | Natural language database queries | `/message` → DatabaseManager |
| `sell` | Item intake via photos | Local + Vision Worker |
| `seraphe` | Cosmology assistant | `/message` → (planned) |
| `genealogy` | Bloodline research | `/message` → (planned) |

**Key Commands:**
- `/mode <mode>` - Switch modes
- `/model auto|fast|deep` - Select LLM routing
- `/status` - Current mode, context, activity
- `/clear` - Reset chat context
- `/help` - Command reference

**Files:**
- `/opt/mythos/telegram_bot/mythos_bot.py` - Main entry point
- `/opt/mythos/telegram_bot/handlers/` - Command handlers

---

### 2. API Gateway (`mythos-api.service`)

**Role:** Central routing layer. ALL message processing goes through here.

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status, assistant availability |
| `/health` | GET | Health check |
| `/message` | POST | **Primary endpoint** - routes to assistants |
| `/user/{id}` | GET | User lookup |
| `/chat/clear/{id}` | POST | Clear chat context |
| `/chat/stats/{id}` | GET | Chat context statistics |
| `/sales/*` | Various | Sales intake API |

**Authentication:** API key via `X-API-Key` header

**Files:**
- `/opt/mythos/api/main.py` - FastAPI app + routing logic
- `/opt/mythos/api/orchestrator.py` - Redis stream dispatcher
- `/opt/mythos/api/routes/sales.py` - Sales endpoints

---

### 3. Assistants (`/opt/mythos/assistants/`)

**Role:** Mode-specific processing logic. Called by API gateway.

| Assistant | File | Purpose |
|-----------|------|---------|
| `ChatAssistant` | `chat_assistant.py` | General conversation, context management |
| `DatabaseManager` | `db_manager.py` | NL → Cypher/SQL, query execution |
| `SerapheAssistant` | (planned) | Cosmology, symbolism, spiritual guidance |
| `GenealogyAssistant` | (planned) | Bloodline tracing, family trees |

**Pattern:**
```python
class SomeAssistant:
    def __init__(self):
        # Initialize connections, load prompts
        
    def set_user(self, user_info: dict):
        # Set current user context
        
    def query(self, message: str, **kwargs) -> str:
        # Process message, return response
```

---

### 4. Worker System (Async Tasks)

**Role:** Handle long-running or background tasks via Redis streams.

**When to use workers vs. direct calls:**
- **Workers:** Vision analysis, embeddings, summaries (seconds to minutes)
- **Direct:** Chat, DB queries (sub-second to seconds)

**Workers:**
| Worker | Stream | Function |
|--------|--------|----------|
| `vision` | `mythos:assignments:vision` | Photo analysis via llava |
| `embedding` | `mythos:assignments:embedding` | Text → vector |
| `grid` | `mythos:assignments:grid_analysis` | 9-node consciousness |
| `entity` | `mythos:assignments:entity` | Entity resolution |
| `temporal` | `mythos:assignments:temporal` | Date/time extraction |
| `summary` | `mythos:assignments:summary_rebuild` | Conversation summaries |

**Files:**
- `/opt/mythos/workers/worker.py` - Worker framework
- `/opt/mythos/workers/<type>_worker.py` - Individual workers
- `/opt/mythos/api/orchestrator.py` - Dispatcher

---

### 5. Vision System

Photo analysis using Ollama vision models.

**Flow:**
```
Photo → Base64 encode → Ollama llava:34b → JSON extraction → Database
```

**Files:**
- `/opt/mythos/vision/core.py` - `analyze_image()`
- `/opt/mythos/vision/config.py` - Configuration
- `/opt/mythos/vision/prompts/` - LLM prompts

---

### 6. Sales Intake System

Photo-to-marketplace pipeline for reselling items.

**Flow:**
```
Telegram Photo (x3) → Vision Worker → PostgreSQL → /export → FB Marketplace
```

**Files:**
- `/opt/mythos/telegram_bot/handlers/sell_mode.py` - Telegram sell mode
- `/opt/mythos/telegram_bot/handlers/export_handler.py` - Marketplace export

---

### 7. Finance System

Bank transaction import and categorization.

**Files:**
- `/opt/mythos/finance/parsers.py` - Bank-specific parsers
- `/opt/mythos/finance/import_transactions.py` - Import CLI
- `/opt/mythos/finance/reports.py` - Report generation

---

### 8. Patch System

Automated deployment with Git versioning.

**Flow:**
```
Claude creates patch.zip → User downloads → ~/Downloads → Auto-detect → Git tag → Install
```

**Files:**
- `/opt/mythos/mythos_patch_monitor.py` - File watcher daemon
- `/opt/mythos/telegram_bot/handlers/patch_handlers.py` - Telegram commands

---

## Directory Structure

```
/opt/mythos/
├── .env                          # All secrets and configuration
├── .venv/                        # Python virtual environment
├── .git/                         # Git repository
│
├── docs/                         # Documentation
│   ├── TODO.md                   # Living work journal
│   └── ARCHITECTURE.md           # This file
│
├── api/                          # FastAPI service (CENTRAL HUB)
│   ├── main.py                   # App entry + routing
│   ├── orchestrator.py           # Redis dispatcher
│   └── routes/                   # API routes
│
├── assistants/                   # LLM assistants (called by API)
│   ├── chat_assistant.py         # General chat
│   └── db_manager.py             # Database queries
│
├── telegram_bot/                 # Telegram bot (thin client)
│   ├── mythos_bot.py             # Main entry point
│   └── handlers/                 # Command handlers
│
├── workers/                      # Async workers
│   ├── worker.py                 # Framework
│   └── *_worker.py               # Individual workers
│
├── vision/                       # Vision module
├── finance/                      # Finance system
├── graph_logging/                # Neo4j event logging
├── intake/                       # Sales intake staging
├── assets/                       # Permanent asset storage
└── patches/                      # Patch system
```

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| `mythos-api.service` | 8000 | **API Gateway** (central hub) |
| `mythos-bot.service` | - | Telegram bot |
| `mythos-patch-monitor.service` | - | Patch file watcher |
| `mythos-worker-*.service` | - | Async workers (6 total) |
| `postgresql` | 5432 | Primary database |
| `neo4j` | 7474/7687 | Graph database |
| `redis` | 6379 | Job queues |
| `ollama` | 11434 | Local LLM |

---

## Databases

### PostgreSQL: `mythos`

**Core Tables:** `users`, `chat_messages`, `media_files`
**Finance Tables:** `accounts`, `transactions`, `categories`, `category_mappings`
**Sales Tables:** `items_for_sale`, `item_images`, `sales`

### Neo4j: `mythos`

**Node Labels:** `Soul`, `Person`, `Incarnation`, `Conversation`, `Exchange`, etc.
**Key Relationships:** `CURRENTLY_EMBODIED_AS`, `PARENT_OF`, `SPOUSE_OF`, etc.

### Redis Streams

Job queues for async workers: `mythos:assignments:<type>`

---

## Ollama Models

| Model | Size | Purpose |
|-------|------|---------|
| `qwen2.5:32b` | 19GB | Primary text (chat, db mode) |
| `llava:34b` | 20GB | Vision analysis |
| `llama3.2:3b` | 2GB | Fast responses |
| `deepseek-coder-v2:16b` | 8.9GB | Code generation |

---

## Common Commands

```bash
# Services
sudo systemctl status mythos-api.service
sudo systemctl restart mythos-api.service
sudo systemctl restart mythos-bot.service
journalctl -u mythos-api.service -f

# Test API
curl http://localhost:8000/
curl http://localhost:8000/health

# Databases
sudo -u postgres psql -d mythos
cypher-shell -u neo4j

# Ollama
ollama list
curl http://localhost:11434/api/tags
```

---

## Adding a New Assistant

1. Create `/opt/mythos/assistants/my_assistant.py`:
```python
class MyAssistant:
    def __init__(self):
        self.ollama = Client(host=os.getenv('OLLAMA_HOST'))
        
    def set_user(self, user_info):
        self.current_user = user_info
        
    def query(self, message: str) -> str:
        # Process and return response
```

2. Import and initialize in `/opt/mythos/api/main.py`:
```python
from my_assistant import MyAssistant
my_assistant_instance = MyAssistant()
```

3. Add routing in `/message` endpoint:
```python
elif request.mode == "mymode" and my_assistant_instance:
    my_assistant_instance.set_user(user)
    response_text = my_assistant_instance.query(request.message)
```

4. Add mode to bot's valid modes list in `mythos_bot.py`

---

*This document reflects the actual deployed state of the Mythos system as of 2026-01-27.*
