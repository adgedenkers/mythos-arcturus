# workers/temporal_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 207

---

### Documentation for `workers/temporal_worker.py`

#### Purpose
This file contains the logic for extracting temporal references (dates and times) from messages and linking them to astrological events stored in the PostgreSQL database.

#### Architecture
The file consists of several top-level functions:
- `get_db()`: Establishes a connection to the PostgreSQL database.
- `extract_dates(text: str)`: Extracts date references from the given text.
- `find_active_transits(date: datetime)`: Finds astrological events active on the given date.
- `store_temporal_data(message_id: int, user_uuid: str, dates: List[datetime], transits: List[Dict])`: Stores the extracted temporal data and links it to astrological events.
- `process_temporal(payload: Dict[str, Any])`: Main entry point for the temporal extraction worker.

#### Patterns
- **Singleton Pattern**: The `get_db()` function can be considered a singleton pattern as it ensures a single database connection is established.
- **Factory Method**: The `extract_dates()` function can be seen as a factory method that produces a list of `datetime` objects based on the input text.

#### Dependencies
- `os`: For environment variable access.
- `re`: For regular expression operations.
- `logging`: For logging.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from `.env` files.

#### Interfaces
- `process_temporal(payload: Dict[str, Any]) -> Dict[str, Any]`: The main entry point that processes the payload and returns a dictionary with the status and details of the operation.

#### Database
- **PostgreSQL Tables**:
  - `astrological_events`: Stores astrological events.
  - `chat_messages`: Stores chat messages.
  - `message_astrological_context`: Links messages to astrological events.

#### Configuration
- Uses environment variables loaded from `/opt/mythos/.env` for database connection details:
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`

#### Key Logic
1. **Date Extraction**:
   - `extract_dates(text: str)`: Uses regular expressions to find and parse dates in various formats (ISO, US, month names) and relative time references (e.g., "yesterday", "next week").
   
2. **Astrological Event Retrieval**:
   - `find_active_transits(date: datetime)`: Queries the `astrological_events` table to find events active on the given date, considering a 7-day influence window around the exact time of the event.
   
3. **Data Storage**:
   - `store_temporal_data(message_id: int, user_uuid: str, dates: List[datetime], transits: List[Dict])`: Updates the `chat_messages` table with the extracted dates and links the message to relevant astrological events in the `message_astrological_context` table.

4. **Main Processing**:
   - `process_temporal(payload: Dict[str, Any])`: Orchestrates the extraction and storage process, handling the payload, extracting dates, finding transits, and storing the results.

#### Integration Points
- **Mythos Subsystems**:
  - **Database Integration**: Connects to the PostgreSQL database to retrieve astrological events and store temporal data.
  - **Message Processing**: Integrates with the message processing pipeline to extract temporal data from messages and link them to astrological events.
  - **Logging**: Uses the logging subsystem to log the processing steps and any errors encountered.

This file is a critical component of the Mythos system, enabling the extraction and contextualization of temporal references within messages, thereby enriching the system's ability to provide astrological insights.
