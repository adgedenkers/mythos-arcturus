# eval/challenges/add_idea/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 35

---

### File: `eval/challenges/add_idea/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for developing a skill in the Mythos system that captures new ideas into an idea inbox. It provides detailed instructions, patterns, and test cases for implementing the `AddIdeaSkill` class.

#### Architecture
The file is structured into several key sections:
- **plan_id**: Identifies the skill.
- **version**: Specifies the version of the plan.
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the type of skill.
- **model_hint**: Suggests the model to be used.
- **context**: Contains detailed information about the system context, table schema, class scaffold, and mandatory patterns.
- **build_plan**: Lists step-by-step instructions for implementing the skill.
- **test_cases**: Provides test cases to validate the implementation.

#### Patterns
- **Factory Method**: The `AddIdeaSkill` class is a factory method for creating instances of the skill.
- **Singleton**: The `_get_conn` function ensures a single connection to the PostgreSQL database.
- **Observer**: The `execute` method observes the incoming request and triggers the idea capture process.

#### Dependencies
- **Imports**: The file requires imports from `os`, `logging`, `json`, `psycopg2`, `RealDictCursor`, `dotenv`, and `engine.base`.
- **Environment Variables**: Uses `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT`.

#### Interfaces
- **SkillBase Class**: The `AddIdeaSkill` class inherits from `SkillBase` and implements methods like `execute`, `_extract_idea`, `_detect_domain`, and `_insert_idea`.
- **SkillResponse**: The `execute` method returns an instance of `SkillResponse` with specific attributes.

#### Database
- **Table**: `idea_inbox` with columns `id`, `created_at`, `conversation_context`, `items`, `item_count`, `disposition`, `domain`, and `tags`.

#### Configuration
- **Environment Variables**: The `_get_conn` function uses environment variables to configure the PostgreSQL connection.
- **Mandatory Patterns**: Specific patterns like `_get_conn`, `connection_cleanup`, `no_unicode`, `skillresponse_signature`, and `json_import` are enforced.

#### Key Logic
1. **Extract Idea**: The `_extract_idea` method cleans and normalizes the idea text.
2. **Detect Domain**: The `_detect_domain` method identifies the domain of the idea.
3. **Insert Idea**: The `_insert_idea` method inserts the idea into the `idea_inbox` table.
4. **Execute**: The `execute` method orchestrates the extraction, detection, and insertion processes and returns a `SkillResponse`.

#### Integration Points
- **Engine Base**: The `AddIdeaSkill` class integrates with the `engine.base` module to inherit from `SkillBase`.
- **PostgreSQL**: The `_get_conn` function integrates with the PostgreSQL database to manage connections and transactions.
- **JSON Handling**: The `json.dumps` method is used to handle `jsonb` columns in the database.

### Detailed Breakdown

#### Context
- **System Context**: Specifies the PostgreSQL database and necessary imports.
- **Table Schema**: Describes the `idea_inbox` table structure.
- **Scaffold**: Provides a class template for `AddIdeaSkill` with placeholders for methods.
- **Mandatory Patterns**: Ensures consistency in connection handling, ASCII-only comments, and `SkillResponse` usage.

#### Build Plan
1. **Pass 1**: Write the file skeleton with required imports and class structure.
2. **Pass 2**: Implement `_extract_idea` and `_detect_domain` methods.
3. **Pass 3**: Implement `_insert_idea` method to insert ideas into the database.
4. **Pass 4**: Implement the `execute` method to orchestrate the idea capture process.
5. **Pass 5**: Review and ensure production readiness.

#### Test Cases
- **Test Case 1**: Validates capturing a detailed idea.
- **Test Case 2**: Validates capturing a shorter idea.
- **Test Case 3**: Validates handling too short ideas with guidance.

This JSON file provides a comprehensive guide for developing the `AddIdeaSkill` in the Mythos system, ensuring consistency and correctness in implementation.
