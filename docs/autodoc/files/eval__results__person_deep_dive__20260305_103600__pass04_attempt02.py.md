# eval/results/person_deep_dive/20260305_103600/pass04_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 105

---

### Documentation for `pass04_attempt02.py`

#### Purpose
This file defines the `PersonDeepDiveSkill` class, which is responsible for executing a deep dive into a person's profile by aggregating data from multiple sub-skills. It handles the orchestration of these sub-skills and builds a comprehensive profile summary.

#### Architecture
- **Class Structure**: 
  - `PersonDeepDiveSkill` inherits from `SkillBase`.
  - Contains methods: `execute`, `_run_skill`, `_build_profile`.
- **Data Flow**:
  - The `execute` method orchestrates the execution of sub-skills.
  - `_run_skill` dynamically imports and runs sub-skills.
  - `_build_profile` aggregates and formats the results into a summary.

#### Patterns
- **Factory Method**: `_run_skill` dynamically creates instances of sub-skills using `importlib`.
- **Composite**: The `execute` method combines results from multiple sub-skills into a single response.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors and information.
  - `importlib`: For dynamic module and class loading.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response structures.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Main method to execute the skill, taking a `SkillRequest` and returning a `SkillResponse`.
  - `_run_skill`: Internal method to run a specific sub-skill.
  - `_build_profile`: Internal method to build the profile summary from sub-skill results.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Likely used for storing engine-related configurations or metadata.
  - `sub`: Likely used for storing sub-skill configurations or metadata.

#### Configuration
- **Environment Variables**: None explicitly used in this file.
- **Config Files**: None explicitly used in this file.

#### Key Logic
- **Sub-Skill Execution**:
  - The `execute` method iterates over predefined sub-skills, dynamically imports and runs each one using `_run_skill`.
  - Results are aggregated into a dictionary.
- **Profile Building**:
  - `_build_profile` constructs a summary from the aggregated results, ensuring ASCII compatibility and handling empty data gracefully.
- **Error Handling**:
  - Errors during sub-skill execution are logged, and the system ensures a non-empty summary is always returned.

#### Integration Points
- **Sub-Skills**:
  - `data.people_lookup.PeopleLookupSkill`
  - `data.query_natal_chart.QueryNatalChartSkill`
  - `data.search_life_events.SearchLifeEventsSkill`
  - `data.search_voice_memos.SearchVoiceMemoSkill`
- **SkillBase**:
  - Inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` for request and response handling.
- **Logging**:
  - Uses `logging` to log errors and information during execution.

### Summary
The `PersonDeepDiveSkill` class in `pass04_attempt02.py` orchestrates a deep dive into a person's profile by dynamically executing multiple sub-skills. It aggregates the results and builds a comprehensive profile summary, ensuring robust error handling and ASCII compatibility. The class integrates with other subsystems through dynamic module loading and uses logging for error tracking.
