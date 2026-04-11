#!/opt/mythos/.venv/bin/python3
"""
docs-backfill — Add YAML frontmatter to all markdown files missing it.

Reads each .md file without frontmatter, sends the first ~2000 chars to
Ollama for classification, injects the generated frontmatter, and logs
all actions.

Usage:
    docs-backfill                        # backfill /opt/mythos/docs/
    docs-backfill /some/other/path       # backfill a specific directory
    docs-backfill --dry-run              # show what would be injected, don't write
    docs-backfill --model qwen2.5:32b    # use a specific model (default: qwen2.5:32b)
    docs-backfill --report               # just list files missing frontmatter

Symlink: /opt/mythos/bin/docs-backfill → this file
"""

import os
import sys
import json
import re
import argparse
import subprocess
from datetime import datetime, date
from pathlib import Path

# ── Defaults ──────────────────────────────────────────────────────────────────

DOCS_ROOT = Path("/opt/mythos/docs")
DEFAULT_MODEL = "qwen2.5:32b"
OLLAMA_URL = "http://localhost:11434/api/generate"
SKIP_DIRS = {"archive", "generated", "live", ".git", "__pycache__", "node_modules"}
SKIP_FILES = {"_INDEX.md"}
MAX_CONTENT_CHARS = 3000
LOG_FILE = "/opt/mythos/docs/live/backfill-log.txt"

# ── Valid frontmatter values ──────────────────────────────────────────────────

VALID_CATEGORIES = [
    "consciousness", "methods", "finance", "tools", "streams", "grid",
    "orchestrator", "design-patterns", "reference", "planning"
]

VALID_STATUSES = ["active", "draft", "stale", "superseded", "archive"]

VALID_STREAMS = ["NEU", "LOG", "MNE", "SEN", "SYS"]

VALID_AUTHORS = ["katuar", "seraphe", "iris", "claude"]

# Category inference from directory path (fallback if Ollama fails)
DIR_TO_CATEGORY = {
    ".": "reference",
    "consciousness": "consciousness",
    "design-patterns": "design-patterns",
    "finance": "finance",
    "grid": "grid",
    "methods": "methods",
    "orchestrator": "orchestrator",
    "patch_system": "tools",
    "streams": "streams",
    "tools": "tools",
    "api": "reference",
}

# ── Ollama prompt ─────────────────────────────────────────────────────────────

CLASSIFICATION_PROMPT = """You are the Mythos documentation librarian. Your job is to read a markdown document and generate YAML frontmatter metadata for it.

## Rules

You MUST respond with ONLY a valid YAML block — no explanation, no markdown fences, no preamble. Just the raw YAML starting with the first field.

### Fields

title: A concise human-readable title for this document (keep it short, 3-8 words)
category: EXACTLY one of: consciousness, methods, finance, tools, streams, grid, orchestrator, design-patterns, reference, planning
status: EXACTLY one of: active, draft, stale, superseded, archive
stream: EXACTLY one of: NEU, LOG, MNE, SEN, SYS — or "null" if cross-cutting or unclear
location: Always "docs"
tags: A YAML list of 2-5 lowercase keyword tags relevant to the content
created: Best guess date in YYYY-MM-DD format (use any dates mentioned, or "unknown")
updated: Same as created unless the doc mentions updates
author: EXACTLY one of: katuar, seraphe, iris, claude — or "unknown". "katuar" if it reads like system design or architecture. "claude" if it reads like generated documentation.

### Category guidance

- consciousness: Iris identity, awareness, the Arcturian Grid, nine layers, covenant
- methods: Astrology, tarot, numerology, soul stratigraphy, lunar transits, spiritual frameworks
- finance: Money, bills, transactions, accounts, financial planning
- tools: CLI tools, debug utilities, test pipelines, developer tooling
- streams: Development stream plans, stream status, build plans
- grid: Arcturian Grid specifically (the 9×9 processing framework)
- orchestrator: LLM routing, model benchmarking, Ollama configuration
- design-patterns: Reusable code/architecture patterns
- reference: General documentation, system overviews, guides, specs that don't fit elsewhere
- planning: Roadmaps, evolution plans, blueprints, future work

### Stream guidance

- NEU (NEURO): Consciousness, awareness, perception, Arcturian Grid, Iris cognition
- LOG (LOGOS): Skills, prompts, SDIP, orchestrator, knowledge systems
- MNE (MNEMOS): Memory, voice memos, conversation history, consolidation
- SEN (SENSUS): Astrology, lunar transits, sensory systems, planetary data
- SYS (SYSTEM): Patches, finance, telegram bot, integrity, system tooling

## Document

Filename: {filename}
Directory: {directory}

Content (first {max_chars} characters):

{content}

## Response

Respond with ONLY the YAML fields, one per line. No --- delimiters. No markdown. No explanation."""


