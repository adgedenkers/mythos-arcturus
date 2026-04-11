# photos/docker-compose.yml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 67

---

### File: `photos/docker-compose.yml`

#### Purpose
This YAML file defines the Docker Compose configuration for the Immich photo management service, including the Immich server, machine learning service, Redis, and PostgreSQL database. It sets up the necessary environment variables, volumes, and health checks for each service.

#### Architecture
The file is structured into several services, each defining a Docker container with specific configurations:
- `immich-server`: The main Immich server container.
- `immich-machine-learning`: The machine learning service container.
- `redis`: The Redis container for caching.
- `database`: The PostgreSQL container for database storage.

#### Patterns
- **Service Dependency**: The `immich-server` service depends on the `database` and `redis` services being healthy before starting.
- **Environment Configuration**: Uses environment files and variables to configure services dynamically.

#### Dependencies
- **Docker Images**:
  - `ghcr.io/immich-app/immich-server:release`
  - `ghcr.io/immich-app/immich-machine-learning:release`
  - `docker.io/redis:6.2-alpine`
  - `docker.io/tensorchord/pgvecto-rs:pg14-v0.2.0`
- **Environment Files**:
  - `/opt/mythos/photos/.env`
- **Volumes**:
  - `/opt/photos/library` for uploads
  - `/opt/photos/pgdata` for PostgreSQL data
  - `model-cache` for machine learning model cache

#### Interfaces
- **Environment Variables**: Exposes environment variables for configuration (e.g., `DB_HOSTNAME`, `REDIS_HOSTNAME`, `POSTGRES_PASSWORD`).
- **Ports**: Exposes port `2283` for the Immich server.

#### Database
- **PostgreSQL**:
  - **Environment Variables**: `POSTGRES_PASSWORD`, `POSTGRES_USER`, `POSTGRES_DB`
  - **Volumes**: `/opt/photos/pgdata` for data storage
  - **Health Check**: Uses `pg_isready` to check the database health
- **Redis**:
  - **Health Check**: Uses `redis-cli ping` to check the Redis health

#### Configuration
- **Environment File**: `/opt/mythos/photos/.env` contains environment variables for configuration.
- **Environment Variables**: Used for setting up database and Redis connections.

#### Key Logic
- **Health Checks**: Ensures services are healthy before starting dependent services.
- **Volume Mounts**: Ensures data persistence for uploads and PostgreSQL data.

#### Integration Points
- **Immich Server**: Integrates with Redis for caching and PostgreSQL for database storage.
- **Machine Learning Service**: Integrates with Redis for caching and uses a volume for model cache.
- **Database and Redis**: Provide backend services for the Immich server and machine learning service.

### Summary
This `docker-compose.yml` file sets up a comprehensive Docker environment for the Immich photo management system, including the server, machine learning service, Redis, and PostgreSQL database. It ensures that all services are properly configured, healthy, and integrated, with specific volumes and environment variables for dynamic configuration.
