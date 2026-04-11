# eval/results/neo4j_graph_search/20260305_110247/report.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 176

---

### Documentation for `eval/results/neo4j_graph_search/20260305_110247/report.json`

#### Purpose
This JSON file contains the results of a series of tests and evaluations for the `neo4j_graph_search` plan, including details on the model used, timestamps, test outcomes, and specific errors encountered during the evaluation process.

#### Architecture
The JSON file is structured as a dictionary with several key-value pairs:
- `plan_id`: Identifier for the plan being evaluated.
- `model`: The AI model used for the evaluation.
- `timestamp`: Timestamp of the evaluation.
- `total_passes`: Number of passes in the evaluation.
- `total_ollama_calls`: Number of calls made to the Ollama service.
- `final_parse`: Boolean indicating if the final parse check passed.
- `final_import`: Boolean indicating if the final import check passed.
- `final_behavioral`: Details of the final behavioral check, including pass/fail status and errors.
- `steps`: List of detailed steps and their respective evaluations.

Each step in the `steps` list contains:
- `pass`: Step number.
- `instruction`: Detailed instruction for the step.
- `test_type`: Type of test performed (e.g., parse_check, import_check, full_behavioral).
- `recursive`: Boolean indicating if the step is recursive.
- `attempts`: List of attempts, each containing:
  - `attempt`: Attempt number.
  - `test_pass`: Boolean indicating if the test passed.
  - `errors`: List of errors encountered.
- `elapsed_seconds`: Time taken for the step.
- `final_code_lines`: Number of lines in the final code.

#### Patterns
No specific design patterns are used in this JSON file as it is a data structure rather than a code implementation.

#### Dependencies
This JSON file does not import or rely on any external dependencies directly. However, it references the `SkillResponse` class and the `neo4j` driver, indicating that these components are used in the evaluated code.

#### Interfaces
The JSON file does not expose any interfaces directly. It is a data structure used to store and report the results of the evaluation process.

#### Database
The JSON file references the Neo4j database through the `_get_driver` function and the Cypher queries used in the `_search_ontology` and `_search_nodes` methods. The Neo4j labels and nodes accessed include:
- `OntologyTerm` (Neo4j label)
- `Person`, `Soul`, `SpiritualConcept` (Neo4j labels)

#### Configuration
The JSON file references environment variables used to configure the Neo4j driver:
- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`

#### Key Logic
The key logic described in the JSON file involves:
- Setting up the Neo4j driver and session.
- Implementing the `_extract_search_term`, `_search_ontology`, and `_search_nodes` methods.
- Combining results from ontology and node searches.
- Building a summary and returning a `SkillResponse` object.

#### Integration Points
The JSON file integrates with the following components of the Mythos system:
- **Ollama Service**: Through the `total_ollama_calls` field.
- **Neo4j Database**: Through the `_get_driver` function and Cypher queries.
- **SkillResponse Class**: Used to format the final response.

### Summary
This JSON file serves as a comprehensive report for the evaluation of the `neo4j_graph_search` plan, detailing the steps taken, the tests performed, and the outcomes, including any errors encountered. It provides a structured overview of the evaluation process and the integration with various components of the Mythos system, such as the Neo4j database and the Ollama service.
