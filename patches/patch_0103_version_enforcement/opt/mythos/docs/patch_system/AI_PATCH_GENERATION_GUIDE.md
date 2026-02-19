# AI Patch Generation Guide for Mythos System

**Version:** 2.0.0  
**Last Updated:** 2026-02-19  
**Compatible AIs:** Claude (Anthropic), ChatGPT (OpenAI), Iris (Local Ollama), any LLM with file generation capability

---

## MANDATORY RULES (Non-Negotiable)

### 1. File Delivery Method

**NEVER use heredocs or inline bash to write multi-line Python/SQL files.**
The escaping is unreliable and causes repeated deployment failures.

**Allowed methods (in order of preference):**
1. **Patch system** — Build complete file in AI environment, zip it, user downloads, patch monitor installs. This is the DEFAULT for ALL real changes.
2. **Python temp script** — `cat > /tmp/fix.py << 'EOF'` with quoted heredoc delimiter, then `sudo python3 /tmp/fix.py`. Python handles its own quoting. Use for surgical hotfixes ONLY.
3. **Simple sed** — Only for single-line replacements with no special characters.

**NEVER do:** `echo '...' >> file.py`, unquoted heredocs for code, or `sudo sed` with complex regex containing quotes/backslashes.

### 2. Schema Verification Before SQL

**ALWAYS query actual table schemas before writing any SQL.**
```bash
sudo -u postgres psql -d mythos -c "\d tablename"
```
Column names, types, and constraints MUST match the real database. Do not assume from memory or previous sessions.

### 3. Patch Numbering and Versioning

- Patch numbers are sequential 4-digit integers: patch_0103, patch_0104, etc.
- Every patch MUST have a `manifest.json` with correct version numbers.
- Version in manifest MUST be the next increment from the ACTUAL latest git tag.
- The patch monitor reads `manifest.json` for the version (not auto-increment).
- The `.version` file is updated automatically by the patch monitor.

**To determine next patch number and version:**
```bash
mnp   # Copies next patch info to clipboard as JSON
# OR manually:
mversion   # Shows current version, patch, commit
```

### 4. Test Blocks

- All patches MUST include a paste-and-run terminal test block (NOT a separate file).
- Test blocks must NOT use `set -e` or `exit` (kills the terminal session).
- Test blocks should print results AND copy to clipboard via `| xclip -selection clipboard`.
- Separate the test into basic checks and an optional `--live` section.

### 5. Patch Contents Checklist

Every patch zip MUST contain:
- [ ] `manifest.json` with correct version
- [ ] `install.sh` with `#!/bin/bash` shebang  
- [ ] All files under `opt/mythos/` mirroring deploy paths
- [ ] Migration SQL if database changes needed

`install.sh` MUST:
- [ ] Set correct file ownership (typically root:root for system files)
- [ ] Restart affected services
- [ ] Print wiring instructions if manual steps needed
- [ ] NOT need to update `.version` (patch monitor handles this now)

---

## Quick Start

### 1. Get Current System State

Run on Arcturus:
```bash
mnp   # Copies JSON with next patch number and version to clipboard
```

Or request the user runs this diagnostic:
```bash
D=~/patch_context.txt; > "$D"
echo "=== CURRENT STATE ===" >> "$D"
mversion >> "$D" 2>&1
echo -e "\n=== NEXT PATCH ===" >> "$D"
source /opt/mythos/.venv/bin/activate && cd /opt/mythos/patches/scripts && ./get_next_patch_info.sh >> "$D" 2>&1
echo -e "\n=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied"
```

### 2. Determine Version Increment

| Change Type | Version Increment | Example |
|-------------|------------------|---------|
| Bug fix, typo, small tweak | **PATCH** (1.16.0 → 1.16.1) | Fix typo in error message |
| New feature, backward compatible | **MINOR** (1.16.0 → 1.17.0) | Add voice transcription |
| Breaking change, major refactor | **MAJOR** (1.16.0 → 2.0.0) | Change database schema fundamentally |

