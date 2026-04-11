# engine/chains/chain.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 98

---

### File: `engine/chains/chain.py`

#### Purpose
This file defines the core models for handling tool chains in the Mythos system. It includes classes for representing individual chain links, the chain itself, execution traces, and the result of chain execution.

#### Architecture
The file consists of several Pydantic models:
- `ChainLink`: Represents a single step in a tool chain, including the tool name, field mapping, static arguments, and model override.
- `Chain`: Represents a sequence of `ChainLink` objects, defining a named tool chain.
- `LinkTrace`: Captures the execution trace for a single chain link, including input, output, elapsed time, and success status.
- `ChainTrace`: Captures the full execution trace for a chain, including the chain name, start time, and a list of `LinkTrace` objects.
- `ChainResult`: Represents the result of a chain execution, including success status, final output, error message, and execution trace.

#### Patterns
- **Data Transfer Object (DTO)**: The classes `ChainLink`, `Chain`, `LinkTrace`, `ChainTrace`, and `ChainResult` are used as DTOs to transfer and validate data.
- **Factory Method**: The `ChainTrace` and `LinkTrace` classes use default factory methods to initialize their fields.

#### Dependencies
- **Imports**:
  - `datetime`: For handling timestamps.
  - `typing`: For type annotations.
  - `pydantic`: For defining the Pydantic models.
  - `ToolOutput` from `../tools/base`: For handling tool outputs.

#### Interfaces
- **Exposed Classes**:
  - `ChainLink`: Represents a single step in a tool chain.
  - `Chain`: Represents a sequence of `ChainLink` objects.
  - `LinkTrace`: Captures the execution trace for a single chain link.
  - `ChainTrace`: Captures the full execution trace for a chain.
  - `ChainResult`: Represents the result of a chain execution.
- **Properties**:
  - `ChainTrace.total_ms`: Returns the total elapsed time in milliseconds for the entire chain.
  - `ChainTrace.tools_called`: Returns a list of tool names called in the chain.

#### Database
- **References**:
  - `chains`: This table likely stores predefined chains, though no direct database operations are performed in this file.

#### Configuration
- **Configuration Files**:
  - `chains.yaml`: Predefined chains can be loaded from this file.
- **Environment Variables**:
  - None directly used in this file.

#### Key Logic
- **ChainLink**:
  - Represents a single step in a tool chain with fields for tool name, field mapping, static arguments, and model override.
- **Chain**:
  - Represents a sequence of `ChainLink` objects, defining a named tool chain.
- **LinkTrace**:
  - Captures the execution trace for a single chain link, including input, output, elapsed time, and success status.
- **ChainTrace**:
  - Captures the full execution trace for a chain, including the chain name, start time, and a list of `LinkTrace` objects.
- **ChainResult**:
  - Represents the result of a chain execution, including success status, final output, error message, and execution trace.

#### Integration Points
- **Mythos Subsystems**:
  - **Tool Execution**: The `Chain` and `ChainLink` classes are used to define and execute sequences of tools.
  - **Logging and Telemetry**: The `LinkTrace` and `ChainTrace` classes are used to capture and store execution telemetry.
  - **Result Handling**: The `ChainResult` class is used to handle and return the result of chain execution.

This file serves as the foundation for defining and executing tool chains in the Mythos system, providing a structured way to represent and trace the execution of these chains.
