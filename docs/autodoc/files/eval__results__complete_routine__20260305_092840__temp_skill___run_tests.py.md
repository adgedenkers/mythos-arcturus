# eval/results/complete_routine/20260305_092840/temp_skill/_run_tests.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 55

---

### File: `eval/results/complete_routine/20260305_092840/temp_skill/_run_tests.py`

#### Purpose
This file is designed to dynamically load and run test cases for a skill module in the Mythos system. It imports a skill class from a specified module, executes test cases, and collects results.

#### Architecture
The file consists of a single asynchronous function `run` that performs the following steps:
1. Dynamically imports a skill module from a specified file.
2. Identifies the skill class that inherits from `SkillBase`.
3. Loads test cases from a JSON file.
4. Executes each test case by creating a `SkillRequest`, invoking the skill's `run` method, and comparing the response against expected outcomes.
5. Collects and formats the results.

#### Patterns
- **Dynamic Module Loading**: Uses `importlib.util` to dynamically load a module from a file.
- **Asynchronous Execution**: The `run` function is asynchronous, allowing for non-blocking execution of test cases.

#### Dependencies
- **Standard Libraries**: `sys`, `json`, `asyncio`, `traceback`, `importlib.util`
- **Custom Modules**: `engine.base` (for `SkillBase` and `SkillRequest`)

#### Interfaces
- **Exposed Function**: `run` (asynchronous)
- **Output**: JSON-formatted results printed to stdout.

#### Database
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` and `SkillRequest`)

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
1. **Dynamic Module Import**:
   ```python
   spec_obj = importlib.util.spec_from_file_location("test_skill", "/opt/mythos/eval/results/complete_routine/20260305_092840/temp_skill/test_skill.py")
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
               # Compare response against expected outcomes
           except Exception as e:
               tr["failed"].append(f"Error: {e}")
           results.append(tr)
   ```

#### Integration Points
- **Skill Module**: Dynamically loads and executes a skill module from `/opt/mythos/eval/results/complete_routine/20260305_092840/temp_skill/test_skill.py`.
- **Test Cases**: Loads test cases from `/opt/mythos/eval/results/complete_routine/20260305_092840/temp_skill/_test_cases.json`.
- **SkillBase and SkillRequest**: Uses classes from `engine.base` to interact with the skill and handle requests.
- **Output**: Results are printed in JSON format to stdout, which can be captured and processed by other parts of the system.

This file serves as a crucial component in the automated testing workflow of the Mythos system, ensuring that newly developed or modified skills meet the expected standards and behaviors.
