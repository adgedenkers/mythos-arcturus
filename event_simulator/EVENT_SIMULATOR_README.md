# Mythos Event Simulator

## Overview

A comprehensive testing framework that triggers system events to test your monitoring infrastructure and tracks test history per-machine in Neo4j.

## What It Does

### Simulates 5 Types of Events:

1. **CPU Spike** - Spawns CPU-burning processes to exceed 80% threshold
2. **Memory Pressure** - Allocates large memory blocks to trigger memory alerts
3. **Disk Fill** - Creates temporary large files (safely in /tmp)
4. **Service Restart** - Stops/starts services to trigger service events
5. **Process Spawn** - Creates multiple processes to test process tracking

### Tracks History Per-Machine

All test results are stored in Neo4j with:
- Hostname (identifies which machine ran the tests)
- Timestamp (when tests were run)
- Individual test results (pass/fail, events triggered)
- Historical trends (common failures, success rates)

## Installation

```bash
# Navigate to where you downloaded the files
cd /tmp

# Make install script executable
chmod +x install_simulator.sh

# Run installation
./install_simulator.sh
```

This installs:
- `/opt/mythos/tools/event_simulator.py` - Main Python script
- `/usr/local/bin/mythos-test` - Command wrapper

## Usage

### Run All Tests

```bash
# Run with default 90-second duration
mythos-test --run

# Run with custom duration (60 seconds)
mythos-test --run --duration 60

# Or just:
mythos-test  # Defaults to --run
```

**What happens:**
1. Triggers each test type sequentially
2. Waits for monitor to detect (65 seconds between tests)
3. Displays results in real-time
4. Saves results to Neo4j
5. Shows summary at end

**Example output:**
```
==========================================
Mythos Event Simulator
==========================================
Machine: arcturus
Test Run ID: 123e4567-e89b-12d3-a456-426614174000
Started: 2026-01-14T12:00:00
==========================================

[TEST] CPU Spike
------------------------------------------------------------
Spawning CPU stress for 90 seconds...
Spawned 32 CPU-burning processes
Current CPU: 95.2%
Status: ✓ PASS
Events triggered: 1

Waiting 65s for monitor to detect...

[TEST] Memory Pressure
------------------------------------------------------------
Allocating memory for 30 seconds...
Target allocation: 4.50 GB
Allocated: 4.50 GB
Current memory: 85.3%
Status: ✓ PASS
Events triggered: 1

...

==========================================
TEST SUMMARY
==========================================
Total Tests: 5
Passed: 5
Failed: 0
Events Triggered: 3
==========================================
```

### View Test History

```bash
# Show last 10 test runs on this machine
mythos-test --history

# Show last 20 runs
mythos-test --history --limit 20
```

**Example output:**
```
==========================================
Test History for arcturus
==========================================

Last 10 test runs:

Date                 Total    Passed   Failed   Events
------------------------------------------------------------
2026-01-14 12:00:00  5        5        0        3
2026-01-10 15:30:00  5        4        1        2
2026-01-05 09:15:00  5        5        0        3
2025-12-28 14:20:00  5        3        2        1

Statistics:
  Total runs: 10
  Average pass rate: 88.0%
  Total events triggered: 25
```

### Analyze Common Failures

```bash
mythos-test --failures
```

**Example output:**
```
==========================================
Common Failures for arcturus
==========================================

Most common failures:

  memory_pressure: 3 failures
  disk_fill: 2 failures
  cpu_spike: 1 failure
```

## How It Works

### Event Triggering

Each test is designed to exceed monitoring thresholds:

**CPU Spike:**
- Spawns one process per CPU core
- Each process runs `while True: pass` (infinite loop)
- Should exceed 80% CPU threshold
- Runs for specified duration
- Cleanly terminates all processes

**Memory Pressure:**
- Calculates 30% of available memory
- Allocates in 100MB chunks
- Holds memory for duration
- Releases cleanly

**Disk Fill:**
- Creates 1GB temporary file in /tmp
- Monitors disk usage
- Removes file after test
- Safe - won't fill actual disk

**Service Restart:**
- Stops arcturus-cleanup.service (safe test service)
- Waits 5 seconds
- Starts it again
- Triggers service_stopped and service_started events

**Process Spawn:**
- Spawns 20 `sleep` processes
- Monitors them for duration
- Cleanly terminates all

### Neo4j Storage

Test results are stored as graph nodes:

```cypher
(:TestMachine {hostname: "arcturus"})
  -[:HAD_TEST_RUN]->
(:TestRun {
  id: "uuid",
  timestamp: datetime(),
  total_tests: 5,
  passed_tests: 4,
  failed_tests: 1,
  events_triggered: 3,
  results: "[JSON array of individual test results]"
})
  <-[:TESTED_BY]-
(:System {name: "localhost"})
```

This enables:
- Historical trending per machine
- Cross-machine comparison
- Failure pattern analysis
- Test reliability tracking

## Querying Results in Neo4j

### Get All Test Runs for a Machine

```cypher
MATCH (machine:TestMachine {hostname: "arcturus"})-[:HAD_TEST_RUN]->(run:TestRun)
RETURN run
ORDER BY run.timestamp DESC
LIMIT 10
```

### Find Failing Tests

