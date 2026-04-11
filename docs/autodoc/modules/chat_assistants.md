# Chat Assistants

**Stream:** LOG
**Files:** 5

## Files in this Module

- `assistants/chat_assistant.py` (735L)
- `assistants/db_manager.backup.2026-01-06-1.py` (254L)
- `assistants/db_manager.backup.2026-01-06-2.py` (221L)
- `assistants/db_manager.py` (259L)
- `assistants/iris_memory.py` (244L)

---

# Mythos Chat Assistants Module Documentation

## 1. Module Purpose
The Chat Assistants module provides a comprehensive system for managing multi-turn conversations with AI assistants, integrating natural language database querying, persistent memory storage, and consciousness mapping capabilities. It enables:
- Context-aware chat interactions with Ollama-based models
- Natural language querying of Neo4j and PostgreSQL databases
- Persistent memory storage of conversation history
- Consciousness mapping through grid analysis integration
- Structured logging of exchanges to Neo4j

## 2. Architecture Overview
The module follows a layered architecture with three core components working in concert:

1. **ChatAssistant (chat_assistant.py)**
   - Manages conversation context and flow
   - Integrates with Ollama for response generation
   - Coordinates with IrisMemory for persistent storage
   - Dispatches to grid analysis via Redis
   - Logs exchanges to Neo4j via ConversationBridge

2. **DatabaseManager (db_manager.py)**
   - Natural language interface to databases
   - Routes queries to Neo4j/PostgreSQL based on context
   - Uses Ollama to generate SQL/Cypher queries
   - Formats results for Telegram display

3. **IrisMemory (iris_memory.py)**
   - Persistent memory layer for conversation history
   - Stores chat messages in PostgreSQL
   - Provides context window management
   - Tracks conversation statistics

Data flows through the system as:
User Input → ChatAssistant (context management) → Ollama (response generation) → DatabaseManager (query execution) → IrisMemory (persistent storage) → Neo4j (conversation logging)

## 3. Key Components

### ChatAssistant Class
- **Context Management**: Maintains conversation history with `load_context()` and `trim_context()`
- **Prompt Assembly**: Uses `prompt_assembler` to build system prompts with layers
- **Grid Analysis**: Dispatches to analysis workers via Redis
- **Conversation Logging**: Writes exchanges to Neo4j via `ConversationBridge`

### DatabaseManager Class
- **Query Routing**: `route_query()` determines database type
- **Query Generation**: 
  - `generate_cypher()` for Neo4j queries
  - `generate_sql()` for PostgreSQL queries
- **Result Formatting**: `format_neo4j_result()` for Telegram display

### IrisMemory Class
- **Message Storage**: `save_message()` to PostgreSQL
- **Context Retrieval**: `load_recent()` for conversation history
- **Statistics**: `get_conversation_stats()` for analytics

## 4. Design Patterns

| Pattern        | Implementation                                                                 |
|----------------|--------------------------------------------------------------------------------|
| Singleton      | ChatAssistant maintains single instance for user context                       |
| Facade         | ChatAssistant simplifies complex subsystem interactions                        |
| Factory Method | DatabaseManager's generate_cypher/generate_sql create query objects            |
| Strategy       | Query routing selects between Neo4j/PostgreSQL based on input                  |
| Observer       | Redis dispatch for grid analysis workers                                       |

## 5. Data Model

### PostgreSQL Tables
- `chat_messages` (IrisMemory):
  - `user_uuid`, `telegram_user_id`, `conversation_id`, `role`, `content`, `mode`, `model_used`, `response_time_ms`, `created_at`

- `prompt_layers` (ChatAssistant):
  - Stores system prompt components for different contexts

### Neo4j Schema
- **Nodes**:
  - `Person` (with properties: name, birth, death)
  - `Soul` (with properties: soul_id, incarnations)
  - `Incarnation` (with properties: lifetime, birth, death)

- **Relationships**:
  - `(:Soul)-[:HAS_INCARNATION]->(:Incarnation)`
  - `(:Person)-[:HAS_SOUL]->(:Soul)`

### Redis Usage
- Message queues for grid analysis workers
- Temporary context storage for active conversations

## 6. API Surface

### ChatAssistant Public Methods
- `set_user(user_info: Dict[str, Any])` - Sets current user context
- `query(message: str, model_preference: str, telegram_id: str)` - Main chat interface
- `get_last_prompt()` - Debugging method
- `clear_context(user_uuid: str)` - Resets conversation history
- `get_context_stats(user_uuid: str)` - Conversation analytics

### DatabaseManager Public Methods
- `query(natural_language_query: str)` - Main query interface
- `generate_cypher(natural_language_query: str)` - Cypher query generation
- `generate_sql(natural_language_query: str)` - SQL query generation
- `format_neo4j_result(result: dict, cypher: str)` - Result formatting

### IrisMemory Public Methods
- `save_message(message_data: dict)` - Message persistence
- `load_recent(user_uuid: str, limit: int)` - Context retrieval
- `build_memory_context(user_uuid: str)` - Context window construction
- `get_conversation_stats(user_uuid: str)` - Conversation analytics

## 7. Dependencies

### Internal Modules
- `ollama` - For model inference
- `conversation_bridge` - Neo4j logging
- `prompt_assembler` - System prompt construction
- `subject_tracker` - Consciousness mapping
- `research_router` - Query routing logic

### External Systems
- **Databases**:
  - PostgreSQL (chat_messages, prompt_layers)
  - Neo4j (consciousness graph)
- **Message Queue**:
  - Redis (grid analysis workers)
- **AI Models**:
  - Ollama (query generation and response generation)

## 8. Configuration

### Environment Variables
```env
# Ollama Configuration
OLLAMA_HOST="localhost:11434"
OLLAMA_MODEL="llama3"

# Database Configuration
POSTGRES_HOST="localhost"
POSTGRES_DB="mythos"
POSTGRES_USER="mythos_user"
POSTGRES_PASSWORD="secure_password"

NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="neo4j_password"

# Redis Configuration
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0
```

### Configuration Files
- `.env` - Loaded via `load_dotenv()`
- `~/main-vault/systems/arcturus/prompts/db_mode_prompt.md` - System prompt for database queries

### Runtime Configuration
- Context window size (via `MAX_CONTEXT_MESSAGES` constant)
- Prompt layer configuration (via `PROMPT_LAYERS` dictionary)
- Database query timeout settings (via `QUERY_TIMEOUT`)

---

This module provides a robust foundation for AI-powered chat assistants with integrated database capabilities and persistent memory, while maintaining flexibility through configuration and modular design.
