# eval/results/neo4j_graph_search/20260305_110247/pass06_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 160

---

### Documentation for `pass06_attempt04.py`

#### Purpose
This file implements a Neo4j graph search skill (`Neo4jGraphSearchSkill`) that processes user queries to search for ontology terms and graph nodes in a Neo4j database. It extracts search terms from the query, searches the ontology and nodes, and returns the results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. The class has methods for executing the skill (`execute`), extracting search terms (`_extract_search_term`), searching the ontology (`_search_ontology`), and searching nodes (`_search_nodes`). Additionally, there are top-level functions for initializing the Neo4j driver (`_get_driver`) and executing the skill (`execute`).

#### Patterns
- **Singleton**: The `_get_driver` function ensures that the Neo4j driver is initialized only once.
- **Factory**: The `execute` method acts as a factory to create and return a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `engine.base`, `neo4j`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**: `execute`
- **Private Methods**: `_extract_search_term`, `_search_ontology`, `_search_nodes`
- **Exposed Interfaces**: The `execute` method is exposed to other parts of the system, allowing it to be invoked with a `SkillRequest` object and returning a `SkillResponse` object.

#### Database
- **Neo4j**: 
  - **Labels**: `OntologyTerm`, `Person`, `Soul`, `SpiritualConcept`
  - **Queries**: 
    - `_search_ontology`: Searches for ontology terms where the term name contains the search term.
    - `_search_nodes`: Searches for nodes with labels `Person`, `Soul`, `SpiritualConcept` where the node name contains the search term.

#### Configuration
- **Environment Variables**: 
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Configuration File**: `.env` file located at `/opt/mythos/.env`

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method processes the query to extract a meaningful search term by removing triggers, normalizing whitespace, and removing non-ASCII characters.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that match the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes with specific labels that match the search term.
- **Response Construction**: The `execute` method constructs a `SkillResponse` object with the search results and a summary of the findings.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class inherits from `SkillBase`, indicating it integrates with the broader skill system.
- **SkillRequest/SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the request-response framework.
- **Neo4j**: The `_get_driver`, `_search_ontology`, and `_search_nodes` methods interact with the Neo4j database to perform searches.

### Summary
This file implements a Neo4j graph search skill that processes user queries to search for ontology terms and graph nodes in a Neo4j database. It uses environment variables for configuration, follows singleton and factory patterns, and integrates with the broader Mythos system through the `SkillBase` class and request-response framework.
