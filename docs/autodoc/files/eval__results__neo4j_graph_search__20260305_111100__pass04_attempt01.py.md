# eval/results/neo4j_graph_search/20260305_111100/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 74

---

### Documentation for `eval/results/neo4j_graph_search/20260305_111100/pass04_attempt01.py`

#### Purpose
This file implements a Neo4j-based graph search skill for the Mythos system, allowing users to search for ontology terms and related nodes within the Neo4j database.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` which inherits from `SkillBase`. The class has several methods to handle different aspects of the search process:
- `_extract_search_term`: Extracts the search term from the user request.
- `_search_ontology`: Searches for ontology terms in the Neo4j database.
- `_search_nodes`: Searches for nodes (e.g., Person, Soul, SpiritualConcept) in the Neo4j database.
- `_build_summary`: Builds a summary of the search results.
- `execute`: The main entry point for the skill, which orchestrates the search process.

Additionally, there are top-level functions:
- `_get_driver`: Returns a Neo4j driver instance.
- `execute`: An asynchronous function that processes the request and returns a response.

#### Patterns
- **Singleton Pattern**: The `_get_driver` function ensures that a single Neo4j driver instance is used throughout the module.
- **Factory Method Pattern**: The `_search_ontology` and `_search_nodes` methods can be seen as factory methods that produce search results.

#### Dependencies
- `os`: Used for environment variable handling.
- `logging`: For logging purposes.
- `dotenv`: Loads environment variables from a `.env` file.
- `engine.base`: Provides the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.
- `neo4j`: Provides the `GraphDatabase` class for interacting with Neo4j.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that processes the request and returns a response.
- **Internal Methods**:
  - `_extract_search_term`: Extracts the search term from the request.
  - `_search_ontology`: Searches for ontology terms.
  - `_search_nodes`: Searches for nodes.
  - `_build_summary`: Builds a summary of the results.

#### Database
- **Neo4j Labels**:
  - `OntologyTerm`: Used in the `_search_ontology` method.
  - `Person`, `Soul`, `SpiritualConcept`: Used in the `_search_nodes` method.

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Configuration Files**:
  - `.env`: Contains environment variables for the Neo4j connection.

#### Key Logic
- **Term Extraction**: The `_extract_search_term` method removes common triggers and filters out short words to extract a meaningful search term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that contain the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes of specific labels that contain the search term.
- **Summary Building**: The `_build_summary` method is intended to create a summary of the search results, but it is currently unimplemented.

#### Integration Points
- **SkillBase Integration**: The `Neo4jGraphSearchSkill` class extends `SkillBase`, integrating with the Mythos system's skill framework.
- **Neo4j Integration**: The `_get_driver` function initializes the Neo4j driver, allowing the skill to interact with the Neo4j database.
- **Environment Configuration**: The `.env` file and environment variables are used to configure the Neo4j connection, ensuring the skill can connect to the database.

This file is a critical component of the Mythos system, enabling users to perform complex graph-based searches within the Neo4j database.
