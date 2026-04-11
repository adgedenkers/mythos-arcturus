# services/mythos-worker-lunar.service

**Language:** systemd
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 19

---

### Documentation for `services/mythos-worker-lunar.service`

#### 1. Purpose
The `mythos-worker-lunar.service` is a systemd service file that configures and manages the execution of the `lunar_calendar_worker.py` script, which auto-generates Seraphe's monthly transit calendar.

#### 2. Architecture
- **Systemd Unit**: The file is structured as a systemd unit file, which is used to define the service's behavior and dependencies.
- **Service Configuration**: The service runs as a simple type, specifying the user (`adge`), group (`adge`), working directory (`/opt/mythos`), and the command to execute (`/opt/mythos/.venv/bin/python3 /opt/mythos/workers/lunar_calendar_worker.py`).

#### 3. Patterns
- **N/A**: This is a systemd service file and does not employ any design patterns as it is a configuration file rather than a code file.

#### 4. Dependencies
- **Systemd Targets**: The service depends on `network.target` and `mythos-api.service`.
- **Environment Variables**: The service sets the `PYTHONPATH` environment variable to `/opt/mythos`.
- **Executable**: The service relies on the Python interpreter located at `/opt/mythos/.venv/bin/python3`.

#### 5. Interfaces
- **N/A**: This systemd service file does not expose any interfaces. It is a configuration file that defines how the service should be run.

#### 6. Database
- **N/A**: The systemd service file does not directly interact with any databases. However, the `lunar_calendar_worker.py` script it runs may interact with databases.

#### 7. Configuration
- **Environment Variables**: The service sets the `PYTHONPATH` environment variable to `/opt/mythos`.
- **Systemd Configuration**: The service is configured to restart on failure with a delay of 60 seconds.

#### 8. Key Logic
- **N/A**: The key logic is contained within the `lunar_calendar_worker.py` script, which is executed by this service. The service file itself does not contain any logic.

#### 9. Integration Points
- **Systemd**: The service integrates with systemd to manage its lifecycle.
- **Mythos API**: The service depends on the `mythos-api.service` being available, indicating that it likely interacts with the Mythos API to fetch or update data.
- **Python Environment**: The service uses a virtual environment located at `/opt/mythos/.venv` to run the Python script.

### Summary
The `mythos-worker-lunar.service` systemd unit file is responsible for managing the execution of the `lunar_calendar_worker.py` script, which auto-generates Seraphe's monthly transit calendar. It ensures the script runs within the appropriate environment and handles restarts on failure. The service depends on the network and the Mythos API being available.
