# orchestrator/benchmark/run_benchmark.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 667

---

### File: `orchestrator/benchmark/run_benchmark.py`

#### Purpose
This file contains the logic for running a benchmark suite across multiple AI models using the Ollama API. It manages dependencies, records results, and scores responses using a judge model.

#### Architecture
The file is organized into several classes and functions:
- **Classes:**
  - `JSONLWriter`: Manages thread-safe writing to JSONL files.
  - `RunManager`: Manages the overall run, including initialization, writing manifests, and summaries.
  - `DependencyResolver`: Tracks dependencies for tasks and models to determine if a task is runnable.
- **Functions:**
  - `call_ollama`: Calls the Ollama API with a given model and prompt.
  - `judge_response`: Scores a response using a judge model.
  - `run_task_for_model`: Runs a single task for a single model.
  - `build_execution_waves`: Topologically sorts tasks into execution waves.
  - `run_benchmark`: Main function to orchestrate the benchmark run.
  - `_build_summary`: Builds a summary of the run.
  - `main`: Entry point for the script.

#### Patterns
- **Singleton**: `RunManager` and `DependencyResolver` are used as singletons within the context of a run.
- **Observer**: `DependencyResolver` observes the status of tasks and models to determine if a task is runnable.

#### Dependencies
- **Imports**: `os`, `sys`, `json`, `uuid`, `time`, `logging`, `argparse`, `threading`, `subprocess`, `requests`, `datetime`, `concurrent.futures`, `pathlib`, `typing`.
- **External Services**: Ollama API for model interactions.

#### Interfaces
- **Public Functions**:
  - `call_ollama`: Exposes the Ollama API call.
  - `judge_response`: Scores a response.
  - `run_task_for_model`: Runs a single task for a model.
  - `build_execution_waves`: Topologically sorts tasks.
  - `run_benchmark`: Orchestrates the benchmark run.
  - `_build_summary`: Builds a summary of the run.
  - `main`: Entry point for the script.

#### Database
- **PostgreSQL Tables**: `datetime`, `concurrent`, `pathlib`, `typing`, `tasks`.
- **Neo4j Labels**: None.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: `CONFIG` is populated from a configuration file or command-line arguments.

#### Key Logic
- **Dependency Resolution**: `DependencyResolver` tracks dependencies and determines if a task is runnable.
- **Task Execution**: `run_task_for_model` executes a task for a model, checks for expected keywords, and handles errors.
- **Scoring**: `judge_response` scores responses using a judge model.
- **Result Recording**: `JSONLWriter` records results, skips, and errors in JSONL files.

#### Integration Points
- **Ollama API**: `call_ollama` interacts with the Ollama API to get model responses.
- **Judge Model**: `judge_response` uses a judge model to score responses.
- **File System**: Writes results to JSONL files in the `runs` directory.
- **Command Line**: `main` parses command-line arguments to configure the benchmark run.

### Detailed Analysis

#### Classes

1. **JSONLWriter**
   - **Purpose**: Manages thread-safe writing to JSONL files.
   - **Methods**:
     - `__init__`: Initializes the writer with a file path.
     - `write`: Writes a record to the file in JSONL format.

2. **RunManager**
   - **Purpose**: Manages the overall run, including initialization, writing manifests, and summaries.
   - **Methods**:
     - `__init__`: Initializes the run manager with a run ID and models.
     - `_get_git_hash`: Retrieves the current Git hash.
     - `write_summary`: Writes a summary of the run to a JSON file.

3. **DependencyResolver**
   - **Purpose**: Tracks dependencies for tasks and models to determine if a task is runnable.
   - **Methods**:
     - `__init__`: Initializes the resolver with tasks and models.
     - `record_result`: Records the result status of a task for a model.
     - `is_runnable`: Determines if a task is runnable for a model.
     - `should_skip`: Determines if a task should be skipped.
     - `all_deps_resolved`: Checks if all dependencies are resolved.

#### Functions

1. **call_ollama**
   - **Purpose**: Calls the Ollama API with a given model and prompt.
   - **Parameters**: `model`, `prompt`, `timeout`.
   - **Returns**: `(response_text, response_ms, error_or_none)`.

2. **judge_response**
   - **Purpose**: Scores a response using a judge model.
   - **Parameters**: `task`, `model`, `response`, `run_manager`.
   - **Returns**: A dictionary containing the score record.

3. **run_task_for_model**
   - **Purpose**: Runs a single task for a single model.
   - **Parameters**: `task`, `model`, `run_manager`, `resolver`, `judge_enabled`.
   - **Returns**: The status of the task (`"pass"`, `"fail"`, `"timeout"`, `"error"`, `"skip"`).

4. **build_execution_waves**
   - **Purpose**: Topologically sorts tasks into execution waves.
   - **Parameters**: `tasks`, `task_ids`.
   - **Returns**: Execution waves.

5. **run_benchmark**
   - **Purpose**: Orchestrates the benchmark run.
   - **Parameters**: `models`, `task_filter`, `judge_enabled`.

6. **_build_summary**
   - **Purpose**: Reads all JSONL files and builds a summary.
   - **Parameters**: `run_id`, `run_manager`, `models`, `tasks`, `start_time`.

7. **main**
   - **Purpose**: Entry point for the script.
   - **Parameters**: None.

#### Configuration and Environment
- **CONFIG**: Populated from a configuration file or command-line arguments.
- **BENCH_DIR**: Set to `/opt/mythos/orchestrator/benchmark`.

#### Integration with Other Subsystems
- **Ollama API**: `call_ollama` interacts with the Ollama API to get model responses.
- **Judge Model**: `judge_response` uses a judge model to score responses.
- **File System**: Writes results to JSONL files in the `runs` directory.
- **Command Line**: `main` parses command-line arguments to configure the benchmark run.
