# core/conversation_bridge.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 389

---

### File: core/conversation_bridge.py

#### Purpose
The `conversation_bridge.py` file is responsible for extracting structured knowledge from chat exchanges and logging them into a Neo4j graph database. It provides methods to ensure the connection to Neo4j, extract relevant information from user and assistant messages, and log these exchanges into the graph.

#### Architecture
The file consists of a single class `ConversationBridge` and a top-level function `extract_fast`. The `ConversationBridge` class handles the connection to Neo4j and provides methods to log exchanges and retrieve conversation knowledge. The `extract_fast` function performs fast keyword-based extraction from user and assistant messages.

#### Patterns
- **Singleton Pattern**: The `ConversationBridge` class ensures a single connection to Neo4j through the `_connect` and `_ensure_connected` methods.
- **Factory Pattern**: The `extract_fast` function acts as a factory for extracting structured knowledge from messages.

#### Dependencies
- **Standard Libraries**: `os`, `re`, `json`, `uuid`, `logging`, `datetime`, `typing`
- **External Libraries**: `neo4j`, `dotenv`

#### Interfaces
- **Public Methods**:
  - `log_exchange`: Logs a complete exchange (user + assistant) to the Neo4j graph.
  - `get_conversation_knowledge`: Retrieves structured knowledge about a conversation from the graph.
  - `close`: Closes the Neo4j connection.
- **Private Methods**:
  - `_connect`: Establishes a connection to Neo4j.
  - `_ensure_connected`: Ensures the Neo4j connection is active.
- **Top-level Functions**:
  - `extract_fast`: Performs fast keyword-based extraction from messages.

#### Database
- **Neo4j Labels and Relationships**:
  - Labels: `Conversation`, `Exchange`, `Person`, `GridNode`, `Topic`, `System`
  - Relationships: `CONTAINS`, `FOLLOWED_BY`, `DISCUSSED`, `HAS_THEME`, `INVOLVES`, `ACTIVATED`, `HAD_CONVERSATION`

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Configuration for Neo4j connection.
  - `OLLAMA_HOST`, `OLLAMA_MODEL`: Configuration for Ollama (optional deep extraction).

#### Key Logic
- **Fast Extraction**: The `extract_fast` function uses keyword matching to extract topics, entities, systems, and grid activations from user and assistant messages.
- **Logging Exchanges**: The `log_exchange` method logs the extracted information into Neo4j, creating or updating nodes and relationships for `Conversation`, `Exchange`, `Topic`, `Theme`, and `Entities`.

#### Integration Points
- **IrisMemory**: The `ConversationBridge` is designed to integrate with the `IrisMemory` subsystem, which saves chat messages to a PostgreSQL database. After each exchange is saved, `ConversationBridge` extracts and logs the knowledge into Neo4j.
- **Ollama**: The file is designed to optionally integrate with Ollama for deep extraction, though this feature is currently disabled.

### Detailed Documentation

#### Class: `ConversationBridge`
- **Purpose**: Manages the connection to Neo4j and provides methods to log and retrieve conversation knowledge.
- **Methods**:
  - `__init__`: Initializes the class and connects to Neo4j.
  - `_connect`: Establishes a connection to Neo4j.
  - `_ensure_connected`: Ensures the Neo4j connection is active.
  - `log_exchange`: Logs a complete exchange to Neo4j, including user and assistant messages, and extracted knowledge.
  - `get_conversation_knowledge`: Retrieves structured knowledge about a conversation from the graph.
  - `close`: Closes the Neo4j connection.

#### Top-level Function: `extract_fast`
- **Purpose**: Performs fast keyword-based extraction from user and assistant messages.
- **Parameters**:
  - `user_message`: The user's message.
  - `assistant_response`: The assistant's response.
- **Returns**: A dictionary containing extracted topics, entities, systems, grid activations, and other metadata.

### Example Usage
```python
from conversation_bridge import ConversationBridge

bridge = ConversationBridge()
exchange_id = bridge.log_exchange(
    conversation_id="chat-d01f9f28-20260226110114",
    user_uuid="d01f9f28-...",
    telegram_id=7811548479,
    user_message="How's the finance system looking?",
    assistant_response="The imports are clean. 847 transactions loaded.",
    model_used="qwen3:30b-a3b",
    response_time_ms=1200,
)
```

This example demonstrates how to use the `ConversationBridge` to log a chat exchange and extract relevant knowledge into the Neo4j graph.
