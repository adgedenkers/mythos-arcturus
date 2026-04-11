# eval/results/neo4j_graph_search/20260305_110247/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 146

---

### File: `eval/results/neo4j_graph_search/20260305_110247/pass02_attempt01.py`

#### Purpose
This file defines a skill (`Neo4jGraphSearchSkill`) for searching an ontology and nodes in a Neo4j graph database based on a user query. It extracts a search term from the query, searches the ontology and nodes, and builds a summary of the results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. The class has several methods for executing the search, extracting the search term, searching the ontology, searching nodes, and building a summary of the results. Additionally, there are top-level functions for getting the Neo4j driver and extracting the search term.

#### Patterns
- **Factory Pattern**: The `_get_driver` function acts as a factory method to create and return a Neo4j driver instance.
- **Singleton Pattern**: The `_get_driver` function ensures that the Neo4j driver is instantiated only once per application run.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `engine.base`, `neo4j`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_extract_search_term`: Extracts a search term from the query.
  - `_search_ontology`: Searches the ontology for terms matching the search term.
  - `_search_nodes`: Searches nodes for terms matching the search term.
  - `_build_summary`: Builds a summary of the search results.

#### Database
- **Neo4j Labels**:
  - `OntologyTerm`: Used in `_search_ontology` to find ontology terms.
  - `n`: Used in `_search_nodes` to find nodes.

#### Configuration
- **Environment Variables**: 
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Configuration File**: `.env` file loaded using `dotenv`.

#### Key Logic
1. **Extract Search Term**:
   - Converts the query to lowercase.
   - Removes specific triggers and normalizes whitespace.
   - Filters out single-character words and trims the query.

2. **Search Ontology**:
   - Uses a Cypher query to find ontology terms where the name or definition contains the search term.
   - Returns a list of ontology terms with their names, definitions, and categories.

3. **Search Nodes**:
   - Uses a Cypher query to find nodes where the name contains the search term.
   - Returns a list of nodes with their names and labels.

4. **Build Summary**:
   - Constructs a summary string from the search results, formatting ontology terms and node names appropriately.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class extends `SkillBase`, integrating with the broader Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request/response model.
- **Neo4j**: The `_get_driver` function and methods `_search_ontology` and `_search_nodes` integrate with the Neo4j graph database to perform searches.

This file is a critical component of the Mythos system, enabling users to query the Neo4j graph database for ontology terms and nodes based on natural language queries.
