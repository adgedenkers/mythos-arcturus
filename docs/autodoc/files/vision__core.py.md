# vision/core.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 276

---

### File: vision/core.py

#### Purpose
This file contains core functionality for analyzing images using the Ollama vision model. It includes functions to load images, extract JSON from responses, and perform both synchronous and asynchronous image analysis.

#### Architecture
The file consists of several top-level functions:
- `_load_image_as_base64`: Converts an image file to a base64 string.
- `_extract_json_from_response`: Extracts JSON from a model response, handling common formatting issues.
- `analyze_image`: Synchronous function to analyze images using the Ollama vision model.
- `analyze_image_async`: Asynchronous version of `analyze_image`.
- `test_vision`: Tests the vision analysis functionality.

The functions are designed to handle image loading, request building, and response parsing. The `analyze_image` and `analyze_image_async` functions are the primary entry points for image analysis.

#### Patterns
- **Helper Functions**: `_load_image_as_base64` and `_extract_json_from_response` are helper functions used by `analyze_image` and `analyze_image_async`.
- **Configuration Management**: The `get_config` function is used to retrieve configuration settings, demonstrating a dependency injection pattern.

#### Dependencies
- **Standard Libraries**: `base64`, `json`, `logging`, `re`, `httpx`, `pathlib`, `typing`.
- **Internal Modules**: `vision.config` for configuration management.

#### Interfaces
- **Public Functions**:
  - `analyze_image(images, prompt, model=None, response_format="auto", timeout=None)`: Analyzes one or more images synchronously.
  - `analyze_image_async(images, prompt, model=None, response_format="auto", timeout=None)`: Analyzes one or more images asynchronously.
  - `test_vision(image_path=None)`: Tests the vision analysis functionality.

#### Database
- **References**: The file does not directly interact with any database tables or Neo4j labels. However, it relies on configuration settings that might be stored in a database.

#### Configuration
- **Configuration Files/Environment Variables**: The file uses `get_config()` to retrieve configuration settings, which likely come from a configuration file or environment variables.

#### Key Logic
- **Image Loading**: Converts image files to base64 strings.
- **Response Parsing**: Extracts JSON from model responses, handling common formatting issues.
- **Analysis**: Sends image data to the Ollama model for analysis, handling different response formats (text or JSON).

#### Integration Points
- **Ollama Model**: The file integrates with the Ollama model via HTTP requests to the Ollama API.
- **Configuration Management**: Uses `get_config()` to retrieve configuration settings, which might be managed through a configuration service.
- **Logging**: Uses the `logging` module to log errors and important events.

### Detailed Analysis of Functions

#### `_load_image_as_base64(image_path)`
- **Purpose**: Converts an image file to a base64 string.
- **Parameters**: `image_path` (Union[str, Path])
- **Returns**: Base64 string representation of the image.
- **Logic**: Converts the image file to a base64 string and handles file not found errors.

#### `_extract_json_from_response(text)`
- **Purpose**: Extracts JSON from a model response, handling common formatting issues.
- **Parameters**: `text` (str)
- **Returns**: Dictionary containing the extracted JSON or the raw response if parsing fails.
- **Logic**: Uses regular expressions to find JSON in markdown code blocks and attempts to parse the JSON.

#### `analyze_image(images, prompt, model=None, response_format="auto", timeout=None)`
- **Purpose**: Analyzes one or more images using the Ollama vision model synchronously.
- **Parameters**:
  - `images`: Single image path or list of image paths.
  - `prompt`: Analysis prompt.
  - `model`: Override default model.
  - `response_format`: Response format ("text", "json", or "auto").
  - `timeout`: Override default timeout.
- **Returns**: String for text format, dict for JSON format.
- **Logic**: Loads images, builds a request, sends it to the Ollama model, and processes the response.

#### `analyze_image_async(images, prompt, model=None, response_format="auto", timeout=None)`
- **Purpose**: Analyzes one or more images using the Ollama vision model asynchronously.
- **Parameters**: Same as `analyze_image`.
- **Returns**: Same as `analyze_image`.
- **Logic**: Similar to `analyze_image` but uses asynchronous HTTP requests.

#### `test_vision(image_path=None)`
- **Purpose**: Tests the vision analysis functionality.
- **Parameters**: `image_path` (Optional[str])
- **Returns**: Dictionary with test results.
- **Logic**: Tests Ollama connectivity, checks if the model is available, and optionally tests vision analysis with a provided image.

### Integration Points
- **Ollama API**: The file makes HTTP requests to the Ollama API to analyze images.
- **Configuration Management**: Uses `get_config()` to retrieve configuration settings.
- **Logging**: Uses the `logging` module to log errors and important events.

This file is a critical component of the Mythos system, providing the core functionality for image analysis and ensuring that the system can interact with the Ollama model effectively.
