# Mythos System Architecture

> **Version:** 2.0.0
> **Last Updated:** 2026-01-24
> **Host:** arcturus (Ubuntu 24.04)

---

## 📖 Document Purpose

**ARCHITECTURE.md is the stable system reference.** It documents what actually exists and works.

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `TODO.md` | What we're trying to do | Every work session |
| `ARCHITECTURE.md` | What actually exists and works | Only at stable milestones |

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                 ARCTURUS SERVER                                      │
│                             (Ubuntu 24.04 / x86_64)                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐                      │
│   │   Telegram   │      │    FastAPI   │      │    Patch     │                      │
│   │     Bot      │─────▶│   Gateway    │      │   Monitor    │                      │
│   │              │      │   :8000      │      │              │                      │
│   └──────┬───────┘      └──────┬───────┘      └──────────────┘                      │
│          │                     │                                                     │
│          │    ┌────────────────┴────────────────┐                                   │
│          │    │          ORCHESTRATOR           │                                   │
│          │    │     (Redis Stream Dispatch)     │                                   │
│          │    └────────────────┬────────────────┘                                   │
│          │                     │                                                     │
│          │    ┌────────────────┼────────────────┐                                   │
│          │    │                │                │                                    │
│          ▼    ▼                ▼                ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐                │
│   │                      WORKER POOL (6 workers)                   │                │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │                │
│   │  │ Vision  │ │Embedding│ │  Grid   │ │ Entity  │ │Temporal │  │                │
│   │  │ Worker  │ │ Worker  │ │ Worker  │ │ Worker  │ │ Worker  │  │                │
│   │  │ (llava) │ │(MiniLM) │ │ (qwen)  │ │         │ │         │  │                │
│   │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │                │
│   │       │           │           │           │           │       │                │
│   └───────┼───────────┼───────────┼───────────┼───────────┼───────┘                │
│           │           │           │           │           │                         │
│           └───────────┴─────┬─────┴───────────┴───────────┘                         │
│                             │                                                        │
│   ┌─────────────────────────┼─────────────────────────────────┐                     │
│   │                    DATA LAYER                              │                     │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │                     │
│   │  │PostgreSQL│  │  Neo4j   │  │  Redis   │  │  Qdrant  │   │                     │
│   │  │ :5432    │  │  :7687   │  │  :6379   │  │  :6333   │   │                     │
│   │  │ mythos   │  │  mythos  │  │ streams  │  │embeddings│   │                     │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │                     │
│   └────────────────────────────────────────────────────────────┘                     │
│                                                                                      │
│   ┌──────────────────────────────────────────┐                                      │
│   │              OLLAMA (Local LLM)          │                                      │
│   │  • qwen2.5:32b    (text, 19GB)           │                                      │
│   │  • llava:34b      (vision, 20GB)         │                                      │
│   │  • deepseek-coder-v2:16b (code, 8.9GB)   │                                      │
│   │  • llama3.2:3b    (fast, 2GB)            │                                      │
│   └──────────────────────────────────────────┘                                      │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Subsystems

### 1. Telegram Bot (`mythos-bot.service`)

Multi-mode conversational interface with photo handling.

**Modes:**
| Mode | Description | Handler |
|------|-------------|---------|
| `db` | Natural language database queries | `db_manager.py` → Ollama → Neo4j/Postgres |
| `seraphe` | Cosmology assistant | Planned |
| `genealogy` | Bloodline research | Planned |
| `chat` | General conversation | Ollama direct |
| `sell` | Item intake via photos | `sell_mode.py` → Vision → DB |

**Key Commands:**
- `/mode <mode>` - Switch modes
- `/model auto|fast|deep` - Select LLM routing
- `/convo` / `/endconvo` - Tracked conversations
- `/inventory` - View items for sale
- `/export` - Generate FB Marketplace listings
- `/patch_status` - System patch status

**Files:**
- `/opt/mythos/telegram_bot/mythos_bot.py` - Main entry point
- `/opt/mythos/telegram_bot/handlers/` - Command handlers

