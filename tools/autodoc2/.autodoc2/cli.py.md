# cli.py

- **Language:** python
- **Lines:** 130
- **Path:** `/opt/mythos/tools/autodoc2/cli.py`

## Summary

This script is a command-line interface for the AutoDoc2 tool, which crawls and documents codebases, supporting options like custom output directories, environment configuration, file inclusion/exclusion, Neo4j integration for storing analysis data, and optional structural analysis using a large language model (gemma4:26b). It defaults to analyzing the `/opt/mythos` directory but allows overriding paths, cleaning prior runs, skipping LLM-generated summaries, and printing supported languages. The tool outputs markdown documentation and metadata to Neo4j, with configurable verbosity and analysis depth.

## Functions

### `build_parser()`

Lines 43–95

**Calls:** `argparse.ArgumentParser`, `p.add_argument`

### `main()`

Lines 98–125

**Calls:** `', '.join`, `AutodocEngine`, `Path`, `build_parser`, `engine.run`, `load_config`, `parser.parse_args`, `print`, `supported_languages`

## Imports

- `import argparse`
- `import sys`
- `from pathlib import Path`
- `from .config import load_config`
- `from .engine import AutodocEngine`
- `from .walkers import supported_languages`
- `from . import __version__`
