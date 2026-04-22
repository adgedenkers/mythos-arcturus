# walkers/typescript_walker.py

- **Language:** python
- **Lines:** 123
- **Path:** `/opt/mythos/tools/autodoc2/walkers/typescript_walker.py`

## Summary

This file implements a TypeScript code parser that extends a JavaScript parser to handle TypeScript-specific constructs like interfaces and type aliases. It uses Tree-Sitter parsers for both `.ts` and `.tsx` files, extracting type declarations into class-like structures with special tags to distinguish them from regular classes. The parser adds interfaces and type aliases to the output with metadata like names, module paths, and inheritance relationships.

## Classes

### `TypeScriptWalker(JavaScriptWalker)`

Lines 43–112

**Methods:** `__init__`, `_walk_top_level`, `_handle_interface`, `_handle_type_alias`

### `TsxWalker(TypeScriptWalker)`

Lines 115–122

## Imports

- `from pathlib import Path`
- `from typing import Optional`
- `from ..walker import ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
- `from .javascript_walker import JavaScriptWalker`
