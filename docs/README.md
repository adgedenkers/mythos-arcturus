# Mythos System Documentation

## Overview

Mythos is a sovereign spiritual infrastructure system combining graph databases, vector storage, and AI processing for tracking soul lineages, incarnations, and spiritual patterns.

**Base Directory:** `/opt/mythos`  
**Primary User:** Ka'tuar'el (ka)

## Documentation Structure

```
/opt/mythos/docs/
├── README.md           # This file
├── tools/              # Utility and debugging tools
├── patches/            # Patch-specific documentation
├── architecture/       # System design docs
└── api/                # API endpoint documentation
```

## Quick Links

### Tools
- [Debug Pipeline](tools/debug_pipeline.md) - System monitoring and debugging
- [Test Pipeline](tools/test_pipeline.md) - Automated health checks

### Patches Applied
- [Patch 0008](patches/patch_0008.md) - Orchestration System (Qdrant, Redis, Workers)

### Architecture
- [System Overview](architecture/overview.md)
- [Data Flow](architecture/data_flow.md)

## Core Components

| Component | Port | Purpose |
|-----------|------|---------|
| FastAPI | 8000 | Main API |
| PostgreSQL | 5432 | Relational data |
| Neo4j | 7687 | Graph database |
| Qdrant | 6333 | Vector storage |
| Redis | 6379 | Task queue |
| Ollama | 11434 | Local LLM |

## Services

```bash
# API
sudo systemctl status mythos-api

# Workers
sudo systemctl status mythos-worker-grid
sudo systemctl status mythos-worker-embedding
sudo systemctl status mythos-worker-vision
sudo systemctl status mythos-worker-temporal
sudo systemctl status mythos-worker-entity
sudo systemctl status mythos-worker-summary
```

## Common Commands

```bash
# Activate environment
cd /opt/mythos && source .venv/bin/activate

# Run tests
python3 utils/test_pipeline.py

# Debug status
python3 utils/debug_pipeline.py status

# View logs
journalctl -u mythos-api -f
journalctl -u mythos-worker-grid -f
```

## Maintenance

### Restart All Services
```bash
sudo systemctl restart mythos-api
for w in grid embedding vision temporal entity summary; do
  sudo systemctl restart mythos-worker-$w
done
```

### Check All Services
```bash
python3 /opt/mythos/utils/debug_pipeline.py status
```

---
*Last updated: 2026-01-21*
