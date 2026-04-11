# workers/tests/results/7b_vs_32b_calibrated.json

**Language:** json
**Stream:** SYS
**Module:** Background Workers
**Lines:** 496

---

### File: workers/tests/results/7b_vs_32b_calibrated.json

#### Purpose
This JSON file contains the results of a test suite comparing the performance and accuracy of two different configurations of the `qwen2.5` model: `7b@0.1` and `32b@0.1`. Each configuration is tested against a set of predefined messages, and the results include pass/fail counts, total time, and detailed information about each test case.

#### Architecture
The file is structured as a JSON object with two main keys, each representing a different model configuration (`qwen2.5:7b@0.1` and `qwen2.5:32b@0.1`). Each configuration object contains:
- `pass`: Number of passed tests.
- `fail`: Number of failed tests.
- `error`: Number of errors encountered.
- `total_time`: Total time taken for all tests.
- `details`: Array of detailed test results, each containing:
  - `test_id`: Unique identifier for the test case.
  - `message`: The input message for the test.
  - `elapsed`: Time taken to process the message.
  - `schema_errors`: List of schema validation errors.
  - `expect_fails`: List of expected failures.
  - `raw_excerpt`: Raw excerpt of the processed message.
  - `actual`: Actual processed message details.

#### Patterns
No specific design patterns are used since this is a data file rather than a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone JSON file.

#### Interfaces
This file does not expose any interfaces as it is a data file. It is intended to be read by other parts of the system for analysis and reporting.

#### Database
This file does not interact with any databases directly. However, the data it contains could be used to populate a database for further analysis.

#### Configuration
This file does not use any configuration files or environment variables. The data is static and predefined.

#### Key Logic
The key logic represented in this file is the comparison of two different model configurations (`7b@0.1` and `32b@0.1`) based on their performance and accuracy in processing a set of predefined messages. The detailed results include:
- Pass/fail counts.
- Total processing time.
- Detailed information about each test case, including elapsed time, schema errors, expected failures, and actual processed message details.

#### Integration Points
This file is likely used by the Mythos system for:
- Analyzing the performance and accuracy of different model configurations.
- Generating reports and metrics for model evaluation.
- Comparing the efficiency and correctness of different model sizes (`7b` vs `32b`).

The data in this file could be integrated into a dashboard or reporting system to provide insights into the model's performance. It could also be used to feed into further analysis or machine learning pipelines for model tuning and optimization.
