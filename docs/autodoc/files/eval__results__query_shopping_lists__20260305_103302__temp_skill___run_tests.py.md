# eval/results/query_shopping_lists/20260305_103302/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/query_shopping_lists/20260305_103302/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and test a skill module (`test_skill.py`) against a set of test cases defined in `_test_cases.json`. It runs the skill's `run` method asynchronously, evaluates the responses against expected outcomes, and outputs the results in JSON format.

#### Architecture
- **Functions**:
  - `run`: An asynchronous function that iterates over test cases, executes the skill's `run` method, and evaluates the response against expected outcomes.
- **Data Flow**:
  1. The script dynamically imports the `test_skill.py` module.
  2. It identifies a class that inherits from `SkillBase`.
  3. It loads test cases from `_test_cases.json`.
  4. It runs each test case asynchronously, evaluates the response, and collects results.
  5. The results are printed in JSON format.

#### Patterns
- **Dynamic Module Loading**: The script uses `importlib.util` to dynamically load the `test_skill.py` module.
- **Asynchronous Execution**: The `run` function is asynchronous, using `asyncio` to handle test case execution.

#### Dependencies
- **Imports**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **External Modules**: `engine.base` for `SkillBase` and `SkillRequest`
- **File Paths**: `/opt/mythos/eval/results/query_shopping_lists/20260305_103302/temp_skill/test_skill.py`, `/opt/mythos/eval/results/query_shopping_lists/20260305_103302/temp_skill/_test_cases.json`

#### Interfaces
- **Exposed Functions**: `run` (asynchronous)
- **Output**: JSON-formatted test results printed to stdout.

#### Database
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` and `SkillRequest`)

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
- **Dynamic Skill Loading**: The script dynamically imports and instantiates a skill class that inherits from `SkillBase`.
- **Test Case Execution**: Each test case is executed asynchronously, and the skill's response is evaluated against expected outcomes.
- **Result Collection**: Results are collected in a list of dictionaries, each representing the outcome of a test case.

#### Integration Points
- **Skill Module**: The script dynamically loads and tests a skill module (`test_skill.py`).
- **Test Cases**: The script reads test cases from `_test_cases.json`.
- **SkillBase**: The script relies on the `SkillBase` class and `SkillRequest` from the `engine.base` module to run and evaluate the skill's responses.

### Detailed Breakdown

1. **Dynamic Module Loading**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/query_shopping_lists/20260305_103302/temp_skill/test_skill.py")
   module = importlib.util.module_from_spec(spec_obj)
   spec_obj.loader.exec_module(module)
   ```
   This code dynamically loads the `test_skill.py` module and makes it available for use.

2. **Skill Class Identification**:
   ```python
   for attr_name in dir(module):
       attr = getattr(module, attr_name)
       if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
           skill_class = attr
           break
   ```
   This loop identifies a class in the module that inherits from `SkillBase`.

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
   This asynchronous function iterates over each test case, executes the skill's `run` method, and evaluates the response against expected outcomes.

4. **Result Output**:
   ```python
   print(json.dumps({"results": results}))
   ```
   The results are printed in JSON format, providing a structured output of the test outcomes.

This file serves as a critical component of the Mythos system, enabling dynamic testing of skill modules against predefined test cases.
