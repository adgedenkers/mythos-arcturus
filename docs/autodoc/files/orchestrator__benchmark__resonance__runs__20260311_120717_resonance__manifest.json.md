# orchestrator/benchmark/resonance/runs/20260311_120717_resonance/manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 16

---

### File: `orchestrator/benchmark/resonance/runs/20260311_120717_resonance/manifest.json`

#### Purpose
This JSON file serves as a manifest for a specific benchmark run within the Mythos system, detailing the configuration, models used, and metrics related to the run.

#### Architecture
The file is structured as a JSON object with several key-value pairs. It includes metadata such as the run ID, phase, start time, models used, configurations, prompt count, total calls, and prompt tokens.

#### Patterns
There are no design patterns applicable to this JSON file as it is a simple data structure.

#### Dependencies
This file does not import or rely on any external dependencies directly. However, it is used by the Mythos system to track and manage benchmark runs.

#### Interfaces
This file is consumed by the Mythos system's orchestrator and benchmarking components. It does not expose any interfaces but provides data to other parts of the system.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data within this file might be used to populate or update records in the database.

#### Configuration
This file does not use any config files or environment variables directly. The data within it is likely generated based on the system's configuration and run parameters.

#### Key Logic
The key logic related to this file involves tracking the benchmark run's metadata, including the models used, configurations, and metrics such as prompt count and total calls. This information is crucial for analyzing the performance and behavior of the AI models during the benchmark.

#### Integration Points
This file integrates with the following subsystems within the Mythos system:
- **Orchestrator**: Manages the benchmark runs and tracks their progress.
- **Benchmarking Components**: Uses the data in this file to execute and monitor the benchmark runs.
- **Logging and Monitoring**: The data in this file might be used to log and monitor the benchmark run's progress and results.

### Detailed Explanation of Key Fields

- **run_id**: A unique identifier for the benchmark run, formatted as `YYYYMMDD_HHMMSS_resonance`.
- **phase**: Indicates the phase of the benchmark run (e.g., 1 for the initial phase).
- **started_at**: Timestamp indicating when the benchmark run started.
- **models**: List of AI models used in the benchmark run.
- **configs**: List of configurations used for the benchmark run.
- **prompt_count**: Number of prompts used in the benchmark run.
- **total_calls**: Total number of API calls made during the benchmark run.
- **prompt_tokens**: Dictionary mapping configurations to the number of tokens used in the prompts.

This manifest file is critical for tracking the details of each benchmark run, ensuring that the system can accurately log and analyze the performance of different AI models under various configurations.
