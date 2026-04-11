#!/bin/bash
# Validate a patch manifest.json file
# Usage: validate_manifest.sh <path_to_manifest.json>

set -e

MANIFEST_FILE="${1:-manifest.json}"

if [ ! -f "$MANIFEST_FILE" ]; then
    echo "ERROR: Manifest file not found: $MANIFEST_FILE"
    exit 1
fi

echo "Validating manifest: $MANIFEST_FILE"
echo ""

# Validate using Python (works everywhere, no jq dependency)
python3 << PYEOF
import json
import sys
import re

try:
    with open("$MANIFEST_FILE", 'r') as f:
        manifest = json.load(f)
    print("✓ Valid JSON syntax")
except json.JSONDecodeError as e:
    print(f"❌ FAIL: Invalid JSON syntax: {e}")
    sys.exit(1)

# Required fields
required_fields = {
    'manifest_version': ['manifest_version'],
    'patch.number': ['patch', 'number'],
    'patch.semantic_version': ['patch', 'semantic_version'],
    'patch.name': ['patch', 'name'],
    'patch.title': ['patch', 'title'],
    'patch.description': ['patch', 'description'],
    'patch.date': ['patch', 'date'],
    'patch.author': ['patch', 'author']
}

fail_count = 0

for field_name, field_path in required_fields.items():
    try:
        value = manifest
        for key in field_path:
            value = value[key]
        if not value:
            raise KeyError
        print(f"✓ {field_name} = {value}")
    except (KeyError, TypeError):
        print(f"❌ MISSING: {field_name}")
        fail_count += 1

# Validate semantic version
try:
    semver = manifest['patch']['semantic_version']
    if not re.match(r'^\d+\.\d+\.\d+$', semver):
        print(f"❌ FAIL: Invalid semantic version format: {semver} (must be MAJOR.MINOR.PATCH)")
        fail_count += 1
    else:
        print(f"✓ Valid semantic version: {semver}")
except KeyError:
    pass  # Already reported as missing

# Validate date format
try:
    date = manifest['patch']['date']
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        print(f"⚠️  WARNING: Date format should be YYYY-MM-DD: {date}")
except KeyError:
    pass

# Check recommended sections
recommended = ['dependencies', 'changes', 'testing', 'rollback']
print("\nRecommended sections:")
for section in recommended:
    if section in manifest:
        print(f"✓ {section} present")
    else:
        print(f"⚠️  {section} missing (recommended)")

print()
if fail_count == 0:
    print("✅ VALIDATION PASSED")
    sys.exit(0)
else:
    print(f"❌ VALIDATION FAILED: {fail_count} required fields missing")
    sys.exit(1)
PYEOF
