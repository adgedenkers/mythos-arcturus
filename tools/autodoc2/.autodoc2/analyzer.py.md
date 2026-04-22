# analyzer.py

- **Language:** python
- **Lines:** 209
- **Path:** `/opt/mythos/tools/autodoc2/analyzer.py`

## Summary

This Python file uses a language model (gemma4:26b) to analyze code structure by sending metadata about parsed files (like function/class names, imports, and line counts) to an Ollama API endpoint. It returns structured JSON analysis results (complexity, coupling signals, design patterns, drift risk) stored in Neo4j, without ever sharing raw source code. Errors are logged but don't interrupt the analysis workflow.

## Classes

### `AnalysisResult`

Lines 60–84

**Methods:** `ok`, `to_neo4j_props`

### `Analyzer`

Lines 87–208

**Methods:** `__init__`, `analyze`, `_call_ollama`, `_parse_response`

## Imports

- `import json`
- `import urllib.request`
- `import urllib.error`
- `from dataclasses import dataclass, field, asdict`
- `from datetime import datetime, timezone`
- `from typing import Optional, List`
- `from .walker import ParsedFile`