```cypher
MATCH (machine:TestMachine)-[:HAD_TEST_RUN]->(run:TestRun)
WHERE run.failed_tests > 0
RETURN machine.hostname, run.timestamp, run.failed_tests
ORDER BY run.timestamp DESC
```

### Compare Multiple Machines

```cypher
MATCH (machine:TestMachine)-[:HAD_TEST_RUN]->(run:TestRun)
RETURN machine.hostname AS machine,
       count(run) AS total_runs,
       avg(run.passed_tests) AS avg_passed,
       avg(run.events_triggered) AS avg_events
GROUP BY machine.hostname
```

### See Events Triggered by Tests

```cypher
MATCH (run:TestRun)-[:TESTED_BY]->(:System)-[:LOGGED]->(event:Event)
WHERE event.timestamp >= run.timestamp
  AND event.timestamp <= run.timestamp + duration({minutes: 10})
RETURN run.id, event.type, event.timestamp
```

## Best Practices

### Regular Testing Schedule

Set up a cron job to run tests regularly:

```bash
# Edit crontab
crontab -e

# Add line to run tests daily at 3 AM
0 3 * * * /usr/local/bin/mythos-test --run --duration 60 >> /var/log/mythos-tests.log 2>&1

# Or weekly on Sundays at 2 AM
0 2 * * 0 /usr/local/bin/mythos-test --run --duration 90 >> /var/log/mythos-tests.log 2>&1
```

### Multi-Machine Testing

Run the same tests on multiple machines:
1. Install on each machine
2. Run tests with same schedule
3. Compare results in Neo4j

The hostname automatically differentiates results, so you can see:
- Which machines have issues
- Which tests consistently fail on specific hardware
- Cross-machine reliability patterns

### Monitor Impact

After running tests, check:

```bash
# Did events get logged?
cypher-shell "MATCH (e:Event) WHERE e.timestamp > datetime() - duration({minutes: 20}) RETURN e.type, e.timestamp ORDER BY e.timestamp DESC"

# Ask the LLM
mythos-ask "what happened in the last 30 minutes?"

# Check monitor logs
tail -100 /opt/mythos/graph_logging/logs/monitor.log
```

## Troubleshooting

### Tests Don't Trigger Events

**Symptoms:** All tests pass but events_triggered = 0

**Causes:**
1. Monitor interval (60s) - events may be detected in next cycle
2. Thresholds too high - system doesn't reach 80% CPU/memory
3. Monitor not running

**Solutions:**
```bash
# Check monitor is running
systemctl --user status arcturus-monitor

# Check thresholds
cat /opt/mythos/graph_logging/config/monitoring_config.yaml

# Wait longer between tests
mythos-test --duration 120  # Longer duration
```

### History Not Saved

**Symptoms:** Tests run but `--history` shows nothing

**Causes:**
1. Neo4j not connected
2. NEO4J_PASSWORD not set
3. Permissions issue

**Solutions:**
```bash
# Check environment
echo $NEO4J_PASSWORD

# Test Neo4j connection
cypher-shell "RETURN 1"

# Check Neo4j is running
systemctl status neo4j
```

### CPU Test Doesn't Reach 80%

**Symptoms:** CPU spike test completes but CPU stays below threshold

**Causes:**
1. Too many CPU cores (harder to saturate)
2. Short duration
3. System under other load

**Solutions:**
```bash
# Increase duration
mythos-test --duration 120

# Check current CPU
top

# Watch in real-time
mythos-test --run & watch -n 1 'top -bn1 | head -20'
```

## Safety Notes

### Safe for Production
- All tests are designed to be non-destructive
- Memory/CPU stress is temporary and cleaned up
- Disk test uses /tmp (not production data)
- Service restart uses safe test service only
- Everything terminates cleanly

### When NOT to Run
- During critical operations
- On severely resource-constrained systems
- During active deployments
- If disk is already >90% full

### Emergency Stop
```bash
# If tests are causing issues, kill them:
killall python3
killall sleep

# Or reboot if necessary
sudo reboot
```

## Integration with LLM Diagnostics

After running tests, you can ask the LLM about them:

```bash
# What happened?
mythos-ask "what events were triggered in the last hour?"

# Why did CPU spike?
mythos-ask "why was CPU high at 3 AM?"

# Show me test results
mythos-ask "show me recent test runs"
```

The LLM can:
- Trace causality from test to event
- Explain what happened
- Correlate test runs with system behavior

## Advanced Usage

### Custom Test Durations Per Test

Edit `/opt/mythos/tools/event_simulator.py` and modify the `tests` list:

```python
tests = [
    ("CPU Spike", self.test_cpu_spike, 120),      # 120 seconds
    ("Memory Pressure", self.test_memory_pressure, 60),  # 60 seconds
    # ... etc
]
```

### Add Custom Tests

Add new test methods to the `EventSimulator` class:

```python
def test_custom(self, duration: int) -> Dict:
    """Your custom test"""
    result = {
        'test': 'custom_test',
        'started': datetime.now().isoformat(),
        'success': False,
        'events_triggered': 0
    }
    
    try:
        # Your test code here
        result['success'] = True
        result['completed'] = datetime.now().isoformat()
    except Exception as e:
        result['error'] = str(e)
    
    return result
```

Then add to the tests list in `run_all_tests()`.

---

**Now you have comprehensive event simulation with historical tracking!** 🎉
