# eval/results/neo4j_graph_search/20260305_110247/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 166

---

### File: eval/results/neo4j_graph_search/20260305_110247/temp_skill/test_skill.py

#### Purpose
This file defines a skill (`Neo4jGraphSearchSkill`) that performs searches on a Neo4j graph database for ontology terms and related nodes based on user queries. It processes the query to extract a search term, searches the ontology and nodes, and builds a summary of the results.

#### Architecture
- **Class**: `Neo4jGraphSearchSkill` inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Methods**:
  - `_extract_search_term(query)`: Extracts the search term from the query.
  - `_search_ontology(term)`: Queries the Neo4j database for ontology terms matching the search term.
  - `_search_nodes(term)`: Queries the Neo4j database for nodes matching the search term.
  - `_build_summary(results)`: Builds a summary of the search results.
- **Functions**:
  - `_get_driver()`: Returns a Neo4j driver instance.
  - `execute(request)`: The main entry point for the skill, orchestrating the extraction, search, and summary processes.

#### Patterns
- **Singleton**: The `_get_driver` function can be considered a singleton pattern as it ensures a single instance of the Neo4j driver.
- **Factory**: The `_search_ontology` and `_search_nodes` methods can be seen as factory methods that produce lists of results based on the search term.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `engine.base`, `neo4j`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Exposed Methods**: `execute(request: SkillRequest) -> SkillResponse`
- **Classes**: `Neo4jGraphSearchSkill` inherits from `SkillBase` and implements the `execute` method.

#### Database
- **Neo4j**: 
  - **Label**: `OntologyTerm`
  - **Queries**: 
    - `_search_ontology`: Queries for ontology terms.
    - `_search_nodes`: Queries for nodes with labels `Person`, `Soul`, `SpiritualConcept`.

#### Configuration
- **Environment Variables**: 
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Config Files**: `.env` file loaded using `dotenv`.

#### Key Logic
- **Term Extraction**: The `_extract_search_term` method cleans and normalizes the query to extract a meaningful search term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that match the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes that match the search term.
- **Summary Building**: The `_build_summary` method constructs a summary of the search results.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class extends `SkillBase` and integrates with the Mythos skill system.
- **Neo4j**: The `_get_driver` function integrates with the Neo4j database to perform searches.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse` objects, integrating with the Mythos request/response framework.

This file is a critical component of the Mythos system, enabling users to search the Neo4j graph database for ontology terms and related nodes based on natural language queries.
