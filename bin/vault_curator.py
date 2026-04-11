#!/usr/bin/env python3
"""
Vault Curator — Phase 1
=======================
Ingests a directory of markdown/text files, classifies each through a local LLM,
and reorganizes them into a clean output structure.

Usage:
    python3 vault_curator.py /path/to/source /path/to/output
    python3 vault_curator.py /path/to/source1 /path/to/source2 /path/to/output
    
    # Use a different model
    python3 vault_curator.py --model qwen2.5:32b /path/to/source /path/to/output
    
    # Dry run — classify only, don't copy/reorganize
    python3 vault_curator.py --dry-run /path/to/source /path/to/output

    # Resume from where you left off (skips already-classified files)
    python3 vault_curator.py --resume /path/to/source /path/to/output

The last argument is always the output directory. Everything before it is a source.
Original files are NEVER modified or deleted.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"   # fast pass; use 32b for deeper analysis
MAX_CONTENT_CHARS = 6000        # how much of each file to send to the LLM
SUPPORTED_EXTENSIONS = {
    '.md', '.txt', '.html', '.htm', '.json', '.yaml', '.yml',
    '.csv', '.log', '.rst', '.org', '.tex', '.xml', '.toml',
    '.cfg', '.ini', '.conf', '.py', '.sh', '.sql', '.js', '.ts',
}
# Files/dirs to always skip
SKIP_DIRS = {'.obsidian', '.git', '.github', 'node_modules', '__pycache__', '.venv', 'venv'}
SKIP_FILES = {'.DS_Store', 'Thumbs.db', '.gitignore', '.gitattributes'}

# ---------------------------------------------------------------------------
# Classification prompt
# ---------------------------------------------------------------------------

CLASSIFY_PROMPT = """You are a document classifier. Analyze this file and respond with ONLY a JSON object — no markdown, no explanation, no backticks.

File path: {filepath}
File size: {filesize} bytes
Last modified: {modified}

Content (first {max_chars} chars):
---
{content}
---

Respond with this exact JSON structure:
{{
    "category": "<one of: spiritual, technical, research, personal, operational, code, empty>",
    "subcategory": "<specific topic like 'channeling', 'lineage', 'astrology', 'server-config', 'python-script', 'genealogy', 'journal', 'todo', etc>",
    "summary": "<1-2 sentence summary of what this file contains>",
    "quality": "<one of: substantial, fragment, stub, duplicate, junk>",
    "suggested_folder": "<clean folder path like 'spiritual/channeling' or 'technical/mythos' or 'research/genealogy'>",
    "suggested_filename": "<clean descriptive filename with .md extension>",
    "keep": true,
    "reasoning": "<brief explanation of classification>"
}}

Category definitions:
- spiritual: channeling, transmissions, entity work, lineage documentation, sacred geometry, consciousness work, field work
- technical: system architecture, server configs, code documentation, deployment notes, API docs
- research: historical research, genealogy, esoteric study, astrology analysis, academic-style investigation
- personal: journal entries, reflections, processing, life logs, trip notes
- operational: todo lists, project plans, meeting notes, task tracking, shopping lists
- code: actual source code files (scripts, configs, etc)
- empty: file has no meaningful content

Quality definitions:
- substantial: complete, meaningful document with real content
- fragment: partial content, incomplete thought, needs merging
- stub: barely any content, placeholder
- duplicate: clearly restates content from another common document
- junk: irrelevant, broken, or meaningless

For spiritual/channeling/lineage content: ALWAYS set keep=true unless truly empty.
For code files: classify as 'code' and note the language in subcategory.
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert text to a clean filename-safe slug."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text[:80] if text else 'untitled'


def file_hash(filepath: Path) -> str:
    """SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def read_file_content(filepath: Path, max_chars: int = MAX_CONTENT_CHARS) -> str:
    """Read file content, handling encoding issues."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read(max_chars)
    except Exception as e:
        return f"[Error reading file: {e}]"


