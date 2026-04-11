# Telegram Bot

**Stream:** SYS
**Files:** 46

## Files in this Module

- `telegram_bot/mythos_bot.py` (1314L)
- `telegram_bot/send_notification.py` (79L)
- `telegram_bot/handlers/__init__.py` (80L)
- `telegram_bot/handlers/analyst_handler.py` (143L)
- `telegram_bot/handlers/astrology_handler.py` (462L)
- `telegram_bot/handlers/backlog_handler.py` (380L)
- `telegram_bot/handlers/calendar_handler.py` (211L)
- `telegram_bot/handlers/chat_mode.py` (424L)
- `telegram_bot/handlers/checkin_handler.py` (301L)
- `telegram_bot/handlers/diag_handler.py` (453L)
- `telegram_bot/handlers/export_fb.py` (269L)
- `telegram_bot/handlers/export_handler.py` (348L)
- `telegram_bot/handlers/finance_handler.py` (1144L)
- `telegram_bot/handlers/forecast_handler.py` (668L)
- `telegram_bot/handlers/grid_manifest_handler.py` (212L)
- `telegram_bot/handlers/help_handler.py` (1071L)
- `telegram_bot/handlers/inspect_handler.py` (735L)
- `telegram_bot/handlers/integrity_handler.py` (280L)
- `telegram_bot/handlers/iris_handler.py` (294L)
- `telegram_bot/handlers/layer_handler.py` (154L)
- `telegram_bot/handlers/media_handler.py` (451L)
- `telegram_bot/handlers/meditation_handler.py` (187L)
- `telegram_bot/handlers/ollama_models.py` (480L)
- `telegram_bot/handlers/ontology_handler.py` (251L)
- `telegram_bot/handlers/patch_handlers.py` (440L)
- `telegram_bot/handlers/people_handler.py` (469L)
- `telegram_bot/handlers/planets_handler.py` (32L)
- `telegram_bot/handlers/prompt_debug_handler.py` (94L)
- `telegram_bot/handlers/pulse_handler.py` (330L)
- `telegram_bot/handlers/quakes_handler.py` (32L)
- `telegram_bot/handlers/quote_handler.py` (379L)
- `telegram_bot/handlers/reflect_handler.py` (148L)
- `telegram_bot/handlers/registry_handler.py` (163L)
- `telegram_bot/handlers/review_handler.py` (100L)
- `telegram_bot/handlers/route_handler.py` (412L)
- `telegram_bot/handlers/sell_mode.py` (708L)
- `telegram_bot/handlers/shopping_handler.py` (510L)
- `telegram_bot/handlers/snapshot_handler.py` (363L)
- `telegram_bot/handlers/solar_handler.py` (37L)
- `telegram_bot/handlers/spiral_handler.py` (133L)
- `telegram_bot/handlers/task_handler.py` (524L)
- `telegram_bot/handlers/voice_handler.py` (324L)
- `telegram_bot/handlers/voice_memo_handler.py` (325L)
- `telegram_bot/handlers/voice_profile_handler.py` (83L)
- `telegram_bot/handlers/watchlist_handler.py` (508L)
- `telegram_bot/handlers/weather_handler.py` (45L)

---

# Mythos Telegram Bot Module Overview

## 1. Module Purpose
The Mythos Telegram Bot module serves as the primary user interface for interacting with the Mythos system via the Telegram messaging platform. It provides a comprehensive command-based interface for:
- Session management and user tracking
- Multi-mode operation (chat, sell, db, etc.)
- Astrology and calendar functionality
- Backlog and task management
- Routine check-ins and diagnostics
- Photo analysis and inventory management
- Notification system integration
- Integration with Ollama AI models and PostgreSQL/Neo4j databases

The module acts as a central hub for user interaction, orchestrating requests between the Telegram API and various backend subsystems.

## 2. Architecture Overview
The module follows a layered architecture with clear separation of concerns:
```
[Telegram API] 
  ↓
[Command Router] (mythos_bot.py)
  ↓
[Handler Modules] (handlers/)
  ↓
[Database/Service Integration] (PostgreSQL, Neo4j, Ollama)
  ↓
[Response Generation]
```

Key architectural components:
- **Command Router**: Centralized in `mythos_bot.py`, routes commands to appropriate handlers
- **Handler Modules**: Specialized modules in `handlers/` for specific domains (astrology, backlog, calendar, etc.)
- **Session Management**: In-memory singleton (`SESSIONS` dict) for tracking user state
- **Database Layer**: PostgreSQL for structured data, Neo4j for graph relationships
- **Notification System**: `send_notification.py` for cross-service alerts

## 3. Key Components
### Core Components
- **MythosBot Class** (`mythos_bot.py`): Main bot instance with command routing and session management
- **SessionManager**: In-memory singleton (`SESSIONS` dict) for user state tracking
- **NotificationService** (`send_notification.py`): Centralized message delivery system
- **Handler Registry**: Exports 50+ command handlers through `handlers/__init__.py`

### Domain-Specific Handlers
| Domain          | Key Functions                                  | File Location                      |
|-----------------|------------------------------------------------|------------------------------------|
| Astrology       | Chart generation, planet positions             | `astrology_handler.py`             |
| Backlog         | Task management, status updates                | `backlog_handler.py`               |
| Calendar        | Event display and quick-add                    | `calendar_handler.py`              |
| Chat            | Context management, Ollama integration         | `chat_mode.py`                     |
| Routines        | Daily check-ins and routine tracking           | `checkin_handler.py`               |
| Diagnostics     | System health checks                           | `diag_handler.py`                  |
| Analyst         | Backlog analysis and recommendations           | `analyst_handler.py`               |

## 4. Design Patterns
1. **Singleton Pattern**
   - Session management (`SESSIONS` dict)
   - Database connection pooling (`get_db_connection`)

