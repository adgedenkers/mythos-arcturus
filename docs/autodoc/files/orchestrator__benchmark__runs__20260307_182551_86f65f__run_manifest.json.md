# orchestrator/benchmark/runs/20260307_182551_86f65f/run_manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 34

---

### File: `orchestrator/benchmark/runs/20260307_182551_86f65f/run_manifest.json`

#### 1. Purpose
This JSON file serves as a manifest for a specific benchmark run in the Mythos system, detailing the configuration, models used, and metadata related to the run.

#### 2. Architecture
The file is structured as a JSON object with the following key components:
- `run_id`: A unique identifier for the run.
- `started_at`: The timestamp when the run started.
- `models`: A list of models used in the run.
- `task_count`: The number of tasks in the run.
- `git_hash`: The Git commit hash associated with the run.
- `config`: A nested object containing detailed configuration settings for the run.

#### 3. Patterns
No design patterns are directly applicable to this JSON file, as it is a configuration file rather than executable code.

#### 4. Dependencies
This file does not directly import or rely on any external dependencies. However, it is used by the Mythos system's benchmarking subsystem.

#### 5. Interfaces
This file is read by the Mythos system's benchmarking subsystem to configure and track the benchmark run. It does not expose any interfaces but is consumed by other parts of the system.

#### 6. Database
This file does not directly interact with any database tables or Neo4j labels. However, the data within this file might be used to populate or update database records during the benchmark run.

#### 7. Configuration
The file itself is a configuration file and does not rely on external configuration files or environment variables. However, it contains configuration settings that are used during the benchmark run.

#### 8. Key Logic
The key logic related to this file involves:
- **Model Configuration**: Specifies the models (`gemma3:27b`, `qwen2.5:32b`, `llama3.3:70b`) used in the run.
- **Timeouts**: Defines different timeout values for various tasks (`reasoning`, `code`, `mythos`, `narrative`, `tool_use`, `voice`).
- **Judge Configuration**: Configures the judge model (`gemma3:27b`) and whether judging is enabled.
- **Task Management**: Specifies the number of tasks (`task_count`) and whether to retry on timeout (`retry_on_timeout`).

#### 9. Integration Points
This file integrates with the following subsystems of the Mythos system:
- **Benchmarking Subsystem**: Reads the configuration to set up and execute the benchmark run.
- **Model Management**: Uses the `models` and `judge_model` fields to load and manage the models.
- **Task Execution**: Uses the `task_count` and `timeouts` fields to manage task execution and timeouts.
- **Output Management**: Uses the `output_dir` field to specify where the output of the benchmark run should be stored.

### Summary
The `run_manifest.json` file is a critical configuration file for a specific benchmark run in the Mythos system. It provides detailed information about the run, including the models used, configuration settings, and metadata. This file is consumed by the benchmarking subsystem to set up and execute the run, and it integrates with various subsystems to manage models, tasks, and output.
