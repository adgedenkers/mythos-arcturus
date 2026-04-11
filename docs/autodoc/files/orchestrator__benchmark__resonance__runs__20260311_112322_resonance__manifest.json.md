# orchestrator/benchmark/resonance/runs/20260311_112322_resonance/manifest.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 16

---

### File: `orchestrator/benchmark/resonance/runs/20260311_112322_resonance/manifest.json`

#### Purpose
This JSON file serves as a manifest for a specific benchmark run within the Mythos system, capturing metadata about the run including the run ID, phase, start time, models used, configurations, prompt count, total API calls, and prompt token counts.

#### Architecture
The file is structured as a JSON object with several key-value pairs. Each key represents a specific attribute of the benchmark run, such as `run_id`, `phase`, `started_at`, `models`, `configs`, `prompt_count`, `total_calls`, and `prompt_tokens`.

#### Patterns
No design patterns are applicable as this is a JSON configuration file, not a code file.

#### Dependencies
This JSON file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is read by other parts of the Mythos system, particularly the benchmarking and logging subsystems, to retrieve metadata about the benchmark run.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data within this file might be used to populate or update records in a database.

#### Configuration
This file itself is a configuration file that captures the state and metadata of a specific benchmark run. It does not reference any external configuration files or environment variables.

#### Key Logic
The key logic captured in this file is the metadata of a benchmark run, including the run ID, start time, models used, configurations, and token counts. This metadata is crucial for tracking and analyzing the performance of the benchmark run.

#### Integration Points
This JSON file integrates with the following subsystems within the Mythos system:
- **Benchmarking Subsystem**: Reads the metadata to track and analyze the performance of the benchmark run.
- **Logging Subsystem**: Uses the metadata to log the details of the benchmark run.
- **Database Subsystem**: Potentially uses the metadata to populate or update records in the database for tracking purposes.

### Detailed Explanation of Key Fields
- **run_id**: A unique identifier for the benchmark run, formatted as `YYYYMMDD_HHMMSS_resonance`.
- **phase**: Indicates the phase of the benchmark run, typically an integer.
- **started_at**: Timestamp indicating when the benchmark run started.
- **models**: List of models used in the benchmark run.
- **configs**: List of configurations used in the benchmark run.
- **prompt_count**: Number of prompts used in the benchmark run.
- **total_calls**: Total number of API calls made during the benchmark run.
- **prompt_tokens**: Dictionary mapping configurations to the number of prompt tokens used.

This manifest file is essential for maintaining a record of benchmark runs, facilitating analysis and logging within the Mythos system.
