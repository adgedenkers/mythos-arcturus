# skills/data/daily_task_planner.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 91

---

### File: skills/data/daily_task_planner.py

#### Purpose
This file contains the `DailyTaskPlannerSkill` class, which is responsible for generating a prioritized daily task list by combining data from the calendar, routines, and bills. It integrates with other subsystems to fetch relevant data and constructs a plan based on the retrieved information.

#### Architecture
- **Class**: `DailyTaskPlannerSkill` extends `SkillBase`.
- **Methods**:
  - `execute`: The main entry point for the skill, which orchestrates the execution of sub-skills and builds the final plan.
  - `_run_skill`: Dynamically imports and runs a specified sub-skill.
  - `_build_plan`: Constructs the daily task plan from the results of the sub-skills.
- **Data Flow**:
  - The `execute` method fetches data from sub-skills (`calendar`, `routines`, `bills`).
  - The `_build_plan` method processes this data to create a prioritized task list.
  - The final plan is returned as a `SkillResponse` object.

#### Patterns
- **Factory Method**: The `_run_skill` method dynamically imports and instantiates sub-skills based on the provided module path and class name.
- **Composite Pattern**: The `DailyTaskPlannerSkill` composes the results from multiple sub-skills to form a comprehensive daily task plan.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors and information.
  - `importlib`: For dynamic module importing.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects for the skill.

#### Interfaces
- **Public Methods**:
  - `execute`: Exposed to other parts of the system for initiating the task planning process.
- **Private Methods**:
  - `_run_skill`: Used internally to run sub-skills.
  - `_build_plan`: Used internally to construct the plan from sub-skill results.

#### Database
- **PostgreSQL Tables**:
  - `one`: Likely used for some internal state or configuration.
  - `engine`: Possibly used for skill execution metadata.
  - `calendar`: Used to fetch calendar events.

#### Configuration
- **Environment Variables**: None explicitly used in this file.
- **Config Files**: None explicitly used in this file.

#### Key Logic
- **Sub-Skill Execution**: The `execute` method dynamically runs sub-skills (`calendar`, `routines`, `bills`) and collects their results.
- **Plan Construction**: The `_build_plan` method processes the results from sub-skills to create a prioritized task list, categorizing tasks by priority and including details from calendar events, routines, and bills.

#### Integration Points
- **Sub-Skills Integration**: The `DailyTaskPlannerSkill` integrates with sub-skills (`calendar`, `routines`, `bills`) by dynamically importing and running them.
- **SkillBase Integration**: Inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` for communication.
- **Logging Integration**: Uses the `logging` module to log errors and information.

### Summary
The `DailyTaskPlannerSkill` class in `daily_task_planner.py` is designed to generate a prioritized daily task list by integrating data from calendar events, routines, and bills. It dynamically runs sub-skills, processes their results, and constructs a comprehensive plan. The class leverages dynamic module importing and composite design patterns to achieve this functionality.
