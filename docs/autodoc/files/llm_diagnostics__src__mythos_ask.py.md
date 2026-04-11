# llm_diagnostics/src/mythos_ask.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 291

---

### Documentation for `llm_diagnostics/src/mythos_ask.py`

#### Purpose
This file provides a CLI interface for asking the LLM (Large Language Model) about the system state, leveraging diagnostic tools and logging conversations for context.

#### Architecture
The file contains a single class `MythosAsk` and a top-level `main` function for CLI entry. The class encapsulates the logic for initializing the LLM client, loading system prompts, and handling user questions. The `main` function parses CLI arguments and invokes the `MythosAsk` class methods.

#### Patterns
- **Factory Pattern**: The `MythosAsk` class can be instantiated with different models, acting as a factory for LLM interactions.
- **Singleton Pattern**: The `ollama.Client` instance is created once per `MythosAsk` instance, acting as a singleton for the LLM client.

#### Dependencies
- **Standard Libraries**: `sys`, `os`, `json`, `argparse`
- **External Libraries**: `ollama` for LLM interactions
- **Local Modules**: `conversation_logger` for logging conversations, `diagnostics` for diagnostic tools

#### Interfaces
- **Public Methods**:
  - `ask(question: str, conversation_id: Optional[str] = None) -> str`: Asks a question to the LLM and returns the response.
- **CLI Entry Point**:
  - `main()`: Parses CLI arguments and invokes `MythosAsk` to ask a question.

#### Database
- **PostgreSQL Tables**:
  - `datetime`: Used for handling timestamps.
  - `typing`: Used for type hints.
  - `conversation_logger`: Logs conversations with questions, answers, and tools used.
  - `diagnostics`: Stores diagnostic data and results.

#### Configuration
- **Environment Variables**: None explicitly used.
- **CLI Arguments**:
  - `question`: The question to ask.
  - `model`: The LLM model to use (default is `llama3.2:3b`).
  - `conversation_id`: Optional conversation ID for context.

#### Key Logic
- **Initialization**:
  - Loads the system prompt for diagnostics.
  - Initializes the `ollama.Client` for LLM interactions.
- **Question Handling**:
  - Sends the question to the LLM with the system prompt.
  - Handles tool calls by executing diagnostic functions and re-sending the results to the LLM.
  - Logs the conversation with the question, answer, and tools used.
- **Diagnostic Tools**:
  - Executes diagnostic functions like `get_system_health`, `trace_failure`, `get_recent_events`, `get_service_status`, and `get_high_resource_processes`.

#### Integration Points
- **Conversation Logging**: Integrates with `conversation_logger` to log conversations.
- **Diagnostic Tools**: Integrates with `diagnostics` module to execute diagnostic functions.
- **LLM Client**: Uses `ollama.Client` to interact with the LLM.

### Detailed Class and Function Descriptions

#### Class: `MythosAsk`
- **Purpose**: Provides an interface for asking the LLM about the system state.
- **Methods**:
  - `__init__(self, model: str = "llama3.2:3b")`: Initializes the `MythosAsk` instance with the specified model and loads the system prompt.
  - `_load_system_prompt(self) -> str`: Loads the system prompt for diagnostics.
  - `ask(self, question: str, conversation_id: Optional[str] = None) -> str`: Sends a question to the LLM, handles tool calls, and logs the conversation.
  - `_execute_tool(self, tool_call: dict) -> dict`: Executes a diagnostic tool based on the tool call and returns the result.

#### Top-level Functions
- **`main()`**: Parses CLI arguments and invokes the `MythosAsk` class to ask a question and print the answer.
- **`__init__()`**: (Not used in the class, but defined as a top-level function)
- **`_load_system_prompt()`**: (Defined as a top-level function, but also exists in the class)
- **`ask()`**: (Defined as a top-level function, but also exists in the class)
- **`_execute_tool()`**: (Defined as a top-level function, but also exists in the class)

### Summary
The `mythos_ask.py` file provides a comprehensive CLI interface for interacting with the LLM to diagnose system state, leveraging diagnostic tools and logging conversations for context. It integrates with external libraries and local modules to handle LLM interactions, tool execution, and conversation logging.
