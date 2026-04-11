# sdip/sdip_chunker.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 576

---

### File: `sdip/sdip_chunker.py`

#### Purpose
This file contains the logic to read and split various types of documents (e.g., text, markdown, JSON, HTML, code) into smaller, addressable chunks. It provides a single entry point function `chunk_file` that handles different file formats and delegates the chunking logic to specialized functions.

#### Architecture
The file is structured around a `Chunk` class and several top-level functions:
- **Classes**: `Chunk` represents a single addressable section of a document.
- **Functions**:
  - `chunk_file`: Main entry point to read and split a file into chunks.
  - `_read_text`: Reads text files with encoding handling.
  - `_read_docx`: Reads `.docx` files and returns sections.
  - `_chunk_markdown`: Splits markdown content into chunks.
  - `_split_by_headers`: Splits content at header boundaries.
  - `_split_by_paragraphs`: Splits content on paragraph boundaries.
  - `_split_by_sentences`: Splits long text blocks at sentence boundaries.
  - `_chunk_json`: Splits JSON files into chunks based on top-level keys.
  - `_chunk_html`: Splits HTML content into chunks.
  - `_chunk_code`: Splits code files at function/class boundaries.
  - `_chunk_python`: Splits Python files on top-level `def`/`class` boundaries.
  - `_chunk_shell`: Splits shell scripts on function boundaries.
  - `_chunk_js`: Splits JavaScript/TypeScript files on function/class/export boundaries.
  - `_split_on_pattern`: Generic splitter using a regex pattern for boundaries.
  - `_chunk_docx`: Chunks already-parsed `.docx` sections.
  - `_extract_first_heading`: Extracts the first markdown heading from content.

#### Patterns
- **Strategy Pattern**: The `chunk_file` function delegates to different chunking strategies based on the file type.
- **Factory Pattern**: `_read_text` and `_read_docx` act as factories for reading different file types.

#### Dependencies
- **Imports**: `re`, `json`, `sys`, `pathlib`, `dataclasses`, `typing`, `config`
- **Config**: Uses configuration settings from `config` (e.g., `MAX_CHUNK_WORDS`, `MIN_CHUNK_WORDS`, `SMALL_FILE_THRESHOLD`).

#### Interfaces
- **Public Interface**: `chunk_file(filepath: str | Path) -> list[Chunk]`
- **Internal Interfaces**: Various internal functions for reading and chunking different file types.

#### Database
- **PostgreSQL Tables**: `addressable`, `sdip_chunker`, `pathlib`, `dataclasses`, `typing`, `config`, `chunks`, `docx`, `previous`, `groups`, `first`, `content`

#### Configuration
- **Config File/Environment Variables**: Uses settings from `config` module like `MAX_CHUNK_WORDS`, `MIN_CHUNK_WORDS`, `SMALL_FILE_THRESHOLD`, `SUPPORTED_FORMATS`, `BINARY_FORMATS`.

#### Key Logic
- **Chunking Strategies**:
  - **Markdown**: Splits based on headers, paragraphs, and sentences.
  - **JSON**: Splits based on top-level keys.
  - **HTML**: Splits based on section-level tags, falling back to markdown splitting.
  - **Code**: Splits based on function/class boundaries, falling back to line-based chunking.
  - **Docx**: Parses `.docx` files into sections and chunks them.
- **Chunk Class**: Represents a chunk with `chunk_index`, `content_text`, `word_count`, and `parent_heading`.

#### Integration Points
- **Mythos Subsystems**: This file integrates with the document ingestion and processing subsystems of Mythos. It is likely used by other parts of the system to preprocess documents before storing or indexing them.

### Detailed Analysis

#### Classes
- **Chunk**: Represents a single addressable section of a document.
  - **Attributes**: `chunk_index`, `content_text`, `word_count`, `parent_heading`
  - **Methods**: `to_dict()`

#### Top-level Functions
- **chunk_file(filepath: str | Path) -> list[Chunk]**:
  - Reads a file and splits it into chunks based on its content type.
  - Handles different file formats and delegates to specialized chunking functions.

- **_read_text(filepath: Path) -> str**:
  - Reads a text file with encoding handling.
  - Tries different encodings (`utf-8`, `latin-1`, `cp1252`) and falls back to a lossy read.

- **_read_docx(filepath: Path) -> list[dict]**:
  - Reads a `.docx` file and returns a list of sections with headings and text.
  - Requires `python-docx` for parsing.

- **_chunk_markdown(content: str) -> list[Chunk]**:
  - Splits markdown content into chunks based on headers, paragraphs, and sentences.
  - Handles small files as a single chunk.

- **_split_by_headers(content: str, header_matches: list) -> list[Chunk]**:
  - Splits content at header boundaries.
  - Handles merging short sections and sub-splitting long sections.

- **_split_by_paragraphs(content: str, parent_heading: str = None) -> list[Chunk]**:
  - Splits content on paragraph boundaries.
  - Handles merging short paragraphs and splitting long paragraphs by sentences.

- **_split_by_sentences(text: str, parent_heading: str = None) -> list[Chunk]**:
  - Splits a long text block at sentence boundaries.
  - Handles merging short sentences and splitting long sentences.

- **_chunk_json(filepath: Path) -> list[Chunk]**:
  - Splits JSON files into chunks based on top-level keys.
  - Handles JSON decoding errors by treating the file as plain text.

- **_chunk_html(content: str) -> list[Chunk]**:
  - Splits HTML content into chunks based on section-level tags.
  - Falls back to markdown splitting on raw text.

- **_chunk_code(content: str, suffix: str) -> list[Chunk]**:
  - Splits code files at function/class boundaries.
  - Falls back to line-based chunking if no clear boundaries are found.

- **_chunk_python(content: str) -> list[Chunk]**:
  - Splits Python files on top-level `def`/`class` boundaries.

- **_chunk_shell(content: str) -> list[Chunk]**:
  - Splits shell scripts on function boundaries.

- **_chunk_js(content: str) -> list[Chunk]**:
  - Splits JavaScript/TypeScript files on function/class/export boundaries.

- **_split_on_pattern(content: str, pattern: str) -> list[Chunk]**:
  - Generic splitter using a regex pattern for boundaries.

- **_chunk_docx(sections: list[dict]) -> list[Chunk]**:
  - Chunks already-parsed `.docx` sections.

- **_extract_first_heading(content: str) -> str**:
  - Extracts the first markdown heading from content.

### Summary
This file provides a robust mechanism for splitting various document types into smaller, manageable chunks. It handles different file formats and uses specialized strategies for each, ensuring that the chunks are appropriately sized and structured. The `Chunk` class and the various chunking functions work together to provide a flexible and efficient document chunking system.
