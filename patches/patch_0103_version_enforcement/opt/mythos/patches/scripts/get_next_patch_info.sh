#!/bin/bash
# Get next patch number and system version information
# Outputs JSON suitable for AI consumption
# Source of truth: git tags for version, patch directories for patch number

set -e

MYTHOS_ROOT="/opt/mythos"
cd "$MYTHOS_ROOT"

# Get version from git tags (source of truth)
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
LATEST_VERSION="${LATEST_TAG#v}"  # Strip leading v

# Get latest patch number from directories
LATEST_PATCH_DIR=$(ls -1d "$MYTHOS_ROOT/patches/patch_"* 2>/dev/null | sort -t_ -k2 -n | tail -1)
if [ -n "$LATEST_PATCH_DIR" ]; then
    LATEST_NAME=$(basename "$LATEST_PATCH_DIR")
    LATEST_NUM=$(echo "$LATEST_NAME" | grep -oP 'patch_\K\d+' || echo "0000")
else
    LATEST_NAME="none"
    LATEST_NUM="0000"
fi

# Check .version file
VERSION_FILE=$(cat "$MYTHOS_ROOT/.version" 2>/dev/null || echo "unknown")

# Check manifest of latest patch
MANIFEST_FILE="$LATEST_PATCH_DIR/manifest.json"
HAS_MANIFEST=false
MANIFEST_VERSION="unknown"
PATCH_TITLE="Unknown"
PATCH_DESC="No manifest found"
if [ -f "$MANIFEST_FILE" ]; then
    HAS_MANIFEST=true
    MANIFEST_VERSION=$(jq -r '.versioning.new_system_version // .patch.semantic_version // "unknown"' "$MANIFEST_FILE")
    PATCH_TITLE=$(jq -r '.patch.title // "Unknown"' "$MANIFEST_FILE")
    PATCH_DESC=$(jq -r '.patch.description // "No description"' "$MANIFEST_FILE")
fi

# Calculate next numbers
NEXT_NUM=$(printf "%04d" $((10#$LATEST_NUM + 1)))

# Parse semantic version for increment suggestions
IFS='.' read -r MAJOR MINOR PATCH <<< "$LATEST_VERSION"
MAJOR=${MAJOR:-1}
MINOR=${MINOR:-0}
PATCH=${PATCH:-0}

NEXT_PATCH="${MAJOR}.${MINOR}.$((PATCH + 1))"
NEXT_MINOR="${MAJOR}.$((MINOR + 1)).0"
NEXT_MAJOR="$((MAJOR + 1)).0.0"

# Version alignment check
ALIGNED=true
if [ "$VERSION_FILE" != "$LATEST_VERSION" ] && [ "$VERSION_FILE" != "unknown" ]; then
    ALIGNED=false
fi

# Output JSON
cat << EOF
{
  "latest_patch": {
    "directory": "$LATEST_NAME",
    "number": "$LATEST_NUM",
    "has_manifest": $HAS_MANIFEST,
    "manifest_version": "$MANIFEST_VERSION",
    "title": "$PATCH_TITLE",
    "description": "$PATCH_DESC"
  },
  "version": {
    "git_tag": "$LATEST_TAG",
    "version_file": "$VERSION_FILE",
    "aligned": $ALIGNED,
    "source_of_truth": "git tag: $LATEST_TAG"
  },
  "next_patch": {
    "number": "$NEXT_NUM",
    "format": "patch_${NEXT_NUM}_description",
    "version_if_patch": "$NEXT_PATCH",
    "version_if_minor": "$NEXT_MINOR",
    "version_if_major": "$NEXT_MAJOR"
  },
  "versioning_guide": {
    "PATCH": "Bug fixes, small changes → $NEXT_PATCH",
    "MINOR": "New features, backward compatible → $NEXT_MINOR",
    "MAJOR": "Breaking changes, major refactor → $NEXT_MAJOR"
  },
  "system_status": {
    "total_patches": $(ls -1d "$MYTHOS_ROOT/patches/patch_"* 2>/dev/null | wc -l),
    "patches_with_manifests": $(find "$MYTHOS_ROOT/patches/patch_"*/manifest.json 2>/dev/null | wc -l || echo 0),
    "total_git_tags": $(git tag -l "v*" | wc -l)
  }
}
EOF
