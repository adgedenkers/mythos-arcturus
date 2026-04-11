# orchestrator/src/logging/pipeline_logger.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 170

---

### File: `orchestrator/src/logging/pipeline_logger.py`

#### Purpose
This file provides a logging mechanism for the Mythos system, specifically for recording pipeline runs, LLM calls, and queries to a PostgreSQL database. It ensures that every run, LLM call, and query is logged with detailed information for later inspection and replay.

#### Architecture
The file contains a single class, `PipelineLogger`, which is responsible for logging various stages of pipeline runs. The class has several methods for different logging operations:
- `__init__`: Initializes the logger with database connection details.
- `_conn`: Establishes a connection to the PostgreSQL database.
- `start_run`: Logs the start of a new pipeline run.
- `log_llm_call`: Logs an individual LLM call within a run.
- `log_query`: Logs a DISCOVERY query.
- `finish_run`: Updates the run with final results.
- `recent_runs`: Fetches recent pipeline runs for inspection.

#### Patterns
- **Singleton Pattern**: The `PipelineLogger` class can be considered a singleton as it is intended to be instantiated once and reused throughout the application.
- **Database Connection Management**: The `_conn` method manages database connections, ensuring they are properly closed after use.

#### Dependencies
- `json`: For serializing and deserializing JSON data.
- `uuid`: For generating unique identifiers.
- `psycopg2`: For connecting to and interacting with the PostgreSQL database.
- `logging`: For logging errors and informational messages.
- `datetime`: For handling date and time operations.
- `typing`: For type hints.

#### Interfaces
The `PipelineLogger` class exposes the following methods:
- `start_run`: Starts a new pipeline run and returns a unique run identifier.
- `log_llm_call`: Logs an individual LLM call within a run.
- `log_query`: Logs a DISCOVERY query.
- `finish_run`: Updates the run with final results.
- `recent_runs`: Fetches recent pipeline runs for inspection.

#### Database
The file interacts with the following PostgreSQL tables:
- `pipeline_runs`: Stores information about pipeline runs.
- `pipeline_llm_calls`: Logs individual LLM calls within a run.
- `pipeline_queries`: Logs DISCOVERY queries.

#### Configuration
The class is initialized with default database connection details (`dbname="mythos", user="adge"`). These can be overridden when creating an instance of `PipelineLogger`.

#### Key Logic
- **Logging Pipeline Runs**: The `start_run` method inserts a new entry into the `pipeline_runs` table.
- **Logging LLM Calls**: The `log_llm_call` method inserts detailed information about each LLM call into the `pipeline_llm_calls` table.
- **Logging Queries**: The `log_query` method logs DISCOVERY queries into the `pipeline_queries` table.
- **Updating Final Results**: The `finish_run` method updates the `pipeline_runs` table with final results and metadata.
- **Fetching Recent Runs**: The `recent_runs` method retrieves recent pipeline runs for inspection.

#### Integration Points
- **Orchestrator**: The `PipelineLogger` class is likely used by the orchestrator to log pipeline runs, LLM calls, and queries.
- **Database**: The class interacts directly with the PostgreSQL database to store and retrieve logging information.

### Example Usage
```python
from pipeline_logger import PipelineLogger

logger = PipelineLogger()
run_uuid = logger.start_run(speaker, message, gap_description, processing_path, registry_version)
logger.log_llm_call(run_uuid, stage, model, temperature, system_prompt, user_prompt, ...)
logger.log_query(run_uuid, source_type, intent, query_text, ...)
logger.finish_run(run_uuid, iris_response, total_elapsed_ms, perception, discovery)
```

This file serves as a critical component for maintaining a detailed log of pipeline activities, ensuring that all operations are traceable and reproducible.
