# chunks/CHUNK_CONTRACT.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 73

---

### File: chunks/CHUNK_CONTRACT.json

#### Purpose
This JSON file defines the schema and contract for chunks in the Mythos system, specifying the structure, input/output formats, and dependencies for different types of chunks.

#### Architecture
The file is structured as a JSON object with the following key components:
- `schema_version`: Version of the schema.
- `description`: Description of the contract.
- `chunk_contract`: Defines the general structure of a chunk, including fields like `id`, `name`, `type`, `description`, `input`, `output`, `tables`, `cache_ttl`, and `tags`.
- `chunk_types`: Enumerates specific types of chunks (`db_query`, `text_search`, `format_summary`, `route_intent`, `date_filter`, `rank_results`, `db_write`, `compose`), each with its own description, standard input/output formats, and required dependencies.

#### Patterns
- **Contract Pattern**: The file acts as a contract defining the structure and behavior of chunks.
- **Configuration Pattern**: The file serves as a configuration file that defines the expected structure and behavior of different chunk types.

#### Dependencies
- The file itself does not import or rely on external dependencies directly. However, it specifies dependencies for each chunk type, such as `psycopg2`, `dotenv`, and `dateutil`.

#### Interfaces
- The file exposes a contract that other parts of the Mythos system must adhere to when creating or using chunks. It defines the expected structure and behavior for each chunk type.

#### Database
- The `chunk_contract` specifies that chunks may interact with PostgreSQL tables, as indicated by the `tables` field.
- The `chunk_types` section specifies the PostgreSQL tables and operations (e.g., `db_query`, `db_write`) that certain chunk types interact with.

#### Configuration
- The file itself acts as a configuration file, defining the schema and contract for chunks.
- Environment variables or configuration files are not directly referenced in this JSON file, but the `chunk_types` section specifies dependencies that may require configuration (e.g., `dotenv`).

#### Key Logic
- The file defines the structure and behavior of chunks, which are fundamental building blocks in the Mythos system. Each chunk type has a specific purpose, such as querying the database (`db_query`), performing full-text search (`text_search`), or writing to the database (`db_write`).
- The `chunk_contract` defines the general structure, including input and output formats, which are crucial for interoperability between different chunks and subsystems.

#### Integration Points
- The file integrates with other parts of the Mythos system by defining the structure and behavior of chunks, which are used across various subsystems.
- The `chunk_contract` and `chunk_types` sections define how chunks interact with the database (PostgreSQL), other chunks, and the overall system architecture.

### Detailed Breakdown of Chunk Types

1. **db_query**
   - **Description**: Reads from PostgreSQL, returns structured rows and a summary.
   - **Input**: `message` (str), `parameters` (dict)
   - **Output**: `rows` (list[dict]), `count` (int), `summary` (str)
   - **Dependencies**: `psycopg2`, `dotenv`

2. **text_search**
   - **Description**: Performs full-text search against PostgreSQL tsvector or ILIKE.
   - **Input**: `query` (str), `limit` (int)
   - **Output**: `matches` (list[dict]), `count` (int), `summary` (str)
   - **Dependencies**: `psycopg2`

3. **format_summary**
   - **Description**: Takes structured data and produces a natural language summary.
   - **Input**: `data` (list[dict]), `context` (str)
   - **Output**: `summary` (str)
   - **Dependencies**: None

4. **route_intent**
   - **Description**: Analyzes a message to determine which chunks/stores to query.
   - **Input**: `message` (str)
   - **Output**: `targets` (list[str]), `confidence` (float), `extracted_terms` (list[str])
   - **Dependencies**: None

5. **date_filter**
   - **Description**: Extracts date references from natural language and builds SQL WHERE clauses.
   - **Input**: `message` (str)
   - **Output**: `where_clause` (str), `params` (list), `description` (str)
   - **Dependencies**: `dateutil`

6. **rank_results**
   - **Description**: Scores and sorts results by relevance, recency, or custom criteria.
   - **Input**: `results` (list[dict]), `strategy` (str)
   - **Output**: `ranked` (list[dict]), `top_summary` (str)
   - **Dependencies**: None

7. **db_write**
   - **Description**: Writes to PostgreSQL (INSERT/UPDATE) and returns confirmation.
   - **Input**: `table` (str), `data` (dict), `operation` (str)
   - **Output**: `id` (any), `summary` (str)
   - **Dependencies**: `psycopg2`

8. **compose**
   - **Description**: Chains multiple chunks and passes output forward.
   - **Input**: `steps` (list[dict])
   - **Output**: `combined_data` (dict), `summary` (str)
   - **Dependencies**: None

This JSON file is crucial for ensuring consistency and interoperability across the Mythos system, defining the structure and behavior of chunks that form the core of the system's functionality.
