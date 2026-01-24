# Test Pipeline Tool

**Location:** `/opt/mythos/utils/test_pipeline.py`  
**Created:** 2026-01-21  
**Patch:** 0008 - Orchestration System

## Overview

Simple pass/fail test suite for verifying Mythos pipeline health. Runs automatically through all core components and reports status.

## Quick Start

```bash
cd /opt/mythos
source .venv/bin/activate
python3 utils/test_pipeline.py
```

Or use the alias:
```bash
/opt/mythos/utils/test
```

## Tests Performed

1. **API Health** - GET /health endpoint
2. **Redis Connection** - Ping and queue status
3. **Qdrant Connection** - Collections endpoint
4. **Message Pipeline** - POST /message with test content

## Output

```
============================================================
  Mythos Pipeline Test
============================================================
=== Testing API Health ===
  Status: 200
  Response: {'status': 'healthy'}
...
============================================================
  Summary
============================================================
  ✅ api
  ✅ redis
  ✅ qdrant
  ✅ message

  ✅ All tests passed!
```

## Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

## Use Cases

- Post-deployment verification
- CI/CD health checks
- Quick sanity check after changes
- Monitoring scripts

## Related

- `debug_pipeline.py` - Extended debugging tool
