# eval/results/neo4j_graph_search/20260305_111100/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 98

---

### Documentation for `eval/results/neo4j_graph_search/20260305_111100/final.py`

#### Purpose
This file implements a Neo4j graph search skill that allows users to search for ontology terms and graph nodes based on a provided search term. It integrates with the Neo4j database to execute queries and returns the results in a structured format.

#### Architecture
The file consists of a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. The class contains several methods to handle different aspects of the search process:
- `_extract_search_term`: Extracts the search term from the request.
- `_search_ontology`: Queries the Neo4j database for ontology terms.
- `_search_nodes`: Queries the Neo4j database for graph nodes.
- `_build_summary`: Builds a summary of the search results (currently empty).

Additionally, there are top-level functions:
- `_get_driver`: Returns a Neo4j driver instance.
- `execute`: Asynchronous method to execute the search and return the response.

#### Patterns
- **Singleton**: The `_get_driver` function acts as a singleton by returning a single instance of the Neo4j driver.
- **Factory**: The `execute` method acts as a factory to create and return a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `dotenv`, `engine.base`, `neo4j`.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

#### Interfaces
- **Public Methods**: `execute` is the main public method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**: `_extract_search_term`, `_search_ontology`, `_search_nodes`, `_build_summary`.

#### Database
- **Neo4j Labels**: `OntologyTerm` is used in the ontology search.
- **Neo4j Nodes**: Nodes with labels `Person`, `Soul`, `SpiritualConcept` are queried in the node search.

#### Configuration
- **Config Files**: `.env` file is loaded using `dotenv` to set environment variables.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

#### Key Logic
- **Term Extraction**: The `_extract_search_term` method removes common trigger words and filters out short words to form a meaningful search term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that contain the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes with specific labels that contain the search term.
- **Summary Building**: The `_build_summary` method is currently empty but is intended to build a summary of the search results.

#### Integration Points
- **SkillBase Integration**: The `Neo4jGraphSearchSkill` class inherits from `SkillBase` and integrates with the Mythos skill system.
- **Neo4j Integration**: The `_get_driver` function and methods `_search_ontology` and `_search_nodes` interact with the Neo4j database to execute queries and retrieve results.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse` objects, integrating with the Mythos request-response system.

### Detailed Breakdown

#### `_get_driver` Function
- **Purpose**: Returns a Neo4j driver instance.
- **Logic**: Uses environment variables to configure the driver and returns a single instance.

#### `Neo4jGraphSearchSkill` Class
- **Attributes**: `name`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Asynchronous method to execute the search and return a `SkillResponse`.
  - `_extract_search_term`: Extracts the search term from the request.
  - `_search_ontology`: Queries the Neo4j database for ontology terms.
  - `_search_nodes`: Queries the Neo4j database for graph nodes.
  - `_build_summary`: Placeholder method to build a summary of the search results.

#### Top-Level Functions
- **Purpose**: Support the main class methods.
- **Logic**: `_get_driver` provides a singleton Neo4j driver instance, while other methods handle specific parts of the search process.

This file is a crucial component of the Mythos system, enabling users to search and retrieve information from the Neo4j graph database efficiently.
