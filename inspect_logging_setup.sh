#!/usr/bin/env bash
set -euo pipefail

FILES=(
  "/opt/mythos/mythos_patch_monitor.py"
  "/opt/mythos/sales_ingestion/ingest_sales_zip.py"
)

echo "============================================================"
echo "MYTHOS LOGGING INSPECTION"
echo "============================================================"
echo ""

echo "---- SYSTEM ----"
uname -a
echo ""

echo "---- PYTHON ----"
/opt/mythos/.venv/bin/python --version
echo ""

for FILE in "${FILES[@]}"; do
  echo "============================================================"
  echo "FILE: ${FILE}"
  echo "============================================================"

  if [[ ! -f "$FILE" ]]; then
    echo "❌ FILE NOT FOUND"
    echo ""
    continue
  fi

  echo ""
  echo "---- FILE METADATA ----"
  ls -l "$FILE"
  sha256sum "$FILE"
  echo ""

  echo "---- LOGGING IMPORTS ----"
  grep -nE "import logging|from logging" "$FILE" || echo "(none)"
  echo ""

  echo "---- basicConfig CALLS ----"
  grep -nE "logging\.basicConfig" "$FILE" || echo "(none)"
  echo ""

  echo "---- HANDLER CREATION ----"
  grep -nE "FileHandler|StreamHandler|addHandler" "$FILE" || echo "(none)"
  echo ""

  echo "---- getLogger USAGE ----"
  grep -nE "getLogger" "$FILE" || echo "(none)"
  echo ""

  echo "---- LOGGER NAMES (strings) ----"
  grep -nE "getLogger\\(\"|getLogger\\('" "$FILE" || echo "(none)"
  echo ""

  echo "---- TOP OF FILE (first 40 lines) ----"
  sed -n '1,40p' "$FILE"
  echo ""

  echo "---- BOTTOM OF FILE (last 40 lines) ----"
  tail -n 40 "$FILE"
  echo ""
done

echo "============================================================"
echo "DONE"
echo "============================================================"
