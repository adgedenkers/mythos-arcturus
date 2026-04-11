---
title: "Mythos Orchestrator Documentation"
category: orchestrator
status: active
stream: LOG
location: docs
tags: [orchestrator, architecture, development]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Mythos Orchestrator Documentation

**Version:** 1.15.1  
**Phase:** 1.1 - Core Infrastructure

---

## Documentation Index

### Core Documentation
- **ARCHITECTURE.md** - System design and component overview
- **CHANGELOG.md** - Version history and changes
- **API.md** - API reference (Phase 2+)
- **DEVELOPMENT.md** - Development guide (Phase 2+)

### Guides
- **Installation Guide** - See `/opt/mythos/orchestrator/README.md`
- **Configuration Guide** - Environment variables and settings
- **Testing Guide** - How to run and create tests (Phase 1.3+)

### Reference
- **Database Schema** - Table definitions and relationships
- **Module Reference** - Python module documentation
- **CLI Reference** - Command-line tools (Phase 1.7+)

---

## Quick Links

**Getting Started:**
1. Read `/opt/mythos/orchestrator/README.md`
2. Review `ARCHITECTURE.md` for system overview
3. Check configuration in `/opt/mythos/orchestrator/.env`

**For Developers:**
1. See `ARCHITECTURE.md` for component details
2. Read module docstrings for API details
3. Follow development guide (coming in Phase 2)

**Version Control:**
- See `/opt/mythos/docs/VERSION_CONTROL.md` for git workflow

---

## Current Status

### Phase 1.1: Core Infrastructure ✅
- Project structure
- Database schema (7 orch_* tables)
- Configuration system
- Core utilities

### Next: Phase 1.2 - Ollama Integration
Deploy `patch_0083` (v1.15.2)

---

## File Organization

```
docs/orchestrator/
├── README.md           # This file
├── ARCHITECTURE.md     # System architecture
├── CHANGELOG.md        # Version history
├── API.md              # API reference (future)
└── DEVELOPMENT.md      # Dev guide (future)
```

---

## Contributing

This is an internal project for the Mythos system. Changes should follow:

1. Version semantic versioning (MAJOR.MINOR.PATCH)
2. Update CHANGELOG.md for all changes
3. Document new features in ARCHITECTURE.md
4. Keep README.md synchronized

---

## Support

**Documentation Issues:**
- File an issue in the Mythos repository
- Contact Ka'tuar'el

**System Issues:**
- Check `/opt/mythos/orchestrator/logs/`
- Review database logs
- Check Telegram bot `/patch_status`

---

**Last Updated:** 2026-02-16  
**Maintainer:** Ka'tuar'el  
**System:** Arcturus
