# iris/core/requirements.txt

**Language:** text
**Stream:** NEU
**Module:** Iris Core
**Lines:** 33

---

### File: iris/core/requirements.txt

#### Purpose
This file lists all the Python dependencies required for the IRIS Core component of the Mythos system. It ensures that all necessary libraries are installed for the system to function correctly.

#### Architecture
The file is a simple text file that lists Python package dependencies in a format recognized by `pip`. Each line specifies a package and its version constraint.

#### Patterns
No design patterns are applicable here as this is a dependency management file.

#### Dependencies
This file does not import anything directly. Instead, it specifies dependencies that need to be installed for the IRIS Core component to function properly.

#### Interfaces
This file does not expose any interfaces. It is used by `pip` to install the necessary packages.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, it lists dependencies for connecting to PostgreSQL (`psycopg2-binary`), Neo4j (`neo4j`), and Redis (`redis`).

#### Configuration
This file does not use any configuration files or environment variables. It is a static list of dependencies.

#### Key Logic
The key logic here is the specification of dependencies. Each package listed is essential for the proper functioning of the IRIS Core component.

#### Integration Points
This file integrates with the broader Mythos system by ensuring that all necessary dependencies are installed. It supports the following subsystems:
- **Async Framework**: `asyncio-mqtt`, `aiohttp`, `aiofiles` for asynchronous operations.
- **Database Connections**: `psycopg2-binary`, `neo4j`, `redis` for connecting to PostgreSQL, Neo4j, and Redis databases.
- **HTTP Client for Ollama**: `httpx`, `requests` for making HTTP requests.
- **Container Management**: `docker` for managing Docker containers.
- **Utilities**: `pydantic`, `python-dateutil`, `pytz` for various utility functions.
- **Telegram Notifications**: `python-telegram-bot` for sending notifications.
- **FastAPI Health Endpoint**: `fastapi`, `uvicorn` for creating a health endpoint.
- **Logging**: `structlog` for structured logging.

### Summary
The `requirements.txt` file is crucial for setting up the IRIS Core component of the Mythos system. It lists all the necessary Python packages and their version constraints, ensuring that the system has all the required dependencies to function correctly. This file is used by `pip` to install the dependencies, and it supports various subsystems including asynchronous operations, database connections, HTTP clients, container management, utility functions, notifications, health endpoints, and logging.
