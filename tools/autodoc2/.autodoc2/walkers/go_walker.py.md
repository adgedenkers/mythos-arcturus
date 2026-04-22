# walkers/go_walker.py

- **Language:** python
- **Lines:** 252
- **Path:** `/opt/mythos/tools/autodoc2/walkers/go_walker.py`

## Summary

This Python module defines a Go code parser using tree-sitter to extract package declarations, imports, functions, methods, and type declarations (including structs, interfaces, and type aliases). It builds a structured representation of Go source files by analyzing syntax nodes, resolving method receiver types as if they were class relationships, and handling grouped imports and syntax errors gracefully. The output is a parsed file object containing line-numbered functions, qualified names, and call relationships while treating Go's method receivers as class-like parent types.

## Classes

### `GoWalker(LanguageWalker)`

Lines 31–251

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_find_package`, `_walk_top_level`, `_handle_function`, `_handle_method`, `_extract_receiver_type`, `_handle_type_declaration`, `_handle_type_spec`, `_handle_import`, `_handle_import_spec`, `_extract_calls`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
