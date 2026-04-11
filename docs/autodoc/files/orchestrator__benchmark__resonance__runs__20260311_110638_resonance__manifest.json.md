# orchestrator/benchmark/resonance/runs/20260311_110638_resonance/manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 18

---

### Analysis of `manifest.json` from the Mythos System

#### Purpose
The `manifest.json` file serves as a metadata record for a specific run of the Mythos system's benchmarking process. It captures essential details such as the run ID, start time, models used, configurations, and other relevant metrics.

#### Architecture
The file is structured as a JSON object with key-value pairs representing various attributes of the benchmark run. The keys include `run_id`, `phase`, `started_at`, `models`, `configs`, `prompt_count`, `total_calls`, and `prompt_tokens`.

#### Patterns
No design patterns are applicable here since this is a JSON file and not a code file.

#### Dependencies
This JSON file does not import or rely on any external dependencies directly. It is a standalone metadata file.

#### Interfaces
This file is used by the Mythos system to retrieve metadata about a specific benchmark run. It does not expose any interfaces but is consumed by other parts of the system.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a standalone metadata file.

#### Configuration
This file does not use any configuration files or environment variables. It contains static metadata for a specific run.

#### Key Logic
The key logic here is the representation of metadata for a benchmark run. The file captures the essential details needed to understand the context and results of the run, such as the models used, configurations, and metrics like prompt count and total calls.

#### Integration Points
This file integrates with other parts of the Mythos system, particularly the benchmarking subsystem. It is likely used by scripts or services that process benchmark results, generate reports, or perform further analysis.

### Detailed Breakdown

- **run_id**: A unique identifier for the benchmark run, formatted as `YYYYMMDD_HHMMSS_resonance`.
- **phase**: Indicates the phase of the benchmark run, with `1` being the first phase.
- **started_at**: Timestamp indicating when the run started.
- **models**: List of models used in the benchmark run, such as `qwen3:14b-q8_0`, `qwen3:30b-a3b`, and `deepseek-r1:32b`.
- **configs**: List of configurations used, such as `full_iris`.
- **prompt_count**: Number of prompts used in the benchmark run.
- **total_calls**: Total number of API calls made during the run.
- **prompt_tokens**: Dictionary containing the number of tokens for each configuration, e.g., `full_iris` has `1829` tokens.

This metadata file is crucial for tracking and analyzing the performance and behavior of different models and configurations within the Mythos system.
