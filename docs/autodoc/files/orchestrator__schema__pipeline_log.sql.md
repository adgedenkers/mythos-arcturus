# orchestrator/schema/pipeline_log.sql

**Language:** sql
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 139

---

### Purpose
The `pipeline_log.sql` file defines the schema for logging and tracking the execution of the Mythos pipeline, including pipeline runs, individual LLM calls, and queries executed during the DISCOVERY phase. It also creates indexes and views to facilitate efficient querying and monitoring of pipeline activities.

### Architecture
The file consists of several SQL statements that define tables, indexes, and views. The main tables are `pipeline_runs`, `pipeline_llm_calls`, and `pipeline_queries`, each capturing different aspects of the pipeline execution. Indexes are created to optimize common query patterns, and views provide aggregated and summarized information.

### Patterns
- **Entity-Relationship**: The tables represent entities in the pipeline execution process, with relationships defined through foreign keys (e.g., `run_uuid` in `pipeline_llm_calls` and `pipeline_queries` referencing `pipeline_runs`).
- **Normalization**: The schema is designed to avoid redundancy and ensure data integrity through the use of separate tables for different types of data (e.g., LLM calls and queries).

### Dependencies
- **PostgreSQL**: The file is designed to be executed in a PostgreSQL database.
- **gen_random_uuid()**: The `gen_random_uuid()` function is used to generate unique identifiers for pipeline runs.

### Interfaces
- **Tables**: The file exposes tables (`pipeline_runs`, `pipeline_llm_calls`, `pipeline_queries`) that can be queried and updated by other parts of the Mythos system.
- **Indexes**: Indexes (`idx_pipeline_runs_created`, `idx_pipeline_llm_calls_run`, etc.) are created to optimize query performance.
- **Views**: Views (`pipeline_recent`, `prompt_component_usage`) provide summarized and aggregated data for monitoring and analysis.

### Database
- **Tables**: 
  - `pipeline_runs`: Captures the overall state of pipeline runs.
  - `pipeline_llm_calls`: Logs individual LLM calls within a pipeline run.
  - `pipeline_queries`: Logs queries executed during the DISCOVERY phase.
- **Indexes**: 
  - `idx_pipeline_runs_created`: Index on `created_at` in `pipeline_runs`.
  - `idx_pipeline_llm_calls_run`: Index on `run_uuid` in `pipeline_llm_calls`.
  - `idx_pipeline_queries_run`: Index on `run_uuid` in `pipeline_queries`.
- **Views**: 
  - `pipeline_recent`: Provides a quick overview of recent pipeline runs.
  - `prompt_component_usage`: Tracks the usage of prompt components across different stages.

### Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Install Command**: The file is intended to be installed using the command `sudo -u postgres psql -d mythos -f pipeline_log.sql`.

### Key Logic
- **Pipeline Runs**: The `pipeline_runs` table captures the full state of a pipeline run, including input, processing path, registry version, timing, and output.
- **LLM Calls**: The `pipeline_llm_calls` table logs each LLM call, including the stage, model configuration, prompts, response, and timing.
- **Queries**: The `pipeline_queries` table logs queries executed during the DISCOVERY phase, including source type, query text, validation status, and results.
- **Indexes**: Indexes are created to optimize common query patterns, such as filtering by `created_at`, `speaker`, `processing_path`, and `run_uuid`.
- **Views**: The `pipeline_recent` view provides a summarized view of recent pipeline runs, while the `prompt_component_usage` view tracks the usage of prompt components.

### Integration Points
- **Mythos Pipeline**: This schema integrates with the Mythos pipeline to log and track the execution of pipeline runs, LLM calls, and queries.
- **Monitoring and Analysis**: The views (`pipeline_recent`, `prompt_component_usage`) can be used by monitoring and analysis tools to provide insights into pipeline performance and usage patterns.
- **Data Access**: The tables and views can be accessed by other components of the Mythos system for logging, querying, and reporting purposes.
