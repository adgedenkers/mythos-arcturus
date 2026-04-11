# workers/schema/pipeline_log.sql

**Language:** sql
**Stream:** SYS
**Module:** Background Workers
**Lines:** 139

---

### Documentation for `workers/schema/pipeline_log.sql`

#### Purpose
This SQL file defines the schema for logging the execution of the consciousness pipeline in the Mythos system. It captures detailed information about each pipeline run, including individual LLM calls and queries executed during the DISCOVERY phase.

#### Architecture
The schema consists of four main tables and two views:
1. **pipeline_runs**: Captures the overall state of each pipeline run.
2. **pipeline_llm_calls**: Logs individual LLM calls within a pipeline run.
3. **pipeline_queries**: Logs queries executed during the DISCOVERY phase.
4. **Indexes**: Created for efficient querying of the tables.
5. **pipeline_recent**: A view providing a quick overview of recent pipeline runs.
6. **prompt_component_usage**: A view tracking the usage of prompt components.

#### Patterns
- **Entity-Relationship Pattern**: The tables represent entities and their relationships.
- **View Pattern**: The views provide aggregated and summarized data for easier analysis.

#### Dependencies
- **PostgreSQL**: The SQL file is designed to be executed in a PostgreSQL database.
- **UUID Generation**: Uses `gen_random_uuid()` for generating unique identifiers.

#### Interfaces
- **Tables**: Exposes tables for insertion and querying pipeline run data.
- **Views**: Provides views for quick overviews and usage tracking.

#### Database
- **Tables**:
  - `pipeline_runs`: Stores overall pipeline run information.
  - `pipeline_llm_calls`: Stores individual LLM call details.
  - `pipeline_queries`: Stores DISCOVERY phase query details.
- **Indexes**:
  - `idx_pipeline_runs_created`, `idx_pipeline_runs_speaker`, `idx_pipeline_runs_path`, `idx_pipeline_runs_registry`: Indexes for efficient querying of `pipeline_runs`.
  - `idx_pipeline_llm_calls_run`, `idx_pipeline_llm_calls_stage`: Indexes for efficient querying of `pipeline_llm_calls`.
  - `idx_pipeline_queries_run`: Index for efficient querying of `pipeline_queries`.
- **Views**:
  - `pipeline_recent`: Provides a quick overview of recent pipeline runs.
  - `prompt_component_usage`: Tracks the usage of prompt components.

#### Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Configuration Files**: No specific configuration files are used in this file.

#### Key Logic
- **Pipeline Runs**: Captures the full state of each pipeline run, including input, processing path, timing, and output.
- **LLM Calls**: Logs each LLM call within a pipeline run, including the stage, model configuration, prompts, and responses.
- **Queries**: Logs each query executed during the DISCOVERY phase, including source type, query text, validation status, and results.
- **Indexes**: Ensures efficient querying of pipeline run data.
- **Views**: Provides summarized and aggregated data for easier analysis.

#### Integration Points
- **Mythos Subsystems**:
  - **Consciousness Pipeline**: Logs the execution of the pipeline.
  - **DISCOVERY**: Logs queries executed during the DISCOVERY phase.
  - **LLM Integration**: Logs individual LLM calls.
  - **Data Analysis**: Provides views for analyzing pipeline run data.

This schema is integral to the Mythos system, providing a comprehensive logging mechanism for the consciousness pipeline, enabling detailed analysis and auditing of pipeline executions.
