# eval/results/person_deep_dive/20260305_103600/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 108

---

### File: `eval/results/person_deep_dive/20260305_103600/temp_skill/test_skill.py`

#### Purpose
This file defines a `PersonDeepDiveSkill` class that performs a deep dive into a person's profile by aggregating data from multiple sub-skills. It handles requests, executes sub-skills, and builds a comprehensive profile summary.

#### Architecture
- **Classes**:
  - `PersonDeepDiveSkill`: Inherits from `SkillBase`. Contains methods `execute`, `_run_skill`, and `_build_profile`.
- **Functions**:
  - `execute`: Main method to process the request and aggregate results from sub-skills.
  - `_run_skill`: Executes a specific sub-skill by dynamically importing and running it.
  - `_build_profile`: Constructs a profile summary from the aggregated results.

#### Patterns
- **Factory Pattern**: Used in `_run_skill` to dynamically instantiate and run sub-skills based on module and class names.
- **Composite Pattern**: Aggregates results from multiple sub-skills into a single comprehensive profile.

#### Dependencies
- `logging`: For logging errors and information.
- `importlib`: For dynamically importing modules.
- `SkillBase`, `SkillRequest`, `SkillResponse`: Imported from `engine.base`.

#### Interfaces
- **Public Methods**:
  - `execute`: Takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_run_skill`: Takes `module_name`, `class_name`, and `request`, returns a `SkillResponse`.
  - `_build_profile`: Takes `request` and `results`, returns a `str`.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Likely used for storing skill-related configurations or metadata.
  - `sub`: Likely used for storing sub-skill configurations or metadata.

#### Configuration
- **Environment Variables**: None explicitly used in this file.
- **Configuration Files**: None explicitly used in this file.

#### Key Logic
- **Main Execution Logic**:
  - The `execute` method iterates over predefined sub-skills, dynamically imports and runs each one, and aggregates their results.
  - `_run_skill` dynamically imports and instantiates a sub-skill, then runs it with the given request.
  - `_build_profile` constructs a summary from the aggregated results, ensuring ASCII-only characters and handling empty summaries gracefully.

#### Integration Points
- **Sub-Skills**:
  - `data.people_lookup.PeopleLookupSkill`
  - `data.query_natal_chart.QueryNatalChartSkill`
  - `data.search_life_events.SearchLifeEventsSkill`
  - `data.search_voice_memos.SearchVoiceMemoSkill`
- **SkillBase**: The `PersonDeepDiveSkill` class inherits from `SkillBase`, which likely provides a common interface and base functionality for all skills.
- **SkillRequest and SkillResponse**: Used to standardize the input and output of the skill execution.

### Summary
The `PersonDeepDiveSkill` class in `test_skill.py` is designed to perform a comprehensive deep dive into a person's profile by aggregating data from multiple sub-skills. It dynamically imports and runs these sub-skills, then constructs a detailed profile summary. The class handles errors gracefully and ensures that the summary is never empty. It integrates with other subsystems through the `SkillBase` class and uses PostgreSQL tables for configuration and metadata storage.