---

### 2. FastAPI Gateway (`mythos-api.service`)

REST API for internal service communication.

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service status |
| `/health` | GET | Health check |
| `/message` | POST | Process message through assistant |
| `/user/{id}` | GET | Get user info |
| `/media/upload` | POST | Register uploaded media |
| `/sales/*` | Various | Sales intake API |

**Authentication:** API key via `X-API-Key` header

**Files:**
- `/opt/mythos/api/main.py` - FastAPI app
- `/opt/mythos/api/orchestrator.py` - Redis stream dispatcher
- `/opt/mythos/api/routes/sales.py` - Sales endpoints

---

### 3. Worker System

Async processing via Redis streams with dedicated systemd services.

**Architecture:**
```
Orchestrator.dispatch(type, payload)
        │
        ▼
Redis Stream (mythos:assignments:<type>)
        │
        ▼
Worker (mythos-worker-<type>.service)
        │
        ▼
Result → PostgreSQL/Neo4j/Qdrant
```

**Workers:**

| Worker | Stream | Function | Output |
|--------|--------|----------|--------|
| `vision` | `mythos:assignments:vision` | Analyze photos via llava | PostgreSQL `media_files` |
| `embedding` | `mythos:assignments:embedding` | Text → vector (MiniLM-L6-v2) | Qdrant `text_embeddings` |
| `grid` | `mythos:assignments:grid_analysis` | 9-node consciousness analysis | PostgreSQL timeseries |
| `entity` | `mythos:assignments:entity` | Entity resolution to canonical | Neo4j nodes |
| `temporal` | `mythos:assignments:temporal` | Date/time extraction | PostgreSQL + astro links |
| `summary` | `mythos:assignments:summary_rebuild` | Conversation summarization | PostgreSQL |

**Files:**
- `/opt/mythos/workers/worker.py` - Worker framework
- `/opt/mythos/workers/<type>_worker.py` - Individual workers
- `/opt/mythos/api/orchestrator.py` - Dispatcher

---

### 4. Vision System

Photo analysis using Ollama vision models.

**Flow:**
```
Photo → Base64 encode → Ollama llava:34b → JSON extraction → Database
```

**Capabilities:**
- Sales item analysis (brand, size, condition, price estimation)
- General image description
- Symbol/sacred geometry detection
- Text extraction (OCR-like)

**Configuration:**
```python
# /opt/mythos/vision/config.py
VisionConfig:
    ollama_host: "http://localhost:11434"
    ollama_model: "llava:34b"
    timeout: 120  # seconds
```

**Prompts:** `/opt/mythos/vision/prompts/`
- `sales.py` - Item analysis for marketplace
- `symbols.py` - Sacred geometry detection
- `documents.py` - Document analysis
- `journal.py` - Journal entry analysis

**Files:**
- `/opt/mythos/vision/core.py` - `analyze_image()` and `analyze_image_async()`
- `/opt/mythos/vision/config.py` - Configuration
- `/opt/mythos/vision/prompts/` - Prompt templates

---

### 5. Sales Intake System

Photo-to-marketplace pipeline for reselling items.

**Flow:**
```
Telegram Photo (x3)
        │
        ▼
/opt/mythos/intake/pending/<uuid>/
        │
        ▼
Vision Analysis (llava:34b + sales.ITEM_ANALYSIS prompt)
        │
        ▼
PostgreSQL: items_for_sale + item_images
        │
        ▼
/opt/mythos/assets/images/<sha256-shard>/<sha256>.jpeg
        │
        ▼
/export → FB Marketplace formatted listing
```

**Database Tables:**
- `items_for_sale` - Item metadata, pricing, status
- `item_images` - Photo records with SHA256 asset paths

**Statuses:** `available` → `listed` → `sold`

**Files:**
- `/opt/mythos/telegram_bot/handlers/sell_mode.py` - Telegram sell mode
- `/opt/mythos/telegram_bot/handlers/export_handler.py` - Marketplace export
- `/opt/mythos/vision/prompts/sales.py` - Analysis prompts

