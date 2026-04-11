# assistants/chat_assistant.py

**Language:** python
**Stream:** LOG
**Module:** Chat Assistants
**Lines:** 735

---

### File: `assistants/chat_assistant.py`

#### Purpose
This file contains the `ChatAssistant` class, which serves as a general-purpose chat assistant using the Ollama API. It maintains conversation context per user, integrates with grid analysis for consciousness mapping, and writes exchanges to Neo4j via the `ConversationBridge`.

#### Architecture
The `ChatAssistant` class is designed to manage multi-turn conversations by maintaining context and integrating with various subsystems. It includes methods for setting user context, loading and adding to context, building messages for the Ollama API, dispatching grid analysis, logging to the bridge, and processing queries.

#### Patterns
- **Singleton Pattern**: The `ChatAssistant` class can be instantiated once per application, maintaining state across multiple interactions.
- **Facade Pattern**: The class provides a simplified interface to complex subsystems like Ollama, Redis, and Neo4j.

#### Dependencies
- **Imports**: `os`, `time`, `uuid`, `json`, `logging`, `redis`, `sys`
- **External Modules**: `ollama`, `iris_memory`, `perception_router`, `life_context`, `message_extractor`, `action_executor`, `prompt_assembler`, `conversation_bridge`, `subject_tracker`, `research_router`, `node_executor`, `convergence`, `engine`

#### Interfaces
- **Public Methods**:
  - `set_user(user_info: Dict[str, Any])`: Set the current user context.
  - `query(message: str, model_preference: str, telegram_id: str)`: Process a chat message and return the response.
  - `get_last_prompt()`: Return the last assembled system prompt for debugging.
  - `clear_context(user_uuid: str)`: Clear the conversation context for a user.
  - `get_context_stats(user_uuid: str)`: Get statistics about a user's conversation context.

#### Database
- **PostgreSQL Tables**: `prompt_layers`, `datetime`, `typing`, `dotenv`, `ollama`, `iris_memory`, `perception_router`, `life_context`, `message_extractor`, `action_executor`, `prompt_assembler`, `conversation_bridge`, `subject_tracker`, `research_router`, `node_executor`, `convergence`, `engine`, `core`, `DB`, `in`, `context`, `research`, `session`, `dynamic`, `handlers`
- **Neo4j**: Writes exchanges to Neo4j via `ConversationBridge`.

#### Configuration
- **Environment Variables**: `OLLAMA_HOST`, `OLLAMA_MODEL`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- **Configuration Files**: `.env` (loaded via `load_dotenv`)

#### Key Logic
- **Context Management**: Manages conversation context per user, loading recent history from the database and trimming old messages.
- **Prompt Assembly**: Builds messages for the Ollama API, incorporating core layers and optional layers based on configuration.
- **Grid Analysis**: Dispatches exchanges to grid analysis workers for consciousness mapping.
- **Logging**: Writes exchanges to Neo4j via `ConversationBridge`.

#### Integration Points
- **Ollama API**: Uses the Ollama client to generate responses.
- **Redis**: Uses Redis for dispatching to grid analysis workers.
- **Neo4j**: Writes exchanges to Neo4j via `ConversationBridge`.
- **IrisMemory**: Loads recent conversation history from the database.
- **PerceptionRouter**: Integrates with the perception router for NEU stream.
- **SkillEngine**: Routes messages through data skills for enrichment.
- **Research Framework**: Routes messages through the research framework for pre-processing.

### Detailed Method Descriptions

- **`__init__`**: Initializes the `ChatAssistant` with Ollama client, perception router, model mapping, conversation contexts, Iris memory, conversation bridge, and Redis connection.
- **`set_user(user_info: Dict[str, Any])`**: Sets the current user context.
- **`_get_context(user_uuid: str) -> Dict`**: Gets or creates conversation context for a user.
- **`_add_to_context(user_uuid: str, role: str, content: str, timestamp: datetime = None) -> None`**: Adds a message to the user's conversation context.
- **`_load_db_context(user_uuid: str) -> None`**: Loads recent conversation history from the database into the in-memory context.
- **`_get_last_message_timestamp(user_uuid: str) -> Optional[datetime]`**: Extracts the timestamp of the last message in the context.
- **`_build_messages(user_uuid: str, user_message: str, soul_name: str, model: str = '', research_context: str = '', iris_mode: str = 'sovereign') -> List[Dict]`**: Builds the messages array for the Ollama API call, incorporating core and optional layers.
- **`_dispatch_grid_analysis(user_uuid: str, conversation_id: str, user_message: str, assistant_response: str, model_used: str)`**: Dispatches the exchange to the grid analysis worker.
- **`_log_to_bridge(conversation_id: str, user_uuid: str, telegram_id: str, user_message: str, assistant_response: str, model_used: str, response_time_ms: int, mode: str, pg_message_id: str)`**: Writes the exchange to Neo4j via `ConversationBridge`.
- **`query(message: str, model_preference: str, telegram_id: str) -> str`**: Processes a chat message and returns the response.
- **`get_last_prompt() -> str`**: Returns the last assembled system prompt for debugging.
- **`clear_context(user_uuid: str) -> None`**: Clears the conversation context for a user.
- **`get_context_stats(user_uuid: str) -> Dict`**: Gets statistics about a user's conversation context.

This file is a critical component of the Mythos system, handling the core logic for multi-turn conversations and integrating with various subsystems for enhanced functionality.
