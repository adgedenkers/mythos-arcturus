# eval/challenges/search_documents/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 77

---

### File: `eval/challenges/search_documents/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for developing a Mythos skill named `SearchDocumentsSkill`. The skill is designed to search the document registry by title, type, or path, using PostgreSQL as the backend database.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the skill.
- **version**: Specifies the version of the plan.
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the memory search pattern.
- **model_hint**: Specifies the model hint for the skill.
- **context**: Contains detailed information about the system context, table schema, class scaffold, and mandatory patterns.
- **build_plan**: A step-by-step guide for implementing the skill, divided into multiple passes.
- **test_cases**: Provides test cases to validate the skill's functionality.

#### Patterns
- **Singleton**: The `_get_conn` function is designed to be a singleton pattern for database connection.
- **Factory**: The `execute` method can be seen as a factory method that constructs and returns a `SkillResponse` object.

#### Dependencies
- **Imports**: The skill relies on `os`, `logging`, `psycopg2`, `psycopg2.extras.RealDictCursor`, and `dotenv` for database connection and environment variable handling.
- **Environment Variables**: Uses `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT` from the environment.
- **Configuration Files**: Uses `.env` file for loading database connection details.

#### Interfaces
- **SkillBase**: The `SearchDocumentsSkill` class inherits from `SkillBase` and implements methods like `execute`, `_extract_search_terms`, `_detect_doc_type`, `_search_docs`, `_format_results`, and `_build_summary`.
- **SkillRequest and SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object.

#### Database
- **Tables**: The skill interacts with the `document_registry` table and the related `document_versions` table.
- **Queries**: Uses `ILIKE` for case-insensitive title search and optional filtering by `doc_type`.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables.
- **.env File**: Used to load database connection details.

#### Key Logic
- **_extract_search_terms**: Removes trigger phrases and normalizes whitespace.
- **_detect_doc_type**: Detects document type keywords in the message.
- **_search_docs**: Constructs and executes a PostgreSQL query to search the document registry.
- **_format_results**: Formats the query results into a list of dictionaries.
- **_build_summary**: Builds a summary string based on the search results.
- **execute**: Orchestrates the search process, handling extraction, detection, querying, formatting, and summarizing.

#### Integration Points
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **Skill Base Class**: Inherits from `SkillBase` and integrates with the Mythos skill framework.
- **Environment Variables**: Loads database connection details from environment variables.
- **Test Cases**: Provides test cases to validate the skill's functionality within the Mythos system.

### Detailed Breakdown of Build Plan Passes

1. **Pass 1**: Write the complete file skeleton, including the `SearchDocumentsSkill` class with all attributes and methods.
2. **Pass 2**: Implement `_extract_search_terms` and `_detect_doc_type` methods.
3. **Pass 3**: Implement `_search_docs` method to query the `document_registry` table.
4. **Pass 4**: Implement `_format_results` and `_build_summary` methods to format and summarize the search results.
5. **Pass 5**: Implement the `execute` method to orchestrate the search process.
6. **Pass 6**: Review the complete file for production readiness, ensuring all connections are closed and summaries are non-empty.

### Test Cases
- **Test Case 1**: Message "find document about architecture" should return search results.
- **Test Case 2**: Message "what documents do we have" should return search results.
- **Test Case 3**: Message "hey iris" should return the total count of documents in the registry.

This JSON file provides a comprehensive guide for developing the `SearchDocumentsSkill` skill within the Mythos system, ensuring all necessary components and logic are implemented correctly.
