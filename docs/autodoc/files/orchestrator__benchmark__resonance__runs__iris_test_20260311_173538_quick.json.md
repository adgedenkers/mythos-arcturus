# orchestrator/benchmark/resonance/runs/iris_test_20260311_173538_quick.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 44

---

### File: orchestrator/benchmark/resonance/runs/iris_test_20260311_173538_quick.json

#### Purpose
This JSON file contains the results of a benchmark test for the Mythos system, specifically for a quick smoke test using the `qwen3:30b-a3b` model. It includes details about the test set, model, layers used, timestamps, individual prompt-response pairs, and summary statistics.

#### Architecture
The file is structured as a JSON object with the following key components:
- `set`: Indicates the type of test set (e.g., "quick").
- `description`: Provides a brief description of the test.
- `model`: Specifies the model used for the test.
- `model_preference`: Indicates the preference setting for the model.
- `layers`: Lists the layers involved in the test.
- `timestamp`: Records the time when the test was run.
- `results`: An array of objects, each containing details about a specific prompt-response pair.
- `summary`: Provides a summary of the test results, including counts and averages.

#### Patterns
This file does not implement any design patterns as it is a static JSON file used for storing and representing test results.

#### Dependencies
This JSON file does not import or rely on any external dependencies. It is a standalone file used for storing benchmark results.

#### Interfaces
This file does not expose any interfaces. It is intended to be read and processed by other components of the Mythos system, such as reporting tools or analysis scripts.

#### Database
This JSON file does not directly interact with any database tables or Neo4j labels. It is a standalone file used for storing benchmark results.

#### Configuration
This file does not use any configuration files or environment variables. The data within the file is static and predefined.

#### Key Logic
The key logic in this file is the representation of benchmark results. It captures the following:
- The test set and model used.
- The layers involved in the test.
- Timestamp of the test run.
- Individual prompt-response pairs, including status, word count, and elapsed time.
- Summary statistics of the test results.

#### Integration Points
This JSON file is likely used by other components of the Mythos system for:
- Reporting and analysis of benchmark results.
- Monitoring the performance of different models and layers.
- Logging and auditing purposes.

### Detailed Breakdown

- **Test Set and Description**:
  - `set`: "quick"
  - `description`: "Fast smoke test — 3 prompts"
  - `model`: "qwen3:30b-a3b"
  - `model_preference`: "auto"
  - `layers`: ["baseline", "identity", "personality", "voice", "skills_context", "skill_results"]

- **Timestamp**:
  - `timestamp`: "2026-03-11 17:35:38"

- **Results**:
  - Each result object includes:
    - `prompt`: The input prompt.
    - `response`: The model's response to the prompt.
    - `status`: The status of the response (e.g., "ok").
    - `word_count`: The number of words in the response.
    - `elapsed_s`: The time taken to generate the response in seconds.

- **Summary**:
  - `ok`: Number of successful responses.
  - `total`: Total number of prompts.
  - `avg_words`: Average word count of responses.
  - `avg_time`: Average time taken to generate responses.

This JSON file serves as a comprehensive record of the benchmark test, providing insights into the performance and behavior of the specified model and layers.
