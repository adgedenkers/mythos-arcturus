# eval/results/daily_task_planner/20260305_110744/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 21

---

### File: `eval/results/daily_task_planner/20260305_110744/pass01_attempt01.py`

#### Purpose
This file defines the `DailyTaskPlannerSkill` class, which is responsible for planning daily tasks based on user input. It integrates with various sub-skills to gather information and build a comprehensive daily plan.

#### Architecture
- **Class**: `DailyTaskPlannerSkill` extends `SkillBase`.
- **Methods**:
  - `execute`: The main entry point for the skill, which is asynchronous.
  - `_run_skill`: An asynchronous method that runs the skill logic.
  - `_build_plan`: A synchronous method that constructs the daily plan.
- **Attributes**:
  - `name`: The name of the skill.
  - `triggers`: A list of phrases that trigger this skill.
  - `SUB_SKILLS`: A dictionary mapping sub-skills to their respective modules and classes.

#### Patterns
- **Factory**: The `SUB_SKILLS` dictionary acts as a factory for sub-skills, allowing dynamic instantiation based on the skill name.
- **Singleton**: The `DailyTaskPlannerSkill` class itself can be considered a singleton if it is instantiated once and reused throughout the application.

#### Dependencies
- **Imports**:
  - `logging`: For logging purposes.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response models.

#### Interfaces
- **Public Methods**:
  - `execute`: Exposed to other parts of the system for initiating the skill.
  - `_run_skill`: Internal method used by `execute` to run the skill logic.
  - `_build_plan`: Internal method used to construct the daily plan.

#### Database
- **PostgreSQL**:
  - **Table**: `engine`
  - **Usage**: Likely used to store or retrieve data related to the skill execution, such as user preferences or historical task plans.

#### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Config Files**: None explicitly mentioned.

#### Key Logic
- **Skill Execution**:
  - The `execute` method is the entry point for the skill execution.
  - `_run_skill` handles the asynchronous execution of the skill logic.
  - `_build_plan` constructs the daily plan based on the user request.
- **Sub-Skill Integration**:
  - The `SUB_SKILLS` dictionary is used to dynamically instantiate and use sub-skills like `QueryCalendarSkill`, `QueryRoutinesSkill`, and `QueryBillsDueSkill`.

#### Integration Points
- **Sub-Skills**:
  - The `DailyTaskPlannerSkill` integrates with sub-skills defined in `SUB_SKILLS` to gather necessary data for building the plan.
- **SkillBase**:
  - Inherits from `SkillBase`, which likely provides common functionality for all skills, such as logging and request handling.
- **SkillRequest and SkillResponse**:
  - Uses `SkillRequest` and `SkillResponse` to handle input and output data, ensuring consistency across different skills.

### Summary
The `DailyTaskPlannerSkill` class in this file is designed to plan daily tasks by integrating with various sub-skills. It uses a factory pattern to instantiate sub-skills and follows a singleton-like pattern for skill execution. The skill interacts with a PostgreSQL database and is part of a larger skill system, inheriting from `SkillBase` and using `SkillRequest` and `SkillResponse` for data handling.
