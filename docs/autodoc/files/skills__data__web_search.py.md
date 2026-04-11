# skills/data/web_search.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 389

---

### File: skills/data/web_search.py

#### Purpose
This file implements the `WebSearchSkill` class, which provides the Mythos system with the ability to perform web searches using RSS news feeds and Wikipedia. The skill classifies queries into news, factual, or ambiguous categories and uses the appropriate backend to fetch relevant information.

#### Architecture
The file contains:
- **Top-level functions**: `_http_get`, `_strip_html`, `_classify_query`, `_extract_query`, `_score_item`, `_fetch_rss_news`, `_wiki_search`, `_wiki_summary`, `_fetch_wikipedia`, `relevance`, `execute`.
- **Class**: `WebSearchSkill` which inherits from `SkillBase`.

The `WebSearchSkill` class includes methods for determining the relevance of a query and executing the search. The top-level functions handle specific tasks such as HTTP requests, HTML stripping, query classification, and data fetching from RSS feeds and Wikipedia.

#### Patterns
- **Strategy Pattern**: The skill classifies the query and selects the appropriate backend (RSS or Wikipedia) to fetch the relevant information.
- **Factory Method Pattern**: The `_fetch_rss_news` and `_fetch_wikipedia` functions are used to create and return the search results based on the query type.

#### Dependencies
- **Imports**: `html`, `json`, `logging`, `re`, `urllib.parse`, `urllib.request`, `xml.etree.ElementTree`, `sys`, `typing`, `engine.base` (for `SkillBase`, `SkillRequest`, `SkillResponse`).

#### Interfaces
- **Public Methods**:
  - `relevance(message: str, context: Dict[str, Any] = None) -> float`: Determines the relevance of a query to the skill.
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the search based on the request and returns the response.

#### Database
- **References**: The file does not directly interact with the database but relies on the `SkillBase` class which might use PostgreSQL for logging or caching.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Configuration Files**: No explicit configuration files are used.

#### Key Logic
- **Query Classification**: The `_classify_query` function classifies the query into 'news', 'factual', or 'ambiguous' based on predefined signals.
- **RSS News Fetching**: The `_fetch_rss_news` function fetches and scores RSS feed items based on the query keywords.
- **Wikipedia Search**: The `_wiki_search` and `_wiki_summary` functions fetch and summarize Wikipedia articles based on the query.
- **Relevance Calculation**: The `relevance` method calculates the relevance of a query based on explicit search intent, news signals, and factual signals.

#### Integration Points
- **SkillBase Class**: The `WebSearchSkill` class inherits from `SkillBase` and integrates with the broader Mythos system through the `SkillRequest` and `SkillResponse` objects.
- **Logging**: Uses the `logging` module to log information and debug messages.
- **HTTP Requests**: Uses `urllib.request` to perform HTTP GET requests to fetch data from RSS feeds and Wikipedia.

### Detailed Documentation

#### Classes
- **WebSearchSkill**
  - **Inherits**: `SkillBase`
  - **Attributes**:
    - `name`: "web_search"
    - `version`: "2.0"
    - `category`: "data"
    - `description`: Description of the skill.
    - `triggers`: List of phrases that trigger the skill.
    - `cache_ttl`: Cache time-to-live (10 minutes).
  - **Methods**:
    - `relevance(message: str, context: Dict[str, Any] = None) -> float`: Determines the relevance of a query based on explicit search intent, news signals, and factual signals.
    - `execute(request: SkillRequest) -> SkillResponse`: Executes the search based on the request and returns the response.

#### Top-level Functions
- **_http_get(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[bytes]**: Performs an HTTP GET request and returns the raw bytes or `None` on failure.
- **_strip_html(text: str) -> str**: Removes HTML tags and decodes entities from the text.
- **_classify_query(message: str) -> str**: Classifies the query into 'news', 'factual', or 'ambiguous'.
- **_extract_query(message: str) -> str**: Strips conversational filler and returns the core search terms.
- **_score_item(title: str, description: str, keywords: List[str]) -> float**: Scores an RSS item by keyword relevance.
- **_fetch_rss_news(query: str) -> Optional[str]**: Fetches and scores RSS feed items based on the query keywords.
- **_wiki_search(query: str, limit: int = 3) -> List[Dict]**: Performs a full-text Wikipedia search and returns a list of result dictionaries.
- **_wiki_summary(title: str) -> Optional[str]**: Fetches the Wikipedia lead paragraph for a page title.
- **_fetch_wikipedia(query: str) -> Optional[str]**: Searches Wikipedia and returns a summary of the best match.

### Integration with Mythos System
The `WebSearchSkill` integrates with the broader Mythos system through the `SkillBase` class, which provides the necessary infrastructure for skills to interact with the system. The skill uses HTTP requests to fetch data from external sources and logs information and debug messages using the `logging` module. The skill is designed to be part of a larger ecosystem where it can be triggered based on user queries and provide relevant information from RSS feeds and Wikipedia.
