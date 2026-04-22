# walkers/sql_walker.py

- **Language:** python
- **Lines:** 184
- **Path:** `/opt/mythos/tools/autodoc2/walkers/sql_walker.py`

## Summary

This Python module uses tree-sitter to parse SQL files into structured code analysis data, mapping CREATE TABLE/VIEW/INDEX/FUNCTION/PROCEDURE/TRIGGER statements to ParsedClass or ParsedFunction objects with metadata like names, line numbers, and SQL-specific kind tags. It handles syntax errors gracefully by marking error nodes instead of failing, and treats SQL's lack of imports by leaving import fields empty while maintaining compatibility with cross-language query systems through consistent class/function representations.

## Classes

### `SqlWalker(LanguageWalker)`

Lines 34–183

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_walk`, `_extract_object_name`, `_kind_from_node_type`, `_handle_create_structural`, `_handle_create_callable`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
