# llm_client.py

- **Language:** python
- **Lines:** 46
- **Path:** `/opt/mythos/tools/autodoc2/llm_client.py`

## Summary

This file defines an Ollama API client that generates plain-English summaries of code files using a specified language model. It sends code excerpts to the LLM with structured prompts requesting concise 2-3 sentence summaries, handles API errors gracefully, and returns None if the call fails to avoid blocking the main workflow. The client is designed for optional use in documentation pipelines where LLM summaries can be skipped if unavailable.

## Classes

### `LLMClient`

Lines 15–45

**Methods:** `__init__`, `summarize_file`

## Imports

- `import json`
- `from typing import Optional`
- `import urllib.request`
- `import urllib.error`
