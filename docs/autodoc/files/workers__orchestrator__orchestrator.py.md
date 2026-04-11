# workers/orchestrator/orchestrator.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 616

---

### Documentation for `workers/orchestrator/orchestrator.py`

#### Purpose
This file orchestrates the processing of messages through a pipeline that includes perception, discovery, and context fetching, ultimately building a prompt for further processing. It integrates with Ollama, PostgreSQL, and Neo4j to fetch and process data.

#### Architecture
The file contains several functions that handle different stages of the message processing pipeline:
1. **LLM Interface**: Functions to interact with Ollama.
2. **Stages**: Functions for perception and discovery stages.
3. **Database Queries**: Functions to query PostgreSQL and Neo4j.
4. **Helper Functions**: Functions for reading files and fetching context.

The main entry point is `process_message`, which orchestrates the entire pipeline.

#### Patterns
- **Singleton**: The `RegistryLoader` and `PipelineLogger` are used as singletons to manage the registry and logging.
- **Factory**: The `RegistryLoader` is used to assemble prompts and user messages based on the registry.

#### Dependencies
- **Standard Libraries**: `json`, `sys`, `os`, `time`, `subprocess`, `logging`, `datetime`, `typing`.
- **Custom Modules**: `registry_loader`, `pipeline_logger`.
- **External Libraries**: `psycopg2` for PostgreSQL interactions.

#### Interfaces
- **Public Functions**:
  - `query_ollama`: Queries Ollama and returns the response.
  - `run_perception`: Classifies the message using a registry-assembled prompt.
  - `run_discovery`: Fetches context based on perception needs.
  - `assemble_iris_prompt`: Builds an Iris prompt from the registry and discovered context.
  - `process_message`: Main entry point to process a message through the full pipeline.

#### Database
- **PostgreSQL Tables**: `registry`, `transactions`, `calendar_events`, `life_events`, `chat_messages`.
- **Neo4j Labels**: `Exchange`, `Soul`, `System`.

#### Configuration
- **Environment Variables**: `NEO4J_PASSWORD` for Neo4j password.
- **Configuration Files**: `/opt/mythos/.env`, `/opt/mythos/core/.env` for Neo4j password fallback.

#### Key Logic
- **Perception**: Uses Ollama to classify messages based on a registry-assembled prompt.
- **Discovery**: Fetches context based on flags from the perception stage.
- **Database Queries**: Executes queries to PostgreSQL and Neo4j to fetch context data.
- **Logging**: Logs all LLM calls and database queries to a pipeline logger.

#### Integration Points
- **Ollama**: For LLM interactions.
- **RegistryLoader**: For assembling prompts and user messages.
- **PipelineLogger**: For logging LLM calls and database queries.
- **PostgreSQL**: For fetching financial, calendar, life, and conversation data.
- **Neo4j**: For fetching graph data.

### Detailed Function Descriptions

#### `query_ollama`
- **Purpose**: Queries Ollama and returns the parsed response, elapsed time, and raw response.
- **Arguments**: `model`, `system`, `user_msg`, `temperature`, `num_predict`, `timeout`.
- **Logic**: Uses `subprocess` to call Ollama via `curl`, parses the JSON response, and logs the call.

#### `run_perception`
- **Purpose**: Classifies the message using a registry-assembled prompt.
- **Arguments**: `speaker`, `message`, `gap_description`, `run_uuid`.
- **Logic**: Assembles the prompt from the registry, queries Ollama, and logs the LLM call.

#### `run_discovery`
- **Purpose**: Fetches context based on perception needs.
- **Arguments**: `perception`, `original_message`, `run_uuid`.
- **Logic**: Checks active flags and fetches context using various `_query_*` functions.

#### `_query_postgres`
- **Purpose**: Executes a PostgreSQL query and logs the call.
- **Arguments**: `sql`, `params`, `run_uuid`, `intent`.
- **Logic**: Connects to PostgreSQL, executes the query, and logs the call.

#### `_query_neo4j`
- **Purpose**: Executes a Neo4j query and logs the call.
- **Arguments**: `cypher`, `run_uuid`, `intent`.
- **Logic**: Uses `subprocess` to call `cypher-shell`, executes the query, and logs the call.

#### `_get_neo4j_password`
- **Purpose**: Loads the Neo4j password from the environment or configuration files.
- **Arguments**: None.
- **Logic**: Checks environment variables and configuration files for the password.

#### `_read_file`
- **Purpose**: Reads a file, truncated to a maximum number of lines.
- **Arguments**: `path`, `max_lines`.
- **Logic**: Reads the file and truncates it if necessary.

#### `_query_financial`, `_query_calendar`, `_query_life_data`, `_query_conversations`, `_query_cosmology`, `_query_technical`, `_query_graph`
- **Purpose**: Fetches specific context data from PostgreSQL and Neo4j.
- **Arguments**: `perception`, `message`, `run_uuid`.
- **Logic**: Executes specific queries to fetch financial, calendar, life, conversation, cosmology, technical, and graph data.

#### `assemble_iris_prompt`
- **Purpose**: Builds an Iris prompt from the registry and discovered context.
- **Arguments**: `perception`, `context`, `original_message`, `speaker`.
- **Logic**: Assembles the prompt from the registry and context data.

#### `process_message`
- **Purpose**: Main entry point to process a message through the full pipeline.
- **Arguments**: `speaker`, `message`, `gap_description`.
- **Logic**: Orchestrates the perception, discovery, and Iris prompt building stages.

This file is a critical component of the Mythos system, handling the core logic for message processing and context fetching.
