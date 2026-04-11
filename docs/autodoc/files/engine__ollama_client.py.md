# engine/ollama_client.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 152

---

### File: engine/ollama_client.py

#### Purpose
This file defines an asynchronous client (`OllamaChatClient`) for interacting with Ollama's `/api/chat` endpoint, providing methods for sending chat requests, managing connections, and performing health checks.

#### Architecture
The file contains a single class `OllamaChatClient` with the following methods:
- `__init__`: Initializes the client with base URL, timeout, and retry settings.
- `__aenter__` and `__aexit__`: Context manager methods for asynchronous use.
- `connect`: Establishes an HTTP session.
- `close`: Closes the HTTP session.
- `chat`: Sends a chat request with a conversation configuration and messages.
- `chat_raw`: Sends a raw payload to the chat endpoint.
- `_request`: Handles the HTTP request with retry logic.
- `health_check`: Checks the health of the Ollama service.

#### Patterns
- **Context Manager**: The `OllamaChatClient` class implements the `__aenter__` and `__aexit__` methods to support asynchronous context management.
- **Retry Logic**: The `_request` method implements retry logic with exponential backoff.

#### Dependencies
- `json`: For JSON handling.
- `logging`: For logging.
- `os`: For environment variable retrieval.
- `aiohttp`: For asynchronous HTTP requests.
- `asyncio`: For asynchronous operations.
- `ConversationConfig` from `engine.models`: For conversation configuration.

#### Interfaces
- `OllamaChatClient` exposes the following methods:
  - `__aenter__`: Enters the context manager.
  - `__aexit__`: Exits the context manager.
  - `connect`: Establishes a connection.
  - `close`: Closes the connection.
  - `chat`: Sends a chat request.
  - `chat_raw`: Sends a raw payload.
  - `health_check`: Checks the health of the Ollama service.

#### Database
- The file references PostgreSQL tables `orchestrator`, `typing`, and `e`, but does not directly interact with them.

#### Configuration
- Environment variables:
  - `OLLAMA_HOST`: Base URL for Ollama service (default: `http://localhost:11434`).
  - `OLLAMA_CHAT_TIMEOUT`: Timeout for chat requests (default: `120` seconds).

#### Key Logic
- **Chat Request Handling**: The `chat` method constructs a payload from the provided `ConversationConfig` and messages, then sends it via `_request`.
- **Retry Logic**: The `_request` method retries failed requests with exponential backoff.
- **Health Check**: The `health_check` method verifies the availability of the Ollama service by checking the `/api/tags` endpoint.

#### Integration Points
- **Conversation Engine**: This client integrates with the conversation engine to send chat requests and manage the conversation state.
- **Orchestrator**: The client interacts with the orchestrator to manage the lifecycle of chat sessions and ensure the health of the Ollama service.

### Summary
The `OllamaChatClient` class provides a robust and asynchronous interface to interact with Ollama's `/api/chat` endpoint, supporting advanced features like tool calling and structured output. It integrates seamlessly with the Mythos system, ensuring reliable communication and health monitoring of the Ollama service.
