#!/bin/bash
# Patch 0001: Finance Reports
# Creates /opt/mythos/finance/reports/ directory with template and first report

set -e

echo "Installing finance reports..."

# Create reports directory if it doesn't exist
mkdir -p /opt/mythos/finance/reports

# Copy files
cp -v opt/mythos/finance/reports/TEMPLATE.md /opt/mythos/finance/reports/
cp -v opt/mythos/finance/reports/2026-01-30_financial_status.md /opt/mythos/finance/reports/

echo "✓ Finance reports installed"
echo "  - Template: /opt/mythos/finance/reports/TEMPLATE.md"
echo "  - Report:   /opt/mythos/finance/reports/2026-01-30_financial_status.md"
