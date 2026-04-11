# upgrade_sales_ingestion_pipeline.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 434

---

### File: `upgrade_sales_ingestion_pipeline.sh`

#### Purpose
This bash script automates the upgrade process for the sales and shoe ingestion pipeline in the Mythos system. It performs preflight checks, backs up existing files, ensures necessary directories exist, installs the ingestion runner script, and upgrades the monitor script to support new ingestion types.

#### Architecture
The script is structured into several sections:
1. **Settings**: Defines environment variables and paths.
2. **Preflight Checks**: Ensures required files and tools are available.
3. **Backups**: Creates a backup of the current files.
4. **Ensure Directories**: Ensures necessary directories exist for ingestion.
5. **Install Ingestor**: Writes and installs the ingestion runner script.
6. **Upgrade Monitor Script**: Upgrades the monitor script to support new ingestion types.

#### Patterns
- **Singleton**: The script ensures that only one instance of the monitor script runs at a time by checking for existing files and directories.
- **Factory Method**: The ingestion runner script (`ingest_sales_zip.py`) dynamically determines the SQL file to execute based on the directory contents.

#### Dependencies
- **Bash**: The script is written in Bash and relies on Bash built-ins and commands.
- **Python**: The ingestion runner and monitor scripts are written in Python.
- **psql**: The script relies on the `psql` command-line tool for executing SQL files against the PostgreSQL database.
- **watchdog**: The monitor script uses the `watchdog` library for monitoring file system events.

#### Interfaces
- **Ingestion Runner Script**: Exposes a command-line interface for running SQL files against the database.
- **Monitor Script**: Monitors the `Downloads` directory for new zip files and processes them accordingly.

#### Database
- **PostgreSQL**: The ingestion runner script (`ingest_sales_zip.py`) interacts with the PostgreSQL database to execute SQL files.
- **Tables/Labels**: The script does not directly manipulate tables or labels but relies on the SQL files to perform database operations.

#### Configuration
- **Environment Variables**: The script uses `MYTHOS_DB` to specify the database name.
- **Files**: The script writes to and reads from specific files and directories defined in the `MYTHOS_ROOT` environment variable.

#### Key Logic
- **Preflight Checks**: Ensures the Python environment and required files are present.
- **Backup**: Creates a backup of the current monitor script and systemd service file.
- **Directory Management**: Ensures necessary directories exist for ingestion.
- **Ingestion Runner**: Writes and installs a Python script (`ingest_sales_zip.py`) that processes extracted SQL files and executes them against the database.
- **Monitor Upgrade**: Upgrades the monitor script (`mythos_patch_monitor.py`) to support new ingestion types (sales and shoes).

#### Integration Points
- **Systemd Service**: The script ensures the systemd service file is backed up and can be used to manage the monitor script.
- **Watchdog**: The monitor script uses the `watchdog` library to monitor the `Downloads` directory for new zip files.
- **Database Interaction**: The ingestion runner script interacts with the PostgreSQL database to execute SQL files.

### Detailed Analysis of Key Components

#### Ingestion Runner Script (`ingest_sales_zip.py`)
- **Purpose**: Processes extracted SQL files and executes them against the PostgreSQL database.
- **Architecture**: Contains functions for finding and executing SQL files, and a main function that parses command-line arguments.
- **Patterns**: Uses logging for error handling and information tracking.
- **Dependencies**: Relies on `psql` for database interaction.
- **Interfaces**: Exposes a command-line interface for specifying the type of artifact and the extraction directory.
- **Database**: Interacts with the PostgreSQL database to execute SQL files.
- **Configuration**: Uses `MYTHOS_DB` environment variable to specify the database name.
- **Key Logic**: Determines the SQL file to execute based on the directory contents and runs it using `psql`.

#### Monitor Script (`mythos_patch_monitor.py`)
- **Purpose**: Monitors the `Downloads` directory for new zip files and processes them for ingestion.
- **Architecture**: Uses the `watchdog` library to monitor file system events and processes new zip files based on their type.
- **Patterns**: Uses logging for error handling and information tracking.
- **Dependencies**: Relies on `watchdog` for file system monitoring.
- **Interfaces**: Monitors the `Downloads` directory and processes new zip files.
- **Database**: Indirectly interacts with the PostgreSQL database through the ingestion runner script.
- **Configuration**: Uses `MYTHOS_DB` environment variable to specify the database name.
- **Key Logic**: Detects new zip files, processes them based on their type, and runs the ingestion runner script to execute SQL files.

### Summary
This script (`upgrade_sales_ingestion_pipeline.sh`) is a critical component of the Mythos system, ensuring that the sales and shoe ingestion pipeline is upgraded and operational. It performs necessary checks, backups, and installations to ensure the system can process new ingestion types effectively.
