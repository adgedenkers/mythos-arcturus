# assets/bin/backfill_assets_for_batch.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 86

---

### File: assets/bin/backfill_assets_for_batch.py

#### Purpose
This script backfills asset fields for a single clothing batch directory that contains `items.json` and `images/`. It updates the `clothing_images` table with asset information and upserts new media assets into the `media_assets` table.

#### Architecture
The script consists of three main functions:
1. `conn()`: Establishes a connection to the PostgreSQL database.
2. `upsert_media_asset(cur, sha256, file_ext, rel_path, byte_size)`: Upserts a media asset into the `media_assets` table.
3. `main()`: The main function that parses command-line arguments, processes the batch directory, and updates the database.

#### Patterns
- **None**: The script does not use any specific design patterns like factory, singleton, or observer.

#### Dependencies
- `sys`: For system-specific parameters and functions.
- `os`: For interacting with the operating system.
- `json`: For parsing JSON files.
- `psycopg2`: For PostgreSQL database operations.
- `argparse`: For parsing command-line arguments.
- `asset_store`: For ensuring assets are properly managed.

#### Interfaces
- **Command-line Interface**: The script accepts a `--batch-dir` argument to specify the batch directory to process.
- **Database Interface**: The script interacts with the PostgreSQL database to update the `clothing_images` and `media_assets` tables.

#### Database
- **Tables/Labels**:
  - `media_assets`: Insert operations to upsert media assets.
  - `clothing_images`: Update operations to set `batch_name`, `asset_sha256`, and `asset_rel_path`.

#### Configuration
- **Environment Variables**:
  - `MYTHOS_DB`: The name of the PostgreSQL database to connect to (default is "mythos").
- **Paths**:
  - `ASSETS_ROOT`: The root directory for assets, set to `/opt/mythos/assets`.

#### Key Logic
1. **Connection Management**: Establishes a database connection and ensures it is closed properly.
2. **Batch Directory Processing**: Reads `items.json` and processes each item's images.
3. **Asset Management**: Ensures each image asset is properly managed and upserted into the `media_assets` table.
4. **Database Updates**: Updates the `clothing_images` table with the new asset information.

#### Integration Points
- **asset_store**: The script uses the `ensure_asset` function from the `asset_store` module to manage assets.
- **Database**: The script integrates with the PostgreSQL database to perform upserts and updates.

### Detailed Documentation

#### `conn()`
- **Purpose**: Establishes a connection to the PostgreSQL database using the `psycopg2` library.
- **Dependencies**: `psycopg2`, `os.environ.get("MYTHOS_DB")`.

#### `upsert_media_asset(cur, sha256, file_ext, rel_path, byte_size)`
- **Purpose**: Upserts a media asset into the `media_assets` table.
- **Parameters**:
  - `cur`: Database cursor.
  - `sha256`: SHA256 hash of the asset.
  - `file_ext`: File extension of the asset.
  - `rel_path`: Relative path of the asset.
  - `byte_size`: Size of the asset in bytes.
- **Logic**: Uses an `INSERT ... ON CONFLICT` statement to ensure the asset is upserted.

#### `main()`
- **Purpose**: The main function that processes the batch directory and updates the database.
- **Logic**:
  1. **Argument Parsing**: Uses `argparse` to parse the `--batch-dir` argument.
  2. **Directory Validation**: Checks if `items.json` and `images/` exist in the batch directory.
  3. **Database Connection**: Establishes a database connection.
  4. **Batch Processing**: Iterates over each item in `items.json`, processes each image, and updates the database.
  5. **Transaction Management**: Ensures transactions are committed or rolled back based on success or failure.

### Example Usage
```bash
python3 backfill_assets_for_batch.py --batch-dir /opt/mythos/sales_ingestion/sales-db-ingestion-0001
```

This command will backfill the asset fields for the specified batch directory.
