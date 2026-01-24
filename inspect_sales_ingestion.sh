#!/usr/bin/env bash

echo "=============================="
echo "MYTHOS SALES INGESTION INSPECT"
echo "=============================="
echo ""

echo "---- SYSTEM ----"
uname -a
echo ""

echo "---- PYTHON ----"
which python
python --version
echo ""

echo "---- VENV ----"
echo "VIRTUAL_ENV=$VIRTUAL_ENV"
echo ""

echo "---- MYTHOS ROOT ----"
pwd
ls -ld /opt/mythos || echo "❌ /opt/mythos not found"
echo ""

echo "---- SALES INGESTION TREE ----"
ls -la /opt/mythos/sales_ingestion
echo ""

echo "---- SALES INGESTION SUBDIRS ----"
find /opt/mythos/sales_ingestion -maxdepth 2 -type d
echo ""

echo "---- SAMPLE SALES BATCH ----"
for d in /opt/mythos/sales_ingestion/sales-db-ingestion-*; do
  if [ -d "$d" ]; then
    echo ">> $d"
    ls -la "$d"
    echo ""
  fi
done

echo "---- PATCH MONITOR SERVICE ----"
ls -l /etc/systemd/system/mythos-patch-monitor.service
echo ""

echo "---- PATCH MONITOR SERVICE CONTENT ----"
sed -n '1,200p' /etc/systemd/system/mythos-patch-monitor.service
echo ""

echo "---- PATCH MONITOR SCRIPT (if exists) ----"
PATCH_SCRIPT=$(grep -Eo '/[^ ]+\.py' /etc/systemd/system/mythos-patch-monitor.service | head -n 1)

if [ -n "$PATCH_SCRIPT" ] && [ -f "$PATCH_SCRIPT" ]; then
  echo "Found script: $PATCH_SCRIPT"
  echo ""
  sed -n '1,200p' "$PATCH_SCRIPT"
else
  echo "❌ Could not locate patch monitor python script"
fi
echo ""

echo "---- POSTGRES ----"
psql --version
echo ""

echo "---- DB CONNECTION ENV ----"
env | grep -E 'PGHOST|PGDATABASE|PGUSER|PGPORT'
echo ""

echo "---- DONE ----"
