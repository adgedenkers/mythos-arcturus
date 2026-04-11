# finance/parsers.py

**Language:** python
**Stream:** SYS
**Module:** Finance System
**Lines:** 436

---

### File: finance/parsers.py

#### Purpose
This file contains classes and functions for parsing CSV files exported from different banks, specifically USAA and Sunmark. It normalizes the transaction data into a consistent format and provides methods to detect and parse the specific formats of these banks.

#### Architecture
- **Classes**:
  - `Transaction`: A data class representing a normalized transaction record.
  - `BaseParser`: An abstract base class for bank parsers, defining the interface for parsing and detecting file formats.
  - `USAAParser`: A concrete parser for USAA bank exports.
  - `SunmarkParser`: A concrete parser for Sunmark bank exports.
- **Top-level Functions**:
  - `detect_parser`: Automatically detects which parser to use for a given file.
  - `get_parser`: Retrieves a parser by name.
  - `compute_hash`: Static method to generate a deduplication hash for transactions.

#### Patterns
- **Abstract Factory**: The `BaseParser` class defines an abstract interface for parsers, and concrete parsers (`USAAParser`, `SunmarkParser`) implement this interface.
- **Factory Method**: The `detect_parser` function acts as a factory method to instantiate the appropriate parser based on the file format.

#### Dependencies
- **Imports**: `csv`, `hashlib`, `re`, `dataclasses`, `datetime`, `pathlib`, `typing`, `abc`
- **Database**: References to various PostgreSQL tables and data structures (e.g., `Transaction` class).

#### Interfaces
- **Public Methods**:
  - `detect_parser(file_path)`: Detects the appropriate parser for a given file.
  - `get_parser(parser_name)`: Retrieves a parser by its name.
  - `BaseParser.parse_file(file_path, account_identifier)`: Abstract method to parse a CSV file and return normalized transactions.
  - `BaseParser.detect(file_path)`: Abstract method to check if the parser can handle the given file.
- **Classes**:
  - `Transaction`: Represents a normalized transaction record.
  - `BaseParser`: Abstract base class for bank parsers.
  - `USAAParser`: Concrete parser for USAA bank exports.
  - `SunmarkParser`: Concrete parser for Sunmark bank exports.

#### Database
- **References**: The `Transaction` class is used to store transaction data, which is likely persisted in a PostgreSQL database. No specific table names are mentioned, but the `Transaction` class is likely mapped to a corresponding table.

#### Configuration
- **Environment Variables**: No specific environment variables are used.
- **Config Files**: No configuration files are referenced.

#### Key Logic
- **Transaction Normalization**: The `Transaction` class normalizes transaction data from different bank formats into a consistent structure.
- **File Parsing**: The `USAAParser` and `SunmarkParser` classes implement the `parse_file` method to read and parse CSV files according to their respective formats.
- **Detection**: The `detect` method in each parser class checks if the file can be handled by that parser.
- **Hash Generation**: The `compute_hash` method generates a unique hash for each transaction to ensure deduplication.

#### Integration Points
- **Mythos Subsystems**: This file integrates with the Mythos system by providing normalized transaction data, which can be further processed by other subsystems such as categorization, reporting, or database storage.
- **Database Integration**: The `Transaction` class is likely used to store transaction data in the PostgreSQL database, which is part of the Mythos infrastructure.
- **File Handling**: The parsers read CSV files from the file system, which are likely provided by the Mythos system's file management or user input subsystems.

### Detailed Analysis

#### `Transaction` Class
- **Purpose**: Represents a normalized transaction record.
- **Methods**:
  - `compute_hash`: Static method to generate a deduplication hash for transactions.
- **Attributes**: Various fields representing transaction details such as date, description, amount, balance, category, merchant name, transaction type, pending status, and bank transaction ID.

#### `BaseParser` Class
- **Purpose**: Abstract base class for bank parsers.
- **Methods**:
  - `parse_file`: Abstract method to parse a CSV file and return normalized transactions.
  - `detect`: Abstract method to check if the parser can handle the given file.

#### `USAAParser` Class
- **Purpose**: Concrete parser for USAA bank exports.
- **Methods**:
  - `detect`: Checks if the file is in USAA format by looking for specific columns.
  - `parse_file`: Parses the USAA CSV export and returns a list of `Transaction` objects.

#### `SunmarkParser` Class
- **Purpose**: Concrete parser for Sunmark bank exports.
- **Methods**:
  - `detect`: Checks if the file is in Sunmark format by looking for account header metadata.
  - `parse_file`: Parses the Sunmark CSV export and returns a list of `Transaction` objects.
  - `_clean_description`: Cleans up the Sunmark description for display.
  - `_parse_merchant_location`: Parses the merchant name and location from transaction text.
  - `_smart_title_case`: Converts text to title case with special handling for abbreviations and apostrophes.

#### Top-level Functions
- **`detect_parser`**: Automatically detects the appropriate parser for a given file.
- **`get_parser`**: Retrieves a parser by its name.
- **`compute_hash`**: Static method to generate a deduplication hash for transactions.

### Summary
The `finance/parsers.py` file is a critical component of the Mythos system, responsible for parsing and normalizing transaction data from different bank CSV formats. It uses abstract classes and concrete parsers to handle specific formats, ensuring that the data can be consistently processed and stored in the system's database.
