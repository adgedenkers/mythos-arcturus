# AI Patch Generation Guide for Mythos System

**Version:** 1.0.0  
**Last Updated:** 2026-02-14  
**Compatible AIs:** Claude (Anthropic), ChatGPT (OpenAI), Iris (Local Ollama), any LLM with file generation capability

---

## Quick Start

### 1. Get Current System State

Request the user runs this diagnostic command on Arcturus:

```bash
D=~/patch_context.txt; > "$D"

echo "=== LATEST PATCH INFO ===" >> "$D"
LATEST_PATCH=$(ls -1d /opt/mythos/patches/patch_* 2>/dev/null | sort -V | tail -1)
if [ -n "$LATEST_PATCH" ]; then
    echo "Latest: $(basename $LATEST_PATCH)" >> "$D"
    [ -f "$LATEST_PATCH/manifest.json" ] && cat "$LATEST_PATCH/manifest.json" >> "$D"
fi

echo -e "\n\n=== NEXT PATCH NUMBER ===" >> "$D"
if [ -n "$LATEST_PATCH" ]; then
    LATEST_NUM=$(basename "$LATEST_PATCH" | grep -oP 'patch_\K\d+')
    NEXT_NUM=$(printf "%04d" $((10#$LATEST_NUM + 1)))
    
    # Get semantic version if manifest exists
    if [ -f "$LATEST_PATCH/manifest.json" ]; then
        CURRENT_VER=$(python3 -c "import json; print(json.load(open('$LATEST_PATCH/manifest.json'))['versioning']['new_system_version'])")
        IFS='.' read -r MAJ MIN PAT <<< "$CURRENT_VER"
        echo "Current system version: $CURRENT_VER" >> "$D"
        echo "Next PATCH version: ${MAJ}.${MIN}.$((PAT + 1))" >> "$D"
        echo "Next MINOR version: ${MAJ}.$((MIN + 1)).0" >> "$D"
        echo "Next MAJOR version: $((MAJ + 1)).0.0" >> "$D"
    else
        echo "Legacy numbering only" >> "$D"
    fi
    
    echo "Next patch integer: patch_${NEXT_NUM}_" >> "$D"
else
    echo "No patches found. Start with patch_0001_" >> "$D"
fi

echo -e "\n\n=== SYSTEM DOCS ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D"
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D"

cat "$D" | clip && echo "✓ Copied to clipboard"
```

User pastes the result into your conversation.

### 2. Determine Version Increment

| Change Type | Version Increment | Example |
|-------------|------------------|---------|
| Bug fix, typo, small tweak | **PATCH** (1.15.0 → 1.15.1) | Fix typo in error message |
| New feature, backward compatible | **MINOR** (1.15.0 → 1.16.0) | Add voice transcription |
| Breaking change, major refactor | **MAJOR** (1.15.0 → 2.0.0) | Change database schema |

### 3. Generate Patch Structure

Create a zip file with this structure:

```
patch_NNNN_description.zip
└── patch_NNNN_description/
    ├── manifest.json          # REQUIRED
    ├── install.sh             # REQUIRED
    ├── README.md              # RECOMMENDED
    └── opt/mythos/            # Files to deploy
        └── [your files here]
```

---

## Manifest Template

