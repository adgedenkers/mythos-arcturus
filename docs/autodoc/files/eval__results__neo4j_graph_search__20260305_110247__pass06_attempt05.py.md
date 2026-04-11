# eval/results/neo4j_graph_search/20260305_110247/pass06_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 177

---

### Documentation for `eval/results/neo4j_graph_search/20260305_110247/pass06_attempt05.py`

#### Purpose
This file defines a skill (`Neo4jGraphSearchSkill`) that performs graph searches in a Neo4j database to find ontology terms and related nodes based on a user query. It handles the extraction of search terms, querying the Neo4j database, and building a summary of the results.

#### Architecture
- **Classes**: 
  - `Neo4jGraphSearchSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_driver`: Returns a Neo4j driver instance.
  - `_extract_search_term`: Extracts the search term from the user query.
  - `_search_ontology`: Queries the Neo4j database for ontology terms.
  - `_search_nodes`: Queries the Neo4j database for related nodes.
  - `_build_summary`: Builds a summary of the search results.
- **Data Flow**:
  1. The `execute` method processes the user query.
  2. `_extract_search_term` extracts the search term.
  3. `_search_ontology` and `_search_nodes` query the Neo4j database.
  4. `_build_summary` constructs the summary of the results.
  5. The `execute` method returns a `SkillResponse` object with the results.

#### Patterns
- **Singleton**: The `_get_driver` function ensures a single instance of the Neo4j driver is used.
- **Observer**: The `execute` method observes the user query and triggers the appropriate search methods.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `re`: For regular expression operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.
  - `GraphDatabase`: From the `neo4j` module.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes the user query and returns a `SkillResponse` object.
- **Exposed Functions**:
  - `_get_driver`: Returns a Neo4j driver instance.
  - `_extract_search_term`: Extracts the search term from the user query.
  - `_search_ontology`: Queries the Neo4j database for ontology terms.
  - `_search_nodes`: Queries the Neo4j database for related nodes.
  - `_build_summary`: Builds a summary of the search results.

#### Database
- **Neo4j**:
  - **Label**: `OntologyTerm` (used in `_search_ontology`).
  - **Nodes**: `Person`, `Soul`, `SpiritualConcept` (used in `_search_nodes`).

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Config Files**:
  - `.env`: Loaded using `dotenv` to set environment variables.

#### Key Logic
- **Term Extraction**: The `_extract_search_term` method cleans and normalizes the user query to extract a meaningful search term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that match the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes (e.g., `Person`, `Soul`, `SpiritualConcept`) that match the search term.
- **Summary Building**: The `_build_summary` method constructs a human-readable summary of the search results.

#### Integration Points
- **Mythos Subsystems**:
  - **Engine**: The `execute` method is part of the `SkillBase` class, which is part of the Mythos engine.
  - **Neo4j**: The `_get_driver`, `_search_ontology`, and `_search_nodes` methods interact with the Neo4j database.
  - **Logging**: Errors are logged using the `logging` module.
  - **Environment Configuration**: The `.env` file is used to configure the Neo4j connection details.

This file is a critical component of the Mythos system, enabling users to search for ontology terms and related nodes in the Neo4j database, and providing a structured response with the search results.
