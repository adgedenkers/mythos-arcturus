# config.py

- **Language:** python
- **Lines:** 92
- **Path:** `/opt/mythos/tools/autodoc2/config.py`

## Summary

This Python file handles configuration for AutoDoc2 by loading Neo4j and Ollama settings from a `.env` file (defaulting to `/opt/mythos/.env`) and command-line arguments, with CLI values taking precedence. It defines a `Config` dataclass to store connection details, crawl behavior flags, and directory paths, while the `load_config` function resolves output directories based on the target path and merges environment variables with explicit arguments.

## Classes

### `Config`

Lines 13–31

## Functions

### `_parse_env_file()`

Lines 34–49

**Calls:** `k.strip`, `line.split`, `line.startswith`, `path.exists`, `path.read_text`, `path.read_text().splitlines`, `raw.strip`, `v.strip`, `v.strip().strip`, `v.strip().strip('"').strip`

### `load_config()`

Lines 52–91

**Calls:** `Config`, `Path`, `Path('/opt/mythos').resolve`, `_parse_env_file`, `env.get`, `os.environ.get`, `output_dir.resolve`, `target.resolve`

## Imports

- `import os`
- `from dataclasses import dataclass, field`
- `from pathlib import Path`
- `from typing import Optional, List`
