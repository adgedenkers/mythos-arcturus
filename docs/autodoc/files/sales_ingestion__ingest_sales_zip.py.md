# sales_ingestion/ingest_sales_zip.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 392

---

### File: sales_ingestion/ingest_sales_zip.py

#### Purpose
This Python script ingests sales data from JSON files and SQL scripts into a PostgreSQL database, ensuring idempotency and logging the ingestion process. It handles both clothing and shoe data, integrating with an asset store for media assets.

#### Architecture
The file is organized into several sections:
1. **DB helpers**: Functions for database connection, logging, and media asset management.
2. **Ingestion logic**: Functions for ingesting JSON and SQL files, inserting data into various tables, and handling media assets.
3. **Entry point**: The `main` function, which parses command-line arguments and orchestrates the ingestion process.

#### Patterns
- **Singleton**: The database connection is managed as a singleton within the `get_conn` function.
- **Factory**: The `ensure_asset` function from `asset_store` acts as a factory for creating and managing media assets.
- **Observer**: The logging mechanism (`logger`) observes and logs the state of the ingestion process.

#### Dependencies
- **Standard Libraries**: `os`, `json`, `subprocess`, `logging`, `sys`, `argparse`
- **External Libraries**: `psycopg2`, `pathlib`
- **Internal Modules**: `asset_store` (from `/opt/mythos/assets`)

#### Interfaces
- **Functions**: `get_conn`, `upsert_log`, `get_log_status`, `upsert_media_asset`, `run_psql_file`, `ingest_items_json`, `insert_simple`, `insert_shoe_images_with_assets`, `ingest_shoes_json`, `insert_images_with_assets`, `main`
- **Entry Point**: `main` function for command-line execution.

#### Database
- **Tables**: `sales_ingestion_log`, `media_assets`, `clothing_items`, `clothing_colors`, `clothing_materials`, `clothing_images`, `shoe_images`, `shoes_forsale`
- **Operations**: Insertions, updates, and conflict resolution using `ON CONFLICT` clauses.

#### Configuration
- **Environment Variables**: `MYTHOS_DB` (default: `mythos`)
- **Logging**: `LOG_PATH` set to `/var/log/mythos_patch_monitor.log`

#### Key Logic
1. **Database Connection**: Establishes a connection to the PostgreSQL database using `psycopg2`.
2. **Logging**: Tracks the status of each ingestion batch in the `sales_ingestion_log` table.
3. **JSON Ingestion**: Parses JSON files for clothing and shoe items, inserting data into respective tables (`clothing_items` and `shoes_forsale`).
4. **Media Asset Management**: Ensures media assets are stored and referenced correctly using the `asset_store` module.
5. **SQL Ingestion**: Executes SQL scripts for legacy shoe ingestion when JSON files are not available.

#### Integration Points
- **Asset Store**: Integrates with the `asset_store` module to manage media assets.
- **Command-line Interface**: Uses `argparse` to accept command-line arguments for specifying the type of data (`sales` or `shoes`) and the extraction directory.
- **Logging**: Uses `logging` to record the ingestion process and any errors.

### Detailed Analysis

#### Functions

1. **get_conn**
   - **Purpose**: Establishes a connection to the PostgreSQL database.
   - **Dependencies**: `psycopg2`
   - **Returns**: Database connection object.

2. **upsert_log**
   - **Purpose**: Logs the status of an ingestion batch in the `sales_ingestion_log` table.
   - **Parameters**: `cur`, `batch_name`, `artifact_type`, `status`, `extract_dir`, `error`
   - **Operations**: Inserts or updates the log entry with the given status and error (if any).

3. **get_log_status**
   - **Purpose**: Retrieves the status of an ingestion batch from the `sales_ingestion_log` table.
   - **Parameters**: `cur`, `batch_name`, `artifact_type`
   - **Returns**: The status of the batch or `None` if not found.

4. **upsert_media_asset**
   - **Purpose**: Ensures a media asset is stored in the `media_assets` table.
   - **Parameters**: `cur`, `sha256`, `file_ext`, `rel_path`, `byte_size`
   - **Operations**: Inserts the asset if it does not already exist.

5. **run_psql_file**
   - **Purpose**: Executes a SQL file using `psql`.
   - **Parameters**: `sql_file`
   - **Dependencies**: `subprocess`

6. **ingest_items_json**
   - **Purpose**: Ingests clothing items from a JSON file into the `clothing_items` table.
   - **Parameters**: `cur`, `json_path`, `extract_dir`, `batch_name`
   - **Operations**: Inserts clothing items and associated data into various tables.

7. **insert_simple**
   - **Purpose**: Inserts simple data into a table.
   - **Parameters**: `cur`, `table`, `column`, `item_id`, `values`
   - **Operations**: Uses `execute_values` to insert multiple rows efficiently.

8. **insert_shoe_images_with_assets**
   - **Purpose**: Inserts shoe images and associated media assets into the `shoe_images` table.
   - **Parameters**: `cur`, `item_id`, `images`, `images_dir`, `batch_name`
   - **Operations**: Ensures each image is stored as a media asset and inserts the image data.

9. **ingest_shoes_json**
   - **Purpose**: Ingests shoe items from a JSON file into the `shoes_forsale` table.
   - **Parameters**: `cur`, `json_path`, `extract_dir`, `batch_name`
   - **Operations**: Inserts shoe items and associated data into various tables.

10. **insert_images_with_assets**
    - **Purpose**: Inserts clothing images and associated media assets into the `clothing_images` table.
    - **Parameters**: `cur`, `item_id`, `images`, `images_dir`, `batch_name`
    - **Operations**: Ensures each image is stored as a media asset and inserts the image data.

11. **main**
    - **Purpose**: Entry point for the script, orchestrates the ingestion process.
    - **Operations**: Parses command-line arguments, establishes a database connection, and calls the appropriate ingestion functions based on the input type.

### Summary
The `ingest_sales_zip.py` script is a comprehensive tool for ingesting sales data into a PostgreSQL database, ensuring idempotency and logging the process. It integrates with an asset store for managing media assets and supports both JSON and SQL ingestion methods. The script is designed to be run from the command line, making it flexible and easy to integrate into larger data pipelines.
