# iris/core/src/llm.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 430

---

### File: `iris/core/src/llm.py`

#### Purpose
This file contains the `LLMClient` class, which serves as the interface for interacting with the Ollama language model. It provides methods for generating responses, classifying messages, summarizing conversations, and embedding text, among other tasks.

#### Architecture
The `LLMClient` class is designed to manage the connection to the Ollama API and handle various tasks related to language model interactions. It includes methods for initializing and closing the HTTP client, selecting appropriate models for tasks, and generating responses based on prompts and system configurations.

#### Patterns
- **Singleton Pattern**: The `LLMClient` class can be used as a singleton to manage a single connection to the Ollama API.
- **Factory Method Pattern**: `_get_model_for_task` acts as a factory method to select the appropriate model based on the task type.

#### Dependencies
- **Imports**: `asyncio`, `httpx`, `structlog`, `typing`, `Config`, `PromptManager`, `TaskType`, `ModelConfig`, `get_prompt_manager`.
- **External Services**: Ollama API via HTTP requests.

#### Interfaces
- **Public Methods**:
  - `__init__(self, config: Config, prompt_manager: Optional[PromptManager] = None)`: Initializes the client with configuration and prompt manager.
  - `connect(self)`: Initializes the HTTP client and verifies the connection.
  - `disconnect(self)`: Closes the HTTP client.
  - `_get_model_for_task(self, task_type: TaskType) -> str`: Selects the appropriate model for a task type.
  - `generate(self, prompt: str, system: Optional[str] = None, task_type: TaskType = TaskType.CONVERSATION, model_override: Optional[str] = None) -> str`: Generates a response from the LLM.
  - `respond(self, message: str, mode: str = "available", conversation_history: Optional[List[Dict[str, str]]] = None, memories: Optional[List[str]] = None, spiral_day: Optional[int] = None, additional_context: Optional[str] = None, task_type: TaskType = TaskType.CONVERSATION) -> str`: Generates a response as Iris.
  - `_format_conversation_history(self, history: List[Dict[str, str]], max_messages: int = 20) -> str`: Formats conversation history for inclusion in prompts.
  - `chat(self, messages: List[Dict[str, str]], task_type: TaskType = TaskType.CONVERSATION) -> str`: Handles chat completion with message history.
  - `classify(self, message: str) -> str`: Classifies a message type.
  - `summarize_conversation(self, messages: List[str], max_tokens: int = 500) -> str`: Summarizes a conversation.
  - `embed(self, text: str) -> List[float]`: Generates an embedding for text.
  - `analyze_image(self, image_base64: str, prompt: str, context: str) -> str`: Analyzes an image using a vision model.

#### Database
- **References**: The file references `typing` and `the` as PostgreSQL tables, but these are likely placeholders or errors in the provided metadata.

#### Configuration
- **Environment Variables**: The `Config` class is used to load configuration parameters like `ollama_host` and `ollama_model`.
- **Config Files**: The `Config` class likely loads configuration from a file or environment variables.

#### Key Logic
- **Model Selection**: `_get_model_for_task` selects the appropriate model based on the task type, falling back to the default model if necessary.
- **Prompt Management**: The `PromptManager` is used to assemble system prompts and manage task-specific configurations.
- **HTTP Requests**: The `httpx.AsyncClient` is used to make asynchronous HTTP requests to the Ollama API for generating responses, classifying messages, and other tasks.

#### Integration Points
- **Prompt Manager**: The `LLMClient` integrates with the `PromptManager` to assemble system prompts and manage task-specific configurations.
- **Ollama API**: The client connects to the Ollama API to perform language model tasks like generation, classification, and summarization.
- **Logging**: The `structlog` library is used for logging, providing detailed logs for various operations and errors.

### Summary
The `LLMClient` class in `llm.py` serves as the primary interface for interacting with the Ollama language model. It manages the connection to the Ollama API, handles various language model tasks, and integrates with the `PromptManager` for prompt and configuration management. The class is designed to be used as a singleton and employs asynchronous HTTP requests to perform tasks efficiently.
