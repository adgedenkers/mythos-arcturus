# eval/results/search_life_events/20260305_061912/report.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 108

---

### Purpose
The `report.json` file contains the evaluation results of the `search_life_events` plan, which involves generating and testing a Python script for searching life events in the Mythos system. The report details each step of the script generation, including the instructions, test results, and final code lines.

### Architecture
The JSON file is structured as a dictionary with several key-value pairs:
- `plan_id`: Identifier for the plan.
- `model`: The AI model used for generating the script.
- `timestamp`: Timestamp of the evaluation.
- `total_passes`: Total number of passes through the script generation process.
- `total_ollama_calls`: Total number of calls made to the Ollama model.
- `final_parse`: Boolean indicating if the final parse check passed.
- `final_import`: Boolean indicating if the final import check passed.
- `final_behavioral`: Details of the final behavioral test.
- `steps`: A list of dictionaries, each representing a step in the script generation process.

### Patterns
- **Step-wise Execution**: The report follows a step-wise execution pattern, where each step is a dictionary containing instructions, test results, and other metadata.
- **Recursive Testing**: The final step (`pass 6`) includes a recursive test to ensure the script is production-ready.

### Dependencies
- **Environment Variables**: The script relies on environment variables such as `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT`.
- **Libraries**: The script imports `os`, `logging`, `psycopg2`, `psycopg2.extras.RealDictCursor`, and `dotenv`.

### Interfaces
- **SkillResponse**: The script generates `SkillResponse` objects to return results, including data, summary, and error messages.
- **Database Connection**: The script uses a `_get_conn` function to establish a connection to the PostgreSQL database.

### Database
- **Tables**: The script interacts with the `life_events` table in the PostgreSQL database.
- **Queries**: The script performs SELECT queries on the `life_events` table to retrieve life events based on search terms, domain, and person filters.

### Configuration
- **Environment Variables**: The script uses environment variables to configure the PostgreSQL database connection.
- **Model Configuration**: The report includes the model (`qwen3-coder:30b`) used for generating the script.

### Key Logic
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables.
- **_extract_search_terms**: Processes the input message to extract search terms by removing trigger phrases and stripping punctuation.
- **_detect_filters**: Detects domain and person filters from the input message.
- **_search_events**: Dynamically builds and executes a SQL query to search for life events based on the extracted terms and filters.
- **_format_results**: Formats the query results into a dictionary with truncated descriptions and other details.
- **_build_summary**: Builds a summary of the search results.
- **execute**: Main function that orchestrates the extraction of search terms, detection of filters, execution of the search, and formatting of results.

### Integration Points
- **Ollama Model**: The script generation process involves multiple calls to the Ollama model (`qwen3-coder:30b`) to generate and refine the Python script.
- **PostgreSQL Database**: The script interacts with the PostgreSQL database to retrieve life events.
- **SkillResponse**: The script returns `SkillResponse` objects, which are likely used by other components of the Mythos system to handle the results of the life event search.

### Detailed Analysis of Steps
1. **Step 1**: Generates the file skeleton with the `_get_conn` function and the `SearchLifeEventsSkill` class.
2. **Step 2**: Implements `_extract_search_terms` and `_detect_filters`.
3. **Step 3**: Implements `_search_events` to dynamically build and execute SQL queries.
4. **Step 4**: Implements `_format_results` and `_build_summary` to format and summarize the search results.
5. **Step 5**: Implements the `execute` function to orchestrate the search process and return the results.
6. **Step 6**: Final review to ensure the script is production-ready.

Each step includes test results, elapsed time, and the final number of code lines generated.
