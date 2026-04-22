# engine.py

- **Language:** python
- **Lines:** 217
- **Path:** `/opt/mythos/tools/autodoc2/engine.py`

## Summary

This Python script defines an `AutodocEngine` that automates documenting codebases by crawling source files, parsing them into a Neo4j graph database, and generating markdown summaries. It validates input paths, uses language-specific parsers to extract structure, optionally analyzes files with an LLM model for deeper insights, and writes aggregated results including an index file. The engine tracks detailed metrics like files parsed, skipped, or failed, and handles errors gracefully to avoid halting the entire process unless critical system-level failures occur.

## Classes

### `AutodocEngine`

Lines 32–216

**Methods:** `__init__`, `_make_crawl_id`, `run`, `_process_file`

## Imports

- `import hashlib`
- `import time`
- `from collections import Counter`
- `from pathlib import Path`
- `from .config import Config`
- `from .filters import iter_source_files`
- `from .walkers import get_walker, supported_languages`
- `from .neo4j_writer import Neo4jWriter`
- `from .markdown_writer import MarkdownWriter`
- `from .llm_client import LLMClient`
