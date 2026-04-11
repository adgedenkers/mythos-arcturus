# eval/results/neo4j_graph_search/20260305_110247/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 166

---

### Documentation for `pass05_attempt01.py`

#### Purpose
This file implements a Neo4j graph search skill (`Neo4jGraphSearchSkill`) that processes user queries to search for ontology terms and graph nodes in a Neo4j database. It extracts search terms from the query, performs searches, and builds a summary of the results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. The class has several methods for different stages of the search process:
- `_extract_search_term`: Extracts the search term from the query.
- `_search_ontology`: Searches for ontology terms in the Neo4j database.
- `_search_nodes`: Searches for graph nodes in the Neo4j database.
- `_build_summary`: Builds a summary of the search results.
- `execute`: The main method that orchestrates the search process and returns the results.

Additionally, there are top-level functions:
- `_get_driver`: Returns a Neo4j driver instance.
- `execute`: A top-level function that wraps the class method for execution.

#### Patterns
- **Singleton Pattern**: The `_get_driver` function ensures a single instance of the Neo4j driver is used.
- **Factory Method**: The `_get_driver` function acts as a factory method to create and return a Neo4j driver instance.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.
- `neo4j`: For interacting with the Neo4j database.

#### Interfaces
- **`execute`**: The main entry point for the skill, which takes a `SkillRequest` and returns a `SkillResponse`.
- **`_extract_search_term`**: Extracts the search term from the query.
- **`_search_ontology`**: Searches for ontology terms in the Neo4j database.
- **`_search_nodes`**: Searches for graph nodes in the Neo4j database.
- **`_build_summary`**: Builds a summary of the search results.

#### Database
- **Neo4j**: 
  - **Label**: `OntologyTerm` (used in `_search_ontology`).
  - **Nodes**: Nodes with labels `Person`, `Soul`, `SpiritualConcept` (used in `_search_nodes`).

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Dotenv File**: `/opt/mythos/.env` is loaded to provide these environment variables.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method removes specific triggers and normalizes the query to extract the search term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that match the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes with specific labels that match the search term.
- **Summary Building**: The `_build_summary` method constructs a summary of the search results.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class extends `SkillBase`, integrating with the Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request/response model.
- **Neo4j**: The `_get_driver` function and search methods integrate with the Neo4j database to perform searches and retrieve results.

This file is a critical component of the Mythos system, enabling users to search for ontology terms and graph nodes within the Neo4j database, and providing a structured response with the search results.
