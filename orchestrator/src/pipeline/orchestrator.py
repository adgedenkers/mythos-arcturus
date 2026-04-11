#!/usr/bin/env python3
"""
Iris Consciousness Pipeline - Orchestrator v2
===============================================
Routes messages through the neural cascade:
  PERCEPTION → DISCOVERY → STRATEGY → IRIS

Now powered by:
  - prompt_registry.yaml (single source of truth for all prompts)
  - pipeline_logger.py (every call logged to Postgres)
  - registry_loader.py (assembles prompts from registry)

All model configs, prompt text, and component conditions
come from the registry. Nothing hardcoded.
"""

import json
import sys
import os
import time
import subprocess
import logging
from datetime import datetime
from typing import Optional

# Add workers dir to path for imports
sys.path.insert(0, "/opt/mythos/workers")

from registry_loader import RegistryLoader
from pipeline_logger import PipelineLogger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
log = logging.getLogger("orchestrator")

# ═══════════════════════════════════════════════════
# INIT
# ═══════════════════════════════════════════════════

registry = RegistryLoader()
logger = PipelineLogger()

OLLAMA_URL = "http://localhost:11434/api/chat"

POSTGRES_CONFIG = {
    "dbname": "mythos",
    "user": "adge",
}


# ═══════════════════════════════════════════════════
# LLM INTERFACE
# ═══════════════════════════════════════════════════

