# eval/challenges/spending_analysis/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 36

---

### Documentation for `eval/challenges/spending_analysis/build_plan.json`

#### Purpose
This JSON file serves as a build plan for the `SpendingAnalysisSkill` class, detailing the step-by-step implementation process, including the required methods, database queries, and integration with the Mythos system.

#### Architecture
The JSON file is structured into several key sections:
- **plan_id**: Identifies the specific plan.
- **version**: Version of the plan.
- **description**: Brief description of the plan's purpose.
- **pattern**: Indicates the skill pattern (`data_query_skill`).
- **model_hint**: Specifies the model hint (`qwen3-coder:30b`).
- **context**: Contains system context, table schema, and mandatory patterns.
- **build_plan**: Step-by-step instructions for building the skill.
- **test_cases**: Example test cases to validate the skill's functionality.

#### Patterns
- **Factory Pattern**: The plan implicitly uses a factory pattern to create the `SpendingAnalysisSkill` class.
- **Singleton Pattern**: The `_get_conn` function is designed to be a singleton, ensuring a single database connection instance.

#### Dependencies
- **Imports**: The file requires imports from `os`, `logging`, `datetime`, `psycopg2`, `RealDictCursor`, `dotenv`, and `engine.base`.
- **Environment Variables**: The plan relies on environment variables for database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Interfaces
- **Class**: `SpendingAnalysisSkill` with methods `execute`, `_get_category_totals`, `_get_monthly_comparison`, and `_build_summary`.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object.

#### Database
- **Tables**: `transactions` and `accounts`.
- **Queries**: 
  - `_get_category_totals`: Queries `transactions` for category totals.
  - `_get_monthly_comparison`: Queries `transactions` for monthly spending comparisons.

#### Configuration
- **Environment Variables**: Used for database connection details.
- **ASCII Only**: Ensures all text is in ASCII format.

#### Key Logic
- **_get_category_totals**: Retrieves spending totals by category over a specified period.
- **_get_monthly_comparison**: Compares spending totals between the current and previous months.
- **_build_summary**: Constructs a summary string based on the retrieved data.
- **execute**: Orchestrates the execution of the above methods and returns the final response.

#### Integration Points
- **engine.base**: Imports `SkillBase`, `SkillRequest`, and `SkillResponse` for skill execution.
- **Mythos System**: The skill integrates with the Mythos system through the `SkillResponse` object and triggers defined in the class.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton, including imports, `_get_conn` function, and class definition with placeholder methods.
2. **Pass 2**: Implement `_get_category_totals` to query category spending totals.
3. **Pass 3**: Implement `_get_monthly_comparison` to compare spending between months.
4. **Pass 4**: Implement `_build_summary` to construct a summary string.
5. **Pass 5**: Implement `execute` to orchestrate the skill execution and return the final response.
6. **Pass 6**: Final review and production readiness checks.

### Test Cases
- **Test Case 1**: Validates the skill with the message "show me spending analysis".
- **Test Case 2**: Validates the skill with the message "where is my money going".
- **Test Case 3**: Validates the skill with the message "monthly spending breakdown".

This JSON file provides a comprehensive guide for implementing the `SpendingAnalysisSkill` class, ensuring it integrates seamlessly with the Mythos system and meets the specified requirements.
