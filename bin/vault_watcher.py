#!/usr/bin/env python3
"""
Vault Watcher — Auto-filing daemon for Obsidian
================================================
Monitors the vault root for new/changed files, classifies them through
a local LLM, and moves them to the correct subfolder in the curated structure.

Everything is logged. Every move is reversible.

Usage:
    python3 vault_watcher.py /path/to/vault
    python3 vault_watcher.py /path/to/vault --model qwen2.5:32b
    python3 vault_watcher.py /path/to/vault --dry-run          # classify but don't move
    python3 vault_watcher.py /path/to/vault --daemon            # run as background service

Install as systemd service:
    vault-watcher-install /path/to/vault
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"
MAX_CONTENT_CHARS = 6000

# Files that live in root permanently (never moved)
ROOT_PERMANENT = {
    "Welcome.md",
    "HOME.md",
    "_move_log.json",
    "_inbox_review.md",
}

# Directories the watcher ignores
SKIP_DIRS = {'.obsidian', '.git', '.trash', '_superseded', '_deleted', '_fragments', '_scripts', '_inbox'}

# Extensions to process
WATCH_EXTENSIONS = {'.md', '.txt', '.html', '.json', '.yaml', '.yml', '.csv'}

# Minimum file age in seconds before processing (avoids grabbing files mid-write)
MIN_AGE_SECONDS = 3

# How long to wait after last modification before classifying
SETTLE_SECONDS = 5

# ---------------------------------------------------------------------------
# Folder structure map — defines the curated vault structure
# ---------------------------------------------------------------------------

FOLDER_MAP = {
    # Spiritual
    "spiritual/channeling":     {"keywords": ["channeling", "transmission", "scroll", "flame", "codex", "vision", "tarot"]},
    "spiritual/scrolls/seraphe": {"keywords": ["seraphe", "valemira", "rebecca"]},
    "spiritual/scrolls/thresholds": {"keywords": ["threshold"]},
    "spiritual/scrolls/frameworks": {"keywords": ["framework", "stratigraphy", "system prompt", "sovereign alignment"]},
    "spiritual/lineage":        {"keywords": ["lineage", "bloodline", "ancestry", "merovingian", "cathar"]},
    "spiritual/numerology":     {"keywords": ["numerology", "harmonic", "gematria"]},
    "spiritual/emerald-flame":  {"keywords": ["emerald flame", "emerald geometry"]},
    "spiritual/arcturian-grid": {"keywords": ["arcturian grid", "arcturian"]},

    # Astrology
    "astrology/natal-charts":   {"keywords": ["birth chart", "natal chart", "chart analysis"]},
    "astrology/synastry":       {"keywords": ["synastry", "harmonic analysis", "chart compare", "comparison"]},
    "astrology/soul-stratigraphy": {"keywords": ["soul stratigraphy", "field resonance"]},
    "astrology/transits":       {"keywords": ["transit", "forecast", "full moon", "conjunction", "eclipse", "exalted"]},
    "astrology/sacred-geometry": {"keywords": ["geometric pattern", "sacred geometry", "soul fire"]},
    "astrology/methodology":    {"keywords": ["methodology", "vedic", "hellenistic", "tropical"]},
    "astrology/reference":      {"keywords": ["sign_", "house_", "planet_", "element_", "modality_", "matrix"]},
    "astrology/interp-data":    {"keywords": ["asteroids.json", "interpretation", "avatar_points", "world_points"]},

    # Research
    "research/genealogy":       {"keywords": ["genealogy", "wildes", "bloodline", "borden", "salem"]},
    "research/psychology":      {"keywords": ["psychology", "dabrowski", "disintegration"]},

    # Technical
    "technical/mythos/architecture": {"keywords": ["architecture", "expansion plan", "configuration", "quick reference"]},
    "technical/mythos/iris":    {"keywords": ["iris", "nudge", "prompt system", "prompt lab", "biological mapping"]},
    "technical/mythos/arcturian-grid": {"keywords": ["grid implementation", "grid node output doc 2"]},
    "technical/mythos/graph":   {"keywords": ["neo4j", "graph emergence", "node processing", "cypher"]},
    "technical/mythos/witness-system": {"keywords": ["witness system", "witness logging"]},
    "technical/mythos/finance": {"keywords": ["mythos finance", "plaid"]},
    "technical/mythos/sales-intake": {"keywords": ["sales intake", "clothing"]},
    "technical/mythos/reports": {"keywords": ["weekly development", "feature backlog", "diag output", "session-start"]},
    "technical/reference":      {"keywords": ["alphabet integer", "mariana"]},

    # Personal
    "personal/journal":         {"keywords": ["journal", "letter", "reflection", "awakening"]},
    "personal/dates":           {"keywords": ["birthday", "important dates", "dates"]},
    "personal/finance":         {"keywords": ["financial report", "finance report"]},
    "personal/travel":          {"keywords": ["concert", "trip", "travel", "isakov"]},
    "personal/misc":            {"keywords": ["negotiation", "tundra", "nodes"]},
}


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

CLASSIFY_PROMPT = """You are a vault organizer. Classify this note into the correct folder.

