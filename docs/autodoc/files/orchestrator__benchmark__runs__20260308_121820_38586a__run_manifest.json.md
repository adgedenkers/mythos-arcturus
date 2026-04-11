# orchestrator/benchmark/runs/20260308_121820_38586a/run_manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 48

---

### Analysis of `run_manifest.json`

#### Purpose
This JSON file serves as a manifest for a specific benchmark run within the Mythos system, detailing the run's unique identifier, start time, models used, task count, Git hash, and configuration settings.

#### Architecture
The file is structured as a JSON object with nested fields. The primary fields include `run_id`, `started_at`, `models`, `task_count`, `git_hash`, and `config`. The `config` field contains detailed configuration settings for the run, including model-specific settings, timeouts, and other operational parameters.

#### Patterns
No design patterns are applicable as this is a configuration file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is primarily read by the Mythos system's orchestrator to configure and manage the benchmark run. It does not expose any interfaces but is consumed by the orchestrator to initialize and monitor the run.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data within this file might be used to populate or update records in the Mythos system's database.

#### Configuration
The file itself is a configuration file. It uses a `run_id_prefix` and other settings to configure the benchmark run. The `notes` field provides additional context for the run.

#### Key Logic
The key logic encapsulated in this file is the configuration of a benchmark run. The `config` section defines critical parameters such as model selection, timeouts, and operational settings that guide the execution of the benchmark tasks.

#### Integration Points
This file integrates with the Mythos orchestrator, which reads this manifest to initialize and manage the benchmark run. The `models` and `config` sections are particularly important for the orchestrator to set up the environment and execute tasks as specified.

### Detailed Breakdown

- **run_id**: A unique identifier for the benchmark run (`20260308_121820_38586a`).
- **started_at**: The timestamp when the run was initiated (`2026-03-08T16:18:20.542837+00:00`).
- **models**: A list of models used in the benchmark run.
- **task_count**: The number of tasks in the run (`43`).
- **git_hash**: The Git commit hash for the codebase used in the run (`b8570753`).
- **config**: A nested object containing detailed configuration settings:
  - **run_id_prefix**: A prefix for the run ID (`round2`).
  - **models**: List of models to be used.
  - **judge_model**: The model used for judging tasks (`qwen2.5:32b`).
  - **ollama_host**: The host URL for the Ollama service (`http://localhost:11434`).
  - **output_dir**: Directory for output files (`/opt/mythos/orchestrator/benchmark/runs`).
  - **timeouts**: A dictionary of task-specific timeouts.
  - **max_model_threads**: Maximum number of threads for model execution (`3`).
  - **judge_enabled**: Whether judging is enabled (`true`).
  - **skip_task_ids**: List of task IDs to skip (`[]`).
  - **retry_on_timeout**: Whether to retry on timeout (`false`).
  - **notes**: Additional notes for the run.

This manifest file is crucial for the orchestrator to set up and manage the benchmark run according to the specified configurations and parameters.
