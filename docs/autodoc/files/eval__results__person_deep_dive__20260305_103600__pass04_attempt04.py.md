# eval/results/person_deep_dive/20260305_103600/pass04_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 108

---

### Purpose
The `pass04_attempt04.py` file implements the `PersonDeepDiveSkill` class, which is responsible for aggregating detailed information about a person from multiple sub-skills. It integrates various data sources to build a comprehensive profile and returns the aggregated data and summary.

### Architecture
The file contains a single class `PersonDeepDiveSkill` that inherits from `SkillBase`. This class has three methods:
- `execute`: The main method that orchestrates the execution of sub-skills and builds the final profile.
- `_run_skill`: A helper method to dynamically import and execute sub-skills.
- `_build_profile`: A helper method to construct the final profile summary from the results of sub-skills.

### Patterns
- **Factory Method**: The `_run_skill` method dynamically imports and instantiates sub-skills based on the provided module and class names.
- **Composite**: The `execute` method aggregates results from multiple sub-skills into a single response.

### Dependencies
- **Imports**: `logging`, `importlib`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Sub-skills**: `PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, `SearchVoiceMemoSkill` from their respective modules.

### Interfaces
- **Public Methods**:
  - `execute`: Exposed to the system to execute the skill and return a `SkillResponse`.
- **Internal Methods**:
  - `_run_skill`: Used internally to run sub-skills.
  - `_build_profile`: Used internally to build the final profile summary.

### Database
- **Tables**: The file references `engine` and `sub` tables in PostgreSQL, though the exact usage within the file is not explicitly shown in the provided code snippet.

### Configuration
- **Environment Variables**: No explicit configuration or environment variables are used in the provided code snippet.
- **Constants**: The `SUB_SKILLS` dictionary defines the sub-skills and their respective modules and classes.

### Key Logic
- **Sub-skill Execution**: The `execute` method iterates over the `SUB_SKILLS` dictionary, dynamically imports and runs each sub-skill using `_run_skill`.
- **Profile Construction**: The `_build_profile` method constructs a summary by extracting and formatting summaries from the results of sub-skills.
- **Error Handling**: The methods log errors and handle exceptions gracefully, ensuring that the summary is never empty.

### Integration Points
- **SkillBase**: The class inherits from `SkillBase` and integrates with the broader Mythos system through the `execute` method.
- **Sub-skills**: The class integrates with sub-skills by dynamically importing and executing them based on the `SUB_SKILLS` dictionary.
- **Data Aggregation**: The class aggregates data from sub-skills and returns a comprehensive response, integrating with the Mythos system's data flow.

### Summary
The `PersonDeepDiveSkill` class in `pass04_attempt04.py` is designed to aggregate detailed information about a person from multiple sub-skills, dynamically executing them and building a comprehensive profile summary. It integrates with the broader Mythos system through the `SkillBase` interface and handles errors gracefully to ensure robust operation.
