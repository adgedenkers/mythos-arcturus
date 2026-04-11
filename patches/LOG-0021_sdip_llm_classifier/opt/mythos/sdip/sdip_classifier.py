#!/usr/bin/env python3
"""
SDIP LLM Classifier
Runs each unclassified chunk through a local LLM to extract:
  - Topics (3-7 concise labels)
  - Legal domain (e.g., Privacy, Benefits, Employment)
  - Referenced authorities (CFR/USC/FR citations)
  - Key entities (agencies, programs, systems of records)
  - One-line summary

Results are stored in sdip_classifications (per-document aggregate)
and sdip_chunk_topics (per-chunk topic links for graph building).

Designed to run as an integrated pipeline stage after chunking,
or standalone for backfill.

Usage:
    sdip-classify                                # classify all unclassified chunks
    sdip-classify --source-name "title-38-cfr"   # classify only chunks from this source
    sdip-classify --backfill                     # re-classify everything (wipes old)
    sdip-classify --stats                        # show classification stats
    sdip-classify --batch-size 50                # process N chunks per commit
    sdip-classify --model qwen3:30b-a3b          # specify model (default: qwen2.5:7b)
    sdip-classify --dry-run                      # show what would be classified
"""

import sys
import os
import json
import re
import time
import argparse
from datetime import datetime, timezone

sys.path.insert(0, '/opt/mythos/sdip')
from config import get_db_connection

# ── Configuration ──────────────────────────────────────────────

DEFAULT_MODEL = 'qwen2.5:7b'
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
BATCH_SIZE = 50
MAX_CHUNK_CHARS = 3000  # truncate chunks beyond this for classification

# ── Classification Prompt ──────────────────────────────────────

CLASSIFY_PROMPT = """You are a document classification engine. Analyze the following text chunk from a regulatory document and extract structured metadata.

TEXT:
{chunk_text}

Respond with ONLY a JSON object (no markdown, no explanation, no preamble). The JSON must have exactly these keys:

{{
  "topics": ["topic1", "topic2", "topic3"],
  "domain": "primary legal/regulatory domain",
  "authorities": ["38 USC 501", "5 USC 552a"],
  "entities": ["Department of Veterans Affairs", "Inspector General"],
  "summary": "One sentence describing what this chunk covers."
}}

Rules:
- "topics": 3-7 short labels (2-4 words each). Be specific: "Privacy Act Exemptions" not just "Privacy". "Disability Compensation Rates" not just "Benefits".
- "domain": ONE primary domain from: Administrative, Benefits, Compensation, Disability, Education, Employment, Finance, FOIA, Health Care, Housing, Information Security, Insurance, Investigations, Legal, Loan Guaranty, Medical, Pension, Privacy, Procurement, Records Management, Veterans Services, or a new domain if none fit.
- "authorities": Extract any referenced statutes, CFR sections, USC sections, Executive Orders, or Federal Register citations. Empty array if none found.
- "entities": Named agencies, offices, programs, systems of records, or organizational units mentioned. Empty array if none specific.
- "summary": One clear sentence, max 30 words.

Respond with ONLY the JSON object. No /think tags, no explanation."""


# ── Database Schema ────────────────────────────────────────────

CHUNK_TOPICS_DDL = """
CREATE TABLE IF NOT EXISTS sdip_chunk_topics (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL REFERENCES sdip_chunks(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    model_used TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(chunk_id, topic)
);
CREATE INDEX IF NOT EXISTS idx_sdip_chunk_topics_topic ON sdip_chunk_topics(topic);
CREATE INDEX IF NOT EXISTS idx_sdip_chunk_topics_chunk ON sdip_chunk_topics(chunk_id);
"""


# ── Ollama Client ──────────────────────────────────────────────