### 3. Generate Patch Structure

Create a zip file with this structure:
```
patch_NNNN_description.zip
└── patch_NNNN_description/
    ├── manifest.json          # REQUIRED
    ├── install.sh             # REQUIRED  
    └── opt/mythos/            # Files to deploy
        └── [your files here]
```

---

## Manifest Template

```json
{
  "manifest_version": "1.0.0",
  "patch": {
    "number": "NNNN",
    "semantic_version": "MAJOR.MINOR.PATCH",
    "name": "short_snake_case_name",
    "title": "Human Readable Title",
    "description": "Clear description of what this patch does",
    "date": "YYYY-MM-DD",
    "author": "Claude"
  },
  "versioning": {
    "current_system_version": "X.Y.Z",
    "new_system_version": "X.Y.Z",
    "version_increment": "minor|patch|major",
    "reason": "Why this version increment"
  },
  "dependencies": {
    "required_patches": [],
    "required_services": ["service-name"],
    "python_packages": [],
    "system_packages": []
  },
  "changes": {
    "files_added": [],
    "files_modified": [],
    "database_changes": [],
    "services_affected": []
  },
  "installation": {
    "estimated_time_minutes": 5,
    "requires_restart": true,
    "requires_sudo": true,
    "safe_mode": true
  },
  "testing": {
    "verification_steps": [],
    "verification_commands": []
  },
  "rollback": {
    "safe": true,
    "complexity": "low|medium|high",
    "automated": true
  }
}
```

---

## install.sh Template

```bash
#!/bin/bash
# Patch NNNN: Description
set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS_ROOT="/opt/mythos"

echo "=== Installing Patch NNNN: Title ==="

# 1. Copy files
echo "Step 1: Copying files..."
sudo cp "$PATCH_DIR/opt/mythos/path/file.py" "$MYTHOS_ROOT/path/"
sudo chown root:root "$MYTHOS_ROOT/path/file.py"
echo "  ✓ Files copied"

# 2. Database changes (if needed)
# sudo -u postgres psql -d mythos -f "$PATCH_DIR/migration.sql"

# 3. Restart services
echo "Step 2: Restarting services..."
sudo systemctl restart mythos-service.service
sleep 2

# 4. Verify
if systemctl is-active --quiet mythos-service.service; then
    echo "  ✓ Service running"
else
    echo "  ✗ Service failed!"
    exit 1
fi

echo "=== Patch NNNN Complete ==="
```

---

## Version Increment Rules

### PATCH (X.Y.**Z**)
- Bug fixes
- Typo corrections
- Process/tooling improvements
- Performance improvements
- No new user-facing features

### MINOR (X.**Y**.0)
- New features (commands, handlers, capabilities)
- New database tables
- New services
- Backward compatible changes

### MAJOR (**X**.0.0)
- Breaking API changes
- Fundamental architecture changes
- Database schema breaking changes
- Major system redesign

---

## Handoff Between AIs

When switching AI mid-session, the new AI should run:
```bash
mnp   # Get current patch/version state
```

And request:
```bash
cat /opt/mythos/docs/TODO.md
cat /opt/mythos/docs/ARCHITECTURE.md
```

This gives full context to continue work seamlessly.

---

## Common Pitfalls

1. **Wrong column names in SQL** — ALWAYS run `\d tablename` first
2. **Heredoc escaping failures** — Use patch system or temp Python scripts
3. **Version mismatch** — Always check `mversion` before building a patch
4. **install.sh not executable** — Patch monitor now handles chmod, but verify
5. **Missing manifest** — Patch monitor will warn but still auto-increment version
6. **Forgetting to restart services** — install.sh MUST restart affected services
7. **Testing in production** — Once Docker test env exists, use that first

---

**End of AI Patch Generation Guide**
