# docker/docker-compose.iris.yml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 87

---

### File: `docker/docker-compose.iris.yml`

#### Purpose
This YAML file defines the Docker Compose configuration for the `iris-core` service, which is the central component of the Mythos system. It orchestrates the container setup, environment variables, and network configurations necessary for the `iris-core` service to interact with other components and services.

#### Architecture
The file is structured using Docker Compose version 3.8 syntax. It defines a single service, `iris-core`, which is built from a Dockerfile located in `../iris/core`. The service is configured to use a custom network `iris-internal` and mounts several volumes to provide persistent storage and access to the host's Docker socket.

#### Patterns
- **Configuration Management**: The use of environment variables and `.env` files to manage configuration.
- **Service Orchestration**: The `iris-core` service is orchestrated to ensure it restarts unless explicitly stopped.

#### Dependencies
- **Environment Variables**: The service relies on environment variables defined in `../.env`.
- **Docker Socket**: Access to the Docker socket (`/var/run/docker.sock`) is required for spawning sandbox containers.
- **Network Configuration**: The `iris-internal` network is used to facilitate communication between services.

#### Interfaces
- **Health Check**: The service exposes a health check endpoint on port `8100`.
- **Volume Mounts**: The service mounts several volumes to provide access to the host's filesystem for the `iris-core` container.

#### Database
- **PostgreSQL**: The `POSTGRES_HOST` and `POSTGRES_PORT` environment variables are configured to connect to PostgreSQL.
- **Neo4j**: The `NEO4J_URI` environment variable is configured to connect to Neo4j.
- **Redis**: The `REDIS_HOST` and `REDIS_PORT` environment variables are configured to connect to Redis.

#### Configuration
- **Environment Variables**: The service reads environment variables from `../.env` and overrides specific variables for internal networking.
- **Volume Paths**: Paths for workshop, sandbox, apps, proposals, and journal are defined.

#### Key Logic
- **Health Check**: The service includes a health check using `curl` to monitor the health of the `iris-core` service.
- **Environment Variable Mapping**: The service maps environment variables from the `.env` file to specific variables expected by `iris-core`.

#### Integration Points
- **PostgreSQL**: The `iris-core` service connects to PostgreSQL for database operations.
- **Neo4j**: The `iris-core` service connects to Neo4j for graph database operations.
- **Redis**: The `iris-core` service connects to Redis for caching and other operations.
- **Ollama**: The `iris-core` service connects to Ollama for AI-related operations.
- **Sandbox Containers**: The `iris-core` service dynamically spawns sandbox containers using the `iris-sandbox:latest` image and connects them to the `iris-internal` network.

### Summary
The `docker-compose.iris.yml` file orchestrates the `iris-core` service, providing it with the necessary environment, network, and volume configurations to interact with other components of the Mythos system. It ensures the service is always running and includes health checks to monitor its status. The service is designed to dynamically spawn sandbox containers and connect to various databases and services for its operations.
