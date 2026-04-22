# filters.py

- **Language:** python
- **Lines:** 132
- **Path:** `/opt/mythos/tools/autodoc2/filters.py`

## Summary

This file defines filters for skipping common build/cache directories and generated files during codebase crawling, maps file extensions to programming languages, and provides functions to iterate over source files while applying include/exclude patterns. It yields (file_path, language) tuples for every supported file that passes the filters.

## Functions

### `should_skip_dir()`

Lines 75–76

**Calls:** `dirname.startswith`

### `should_skip_file()`

Lines 79–83

**Calls:** `fnmatch.fnmatch`

### `language_for_path()`

Lines 86–92

**Calls:** `EXTENSION_LANGUAGE_MAP.get`, `name_lower.endswith`, `path.name.lower`, `path.suffix.lower`

### `matches_any()`

Lines 95–106

**Calls:** `fnmatch.fnmatch`, `path.as_posix`, `path.relative_to`, `path.relative_to(root).as_posix`

### `iter_source_files()`

Lines 109–131

**Calls:** `Path`, `__import__`, `__import__('os').walk`, `language_for_path`, `matches_any`, `root.resolve`, `should_skip_dir`, `should_skip_file`

## Imports

- `from pathlib import Path`
- `import fnmatch`
- `from typing import Optional, List`