def call_ollama(prompt: str, model: str) -> dict:
    """Send prompt to Ollama and parse JSON response."""
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 500,
            }
        }, timeout=120)
        resp.raise_for_status()
        
        raw = resp.json().get("response", "").strip()
        
        # Try to extract JSON from response (LLMs sometimes wrap it)
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "No JSON found in response", "raw": raw[:500]}
            
    except requests.exceptions.ConnectionError:
        print("  ✗ Cannot connect to Ollama — is it running?")
        sys.exit(1)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": raw[:500]}
    except Exception as e:
        return {"error": str(e)}


def collect_files(source_dirs: list[Path]) -> list[dict]:
    """Walk source directories and collect all supported files."""
    files = []
    seen_hashes = set()
    
    for source_dir in source_dirs:
        source_name = source_dir.name
        for root, dirs, filenames in os.walk(source_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            
            for fname in filenames:
                if fname in SKIP_FILES:
                    continue
                    
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()
                
                if ext not in SUPPORTED_EXTENSIONS:
                    continue
                
                # Get relative path from source root
                rel_path = fpath.relative_to(source_dir)
                fhash = file_hash(fpath)
                
                # Track exact duplicates across sources
                is_dupe = fhash in seen_hashes
                seen_hashes.add(fhash)
                
                stat = fpath.stat()
                files.append({
                    "absolute_path": str(fpath),
                    "relative_path": str(rel_path),
                    "source": source_name,
                    "filename": fname,
                    "extension": ext,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "hash": fhash,
                    "exact_duplicate": is_dupe,
                })
    
    return files


def classify_file(file_info: dict, model: str) -> dict:
    """Classify a single file through the LLM."""
    content = read_file_content(Path(file_info["absolute_path"]))
    
    # Skip truly empty files
    if len(content.strip()) == 0:
        return {
            "category": "empty",
            "subcategory": "empty",
            "summary": "Empty file",
            "quality": "junk",
            "suggested_folder": "_empty",
            "suggested_filename": file_info["filename"],
            "keep": False,
            "reasoning": "File is empty",
        }
    
    prompt = CLASSIFY_PROMPT.format(
        filepath=file_info["relative_path"],
        filesize=file_info["size"],
        modified=file_info["modified"],
        max_chars=MAX_CONTENT_CHARS,
        content=content,
    )
    
    result = call_ollama(prompt, model)
    
    if "error" in result:
        return {
            "category": "unknown",
            "subcategory": "classification-failed",
            "summary": f"LLM error: {result.get('error', 'unknown')}",
            "quality": "unknown",
            "suggested_folder": "_unclassified",
            "suggested_filename": file_info["filename"],
            "keep": True,
            "reasoning": result.get("raw", "")[:200],
        }
    
    return result


def build_output(files: list[dict], output_dir: Path, dry_run: bool = False):
    """
    Copy files into the new organized structure.
    Returns stats dict.
    """
    stats = {"copied": 0, "skipped": 0, "errors": 0}
    
    for f in files:
        classification = f.get("classification", {})
        
        # Skip files marked as don't-keep (but never auto-delete spiritual content)
        if not classification.get("keep", True):
            if classification.get("category") not in ("spiritual", "research"):
                stats["skipped"] += 1
                continue
        
        # Build output path
        suggested_folder = classification.get("suggested_folder", "_unclassified")
        suggested_filename = classification.get("suggested_filename", f["filename"])
        
        # Sanitize the path components
        folder_parts = [slugify(p) for p in suggested_folder.split('/') if p.strip()]
        if not folder_parts:
            folder_parts = ["_unclassified"]
        
        # Keep original extension for code files
        if classification.get("category") == "code":
            suggested_filename = f["filename"]
        
        dest_dir = output_dir / Path(*folder_parts)
        dest_file = dest_dir / suggested_filename
        
        # Handle name collisions
        counter = 1
        while dest_file.exists():
            stem = dest_file.stem
            suffix = dest_file.suffix
            dest_file = dest_dir / f"{stem}-{counter}{suffix}"
            counter += 1
        
        if dry_run:
            stats["copied"] += 1
            continue
        
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f["absolute_path"], dest_file)
            f["output_path"] = str(dest_file)
            stats["copied"] += 1
        except Exception as e:
            print(f"  ✗ Error copying {f['relative_path']}: {e}")
            stats["errors"] += 1
    
    return stats


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(files: list[dict], output_dir: Path, stats: dict, dry_run: bool):
    """Write a classification report as markdown + JSON manifest."""
    
    # Group by category
    by_category = {}
    for f in files:
        cat = f.get("classification", {}).get("category", "unknown")
        by_category.setdefault(cat, []).append(f)
    
    # Markdown report
    lines = [
        "# Vault Curator — Classification Report",
        f"\nGenerated: {datetime.now().isoformat()}",
        f"\nMode: {'DRY RUN' if dry_run else 'LIVE'}",
        f"\n## Summary\n",
        f"- Total files scanned: {len(files)}",
        f"- Files copied/reorganized: {stats['copied']}",
        f"- Files skipped (junk/empty): {stats['skipped']}",
        f"- Errors: {stats['errors']}",
        f"\n## By Category\n",
    ]
    
    for cat in sorted(by_category.keys()):
        cat_files = by_category[cat]
        lines.append(f"\n### {cat.title()} ({len(cat_files)} files)\n")
        for f in cat_files:
            cl = f.get("classification", {})
            keep_marker = "✓" if cl.get("keep", True) else "✗"
            lines.append(
                f"- [{keep_marker}] **{f['relative_path']}** ({f['source']})\n"
                f"  - Quality: {cl.get('quality', '?')} | "
                f"Subcategory: {cl.get('subcategory', '?')}\n"
                f"  - Summary: {cl.get('summary', 'N/A')}\n"
                f"  - → `{cl.get('suggested_folder', '?')}/{cl.get('suggested_filename', '?')}`"
            )
    
    # Quality breakdown
    quality_counts = {}
    for f in files:
        q = f.get("classification", {}).get("quality", "unknown")
        quality_counts[q] = quality_counts.get(q, 0) + 1
    
    lines.append("\n## Quality Breakdown\n")
    for q, count in sorted(quality_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {q}: {count}")
    
    # Exact duplicates
    dupes = [f for f in files if f.get("exact_duplicate")]
    if dupes:
        lines.append(f"\n## Exact Duplicates ({len(dupes)} files)\n")
        for f in dupes:
            lines.append(f"- {f['source']}/{f['relative_path']} (hash: {f['hash'][:12]}...)")
    
    report_path = output_dir / "_curator_report.md"
    if not dry_run:
        report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as fh:
        fh.write('\n'.join(lines))
    
    # JSON manifest (machine-readable, useful for Phase 2 graph import)
    manifest = {
        "generated": datetime.now().isoformat(),
        "stats": stats,
        "files": []
    }
    for f in files:
        manifest["files"].append({
            "source": f["source"],
            "relative_path": f["relative_path"],
            "hash": f["hash"],
            "size": f["size"],
            "modified": f["modified"],
            "exact_duplicate": f.get("exact_duplicate", False),
            "classification": f.get("classification", {}),
            "output_path": f.get("output_path", None),
        })
    
    manifest_path = output_dir / "_curator_manifest.json"
    with open(manifest_path, 'w') as fh:
        json.dump(manifest, fh, indent=2)
    
    print(f"\n  Report:   {report_path}")
    print(f"  Manifest: {manifest_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Vault Curator — classify and reorganize document directories"
    )
    parser.add_argument("paths", nargs="+", help="Source dirs followed by output dir (last arg)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="Classify only, don't copy files")
    parser.add_argument("--resume", action="store_true", help="Skip files already in manifest")
    args = parser.parse_args()
    
    if len(args.paths) < 2:
        print("Error: Need at least one source directory and one output directory")
        sys.exit(1)
    
    source_dirs = [Path(p).resolve() for p in args.paths[:-1]]
    output_dir = Path(args.paths[-1]).resolve()
    
    # Validate sources
    for sd in source_dirs:
        if not sd.is_dir():
            print(f"Error: Source directory not found: {sd}")
            sys.exit(1)
    
    # Don't let output overlap with any source
    for sd in source_dirs:
        if output_dir == sd or str(output_dir).startswith(str(sd)):
            print(f"Error: Output dir cannot be inside source dir: {sd}")
            sys.exit(1)
    
    # Load existing manifest for resume mode
    existing_hashes = set()
    if args.resume:
        manifest_path = output_dir / "_curator_manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as fh:
                existing = json.load(fh)
                existing_hashes = {f["hash"] for f in existing.get("files", [])}
            print(f"  Resume mode: {len(existing_hashes)} files already classified")
    
    print(f"\n{'='*60}")
    print(f"  VAULT CURATOR — Phase 1")
    print(f"{'='*60}")
    print(f"  Sources:  {', '.join(str(s) for s in source_dirs)}")
    print(f"  Output:   {output_dir}")
    print(f"  Model:    {args.model}")
    print(f"  Mode:     {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*60}\n")
    
    # Step 1: Collect files
    print("  [1/4] Scanning source directories...")
    files = collect_files(source_dirs)
    print(f"         Found {len(files)} supported files")
    
    if not files:
        print("  No files found. Check your source paths.")
        sys.exit(0)
    
    # Filter out already-classified files in resume mode
    if args.resume and existing_hashes:
        before = len(files)
        files = [f for f in files if f["hash"] not in existing_hashes]
        print(f"         Skipping {before - len(files)} already-classified files")
    
    # Step 2: Classify each file
    print(f"\n  [2/4] Classifying {len(files)} files through {args.model}...")
    
    start_time = time.time()
    for i, f in enumerate(files, 1):
        short_path = f"{f['source']}/{f['relative_path']}"
        if len(short_path) > 60:
            short_path = "..." + short_path[-57:]
        
        print(f"  [{i:>4}/{len(files)}] {short_path}", end="", flush=True)
        
        if f.get("exact_duplicate"):
            f["classification"] = {
                "category": "duplicate",
                "subcategory": "exact-duplicate",
                "summary": "Exact content duplicate of another file",
                "quality": "duplicate",
                "suggested_folder": "_duplicates",
                "suggested_filename": f["filename"],
                "keep": False,
                "reasoning": "SHA-256 hash matches another file",
            }
            print(" → duplicate (hash match)")
            continue
        
        classification = classify_file(f, args.model)
        f["classification"] = classification
        
        cat = classification.get("category", "?")
        quality = classification.get("quality", "?")
        print(f" → {cat}/{quality}")
    
    elapsed = time.time() - start_time
    rate = len(files) / elapsed if elapsed > 0 else 0
    print(f"\n         Classified {len(files)} files in {elapsed:.0f}s ({rate:.1f} files/sec)")
    
    # Step 3: Build output structure
    print(f"\n  [3/4] {'Simulating' if args.dry_run else 'Building'} output structure...")
    stats = build_output(files, output_dir, dry_run=args.dry_run)
    print(f"         Copied: {stats['copied']}  Skipped: {stats['skipped']}  Errors: {stats['errors']}")
    
    # Step 4: Generate reports
    print(f"\n  [4/4] Generating reports...")
    generate_report(files, output_dir, stats, args.dry_run)
    
    print(f"\n{'='*60}")
    print(f"  DONE {'(dry run)' if args.dry_run else ''}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
