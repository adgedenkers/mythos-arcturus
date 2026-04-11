# eval/results/idea_backlog_manager/20260305_110943/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/idea_backlog_manager/20260305_110943/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and test a skill module (`test_skill.py`) by running predefined test cases stored in `_test_cases.json`. It evaluates the skill's responses against expected outcomes and outputs the results in JSON format.

#### Architecture
- **Top-level Functions**: 
  - `run()`: An asynchronous function that iterates over test cases, runs the skill, and collects results.
- **Data Flow**:
  - The file reads test cases from a JSON file and dynamically imports a skill module.
  - It then runs each test case, evaluates the skill's response, and collects the results.
  - Finally, it outputs the results in JSON format.

#### Patterns
- **Dynamic Module Loading**: Uses `importlib.util` to dynamically load a module from a specified file path.
- **Asynchronous Execution**: The `run()` function is asynchronous, allowing for non-blocking execution of test cases.

#### Dependencies
- **Imports**:
  - `sys`: For manipulating the module search path.
  - `json`: For reading and writing JSON data.
  - `asyncio`: For asynchronous execution of test cases.
  - `traceback`: For handling exceptions.
  - `importlib.util`: For dynamic module loading.

#### Interfaces
- **Exposed Functions**:
  - `run()`: An asynchronous function that runs the test cases and collects results.

#### Database
- **References**:
  - **Table**: `engine` (PostgreSQL)
  - **Usage**: The skill class (`SkillBase`) is imported from the `engine.base` module, indicating that it likely interacts with the `engine` table in PostgreSQL.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: 
  - `_test_cases.json`: Contains the test cases to be run.

#### Key Logic
- **Dynamic Module Loading**:
  - The skill module is dynamically loaded from `/opt/mythos/eval/results/idea_backlog_manager/20260305_110943/temp_skill/test_skill.py`.
- **Test Case Execution**:
  - For each test case, the skill is invoked with a `SkillRequest` object.
  - The response is evaluated against expected outcomes (e.g., `expect_ok`, `expect_summary_contains`, `expect_data_has`).
- **Result Collection**:
  - Results are collected in a list of dictionaries, each representing the outcome of a test case.

#### Integration Points
- **Skill Module**: The skill module (`test_skill.py`) is dynamically loaded and must inherit from `SkillBase`.
- **Test Cases**: The test cases are read from `_test_cases.json` and are expected to have specific keys (`message`, `expect_ok`, `expect_summary_contains`, `expect_data_has`).
- **Output**: The results are printed in JSON format, which can be consumed by other parts of the system for further processing or reporting.

### Detailed Breakdown

1. **Dynamic Module Loading**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/idea_backlog_manager/20260305_110943/temp_skill/test_skill.py")
   module = importlib.util.module_from_spec(spec_obj)
   spec_obj.loader.exec_module(module)
   ```
   - This block dynamically loads the `test_skill.py` module from the specified path.

2. **Skill Class Identification**:
   ```python
   for attr_name in dir(module):
       attr = getattr(module, attr_name)
       if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
           skill_class = attr
           break
   ```
   - This loop identifies the skill class that inherits from `SkillBase`.

3. **Test Case Execution**:
   ```python
   async def run():
       for i, tc in enumerate(test_cases):
           tr = {"test_index": i, "message": tc["message"], "passed": [], "failed": []}
           try:
               req = SkillRequest(message=tc["message"])
               resp = await instance.run(req)
               # Evaluate response against expected outcomes
           except Exception as e:
               tr["failed"].append(f"Error: {e}")
           results.append(tr)
   ```
   - This asynchronous function runs each test case, evaluates the skill's response, and collects the results.

4. **Result Output**:
   ```python
   print(json.dumps({"results": results}))
   ```
   - The results are printed in JSON format, which can be easily consumed by other parts of the system.

This file serves as a critical component for testing and validating skills within the Mythos system, ensuring that they meet the expected criteria and function correctly.
