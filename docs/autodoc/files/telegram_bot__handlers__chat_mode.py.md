# telegram_bot/handlers/chat_mode.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 424

---

### File: `telegram_bot/handlers/chat_mode.py`

#### Purpose
This file handles the core logic for managing chat sessions in the Mythos system, including logging messages to the perception log, building context for Ollama API calls, and managing user session state.

#### Architecture
The file consists of several utility functions and a main handler function (`handle_chat_message`). The functions are organized to handle different aspects of chat management, such as logging, context building, and model selection. The file does not use classes but relies on functions for modular operations.

#### Patterns
- **Singleton Pattern**: The `get_db_connection` function ensures a single database connection is reused.
- **Factory Pattern**: The `get_model_for_preference` function acts as a factory to map user preferences to specific models.

#### Dependencies
- **Standard Libraries**: `os`, `re`, `json`, `logging`, `uuid`, `sys`, `datetime`, `typing`
- **External Libraries**: `psycopg2`, `ollama.Client`
- **Internal Modules**: `handlers.ollama_models`, `prompt_assembler`, `conversation_bridge`, `core.skills_context`, `core.life_context`, `core.model_aliases`

#### Interfaces
- **Public Functions**: 
  - `_get_override_model`
  - `get_db_connection`
  - `log_to_perception`
  - `get_ollama_client`
  - `get_model_for_preference`
  - `init_chat_context`
  - `get_chat_context`
  - `add_to_context`
  - `extract_topics`
  - `_get_last_message_timestamp`
  - `build_messages_for_ollama`
  - `handle_chat_message`
  - `clear_chat_context`
  - `get_chat_stats`
  - `get_recent_topics`
  - `get_last_exchange`
  - `assemble_system_prompt`
  - `get_resolved_personality`
  - `get_available_modes`
  - `build_skills_context`
  - `build_life_context`

#### Database
- **PostgreSQL Tables**: `perception_log`, `user`, `session`, `update`, `live`, `datetime`, `typing`, `ollama`, `handlers`, `prompt_assembler`, `conversation_bridge`, `core`
- **Neo4j**: No direct Neo4j references, but `ConversationBridge` is used to write structured knowledge to Neo4j.

#### Configuration
- **Environment Variables**:
  - `OLLAMA_HOST`: Host for Ollama service (default: `http://localhost:11434`)
  - `OLLAMA_MODEL`: Default model for Ollama (default: `DEFAULT_MODEL`)
  - `POSTGRES_HOST`: PostgreSQL host (default: `/var/run/postgresql`)
  - `POSTGRES_DB`: PostgreSQL database name (default: `mythos`)
  - `POSTGRES_USER`: PostgreSQL user (default: `adge`)
  - `POSTGRES_PASSWORD`: PostgreSQL password (default: empty string)

#### Key Logic
1. **Model Override**: `_get_override_model` checks for a user-specific model override.
2. **Database Connection**: `get_db_connection` establishes a connection to the PostgreSQL database.
3. **Perception Logging**: `log_to_perception` logs messages to the `perception_log` table.
4. **Ollama Client**: `get_ollama_client` initializes the Ollama client.
5. **Model Mapping**: `get_model_for_preference` maps user preferences to specific models.
6. **Context Management**: Functions like `init_chat_context`, `get_chat_context`, and `add_to_context` manage the chat context within a session.
7. **Topic Extraction**: `extract_topics` extracts likely topics from user messages.
8. **Message Building**: `build_messages_for_ollama` constructs the messages array for Ollama API calls.
9. **Chat Handling**: `handle_chat_message` is the main function that processes a chat message, logs it, builds the context, and generates a response using Ollama.

#### Integration Points
- **Ollama**: The file integrates with the Ollama API to generate responses.
- **Prompt Assembler**: Uses the `prompt_assembler` module to generate system prompts.
- **Conversation Bridge**: Integrates with `ConversationBridge` to write structured knowledge to Neo4j.
- **Session Management**: Manages user sessions and context within the `session` dictionary.
- **Logging**: Uses the `logging` module to log various operations and errors.

This file is a critical component of the Mythos system, handling the core chat functionality and ensuring that all interactions are logged and processed appropriately.