---

### 6. Finance System

Bank transaction import and categorization.

**Supported Banks:**
- USAA (CSV with categories)
- Sunmark Credit Union (CSV with memo field)

**Flow:**
```
Bank CSV → Parser → Category Mapping → PostgreSQL transactions
```

**Features:**
- Auto-detection of bank format
- Duplicate detection via hash
- Pattern-based auto-categorization (199+ mappings)
- CLI reports

**Files:**
- `/opt/mythos/finance/parsers.py` - Bank-specific parsers
- `/opt/mythos/finance/import_transactions.py` - Import CLI
- `/opt/mythos/finance/reports.py` - Report generation

**Usage:**
```bash
cd /opt/mythos/finance
python import_transactions.py accounts/usaa_2026_01.csv --account-id 2 --dry-run
python reports.py summary
```

---

### 7. Graph Logging & Diagnostics

System monitoring with causal event tracking in Neo4j.

**Components:**
- `EventLogger` - Writes events to Neo4j with auto-causality linking
- `Diagnostics` - Query interface for AI-powered troubleshooting
- `system_monitor.py` - Collects metrics (CPU, memory, disk, processes)

**Event Types:**
- `high_cpu`, `high_memory`, `low_disk`
- `service_failure`, `service_stopped`
- `connection_error`, `backup_failed`

**LLM Interface:**
```bash
mythos-ask "why did neo4j backup fail?"
mythos-ask "what's using memory?"
```

**Files:**
- `/opt/mythos/graph_logging/src/event_logger.py` - Event logging
- `/opt/mythos/graph_logging/src/diagnostics.py` - Query interface
- `/opt/mythos/llm_diagnostics/src/mythos_ask.py` - CLI tool

---

### 8. Database Manager (db mode)

Natural language → Cypher/SQL query generation.

**Flow:**
```
User question → Ollama (qwen2.5:32b) → Cypher query → Neo4j → Formatted response
```

**Capabilities:**
- Query souls, persons, incarnations, lineages
- Genealogy traversal (PARENT_OF, SPOUSE_OF)
- Context-aware pronoun resolution

**Files:**
- `/opt/mythos/assistants/db_manager.py` - Main class
- System prompt loaded from `~/main-vault/systems/arcturus/prompts/db_mode_prompt.md`

---

### 9. Patch System

Automated deployment with Git versioning.

**Flow:**
```
Claude creates patch_NNNN_description.zip
        │
        ▼
User downloads → copies to ~/Downloads on Arcturus
        │
        ▼
mythos-patch-monitor.service detects file
        │
        ▼
Git tag (pre-patch) → Extract → Commit → Version tag → Push → install.sh
        │
        ▼
Archive to /opt/mythos/patches/archive/
```

