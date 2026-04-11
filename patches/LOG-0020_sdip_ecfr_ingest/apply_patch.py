#!/usr/bin/env python3
"""
LOG-0020: SDIP Dataset Ingestion Framework + eCFR Parser
Adds:
  - parsers/ directory with ecfr_parser.py
  - sdip_ingest_dataset.py (multi-source dataset ingester)
  - datasets/ directory with README
  - CLI symlinks: sdip-ingest-dataset, ecfr-parse
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=20,
    description='SDIP dataset ingestion framework + eCFR parser',
    patch_type='MINOR',
)
patch.begin()

# Deploy parser module
patch.deploy_file(
    'opt/mythos/sdip/parsers/__init__.py',
    '/opt/mythos/sdip/parsers/__init__.py'
)
patch.deploy_file(
    'opt/mythos/sdip/parsers/ecfr_parser.py',
    '/opt/mythos/sdip/parsers/ecfr_parser.py'
)

# Deploy dataset ingester
patch.deploy_file(
    'opt/mythos/sdip/sdip_ingest_dataset.py',
    '/opt/mythos/sdip/sdip_ingest_dataset.py'
)

# Deploy datasets README
import os
os.makedirs('/opt/mythos/sdip/datasets', exist_ok=True)
patch.deploy_file(
    'opt/mythos/sdip/datasets/README.md',
    '/opt/mythos/sdip/datasets/README.md'
)

# Make scripts executable
os.chmod('/opt/mythos/sdip/parsers/ecfr_parser.py', 0o755)
os.chmod('/opt/mythos/sdip/sdip_ingest_dataset.py', 0o755)

# Create CLI symlinks in /opt/mythos/bin/
import subprocess

# sdip-ingest-dataset
link_path = '/opt/mythos/bin/sdip-ingest-dataset'
if os.path.exists(link_path):
    os.remove(link_path)
# Wrapper script that activates venv
wrapper = '''#!/bin/bash
exec /opt/mythos/.venv/bin/python3 /opt/mythos/sdip/sdip_ingest_dataset.py "$@"
'''
with open(link_path, 'w') as f:
    f.write(wrapper)
os.chmod(link_path, 0o755)

# ecfr-parse
link_path = '/opt/mythos/bin/ecfr-parse'
if os.path.exists(link_path):
    os.remove(link_path)
wrapper = '''#!/bin/bash
exec /opt/mythos/.venv/bin/python3 /opt/mythos/sdip/parsers/ecfr_parser.py "$@"
'''
with open(link_path, 'w') as f:
    f.write(wrapper)
os.chmod(link_path, 0o755)

# Ensure lxml is installed
subprocess.run(
    ['/opt/mythos/.venv/bin/pip', 'install', 'lxml', '-q'],
    check=False
)

patch.finish()
