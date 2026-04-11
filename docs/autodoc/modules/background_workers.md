# Background Workers

**Stream:** SYS
**Files:** 24

## Files in this Module

- `workers/__init__.py` (23L)
- `workers/embedding_worker.py` (94L)
- `workers/entity_worker.py` (176L)
- `workers/grid_worker.py` (492L)
- `workers/lunar_calendar_worker.py` (183L)
- `workers/pipeline_logger.py` (170L)
- `workers/prompt_registry.yaml` (311L)
- `workers/registry_loader.py` (174L)
- `workers/subject_worker.py` (230L)
- `workers/summary_worker.py` (248L)
- `workers/temporal_worker.py` (207L)
- `workers/transcription_worker.py` (340L)
- `workers/vision_worker.py` (172L)
- `workers/worker.py` (299L)
- `workers/youtube_channel_monitor.py` (464L)
- `workers/youtube_queue_consumer.py` (381L)
- `workers/schema/pipeline_log.sql` (139L)
- `workers/tests/perception_test_suite.py` (541L)
- `workers/tests/results/7b_vs_32b.json` (514L)
- `workers/tests/results/7b_vs_32b_calibrated.json` (496L)
- `workers/templates/discovery_template.yaml` (300L)
- `workers/templates/perception_template.yaml` (579L)
- `workers/orchestrator/orchestrator.py` (616L)
- `workers/orchestrator/perception_prompts.py` (22L)

---

# Mythos Background Workers Module Documentation

## 1. Module Purpose
The **Background Workers** module in the Mythos system handles asynchronous processing of complex analytical tasks that require significant computational resources or external service integration. It offloads these operations from the main application flow, ensuring real-time responsiveness while maintaining robust data processing capabilities. Key responsibilities include:

- Generating text embeddings for semantic search
- Resolving and tracking entities in conversations
- Performing grid analysis of consciousness domains
- Creating lunar calendars and notifications
- Generating conversation summaries at multiple tiers
- Enriching subject points with LLM-derived metadata
- Logging pipeline execution details for auditability

## 2. Architecture Overview
The module follows a **microservices architecture** with specialized worker processes communicating through message queues and shared databases. The architecture consists of:

1. **Entry Point**: `workers/__init__.py` exports all worker functions for system-wide access
2. **Worker Specializations**:
   - **Embedding Worker**: Qdrant vector storage
   - **Entity Worker**: Neo4j/PostgreSQL entity graph
   - **Grid Worker**: Dual PostgreSQL/Neo4j analysis
   - **Lunar Calendar Worker**: Astronomical event monitoring
   - **Summary Worker**: Tiered summarization pipeline
   - **Subject Worker**: Message enrichment pipeline
3. **Data Flow**:
   - Tasks are consumed from message queues (RabbitMQ/Kafka)
   - Workers process payloads using domain-specific logic
   - Results are stored in appropriate databases (Qdrant, PostgreSQL, Neo4j)
   - PipelineLogger tracks execution metadata in PostgreSQL

## 3. Key Components
| Component | Role | Key Functions |
|----------|------|---------------|
| **Embedding Worker** | Semantic representation | `process_embedding()`, `get_model()`, `get_qdrant()` |
| **Entity Worker** | Entity resolution | `process_entity()`, `resolve_entity()`, `create_or_update_entity()` |
| **Grid Worker** | Consciousness analysis | `process_grid_analysis()`, `analyze_with_llm()`, `store_grid_results()` |
| **Lunar Calendar Worker** | Event-based calendar generation | `run()`, `is_new_moon_today()`, `generate_calendar()` |
| **Summary Worker** | Conversation summarization | `process_summary()`, `generate_summary()`, `store_summary()` |
| **Subject Worker** | Message enrichment | `process_subject()`, `_extract_subject_llm()`, `_update_subject_vector()` |
| **PipelineLogger** | Execution auditing | `start_run()`, `log_llm_call()`, `finish_run()` |
| **RegistryLoader** | Prompt management | `assemble_prompt()`, `get_model()` |

## 4. Design Patterns
- **Lazy Initialization**: Used in `embedding_worker` and `subject_worker` for model loading
- **Singleton Pattern**: Ensures single instances of database connections and models
- **Factory Method**: `resolve_entity()` in entity_worker creates canonical entity forms
- **Polling Pattern**: Lunar_calendar_worker checks for new moon events at intervals
- **Explicit Export**: `__all__` in __init__.py controls public API surface
- **Configuration Management**: `prompt_registry.yaml` centralizes prompt templates

