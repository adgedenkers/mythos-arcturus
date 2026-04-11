# eval/results/daily_task_planner/20260305_110051/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/daily_task_planner/20260305_110051/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and test a skill module (`test_skill.py`) against a set of predefined test cases (`_test_cases.json`). It evaluates the skill's responses and outputs the results in JSON format.

#### Architecture
The file consists of a single asynchronous function `run` that iterates through a list of test cases, executes each test case against the skill instance, and collects the results. The main logic is wrapped in a try-except block to handle any exceptions during the setup or execution.

#### Patterns
- **Dynamic Module Loading**: The file dynamically loads a module using `importlib.util`, which is a form of the **Factory** pattern, where the module is created based on a specified file path.
- **Error Handling**: Uses a try-except block to handle exceptions, which is a common pattern for robust error management.

#### Dependencies
- `sys`: For manipulating the system path and exiting the program.
- `json`: For reading and writing JSON data.
- `asyncio`: For running asynchronous tasks.
- `traceback`: For handling exceptions.
- `importlib.util`: For dynamically importing modules.

#### Interfaces
- **Exposed Functions**: 
  - `async def run()`: The main function that runs the test cases asynchronously.

#### Database
- **PostgreSQL Table**: `engine`
  - The file imports `SkillBase` and `SkillRequest` from `engine.base`, indicating that it interacts with the `engine` table in PostgreSQL.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: 
  - `_test_cases.json`: Contains the test cases to be executed.
  - `test_skill.py`: The skill module to be tested.

#### Key Logic
1. **Dynamic Module Loading**: The skill module is dynamically loaded using `importlib.util`.
2. **Test Case Execution**: Each test case is executed by creating a `SkillRequest` object and calling the `run` method of the skill instance.
3. **Result Collection**: Results are collected in a list of dictionaries, each containing the test index, message, passed conditions, and failed conditions.
4. **Error Handling**: Any exceptions during setup or execution are caught and logged as failed tests.

#### Integration Points
- **Skill Module**: The file dynamically loads and tests a skill module (`test_skill.py`).
- **Test Cases**: The file reads test cases from `_test_cases.json`.
- **Database**: The file interacts with the `engine` table in PostgreSQL through the `SkillBase` and `SkillRequest` classes.

### Detailed Breakdown

1. **Dynamic Module Loading**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/daily_task_planner/20260305_110051/temp_skill/test_skill.py")
   module = importlib.util.module_from_spec(spec_obj)
   spec_obj.loader.exec_module(module)
   ```

2. **Skill Class Identification**:
   ```python
   for attr_name in dir(module):
       attr = getattr(module, attr_name)
       if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
           skill_class = attr
           break
   ```

3. **Test Case Execution**:
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
               # Check summary and data keys
               for kw in tc.get("expect_summary_contains", []):
                   if kw.lower() in resp.summary.lower():
                       tr["passed"].append(f"summary has '{kw}'")
                   else:
                       tr["failed"].append(f"summary missing '{kw}': {resp.summary[:200]}")
               for key in tc.get("expect_data_has", []):
                   if key in resp.data:
                       tr["passed"].append(f"data has '{key}'")
                   else:
                       tr["failed"].append(f"data missing '{key}': {list(resp.data.keys())}")
               if resp.summary:
                   tr["passed"].append("summary non-empty")
               else:
                   tr["failed"].append("summary empty")
           except Exception as e:
               tr["failed"].append(f"Error: {e}")
           results.append(tr)
   ```

4. **Result Output**:
   ```python
   print(json.dumps({"results": results}))
   ```

This file serves as a critical component for testing and validating the functionality of dynamically loaded skill modules within the Mythos system.
