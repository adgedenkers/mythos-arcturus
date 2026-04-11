# eval/results/person_deep_dive/20260305_103600/pass03_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 86

---

### File: `eval/results/person_deep_dive/20260305_103600/pass03_attempt02.py`

#### Purpose
This file defines a class `PersonDeepDiveSkill` that extends `SkillBase` and is responsible for executing a deep dive into a person's profile by aggregating data from multiple sub-skills. It handles the orchestration of these sub-skills and builds a comprehensive profile summary.

#### Architecture
The file contains a single class `PersonDeepDiveSkill` which inherits from `SkillBase`. The class has three methods:
- `execute`: The main entry point that orchestrates the execution of sub-skills and builds the final profile.
- `_run_skill`: A helper method to dynamically import and execute a sub-skill.
- `_build_profile`: Constructs a summary profile based on the results from the sub-skills.

#### Patterns
- **Factory Pattern**: The `_run_skill` method dynamically imports and instantiates sub-skills.
- **Composite Pattern**: The `execute` method aggregates results from multiple sub-skills into a composite response.

#### Dependencies
- `logging`: For logging errors and information.
- `importlib`: For dynamically importing modules.
- `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response models.

#### Interfaces
- `execute`: Exposes the main execution method that takes a `SkillRequest` and returns a `SkillResponse`.
- `_run_skill`: A helper method that takes a module name, class name, and request, and returns a `SkillResponse`.
- `_build_profile`: Constructs a profile summary based on the results from sub-skills.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Likely used for storing engine-related configurations or metadata.
  - `sub`: Possibly used for storing sub-skill configurations or metadata.

#### Configuration
- No explicit configuration files or environment variables are used in this file. However, the sub-skills and their configurations are likely defined elsewhere in the system.

#### Key Logic
- **Orchestration of Sub-Skills**: The `execute` method iterates over a dictionary of sub-skills, dynamically imports and runs each one, and aggregates their results.
- **Error Handling**: The methods handle exceptions and log errors, returning appropriate `SkillResponse` objects.
- **Profile Construction**: The `_build_profile` method constructs a summary profile by combining data from various sub-skills.

#### Integration Points
- **Sub-Skills**: The `PersonDeepDiveSkill` integrates with multiple sub-skills (`PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, `SearchVoiceMemoSkill`) to gather comprehensive data.
- **SkillBase**: Inherits from `SkillBase` to leverage common skill execution patterns and structures.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to standardize the input and output formats.

### Summary
This file implements a comprehensive deep dive skill for profiling individuals by orchestrating multiple sub-skills. It dynamically imports and executes these sub-skills, aggregates their results, and constructs a detailed profile summary. The file is designed to be robust with error handling and logging, and it integrates seamlessly with the broader Mythos system through standardized request and response models.
