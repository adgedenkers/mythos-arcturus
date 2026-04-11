"""
Ollama client for AutoDoc2 markdown summary generation.

Isolated so the engine can call summarize() or skip it entirely (--skip-llm).
Failures here never block the crawl — they fall back to None and the markdown
writer omits the summary section.
"""

import json
from typing import Optional
import urllib.request
import urllib.error


class LLMClient:
    def __init__(self, url: str, model: str, timeout: int = 60):
        self.url = url.rstrip('/')
        self.model = model
        self.timeout = timeout

    def summarize_file(self, relative_path: str, language: str, source_excerpt: str) -> Optional[str]:
        """Generate a 2-3 sentence plain-English summary of what this file does."""
        prompt = (
            f"You are documenting a codebase. Read this {language} file and write a "
            f"2-3 sentence plain-English summary of what it does. No preamble, no "
            f"code blocks, no markdown headers. Just the summary.\n\n"
            f"File: {relative_path}\n\n"
            f"```{language}\n{source_excerpt[:6000]}\n```\n"
        )
        try:
            req = urllib.request.Request(
                f"{self.url}/api/generate",
                data=json.dumps({
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                }).encode('utf-8'),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                return (data.get('response') or '').strip() or None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"[llm_client] summarize failed for {relative_path}: {e}")
            return None
