# eval/results/query_bills_due/20260305_091107/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 196

---

### Purpose
The `pass05_attempt01.py` file contains the implementation of the `QueryBillsDueSkill` class, which is responsible for querying upcoming bills due in the next N days from a PostgreSQL database and formatting the results for display.

### Architecture
The file is structured around a single class `QueryBillsDueSkill` that inherits from `SkillBase`. The class contains several methods:
- `execute`: The main method that orchestrates the bill query process.
- `_detect_days`: Detects the number of days to look ahead based on the input message.
- `_query_bills`: Queries the PostgreSQL database for bills due in the next N days.
- `_format_results`: Formats the raw query results into a more user-friendly structure.
- `_build_summary`: Builds a summary of the query results.

### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function ensures a single database connection is created and reused.

### Dependencies
- **Imports**: The file imports `os`, `logging`, `re`, `psycopg2`, and `dotenv`.
- **Database**: The file relies on PostgreSQL for querying bill data.
- **Environment Variables**: The file uses environment variables to configure the database connection.

### Interfaces
- **Public Methods**: The `execute` method is the primary public interface for executing the skill.
- **SkillBase Inheritance**: The class inherits from `SkillBase`, which likely defines the structure for skills in the Mythos system.

### Database
- **Tables**: The file interacts with the `recurring_bills` and `bill_overrides` tables in PostgreSQL.
- **Queries**: It performs queries to fetch bills due in the next N days and checks for payment overrides.

### Configuration
- **Environment Variables**: The file uses environment variables (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`) to configure the database connection.
- **Dotenv**: The `dotenv` library is used to load environment variables from a `.env` file.

### Key Logic
- **Bill Detection**: The `_detect_days` method parses the input message to determine the number of days to look ahead.
- **Bill Query**: The `_query_bills` method constructs and executes a query to fetch bills due in the next N days, handling month wraparound.
- **Result Formatting**: The `_format_results` method formats the raw query results into a structured list.
- **Summary Building**: The `_build_summary` method generates a summary of the query results, including the total amount due and details of each bill.

### Integration Points
- **SkillBase Integration**: The `QueryBillsDueSkill` class integrates with the `SkillBase` class, which likely handles the overall skill execution framework.
- **Database Connection**: The `_get_conn` function provides a reusable database connection, which is used by the `_query_bills` method.
- **Environment Configuration**: The file integrates with the environment configuration through `dotenv` to load database connection details.

### Detailed Analysis
- **_get_conn**: This function establishes a connection to the PostgreSQL database using environment variables for configuration. It ensures a reusable and consistent connection.
- **_detect_days**: This method parses the input message to determine the number of days to look ahead. It handles specific keywords and numeric values.
- **_query_bills**: This method constructs and executes a query to fetch bills due in the next N days. It handles month wraparound by splitting the query into two parts if the lookahead period spans two months.
- **_format_results**: This method formats the raw query results into a structured list, converting amounts to floats and including payment status.
- **_build_summary**: This method generates a summary of the query results, including the total amount due and details of each bill.

This file is a critical component of the Mythos system, providing a robust and flexible mechanism for querying and summarizing upcoming bills due in the next N days.
