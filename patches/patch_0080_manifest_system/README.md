# Patch 0080: Manifest System

**Version:** 1.15.0  
**Date:** 2026-02-14  
**Author:** Claude  
**Status:** The LAST integer-only patch number

---

## Overview

This patch implements a standardized manifest system for all future patches. It marks the transition from integer-only patch numbering (0001-0080) to semantic versioning (MAJOR.MINOR.PATCH) while maintaining backward compatibility.

## What This Patch Does

### Adds
- **manifest.json** requirement for all future patches
- **Semantic versioning** system (MAJOR.MINOR.PATCH)
- **get_next_patch_info.sh** - Determines next version number
- **validate_manifest.sh** - Validates patch manifests
- **session-start** - Diagnostic command for AI session starts
- **AI_PATCH_GENERATION_GUIDE.md** - Handoff guide for any AI tool
- **MANIFEST_TEMPLATE.json** - Template for new patches

### Changes
- All future patches MUST include manifest.json
- Directory names still use `patch_NNNN_` format (compatibility)
- Semantic versions live in manifest metadata
- Version increments follow semver: MAJOR (breaking), MINOR (features), PATCH (fixes)

## Installation

```bash
cd ~/Downloads
# Extract patch_0080_manifest_system.zip
cd patch_0080_manifest_system
./install.sh
```

## After Installation

### Standard Diagnostic Command

Run this at the start of any AI session:

```bash
session-start            # Full diagnostic (default)
session-start --patch    # Patch-focused (for generating patches)
session-start --quick    # Quick status check
```

**Modes:**
- **--full**: Complete system state (TODO, ARCHITECTURE, services, git)
- **--patch**: Patch info + recent patches + generation context
- **quick**: Just patch info and service status

Output is automatically copied to clipboard.

### Get Next Patch Info

```bash
/opt/mythos/patches/scripts/get_next_patch_info.sh
```

Output shows:
- Current system version
- Next patch number options (PATCH, MINOR, MAJOR)
- Recommended version based on change type

### Validate a Manifest

```bash
/opt/mythos/patches/scripts/validate_manifest.sh manifest.json
```

Checks:
- Valid JSON syntax
- All required fields present
- Semantic version format correct
- Recommended sections included

### AI Handoff Guide

Located at: `/opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md`

This guide enables:
- Claude to generate patches
- ChatGPT to generate patches  
- Iris to generate patches
- Any LLM to generate patches

All AIs will:
- Query the same diagnostic info
- Use consistent version numbering
- Follow the same manifest structure
- Maintain system coherence

## Versioning Rules

| Change Type | Increment | Example |
|-------------|-----------|---------|
| **Bug fix** | PATCH | 1.15.0 → 1.15.1 |
| **New feature** | MINOR | 1.15.0 → 1.16.0 |
| **Breaking change** | MAJOR | 1.15.0 → 2.0.0 |

## Manifest Schema

See `MANIFEST_TEMPLATE.json` or `AI_PATCH_GENERATION_GUIDE.md` for complete schema.

Required fields:
- `manifest_version` - Schema version
- `patch.number` - Integer (0081, 0082, etc.)
- `patch.semantic_version` - Semantic version (1.16.0)
- `patch.name` - Short snake_case name
- `patch.title` - Human readable title
- `patch.description` - What it does
- `patch.date` - YYYY-MM-DD
- `patch.author` - AI name

Recommended sections:
- `versioning` - Version increment details
- `dependencies` - What's required
- `changes` - Files/database/services affected
- `testing` - How to verify
- `rollback` - How to undo

## Example Session

### User Request
"Add voice transcription to bot"

### AI Workflow

1. **Get current state:**
   ```bash
   # User runs diagnostic, AI receives:
   {
     "latest_patch": "0080",
     "current_version": "1.15.0",
     "next_patch_integer": "0081",
     "next_version_minor": "1.16.0"
   }
   ```

2. **Determine increment:**
   - New feature = MINOR increment
   - 1.15.0 → 1.16.0

3. **Generate patch:**
   - Directory: `patch_0081_voice_transcription/`
   - Manifest version: `1.16.0`
   - All files under `opt/mythos/`
   - Valid `manifest.json`
   - Executable `install.sh`

4. **User installs:**
   - Downloads to ~/Downloads
   - Patch monitor auto-detects
   - Validates manifest
   - Runs install.sh
   - System now at version 1.16.0

## Files Created

```
/opt/mythos/
├── patches/
│   ├── scripts/
│   │   ├── get_next_patch_info.sh      # NEW
│   │   └── validate_manifest.sh        # NEW
│   └── MANIFEST_TEMPLATE.json          # NEW
└── docs/
    └── patch_system/
        └── AI_PATCH_GENERATION_GUIDE.md # NEW
```

## Backward Compatibility

- Old patches (0001-0080) still work
- No manifest required for legacy patches
- New patches (0081+) MUST have manifest
- Directory naming unchanged (`patch_NNNN_`)
- Semantic versioning is additive, not breaking

## Testing

### Validate This Patch

```bash
/opt/mythos/patches/scripts/validate_manifest.sh \
  /opt/mythos/patches/patch_0080_manifest_system/manifest.json
```

Expected: `✅ VALIDATION PASSED`

### Get Next Patch Info

```bash
/opt/mythos/patches/scripts/get_next_patch_info.sh
```

Expected output includes:
- Latest patch: 0080
- Current version: 1.15.0
- Next versions: 1.15.1 (PATCH), 1.16.0 (MINOR), 2.0.0 (MAJOR)

## Rollback

Safe to rollback - removes scripts but doesn't break existing patches.

```bash
# Via git tag (standard method)
cd /opt/mythos
git checkout pre-patch_0080_* -- .

# Remove installed files manually
rm /opt/mythos/patches/scripts/get_next_patch_info.sh
rm /opt/mythos/patches/scripts/validate_manifest.sh
rm /opt/mythos/patches/MANIFEST_TEMPLATE.json
rm -rf /opt/mythos/docs/patch_system/
```

## What's Next

After this patch, the system is ready for:
- Multi-AI patch generation
- Consistent semantic versioning
- Better dependency tracking
- Automated validation
- Clear rollback procedures

All future patches will have rich metadata, making the system more maintainable and AI-friendly.

---

**This is patch 0080. The last of the integers. The first of the manifests.**
