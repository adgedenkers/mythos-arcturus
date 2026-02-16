#!/bin/bash
# Create a version snapshot of the Mythos system

# Check if version provided
if [ -z "$1" ]; then
    echo "Usage: $0 <version> [message]"
    echo "Example: $0 v1.15.0 'Pre-orchestrator baseline'"
    exit 1
fi

VERSION="$1"
MESSAGE="${2:-System snapshot at $VERSION}"
REPO_DIR="/opt/mythos"

cd "$REPO_DIR" || exit 1

# Ensure clean state
git checkout main
git add -A

# Commit if there are changes
if ! git diff-staged --quiet; then
    git commit -m "Version $VERSION: $MESSAGE"
fi

# Create annotated tag
git tag -a "$VERSION" -m "$MESSAGE

Created: $(date '+%Y-%m-%d %H:%M:%S')
Host: $(hostname)
User: $(whoami)"

# Push
git push origin main
git push origin "$VERSION"

echo "✅ Version $VERSION created and pushed"
echo ""
echo "To view this version: git checkout $VERSION"
echo "To list all versions: git tag -l"
