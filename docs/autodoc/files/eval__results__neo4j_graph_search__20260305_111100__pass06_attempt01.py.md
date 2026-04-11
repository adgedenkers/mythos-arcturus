# eval/results/neo4j_graph_search/20260305_111100/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 101

---

### Documentation for `eval/results/neo4j_graph_search/20260305_111100/pass06_attempt01.py`

#### Purpose
This file defines a Neo4j graph search skill (`Neo4jGraphSearchSkill`) that performs searches on a Neo4j graph database based on user-provided terms or concepts. It extracts search terms from user requests, searches the ontology and graph nodes for matches, and builds a summary of the results.

#### Architecture
- **Class**: `Neo4jGraphSearchSkill` extends `SkillBase` and includes methods for executing the search, extracting search terms, searching the ontology and nodes, and building a summary.
- **Functions**: 
  - `_get_driver`: Returns a Neo4j driver instance.
  - `execute`: Asynchronous method to execute the search and return a `SkillResponse`.
  - `_extract_search_term`: Extracts the search term from the request message.
  - `_search_ontology`: Searches the ontology for terms matching the search term.
  - `_search_nodes`: Searches the graph nodes for terms matching the search term.
  - `_build_summary`: Placeholder method for building a summary of the results.

#### Patterns
- **Singleton**: The `_get_driver` function acts as a singleton to provide a single instance of the Neo4j driver.
- **Factory**: The `execute` method acts as a factory to create and return a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: 
  - `os`: For environment variable handling.
  - `logging`: For logging exceptions.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.
  - `GraphDatabase` from `neo4j`: Neo4j driver for database operations.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_extract_search_term`, `_search_ontology`, `_search_nodes`, `_build_summary`: Helper methods for internal use.

#### Database
- **Neo4j**: 
  - **Label**: `OntologyTerm` for ontology term searches.
  - **Nodes**: Searches for nodes with labels `Person`, `Soul`, `SpiritualConcept`.

#### Configuration
- **Environment Variables**: 
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for Neo4j.
  - `NEO4J_PASSWORD`: Password for Neo4j.
- **Dotenv File**: `.env` file for loading environment variables.

#### Key Logic
- **Search Execution**:
  - Extracts the search term from the request message.
  - Searches the ontology and graph nodes for matching terms.
  - Builds a summary of the results and returns a `SkillResponse` object.
- **Error Handling**: Logs exceptions and returns a `SkillResponse` with a low confidence level if an error occurs.

#### Integration Points
- **Mythos Subsystems**:
  - **Engine**: Integrates with the `engine.base` module to use `SkillBase`, `SkillRequest`, and `SkillResponse`.
  - **Neo4j**: Connects to the Neo4j graph database to perform searches.
  - **Configuration**: Uses environment variables and a `.env` file for configuration.

### Detailed Breakdown

#### Class: `Neo4jGraphSearchSkill`
- **Attributes**:
  - `name`: Name of the skill (`neo4j_graph_search`).
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results (600 seconds).

- **Methods**:
  - `execute`: Asynchronous method that processes the search request, extracts the term, searches the ontology and nodes, and builds a summary. It returns a `SkillResponse` object.
  - `_extract_search_term`: Extracts the search term from the request message by removing trigger words and filtering out short words.
  - `_search_ontology`: Queries the Neo4j database to find ontology terms matching the search term.
  - `_search_nodes`: Queries the Neo4j database to find graph nodes matching the search term.
  - `_build_summary`: Placeholder method for building a summary of the results.

#### Functions
- **_get_driver**: Returns a Neo4j driver instance using environment variables for connection details.
- **execute**: Asynchronous function that processes the search request and returns a `SkillResponse`.
- **_extract_search_term**: Extracts the search term from the request message.
- **_search_ontology**: Queries the Neo4j database for ontology terms.
- **_search_nodes**: Queries the Neo4j database for graph nodes.
- **_build_summary**: Placeholder function for building a summary.

### Example Usage
```python
# Example request object
request = SkillRequest(message="Define spiritual concept")

# Create an instance of the skill
skill = Neo4jGraphSearchSkill()

# Execute the search
response = skill.execute(request)

# Process the response
print(response.summary)
```

This file is a critical component of the Mythos system, enabling users to search the Neo4j graph database for ontology terms and graph nodes based on user queries.
