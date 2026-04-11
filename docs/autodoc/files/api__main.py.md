# api/main.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 412

---

### Documentation for `api/main.py`

#### Purpose
This file serves as the main entry point for the FastAPI service in the Mythos system. It defines routes, authentication mechanisms, and integrates with various assistants and database management systems.

#### Architecture
- **Classes**: 
  - `MessageRequest` and `MessageResponse` are Pydantic models for request and response validation.
  - `UserInfo` is a Pydantic model for user information.
- **Functions**:
  - `verify_api_key`: Validates API keys.
  - `get_db_connection`: Establishes a database connection.
  - `get_user_by_identifier`: Retrieves user information by Telegram ID or username.
  - `root`: Health check endpoint.
  - `health_check`: Health check endpoint.
  - `process_message`: Processes messages through the Mythos system.
  - `get_user`: Retrieves user information.
  - `clear_chat_context`: Clears chat context for a user.
  - `get_chat_stats`: Retrieves chat context statistics.
  - `report_html`: Serves a report template with live data.
  - `debug_last_prompt`: Returns the last assembled system prompt for debugging.
- **Singleton Pattern**: `DatabaseManager` and `ChatAssistant` instances are initialized as singletons.

#### Patterns
- **Singleton**: The `DatabaseManager` and `ChatAssistant` instances are initialized once and reused throughout the application.
- **Dependency Injection**: API key verification is performed using dependency injection.

#### Dependencies
- **Imports**: 
  - `os`, `sys`, `psycopg2`, `json`, `dotenv`, `pydantic`, `fastapi`, `pathlib`, `datetime`, `BaseModel`, `HTTPException`, `Depends`, `Header`, `StaticFiles`, `CORSMiddleware`, `Attribute`.
- **External Modules**: 
  - `DatabaseManager` and `ChatAssistant` from `/opt/mythos/assistants`.
  - Various routers from `api.routes`.

#### Interfaces
- **Routes**:
  - `GET /`: Root endpoint.
  - `GET /health`: Health check endpoint.
  - `POST /message`: Processes a message.
  - `GET /user/{identifier}`: Retrieves user information.
  - `POST /chat/clear/{user_id}`: Clears chat context.
  - `GET /chat/stats/{user_id}`: Retrieves chat context statistics.
  - `GET /api/finance/report-html`: Serves a report template.
  - `GET /debug/last_prompt`: Returns the last assembled system prompt.

#### Database
- **Tables**: 
  - `users`: Used to retrieve user information by Telegram ID or username.
  - `db_manager`: Used for database queries.
  - `chat_assistant`: Used for chat processing.

#### Configuration
- **Environment Variables**: 
  - `API_KEY_TELEGRAM_BOT`, `API_KEY_KA`, `API_KEY_SERAPHE`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
- **Dotenv**: `.env` file is loaded to retrieve environment variables.

#### Key Logic
- **Message Processing**:
  - Routes messages to different assistants based on the mode (`chat`, `db`, `seraphe`, `genealogy`).
  - Validates user information and processes messages through the appropriate assistant.
- **User Information Retrieval**:
  - Retrieves user information from the `users` table based on Telegram ID or username.
- **Chat Context Management**:
  - Clears chat context and retrieves chat statistics for a user.

#### Integration Points
- **Assistants**: 
  - `ChatAssistant` for chat processing.
  - `DatabaseManager` for database queries.
- **Routers**: 
  - Various routers from `api.routes` are included to handle different endpoints.
- **Middleware**: 
  - `AuthMiddleware` for authentication.
  - `CORSMiddleware` for CORS configuration.

This file is the core of the FastAPI service, integrating various components of the Mythos system and providing a robust API for message processing and user management.
