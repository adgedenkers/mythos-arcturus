# eval/results/log_life_event/20260305_092500/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/log_life_event/20260305_092500/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and execute a skill module for testing purposes. It reads test cases from a JSON file, runs each test case against the skill, and collects the results.

#### Architecture
The file consists of a single asynchronous function `run` that orchestrates the test execution. The main logic is wrapped in a try-except block to handle any exceptions that may occur during the process. The file dynamically imports a skill module and tests it against predefined test cases.

#### Patterns
- **Dynamic Import**: Uses `importlib.util` to dynamically import the skill module.
- **Asynchronous Execution**: The `run` function is asynchronous and uses `asyncio.run` to execute the tests.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **Custom Modules**: `engine.base` (for `SkillBase` and `SkillRequest`)

#### Interfaces
- **Exposed Functions**: `run` (async function)
- **Output**: JSON-formatted test results printed to stdout

#### Database
- **Postgres Table**: `engine` (likely used for storing skill-related data, but not directly accessed in this file)

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
1. **Dynamic Module Import**: The skill module is dynamically loaded from a specified file location.
2. **Test Case Execution**: Each test case is executed against the skill instance, and the results are collected.
3. **Result Aggregation**: Results are aggregated into a list of dictionaries, each representing the outcome of a test case.

#### Integration Points
- **Skill Module**: The skill module is loaded from `/opt/mythos/eval/results/log_life_event/20260305_092500/temp_skill/test_skill.py`.
- **Test Cases**: Test cases are read from `/opt/mythos/eval/results/log_life_event/20260305_092500/temp_skill/_test_cases.json`.
- **SkillBase**: The skill module must contain a class that inherits from `SkillBase` from the `engine.base` module.

### Detailed Breakdown

#### Dynamic Module Import
```python
spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/log_life_event/20260305_092500/temp_skill/test_skill.py")
module = importlib.util.module_from_spec(spec_obj)
spec_obj.loader.exec_module(module)
```
This block dynamically loads the skill module from the specified file path.

#### Skill Class Identification
```python
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
        skill_class = attr
        break
```
This loop iterates over the attributes of the imported module to find a class that inherits from `SkillBase`.

#### Test Case Execution
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
This asynchronous function iterates over each test case, creates a `SkillRequest`, and calls the `run` method of the skill instance. It then checks the response against expected outcomes and collects the results.

#### Exception Handling
```python
except Exception as e:
    results = [{"test_index": -1, "passed": [], "failed": [f"Setup error: {e}"]}]
```
Any exceptions that occur during setup or test execution are caught and logged as a setup error.

#### Output
```python
print(json.dumps({"results": results}))
```
The final results are printed as a JSON-formatted string to stdout.

This file is a critical component of the Mythos system for testing and validating skills dynamically, ensuring they meet the expected behavior as defined in the test cases.
