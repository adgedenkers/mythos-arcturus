# eval/results/neo4j_graph_search/20260305_111100/pass06_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 101

---

### Documentation for `eval/results/neo4j_graph_search/20260305_111100/pass06_attempt04.py`

#### Purpose
This file implements a Neo4j graph search skill (`Neo4jGraphSearchSkill`) that searches for ontology terms and graph nodes based on a user-provided search term. It integrates with a Neo4j database to retrieve relevant information and returns a summary of the search results.

#### Architecture
- **Class**: `Neo4jGraphSearchSkill` inherits from `SkillBase` and includes methods for executing the skill, extracting search terms, searching the ontology, searching nodes, and building a summary.
- **Functions**: 
  - `_get_driver`: Returns a Neo4j driver instance.
  - `execute`: Asynchronous method to execute the skill, handling the search and response generation.
  - `_extract_search_term`: Extracts the search term from the user request.
  - `_search_ontology`: Queries the Neo4j database for ontology terms.
  - `_search_nodes`: Queries the Neo4j database for graph nodes.
  - `_build_summary`: Placeholder for building a summary (currently empty).

#### Patterns
- **Singleton**: The `_get_driver` function acts as a singleton by returning a single instance of the Neo4j driver.
- **Factory**: The `execute` method acts as a factory by creating and returning a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable handling.
  - `logging`: For logging exceptions.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.
  - `GraphDatabase` from `neo4j`: Neo4j driver for database interactions.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_extract_search_term`: Extracts the search term from the request.
  - `_search_ontology`: Queries the ontology terms.
  - `_search_nodes`: Queries the graph nodes.
  - `_build_summary`: Placeholder method for building a summary.

#### Database
- **Neo4j Labels**:
  - `OntologyTerm`: Used in `_search_ontology` to query ontology terms.
  - `Person`, `Soul`, `SpiritualConcept`: Used in `_search_nodes` to query graph nodes.

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for Neo4j authentication.
  - `NEO4J_PASSWORD`: Password for Neo4j authentication.
- **Dotenv File**: `.env` file located in the same directory as the script.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method removes common triggers from the user message and extracts the remaining term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that contain the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes of specific labels that contain the search term.
- **Summary Building**: The `execute` method constructs a summary based on the search results and returns a `SkillResponse`.

#### Integration Points
- **SkillBase Integration**: The `Neo4jGraphSearchSkill` class inherits from `SkillBase` and integrates with the Mythos system through the `execute` method.
- **Neo4j Database**: The skill interacts with the Neo4j database using the `_get_driver` function to retrieve ontology terms and graph nodes.
- **Environment Configuration**: The skill reads environment variables for database connection details from a `.env` file.

This file serves as a critical component of the Mythos system, enabling users to search and retrieve information from a Neo4j graph database based on user-provided terms.
