# finance/schema_validator.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 381

---

### File: finance/schema_validator.py

#### Purpose
This file contains functions to validate and compare the actual PostgreSQL database schema against an expected schema, generating a detailed report of any discrepancies.

#### Architecture
The file consists of several top-level functions that interact with the PostgreSQL database to retrieve schema information and generate a report. The main functions are:
- `get_connection`: Establishes a connection to the PostgreSQL database.
- `get_actual_tables`: Retrieves the list of tables in the public schema.
- `get_actual_columns`: Retrieves the columns for a specific table.
- `format_data_type`: Formats the data type string for columns.
- `get_table_row_count`: Retrieves the row count for a specific table.
- `get_indexes`: Retrieves the indexes for a specific table.
- `generate_report`: Generates a full schema comparison report.

#### Patterns
- **Singleton Pattern**: The `get_connection` function can be considered a singleton as it ensures a single connection to the database.
- **Factory Method**: The `generate_report` function acts as a factory method, orchestrating the generation of the report by calling other functions.

#### Dependencies
- **Imports**: `os`, `sys`, `datetime`, `dotenv`, `psycopg2`, `psycopg2.extras`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Exposed Functions**: `generate_report()`
- **Output**: The report is written to a file specified by `OUTPUT_FILE`.

#### Database
- **Tables/Views**: `information_schema.tables`, `information_schema.columns`, `pg_indexes`
- **Operations**: 
  - Querying `information_schema.tables` to get the list of tables.
  - Querying `information_schema.columns` to get column details.
  - Querying `pg_indexes` to get index details.
  - Querying specific tables to get row counts.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- **Configuration File**: `.env` file loaded using `dotenv`.

#### Key Logic
1. **Connection Management**: Establishes a connection to the PostgreSQL database using environment variables.
2. **Schema Retrieval**: Retrieves actual tables and columns from the database.
3. **Schema Comparison**: Compares the actual schema with the expected schema defined in `EXPECTED_SCHEMA`.
4. **Report Generation**: Generates a detailed report including:
   - Summary of expected vs actual tables.
   - List of missing and extra tables.
   - Detailed column comparison for each table.
   - Suggested SQL migration commands for fixing schema issues.

#### Integration Points
- **Database Integration**: Uses `psycopg2` to interact with PostgreSQL.
- **Configuration Integration**: Loads environment variables from `.env` using `dotenv`.
- **File System Integration**: Writes the generated report to a file specified by `OUTPUT_FILE`.

### Detailed Function Descriptions

1. **`get_connection()`**
   - Establishes a connection to the PostgreSQL database using environment variables.
   - Returns a connection object with `RealDictCursor` as the cursor factory.

2. **`get_actual_tables(cur)`**
   - Retrieves the list of tables in the public schema.
   - Returns a list of table names.

3. **`get_actual_columns(cur, table_name)`**
   - Retrieves the columns for a specific table.
   - Returns a list of column details including name, data type, maximum length, precision, scale, nullability, and default value.

4. **`format_data_type(col)`**
   - Formats the full data type string for a column.
   - Returns the formatted data type string.

5. **`get_table_row_count(cur, table_name)`**
   - Retrieves the row count for a specific table.
   - Returns the count or "ERROR" if an exception occurs.

6. **`get_indexes(cur, table_name)`**
   - Retrieves the indexes for a specific table.
   - Returns a list of index details including name and definition.

7. **`generate_report()`**
   - Generates a full schema comparison report.
   - Connects to the database, retrieves schema information, compares it with the expected schema, and writes the report to a file.

### Example Usage
```python
# Generate the schema validation report
generate_report()
```

This will produce a detailed report in the specified output file, highlighting any discrepancies between the actual and expected database schema.
