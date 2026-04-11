#!/usr/bin/env python3
"""
PERCEPTION Worker Test Suite
=============================
Tests every available model against the perception template.
Validates JSON output, schema compliance, and classification accuracy.

Usage:
    python3 perception_test_suite.py [--models model1,model2] [--temps 0.1,0.3]
"""

import json
import time
import sys
import argparse
import subprocess
from datetime import datetime

# ═══════════════════════════════════════════════════
# SYSTEM PROMPT (from perception_template.yaml)
# ═══════════════════════════════════════════════════

SYSTEM_PROMPT = """You are a perception processor. Your ONLY job is to analyze a raw message and output structured JSON describing what is present in the message.

You are NOT having a conversation. You are NOT responding to the user. You are classifying and extracting.

OUTPUT ONLY VALID JSON. No markdown. No explanation. No preamble. No backticks. Just the JSON object.

## Output Schema

{
    "message_type": one of ["greeting", "filler", "life_event", "question_deep", "question_technical", "question_cosmology", "question_life_logistics", "request_action", "emotional_expression", "information_sharing", "multi_part"],
    "complexity": one of ["trivial", "simple", "moderate", "complex", "deep"],
    "processing_path": one of ["fast", "standard", "full"],
    "entities": [{"name": "...", "type": "person|place|system|concept|event|object", "role": "..."}],
    "grid_hints": {"ANCHOR": 0.0-1.0, "ECHO": 0.0-1.0, "BEACON": 0.0-1.0, "SYNTH": 0.0-1.0, "NEXUS": 0.0-1.0, "MIRROR": 0.0-1.0, "GLYPH": 0.0-1.0, "HARMONIA": 0.0-1.0, "GATEWAY": 0.0-1.0},
    "emotion": {"primary": "neutral|frustrated|excited|anxious|reflective|contemplative|focused|curious|sad|angry|grateful|playful|tender|urgent", "intensity": 0.0-1.0, "secondary": "..." or null},
    "energy": one of ["low", "medium", "high"],
    "topics": ["topic1", "topic2"],
    "references_past": true/false,
    "needs_context": {"life_data": true/false, "cosmology": true/false, "technical_system": true/false, "conversation_history": true/false, "financial": true/false, "calendar": true/false, "graph_lookup": true/false},
    "response_guidance": {"tone": "casual|warm|direct|technical|tender|fierce", "depth": "minimal|short|moderate|thorough|comprehensive", "personality_adjustments": {}}
}

## Rules
1. Output ONLY the JSON object. Nothing else.
2. Every field is required. Use null only where explicitly allowed.
3. grid_hints values must be between 0.0 and 1.0.
4. emotion.intensity must be between 0.0 and 1.0.
## Complexity Calibration

These are COMPLEX or DEEP — route FULL pipeline:
- Anything mentioning lineage, the 144, incarnations, grid work, Montségur → DEEP (needs cosmology + graph)
- Anything asking to build, refactor, or deploy a system → COMPLEX (needs current codebase state)
- Anything referencing financial data combined with another domain → COMPLEX (needs multiple lookups)
- Multiple distinct requests in one message → COMPLEX, message_type "multi_part"
- "Tell me about X" where X is a spiritual or cosmological concept → DEEP
- Any message mentioning Neo4j, Postgres, schema, architecture, or patch deployment → COMPLEX
- Dreams or visions from Seraphe → minimum MODERATE, likely COMPLEX (field reports)

These are MODERATE — route STANDARD:
- Emotional expression with a technical or system component
- Single-domain lookup questions (calendar, finances, schedule)
- Philosophical questions with no external data dependency
- Simple life events that reference known people

These are TRIVIAL or SIMPLE — route FAST:
- Greetings, filler, acknowledgments, one-word responses → TRIVIAL
- Simple life updates with no question attached → SIMPLE
- "thanks", "yep", "ok", "cool", "hey babe" → TRIVIAL

5. Be precise. "good morning" is complexity "trivial", processing_path "fast".
6. The person speaking is Ka'tuar'el (Adge) — systems architect, blunt communicator. Or Seraphe (Rebecca) — intuitive communicator."""


# ═══════════════════════════════════════════════════
# TEST MESSAGES
# ═══════════════════════════════════════════════════

