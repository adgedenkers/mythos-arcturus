# engine/tools/base.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 210

---

### Documentation for `engine/tools/base.py`

#### Purpose
This file defines the foundational classes and decorators for tools in the Mythos system. It provides the base classes `ToolInput` and `ToolOutput`, the `ToolDefinition` class for registering tools, and the `@tool` decorator for registering functions as tools.

#### Architecture
- **ToolInput**: Base class for all tool inputs, derived from `BaseModel`.
- **ToolOutput**: Base class for all tool outputs, derived from `BaseModel`.
- **ToolDefinition**: Class for registering a single tool, derived from `BaseModel`. It holds metadata, Pydantic types, and the handler function.
- **@tool**: Decorator for registering functions as tools, ensuring they have typed inputs and outputs.

#### Patterns
- **Factory Method**: The `@tool` decorator acts as a factory method to create and register `ToolDefinition` instances.
- **Decorator Pattern**: The `@tool` decorator enhances the functionality of the decorated function by registering it as a tool.

#### Dependencies
- **Imports**: `json`, `logging`, `dataclasses`, `typing`, `pydantic`.
- **Internal Imports**: `ToolRegistry` from `engine.tools.registry`.

#### Interfaces
- **ToolInput**: Base class for all tool inputs.
- **ToolOutput**: Base class for all tool outputs.
- **ToolDefinition**: Class for registering tools, with methods to set runtime properties and execute the tool.
- **@tool**: Decorator for registering functions as tools.

#### Database
- **References**: No direct database references are found in this file.

#### Configuration
- **Logging**: Uses `logging` for logging purposes.
- **Environment Variables**: No explicit use of environment variables.

#### Key Logic
- **ToolDefinition**:
  - **model_post_init**: Initializes runtime-only attributes.
  - **set_runtime**: Sets runtime-only fields after construction.
  - **to_ollama_schema**: Generates an Ollama-compatible tool schema.
  - **execute**: Executes the tool with validated input and returns validated output.
- **@tool**:
  - Registers a function as a tool by creating a `ToolDefinition` instance and setting its properties.
  - Ensures the function has typed inputs and outputs.
  - Registers the tool in the `ToolRegistry`.

#### Integration Points
- **ToolRegistry**: The `@tool` decorator registers tools in the `ToolRegistry`, which is a global registry for all tools.
- **Pydantic Models**: `ToolInput` and `ToolOutput` are base classes for all tool inputs and outputs, ensuring type safety and consistency.
- **Ollama**: The `to_ollama_schema` method generates a schema compatible with Ollama, facilitating integration with Ollama.

### Detailed Class and Function Descriptions

#### ToolInput
- **Purpose**: Base class for all tool inputs.
- **Attributes**:
  - `Config`: Ensures no extra fields are allowed (`extra = "forbid"`).

#### ToolOutput
- **Purpose**: Base class for all tool outputs.
- **Attributes**:
  - `success`: Boolean indicating success.
  - `error`: Optional string for error messages.
  - `Config`: Ensures no extra fields are allowed (`extra = "forbid"`).

#### ToolDefinition
- **Purpose**: Registration record for a single tool.
- **Attributes**:
  - `name`: Tool name.
  - `description`: Tool description.
  - `categories`: List of categories.
  - `input_type_name`: Qualified class name for input type.
  - `output_type_name`: Qualified class name for output type.
  - `_handler`: Runtime-only handler function.
  - `_input_cls`: Runtime-only input class.
  - `_output_cls`: Runtime-only output class.
- **Methods**:
  - `model_post_init`: Initializes runtime-only attributes.
  - `set_runtime`: Sets runtime-only fields after construction.
  - `handler`: Property to get the handler function.
  - `input_cls`: Property to get the input class.
  - `output_cls`: Property to get the output class.
  - `to_ollama_schema`: Generates an Ollama-compatible tool schema.
  - `execute`: Executes the tool with validated input and returns validated output.

#### @tool Decorator
- **Purpose**: Registers a function as a tool.
- **Parameters**:
  - `name`: Tool name.
  - `description`: Tool description.
  - `categories`: Optional list of categories.
- **Logic**:
  - Extracts type hints from the function to determine input and output types.
  - Creates a `ToolDefinition` instance and sets its properties.
  - Registers the tool in the `ToolRegistry`.
  - Attaches metadata to the function for inspection.

### Example Usage
```python
from engine.tools.base import tool

@tool(
    name="natal_chart",
    description="Calculate natal chart from birth data",
    categories=["astrology"],
)
def natal_chart(input: NatalChartInput) -> NatalChart:
    # Pure computation — takes typed input, returns typed output
    ...
```

This example demonstrates how to use the `@tool` decorator to register a function as a tool, ensuring it has typed inputs and outputs and is registered in the `ToolRegistry`.
