# eval/results/query_natal_chart/20260305_103408/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 112

---

### Documentation for `eval/results/query_natal_chart/20260305_103408/pass04_attempt01.py`

#### Purpose
This file contains the implementation of the `QueryNatalChartSkill` class, which is responsible for querying and formatting natal astrology charts from a PostgreSQL database based on user input.

#### Architecture
The file consists of a single class `QueryNatalChartSkill` that inherits from `SkillBase`. The class contains several methods to handle the execution of the skill, resolving names, querying the database, formatting the results, and building summaries. Additionally, there are top-level functions for database connection and name resolution.

- **Classes:**
  - `QueryNatalChartSkill`: Inherits from `SkillBase` and contains methods for resolving names, querying the database, formatting results, and building summaries.
  
- **Methods:**
  - `execute`: Main method to execute the skill, resolving the name, querying the chart and placements, and formatting the response.
  - `_resolve_name`: Resolves the user-provided name to a standardized name.
  - `_query_chart`: Queries the `astro_natal_charts` table for chart data.
  - `_query_placements`: Queries the `astro_chart_objects` table for placements data.
  - `_format`: Formats the chart and placements data into a readable string.
  - `_build_summary`: Builds a summary of the chart data.

- **Top-level Functions:**
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for execution.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established per call.
- **Factory Method Pattern**: The `execute` method acts as a factory method to create a `SkillResponse` object based on the query results.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Exposed to other parts of the system to execute the skill.
  - `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`: Internal methods used by `execute`.

#### Database
- **Tables/Labels**:
  - `astro_natal_charts`: Contains natal chart data.
  - `astro_chart_objects`: Contains placements data for each chart.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`: Configured in `.env` file for database connection.

#### Key Logic
- **Name Resolution**: The `_resolve_name` method maps user-provided names to standardized names using a predefined mapping.
- **Database Queries**: The `_query_chart` and `_query_placements` methods fetch chart and placements data from the PostgreSQL database.
- **Result Formatting**: The `_format` and `_build_summary` methods format the fetched data into a readable summary and detailed placements list.

#### Integration Points
- **Skill Execution**: The `execute` method integrates with the Mythos system to process user requests and return formatted responses.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to fetch astrology chart data.
- **Environment Configuration**: The `load_dotenv` function integrates with the `.env` file to load necessary environment variables for database connection.

This file is a crucial component of the Mythos system, enabling the retrieval and formatting of astrology chart data based on user input.
