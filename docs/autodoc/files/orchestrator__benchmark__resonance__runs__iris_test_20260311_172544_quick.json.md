# orchestrator/benchmark/resonance/runs/iris_test_20260311_172544_quick.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 44

---

### File: orchestrator/benchmark/resonance/runs/iris_test_20260311_172544_quick.json

#### Purpose
This JSON file contains the results of a quick benchmark test for the Mythos system, specifically for the model `qwen3:30b-a3b`. It includes details about the test set, model configuration, layers used, and the responses generated for specific prompts.

#### Architecture
The file is structured as a JSON object with the following key-value pairs:
- `set`: Indicates the type of test set.
- `description`: Provides a brief description of the test.
- `model`: Specifies the AI model used for the test.
- `model_preference`: Indicates the preference setting for the model.
- `layers`: Lists the layers or components of the model used.
- `timestamp`: Records the time when the test was executed.
- `results`: An array of objects, each containing details about a specific prompt-response interaction.
- `summary`: A summary of the test results, including counts and averages.

#### Patterns
This file does not implement any design patterns as it is a data file rather than a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone JSON file.

#### Interfaces
This file does not expose any interfaces. It is intended to be read and processed by other parts of the Mythos system, such as reporting tools or analysis scripts.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a data file that could be used to populate a database or be derived from a database query.

#### Configuration
This file does not use any configuration files or environment variables. The settings and results are hardcoded within the JSON structure.

#### Key Logic
The key logic in this file is the representation of the benchmark test results. It captures the model's performance in terms of response time, word count, and status for each prompt.

#### Integration Points
This file is likely integrated into the Mythos system through:
- **Benchmarking Tools**: Used to analyze the performance of the AI model.
- **Logging and Reporting**: Used to generate reports on the model's performance.
- **Monitoring Systems**: Used to track the health and performance of the AI infrastructure.

### Detailed Breakdown of Key Sections

#### `set` and `description`
- **set**: `"quick"` indicates a quick smoke test.
- **description**: `"Fast smoke test — 3 prompts"` provides a brief description of the test type and scope.

#### `model` and `model_preference`
- **model**: `"qwen3:30b-a3b"` specifies the AI model used.
- **model_preference**: `"auto"` indicates the preference setting for the model.

#### `layers`
- **layers**: `["baseline", "identity", "personality", "voice", "skills_context", "skill_results"]` lists the layers or components of the model used in the test.

#### `timestamp`
- **timestamp**: `"2026-03-11 17:25:44"` records the exact time when the test was executed.

#### `results`
- **results**: An array of objects, each containing:
  - `prompt`: The input prompt.
  - `response`: The generated response from the model.
  - `status`: The status of the response (e.g., `"ok"`).
  - `word_count`: The number of words in the response.
  - `elapsed_s`: The time taken to generate the response in seconds.

#### `summary`
- **summary**: Provides a summary of the test results:
  - `ok`: The number of successful responses.
  - `total`: The total number of prompts.
  - `avg_words`: The average number of words in the responses.
  - `avg_time`: The average time taken to generate the responses.

This JSON file serves as a detailed record of the benchmark test, providing insights into the performance and behavior of the AI model `qwen3:30b-a3b` under specific conditions.
