# walkers/json_walker.py

- **Language:** python
- **Lines:** 136
- **Path:** `/opt/mythos/tools/autodoc2/walkers/json_walker.py`

## Summary

This Python module defines a JSON parser that extracts top-level keys and arrays from JSON files (like package.json or config files) using the tree-sitter library. It converts each key into a class marker (`__json_key__`) and root-level arrays into a special class (`__root_array__`), enabling queries about JSON structure across codebases. The parser is resilient to syntax errors and skips functions/imports since JSON has none.

## Classes

### `JsonWalker(LanguageWalker)`

Lines 34–135

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_find_top_value`, `_emit_object_keys`, `_emit_pair`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
