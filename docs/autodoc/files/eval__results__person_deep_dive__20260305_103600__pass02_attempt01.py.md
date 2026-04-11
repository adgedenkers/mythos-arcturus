# eval/results/person_deep_dive/20260305_103600/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 61

---

### File: `eval/results/person_deep_dive/20260305_103600/pass02_attempt01.py`

#### Purpose
This file defines a class `PersonDeepDiveSkill` that extends `SkillBase` to perform a deep dive into a person's profile by aggregating data from multiple sub-skills. It also contains utility functions for executing and building the profile.

#### Architecture
- **Class**: `PersonDeepDiveSkill` extends `SkillBase` and includes methods for executing the skill, running sub-skills, and building the profile.
- **Methods**:
  - `execute`: Main method to orchestrate the execution of sub-skills and build the final profile.
  - `_run_skill`: Helper method to dynamically import and run a sub-skill.
  - `_build_profile`: Helper method to construct the profile based on the results from sub-skills.
- **Data Flow**: The `execute` method iterates over predefined sub-skills, runs each one using `_run_skill`, collects the results, and then builds the final profile using `_build_profile`.

#### Patterns
- **Factory Method**: The `_run_skill` method dynamically imports and instantiates sub-skills based on their module and class names.
- **Composite**: The `PersonDeepDiveSkill` class composes the results from multiple sub-skills to build a comprehensive profile.

#### Dependencies
- **Imports**: `logging`, `importlib`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **External Modules**: Dynamically imported based on the `SUB_SKILLS` dictionary.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Takes a `SkillRequest` and returns a `SkillResponse` containing the profile.
  - `_run_skill`: Takes `module_name`, `class_name`, and `request` and returns a `SkillResponse`.
  - `_build_profile`: Takes `request` and `results` and returns a string profile.

#### Database
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` and `SkillRequest`).

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Main Logic**: The `execute` method orchestrates the execution of sub-skills by dynamically importing and running them. It collects the results and builds a comprehensive profile.
- **Error Handling**: Uses `logging.error` to log errors when sub-skills fail.

#### Integration Points
- **Sub-Skills**: Integrates with multiple sub-skills defined in `SUB_SKILLS` dictionary, such as `PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, and `SearchVoiceMemoSkill`.
- **SkillBase**: Inherits from `SkillBase` which likely provides common functionality for skills, such as handling requests and responses.

### Detailed Documentation

#### Class: `PersonDeepDiveSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: The name of the skill (`'person_deep_dive'`).
  - `triggers`: List of phrases that can trigger this skill.
  - `SUB_SKILLS`: Dictionary mapping sub-skill keys to their module and class names.
- **Methods**:
  - `execute`: Main method to execute the skill. It iterates over `SUB_SKILLS`, runs each sub-skill using `_run_skill`, collects the results, and builds the final profile using `_build_profile`.
  - `_run_skill`: Dynamically imports and runs a sub-skill based on the provided `module_name` and `class_name`.
  - `_build_profile`: Constructs the final profile by aggregating summaries from the results of sub-skills.

#### Top-Level Functions
- **execute**: Not used in this file. Likely a placeholder or part of a larger framework.
- **_run_skill**: Not used in this file. Likely a placeholder or part of a larger framework.
- **_build_profile**: Not used in this file. Likely a placeholder or part of a larger framework.

#### Database References
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` and `SkillRequest`).

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Main Logic**: The `execute` method orchestrates the execution of sub-skills by dynamically importing and running them. It collects the results and builds a comprehensive profile.
- **Error Handling**: Uses `logging.error` to log errors when sub-skills fail.

#### Integration Points
- **Sub-Skills**: Integrates with multiple sub-skills defined in `SUB_SKILLS` dictionary, such as `PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, and `SearchVoiceMemoSkill`.
- **SkillBase**: Inherits from `SkillBase` which likely provides common functionality for skills, such as handling requests and responses.
