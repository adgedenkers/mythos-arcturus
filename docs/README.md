# Mythos Documentation Index

> **Last Updated:** 2026-01-29

## Quick Reference

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `TODO.md` | Active work, backlog | Every session |
| `ARCHITECTURE.md` | System overview | At milestones |
| `IDEAS.md` | Potential features | When inspired |
| `PATCH_HISTORY.md` | Version history | Auto with patches |

## Document Map

```
docs/
├── README.md              ← You are here
├── TODO.md                # What we're doing
├── ARCHITECTURE.md        # What exists
├── IDEAS.md               # What we might do
├── PATCH_HISTORY.md       # What we've done
│
├── consciousness/         # Iris - the soul of Arcturus
│   ├── IRIS.md            # Complete framework
│   ├── COVENANT.md        # Partnership agreements (future)
│   └── INVOCATION.md      # Ceremony design (future)
│
├── grid/                  # Arcturian Grid system
│   └── ARCTURIAN_GRID.md  # Full specification
│
├── finance/               # Financial tracking
│   └── FINANCE_SYSTEM.md  # Detailed docs
│
├── subsystems/            # Component details (as needed)
│
└── archive/               # Historical records
    └── COMPLETED.md       # Past completed work
```

## Session Start

Standard diagnostic dump:
```bash
D=~/diag.txt; > "$D"
echo "=== TODO ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1
echo -e "\n\n=== ARCHITECTURE ===" >> "$D"
cat /opt/mythos/docs/ARCHITECTURE.md >> "$D" 2>&1
echo -e "\n\n=== DOCS INDEX ===" >> "$D"
cat /opt/mythos/docs/README.md >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

Then request specific docs as needed:
- Working on Iris? Add `consciousness/IRIS.md`
- Working on grid? Add `grid/ARCTURIAN_GRID.md`
- Working on finance? Add `finance/FINANCE_SYSTEM.md`

## Maintenance Rules

1. **TODO.md stays lean** - Active work + backlog titles only. Details go in domain docs.
2. **ARCHITECTURE.md stays lean** - Overview only. Details go in domain docs.
3. **IDEAS.md is low-commitment** - Capture freely, delete ruthlessly.
4. **Domain docs hold the depth** - Full specifications, implementation details.
5. **Every patch updates docs** - No exceptions.