Available folders:
{folders}

File: {filename}
Content (first {max_chars} chars):
---
{content}
---

Respond with ONLY a JSON object, no markdown, no backticks:
{{
    "folder": "<exact folder path from the list above>",
    "summary": "<1 sentence summary>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<brief explanation>"
}}

If you're not confident (below 0.6), use "_inbox" as the folder.
For spiritual/channeling content, ALWAYS classify — never send to _inbox.
"""


def call_ollama(prompt: str, model: str) -> dict:
    """Send prompt to Ollama and parse JSON response."""
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300},
        }, timeout=120)
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            return json.loads(json_match.group())
        return {"error": "No JSON in response", "raw": raw[:300]}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Ollama"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}"}
    except Exception as e:
        return {"error": str(e)}


def classify_file(filepath: Path, model: str) -> dict:
    """Classify a file and return target folder + metadata."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')[:MAX_CONTENT_CHARS]
    except Exception as e:
        return {"folder": "_inbox", "summary": f"Error reading: {e}", "confidence": 0.0}

    if len(content.strip()) < 10:
        return {"folder": "_inbox", "summary": "Empty or near-empty file", "confidence": 1.0}

    # Quick match: check frontmatter category tag first
    fm_match = re.search(r'^---\s*\n.*?^category:\s*(.+?)\s*$.*?^---', content, re.MULTILINE | re.DOTALL)
    if fm_match:
        category = fm_match.group(1).strip().strip('"\'')
        # Check if it matches a known folder
        for folder in FOLDER_MAP:
            if category.lower() in folder.lower():
                return {"folder": folder, "summary": "Matched via frontmatter category", "confidence": 0.95}

    # Quick match: keyword scan against filename + first 500 chars
    scan_text = (filepath.name + " " + content[:500]).lower()
    for folder, config in FOLDER_MAP.items():
        for kw in config.get("keywords", []):
            if kw.lower() in scan_text:
                return {"folder": folder, "summary": f"Keyword match: {kw}", "confidence": 0.8,
                        "reasoning": f"Matched keyword '{kw}' in filename or opening content"}

    # Fall back to LLM classification
    folders_list = "\n".join(f"  - {f}" for f in sorted(FOLDER_MAP.keys()))
    folders_list += "\n  - _inbox  (uncertain / needs review)"

    prompt = CLASSIFY_PROMPT.format(
        folders=folders_list,
        filename=filepath.name,
        max_chars=MAX_CONTENT_CHARS,
        content=content,
    )

    result = call_ollama(prompt, model)
    if "error" in result:
        return {"folder": "_inbox", "summary": f"LLM error: {result['error']}", "confidence": 0.0}

    # Validate the folder exists in our map
    suggested = result.get("folder", "_inbox")
    if suggested not in FOLDER_MAP and suggested != "_inbox":
        # Try fuzzy match
        for folder in FOLDER_MAP:
            if suggested.replace("-", "").replace("_", "") in folder.replace("-", "").replace("_", ""):
                result["folder"] = folder
                break
        else:
            result["folder"] = "_inbox"

    return result


# ---------------------------------------------------------------------------
# Move log — every action is recorded and reversible
# ---------------------------------------------------------------------------

