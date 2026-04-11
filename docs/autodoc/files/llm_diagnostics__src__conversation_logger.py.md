# llm_diagnostics/src/conversation_logger.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 170

---

### Documentation for `llm_diagnostics/src/conversation_logger.py`

#### Purpose
This file is responsible for logging conversations between users and the LLM (Language Model) to Neo4j for audit and learning purposes. It also provides functionality to retrieve conversation histories and recent conversations.

#### Architecture
The file consists of four main functions:
1. `log_conversation`: Logs a conversation to Neo4j.
2. `_create_conversation_node`: Helper function to create a conversation node in Neo4j.
3. `get_conversation_history`: Retrieves the conversation history for a specific conversation ID.
4. `get_recent_conversations`: Retrieves recent conversations for analysis.

The file uses the `neo4j` library to interact with the Neo4j database and `os` and `uuid` for environment variables and UUID generation, respectively.

#### Patterns
- **Singleton Pattern**: The Neo4j driver connection is established and closed within each function, ensuring that the connection is only active when needed.
- **Helper Function**: `_create_conversation_node` is a helper function used within `log_conversation` to encapsulate the logic for creating a conversation node.

#### Dependencies
- `os`: For accessing environment variables.
- `uuid`: For generating unique IDs.
- `datetime`: For handling timestamps.
- `typing`: For type annotations.
- `neo4j`: For interacting with the Neo4j database.
- `json`: For handling metadata as a string.

#### Interfaces
- `log_conversation`: Exposes a function to log a conversation to Neo4j.
- `get_conversation_history`: Exposes a function to retrieve the conversation history for a given conversation ID.
- `get_recent_conversations`: Exposes a function to retrieve recent conversations for analysis.

#### Database
- **Neo4j Labels and Relationships**:
  - `Conversation`: Node representing a conversation.
  - `Service`: Node representing a service mentioned in the conversation.
  - `Event`: Node representing an event referenced in the conversation.
  - `HAD_CONVERSATION`: Relationship between `System` and `Conversation`.
  - `MENTIONED`: Relationship between `Conversation` and `Service`.
  - `REFERENCED`: Relationship between `Conversation` and `Event`.

#### Configuration
- Environment variables:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.

#### Key Logic
- **Logging Conversations**:
  - The `log_conversation` function logs a conversation to Neo4j by creating a `Conversation` node and linking it to relevant `Service` and `Event` nodes.
  - The `_create_conversation_node` function creates a `Conversation` node and establishes relationships with `Service` and `Event` nodes based on the content of the conversation.

- **Retrieving Conversations**:
  - The `get_conversation_history` function retrieves the conversation history for a specific conversation ID.
  - The `get_recent_conversations` function retrieves recent conversations based on a specified time window.

#### Integration Points
- **Neo4j Integration**: The file integrates with Neo4j to log and retrieve conversations. It uses the `neo4j` library to establish a connection, execute queries, and manage transactions.
- **Environment Variables**: The file relies on environment variables for database connection details, ensuring that the database connection is configurable.

### Detailed Function Descriptions

#### `log_conversation`
- **Purpose**: Logs a conversation to Neo4j.
- **Parameters**:
  - `question`: User's question.
  - `answer`: LLM's answer.
  - `tools_used`: List of diagnostic tools used.
  - `conversation_id`: Optional conversation ID for threading.
  - `metadata`: Optional additional metadata.
- **Returns**: The conversation ID.
- **Logic**: Establishes a connection to Neo4j, creates a conversation node, and establishes relationships with relevant nodes.

#### `_create_conversation_node`
- **Purpose**: Creates a conversation node in Neo4j.
- **Parameters**:
  - `tx`: Neo4j transaction object.
  - `conv_id`: Conversation ID.
  - `question`: User's question.
  - `answer`: LLM's answer.
  - `tools_used`: List of diagnostic tools used.
  - `metadata`: Additional metadata.
- **Logic**: Creates a `Conversation` node and establishes relationships with `Service` and `Event` nodes based on the content of the conversation.

#### `get_conversation_history`
- **Purpose**: Retrieves the conversation history for a specific conversation ID.
- **Parameters**:
  - `conversation_id`: ID of the conversation.
  - `limit`: Number of records to retrieve.
- **Returns**: List of dictionaries containing conversation details.
- **Logic**: Executes a Neo4j query to retrieve the conversation history for the specified conversation ID.

#### `get_recent_conversations`
- **Purpose**: Retrieves recent conversations for analysis.
- **Parameters**:
  - `hours`: Time window in hours.
  - `limit`: Number of records to retrieve.
- **Returns**: List of dictionaries containing recent conversation details.
- **Logic**: Executes a Neo4j query to retrieve recent conversations based on the specified time window.

This documentation provides a comprehensive overview of the `conversation_logger.py` file, detailing its purpose, architecture, dependencies, interfaces, and key logic.
