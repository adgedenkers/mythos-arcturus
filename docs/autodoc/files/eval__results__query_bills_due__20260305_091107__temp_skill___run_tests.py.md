# eval/results/query_bills_due/20260305_091107/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/query_bills_due/20260305_091107/temp_skill/_run_tests.py`

#### Purpose
This file is designed to run tests on a dynamically imported skill module, specifically testing its response to various test cases defined in a JSON file. It evaluates the skill's output against expected outcomes and logs the results.

#### Architecture
- **Functions**: The file contains a single top-level function `run` which is an asynchronous function.
- **Data Flow**: The script imports a skill module, reads test cases from a JSON file, and runs each test case against the skill. The results are collected and printed in JSON format.
- **Error Handling**: The script uses try-except blocks to handle exceptions and log errors.

#### Patterns
- **Dynamic Import**: The script dynamically imports a module using `importlib.util`.
- **Singleton**: The skill instance is created once and reused for all test cases.

#### Dependencies
- **Imports**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **External Modules**: `engine.base` for `SkillBase` and `SkillRequest`

#### Interfaces
- **Exposed Functions**: `run` (async function)
- **Output**: JSON-formatted test results printed to stdout.

#### Database
- **References**: The script interacts with the `engine` table in PostgreSQL to load the `SkillBase` class.

#### Configuration
- **Environment Variables**: None
- **Config Files**: The script reads test cases from `/opt/mythos/eval/results/query_bills_due/20260305_091107/temp_skill/_test_cases.json`.

#### Key Logic
1. **Dynamic Module Import**: The script dynamically imports a skill module from a specified location.
2. **Test Case Execution**: For each test case, it creates a `SkillRequest` and invokes the `run` method of the skill instance.
3. **Result Evaluation**: The script checks if the response matches expected outcomes (e.g., `ok` status, summary content, data keys) and logs the results.

#### Integration Points
- **Skill Module**: The script dynamically imports and uses a skill module from `/opt/mythos/eval/results/query_bills_due/20260305_091107/temp_skill/test_skill.py`.
- **Test Cases**: The script reads test cases from `/opt/mythos/eval/results/query_bills_due/20260305_091107/temp_skill/_test_cases.json`.
- **Engine Module**: The script imports `SkillBase` and `SkillRequest` from the `engine.base` module, which is assumed to be part of the Mythos system.

### Detailed Analysis

#### Purpose
The script is a test runner for a dynamically loaded skill module. It reads test cases from a JSON file, executes each test case against the skill, and logs the results.

#### Architecture
- **Main Function**: `run` is an asynchronous function that iterates over test cases and evaluates the skill's response.
- **Data Flow**:
  1. Import the skill module dynamically.
  2. Read test cases from a JSON file.
  3. For each test case, create a `SkillRequest` and invoke the skill's `run` method.
  4. Evaluate the response against expected outcomes.
  5. Collect and print the results in JSON format.

#### Patterns
- **Dynamic Import**: The script uses `importlib.util` to dynamically import the skill module.
- **Singleton**: The skill instance is created once and reused for all test cases.

#### Dependencies
- **Imports**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **External Modules**: `engine.base` for `SkillBase` and `SkillRequest`

#### Interfaces
- **Exposed Functions**: `run` (async function)
- **Output**: JSON-formatted test results printed to stdout.

#### Database
- **References**: The script interacts with the `engine` table in PostgreSQL to load the `SkillBase` class.

#### Configuration
- **Environment Variables**: None
- **Config Files**: The script reads test cases from `/opt/mythos/eval/results/query_bills_due/20260305_091107/temp_skill/_test_cases.json`.

#### Key Logic
1. **Dynamic Module Import**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/query_bills_due/20260305_091107/temp_skill/test_skill.py")
   module = importlib.util.module_from_spec(spec_obj)
   spec_obj.loader.exec_module(module)
   ```
2. **Test Case Execution**:
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
3. **Result Evaluation**:
   ```python
   if "expect_ok" in tc:
       if resp.ok == tc["expect_ok"]:
           tr["passed"].append(f"ok={resp.ok}")
       else:
           tr["failed"].append(f"Expected ok={tc['expect_ok']}, got {resp.ok} (error: {resp.error})")
   ```

#### Integration Points
- **Skill Module**: The script dynamically imports and uses a skill module from `/opt/mythos/eval/results/query_bills_due/20260305_091107/temp_skill/test_skill.py`.
- **Test Cases**: The script reads test cases from `/opt/mythos/eval/results/query_bills_due/20260305_091107/temp_skill/_test_cases.json`.
- **Engine Module**: The script imports `SkillBase` and `SkillRequest` from the `engine.base` module, which is assumed to be part of the Mythos system.
