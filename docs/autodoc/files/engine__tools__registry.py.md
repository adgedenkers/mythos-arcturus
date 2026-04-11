# engine/tools/registry.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 126

---

### File: engine/tools/registry.py

#### Purpose
This file implements a central registry (`ToolRegistry`) for managing and executing tools within the Mythos system. It uses the Singleton design pattern to ensure that only one instance of the registry exists throughout the application.

#### Architecture
The `ToolRegistry` class is the primary component of this file. It maintains a dictionary `_tools` to store registered tools and provides methods for registration, lookup, filtering, and execution of these tools. The class is designed as a Singleton to ensure that all parts of the system interact with the same instance of the registry.

#### Patterns
- **Singleton**: The `ToolRegistry` class ensures that only one instance of the registry exists by using the `instance` class method and the `_instance` class variable.

#### Dependencies
- **Imports**: `json`, `logging`, `typing`
- **Local Imports**: `ToolDefinition`, `ToolInput`, `ToolOutput` from `engine.tools.base`

#### Interfaces
- **Public Methods**:
  - `instance()`: Returns the singleton instance of `ToolRegistry`.
  - `reset()`: Resets the singleton instance (useful for testing).
  - `register(definition: ToolDefinition)`: Registers a new tool.
  - `get(name: str)`: Retrieves a tool by name.
  - `has(name: str)`: Checks if a tool is registered.
  - `list_tools()`: Lists all registered tool names.
  - `list_tools_with_categories()`: Lists all registered tools with their categories.
  - `get_tools_for_mode(allowed_tools: Optional[list[str]])`: Filters tools based on allowed categories or names.
  - `execute(name: str, arguments: dict)`: Executes a tool with given arguments.
  - `get_input_schema(name: str)`: Retrieves the input schema for a tool.
  - `get_output_schema(name: str)`: Retrieves the output schema for a tool.
  - `status()`: Returns the status of the registry.

#### Database
- **References**: None (This file does not interact directly with any database tables or Neo4j labels.)

#### Configuration
- **Environment Variables**: None (This file does not use any environment variables.)
- **Config Files**: None (This file does not use any configuration files.)

#### Key Logic
- **Registration**: Tools are registered in the `_tools` dictionary with their names as keys.
- **Lookup**: Tools can be retrieved by name or checked for existence using `get` and `has` methods.
- **Mode-based Filtering**: Tools can be filtered based on allowed categories or names using `get_tools_for_mode`.
- **Execution**: Tools can be executed with raw arguments, and the output is validated using Pydantic models.
- **Schema Inspection**: Input and output schemas of tools can be retrieved using `get_input_schema` and `get_output_schema`.

#### Integration Points
- **Tool Registration**: Tools are registered using the `register` method, which can be called from other parts of the system where tools are defined.
- **Tool Execution**: The `execute` method is used by other parts of the system to execute registered tools.
- **Tool Lookup and Filtering**: The `get`, `has`, `list_tools`, `list_tools_with_categories`, and `get_tools_for_mode` methods are used by other subsystems to manage and filter tools.
- **Logging**: The `logger` instance is used to log registration, lookup, and execution activities, which can be integrated with the system's logging infrastructure.

This file serves as a central hub for managing and executing tools within the Mythos system, ensuring that all interactions with tools are consistent and controlled through the Singleton instance of `ToolRegistry`.
