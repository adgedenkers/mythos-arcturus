# iris/core/src/decision_gate.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 289

---

### Documentation for `decision_gate.py`

#### Purpose
The `decision_gate.py` file contains the `DecisionGate` class, which serves as the LLM-based decision layer for the trigger engine in the Mythos system. It evaluates gathered context against a trigger's decision prompt and returns a structured decision with confidence-based routing.

#### Architecture
- **Classes**:
  - `DecisionResult`: Represents the structured result from the decision gate, containing action, confidence, reasoning, and other metadata.
  - `DecisionGate`: The main class that handles the evaluation process, including assembling prompts, calling the LLM, parsing responses, and applying confidence thresholds.

- **Functions**:
  - `to_dict`: Converts a `DecisionResult` instance to a dictionary.
  - `__init__`: Initializes the `DecisionGate` with configuration parameters.
  - `evaluate`: Evaluates a trigger's decision prompt against gathered context.
  - `_call_ollama`: Makes a synchronous HTTP request to the Ollama API.
  - `_parse_response`: Parses the LLM response into a `DecisionResult`.
  - `_validated_result`: Validates and builds a `DecisionResult` from parsed JSON.

#### Patterns
- **Factory Method**: `_validated_result` acts as a factory method to create `DecisionResult` instances from parsed JSON.
- **Singleton**: Not explicitly used, but the `DecisionGate` instance could be managed as a singleton in the broader system.

#### Dependencies
- **Imports**: `json`, `logging`, `time`, `httpx`
- **Classes**: `DecisionResult`, `ContextEngine` (assumed to be part of the broader system)

#### Interfaces
- **Public Methods**:
  - `evaluate`: Exposed to other parts of the system for evaluating triggers.
- **Data Structures**:
  - `DecisionResult`: Exposed as the result structure for decisions.

#### Database
- **References**: No direct database interactions are performed in this file. However, the `db_config` parameter in `__init__` suggests that database configurations are passed for potential future use.

#### Configuration
- **Environment Variables**: None directly used.
- **Configuration Parameters**:
  - `db_config`: Database configuration.
  - `ollama_host`: Host for the Ollama API.
  - `default_model`: Default LLM model.
  - `default_temperature`: Default temperature for LLM generation.
  - `default_max_tokens`: Default maximum tokens for LLM generation.
  - `request_timeout`: Timeout for HTTP requests to Ollama.

#### Key Logic
- **Prompt Assembly**: Combines the trigger's decision prompt with gathered context and appends a structured response instruction.
- **LLM Call**: Makes a synchronous HTTP request to the Ollama API to generate a response.
- **Response Parsing**: Parses the LLM response to extract structured decision data, handling various parsing scenarios.
- **Confidence Thresholds**: Applies thresholds to determine whether to auto-execute, notify, or defer actions based on the LLM's confidence.

#### Integration Points
- **ContextEngine**: The `evaluate` method relies on context gathered by the `ContextEngine`.
- **Ollama API**: The `_call_ollama` method makes HTTP requests to the Ollama API for LLM generation.
- **Trigger Engine**: The `evaluate` method is likely called by the trigger engine to make decisions based on gathered context and triggers.

### Summary
The `decision_gate.py` file implements the core logic for evaluating triggers using an LLM. It handles prompt assembly, LLM interaction, response parsing, and decision routing based on confidence thresholds. This module integrates with the broader Mythos system through the `ContextEngine` for context gathering and the Ollama API for LLM generation.
