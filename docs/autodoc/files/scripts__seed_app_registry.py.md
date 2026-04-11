# scripts/seed_app_registry.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 51

---

### File: scripts/seed_app_registry.py

#### Purpose
This script seeds the Neo4j database with `AppRegistry` nodes, ensuring that the application registry is synchronized with the database. It is intended to be run once after installation or anytime to re-sync the registry.

#### Architecture
The script consists of a single `main` function that handles the entire process of connecting to the Neo4j database, seeding the `AppRegistry` nodes, and generating an audit report. The script uses environment variables for database connection details and leverages the `AppRegistry` class from the `core.app_registry` module to perform the seeding.

#### Patterns
- **Singleton Pattern**: The `AppRegistry` class likely follows the Singleton pattern to ensure that only one instance of the registry exists.
- **Dependency Injection**: The `AppRegistry` class is initialized with the `neo4j_driver` as a dependency, promoting loose coupling.

#### Dependencies
- **Standard Library**: `os`, `sys`
- **Neo4j Driver**: `GraphDatabase` from `neo4j`
- **Custom Module**: `AppRegistry` from `core.app_registry`

#### Interfaces
- **Main Function**: The `main` function serves as the entry point for the script. It does not expose any public API but is designed to be executed directly.

#### Database
- **Neo4j**: The script interacts with Neo4j to seed `AppRegistry` nodes.
- **Postgres**: The `AppRegistry` class may interact with the `core` PostgreSQL database to fetch application metadata.

#### Configuration
- **Environment Variables**: 
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.

#### Key Logic
1. **Database Connection**: Establishes a connection to the Neo4j database using the provided credentials.
2. **Verification**: Verifies the connection by running a simple query.
3. **Seeding**: Uses the `AppRegistry` class to seed the Neo4j database with `AppRegistry` nodes.
4. **Audit Report**: Generates and prints an audit report to verify the seeding process.

#### Integration Points
- **Neo4j Driver**: The script uses the `GraphDatabase.driver` to connect to Neo4j.
- **AppRegistry Class**: The `AppRegistry` class from `core.app_registry` is used to seed the Neo4j database and generate audit reports.

### Detailed Breakdown

#### `main` Function
- **Purpose**: Orchestrates the seeding process by connecting to Neo4j, verifying the connection, seeding the registry, and generating an audit report.
- **Flow**:
  1. Retrieves database connection details from environment variables.
  2. Establishes a connection to Neo4j using `GraphDatabase.driver`.
  3. Verifies the connection by running a simple query.
  4. Initializes the `AppRegistry` class with the Neo4j driver.
  5. Calls the `seed_neo4j` method to seed the registry.
  6. Generates and prints an audit report.
  7. Closes the Neo4j driver connection.

#### Environment Variables
- **NEO4J_URI**: Specifies the URI for the Neo4j database.
- **NEO4J_USER**: Specifies the username for the Neo4j database.
- **NEO4J_PASSWORD**: Specifies the password for the Neo4j database.

#### AppRegistry Class
- **Initialization**: The `AppRegistry` class is initialized with the `neo4j_driver` as a dependency.
- **Methods**:
  - `seed_neo4j()`: Seeds the Neo4j database with `AppRegistry` nodes.
  - `format_audit_report()`: Generates an audit report to verify the seeding process.

### Example Usage
To run the script, execute the following command:
```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/scripts/seed_app_registry.py
```

This script ensures that the `AppRegistry` nodes are correctly seeded in the Neo4j database, providing a crucial step in maintaining the integrity of the Mythos system's application registry.