def call_ollama(prompt, model=DEFAULT_MODEL):
    """Call Ollama chat API and return response text.
    Uses chat endpoint with think:false to suppress qwen3 thinking."""
    import urllib.request
    import urllib.error

    payload = {
        'model': model,
        'messages': [
            {'role': 'user', 'content': prompt}
        ],
        'stream': False,
        'think': False,
        'options': {
            'temperature': 0.1,
            'num_predict': 512,
        }
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f'{OLLAMA_URL}/api/chat',
        data=data,
        headers={'Content-Type': 'application/json'},
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result.get('message', {}).get('content', '')
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama connection failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {e}")


def parse_llm_response(response_text):
    """
    Parse JSON from LLM response, handling common issues:
    - Markdown code fences
    - Think tags from qwen3
    - Trailing text after JSON
    """
    text = response_text.strip()

    # Strip <think>...</think> blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    # Strip markdown code fences
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    # Find JSON object boundaries
    start = text.find('{')
    if start == -1:
        return None

    # Find matching closing brace
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                json_str = text[start:i+1]
                try:
                    parsed = json.loads(json_str)
                    # Validate expected keys
                    result = {
                        'topics': parsed.get('topics', []),
                        'domain': parsed.get('domain', 'Unknown'),
                        'authorities': parsed.get('authorities', []),
                        'entities': parsed.get('entities', []),
                        'summary': parsed.get('summary', ''),
                    }
                    # Ensure topics is a list of strings
                    if not isinstance(result['topics'], list):
                        result['topics'] = [str(result['topics'])]
                    result['topics'] = [str(t) for t in result['topics'] if t][:10]
                    if not isinstance(result['authorities'], list):
                        result['authorities'] = []
                    if not isinstance(result['entities'], list):
                        result['entities'] = []
                    return result
                except json.JSONDecodeError:
                    return None

    return None


# ── Pipeline Functions ─────────────────────────────────────────

def ensure_schema(conn):
    """Create sdip_chunk_topics table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute(CHUNK_TOPICS_DDL)
    conn.commit()


def get_unclassified_chunks(conn, source_name=None, limit=None):
    """
    Get chunks that haven't been classified yet.
    Returns list of (chunk_id, document_id, content_text, relative_path).
    """
    query = """
        SELECT c.id, c.document_id, c.content_text, d.relative_path
        FROM sdip_chunks c
        JOIN sdip_documents d ON c.document_id = d.id
        LEFT JOIN sdip_chunk_topics ct ON ct.chunk_id = c.id
        WHERE ct.id IS NULL
    """
    params = []

    if source_name:
        query += """
            AND d.source_id = (SELECT id FROM sdip_sources WHERE name = %s)
        """
        params.append(source_name)

    query += " ORDER BY c.id"

    if limit:
        query += " LIMIT %s"
        params.append(limit)

    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def classify_chunk(chunk_text, model=DEFAULT_MODEL):
    """Classify a single chunk. Returns parsed classification dict or None."""
    # Truncate for efficiency
    text = chunk_text[:MAX_CHUNK_CHARS]
    prompt = CLASSIFY_PROMPT.format(chunk_text=text)
    response = call_ollama(prompt, model=model)
    return parse_llm_response(response)


def store_classification(conn, chunk_id, document_id, classification, model):
    """Store classification results in both tables."""
    with conn.cursor() as cur:
        # Store in sdip_chunk_topics (per-chunk, per-topic)
        for topic in classification.get('topics', []):
            topic = topic.strip()
            if not topic:
                continue
            cur.execute("""
                INSERT INTO sdip_chunk_topics (chunk_id, topic, model_used)
                VALUES (%s, %s, %s)
                ON CONFLICT (chunk_id, topic) DO NOTHING
            """, (chunk_id, topic, model))

        # Store full classification in chunk's classification_json
        cur.execute("""
            UPDATE sdip_chunks
            SET classification_json = %s
            WHERE id = %s
        """, (json.dumps(classification), chunk_id))


def classify_chunks(source_name=None, model=DEFAULT_MODEL, batch_size=BATCH_SIZE,
                    backfill=False, dry_run=False):
    """
    Main classification pipeline.
    Processes unclassified chunks through the LLM.
    """
    conn = get_db_connection()
    conn.autocommit = False

    try:
        ensure_schema(conn)

        if backfill:
            print("Backfill mode: clearing existing classifications...")
            with conn.cursor() as cur:
                if source_name:
                    cur.execute("""
                        DELETE FROM sdip_chunk_topics
                        WHERE chunk_id IN (
                            SELECT c.id FROM sdip_chunks c
                            JOIN sdip_documents d ON c.document_id = d.id
                            WHERE d.source_id = (SELECT id FROM sdip_sources WHERE name = %s)
                        )
                    """, (source_name,))
                    cur.execute("""
                        UPDATE sdip_chunks SET classification_json = NULL
                        WHERE document_id IN (
                            SELECT id FROM sdip_documents
                            WHERE source_id = (SELECT id FROM sdip_sources WHERE name = %s)
                        )
                    """, (source_name,))
                else:
                    cur.execute("DELETE FROM sdip_chunk_topics")
                    cur.execute("UPDATE sdip_chunks SET classification_json = NULL")
            conn.commit()

        chunks = get_unclassified_chunks(conn, source_name)
        total = len(chunks)

        if total == 0:
            print("✓ All chunks already classified.")
            return

        print(f"SDIP LLM Classifier")
        print(f"  Model:      {model}")
        print(f"  Source:      {source_name or 'all'}")
        print(f"  To classify: {total} chunks")
        print(f"  Batch size:  {batch_size}")

        if dry_run:
            print(f"\n  [DRY RUN] Would classify {total} chunks")
            # Show a sample
            if chunks:
                sample = chunks[0]
                print(f"\n  Sample chunk (id={sample[0]}):")
                print(f"    Path: {sample[3]}")
                print(f"    Text: {sample[2][:200]}...")
            return

        stats = {
            'classified': 0,
            'errors': 0,
            'topics_created': 0,
            'start_time': time.time(),
        }

        for i, (chunk_id, doc_id, content_text, rel_path) in enumerate(chunks):
            try:
                classification = classify_chunk(content_text, model=model)

                if classification is None:
                    print(f"  ✗ Chunk {chunk_id}: failed to parse LLM response")
                    stats['errors'] += 1
                    continue

                store_classification(conn, chunk_id, doc_id, classification, model)
                stats['classified'] += 1
                stats['topics_created'] += len(classification.get('topics', []))

                # Commit in batches
                if (i + 1) % batch_size == 0:
                    conn.commit()
                    elapsed = time.time() - stats['start_time']
                    rate = stats['classified'] / elapsed if elapsed > 0 else 0
                    eta_secs = (total - i - 1) / rate if rate > 0 else 0
                    eta_min = eta_secs / 60
                    print(f"  [{i+1}/{total}] {stats['classified']} classified, "
                          f"{stats['topics_created']} topics, "
                          f"{rate:.1f}/sec, ETA {eta_min:.0f}min")

            except KeyboardInterrupt:
                print(f"\n  Interrupted at chunk {i+1}/{total}")
                conn.commit()
                break
            except Exception as e:
                print(f"  ✗ Chunk {chunk_id}: {e}")
                stats['errors'] += 1
                conn.rollback()
                conn.autocommit = False
                continue

        conn.commit()

        elapsed = time.time() - stats['start_time']
        print(f"\n✓ Classification complete:")
        print(f"  Classified:  {stats['classified']}")
        print(f"  Topics:      {stats['topics_created']}")
        print(f"  Errors:      {stats['errors']}")
        print(f"  Time:        {elapsed:.0f}s ({elapsed/60:.1f}min)")
        if stats['classified'] > 0:
            print(f"  Rate:        {stats['classified']/elapsed:.2f} chunks/sec")

    except Exception as e:
        conn.rollback()
        print(f"✗ Fatal error: {e}")
        raise
    finally:
        conn.close()


def classify_single_chunk_inline(conn, chunk_id, document_id, content_text, model=DEFAULT_MODEL):
    """
    Classify a single chunk inline during ingestion.
    Called by the ingester after inserting a chunk.
    Returns True if successful.
    """
    try:
        classification = classify_chunk(content_text, model=model)
        if classification:
            store_classification(conn, chunk_id, document_id, classification, model)
            return True
    except Exception:
        pass
    return False


def show_stats(source_name=None):
    """Show classification statistics."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Total classified vs unclassified
            if source_name:
                src_filter = """
                    JOIN sdip_documents d ON c.document_id = d.id
                    WHERE d.source_id = (SELECT id FROM sdip_sources WHERE name = %s)
                """
                params = (source_name,)
            else:
                src_filter = ""
                params = ()

            cur.execute(f"""
                SELECT
                    COUNT(*) as total,
                    COUNT(c.classification_json) as classified
                FROM sdip_chunks c
                {src_filter}
            """, params)
            total, classified = cur.fetchone()

            # Topic distribution
            if source_name:
                cur.execute("""
                    SELECT ct.topic, COUNT(*) as cnt
                    FROM sdip_chunk_topics ct
                    JOIN sdip_chunks c ON ct.chunk_id = c.id
                    JOIN sdip_documents d ON c.document_id = d.id
                    WHERE d.source_id = (SELECT id FROM sdip_sources WHERE name = %s)
                    GROUP BY ct.topic
                    ORDER BY cnt DESC
                    LIMIT 25
                """, (source_name,))
            else:
                cur.execute("""
                    SELECT topic, COUNT(*) as cnt
                    FROM sdip_chunk_topics
                    GROUP BY topic
                    ORDER BY cnt DESC
                    LIMIT 25
                """)
            topics = cur.fetchall()

            # Domain distribution
            if source_name:
                cur.execute("""
                    SELECT c.classification_json->>'domain' as domain, COUNT(*) as cnt
                    FROM sdip_chunks c
                    JOIN sdip_documents d ON c.document_id = d.id
                    WHERE d.source_id = (SELECT id FROM sdip_sources WHERE name = %s)
                      AND c.classification_json IS NOT NULL
                    GROUP BY domain
                    ORDER BY cnt DESC
                    LIMIT 15
                """, (source_name,))
            else:
                cur.execute("""
                    SELECT classification_json->>'domain' as domain, COUNT(*) as cnt
                    FROM sdip_chunks
                    WHERE classification_json IS NOT NULL
                    GROUP BY domain
                    ORDER BY cnt DESC
                    LIMIT 15
                """)
            domains = cur.fetchall()

        print(f"\nSDIP Classification Stats{' (' + source_name + ')' if source_name else ''}")
        print(f"{'=' * 50}")
        print(f"  Total chunks:      {total}")
        print(f"  Classified:        {classified}")
        print(f"  Unclassified:      {total - classified}")
        if total > 0:
            print(f"  Coverage:          {classified/total*100:.1f}%")

        if domains:
            print(f"\n  Domains:")
            for domain, cnt in domains:
                print(f"    {domain or 'Unknown'}: {cnt}")

        if topics:
            print(f"\n  Top Topics:")
            for topic, cnt in topics:
                print(f"    {topic}: {cnt}")

    finally:
        conn.close()


# ── CLI ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='SDIP LLM Classifier')
    parser.add_argument('--source-name', default=None,
                        help='Only classify chunks from this source')
    parser.add_argument('--model', default=DEFAULT_MODEL,
                        help=f'Ollama model to use (default: {DEFAULT_MODEL})')
    parser.add_argument('--batch-size', type=int, default=BATCH_SIZE,
                        help=f'Commit every N chunks (default: {BATCH_SIZE})')
    parser.add_argument('--backfill', action='store_true',
                        help='Re-classify everything (clears existing)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be classified')
    parser.add_argument('--stats', action='store_true',
                        help='Show classification statistics')

    args = parser.parse_args()

    if args.stats:
        show_stats(args.source_name)
    else:
        classify_chunks(
            source_name=args.source_name,
            model=args.model,
            batch_size=args.batch_size,
            backfill=args.backfill,
            dry_run=args.dry_run,
        )


if __name__ == '__main__':
    main()
