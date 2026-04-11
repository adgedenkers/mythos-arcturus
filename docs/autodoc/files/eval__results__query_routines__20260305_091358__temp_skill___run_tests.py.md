# eval/results/query_routines/20260305_091358/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/query_routines/20260305_091358/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and test a skill module (`test_skill.py`) against a set of predefined test cases (`_test_cases.json`). It runs the skill's `run` method asynchronously and evaluates the responses based on expected outcomes.

#### Architecture
- **Imports**: The file imports necessary modules (`sys`, `json`, `asyncio`, `traceback`, `importlib.util`).
- **Dynamic Module Loading**: It dynamically loads the `test_skill.py` module and identifies a class that inherits from `SkillBase`.
- **Test Execution**: The `run` function iterates over test cases, creates `SkillRequest` objects, and evaluates the skill's responses.
- **Error Handling**: The file includes comprehensive error handling to capture and report any issues during setup or test execution.

#### Patterns
- **Dynamic Module Loading**: Uses `importlib.util` to dynamically load the skill module.
- **Asynchronous Execution**: The `run` function is marked as `async` to handle asynchronous operations.

#### Dependencies
- **Imports**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **External Modules**: `engine.base` for `SkillBase` and `SkillRequest`
- **File Paths**: `/opt/mythos/skills`, `/opt/mythos/eval/results/query_routines/20260305_091358/temp_skill/test_skill.py`, `/opt/mythos/eval/results/query_routines/20260305_091358/temp_skill/_test_cases.json`

#### Interfaces
- **Exposed Function**: `run` (async function that executes the test cases and evaluates the skill's responses).

#### Database
- **PostgreSQL Table**: `engine` (used to import `SkillBase` and `SkillRequest` classes).

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
1. **Dynamic Module Loading**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/query_routines/20260305_091358/temp_skill/test_skill.py")
   module = importlib.util.module_from_spec(spec_obj)
   spec_obj.loader.exec_module(module)
   ```

2. **Identifying Skill Class**:
   ```python
   for attr_name in dir(module):
       attr = getattr(module, attr_name)
       if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
           skill_class = attr
           break
   ```

3. **Test Case Evaluation**:
   ```python
   async def run():
       for i, tc in enumerate(test_cases):
           tr = {"test_index": i, "message": tc["message"], "passed": [], "failed": []}
           try:
               req = SkillRequest(message=tc["message"])
               resp = await instance.run(req)
               if "expect_ok" in tc:
                   if resp.ok == tc["expect_ok"]:
                       tr["passed"].append(f"ok={resp.ok}")
                   else:
                       tr["failed"].append(f"Expected ok={tc['expect_ok']}, got {resp.ok} (error: {resp.error})")
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

#### Integration Points
- **Skill Module**: Dynamically loads and tests the `test_skill.py` module.
- **Test Cases**: Reads test cases from `_test_cases.json`.
- **SkillBase and SkillRequest**: Uses classes from `engine.base` to create and evaluate skill requests.
- **Output**: Prints JSON-formatted results to stdout, which can be captured and processed by other components of the Mythos system.
