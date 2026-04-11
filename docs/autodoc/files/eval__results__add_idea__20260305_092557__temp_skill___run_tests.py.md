# eval/results/add_idea/20260305_092557/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/add_idea/20260305_092557/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and test a skill module (`test_skill.py`) by running predefined test cases against it. The results of these tests are collected and printed in JSON format.

#### Architecture
The file consists of a single top-level asynchronous function `run` that orchestrates the testing process. The main steps include:
1. Dynamically importing the `test_skill.py` module.
2. Identifying a class that inherits from `SkillBase`.
3. Loading test cases from `_test_cases.json`.
4. Running each test case and collecting results.

#### Patterns
- **Dynamic Module Loading**: The file uses `importlib.util` to dynamically load the `test_skill.py` module.
- **Asynchronous Execution**: The `run` function is asynchronous, allowing for non-blocking execution of tests.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `asyncio`, `traceback`
- **Custom Libraries**: `importlib.util`, `engine.base` (for `SkillBase` and `SkillRequest`)

#### Interfaces
- **Exposed Function**: `run` (async function that orchestrates the testing process)
- **Output**: JSON-formatted test results printed to stdout

#### Database
- **PostgreSQL Table**: `engine` (used to import `SkillBase` and `SkillRequest` classes)

#### Configuration
- **Environment Variables**: None
- **Config Files**: `_test_cases.json` (contains the test cases to be run)

#### Key Logic
1. **Dynamic Module Import**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/add_idea/20260305_092557/temp_skill/test_skill.py")
   module = importlib.util.module_from_spec(spec_obj)
   spec_obj.loader.exec_module(module)
   ```

2. **Identify Skill Class**:
   ```python
   for attr_name in dir(module):
       attr = getattr(module, attr_name)
       if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
           skill_class = attr
           break
   ```

3. **Run Test Cases**:
   ```python
   async def run():
       for i, tc in enumerate(test_cases):
           tr = {"test_index": i, "message": tc["message"], "passed": [], "failed": []}
           try:
               req = SkillRequest(message=tc["message"])
               resp = await instance.run(req)
               # Check expected outcomes
               if "expect_ok" in tc:
                   if resp.ok == tc["expect_ok"]:
                       tr["passed"].append(f"ok={resp.ok}")
                   else:
                       tr["failed"].append(f"Expected ok={tc['expect_ok']}, got {resp.ok} (error: {resp.error})")
               # Additional checks for summary and data
           except Exception as e:
               tr["failed"].append(f"Error: {e}")
           results.append(tr)
   ```

#### Integration Points
- **Skill Module**: Dynamically imports and uses a skill module (`test_skill.py`).
- **Test Cases**: Loads and processes test cases from `_test_cases.json`.
- **SkillBase and SkillRequest**: Uses classes from `engine.base` to create and run skill requests.
- **Output**: Prints JSON-formatted results to stdout, which can be captured and processed by other parts of the system.

This file serves as a crucial component in the Mythos system for validating and testing newly developed skill modules, ensuring they meet the expected criteria before being integrated into the broader system.
