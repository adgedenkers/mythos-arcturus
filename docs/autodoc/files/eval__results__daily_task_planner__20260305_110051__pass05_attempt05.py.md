# eval/results/daily_task_planner/20260305_110051/pass05_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 109

---

### File: eval/results/daily_task_planner/20260305_110051/pass05_attempt05.py

#### Purpose
This file contains the `DailyTaskPlannerSkill` class, which is responsible for planning daily tasks by integrating data from multiple sub-skills (calendar, routines, bills) and generating a comprehensive task plan.

#### Architecture
- **Classes**: 
  - `DailyTaskPlannerSkill` inherits from `SkillBase` and contains methods `execute`, `_run_skill`, and `_build_plan`.
- **Methods**:
  - `execute`: The main method that orchestrates the execution of sub-skills and builds the final plan.
  - `_run_skill`: Executes a sub-skill by dynamically importing and running the specified class.
  - `_build_plan`: Constructs the task plan based on the results from sub-skills.
- **Data Flow**:
  - The `execute` method calls `_run_skill` for each sub-skill, collects their results, and then calls `_build_plan` to generate the final plan.
  - The results from sub-skills are merged and formatted into a `SkillResponse` object.

#### Patterns
- **Factory Pattern**: The `_run_skill` method dynamically imports and instantiates sub-skills based on the provided module path and class name.
- **Composite Pattern**: The `execute` method integrates results from multiple sub-skills to form a composite plan.

#### Dependencies
- **Imports**: 
  - `logging`: For logging errors.
  - `importlib`: For dynamic module importing.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Exposed to the system for executing the daily task planning.
  - `_run_skill`: Internal method for running sub-skills.
  - `_build_plan`: Internal method for building the task plan.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Likely used for storing engine-related configurations or states.
  - `successful`: Likely used for tracking successful executions or storing results.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Sub-Skill Execution**: The `execute` method iterates over predefined sub-skills, dynamically imports and runs each one, and collects their results.
- **Plan Construction**: The `_build_plan` method processes the results from sub-skills (calendar, routines, bills) and constructs a detailed task plan with a summary.
- **Error Handling**: Errors are logged and handled gracefully, ensuring the system returns a meaningful response even in failure scenarios.

#### Integration Points
- **Sub-Skills Integration**: The `DailyTaskPlannerSkill` integrates with multiple sub-skills (`QueryCalendarSkill`, `QueryRoutinesSkill`, `QueryBillsDueSkill`) to gather data.
- **SkillBase Integration**: Inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` for request handling and response formatting.
- **Database Integration**: Likely interacts with PostgreSQL tables for storing and retrieving execution states or results.

### Detailed Breakdown

#### `DailyTaskPlannerSkill` Class
- **Attributes**:
  - `name`: Identifier for the skill.
  - `triggers`: List of phrases that trigger the skill.
  - `SUB_SKILLS`: Dictionary mapping sub-skill names to their module paths and class names.
- **Methods**:
  - `execute`: Orchestrates the execution of sub-skills and builds the final plan.
  - `_run_skill`: Dynamically imports and runs a sub-skill.
  - `_build_plan`: Constructs the task plan based on sub-skill results.

#### `execute` Method
- **Parameters**: `request` (SkillRequest object).
- **Logic**:
  - Iterates over `SUB_SKILLS`, dynamically runs each sub-skill, and collects results.
  - Merges results from sub-skills into a comprehensive plan.
  - Constructs and returns a `SkillResponse` object with the plan and summary.

#### `_run_skill` Method
- **Parameters**: `module_path`, `class_name`, `request`.
- **Logic**:
  - Dynamically imports the specified module and class.
  - Instantiates and runs the sub-skill, returning its response.

#### `_build_plan` Method
- **Parameters**: `results` (dictionary of sub-skill results).
- **Logic**:
  - Processes results from calendar, routines, and bills sub-skills.
  - Constructs a detailed task plan with a summary of tasks, routines, and bills.
  - Returns the constructed plan as a string.

### Example Use Case
The `DailyTaskPlannerSkill` is triggered when a user inputs a phrase like "plan my day". It dynamically runs sub-skills to gather calendar events, daily routines, and bills due, and constructs a comprehensive daily task plan. The plan is then returned to the user in a structured format, providing a clear overview of their day's tasks.