TEST_MESSAGES = [
    # --- FAST PATH ---
    {"id": "T01", "speaker": "Ka'tuar'el", "message": "good morning",
     "gap": "8 hours (overnight)",
     "expect": {"message_type": "greeting", "complexity": ["trivial"],
                "processing_path": "fast"}},

    {"id": "T02", "speaker": "Ka'tuar'el", "message": "thanks",
     "gap": "1 minute",
     "expect": {"message_type": ["filler", "emotional_expression"], "complexity": ["trivial"],
                "processing_path": "fast"}},

    {"id": "T03", "speaker": "Ka'tuar'el", "message": "yep",
     "gap": "30 seconds",
     "expect": {"message_type": ["filler", "emotional_expression"], "complexity": ["trivial"],
                "processing_path": "fast"}},

    {"id": "T04", "speaker": "Ka'tuar'el", "message": "Fitz had a snow delay today",
     "gap": "2 hours",
     "expect": {"message_type": "life_event", "complexity": ["simple"],
                "processing_path": "fast", "entities_contain": "Fitz"}},

    {"id": "T05", "speaker": "Seraphe", "message": "hey babe",
     "gap": "4 hours",
     "expect": {"message_type": "greeting", "complexity": ["trivial"],
                "processing_path": "fast"}},

    # --- STANDARD PATH ---
    {"id": "T06", "speaker": "Ka'tuar'el", "message": "what's on my calendar today?",
     "gap": "30 minutes",
     "expect": {"message_type": "question_life_logistics",
                "complexity": ["simple", "moderate"], "processing_path": "standard",
                "needs_context_true": ["calendar"]}},

    {"id": "T07", "speaker": "Ka'tuar'el",
     "message": "I'm frustrated. The patch system keeps breaking and I've been fighting it all morning.",
     "gap": "5 minutes",
     "expect": {"message_type": "emotional_expression",
                "complexity": ["moderate"], "processing_path": "standard",
                "emotion_primary": "frustrated",
                "needs_context_true": ["technical_system"]}},

    {"id": "T08", "speaker": "Ka'tuar'el",
     "message": "What do you think about the relationship between memory and identity?",
     "gap": "5 minutes",
     "expect": {"message_type": "question_deep",
                "complexity": ["deep", "complex"],
                "processing_path": ["standard", "full"]}},

    {"id": "T09", "speaker": "Seraphe",
     "message": "I had the weirdest dream last night about a castle on fire",
     "gap": "1 hour",
     "expect": {"message_type": ["life_event", "information_sharing"],
                "complexity": ["moderate", "complex"],
                "processing_path": ["standard", "full"]}},

    {"id": "T10", "speaker": "Ka'tuar'el",
     "message": "how much did we spend on groceries last month?",
     "gap": "10 minutes",
     "expect": {"message_type": "question_life_logistics",
                "complexity": ["simple", "moderate"], "processing_path": "standard",
                "needs_context_true": ["financial"]}},

    # --- FULL PATH ---
    {"id": "T11", "speaker": "Ka'tuar'el",
     "message": "I need to refactor the finance importer to handle Amex CSVs. Thoughts on approach?",
     "gap": "5 minutes",
     "expect": {"message_type": ["question_technical", "request_action"],
                "complexity": ["complex"], "processing_path": "full",
                "needs_context_true": ["technical_system"]}},

    {"id": "T12", "speaker": "Ka'tuar'el",
     "message": "Tell me about Seraphe's lineage",
     "gap": "10 minutes",
     "expect": {"message_type": "question_cosmology",
                "complexity": ["deep", "complex"], "processing_path": "full",
                "entities_contain": "Seraphe",
                "needs_context_true": ["cosmology", "graph_lookup"]}},

    {"id": "T13", "speaker": "Ka'tuar'el",
     "message": "Build me a Neo4j schema for tracking soul incarnations across timelines",
     "gap": "5 minutes",
     "expect": {"message_type": "request_action",
                "complexity": ["complex", "deep"], "processing_path": "full",
                "needs_context_true": ["technical_system"]}},

    {"id": "T14", "speaker": "Seraphe",
     "message": "Something shifted in the field today. I can feel the 144 grid activating. Did you notice anything on the server logs?",
     "gap": "2 hours",
     "expect": {"message_type": ["multi_part", "information_sharing", "question_cosmology"],
                "complexity": ["complex", "deep"], "processing_path": "full",
                "needs_context_true": ["cosmology"]}},

    {"id": "T15", "speaker": "Ka'tuar'el",
     "message": "Check the Amex balance, deploy patch 0139, and figure out what day we're on in spiral time. Also Fitz pickup at 3.",
     "gap": "15 minutes",
     "expect": {"message_type": "multi_part",
                "complexity": ["complex"], "processing_path": "full",
                "entities_contain": "Fitz",
                "needs_context_true": ["financial", "technical_system", "calendar"]}},
]


