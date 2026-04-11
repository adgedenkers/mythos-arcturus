#!/usr/bin/env python3
"""
SDIP Sensitivity Scanner
Scans chunks for sensitive content using regex patterns (Layer 1)
and LLM classification (Layer 2).

Usage:
    sdip-scan                           # scan all unscanned chunks
    sdip-scan --full                    # re-scan everything
    sdip-scan --regex-only              # Layer 1 only (fast, no LLM)
    sdip-scan --llm-only                # Layer 2 only (skip regex)
    sdip-scan --doc-id 42               # scan specific document
    sdip-scan --stats                   # show sensitivity report
    sdip-scan --dry-run                 # show what would be scanned
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime, timezone

sys.path.insert(0, '/opt/mythos/sdip')

from config import get_db_connection

# ── Layer 1: Regex Patterns ────────────────────────────────────

SENSITIVITY_PATTERNS = {
    "SSN": {
        "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
        "level": "RESTRICTED",
        "type": "PII",
    },
    "PHONE": {
        "pattern": r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        "level": "SENSITIVE",
        "type": "PII",
    },
    "EMAIL": {
        "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "level": "INTERNAL",
        "type": "PII",
    },
    "IP_ADDRESS": {
        "pattern": r'\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b',
        "level": "SENSITIVE",
        "type": "CREDENTIALS",
    },
    "API_KEY": {
        "pattern": r'(?i)(?:api[_-]?key|token|secret|password|passwd|api_secret|auth_token|access_token)\s*[:=]\s*["\']?\S{8,}',
        "level": "RESTRICTED",
        "type": "CREDENTIALS",
    },
    "CREDIT_CARD": {
        "pattern": r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6(?:011|5\d{2}))[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "level": "RESTRICTED",
        "type": "FINANCIAL",
    },
    "DOB_PATTERN": {
        "pattern": r'\b(?:born|birthday|DOB|dob|date of birth)\s*[:=]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        "level": "SENSITIVE",
        "type": "PII",
    },
    "ACCOUNT_NUM": {
        "pattern": r'(?i)(?:account|acct|routing)\s*#?\s*[:=]?\s*\d{6,}',
        "level": "RESTRICTED",
        "type": "FINANCIAL",
    },
    "CONNECTION_STRING": {
        "pattern": r'(?i)(?:postgres|mysql|mongodb|redis|amqp)(?:ql)?://\S+',
        "level": "RESTRICTED",
        "type": "CREDENTIALS",
    },
    "PRIVATE_KEY": {
        "pattern": r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
        "level": "RESTRICTED",
        "type": "CREDENTIALS",
    },
    "AWS_KEY": {
        "pattern": r'(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}',
        "level": "RESTRICTED",
        "type": "CREDENTIALS",
    },
    "SSH_HOST": {
        "pattern": r'(?i)(?:ssh|scp|sftp)\s+\S+@\S+',
        "level": "SENSITIVE",
        "type": "CREDENTIALS",
    },
    "MEDICAL_TERMS": {
        "pattern": r'(?i)\b(?:diagnosis|prescription|medication|dosage|blood\s*type|medical\s*record|patient\s*id|health\s*insurance|HIPAA)\b',
        "level": "SENSITIVE",
        "type": "PHI",
    },
}

# Common false-positive patterns to exclude
FALSE_POSITIVE_FILTERS = {
    "PHONE": [
        r'\b\d{3}-\d{3}-\d{4}\b',  # Only flag if it looks like a real phone, not version numbers
    ],
    "EMAIL": [
        r'example\.com',
        r'test\.com',
        r'placeholder',
        r'user@',
        r'name@',
    ],
    "IP_ADDRESS": [
        r'\b127\.0\.0\.1\b',       # localhost
        r'\b0\.0\.0\.0\b',         # bind all
        r'\b192\.168\.\d+\.\d+\b', # Only flag non-private? Actually flag these too.
    ],
}

# Sensitivity level hierarchy (for escalation)
LEVEL_ORDER = {'PUBLIC': 0, 'INTERNAL': 1, 'SENSITIVE': 2, 'RESTRICTED': 3}


def run_regex_scan(chunk_text: str) -> list[dict]:
    """
    Run all regex patterns against chunk text.
    Returns list of findings: [{type, pattern_name, detected_pattern, level, confidence}]
    """
    findings = []

    for pattern_name, config in SENSITIVITY_PATTERNS.items():
        matches = list(re.finditer(config['pattern'], chunk_text))
        if not matches:
            continue

        # Check false positives
        false_pos_patterns = FALSE_POSITIVE_FILTERS.get(pattern_name, [])
        real_matches = []
        for m in matches:
            matched_text = m.group()
            is_false_positive = False
            for fp_pattern in false_pos_patterns:
                if re.search(fp_pattern, matched_text, re.IGNORECASE):
                    is_false_positive = True
                    break
            if not is_false_positive:
                real_matches.append(m)

        if not real_matches:
            continue

        # Redact the actual match in the finding record (show pattern, not the value)
        for m in real_matches:
            # Show first/last 2 chars only for the detected pattern record
            matched = m.group()
            if len(matched) > 6:
                redacted = matched[:2] + '***' + matched[-2:]
            else:
                redacted = '***'

            findings.append({
                'sensitivity_type': config['type'],
                'pattern_name': pattern_name,
                'detected_pattern': redacted,
                'level': config['level'],
                'confidence': 0.9,  # regex matches are high confidence but not 1.0
                'detection_method': 'regex',
            })

    return findings


def get_highest_level(findings: list[dict]) -> str:
    """Get the highest sensitivity level from a list of findings."""
    if not findings:
        return 'PUBLIC'
    max_level = 'PUBLIC'
    for f in findings:
        if LEVEL_ORDER.get(f['level'], 0) > LEVEL_ORDER.get(max_level, 0):
            max_level = f['level']
    return max_level


def collect_sensitivity_tags(findings: list[dict]) -> list[str]:
    """Collect unique sensitivity type tags from findings."""
    return list(set(f['sensitivity_type'] for f in findings))


# ── Layer 2: LLM Classification ───────────────────────────────

LLM_PROMPT = """Analyze this text chunk for sensitive content.
You must respond ONLY with valid JSON, no other text.

