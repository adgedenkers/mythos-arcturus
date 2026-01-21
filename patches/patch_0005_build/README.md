# Patch 0005: AI-Native Graph Event Logging

## Overview

This patch implements a secondary logging system where system events are stored as graph nodes in Neo4j, enabling AI-powered diagnostics, causality analysis, and predictive maintenance.

## What This Patch Does

### Creates
- `/opt/mythos/graph_logging/` - Complete monitoring infrastructure
- System monitoring service (runs continuously)
- Daily event cleanup service (auto-removes events older than 10 days)
- Neo4j event schema with causality tracking

### Monitors
- System metrics (CPU, memory, disk) every 60 seconds
- Running processes and resource usage
- Systemd services: neo4j, postgresql, mythos_api, mythos_bot
- Auto-discovers services matching `mythos-*` or `arcturus-*` patterns

### Features
- **Event causality tracking** - Automatically links related events
- **AI query interface** - Structured diagnostic queries for LLM
- **Automatic cleanup** - Removes events older than 10 days
- **Automatic rollback** - Rolls back on any installation failure
- **Detailed error reporting** - Full diagnostic logs if installation fails

## Installation

```bash
# Extract the patch
cd ~/Downloads
unzip patch_0005_graph_logging.zip
cd patch_0005_graph_logging

# Run installation
./install.sh

# Or use the pa command (if configured)
pa 5
```

## Verification

```bash
# Check service is running
systemctl --user status arcturus-monitor

# Check recent events in Neo4j
cypher-shell "MATCH (e:Event) WHERE e.timestamp > datetime() - duration({minutes: 5}) RETURN e.type, e.timestamp ORDER BY e.timestamp DESC LIMIT 10"

# View logs
tail -f /opt/mythos/graph_logging/logs/monitor.log
```

## Configuration

Edit `/opt/mythos/graph_logging/config/monitoring_config.yaml` to adjust:
- Monitoring interval
- Alert thresholds
- Services to monitor
- Event retention period

Changes take effect after service restart:
```bash
systemctl --user restart arcturus-monitor
```

## Rollback

```bash
# Automatic rollback (if installation fails)
# - Handled automatically by install.sh

# Manual rollback
./rollback.sh

# Or use pa-rollback command
pa-rollback 5
```

## What Gets Logged

### System Events (When Thresholds Exceeded)
- High CPU usage (>80%)
- High memory usage (>80%)
- Low disk space (>90%)
- Process starts/stops
- Service failures

### Not Logged
- Every CPU/memory reading (only when thresholds exceeded)
- File system changes
- Network packets
- User activity

## Performance Impact

- **CPU**: ~0.5% (checks every 60 seconds)
- **Memory**: ~50-100 MB
- **Disk**: ~1-5 MB per day of events (auto-cleaned after 10 days)
- **Neo4j writes**: ~50-100 events per hour (only notable events)

## Files Created

```
/opt/mythos/graph_logging/
├── src/
│   ├── __init__.py
│   ├── system_monitor.py
│   ├── event_logger.py
│   └── diagnostics.py
├── config/
│   └── monitoring_config.yaml
├── logs/
│   └── monitor.log
└── scripts/
    └── cleanup_old_events.py

~/.config/systemd/user/
├── arcturus-monitor.service
├── arcturus-cleanup.service
└── arcturus-cleanup.timer
```

## Requirements

- Neo4j running at bolt://localhost:7687
- Python 3.11+
- psutil Python package
- neo4j Python driver
- systemd user services enabled

## Troubleshooting

### Service won't start
```bash
# Check logs
journalctl --user -u arcturus-monitor -n 50

# Check Neo4j connection
echo "MATCH (n) RETURN count(n) LIMIT 1" | cypher-shell -a bolt://localhost:7687
```

### Events not appearing
```bash
# Check if service is running
systemctl --user is-active arcturus-monitor

# Check for errors in log
tail -50 /opt/mythos/graph_logging/logs/monitor.log
```

### High resource usage
```bash
# Check monitoring interval (may be too frequent)
cat /opt/mythos/graph_logging/config/monitoring_config.yaml | grep interval

# Adjust if needed and restart
systemctl --user restart arcturus-monitor
```

## Next Steps

After this patch, you can:
- Query system state via Neo4j graph queries
- Integrate with local LLM for diagnostics (future patch)
- Add custom event types for your applications
- Build predictive failure detection (future patch)