def query_ollama(model, system, user_msg, temperature=0.1,
                 num_predict=1024, timeout=60):
    """Query Ollama. Returns (parsed_json_or_text, elapsed_seconds, raw)."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg}
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": num_predict}
    }
    start = time.time()
    try:
        result = subprocess.run(
            ["curl", "-s", OLLAMA_URL, "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=timeout
        )
        elapsed = time.time() - start
        if result.returncode != 0:
            return None, elapsed, f"CURL_ERROR: {result.stderr}"

        resp = json.loads(result.stdout)
        raw = resp.get("message", {}).get("content", "")

        # Try to parse as JSON
        try:
            text = raw.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                text = "\n".join(lines).strip()
            idx = text.find("{")
            if idx >= 0:
                end = text.rfind("}")
                if end >= 0:
                    return json.loads(text[idx:end+1]), elapsed, raw
            return raw, elapsed, raw
        except json.JSONDecodeError:
            return raw, elapsed, raw

    except subprocess.TimeoutExpired:
        return None, time.time() - start, "TIMEOUT"
    except Exception as e:
        return None, time.time() - start, f"ERROR: {e}"


# ═══════════════════════════════════════════════════
# STAGE 1: PERCEPTION
# ═══════════════════════════════════════════════════

def run_perception(speaker, message, gap_description, run_uuid=None):
    """Classify the message via registry-assembled prompt."""

    # Assemble prompt from registry
    ctx = {
        "speaker_name": speaker,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "gap_description": gap_description,
        "message": message,
    }
    system_prompt, components = registry.assemble_prompt("perception", ctx)
    user_msg = registry.assemble_user_prompt("perception", ctx)

    # Get model config from registry
    model_cfg = registry.get_model("perception")

    result, elapsed, raw = query_ollama(
        model_cfg["model"], system_prompt, user_msg,
        model_cfg["temperature"], model_cfg["num_predict"],
        model_cfg["timeout"]
    )

    parse_ok = isinstance(result, dict)

    log.info(f"[PERCEPTION] {model_cfg['model']} → {elapsed:.1f}s "
             f"path={result.get('processing_path') if parse_ok else '?'}")

    # Log the LLM call
    if run_uuid:
        logger.log_llm_call(
            run_uuid=run_uuid,
            stage="perception",
            model=model_cfg["model"],
            temperature=model_cfg["temperature"],
            system_prompt=system_prompt,
            user_prompt=user_msg,
            prompt_components=components,
            raw_response=raw,
            parsed_response=result if parse_ok else None,
            elapsed_ms=int(elapsed * 1000),
            parse_success=parse_ok,
        )

    if parse_ok:
        result["_elapsed"] = elapsed
        return result

    log.warning(f"[PERCEPTION] Failed to parse: {raw[:200]}")
    return {
        "processing_path": "standard",
        "message_type": "unknown",
        "complexity": "moderate",
        "entities": [],
        "needs_context": {},
        "response_guidance": {"tone": "warm", "depth": "moderate"},
        "_elapsed": elapsed,
        "_fallback": True,
    }


# ═══════════════════════════════════════════════════
# STAGE 2: DISCOVERY
# ═══════════════════════════════════════════════════

def run_discovery(perception, original_message, run_uuid=None):
    """Fetch context based on perception needs_context flags."""

    needs = perception.get("needs_context", {})
    active_flags = [k for k, v in needs.items() if v]

    if not active_flags:
        log.info("[DISCOVERY] No context flags active, skipping")
        return {"_skipped": True, "_elapsed": 0}

    log.info(f"[DISCOVERY] Active flags: {active_flags}")

    context = {
        "_active_flags": active_flags,
        "_elapsed": 0,
        "query_log": [],
    }

    start = time.time()

    for flag in active_flags:
        if flag == "financial":
            context["financial_context"] = _query_financial(perception, original_message, run_uuid)
        elif flag == "calendar":
            context["calendar_context"] = _query_calendar(perception, run_uuid)
        elif flag == "life_data":
            context["life_context"] = _query_life_data(perception, run_uuid)
        elif flag == "conversation_history":
            context["conversation_context"] = _query_conversations(perception, original_message, run_uuid)
        elif flag == "cosmology":
            context["cosmology_context"] = _query_cosmology(perception, original_message, run_uuid)
        elif flag == "technical_system":
            context["technical_context"] = _query_technical(perception, original_message, run_uuid)
        elif flag == "graph_lookup":
            context["graph_context"] = _query_graph(perception, original_message, run_uuid)

    context["_elapsed"] = time.time() - start
    return context


def _query_postgres(sql, params=None, run_uuid=None, intent=None):
    """Execute a Postgres query and return results. Logs to pipeline."""
    import psycopg2
    start = time.time()
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_CONFIG["dbname"],
            user=POSTGRES_CONFIG["user"]
        )
        cur = conn.cursor()
        cur.execute(sql, params)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        cur.close()
        conn.close()
        elapsed = time.time() - start
        result = {"columns": columns, "rows": rows, "count": len(rows)}

        if run_uuid:
            logger.log_query(
                run_uuid=run_uuid,
                source_type="postgres",
                intent=intent or "query",
                query_text=sql,
                rows_returned=len(rows),
                elapsed_ms=int(elapsed * 1000),
                priority="critical",
            )

        return result
    except Exception as e:
        log.error(f"[POSTGRES] {e}")
        return {"error": str(e)}


def _query_neo4j(cypher, run_uuid=None, intent=None):
    """Execute a Neo4j query and return results. Logs to pipeline."""
    start = time.time()
    try:
        password = _get_neo4j_password()
        result = subprocess.run(
            ["cypher-shell", "-u", "neo4j", "-p", password,
             "--format", "plain", cypher],
            capture_output=True, text=True, timeout=10
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        output = {"raw": result.stdout.strip(),
                  "rows": result.stdout.strip().count("\n")}

        if run_uuid:
            logger.log_query(
                run_uuid=run_uuid,
                source_type="neo4j",
                intent=intent or "query",
                query_text=cypher,
                rows_returned=output["rows"],
                elapsed_ms=int(elapsed * 1000),
                priority="critical",
            )

        return output
    except Exception as e:
        log.error(f"[NEO4J] {e}")
        return {"error": str(e)}


def _get_neo4j_password():
    """Load Neo4j password from env."""
    pw = os.environ.get("NEO4J_PASSWORD")
    if pw:
        return pw
    for env_path in ["/opt/mythos/.env", "/opt/mythos/core/.env"]:
        try:
            with open(env_path) as f:
                for line in f:
                    if line.startswith("NEO4J_PASSWORD="):
                        return line.strip().split("=", 1)[1]
        except FileNotFoundError:
            continue
    return "neo4j"


def _read_file(path, max_lines=100):
    """Read a file, truncated to max_lines."""
    try:
        with open(path) as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            return "".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
        return "".join(lines)
    except Exception as e:
        return f"ERROR reading {path}: {e}"


# --- Context fetchers ---

def _query_financial(perception, message, run_uuid=None):
    result = _query_postgres(
        "SELECT category_primary, SUM(amount) as total, COUNT(*) as txn_count "
        "FROM transactions WHERE transaction_date >= NOW() - INTERVAL '1 month' "
        "GROUP BY category_primary ORDER BY total DESC LIMIT 15",
        run_uuid=run_uuid, intent="monthly spending by category"
    )
    return {"recent_by_category": result}


def _query_calendar(perception, run_uuid=None):
    today = _query_postgres(
        "SELECT title, start_time, end_time, description "
        "FROM calendar_events WHERE event_date = CURRENT_DATE "
        "ORDER BY event_date, start_time",
        run_uuid=run_uuid, intent="today's events"
    )
    upcoming = _query_postgres(
        "SELECT title, start_time, end_time "
        "FROM calendar_events WHERE event_date >= CURRENT_DATE "
        "ORDER BY event_date LIMIT 5",
        run_uuid=run_uuid, intent="upcoming events"
    )
    return {"today": today, "upcoming": upcoming}


def _query_life_data(perception, run_uuid=None):
    events = _query_postgres(
        "SELECT event_date, title, description FROM life_events "
        "ORDER BY event_date DESC LIMIT 10",
        run_uuid=run_uuid, intent="recent life events"
    )
    return {"recent_events": events}


def _query_conversations(perception, message, run_uuid=None):
    topics = perception.get("topics", [])
    results = {}
    results["recent_messages"] = _query_postgres(
        "SELECT timestamp, speaker, content FROM chat_messages "
        "ORDER BY timestamp DESC LIMIT 20",
        run_uuid=run_uuid, intent="recent messages"
    )
    if topics:
        for topic in topics[:3]:
            r = _query_neo4j(
                f"MATCH (e:Exchange)-[:DISCUSSED]->(c:Concept) "
                f"WHERE c.name =~ '(?i).*{topic}.*' "
                f"RETURN e.summary, c.name LIMIT 5",
                run_uuid=run_uuid, intent=f"exchanges about {topic}"
            )
            results[f"topic_{topic}"] = r
    return results


def _query_cosmology(perception, message, run_uuid=None):
    entities = perception.get("entities", [])
    results = {}
    for entity in entities:
        name = entity.get("name", "")
        if name:
            r = _query_neo4j(
                f"MATCH (s:Soul)-[r]-(connected) "
                f"WHERE s.name =~ '(?i).*{name}.*' "
                f"RETURN s.name, type(r), labels(connected), connected.name LIMIT 20",
                run_uuid=run_uuid, intent=f"soul connections for {name}"
            )
            results[f"soul_{name}"] = r
    results["lineages"] = _query_neo4j(
        "MATCH (s:Soul)-[:CARRIES_LINEAGE]->(l:Lineage) "
        "RETURN s.name, l.name LIMIT 20",
        run_uuid=run_uuid, intent="all lineage connections"
    )
    return results


def _query_technical(perception, message, run_uuid=None):
    results = {}
    results["todo"] = _read_file("/opt/mythos/docs/TODO.md", max_lines=50)
    try:
        git = subprocess.run(
            ["git", "-C", "/opt/mythos", "log", "--oneline", "-10"],
            capture_output=True, text=True, timeout=5
        )
        results["recent_commits"] = git.stdout.strip()
    except:
        results["recent_commits"] = "unavailable"
    entities = perception.get("entities", [])
    for entity in entities:
        if entity.get("type") == "system":
            name = entity.get("name", "")
            r = _query_neo4j(
                f"MATCH (s:System)-[r]-(connected) "
                f"WHERE s.name =~ '(?i).*{name}.*' "
                f"RETURN s.name, type(r), connected.name LIMIT 10",
                run_uuid=run_uuid, intent=f"system graph for {name}"
            )
            results[f"system_{name}"] = r
    return results


def _query_graph(perception, message, run_uuid=None):
    entities = perception.get("entities", [])
    results = {}
    for entity in entities:
        name = entity.get("name", "")
        if name:
            r = _query_neo4j(
                f"MATCH (n)-[r]-(connected) "
                f"WHERE n.name =~ '(?i).*{name}.*' "
                f"RETURN labels(n), n.name, type(r), labels(connected), connected.name LIMIT 15",
                run_uuid=run_uuid, intent=f"graph lookup for {name}"
            )
            results[f"entity_{name}"] = r
    return results


# ═══════════════════════════════════════════════════
# STAGE 3: PROMPT ASSEMBLY (from registry)
# ═══════════════════════════════════════════════════

def assemble_iris_prompt(perception, context, original_message, speaker):
    """Build Iris prompt from registry + discovered context."""

    guidance = perception.get("response_guidance", {})
    tone = guidance.get("tone", "warm")
    depth = guidance.get("depth", "moderate")
    path = perception.get("processing_path", "standard")

    # Build context string for injection
    assembled_context = ""
    if context and not context.get("_skipped"):
        assembled_context = "\n## Available Context\n"
        for key, value in context.items():
            if key.startswith("_") or key == "query_log":
                continue
            if value:
                assembled_context += f"\n### {key}\n{json.dumps(value, indent=2, default=str)[:2000]}\n"

    ctx = {
        "speaker": speaker,
        "tone": tone,
        "depth": depth,
        "assembled_context": assembled_context,
    }

    is_fast = (path == "fast")
    system_prompt, components = registry.assemble_prompt("iris", ctx, fast_path=is_fast)

    return system_prompt, components


# ═══════════════════════════════════════════════════
# PIPELINE ORCHESTRATOR
# ═══════════════════════════════════════════════════

def process_message(speaker, message, gap_description="unknown"):
    """Main entry point. Process a message through the full pipeline."""

    pipeline_start = time.time()
    trace = {"stages": [], "total_elapsed": 0}

    # Get model configs from registry
    perception_cfg = registry.get_model("perception")
    iris_cfg = registry.get_model("iris")

    # Start pipeline log
    run_uuid = logger.start_run(
        speaker=speaker,
        message=message,
        gap_description=gap_description,
        processing_path="pending",  # updated after perception
        registry_version=registry.get_version(),
        perception_model=perception_cfg["model"],
        iris_model=iris_cfg["model"],
    )

    # STAGE 1: PERCEPTION
    perception = run_perception(speaker, message, gap_description, run_uuid)
    path = perception.get("processing_path", "standard")

    trace["stages"].append({
        "name": "PERCEPTION",
        "model": perception_cfg["model"],
        "elapsed": perception.get("_elapsed", 0),
        "result": {
            "path": path,
            "type": perception.get("message_type"),
            "complexity": perception.get("complexity"),
        }
    })

    # ROUTING DECISION
    if path == "fast":
        log.info("[ROUTE] Fast path → direct to Iris")
        context = {"_skipped": True}

    elif path == "standard":
        log.info("[ROUTE] Standard path → Discovery → Iris")
        context = run_discovery(perception, message, run_uuid)
        trace["stages"].append({
            "name": "DISCOVERY",
            "elapsed": context.get("_elapsed", 0),
            "flags": context.get("_active_flags", []),
        })

    elif path == "full":
        log.info("[ROUTE] Full path → Discovery → Strategy → Iris")
        context = run_discovery(perception, message, run_uuid)
        trace["stages"].append({
            "name": "DISCOVERY",
            "elapsed": context.get("_elapsed", 0),
            "flags": context.get("_active_flags", []),
        })

    else:
        log.warning(f"[ROUTE] Unknown path '{path}', defaulting to standard")
        context = run_discovery(perception, message, run_uuid)

    # FINAL: IRIS RESPONSE
    system_prompt, iris_components = assemble_iris_prompt(
        perception, context, message, speaker
    )

    iris_result, iris_elapsed, iris_raw = query_ollama(
        iris_cfg["model"], system_prompt, message,
        iris_cfg["temperature"], iris_cfg["num_predict"],
        iris_cfg["timeout"]
    )

    # Log the Iris call
    logger.log_llm_call(
        run_uuid=run_uuid,
        stage="iris",
        model=iris_cfg["model"],
        temperature=iris_cfg["temperature"],
        system_prompt=system_prompt,
        user_prompt=message,
        prompt_components=iris_components,
        raw_response=iris_raw,
        parsed_response=None,
        elapsed_ms=int(iris_elapsed * 1000),
        parse_success=True,
    )

    trace["stages"].append({
        "name": "IRIS",
        "model": iris_cfg["model"],
        "elapsed": iris_elapsed,
    })

    trace["total_elapsed"] = time.time() - pipeline_start

    # Finish pipeline log
    response_text = iris_raw if isinstance(iris_raw, str) else json.dumps(iris_result)

    # Clean perception for storage (remove internal keys)
    perception_clean = {k: v for k, v in perception.items() if not k.startswith("_")}

    logger.finish_run(
        processing_path=path,
        run_uuid=run_uuid,
        iris_response=response_text,
        total_elapsed_ms=int(trace["total_elapsed"] * 1000),
        perception=perception_clean,
        discovery=context,
    )

    log.info(f"[PIPELINE] {path} path complete in {trace['total_elapsed']:.1f}s "
             f"[registry v{registry.get_version()}] [run {run_uuid[:8]}]")

    return {
        "response": response_text,
        "trace": trace,
        "perception": perception,
        "run_uuid": run_uuid,
    }


# ═══════════════════════════════════════════════════
# CLI FOR TESTING
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = input("Message: ")

    speaker = "Ka'tuar'el"
    result = process_message(speaker, message, "5 minutes")

    print("\n" + "=" * 60)
    print("IRIS RESPONSE:")
    print("=" * 60)
    print(result["response"])
    print("\n" + "-" * 60)
    print("TRACE:")
    for stage in result["trace"]["stages"]:
        print(f"  {stage['name']}: {stage.get('elapsed', 0):.1f}s"
              f" [{stage.get('model', 'code')}]"
              f" {stage.get('result', stage.get('flags', ''))}")
    print(f"  TOTAL: {result['trace']['total_elapsed']:.1f}s")
    print(f"  RUN: {result['run_uuid'][:8]}")
    print(f"  REGISTRY: v{registry.get_version()}")
