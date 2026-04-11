# Stream: SYS

## Modules

- Root / Miscellaneous
- FastAPI Gateway
- Telegram Bot
- Background Workers
- Documentation
- Database Migrations
- Finance System
- Tools
- Integrity Scanner
- Configuration

---

# SYS Stream Architecture Overview

## 1. Stream Purpose
The **SYS (SYSTEM)** stream forms the foundational infrastructure layer of the Mythos system, providing:
- **Core infrastructure** for system operations and maintenance
- **Financial management** capabilities including transaction tracking and reporting
- **Bot integration** for user interaction via Telegram
- **Background processing** for asynchronous tasks
- **System documentation** and architectural definitions
- **Database management** for schema evolution and data integrity

This stream acts as the backbone of the Mythos system, enabling all other streams (NEU, LOG, MNE, SEN) to operate through its infrastructure services and system-level coordination.

## 2. Architecture Overview
The SYS stream follows a **modular, microservices-based architecture** with clear separation of concerns across five primary functional domains:

```
[Telegram Bot] → [FastAPI Gateway] → [Database Layer] ↔ [Background Workers]
    ↑                 ↑                  ↑                   ↑
    ↓                 ↓                  ↓                   ↓
[User Interaction] [API Entry Point] [Data Persistence] [Async Processing]
```

### Key Components
1. **Root/Miscellaneous Module** (897 files)
   - System configuration and utility functions
   - Schema definitions and database migrations
   - Logging and patch management
   - Infrastructure setup scripts

2. **FastAPI Gateway Module** (31 files)
   - Central API entry point for external services
   - Route handlers for grocery, media, finance, and document operations
   - Context management for LLM interactions

3. **Telegram Bot Module** (46 files)
   - Primary user interface for Telegram users
   - Command routing and session management
   - Integration with astrology, calendar, and task management

4. **Background Workers Module** (24 files)
   - Asynchronous processing of complex tasks
   - Specialized workers for embeddings, summarization, and entity resolution
   - Integration with Qdrant, Neo4j, and PostgreSQL

5. **Documentation Module** (107 files)
   - System architecture and design specifications
   - Development guides and technical documentation
   - Pattern definitions and migration history

6. **Database Migrations Module** (9 files)
   - Schema evolution for PostgreSQL and Neo4j
   - Versioned migration scripts for data consistency
   - Index optimization and constraint management

## 3. Data Flow Architecture

### Primary Data Flow Path
```
Telegram Bot → FastAPI Gateway → Orchestrator → Background Workers → Database
```

1. **User Interaction**:
   - Telegram users send commands to the bot
   - Bot handlers validate and route commands to appropriate services

2. **API Processing**:
   - FastAPI Gateway receives and authenticates requests
   - Context managers assemble multi-tier conversation contexts
   - Orchestrator dispatches tasks to Redis queues

3. **Background Processing**:
   - Workers consume tasks from message queues
   - Specialized workers process data (embeddings, summarization, etc.)
   - Results are stored in appropriate databases

4. **Database Operations**:
   - PostgreSQL stores structured data (transactions, summaries)
   - Neo4j manages graph relationships (entities, conversations)
   - Qdrant handles vector embeddings for semantic search

5. **Response Generation**:
   - Processed results are returned to the originating service
   - Telegram bot delivers responses to users
   - API endpoints return structured data to clients

## 4. Module Interactions

| Module | Key Interactions | Communication Pattern |
|--------|------------------|-----------------------|
| **Telegram Bot** | Routes commands to FastAPI Gateway | Synchronous API calls |
| **FastAPI Gateway** | Triggers background workers via orchestrator | Message queue (Redis) |
| **Background Workers** | Writes results to databases | Direct database access |
| **Database Migrations** | Provides schema for all modules | Versioned schema files |
| **Documentation** | References all module specifications | Static documentation |

## 5. Key Design Patterns

