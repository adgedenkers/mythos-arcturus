# eval/results/neo4j_graph_search/20260305_110247/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 169

---

### File: `eval/results/neo4j_graph_search/20260305_110247/pass06_attempt01.py`

#### Purpose
This file implements a Neo4j-based graph search skill for the Mythos system, enabling users to search for ontology terms and graph nodes based on provided queries.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. The class includes methods for executing the search, extracting search terms, searching the ontology, searching nodes, and building summaries. Additionally, there are top-level functions for getting the Neo4j driver and extracting search terms.

#### Patterns
- **Singleton**: The `_get_driver` function acts as a singleton for the Neo4j driver, ensuring a single instance is used throughout the module.
- **Factory**: The `_get_driver` function can be seen as a factory method for creating the Neo4j driver instance.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `engine.base`, `neo4j`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method to execute the search based on a `SkillRequest` and return a `SkillResponse`.
  - `_extract_search_term`: Extracts the search term from the query.
  - `_search_ontology`: Searches the ontology for terms.
  - `_search_nodes`: Searches the graph nodes for terms.
  - `_build_summary`: Builds a summary of the search results.

#### Database
- **Neo4j**:
  - **Label**: `OntologyTerm`
  - **Queries**:
    - `_search_ontology`: Queries nodes with the label `OntologyTerm`.
    - `_search_nodes`: Queries nodes with labels `Person`, `Soul`, and `SpiritualConcept`.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Configuration File**: `.env` loaded using `dotenv.load_dotenv`

#### Key Logic
- **Search Execution**:
  - The `execute` method processes the user query, extracts the search term, and performs searches on both ontology and graph nodes.
  - The `_extract_search_term` method cleans the query to extract a meaningful search term.
  - The `_search_ontology` and `_search_nodes` methods query the Neo4j database for relevant terms and nodes.
  - The `_build_summary` method constructs a summary of the search results.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class extends `SkillBase`, integrating with the Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request/response framework.
- **Neo4j**: The `_get_driver` function and methods like `_search_ontology` and `_search_nodes` integrate with the Neo4j database for querying graph data.

### Detailed Analysis

#### Class: `Neo4jGraphSearchSkill`
- **Attributes**:
  - `name`: The name of the skill (`neo4j_graph_search`).
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results (600 seconds).

- **Methods**:
  - `execute`: Asynchronous method to handle the search request and return a response.
  - `_extract_search_term`: Cleans the query to extract a meaningful search term.
  - `_search_ontology`: Queries the ontology for terms matching the search term.
  - `_search_nodes`: Queries the graph nodes for terms matching the search term.
  - `_build_summary`: Constructs a summary of the search results.

#### Top-Level Functions
- **_get_driver**: Singleton function to get the Neo4j driver instance.
- **execute**: Asynchronous function to handle the search request and return a response.
- **_extract_search_term**: Cleans the query to extract a meaningful search term.
- **_search_ontology**: Queries the ontology for terms matching the search term.
- **_search_nodes**: Queries the graph nodes for terms matching the search term.
- **_build_summary**: Constructs a summary of the search results.

### Example Usage
```python
# Example usage of the Neo4jGraphSearchSkill
skill = Neo4jGraphSearchSkill()
request = SkillRequest(message="Define ontology term")
response = skill.execute(request)
print(response.response)
```

This file is a crucial component of the Mythos system, enabling users to interact with the Neo4j graph database through natural language queries.
