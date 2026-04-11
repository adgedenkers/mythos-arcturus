# eval/results/search_life_events/20260305_061912/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: eval/results/search_life_events/20260305_061912/temp_skill/_run_tests.py

#### Purpose
This file is designed to dynamically load and test a skill module (`test_skill.py`) against a set of predefined test cases (`_test_cases.json`). It evaluates the skill's performance based on expected outcomes and reports the results in JSON format.

#### Architecture
- **Functions**: 
  - `run()`: An asynchronous function that iterates through test cases, runs the skill, and collects results.
- **Data Flow**:
  - The file dynamically imports the `test_skill.py` module and identifies a class that inherits from `SkillBase`.
  - It reads test cases from `_test_cases.json`.
  - For each test case, it creates a `SkillRequest`, runs the skill, and checks the response against expected outcomes.
  - Results are collected and printed as JSON.

#### Patterns
- **Dynamic Import**: Uses `importlib.util` to dynamically import and execute the `test_skill.py` module.
- **Error Handling**: Uses try-except blocks to handle exceptions and report errors in the results.

#### Dependencies
- **Imports**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **External Modules**: `engine.base` for `SkillBase` and `SkillRequest`

#### Interfaces
- **Exposed Functions**: 
  - `run()`: An asynchronous function that processes test cases and returns results.

#### Database
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` and `SkillRequest`)

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
- **Dynamic Module Loading**: 
  - The file dynamically loads the `test_skill.py` module and identifies a class that inherits from `SkillBase`.
- **Test Case Execution**:
  - For each test case, it creates a `SkillRequest` and runs the skill.
  - It checks the response against expected outcomes (`expect_ok`, `expect_summary_contains`, `expect_data_has`).
- **Result Aggregation**:
  - Results are aggregated into a list of dictionaries, each representing the outcome of a test case.

#### Integration Points
- **Skill Module**: Integrates with the dynamically loaded `test_skill.py` module.
- **Test Cases**: Reads test cases from `_test_cases.json`.
- **SkillBase and SkillRequest**: Uses `SkillBase` and `SkillRequest` from the `engine.base` module to interact with the skill.

### Detailed Breakdown

#### Dynamic Module Loading
The file uses `importlib.util` to dynamically load the `test_skill.py` module:
```python
spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/search_life_events/20260305_061912/temp_skill/test_skill.py")
module = importlib.util.module_from_spec(spec_obj)
spec_obj.loader.exec_module(module)
```
It then searches for a class that inherits from `SkillBase`:
```python
for attr_name in dir(module):
    attr = getattr(module, attr_name)
    if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
        skill_class = attr
        break
```

#### Test Case Execution
The `run()` function is an asynchronous function that processes each test case:
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
            # Check summary contains expected keywords
            for kw in tc.get("expect_summary_contains", []):
                if kw.lower() in resp.summary.lower():
                    tr["passed"].append(f"summary has '{kw}'")
                else:
                    tr["failed"].append(f"summary missing '{kw}': {resp.summary[:200]}")
            # Check data contains expected keys
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

#### Result Aggregation and Reporting
Results are aggregated into a list and printed as JSON:
```python
print(json.dumps({"results": results}))
```

This file serves as a critical component for testing and validating skills within the Mythos system, ensuring they meet the expected performance criteria.
