# eval/results/neo4j_graph_search/20260305_110247/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 166

---

### File: `eval/results/neo4j_graph_search/20260305_110247/final.py`

#### Purpose
This file defines a `Neo4jGraphSearchSkill` class that performs graph searches in a Neo4j database based on user queries. It extracts search terms from queries, searches for ontology terms and graph nodes, and builds a summary of the results.

#### Architecture
- **Class**: `Neo4jGraphSearchSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Main method that processes the request, extracts the search term, and performs the search.
  - `_extract_search_term`: Extracts the search term from the query.
  - `_search_ontology`: Searches for ontology terms in Neo4j.
  - `_search_nodes`: Searches for nodes in Neo4j.
  - `_build_summary`: Builds a summary of the search results.
- **Top-level Functions**:
  - `_get_driver`: Returns a Neo4j driver instance.
  - `execute`: Top-level function that wraps the `execute` method of `Neo4jGraphSearchSkill`.

#### Patterns
- **Singleton**: The `_get_driver` function ensures a single Neo4j driver instance is used.
- **Factory**: The `execute` method and `_search_ontology`, `_search_nodes` methods act as factories for generating search results.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging errors.
  - `re`: For regular expression operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.
  - `neo4j`: For interacting with Neo4j.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes a request and returns a response.
- **Exposed Functions**:
  - `_get_driver`: Returns a Neo4j driver instance.
  - `execute`: Top-level function that wraps the `execute` method of `Neo4jGraphSearchSkill`.

#### Database
- **Neo4j**:
  - **Label**: `OntologyTerm` is used for ontology term searches.
  - **Nodes**: Nodes with labels `Person`, `Soul`, and `SpiritualConcept` are searched.

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for Neo4j.
  - `NEO4J_PASSWORD`: Password for Neo4j.
- **Dotenv**: `.env` file located at `/opt/mythos/.env`.

#### Key Logic
- **Search Term Extraction**: `_extract_search_term` removes specific triggers and normalizes the query.
- **Ontology Search**: `_search_ontology` queries Neo4j for ontology terms that match the search term.
- **Node Search**: `_search_nodes` queries Neo4j for nodes with specific labels that match the search term.
- **Summary Building**: `_build_summary` constructs a summary of the search results.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class inherits from `SkillBase`, integrating with the broader Mythos system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the request-response cycle of the Mythos system.
- **Neo4j**: The `_get_driver` function and search methods integrate with the Neo4j database to perform graph searches.
