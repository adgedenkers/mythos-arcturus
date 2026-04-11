# eval/challenges/daily_task_planner/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 31

---

### File: `eval/challenges/daily_task_planner/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for constructing the `DailyTaskPlannerSkill` class, which is responsible for generating a prioritized daily task list by combining calendar events, routines, and upcoming bills.

#### Architecture
The file is structured into several key sections:
- **Metadata**: Contains basic information about the plan, such as `plan_id`, `version`, and `description`.
- **Context**: Provides system context and mandatory patterns for the skill implementation.
- **Build Plan**: A step-by-step guide for implementing the `DailyTaskPlannerSkill` class, including instructions for each method and the overall structure.
- **Test Cases**: Example test cases to validate the functionality of the skill.

#### Patterns
- **Composite Pattern**: The skill is a composite skill, combining multiple sub-skills to generate a final output.
- **Factory Pattern**: Uses `importlib` to dynamically import and instantiate sub-skills.

#### Dependencies
- **Imports**: The skill imports `logging`, `importlib`, and `engine.base` for `SkillBase`, `SkillRequest`, and `SkillResponse`.
- **Sub-Skills**: The skill depends on three sub-skills: `QueryCalendarSkill`, `QueryRoutinesSkill`, and `QueryBillsDueSkill`.

#### Interfaces
- **SkillBase Class**: The `DailyTaskPlannerSkill` class inherits from `SkillBase` and implements `execute` and `_run_skill` methods.
- **SkillRequest and SkillResponse**: The skill uses `SkillRequest` for input and `SkillResponse` for output.

#### Database
- **No Database Access**: The skill does not directly access any database. It relies on sub-skills to fetch data.

#### Configuration
- **Environment Variables**: No specific environment variables are mentioned.
- **Configuration Files**: No specific configuration files are mentioned.

#### Key Logic
- **_run_skill Method**: Dynamically imports and runs sub-skills using `importlib`.
- **_build_plan Method**: Combines results from sub-skills to build a prioritized task list.
- **execute Method**: Orchestrates the execution of sub-skills and builds the final task list.

#### Integration Points
- **Sub-Skills**: The skill integrates with `QueryCalendarSkill`, `QueryRoutinesSkill`, and `QueryBillsDueSkill` to fetch data.
- **SkillBase**: The skill integrates with the `SkillBase` class to follow the skill execution pattern.

### Detailed Breakdown of Key Sections

#### Metadata
- **plan_id**: `daily_task_planner`
- **version**: `1.0`
- **description**: Combines calendar events, routines, and upcoming bills into one prioritized daily task list.
- **pattern**: `composite_skill`
- **model_hint**: `qwen3-coder:30b`

#### Context
- **system_context**: 
  - `engine_import`: `from engine.base import SkillBase, SkillRequest, SkillResponse`
- **mandatory_patterns**:
  - `no_database`: Composite skill, no database connection.
  - `import_pattern`: Uses `importlib` to dynamically import and run sub-skills.
  - `no_unicode`: ASCII only.
  - `skillresponse_signature`: `SkillResponse` accepts specific fields.
  - `async_required`: All methods that use `await` must be `async def`.

#### Build Plan
- **Pass 1**: Write file skeleton, define `DailyTaskPlannerSkill` class, and `SUB_SKILLS` dictionary.
- **Pass 2**: Implement `_run_skill` method to dynamically import and run sub-skills.
- **Pass 3**: Implement `_build_plan` method to build a prioritized task list.
- **Pass 4**: Implement `execute` method to orchestrate the execution of sub-skills and build the final task list.
- **Pass 5**: Review and ensure all methods are `async def`, no database imports, and ASCII only.

#### Test Cases
- **Test Case 1**: Message: `plan my day`, Expect: `true`, Expect Summary Contains: `Routine`.
- **Test Case 2**: Message: `what should i do today`, Expect: `true`.
- **Test Case 3**: Message: `to do list`, Expect: `true`.

This JSON file provides a comprehensive guide for implementing the `DailyTaskPlannerSkill` class, ensuring it integrates with other components of the Mythos system and follows the specified design patterns and requirements.
