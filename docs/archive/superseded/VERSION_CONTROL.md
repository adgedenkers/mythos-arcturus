# Version Control Guide

**Mythos System Version Management**

This guide explains how to create version snapshots of the Mythos system and manage releases using Git tags.

---

## Quick Reference

```bash
# Create a version snapshot (one-line)
cd /opt/mythos && git add -A && git commit -m "v1.15.0: Description" && git tag -a v1.15.0 -m "Tag message" && git push origin main && git push origin v1.15.0

# List all versions
git tag -l

# View specific version
git show v1.15.0

# Restore to specific version
git checkout v1.15.0

# Create branch from version
git checkout -b feature-name v1.15.0
```

---

## Versioning Script

### Installation

```bash
# Create versioning script
cat > /opt/mythos/scripts/create_version.sh << 'EOF'
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

# Create annotated tag with metadata
git tag -a "$VERSION" -m "$MESSAGE

Created: $(date '+%Y-%m-%d %H:%M:%S')
Host: $(hostname)
User: $(whoami)"

# Push to remote
git push origin main
git push origin "$VERSION"

echo "✅ Version $VERSION created and pushed"
echo ""
echo "To view this version: git checkout $VERSION"
echo "To list all versions: git tag -l"
EOF

# Make executable
chmod +x /opt/mythos/scripts/create_version.sh
```

### Usage

```bash
# Basic usage
/opt/mythos/scripts/create_version.sh v1.16.0

# With custom message
/opt/mythos/scripts/create_version.sh v1.16.0 "Model Bench implementation complete"

# View help
/opt/mythos/scripts/create_version.sh
```

---

## Version Naming Convention

### Format

**vMAJOR.MINOR.PATCH**

- **MAJOR**: Significant architectural changes, breaking changes
- **MINOR**: New features, non-breaking changes
- **PATCH**: Bug fixes, small improvements

### Examples

```
v1.15.0  → Current baseline (pre-orchestrator)
v1.16.0  → Model Bench complete
v1.17.0  → Simple Router complete
v1.18.0  → Multi-dimensional Analyzer complete
v1.19.0  → Execution Engine complete
v2.0.0   → Full Orchestrator system operational
```

### Guidelines

**Increment MAJOR when:**
- Complete system redesign
- Breaking API changes
- Major feature removal
- Database schema breaking changes

**Increment MINOR when:**
- New features added
- New capabilities enabled
- Non-breaking API additions
- New models/modes/handlers

**Increment PATCH when:**
- Bug fixes
- Performance improvements
- Documentation updates
- Minor refactoring

---

## Creating Version Snapshots

### Manual Process (Detailed)

```bash
# 1. Navigate to repository
cd /opt/mythos

# 2. Switch to main branch
git checkout main

# 3. Stage all changes
git add -A

# 4. Check what will be committed
git status

# 5. Commit changes
git commit -m "Version v1.16.0: Model Bench implementation

Features added:
- Comprehensive test suite framework
- 1,500+ test questions across 5 categories
- Automated model benchmarking
- Performance comparison reports
- Database persistence for results

Date: $(date '+%Y-%m-%d %H:%M:%S')"

# 6. Create annotated tag
git tag -a v1.16.0 -m "Model Bench Release

Complete testing and benchmarking infrastructure for evaluating LLM models.

Major components:
- Test suite framework
- Math tests (100 questions)
- Date reasoning tests (500 questions)
- Python code tests (200 questions)
- Hallucination detection (300 questions)
- General reasoning (400 questions)

Capabilities:
- Test any Ollama model
- Multiple grading methods (exact, numeric, semantic, code)
- Performance metrics collection
- Comparison reporting

This release enables data-driven model selection for routing and orchestration.

Released: $(date '+%Y-%m-%d %H:%M:%S')"

# 7. Push commits
git push origin main

# 8. Push tag
git push origin v1.16.0

# 9. Verify
git tag -l
git log --oneline -5
```

