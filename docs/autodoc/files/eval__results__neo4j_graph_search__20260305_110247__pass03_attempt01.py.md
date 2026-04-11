# eval/results/neo4j_graph_search/20260305_110247/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 146

---

### Documentation for `eval/results/neo4j_graph_search/20260305_110247/pass03_attempt01.py`

#### Purpose
This file implements a Neo4j graph search skill that processes user queries to extract search terms, searches for ontology terms and nodes in a Neo4j graph database, and builds a summary of the search results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. This class has several methods to handle different aspects of the search process:
- `_extract_search_term`: Extracts the search term from the user query.
- `_search_ontology`: Searches for ontology terms in the Neo4j graph.
- `_search_nodes`: Searches for nodes in the Neo4j graph.
- `_build_summary`: Builds a summary of the search results.

There are also several top-level functions:
- `_get_driver`: Returns a Neo4j driver instance.
- `execute`: The main entry point for the skill, which orchestrates the search process.

#### Patterns
- **Singleton**: The `_get_driver` function ensures that the Neo4j driver is instantiated only once.
- **Factory**: The `execute` method acts as a factory to create and return `SkillResponse` objects based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `engine.base`, `neo4j`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` (loaded from `.env` file)

#### Interfaces
- **Exposed Methods**: `execute` (async method)
- **Exposed Classes**: `Neo4jGraphSearchSkill` (inherits from `SkillBase`)

#### Database
- **Neo4j Labels**: `OntologyTerm`
- **Neo4j Queries**:
  - `_search_ontology`: Queries nodes with label `OntologyTerm` where the term is contained in the `name` property.
  - `_search_nodes`: Queries nodes where the term is contained in the `name` property.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are loaded from the `.env` file.
- **Class Attributes**: `name`, `triggers`, `cache_ttl` are defined in `Neo4jGraphSearchSkill`.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method processes the user query to extract a meaningful search term by removing specific triggers and normalizing the query.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j graph for ontology terms that contain the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j graph for nodes that contain the search term.
- **Summary Building**: The `_build_summary` method constructs a summary of the search results, formatting them into a readable string.

#### Integration Points
- **SkillBase Integration**: The `Neo4jGraphSearchSkill` class inherits from `SkillBase` and integrates with the broader Mythos system through the `execute` method, which processes `SkillRequest` and returns `SkillResponse`.
- **Neo4j Integration**: The `_get_driver` function initializes the Neo4j driver, which is used by `_search_ontology` and `_search_nodes` to interact with the Neo4j graph database.

This file is a critical component of the Mythos system, enabling users to perform graph-based searches and retrieve meaningful information from the Neo4j database.
