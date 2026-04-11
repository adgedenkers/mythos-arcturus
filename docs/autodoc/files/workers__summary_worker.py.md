# workers/summary_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 248

---

### Documentation for `workers/summary_worker.py`

#### 1. Purpose
The `summary_worker.py` file is responsible for rebuilding conversation summaries (Tier 1 and Tier 2) when triggered. It retrieves messages from a PostgreSQL database, generates summaries using a language model (LLM), and stores the summaries back into the database.

#### 2. Architecture
The file consists of several top-level functions:
- `get_db`: Establishes a connection to the PostgreSQL database.
- `get_messages_for_summary`: Retrieves messages within a specified range for summarization.
- `generate_summary`: Generates a summary of the messages using an LLM.
- `store_summary`: Stores the generated summary in the database.
- `process_summary`: The main entry point that orchestrates the summarization process.

#### 3. Patterns
- **Singleton Pattern**: The `get_db` function can be considered a singleton as it ensures a single database connection is used throughout the file.
- **Factory Pattern**: The `generate_summary` function can be seen as a factory method that creates and returns a summary based on the input messages and tier.

#### 4. Dependencies
- **Imports**: `os`, `json`, `logging`, `requests`, `psycopg2`, `dotenv`, `typing`, `datetime`
- **Environment Variables**: `OLLAMA_HOST`, `OLLAMA_MODEL`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

#### 5. Interfaces
- **Exposed Functions**: 
  - `get_db`: Returns a database connection.
  - `get_messages_for_summary`: Retrieves messages for summarization.
  - `generate_summary`: Generates a summary using an LLM.
  - `store_summary`: Stores the summary in the database.
  - `process_summary`: Main entry point for the summarization process.

#### 6. Database
- **Tables/Labels**: 
  - `chat_messages`: Stores individual chat messages.
  - `conversation_summaries`: Stores conversation summaries, including metadata like `summary_text`, `themes`, `emotional_tone`, `context_notes`, `key_entities`, `original_tokens`, `summary_tokens`, `compression_ratio`.

#### 7. Configuration
- **Environment Variables**: 
  - `OLLAMA_HOST`: Host for the LLM service.
  - `OLLAMA_MODEL`: Model to use for LLM generation.
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL database connection details.

#### 8. Key Logic
- **Message Retrieval**: The `get_messages_for_summary` function retrieves messages from the `chat_messages` table based on a specified range.
- **Summary Generation**: The `generate_summary` function formats the messages into a prompt and sends it to the LLM service to generate a summary.
- **Summary Storage**: The `store_summary` function updates the `conversation_summaries` table with the new summary, marking the old summary as superseded.

#### 9. Integration Points
- **Database Integration**: The worker interacts with the PostgreSQL database to retrieve messages and store summaries.
- **LLM Integration**: The worker sends requests to the LLM service to generate summaries.
- **Worker Entry Point**: The `process_summary` function is the main entry point, which is likely triggered by a task queue or a scheduled job.

### Detailed Function Descriptions

#### `get_db`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `psycopg2`, environment variables for database credentials.

#### `get_messages_for_summary`
- **Purpose**: Retrieves messages within a specified range for summarization.
- **Dependencies**: `get_db`, `psycopg2`.
- **Database Interaction**: Queries the `chat_messages` table to retrieve messages based on the conversation ID and message index range.

#### `generate_summary`
- **Purpose**: Generates a summary of the messages using an LLM.
- **Dependencies**: `requests`, `json`, `logging`, environment variables for LLM service details.
- **Logic**: Formats the messages into a prompt and sends it to the LLM service to generate a summary.

#### `store_summary`
- **Purpose**: Stores the generated summary in the database.
- **Dependencies**: `get_db`, `psycopg2`.
- **Database Interaction**: Updates the `conversation_summaries` table with the new summary, marking the old summary as superseded.

#### `process_summary`
- **Purpose**: The main entry point that orchestrates the summarization process.
- **Dependencies**: `get_messages_for_summary`, `generate_summary`, `store_summary`.
- **Logic**: Retrieves messages, generates a summary, and stores the summary in the database. Returns a status indicating the success or failure of the process.
