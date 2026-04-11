# neuro/grid_manifest/manifest_writer.py

**Language:** python
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 275

---

### File: `neuro/grid_manifest/manifest_writer.py`

#### Purpose
This file contains the `ManifestWriter` class and several top-level functions to record and retrieve manifest entries for grid processing activities in the Mythos system. It primarily interacts with a PostgreSQL database to log activations, skips, and legacy activations of nodes and layers.

#### Architecture
- **Classes**: 
  - `ManifestWriter`: A class responsible for recording and retrieving manifest entries from the PostgreSQL database.
- **Methods**:
  - `record_activation`: Records an activation event.
  - `record_skip`: Records a skip event.
  - `record_legacy_activation`: Records legacy activation events.
  - `get_exchange_manifest`: Retrieves the full manifest for a specific exchange.
  - `get_processing_stats`: Retrieves processing statistics for the last N hours.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `record_activation`: Top-level function to record an activation event.
  - `record_skip`: Top-level function to record a skip event.
  - `record_legacy_activation`: Top-level function to record legacy activation events.
  - `get_exchange_manifest`: Top-level function to retrieve the full manifest for a specific exchange.
  - `get_processing_stats`: Top-level function to retrieve processing statistics for the last N hours.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection object is returned.
- **Factory**: The `ManifestWriter` class acts as a factory for creating and managing manifest entries.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `hashlib`: For generating hashes.
  - `logging`: For logging messages.
  - `psycopg2`: For PostgreSQL database interaction.
  - `typing`: For type hints.
  - `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- **Public Methods**:
  - `record_activation`: Records an activation event.
  - `record_skip`: Records a skip event.
  - `record_legacy_activation`: Records legacy activation events.
  - `get_exchange_manifest`: Retrieves the full manifest for a specific exchange.
  - `get_processing_stats`: Retrieves processing statistics for the last N hours.

#### Database
- **Tables**:
  - `grid_processing_manifest`: Used for recording activation, skip, and legacy activation events.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured via `.env` file.
- **Configuration File**:
  - `/opt/mythos/.env`: Used to load environment variables.

#### Key Logic
- **Record Activation**:
  - Hashes input content if provided.
  - Inserts a new row into `grid_processing_manifest` with details of the activation.
- **Record Skip**:
  - Inserts a new row into `grid_processing_manifest` with details of the skip.
- **Record Legacy Activation**:
  - Iterates over a list of nodes and records each as a legacy activation.
- **Get Exchange Manifest**:
  - Retrieves all records from `grid_processing_manifest` for a given exchange ID.
- **Get Processing Stats**:
  - Retrieves aggregate statistics from `grid_processing_manifest` for the last N hours.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Interacts with PostgreSQL to store and retrieve manifest entries.
  - **Logging**: Uses the `logging` module to log important events and errors.
  - **Environment Configuration**: Relies on environment variables for database connection details.

This file serves as a critical component of the Mythos system, ensuring that all processing activities are logged and can be audited or analyzed later.
