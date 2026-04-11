# eval/results/query_bills_due/20260305_091107/report.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 108

---

### Documentation for `eval/results/query_bills_due/20260305_091107/report.json`

#### Purpose
This JSON file contains the evaluation report for a specific execution of the `query_bills_due` plan, using the `qwen3-coder:30b` model. It captures the results of multiple passes and steps involved in generating and testing the code for querying due bills.

#### Architecture
The JSON structure is organized into several key sections:
- **Metadata**: Contains general information like `plan_id`, `model`, `timestamp`, and counts of passes and Ollama calls.
- **Final Checks**: Includes `final_parse`, `final_import`, and `final_behavioral` checks.
- **Steps**: Detailed breakdown of each pass, including instructions, test types, attempts, and final code metrics.

#### Patterns
- **Step-by-Step Execution**: The report follows a step-by-step execution pattern, where each step builds upon the previous one to produce a complete and tested piece of code.
- **Recursive Testing**: The final step includes recursive testing to ensure the code is production-ready.

#### Dependencies
- **External Systems**: The report relies on the `qwen3-coder:30b` model and the Mythos system for generating and testing the code.
- **Database**: The code generated interacts with PostgreSQL tables (`recurring_bills`, `bill_overrides`).

#### Interfaces
- **SkillResponse**: The final step generates a `SkillResponse` object with specific data fields (`bills`, `days_ahead`, `count`, `total_due`, `summary`, `confidence`, `sources`).

#### Database
- **Tables**: The code interacts with the `recurring_bills` and `bill_overrides` tables.
- **Queries**: The `_query_bills` method performs a SELECT query to retrieve bills due within a specified range of days.

#### Configuration
- **Environment Variables**: The code uses `POSTGRES_HOST` for database connection.
- **Configuration Files**: The code uses `dotenv` to load environment variables.

#### Key Logic
1. **_detect_days()**: Parses the message to detect the number of days ahead for the query. Uses regular expressions to find numeric values and handles keywords like 'week', 'month', 'today', and 'tomorrow'.
2. **_query_bills()**: Constructs a SQL query to fetch bills due within the specified range of days. Handles month wraparound by including days from the next month if necessary.
3. **_format_results()**: Formats the query results into a dictionary with specific fields.
4. **_build_summary()**: Builds a summary string based on the query results.
5. **execute()**: Combines the above methods to generate the final response, including error handling and connection management.

#### Integration Points
- **Ollama**: The report is generated as part of the Ollama calls, indicating integration with the Ollama system for model execution.
- **Mythos System**: The report and generated code integrate with the Mythos system, particularly with the PostgreSQL database and the `SkillResponse` object for returning results.

### Summary
This JSON file provides a comprehensive evaluation report for the `query_bills_due` plan, detailing each step of the code generation and testing process. It captures the logic for detecting days ahead, querying due bills, formatting results, and building summaries, all integrated with the Mythos system and PostgreSQL database.
