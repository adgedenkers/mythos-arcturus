# orchestrator/benchmark/runs/20260307_173034_2b7a93/run_manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 34

---

### Analysis of `run_manifest.json`

#### Purpose
This JSON file serves as a manifest for a specific benchmark run within the Mythos system, detailing various parameters and configurations used during the run.

#### Architecture
The file is structured as a JSON object with several key-value pairs, including metadata about the run (e.g., `run_id`, `started_at`), a list of models used (`models`), task count (`task_count`), Git hash (`git_hash`), and a detailed configuration section (`config`).

#### Patterns
No design patterns are applicable as this is a configuration file, not a code file.

#### Dependencies
This file does not directly import or rely on any external libraries or modules. However, it is used by the Mythos system to configure and track the benchmark run.

#### Interfaces
This file is primarily used by the Mythos system's orchestrator to configure and monitor the benchmark run. It does not expose any interfaces but serves as a configuration input for the system.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data within this file might be used to populate or reference records in the Mythos system's database.

#### Configuration
The file itself acts as a configuration file, detailing various settings and parameters for the benchmark run. It does not reference any external config files but relies on environment variables or other system settings for dynamic values.

#### Key Logic
The key logic embedded in this file is the configuration of the benchmark run, including the models to be used (`models`), the judge model (`judge_model`), timeouts for different tasks (`timeouts`), and other operational settings (`max_model_threads`, `judge_enabled`, etc.).

#### Integration Points
This file integrates with the Mythos system's orchestrator, which uses the information to configure and monitor the benchmark run. Specifically, it interacts with subsystems responsible for model execution, task management, and result logging.

### Detailed Breakdown

- **run_id**: A unique identifier for the benchmark run (`20260307_173034_2b7a93`).
- **started_at**: Timestamp indicating when the run started (`2026-03-07T22:30:34.518044+00:00`).
- **models**: List of models used in the benchmark (`["gemma3:27b", "qwen2.5:32b", "llama3.3:70b"]`).
- **task_count**: Number of tasks in the benchmark (`43`).
- **git_hash**: Git commit hash associated with the run (`efd60502`).
- **config**: Detailed configuration section:
  - **models**: Same list of models used.
  - **judge_model**: Model used for judging (`gemma3:27b`).
  - **ollama_host**: Host for the Ollama service (`http://localhost:11434`).
  - **output_dir**: Directory for output files (`/opt/mythos/orchestrator/benchmark/runs`).
  - **timeouts**: Timeouts for different tasks (`reasoning`, `code`, `mythos`, `narrative`, `tool_use`, `voice`, `default`).
  - **max_model_threads**: Maximum number of threads for model execution (`3`).
  - **judge_enabled**: Flag indicating whether judging is enabled (`true`).
  - **skip_task_ids**: List of task IDs to skip (`[]`).
  - **retry_on_timeout**: Flag indicating whether to retry on timeout (`false`).

This manifest file is crucial for the Mythos system to configure and manage the benchmark run effectively, ensuring that all necessary parameters and configurations are set correctly.
