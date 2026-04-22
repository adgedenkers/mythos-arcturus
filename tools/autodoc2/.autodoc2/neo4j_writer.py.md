# neo4j_writer.py

- **Language:** python
- **Lines:** 298
- **Path:** `/opt/mythos/tools/autodoc2/neo4j_writer.py`

## Summary

This Python script connects to a Neo4j database and writes parsed code file data into it using a structured node and relationship schema. It creates unique constraints for nodes representing files, classes, functions, modules, and crawls, ensuring data consistency. The script handles the lifecycle of a "crawl" (starting, finishing, cleaning up) and writes file, class, and function details into the graph, linking them via relationships like `CONTAINS`, `DEFINED_IN`, and `IMPORTS` to model code structure and dependencies.

## Classes

### `Neo4jWriter`

Lines 34–297

**Methods:** `__init__`, `close`, `setup_constraints`, `begin_crawl`, `finish_crawl`, `clean_crawl`, `write_file`, `_write_file_tx`, `write_analysis`, `link_calls`, `write_call_property`

## Imports

- `from datetime import datetime`
- `from typing import Optional`
- `from .walker import ParsedFile`
