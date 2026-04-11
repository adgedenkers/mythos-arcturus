# api/auth/google_auth.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 302

---

### File: api/auth/google_auth.py

#### Purpose
This file implements Google OAuth2 authentication and JWT token management for the Mythos system. It provides routes for initiating and handling Google OAuth2 login, creating and verifying JWT tokens, and protecting certain routes with middleware.

#### Architecture
The file is structured around several top-level functions and a middleware class:
- **Top-level functions**: Handle database connections, JWT creation and verification, user authentication, and OAuth2 flow.
- **Middleware class**: `AuthMiddleware` to protect specific routes.

#### Patterns
- **Factory Method**: Not explicitly used.
- **Singleton**: Not explicitly used.
- **Observer**: Not explicitly used.
- **Dependency Injection**: Used in `require_auth` to inject authenticated user data into routes.

#### Dependencies
- **Imports**: `os`, `json`, `secrets`, `logging`, `httpx`, `jwt`, `psycopg2`, `fastapi`, `starlette`, `dotenv`.
- **Environment Variables**: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `JWT_SECRET`, `JWT_EXPIRY_HOURS`, PostgreSQL connection parameters.

#### Interfaces
- **Routes**:
  - `GET /google/login`: Initiates Google OAuth2 login.
  - `GET /google/callback`: Handles the OAuth2 callback from Google.
  - `GET /logout`: Clears the session cookie and redirects to login.
  - `GET /me`: Returns current authenticated user info.
- **Functions**:
  - `get_db_connection()`: Returns a PostgreSQL database connection.
  - `check_whitelist(email: str)`: Checks if an email is in the `web_users` whitelist.
  - `update_last_login(email: str, google_name: str = None, google_picture: str = None)`: Updates the last login timestamp and Google profile info.
  - `create_jwt(user: dict)`: Creates a JWT token for an authenticated user.
  - `verify_jwt(token: str)`: Verifies and decodes a JWT token.
  - `get_current_user(request: Request)`: Extracts the current user from the JWT cookie.
  - `require_auth(request: Request)`: Ensures the user is authenticated.
- **Middleware**:
  - `AuthMiddleware`: Protects routes with authentication.

#### Database
- **Tables/Labels**:
  - `web_users`: Used to check if an email is in the whitelist and to update last login info.
  - `last`: Not explicitly defined in the code but likely refers to the `last_login` column in `web_users`.

#### Configuration
- **Environment Variables**: Configured via `.env` file, including Google OAuth2 credentials and JWT secret.
- **Logging**: Uses `logging` module with a logger named `__name__`.

#### Key Logic
- **OAuth2 Flow**:
  - Redirects users to Google's OAuth2 consent screen.
  - Exchanges the authorization code for tokens.
  - Fetches user info from Google.
  - Checks if the user's email is in the `web_users` whitelist.
  - Updates last login info in the database.
  - Creates a JWT token and sets it as a cookie.
- **JWT Management**:
  - Creates JWT tokens with user info and a specified expiry.
  - Verifies JWT tokens and extracts user info.
- **Middleware**:
  - Protects specific routes by checking for a valid JWT token.
  - Redirects unauthenticated users to the login page or returns a 401 error for API routes.

#### Integration Points
- **FastAPI**: Uses FastAPI's `APIRouter` and `Depends` for route definitions and dependency injection.
- **PostgreSQL**: Uses `psycopg2` for database operations.
- **HTTP Client**: Uses `httpx` for making HTTP requests to Google OAuth2 endpoints.
- **Logging**: Uses Python's `logging` module for logging events.
- **Environment Configuration**: Uses `dotenv` to load environment variables from `.env` file.

This file serves as a crucial component for user authentication and authorization in the Mythos system, integrating with Google OAuth2 and managing JWT tokens to secure the application's routes.
