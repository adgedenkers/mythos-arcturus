#!/usr/bin/env python3
"""
LOG-0021: SDIP LLM Classifier
Adds:
  - sdip_classifier.py — LLM-based topic/domain/entity extraction per chunk
  - sdip_chunk_topics table — per-chunk topic links for graph building
  - CLI: sdip-classify
  - Integrated classify_single_chunk_inline() for pipeline use
"""
import sys
import os
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=21,
    description='SDIP LLM classifier — topic/domain/entity extraction per chunk',
    patch_type='MINOR',
)
patch.begin()

# Deploy classifier
patch.deploy_file(
    'opt/mythos/sdip/sdip_classifier.py',
    '/opt/mythos/sdip/sdip_classifier.py'
)
os.chmod('/opt/mythos/sdip/sdip_classifier.py', 0o755)

# Create CLI symlink
link_path = '/opt/mythos/bin/sdip-classify'
if os.path.exists(link_path):
    os.remove(link_path)
wrapper = '''#!/bin/bash
exec /opt/mythos/.venv/bin/python3 /opt/mythos/sdip/sdip_classifier.py "$@"
'''
with open(link_path, 'w') as f:
    f.write(wrapper)
os.chmod(link_path, 0o755)

# Create the sdip_chunk_topics table
import psycopg2
conn = psycopg2.connect(
    host='/var/run/postgresql',
    database='mythos',
    user='postgres',
)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sdip_chunk_topics (
            id SERIAL PRIMARY KEY,
            chunk_id INTEGER NOT NULL REFERENCES sdip_chunks(id) ON DELETE CASCADE,
            topic TEXT NOT NULL,
            confidence FLOAT DEFAULT 1.0,
            model_used TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now(),
            UNIQUE(chunk_id, topic)
        );
        CREATE INDEX IF NOT EXISTS idx_sdip_chunk_topics_topic
            ON sdip_chunk_topics(topic);
        CREATE INDEX IF NOT EXISTS idx_sdip_chunk_topics_chunk
            ON sdip_chunk_topics(chunk_id);
    """)
conn.close()
print("  ✓ sdip_chunk_topics table created")

patch.finish()
