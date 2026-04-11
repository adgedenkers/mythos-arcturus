#!/usr/bin/env python3
"""
SDIP Ingester
Walks the curated vault, chunks every file, and populates PostgreSQL.
Imports existing classification data from _build_manifest.json and _vault_index.json.

Usage:
    sdip-ingest                         # full ingest of curated-vault
    sdip-ingest --path /some/dir        # ingest a specific directory
    sdip-ingest --incremental           # only process changed files
    sdip-ingest --stats                 # show current database stats
    sdip-ingest --dry-run               # show what would happen without writing
"""

import sys
import os
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add SDIP to path
sys.path.insert(0, '/opt/mythos/sdip')

import psycopg2
from psycopg2.extras import Json

from config import (
    VAULT_PATH, SUPPORTED_FORMATS, BINARY_FORMATS, SKIP_PATTERNS,
    DEFAULT_SOURCE_NAME, DEFAULT_SOURCE_TYPE, get_db_dsn,
)
from sdip_chunker import chunk_file


def get_connection():
    """Get a PostgreSQL connection."""
    return psycopg2.connect(get_db_dsn())


def sha256_file(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def should_skip(filepath: Path) -> bool:
    """Check if a file should be skipped."""
    name = filepath.name
    if name in SKIP_PATTERNS:
        return True
    if name.startswith('.'):
        return True
    if name.startswith('_') and name.endswith('.json'):
        return True
    suffix = filepath.suffix.lower()
    if suffix not in SUPPORTED_FORMATS and suffix not in BINARY_FORMATS:
        return True
    return False


def load_classifications(vault_path: Path) -> dict:
    """
    Load existing classification data from both manifests.
    Returns a dict keyed by relative_path with merged classification info.
    """
    classifications = {}

    # Load _build_manifest.json
    build_manifest = vault_path / '_build_manifest.json'
    if build_manifest.exists():
        try:
            data = json.loads(build_manifest.read_text(encoding='utf-8'))
            files = data if isinstance(data, list) else data.get('files', data.get('entries', []))
            if isinstance(files, dict):
                # Handle dict-style manifest keyed by path
                for path_key, entry in files.items():
                    rel = _normalize_rel_path(path_key, vault_path)
                    if rel:
                        classifications[rel] = _extract_classification(entry, source='build_manifest')
            elif isinstance(files, list):
                for entry in files:
                    rel = _get_rel_from_entry(entry, vault_path)
                    if rel:
                        classifications[rel] = _extract_classification(entry, source='build_manifest')
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ⚠ Warning reading _build_manifest.json: {e}")

    # Load _vault_index.json and merge/supplement
    vault_index = vault_path / '_vault_index.json'
    if vault_index.exists():
        try:
            data = json.loads(vault_index.read_text(encoding='utf-8'))
            files = data.get('files', [])
            if isinstance(files, dict):
                for path_key, entry in files.items():
                    rel = _normalize_rel_path(path_key, vault_path)
                    if rel:
                        existing = classifications.get(rel, {})
                        new_data = _extract_classification(entry, source='vault_index')
                        # Merge: vault_index fills in gaps, build_manifest takes priority
                        for key, val in new_data.items():
                            if val and not existing.get(key):
                                existing[key] = val
                        classifications[rel] = existing
            elif isinstance(files, list):
                for entry in files:
                    rel = _get_rel_from_entry(entry, vault_path)
                    if rel:
                        existing = classifications.get(rel, {})
                        new_data = _extract_classification(entry, source='vault_index')
                        for key, val in new_data.items():
                            if val and not existing.get(key):
                                existing[key] = val
                        classifications[rel] = existing
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ⚠ Warning reading _vault_index.json: {e}")

    return classifications


def _normalize_rel_path(path_str: str, vault_path: Path) -> str | None:
    """Normalize a path string to a vault-relative path."""
    if not path_str:
        return None
    p = Path(path_str)
    # If it's absolute, make it relative to vault
    try:
        if p.is_absolute():
            return str(p.relative_to(vault_path))
        return str(p)
    except ValueError:
        return str(p)


def _get_rel_from_entry(entry: dict, vault_path: Path) -> str | None:
    """Extract relative path from a manifest entry."""
    for key in ('relative_path', 'output_path', 'path', 'file', 'filename'):
        val = entry.get(key)
        if val:
            return _normalize_rel_path(val, vault_path)
    return None


def _extract_classification(entry: dict, source: str) -> dict:
    """Extract classification fields from a manifest entry."""
    return {
        'category': entry.get('category', ''),
        'subcategory': entry.get('subcategory', ''),
        'quality': entry.get('quality', ''),
        'summary': entry.get('summary', ''),
        '_source': source,
    }


def ensure_source(conn, name: str, path: str, source_type: str) -> int:
    """Create or get the source record. Returns source_id."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM sdip_sources WHERE name = %s",
            (name,)
        )
        row = cur.fetchone()
        if row:
            # Update path if changed
            cur.execute(
                "UPDATE sdip_sources SET path = %s, last_scanned = now() WHERE id = %s",
                (path, row[0])
            )
            return row[0]
        else:
            cur.execute(
                """INSERT INTO sdip_sources (name, path, source_type, last_scanned)
                   VALUES (%s, %s, %s, now()) RETURNING id""",
                (name, path, source_type)
            )
            return cur.fetchone()[0]


def upsert_document(conn, source_id: int, relative_path: str, filepath: Path,
                     classification: dict) -> tuple[int, bool]:
    """
    Insert or update a document record.
    Returns (document_id, is_new_or_changed).
    """
    content_hash = sha256_file(filepath)
    stat = filepath.stat()

    with conn.cursor() as cur:
        # Check existing
        cur.execute(
            "SELECT id, content_hash FROM sdip_documents WHERE source_id = %s AND relative_path = %s",
            (source_id, relative_path)
        )
        row = cur.fetchone()

        if row:
            doc_id, existing_hash = row
            if existing_hash == content_hash:
                # No change
                cur.execute(
                    "UPDATE sdip_documents SET last_scanned = now() WHERE id = %s",
                    (doc_id,)
                )
                return doc_id, False
            else:
                # File changed — update record, delete old chunks
                cur.execute(
                    """UPDATE sdip_documents SET
                        content_hash = %s, file_size = %s,
                        file_format = %s, category = %s, subcategory = %s,
                        quality = %s, summary = %s,
                        last_scanned = now(), last_modified = %s
                    WHERE id = %s""",
                    (
                        content_hash, stat.st_size,
                        filepath.suffix.lstrip('.').lower(),
                        classification.get('category', ''),
                        classification.get('subcategory', ''),
                        classification.get('quality', ''),
                        classification.get('summary', ''),
                        datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                        doc_id,
                    )
                )
                cur.execute("DELETE FROM sdip_chunks WHERE document_id = %s", (doc_id,))
                return doc_id, True
        else:
            # New document
            cur.execute(
                """INSERT INTO sdip_documents
                    (source_id, relative_path, filename, content_hash, file_size,
                     file_format, category, subcategory, quality, summary,
                     last_modified)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                (
                    source_id, relative_path, filepath.name,
                    content_hash, stat.st_size,
                    filepath.suffix.lstrip('.').lower(),
                    classification.get('category', ''),
                    classification.get('subcategory', ''),
                    classification.get('quality', ''),
                    classification.get('summary', ''),
                    datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                )
            )
            return cur.fetchone()[0], True


