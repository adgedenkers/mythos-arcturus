# eval/challenges/query_bills_due/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 34

---

### Documentation for `eval/challenges/query_bills_due/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for developing a skill that queries upcoming bills due in the next N days, including their payment status. It outlines the structure, logic, and steps required to implement the skill.

#### Architecture
The file is structured into several sections:
- **plan_id**: Identifier for the plan.
- **version**: Version of the plan.
- **description**: Description of the skill's purpose.
- **pattern**: Design pattern used.
- **model_hint**: Model hint for the AI model.
- **context**: Detailed context including database schema, class scaffold, and mandatory patterns.
- **build_plan**: Step-by-step instructions for building the skill.
- **test_cases**: Test cases to validate the skill.

#### Patterns
- **Data Query Skill**: The skill follows a data query pattern, focusing on retrieving and processing data from the database.
- **Mandatory Patterns**: Specific patterns like `_get_conn`, `connection_cleanup`, and `no_unicode` are enforced.

#### Dependencies
- **PostgreSQL**: The skill relies on a PostgreSQL database.
- **psycopg2**: For database connection and querying.
- **os**: For environment variable access.
- **datetime**: For date and time manipulation.
- **re**: For regular expression operations.
- **RealDictCursor**: For cursor factory to return results as dictionaries.
- **dotenv**: For loading environment variables.
- **engine.base**: For base classes and utilities (`SkillBase`, `SkillRequest`, `SkillResponse`).

#### Interfaces
- **Class**: `QueryBillsDueSkill` inherits from `SkillBase` and implements methods like `execute`, `_detect_days`, `_query_bills`, `_format_results`, and `_build_summary`.
- **Methods**:
  - `execute`: Main method to execute the skill.
  - `_detect_days`: Detects the number of days from the message.
  - `_query_bills`: Queries bills due in the next N days.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the results.

#### Database
- **Tables**:
  - `recurring_bills`: Contains recurring bill details.
  - `bill_overrides`: Contains overrides for specific months.
- **Queries**:
  - Query bills due between today's day-of-month and today+N.
  - Join `bill_overrides` to check payment status.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`

#### Key Logic
- **_detect_days**: Detects the number of days from the message using regular expressions and keyword matching.
- **_query_bills**: Queries the database to get bills due in the next N days, joining with `bill_overrides` to check payment status.
- **_format_results**: Formats the query results into a list of dictionaries.
- **_build_summary**: Builds a summary string of the results.
- **execute**: Orchestrates the detection of days, querying, formatting, and summarizing, and returns a `SkillResponse`.

#### Integration Points
- **engine.base**: The skill integrates with the base skill framework (`SkillBase`, `SkillRequest`, `SkillResponse`).
- **PostgreSQL**: The skill integrates with the PostgreSQL database through the `_get_conn` method.
- **Test Cases**: The skill is tested with predefined messages to ensure it returns the expected data and summary.

### Detailed Breakdown of Build Plan Steps
1. **Write File Skeleton**: Create the file structure with necessary imports and class definition.
2. **Implement `_detect_days`**: Implement logic to detect the number of days from the message.
3. **Implement `_query_bills`**: Implement the database query to get bills due in the next N days.
4. **Implement `_format_results` and `_build_summary`**: Implement methods to format the query results and build a summary.
5. **Implement `execute`**: Implement the main method to orchestrate the skill's execution.
6. **Review**: Final review to ensure all mandatory patterns are followed and the skill is production-ready.

### Test Cases
- **"what bills are due this week"**: Should return bills due in the next 7 days.
- **"upcoming bills next 14 days"**: Should return bills due in the next 14 days.
- **"bills due"**: Should return bills due in the default 7 days.

This JSON file provides a comprehensive guide for developing the `QueryBillsDueSkill` skill, ensuring it meets the required functionality and adheres to the specified patterns and configurations.
