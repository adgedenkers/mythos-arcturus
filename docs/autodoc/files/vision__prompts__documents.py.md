# vision/prompts/documents.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 52

---

### File: vision/prompts/documents.py

#### Purpose
This file contains predefined prompts used for various types of document/text analysis tasks, such as reading, summarizing, genealogical data extraction, handwriting transcription, and receipt information extraction.

#### Architecture
The file is structured as a collection of string constants, each representing a specific prompt for a document analysis task. There are no classes or functions defined in this file; it solely serves as a repository for these prompts.

#### Patterns
No design patterns are used in this file as it is a simple collection of string constants.

#### Dependencies
This file does not import any external libraries or modules. It is a standalone file that only contains string literals.

#### Interfaces
This file exposes several string constants that can be imported and used by other parts of the Mythos system for document analysis tasks. The constants are:
- `READ_DOCUMENT`
- `SUMMARIZE_DOCUMENT`
- `GENEALOGY_DOCUMENT`
- `HANDWRITING_TRANSCRIPTION`
- `RECEIPT_EXTRACTION`

#### Database
This file does not interact with any database tables or Neo4j labels directly. The provided DB references appear to be placeholders or errors, as they do not correspond to any actual database operations within the file.

#### Configuration
This file does not use any configuration files or environment variables. The prompts are hardcoded as string literals.

#### Key Logic
The key logic in this file is the definition of the prompts themselves. Each prompt is designed to guide the AI in performing a specific type of document analysis:
- `READ_DOCUMENT`: Extracts all readable text from a document.
- `SUMMARIZE_DOCUMENT`: Provides a structured summary of the document.
- `GENEALOGY_DOCUMENT`: Extracts genealogical information in a structured format.
- `HANDWRITING_TRANSCRIPTION`: Transcribes handwritten text from an image.
- `RECEIPT_EXTRACTION`: Extracts information from a receipt in a structured format.

#### Integration Points
This file integrates with other parts of the Mythos system by providing the prompts used in document analysis tasks. These prompts can be used by other modules (e.g., FastAPI endpoints, Ollama integration) to interact with the AI for document analysis.

### Summary
The `documents.py` file in the `vision/prompts` directory serves as a repository for predefined prompts used in various document/text analysis tasks. It does not contain any complex logic or dependencies and is designed to be imported and used by other parts of the Mythos system for guiding AI tasks related to document analysis.
