# api/integration_example.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 226

---

### Documentation for `api/integration_example.py`

#### 1. Purpose
This file serves as a reference guide for integrating the orchestrator and context manager into an existing FastAPI application (`main.py`). It provides step-by-step instructions and code snippets for modifying the application to include asynchronous task dispatching and context management functionalities.

#### 2. Architecture
The file is structured into several sections, each detailing a specific step in the integration process:
- **Step 1**: Adds necessary imports.
- **Step 2**: Initializes the orchestrator and context manager.
- **Step 3**: Modifies the `/message` endpoint to include context management and asynchronous task dispatching.
- **Step 4**: Adds an endpoint to retrieve orchestrator statistics.
- **Step 5**: Adds an endpoint to manually trigger summary rebuilds.
- **Helper Functions**: Provides utility functions for database interactions.

#### 3. Patterns
- **Factory Pattern**: The `get_orchestrator` function acts as a factory to create an instance of the `Orchestrator`.
- **Singleton Pattern**: The `Orchestrator` and `ContextManager` are initialized once and reused throughout the application.
- **Dependency Injection**: The `ContextManager` and `Orchestrator` are passed as dependencies to the `/message` endpoint.

#### 4. Dependencies
- **Imports**:
  - `fastapi`: For `BackgroundTasks`.
  - `api.orchestrator`: For `get_orchestrator` and `Orchestrator`.
  - `api.context_manager`: For `ContextManager`.
  - `qdrant_client`: For initializing the Qdrant client.
  - `get_db_connection`: Function to get a database connection.
  - `neo4j_driver`: Neo4j driver instance.
  - `verify_api_key`: Function to verify API keys.
  - `generate_llm_response`: Function to generate LLM responses.
  - `store_message`: Function to store messages in the database.
  - `get_message_count`: Function to get message counts.
  - `get_user_uuid_from_conversation`: Function to get user UUID from a conversation.

#### 5. Interfaces
- **Endpoints**:
  - `/message`: Handles message processing and dispatches asynchronous tasks.
  - `/orchestrator/stats`: Retrieves orchestrator statistics.
  - `/conversation/{conversation_id}/rebuild-summaries`: Manually triggers summary rebuilds for a conversation.

#### 6. Database
- **Tables/Lables**:
  - `chat_messages`: Stores messages with fields like `conversation_id`, `user_uuid`, `role`, and `content`.
  - `Qdrant`: Used for vector storage and retrieval.

#### 7. Configuration
- **Environment Variables**:
  - No specific environment variables are used directly in this file, but the `QdrantClient` initialization assumes `localhost` and `6333` as default values.

#### 8. Key Logic
- **Message Handling**:
  - Stores user messages in the database.
  - Assembles context for LLM using `ContextManager`.
  - Generates LLM responses.
  - Stores assistant responses in the database.
  - Dispatches asynchronous tasks for message extraction and summary rebuilds.

- **Orchestrator Statistics**:
  - Retrieves and returns orchestrator statistics.

- **Summary Rebuilds**:
  - Manually triggers summary rebuilds for a conversation.

#### 9. Integration Points
- **Orchestrator**:
  - `get_orchestrator()`: Initializes the orchestrator.
  - `orchestrator.dispatch_message_extraction()`: Dispatches message extraction tasks.
  - `orchestrator.check_summary_triggers()`: Checks if summary rebuilds are needed.
  - `orchestrator.dispatch_summary_rebuild()`: Dispatches summary rebuild tasks.
  - `orchestrator.get_stats()`: Retrieves orchestrator statistics.

- **Context Manager**:
  - `context_manager.assemble_context()`: Assembles context for LLM.
  - `context_manager.format_context_for_llm()`: Formats context for LLM.

- **Database**:
  - `get_db_connection()`: Provides a database connection.
  - `store_message()`: Stores messages in the database.
  - `get_message_count()`: Retrieves message counts.
  - `get_user_uuid_from_conversation()`: Retrieves user UUID from a conversation.

- **Qdrant Client**:
  - `QdrantClient(host="localhost", port=6333)`: Initializes the Qdrant client.

This file serves as a comprehensive guide for integrating the orchestrator and context manager into the main application, ensuring that all necessary components are properly initialized and utilized.