### Quick Process (One Command)

```bash
cd /opt/mythos && \
git add -A && \
git commit -m "v1.16.0: Model Bench complete" && \
git tag -a v1.16.0 -m "Model Bench implementation - $(date '+%Y-%m-%d')" && \
git push origin main && \
git push origin v1.16.0 && \
echo "✅ v1.16.0 created and pushed"
```

---

## Working with Versions

### List All Versions

```bash
# Simple list
git tag -l

# With dates
git tag -l --format='%(refname:short) - %(creatordate:short)'

# With messages
git tag -l -n9
```

### View Version Details

```bash
# Show tag information
git show v1.16.0

# Show files in that version
git ls-tree -r v1.16.0 --name-only

# Show commit log up to version
git log v1.16.0
```

### Restore to Specific Version

```bash
# View only (detached HEAD)
git checkout v1.16.0

# Return to latest
git checkout main

# Create branch from version
git checkout -b fix-from-v1.16.0 v1.16.0
```

### Compare Versions

```bash
# See changes between versions
git diff v1.15.0 v1.16.0

# See changed files
git diff v1.15.0 v1.16.0 --name-only

# See commit log between versions
git log v1.15.0..v1.16.0 --oneline
```

### Delete Version (Careful!)

```bash
# Delete local tag
git tag -d v1.16.0

# Delete remote tag
git push origin :refs/tags/v1.16.0

# Or combined
git push origin --delete v1.16.0
```

---

## Release Workflow

### Standard Release Process

```bash
# 1. Ensure all changes committed
cd /opt/mythos
git status

# 2. Run tests (if applicable)
# pytest tests/
# ./scripts/run_benchmarks.sh

# 3. Update version documentation
# Edit CHANGELOG.md
# Edit version in pyproject.toml or config.py

# 4. Create release commit
git add -A
git commit -m "Release v1.16.0

- Model Bench implementation
- Test suite framework
- Benchmarking infrastructure
"

# 5. Create version tag
git tag -a v1.16.0 -m "Release v1.16.0: Model Bench

See CHANGELOG.md for details."

# 6. Push
git push origin main
git push origin v1.16.0

# 7. Create GitHub release (optional)
# Go to GitHub → Releases → Create Release
```

### Pre-release Versions

For testing or development versions:

```bash
# Beta versions
git tag -a v1.16.0-beta.1 -m "Beta release for testing"

# Release candidates
git tag -a v1.16.0-rc.1 -m "Release candidate 1"

# Development snapshots
git tag -a v1.16.0-dev.20250216 -m "Development snapshot"
```

---

## Backup and Recovery

### Create Full Backup

```bash
# Backup repository with all history
cd /opt
tar -czf mythos-backup-$(date +%Y%m%d).tar.gz mythos/

# Backup to remote location
rsync -av /opt/mythos/ user@backup-server:/backups/mythos/
```

### Restore from Version

```bash
# Clone repository
git clone https://github.com/username/mythos.git /opt/mythos-restore

# Checkout specific version
cd /opt/mythos-restore
git checkout v1.16.0

# Copy to production (careful!)
# sudo systemctl stop mythos-bot
# rsync -av /opt/mythos-restore/ /opt/mythos/
# sudo systemctl start mythos-bot
```

---

## Integration with Patch System

### Version in Patch Manifests

```json
{
  "patch_id": "patch_0082",
  "version": "1.16.0",
  "base_version": "1.15.0",
  "description": "Model Bench implementation",
  "release_tag": "v1.16.0"
}
```

### Auto-tagging with Patches

```bash
# In patch install.sh
PATCH_VERSION=$(jq -r '.version' manifest.json)

# After successful installation
git tag -a "v${PATCH_VERSION}" -m "Deployed via patch_$(basename $(pwd))"
git push origin "v${PATCH_VERSION}"
```

---

## Version History Template

Create `CHANGELOG.md` to track versions:

