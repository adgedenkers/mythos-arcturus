# services/mythos-seismic-ingest.service

**Language:** systemd
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 19

---

### Documentation for `services/mythos-seismic-ingest.service`

#### Purpose
This systemd service file defines the configuration for the Mythos Earthquake Ingestion Service, which is responsible for ingesting seismic data and processing it for further analysis within the Mythos system.

#### Architecture
The service file is structured into three main sections:
1. **[Unit]**: Provides metadata and dependencies for the service.
2. **[Service]**: Defines the runtime configuration for the service, including the command to start the service, user and group permissions, working directory, and restart policy.
3. **[Install]**: Specifies the target to which the service should be linked for automatic startup.

#### Patterns
- **Dependency Management**: The service specifies dependencies on the network and PostgreSQL services, ensuring that these services are up and running before the seismic ingestion service starts.
- **Restart Policy**: The service is configured to restart automatically if it fails, with a 30-second delay before the next restart attempt.

#### Dependencies
- **Network Service**: The service depends on the network being up.
- **PostgreSQL Service**: The service depends on PostgreSQL being available.
- **Python Environment**: The service uses a Python virtual environment located at `/opt/mythos/.venv`.

#### Interfaces
- **Standard Output and Error**: Redirected to the systemd journal for logging.
- **Environment Variable**: `PYTHONPATH` is set to `/opt/mythos` to ensure the Python interpreter can find the necessary modules.

#### Database
- **PostgreSQL**: The service likely interacts with PostgreSQL to store and manage seismic data. Specific tables or schemas are not explicitly mentioned in the service file but can be inferred from the service's purpose.

#### Configuration
- **Environment Variables**: The service sets the `PYTHONPATH` environment variable.
- **User and Group**: The service runs as the user and group `adge`.

#### Key Logic
- **Seismic Data Ingestion**: The service executes the Python script `/opt/mythos/observatory/ingest/seismic_ingest.py`, which contains the logic for ingesting and processing seismic data. This script likely handles data acquisition, validation, and storage in the PostgreSQL database.

#### Integration Points
- **PostgreSQL**: The service integrates with the PostgreSQL database to store seismic data.
- **Systemd**: The service is managed by systemd, which handles its lifecycle, including startup, restarts, and logging.

### Summary
The `mythos-seismic-ingest.service` file configures a systemd service that runs a Python script to ingest and process seismic data. It ensures the service starts after the network and PostgreSQL services are up, runs as a specific user, and logs output to the systemd journal. The service is designed to restart automatically if it fails, ensuring continuous operation. The script itself handles the core logic of data ingestion and storage in PostgreSQL.