def insert_chunks(conn, document_id: int, chunks: list) -> int:
    """Insert chunk records for a document. Returns count inserted."""
    if not chunks:
        return 0

    with conn.cursor() as cur:
        for chunk in chunks:
            cur.execute(
                """INSERT INTO sdip_chunks
                    (document_id, chunk_index, parent_heading, content_text, word_count)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    document_id,
                    chunk.chunk_index,
                    chunk.parent_heading,
                    chunk.content_text,
                    chunk.word_count,
                )
            )
    return len(chunks)


def ingest_vault(vault_path: Path, incremental: bool = False, dry_run: bool = False):
    """
    Main ingestion pipeline.
    Walks the vault, chunks every file, populates the database.
    """
    vault_path = vault_path.resolve()

    if not vault_path.exists():
        print(f"✗ Vault path not found: {vault_path}")
        sys.exit(1)

    print(f"{'[DRY RUN] ' if dry_run else ''}SDIP Ingest: {vault_path}")
    print(f"  Mode: {'incremental' if incremental else 'full'}")

    # Load classifications from both manifests
    print("  Loading classifications from manifests...")
    classifications = load_classifications(vault_path)
    print(f"  Loaded {len(classifications)} classification records")

    # Collect files
    all_files = []
    for fp in sorted(vault_path.rglob('*')):
        if fp.is_file() and not should_skip(fp):
            all_files.append(fp)

    print(f"  Found {len(all_files)} files to process")

    if dry_run:
        print("\n  [DRY RUN] Would process:")
        for fp in all_files[:20]:
            rel = str(fp.relative_to(vault_path))
            cls = classifications.get(rel, {})
            cat = cls.get('category', '?')
            print(f"    {rel} [{cat}]")
        if len(all_files) > 20:
            print(f"    ... and {len(all_files) - 20} more")
        return

    # Database operations
    conn = get_connection()
    conn.autocommit = False

    try:
        # Ensure source record
        source_id = ensure_source(conn, DEFAULT_SOURCE_NAME, str(vault_path), DEFAULT_SOURCE_TYPE)
        print(f"  Source ID: {source_id}")

        stats = {
            'files_processed': 0,
            'files_skipped': 0,
            'files_new': 0,
            'files_updated': 0,
            'files_unchanged': 0,
            'chunks_created': 0,
            'errors': 0,
        }

        for i, fp in enumerate(all_files):
            rel = str(fp.relative_to(vault_path))
            cls = classifications.get(rel, {})

            try:
                # Upsert document
                doc_id, changed = upsert_document(conn, source_id, rel, fp, cls)

                if not changed and incremental:
                    stats['files_unchanged'] += 1
                    stats['files_skipped'] += 1
                    continue

                if changed:
                    # Chunk the file
                    chunks = chunk_file(fp)
                    n_chunks = insert_chunks(conn, doc_id, chunks)
                    stats['chunks_created'] += n_chunks

                    if stats['files_processed'] == 0 or doc_id:
                        stats['files_new' if not incremental else 'files_updated'] += 1
                else:
                    # Full mode: still need to re-chunk if no chunks exist
                    chunks = chunk_file(fp)
                    n_chunks = insert_chunks(conn, doc_id, chunks)
                    stats['chunks_created'] += n_chunks
                    stats['files_unchanged'] += 1

                stats['files_processed'] += 1

                # Progress
                if (i + 1) % 50 == 0 or (i + 1) == len(all_files):
                    print(f"  [{i+1}/{len(all_files)}] {stats['chunks_created']} chunks...")

            except Exception as e:
                print(f"  ✗ Error processing {rel}: {e}")
                stats['errors'] += 1
                continue

        conn.commit()
        print(f"\n✓ Ingest complete:")
        print(f"  Files processed: {stats['files_processed']}")
        print(f"  Files skipped (unchanged): {stats['files_skipped']}")
        print(f"  Chunks created: {stats['chunks_created']}")
        if stats['errors']:
            print(f"  Errors: {stats['errors']}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Fatal error: {e}")
        raise
    finally:
        conn.close()


def show_stats():
    """Show current SDIP database statistics."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sdip_sources")
            sources = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM sdip_documents")
            docs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM sdip_chunks")
            chunks = cur.fetchone()[0]

            cur.execute("SELECT SUM(word_count) FROM sdip_chunks")
            total_words = cur.fetchone()[0] or 0

            cur.execute("""
                SELECT category, COUNT(*) as cnt
                FROM sdip_documents
                WHERE category IS NOT NULL AND category != ''
                GROUP BY category ORDER BY cnt DESC LIMIT 15
            """)
            categories = cur.fetchall()

            cur.execute("""
                SELECT file_format, COUNT(*) as cnt
                FROM sdip_documents
                GROUP BY file_format ORDER BY cnt DESC LIMIT 10
            """)
            formats = cur.fetchall()

            cur.execute("""
                SELECT sensitivity_level, COUNT(*) as cnt
                FROM sdip_chunks
                GROUP BY sensitivity_level ORDER BY cnt DESC
            """)
            sensitivity = cur.fetchall()

        print("SDIP Database Stats")
        print("=" * 40)
        print(f"Sources:    {sources}")
        print(f"Documents:  {docs}")
        print(f"Chunks:     {chunks}")
        print(f"Total words: {total_words:,}")

        if categories:
            print(f"\nTop categories:")
            for cat, cnt in categories:
                print(f"  {cat}: {cnt}")

        if formats:
            print(f"\nFile formats:")
            for fmt, cnt in formats:
                print(f"  .{fmt}: {cnt}")

        if sensitivity:
            print(f"\nSensitivity levels:")
            for level, cnt in sensitivity:
                print(f"  {level}: {cnt}")

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='SDIP Vault Ingester')
    parser.add_argument('--path', type=str, default=str(VAULT_PATH),
                        help=f'Vault path to ingest (default: {VAULT_PATH})')
    parser.add_argument('--incremental', action='store_true',
                        help='Only process changed files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without writing')
    parser.add_argument('--stats', action='store_true',
                        help='Show current database stats')

    args = parser.parse_args()

    if args.stats:
        show_stats()
    else:
        ingest_vault(Path(args.path), incremental=args.incremental, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