| Pattern | Usage Example | Description |
|--------|----------------|-------------|
| **Microservices Architecture** | Worker modules | Independent processing units with clear responsibilities |
| **Event-Driven Processing** | Orchestrator system | Task dispatching through Redis queues |
| **Layered Architecture** | API Gateway | Separation of concerns between presentation, business logic, and data |
| **Singleton Pattern** | SessionManager | Centralized user state tracking |
| **Factory Pattern** | `_get_conn` | Database connection creation |
| **CQRS Pattern** | ContextManager | Separation of read/write operations for conversation data |
| **Idempotent Operations** | Migration scripts | Safe schema updates with version control |

## 6. Data Model

### Database Layer
- **PostgreSQL**:
  - `chat_messages`: Conversation history
  - `conversation_summaries`: Tiered summaries
  - `grocery_lists`: Grocery management
  - `transactions`: Financial records
  - `pipeline_runs`: Worker execution logs

- **Neo4j**:
  - `Person`, `Concept`, `Entity` nodes
  - `MENTIONS`, `CONTINUES` relationships
  - Graph-based entity resolution

- **Qdrant**:
  - `text_embeddings` collection
  - Semantic search for conversation context

- **Redis**:
  - Task queues for background workers
  - Session state caching

### External Integrations
- **Telegram API**: User interface
- **Ollama**: LLM inference
- **Plaid**: Financial data
- **YouTube API**: Video monitoring

## 7. System Capabilities

### Infrastructure Services
- **Patch Management**: `mythos_patch_monitor.py` tracks and applies system updates
- **Logging System**: Centralized logging with duplication prevention
- **Schema Management**: Versioned migrations for PostgreSQL/Neo4j
- **Service Discovery**: `requirements.txt` and `setup_asset_store_and_helpers.sh`

### Financial Operations
- Transaction tracking and categorization
- Spending analytics and reporting
- Bill tracking and reminders
- Financial dashboard integration

### Bot Functionality
- Command routing with 50+ handlers
- Session management for user state
- Integration with astrology and calendar systems
- Voice memo and media handling

### Background Processing
- Embedding generation for semantic search
- Entity resolution and graph building
- Tiered conversation summarization
- Lunar calendar generation
- Audio transcription and analysis

## 8. Key Implementation Details

### Communication Protocols
- **REST API**: FastAPI endpoints for external services
- **Message Queues**: Redis for task orchestration
- **Database**: PostgreSQL/Neo4j for persistent storage
- **File System**: JSON/SQL files for configuration and migrations

### Performance Considerations
- **Caching**: Redis for session state and frequent queries
- **Indexing**: PostgreSQL indexes for common query patterns
- **Asynchronous Processing**: Background workers for resource-intensive tasks
- **Connection Pooling**: Efficient database connection management

### Security Measures
- **Authentication**: API key verification middleware
- **Authorization**: Role-based access control
- **Data Validation**: Pydantic models for request/response validation
- **Input Sanitization**: Prevent SQL injection and XSS attacks

## 9. System Evolution

### Migration Strategy
- Versioned migration files with numeric prefixes (e.g., migration_0057_perception_layer.sql)
- Dual schema management for PostgreSQL and Neo4j
- Idempotent operations with `IF NOT EXISTS` clauses
- Schema validation through `verify_patches.sh`

### Upgrade Process
1. Apply database migrations
2. Update service dependencies
3. Restart affected workers
4. Validate through test_pipeline.py
5. Monitor with mythos_patch_monitor.py

### Monitoring and Maintenance
- `mythos_patch_monitor.py` tracks system updates
- `verify_patches.sh` ensures migration consistency
- `test_pipeline.py` validates system functionality
- `inspect_sales_ingestion.sh` audits financial data

## 10. Future Directions
- **Enhanced Automation**: Expand background worker capabilities for real-time processing
- **Improved Scalability**: Implement distributed task queues for high-load scenarios
- **Advanced Analytics**: Develop predictive models for financial and behavioral patterns
- **Enhanced Documentation**: Expand pattern definitions and system architecture diagrams
- **Security Hardening**: Implement stricter access controls and audit logging

This architecture enables the SYS stream to provide robust infrastructure services while maintaining flexibility for future expansion and adaptation to new requirements.
