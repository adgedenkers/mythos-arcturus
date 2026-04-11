# eval/results/search_life_events/20260305_061912/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 227

---

### Purpose
The `pass05_attempt01.py` file implements a skill for the Mythos system that allows users to search for life events based on keywords, domain, or person. The skill interacts with a PostgreSQL database to retrieve and format the search results.

### Architecture
The file contains a single class, `SearchLifeEventsSkill`, which inherits from `SkillBase`. The class includes several methods for extracting search terms, detecting filters, searching events, formatting results, and building summaries. Additionally, there are top-level functions for database connection and asynchronous execution.

### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a consistent way to get a database connection.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

### Interfaces
- **Public Methods**: `execute` (asynchronous), `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, `_build_summary`.
- **Top-level Functions**: `_get_conn`, `execute`.

### Database
- **Tables**: `life_events`.
- **Operations**: 
  - **Count**: `SELECT COUNT(*) as total FROM life_events`.
  - **Search**: `SELECT id, description, domain, person, mood, created_at FROM life_events WHERE 1=1 [AND conditions] ORDER BY created_at DESC LIMIT %s`.

### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`
- **Dotenv File**: Loaded from `/opt/mythos/.env`.

### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and normalizes the message.
2. **Detect Filters**: `_detect_filters` identifies domain and person filters from the message.
3. **Search Events**: `_search_events` constructs a dynamic SQL query based on search terms and filters.
4. **Format Results**: `_format_results` formats the retrieved events into a clean dictionary format.
5. **Build Summary**: `_build_summary` creates a summary string of the search results.

### Integration Points
- **SkillBase**: Inherits from `SkillBase` and implements the `execute` method.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for request and response handling.
- **Database**: Connects to PostgreSQL using `psycopg2` for database operations.
- **Logging**: Uses `logging` for error handling and logging.

### Detailed Breakdown
1. **Class `SearchLifeEventsSkill`**:
   - **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
   - **Methods**:
     - `execute`: Main entry point for the skill, handles the request and returns a `SkillResponse`.
     - `_extract_search_terms`: Removes trigger phrases and normalizes the message.
     - `_detect_filters`: Identifies domain and person filters from the message.
     - `_search_events`: Constructs and executes a dynamic SQL query to search for life events.
     - `_format_results`: Formats the retrieved events into a clean dictionary format.
     - `_build_summary`: Creates a summary string of the search results.

2. **Top-level Functions**:
   - `_get_conn`: Returns a database connection using `psycopg2`.
   - `execute`: Asynchronous function to handle the skill execution.

### Example Usage
```python
skill = SearchLifeEventsSkill()
request = SkillRequest(message="What happened in the personal domain?")
response = skill.execute(request)
print(response.summary)
```

This file is a critical component of the Mythos system, enabling users to query and retrieve life events based on various criteria, providing a robust and flexible search functionality.
