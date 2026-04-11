# eval/results/query_calendar/20260305_091625/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/query_calendar/20260305_091625/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and execute test cases for a skill module in the Mythos system. It reads test cases from a JSON file, runs each test case against the skill, and collects the results for reporting.

#### Architecture
- **Main Function**: `run` is the primary asynchronous function that iterates through each test case, executes the skill, and collects the results.
- **Dynamic Import**: The skill module is dynamically imported using `importlib.util`, allowing for flexible testing of different skill implementations.
- **Test Case Execution**: Each test case is processed by creating a `SkillRequest` object, invoking the skill's `run` method, and comparing the response against expected outcomes.

#### Patterns
- **Factory Method**: The skill class is dynamically instantiated from the imported module.
- **Singleton**: The skill instance is created once and reused for all test cases.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **Custom Modules**: `engine.base` for `SkillBase` and `SkillRequest`

#### Interfaces
- **Exposed Functions**: `run` is the only exposed function, which is an asynchronous function that processes test cases and collects results.

#### Database
- **PostgreSQL Table**: `engine` is referenced but not directly manipulated in this file. The `SkillBase` class likely interacts with this table.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: Test cases are loaded from `/opt/mythos/eval/results/query_calendar/20260305_091625/temp_skill/_test_cases.json`.

#### Key Logic
- **Test Case Processing**: Each test case is processed by creating a `SkillRequest` object, invoking the skill's `run` method, and comparing the response against expected outcomes.
- **Result Collection**: Results are collected in a list of dictionaries, each representing the outcome of a test case.

#### Integration Points
- **Skill Module**: The skill module is dynamically loaded from `/opt/mythos/eval/results/query_calendar/20260305_091625/temp_skill/test_skill.py`.
- **Test Cases**: Test cases are loaded from `/opt/mythos/eval/results/query_calendar/20260305_091625/temp_skill/_test_cases.json`.
- **SkillBase Class**: The `SkillBase` class from `engine.base` is used to ensure the dynamically loaded skill class is a valid skill implementation.

### Detailed Breakdown

1. **Dynamic Import and Initialization**:
    - The skill module is dynamically imported using `importlib.util` to ensure flexibility in testing different skill implementations.
    - The skill class is identified by checking if it is a subclass of `SkillBase` and not the base class itself.

2. **Test Case Execution**:
    - Test cases are loaded from a JSON file and processed one by one.
    - For each test case, a `SkillRequest` object is created and passed to the skill's `run` method.
    - The response is checked against expected outcomes (e.g., `expect_ok`, `expect_summary_contains`, `expect_data_has`).

3. **Result Collection**:
    - Results are collected in a list of dictionaries, each representing the outcome of a test case.
    - Each dictionary includes the test index, message, passed conditions, and failed conditions.

4. **Error Handling**:
    - Errors during setup or test execution are caught and reported in the results.

5. **Output**:
    - The final results are printed in JSON format, providing a structured output for further processing or reporting.

This file serves as a critical component in the Mythos system for testing and validating skill implementations, ensuring they meet the expected behavior and criteria.
