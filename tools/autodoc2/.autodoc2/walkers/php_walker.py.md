# walkers/php_walker.py

- **Language:** python
- **Lines:** 282
- **Path:** `/opt/mythos/tools/autodoc2/walkers/php_walker.py`

## Summary

This Python file implements a PHP code parser using the tree-sitter library to extract structural elements like functions, classes, interfaces, traits, and imports. It handles PHP's namespace declarations to qualify symbol names, and processes syntax trees resiliently even with partial or error-prone code. The parser builds a model of the codebase by walking the AST, capturing definitions and their relationships (like method calls and class inheritance) into structured objects for further analysis.

## Classes

### `PhpWalker(LanguageWalker)`

Lines 30–281

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_find_namespace`, `_walk`, `_handle_function`, `_handle_class`, `_handle_method`, `_handle_use`, `_extract_calls`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
