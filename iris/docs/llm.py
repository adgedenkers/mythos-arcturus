"""
Shared Ollama LLM caller with prompt templates for doc generation.
"""
import json
import logging
import requests

logger = logging.getLogger("iris.docs.llm")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:32b"


def call_llm(prompt, max_tokens=4096, temperature=0.3):
    """Call iris-thinking-v2 via Ollama and return the text response."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama - is it running?")
        return None
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return None


def build_component_prompt(component_name, files_data):
    """Build prompt for generating a component documentation page."""
    file_listing = []
    for f in files_data:
        entry = f"- **{f.get('file_path', '?')}** ({f.get('line_count', 0)} lines, {f.get('file_type', '?')})"
        if f.get("llm_purpose"):
            entry += f"\n  Purpose: {f['llm_purpose']}"
        if f.get("llm_summary"):
            entry += f"\n  {f['llm_summary']}"
        file_listing.append(entry)

    files_text = "\n".join(file_listing)
    return f"""You are documenting the **{component_name}** component of the Mythos system.
Mythos is a sovereign AI infrastructure platform running on a home server called Arcturus.
It includes PostgreSQL, Neo4j, Redis, FastAPI, Ollama, and a Telegram bot.

Here are the files in this component:

{files_text}

Write a comprehensive component reference document in Markdown. Include:
1. A brief overview (2-3 sentences: what this component does and why it exists)
2. Key files and their roles
3. Data stores used (Postgres tables, Neo4j nodes, Redis keys if any)
4. Integration points (how this component connects to others)
5. Configuration and environment variables if apparent
6. Known patterns or conventions used

Write clearly and directly. No filler. This is internal engineering documentation."""


def build_architecture_prompt(component_name, files_data, component_summary=None):
    """Build prompt for generating an ARCHITECTURE.md section."""
    file_names = [f.get("file_path", "?").split("/")[-1] for f in files_data]
    file_types = list(set(f.get("file_type", "?") for f in files_data))
    total_lines = sum(f.get("line_count", 0) for f in files_data)

    summary_block = ""
    if component_summary:
        summary_block = f"\nComponent summary from analysis: {component_summary}\n"

    file_names_str = ", ".join(file_names[:15])
    file_types_str = ", ".join(file_types)
    return f"""Write an ARCHITECTURE.md section for the **{component_name}** component of Mythos.
{summary_block}
Stats: {len(files_data)} files, {total_lines} lines
File types: {file_types_str}
Key files: {file_names_str}

Write a concise architecture section covering:
1. Purpose (one paragraph)
2. Key files and structure
3. Data flow
4. Dependencies and integration points
5. Any known issues or technical debt

Format as a Markdown section starting with ## {component_name}
Keep it factual and concise. This goes into the system architecture reference."""


def build_system_map_prompt(components_data):
    """Build prompt for generating the full system map."""
    comp_listing = []
    for comp in components_data:
        entry = f"- **{comp['name']}**: {comp['file_count']} files, {comp['total_lines']} lines"
        if comp.get("summary"):
            entry += f"\n  {comp['summary']}"
        comp_listing.append(entry)

    comps_text = "\n".join(comp_listing)
    return f"""Generate a complete system map for **Mythos**, a sovereign AI infrastructure platform.
It runs on a home server called Arcturus (Ubuntu 24.04, RTX 5090).

Components:

{comps_text}

Write a system map document in Markdown that includes:
1. System overview (what Mythos is, what it does, 2-3 paragraphs)
2. Component inventory (table: name, purpose, file count, key tech)
3. Data layer (PostgreSQL tables, Neo4j graph, Redis queues)
4. Service layer (systemd services, APIs, bots)
5. Integration diagram (text-based, showing how components connect)
6. Technology stack summary

This is the top-level reference document for understanding the entire system.
Write clearly, no filler, engineering audience."""
