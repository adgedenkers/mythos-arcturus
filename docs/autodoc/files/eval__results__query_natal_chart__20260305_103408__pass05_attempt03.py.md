# eval/results/query_natal_chart/20260305_103408/pass05_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### Documentation for `eval/results/query_natal_chart/20260305_103408/pass05_attempt03.py`

#### Purpose
This file contains the implementation of a skill (`QueryNatalChartSkill`) that queries a PostgreSQL database to retrieve and format natal chart data for specified individuals. The skill handles resolving names, querying chart data, and formatting the results into a readable summary.

#### Architecture
The file consists of a single class `QueryNatalChartSkill` which inherits from `SkillBase`. The class contains several methods for resolving names, querying chart data, and formatting the results. Additionally, there are several top-level functions for database connection and utility operations.

- **Class: `QueryNatalChartSkill`**
  - **Methods:**
    - `execute`: Main method to execute the skill, resolving the name, querying the chart, and formatting the results.
    - `_resolve_name`: Resolves the input name to a standardized name.
    - `_query_chart`: Queries the PostgreSQL database for the natal chart data.
    - `_query_placements`: Queries the PostgreSQL database for the placements in the chart.
    - `_format`: Formats the chart data and placements into a readable string.
    - `_build_summary`: Builds a summary of the chart data and placements.

- **Top-level Functions:**
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that might be used for testing or other purposes.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures that a database connection is established only when needed and closed properly.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that constructs and returns a `SkillResponse` object based on the input request.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Public method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, `_build_summary`: Private methods used internally by `execute`.

#### Database
- **Tables/Labels**:
  - `astro_natal_charts`: Table containing natal chart data.
  - `astro_chart_objects`: Table containing placements in the chart.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_PORT`: Used to configure the PostgreSQL database connection.

#### Key Logic
- **Name Resolution**: The `_resolve_name` method maps input names to standardized names using a predefined `NAME_MAP`.
- **Database Queries**: The `_query_chart` and `_query_placements` methods execute SQL queries to retrieve chart data and placements from the PostgreSQL database.
- **Result Formatting**: The `_format` and `_build_summary` methods format the retrieved data into a readable summary and detailed placements list.

#### Integration Points
- **SkillBase Integration**: The `QueryNatalChartSkill` class integrates with the `SkillBase` class, which likely defines the overall structure and lifecycle of a skill in the Mythos system.
- **Database Integration**: The skill interacts with the PostgreSQL database to retrieve and process natal chart data.
- **Response Integration**: The skill constructs and returns a `SkillResponse` object, which is likely used by other parts of the Mythos system to handle and present the results.

This file is a critical component of the Mythos system, providing a structured way to query and present natal chart data, and it integrates seamlessly with the broader system architecture.
