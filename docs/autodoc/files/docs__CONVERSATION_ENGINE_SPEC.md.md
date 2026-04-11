# docs/CONVERSATION_ENGINE_SPEC.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 1756

---

### Purpose
The `CONVERSATION_ENGINE_SPEC.md` file outlines the design and architecture of the Iris Conversation Engine, a component of the Mythos system. It details the problems with the existing system and proposes a new design that leverages Pydantic for type safety and structured data handling, introduces the concept of a Conversation Engine with three layers, and specifies the control surfaces available in the Ollama API.

### Architecture
The document is structured into several parts:
1. **Introduction**: Describes the problem and the proposed solution.
2. **Design Principle**: Emphasizes the use of Pydantic for type safety and structured data handling.
3. **Part 1: The Seven Levers**: Lists and explains the control surfaces available in the Ollama API.
4. **Part 2: Call Layer**: Details the `ConversationConfig` and `ConversationMode` classes, and includes configuration presets.
5. **Part 3: Chainable Tools**: Describes the principle of chainable tools and provides examples of tool input and output classes.

### Patterns
- **Pydantic Everywhere**: Uses Pydantic models for all data boundaries to ensure type safety and structured data handling.
- **Configuration Presets**: Uses named presets (`ConversationMode`) to configure different conversation modes.

### Dependencies
- **Pydantic**: Used for defining typed models and ensuring data integrity.
- **Ollama API**: The target API for LLM interactions, which the `ConversationConfig` class is designed to interface with.

### Interfaces
- **ConversationConfig**: Exposes methods and fields to configure and generate payloads for the Ollama API.
- **ConversationMode**: Provides a way to define and load named presets for different conversation modes.

### Database
- **No direct database interactions**: The document does not specify direct interactions with PostgreSQL, Neo4j, or Redis. However, the `ConversationConfig` and `ConversationMode` classes could be serialized and stored in these databases.

### Configuration
- **YAML Configuration**: Uses YAML files (`/opt/mythos/config/conversation_modes.yaml`) to define conversation modes and their configurations.

### Key Logic
- **Control Surfaces**: The document specifies seven control surfaces (`thinking`, `format`, `tools`, `system`, `sampling`, `num_ctx`, `stop`) that can be configured per request to the Ollama API.
- **Pydantic Models**: The use of Pydantic models ensures that all data is validated and serialized correctly, and JSON schemas are automatically generated for structured output.

### Integration Points
- **Ollama API**: The `ConversationConfig` class is designed to generate payloads for the Ollama API's `/api/chat` endpoint.
- **Tool Chains**: The document outlines how tools can be chained together, with each tool having a typed input and output, allowing for composable chains of operations.

### Detailed Analysis

#### Part 1: The Seven Levers
- **Thinking Mode**: Enables or disables reasoning in the model's response.
- **Structured Output**: Uses a JSON schema to constrain the model's output.
- **Tool Calling**: Allows the model to call external functions and use their outputs.
- **System Prompt**: Overrides the default system prompt per request.
- **Temperature + Sampling**: Controls the randomness and diversity of the model's output.
- **Context Window**: Adjusts the size of the context window for the model.
- **Stop Sequences**: Specifies tokens that halt the model's generation.

#### Part 2: Call Layer
- **ConversationConfig**: A Pydantic model that encapsulates all configuration options for a single LLM call. It includes methods to generate payloads for the Ollama API.
- **ConversationMode**: A named preset loaded from YAML, defining default configurations for different types of conversations.

#### Part 3: Chainable Tools
- **ToolInput / ToolOutput**: Base classes for tool inputs and outputs, ensuring that all tools have typed inputs and outputs.
- **Example Tools**: Provides examples of astrology tools, demonstrating how inputs and outputs are defined using Pydantic models.

### Conclusion
The `CONVERSATION_ENGINE_SPEC.md` document provides a comprehensive design for the Iris Conversation Engine, emphasizing type safety and structured data handling through Pydantic. It outlines the control surfaces available in the Ollama API and proposes a modular, chainable tool system for greater flexibility and composability.
