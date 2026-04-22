# walkers/python_walker.py

- **Language:** python
- **Lines:** 264
- **Path:** `/opt/mythos/tools/autodoc2/walkers/python_walker.py`

## Summary

This Python file defines a `PythonWalker` class that uses the tree-sitter library to parse Python source code, extracting top-level functions (including async), classes (with methods and inheritance), import statements, and function/method call expressions. It converts file paths to module names, handles syntax errors gracefully, and builds structured data objects (`ParsedFile`, `ParsedClass`, `ParsedFunction`, `ParsedImport`) to represent the code's structure, including line numbers, docstrings, and call graphs. The walker is designed for robustness and integrates with a broader system for code analysis or documentation.

## Classes

### `PythonWalker(LanguageWalker)`

Lines 27–263

**Methods:** `__init__`, `_module_name_from_path`, `_text`, `_walk_top_level`, `_handle_class`, `_walk_class_body`, `_handle_function`, `_extract_docstring`, `_extract_calls`, `_handle_import`, `_handle_import_from`, `parse_file`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
