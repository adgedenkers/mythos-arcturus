#!/usr/bin/env bash
# Patch 0095 - Google Photos Takeout Ingestion Pipeline
# Version: v1.16.1

set -euo pipefail

PATCH="0095"
VERSION="v1.16.1"

echo "╔══════════════════════════════════════════════════════╗"
echo "║  Patch ${PATCH} - Google Photos Ingestion - ${VERSION}  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── 1. Install exiftool ───────────────────────────────────────────────────────
echo "▶ Installing exiftool..."
apt-get install -y libimage-exiftool-perl > /dev/null 2>&1
echo "  ✓ exiftool installed: $(exiftool -ver)"

# ── 2. Install Python deps ────────────────────────────────────────────────────
echo ""
echo "▶ Installing Python dependencies..."
/opt/mythos/.venv/bin/pip install pillow --quiet
echo "  ✓ Dependencies ready"

# ── 3. Install ingestion script ───────────────────────────────────────────────
echo ""
echo "▶ Installing ingestion script..."
cp opt/mythos/photos/google_ingest.py /opt/mythos/photos/google_ingest.py
chmod +x /opt/mythos/photos/google_ingest.py
echo "  ✓ Script installed at /opt/mythos/photos/google_ingest.py"

# ── 4. Create import directories ─────────────────────────────────────────────
echo ""
echo "▶ Ensuring import directories exist..."
mkdir -p /opt/photos/import/google/zips
mkdir -p /opt/photos/import/google/extracted
mkdir -p /opt/photos/import/google/staging
mkdir -p /opt/photos/import/google/ready
echo "  ✓ Directories ready"

# ── 5. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   INSTALLATION COMPLETE                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  WHEN GOOGLE TAKEOUT ARRIVES:                                ║"
echo "║                                                              ║"
echo "║  1. Download all zip files from Google                       ║"
echo "║  2. Copy them to Arcturus:                                   ║"
echo "║       scp takeout-*.zip adge@arcturus.local:/opt/photos/import/google/zips/"
echo "║                                                              ║"
echo "║  3. Run dry-run first to see what will happen:               ║"
echo "║       /opt/mythos/.venv/bin/python3 \\                        ║"
echo "║         /opt/mythos/photos/google_ingest.py \\                ║"
echo "║         --zips /opt/photos/import/google/zips --dry-run      ║"
echo "║                                                              ║"
echo "║  4. Run for real:                                            ║"
echo "║       /opt/mythos/.venv/bin/python3 \\                        ║"
echo "║         /opt/mythos/photos/google_ingest.py \\                ║"
echo "║         --zips /opt/photos/import/google/zips                ║"
echo "║                                                              ║"
echo "║  5. In Immich UI:                                            ║"
echo "║     Administration → Libraries → Create External Library     ║"
echo "║     Path: /opt/photos/import/google/ready                    ║"
echo "║                                                              ║"
echo "║  Log file: /opt/photos/import/google/ingest.log              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Patch ${PATCH} ${VERSION} complete."