Copy and fill this out:

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
    "author": "YourAIName"
  },
  "versioning": {
    "current_system_version": "1.15.0",
    "new_system_version": "1.16.0",
    "version_increment": "minor|patch|major",
    "reason": "Why this version increment"
  },
  "dependencies": {
    "required_patches": [],
    "required_services": ["service-name"],
    "python_packages": ["package-name"],
    "system_packages": ["apt-package"],
    "minimum_system_version": "1.0.0"
  },
  "changes": {
    "files_added": ["/opt/mythos/path/file.py"],
    "files_modified": ["/opt/mythos/existing/file.py"],
    "database_changes": ["Description of DB changes"],
    "services_affected": ["mythos-service.service"]
  },
  "installation": {
    "estimated_time_minutes": 5,
    "requires_restart": true,
    "requires_sudo": true,
    "safe_mode": true
  },
  "testing": {
    "verification_steps": [
      "Step 1 description",
      "Step 2 description"
    ],
    "verification_commands": [
      "command to run",
      "another command"
    ]
  },
  "rollback": {
    "safe": true,
    "complexity": "low|medium|high",
    "automated": true,
    "notes": "What happens on rollback"
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
echo "Step 1/N: Copying files..."
cp "$PATCH_DIR/opt/mythos/path/file.py" "$MYTHOS_ROOT/path/"
echo "  ✓ Files copied"

# 2. Install dependencies (if needed)
# /opt/mythos/.venv/bin/pip install package --break-system-packages

# 3. Database changes (if needed)
# sudo -u postgres psql -d mythos -f migration.sql

# 4. Restart services (if needed)
echo "Step N: Restarting services..."
sudo systemctl restart mythos-service.service
sleep 2

# 5. Verify
if systemctl is-active --quiet mythos-service.service; then
    echo "  ✓ Service running"
else
    echo "  ✗ Service failed!"
    exit 1
fi

echo ""
echo "=== Patch NNNN Complete ==="
```

---

## Naming Conventions

### Before Patch 0080 (Legacy)
- `patch_0079_description.zip`
- Integer only, 4 digits, zero-padded

### After Patch 0080 (New Standard)
- **Directory name:** `patch_0081_description/` (maintains backward compatibility)
- **Manifest version:** `1.16.0` (semantic versioning)
- **File names unchanged:** Still uses integer-based naming for directory/archive

This hybrid approach maintains compatibility with existing tooling while adding semantic versioning metadata.

---

## Complete Example

### User Request
"Add voice message transcription to Telegram bot"

### Your Analysis
- This is a new feature → MINOR version increment
- Current version: 1.15.0 → New version: 1.16.0
- Last patch: 0080 → Next patch: 0081

### manifest.json
```json
{
  "manifest_version": "1.0.0",
  "patch": {
    "number": "0081",
    "semantic_version": "1.16.0",
    "name": "voice_transcription",
    "title": "Voice Message Transcription",
    "description": "Adds voice message handling with GPU-accelerated whisper",
    "date": "2026-02-14",
    "author": "Claude"
  },
  "versioning": {
    "current_system_version": "1.15.0",
    "new_system_version": "1.16.0",
    "version_increment": "minor",
    "reason": "New feature: voice transcription capability"
  },
  "dependencies": {
    "required_patches": ["0074"],
    "required_services": ["mythos-bot.service"],
    "python_packages": ["faster-whisper"],
    "system_packages": ["ffmpeg"]
  },
  "changes": {
    "files_added": [
      "/opt/mythos/services/transcription.py",
      "/opt/mythos/telegram_bot/handlers/voice_handler.py"
    ],
    "files_modified": [
      "/opt/mythos/telegram_bot/mythos_bot.py"
    ],
    "services_affected": ["mythos-bot.service"]
  },
  "testing": {
    "verification_steps": [
      "Send voice message in Telegram",
      "Verify transcript appears"
    ]
  },
  "rollback": {
    "safe": true,
    "complexity": "low",
    "automated": true
  }
}
```

---

## Validation Before Delivery

Always validate your manifest:

```bash
python3 << 'PYEOF'
import json
with open('manifest.json', 'r') as f:
    manifest = json.load(f)
required = ['manifest_version', 'patch', 'versioning', 'dependencies', 'changes']
for field in required:
    assert field in manifest, f"Missing: {field}"
print("✓ Manifest valid")
PYEOF
```

---


---

## MANDATORY RULES (Added 2026-02-19)

### File Delivery Method
**NEVER use heredocs or inline bash to write multi-line Python/SQL files.**
The escaping is unreliable and has caused repeated deployment failures.

**Allowed methods (in order of preference):**
1. **Patch system** — Build complete file in Claude/AI environment, zip it, user downloads, patch monitor installs. This is the default for ALL real changes.
2. **Python temp script** — `cat > /tmp/fix.py << 'EOF'` with a heredoc delimiter, then `sudo python3 /tmp/fix.py`. Python handles its own quoting. Use for surgical hotfixes only.
3. **Simple sed** — Only for single-line replacements with no special characters.

**NEVER do:** `echo '...' >> file`, `cat << 'EOF' >> file.py` for multi-line code, or `sudo sed` with complex regex containing quotes.

### Schema Verification Before SQL
**ALWAYS query actual table schemas before writing any SQL.**
```bash
sudo -u postgres psql -d mythos -c "\d tablename"
```
Column names, types, and constraints MUST match the real database. Do not assume from memory or previous sessions.

### Patch Numbering and Versioning
- Patch numbers are sequential 4-digit integers: patch_0103, patch_0104, etc.
- Every patch MUST have a manifest.json with correct version numbers.
- Version in manifest MUST be the next increment from the ACTUAL latest git tag.
- After install, patch monitor MUST create a git tag matching the manifest version.
- The .version file MUST be updated by install.sh to match the manifest version.

### To determine next patch number and version:
```bash
# Get real state
LAST_TAG=$(cd /opt/mythos && git describe --tags --abbrev=0 2>/dev/null)
LAST_PATCH=$(ls -1d /opt/mythos/patches/patch_* 2>/dev/null | sort -t_ -k2 -n | tail -1 | xargs basename)
echo "Last tag: $LAST_TAG"
echo "Last patch: $LAST_PATCH"
```

### Test Blocks
- All patches MUST include a paste-and-run terminal test block (not a file).
- Test blocks must NOT use `set -e` or `exit` (kills the terminal).
- Test blocks should print results AND copy to clipboard via `xclip -selection clipboard`.

### Patch Contents Checklist
Every patch zip MUST contain:
- [ ] manifest.json with correct version
- [ ] install.sh (with `chmod +x` in the zip or set by monitor)
- [ ] All files under opt/mythos/ mirroring deploy paths
- [ ] Migration SQL if database changes are needed

install.sh MUST:
- [ ] Update /opt/mythos/.version with the new version
- [ ] Create git tag matching manifest version
- [ ] Set correct file ownership
- [ ] Restart affected services
- [ ] Print wiring instructions if manual steps needed


## Common Pitfalls

1. **Wrong version increment**
   - Bug fix but used MINOR → Should be PATCH
   - Breaking change but used MINOR → Should be MAJOR

2. **Missing dependencies**
   - Forgot to list required Python packages
   - Didn't specify which services need restart

3. **Invalid JSON**
   - Trailing commas
   - Unescaped quotes in strings
   - Always validate before delivery

4. **install.sh not executable**
   - Must have `#!/bin/bash` shebang
   - Must have `set -e` for error handling
   - Remember to make it executable in your generation process

---

## Temp File Format

When user requests a patch, generate `/tmp/mythos_patch_context.json`:

```json
{
  "session": {
    "timestamp": "2026-02-14T10:30:00Z",
    "ai": "Claude",
    "user": "Ka'tuar'el"
  },
  "current_state": {
    "last_patch": "0080",
    "current_version": "1.15.0",
    "total_patches": 80
  },
  "next_patch": {
    "number": "0081",
    "version_patch": "1.15.1",
    "version_minor": "1.16.0",
    "version_major": "2.0.0"
  },
  "request": {
    "description": "Add voice transcription",
    "type": "feature",
    "urgency": "normal"
  },
  "decision": {
    "version_increment": "minor",
    "new_version": "1.16.0",
    "rationale": "New feature, backward compatible"
  }
}
```

---

## Handoff Between AIs

If user wants to switch AI mid-patch:

1. **Current AI generates temp file:** `/tmp/mythos_patch_context.json`
2. **User copies file content to new AI**
3. **New AI reads context and continues from that state**

This ensures consistent version numbering across AI tools.

---

## Questions?

Common questions and answers:

**Q: What if I don't know the current version?**  
A: Ask user to run the diagnostic command at the top of this doc.

**Q: Should I use MAJOR version for big patches?**  
A: Only if it breaks backward compatibility. Big ≠ breaking.

**Q: Can I skip the manifest?**  
A: No. After patch 0080, all patches MUST have manifest.json.

**Q: What about database migrations?**  
A: Include SQL in patch, reference in manifest.json under `changes.database_changes`.

---

**End of AI Handoff Guide**

Save this file and reference it when generating patches for the Mythos system.
