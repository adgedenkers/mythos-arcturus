# migrations/migration_0186_conversation_metadata.sql

**Language:** sql
**Stream:** SYS
**Module:** Database Migrations
**Lines:** 274

---

### Purpose
The `migration_0186_conversation_metadata.sql` file is a PostgreSQL migration script that defines the schema for storing conversation metadata within the Mythos system. It includes the creation of tables, enums, indexes, and a trigger function to support full-text search capabilities.

### Architecture
The file is structured into several sections:
1. **Extensions**: It creates or ensures the existence of necessary PostgreSQL extensions (`pgcrypto` and `citext`).
2. **Enums**: It defines two enums (`conversation_type` and `initiator_type`) used to categorize conversations and their initiators.
3. **Tables**:
   - `conversations`: The core table containing detailed metadata about each conversation.
   - `conversation_participants`: A normalized table for participants in conversations.
   - `conversation_turns`: A table for individual turns within a conversation.
   - `thread_groups`: A table for clustering related conversations.
   - `spiral_epochs`: A table for personal time anchors.
4. **Indexes**: Multiple indexes are created to optimize queries on various fields.
5. **Trigger Function**: A function (`conversations_search_doc_update`) is created to update the full-text search vector for each conversation.

### Patterns
- **Singleton**: The creation of enums and extensions ensures they exist only once (`CREATE EXTENSION IF NOT EXISTS` and `CREATE TYPE ... EXCEPTION WHEN duplicate_object`).
- **Normalization**: The `conversation_participants` and `conversation_turns` tables are normalized to avoid redundancy and improve query performance.

### Dependencies
- **PostgreSQL Extensions**: `pgcrypto` and `citext`.
- **Enums**: `conversation_type` and `initiator_type`.

### Interfaces
- **Tables**: The file exposes several tables (`conversations`, `conversation_participants`, `conversation_turns`, `thread_groups`, `spiral_epochs`) that other parts of the system can interact with.
- **Indexes**: Various indexes are created to optimize querying these tables.
- **Trigger Function**: The `conversations_search_doc_update` function is used to maintain the full-text search vector.

### Database
- **Tables**:
  - `conversations`: Stores detailed metadata about each conversation.
  - `conversation_participants`: Stores participants in conversations.
  - `conversation_turns`: Stores individual turns within a conversation.
  - `thread_groups`: Stores clustering information for related conversations.
  - `spiral_epochs`: Stores personal time anchors.
- **Indexes**: Multiple indexes are created on the `conversations` table to optimize querying.

### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Configuration Files**: No configuration files are referenced.

### Key Logic
- **Core Table Logic**: The `conversations` table is the central repository for all conversation metadata, including raw logs, summaries, decisions, and actions.
- **Full-Text Search**: The `conversations_search_doc_update` function constructs a weighted search vector for full-text search capabilities.
- **Normalization**: The `conversation_participants` and `conversation_turns` tables are normalized to store participant and turn information, respectively.

### Integration Points
- **Neo4j**: The `edges` field in the `conversations` table provides hints for graph edges, which are canonical in Neo4j.
- **FastAPI**: The tables and indexes created here are likely to be queried by FastAPI endpoints for various operations.
- **Ollama**: The `raw_payload` field in the `conversations` table stores raw logs, which could be ingested from Ollama.
- **Redis**: Not directly referenced, but Redis might be used for caching or other auxiliary operations.

This migration script sets up the foundational schema for storing and querying conversation metadata within the Mythos system, ensuring efficient data storage and retrieval.
