# orchestrator/voice_tuning/runs/baseline_20260307_234222/manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 10

---

### File: orchestrator/voice_tuning/runs/baseline_20260307_234222/manifest.json

#### Purpose
This JSON file serves as a manifest for a specific run of the voice tuning process in the Mythos system. It contains metadata about the run, including the model used, the judge model, start time, and a preview of the system prompt.

#### Architecture
The file is a simple JSON object with key-value pairs representing various attributes of the run. There are no classes or functions in this file; it is purely a data structure.

#### Patterns
No design patterns are applicable since this is a static JSON file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file does not expose any interfaces. It is intended to be read by other parts of the system to retrieve metadata about the run.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a standalone manifest file.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic is encapsulated in the metadata it provides. The file contains essential information such as the run name, model names, start time, and a preview of the system prompt, which is crucial for understanding the context and parameters of the run.

#### Integration Points
This file is likely read by other components of the Mythos system, such as the orchestrator or logging modules, to gather information about the run. It serves as a reference point for tracking and analyzing the performance and behavior of the voice tuning process.

### Detailed Breakdown of Attributes

- **run_name**: A unique identifier for the run, in this case, `baseline_20260307_234222`.
- **label**: A descriptive label for the run, here `baseline`.
- **model**: The primary model used for the run, `nous-hermes2:latest`.
- **judge_model**: The model used for judging the performance, `gemma3:27b`.
- **started_at**: The timestamp when the run started, `2026-03-08T04:42:22.823777+00:00`.
- **system_prompt_length**: The length of the system prompt, `4514` characters.
- **system_prompt_preview**: A preview of the system prompt, which includes details about the identity and context of the run.
- **task_filter**: A placeholder for any task filtering criteria, currently `null`.

This manifest file is critical for tracking and analyzing the performance and behavior of the voice tuning process within the Mythos system.
