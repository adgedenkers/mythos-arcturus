# eval/results/format_person_summary/20260305_094735/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/format_person_summary/20260305_094735/temp_skill/_run_tests.py`

#### Purpose
This file is designed to run and evaluate tests for a specific skill module (`test_skill.py`) by comparing its output against predefined test cases stored in `_test_cases.json`. It uses asynchronous operations to handle the tests and outputs the results in JSON format.

#### Architecture
The file consists of a single top-level asynchronous function `run()` that orchestrates the test execution. The main logic is encapsulated within this function, which iterates over test cases, executes the skill, and collects the results. The file dynamically imports the skill module and checks for a class that inherits from `SkillBase`.

#### Patterns
- **Dynamic Module Loading**: The file dynamically loads the skill module using `importlib.util`.
- **Asynchronous Execution**: The `run()` function is asynchronous, leveraging `asyncio` for non-blocking operations.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `asyncio`, `traceback`
- **Custom Libraries**: `importlib.util`, `engine.base` (for `SkillBase` and `SkillRequest`)

#### Interfaces
- **Exposed Functions**: `run()` (an asynchronous function that runs the tests)
- **Output**: JSON-formatted test results printed to stdout

#### Database
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` and `SkillRequest`)

#### Configuration
- **Environment Variables**: None
- **Config Files**: `_test_cases.json` (contains test cases)

#### Key Logic
1. **Dynamic Import**: The skill module is dynamically imported from a specified file path.
2. **Test Case Execution**: Each test case is processed, and the skill's response is evaluated against expected outcomes.
3. **Result Aggregation**: Results are aggregated into a list of dictionaries, each representing the outcome of a test case.

#### Integration Points
- **Skill Module**: The file dynamically imports and uses a skill module (`test_skill.py`).
- **Test Cases**: The file reads test cases from `_test_cases.json`.
- **SkillBase and SkillRequest**: The file uses these classes from the `engine.base` module to create and process skill requests.

### Detailed Breakdown

#### Dynamic Module Loading
The file dynamically loads the skill module using `importlib.util`:
```python
spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/format_person_summary/20260305_094735/temp_skill/test_skill.py")
module = importlib.util.module_from_spec(spec_obj)
spec_obj.loader.exec_module(module)
```

#### Test Case Processing
The file reads test cases from `_test_cases.json` and processes each one:
```python
with open("/opt/mythos/eval/results/format_person_summary/20260305_094735/temp_skill/_test_cases.json") as _tc_f:
    test_cases = json.load(_tc_f)
```

#### Asynchronous Test Execution
The `run()` function is asynchronous and processes each test case:
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

#### Result Aggregation
Results are aggregated into a list of dictionaries:
```python
results.append(tr)
```

#### Error Handling
The file handles exceptions and prints error messages in JSON format:
```python
except Exception as e:
    results = [{"test_index": -1, "passed": [], "failed": [f"Setup error: {e}"]}]
print(json.dumps({"results": results}))
```

This file is crucial for evaluating the functionality of the skill module and ensuring it meets the expected outcomes based on predefined test cases.
