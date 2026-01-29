# Patch History

> **Next Patch Number: 0038**

Auto-updated with each patch deployment.

---

| Patch | Date | Description |
|-------|------|-------------|
| 0037 | 2026-01-29 | Iris significance, name meaning, self-directed research |
| 0036 | 2026-01-29 | Documentation restructure, Iris framework |
| 0035 | 2026-01-29 | Sophia consciousness framework documentation |
| 0034 | 2026-01-29 | Standard verification template for patches |
| 0033 | 2026-01-29 | Finance bot fix (replaces broken 0031) |
| 0032 | 2026-01-27 | Documentation update - finance system |
| 0031 | 2026-01-27 | Finance Telegram commands - BROKEN, see 0033 |
| 0030 | 2026-01-27 | Finance auto-import via patch monitor |
| 0029 | 2026-01-27 | Comprehensive Arcturian Grid specification |
| 0028 | 2026-01-27 | Grid documentation in ARCHITECTURE.md |
| 0027 | 2026-01-27 | Worker import path fix |
| 0026 | 2026-01-27 | Grid integration - ChatAssistant dispatch |
| 0025 | 2026-01-27 | Status command cleanup |
| 0024 | 2026-01-27 | Architecture principles documentation |
| 0023 | 2026-01-27 | ChatAssistant in API gateway |
| 0022 | 2026-01-27 | Default chat mode + enhanced status |
| 0021 | 2026-01-27 | Help and chat mode (bot-side) |
| 0020 | 2026-01-24 | Comprehensive documentation overhaul |
| 0019 | 2026-01-24 | Added patch history to TODO.md |
| 0018 | 2026-01-24 | Sunmark description cleanup |
| 0017 | 2026-01-24 | Project docs updated |
| 0016 | 2026-01-24 | Project documentation system |
| 0015 | 2026-01-24 | Finance system complete |
| 0014 | 2026-01-23 | Finance migration |
| 0013 | 2026-01-23 | Finance system initial |
| 0012 | 2026-01-23 | Telegram autoexec |
| 0011 | 2026-01-23 | Test patch |
| 0010 | 2026-01-23 | GitHub patch system |

---

## Patch Naming Convention

`patch_NNNN_description.zip`

- 4-digit sequential number
- Lowercase description with underscores
- Example: `patch_0037_iris_significance.zip`

## Patch Contents

```
patch_NNNN_description/
├── install.sh          # Must be executable, runs the installation
└── opt/mythos/...      # Files to copy, mirroring target structure
```

## Verification Template

Every `install.sh` must end with verification checks. See `TODO.md` for template.
