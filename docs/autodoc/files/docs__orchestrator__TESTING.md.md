# docs/orchestrator/TESTING.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 370

---

### Purpose
The `TESTING.md` file serves as a comprehensive guide for the test framework in the Mythos system. It details the components, usage, and integration of the test suite management system, including `TestQuestion`, `TestSuite`, and `TestLoader`.

### Architecture
The file is structured into several sections, each detailing different aspects of the test framework:
- **Overview**: Describes the components and purpose.
- **Quick Start**: Provides a step-by-step guide to creating and managing test suites.
- **TestQuestion**: Explains the creation and validation of individual test questions.
- **TestSuite**: Details the creation, management, and validation of test suites.
- **TestLoader**: Describes the loading and saving of test suites to JSON and the database.
- **File Format**: Outlines the JSON format for test suites.
- **Directory Structure**: Shows the directory structure for test suites.
- **Examples**: Provides complete examples of using the framework.
- **Next Steps**: Outlines future phases and enhancements.

### Patterns
- **Builder Pattern**: Used for constructing `TestQuestion` and `TestSuite` objects.
- **Factory Pattern**: `TestLoader` can be seen as a factory for loading and saving test suites.

### Dependencies
- **Python Standard Library**: `asyncio` for asynchronous operations.
- **Custom Modules**: `bench` module for `TestQuestion`, `TestSuite`, and `TestLoader`.

### Interfaces
- **TestQuestion**: Methods like `validate`, `to_dict`, `from_dict`.
- **TestSuite**: Methods like `add_question`, `remove_question`, `get_question`, `get_statistics`, `validate`.
- **TestLoader**: Methods like `load_from_json`, `save_to_json`, `load_from_database`, `save_to_database`, `list_json_files`, `list_suites`.

### Database
- **Tables/Labels**: The `TestLoader` interacts with a database to save and load test suites, though specific table names are not mentioned in the file.

### Configuration
- **Environment Variables**: No specific environment variables are mentioned.
- **Config Files**: No specific configuration files are mentioned.

### Key Logic
- **TestQuestion**: Validation and conversion to/from dictionary.
- **TestSuite**: Management of questions, validation, and statistics.
- **TestLoader**: Loading and saving test suites to JSON and the database.

### Integration Points
- **Mythos Subsystems**: The test framework integrates with the database subsystem for saving and loading test suites. It also integrates with the JSON file system for saving and loading test suites in JSON format.

### Detailed Analysis

#### TestQuestion
- **Purpose**: Represents an individual test question with grading criteria.
- **Architecture**: Contains attributes like `text`, `correct_answer`, `answer_type`, `difficulty`, `tags`, `grading_criteria`, and `metadata`.
- **Key Logic**: Validation and conversion to/from dictionary.
- **Methods**:
  - `validate()`: Validates the question.
  - `to_dict()`: Converts the question to a dictionary.
  - `from_dict(data)`: Creates a question from a dictionary.

#### TestSuite
- **Purpose**: Manages a collection of related test questions.
- **Architecture**: Contains attributes like `name`, `category`, `description`, and `version`.
- **Key Logic**: Management of questions, validation, and statistics.
- **Methods**:
  - `add_question(question)`: Adds a question to the suite.
  - `remove_question(question_id)`: Removes a question from the suite.
  - `get_question(question_id)`: Retrieves a question from the suite.
  - `get_statistics()`: Returns statistics about the suite.
  - `validate()`: Validates the suite.

#### TestLoader
- **Purpose**: Handles loading and saving of test suites to JSON and the database.
- **Architecture**: Provides methods for loading and saving test suites.
- **Key Logic**: Loading and saving test suites to JSON and the database.
- **Methods**:
  - `load_from_json(path)`: Loads a test suite from a JSON file.
  - `save_to_json(suite, path)`: Saves a test suite to a JSON file.
  - `load_from_database(suite_id)`: Loads a test suite from the database.
  - `save_to_database(suite)`: Saves a test suite to the database.
  - `list_json_files(category)`: Lists JSON files for a given category.
  - `list_suites(category, public_only)`: Lists test suites from the database.

### Next Steps
- **Phase 1.4**: Introduction of a Grading System with classes for grading and scoring.
- **Phase 1.5**: Development of a Test Runner to execute tests against models and track results.

This documentation provides a comprehensive overview of the test framework in the Mythos system, detailing its components, usage, and integration points.
