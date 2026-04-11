# eval/results/person_deep_dive/20260305_103600/pass04_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 108

---

### Purpose
The `pass04_attempt05.py` file contains the `PersonDeepDiveSkill` class, which is responsible for performing a deep dive into a person's profile by aggregating data from multiple sub-skills. It integrates with other subsystems to gather and summarize information about a person, including their natal chart, life events, and voice memos.

### Architecture
The file contains a single class `PersonDeepDiveSkill` that inherits from `SkillBase`. The class has three methods:
- `execute`: The main method that orchestrates the execution of sub-skills and builds the final profile.
- `_run_skill`: A helper method to dynamically import and run a sub-skill.
- `_build_profile`: A method to compile the results from sub-skills into a human-readable summary.

### Patterns
- **Factory Method**: The `_run_skill` method dynamically imports and instantiates sub-skills based on the provided module and class names.
- **Composite**: The `execute` method aggregates results from multiple sub-skills, treating each sub-skill as a component of the overall profile.

### Dependencies
- **Imports**: `logging`, `importlib`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Database**: References `engine` and `sub` tables in PostgreSQL.

### Interfaces
- **Public Methods**: `execute` is the primary interface method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Helper Methods**: `_run_skill` and `_build_profile` are private methods used internally by `execute`.

### Database
- **Tables**: The file references `engine` and `sub` tables in PostgreSQL, though specific queries or operations are not detailed in the provided code.

### Configuration
- **Environment Variables**: No explicit configuration or environment variables are used in the provided code.
- **Constants**: The `SUB_SKILLS` dictionary defines the sub-skills and their corresponding modules and classes.

### Key Logic
- **Sub-Skill Execution**: The `execute` method iterates over the `SUB_SKILLS` dictionary, dynamically importing and running each sub-skill to gather data.
- **Profile Compilation**: The `_build_profile` method compiles the results from sub-skills into a summary, ensuring ASCII-only characters and handling cases where data is not available.
- **Error Handling**: Robust error handling is implemented to log errors and return appropriate responses when sub-skills fail.

### Integration Points
- **Sub-Skills**: The `PersonDeepDiveSkill` integrates with multiple sub-skills (`PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, `SearchVoiceMemoSkill`) to gather comprehensive information about a person.
- **SkillBase**: Inherits from `SkillBase`, which likely provides common functionality for skills in the Mythos system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle input and output, indicating integration with the broader Mythos request-response framework.

### Summary
The `pass04_attempt05.py` file implements the `PersonDeepDiveSkill` class, which orchestrates the execution of multiple sub-skills to build a comprehensive profile of a person. It leverages dynamic module importing and robust error handling to ensure reliable operation, integrating seamlessly with the Mythos system's request-response architecture.
