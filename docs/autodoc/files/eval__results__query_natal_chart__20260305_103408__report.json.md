# eval/results/query_natal_chart/20260305_103408/report.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 188

---

### File: `eval/results/query_natal_chart/20260305_103408/report.json`

#### Purpose
This JSON file contains a detailed report of the evaluation process for the `query_natal_chart` plan, including various steps, instructions, and test results for each pass. It documents the development and testing phases of the `QueryNatalChartSkill` class, which is responsible for querying and formatting natal chart data from a PostgreSQL database.

#### Architecture
The file is structured as a JSON object with the following key components:
- **Metadata**: `plan_id`, `model`, `timestamp`, `total_passes`, `total_ollama_calls`, `final_parse`, `final_import`, `final_behavioral`.
- **Steps**: An array of objects, each representing a pass in the evaluation process. Each step includes:
  - `pass`: The pass number.
  - `instruction`: The instruction given for that pass.
  - `test_type`: The type of test performed (`parse_check`, `import_check`, `full_behavioral`).
  - `recursive`: Whether the test was recursive.
  - `attempts`: An array of objects detailing each attempt, including `attempt`, `test_pass`, and `errors`.
  - `elapsed_seconds`: The time taken for the pass.
  - `final_code_lines`: The number of lines in the final code after the pass.

#### Patterns
- **Step-by-Step Development**: The file follows a step-by-step development pattern, where each pass builds upon the previous one.
- **Error Handling**: Each pass includes error handling, documenting any issues encountered during the test.

#### Dependencies
- **Imports**: The file references several Python modules and libraries such as `os`, `logging`, `psycopg2`, `RealDictCursor`, `dotenv`, and `engine.base`.
- **Database**: The file relies on PostgreSQL for querying natal chart data.

#### Interfaces
- **Methods**: The `QueryNatalChartSkill` class is expected to have methods such as `execute`, `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, and `_build_summary`.
- **SkillResponse**: The `execute` method is expected to return a `SkillResponse` object with specific attributes like `skill_name`, `data`, `summary`, `confidence`, and `sources`.

#### Database
- **Tables**: The file references the following PostgreSQL tables:
  - `astro_natal_charts`: Contains natal chart data.
  - `astro_chart_objects`: Contains placements data for each chart.

#### Configuration
- **Environment Variables**: The file mentions the use of `POSTGRES_HOST` for database connection.
- **Name Mapping**: The file uses a `NAME_MAP` dictionary to map names to specific values.

#### Key Logic
- **_resolve_name**: Converts the input message to lowercase and maps it to a predefined name using `NAME_MAP`.
- **_query_chart**: Queries the `astro_natal_charts` table to retrieve chart data based on the name.
- **_query_placements**: Queries the `astro_chart_objects` table to retrieve placements data for a given chart ID.
- **_format**: Formats the chart data and placements into a dictionary.
- **_build_summary**: Constructs a summary string based on the chart data and placements.
- **execute**: Orchestrates the resolution of the name, querying of the chart and placements, formatting, and summarizing, and returns a `SkillResponse` object.

#### Integration Points
- **Ollama**: The file mentions `total_ollama_calls`, indicating integration with the Ollama subsystem.
- **PostgreSQL**: The file integrates with PostgreSQL for database queries.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, indicating integration with the Mythos skill response system.

### Summary
The `report.json` file provides a comprehensive log of the development and testing process for the `QueryNatalChartSkill` class. It details each step, including instructions, test results, and error handling, and highlights the integration with PostgreSQL and the Mythos skill response system.
