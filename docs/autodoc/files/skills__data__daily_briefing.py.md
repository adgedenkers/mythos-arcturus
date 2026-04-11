# skills/data/daily_briefing.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 71

---

### File: skills/data/daily_briefing.py

#### Purpose
This file defines the `DailyBriefingSkill` class, which is responsible for generating a daily briefing by aggregating data from multiple sub-skills such as spiral time, calendar, routines, and bills. It integrates these sub-skills to provide a comprehensive overview for the user.

#### Architecture
- **Class**: `DailyBriefingSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main entry point for the skill, which orchestrates the execution of sub-skills and builds the final briefing.
  - `_run_skill`: A helper method to dynamically load and execute sub-skills.
  - `_build_briefing`: Constructs the final briefing string from the results of the sub-skills.
- **Data Flow**: The `execute` method calls `_run_skill` for each sub-skill, collects their results, and then passes these results to `_build_briefing` to generate the final briefing.

#### Patterns
- **Factory Pattern**: The `_run_skill` method dynamically loads and instantiates sub-skills based on their module path and class name.
- **Composite Pattern**: The `DailyBriefingSkill` class acts as a composite that aggregates the results of multiple sub-skills to form a complete briefing.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors.
  - `importlib`: For dynamic module loading.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_run_skill`: Asynchronous method that takes a module path, class name, and `SkillRequest`, and returns a `SkillResponse`.
  - `_build_briefing`: Synchronous method that takes a dictionary of results and returns a string.

#### Database
- **PostgreSQL Table**: `engine` - This table is referenced for the `SkillBase` class, which `DailyBriefingSkill` inherits from.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **Aggregation of Sub-Skills**: The `execute` method iterates over the `SUB_SKILLS` dictionary, dynamically loading and executing each sub-skill using `_run_skill`.
- **Result Compilation**: The `_build_briefing` method compiles the results from the sub-skills into a single, coherent briefing string.

#### Integration Points
- **Sub-Skills Integration**: The `DailyBriefingSkill` integrates with other skills (`SpiralTimeSkill`, `QueryCalendarSkill`, `QueryRoutinesSkill`, `QueryBillsDueSkill`) by dynamically loading and executing them.
- **Request/Response Handling**: The skill uses `SkillRequest` and `SkillResponse` objects to communicate with the broader system, ensuring consistency in how requests are processed and responses are returned.

### Summary
The `DailyBriefingSkill` class in `daily_briefing.py` serves as a composite skill that aggregates data from multiple sub-skills to provide a comprehensive daily briefing. It leverages dynamic module loading and error handling to ensure robust operation, and it integrates seamlessly with the Mythos system through standardized request and response handling.
