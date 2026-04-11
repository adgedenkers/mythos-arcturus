# eval/challenges/person_deep_dive/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 29

---

### File: eval/challenges/person_deep_dive/build_plan.json

#### Purpose
This JSON file serves as a blueprint for constructing the `PersonDeepDiveSkill` class, detailing the step-by-step process of its development, including the required imports, class structure, methods, and integration tests.

#### Architecture
The file is structured into several sections:
- **plan_id**: Identifies the skill being developed.
- **version**: Specifies the version of the plan.
- **description**: Provides a brief description of the skill.
- **pattern**: Indicates the type of skill (composite).
- **model_hint**: Suggests the AI model to be used.
- **context**: Contains system context and mandatory patterns.
- **build_plan**: A sequence of steps to develop the skill.
- **test_cases**: Example test cases to validate the skill.

#### Patterns
- **Composite Pattern**: The skill is composed of multiple sub-skills.
- **Factory Pattern**: Sub-skills are dynamically loaded using `importlib.import_module`.

#### Dependencies
- **Imports**: `logging`, `importlib`, `engine.base` (for `SkillBase`, `SkillRequest`, `SkillResponse`).
- **Sub-skills**: `PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, `SearchVoiceMemoSkill`.

#### Interfaces
- **Class**: `PersonDeepDiveSkill` with methods `execute`, `_run_skill`, `_build_profile`.
- **SkillResponse**: Used to return the final response with attributes `skill_name`, `data`, `summary`, `confidence`, `sources`, `error`.

#### Database
- **No direct database access**: The skill does not directly interact with the database. Sub-skills may interact with the database.

#### Configuration
- **Environment Variables**: Not explicitly mentioned in the JSON.
- **Config Files**: Not explicitly mentioned in the JSON.

#### Key Logic
- **_run_skill**: Dynamically imports and runs sub-skills using `importlib.import_module` and `getattr`.
- **_build_profile**: Collects summaries from sub-skills and constructs a profile string.
- **execute**: Runs all sub-skills, builds the profile, and returns a `SkillResponse` object.

#### Integration Points
- **Sub-skills**: The skill integrates with other sub-skills (`PeopleLookupSkill`, `QueryNatalChartSkill`, `SearchLifeEventsSkill`, `SearchVoiceMemoSkill`) to gather data.
- **SkillBase**: Inherits from `SkillBase` to utilize its methods and structure.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for input and output.

### Detailed Breakdown of `build_plan` Steps

1. **Pass 1**: Write the file skeleton, including necessary imports and class structure. Define `SUB_SKILLS` and placeholder methods.
2. **Pass 2**: Implement the `_run_skill` method to dynamically load and run sub-skills. Implement `_build_profile` to collect and format summaries from sub-skills.
3. **Pass 3**: Implement the `execute` method to run all sub-skills, build the profile, and return a `SkillResponse` object.
4. **Pass 4**: Review the implementation to ensure no database imports, all sub-skills are referenced, summaries are never empty, and the code is ASCII-only and production-ready.

### Test Cases
- **"tell me everything about adge"**: Expected to succeed.
- **"deep dive on seraphe"**: Expected to succeed.
- **"who is fitz"**: Expected to succeed.

This JSON file provides a comprehensive guide for developing the `PersonDeepDiveSkill`, ensuring that all necessary components and logic are correctly implemented and tested.