**Commands:**
- `/patch_status` - Current version and recent activity
- `/patch_list` - Available patches
- `/patch_apply <name>` - Manual apply
- `/patch_rollback` - Rollback options

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
├── telegram_bot/                 # Telegram bot
│   ├── mythos_bot.py             # Main entry point
│   └── handlers/                 # Command handlers
│       ├── sell_mode.py          # Photo intake for sales
│       ├── export_handler.py     # Marketplace export
│       └── patch_handlers.py     # Patch management
│
├── api/                          # FastAPI service
│   ├── main.py                   # App entry point
│   ├── orchestrator.py           # Redis dispatcher
│   └── routes/                   # API routes
│
├── workers/                      # Async workers
│   ├── worker.py                 # Framework
│   ├── vision_worker.py          # Photo analysis
│   ├── embedding_worker.py       # Text embeddings
│   ├── grid_worker.py            # 9-node analysis
│   ├── entity_worker.py          # Entity resolution
│   ├── temporal_worker.py        # Date extraction
│   └── summary_worker.py         # Summarization
│
├── vision/                       # Vision module
│   ├── core.py                   # analyze_image()
│   ├── config.py                 # Configuration
│   └── prompts/                  # LLM prompts
│       ├── sales.py              # Item analysis
│       ├── symbols.py            # Sacred geometry
│       └── ...
│
├── finance/                      # Finance system
│   ├── parsers.py                # Bank CSV parsers
│   ├── import_transactions.py    # Import CLI
│   ├── reports.py                # Reports CLI
│   └── accounts/                 # CSV files (gitignored)
│
├── assistants/                   # LLM assistants
│   └── db_manager.py             # Database query assistant
│
├── graph_logging/                # Neo4j event logging
│   ├── src/
│   │   ├── event_logger.py       # Event writer
│   │   ├── diagnostics.py        # Query interface
│   │   └── system_monitor.py     # Metrics collector
│   └── config/
│
├── llm_diagnostics/              # LLM diagnostic tools
│   └── src/
│       └── mythos_ask.py         # CLI tool
│
├── intake/                       # Sales intake staging
│   ├── pending/                  # Photos awaiting processing
│   └── processed/                # Completed intakes
│
├── assets/                       # Permanent asset storage
│   └── images/                   # SHA256-sharded images
│
├── patches/                      # Patch system
│   ├── archive/                  # Processed zips
│   └── logs/                     # Application logs
│
├── media/                        # User media uploads
│
└── mythos_patch_monitor.py       # Patch watcher daemon
```

---

## Services

| Service | Port | Description | Restart |
|---------|------|-------------|---------|
| `mythos-bot.service` | - | Telegram bot (polling) | always |
| `mythos-api.service` | 8000 | FastAPI gateway | always |
| `mythos-patch-monitor.service` | - | Patch file watcher | always |
| `mythos-worker-vision.service` | - | Vision analysis | always |
| `mythos-worker-embedding.service` | - | Text embeddings | always |
| `mythos-worker-grid.service` | - | Grid analysis | always |
| `mythos-worker-entity.service` | - | Entity resolution | always |
| `mythos-worker-temporal.service` | - | Temporal extraction | always |
| `mythos-worker-summary.service` | - | Summarization | always |
| `postgresql` | 5432 | Primary database | system |
| `neo4j` | 7474/7687 | Graph database | system |
| `redis` | 6379 | Job queues | system |
| `ollama` | 11434 | Local LLM | system |

---

## Databases

### PostgreSQL: `mythos`

**Core Tables:**
| Table | Description |
|-------|-------------|
| `users` | System users with Telegram IDs |
| `chat_messages` | Conversation messages |
| `media_files` | Uploaded media metadata |

**Finance Tables:**
| Table | Description |
|-------|-------------|
| `accounts` | Bank accounts |
| `transactions` | All transactions |
| `categories` | Category definitions |
| `category_mappings` | Auto-categorization patterns |
| `import_logs` | Import history |

**Sales Tables:**
| Table | Description |
|-------|-------------|
| `items_for_sale` | Item metadata and pricing |
| `item_images` | Photo records |
| `sales` | Completed sales |

**Timeseries Tables:**
| Table | Description |
|-------|-------------|
| `grid_activation_timeseries` | 9-node analysis results |
| `emotional_state_timeseries` | Emotional tracking |
| `entity_mention_timeseries` | Entity mentions over time |

### Neo4j: `mythos`

**Node Labels:**
| Label | Description |
|-------|-------------|
| `Soul` | Spiritual entities |
| `Person` | Physical people |
| `Incarnation` | Soul manifestations |
| `Lifetime` | Life spans |
| `Alias` | Alternative names |
| `Conversation` | Chat sessions |
| `Exchange` | Message pairs |
| `Topic` | Discussion topics |
| `Concept` | Abstract concepts |
| `Fact` | Extracted facts |
| `System` | Monitored systems |
| `Service` | Systemd services |
| `Process` | Running processes |
| `Event` | System events |
| `Metric` | System metrics |
| `File` | Filesystem files |
| `Directory` | Filesystem directories |
| `Function` | Code functions |
| `GitRepo` | Git repositories |

**Key Relationships:**
| Relationship | Description |
|--------------|-------------|
| `CURRENTLY_EMBODIED_AS` | Soul → Person (active) |
| `INCARNATED_AS` | Soul → Incarnation |
| `MANIFESTED_AS` | Soul → Lifetime |
| `PARENT_OF` | Person → Person |
| `SPOUSE_OF` | Person ↔ Person |
| `KNOWN_AS` | Person/Soul → Alias |
| `HAD_CONVERSATION` | Person → Conversation |
| `CONTAINS` | Conversation → Exchange |
| `MENTIONED` | Exchange → Entity |
| `MAY_HAVE_CAUSED` | Event → Event |
| `RUNS_SERVICE` | System → Service |
| `RUNS` | System → Process |

### Redis Streams

| Stream | Purpose |
|--------|---------|
| `mythos:assignments:vision` | Photo analysis jobs |
| `mythos:assignments:embedding` | Embedding generation jobs |
| `mythos:assignments:grid_analysis` | Grid analysis jobs |
| `mythos:assignments:entity` | Entity resolution jobs |
| `mythos:assignments:temporal` | Temporal extraction jobs |
| `mythos:assignments:summary_rebuild` | Summary rebuild jobs |

### Qdrant Collections

| Collection | Dimensions | Purpose |
|------------|------------|---------|
| `text_embeddings` | 384 | MiniLM-L6-v2 text vectors |

---

## Ollama Models

| Model | Size | Purpose |
|-------|------|---------|
| `qwen2.5:32b` | 19GB | Primary text (db mode, grid analysis) |
| `llava:34b` | 20GB | Vision analysis |
| `llava-llama3` | 5.5GB | Fast vision |
| `deepseek-coder-v2:16b` | 8.9GB | Code generation |
| `llama3.2:3b` | 2GB | Fast responses, diagnostics |

---

## Environment Variables

```bash
# /opt/mythos/.env

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<secret>