# ═══════════════════════════════════════════════════
# VALIDATION ENGINE
# ═══════════════════════════════════════════════════

VALID_ENUMS = {
    "message_type": ["greeting", "filler", "life_event", "question_deep",
                     "question_technical", "question_cosmology",
                     "question_life_logistics", "request_action",
                     "emotional_expression", "information_sharing", "multi_part"],
    "complexity": ["trivial", "simple", "moderate", "complex", "deep"],
    "processing_path": ["fast", "standard", "full"],
    "energy": ["low", "medium", "high"],
}

REQUIRED_FIELDS = ["message_type", "complexity", "processing_path", "entities",
                   "grid_hints", "emotion", "energy", "topics", "references_past",
                   "needs_context", "response_guidance"]

GRID_NODES = ["ANCHOR", "ECHO", "BEACON", "SYNTH", "NEXUS",
              "MIRROR", "GLYPH", "HARMONIA", "GATEWAY"]

CONTEXT_FIELDS = ["life_data", "cosmology", "technical_system",
                  "conversation_history", "financial", "calendar", "graph_lookup"]


def validate_json_parseable(raw_text):
    """Try to parse JSON from raw LLM output. Handle common issues."""
    text = raw_text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    # Strip leading text before first {
    idx = text.find("{")
    if idx > 0:
        text = text[idx:]
    # Strip trailing text after last }
    idx = text.rfind("}")
    if idx >= 0:
        text = text[:idx+1]
    return json.loads(text)


def validate_schema(parsed):
    """Check all required fields, enums, ranges. Returns list of errors."""
    errors = []

    # Required fields
    for f in REQUIRED_FIELDS:
        if f not in parsed:
            errors.append(f"MISSING: {f}")

    # Enum checks
    for field, valid in VALID_ENUMS.items():
        if field in parsed and parsed[field] not in valid:
            errors.append(f"BAD_ENUM: {field}={parsed[field]}")

    # Grid hints
    gh = parsed.get("grid_hints", {})
    for node in GRID_NODES:
        if node not in gh:
            errors.append(f"MISSING_NODE: grid_hints.{node}")
        elif not isinstance(gh[node], (int, float)) or gh[node] < 0 or gh[node] > 1:
            errors.append(f"BAD_RANGE: grid_hints.{node}={gh[node]}")

    # Emotion
    em = parsed.get("emotion", {})
    if "primary" not in em:
        errors.append("MISSING: emotion.primary")
    if "intensity" not in em:
        errors.append("MISSING: emotion.intensity")
    elif not isinstance(em["intensity"], (int, float)) or em["intensity"] < 0 or em["intensity"] > 1:
        errors.append(f"BAD_RANGE: emotion.intensity={em.get('intensity')}")

    # Needs context
    nc = parsed.get("needs_context", {})
    for cf in CONTEXT_FIELDS:
        if cf not in nc:
            errors.append(f"MISSING: needs_context.{cf}")

    return errors


