# orchestrator/benchmark/resonance/runs/20260311_133055_resonance/manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 16

---

### File: `orchestrator/benchmark/resonance/runs/20260311_133055_resonance/manifest.json`

#### Purpose
This JSON file serves as a manifest for a specific run of the Resonance benchmark in the Mythos system, detailing the configuration, models used, and metrics collected during the run.

#### Architecture
The file is a simple JSON object with key-value pairs that describe various aspects of the benchmark run. It does not contain classes or functions as it is a data file.

#### Patterns
No design patterns are applicable since this is a data file.

#### Dependencies
This file does not import or rely on any external libraries or modules. It is a standalone data file.

#### Interfaces
This file is not an executable component and does not expose any interfaces. It is intended to be read by other parts of the system, such as scripts or services that process benchmark results.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, it may be used to populate or reference data in a database as part of the benchmarking process.

#### Configuration
The file itself does not use any configuration files or environment variables. However, it may be generated based on configuration settings specified elsewhere in the system.

#### Key Logic
The key logic represented in this file is the metadata and metrics of a specific benchmark run. It captures essential information such as the run ID, phase, start time, models used, configurations, number of prompts, total calls, and prompt tokens.

#### Integration Points
This file integrates with other parts of the Mythos system, particularly with the benchmarking and logging subsystems. It is likely used by scripts or services that aggregate and analyze benchmark results.

### Detailed Breakdown of Key Fields

- **run_id**: A unique identifier for this specific run of the benchmark.
- **phase**: Indicates the phase of the benchmark run (e.g., 1 for the first phase).
- **started_at**: Timestamp indicating when the run started.
- **models**: List of models used in the run (e.g., `qwen3:32b`).
- **configs**: List of configurations used for the run (e.g., `full_iris`).
- **prompt_count**: Number of prompts used in the run.
- **total_calls**: Total number of API calls made during the run.
- **prompt_tokens**: Dictionary mapping configurations to the number of tokens used in prompts (e.g., `full_iris` has 1829 tokens).

This manifest file is crucial for tracking and analyzing the performance and behavior of the models and configurations used in the benchmarking process.