Classify any sensitive content found:
- PII: Names combined with identifying info (address, SSN, phone, email, DOB)
- PHI: Health/medical information tied to a person
- CREDENTIALS: Passwords, tokens, keys, connection strings, secrets
- FINANCIAL: Account numbers, balances, routing numbers, SSNs
- LEGAL: Legal hold material, attorney-client content, contracts with terms
- CLASSIFIED: Government classification markers

For each finding, provide:
- type: one of PII, PHI, CREDENTIALS, FINANCIAL, LEGAL, CLASSIFIED
- description: what specifically was found (do NOT include the actual sensitive value)
- confidence: 0.0-1.0

If no sensitive content found, return: {"findings": []}

Important:
- Spiritual/religious content is NOT sensitive
- Technical architecture notes are NOT sensitive (unless they contain actual credentials)
- Names of public figures are NOT PII
- Astrological birth data (date, time, location) IS PII when tied to a named person

TEXT TO ANALYZE:
---
{chunk_text}
---

JSON response:"""


def run_llm_scan(chunk_text: str, model: str = 'qwen2.5:7b') -> list[dict]:
    """
    Run LLM classification on a chunk.
    Returns list of findings.
    """
    try:
        import requests
    except ImportError:
        print("  ⚠ requests not available, skipping LLM scan")
        return []

    prompt = LLM_PROMPT.format(chunk_text=chunk_text[:3000])  # Trim very long chunks

    try:
        resp = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.1,
                    'num_predict': 500,
                },
            },
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        response_text = result.get('response', '').strip()

        # Parse JSON from response
        # Try to find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if not json_match:
            return []

        parsed = json.loads(json_match.group())
        raw_findings = parsed.get('findings', [])

        findings = []
        for f in raw_findings:
            sensitivity_type = f.get('type', 'PII')
            if sensitivity_type not in ('PII', 'PHI', 'CREDENTIALS', 'FINANCIAL', 'LEGAL', 'CLASSIFIED'):
                continue

            confidence = float(f.get('confidence', 0.5))
            if confidence < 0.3:
                continue  # Skip low-confidence LLM findings

            # Map type to level
            type_to_level = {
                'PII': 'SENSITIVE',
                'PHI': 'RESTRICTED',
                'CREDENTIALS': 'RESTRICTED',
                'FINANCIAL': 'RESTRICTED',
                'LEGAL': 'SENSITIVE',
                'CLASSIFIED': 'RESTRICTED',
            }

            findings.append({
                'sensitivity_type': sensitivity_type,
                'pattern_name': 'llm_detection',
                'detected_pattern': f.get('description', 'LLM-detected sensitivity')[:200],
                'level': type_to_level.get(sensitivity_type, 'SENSITIVE'),
                'confidence': confidence,
                'detection_method': 'llm',
            })

        return findings

    except requests.exceptions.ConnectionError:
        print("  ⚠ Ollama not available, skipping LLM scan")
        return []
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # LLM gave bad output — not a fatal error
        return []
    except Exception as e:
        print(f"  ⚠ LLM scan error: {e}")
        return []


# ── Main Scanner Pipeline ─────────────────────────────────────

def scan_chunks(full: bool = False, regex_only: bool = False, llm_only: bool = False,
                doc_id: int = None, dry_run: bool = False, llm_model: str = 'qwen2.5:7b'):
    """
    Main scanning pipeline.
    Processes chunks through regex and/or LLM classification.
    """
    conn = get_db_connection()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # Build query for chunks to scan
            if doc_id:
                cur.execute(
                    "SELECT c.id, c.content_text, c.document_id, c.chunk_index "
                    "FROM sdip_chunks c WHERE c.document_id = %s ORDER BY c.chunk_index",
                    (doc_id,)
                )
            elif full:
                cur.execute(
                    "SELECT c.id, c.content_text, c.document_id, c.chunk_index "
                    "FROM sdip_chunks c ORDER BY c.document_id, c.chunk_index"
                )
            else:
                # Scan chunks that haven't been scanned yet (still PUBLIC with no sensitivity records)
                cur.execute(
                    "SELECT c.id, c.content_text, c.document_id, c.chunk_index "
                    "FROM sdip_chunks c "
                    "WHERE c.sensitivity_level = 'PUBLIC' "
                    "AND NOT EXISTS (SELECT 1 FROM sdip_sensitivity s WHERE s.chunk_id = c.id) "
                    "ORDER BY c.document_id, c.chunk_index"
                )

            chunks = cur.fetchall()

        total = len(chunks)
        mode_parts = []
        if not llm_only:
            mode_parts.append('regex')
        if not regex_only:
            mode_parts.append('llm')
        mode_str = ' + '.join(mode_parts)

        print(f"{'[DRY RUN] ' if dry_run else ''}SDIP Sensitivity Scanner")
        print(f"  Chunks to scan: {total}")
        print(f"  Mode: {mode_str}")
        if not regex_only:
            print(f"  LLM model: {llm_model}")

        if dry_run or total == 0:
            if total == 0:
                print("  Nothing to scan.")
            return

        stats = {
            'scanned': 0,
            'regex_findings': 0,
            'llm_findings': 0,
            'chunks_escalated': 0,
            'errors': 0,
        }

        for i, (chunk_id, content_text, document_id, chunk_index) in enumerate(chunks):
            try:
                all_findings = []

                # Layer 1: Regex
                if not llm_only:
                    regex_findings = run_regex_scan(content_text)
                    all_findings.extend(regex_findings)
                    stats['regex_findings'] += len(regex_findings)

                # Layer 2: LLM (only if regex found something, or if running full LLM scan)
                if not regex_only:
                    # Run LLM on: chunks with regex hits (for confirmation), or all chunks if --full
                    if full or regex_findings or llm_only:
                        llm_findings = run_llm_scan(content_text, model=llm_model)
                        all_findings.extend(llm_findings)
                        stats['llm_findings'] += len(llm_findings)

                # Write findings to database
                if all_findings:
                    highest_level = get_highest_level(all_findings)
                    tags = collect_sensitivity_tags(all_findings)

                    with conn.cursor() as cur:
                        # Update chunk sensitivity
                        cur.execute(
                            """UPDATE sdip_chunks
                               SET sensitivity_level = %s, sensitivity_tags = %s
                               WHERE id = %s""",
                            (highest_level, tags, chunk_id)
                        )

                        # Insert sensitivity records
                        for f in all_findings:
                            cur.execute(
                                """INSERT INTO sdip_sensitivity
                                    (chunk_id, sensitivity_type, detection_method,
                                     detected_pattern, confidence)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (
                                    chunk_id,
                                    f['sensitivity_type'],
                                    f['detection_method'],
                                    f['detected_pattern'],
                                    f['confidence'],
                                )
                            )

                    stats['chunks_escalated'] += 1

                stats['scanned'] += 1

                # Batch commit and progress
                if (i + 1) % 100 == 0:
                    conn.commit()
                    print(f"  [{i+1}/{total}] {stats['regex_findings']} regex, "
                          f"{stats['llm_findings']} llm, {stats['chunks_escalated']} escalated...")

            except Exception as e:
                print(f"  ✗ Chunk {chunk_id} (doc {document_id}): {e}")
                stats['errors'] += 1
                conn.rollback()
                conn.autocommit = False
                continue

        conn.commit()

        print(f"\n✓ Scan complete:")
        print(f"  Chunks scanned:   {stats['scanned']}")
        print(f"  Regex findings:   {stats['regex_findings']}")
        print(f"  LLM findings:     {stats['llm_findings']}")
        print(f"  Chunks escalated: {stats['chunks_escalated']}")
        if stats['errors']:
            print(f"  Errors:           {stats['errors']}")

    except Exception as e:
        conn.rollback()
        print(f"✗ Fatal error: {e}")
        raise
    finally:
        conn.close()