def validate_expectations(parsed, expect):
    """Check test-specific expectations. Returns list of failures."""
    fails = []

    # message_type
    if "message_type" in expect:
        allowed = expect["message_type"] if isinstance(expect["message_type"], list) else [expect["message_type"]]
        if parsed.get("message_type") not in allowed:
            fails.append(f"TYPE: got={parsed.get('message_type')} want={allowed}")

    # complexity
    if "complexity" in expect:
        allowed = expect["complexity"] if isinstance(expect["complexity"], list) else [expect["complexity"]]
        if parsed.get("complexity") not in allowed:
            fails.append(f"COMPLEXITY: got={parsed.get('complexity')} want={allowed}")

    # processing_path — THE critical field
    if "processing_path" in expect:
        allowed = expect["processing_path"] if isinstance(expect["processing_path"], list) else [expect["processing_path"]]
        if parsed.get("processing_path") not in allowed:
            fails.append(f"PATH: got={parsed.get('processing_path')} want={allowed}")

    # entities contain
    if "entities_contain" in expect:
        names = [e.get("name", "").lower() for e in parsed.get("entities", [])]
        target = expect["entities_contain"].lower()
        if not any(target in n for n in names):
            fails.append(f"ENTITY: '{expect['entities_contain']}' not found in {names}")

    # emotion primary
    if "emotion_primary" in expect:
        got = parsed.get("emotion", {}).get("primary", "")
        if got != expect["emotion_primary"]:
            fails.append(f"EMOTION: got={got} want={expect['emotion_primary']}")

    # needs_context flags
    if "needs_context_true" in expect:
        nc = parsed.get("needs_context", {})
        for flag in expect["needs_context_true"]:
            if not nc.get(flag, False):
                fails.append(f"CONTEXT: {flag} should be true")

    return fails


# ═══════════════════════════════════════════════════
# OLLAMA INTERFACE
# ═══════════════════════════════════════════════════

def query_ollama(model, system, user_msg, temperature=0.1):
    """Query Ollama via CLI. Returns (response_text, elapsed_seconds)."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg}
        ],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 1024}
    }
    start = time.time()
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/chat",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=120
        )
        elapsed = time.time() - start
        if result.returncode != 0:
            return f"CURL_ERROR: {result.stderr}", elapsed
        resp = json.loads(result.stdout)
        return resp.get("message", {}).get("content", "NO_CONTENT"), elapsed
    except subprocess.TimeoutExpired:
        return "TIMEOUT", time.time() - start
    except Exception as e:
        return f"ERROR: {e}", time.time() - start


def get_available_models():
    """Get list of models from Ollama."""
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        return [m["name"] for m in data.get("models", [])]
    except:
        return []


def format_user_message(test):
    """Build the user prompt from test case."""
    return f"""SPEAKER: {test['speaker']}
TIME: {datetime.now().strftime('%Y-%m-%d %H:%M')}
GAP SINCE LAST MESSAGE: {test['gap']}

