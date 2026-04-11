# Configuration

**Stream:** SYS
**Files:** 5

## Files in this Module

- `config/context_access_policy.yaml` (66L)
- `config/conversation_modes.yaml` (105L)
- `config/yt-cookies.txt` (31L)
- `config/yt-oauth-client.json` (1L)
- `config/yt-oauth-token.json` (10L)

---

# Mythos Configuration Module Overview

## 1. Module Purpose
The Configuration module in Mythos centralizes and manages system-wide settings, access policies, and integration parameters. It provides structured configuration for:
- **Security policies** (file/DB access control and data sanitization)
- **AI behavior** (conversation modes and model parameters)
- **External service integrations** (YouTube API authentication)
- **Runtime constraints** (file size limits, timeouts)

This module ensures consistent enforcement of security rules, enables flexible AI behavior customization, and facilitates secure external service interactions through centralized configuration management.

## 2. Architecture Overview
The module uses a layered architecture with three primary configuration domains:

**Security Configuration Layer**
- `context_access_policy.yaml` defines access control rules for file/DB operations
- Policies are enforced by ContextEngine and data providers at runtime

**Behavior Configuration Layer**
- `conversation_modes.yaml` defines AI model parameters and tool permissions
- Configuration is loaded by chat_mode.py to determine AI behavior

**External Service Layer**
- `yt-*` files (cookies.txt, oauth-client.json, oauth-token.json) manage YouTube API credentials
- OAuth tokens are used by YouTube API integration components for authentication

All configuration files are loaded at startup by their respective consumers, with runtime validation of policy constraints during data access operations.

## 3. Key Components

| Component | Role |
|---------|------|
| **ContextEngine** | Enforces access policies from `context_access_policy.yaml` for file/DB operations |
| **chat_mode.py** | Applies conversation mode configurations from `conversation_modes.yaml` to AI responses |
| **YouTubeAuthManager** | Uses `yt-oauth-*` files to handle YouTube API authentication and token management |
| **ConfigLoader** | Centralized configuration parsing utility for YAML/JSON files |
| **SanitizationEngine** | Implements data sanitization rules defined in `context_access_policy.yaml` |

## 4. Design Patterns

1. **Configuration Pattern**  
   - Centralized YAML/JSON configuration files for policy and parameter management
   - Hierarchical structure with default/base configurations and mode-specific overrides

2. **Deny-First Security Pattern**  
   - Security policies in `context_access_policy.yaml` use explicit deny rules that take precedence over allow rules

3. **OAuth 2.0 Client Credentials Pattern**  
   - YouTube integration uses client credentials flow with refresh tokens for persistent access

4. **Policy Enforcement Pattern**  
   - Runtime validation of access rules during file/DB operations using pre-defined policy sets

## 5. Data Model

### Configuration Files
1. **YAML Structure** (`context_access_policy.yaml`):
```yaml
file_access:
  allowed_paths: ["/safe/path1", "/safe/path2"]
  denied_paths: ["/restricted/**"]
  max_file_size: 1048576 # 1MB
postgres_access:
  allowed_prefixes: ["SELECT ", "EXPLAIN "]
  denied_prefixes: ["INSERT", "UPDATE", "DELETE"]
sanitization:
  redact_keys: ["password", "secret"]
  output_limit: 1024 # bytes
  timeout: 5000 # ms
```

2. **Conversation Modes** (`conversation_modes.yaml`):
```yaml
default_model: "qwen3:30b-a3b"
deep_model: "qwen3:32b"
default_config:
  temperature: 0.7
  num_ctx: 8192
modes:
  code:
    temperature: 0.2
    allowed_tools: ["code_interpreter"]
  chat:
    temperature: 0.8
    allowed_tools: ["web_search"]
user_routes:
  "123456789": "code"
```

3. **OAuth Configuration** (`yt-oauth-client.json`):
```json
{
  "installed": {
    "client_id": "1234567890-abcdefg.apps.googleusercontent.com",
    "client_secret": "s3cr3t",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

4. **OAuth Tokens** (`yt-oauth-token.json`):
```json
{
  "token": "ya29.A0ARrdaM9CZ9Bp...",
  "refresh_token": "1//0sdfghjkl-...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "1234567890-abcdefg.apps.googleusercontent.com",
  "client_secret": "s3cr3t",
  "scopes": ["https://www.googleapis.com/auth/youtube.readonly"]
}
```

5. **Cookies** (`yt-cookies.txt`):
```
.youtube.com	TRUE	/	FALSE	1776012447	_ga_R3HTL8G9BH	GS1.2.1741452446.1.0.1741452446.0.0.0
```

## 6. API Surface

### Internal Interfaces
- **ContextEngine API**  
  ```python
  class ContextEngine:
      def apply_file_policy(self, path: str) -> bool
      def apply_db_policy(self, query: str) -> bool
      def sanitize_output(self, data: str) -> str
  ```

- **ChatMode API**  
  ```python
  class ChatModeManager:
      def get_mode_config(self, user_id: str) -> dict
      def get_model_config(self, mode: str) -> dict
  ```

- **YouTubeAuth API**  
  ```python
  class YouTubeAuth:
      def get_access_token(self) -> str
      def refresh_token(self) -> None
  ```

### External Dependencies
- **Ollama API** for model execution
- **PostgreSQL database** for query validation
- **YouTube Data API** for video metadata

## 7. Dependencies

| Dependency Type | Description |
|----------------|-------------|
| **Internal** | ContextEngine, file_content provider, postgres_query provider |
| **External Services** | YouTube API (OAuth 2.0), PostgreSQL database |
| **Tools** | `yt-dlp` for YouTube cookie management |
| **Configuration Formats** | YAML for policy/mode configurations, JSON for OAuth credentials |

## 8. Configuration

### Configuration Loading Process
1. **Startup Phase**  
   - All configuration files are loaded into memory at system startup
   - Validation occurs for required fields and format correctness

2. **Runtime Behavior**  
   - Security policies are enforced during file/DB operations
   - Conversation modes are applied based on user ID or explicit selection
   - YouTube API credentials are refreshed automatically when tokens expire

### Configuration Management

| File | Configuration Type | Management Notes |
|------|--------------------|------------------|
| `context_access_policy.yaml` | Security Policies | Requires restart for changes to take effect |
| `conversation_modes.yaml` | AI Behavior | Changes take effect immediately after reload |
| `yt-cookies.txt` | Session State | Regenerated periodically by `yt-dlp` |
| `yt-oauth-client.json` | OAuth Credentials | Should be protected with file permissions |
| `yt-oauth-token.json` | OAuth Tokens | Automatically refreshed by YouTubeAuthManager |

### Environment Variables
While configuration files are self-contained, the following environment variables can influence behavior:
- `MAX_FILE_SIZE_OVERRIDE` (overrides file size limit in `context_access_policy`)
- `OAUTH_REFRESH_INTERVAL` (controls token refresh frequency for YouTube API)
- `SANITIZATION_DEBUG` (enables debug logging for data sanitization)

---

This configuration module provides a robust foundation for secure, flexible, and maintainable system behavior while maintaining clear separation between security policies, AI behavior, and external service integrations.