2. **Command Pattern**
   - Each command (e.g., `/chart`, `/backlog`, `/checkin`) has dedicated handler functions
   - Centralized command routing in `mythos_bot.py`

3. **Observer Pattern**
   - Message observation system in `mythos_bot.py` triggers appropriate handlers

4. **Factory Pattern**
   - `get_model_for_preference()` in `chat_mode.py` maps user preferences to AI models
   - `BacklogAnalyst` instantiation in `analyst_handler.py`

5. **Facade Pattern**
   - `handlers/__init__.py` provides unified interface to all handler functions

## 5. Data Model
### PostgreSQL Tables
- **Core Tables**
  - `idea_backlog`: Task tracking with status fields
  - `calendar_events`: Calendar entries with timestamps
  - `astro_charts`: Astrology chart data
  - `perception_log`: Chat history and user interactions
  - `routines`: Daily routine definitions and completions

- **Support Tables**
  - `astro_placements`: Planet positions in charts
  - `astro_house_cusps`: House cusp calculations
  - `patch_history`: System patch tracking

### Neo4j Graph
- **Labels**
  - `Person`: User profiles with relationships to routines
  - `Chart`: Astrology charts with planetary relationships
  - `Task`: Backlog items with status transitions

## 6. API Surface
### Telegram Commands
| Command       | Description                          | Handler File               |
|---------------|--------------------------------------|----------------------------|
| `/start`      | Initialize session                   | `mythos_bot.py`            |
| `/chart`      | Generate astrology chart             | `astrology_handler.py`     |
| `/backlog`    | Task management                      | `backlog_handler.py`       |
| `/calendar`   | View/add calendar events             | `calendar_handler.py`      |
| `/checkin`    | Daily routine tracking               | `checkin_handler.py`       |
| `/diag`       | System diagnostics                   | `diag_handler.py`          |
| `/export`     | Data export functionality            | `export_handler.py`        |

### Notification API
- `send_message(text: str, chat_id: str = None)` in `send_notification.py`
  - Asynchronous message delivery to specified or default admin chat
  - Used by external services for alerts

## 7. Dependencies
### External Libraries
- **Core Dependencies**
  - `python-telegram-bot` (Telegram API)
  - `psycopg2` (PostgreSQL)
  - `httpx` (Async HTTP requests)
  - `ollama` (AI model integration)
  - `python-dotenv` (Environment variables)

- **Optional Dependencies**
  - `neo4j` (Graph database)
  - `redis` (Caching)
  - `apscheduler` (Scheduling)

### Internal Modules
- **Core Services**
  - `core.backlog_analyst` (Analysis engine)
  - `core.skills_context` (Context management)
  - `prompt_assembler` (Prompt engineering)

- **Support Modules**
  - `calendar_formatter` (Calendar rendering)
  - `conversation_bridge` (Graph database integration)
  - `routines_engine` (Routine management)

## 8. Configuration
### Environment Variables
| Variable                  | Description                          | Required |
|---------------------------|--------------------------------------|----------|
| `TELEGRAM_BOT_TOKEN`      | Telegram bot API token               | ✅       |
| `POSTGRES_HOST`           | PostgreSQL database host             | ✅       |
| `POSTGRES_DB`             | Database name                        | ✅       |
| `POSTGRES_USER`           | Database username                    | ✅       |
| `POSTGRES_PASSWORD`       | Database password                    | ✅       |
| `OLLAMA_HOST`             | Ollama AI service endpoint           | ✅       |
| `TELEGRAM_ADMIN_CHAT_ID`  | Default admin chat ID                | ✅       |
| `NEO4J_PASSWORD`          | Neo4j database password              | ⚠️ (Optional) |

### Configuration Files
- `.env`: Standard dotenv file for environment variables
- `config.yaml`: Optional YAML configuration for advanced settings (not shown in provided files)

### Configuration Process
1. Create `.env` file with required variables
2. Set up PostgreSQL database with appropriate tables
3. Configure Ollama service endpoint
4. (Optional) Set up Neo4j for graph storage
5. (Optional) Configure Redis for caching

## Data Flow Diagram
```
Telegram User
    ↓
[Command Router] (mythos_bot.py)
    ↓
[Handler Module] (e.g., astrology_handler.py)
    ↓
[Database/Service] (PostgreSQL/Neo4j/Ollama)
    ↓
[Response Generation]
    ↓
Telegram Response
```

## Error Handling
- Centralized error handling in `mythos_bot.py` via `error_handler()`
- Database exceptions caught and logged in handler modules
- Retry logic in `send_notification.py` for failed requests
- Graceful degradation for optional services (e.g., Neo4j)

## Security Considerations
- Environment variables stored in `.env` file (not committed to source control)
- Telegram bot token protected via environment variable
- Database credentials secured via environment variables
- Sensitive operations (e.g., `/diag`) restricted to admin users

## Performance Characteristics
- Asynchronous message handling via `asyncio`
- Connection pooling for PostgreSQL
- Caching of frequently accessed data (optional)
- Rate limiting for Telegram API interactions

## Extensibility
- New command handlers can be added by extending `handlers/` modules
- Additional database tables can be integrated through handler modules
- New AI models can be supported by updating `chat_mode.py` and `ollama_models.py`

## Versioning
- Follows semantic versioning (MAJOR.MINOR.PATCH)
- Version number maintained in `mythos_bot.py`
- API changes tracked in `handlers/__init__.py`

## Testing Strategy
- Unit tests for individual handler functions
- Integration tests for end-to-end command flows
- Mock tests for database interactions
- Load tests for high-volume message handling

This module provides a robust foundation for user interaction with the Mythos system, combining Telegram's real-time capabilities with the system's backend services for a comprehensive user experience.
