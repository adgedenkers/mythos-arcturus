# walkers/__init__.py

- **Language:** python
- **Lines:** 45
- **Path:** `/opt/mythos/tools/autodoc2/walkers/__init__.py`

## Summary

This file registers language-specific walker classes for code analysis, mapping language identifiers to their respective walker instances (e.g., Python → PythonWalker). It provides `get_walker()` to retrieve a walker by language name and `supported_languages()` to list all registered languages. New languages are added by implementing a walker subclass, importing it here, and adding it to the registry dictionary.

## Functions

### `get_walker()`

Lines 39–40

**Calls:** `WALKER_REGISTRY.get`

### `supported_languages()`

Lines 43–44

**Calls:** `WALKER_REGISTRY.keys`, `sorted`

## Imports

- `from typing import Dict, Optional`
- `from ..walker import LanguageWalker`
- `from .python_walker import PythonWalker`
- `from .javascript_walker import JavaScriptWalker`
- `from .typescript_walker import TypeScriptWalker, TsxWalker`
- `from .sql_walker import SqlWalker`
- `from .php_walker import PhpWalker`
- `from .go_walker import GoWalker`
- `from .bash_walker import BashWalker`
- `from .yaml_walker import YamlWalker`
- `from .json_walker import JsonWalker`
- `from .rust_walker import RustWalker`
