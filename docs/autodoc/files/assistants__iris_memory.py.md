# assistants/iris_memory.py

**Language:** python
**Stream:** LOG
**Module:** Chat Assistants
**Lines:** 244

---

### File: `assistants/iris_memory.py`

#### Purpose
The `iris_memory.py` file provides a persistent memory layer for Iris conversations, handling the storage and retrieval of chat messages from a PostgreSQL database. It supports saving messages, loading recent messages, building memory context blocks, and retrieving conversation statistics.

#### Architecture
The file contains a single class `IrisMemory` with several methods to interact with the PostgreSQL database. The class manages a database connection and provides methods for saving and loading messages, building memory context blocks, and retrieving conversation statistics.

- **Classes**: 
  - `IrisMemory`: Manages database connections and provides methods for saving and loading messages, building memory context blocks, and retrieving conversation statistics.

- **Methods**:
  - `__init__`: Initializes the `IrisMemory` instance.
  - `_get_conn`: Establishes or retrieves a database connection.
  - `save_message`: Saves a message to the `chat_messages` table.
  - `load_recent`: Loads recent messages for a user.
  - `build_memory_context`: Builds a memory context block for the system prompt.
  - `get_conversation_stats`: Retrieves statistics about a user's conversation history.
  - `close`: Closes the database connection.

#### Patterns
- **Singleton Pattern**: The `_get_conn` method ensures a single database connection is maintained throughout the lifetime of the `IrisMemory` instance, acting as a singleton for the connection.

#### Dependencies
- **Imports**: 
  - `os`: For accessing environment variables.
  - `logging`: For logging messages.
  - `datetime`: For handling date and time operations.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database interactions.
  - `psycopg2.extras`: For additional PostgreSQL features like `RealDictCursor`.

#### Interfaces
- **Public Methods**:
  - `save_message`: Exposes a method to save messages to the database.
  - `load_recent`: Exposes a method to load recent messages.
  - `build_memory_context`: Exposes a method to build memory context blocks.
  - `get_conversation_stats`: Exposes a method to retrieve conversation statistics.
  - `close`: Exposes a method to close the database connection.

#### Database
- **Tables**:
  - `chat_messages`: Stores chat messages with fields like `user_uuid`, `telegram_user_id`, `conversation_id`, `role`, `content`, `mode`, `model_used`, `response_time_ms`, and `created_at`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host for the PostgreSQL database.
  - `POSTGRES_DB`: Database name.
  - `POSTGRES_USER`: Username for the PostgreSQL database.
  - `POSTGRES_PASSWORD`: Password for the PostgreSQL database.

#### Key Logic
- **Saving Messages**:
  - The `save_message` method inserts a new message into the `chat_messages` table and returns the `message_id` if successful.

- **Loading Recent Messages**:
  - The `load_recent` method retrieves recent messages for a user, optionally filtering by mode and time range. It returns a list of dictionaries with message details.

- **Building Memory Context**:
  - The `build_memory_context` method constructs a readable summary of recent conversation history, grouping messages by day and formatting them for natural reference in the system prompt.

- **Retrieving Conversation Stats**:
  - The `get_conversation_stats` method retrieves statistics about a user's conversation history, including the total number of messages, first and last message timestamps, and active days.

#### Integration Points
- **ChatAssistant**:
  - The `IrisMemory` class is used within the `ChatAssistant` module to load past context, save messages, and build memory context blocks for system prompts.
  - Example usage:
    ```python
    from iris_memory import IrisMemory
    memory = IrisMemory()
    
    # Load past context for a user
    past_messages = memory.load_recent(user_uuid, limit=30)
    
    # Save an exchange
    memory.save_message(user_uuid, telegram_id, 'user', message, mode='chat')
    memory.save_message(user_uuid, telegram_id, 'assistant', response, mode='chat', model_used='qwen2.5:32b')
    
    # Build memory context block for system prompt
    context_block = memory.build_memory_context(user_uuid, limit=20)
    ```

This file serves as a critical component of the Mythos system, ensuring that Iris can maintain and reference conversation history effectively.
