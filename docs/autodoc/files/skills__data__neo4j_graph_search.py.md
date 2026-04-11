# skills/data/neo4j_graph_search.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 100

---

### File: `skills/data/neo4j_graph_search.py`

#### Purpose
This file implements a skill (`Neo4jGraphSearchSkill`) for searching the Neo4j graph database to find ontology terms and related nodes based on a search term extracted from a user request.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. The class has several methods:
- `execute`: The main method that processes the request and returns a response.
- `_extract_search_term`: Extracts the search term from the request message.
- `_search_ontology`: Queries the Neo4j graph for ontology terms matching the search term.
- `_search_nodes`: Queries the Neo4j graph for nodes matching the search term.
- `_build_summary`: Builds a summary of the search results (currently a placeholder).

Additionally, there is a top-level function `_get_driver` that initializes the Neo4j driver.

#### Patterns
- **Singleton Pattern**: The `_get_driver` function can be considered a singleton pattern as it initializes and returns a single instance of the Neo4j driver.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the extraction of the search term, searching the ontology and nodes, and building the response.

#### Dependencies
- **Imports**: `os`, `logging`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`, `GraphDatabase`.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system.
- **Internal Methods**: `_extract_search_term`, `_search_ontology`, `_search_nodes`, `_build_summary` are used internally within the class.

#### Database
- **Neo4j Labels**: `OntologyTerm` is used in the ontology search.
- **Neo4j Nodes**: Nodes with labels `Person`, `Soul`, `SpiritualConcept` are queried in the node search.

#### Configuration
- **Environment Variables**: The file reads environment variables from `.env` for Neo4j connection details.
- **Class Attributes**: `name`, `triggers`, `cache_ttl` are defined in the `Neo4jGraphSearchSkill` class.

#### Key Logic
- **Term Extraction**: The `_extract_search_term` method processes the request message to extract a meaningful search term by removing common trigger words.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j graph for ontology terms that contain the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j graph for nodes with specific labels that contain the search term.
- **Response Construction**: The `execute` method constructs the response by combining the results from the ontology and node searches.

#### Integration Points
- **SkillBase**: The class extends `SkillBase`, integrating with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The class uses `SkillRequest` and `SkillResponse` to interact with the request and response objects.
- **Neo4j Driver**: The `_get_driver` function initializes the Neo4j driver, which is used to connect to the Neo4j graph database.

### Detailed Documentation

#### Class: `Neo4jGraphSearchSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: The name of the skill (`'neo4j_graph_search'`).
  - `triggers`: List of trigger words that activate this skill.
  - `cache_ttl`: Time to live for cache (600 seconds).

- **Methods**:
  - **`execute(self, request: SkillRequest) -> SkillResponse`**:
    - **Purpose**: Processes the request and returns a response.
    - **Logic**: Extracts the search term, searches the ontology and nodes, and builds a summary.
    - **Returns**: `SkillResponse` object containing the results and summary.

  - **`_extract_search_term(self, request: SkillRequest) -> str`**:
    - **Purpose**: Extracts the search term from the request message.
    - **Logic**: Removes common trigger words and returns the remaining term.

  - **`_search_ontology(self, term: str) -> list`**:
    - **Purpose**: Queries the Neo4j graph for ontology terms matching the search term.
    - **Logic**: Uses a Cypher query to find ontology terms and returns a list of results.

  - **`_search_nodes(self, term: str) -> list`**:
    - **Purpose**: Queries the Neo4j graph for nodes matching the search term.
    - **Logic**: Uses a Cypher query to find nodes with specific labels and returns a list of results.

  - **`_build_summary(self, results: list) -> str`**:
    - **Purpose**: Builds a summary of the search results.
    - **Logic**: Placeholder method (currently does nothing).

#### Top-Level Functions
- **`_get_driver()`**:
  - **Purpose**: Initializes and returns the Neo4j driver.
  - **Logic**: Uses environment variables to configure the driver.

### Summary
The `neo4j_graph_search.py` file implements a skill for searching the Neo4j graph database based on user requests. It extracts search terms, queries the graph for ontology terms and nodes, and constructs a response summarizing the results. The class integrates with the Mythos skill system and uses the Neo4j driver to connect to the graph database.
