# engine/chains/executor.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 194

---

### Documentation for `engine/chains/executor.py`

#### Purpose
The `ChainExecutor` class in `executor.py` is responsible for executing a chain of tools, ensuring that the output of one tool is correctly mapped and passed as input to the next tool in the chain. It handles validation, error management, and records the full execution trace.

#### Architecture
The file contains a single class, `ChainExecutor`, which is initialized with an optional `ToolRegistry`. The class has three methods:
- `__init__`: Initializes the `ChainExecutor` with a `ToolRegistry`.
- `execute`: Executes a chain of tools, handling input mapping and error logging.
- `_build_link_input`: Maps the output of one tool to the input of the next tool, following a specific priority order.

#### Patterns
- **Singleton Pattern**: The `ToolRegistry` is instantiated using the singleton pattern (`ToolRegistry.instance()`).
- **Chain of Responsibility Pattern**: The `execute` method processes each link in the chain sequentially, handling errors and passing data between links.

#### Dependencies
- **Imports**: `logging`, `time`, `typing`, `pydantic`
- **Internal Imports**: `ToolInput`, `ToolOutput`, `ToolRegistry`, `Chain`, `ChainLink`, `ChainResult`, `ChainTrace`, `LinkTrace` from other modules within the Mythos system.

#### Interfaces
- **Public Methods**:
  - `execute(chain: Chain, initial_input: dict | ToolInput, context: Optional[dict] = None) -> ChainResult`: Executes a chain of tools and returns the final output and execution trace.
  - `_build_link_input(tool_def: Any, previous_output: dict, field_mapping: Optional[dict[str, str]], static_args: Optional[dict[str, Any]], context: Optional[dict]) -> ToolInput`: Maps the output of one tool to the input of the next tool.

#### Database
- **References**: The file does not directly interact with any database tables or Neo4j labels. It uses Pydantic models for data validation and structuring.

#### Configuration
- **Environment Variables**: No environment variables are used directly in this file.
- **Config Files**: No configuration files are used directly in this file.

#### Key Logic
- **Input Mapping**: The `_build_link_input` method maps the output of one tool to the input of the next tool using a priority order: static arguments, explicit field mapping, auto-mapping by name, whole-object injection, and context fallback.
- **Error Handling**: The `execute` method handles errors at each link, logging them and returning a `ChainResult` with the error details and execution trace.

#### Integration Points
- **ToolRegistry**: The `ChainExecutor` relies on the `ToolRegistry` to fetch tool definitions.
- **ToolInput/ToolOutput**: The `ChainExecutor` uses `ToolInput` and `ToolOutput` Pydantic models to validate and structure the input and output data for each tool.
- **Chain/ChainLink**: The `execute` method processes a `Chain` object, which contains a list of `ChainLink` objects, each representing a tool and its configuration.

### Summary
The `ChainExecutor` class in `executor.py` is a crucial component of the Mythos system, responsible for executing chains of tools, managing input and output mapping, and handling errors. It integrates with the `ToolRegistry` and uses Pydantic models for data validation, ensuring that the execution of tool chains is robust and traceable.
