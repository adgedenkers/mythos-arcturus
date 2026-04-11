"""
Analyzer - LLM analysis of components via Ollama (iris-thinking-v2).
Skipped in --quick mode.
"""

import json
import logging
import requests

logger = logging.getLogger("iris.introspection.analyzer")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "iris-thinking-v2"


def analyze_file(file_meta: dict, content: str = None) -> dict:
    """
    Send a file to iris-thinking-v2 for analysis.
    Returns dict with: summary, purpose, dependencies, issues.
    """
    if content is None:
        try:
            with open(file_meta["file_path"], "r", errors="replace") as f:
                content = f.read(50000)  # Cap at 50k chars
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot read {file_meta['file_path']}: {e}")
            return _empty_analysis()

    if not content.strip():
        return _empty_analysis()

    prompt = f"""Analyze this file from the Mythos system.

File: {file_meta['file_path']}
Component: {file_meta.get('component', 'unknown')}
Type: {file_meta.get('file_type', 'unknown')}
Lines: {file_meta.get('line_count', 0)}

Content (first 50k chars):
```
{content[:50000]}
```

Respond with ONLY a JSON object (no markdown, no explanation):
{{
  "summary": "2-3 sentence description of what this file does",
  "purpose": "single sentence: the role this plays in Mythos",
  "dependencies": ["list", "of", "internal", "modules", "it", "depends", "on"],
  "issues": ["list of potential problems, empty if none"]
}}"""

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 1024},
            },
            timeout=120,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()

        # Try to extract JSON from response
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)
        return {
            "llm_summary": result.get("summary", ""),
            "llm_purpose": result.get("purpose", ""),
            "llm_dependencies": result.get("dependencies", []),
            "llm_issues": result.get("issues", []),
        }
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama - is it running?")
        return _empty_analysis()
    except json.JSONDecodeError:
        logger.warning(f"LLM returned non-JSON for {file_meta['file_path']}")
        return _empty_analysis()
    except Exception as e:
        logger.warning(f"LLM analysis failed for {file_meta['file_path']}: {e}")
        return _empty_analysis()


def analyze_component(component_name: str, file_list: list[dict]) -> dict:
    """
    Analyze an entire component (group of files) and return
    a component-level summary.
    """
    file_summaries = []
    for fm in file_list:
        if fm.get("llm_summary"):
            file_summaries.append(f"- {fm['file_path']}: {fm['llm_summary']}")

    if not file_summaries:
        return {"component_summary": f"Component '{component_name}' with {len(file_list)} files (no LLM analysis available)"}

    prompt = f"""Summarize this Mythos system component.

Component: {component_name}
Files analyzed:
{chr(10).join(file_summaries)}

Respond with ONLY a JSON object:
{{
  "component_summary": "3-4 sentence summary of what this component does and its role in Mythos",
  "health": "healthy | needs_attention | critical",
  "documentation_gaps": ["list of what needs documenting"]
}}"""

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 512},
            },
            timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        logger.warning(f"Component analysis failed for {component_name}: {e}")
        return {"component_summary": f"Analysis failed: {e}"}


def _empty_analysis() -> dict:
    return {
        "llm_summary": None,
        "llm_purpose": None,
        "llm_dependencies": [],
        "llm_issues": [],
    }
