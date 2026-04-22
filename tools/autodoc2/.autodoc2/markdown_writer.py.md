# markdown_writer.py

- **Language:** python
- **Lines:** 114
- **Path:** `/opt/mythos/tools/autodoc2/markdown_writer.py`

## Summary

This Python module generates Markdown documentation for AutoDoc2 by creating a `.md` file for each source code file, preserving their original directory structure under a specified output folder. It includes metadata like language, line count, and file path, along with optional LLM-generated summaries, class/function details (names, parameters, docstrings, and calls), imports, and parse errors. A root `index.md` file aggregates statistics and links to all generated docs.

## Classes

### `MarkdownWriter`

Lines 14–113

**Methods:** `__init__`, `write_file`, `write_index`

## Imports

- `from pathlib import Path`
- `from typing import Optional`
- `from .walker import ParsedFile`
