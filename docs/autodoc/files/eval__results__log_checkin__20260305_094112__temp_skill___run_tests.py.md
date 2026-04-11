# eval/results/log_checkin/20260305_094112/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/log_checkin/20260305_094112/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically import and test a skill module (`test_skill.py`) against a set of test cases defined in `_test_cases.json`. It evaluates the skill's responses and logs the results in JSON format.

#### Architecture
- **Functions**: 
  - `run()`: An asynchronous function that iterates over test cases, runs the skill, and evaluates the response.
- **Data Flow**:
  - The file dynamically imports the `test_skill.py` module and checks for a subclass of `SkillBase`.
  - It reads test cases from `_test_cases.json` and processes each case by creating a `SkillRequest` and invoking the skill's `run` method.
  - Results are collected in a list and printed as a JSON object.

#### Patterns
- **Dynamic Import**: Uses `importlib.util` to dynamically import the skill module.
- **Asynchronous Execution**: Uses `asyncio` to handle asynchronous operations.

#### Dependencies
- **Imports**:
  - `sys`: For path manipulation and system exit.
  - `json`: For reading and writing JSON data.
  - `asyncio`: For asynchronous execution.
  - `traceback`: For handling exceptions.
  - `importlib.util`: For dynamic module importing.
- **External Modules**:
  - `engine.base`: For `SkillBase` and `SkillRequest`.

#### Interfaces
- **Exposed Functions**:
  - `async def run()`: The main asynchronous function that processes test cases and evaluates the skill's responses.

#### Database
- **PostgreSQL Table**: `engine`
  - The file does not directly interact with the `engine` table but relies on the `SkillBase` class which might interact with the database.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
- **Dynamic Import and Class Detection**:
  - The file dynamically imports `test_skill.py` and searches for a subclass of `SkillBase`.
- **Test Case Processing**:
  - For each test case, it creates a `SkillRequest` and invokes the skill's `run` method.
  - It evaluates the response based on predefined criteria such as `expect_ok`, `expect_summary_contains`, and `expect_data_has`.
- **Result Collection**:
  - Results are collected in a list and printed as a JSON object.

#### Integration Points
- **Skill Module**: The file dynamically imports and uses the `test_skill.py` module.
- **Test Cases**: It reads test cases from `_test_cases.json`.
- **SkillBase Class**: It relies on the `SkillBase` class from `engine.base` for the skill's base functionality.
- **SkillRequest Class**: It uses the `SkillRequest` class from `engine.base` to create requests for the skill.

### Detailed Breakdown

1. **Dynamic Import**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/log_checkin/20260305_094112/temp_skill/test_skill.py")
   module = importlib.util.module_from_spec(spec_obj)
   spec_obj.loader.exec_module(module)
   ```
   This block dynamically imports the `test_skill.py` module.

2. **Class Detection**:
   ```python
   skill_class = None
   for attr_name in dir(module):
       attr = getattr(module, attr_name)
       if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
           skill_class = attr
           break
   ```
   This block searches for a subclass of `SkillBase` in the imported module.

3. **Test Case Processing**:
   ```python
   async def run():
       for i, tc in enumerate(test_cases):
           tr = {"test_index": i, "message": tc["message"], "passed": [], "failed": []}
           try:
               req = SkillRequest(message=tc["message"])
               resp = await instance.run(req)
               # Evaluate response based on test case criteria
           except Exception as e:
               tr["failed"].append(f"Error: {e}")
           results.append(tr)
   ```
   This asynchronous function processes each test case, creates a `SkillRequest`, and evaluates the skill's response.

4. **Result Collection and Output**:
   ```python
   print(json.dumps({"results": results}))
   ```
   The results are collected in a list and printed as a JSON object.

This file serves as a critical component in the Mythos system for evaluating the functionality of dynamically loaded skill modules against predefined test cases.
