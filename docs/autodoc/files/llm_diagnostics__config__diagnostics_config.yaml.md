# llm_diagnostics/config/diagnostics_config.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 54

---

### File: llm_diagnostics/config/diagnostics_config.yaml

#### Purpose
This YAML file contains the configuration settings for the LLM diagnostics subsystem in the Mythos system. It specifies various parameters for interacting with the Ollama server, MCP server (if enabled), logging, Neo4j database, and diagnostics thresholds.

#### Architecture
The file is structured into several sections, each defining specific configurations for different components of the diagnostics subsystem:
- `ollama`: Configuration for the Ollama server.
- `mcp_server`: Configuration for the MCP server if used.
- `logging`: Configuration for logging diagnostics data.
- `neo4j`: Configuration for connecting to the Neo4j database.
- `diagnostics`: Configuration for diagnostics thresholds and time windows.

#### Patterns
No specific design patterns are used in this configuration file. It is a straightforward configuration file that defines settings for various components.

#### Dependencies
This file does not directly import or rely on any Python modules or libraries. However, it relies on environment variables for the Neo4j connection settings.

#### Interfaces
This configuration file is used by the diagnostics subsystem to initialize and configure various components. It does not expose any interfaces directly but is read by the subsystem to set up its environment.

#### Database
- **Neo4j**: The configuration specifies the connection details for Neo4j, including `uri`, `user`, and `password`. It also indicates that conversations and tool calls are logged to Neo4j.

#### Configuration
- **Environment Variables**: The Neo4j connection settings (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`) are sourced from environment variables defined in `~/.config/arcturus/systemd.env`.
- **File Paths**: The log file location is specified as `/opt/mythos/llm_diagnostics/logs/diagnostics.log`.

#### Key Logic
- **Ollama Configuration**: Sets up the Ollama server URL, model, temperature, and max tokens for diagnostics.
- **Logging Configuration**: Defines the logging level, log file location, and whether to log conversations and tool calls.
- **Diagnostics Configuration**: Specifies thresholds for high resource queries and the default lookback time for recent events.

#### Integration Points
- **Ollama Server**: The subsystem interacts with the Ollama server using the specified `base_url` and `model`.
- **MCP Server**: If enabled, the subsystem interacts with the MCP server using the specified `host` and `port`.
- **Neo4j Database**: The subsystem logs diagnostics data to the Neo4j database using the specified connection details.
- **Logging**: The subsystem logs diagnostics information to the specified log file and level.

### Summary
This configuration file is crucial for setting up the LLM diagnostics subsystem in the Mythos system. It provides detailed settings for interacting with the Ollama server, logging diagnostics data, and connecting to the Neo4j database. The file is read by the diagnostics subsystem to initialize its environment and configure various components.
