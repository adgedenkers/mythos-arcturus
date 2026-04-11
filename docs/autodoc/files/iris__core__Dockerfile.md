# iris/core/Dockerfile

**Language:** dockerfile
**Stream:** NEU
**Module:** Iris Core
**Lines:** 53

---

### File: `iris/core/Dockerfile`

#### Purpose
This Dockerfile defines the environment and dependencies for the IRIS Core component of the Mythos system, which acts as the central consciousness loop for Iris. It sets up a Python environment with necessary dependencies and configurations for running Iris's core logic.

#### Architecture
The Dockerfile follows a standard structure for defining a container image:
1. **Base Image**: Uses `python:3.11-slim` as the base image.
2. **Labels**: Adds metadata labels for maintainer, description, and version.
3. **System Packages Installation**: Installs `curl` for health checks.
4. **Python Dependencies Installation**: Installs various Python packages using `pip`.
5. **Working Directory**: Sets `/app` as the working directory.
6. **Source Code and Prompts**: Copies the source code and prompts directory into the container.
7. **Port Exposure**: Exposes port 8100 for health checks.
8. **Command**: Specifies the command to run the main entry point of the application.

#### Patterns
- **Containerization**: Uses Docker to package the application and its dependencies.
- **Dependency Management**: Uses `pip` to manage Python dependencies.

#### Dependencies
- **System Packages**: `curl`
- **Python Packages**:
  - `asyncio-throttle`
  - `structlog`
  - `fastapi`
  - `uvicorn`
  - `httpx`
  - `aiohttp`
  - `aiodocker`
  - `asyncpg`
  - `psycopg2-binary`
  - `neo4j`
  - `redis`
  - `pydantic`
  - `python-dateutil`

#### Interfaces
- **Health Check Endpoint**: Exposes port 8100 for health checks.
- **Main Entry Point**: The command `CMD ["python", "-m", "iris.main"]` runs the main entry point of the application.

#### Database
- **PostgreSQL**: Uses `asyncpg` and `psycopg2-binary` for PostgreSQL interactions.
- **Neo4j**: Uses `neo4j` for Neo4j interactions.
- **Redis**: Uses `redis` for Redis interactions.

#### Configuration
- **Environment Variables**: No explicit environment variables are set in the Dockerfile, but the application might use environment variables for configuration.
- **Prompts Directory**: Copies the `prompts` directory into the container, which contains identity and operational instructions for Iris.

#### Key Logic
- **Main Entry Point**: The `iris.main` module is the entry point of the application, likely containing the main loop and initialization logic for Iris.
- **Health Check**: The application likely includes a health check endpoint on port 8100 to monitor the status of the IRIS Core.

#### Integration Points
- **Web Framework**: Uses `FastAPI` and `Uvicorn` for handling HTTP requests, likely for the health check endpoint.
- **Database Clients**: Integrates with PostgreSQL, Neo4j, and Redis for data storage and retrieval.
- **HTTP Clients**: Uses `httpx` and `aiohttp` for making HTTP requests, possibly for integrating with other services.
- **Docker Client**: Uses `aiodocker` for managing Docker containers, likely for sandbox execution.

### Summary
This Dockerfile sets up the IRIS Core component of the Mythos system, defining a Python environment with necessary dependencies and configurations. It includes health check functionality and integrates with various databases and HTTP services, making it a crucial part of the Mythos infrastructure.
