# eval/results/memory_search_composite/20260305_071348/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/memory_search_composite/20260305_071348/temp_skill/_run_tests.py`

#### Purpose
This file is designed to run tests on a dynamically imported skill module, comparing the skill's output against expected results defined in a JSON file. It uses asynchronous operations to handle the test execution and outputs the results in JSON format.

#### Architecture
The file consists of a single asynchronous function `run` that iterates over test cases, executes the skill's `run` method, and compares the output against expected values. The main logic is wrapped in a try-except block to handle any exceptions that might occur during the import or test execution.

#### Patterns
- **Factory Pattern**: The skill class is dynamically loaded and instantiated from the imported module.
- **Singleton Pattern**: The skill instance is created once and reused for all test cases.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **Custom Modules**: `engine.base` (for `SkillBase` and `SkillRequest`)

#### Interfaces
- **Public Interface**: The `run` function is the only public interface, which is an asynchronous function that performs the test execution.
- **External Interfaces**: The file reads test cases from a JSON file and dynamically imports a skill module.

#### Database
- **PostgreSQL Table**: `engine` (used indirectly through the `SkillBase` class)

#### Configuration
- **Environment Variables**: None
- **Config Files**: `/opt/mythos/eval/results/memory_search_composite/20260305_071348/temp_skill/_test_cases.json`

#### Key Logic
1. **Dynamic Module Import**: The skill module is dynamically imported using `importlib.util`.
2. **Test Case Execution**: For each test case, the skill's `run` method is called with a `SkillRequest` object.
3. **Result Comparison**: The response from the skill is compared against expected values such as `expect_ok`, `expect_summary_contains`, and `expect_data_has`.
4. **Result Aggregation**: Test results are aggregated and stored in the `results` list, which is then output as JSON.

#### Integration Points
- **Skill Module**: The skill module is dynamically loaded from `/opt/mythos/eval/results/memory_search_composite/20260305_071348/temp_skill/test_skill.py`.
- **Test Cases**: Test cases are read from `/opt/mythos/eval/results/memory_search_composite/20260305_071348/temp_skill/_test_cases.json`.
- **SkillBase Class**: The `SkillBase` class from `engine.base` is used to instantiate the skill and define the `run` method signature.

### Detailed Breakdown

1. **Dynamic Module Import**:
   - The file dynamically imports a skill module from a specified path using `importlib.util`.
   - It then searches for a class that inherits from `SkillBase` and instantiates it.

2. **Test Case Execution**:
   - The `run` function is an asynchronous function that iterates over each test case defined in `_test_cases.json`.
   - For each test case, it creates a `SkillRequest` object and calls the skill's `run` method.
   - The response is then compared against expected values.

3. **Result Aggregation**:
   - Test results are stored in a dictionary (`tr`) for each test case, which includes whether the test passed or failed.
   - The `results` list accumulates these dictionaries and is finally output as a JSON string.

4. **Error Handling**:
   - The file uses try-except blocks to catch and handle any exceptions that occur during the import or test execution.
   - Any errors are captured and included in the final JSON output.

This file serves as a critical component in the Mythos system for validating the functionality of dynamically loaded skill modules against predefined test cases.
