# eval/results/neo4j_graph_search/20260305_111100/pass06_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 101

---

### Documentation for `eval/results/neo4j_graph_search/20260305_111100/pass06_attempt05.py`

#### Purpose
This file implements a Neo4j-based graph search skill (`Neo4jGraphSearchSkill`) that processes user requests to search for ontology terms and graph nodes in a Neo4j database. It extracts search terms from the request, performs searches, and builds a summary of the results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` which inherits from `SkillBase`. The class has several methods for executing the search, extracting search terms, searching the ontology, searching nodes, and building a summary. Additionally, there are top-level functions for getting the Neo4j driver and executing the skill.

#### Patterns
- **Singleton Pattern**: The `_get_driver` function ensures a single instance of the Neo4j driver is used throughout the module.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the extraction of search terms, ontology searches, node searches, and summary building.

#### Dependencies
- **Imports**: `os`, `logging`, `dotenv`, `engine.base`, `neo4j`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**: `execute`
- **Private Methods**: `_extract_search_term`, `_search_ontology`, `_search_nodes`, `_build_summary`

#### Database
- **Neo4j Labels**: `OntologyTerm`
- **Neo4j Queries**:
  - Ontology Search: `MATCH (t:OntologyTerm) WHERE toLower(t.name) CONTAINS toLower($term) RETURN t.name as name, t.definition as definition, t.category as category LIMIT 10`
  - Node Search: `MATCH (n) WHERE any(label IN labels(n) WHERE label IN ['Person', 'Soul', 'SpiritualConcept']) AND toLower(n.name) CONTAINS toLower($term) RETURN labels(n) as labels, n.name as name, n.canonical_id as canonical_id LIMIT 10`

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **.env File**: Loaded using `load_dotenv`

#### Key Logic
- **Term Extraction**: `_extract_search_term` removes common triggers and filters out short words to extract a meaningful search term.
- **Ontology Search**: `_search_ontology` queries the Neo4j database for ontology terms that contain the search term.
- **Node Search**: `_search_nodes` queries the Neo4j database for nodes of specific labels that contain the search term.
- **Summary Building**: `_build_summary` constructs a summary of the search results.

#### Integration Points
- **SkillBase**: The class inherits from `SkillBase` and integrates with the Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle input and output.
- **Neo4j Integration**: Uses the `neo4j` library to connect to and query the Neo4j database.

### Detailed Breakdown

#### Class: `Neo4jGraphSearchSkill`
- **Attributes**:
  - `name`: 'neo4j_graph_search'
  - `triggers`: List of strings that trigger the skill
  - `cache_ttl`: Time to live for cache (600 seconds)

- **Methods**:
  - `execute`: Asynchronous method that processes the request, extracts the search term, searches the ontology and nodes, and builds a summary.
  - `_extract_search_term`: Extracts the search term from the request by removing common triggers and filtering out short words.
  - `_search_ontology`: Queries the Neo4j database for ontology terms that contain the search term.
  - `_search_nodes`: Queries the Neo4j database for nodes of specific labels that contain the search term.
  - `_build_summary`: Constructs a summary of the search results (currently empty).

#### Top-Level Functions
- `_get_driver`: Returns a Neo4j driver instance using environment variables for connection details.
- `execute`: Asynchronous function that processes the request and returns a `SkillResponse`.

#### Database Interactions
- The file interacts with the Neo4j database to perform searches on `OntologyTerm` nodes and specific labels (`Person`, `Soul`, `SpiritualConcept`).

#### Configuration and Environment
- The file loads environment variables from a `.env` file using `load_dotenv` and uses these variables to configure the Neo4j driver.

This documentation provides a comprehensive overview of the file's purpose, architecture, patterns, dependencies, interfaces, database interactions, configuration, key logic, and integration points within the Mythos system.
