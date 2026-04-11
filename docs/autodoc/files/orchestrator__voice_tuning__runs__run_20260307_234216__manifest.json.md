# orchestrator/voice_tuning/runs/run_20260307_234216/manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 10

---

### File: `orchestrator/voice_tuning/runs/run_20260307_234216/manifest.json`

#### Purpose
This JSON file serves as a manifest for a specific run of the voice tuning process in the Mythos system. It contains metadata and configuration details for the run, including the models used, start time, and system prompt information.

#### Architecture
The file is a simple JSON structure with key-value pairs representing various attributes of the run. There are no classes or functions as this is a data file.

#### Patterns
No design patterns are applicable since this is a data file.

#### Dependencies
This file does not import or rely on any external modules or libraries. It is a standalone data file.

#### Interfaces
This file is intended to be read by other parts of the system, particularly the orchestrator components responsible for managing and monitoring the voice tuning runs. It does not expose any functions or methods.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, it might be used to populate or reference data in the database during the run.

#### Configuration
This file itself does not use any configuration files or environment variables. However, it contains configuration details that might be used by other parts of the system.

#### Key Logic
The key logic related to this file involves the interpretation and use of the metadata it contains. For example:
- The `model` and `judge_model` fields specify the AI models used for the run.
- The `started_at` field indicates when the run was initiated.
- The `system_prompt_length` and `system_prompt_preview` fields provide details about the system prompt used during the run.

#### Integration Points
This file integrates with the following subsystems in the Mythos system:
- **Orchestrator**: The orchestrator component reads this file to manage and monitor the run.
- **Voice Tuning Engine**: The voice tuning engine uses the metadata in this file to configure and execute the run.
- **Logging and Monitoring**: The data in this file might be used for logging and monitoring purposes to track the progress and outcomes of the run.

### Detailed Explanation of Fields

1. **run_name**: A unique identifier for the run, formatted as `run_YYYYMMDD_HHMMSS`.
2. **label**: A label indicating the type of run, in this case, "run".
3. **model**: The primary AI model used for the run, specified as `nous-hermes2:latest`.
4. **judge_model**: The AI model used for judging or evaluating the run, specified as `gemma3:27b`.
5. **started_at**: The timestamp when the run was started, in ISO 8601 format.
6. **system_prompt_length**: The length of the system prompt used in the run.
7. **system_prompt_preview**: A preview of the system prompt, truncated for brevity.
8. **task_filter**: A placeholder for any task filtering criteria, currently set to `null`.

This manifest file is crucial for tracking and managing the voice tuning runs within the Mythos system, providing essential metadata for monitoring and analysis.
