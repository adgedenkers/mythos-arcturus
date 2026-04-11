# setup_asset_store_and_helpers.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 612

---

### File: `setup_asset_store_and_helpers.sh`

#### Purpose
This bash script sets up the asset store and read helper components for the Mythos system. It ensures the necessary directories and files are in place, installs required Python dependencies, and creates or updates database structures for asset management.

#### Architecture
The script follows a step-by-step approach to:
1. Perform preflight checks.
2. Backup existing files.
3. Ensure necessary directories exist.
4. Install Python dependencies.
5. Create or update database structures.
6. Write Python scripts for asset management and read helpers.
7. Update the sales ingestion script to integrate with the asset store.

#### Patterns
- **Scripting**: The script uses a sequence of commands to ensure the setup is done in a structured manner.
- **Error Handling**: Uses `set -euo pipefail` to ensure the script exits on any error.

#### Dependencies
- **System Commands**: `echo`, `test`, `command`, `mkdir`, `cp`, `date`, `psql`, `pip`.
- **Python Scripts**: `ingest_sales_zip.py`, `asset_store.py`, `read_helper.py`, `backfill_assets_for_batch.py`.

#### Interfaces
- **Directories**: Ensures the existence of directories like `/opt/mythos/assets`, `/opt/mythos/sales_ingestion`, and `/opt/mythos/shoe_ingestion`.
- **Python Scripts**: Writes and makes executable Python scripts for asset management and read helpers.
- **Database**: Creates and updates database tables and columns.

#### Database
- **Tables**: `media_assets`, `clothing_images`, `shoe_images`.
- **Columns**: Adds columns `batch_name`, `asset_sha256`, `asset_rel_path` to `clothing_images` and `shoe_images` if they do not exist.

#### Configuration
- **Environment Variables**: `MYTHOS_DB` (default value: `mythos`).
- **File Paths**: Uses paths like `/opt/mythos`, `/var/log/mythos_patch_monitor.log`.

#### Key Logic
1. **Preflight Checks**: Ensures `venv` Python and `psql` are available.
2. **Backup**: Backs up existing files to a timestamped directory.
3. **Directory Setup**: Ensures necessary directories exist.
4. **Python Dependencies**: Upgrades `pip` and installs `psycopg2-binary`.
5. **Database Setup**: Creates `media_assets` table and adds necessary columns to `clothing_images` and `shoe_images`.
6. **Asset Management**: Writes `asset_store.py` and `read_helper.py` scripts for managing and resolving asset paths.
7. **Backfill Script**: Writes `backfill_assets_for_batch.py` to backfill asset fields for legacy ingestions.
8. **Ingestor Update**: Updates `ingest_sales_zip.py` to integrate with the asset store.

#### Integration Points
- **Asset Store**: Integrates with the asset store to manage and deduplicate assets.
- **Sales Ingestion**: Updates the sales ingestion script to use the asset store for managing clothing images.
- **Database**: Connects to the PostgreSQL database to create tables and update columns.
- **Logging**: Logs actions to `/var/log/mythos_patch_monitor.log`.

### Detailed Breakdown

#### Preflight Checks
- Ensures `venv` Python and `psql` are available.

#### Backup
- Backs up the existing `ingest_sales_zip.py` to a timestamped directory.

#### Directory Setup
- Ensures the existence of directories like `/opt/mythos/assets/images`, `/opt/mythos/assets/bin`, `/opt/mythos/sales_ingestion`, and `/opt/mythos/shoe_ingestion`.

#### Python Dependencies
- Upgrades `pip` and installs `psycopg2-binary`.

#### Database Setup
- Creates `media_assets` table with columns `id`, `sha256`, `file_ext`, `rel_path`, `byte_size`, and `created_at`.
- Adds columns `batch_name`, `asset_sha256`, and `asset_rel_path` to `clothing_images` and `shoe_images` if they do not exist.

#### Asset Management
- Writes `asset_store.py` to manage assets by ensuring they are stored in the central asset store.
- Writes `read_helper.py` to resolve image paths for clothing and shoes.

#### Backfill Script
- Writes `backfill_assets_for_batch.py` to backfill asset fields for legacy ingestions.

#### Ingestor Update
- Updates `ingest_sales_zip.py` to integrate with the asset store for managing clothing images.

This script ensures that the asset store and read helper components are properly set up and integrated into the Mythos system.
