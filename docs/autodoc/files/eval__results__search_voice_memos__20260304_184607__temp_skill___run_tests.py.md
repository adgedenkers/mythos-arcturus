# eval/results/search_voice_memos/20260304_184607/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 54

---

### File: eval/results/search_voice_memos/20260304_184607/temp_skill/_run_tests.py

#### Purpose
This file is designed to dynamically import and test a specific skill module (`test_skill.py`) by running predefined test cases against it. The results are collected and printed in JSON format.

#### Architecture
The file consists of a single top-level asynchronous function `run()` that iterates over a list of test cases, executes each test case against the imported skill module, and collects the results. The main logic is wrapped in a try-except block to handle any exceptions that might occur during the import or test execution.

#### Patterns
- **Dynamic Import**: The file uses `importlib.util` to dynamically import the `test_skill.py` module.
- **Asynchronous Execution**: The `run()` function is asynchronous, allowing for non-blocking execution of the test cases.

#### Dependencies
- `sys`: For manipulating the module search path and exiting the script.
- `json`: For serializing the test results into JSON format.
- `asyncio`: For asynchronous execution of the test cases.
- `traceback`: For handling exceptions.
- `importlib.util`: For dynamic module import.

#### Interfaces
- **Exposed Function**: `run()`: An asynchronous function that runs the test cases and collects results.

#### Database
- **PostgreSQL Table**: `engine`: The file imports `SkillBase` and `SkillRequest` from `engine.base`, indicating that it interacts with the `engine` table in PostgreSQL.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
1. **Dynamic Module Import**: The `test_skill.py` module is dynamically imported using `importlib.util`.
2. **Skill Class Identification**: The file searches for a class in the imported module that is a subclass of `SkillBase`.
3. **Test Case Execution**: For each test case, the file creates a `SkillRequest` object, calls the `run()` method of the skill instance, and checks the response against expected outcomes.
4. **Result Collection**: The results of each test case are collected in a list and printed as a JSON object.

#### Integration Points
- **Skill Module**: The file dynamically imports and tests a skill module (`test_skill.py`), which is expected to be a subclass of `SkillBase`.
- **Engine Module**: The file imports `SkillBase` and `SkillRequest` from `engine.base`, indicating integration with the `engine` module for skill execution and request handling.

### Detailed Analysis

#### Dynamic Import
The file uses `importlib.util` to dynamically import the `test_skill.py` module from a specified path. This allows the script to test different skill modules without hardcoding the module name.

#### Test Case Execution
The `run()` function is defined as an asynchronous function to handle the execution of test cases. Each test case is defined as a dictionary with keys such as `message`, `expect_ok`, `expect_summary_contains`, and `expect_data_has`. The function iterates over these test cases, creates a `SkillRequest` object, and calls the `run()` method of the skill instance.

#### Result Collection
The results of each test case are collected in a dictionary (`tr`) and appended to the `results` list. The results include whether the test passed or failed, along with any error messages or details about the response.

#### Error Handling
The file includes comprehensive error handling to catch and report any exceptions that occur during the import or test execution. If an exception occurs, the error is captured and included in the results.

### Example Output
The output of the script is a JSON object containing the results of the test cases. For example:
```json
{
  "results": [
    {
      "test_index": 0,
      "message": "search voice memos for love",
      "passed": [
        "ok=True",
        "summary has 'voice memo'",
        "data has 'matches'",
        "summary non-empty"
      ],
      "failed": []
    },
    {
      "test_index": 1,
      "message": "what did we say about relationship",
      "passed": [
        "ok=True",
        "data has 'matches'",
        "summary non-empty"
      ],
      "failed": []
    },
    {
      "test_index": 2,
      "message": "hello how are you today",
      "passed": [
        "ok=True",
        "summary non-empty"
      ],
      "failed": [
        "summary missing 'voice memo': ...",
        "data missing 'matches': [...]"
      ]
    }
  ]
}
```

This output provides a clear and structured view of the test results, making it easy to identify any issues with the skill module being tested.
