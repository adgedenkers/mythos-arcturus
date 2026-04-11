# docs/generated/components/iris.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 102

---

### Purpose
The `docs/generated/components/iris.md` file serves as a comprehensive reference document for the Iris component of the Mythos system. It outlines the roles of key files, data stores, integration points, configuration, and design patterns used within the Iris component.

### Architecture
The Iris component is structured around several key files and roles:
- **Entry Point**: `core/src/main.py` initializes the loop, health server, and configuration.
- **Main Loop**: `core/src/loop.py` manages the primary event loop for perception, memory, and action cycles.
- **LLM Interactions**: `core/src/llm.py` handles interactions with the Ollama LLM, including prompting and model selection.
- **Memory Management**: `core/src/memory.py` manages both persistent (PostgreSQL) and ephemeral (Redis) memory.
- **Perception**: `core/src/perception.py` processes incoming data into agent-readable formats.
- **Prompt Templates**: `core/src/prompts.py` centralizes prompt templates loaded from `core/prompts/*.md`.
- **Self-Model**: `core/src/self_model.py` defines the agent's identity and capabilities, interfacing with introspection.
- **Introspection**: `introspection/run.py`, `introspection/analyzer.py`, and `introspection/graph_enricher.py` handle the introspection cycle, analyzing system state and enriching the Neo4j knowledge graph.

### Patterns
- **Self-Model-Driven Operation**: All operations are validated against the agent's capabilities defined in `capabilities.yaml`.
- **Prompt-First Architecture**: LLM interactions use templates from `core/prompts/`.
- **Introspection Cycle**: A cycle involving scanning, analyzing, enriching, and updating the self-model.
- **Memory Segregation**: Ephemeral memory in Redis and persistent memory in PostgreSQL.
- **Health-First Design**: Provides liveness and readiness endpoints for orchestration.
- **Documentation as Code**: Generates system maps and component documentation using introspection data.

### Dependencies
- **Ollama**: For LLM interactions.
- **Telegram Bot**: For incoming messages.
- **PostgreSQL**: For persistent memory storage.
- **Neo4j**: For knowledge graph updates.
- **Redis**: For ephemeral memory storage.
- **Arcturus (System)**: For system state scanning.
- **Mythos Docs**: For generating architecture and system documentation.

### Interfaces
- **Entry Point**: `core/src/main.py` initializes the system.
- **Main Loop**: `core/src/loop.py` manages the event loop.
- **LLM Interactions**: `core/src/llm.py` handles LLM interactions.
- **Memory Management**: `core/src/memory.py` manages memory.
- **Perception**: `core/src/perception.py` processes incoming data.
- **Prompt Templates**: `core/src/prompts.py` centralizes prompt templates.
- **Self-Model**: `core/src/self_model.py` defines and updates the self-model.
- **Introspection**: `introspection/run.py`, `introspection/analyzer.py`, and `introspection/graph_enricher.py` handle introspection cycles.

### Database
- **PostgreSQL**:
  - `memory`: Stores persistent memory.
  - `self_model`: Stores the agent's identity and capabilities.
- **Neo4j**:
  - `Agent`: Represents the Iris agent instance.
  - `Capability`: Represents agent capabilities.
  - `SystemComponent`: Represents other Mythos components.
  - `Event`: Represents system events.

### Configuration
- **Environment Variables**:
  - `IRIS_PROMPTS_DIR`: Path to prompt template directory.
  - `IRIS_SELF_MODEL_CAPABILITIES`: Path to capability definition.
  - `POSTGRES_HOST`: PostgreSQL connection host.
  - `NEO4J_URI`: Neo4j connection URI.
  - `OLLAMA_BASE_URL`: LLM backend URL.
  - `IRIS_LOOP_INTERVAL`: Main loop execution interval.

### Key Logic
- **Self-Model Validation**: Ensures all operations are within the agent's defined capabilities.
- **Prompt Template Usage**: Uses centralized prompt templates for LLM interactions.
- **Introspection Cycle**: Regularly updates the self-model based on system state analysis.
- **Memory Management**: Segregates memory into ephemeral (Redis) and persistent (PostgreSQL) stores.

### Integration Points
- **Ollama**: `llm.py` interacts with the Ollama API for text generation and analysis.
- **Telegram Bot**: `perception.py` processes incoming messages from the Telegram bot.
- **PostgreSQL**: `memory.py` manages persistent memory storage.
- **Neo4j**: `graph_enricher.py` updates the knowledge graph.
- **Arcturus (System)**: `introspection/scanner.py` scans the system state.
- **Mythos Docs**: `docs/handlers/` generates documentation using introspection data.
