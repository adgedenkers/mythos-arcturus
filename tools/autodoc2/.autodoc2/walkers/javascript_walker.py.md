# walkers/javascript_walker.py

- **Language:** python
- **Lines:** 369
- **Path:** `/opt/mythos/tools/autodoc2/walkers/javascript_walker.py`

## Summary

This script uses the tree-sitter library to analyze JavaScript/JSX files, extracting functions (including generators and arrow functions), classes and their methods, imports (ES modules and CommonJS), and tracks call expressions. It builds structured data about the code's structure while handling syntax errors gracefully and supporting multiple file types (.js, .jsx, etc.).

## Classes

### `JavaScriptWalker(LanguageWalker)`

Lines 36–368

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_walk_top_level`, `_handle_function_declaration`, `_handle_variable_declarator_function`, `_is_async`, `_handle_class_declaration`, `_handle_method_definition`, `_handle_import_statement`, `_maybe_handle_require`, `_extract_calls`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
