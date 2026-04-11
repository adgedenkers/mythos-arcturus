# eval/challenges/daily_briefing/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 31

---

### File: `eval/challenges/daily_briefing/build_plan.json`

#### Purpose
This JSON file serves as a build plan and blueprint for constructing the `DailyBriefingSkill` class, which is a composite skill designed to provide a daily briefing by chaining together multiple sub-skills related to spiral time, calendar, routines, and upcoming bills.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the skill being built.
- **version**: Version of the plan.
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the type of skill (composite).
- **model_hint**: Specifies the AI model to use.
- **context**: Contains system context and scaffold details.
- **build_plan**: A step-by-step guide to building the skill.
- **test_cases**: Test cases to validate the skill.

#### Patterns
- **Composite Pattern**: The `DailyBriefingSkill` is a composite skill that aggregates multiple sub-skills.
- **Factory Pattern**: The `importlib` module is used to dynamically import and instantiate sub-skills.

#### Dependencies
- **Imports**: The `build_plan` specifies the use of `logging`, `importlib`, and `engine.base`.
- **Sub-Skills**: The `SUB_SKILLS` dictionary maps sub-skills to their respective modules and classes.

#### Interfaces
- **SkillBase Class**: The `DailyBriefingSkill` class inherits from `SkillBase` and implements methods like `execute`, `_run_skill`, and `_build_briefing`.
- **SkillResponse**: The skill returns responses using the `SkillResponse` class.

#### Database
- **No Database Access**: The plan explicitly states that no database access is required (`no_database` pattern).

#### Configuration
- **Environment Variables**: No specific environment variables are mentioned.
- **Configuration Files**: No configuration files are mentioned.

#### Key Logic
- **_run_skill**: Dynamically imports and runs sub-skills using `importlib`.
- **_build_briefing**: Aggregates the summaries from sub-skills into a single briefing string.
- **execute**: Orchestrates the execution of sub-skills and builds the final briefing.

#### Integration Points
- **Sub-Skills Integration**: The `DailyBriefingSkill` integrates with sub-skills (`spiral_time`, `calendar`, `routines`, `bills`) by dynamically importing and running them.
- **SkillBase Integration**: Inherits from `SkillBase` and uses its methods and attributes.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton, including necessary imports and class definition with attributes and placeholder methods.
2. **Pass 2**: Implement `_run_skill` to dynamically import and run sub-skills, handling exceptions and returning appropriate responses.
3. **Pass 3**: Implement `_build_briefing` to aggregate summaries from sub-skills into a single briefing string.
4. **Pass 4**: Implement `execute` to orchestrate the execution of sub-skills, collect results, and build the final briefing.
5. **Pass 5**: Review the implementation to ensure no database imports, correct use of `importlib`, and production readiness.

### Test Cases
- **Test Case 1**: Message "good morning iris" should return a summary containing "Routine".
- **Test Case 2**: Message "daily briefing" should return a valid response.
- **Test Case 3**: Message "whats today look like" should return a valid response.

This JSON file provides a comprehensive guide for building and testing the `DailyBriefingSkill`, ensuring it integrates multiple sub-skills to provide a cohesive daily briefing.
