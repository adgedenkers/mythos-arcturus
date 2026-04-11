#!/usr/bin/env python3
"""
SDIP Ingester
Walks the curated vault, chunks every file, and populates PostgreSQL.

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
    VAULT_PATH, SUPPORTED_FORMATS, BINARY_FORMATS, SKIP_PATTERNS, SKIP_DIRS,
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


def should_skip(filepath: Path, vault_path: Path) -> bool:
    """Check if a file should be skipped."""
    name = filepath.name

    # Skip by filename
    if name in SKIP_PATTERNS:
        return True
    if name.startswith('.'):
        return True
    if name.startswith('_') and name.endswith('.json'):
        return True

    # Skip by directory
    rel = filepath.relative_to(vault_path)
    for part in rel.parts[:-1]:  # check all parent dirs, not the filename
        if part in SKIP_DIRS:
            return True

    # Skip by extension
    suffix = filepath.suffix.lower()
    if suffix not in SUPPORTED_FORMATS and suffix not in BINARY_FORMATS:
        return True

    return False


def ensure_source(conn, name: str, path: str, source_type: str) -> int:
    """Create or get the source record. Returns source_id."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM sdip_sources WHERE name = %s",
            (name,)
        )
        row = cur.fetchone()
        if row:
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


def upsert_document(conn, source_id: int, relative_path: str, filepath: Path) -> tuple[int, bool]:
    """
    Insert or update a document record.
    Returns (document_id, needs_chunking).
    """
    content_hash = sha256_file(filepath)
    stat = filepath.stat()
    suffix = filepath.suffix.lstrip('.').lower()

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
                # No change — just touch the scan time
                cur.execute(
                    "UPDATE sdip_documents SET last_scanned = now() WHERE id = %s",
                    (doc_id,)
                )
                return doc_id, False
            else:
                # File changed — update record, delete old chunks
                cur.execute(
                    """UPDATE sdip_documents SET
                        content_hash = %s, file_size = %s, file_format = %s,
                        last_scanned = now(), last_modified = %s
                    WHERE id = %s""",
                    (
                        content_hash, stat.st_size, suffix,
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
                     file_format, last_modified)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   RETURNING id""",
                (
                    source_id, relative_path, filepath.name,
                    content_hash, stat.st_size, suffix,
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


def collect_files(vault_path: Path) -> list[Path]:
    """Walk the vault and collect all processable files, respecting skip rules."""
    files = []
    for fp in sorted(vault_path.rglob('*')):
        if fp.is_file() and not should_skip(fp, vault_path):
            files.append(fp)
    return files


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

    # Collect files
    all_files = collect_files(vault_path)
    print(f"  Found {len(all_files)} files to process")

    if dry_run:
        # Group by extension for a useful summary
        by_ext = {}
        for fp in all_files:
            ext = fp.suffix.lower() or '(none)'
            by_ext[ext] = by_ext.get(ext, 0) + 1

        print(f"\n  File types:")
        for ext, count in sorted(by_ext.items(), key=lambda x: -x[1]):
            print(f"    {ext}: {count}")

        # Show first 15
        print(f"\n  Sample files:")
        for fp in all_files[:15]:
            rel = str(fp.relative_to(vault_path))
            print(f"    {rel}")
        if len(all_files) > 15:
            print(f"    ... and {len(all_files) - 15} more")
        return

    # Database operations
    conn = get_connection()
    conn.autocommit = False

    try:
        source_id = ensure_source(conn, DEFAULT_SOURCE_NAME, str(vault_path), DEFAULT_SOURCE_TYPE)
        print(f"  Source ID: {source_id}")

        stats = {
            'files_new': 0,
            'files_updated': 0,
            'files_unchanged': 0,
            'chunks_created': 0,
            'errors': 0,
            'error_files': [],
        }

        for i, fp in enumerate(all_files):
            rel = str(fp.relative_to(vault_path))

            try:
                doc_id, needs_chunking = upsert_document(conn, source_id, rel, fp)

                if not needs_chunking:
                    if incremental:
                        stats['files_unchanged'] += 1
                        continue
                    # Full mode — check if chunks already exist
                    with conn.cursor() as cur:
                        cur.execute("SELECT COUNT(*) FROM sdip_chunks WHERE document_id = %s", (doc_id,))
                        if cur.fetchone()[0] > 0:
                            stats['files_unchanged'] += 1
                            continue

                # Chunk the file
                chunks = chunk_file(fp)
                n_chunks = insert_chunks(conn, doc_id, chunks)
                stats['chunks_created'] += n_chunks
                stats['files_new'] += 1

                # Commit in batches of 50
                if (i + 1) % 50 == 0:
                    conn.commit()
                    print(f"  [{i+1}/{len(all_files)}] {stats['chunks_created']} chunks, {stats['files_new']} files...")

            except Exception as e:
                print(f"  ✗ {rel}: {e}")
                stats['errors'] += 1
                stats['error_files'].append(rel)
                # Rollback just this file's work and continue
                conn.rollback()
                # Re-establish source_id after rollback
                conn.autocommit = False
                source_id = ensure_source(conn, DEFAULT_SOURCE_NAME, str(vault_path), DEFAULT_SOURCE_TYPE)
                continue

        conn.commit()

        print(f"\n✓ Ingest complete:")
        print(f"  New/updated files: {stats['files_new']}")
        print(f"  Unchanged files:   {stats['files_unchanged']}")
        print(f"  Chunks created:    {stats['chunks_created']}")
        if stats['errors']:
            print(f"  Errors:            {stats['errors']}")
            for ef in stats['error_files'][:10]:
                print(f"    ✗ {ef}")

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

            # Chunk distribution
            cur.execute("""
                SELECT
                    MIN(c.cnt) as min_chunks,
                    MAX(c.cnt) as max_chunks,
                    ROUND(AVG(c.cnt), 1) as avg_chunks
                FROM (
                    SELECT document_id, COUNT(*) as cnt
                    FROM sdip_chunks GROUP BY document_id
                ) c
            """)
            chunk_dist = cur.fetchone()

        print("SDIP Database Stats")
        print("=" * 40)
        print(f"Sources:      {sources}")
        print(f"Documents:    {docs}")
        print(f"Chunks:       {chunks}")
        print(f"Total words:  {total_words:,}")

        if chunk_dist and chunk_dist[0] is not None:
            print(f"\nChunks per doc: min={chunk_dist[0]}, max={chunk_dist[1]}, avg={chunk_dist[2]}")

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