## 5. Data Model
### Databases
| Worker | Database | Tables/Labels |
|--------|----------|---------------|
| Embedding Worker | Qdrant | `text_embeddings` collection |
| Entity Worker | PostgreSQL | `entity_mention_timeseries` | 
| Entity Worker | Neo4j | `Person`, `Place`, `Concept`, `Entity` |
| Grid Worker | PostgreSQL | `grid_activation_timeseries`, `emotional_state_timeseries` |
| Grid Worker | Neo4j | `Exchange`, `GridNode`, `Theme` |
| Summary Worker | PostgreSQL | `conversation_summaries` |
| Subject Worker | PostgreSQL | `conversation_subject_points` |
| PipelineLogger | PostgreSQL | `pipeline_runs`, `pipeline_llm_calls`, `pipeline_queries` |

### Key Data Structures
- **Embedding Payload**: `{user_uuid, conversation_id, content, metadata}`
- **Entity Mention**: `{entity_name, canonical_form, timestamp, conversation_id}`
- **Grid Analysis**: `{domain_activation, emotional_state, theme_strengths}`
- **Calendar Event**: `{moon_phase, calendar_path, notification_status}`

## 6. API Surface
### Public Functions
```python
# From workers/__init__.py
process_grid_analysis(payload: Dict) -> None
process_embedding(payload: Dict) -> Dict
process_vision(payload: Dict) -> None
process_temporal(payload: Dict) -> None
process_entity(payload: Dict) -> None
process_summary(payload: Dict) -> None
process_subject(payload: Dict) -> None
```

### Internal APIs
- **LLM Services**: REST API calls to OLLAMA for analysis
- **Telegram Bot**: `send_telegram()` for lunar calendar notifications
- **Prompt Registry**: `assemble_prompt()` from registry_loader.py

## 7. Dependencies
### Internal
- `grid_manifest` for analysis output
- `perception.engine` for consciousness modeling
- `workers/prompt_registry.yaml` for prompt templates

### External
| Dependency | Purpose |
|------------|---------|
| PostgreSQL | Relational storage for metadata |
| Neo4j | Graph database for entity relationships |
| Qdrant | Vector database for embeddings |
| OLLAMA | LLM inference service |
| Telegram Bot API | Notification system |
| Swiss Ephemeris | Astronomical calculations |

## 8. Configuration
### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_HOST` | Qdrant database host | `localhost` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `NEO4J_URI` | Neo4j connection string | `bolt://localhost:7687` |
| `OLLAMA_HOST` | LLM service host | `http://localhost:11434` |
| `SUBJECT_EXTRACTION_MODEL` | LLM model for subject analysis | `qwen2.5:32b` |

### Configuration Files
- `/opt/mythos/.env`: Environment variables for all services
- `/opt/mythos/workers/prompt_registry.yaml`: Centralized prompt templates
- `/opt/mythos/config/telegram.conf`: Telegram bot credentials

## Integration Points
1. **Message Queue**: Consumes tasks from RabbitMQ/Kafka queues
2. **Main Application**: Exposes worker functions via `workers/__init__.py`
3. **Database Layer**: Connects to PostgreSQL, Neo4j, and Qdrant
4. **LLM Services**: Integrates with OLLAMA for analysis
5. **Notification System**: Telegram bot for lunar calendar alerts
6. **Audit System**: PipelineLogger tracks execution metadata

## Error Handling
All workers implement:
- Comprehensive logging via Python's `logging` module
- Database transaction rollback on failure
- Graceful degradation for non-critical errors
- Retry logic for transient failures (e.g., network issues)
- Dead-letter queue for unprocessable messages

## Performance Considerations
- **Model Caching**: SentenceTransformer and LLM models are loaded once
- **Connection Pooling**: Database connections are reused
- **Batch Processing**: Entity mentions are stored in batches
- **Asynchronous Execution**: Non-blocking I/O for external service calls

This module forms the backbone of Mythos' analytical capabilities, enabling complex processing while maintaining system responsiveness through asynchronous execution and robust error handling.
