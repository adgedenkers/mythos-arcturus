# workers/tests/results/7b_vs_32b.json

**Language:** json
**Stream:** SYS
**Module:** Background Workers
**Lines:** 514

---

### File: workers/tests/results/7b_vs_32b.json

#### Purpose
This JSON file contains test results for two different configurations of the `qwen2.5` model: `qwen2.5:7b@0.1` and `qwen2.5:32b@0.1`. It includes metrics such as pass/fail counts, total time, and detailed test outcomes for each message processed by the model.

#### Architecture
The file is structured as a JSON object with two main keys, each representing a different model configuration. Each configuration object contains:
- `pass`: Number of tests passed.
- `fail`: Number of tests failed.
- `error`: Number of errors encountered.
- `total_time`: Total time taken for all tests.
- `details`: An array of detailed test results, each containing:
  - `test_id`: Unique identifier for the test.
  - `message`: The input message.
  - `elapsed`: Time taken to process the message.
  - `schema_errors`: Errors related to schema validation.
  - `expect_fails`: Expected failures that did not match the actual outcome.
  - `raw_excerpt`: Raw excerpt of the processed message.
  - `actual`: Actual processed message details.

#### Patterns
No design patterns are applicable as this is a data file and not a source code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file does not expose any interfaces. It is intended for consumption by test reporting and analysis tools.

#### Database
This file does not interact with any databases directly. It is a standalone test result file.

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic is encapsulated in the detailed test results, which include:
- **Test Outcome**: Whether the test passed or failed.
- **Performance Metrics**: Time taken to process each message (`elapsed`).
- **Validation Errors**: Any schema errors or expected failures that did not match the actual outcome.

#### Integration Points
This file is likely used by the test reporting and analysis subsystems of the Mythos system to aggregate and present test results. It integrates with:
- **Test Execution Framework**: The framework that runs the tests and generates this file.
- **Test Reporting Tools**: Tools that consume this file to generate reports and dashboards.

### Detailed Analysis of Test Results

#### `qwen2.5:7b@0.1`
- **Pass/Fail**: 2 passes, 13 fails, 0 errors.
- **Total Time**: 18.93 seconds.
- **Test Details**:
  - **T01**: Passed. Message: "good morning". No schema errors or expected failures.
  - **T02**: Failed. Message: "thanks". Expected `message_type` to be `filler` but got `emotional_expression`.
  - **T03**: Failed. Message: "yep". Expected `message_type` to be `filler` but got `greeting`.
  - **T04**: Failed. Message: "Fitz had a snow delay today". Expected `message_type` to be `life_event` and `complexity` to be `simple` but got `information_sharing` and `trivial`.
  - **T05**: Passed. Message: "hey babe". No schema errors or expected failures.
  - **T06**: Failed. Message: "what's on my calendar today?". Expected `message_type` to be `question_life_logistics` but got `request_action`.
  - **T07**: Failed. Message: "I'm frustrated. The patch system keeps breaking an". Expected `complexity` to be `moderate` but got `simple`.
  - **T08**: Failed. Message: "What do you think about the relationship between m". Expected `complexity` to be `deep` or `complex` but got `moderate`.
  - **T09**: Failed. Message: "I had the weirdest dream last night about a castle". Expected `complexity` to be `moderate` or `complex` but got `simple`.
  - **T10**: Passed. Message: "how much did we spend on groceries last month?". No schema errors or expected failures.
  - **T11**: Failed. Message: "I need to refactor the finance importer to handle". Expected `message_type` to be `question_technical` or `request_action`, `complexity` to be `complex`, and `processing_path` to be `full` but got `question_life_logistics`, `moderate`, and `standard`.
  - **T12**: Failed. Message: "Tell me about Seraphe's lineage". Expected `message_type` to be `question_cosmology`, `complexity` to be `deep` or `complex`, `processing_path` to be `full`, and `cosmology` and `graph_lookup` context to be true but got `information_sharing`, `moderate`, and `standard`.
  - **T13**: Failed. Message: "Build me a Neo4j schema for tracking soul incarnat". Expected `complexity` to be `complex` or `deep` and `processing_path` to be `full` but got `moderate` and `standard`.
  - **T14**: Failed. Message: "Something shifted in the field today. I can feel t". Expected `complexity` to be `complex` or `deep`, `processing_path` to be `full`, and `cosmology` context to be true but got `moderate` and `standard`.
  - **T15**: Failed. Message: "Check the Amex balance, deploy patch 0139, and fig". Expected `message_type` to be `multi_part`, `complexity` to be `complex`, and `processing_path` to be `full` but got `request_action`, `moderate`, and `standard`.

#### `qwen2.5:32b@0.1`
- **Pass/Fail**: 4 passes, 11 fails, 0 errors.
- **Total Time**: 70.16 seconds.
- **Test Details**:
  - **T01**: Passed. Message: "good morning". No schema errors or expected failures.
  - **T02**: Failed. Message: "thanks". Expected `message_type` to be `filler` but got `emotional_expression`.

This file provides a comprehensive overview of the performance and accuracy of the `qwen2.5` model under different configurations, which can be used to identify areas for improvement and to compare the effectiveness of different model sizes and settings.
