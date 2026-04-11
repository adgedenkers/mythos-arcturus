# orchestrator/src/utils.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 340

---

### File: orchestrator/src/utils.py

#### Purpose
This file contains a collection of utility functions for the Mythos Orchestrator, providing functionality for ID generation, hashing, time formatting, JSON handling, string operations, and more.

#### Architecture
The file is structured as a collection of top-level functions, each designed to perform a specific utility task. There are no classes defined in this file. Each function is documented with docstrings that include examples and detailed descriptions of their arguments and return values.

#### Patterns
- **Singleton Pattern**: Not applicable, as the file consists of standalone utility functions.
- **Factory Pattern**: Not applicable, as there are no object creation patterns used.
- **Observer Pattern**: Not applicable, as there are no event-driven mechanisms.

#### Dependencies
- `hashlib`: Used for generating SHA-256 hashes.
- `uuid`: Used for generating unique IDs.
- `json`: Used for JSON parsing and serialization.
- `logging`: Used for logging warnings during JSON operations.
- `re`: Used for extracting numbers from strings.
- `datetime`: Used for time-related operations.
- `typing`: Used for type annotations.

#### Interfaces
The file exposes the following functions to other parts of the system:
- `generate_id(prefix: str = "") -> str`
- `hash_string(text: str, length: Optional[int] = None) -> str`
- `format_duration(seconds: float) -> str`
- `format_timestamp(dt: Optional[datetime] = None, format: str = "iso") -> str`
- `parse_timestamp(timestamp: str) -> datetime`
- `safe_json_loads(text: str, default: Any = None) -> Any`
- `safe_json_dumps(obj: Any, default: str = "{}") -> str`
- `truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str`
- `calculate_percentage(part: float, total: float, decimals: int = 1) -> float`
- `merge_dicts(*dicts: Dict) -> Dict`
- `extract_numbers(text: str) -> List[float]`
- `clean_whitespace(text: str) -> str`
- `chunks(lst: List, n: int) -> List[List]`

#### Database
The file does not directly interact with any database tables or Neo4j labels. The imports related to `datetime` and `typing` are for type annotations and time-related operations, not database interactions.

#### Configuration
The file does not use any configuration files or environment variables.

#### Key Logic
- **ID Generation**: Uses `uuid.uuid4()` to generate unique IDs.
- **Hashing**: Uses `hashlib.sha256()` to generate SHA-256 hashes.
- **Time Formatting**: Converts seconds to human-readable time strings and formats datetimes.
- **JSON Handling**: Safely parses and serializes JSON strings.
- **String Operations**: Truncates strings, extracts numbers, and cleans whitespace.
- **List Operations**: Splits lists into chunks.

#### Integration Points
This file integrates with other parts of the Mythos system by providing utility functions that can be used in various subsystems for tasks such as:
- Generating unique IDs for entities.
- Hashing strings for security or caching purposes.
- Formatting time and dates for logging or user interfaces.
- Parsing and serializing JSON data.
- Manipulating strings and lists for data processing tasks.

### Detailed Function Descriptions

1. **generate_id(prefix: str = "") -> str**
   - Generates a unique ID with an optional prefix using UUID4.

2. **hash_string(text: str, length: Optional[int] = None) -> str**
   - Generates a SHA-256 hash of a string, optionally truncated to a specified length.

3. **format_duration(seconds: float) -> str**
   - Converts a duration in seconds to a human-readable string format.

4. **format_timestamp(dt: Optional[datetime] = None, format: str = "iso") -> str**
   - Formats a datetime object to a string in various formats (ISO, date, time, datetime).

5. **parse_timestamp(timestamp: str) -> datetime**
   - Parses an ISO 8601 formatted timestamp string into a `datetime` object.

6. **safe_json_loads(text: str, default: Any = None) -> Any**
   - Safely parses a JSON string, returning a default value if parsing fails.

7. **safe_json_dumps(obj: Any, default: str = "{}") -> str**
   - Safely serializes an object to a JSON string, returning a default value if serialization fails.

8. **truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str**
   - Truncates a string to a maximum length, appending a suffix if truncated.

9. **calculate_percentage(part: float, total: float, decimals: int = 1) -> float**
   - Calculates a percentage safely, handling division by zero.

10. **merge_dicts(*dicts: Dict) -> Dict**
    - Merges multiple dictionaries, with later dictionaries overriding earlier ones.

11. **extract_numbers(text: str) -> List[float]**
    - Extracts all numbers from a string using regular expressions.

12. **clean_whitespace(text: str) -> str**
    - Cleans excessive whitespace from a string, replacing multiple spaces with a single space and removing leading/trailing whitespace.

13. **chunks(lst: List, n: int) -> List[List]**
    - Splits a list into chunks of a specified size.

These functions collectively provide a robust set of utilities for various common tasks in the Mythos system.
