# neuro/perception/__init__.py

**Language:** python
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 300

---

### File: `neuro/perception/__init__.py`

#### Purpose
This file contains functions and configurations for generating perception prompts for different nodes in the Mythos system. Each node is designed to extract specific types of knowledge from a conversation exchange.

#### Architecture
The file is structured around a dictionary `PERCEPTION_PROMPTS` that contains configurations for each node. Each node configuration includes a domain, description, and a detailed prompt template. The file also contains three top-level functions: `get_perception_prompt`, `get_all_active_nodes`, and `get_node_domain`.

#### Patterns
- **Singleton Pattern**: The `PERCEPTION_PROMPTS` dictionary acts as a singleton, holding the configuration for all nodes.
- **Template Method Pattern**: The `get_perception_prompt` function uses a template method to construct the full prompt for a given node.

#### Dependencies
- **Imports**: No explicit imports are shown in the provided code snippet.
- **Dependencies**: The file relies on the `PERCEPTION_PROMPTS` dictionary and string formatting.

#### Interfaces
- **`get_perception_prompt(node: str, user_message: str, assistant_response: str) -> str`**: Builds the full perception prompt for a given node.
- **`get_all_active_nodes() -> list`**: Returns a list of all node names with perception prompts.
- **`get_node_domain(node: str) -> str`**: Returns the domain label for a given node.

#### Database
- **PostgreSQL**: The file references a PostgreSQL table named `this`, though no specific operations are shown in the provided code.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Config Files**: No configuration files are used.

#### Key Logic
- **Prompt Construction**: The `get_perception_prompt` function constructs a full perception prompt by combining the shared preamble, node-specific prompt, and the user/assistant exchange.
- **Node Domain Retrieval**: The `get_node_domain` function retrieves the domain label for a given node from the `PERCEPTION_PROMPTS` dictionary.

#### Integration Points
- **Mythos Subsystems**: This file integrates with other subsystems by providing perception prompts for nodes, which are likely used in the knowledge extraction and processing pipelines.
- **Database Interaction**: The file references a PostgreSQL table, indicating that it may interact with the database to store or retrieve perception-related data.

### Detailed Analysis

#### `get_perception_prompt(node: str, user_message: str, assistant_response: str) -> str`
- **Purpose**: Constructs a full perception prompt for a given node by combining the node-specific prompt with the user and assistant messages.
- **Logic**: Uses the `PERCEPTION_PROMPTS` dictionary to retrieve the node-specific prompt and appends the user and assistant messages to it.

#### `get_all_active_nodes() -> list`
- **Purpose**: Returns a list of all node names that have perception prompts configured.
- **Logic**: Simply returns the keys of the `PERCEPTION_PROMPTS` dictionary.

#### `get_node_domain(node: str) -> str`
- **Purpose**: Retrieves the domain label for a given node.
- **Logic**: Uses the `PERCEPTION_PROMPTS` dictionary to find the domain label associated with the given node.

### Example Usage
```python
# Get the perception prompt for the "anchor" node
prompt = get_perception_prompt("anchor", "I'm feeling tired", "You should rest more.")
print(prompt)

# Get all active nodes
nodes = get_all_active_nodes()
print(nodes)

# Get the domain of the "echo" node
domain = get_node_domain("echo")
print(domain)
```

### Conclusion
This file serves as a central configuration and utility module for generating perception prompts in the Mythos system. It provides a flexible and extensible way to define and retrieve prompts for different nodes, each focusing on a specific domain of knowledge extraction.
