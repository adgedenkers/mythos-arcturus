# api/routes/system.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 194

---

### File: api/routes/system.py

#### Purpose
This file provides API endpoints to retrieve the system status, including uptime, service statuses, CPU, memory, disk, GPU information, database connectivity, and recent patches.

#### Architecture
The file is structured around a set of utility functions that gather various system metrics and a FastAPI route that aggregates these metrics into a comprehensive system status response. The utility functions are designed to be modular and reusable.

- **Utility Functions**: Functions like `run_cmd`, `check_service`, `get_uptime`, `get_cpu`, `get_memory`, `get_disk`, `get_gpu`, `get_databases`, `get_patches`, and `get_last_patch` are used to gather specific system information.
- **Main Route**: The `system_status` function aggregates the results from the utility functions and returns them in a JSON response.

#### Patterns
- **Utility Functions**: Each function is designed to perform a specific task and return the result, adhering to the Single Responsibility Principle.
- **Aggregation**: The `system_status` function acts as an orchestrator, calling multiple utility functions and combining their results.

#### Dependencies
- **Standard Libraries**: `os`, `subprocess`, `logging`, `datetime`, `pathlib`
- **Third-party Libraries**: `fastapi`, `fastapi.responses`

#### Interfaces
- **FastAPI Route**: 
  - `@router.get("/status")`: Returns the full system status as a JSON response.

#### Database
- **PostgreSQL**:
  - Tables: `information_schema.tables`, `mythos` (for database connectivity checks)
- **Neo4j**: 
  - No specific tables/labels, but connectivity is checked via HTTP.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **System Metrics Collection**: 
  - `run_cmd`: Executes shell commands and captures their output.
  - `check_service`: Checks the status of systemd services.
  - `get_uptime`: Retrieves system uptime.
  - `get_cpu`: Retrieves CPU information, including core count, load average, and usage percentage.
  - `get_memory`: Retrieves memory usage statistics.
  - `get_disk`: Retrieves disk usage statistics for the root filesystem.
  - `get_gpu`: Retrieves GPU information using `nvidia-smi`.
  - `get_databases`: Checks connectivity to PostgreSQL and Neo4j databases.
  - `get_patches`: Retrieves recent patches from git tags.
  - `get_last_patch`: Retrieves the name of the most recent patch.

- **Aggregation**:
  - `system_status`: Aggregates all the collected metrics and returns them in a JSON response.

#### Integration Points
- **System Metrics**: The utility functions interact with the system via shell commands and file I/O.
- **Database Connectivity**: The `get_databases` function checks connectivity to PostgreSQL and Neo4j.
- **Git Repository**: The `get_patches` function interacts with the local Git repository to retrieve recent patches.
- **FastAPI**: The `system_status` function is integrated with FastAPI to expose the system status as an API endpoint.

### Summary
This file serves as a comprehensive system status endpoint for the Mythos system, providing detailed information about the system's health, including service statuses, resource usage, and recent patches. It leverages shell commands and database connectivity checks to gather the necessary data and exposes this information via a FastAPI route.
