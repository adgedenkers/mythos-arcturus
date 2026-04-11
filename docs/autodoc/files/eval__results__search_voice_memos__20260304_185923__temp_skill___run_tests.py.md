# eval/results/search_voice_memos/20260304_185923/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/search_voice_memos/20260304_185923/temp_skill/_run_tests.py`

#### Purpose
This file is designed to run tests on a dynamically imported skill module, `test_skill.py`, and evaluate its performance based on predefined test cases stored in `_test_cases.json`. It outputs the test results in JSON format.

#### Architecture
- **Functions**: 
  - `run()`: An asynchronous function that iterates over test cases, runs the skill, and collects results.
- **Data Flow**:
  1. Import the `test_skill.py` module dynamically.
  2. Load test cases from `_test_cases.json`.
  3. For each test case, create a `SkillRequest` and run the skill.
  4. Collect results based on expected outcomes and actual responses.
  5. Output results in JSON format.

#### Patterns
- **Dynamic Module Loading**: Uses `importlib.util` to dynamically load the `test_skill.py` module.
- **Exception Handling**: Uses try-except blocks to handle errors gracefully and report them in the results.

#### Dependencies
- **Imports**:
  - `sys`: For system-specific parameters and functions.
  - `json`: For JSON serialization and deserialization.
  - `asyncio`: For asynchronous execution.
  - `traceback`: For handling exceptions.
  - `importlib.util`: For dynamic module loading.
- **Database References**:
  - `engine`: PostgreSQL table used for skill-related operations.

#### Interfaces
- **Exposed Functions**:
  - `run()`: An asynchronous function that processes test cases and collects results.

#### Database
- **PostgreSQL**:
  - **Table**: `engine`
  - **Operations**: Reads skill-related configurations or data.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Dynamic Skill Loading**: Dynamically imports the `test_skill.py` module and identifies the skill class that inherits from `SkillBase`.
- **Test Case Execution**: Iterates over test cases, creates `SkillRequest` objects, and runs the skill asynchronously.
- **Result Collection**: Compares expected outcomes with actual responses and collects results in a structured format.

#### Integration Points
- **Skill Module**: Integrates with the dynamically loaded `test_skill.py` module.
- **Test Cases**: Integrates with the `_test_cases.json` file to load test cases.
- **SkillBase Class**: Uses the `SkillBase` class from the `engine.base` module to ensure the skill class is correctly instantiated.
- **SkillRequest Class**: Uses the `SkillRequest` class from the `engine.base` module to create request objects for the skill.

### Detailed Analysis

#### Dynamic Module Loading
The file dynamically loads the `test_skill.py` module using `importlib.util`:
```python
spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/search_voice_memos/20260304_185923/temp_skill/test_skill.py")
module = importlib.util.module_from_spec(spec_obj)
spec_obj.loader.exec_module(module)
```

#### Skill Class Identification
Identifies the skill class that inherits from `SkillBase`:
```python
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
        skill_class = attr
        break
```

#### Test Case Execution
Iterates over test cases, creates `SkillRequest` objects, and runs the skill asynchronously:
```python
async def run():
    for i, tc in enumerate(test_cases):
        tr = {"test_index": i, "message": tc["message"], "passed": [], "failed": []}
        try:
            req = SkillRequest(message=tc["message"])
            resp = await instance.run(req)
            # Compare expected outcomes with actual responses
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

#### Result Collection
Collects results in a structured format and outputs them in JSON:
```python
print(json.dumps({"results": results}))
```

This file serves as a critical component of the Mythos system for testing and validating skills dynamically, ensuring they meet the expected performance criteria.
