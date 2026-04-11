# docs/generated/architecture/iris.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 21

---

### Documentation for `docs/generated/architecture/iris.md`

#### Purpose
The **iris** component serves as the core operational layer of the Mythos system, managing the agent's self-model, perception, memory, and interactions with the Large Language Model (LLM) to enable coherent environmental understanding and context-aware responses. It maintains the agent's persistent identity and operational state while processing inputs and generating outputs through a structured data flow.

#### Architecture
The **iris** component is structured into several key files and modules:
- **Identity/Config**: `IDENTITY.md`, `MODEL_CONFIG.md`, `OPERATIONAL.md` for defining the agent's role, LLM parameters, and operational constraints.
- **Core Logic**: `agency.py`, `self_model.py`, `memory.py`, `perception.py` for handling decision flow, internal representation, state storage, and input processing.
- **Integration Points**: `llm.py`, `prompts.py`, `loop.py`, `config.py` for integrating with the LLM API, managing prompts, orchestrating the event cycle, and configuring component settings.
- **Entry Points**: `main.py`, `__init__.py`, `health.py` for startup, module initialization, and monitoring.

#### Patterns
- **Singleton**: The `self_model.py` and `memory.py` modules likely use a singleton pattern to ensure consistent and persistent state across the system.
- **Observer**: The `health.py` module might use an observer pattern to monitor the system's health and report issues.
- **Factory**: The `prompts.py` module could use a factory pattern to generate different prompt templates based on the context.

#### Dependencies
- **Internal**: `memory.py`, `self_model.py`, `prompts.py`, `llm.py`, `loop.py`, `config.py`.
- **External**: `MODEL_CONFIG.md` for LLM parameters, `IDENTITY.md` for agent role, `OPERATIONAL.md` for constraints.

#### Interfaces
- **Primary Interface**: `main.py` serves as the primary interface for higher-level components to interact with the **iris** component.
- **Monitoring Interface**: `health.py` provides monitoring capabilities.
- **Configuration Interface**: `config.py` allows for setting up component-specific configurations.

#### Database
- **Tables/Labels**: The `memory.py` module likely interacts with PostgreSQL and Neo4j to store and retrieve state information. The specific tables and labels are not explicitly mentioned but can be inferred from the context.

#### Configuration
- **Config Files**: `IDENTITY.md`, `MODEL_CONFIG.md`, `OPERATIONAL.md`.
- **Environment Variables**: Not explicitly mentioned, but the `config.py` module might use environment variables to configure the system.

#### Key Logic
- **Data Flow**: Environmental inputs are processed by `perception.py`, which updates the state in `memory.py` and aligns with the agent's identity in `self_model.py`. Prompts are assembled in `prompts.py` and passed to the LLM via `llm.py`. Responses are stored in `memory.py` and actions are routed by `agency.py`, which then iterates the cycle through `loop.py`.
- **Critical Path**: `loop.py` orchestrates the entire data flow, and `agency.py` handles state transitions.

#### Integration Points
- **Internal Integration**: `memory.py` and `self_model.py` are tightly integrated for state persistence and identity consistency.
- **External Integration**: The `llm.py` module integrates with the LLM API, and `main.py` serves as the primary interface to higher-level components.

#### Known Issues
- **Technical Debt**: `self_model.py` tightly couples identity logic with `memory.py`, complicating memory system replacement.
- **Edge Cases**: `loop.py` lacks robust error handling for LLM timeouts, which is tracked in `health.py` monitoring gaps.
- **Documentation Gap**: `OPERATIONAL.md` requires updates to reflect current constraint handling in `agency.py`.

This documentation provides a comprehensive overview of the **iris** component within the Mythos system, detailing its purpose, architecture, dependencies, interfaces, and key logic.
