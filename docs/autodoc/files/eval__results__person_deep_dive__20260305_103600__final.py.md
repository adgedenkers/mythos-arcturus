# eval/results/person_deep_dive/20260305_103600/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 86

---

### Purpose
The `final.py` file in the `eval/results/person_deep_dive` directory implements the `PersonDeepDiveSkill` class, which is responsible for aggregating detailed information about a person by executing multiple sub-skills and combining their results into a comprehensive profile.

### Architecture
The file contains a single class `PersonDeepDiveSkill` that inherits from `SkillBase`. It includes three methods: `execute`, `_run_skill`, and `_build_profile`. The `execute` method is the primary entry point that orchestrates the execution of sub-skills and builds the final profile. The `_run_skill` method dynamically imports and runs sub-skills based on the provided module and class names. The `_build_profile` method constructs a summary profile based on the results from the sub-skills.

### Patterns
- **Factory Pattern**: The `_run_skill` method dynamically creates instances of sub-skills based on the provided module and class names.
- **Composite Pattern**: The `execute` method aggregates results from multiple sub-skills into a composite response.

### Dependencies
- **Imports**: `logging`, `importlib`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Database**: References `engine` and `sub` tables in PostgreSQL.

### Interfaces
- **Public Methods**: `execute` is the primary method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**: `_run_skill` and `_build_profile` are helper methods used internally by `execute`.

### Database
- **Tables**: `engine` and `sub` in PostgreSQL are referenced, though specific operations are not detailed in the provided code.

### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

### Key Logic
- **Sub-Skill Execution**: The `execute` method iterates over predefined sub-skills, dynamically imports and runs each sub-skill using `_run_skill`, and aggregates the results.
- **Profile Construction**: The `_build_profile` method constructs a summary profile by extracting relevant summaries from the results of sub-skills.
- **Error Handling**: Robust error handling is implemented to log errors and return appropriate responses in case of failures.

### Integration Points
- **Sub-Skills**: The `PersonDeepDiveSkill` integrates with multiple sub-skills (`PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, `SearchVoiceMemoSkill`) by dynamically importing and executing them.
- **SkillBase**: Inherits from `SkillBase`, indicating it integrates with the broader skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle input and output, indicating integration with the request-response mechanism of the Mythos system.

### Detailed Breakdown

#### Class: `PersonDeepDiveSkill`
- **Attributes**:
  - `name`: The name of the skill, set to `'person_deep_dive'`.
  - `triggers`: A list of trigger phrases that can activate this skill.
  - `SUB_SKILLS`: A dictionary mapping sub-skill keys to tuples containing the module name and class name of the sub-skill.

- **Methods**:
  - `execute`: The main method that orchestrates the execution of sub-skills and builds the final profile.
  - `_run_skill`: Dynamically imports and runs a sub-skill based on the provided module and class names.
  - `_build_profile`: Constructs a summary profile based on the results from the sub-skills.

#### Top-Level Functions
- **execute**: Not used directly in the class but could be a standalone function for executing the skill.
- **_run_skill**: Not used directly in the class but could be a standalone function for running a sub-skill.
- **_build_profile**: Not used directly in the class but could be a standalone function for building a profile.

### Summary
The `final.py` file implements the `PersonDeepDiveSkill` class, which dynamically executes multiple sub-skills to gather detailed information about a person and constructs a comprehensive profile. It integrates with the broader Mythos skill framework and handles errors gracefully, providing a robust mechanism for deep dives into person-related data.
