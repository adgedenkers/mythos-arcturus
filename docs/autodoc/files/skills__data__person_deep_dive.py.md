# skills/data/person_deep_dive.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 71

---

### Documentation for `skills/data/person_deep_dive.py`

#### Purpose
The `PersonDeepDiveSkill` class in `person_deep_dive.py` is designed to perform a comprehensive deep dive on a person by aggregating data from multiple subsystems, including person lookup, natal chart, life events, and voice memos.

#### Architecture
- **Class Structure**: The class `PersonDeepDiveSkill` inherits from `SkillBase` and contains two primary methods: `execute` and `_run_skill`.
- **Data Flow**: The `execute` method orchestrates the execution of multiple sub-skills, each responsible for fetching a specific type of data. The `_run_skill` method dynamically loads and runs these sub-skills based on their module path and class name.

#### Patterns
- **Factory Pattern**: The `_run_skill` method acts as a factory to dynamically instantiate and run sub-skills.
- **Composite Pattern**: The `PersonDeepDiveSkill` class acts as a composite skill that aggregates the results from multiple sub-skills.

#### Dependencies
- **Imports**: 
  - `logging`: For logging errors and information.
  - `importlib`: For dynamically importing modules.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.

#### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: The main entry point for executing the deep dive skill.
  - `_run_skill(module_path, class_name, request)`: An internal method to dynamically run a sub-skill.

#### Database
- **PostgreSQL Table**: `engine` table is referenced, though the exact usage within the file is not explicitly shown in the provided code snippet.

#### Configuration
- **Environment Variables**: No direct usage of environment variables is shown in the provided code.
- **Config Files**: No explicit configuration files are used.

#### Key Logic
- **Aggregation of Sub-Skills**: The `execute` method iterates over predefined sub-skills (`SUB_SKILLS`), dynamically loads and runs each sub-skill using `_run_skill`, and aggregates the results.
- **Error Handling**: Both `execute` and `_run_skill` methods include error handling to log exceptions and return appropriate `SkillResponse` objects.

#### Integration Points
- **Sub-Skills Integration**: The `PersonDeepDiveSkill` integrates with multiple sub-skills (`PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, `SearchVoiceMemoSkill`) by dynamically loading and executing them.
- **SkillBase Interface**: The class inherits from `SkillBase` and implements the `execute` method, adhering to the skill interface defined in the `engine.base` module.

### Detailed Breakdown

#### Classes
- **PersonDeepDiveSkill**: 
  - **Attributes**:
    - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Metadata about the skill.
    - `SUB_SKILLS`: Dictionary mapping sub-skill labels to their module path and class name.
    - `LABELS`: Dictionary mapping sub-skill labels to their display labels.
  - **Methods**:
    - `execute(request: SkillRequest) -> SkillResponse`: Executes the deep dive by running all sub-skills and aggregating their results.
    - `_run_skill(module_path, class_name, request)`: Dynamically loads and runs a sub-skill.

#### Top-Level Functions
- **execute(request)**: This function is not defined at the top level but is part of the `PersonDeepDiveSkill` class.
- **_run_skill(module_path, class_name, request)**: This function is also part of the `PersonDeepDiveSkill` class.

#### Imports
- `logging`: For logging.
- `importlib`: For dynamic module loading.
- `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.

#### Database References
- **PostgreSQL Table**: `engine` table is referenced, though the exact usage within the file is not explicitly shown in the provided code snippet.

#### Configuration
- No direct configuration files or environment variables are used in the provided code.

#### Key Logic
- **Aggregation of Sub-Skills**: The `execute` method orchestrates the execution of multiple sub-skills, dynamically loading and running each one.
- **Error Handling**: Both `execute` and `_run_skill` methods include comprehensive error handling to ensure robustness.

#### Integration Points
- **Sub-Skills Integration**: The `PersonDeepDiveSkill` integrates with multiple sub-skills by dynamically loading and executing them.
- **SkillBase Interface**: The class adheres to the `SkillBase` interface by implementing the `execute` method.
