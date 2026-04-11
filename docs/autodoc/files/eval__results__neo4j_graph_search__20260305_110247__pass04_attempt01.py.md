# eval/results/neo4j_graph_search/20260305_110247/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 148

---

### File: eval/results/neo4j_graph_search/20260305_110247/pass04_attempt01.py

#### Purpose
This file implements a Neo4j graph search skill that extracts search terms from user queries, searches for ontology terms and nodes in a Neo4j database, and builds a summary of the results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_term`: Extracts a meaningful search term from the user query.
- `_search_ontology`: Searches for ontology terms in the Neo4j database.
- `_search_nodes`: Searches for nodes in the Neo4j database.
- `_build_summary`: Builds a summary of the search results.

Additionally, there is a top-level function `_get_driver` to initialize the Neo4j driver.

#### Patterns
- **Singleton**: The `_get_driver` function can be considered a singleton pattern as it returns a single instance of the Neo4j driver.
- **Factory**: The `execute` method acts as a factory method, orchestrating the extraction, search, and summary building processes.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `neo4j`, `engine.base`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` loaded from `.env` file.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_extract_search_term`: Extracts a search term from the query.
  - `_search_ontology`: Searches ontology terms.
  - `_search_nodes`: Searches nodes.
  - `_build_summary`: Builds a summary of the results.

#### Database
- **Neo4j Labels**: `OntologyTerm`, `Person`, `Soul`, `SpiritualConcept`
- **PostgreSQL Tables**: `dotenv`, `engine`, `neo4j`, `your` (likely used for configuration or other purposes)

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are loaded from the `.env` file.
- **Class Attributes**: `name`, `triggers`, `cache_ttl` are defined in the `Neo4jGraphSearchSkill` class.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method removes specific triggers and normalizes the query to extract a meaningful search term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that contain the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes with labels `Person`, `Soul`, `SpiritualConcept` that contain the search term.
- **Summary Building**: The `_build_summary` method constructs a summary of the search results.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class inherits from `SkillBase`, indicating it integrates with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method uses `SkillRequest` and `SkillResponse` classes, indicating integration with the Mythos request/response handling system.
- **Neo4j Driver**: The `_get_driver` function initializes the Neo4j driver, which is used to interact with the Neo4j database.

### Summary
This file implements a Neo4j graph search skill that processes user queries, searches for ontology terms and nodes in a Neo4j database, and builds a summary of the results. It integrates with the Mythos skill system and uses environment variables for configuration.