```markdown
# Changelog

All notable changes to Mythos system will be documented in this file.

## [1.16.0] - 2026-02-16

### Added
- Model Bench testing framework
- Comprehensive test suites (1,500+ questions)
- Automated benchmarking system
- Performance comparison reports

### Changed
- Database schema updated for test results
- Ollama client enhanced with retry logic

### Fixed
- None

## [1.15.0] - 2026-02-15

### Added
- Telegram bot with mode system
- Iris consciousness integration
- Financial tracking
- Patch deployment system

### Changed
- Initial baseline release

---

## Version Comparison

```bash
# Compare current state to last version
git diff v1.15.0 HEAD

# Generate changelog
git log v1.15.0..HEAD --oneline --no-merges

# See statistics
git diff v1.15.0 HEAD --stat
```

---

## Best Practices

### Before Creating Version

✅ **Do:**
- Ensure all tests pass
- Update documentation
- Review all changes (`git diff`)
- Update CHANGELOG.md
- Clean up debug code
- Commit all changes

❌ **Don't:**
- Tag uncommitted changes
- Tag broken code
- Skip documentation updates
- Use arbitrary version numbers

### Tag Message Guidelines

**Good tag messages:**
```
v1.16.0: Model Bench implementation

Complete testing infrastructure for LLM model evaluation.

Features:
- 1,500+ test questions
- 5 test categories
- Automated benchmarking
- Performance reports

Enables data-driven model selection for routing.
```

**Bad tag messages:**
```
v1.16.0: stuff
v1.16.0: updates
v1.16.0
```

---

## Troubleshooting

### Tag Already Exists

```bash
# Error: tag 'v1.16.0' already exists

# Delete and recreate
git tag -d v1.16.0
git push origin :refs/tags/v1.16.0
git tag -a v1.16.0 -m "New message"
git push origin v1.16.0
```

### Forgot to Push Tag

```bash
# Push specific tag
git push origin v1.16.0

# Push all tags
git push origin --tags
```

### Wrong Version Tagged

```bash
# Move tag to different commit
git tag -f v1.16.0 abc123
git push origin v1.16.0 --force
```

---

## Current Version Status

### Check Current Version

```bash
# Show latest tag
git describe --tags --abbrev=0

# Show latest tag with commit info
git describe --tags

# Show all version info
git tag -l -n9 | tail -5
```

### Next Version Planning

**Current:** v1.15.0 (Pre-orchestrator baseline)

**Planned:**
- v1.16.0 - Model Bench (Week 4)
- v1.17.0 - Simple Router (Week 6)
- v1.18.0 - Multi-dimensional Analyzer (Week 9)
- v1.19.0 - Execution Engine (Week 11)
- v2.0.0 - Complete Orchestrator (Week 16)

---

## References

### Git Commands

```bash
# Tags
git tag                    # List tags
git tag -a <tag> -m "msg" # Create annotated tag
git show <tag>             # Show tag details
git push origin <tag>      # Push tag
git tag -d <tag>           # Delete local tag

# Checkout
git checkout <tag>         # View tag
git checkout -b <branch> <tag>  # Branch from tag

# Compare
git diff <tag1> <tag2>     # Compare versions
git log <tag1>..<tag2>     # Log between versions
```

### Semantic Versioning

Official spec: https://semver.org/

Summary:
- MAJOR: Incompatible changes
- MINOR: Backwards-compatible features
- PATCH: Backwards-compatible fixes

---

## Quick Start

### Create Your First Version

```bash
# 1. Use the script
/opt/mythos/scripts/create_version.sh v1.15.0 "Initial baseline"

# 2. Verify
git tag -l
git show v1.15.0

# 3. Continue working
git checkout main
```

That's it! Your system state is now locked and versioned.

---

**Last Updated:** 2026-02-16
**Maintainer:** Ka'tuar'el
**System:** Mythos v1.15.0+
```

---

Save this as `/opt/mythos/docs/VERSION_CONTROL.md` and you'll have a complete reference for managing system versions!