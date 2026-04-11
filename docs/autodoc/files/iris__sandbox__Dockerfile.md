# iris/sandbox/Dockerfile

**Language:** dockerfile
**Stream:** NEU
**Module:** Iris Core
**Lines:** 34

---

### File: `iris/sandbox/Dockerfile`

#### Purpose
This Dockerfile defines an ephemeral execution environment for running Iris-generated code. It sets up a Python environment with necessary dependencies and a non-root user to execute tasks securely.

#### Architecture
The Dockerfile follows a standard structure for defining a container:
1. **Base Image**: Uses `python:3.11-slim` as the base image.
2. **Labels**: Provides metadata about the container, including maintainer, description, and version.
3. **Dependencies**: Installs Python packages required for executing Iris-generated code.
4. **Workspace**: Sets up a working directory `/workspace` where code will be executed.
5. **User Management**: Creates a non-root user `sandbox` to run the tasks.
6. **Command**: Specifies the default command to execute the task located at `/workspace/task.py`.

#### Patterns
- **Singleton Pattern**: The container is designed to be a singleton instance for each task, ensuring isolation and security.
- **Dependency Injection**: The dependencies are explicitly defined and installed in the Dockerfile.

#### Dependencies
- **Python Packages**: 
  - `pandas>=2.0.0`
  - `numpy>=1.24.0`
  - `psycopg2-binary>=2.9.9`
  - `neo4j>=5.14.0`
  - `redis>=5.0.0`
  - `requests>=2.31.0`
  - `httpx>=0.25.0`
  - `pydantic>=2.5.0`
  - `python-dateutil>=2.8.0`
  - `structlog>=24.1.0`
  - `aiofiles>=23.2.0`

#### Interfaces
- **Entrypoint**: The container expects a Python script (`task.py`) to be mounted at `/workspace/task.py`.
- **Execution**: The container runs the script using the command `python /workspace/task.py`.

#### Database
- **Dependencies**: The Dockerfile includes dependencies for interacting with PostgreSQL (`psycopg2-binary`), Neo4j (`neo4j`), and Redis (`redis`), but does not define specific tables or labels. These dependencies are intended for use by the Iris-generated code.

#### Configuration
- **Environment Variables**: No explicit environment variables are used in the Dockerfile.
- **Labels**: Metadata labels are provided for the container, including maintainer, description, and version.

#### Key Logic
- **Setup**: The Dockerfile sets up a secure, isolated environment for executing code.
- **Execution**: The container is designed to execute a single task (`task.py`) and then terminate.

#### Integration Points
- **Code Execution**: The container is designed to be used as an ephemeral environment for executing Iris-generated code. The code is expected to be mounted at `/workspace/task.py`.
- **Dependencies**: The container includes dependencies for interacting with various data stores (PostgreSQL, Neo4j, Redis), allowing the Iris-generated code to perform database operations.

### Summary
The `Dockerfile` in `iris/sandbox` defines a secure, ephemeral execution environment for running Iris-generated code. It sets up a Python environment with necessary dependencies and a non-root user to ensure security and isolation. The container expects a Python script (`task.py`) to be mounted and executed, making it a flexible and secure environment for code execution within the Mythos system.
