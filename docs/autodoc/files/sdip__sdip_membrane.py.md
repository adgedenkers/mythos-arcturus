# sdip/sdip_membrane.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 553

---

### File: `sdip/sdip_membrane.py`

#### Purpose
This file provides FastAPI routes for accessing and managing documents and chunks within the SDIP (Secure Document Information Platform) system. It includes functionality for listing, searching, and retrieving documents and chunks with sensitivity filtering based on user clearance levels.

#### Architecture
The file is structured into several sections:
1. **Models**: Defines Pydantic models (`DocumentSummary`, `ChunkResult`, `SensitivityFinding`) for representing document summaries, chunk results, and sensitivity findings.
2. **Redaction Functions**: Functions for determining allowed sensitivity levels and applying redaction based on clearance levels.
3. **Endpoints**: FastAPI routes for various operations such as getting statistics, listing documents, retrieving document details, searching chunks, and querying documents.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the `get_allowed_levels` function can be seen as a factory for generating allowed sensitivity levels based on clearance.
- **Singleton Pattern**: Not explicitly used, but the database connection (`get_db_connection`) can be considered a singleton if it returns a single instance.

#### Dependencies
- **Imports**: `os`, `sys`, `typing`, `datetime`, `fastapi`, `pydantic`, `config`, `dotenv`, `neo4j`.
- **Database Connection**: Uses `get_db_connection` from `config` to manage database connections.

#### Interfaces
- **FastAPI Routes**:
  - `GET /api/sdip/stats`: Returns overall SDIP database statistics.
  - `GET /api/sdip/documents`: Lists and searches documents.
  - `GET /api/sdip/documents/{doc_id}`: Retrieves document details with all chunks.
  - `GET /api/sdip/chunks/search`: Searches chunks by content.
  - `GET /api/sdip/sensitivity`: Provides sensitivity findings report.
  - `GET /api/sdip/topics`: Lists topics from the Neo4j graph.
  - `POST /api/sdip/query`: Queries documents by content.

#### Database
- **PostgreSQL Tables**: `sdip_sources`, `sdip_documents`, `sdip_chunks`, `sdip_sensitivity`, `sdip_audit_log`.
- **Neo4j Labels**: `SDIPTopic`, `SDIPDocument`.

#### Configuration
- **Environment Variables**: Uses `get_db_connection` from `config` which likely reads from environment variables or a configuration file.

#### Key Logic
1. **Redaction Logic**:
   - `get_allowed_levels`: Determines allowed sensitivity levels based on clearance.
   - `redact_content`: Applies redaction to content based on sensitivity and clearance levels.
2. **Database Queries**:
   - `get_stats`: Fetches overall statistics from the database.
   - `list_documents`: Lists documents with optional filters and sensitivity filtering.
   - `get_document`: Retrieves document details and chunks with sensitivity filtering.
   - `search_chunks`: Searches chunks by content with optional sensitivity filtering.
   - `sensitivity_report`: Provides a report on sensitivity findings.
   - `list_topics`: Lists topics from the Neo4j graph.
   - `query_documents`: Queries documents by content and returns matching documents with relevant chunks.

#### Integration Points
- **Database Integration**: Uses PostgreSQL for storing and retrieving documents, chunks, and sensitivity findings.
- **Neo4j Integration**: Uses Neo4j for managing topics and their relationships.
- **Audit Logging**: Logs access events to the `sdip_audit_log` table.

### Detailed Documentation

#### Models
- **DocumentSummary**: Represents a summary of a document.
- **ChunkResult**: Represents a chunk of a document.
- **SensitivityFinding**: Represents a sensitivity finding for a chunk.

#### Redaction Functions
- **get_allowed_levels**: Returns a list of allowed sensitivity levels based on the clearance level.
- **redact_content**: Applies redaction to the content based on the sensitivity level and clearance level.

#### Endpoints
- **get_stats**: Returns overall statistics about the SDIP database.
- **list_documents**: Lists documents with optional filters and sensitivity filtering.
- **get_document**: Retrieves document details and chunks with sensitivity filtering.
- **search_chunks**: Searches chunks by content with optional sensitivity filtering.
- **sensitivity_report**: Provides a report on sensitivity findings.
- **list_topics**: Lists topics from the Neo4j graph.
- **query_documents**: Queries documents by content and returns matching documents with relevant chunks.

### Example Usage
```python
# Example: Get overall statistics
response = await get_stats()
print(response)

# Example: List documents with filters
response = await list_documents(search="example", category="tech", clearance="internal")
print(response)

# Example: Get document details
response = await get_document(doc_id=123, clearance="admin")
print(response)
```

This file serves as a critical interface for accessing and managing documents and chunks within the SDIP system, ensuring that data is appropriately filtered and redacted based on user clearance levels.