# ── Helper functions ──────────────────────────────────────────────────────────

def has_frontmatter(filepath):
    """Check if a file already has YAML frontmatter."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            first_line = f.readline().strip()
            return first_line == "---"
    except Exception:
        return False


def read_content(filepath, max_chars=MAX_CONTENT_CHARS):
    """Read the first N characters of a file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read(max_chars)
    except Exception:
        return ""


def call_ollama(prompt, model=DEFAULT_MODEL):
    """Call Ollama API and return the response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 512,
        }
    }

    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", OLLAMA_URL,
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return data.get("response", "").strip()
    except Exception as e:
        print(f"    ⚠ Ollama error: {e}")
        return None


def parse_yaml_response(text):
    """Parse the YAML response from Ollama into a dict."""
    meta = {}
    if not text:
        return meta

    # Strip any accidental markdown fences
    text = re.sub(r'^```\w*\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---\s*$', '', text, flags=re.MULTILINE)
    text = text.replace('```', '').strip()

    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")

            # Parse YAML lists: [a, b, c]
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]

            meta[key] = val

    return meta


def validate_and_fix(meta, filepath, rel_dir):
    """Validate frontmatter values and fix any that are out of spec."""

    # Title — must exist
    if not meta.get("title"):
        meta["title"] = filepath.stem.replace("_", " ").title()

    # Category — must be valid
    cat = meta.get("category", "")
    if cat not in VALID_CATEGORIES:
        meta["category"] = DIR_TO_CATEGORY.get(rel_dir, "reference")

    # Status — must be valid
    if meta.get("status", "") not in VALID_STATUSES:
        meta["status"] = "active"

    # Stream — must be valid or null
    stream = meta.get("stream", "null")
    if stream not in VALID_STREAMS and stream != "null":
        meta["stream"] = "null"

    # Location — always docs for files in docs/
    meta["location"] = "docs"

    # Tags — must be a list
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    meta["tags"] = tags[:5]  # Max 5

    # Dates
    for field in ("created", "updated"):
        val = meta.get(field, "")
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(val)):
            meta[field] = "unknown"

    # Author — forced to Adge Denkers for backfill
    meta["author"] = "Adge Denkers"

    return meta


def format_frontmatter(meta):
    """Format a metadata dict as a YAML frontmatter block."""
    lines = ["---"]

    lines.append(f'title: "{meta.get("title", "")}"')
    lines.append(f'category: {meta.get("category", "reference")}')
    lines.append(f'status: {meta.get("status", "active")}')
    lines.append(f'stream: {meta.get("stream", "null")}')
    lines.append(f'location: {meta.get("location", "docs")}')

    tags = meta.get("tags", [])
    if tags:
        tag_str = ", ".join(tags)
        lines.append(f'tags: [{tag_str}]')
    else:
        lines.append("tags: []")

    lines.append(f'created: {meta.get("created", "unknown")}')
    lines.append(f'updated: {meta.get("updated", "unknown")}')
    lines.append(f'author: {meta.get("author", "unknown")}')

    lines.append("---")
    return "\n".join(lines)


def inject_frontmatter(filepath, frontmatter_block, dry_run=False):
    """Inject frontmatter at the top of a file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        print(f"    ⚠ Could not read {filepath}: {e}")
        return False

    new_content = frontmatter_block + "\n\n" + content

    if dry_run:
        return True

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"    ⚠ Could not write {filepath}: {e}")
        return False