# PostgreSQL
POSTGRES_HOST=/var/run/postgresql
POSTGRES_DB=mythos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<secret>

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:32b
OLLAMA_VISION_MODEL=llava:34b

# Telegram
TELEGRAM_BOT_TOKEN=<secret>
TELEGRAM_ID_KA=<id>
TELEGRAM_ID_SERAPHE=<id>

# API Keys
API_KEY_TELEGRAM_BOT=<secret>
API_KEY_KA=<secret>
API_KEY_SERAPHE=<secret>

# Plaid (finance)
PLAID_CLIENT_ID=<id>
PLAID_ENV=development
```

---

## Common Commands

```bash
# Services
sudo systemctl status mythos-bot.service
sudo systemctl restart mythos-bot.service
journalctl -u mythos-bot.service -f

# All Mythos services
systemctl list-units --type=service | grep mythos

# Finance
cd /opt/mythos/finance
/opt/mythos/.venv/bin/python import_transactions.py accounts/file.csv --account-id 1 --dry-run
/opt/mythos/.venv/bin/python reports.py summary

# Database
sudo -u postgres psql -d mythos
cypher-shell -u neo4j

# Ollama
ollama list
ollama run qwen2.5:32b

# Redis
redis-cli KEYS "mythos:*"
redis-cli XLEN mythos:assignments:vision

# Git
cd /opt/mythos && git log --oneline -10
cd /opt/mythos && git tag -l --sort=-v:refname | head -10

# LLM Diagnostics
/opt/mythos/.venv/bin/python /opt/mythos/llm_diagnostics/src/mythos_ask.py "system health"
```

---

## Diagnostic Workflow

When troubleshooting with Claude, use the **diagnostic dump pattern**:

```bash
D=~/diag.txt; > "$D"
echo "=== SECTION 1 ===" >> "$D"
<command1> >> "$D" 2>&1
echo -e "\n\n=== SECTION 2 ===" >> "$D"
<command2> >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

**Standard Session Start:**
```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

---

*This document reflects the actual deployed state of the Mythos system as of 2026-01-24.*
