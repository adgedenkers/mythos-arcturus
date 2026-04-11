# orchestrator/benchmark/resonance/runs/20260311_102839_resonance/manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 16

---

### File: `orchestrator/benchmark/resonance/runs/20260311_102839_resonance/manifest.json`

#### Purpose
This JSON file serves as a manifest for a specific run of the Mythos benchmarking system, capturing metadata about the run including the run ID, phase, start time, models used, configurations, prompt count, total calls, and prompt tokens.

#### Architecture
The manifest file is a simple JSON structure containing key-value pairs. It does not have classes or functions as it is a data file, but it organizes information in a structured manner for easy retrieval and processing.

#### Patterns
No design patterns are applicable since this is a data file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file is not an executable component and does not expose any interfaces. It is intended to be read by other parts of the system, such as the benchmarking orchestrator.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, it may be used to populate or reference data in a database during the benchmarking process.

#### Configuration
This file itself does not use any configuration files or environment variables. It is a static data file that may be generated based on configuration settings elsewhere in the system.

#### Key Logic
The key logic is not present in this file, but rather in the systems that generate and use this file. The manifest file captures the essential metadata needed to track and analyze the benchmark run.

#### Integration Points
This file integrates with the Mythos benchmarking system, particularly with the orchestrator component. The orchestrator reads this manifest to understand the details of the run, such as the models used, configurations, and other metadata. This information is crucial for tracking the performance and behavior of the AI models during benchmarking.

### Detailed Breakdown of Key Fields

- **run_id**: A unique identifier for the run, formatted as `YYYYMMDD_HHMMSS_resonance`.
- **phase**: Indicates the phase of the run, typically an integer.
- **started_at**: Timestamp indicating when the run started.
- **models**: List of models used in the run, e.g., `gemma3:27b`.
- **configs**: List of configurations used, e.g., `full_iris`.
- **prompt_count**: Number of prompts used in the run.
- **total_calls**: Total number of API calls made during the run.
- **prompt_tokens**: Dictionary mapping configurations to the number of tokens used in prompts, e.g., `full_iris` to `1829`.

This manifest file is critical for maintaining a record of benchmarking runs and allows for easy tracking and analysis of performance metrics across different configurations and models.
