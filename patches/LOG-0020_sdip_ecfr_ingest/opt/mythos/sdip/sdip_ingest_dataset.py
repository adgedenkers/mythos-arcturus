#!/usr/bin/env python3
"""
SDIP Dataset Ingester
Ingests parsed datasets (like eCFR sections) into SDIP as a named source,
completely segregated from other SDIP data.

Usage:
    sdip-ingest-dataset --source-name "title-38-cfr" \
                        --source-type "ecfr" \
                        --path /opt/mythos/sdip/datasets/title38_sections \
                        [--dry-run] [--stats] [--incremental]

This is a thin wrapper around the core SDIP ingester that:
  1. Accepts a custom source name (instead of hardcoded 'curated-vault')
  2. Creates a new sdip_sources record for the dataset
  3. All documents/chunks are tied to that source_id
  4. Datasets can be queried, graphed, or wiped independently
"""

import sys
import os
import argparse
from pathlib import Path

# Add SDIP to path
sys.path.insert(0, '/opt/mythos/sdip')

import psycopg2
from config import get_db_connection, SUPPORTED_FORMATS, SKIP_PATTERNS, SKIP_DIRS
from sdip_chunker import chunk_file


def get_connection():
    return get_db_connection()


def ensure_source(conn, name, path, source_type='dataset'):
    """Create or get a source record. Returns source_id."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM sdip_sources WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE sdip_sources SET path = %s, source_type = %s, last_scanned = now() WHERE id = %s",
                (path, source_type, row[0])
            )
            return row[0]
        else:
            cur.execute(
                """INSERT INTO sdip_sources (name, path, source_type, last_scanned)
                   VALUES (%s, %s, %s, now()) RETURNING id""",
                (name, path, source_type)
            )
            return cur.fetchone()[0]


def sha256_file(filepath):
    import hashlib
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def should_skip(filepath, base_path):
    name = filepath.name
    if name in SKIP_PATTERNS or name.startswith('.'):
        return True
    rel = filepath.relative_to(base_path)
    for part in rel.parts[:-1]:
        if part in SKIP_DIRS:
            return True
    suffix = filepath.suffix.lower()
    # Accept .txt files (our parser output) plus standard formats
    if suffix not in SUPPORTED_FORMATS and suffix not in {'.txt', '.text'}:
        return True
    return False


def collect_files(base_path):
    files = []
    for fp in sorted(base_path.rglob('*')):
        if fp.is_file() and not should_skip(fp, base_path):
            files.append(fp)
    return files


def upsert_document(conn, source_id, relative_path, filepath):
    """Insert or update document. Returns (doc_id, needs_chunking)."""
    from datetime import datetime, timezone
    content_hash = sha256_file(filepath)
    stat = filepath.stat()
    suffix = filepath.suffix.lstrip('.').lower()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, content_hash FROM sdip_documents WHERE source_id = %s AND relative_path = %s",
            (source_id, relative_path)
        )
        row = cur.fetchone()
        if row:
            doc_id, existing_hash = row
            if existing_hash == content_hash:
                cur.execute("UPDATE sdip_documents SET last_scanned = now() WHERE id = %s", (doc_id,))
                return doc_id, False
            else:
                cur.execute(
                    """UPDATE sdip_documents SET
                        content_hash = %s, file_size = %s, file_format = %s,
                        last_scanned = now(), last_modified = %s
                    WHERE id = %s""",
                    (content_hash, stat.st_size, suffix,
                     datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc), doc_id)
                )
                cur.execute("DELETE FROM sdip_chunks WHERE document_id = %s", (doc_id,))
                return doc_id, True
        else:
            cur.execute(
                """INSERT INTO sdip_documents
                    (source_id, relative_path, filename, content_hash, file_size,
                     file_format, category, last_modified)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (source_id, relative_path, filepath.name,
                 content_hash, stat.st_size, suffix,
                 'regulation',  # category for CFR docs
                 datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc))
            )
            return cur.fetchone()[0], True


def insert_chunks(conn, document_id, chunks):
    if not chunks:
        return 0
    with conn.cursor() as cur:
        for chunk in chunks:
            cur.execute(
                """INSERT INTO sdip_chunks
                    (document_id, chunk_index, parent_heading, content_text, word_count)
                   VALUES (%s, %s, %s, %s, %s)""",
                (document_id, chunk.chunk_index, chunk.parent_heading,
                 chunk.content_text, chunk.word_count)
            )
    return len(chunks)


