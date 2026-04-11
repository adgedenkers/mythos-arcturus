# telegram_bot/handlers/grid_manifest_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 212

---

### File: `telegram_bot/handlers/grid_manifest_handler.py`

#### Purpose
This file contains the logic for handling the `/grid` command in the Telegram bot, which allows users to inspect the processing manifest for exchanges, view processing stats, and manage version registries.

#### Architecture
The file consists of several asynchronous functions that handle different subcommands of the `/grid` command. The main function `handle_grid` parses the command arguments and delegates to other functions based on the subcommand. Each subcommand function (`_show_last`, `_show_manifest`, `_show_stats`, `_show_versions`, `_show_stale`) performs specific tasks related to querying and displaying data from the PostgreSQL database.

#### Patterns
- **Command Pattern**: The `handle_grid` function acts as a dispatcher for different subcommands, invoking the appropriate handler function based on the user input.
- **Database Access**: Functions like `_show_last` and `_show_manifest` directly interact with the PostgreSQL database to fetch and process data.

#### Dependencies
- **Standard Libraries**: `logging`, `sys`
- **PostgreSQL**: `psycopg2`, `os` (for environment variables)
- **Telegram Bot Framework**: `telegram`, `telegram.ext`
- **Internal Modules**: `grid_manifest` (for `ManifestWriter` and `VersionRegistry`)

#### Interfaces
- **Public Interface**: `handle_grid(update, context)` — This function is called by the Telegram bot framework to handle the `/grid` command.
- **Private Interfaces**: `_show_last(update)`, `_show_manifest(update, exchange_id)`, `_show_stats(update)`, `_show_versions(update)`, `_show_stale(update, node)` — These functions are internal and are called by `handle_grid` based on the subcommand.

#### Database
- **Tables**: `grid_processing_manifest`, `grid_manifest`
- **Operations**: 
  - `grid_processing_manifest`: Queries for the most recent exchange and its manifest.
  - `grid_manifest`: Queries for specific exchange manifests and processing stats.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` — Used to connect to the PostgreSQL database.

#### Key Logic
- **_show_last**: Fetches the most recent exchange manifest from `grid_processing_manifest` and calls `_show_manifest` to display it.
- **_show_manifest**: Fetches and formats the manifest for a specific exchange using `ManifestWriter`.
- **_show_stats**: Fetches and formats processing stats for the last 24 hours using `ManifestWriter`.
- **_show_versions**: Fetches and formats the version registry using `VersionRegistry`.
- **_show_stale**: Fetches and formats exchanges needing reprocessing for a specific node using `VersionRegistry`.

#### Integration Points
- **Telegram Bot Framework**: The file integrates with the Telegram bot framework via the `handle_grid` function, which is called when the `/grid` command is issued.
- **PostgreSQL Database**: The file interacts with the PostgreSQL database to fetch and process data related to grid manifests and processing stats.
- **Internal Modules**: The file uses `grid_manifest` module for accessing manifest and version registry data.

### Detailed Analysis

#### `handle_grid`
- **Purpose**: Dispatches the appropriate subcommand handler based on the user input.
- **Logic**: Parses the command arguments and calls the corresponding subcommand handler (`_show_last`, `_show_manifest`, `_show_stats`, `_show_versions`, `_show_stale`).

#### `_show_last`
- **Purpose**: Displays the manifest for the most recent exchange.
- **Logic**: Connects to the PostgreSQL database, fetches the most recent exchange ID, and calls `_show_manifest` to display the manifest.

#### `_show_manifest`
- **Purpose**: Displays the full manifest for a specific exchange.
- **Logic**: Uses `ManifestWriter` to fetch and format the manifest entries, grouping them by node and layer.

#### `_show_stats`
- **Purpose**: Displays processing stats for the last 24 hours.
- **Logic**: Uses `ManifestWriter` to fetch and format the processing stats.

#### `_show_versions`
- **Purpose**: Displays the version registry.
- **Logic**: Uses `VersionRegistry` to fetch and format the version registry summary.

#### `_show_stale`
- **Purpose**: Displays exchanges needing reprocessing for a specific node.
- **Logic**: Uses `VersionRegistry` to fetch and format the stale exchanges for the specified node.

### Conclusion
This file is a crucial part of the Mythos system, providing a comprehensive interface for users to inspect and manage grid processing manifests via the Telegram bot. It integrates with the PostgreSQL database and internal modules to fetch and format data, ensuring that users can easily access and understand the processing status and version information.