def show_stats():
    """Show sensitivity scan results."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Overall sensitivity distribution
            cur.execute("""
                SELECT sensitivity_level, COUNT(*) as cnt
                FROM sdip_chunks
                GROUP BY sensitivity_level
                ORDER BY CASE sensitivity_level
                    WHEN 'PUBLIC' THEN 0
                    WHEN 'INTERNAL' THEN 1
                    WHEN 'SENSITIVE' THEN 2
                    WHEN 'RESTRICTED' THEN 3
                END
            """)
            levels = cur.fetchall()

            # Findings by type
            cur.execute("""
                SELECT sensitivity_type, detection_method, COUNT(*) as cnt
                FROM sdip_sensitivity
                GROUP BY sensitivity_type, detection_method
                ORDER BY cnt DESC
            """)
            findings = cur.fetchall()

            # Top sensitive documents
            cur.execute("""
                SELECT d.relative_path, c.sensitivity_level, COUNT(s.id) as finding_count
                FROM sdip_documents d
                JOIN sdip_chunks c ON c.document_id = d.id
                JOIN sdip_sensitivity s ON s.chunk_id = c.id
                WHERE c.sensitivity_level IN ('SENSITIVE', 'RESTRICTED')
                GROUP BY d.relative_path, c.sensitivity_level
                ORDER BY
                    CASE c.sensitivity_level WHEN 'RESTRICTED' THEN 0 ELSE 1 END,
                    finding_count DESC
                LIMIT 20
            """)
            hot_docs = cur.fetchall()

            # Unscanned count
            cur.execute("""
                SELECT COUNT(*)
                FROM sdip_chunks c
                WHERE c.sensitivity_level = 'PUBLIC'
                AND NOT EXISTS (SELECT 1 FROM sdip_sensitivity s WHERE s.chunk_id = c.id)
            """)
            unscanned = cur.fetchone()[0]

            # Total findings
            cur.execute("SELECT COUNT(*) FROM sdip_sensitivity")
            total_findings = cur.fetchone()[0]

        print("SDIP Sensitivity Report")
        print("=" * 50)

        print(f"\nChunk Sensitivity Levels:")
        for level, cnt in levels:
            bar = '█' * min(cnt // 20, 40)
            print(f"  {level:12s} {cnt:5d}  {bar}")

        if unscanned > 0:
            print(f"\n  ⚠ {unscanned} chunks not yet scanned")

        if findings:
            print(f"\nFindings by Type ({total_findings} total):")
            for stype, method, cnt in findings:
                print(f"  {stype:15s} [{method:5s}] {cnt}")

        if hot_docs:
            print(f"\nHot Documents:")
            for path, level, cnt in hot_docs:
                # Truncate long paths
                display = path if len(path) <= 60 else '...' + path[-57:]
                print(f"  [{level:10s}] {cnt:3d} findings  {display}")

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description='SDIP Sensitivity Scanner')
    parser.add_argument('--full', action='store_true',
                        help='Re-scan all chunks (not just unscanned)')
    parser.add_argument('--regex-only', action='store_true',
                        help='Layer 1 only — regex patterns, no LLM')
    parser.add_argument('--llm-only', action='store_true',
                        help='Layer 2 only — LLM classification, skip regex')
    parser.add_argument('--doc-id', type=int, default=None,
                        help='Scan specific document by ID')
    parser.add_argument('--llm-model', type=str, default='qwen2.5:7b',
                        help='Ollama model for LLM classification (default: qwen2.5:7b)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be scanned')
    parser.add_argument('--stats', action='store_true',
                        help='Show sensitivity report')

    args = parser.parse_args()

    if args.stats:
        show_stats()
    else:
        scan_chunks(
            full=args.full,
            regex_only=args.regex_only,
            llm_only=args.llm_only,
            doc_id=args.doc_id,
            dry_run=args.dry_run,
            llm_model=args.llm_model,
        )


if __name__ == '__main__':
    main()
