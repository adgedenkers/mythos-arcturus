# walker.py

- **Language:** python
- **Lines:** 78
- **Path:** `/opt/mythos/tools/autodoc2/walker.py`

## Summary

This Python module defines a framework for language-agnostic code parsing. It provides base classes and data structures to extract structural information from source files, including functions, classes, imports, and file metadata. Language-specific parsers inherit from `LanguageWalker`, implementing `parse_file()` to return standardized `ParsedFile` objects containing detailed code structure and relationships, enabling uniform analysis across different programming languages.

## Classes

### `ParsedFunction`

Lines 15–24

### `ParsedClass`

Lines 28–35

### `ParsedImport`

Lines 39–43

### `ParsedFile`

Lines 47–55

### `LanguageWalker`

Lines 58–77

**Methods:** `parse_file`, `_decode`

## Imports

- `from dataclasses import dataclass, field`
- `from pathlib import Path`
- `from typing import List, Optional`