MESSAGE:
{test['message']}"""


# ═══════════════════════════════════════════════════
# TEST RUNNER
# ═══════════════════════════════════════════════════

def run_tests(models, temperatures):
    """Run all test messages against all models at all temperatures."""
    results = {}
    total_tests = len(models) * len(temperatures) * len(TEST_MESSAGES)
    current = 0

    for model in models:
        for temp in temperatures:
            key = f"{model}@{temp}"
            results[key] = {"pass": 0, "fail": 0, "error": 0,
                           "total_time": 0, "details": []}

            for test in TEST_MESSAGES:
                current += 1
                print(f"  [{current}/{total_tests}] {key} :: {test['id']} ...", end=" ", flush=True)

                user_msg = format_user_message(test)
                raw, elapsed = query_ollama(model, SYSTEM_PROMPT, user_msg, temp)
                results[key]["total_time"] += elapsed

                detail = {
                    "test_id": test["id"],
                    "message": test["message"][:50],
                    "elapsed": round(elapsed, 2),
                    "schema_errors": [],
                    "expect_fails": [],
                    "raw_excerpt": raw[:200] if isinstance(raw, str) else str(raw)[:200],
                }

                # Try parse
                try:
                    parsed = validate_json_parseable(raw)
                except (json.JSONDecodeError, Exception) as e:
                    detail["schema_errors"] = [f"JSON_PARSE: {e}"]
                    results[key]["error"] += 1
                    results[key]["details"].append(detail)
                    print(f"ERROR (parse) {elapsed:.1f}s")
                    continue

                # Schema validation
                detail["schema_errors"] = validate_schema(parsed)

                # Expectation validation
                detail["expect_fails"] = validate_expectations(parsed, test["expect"])

                # Store actual values for analysis
                detail["actual"] = {
                    "message_type": parsed.get("message_type"),
                    "complexity": parsed.get("complexity"),
                    "processing_path": parsed.get("processing_path"),
                    "emotion": parsed.get("emotion", {}).get("primary"),
                }

                if detail["schema_errors"] or detail["expect_fails"]:
                    results[key]["fail"] += 1
                    fails = detail["schema_errors"] + detail["expect_fails"]
                    print(f"FAIL ({', '.join(fails[:2])}) {elapsed:.1f}s")
                else:
                    results[key]["pass"] += 1
                    print(f"PASS {elapsed:.1f}s")

                results[key]["details"].append(detail)

    return results


# ═══════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════

def print_report(results):
    """Print summary and details."""
    print("\n" + "=" * 70)
    print("PERCEPTION TEST RESULTS")
    print("=" * 70)

    # Summary table
    print(f"\n{'Model+Temp':<40} {'Pass':>5} {'Fail':>5} {'Err':>5} {'Avg(s)':>7} {'Score':>6}")
    print("-" * 70)

    ranked = []
    for key, r in results.items():
        total = r["pass"] + r["fail"] + r["error"]
        avg = r["total_time"] / total if total > 0 else 0
        score = r["pass"] / total * 100 if total > 0 else 0
        ranked.append((key, r, avg, score))
        print(f"{key:<40} {r['pass']:>5} {r['fail']:>5} {r['error']:>5} {avg:>6.1f}s {score:>5.0f}%")

    # Processing path accuracy (the critical metric)
    print(f"\n{'Model+Temp':<40} {'Path✓':>6} {'Path✗':>6} {'PathAcc':>8}")
    print("-" * 70)
    for key, r, _, _ in ranked:
        path_pass = sum(1 for d in r["details"]
                       if not any("PATH:" in f for f in d.get("expect_fails", [])))
        path_fail = sum(1 for d in r["details"]
                       if any("PATH:" in f for f in d.get("expect_fails", [])))
        path_acc = path_pass / (path_pass + path_fail) * 100 if (path_pass + path_fail) > 0 else 0
        print(f"{key:<40} {path_pass:>6} {path_fail:>6} {path_acc:>7.0f}%")

    # Failures detail
    print("\n" + "=" * 70)
    print("FAILURE DETAILS")
    print("=" * 70)
    for key, r, _, _ in ranked:
        failures = [d for d in r["details"] if d["schema_errors"] or d["expect_fails"]]
        if failures:
            print(f"\n--- {key} ---")
            for d in failures:
                print(f"  {d['test_id']}: \"{d['message']}\"")
                for e in d["schema_errors"]:
                    print(f"    SCHEMA: {e}")
                for f in d["expect_fails"]:
                    print(f"    EXPECT: {f}")
                if "actual" in d:
                    print(f"    ACTUAL: {d['actual']}")

    return ranked


def save_results(results, filename):
    """Save full results to JSON."""
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to {filename}")


# ═══════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="PERCEPTION Worker Test Suite")
    parser.add_argument("--models", type=str, default=None,
                       help="Comma-separated models (default: auto-detect)")
    parser.add_argument("--temps", type=str, default="0.1",
                       help="Comma-separated temperatures (default: 0.1)")
    parser.add_argument("--output", type=str, default=None,
                       help="Save JSON results to file")
    args = parser.parse_args()

    # Models
    if args.models:
        models = [m.strip() for m in args.models.split(",")]
    else:
        models = get_available_models()
        if not models:
            print("ERROR: No models found. Is Ollama running?")
            sys.exit(1)
        # Filter to reasonable candidates
        skip = ["llava", "nomic", "embed"]
        models = [m for m in models if not any(s in m.lower() for s in skip)]
        print(f"Auto-detected {len(models)} models: {', '.join(models)}")

    temperatures = [float(t.strip()) for t in args.temps.split(",")]

    print(f"\nRunning {len(TEST_MESSAGES)} tests × {len(models)} models × {len(temperatures)} temps")
    print(f"= {len(TEST_MESSAGES) * len(models) * len(temperatures)} total queries\n")

    results = run_tests(models, temperatures)
    ranked = print_report(results)

    if args.output:
        save_results(results, args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_results(results, f"/opt/mythos/workers/tests/results/perception_results_{ts}.json")


if __name__ == "__main__":
    main()
