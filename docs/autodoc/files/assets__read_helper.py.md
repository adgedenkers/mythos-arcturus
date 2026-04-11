# assets/read_helper.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 84

---

### File: assets/read_helper.py

#### Purpose
This file contains helper functions to resolve image paths for clothing and shoe items by querying PostgreSQL tables and constructing file paths based on the retrieved data.

#### Architecture
The file consists of three main functions:
1. `_conn`: A utility function to establish a connection to the PostgreSQL database.
2. `resolve_clothing_images`: Resolves image paths for clothing items by querying the `clothing_images` table.
3. `resolve_shoe_images`: Resolves image paths for shoe items by querying the `shoe_images` table.

Each function follows a similar pattern of connecting to the database, executing a query, and processing the results to construct the resolved paths.

#### Patterns
- **Utility Function**: `_conn` acts as a utility function to manage database connections.
- **Data Access Object (DAO)**: The functions `resolve_clothing_images` and `resolve_shoe_images` can be considered as simple DAOs that encapsulate the logic for accessing and processing data from the database.

#### Dependencies
- `os`: Used to access environment variables.
- `psycopg2`: Used to connect to and query the PostgreSQL database.
- `pathlib.Path`: Used to construct and manipulate file paths.

#### Interfaces
- `resolve_clothing_images(item_id: str)`: Exposes a function to resolve clothing image paths given an item ID.
- `resolve_shoe_images(item_id: str)`: Exposes a function to resolve shoe image paths given an item ID.

#### Database
- **Tables**: 
  - `clothing_images`: Contains columns `filename`, `original_filename`, `view_type`, `batch_name`, and `asset_rel_path`.
  - `shoe_images`: Contains columns `filename`, `original_filename`, `view_type`, `batch_name`, and `asset_rel_path`.

#### Configuration
- Environment variables:
  - `MYTHOS_DB`: Specifies the PostgreSQL database name.
- Constants:
  - `ASSETS_ROOT`: Base directory for asset files.
  - `SALES_ROOT`: Base directory for sales ingestion files.
  - `SHOE_ROOT`: Base directory for shoe ingestion files.

#### Key Logic
- **Database Query Execution**: Both `resolve_clothing_images` and `resolve_shoe_images` execute a query to fetch image details from the respective tables.
- **Path Resolution**: The functions resolve the image paths based on the `asset_rel_path` or `batch_name` retrieved from the database. If `asset_rel_path` is present, it constructs the path directly from the assets root directory. If not, it constructs the path from the batch name directory.

#### Integration Points
- **Database Integration**: The functions interact with the PostgreSQL database to fetch image details.
- **File System Integration**: The functions construct file paths based on the retrieved data and predefined root directories.
- **API Integration**: These functions can be called by other parts of the Mythos system to resolve image paths for clothing and shoe items.

### Detailed Documentation

#### `_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `psycopg2`
- **Logic**: Uses the `MYTHOS_DB` environment variable to connect to the database.

#### `resolve_clothing_images`
- **Purpose**: Resolves image paths for clothing items.
- **Dependencies**: `_conn`, `psycopg2`, `pathlib.Path`
- **Logic**:
  - Connects to the database.
  - Executes a query to fetch image details from the `clothing_images` table.
  - Constructs resolved paths based on `asset_rel_path` or `batch_name`.
  - Returns a list of dictionaries containing image details and resolved paths.

#### `resolve_shoe_images`
- **Purpose**: Resolves image paths for shoe items.
- **Dependencies**: `_conn`, `psycopg2`, `pathlib.Path`
- **Logic**:
  - Connects to the database.
  - Executes a query to fetch image details from the `shoe_images` table.
  - Constructs resolved paths based on `asset_rel_path` or `batch_name`.
  - Returns a list of dictionaries containing image details and resolved paths.

### Example Usage
```python
from assets.read_helper import resolve_clothing_images, resolve_shoe_images

# Resolve clothing images for item ID '123'
clothing_images = resolve_clothing_images('123')
print(clothing_images)

# Resolve shoe images for item ID '456'
shoe_images = resolve_shoe_images('456')
print(shoe_images)
```

This file is integral to the Mythos system for managing and resolving image paths for clothing and shoe items, ensuring that the correct images are retrieved based on the item ID and database records.
