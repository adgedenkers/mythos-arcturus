# services/mythos-worker-entity.service

**Language:** systemd
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 15

---

### Documentation for `services/mythos-worker-entity.service`

#### 1. Purpose
This systemd service file defines the configuration for the Mythos Entity Resolution Worker, which is responsible for processing entity resolution tasks. It ensures the worker starts after network and database services are up and runs under a specific user with a defined working directory and environment.

#### 2. Architecture
The service file is structured into three main sections:
- **[Unit]**: Contains metadata and dependencies.
- **[Service]**: Defines the runtime environment and execution details.
- **[Install]**: Specifies the conditions under which the service should be started.

#### 3. Patterns
No design patterns are directly applicable here as this is a systemd configuration file, not a code file.

#### 4. Dependencies
- **Systemd**: The service relies on systemd to manage its lifecycle.
- **Network**: The service depends on the network being up (`network.target`).
- **Redis**: The service depends on Redis being available (`redis.service`).
- **PostgreSQL**: The service depends on PostgreSQL being available (`postgresql.service`).

#### 5. Interfaces
This service file does not expose any direct interfaces. It is a configuration file that defines how the `worker.py` script is executed and managed by systemd.

#### 6. Database
The service indirectly interacts with:
- **PostgreSQL**: For data storage and retrieval.
- **Redis**: For caching and task queuing.

#### 7. Configuration
- **Environment Variables**: The `PATH` environment variable is set to include the virtual environment bin directory and system paths.
- **User Configuration**: The service runs as the `adge` user.
- **Working Directory**: The working directory is set to `/opt/mythos`.

#### 8. Key Logic
The service starts the `worker.py` script with the argument `entity`, which likely triggers specific entity resolution logic within the script. The script itself is not detailed here but is expected to handle entity resolution tasks, possibly involving database queries and updates.

#### 9. Integration Points
- **Network**: Ensures the service starts only after the network is up.
- **Redis**: The worker likely uses Redis for task queuing and caching.
- **PostgreSQL**: The worker interacts with PostgreSQL for data storage and retrieval.
- **Worker Script**: The service integrates with the `worker.py` script, which is the main executable for entity resolution tasks.

### Summary
The `mythos-worker-entity.service` systemd file configures the Mythos Entity Resolution Worker to run as a service under the `adge` user, ensuring it starts after the network and required database services are up. It sets the environment and working directory and specifies the script to execute for entity resolution tasks. The service is designed to restart automatically if it fails, with a 10-second delay between restart attempts.
