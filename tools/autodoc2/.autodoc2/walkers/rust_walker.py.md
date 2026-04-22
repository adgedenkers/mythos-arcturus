# walkers/rust_walker.py

- **Language:** python
- **Lines:** 282
- **Path:** `/opt/mythos/tools/autodoc2/walkers/rust_walker.py`

## Summary

This Rust walker uses tree-sitter to parse Rust source files into structured metadata. It identifies and extracts functions, structs, enums, traits, unions, type aliases, and imports, tracking their relationships (like methods inside impl blocks) and qualified names through module hierarchy. The parser handles nested modules, syntax errors gracefully, and builds a program representation with line numbers, parent-child relationships, and call references.

## Classes

### `RustWalker(LanguageWalker)`

Lines 34–281

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_qual`, `_walk_items`, `_extract_name`, `_handle_function`, `_is_async`, `_handle_typedef`, `_handle_impl`, `_handle_mod`, `_handle_use`, `_extract_calls`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