class MoveLog:
    """Persistent log of all file moves. Supports undo."""

    def __init__(self, vault_root: Path):
        self.log_path = vault_root / "_move_log.json"
        self.entries = self._load()

    def _load(self) -> list:
        if self.log_path.exists():
            try:
                return json.loads(self.log_path.read_text())
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save(self):
        self.log_path.write_text(json.dumps(self.entries, indent=2))

    def record(self, source: str, dest: str, classification: dict):
        entry = {
            "id": len(self.entries) + 1,
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "destination": dest,
            "classification": classification,
            "undone": False,
        }
        self.entries.append(entry)
        self._save()
        return entry

    def undo(self, entry_id: int, vault_root: Path) -> bool:
        """Undo a specific move by ID."""
        for entry in self.entries:
            if entry["id"] == entry_id and not entry["undone"]:
                src = vault_root / entry["destination"]
                dst = vault_root / entry["source"]
                if src.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src), str(dst))
                    entry["undone"] = True
                    entry["undone_at"] = datetime.now().isoformat()
                    self._save()
                    return True
        return False

    def undo_last(self, vault_root: Path) -> bool:
        """Undo the most recent non-undone move."""
        for entry in reversed(self.entries):
            if not entry["undone"]:
                return self.undo(entry["id"], vault_root)
        return False

    def recent(self, n: int = 20) -> list:
        return list(reversed(self.entries[-n:]))


# ---------------------------------------------------------------------------
# Frontmatter injection
# ---------------------------------------------------------------------------

def inject_frontmatter(filepath: Path, classification: dict):
    """Add or update frontmatter with classification metadata."""
    content = filepath.read_text(encoding='utf-8', errors='replace')

    meta = {
        "classified": datetime.now().strftime("%Y-%m-%d"),
        "category": classification.get("folder", "unknown"),
        "summary": classification.get("summary", ""),
    }

    yaml_block = "---\n"
    for k, v in meta.items():
        yaml_block += f'{k}: "{v}"\n'
    yaml_block += "---\n\n"

    # Check if frontmatter already exists
    if content.startswith("---\n"):
        # Find the closing ---
        end = content.find("\n---\n", 4)
        if end != -1:
            existing_fm = content[4:end]
            # Merge — add our fields without overwriting existing ones
            for k, v in meta.items():
                if f"{k}:" not in existing_fm:
                    existing_fm += f'\n{k}: "{v}"'
            content = f"---\n{existing_fm}\n---\n{content[end+5:]}"
        else:
            content = yaml_block + content
    else:
        content = yaml_block + content

    filepath.write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# File processor
# ---------------------------------------------------------------------------

def process_file(filepath: Path, vault_root: Path, model: str, move_log: MoveLog,
                 dry_run: bool = False) -> Optional[dict]:
    """Classify and move a single file."""

    # Skip non-watched extensions
    if filepath.suffix.lower() not in WATCH_EXTENSIONS:
        return None

    # Skip permanent root files
    if filepath.name in ROOT_PERMANENT:
        return None

    # Skip files not in root (already organized)
    rel = filepath.relative_to(vault_root)
    if len(rel.parts) > 1:
        return None

    # Skip files that are too new (still being written)
    try:
        age = time.time() - filepath.stat().st_mtime
        if age < MIN_AGE_SECONDS:
            return None
    except OSError:
        return None

    print(f"  → Classifying: {filepath.name}", end="", flush=True)

    classification = classify_file(filepath, model)
    folder = classification.get("folder", "_inbox")
    confidence = classification.get("confidence", 0.0)

    print(f" → {folder} (confidence: {confidence:.0%})")

    if dry_run:
        return classification

    # Build destination
    dest_dir = vault_root / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / filepath.name

    # Handle name collisions
    counter = 1
    while dest_file.exists():
        stem = filepath.stem
        suffix = filepath.suffix
        dest_file = dest_dir / f"{stem}-{counter}{suffix}"
        counter += 1

    # Inject frontmatter before moving
    try:
        if filepath.suffix.lower() == '.md':
            inject_frontmatter(filepath, classification)
    except Exception as e:
        print(f"    Warning: couldn't inject frontmatter: {e}")

    # Move the file
    try:
        shutil.move(str(filepath), str(dest_file))
        rel_source = str(filepath.relative_to(vault_root))
        rel_dest = str(dest_file.relative_to(vault_root))
        move_log.record(rel_source, rel_dest, classification)
        print(f"    Moved: {rel_source} → {rel_dest}")
        return classification
    except Exception as e:
        print(f"    Error moving: {e}")
        return None


# ---------------------------------------------------------------------------
# Watcher (daemon mode)
# ---------------------------------------------------------------------------

