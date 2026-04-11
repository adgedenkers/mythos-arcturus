# eval/results/daily_briefing/20260305_103508/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/daily_briefing/20260305_103508/temp_skill/_run_tests.py`

#### Purpose
This file runs tests on a dynamically imported skill module, evaluates its responses against expected outcomes, and outputs the results in JSON format.

#### Architecture
- **Imports and Path Adjustments**: The file begins by adjusting the `sys.path` to include necessary directories and imports required modules.
- **Dynamic Module Loading**: It dynamically loads a skill module from a specified file path.
- **Test Execution**: The `run` function is defined to asynchronously execute test cases loaded from a JSON file, comparing the skill's responses against expected results.
- **Error Handling**: The file includes comprehensive error handling to capture and report any issues encountered during setup or test execution.

#### Patterns
- **Dynamic Module Loading**: Uses `importlib.util` to dynamically load and execute a module.
- **Asynchronous Execution**: The `run` function is defined as an asynchronous function to handle I/O-bound operations efficiently.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **Custom Modules**: `engine.base` (for `SkillBase` and `SkillRequest`)

#### Interfaces
- **Public Interface**: The `run` function is the primary entry point for asynchronous test execution.
- **Output**: Results are printed in JSON format to the standard output.

#### Database
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` and `SkillRequest` classes)

#### Configuration
- **File Paths**: Hardcoded file paths for the skill module and test cases.
- **Environment Variables**: None used directly, but the paths could be parameterized.

#### Key Logic
- **Dynamic Skill Import**: The skill module is dynamically loaded and instantiated.
- **Test Case Execution**: Each test case is executed asynchronously, and the skill's response is evaluated against expected outcomes.
- **Result Aggregation**: Test results are aggregated and formatted into a JSON structure for output.

#### Integration Points
- **Skill Module**: The skill module is dynamically loaded from a specified file path and must conform to the `SkillBase` interface.
- **Test Cases**: Test cases are loaded from a JSON file and are expected to have specific keys (`message`, `expect_ok`, `expect_summary_contains`, `expect_data_has`).
- **Database**: The skill's `run` method likely interacts with the `engine` table in PostgreSQL to perform its operations.

### Detailed Breakdown

#### Dynamic Module Loading
- The `importlib.util` module is used to dynamically load a skill module from the file `/opt/mythos/eval/results/daily_briefing/20260305_103508/temp_skill/test_skill.py`.
- The module is then inspected to find a class that inherits from `SkillBase` and is not `SkillBase` itself.

#### Test Case Execution
- Test cases are loaded from `/opt/mythos/eval/results/daily_briefing/20260305_103508/temp_skill/_test_cases.json`.
- Each test case is executed asynchronously using the `run` function, which creates a `SkillRequest` object and calls the skill's `run` method.
- The response is evaluated based on several criteria:
  - `expect_ok`: Checks if the response's `ok` attribute matches the expected value.
  - `expect_summary_contains`: Verifies if certain keywords are present in the response summary.
  - `expect_data_has`: Ensures specific keys are present in the response data.
  - Summary non-emptiness: Checks if the summary is non-empty.

#### Error Handling
- Errors during setup or test execution are captured and reported in the results JSON.
- The `asyncio.run(run())` function is used to execute the `run` function, which handles all test cases.

#### Output
- The final results are printed in JSON format, containing a list of test results with details on passed and failed criteria for each test case.

This file serves as a critical component of the Mythos system for evaluating the functionality and correctness of dynamically loaded skill modules.
