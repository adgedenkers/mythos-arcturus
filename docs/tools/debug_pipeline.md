# Debug Pipeline Tool

**Location:** `/opt/mythos/utils/debug_pipeline.py`  
**Created:** 2026-01-21  
**Patch:** 0008 - Orchestration System

## Overview

Multi-purpose debugging and monitoring tool for the Mythos orchestration pipeline. Provides real-time visibility into system health, queue status, worker activity, and message flow.

## Quick Start

```bash
cd /opt/mythos
source .venv/bin/activate

# Full system status
python3 utils/debug_pipeline.py status

# Send test message
python3 utils/debug_pipeline.py send "Test message about spiral time"
```

## Commands

### `status`
Shows complete system health check.

```bash
python3 utils/debug_pipeline.py status
```

**Checks:**
- API health (localhost:8000)
- Redis connection and queue depths
- Qdrant connection and collections
- Worker service status (systemd)

---

### `queues`
Displays contents of all Redis worker queues.

```bash
python3 utils/debug_pipeline.py queues
```

**Queues monitored:**
- `mythos:grid` - Arcturian Grid analysis tasks
- `mythos:embedding` - Text embedding generation
- `mythos:vision` - Image/photo analysis
- `mythos:temporal` - Time extraction tasks
- `mythos:entity` - Entity resolution tasks
- `mythos:summary` - Conversation summarization

---

### `results`
Shows worker processing results stored in Redis.

```bash
python3 utils/debug_pipeline.py results
```

**Output includes:**
- Result key
- Worker type
- Processing status
- Result preview

---

### `clear`
Clears all queues and results. Useful for resetting state during testing.

```bash
python3 utils/debug_pipeline.py clear
```

**⚠️ Warning:** This deletes all pending tasks and results.

---

### `send [message]`
Sends a test message through the pipeline.

```bash
# Default test message
python3 utils/debug_pipeline.py send

# Custom message
python3 utils/debug_pipeline.py send "I'm exploring the connection between spiral time and the Montségur event"
```

**Uses:**
- API key: ka (Ka'tuar'el)
- Conversation ID: debug-test-001
- Endpoint: POST /message

---

### `logs [worker] [lines]`
Shows recent logs from a worker service.

```bash
# Default: grid worker, 20 lines
python3 utils/debug_pipeline.py logs

# Specific worker
python3 utils/debug_pipeline.py logs embedding

# More lines
python3 utils/debug_pipeline.py logs vision 50
```

**Available workers:** grid, embedding, vision, temporal, entity, summary

---

### `help`
Displays command reference.

```bash
python3 utils/debug_pipeline.py help
```

## Configuration

Located at top of script:

```python
API_URL = "http://localhost:8000"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
API_KEY = "cHPIHNR7DOE_rq85ZDjJkAiJcbik8ub7U9iTGCjbwyc"  # ka
```

## Dependencies

- `redis` - Redis client
- `requests` - HTTP client
- `systemctl` - Worker status checks (system)

## Related Tools

- `/opt/mythos/utils/test_pipeline.py` - Simple pass/fail test
- `/opt/mythos/utils/test` - Quick test runner alias

## Troubleshooting

### "Connection refused" on API
```bash
sudo systemctl status mythos-api
sudo systemctl restart mythos-api
```

### Workers not processing
```bash
# Check if workers are running
python3 utils/debug_pipeline.py status

# Check specific worker logs
python3 utils/debug_pipeline.py logs grid 50

# Restart a worker
sudo systemctl restart mythos-worker-grid
```

### Queues backing up
```bash
# Check queue depths
python3 utils/debug_pipeline.py queues

# Check worker logs for errors
python3 utils/debug_pipeline.py logs embedding 100
```

## Changelog

| Date | Change |
|------|--------|
| 2026-01-21 | Initial creation with patch 0008 |