class VaultHandler(FileSystemEventHandler):
    """Handles new file events in the vault root."""

    def __init__(self, vault_root: Path, model: str, move_log: MoveLog, dry_run: bool = False):
        self.vault_root = vault_root
        self.model = model
        self.move_log = move_log
        self.dry_run = dry_run
        self.pending = {}  # filepath -> last_seen_time

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        if filepath.parent == self.vault_root:
            self.pending[str(filepath)] = time.time()

    def on_moved(self, event):
        if event.is_directory:
            return
        filepath = Path(event.dest_path)
        if filepath.parent == self.vault_root:
            self.pending[str(filepath)] = time.time()

    def process_pending(self):
        """Process files that have settled (no changes for SETTLE_SECONDS)."""
        now = time.time()
        to_remove = []
        for fpath_str, last_seen in self.pending.items():
            if now - last_seen >= SETTLE_SECONDS:
                fpath = Path(fpath_str)
                if fpath.exists():
                    process_file(fpath, self.vault_root, self.model, self.move_log, self.dry_run)
                to_remove.append(fpath_str)
        for f in to_remove:
            del self.pending[f]


# ---------------------------------------------------------------------------
# Sweep mode — process all root files now
# ---------------------------------------------------------------------------

def sweep_root(vault_root: Path, model: str, move_log: MoveLog, dry_run: bool = False):
    """One-time sweep of all files in root that don't belong there."""
    print(f"\n  Sweeping vault root: {vault_root}")

    root_files = [f for f in vault_root.iterdir()
                  if f.is_file()
                  and f.suffix.lower() in WATCH_EXTENSIONS
                  and f.name not in ROOT_PERMANENT]

    if not root_files:
        print("  No files to process in root.")
        return

    print(f"  Found {len(root_files)} files to classify\n")

    for f in sorted(root_files):
        process_file(f, vault_root, model, move_log, dry_run)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Vault Watcher — auto-filing daemon for Obsidian")
    parser.add_argument("vault", help="Path to Obsidian vault root")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="Classify but don't move files")
    parser.add_argument("--daemon", action="store_true", help="Run as persistent watcher")
    parser.add_argument("--sweep", action="store_true", help="Process all root files now, then exit")
    parser.add_argument("--undo", type=int, metavar="ID", help="Undo a specific move by log ID")
    parser.add_argument("--undo-last", action="store_true", help="Undo the most recent move")
    parser.add_argument("--log", action="store_true", help="Show recent move log")
    args = parser.parse_args()

    vault_root = Path(args.vault).resolve()
    if not vault_root.is_dir():
        print(f"Error: Vault not found: {vault_root}")
        sys.exit(1)

    move_log = MoveLog(vault_root)

    # Undo commands
    if args.undo:
        if move_log.undo(args.undo, vault_root):
            print(f"  ✓ Undone move #{args.undo}")
        else:
            print(f"  ✗ Could not undo move #{args.undo}")
        return

    if args.undo_last:
        if move_log.undo_last(vault_root):
            print("  ✓ Undone last move")
        else:
            print("  ✗ No moves to undo")
        return

    if args.log:
        entries = move_log.recent(20)
        if not entries:
            print("  No moves recorded.")
            return
        for e in entries:
            status = "UNDONE" if e.get("undone") else "OK"
            print(f"  [{e['id']:>4}] [{status}] {e['timestamp'][:16]}  {e['source']} → {e['destination']}")
        return

    print(f"\n{'='*60}")
    print(f"  VAULT WATCHER")
    print(f"{'='*60}")
    print(f"  Vault:   {vault_root}")
    print(f"  Model:   {args.model}")
    print(f"  Mode:    {'DRY RUN' if args.dry_run else 'DAEMON' if args.daemon else 'SWEEP'}")
    print(f"{'='*60}\n")

    if args.sweep or not args.daemon:
        sweep_root(vault_root, args.model, move_log, args.dry_run)
        if not args.daemon:
            return

    # Daemon mode
    if not HAS_WATCHDOG:
        print("  Error: watchdog package required for daemon mode")
        print("  Install: pip install watchdog --break-system-packages")
        sys.exit(1)

    handler = VaultHandler(vault_root, args.model, move_log, args.dry_run)
    observer = Observer()
    observer.schedule(handler, str(vault_root), recursive=False)
    observer.start()
    print(f"  Watching {vault_root} for new files... (Ctrl+C to stop)\n")

    try:
        while True:
            handler.process_pending()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n  Stopping watcher...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