def ingest_dataset(path, source_name, source_type='dataset',
                   incremental=False, dry_run=False):
    """Ingest a dataset directory into SDIP under its own source."""
    path = Path(path).resolve()
    if not path.exists():
        print(f"✗ Path not found: {path}")
        sys.exit(1)

    print(f"{'[DRY RUN] ' if dry_run else ''}SDIP Dataset Ingest")
    print(f"  Source:  {source_name} ({source_type})")
    print(f"  Path:    {path}")
    print(f"  Mode:    {'incremental' if incremental else 'full'}")

    all_files = collect_files(path)
    print(f"  Files:   {len(all_files)}")

    if dry_run:
        by_ext = {}
        for fp in all_files:
            ext = fp.suffix.lower() or '(none)'
            by_ext[ext] = by_ext.get(ext, 0) + 1
        print(f"\n  File types:")
        for ext, count in sorted(by_ext.items(), key=lambda x: -x[1]):
            print(f"    {ext}: {count}")
        for fp in all_files[:10]:
            print(f"    {fp.relative_to(path)}")
        if len(all_files) > 10:
            print(f"    ... and {len(all_files) - 10} more")
        return

    conn = get_connection()
    conn.autocommit = False

    try:
        source_id = ensure_source(conn, source_name, str(path), source_type)
        print(f"  Source ID: {source_id}")
        conn.commit()

        stats = {
            'files_new': 0, 'files_updated': 0, 'files_unchanged': 0,
            'chunks_created': 0, 'errors': 0, 'error_files': [],
        }

        for i, fp in enumerate(all_files):
            rel = str(fp.relative_to(path))
            try:
                doc_id, needs_chunking = upsert_document(conn, source_id, rel, fp)

                if not needs_chunking:
                    if incremental:
                        stats['files_unchanged'] += 1
                        continue
                    with conn.cursor() as cur:
                        cur.execute("SELECT COUNT(*) FROM sdip_chunks WHERE document_id = %s", (doc_id,))
                        if cur.fetchone()[0] > 0:
                            stats['files_unchanged'] += 1
                            continue

                chunks = chunk_file(fp)
                n_chunks = insert_chunks(conn, doc_id, chunks)
                stats['chunks_created'] += n_chunks
                stats['files_new'] += 1

                if (i + 1) % 100 == 0:
                    conn.commit()
                    print(f"  [{i+1}/{len(all_files)}] {stats['chunks_created']} chunks, "
                          f"{stats['files_new']} docs...")

            except Exception as e:
                print(f"  ✗ {rel}: {e}")
                stats['errors'] += 1
                stats['error_files'].append(rel)
                conn.rollback()
                conn.autocommit = False
                source_id = ensure_source(conn, source_name, str(path), source_type)
                conn.commit()
                continue

        conn.commit()

        print(f"\n✓ Dataset ingest complete:")
        print(f"  Source:          {source_name}")
        print(f"  New/updated:     {stats['files_new']}")
        print(f"  Unchanged:       {stats['files_unchanged']}")
        print(f"  Chunks created:  {stats['chunks_created']}")
        if stats['errors']:
            print(f"  Errors:          {stats['errors']}")
            for ef in stats['error_files'][:10]:
                print(f"    ✗ {ef}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Fatal error: {e}")
        raise
    finally:
        conn.close()


def show_dataset_stats(source_name):
    """Show stats for a specific dataset source."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, path, source_type, last_scanned FROM sdip_sources WHERE name = %s", (source_name,))
            src = cur.fetchone()
            if not src:
                print(f"✗ Source '{source_name}' not found")
                return
            source_id = src[0]

            cur.execute("SELECT COUNT(*) FROM sdip_documents WHERE source_id = %s", (source_id,))
            docs = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(c.word_count), 0)
                FROM sdip_chunks c
                JOIN sdip_documents d ON c.document_id = d.id
                WHERE d.source_id = %s
            """, (source_id,))
            chunks, total_words = cur.fetchone()

            cur.execute("""
                SELECT sensitivity_level, COUNT(*)
                FROM sdip_chunks c
                JOIN sdip_documents d ON c.document_id = d.id
                WHERE d.source_id = %s
                GROUP BY sensitivity_level ORDER BY COUNT(*) DESC
            """, (source_id,))
            sensitivity = cur.fetchall()

        print(f"\nSDIP Dataset: {source_name}")
        print(f"{'=' * 40}")
        print(f"  Path:       {src[1]}")
        print(f"  Type:       {src[2]}")
        print(f"  Scanned:    {src[3]}")
        print(f"  Documents:  {docs}")
        print(f"  Chunks:     {chunks}")
        print(f"  Words:      {total_words:,}")
        if sensitivity:
            print(f"\n  Sensitivity:")
            for level, cnt in sensitivity:
                print(f"    {level}: {cnt}")
    finally:
        conn.close()


def wipe_dataset(source_name):
    """Delete all data for a specific dataset source."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM sdip_sources WHERE name = %s", (source_name,))
            row = cur.fetchone()
            if not row:
                print(f"✗ Source '{source_name}' not found")
                return
            source_id = row[0]

            # Cascading deletes handle chunks, sensitivity, etc.
            cur.execute("DELETE FROM sdip_documents WHERE source_id = %s", (source_id,))
            deleted = cur.rowcount
            cur.execute("DELETE FROM sdip_sources WHERE id = %s", (source_id,))
            conn.commit()
            print(f"✓ Wiped source '{source_name}': {deleted} documents deleted")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error: {e}")
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='SDIP Dataset Ingester')
    parser.add_argument('--source-name', required=True,
                        help='Unique name for this dataset source')
    parser.add_argument('--source-type', default='dataset',
                        help='Source type label (default: dataset)')
    parser.add_argument('--path', required=False,
                        help='Directory containing parsed files to ingest')
    parser.add_argument('--incremental', action='store_true',
                        help='Only process changed files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without writing')
    parser.add_argument('--stats', action='store_true',
                        help='Show stats for this source')
    parser.add_argument('--wipe', action='store_true',
                        help='Delete all data for this source (requires confirmation)')

    args = parser.parse_args()

    if args.stats:
        show_dataset_stats(args.source_name)
    elif args.wipe:
        confirm = input(f"Delete ALL data for source '{args.source_name}'? (yes/no): ")
        if confirm.strip().lower() == 'yes':
            wipe_dataset(args.source_name)
        else:
            print("Cancelled.")
    else:
        if not args.path:
            print("✗ --path is required for ingestion")
            sys.exit(1)
        ingest_dataset(args.path, args.source_name, args.source_type,
                       args.incremental, args.dry_run)


if __name__ == '__main__':
    main()
