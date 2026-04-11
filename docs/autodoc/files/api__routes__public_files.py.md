# api/routes/public_files.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 79

---

### File: `api/routes/public_files.py`

#### Purpose
This file provides API endpoints for listing files and directories under `/opt/mythos/public/` and generating a shallow tree structure of the public directory. It is part of the Mythos system's file server functionality.

#### Architecture
The file is structured around FastAPI routes and includes:
- Two top-level asynchronous functions: `list_directory` and `file_tree`.
- A helper function `walk` used by `file_tree` to recursively generate the directory tree.
- The `router` object from FastAPI is used to define the routes.

#### Patterns
- **Decorator Pattern**: The `@router.get` decorators are used to define the HTTP GET endpoints.
- **Helper Function**: The `walk` function is a helper function used within `file_tree` to recursively build the directory tree.

#### Dependencies
- **Imports**: `os`, `time`, `fastapi`, `pathlib`, `typing`.
- **FastAPI**: Uses `APIRouter` and `HTTPException` from FastAPI.
- **Pathlib**: Uses `Path` from `pathlib` for file path operations.

#### Interfaces
- **Endpoints**:
  - `GET /api/public/ls`: Lists files and directories under `/opt/mythos/public/`.
  - `GET /api/public/tree`: Returns a shallow tree of the public directory.

#### Database
- **References**: No direct database references are made in this file. The file operations are handled using `os` and `pathlib`.

#### Configuration
- **Environment Variables**: No environment variables are used directly in this file.
- **Constants**: `PUBLIC_ROOT` is defined as `Path("/opt/mythos/public")`.

#### Key Logic
- **Security**: Ensures that the requested path does not allow traversal outside of the `/opt/mythos/public` directory.
- **Directory Listing**: Lists files and directories, providing metadata such as type, size, and modification time.
- **Tree Generation**: Recursively generates a shallow tree structure of the public directory up to a specified depth.

#### Integration Points
- **FastAPI**: Integrates with FastAPI to provide RESTful endpoints.
- **Command Center**: The JSON directory listings are intended for the Command Center file browser.
- **File Serving**: The actual file serving is handled by FastAPI's `StaticFiles` mount, which is not directly implemented in this file but is referenced.

### Detailed Breakdown

#### `list_directory` Function
- **Purpose**: Lists files and directories under `/opt/mythos/public/`.
- **Parameters**: `path` (optional string representing the subdirectory path).
- **Logic**:
  - Constructs the target path using `PUBLIC_ROOT` and the provided `path`.
  - Ensures the path does not allow traversal outside the public root.
  - Checks if the target exists and is a directory.
  - Iterates over the directory entries, collecting metadata for each file or directory.
  - Returns a JSON response containing the list of items with their metadata.

#### `file_tree` Function
- **Purpose**: Returns a shallow tree of the public directory up to a specified depth.
- **Parameters**: `depth` (integer representing the depth of the tree).
- **Logic**:
  - Uses the `walk` helper function to recursively generate the tree structure.
  - The `walk` function collects metadata for each file and directory, including type, path, URL, and size.
  - Returns a JSON response containing the tree structure.

#### `walk` Function
- **Purpose**: Helper function to recursively generate the directory tree.
- **Parameters**: `p` (path to the current directory), `d` (remaining depth).
- **Logic**:
  - Recursively iterates over the directory entries, collecting metadata for each file or directory.
  - Constructs a tree structure with nodes representing files and directories.

### Summary
This file provides essential functionality for listing and navigating the public directory structure within the Mythos system. It integrates with FastAPI to expose RESTful endpoints and ensures security by preventing directory traversal outside the designated public root.
