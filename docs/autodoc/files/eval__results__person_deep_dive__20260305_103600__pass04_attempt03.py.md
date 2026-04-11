# eval/results/person_deep_dive/20260305_103600/pass04_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 108

---

### Purpose
The `pass04_attempt03.py` file defines the `PersonDeepDiveSkill` class, which is responsible for performing a deep dive into a person's profile by aggregating data from multiple sub-skills. It integrates with various subsystems to gather detailed information and constructs a comprehensive profile summary.

### Architecture
The file contains a single class `PersonDeepDiveSkill` that inherits from `SkillBase`. This class has three primary methods:
- `execute`: Orchestrates the execution of sub-skills and builds the final profile.
- `_run_skill`: Dynamically imports and runs a specified sub-skill.
- `_build_profile`: Constructs a textual summary of the aggregated data.

### Patterns
- **Factory Method**: The `_run_skill` method dynamically instantiates and runs sub-skills based on their module and class names.
- **Composite**: The `execute` method aggregates results from multiple sub-skills into a single response.

### Dependencies
- **Imports**: 
  - `logging`: For logging errors and information.
  - `importlib`: For dynamically importing sub-skills.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects for skills.

### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Entry point for the skill, takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_run_skill(module_name: str, class_name: str, request: SkillRequest) -> SkillResponse`: Runs a specific sub-skill.
  - `_build_profile(request: SkillRequest, results: dict) -> str`: Builds a textual profile summary from the results of sub-skills.

### Database
- **PostgreSQL Tables**:
  - `engine`: Likely used for storing skill-related metadata.
  - `sub`: Likely used for storing sub-skill metadata or results.

### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

### Key Logic
- **Sub-Skill Execution**: The `execute` method iterates over predefined sub-skills, dynamically imports and runs each one, and aggregates their results.
- **Profile Construction**: The `_build_profile` method constructs a textual summary by extracting relevant data from the results of sub-skills and ensuring the summary is ASCII-only.
- **Error Handling**: Robust error handling is implemented to ensure the skill returns a meaningful response even if individual sub-skills fail.

### Integration Points
- **Sub-Skills**: The skill integrates with multiple sub-skills defined in `SUB_SKILLS`, such as `PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, and `SearchVoiceMemoSkill`.
- **SkillBase**: Inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` for request and response handling.
- **Logging**: Uses `logging` to record errors and informational messages.
- **Dynamic Import**: Uses `importlib` to dynamically import and run sub-skills based on their module and class names.

### Detailed Breakdown

#### `PersonDeepDiveSkill` Class
- **Attributes**:
  - `name`: Name of the skill (`'person_deep_dive'`).
  - `triggers`: List of phrases that trigger this skill.
  - `SUB_SKILLS`: Dictionary mapping sub-skill names to their module and class names.

- **Methods**:
  - `execute`: 
    - Iterates over `SUB_SKILLS` and runs each sub-skill using `_run_skill`.
    - Aggregates results and builds a profile summary using `_build_profile`.
    - Constructs and returns a `SkillResponse` object with the aggregated data and summary.
  - `_run_skill`: 
    - Dynamically imports a module and class using `importlib`.
    - Instantiates the class and runs it with the provided `request`.
    - Ensures the response has a proper status.
  - `_build_profile`: 
    - Constructs a textual summary by extracting relevant data from the results of sub-skills.
    - Ensures the summary is ASCII-only and handles cases where no data is available.

### Conclusion
This file is a critical component of the Mythos system, responsible for orchestrating a deep dive into a person's profile by leveraging multiple sub-skills. It demonstrates robust error handling and dynamic sub-skill execution, ensuring comprehensive and reliable profile construction.
