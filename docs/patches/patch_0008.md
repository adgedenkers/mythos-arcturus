# Patch 0008: Orchestration System

**Applied:** 2026-01-21  
**Status:** ✅ Complete

## Overview

Adds asynchronous processing infrastructure with Redis task queues, Qdrant vector storage, and worker processes for distributed analysis.

## Components Added

### Qdrant (Vector Database)
- **Container:** `mythos-qdrant`
- **Port:** 6333 (HTTP), 6334 (gRPC)
- **Purpose:** Store and search text embeddings
- **Data:** `/opt/mythos/data/qdrant`

### Redis (Task Queue)
- **Container:** `mythos-redis`
- **Port:** 6379
- **Purpose:** Distribute tasks to workers
- **Queues:** grid, embedding, vision, temporal, entity, summary

### Workers (6 services)

| Worker | Service | Purpose |
|--------|---------|---------|
| Grid | mythos-worker-grid | Arcturian 9-node consciousness analysis |
| Embedding | mythos-worker-embedding | Generate text embeddings for Qdrant |
| Vision | mythos-worker-vision | Analyze images via Llama Vision |
| Temporal | mythos-worker-temporal | Extract dates, times, cycles |
| Entity | mythos-worker-entity | Resolve entities to Neo4j |
| Summary | mythos-worker-summary | Generate conversation summaries |

### API Modules
- `/opt/mythos/api/orchestrator.py` - Task dispatch to Redis
- `/opt/mythos/api/context_manager.py` - Context assembly for LLM

## Files Created

```
/opt/mythos/
├── workers/
│   ├── __init__.py
│   ├── worker.py          # Base worker class
│   ├── grid_worker.py
│   ├── embedding_worker.py
│   ├── vision_worker.py
│   ├── temporal_worker.py
│   ├── entity_worker.py
│   └── summary_worker.py
├── services/
│   ├── mythos-worker-grid.service
│   ├── mythos-worker-embedding.service
│   ├── mythos-worker-vision.service
│   ├── mythos-worker-temporal.service
│   ├── mythos-worker-entity.service
│   ├── mythos-worker-summary.service
│   └── install_services.sh
├── api/
│   ├── orchestrator.py
│   └── context_manager.py
└── utils/
    ├── test_pipeline.py
    └── debug_pipeline.py
```

## Database Tables Added

TimescaleDB tables (created as regular tables if extension unavailable):
- `grid_activation_timeseries`
- `entity_mention_timeseries`
- `emotional_state_timeseries`
- `astrological_events`
- `message_astrological_context`

## Service Management

```bash
# Start all workers
for w in grid embedding vision temporal entity summary; do
  sudo systemctl enable mythos-worker-$w
  sudo systemctl start mythos-worker-$w
done

# Check status
sudo systemctl status mythos-worker-* --no-pager

# View logs
journalctl -u mythos-worker-grid -f
```

## Verification

```bash
python3 /opt/mythos/utils/test_pipeline.py
python3 /opt/mythos/utils/debug_pipeline.py status
```

## Known Issues

- TimescaleDB extension not installed (using regular PostgreSQL tables)
- Workers don't yet receive tasks from orchestrator (integration pending)

## Next Steps

1. Wire orchestrator dispatch into /message endpoint
2. Create Qdrant collections for embeddings
3. Add embedding model download to embedding worker
4. Test full async flow
