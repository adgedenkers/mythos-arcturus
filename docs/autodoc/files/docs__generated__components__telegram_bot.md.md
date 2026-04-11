# docs/generated/components/telegram_bot.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 75

---

### Purpose
The `telegram_bot` component serves as the primary user interface for the Mythos sovereign AI platform, enabling users to interact with core AI services (Ollama, Neo4j, PostgreSQL) via Telegram. It provides a familiar and accessible channel for users to query, manage, and interact with their personal AI infrastructure.

### Architecture
The `telegram_bot` component is structured into multiple handler files, each responsible for a specific feature or functionality. The core bot entrypoint is defined in `mythos_bot.py`, which initializes handlers, manages updates, and routes messages to the appropriate handlers. Each handler file contains methods prefixed with `handle_*` to process specific types of user interactions.

### Patterns
- **Handler Pattern**: Each feature is encapsulated in a dedicated handler file (e.g., `finance_handler.py`), with `handle_*` methods for message routing.
- **Async First**: All Telegram callbacks are asynchronous, using `async` functions.
- **Contextual Help**: The `help_handler.py` dynamically generates help menus based on the user's current context.
- **State Management**: Redis is used to store session state and active modes.
- **Debugging Hooks**: The `prompt_debug_handler.py` logs LLM prompts and token usage without affecting the core flow.
- **Minimalist Handlers**: Short handlers delegate to core services, keeping the codebase modular and maintainable.

### Dependencies
The `telegram_bot` component relies on the following dependencies:
- **Telegram Bot API**: For handling user interactions.
- **PostgreSQL**: For persistent storage of user profiles, task logs, financial transactions, and chat history.
- **Neo4j**: For querying graph data related to astrological relationships and ontology mappings.
- **Redis**: For session state management and temporary storage of voice memos.
- **Ollama**: For generating responses using LLMs.
- **FastAPI**: For backend API calls.
- **External Services**: For integrating with email/SMS APIs for alerts.

### Interfaces
The `telegram_bot` component exposes the following interfaces:
- **Telegram Bot API**: Handles user messages and updates.
- **FastAPI Backend**: Communicates with `/api/chat` and `/api/tasks` endpoints for state management.
- **Ollama API**: Uses `ollama.generate()` for LLM responses.
- **Neo4j Driver**: Queries graph data via `neo4j_driver`.
- **PostgreSQL**: Writes to and reads from various tables (e.g., `users`, `tasks`, `transactions`, `chats`).
- **Redis**: Stores session state and rate-limiting keys.

### Database
The `telegram_bot` component interacts with the following database tables and Neo4j labels:
- **PostgreSQL**:
  - `users`: Stores user profiles.
  - `tasks`: Stores task logs.
  - `transactions`: Stores financial transactions.
  - `chats`: Stores chat history.
- **Neo4j**:
  - `astrology_nodes`: Stores astrological relationships.
  - `ontology_edges`: Stores ontology mappings.
  - `people_nodes`: Stores social graphs.

### Configuration
The `telegram_bot` component uses the following configuration variables:
- `TELEGRAM_BOT_TOKEN`: Bot API token for Telegram API access.
- `DB_URL`: PostgreSQL connection string.
- `NEO4J_URL`: Neo4j Bolt URI.
- `OLLAMA_URL`: Ollama API endpoint.
- `REDIS_URL`: Redis connection string.
- `BOT_MODE`: Default mode for new users (e.g., `finance`, `reflect`).

### Key Logic
The most important business logic and algorithms in the `telegram_bot` component include:
- **Message Routing**: Efficiently routing user messages to the appropriate handler based on the message content and context.
- **State Management**: Managing user session states and active modes using Redis.
- **LLM Integration**: Generating responses using Ollama for financial and astrological queries.
- **Data Persistence**: Persisting user interactions and data in PostgreSQL and Neo4j.
- **Contextual Help**: Dynamically generating help menus based on the user's current context.

### Integration Points
The `telegram_bot` component integrates with the following subsystems:
1. **FastAPI Backend**: `chat_mode.py` and `task_handler.py` call `/api/chat` and `/api/tasks` endpoints for state management.
2. **Ollama**: `finance_handler.py` and `astrology_handler.py` use `ollama.generate()` for LLM responses.
3. **Neo4j**: `astrology_handler.py` and `ontology_handler.py` query graph data via `neo4j_driver`.
4. **PostgreSQL**: All data persistence (e.g., `people_handler.py` writes to `users` table).
5. **External Services**: `send_notification.py` integrates with email/SMS APIs for alerts.
