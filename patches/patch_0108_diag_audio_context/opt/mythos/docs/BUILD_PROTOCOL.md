# Mythos Build Protocol

**This document is mandatory reading before any system change. No exceptions.**

---

## Starting a New Session

Every new conversation involving Mythos work MUST begin with loading system context. No exceptions.

### Option A: Telegram `/context` command (preferred)
Send `/context` in Telegram. The bot outputs TODO.md + ARCHITECTURE.md + BUILD_PROTOCOL.md formatted for pasting into a new Claude conversation.

### Option B: Manual diagnostic dump
Run `~/diag.sh` and paste the output.

### Option C: Direct file paste
Copy the contents of these three files into the conversation:
1. `/opt/mythos/docs/TODO.md`
2. `/opt/mythos/docs/ARCHITECTURE.md`
3. `/opt/mythos/docs/BUILD_PROTOCOL.md`

**The AI must not propose, plan, or build anything until it has read and confirmed understanding of these documents.**

---

## The Golden Rule

> **If you don't know the current state of the system, you don't touch the system.**

Never assume. Never guess. Never build from memory of a previous session. Sessions don't carry state. The system on disk is the only truth.

---

## Phase 1: ASSESS

Before proposing any work, gather:

| What | How | Why |
|------|-----|-----|
| Current priorities | Read `TODO.md` | Know what's active, what's blocked, what's done |
| System architecture | Read `ARCHITECTURE.md` | Know what exists and how it connects |
| Current patch number | `git -C /opt/mythos tag --sort=-v:refname \| head -10` | Never guess or collide patch numbers |
| Target code | `cat` the actual files you'd modify | Know the real structure, not what you think it is |
| Running services | `systemctl status mythos-*` | Know what's live |
| Dependencies | Check imports, .env, requirements | Know what the code actually uses |

**If you can't get this information, ASK for a diagnostic dump. Do not proceed without it.**

**If the user is on mobile (Termius), provide a single script file they can run — never multi-line paste blocks.**

---

## Phase 2: PLAN

Present the plan to Adge before writing any code. The plan must include:

1. **What** — Clear description of what's being built or changed
2. **Where** — Exact file paths being created or modified
3. **Patch number** — Confirmed from actual git tags, not guessed
4. **Dependencies** — Any new packages, env vars, or config changes
5. **Service impact** — What needs to restart, what might break
6. **Integration points** — How this connects to existing code
7. **Testing steps** — How to verify it works after deployment

Format:

```
PATCH PLAN: patch_NNNN_description
═══════════════════════════════════
What: [description]
Files:
  NEW: /opt/mythos/path/to/new_file.py
  MOD: /opt/mythos/path/to/existing_file.py (adding X)
  NEW: /opt/mythos/path/to/another.py
Patch #: NNNN (confirmed: last tag is patch_NNNN-1)
New deps: [none | package names]
Env vars: [none | VAR_NAME=description]
Restarts: [service names]
Test: [how to verify]
```

**Wait for approval before proceeding.**

---

## Phase 3: BUILD

### Code Standards
- Match the style and patterns of existing code (don't introduce new frameworks or patterns without discussion)
- Use the venv Python: `/opt/mythos/.venv/bin/python3`
- All Python files get docstrings explaining what they do
- No hardcoded secrets — use .env and environment variables

### Patch Structure
```
patch_NNNN_description/
├── install.sh              # Executable, handles everything
├── opt/mythos/             # Files mirroring target paths
│   └── ...
├── test.sh                 # Optional: verification script
└── README.md               # What this patch does
```

### install.sh Rules
1. Starts with `set -e` (fail on any error)
2. Prints clear status messages as it goes
3. Creates directories before copying files
4. Sets ownership to `adge:adge`
5. Does NOT restart services automatically — prints instructions instead
6. Exits with clear success/failure message

---

## Phase 4: TEST

Testing happens BEFORE git commit, not after.

### Required Testing
1. **Syntax check**: `python3 -m py_compile <file>` for every Python file
2. **Import check**: Verify imports resolve in the venv
3. **Service check**: After restart, confirm service is running
4. **Functional check**: Actually exercise the new feature

### Test Commands
Provide specific test commands in the patch README and install.sh output. Examples:
```bash
# Syntax check
/opt/mythos/.venv/bin/python3 -m py_compile /opt/mythos/path/to/file.py

# Service check  
sudo systemctl restart mythos-bot.service
sudo systemctl status mythos-bot.service

# Functional check
# (specific to what was built — e.g., send /diag hw in Telegram)
```

### If Tests Fail
- Do NOT commit
- Diagnose the issue
- Fix and re-test
- Only proceed to Phase 5 when tests pass

---

## Phase 5: COMMIT

Git commits happen through the patch monitor system:

1. Patch zip is placed in `~/Downloads/`
2. Patch monitor detects, extracts, runs install.sh
3. Patch monitor commits to git with tag `patch_NNNN`
4. Patch monitor pushes to GitHub
5. Verify via `/patch_status` in Telegram

### Manual Git (only if patch monitor isn't involved)
```bash
cd /opt/mythos
git add -A
git commit -m "patch_NNNN: description of changes"
git tag patch_NNNN
git push origin main --tags
```

**Git is updated ONLY after successful testing. Never before.**

---

## Phase 6: UPDATE DOCS

**This is not optional. A patch is not complete until docs are updated.**

1. **TODO.md** — ALWAYS update:
   - Move completed items to Completed section
   - Update Active Work with current status
   - Add any new items that emerged during the work
2. **ARCHITECTURE.md** — Update if:
   - New services, endpoints, or modules were added
   - Directory structure changed
   - New environment variables or config were introduced
   - Integration points changed
3. **BUILD_PROTOCOL.md** — Update if:
   - We learned something new about the process
   - A failure revealed a missing step

**Include doc updates IN the patch itself** — the patch should contain updated .md files so they're committed together with the code changes. Docs and code travel together, always.

---

## Phase 7: VERIFY

After deployment:

1. Check `/patch_status` in Telegram
2. Run relevant `/diag` commands
3. Exercise the new feature
4. Confirm docs are accurate against what's actually running

---

## When Things Go Wrong

### During Build
- Stop, explain what happened, ask for guidance
- Don't try to fix-forward blindly

### During Testing  
- Report the error output
- Propose a fix but wait for approval before applying
- If unsure, ask

### After Deployment
- If a service won't start, check `journalctl -u <service> -n 50`
- If rollback is needed: `git -C /opt/mythos log --oneline -5` to find the pre-patch commit
- Roll back with: `git -C /opt/mythos revert HEAD` or check out specific files

### The Universal Rule
> **When in doubt, ASK. Asking is always better than guessing.**

---

## Diagnostic Dumps

When you need system state and the user is on mobile, provide a **single script file** approach:

```bash
cat << 'SCRIPT' > ~/diag.sh
#!/bin/bash
# ... commands here ...
SCRIPT
chmod +x ~/diag.sh
```

Then: `~/diag.sh && cat ~/diag.txt`

Never provide multi-line commands for direct paste — Termius and other mobile terminals will mangle them.

---

## Document Update Rules

| Document | When to Update | Included in Patch? |
|----------|---------------|-------------------|
| `TODO.md` | Every patch, every session | YES — always |
| `ARCHITECTURE.md` | Any new module, endpoint, service, env var, or structural change | YES — when relevant |
| `BUILD_PROTOCOL.md` | When process improves or a failure reveals a gap | YES — when relevant |

**Docs ship with code. A patch without doc updates is incomplete.**

---

*This protocol exists because building blind wastes time and breaks things. Follow it.*
