#!/bin/bash
# Get next patch number and system version information
# Outputs JSON suitable for AI consumption

set -e

# Find latest patch
LATEST_PATCH=$(ls -1d /opt/mythos/patches/patch_* 2>/dev/null | sort -V | tail -1)

if [ -z "$LATEST_PATCH" ]; then
    # No patches exist yet
    cat << 'EOF'
{
  "latest_patch": null,
  "latest_version": "1.0.0",
  "next_patch_integer": "0001",
  "next_version": "1.0.1",
  "recommended_name_format": "patch_0001_initial_system",
  "system_status": "No patches installed"
}
EOF
    exit 0
fi

# Extract info from latest patch
LATEST_NAME=$(basename "$LATEST_PATCH")
LATEST_NUM=$(echo "$LATEST_NAME" | grep -oP 'patch_\K\d+' || echo "0000")

# Check for manifest
MANIFEST_FILE="$LATEST_PATCH/manifest.json"
if [ -f "$MANIFEST_FILE" ]; then
    # Extract version info from manifest
    LATEST_VERSION=$(jq -r '.versioning.new_system_version // .patch.semantic_version // "1.0.0"' "$MANIFEST_FILE")
    PATCH_TITLE=$(jq -r '.patch.title' "$MANIFEST_FILE")
    PATCH_DESC=$(jq -r '.patch.description' "$MANIFEST_FILE")
else
    # No manifest, use legacy numbering
    LATEST_VERSION="1.0.$LATEST_NUM"
    PATCH_TITLE="Unknown"
    PATCH_DESC="No manifest found"
fi

# Calculate next numbers
NEXT_NUM=$(printf "%04d" $((10#$LATEST_NUM + 1)))

# Parse semantic version
IFS='.' read -r MAJOR MINOR PATCH <<< "$LATEST_VERSION"

# Default to patch increment
NEXT_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))"

# Output JSON
cat << EOF
{
  "latest_patch": {
    "directory": "$LATEST_NAME",
    "number": "$LATEST_NUM",
    "version": "$LATEST_VERSION",
    "title": "$PATCH_TITLE",
    "description": "$PATCH_DESC",
    "has_manifest": $([ -f "$MANIFEST_FILE" ] && echo "true" || echo "false")
  },
  "next_patch": {
    "integer": "$NEXT_NUM",
    "version_patch": "$NEXT_VERSION",
    "version_minor": "${MAJOR}.$((MINOR + 1)).0",
    "version_major": "$((MAJOR + 1)).0.0",
    "recommended_format": "patch_${NEXT_NUM}_description_name",
    "new_format": "${NEXT_VERSION}_description_name"
  },
  "versioning_guide": {
    "PATCH": "Bug fixes, small changes (${MAJOR}.${MINOR}.X)",
    "MINOR": "New features, backward compatible (${MAJOR}.X.0)",
    "MAJOR": "Breaking changes, major refactor (X.0.0)"
  },
  "system_status": {
    "total_patches": $(ls -1d /opt/mythos/patches/patch_* 2>/dev/null | wc -l),
    "patches_with_manifests": $(find /opt/mythos/patches/patch_*/manifest.json 2>/dev/null | wc -l),
    "current_system_version": "$LATEST_VERSION"
  },
  "note": "After patch_0080, use semantic versioning: MAJOR.MINOR.PATCH"
}
EOF
