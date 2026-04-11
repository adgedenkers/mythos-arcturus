# workers/pipeline_logger.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 170

---

### Documentation for `workers/pipeline_logger.py`

#### Purpose
The `PipelineLogger` class in `pipeline_logger.py` is responsible for logging every pipeline run, LLM call, and query to a PostgreSQL database. It captures full prompt state to ensure any response can be replayed.

#### Architecture
- **Class**: `PipelineLogger`
  - **Methods**:
    - `__init__`: Initializes the logger with database connection details.
    - `_conn`: Establishes a connection to the PostgreSQL database.
    - `start_run`: Creates a new pipeline run and returns a unique run UUID.
    - `log_llm_call`: Logs an individual LLM call within a run.
    - `log_query`: Logs a DISCOVERY query.
    - `finish_run`: Updates the run with final results.
    - `recent_runs`: Fetches recent pipeline runs for inspection.

#### Patterns
- **Singleton Pattern**: The `PipelineLogger` class can be instantiated once and reused, but it does not enforce singleton behavior explicitly.
- **Database Connection**: Uses a simple connection method `_conn` to manage database connections.

#### Dependencies
- **Imports**:
  - `json`: For handling JSON serialization.
  - `uuid`: For generating unique identifiers.
  - `psycopg2`: For PostgreSQL database operations.
  - `logging`: For logging errors and information.
  - `datetime`: For handling date and time operations.
  - `typing`: For type hints.

#### Interfaces
- **Public Methods**:
  - `start_run`: Initiates a new pipeline run.
  - `log_llm_call`: Logs an LLM call.
  - `log_query`: Logs a DISCOVERY query.
  - `finish_run`: Updates the run with final results.
  - `recent_runs`: Fetches recent pipeline runs.

#### Database
- **Tables**:
  - `pipeline_runs`: Stores information about pipeline runs.
  - `pipeline_llm_calls`: Logs individual LLM calls.
  - `pipeline_queries`: Logs DISCOVERY queries.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.
- **Initialization Parameters**:
  - `dbname`: Database name (default: "mythos").
  - `user`: Database user (default: "adge").

#### Key Logic
- **start_run**:
  - Inserts a new record into `pipeline_runs` with details about the run.
  - Returns a unique run UUID.
- **log_llm_call**:
  - Logs an individual LLM call by inserting a record into `pipeline_llm_calls`.
  - Serializes `prompt_components` and `parsed_response` to JSON.
- **log_query**:
  - Logs a DISCOVERY query by inserting a record into `pipeline_queries`.
- **finish_run**:
  - Updates the `pipeline_runs` table with final results.
  - Serializes `perception` and `discovery` to JSON.
- **recent_runs**:
  - Fetches recent pipeline runs from `pipeline_runs` and returns them.

#### Integration Points
- **Mythos Subsystems**:
  - **Orchestrator**: Initiates pipeline runs and logs LLM calls and queries.
  - **LLM Services**: Logs individual LLM calls.
  - **DISCOVERY**: Logs queries.
  - **Database**: Stores and retrieves pipeline run data.

### Example Usage
```python
from workers.pipeline_logger import PipelineLogger

logger = PipelineLogger()
run_uuid = logger.start_run(speaker="Alice", message="Hello", gap_description="Gap 1", processing_path="path1", registry_version="v1")
logger.log_llm_call(run_uuid, stage="initial", model="gpt-3.5", temperature=0.7, system_prompt="System", user_prompt="User", prompt_components={}, raw_response="Raw", parsed_response="Parsed", elapsed_ms=100)
logger.log_query(run_uuid, source_type="source1", intent="intent1", query_text="Query", validated=True, validator_approved=True, corrected_query="Corrected", risk_level="low", rows_returned=10, result_summary="Summary", elapsed_ms=50)
logger.finish_run(run_uuid, iris_response="Iris", total_elapsed_ms=200, processing_path="path1", perception="Perception", discovery="Discovery")
```

This file is crucial for maintaining a detailed log of all pipeline activities, ensuring traceability and replayability of AI interactions within the Mythos system.
