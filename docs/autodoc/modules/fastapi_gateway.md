# FastAPI Gateway

**Stream:** SYS
**Files:** 31

## Files in this Module

- `api/__init__.py` (0L)
- `api/context_manager.py` (601L)
- `api/grocery_routes.py` (179L)
- `api/integration_example.py` (226L)
- `api/main.py` (412L)
- `api/media_routes.py` (457L)
- `api/orchestrator.py` (242L)
- `api/routes/__init__.py` (0L)
- `api/routes/doc_registry.py` (401L)
- `api/routes/finance.py` (708L)
- `api/routes/finance_dashboard.py` (349L)
- `api/routes/frontend.py` (54L)
- `api/routes/iris_systems.py` (113L)
- `api/routes/ontology.py` (344L)
- `api/routes/overview.py` (326L)
- `api/routes/people.py` (671L)
- `api/routes/projection.py` (456L)
- `api/routes/public_files.py` (79L)
- `api/routes/quotes.py` (428L)
- `api/routes/review.py` (23L)
- `api/routes/rolodex.py` (785L)
- `api/routes/sales.py` (164L)
- `api/routes/shell_result.py` (81L)
- `api/routes/shopping.py` (535L)
- `api/routes/smart_overview.py` (244L)
- `api/routes/spending_analytics.py` (250L)
- `api/routes/system.py` (194L)
- `api/routes/voice.py` (317L)
- `api/routes/web.py` (129L)
- `api/auth/__init__.py` (0L)
- `api/auth/google_auth.py` (302L)

---

# Mythos FastAPI Gateway Module Documentation

## 1. Module Purpose
The FastAPI Gateway module serves as the central API entry point for the Mythos system, handling:
- Conversation context management for LLM interactions
- Grocery list management with persistent storage
- Media file handling and tagging
- Financial operations and reporting
- Document registry and search
- Task orchestration via Redis
- Frontend static asset serving

This module acts as the primary interface between external clients (Telegram, React frontend) and internal Mythos services, coordinating data flow between databases, vector stores, and LLM components.

## 2. Architecture Overview
The module follows a layered architecture with distinct responsibilities:
1. **Entry Point**: `main.py` initializes the FastAPI app, routes, and core services
2. **Context Layer**: `context_manager.py` assembles multi-tier conversation contexts
3. **Orchestration Layer**: `orchestrator.py` manages Redis-based task dispatching
4. **Route Layers**: 
   - Grocery, media, finance, and document routes handle domain-specific operations
   - Frontend routes serve static assets and React application
5. **Database Layer**: PostgreSQL for structured data, Neo4j for graph data, Qdrant for vector search

Data flows through the system as:
```
Client Request → API Route → Context/Orchestrator → Database/External Services → Response
```

## 3. Key Components

### Core Classes
- **ContextManager**: Assembles conversation context windows with mode prompts, summaries, and semantic search results
- **Orchestrator**: Manages Redis task streams for asynchronous processing (entity resolution, summary rebuilds)
- **DatabaseManager**: Handles PostgreSQL connections and queries
- **ChatAssistant**: Routes messages to appropriate LLM modes

### Route Handlers
- **GroceryRoutes**: CRUD operations for grocery lists
- **MediaRoutes**: Media upload, retrieval, and tagging
- **FinanceRoutes**: Financial transaction management
- **DocRegistry**: Document search and versioning
- **FrontendRoutes**: Static asset and React app serving

### Helper Functions
- `_get_conn`: Database connection factory
- `verify_api_key`: Authentication middleware
- `get_orchestrator`: Singleton orchestrator instance

## 4. Design Patterns

| Pattern        | Usage Example                          |
|----------------|----------------------------------------|
| **Singleton**  | Orchestrator, DatabaseManager instances |
| **Factory**    | `_get_conn` database connection factory |
| **Facade**     | `assemble_context()` in ContextManager  |
| **Dependency Injection** | API key verification middleware |
| **Pydantic Models** | Request/response validation in routes |

## 5. Data Model

### PostgreSQL Tables
- `chat_messages`: Stores conversation history
- `conversation_summaries`: Tiered conversation summaries
- `grocery_lists`: Grocery list metadata
- `grocery_items`: Grocery list items with aisle categorization
- `media_files`: Media metadata and tags
- `document_registry`: Document metadata and versions
- `transactions`: Financial transactions
- `recurring_bills`: Bill tracking data

### External Stores
- **Neo4j**: Entity graph for semantic relationships
- **Qdrant**: Vector store for semantic search
- **Redis**: Task queue for asynchronous processing

## 6. API Surface

### Public Endpoints
#### Core Functionality
- `POST /message`: Process user messages with context management
- `GET /orchestrator/stats`: View task queue statistics

#### Grocery Management
- `GET /list`: Retrieve current grocery list
- `POST /add`: Add items to list
- `POST /reset`: Reset grocery list

#### Media Management
- `POST /media/upload`: Upload media files
- `GET /media/recent`: Retrieve recent photos
- `POST /media/tag/add`: Add tags to media

#### Financial Operations
- `GET /api/finance/summary`: Financial summary
- `GET /api/finance/report`: Generate financial report
- `GET /api/finance/v2/dashboard`: Finance dashboard view

#### Document Management
- `GET /search`: Search registered documents
- `POST /register`: Register new documents
- `PUT /{slug}`: Update document metadata

#### Frontend
- `GET /app/v2/`: Serve React application
- `GET /app/v2/assets/`: Serve static assets

## 7. Dependencies

### Internal Modules
- `assistants`: Chat and database assistants
- `context_manager`: Context assembly logic
- `orchestrator`: Task dispatching system

### External Services
- **PostgreSQL**: Structured data storage
- **Neo4j**: Graph database for entity relationships
- **Qdrant**: Vector similarity search
- **Redis**: Task queue and statistics tracking

### Required Libraries
- FastAPI (routing and validation)
- Psycopg2 (PostgreSQL)
- Pydantic (data validation)
- Redis-py (Redis client)
- Qdrant-client (vector search)
- Neo4j (graph database)

## 8. Configuration

### Environment Variables
```env
# Database
POSTGRES_HOST=host.docker.internal
POSTGRES_DB=mythos
POSTGRES_USER=mythos
POSTGRES_PASSWORD=secret
POSTGRES_PORT=5432

# Redis
REDIS_HOST=host.docker.internal
REDIS_PORT=6379
REDIS_DB=0

# API Keys
API_KEY_TELEGRAM_BOT=telegram_key
API_KEY_KA=ka_key
API_KEY_SERAPHE=seraphe_key

# File Paths
DIST_DIR=/opt/mythos/web/frontend/dist
PROMPTS_DIR=/opt/mythos/prompts
```

### Configuration Files
- `.env`: Environment variables for database and API keys
- `main.py`: Route configuration and middleware setup
- `context_manager.py`: Constants for context window limits and directories

### Configuration Logic
- `.env` loaded via `python-dotenv`
- Database connections configured via `_get_conn()`
- Redis connection configured via `get_orchestrator()`
- Frontend paths defined in `frontend.py`

---

This documentation provides a comprehensive overview of the FastAPI Gateway module, covering its architecture, key components, and integration points within the Mythos system. The module serves as the central API hub, coordinating between client requests and internal services while maintaining strict separation of concerns through well-defined patterns and interfaces.
