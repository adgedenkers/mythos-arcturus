# walkers/bash_walker.py

- **Language:** python
- **Lines:** 159
- **Path:** `/opt/mythos/tools/autodoc2/walkers/bash_walker.py`

## Summary

This Bash parser extracts function definitions, source/. imports, and command call relationships from shell scripts using tree-sitter. It builds a structured representation of the code including function names, their line numbers, and the commands they invoke, while handling syntax errors and nested structures gracefully. The output focuses on call graph data since Bash lacks classes.

## Classes

### `BashWalker(LanguageWalker)`

Lines 24–158

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_walk`, `_handle_function`, `_maybe_handle_source`, `_extract_calls`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
