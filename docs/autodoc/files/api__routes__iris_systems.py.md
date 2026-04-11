# api/routes/iris_systems.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 113

---

### File: api/routes/iris_systems.py

#### Purpose
This file serves as a FastAPI router for handling requests related to Iris systems data. It provides endpoints for loading, summarizing, and updating system statuses from a JSON file.

#### Architecture
The file is structured around a FastAPI router (`router`) and includes several top-level functions and a Pydantic model (`StatusUpdate`). The primary functions are:
- `load_systems`: Loads the systems data from a JSON file.
- `save_systems`: Saves updated systems data back to the JSON file.
- `get_systems`: Retrieves and returns the full systems data.
- `get_systems_summary`: Provides a summary of system statuses and categories.
- `update_system_status`: Updates the status of a specific system.

#### Patterns
- **Pydantic Model**: `StatusUpdate` is a Pydantic model used to validate and parse the incoming status update request.
- **FastAPI Router**: The `router` object is used to define the API endpoints.

#### Dependencies
- `json`: For parsing and writing JSON data.
- `pathlib`: For file path handling.
- `datetime`: For date handling.
- `fastapi`: For defining the API router and handling HTTP requests.
- `pydantic`: For defining the `StatusUpdate` model.

#### Interfaces
- **Endpoints**:
  - `GET /api/iris/systems`: Returns full systems data.
  - `GET /api/iris/systems/summary`: Returns a summary of system statuses and categories.
  - `POST /api/iris/systems/update`: Updates the status of a specific system.

#### Database
- The file does not directly interact with a database. It reads from and writes to a JSON file located at `/opt/mythos/docs/iris_systems.json`.

#### Configuration
- The file uses a constant `SYSTEMS_FILE` to define the path to the JSON file containing the systems data.

#### Key Logic
- **Loading and Saving Systems Data**:
  - `load_systems`: Reads the JSON file and returns the data.
  - `save_systems`: Updates the JSON file with new data, including the current date as the last updated timestamp.
- **Summarizing Systems Data**:
  - `get_systems_summary`: Iterates through the systems data to count statuses and categorize them, returning a summary.
- **Updating System Status**:
  - `update_system_status`: Validates the new status, updates the system status in the JSON data, and saves the changes.

#### Integration Points
- The file integrates with the FastAPI framework to define and handle API endpoints.
- It interacts with the filesystem to read from and write to the `iris_systems.json` file.
- The `StatusUpdate` model is used to validate incoming POST requests for updating system statuses.

### Summary
This file is a crucial part of the Mythos system, providing API endpoints to manage and retrieve Iris systems data. It leverages FastAPI for routing and Pydantic for data validation, ensuring robust and reliable data handling. The file reads from and writes to a JSON file, making it easy to manage system statuses and provide summaries.
