# orchestrator/src/pipeline/orchestrator.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 616

---

### File: orchestrator/src/pipeline/orchestrator.py

#### Purpose
This file orchestrates the processing of messages through a pipeline that includes stages for perception, discovery, and context fetching. It interfaces with various data sources including Ollama, PostgreSQL, and Neo4j.

#### Architecture
The file is organized into several top-level functions that handle different stages of the message processing pipeline:
1. **query_ollama**: Queries the Ollama model.
2. **run_perception**: Classifies the message using a registry-assembled prompt.
3. **run_discovery**: Fetches context based on the perception needs.
4. **_query_postgres**: Executes a PostgreSQL query.
5. **_query_neo4j**: Executes a Neo4j query.
6. **_get_neo4j_password**: Loads the Neo4j password from environment variables.
7. **_read_file**: Reads a file and truncates it to a specified number of lines.
8. **_query_financial**, **_query_calendar**, **_query_life_data**, **_query_conversations**, **_query_cosmology**, **_query_technical**, **_query_graph**: Context fetchers for different types of data.
9. **assemble_iris_prompt**: Builds the Iris prompt from the registry and discovered context.
10. **process_message**: The main entry point for processing a message through the full pipeline.

#### Patterns
- **Factory Method**: The registry loader (`RegistryLoader`) is used to assemble prompts and user messages.
- **Singleton**: The `PipelineLogger` is used to log pipeline activities, suggesting a singleton pattern for logging.
- **Observer**: The logging mechanism (`PipelineLogger`) observes and logs the stages of the pipeline.

#### Dependencies
- **Imports**: `json`, `sys`, `os`, `time`, `subprocess`, `logging`, `datetime`, `typing`, `RegistryLoader`, `PipelineLogger`.
- **External Modules**: `registry_loader` and `pipeline_logger` are imported from the `workers` directory.

#### Interfaces
- **Public Functions**: `query_ollama`, `run_perception`, `run_discovery`, `assemble_iris_prompt`, `process_message`.
- **Private Functions**: `_query_postgres`, `_query_neo4j`, `_get_neo4j_password`, `_read_file`, `_query_financial`, `_query_calendar`, `_query_life_data`, `_query_conversations`, `_query_cosmology`, `_query_technical`, `_query_graph`.

#### Database
- **PostgreSQL Tables**: `registry`, `transactions`, `calendar_events`, `life_events`, `chat_messages`.
- **Neo4j Labels**: `Exchange`, `Soul`, `System`.

#### Configuration
- **Environment Variables**: `NEO4J_PASSWORD`.
- **Configuration Files**: `.env` files in `/opt/mythos/` and `/opt/mythos/core/`.

#### Key Logic
1. **query_ollama**: Sends a message to the Ollama model and processes the response, handling JSON parsing and logging.
2. **run_perception**: Assembles a prompt from the registry, queries the Ollama model, and logs the LLM call.
3. **run_discovery**: Fetches context based on the perception needs, using various context fetchers.
4. **_query_postgres** and **_query_neo4j**: Execute database queries and log the queries to the pipeline.
5. **_get_neo4j_password**: Retrieves the Neo4j password from environment variables or `.env` files.
6. **assemble_iris_prompt**: Builds the Iris prompt using the registry and discovered context.
7. **process_message**: The main entry point that orchestrates the entire pipeline from perception to discovery.

#### Integration Points
- **RegistryLoader**: Loads prompts and model configurations from the registry.
- **PipelineLogger**: Logs pipeline activities to PostgreSQL.
- **Ollama**: Interfaces with the Ollama model for perception.
- **PostgreSQL**: Queries for financial, calendar, life data, and conversation history.
- **Neo4j**: Queries for graph-based context.

This file serves as the core orchestrator for the Mythos system, managing the flow of message processing through various stages and data sources.
