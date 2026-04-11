# core/weather_service.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 225

---

### File: `core/weather_service.py`

#### Purpose
This file contains functions to fetch and format weather data from the Open-Meteo API. It provides functionality to geocode location queries, fetch weather data, and format the data for different interfaces such as Telegram and the backlog analyst prompt.

#### Architecture
The file consists of four top-level functions:
1. `_geocode(query: str)`: Geocodes a location string using the Open-Meteo geocoding API.
2. `fetch_weather(lat: float, lon: float)`: Fetches weather data from the Open-Meteo API for a given latitude and longitude.
3. `format_weather_telegram(data: dict, location_name: str)`: Formats weather data as a Telegram message.
4. `format_weather_for_analyst(data: dict)`: Formats weather data as plain text for the backlog analyst prompt.

#### Patterns
- **No specific design patterns**: The file primarily consists of utility functions without complex design patterns.

#### Dependencies
- `json`: For parsing JSON responses.
- `logging`: For logging errors and warnings.
- `urllib.request`: For making HTTP requests.
- `urllib.parse`: For URL encoding.
- `datetime`: For date and time operations.
- `typing`: For type hints.

#### Interfaces
- `_geocode(query: str) -> Optional[dict]`: Geocodes a location string and returns a dictionary with latitude, longitude, and location name.
- `fetch_weather(lat: float, lon: float) -> Optional[dict]`: Fetches weather data and returns a dictionary with weather information.
- `format_weather_telegram(data: dict, location_name: str) -> str`: Formats weather data as a Telegram message.
- `format_weather_for_analyst(data: dict) -> str`: Formats weather data as plain text for the backlog analyst prompt.

#### Database
- **No direct database interactions**: The file does not interact directly with any database tables or Neo4j labels.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Constants**: 
  - `DEFAULT_LAT`, `DEFAULT_LON`, `DEFAULT_NAME`: Default latitude, longitude, and location name.
  - `WEATHER_CODES`: Dictionary mapping weather codes to descriptions.

#### Key Logic
- **Geocoding**: The `_geocode` function checks if the query is a US zip code and constructs the appropriate URL for the Open-Meteo geocoding API. It parses the JSON response to extract latitude, longitude, and location name.
- **Weather Fetching**: The `fetch_weather` function constructs a URL for the Open-Meteo weather API with the specified latitude and longitude, and fetches the weather data.
- **Telegram Formatting**: The `format_weather_telegram` function formats the weather data into a structured message suitable for Telegram, including current weather conditions, daily forecasts, and snow day likelihood.
- **Analyst Formatting**: The `format_weather_for_analyst` function formats the weather data into plain text for the backlog analyst prompt, including current weather conditions and daily forecasts.

#### Integration Points
- **Telegram Integration**: The `format_weather_telegram` function is used to format weather data for Telegram messages.
- **Backlog Analyst Integration**: The `format_weather_for_analyst` function is used to format weather data for the backlog analyst prompt.
- **Iris Conversational Queries**: The weather data fetched and formatted by this service can be used in Iris conversational queries.

### Summary
The `core/weather_service.py` file provides essential functionality for fetching and formatting weather data from the Open-Meteo API. It supports integration with Telegram and the backlog analyst prompt, ensuring that weather information is presented in a user-friendly and structured manner.
