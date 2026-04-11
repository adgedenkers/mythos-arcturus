# eval/challenges/query_shopping_lists/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 34

---

### Documentation for `eval/challenges/query_shopping_lists/build_plan.json`

#### Purpose
This JSON file serves as a build plan for constructing a skill in the Mythos system that queries active shopping lists and their items from a PostgreSQL database. It outlines the step-by-step process, including mandatory patterns, database schema, and implementation details.

#### Architecture
The file is structured as a JSON object with the following key components:
- `plan_id`: Identifier for the build plan.
- `version`: Version of the build plan.
- `description`: Brief description of the skill.
- `pattern`: Pattern identifier for the skill.
- `model_hint`: Model hint for the skill.
- `context`: Contains system context, table schema, and mandatory patterns.
- `build_plan`: A list of steps to build the skill, each with an instruction and test case.
- `test_cases`: Test cases to validate the skill.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the build plan follows a step-by-step factory-like approach to construct the skill.
- **Singleton Pattern**: Not used.
- **Observer Pattern**: Not used.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `RealDictCursor`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **SkillBase Class**: The skill extends `SkillBase` from `engine.base`.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` from `engine.base`.

#### Database
- **Tables**:
  - `shopping_lists`: Columns include `id`, `name`, `status`, `is_active`, `created_at`.
  - `shopping_list_items`: Columns include `id`, `list_id`, `item_id`, `quantity`, `priority`, `notes`, `completed`.
  - `shopping_items`: Columns include `id`, `name`, `department`, `default_unit`, `usual_price`, `is_active`.
- **JOIN Path**: `shopping_lists -> shopping_list_items -> shopping_items`.

#### Configuration
- **Environment Variables**: Used to configure the PostgreSQL connection.
- **Database Configuration**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Key Logic
- **_get_conn()**: Establishes a connection to the PostgreSQL database.
- **_query_lists()**: Queries active shopping lists.
- **_query_items(list_id)**: Queries items for a specific shopping list.
- **_format_results()**: Formats the query results into a dictionary.
- **_build_summary()**: Builds a summary of the shopping lists.
- **execute()**: Main method that orchestrates the querying, formatting, and summarizing.

#### Integration Points
- **SkillBase**: The skill integrates with the `SkillBase` class from `engine.base`.
- **Database Connection**: Uses `psycopg2` to connect to PostgreSQL.
- **Logging**: Uses Python's `logging` module for logging.
- **Environment Configuration**: Uses `dotenv` to load environment variables.

### Detailed Steps in the Build Plan

1. **Pass 1**: Write the file skeleton, including the class `QueryShoppingListsSkill` and placeholder methods.
2. **Pass 2**: Implement `_query_lists()` and `_query_items()`, ensuring connections are properly managed.
3. **Pass 3**: Implement `_format_results()` and `_build_summary()`, formatting the results and building a summary.
4. **Pass 4**: Implement `execute()`, which queries lists, items, formats results, and builds a summary.
5. **Pass 5**: Review the implementation, ensuring all patterns and requirements are met.

### Test Cases
- **Test Case 1**: Query with "what is on my shopping list" should return data with "lists".
- **Test Case 2**: Query with "groceries" should return a valid response.
- **Test Case 3**: Query with "do I need to buy anything" should return a valid response.

This build plan ensures that the skill is thoroughly developed and tested, adhering to the specified patterns and requirements.