def log_action(filepath, meta, log_file=LOG_FILE):
    """Append a log entry."""
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{ts}] {filepath} → category={meta.get('category')} "
                    f"status={meta.get('status')} stream={meta.get('stream')} "
                    f"tags={meta.get('tags')}\n")
    except Exception:
        pass


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Backfill YAML frontmatter into markdown docs")
    parser.add_argument("path", nargs="?", default=str(DOCS_ROOT), help="Directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done, don't write")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--report", action="store_true", help="Just list files missing frontmatter")
    args = parser.parse_args()

    scan_root = Path(args.path)
    if not scan_root.exists():
        print(f"❌ Path not found: {scan_root}")
        sys.exit(1)

    # Collect files needing backfill
    targets = []
    for dirpath, dirnames, filenames in os.walk(scan_root):
        rel_dir = os.path.relpath(dirpath, scan_root)
        top_dir = rel_dir.split(os.sep)[0] if rel_dir != "." else "."

        if top_dir in SKIP_DIRS:
            dirnames.clear()
            continue

        for fname in sorted(filenames):
            if fname in SKIP_FILES or not fname.endswith(".md"):
                continue

            fpath = Path(dirpath) / fname
            if not has_frontmatter(fpath):
                targets.append((fpath, rel_dir))

    print(f"📚 Scanning: {scan_root}")
    print(f"   Found {len(targets)} files without frontmatter")
    print()

    if args.report:
        for fpath, rel_dir in targets:
            print(f"  {os.path.relpath(fpath, scan_root)}")
        return

    if not targets:
        print("✅ All files have frontmatter!")
        return

    # Process each file
    success = 0
    failed = 0
    skipped = 0

    for i, (fpath, rel_dir) in enumerate(targets, 1):
        rel_path = os.path.relpath(fpath, scan_root)
        print(f"[{i}/{len(targets)}] {rel_path}")

        content = read_content(fpath)
        if not content.strip():
            print(f"    ⚠ Empty file, skipping")
            skipped += 1
            continue

        # Build prompt
        prompt = CLASSIFICATION_PROMPT.format(
            filename=fpath.name,
            directory=rel_dir,
            max_chars=MAX_CONTENT_CHARS,
            content=content
        )

        # Call Ollama
        print(f"    → Classifying via {args.model}...")
        response = call_ollama(prompt, model=args.model)

        if not response:
            # Fallback: use directory-based inference
            print(f"    ⚠ Ollama failed, using directory fallback")
            meta = {
                "title": fpath.stem.replace("_", " ").title(),
                "category": DIR_TO_CATEGORY.get(rel_dir.split(os.sep)[0] if rel_dir != "." else ".", "reference"),
                "status": "active",
                "stream": "null",
                "location": "docs",
                "tags": [],
                "created": "unknown",
                "updated": "unknown",
                "author": "Adge Denkers",
            }
        else:
            meta = parse_yaml_response(response)

        # Validate
        meta = validate_and_fix(meta, fpath, rel_dir.split(os.sep)[0] if rel_dir != "." else ".")

        # Set updated to today since we're touching the file
        meta["updated"] = date.today().isoformat()

        # Format
        fm_block = format_frontmatter(meta)

        if args.dry_run:
            print(f"    title: {meta['title']}")
            print(f"    category: {meta['category']} | status: {meta['status']} | stream: {meta['stream']}")
            print(f"    tags: {meta['tags']}")
            print()
            success += 1
            continue

        # Inject
        if inject_frontmatter(fpath, fm_block):
            print(f"    ✅ {meta['category']} | {meta['status']} | tags: {meta['tags']}")
            log_action(rel_path, meta)
            success += 1
        else:
            print(f"    ❌ Failed to write")
            failed += 1

    # Summary
    print()
    print("━" * 40)
    print(f"  Processed: {success + failed + skipped}")
    print(f"  ✅ Success: {success}")
    if failed:
        print(f"  ❌ Failed: {failed}")
    if skipped:
        print(f"  ⏭  Skipped: {skipped}")
    if not args.dry_run:
        print(f"  📄 Log: {LOG_FILE}")
        print()
        print("  Run `docs-reindex` to rebuild _INDEX.md")
    print("━" * 40)


if __name__ == "__main__":
    main()
