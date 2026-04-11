# eval/challenges/rank_by_recency/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 28

---

### File: eval/challenges/rank_by_recency/build_plan.json

#### Purpose
This JSON file serves as a structured plan for building a specific skill (`RankByRecencySkill`) within the Mythos system. It outlines the steps, instructions, and tests required to develop and validate the skill.

#### Architecture
The file is structured as a JSON object containing several key sections:
- `plan_id`: Identifies the plan.
- `version`: Specifies the version of the plan.
- `description`: Provides a brief description of the skill.
- `pattern`: Indicates the pattern or type of the skill.
- `model_hint`: Suggests a model to use for the skill.
- `context`: Contains context information including system context, scaffold (template for the skill class), and mandatory patterns.
- `build_plan`: Lists the steps and instructions for building the skill.
- `test_cases`: Specifies test cases to validate the skill.

#### Patterns
- **Template Method Pattern**: The scaffold section provides a template for the `RankByRecencySkill` class, which inherits from `SkillBase` and defines methods that need to be implemented.
- **Configuration Pattern**: The `context` and `build_plan` sections act as configuration settings for the skill development process.

#### Dependencies
- **Imports**: The skill imports `logging`, `datetime`, and `engine.base`.
- **External Libraries**: No external libraries are required, but the skill relies on the `datetime` module for date handling.

#### Interfaces
- **SkillBase Class**: The `RankByRecencySkill` class extends `SkillBase` and implements methods like `execute` and `_relative_time`.
- **SkillResponse**: The skill returns instances of `SkillResponse`.

#### Database
- **No Database Usage**: The skill does not interact with any database.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Configuration Files**: No configuration files are used.

#### Key Logic
- **_relative_time Method**: Converts an ISO date string to a relative time string (e.g., "X minutes ago").
- **execute Method**: Sorts a list of results by their `created_at` field in descending order, adds a `relative_time` field to each result, and returns a `SkillResponse` object.

#### Integration Points
- **Engine Module**: The skill integrates with the `engine.base` module, which provides the `SkillBase` class and `SkillResponse` class.
- **FastAPI**: The skill is expected to be part of a FastAPI application, where it will handle requests and return responses.

### Detailed Breakdown of `build_plan` Steps

1. **Pass 1**: Write the file skeleton with necessary imports and class structure.
   - **Imports**: `logging`, `datetime`, `engine.base`.
   - **Class Structure**: `RankByRecencySkill` with attributes and methods having `pass`.

2. **Pass 2**: Implement the `_relative_time` method.
   - **Logic**: Converts an ISO date string to a relative time string.
   - **Edge Cases**: Handles `None` input and parse errors gracefully.

3. **Pass 3**: Implement the `execute` method.
   - **Logic**: Sorts results by `created_at`, adds `relative_time` field, and returns `SkillResponse`.
   - **Edge Cases**: Handles missing `created_at` fields and empty results.

4. **Pass 4**: Review and finalize the skill.
   - **Validation**: Ensures no database imports, handles date parsing edge cases, and ensures ASCII-only output.

### Test Cases
- **Test Case 1**: Validates the skill's ability to rank results.
- **Test Case 2**: Validates the skill's response to a trigger phrase.

This JSON file provides a comprehensive plan for developing and testing the `RankByRecencySkill` within the Mythos system, ensuring it meets the specified requirements and integrates seamlessly with the existing infrastructure.
