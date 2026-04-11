# orchestrator/benchmark/runs/20260307_171356_2d3c46/run_manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 34

---

### Documentation for `run_manifest.json`

#### Purpose
The `run_manifest.json` file serves as a metadata record for a specific benchmark run within the Mythos system. It captures essential details such as the run ID, start time, models used, task count, and configuration settings.

#### Architecture
This JSON file is structured as a flat dictionary with nested objects and arrays. It contains top-level keys for `run_id`, `started_at`, `models`, `task_count`, `git_hash`, and `config`. The `config` key holds a nested dictionary with detailed configuration parameters.

#### Patterns
There are no design patterns directly applicable to this JSON file since it is a data structure rather than a code implementation.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file does not expose any interfaces. It is intended to be read and processed by other parts of the Mythos system, such as the benchmark orchestrator.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a metadata file used for tracking and reporting purposes.

#### Configuration
The file uses configuration settings embedded within the `config` section, which includes details such as model configurations, timeouts, and other runtime parameters.

#### Key Logic
The key logic captured in this file pertains to the benchmark run configuration, including the models to be used, timeouts for different tasks, and other runtime settings. This metadata is crucial for reproducing and analyzing benchmark results.

#### Integration Points
This file integrates with the Mythos benchmark orchestrator subsystem. The orchestrator reads this manifest to understand the configuration and state of the benchmark run. It is used to initialize the benchmark tasks and to log the results.

### Detailed Breakdown

1. **run_id**: A unique identifier for the benchmark run.
2. **started_at**: The timestamp when the benchmark run started.
3. **models**: A list of models used in the benchmark run.
4. **task_count**: The number of tasks in the benchmark run.
5. **git_hash**: The Git commit hash associated with the benchmark run.
6. **config**: A nested dictionary containing detailed configuration settings:
   - **models**: List of models used.
   - **judge_model**: The model used for judging tasks.
   - **ollama_host**: The host address for the Ollama service.
   - **output_dir**: Directory for storing benchmark output.
   - **timeouts**: Timeouts for different task types.
   - **max_model_threads**: Maximum number of threads for model execution.
   - **judge_enabled**: Whether the judge model is enabled.
   - **skip_task_ids**: List of task IDs to skip.
   - **retry_on_timeout**: Whether to retry tasks on timeout.

This file serves as a comprehensive record of the benchmark run's configuration and state, enabling reproducibility and analysis of the benchmark results.
