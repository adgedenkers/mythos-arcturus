# workers/vision_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 172

---

### File: workers/vision_worker.py

#### Purpose
This file contains the logic for analyzing images using the Llama Vision model via Ollama and storing the analysis results in a PostgreSQL database.

#### Architecture
The file consists of several functions:
- `get_db()`: Establishes a connection to the PostgreSQL database.
- `analyze_image(image_path: str)`: Analyzes an image using the Llama Vision model and returns the analysis results.
- `store_analysis(photo_id: str, analysis: Dict[str, Any])`: Stores the analysis results in the PostgreSQL database.
- `process_vision(payload: Dict[str, Any])`: The main entry point for the vision analysis worker, which orchestrates the image analysis and storage process.

#### Patterns
- **Singleton Pattern**: The `get_db()` function can be considered a singleton pattern as it ensures a single database connection is used throughout the file.
- **Facade Pattern**: The `process_vision()` function acts as a facade, abstracting the complex process of image analysis and storage into a single function call.

#### Dependencies
- `os`: For environment variable handling.
- `base64`: For encoding image data.
- `json`: For JSON handling.
- `logging`: For logging.
- `requests`: For making HTTP requests to the Llama Vision API.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `Path` from `pathlib`: For file path handling.
- `datetime`: For timestamp operations.

#### Interfaces
- `process_vision(payload: Dict[str, Any]) -> Dict[str, Any]`: The main entry point for the vision analysis worker, which takes a payload containing the photo ID and file path, and returns a dictionary with the status of the operation and additional details.

#### Database
- **PostgreSQL Tables/Lables**:
  - `media_files`: The table where the analysis results are stored. The function updates the `analysis_data`, `auto_tags`, `processed`, and `processed_at` fields.

#### Configuration
- Environment variables:
  - `OLLAMA_HOST`: The host for the Ollama API.
  - `OLLAMA_VISION_MODEL`: The model used for vision analysis.
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Database connection details.

#### Key Logic
1. **Image Analysis**:
   - The `analyze_image()` function reads an image file, encodes it in base64, and sends it to the Llama Vision API with a structured prompt.
   - The API response is expected to be in JSON format, which is then parsed and returned.

2. **Storing Analysis Results**:
   - The `store_analysis()` function updates the `media_files` table in the PostgreSQL database with the analysis results, including the analysis data, auto-generated tags, and processing status.

3. **Main Workflow**:
   - The `process_vision()` function orchestrates the entire process by first checking if the image file exists, then analyzing the image, and finally storing the results in the database.

#### Integration Points
- **Ollama API**: The `analyze_image()` function interacts with the Ollama API to perform image analysis.
- **PostgreSQL Database**: The `store_analysis()` function interacts with the PostgreSQL database to store the analysis results.
- **Message Queue/Task Queue**: Although not explicitly shown in the code, this worker is likely integrated with a task queue (e.g., Celery) that sends payloads to this worker for processing.

### Summary
The `vision_worker.py` file is a critical component of the Mythos system, responsible for analyzing images using the Llama Vision model and storing the results in a PostgreSQL database. It integrates with the Ollama API for image analysis and uses environment variables for configuration. The main entry point, `process_vision()`, handles the entire workflow, from file validation to database storage.
