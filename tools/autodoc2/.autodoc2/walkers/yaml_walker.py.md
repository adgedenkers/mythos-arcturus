# walkers/yaml_walker.py

- **Language:** python
- **Lines:** 127
- **Path:** `/opt/mythos/tools/autodoc2/walkers/yaml_walker.py`

## Summary

This Python module defines a YAML file parser that extracts top-level keys (like 'services' or 'version') from YAML documents using tree-sitter syntax analysis. It treats each key as a "class" tagged with `__yaml_key__`, enabling codebase-wide queries about YAML structures while ignoring functions and imports (which YAML doesn't have). The parser handles multi-document YAML files and gracefully skips syntax errors.

## Classes

### `YamlWalker(LanguageWalker)`

Lines 31–126

**Methods:** `__init__`, `parse_file`, `_module_name_from_path`, `_text`, `_handle_document`, `_find_top_mapping`, `_handle_pair`

## Imports

- `from pathlib import Path`
- `from typing import List, Optional`
- `from ..walker import LanguageWalker, ParsedFile, ParsedClass, ParsedFunction, ParsedImport`
